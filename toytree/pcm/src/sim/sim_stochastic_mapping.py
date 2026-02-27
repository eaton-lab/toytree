#!/usr/bin/env python

"""Stochastic character mapping for discrete-state CTMC models on trees.

This module implements stochastic character mapping (SCM) for a single
categorical trait under MK models (ER/SYM/ARD via the shared fitter). The
default branch-history sampler uses uniformization, which is typically much
faster than endpoint-conditioned rejection sampling while producing equivalent
CTMC-conditioned mappings.

A legacy rejection engine is retained for validation and fallback on rare
numerical corner cases.
"""

from __future__ import annotations

from typing import Dict, Literal, Optional, Union

import numpy as np
import pandas as pd
from scipy.linalg import expm
from scipy.special import gammaln

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.data._src.expand_node_mapping import expand_node_mapping
from toytree.pcm.src.traits.discrete_markov_model_fit import (
    DiscreteMarkovModelFit,
    FitMarkovModelResult,
)
from toytree.utils.src.exceptions import ToytreeError

__all__ = ["simulate_stochastic_map"]


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
    name = (
        series.name
        if series.name is not None
        else ("trait" if not isinstance(data, str) else data)
    )
    return pd.Series(arr, index=range(tree.nnodes), name=name)


def _is_missing_value(value: object) -> bool:
    """Return True if a value should be treated as missing."""
    if value is None:
        return True
    try:
        out = pd.isna(value)
    except Exception:
        return False
    if isinstance(out, (bool, np.bool_)):
        return bool(out)
    return False


def _is_vector_like(value: object) -> bool:
    """Return True if value is tuple/list/ndarray."""
    return isinstance(value, (tuple, list, np.ndarray))


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


def _coerce_mapping_inputs(
    series: pd.Series,
    nstates: int,
) -> tuple[str, pd.Series, np.ndarray, np.ndarray]:
    """Return parsed mapping inputs for scalar-state or posterior mode."""
    observed = [i for i in series.tolist() if not _is_missing_value(i)]
    if not observed:
        fit_data = series.copy()
        return (
            "state",
            fit_data,
            np.full((series.size, nstates), np.nan, dtype=float),
            np.full(series.size, -1, dtype=int),
        )

    has_vectors = any(_is_vector_like(i) for i in observed)
    has_scalars = any(not _is_vector_like(i) for i in observed)
    if has_vectors and has_scalars:
        raise ToytreeError(
            "data cannot mix scalar states with posterior vectors. "
            "Use scalar states only, or posterior vectors for all non-missing nodes."
        )

    if not has_vectors:
        fit_data = _normalize_integer_float_states(series)
        _validate_state_types(fit_data)
        return (
            "state",
            fit_data,
            np.full((series.size, nstates), np.nan, dtype=float),
            np.full(series.size, -1, dtype=int),
        )

    entered_posteriors = np.full((series.size, nstates), np.nan, dtype=float)
    fixed_from_onehot = np.full(series.size, -1, dtype=int)
    fit_data = pd.Series(np.nan, index=series.index, name=series.name, dtype=object)

    for idx, value in series.items():
        if _is_missing_value(value):
            continue
        if not _is_vector_like(value):
            raise ToytreeError(
                "posterior mode requires all non-missing node entries to be "
                "tuple/list/array probability vectors."
            )
        arr = np.asarray(value, dtype=float).reshape(-1)
        if arr.size != nstates:
            raise ToytreeError(
                f"posterior vector length must equal nstates ({nstates})."
            )
        if np.any(~np.isfinite(arr)):
            raise ToytreeError("posterior vectors must contain finite values.")
        if np.any(arr < 0.0):
            raise ToytreeError("posterior vectors must be non-negative.")
        ssum = float(arr.sum())
        if not np.isclose(ssum, 1.0, atol=1e-8, rtol=0.0):
            raise ToytreeError("posterior vectors must sum to 1.")
        nidx = int(idx)
        entered_posteriors[nidx] = arr

        # Derive fixed constraints from one-hot rows while retaining posterior mode.
        midx = int(np.argmax(arr))
        is_one_hot = np.isclose(arr[midx], 1.0, atol=1e-8, rtol=0.0) and np.all(
            np.isclose(np.delete(arr, midx), 0.0, atol=1e-8, rtol=0.0)
        )
        if is_one_hot:
            fixed_from_onehot[nidx] = midx
            fit_data.at[idx] = midx

    return "posterior", fit_data, entered_posteriors, fixed_from_onehot


def _simulate_path_unconditioned(
    qmatrix: np.ndarray,
    length: float,
    start_state: int,
    rng: np.random.Generator,
) -> tuple[list[tuple[int, float, float]], int]:
    """Simulate one unconditioned CTMC path and return segments and final state."""
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


def _sample_branch_history_rejection(
    qmatrix: np.ndarray,
    length: float,
    start_state: int,
    end_state: int,
    rng: np.random.Generator,
    max_attempts: int,
) -> list[tuple[int, float, float]]:
    """Sample branch history by endpoint-conditioned rejection sampling."""
    if length < 0:
        raise ToytreeError("edge lengths must be non-negative for stochastic mapping")

    if length == 0:
        if start_state != end_state:
            raise ToytreeError(
                "cannot satisfy endpoint states on zero-length edge: "
                f"{start_state} -> {end_state}"
            )
        return [(int(start_state), 0.0, 0.0)]

    pij = float(expm(qmatrix * length)[int(start_state), int(end_state)])
    if pij <= 0.0:
        raise ToytreeError(
            f"endpoint transition has zero probability for branch length {length}: "
            f"{start_state} -> {end_state}"
        )

    for _ in range(max_attempts):
        segs, final_state = _simulate_path_unconditioned(
            qmatrix, length, start_state, rng
        )
        if int(final_state) == int(end_state):
            return segs

    raise ToytreeError(
        f"stochastic mapping failed to condition branch after {max_attempts} attempts: "
        f"{start_state} -> {end_state}, length={length}"
    )


def _build_uniformization_matrix(
    qmatrix: np.ndarray, omega_buffer: float
) -> np.ndarray:
    """Return uniformized transition matrix R = I + Q / omega."""
    rates = -np.diag(qmatrix).astype(float)
    omega = float(np.max(rates)) * (1.0 + float(omega_buffer))
    if not np.isfinite(omega) or omega <= 0.0:
        raise ToytreeError("uniformization requires a positive maximum departure rate")
    rmat = np.eye(qmatrix.shape[0], dtype=float) + (qmatrix / omega)
    # Numerical guard: clip tiny negatives then renormalize rows.
    rmat = np.clip(rmat, 0.0, None)
    row_sums = rmat.sum(axis=1, keepdims=True)
    if np.any(row_sums <= 0.0):
        raise ToytreeError("uniformization produced invalid embedded matrix rows")
    return rmat / row_sums


def _poisson_logpmf(n: np.ndarray, lam: float) -> np.ndarray:
    """Return Poisson log PMF values for integer vector n and rate lam."""
    n = np.asarray(n, dtype=float)
    if lam <= 0.0:
        out = np.full_like(n, -np.inf, dtype=float)
        out[n == 0] = 0.0
        return out
    return -lam + n * np.log(lam) - gammaln(n + 1.0)


def _sample_jump_count_conditioned(
    i: int,
    j: int,
    t: float,
    omega: float,
    rmat: np.ndarray,
    rng: np.random.Generator,
    max_terms: int,
    tol: float,
) -> tuple[int, list[np.ndarray]]:
    """Sample N from P(N=n | start=i, end=j, t) using truncated conditioning."""
    lam = omega * t
    if lam < 0.0 or not np.isfinite(lam):
        raise ToytreeError("invalid omega*t encountered in uniformization")

    n0 = int(np.floor(lam))
    nmax = max(n0 + 10 * int(np.sqrt(lam + 1.0)) + 100, 100)
    nmax = int(min(max_terms, max(nmax, 10)))

    rpowers: list[np.ndarray] = [np.eye(rmat.shape[0], dtype=float)]
    for _ in range(1, nmax + 1):
        rpowers.append(rpowers[-1] @ rmat)

    ns = np.arange(nmax + 1, dtype=int)
    log_pois = _poisson_logpmf(ns, lam)
    a = np.array([float(rpowers[n][i, j]) for n in ns], dtype=float)
    mask = a > 0.0
    if not np.any(mask):
        raise ToytreeError(
            f"uniformization conditioning has zero mass for endpoint {i}->{j} at t={t}"
        )

    log_w = np.full(nmax + 1, -np.inf, dtype=float)
    log_w[mask] = log_pois[mask] + np.log(a[mask])
    m = float(np.max(log_w[mask]))
    w = np.exp(log_w - m)
    z = float(np.sum(w))
    if (not np.isfinite(z)) or z <= 0.0:
        raise ToytreeError(
            "uniformization conditioning weights are numerically unstable"
        )
    probs = w / z

    if float(np.sum(probs)) < 1.0 - tol:
        raise ToytreeError(
            "uniformization truncation too aggressive; increase max_terms"
        )

    n = int(rng.choice(ns, p=probs))
    return n, rpowers[: n + 1]


def _merge_segments(
    segs: list[tuple[int, float, float]],
) -> list[tuple[int, float, float]]:
    """Merge adjacent segments with identical states."""
    if not segs:
        return segs
    merged: list[tuple[int, float, float]] = [segs[0]]
    for state, start, end in segs[1:]:
        pstate, pstart, pend = merged[-1]
        if int(state) == int(pstate):
            merged[-1] = (pstate, pstart, float(end))
        else:
            merged.append((int(state), float(start), float(end)))
    return merged


def _sample_branch_history_uniformized(
    qmatrix: np.ndarray,
    length: float,
    start_state: int,
    end_state: int,
    rng: np.random.Generator,
    omega_buffer: float,
    max_terms: int,
    tol: float,
) -> list[tuple[int, float, float]]:
    """Sample a conditioned CTMC branch history using uniformization."""
    if length < 0:
        raise ToytreeError("edge lengths must be non-negative for stochastic mapping")
    if length == 0:
        if int(start_state) != int(end_state):
            raise ToytreeError(
                "cannot satisfy endpoint states on zero-length edge: "
                f"{start_state} -> {end_state}"
            )
        return [(int(start_state), 0.0, 0.0)]

    pmat = expm(qmatrix * float(length))
    pij = float(pmat[int(start_state), int(end_state)])
    if pij <= 0.0:
        raise ToytreeError(
            f"endpoint transition has zero probability for branch length {length}: "
            f"{start_state} -> {end_state}"
        )

    omega = float(np.max(-np.diag(qmatrix))) * (1.0 + float(omega_buffer))
    rmat = _build_uniformization_matrix(qmatrix, omega_buffer=omega_buffer)

    n, rpowers = _sample_jump_count_conditioned(
        int(start_state),
        int(end_state),
        float(length),
        omega,
        rmat,
        rng,
        max_terms=max_terms,
        tol=tol,
    )

    if n == 0:
        return [(int(start_state), 0.0, float(length))]

    states = [int(start_state)]
    curr = int(start_state)
    for k in range(1, n):
        rem = n - k
        weights = rmat[curr] * rpowers[rem][:, int(end_state)]
        total = float(np.sum(weights))
        if total <= 0.0 or not np.isfinite(total):
            raise ToytreeError(
                "uniformization failed while sampling conditioned intermediate states"
            )
        probs = weights / total
        curr = int(rng.choice(rmat.shape[0], p=probs))
        states.append(curr)
    states.append(int(end_state))

    jumps = np.sort(rng.uniform(0.0, float(length), size=n))
    bounds = np.concatenate(([0.0], jumps, [float(length)]))

    segs = []
    for idx, state in enumerate(states):
        segs.append((int(state), float(bounds[idx]), float(bounds[idx + 1])))
    return _merge_segments(segs)


def _summarize_segments(
    seg_df: pd.DataFrame,
    state_labels: list,
) -> dict[str, pd.DataFrame]:
    """Return dwell-time and transition-count summaries for segment mappings."""
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
        transitions = (
            pd.DataFrame(trans_rows)
            .groupby(
                ["map_id", "from_state_idx", "to_state_idx", "from_state", "to_state"],
                as_index=False,
            )["count"]
            .sum()
        )
    else:
        transitions = pd.DataFrame(
            columns=[
                "map_id",
                "from_state_idx",
                "to_state_idx",
                "from_state",
                "to_state",
                "count",
            ]
        )

    return {
        "segments": seg_df,
        "dwell": dwell,
        "transitions": transitions,
    }


@add_subpackage_method(PhyloCompAPI)
def simulate_stochastic_map(
    tree,
    data: Union[str, pd.Series],
    model_fit: FitMarkovModelResult,
    nreplicates: int = 1,
    seed: Optional[int] = None,
    max_branch_attempts: int = 10_000,
    return_summary: bool = False,
    engine: Literal["uniformization", "rejection"] = "uniformization",
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Sample stochastic character maps for one discrete trait under MK.

    The ``data`` argument supports two input modes:

    - Scalar-state mode: non-missing entries are discrete scalar states
      (int/str), treated as hard constraints.
    - Posterior-vector mode: non-missing entries are tuple/list/array vectors
      of length ``model_fit.nstates`` that sum to 1. In this mode, all
      non-missing entries must be vector format (no scalar/vector mixing).
      One-hot vectors (e.g., ``(1, 0, 0)``) are treated as fixed constraints.
      Non-one-hot vectors are sampled directly. Missing nodes are sampled from
      model-based posterior probabilities.

    Output remains stochastic-map branch intervals (and optional summaries);
    posterior vectors are input constraints only.

    Parameters
    ----------
    tree : ToyTree
        Input tree on which to map discrete-state histories.
    data : str | pandas.Series
        Trait states as feature name or Series. Values can be provided for all
        nodes or tips only.
        Non-missing entries may be scalar states or posterior vectors, but
        cannot mix formats. Posterior vectors must be non-negative, finite,
        length ``model_fit.nstates``, and sum to 1.
    model_fit : FitMarkovModelResult
        A fitted MK model result from ``fit_discrete_markov_model``.
    nreplicates : int, default=1
        Number of map replicates to sample.
    seed : int | None, default=None
        Seed for the random number generator.
    max_branch_attempts : int, default=10000
        Maximum attempts for the rejection engine and fallback behavior.
    return_summary : bool, default=False
        If True, return dict with segment/dwell/transition tables.
    engine : {"uniformization", "rejection"}, default="uniformization"
        Branch-history sampler. Uniformization is typically faster and is the
        default. Rejection is retained for fallback and validation.

    Returns
    -------
    pandas.DataFrame or dict[str, pandas.DataFrame]
        Segment table, or a dict containing ``segments``, ``dwell``, and
        ``transitions`` summary tables.

    Raises
    ------
    ToytreeError
        If inputs are invalid, endpoint conditioning is impossible, or sampling
        fails under the selected engine.

    Examples
    --------
    Use tip observations from ``tree.get_tip_data()``:

    >>> tree = toytree.rtree.unittree(ntips=20, seed=123)
    >>> tree.pcm.simulate_discrete_trait(
    ...     nstates=3,
    ...     model="ER",
    ...     trait_name="X",
    ...     tips_only=True,
    ...     inplace=True,
    ...     seed=1,
    ... )
    >>> tip_data = tree.get_tip_data("X")
    >>> fit = tree.pcm.fit_discrete_markov_model(data=tip_data, nstates=3, model="ER")
    >>> maps = tree.pcm.simulate_stochastic_map(data=tip_data, model_fit=fit, seed=2)

    Use posterior node constraints from ancestral-state inference:

    >>> result = tree.pcm.infer_ancestral_states_discrete_ctmc(
    ...     "X", nstates=3, model="ER"
    ... )
    >>> fit = result["model_fit"]
    >>> post = result["data"]["X_anc_posterior"]
    >>> maps2 = tree.pcm.simulate_stochastic_map(data=post, model_fit=fit, seed=3)
    """
    if not isinstance(model_fit, FitMarkovModelResult):
        raise ToytreeError(
            "model_fit is required and must be a FitMarkovModelResult "
            "(fit with fit_discrete_markov_model first)."
        )
    if int(max_branch_attempts) < 1:
        raise ToytreeError("max_branch_attempts must be >= 1")
    nreplicates = max(1, int(nreplicates))
    eng = str(engine).lower()
    if eng not in {"uniformization", "rejection"}:
        raise ToytreeError("engine must be one of: 'uniformization', 'rejection'")

    series = _coerce_series_to_all_nodes(tree, data)
    mode, fit_data, entered_posteriors, fixed_from_onehot = _coerce_mapping_inputs(
        series,
        nstates=int(model_fit.nstates),
    )

    fitter = DiscreteMarkovModelFit(
        tree=tree,
        data=fit_data,
        nstates=int(model_fit.nstates),
        model=model_fit.model,
        fixed_rates=model_fit.fixed_rates,
        fixed_state_frequencies=model_fit.fixed_state_frequencies,
        root_prior=None,
        rate_scalar=1.0,
    )

    qmatrix = np.array(model_fit.qmatrix, dtype=float)
    node_probs, _ = fitter._compute_node_posteriors(
        qmatrix, model_fit.state_frequencies
    )
    posterior = node_probs.to_numpy(dtype=float)

    fixed_states = np.full(tree.nnodes, -1, dtype=int)
    if mode == "state":
        for idx, val in enumerate(fitter.tip_states):
            if not np.isnan(val):
                fixed_states[idx] = int(val)
    else:
        fixed_states[:] = fixed_from_onehot

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
                continue
            if mode == "posterior" and np.all(np.isfinite(entered_posteriors[nidx])):
                probs = entered_posteriors[nidx].astype(float)
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

            if eng == "rejection":
                segs = _sample_branch_history_rejection(
                    qmatrix=qmatrix,
                    length=length,
                    start_state=start_state,
                    end_state=end_state,
                    rng=rng,
                    max_attempts=int(max_branch_attempts),
                )
            else:
                try:
                    segs = _sample_branch_history_uniformized(
                        qmatrix=qmatrix,
                        length=length,
                        start_state=start_state,
                        end_state=end_state,
                        rng=rng,
                        omega_buffer=0.05,
                        max_terms=5000,
                        tol=1e-12,
                    )
                except ToytreeError:
                    segs = _sample_branch_history_rejection(
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
    return _summarize_segments(seg_df, state_labels)
