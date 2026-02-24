#!/usr/bin/env python

"""Stochastic character mapping for discrete-state CTMC models on trees.

Stochastic character mapping (SCM) samples full character histories
(state dwell times and transition events along branches) conditional on
an observed discrete trait and an MK model of evolution. Unlike marginal
ancestral-state reconstruction, SCM provides branchwise realizations of
when and where changes occurred, enabling summaries of transition counts,
time spent in each state, and uncertainty in mapped histories.

This module implements SCM for a single discrete trait under fitted MK
models (ER / SYM / ARD via the shared discrete-model fitter). Endpoint-
conditioned branch histories are sampled with rejection sampling from the
continuous-time Markov chain, conditioned on sampled node states from
posterior probabilities.

Implemented outputs include per-segment mappings (state intervals on each
edge) and optional summaries of state dwell times and transition counts
across replicate maps.

References
----------
Nielsen, R. (2002). Mapping mutations on phylogenies.
Systematic Biology, 51(5), 729-739.

Huelsenbeck, J. P., Nielsen, R., & Bollback, J. P. (2003).
Stochastic mapping of morphological characters.
Systematic Biology, 52(2), 131-158.

Bollback, J. P. (2006). SIMMAP: stochastic character mapping of
discrete traits on phylogenies. BMC Bioinformatics, 7, 88.
"""

from __future__ import annotations

from typing import Dict, Optional, Union

import numpy as np
import pandas as pd
from scipy.linalg import expm

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.data._src.expand_node_mapping import expand_node_mapping
from toytree.pcm.src.traits.discrete_markov_model_fit import (
    DiscreteMarkovModelFit,
    FitMarkovModelResult,
)
from toytree.utils import ToytreeError

__all__ = ["stochastic_map_discrete_ctmc"]


def _coerce_series_to_all_nodes(tree, data: Union[str, pd.Series]) -> pd.Series:
    """Return a Series of length nnodes ordered by node idx."""
    if isinstance(data, str):
        series = tree.get_node_data(data, missing=float("nan"))
    elif isinstance(data, pd.Series):
        series = data.copy()
    else:
        raise ToytreeError("data must be a feature name (str) or pandas Series")

    mapping = dict(series.dropna())
    mapping = expand_node_mapping(tree, mapping)
    arr = np.full(tree.nnodes, np.nan, dtype=object)
    for node, value in mapping.items():
        arr[node._idx] = value
    name = series.name if series.name is not None else ("trait" if not isinstance(data, str) else data)
    return pd.Series(arr, index=range(tree.nnodes), name=name)


def _validate_state_types(series: pd.Series) -> None:
    """Require int or str states (missing can be NaN)."""
    observed = series.dropna().unique().tolist()
    valid_types = (int, np.integer, str)
    cleaned = []
    for v in observed:
        if isinstance(v, bool):
            raise ToytreeError("trait states must be int or str")
        if isinstance(v, (float, np.floating)):
            if float(v).is_integer():
                cleaned.append(int(v))
                continue
            raise ToytreeError("trait states must be int or str")
        if not isinstance(v, valid_types):
            raise ToytreeError("trait states must be int or str")
        cleaned.append(v)
    if not cleaned:
        return
    types = {type(v) for v in cleaned}
    if len(types) > 1:
        raise ToytreeError("trait states must be all int or all str (no mixing)")


def _normalize_integer_float_states(series: pd.Series) -> pd.Series:
    """Cast integer-valued float states to int (keep NaN as missing)."""
    out = series.copy()
    for idx, val in out.items():
        if pd.isna(val):
            continue
        if isinstance(val, (float, np.floating)) and float(val).is_integer():
            out.at[idx] = int(val)
    return out


def _simulate_path_unconditioned(
    qmatrix: np.ndarray,
    length: float,
    start_state: int,
    rng: np.random.Generator,
) -> tuple[list[tuple[int, float, float]], int]:
    """Simulate one CTMC path and return segments and final state."""
    t = 0.0
    state = int(start_state)
    segs: list[tuple[int, float, float]] = []
    nstates = qmatrix.shape[0]

    while t < length:
        rate = float(-qmatrix[state, state])
        if rate <= 0.0:
            segs.append((state, t, length))
            return segs, state

        wait = float(rng.exponential(1.0 / rate))
        t_next = t + wait
        if t_next >= length:
            segs.append((state, t, length))
            return segs, state

        segs.append((state, t, t_next))
        probs = np.maximum(qmatrix[state].copy(), 0.0)
        probs[state] = 0.0
        psum = float(probs.sum())
        if psum <= 0.0:
            return segs, state
        probs /= psum
        state = int(rng.choice(nstates, p=probs))
        t = t_next

    return segs, state


def _sample_branch_history_conditioned(
    qmatrix: np.ndarray,
    length: float,
    start_state: int,
    end_state: int,
    rng: np.random.Generator,
    max_attempts: int,
) -> list[tuple[int, float, float]]:
    """Sample CTMC branch history conditioned on endpoint states."""
    if length < 0:
        raise ToytreeError("edge lengths must be non-negative for stochastic mapping")

    if length == 0:
        if start_state != end_state:
            raise ToytreeError(
                f"cannot satisfy endpoint states on zero-length edge: {start_state} -> {end_state}"
            )
        return [(int(start_state), 0.0, 0.0)]

    pij = float(expm(qmatrix * length)[int(start_state), int(end_state)])
    if pij <= 0.0:
        raise ToytreeError(
            f"endpoint transition has zero probability for branch length {length}: "
            f"{start_state} -> {end_state}"
        )

    for _ in range(max_attempts):
        segs, final_state = _simulate_path_unconditioned(qmatrix, length, start_state, rng)
        if int(final_state) == int(end_state):
            return segs

    raise ToytreeError(
        f"stochastic mapping failed to condition branch after {max_attempts} attempts: "
        f"{start_state} -> {end_state}, length={length}"
    )


@add_subpackage_method(PhyloCompAPI)
def stochastic_map_discrete_ctmc(
    tree,
    data: Union[str, pd.Series],
    model_fit: Optional[FitMarkovModelResult] = None,
    nstates: Optional[int] = None,
    model: str = "ER",
    fixed_rates: Optional[np.ndarray] = None,
    fixed_state_frequencies: Optional[np.ndarray] = None,
    root_prior: Optional[np.ndarray] = None,
    rate_scalar: float = 1.0,
    nreplicates: int = 1,
    seed: Optional[int] = None,
    max_branch_attempts: int = 10_000,
    return_summary: bool = False,
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Sample stochastic character maps for one discrete trait under MK.

    Parameters
    ----------
    data: str | pd.Series
        Trait states as feature name or series. Values may be provided
        for all nodes or tips only. Internal node non-NaN values are
        treated as fixed constraints.
    model_fit: FitMarkovModelResult | None
        Optional fitted model result. If None, a model is fit from input
        data using the provided model-fitting arguments.
    nstates, model, fixed_rates, fixed_state_frequencies, root_prior, rate_scalar
        Model-fitting arguments used only when `model_fit` is None.
    nreplicates: int
        Number of stochastic maps to sample.
    seed: int | None
        RNG seed.
    max_branch_attempts: int
        Maximum rejection attempts per branch for endpoint conditioning.
    return_summary: bool
        If True, return dict with `segments`, `dwell`, and `transitions`.

    Returns
    -------
    pd.DataFrame or dict[str, pd.DataFrame]
        Segment table, or segment table plus summary tables.
    """
    if int(max_branch_attempts) < 1:
        raise ToytreeError("max_branch_attempts must be >= 1")
    nreplicates = max(1, int(nreplicates))

    series = _coerce_series_to_all_nodes(tree, data)
    _validate_state_types(series)
    series = _normalize_integer_float_states(series)

    if model_fit is None:
        if nstates is None:
            raise ToytreeError("nstates is required when model_fit is None")
        fitter = DiscreteMarkovModelFit(
            tree=tree,
            data=series,
            nstates=int(nstates),
            model=model,
            fixed_rates=fixed_rates,
            fixed_state_frequencies=fixed_state_frequencies,
            root_prior=root_prior,
            rate_scalar=rate_scalar,
        )
        model_fit = fitter.fit(compute_posteriors=False)
    else:
        if nstates is not None and int(nstates) != int(model_fit.nstates):
            raise ToytreeError("nstates does not match model_fit.nstates")
        fitter = DiscreteMarkovModelFit(
            tree=tree,
            data=series,
            nstates=int(model_fit.nstates),
            model=model_fit.model,
            fixed_rates=model_fit.fixed_rates,
            fixed_state_frequencies=model_fit.fixed_state_frequencies,
            root_prior=root_prior,
            rate_scalar=1.0,
        )

    qmatrix = np.array(model_fit.qmatrix, dtype=float)
    node_probs, _ = fitter._compute_node_posteriors(qmatrix, model_fit.state_frequencies)
    posterior = node_probs.to_numpy(dtype=float)

    fixed_states = np.full(tree.nnodes, -1, dtype=int)
    for idx, val in enumerate(fitter.tip_states):
        if not np.isnan(val):
            fixed_states[idx] = int(val)

    edges = tree.get_edges("idx")
    dists = tree.get_node_data("dist").to_numpy(dtype=float)
    heights = tree.get_node_data("height").to_numpy(dtype=float)
    state_labels = list(node_probs.columns)
    rng = np.random.default_rng(seed)

    rows: list[dict] = []
    for map_id in range(nreplicates):
        sampled_node_states = np.full(tree.nnodes, -1, dtype=int)
        for nidx in range(tree.nnodes):
            if fixed_states[nidx] >= 0:
                sampled_node_states[nidx] = fixed_states[nidx]
            else:
                probs = posterior[nidx].astype(float)
                psum = float(probs.sum())
                if psum <= 0.0:
                    raise ToytreeError(f"invalid posterior probabilities at node {nidx}")
                probs /= psum
                sampled_node_states[nidx] = int(rng.choice(len(probs), p=probs))

        for edge_id, (child, parent) in enumerate(edges):
            child = int(child)
            parent = int(parent)
            length = float(dists[child])
            start_state = int(sampled_node_states[child])
            end_state = int(sampled_node_states[parent])
            segs = _sample_branch_history_conditioned(
                qmatrix=qmatrix,
                length=length,
                start_state=start_state,
                end_state=end_state,
                rng=rng,
                max_attempts=int(max_branch_attempts),
            )
            base_abs = float(heights[child])
            for state_idx, t_start, t_end in segs:
                rows.append(
                    {
                        "map_id": map_id,
                        "edge_id": edge_id,
                        "child": child,
                        "parent": parent,
                        "state_idx": int(state_idx),
                        "state": state_labels[int(state_idx)],
                        "t_start": float(t_start),
                        "t_end": float(t_end),
                        "duration": float(t_end - t_start),
                        "time_abs_start": base_abs + float(t_start),
                        "time_abs_end": base_abs + float(t_end),
                    }
                )

    seg_df = pd.DataFrame(rows)
    if not return_summary:
        return seg_df

    dwell = (
        seg_df.groupby(["map_id", "state_idx", "state"], as_index=False)["duration"]
        .sum()
        .rename(columns={"duration": "total_time"})
    )

    trans_rows: list[dict] = []
    for (map_id, edge_id), subdf in seg_df.groupby(["map_id", "edge_id"], sort=True):
        subdf = subdf.sort_values("t_start")
        states = subdf["state_idx"].to_numpy(dtype=int)
        for i in range(1, len(states)):
            frm = int(states[i - 1])
            to = int(states[i])
            if frm == to:
                continue
            trans_rows.append(
                {
                    "map_id": int(map_id),
                    "from_state_idx": frm,
                    "to_state_idx": to,
                    "from_state": state_labels[frm],
                    "to_state": state_labels[to],
                    "count": 1,
                }
            )
    if trans_rows:
        trans_df = (
            pd.DataFrame(trans_rows)
            .groupby(
                ["map_id", "from_state_idx", "to_state_idx", "from_state", "to_state"],
                as_index=False,
            )["count"]
            .sum()
        )
    else:
        trans_df = pd.DataFrame(
            columns=[
                "map_id",
                "from_state_idx",
                "to_state_idx",
                "from_state",
                "to_state",
                "count",
            ]
        )

    return {"segments": seg_df, "dwell": dwell, "transitions": trans_df}
