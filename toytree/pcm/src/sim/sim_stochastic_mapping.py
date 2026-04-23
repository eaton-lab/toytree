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

from dataclasses import dataclass, field
from typing import Literal, Optional, Union

import numpy as np
import pandas as pd
from scipy.linalg import expm
from scipy.special import gammaln

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.data._src.expand_node_mapping import expand_node_mapping
from toytree.pcm.src.traits.fit_discrete_ctmc import (
    DiscreteMarkovModelFit,
    PCMDiscreteCTMCFitResult,
)
from toytree.utils.src.exceptions import ToytreeError

__all__ = ["PCMStochasticMapResult", "simulate_stochastic_map"]


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


@dataclass
class PCMStochasticMapResult:
    """Container for stochastic-map segments and common summary tables.

    The object stores the sampled branch-interval table returned by stochastic
    mapping and lazily computes common summaries such as dwell times,
    transition counts, edge-specific transition probabilities, and sampled node
    state frequencies.

    Parameters
    ----------
    segments : pandas.DataFrame
        One row per sampled branch segment. Required columns include
        ``map_id``, ``edge_id``, ``child``, ``parent``, ``state_idx``,
        ``state``, ``t_start``, ``t_end``, and ``duration``.
    node_states : pandas.DataFrame
        Sampled node states for each replicate with columns ``map_id``,
        ``node``, ``state_idx``, and ``state``.
    edge_table : pandas.DataFrame
        Edge metadata with columns ``edge_id``, ``child``, ``parent``, and
        ``length``.
    state_labels : tuple
        Labels for modeled states in state-index order.
    model : str
        Name of the fitted CTMC model used for mapping.
    engine : str
        Branch-history sampler used to generate the maps.
    nreplicates : int
        Number of stochastic-map replicates.

    Notes
    -----
    Summary properties return copies of cached tables. The raw ``segments``,
    ``node_states``, and ``edge_table`` attributes are stored as provided.
    """

    segments: pd.DataFrame
    node_states: pd.DataFrame
    edge_table: pd.DataFrame
    state_labels: tuple
    model: str
    engine: str
    nreplicates: int
    _cache: dict[str, pd.DataFrame] = field(default_factory=dict, repr=False)

    def __repr__(self) -> str:
        """Return a concise text summary of the stochastic-map result."""
        return (
            "PCMStochasticMapResult("
            f"model={self.model!r}, nreplicates={self.nreplicates}, "
            f"nsegments={self.segments.shape[0]}, "
            f"nedges={self.edge_table.shape[0]}, "
            f"nstates={len(self.state_labels)})"
        )

    @property
    def events(self) -> pd.DataFrame:
        """Return one row per state transition in parent-to-child direction."""
        if "events" not in self._cache:
            self._cache["events"] = self._get_events()
        return self._cache["events"].copy()

    @property
    def dwell(self) -> pd.DataFrame:
        """Return whole-tree state dwell times for each map replicate."""
        if "dwell" not in self._cache:
            self._cache["dwell"] = self._get_dwell()
        return self._cache["dwell"].copy()

    @property
    def transitions(self) -> pd.DataFrame:
        """Return whole-tree transition counts for each map replicate."""
        if "transitions" not in self._cache:
            self._cache["transitions"] = self._get_transitions()
        return self._cache["transitions"].copy()

    @property
    def edge_dwell(self) -> pd.DataFrame:
        """Return state dwell times for every edge and map replicate."""
        if "edge_dwell" not in self._cache:
            self._cache["edge_dwell"] = self._get_edge_dwell()
        return self._cache["edge_dwell"].copy()

    @property
    def edge_transitions(self) -> pd.DataFrame:
        """Return transition counts for every edge and map replicate."""
        if "edge_transitions" not in self._cache:
            self._cache["edge_transitions"] = self._get_edge_transitions()
        return self._cache["edge_transitions"].copy()

    @property
    def dwell_stats(self) -> pd.DataFrame:
        """Return replicate summaries of whole-tree dwell times."""
        if "dwell_stats" not in self._cache:
            self._cache["dwell_stats"] = _summarize_replicates(
                self.dwell,
                ["state_idx", "state"],
                "total_time",
            )
        return self._cache["dwell_stats"].copy()

    @property
    def transition_stats(self) -> pd.DataFrame:
        """Return replicate summaries of whole-tree transition counts."""
        if "transition_stats" not in self._cache:
            self._cache["transition_stats"] = _summarize_replicates(
                self.transitions,
                ["from_state_idx", "to_state_idx", "from_state", "to_state"],
                "count",
            )
        return self._cache["transition_stats"].copy()

    @property
    def edge_dwell_stats(self) -> pd.DataFrame:
        """Return replicate summaries of edge-specific state dwell times."""
        if "edge_dwell_stats" not in self._cache:
            total = _summarize_replicates(
                self.edge_dwell,
                ["edge_id", "child", "parent", "state_idx", "state"],
                "total_time",
            )
            prop = _summarize_replicates(
                self.edge_dwell,
                ["edge_id", "child", "parent", "state_idx", "state"],
                "prop_edge_time",
            )
            drop = ["prob_nonzero_prop_edge_time"]
            self._cache["edge_dwell_stats"] = total.merge(
                prop.drop(columns=[i for i in drop if i in prop.columns]),
                on=["edge_id", "child", "parent", "state_idx", "state"],
                how="left",
            )
        return self._cache["edge_dwell_stats"].copy()

    @property
    def edge_transition_stats(self) -> pd.DataFrame:
        """Return replicate summaries of edge-specific transition counts."""
        if "edge_transition_stats" not in self._cache:
            self._cache["edge_transition_stats"] = _summarize_replicates(
                self.edge_transitions,
                [
                    "edge_id",
                    "child",
                    "parent",
                    "from_state_idx",
                    "to_state_idx",
                    "from_state",
                    "to_state",
                ],
                "count",
            )
        return self._cache["edge_transition_stats"].copy()

    @property
    def node_state_probs(self) -> pd.DataFrame:
        """Return sampled state frequencies for every node."""
        if "node_state_probs" not in self._cache:
            self._cache["node_state_probs"] = self._get_node_state_probs()
        return self._cache["node_state_probs"].copy()

    def transition_probability(
        self,
        from_state: object,
        to_state: object,
        edge_id: int | None = None,
    ) -> float:
        """Return the fraction of maps containing a selected transition.

        Parameters
        ----------
        from_state : object
            Starting state label in parent-to-child evolutionary direction.
        to_state : object
            Ending state label in parent-to-child evolutionary direction.
        edge_id : int or None, default=None
            If provided, restrict the estimate to one branch. If None, count
            whether the transition occurred anywhere on the tree.

        Returns
        -------
        float
            Fraction of map replicates with at least one matching transition.
        """
        table = self.edge_transitions if edge_id is not None else self.transitions
        mask = table["from_state"].eq(from_state) & table["to_state"].eq(to_state)
        if edge_id is not None:
            mask &= table["edge_id"].eq(int(edge_id))
        subset = table.loc[mask, "count"]
        if subset.empty:
            return 0.0
        return float(subset.gt(0).mean())

    @property
    def _map_ids(self) -> list[int]:
        """Return map identifiers in stable order."""
        return list(range(int(self.nreplicates)))

    @property
    def _state_frame(self) -> pd.DataFrame:
        """Return state labels indexed by state_idx."""
        return pd.DataFrame(
            {
                "state_idx": np.arange(len(self.state_labels), dtype=int),
                "state": list(self.state_labels),
            }
        )

    @property
    def _transition_frame(self) -> pd.DataFrame:
        """Return all ordered off-diagonal state pairs."""
        rows = []
        labels = list(self.state_labels)
        for i, from_state in enumerate(labels):
            for j, to_state in enumerate(labels):
                if i == j:
                    continue
                rows.append(
                    {
                        "from_state_idx": i,
                        "to_state_idx": j,
                        "from_state": from_state,
                        "to_state": to_state,
                    }
                )
        return pd.DataFrame(
            rows,
            columns=[
                "from_state_idx",
                "to_state_idx",
                "from_state",
                "to_state",
            ],
        )

    def _get_events(self) -> pd.DataFrame:
        """Build parent-to-child transition events from segment boundaries."""
        rows: list[dict] = []
        labels = list(self.state_labels)
        edge_lengths = self.edge_table.set_index("edge_id")["length"]
        for (map_id, edge_id), subdf in self.segments.groupby(
            ["map_id", "edge_id"],
            sort=True,
        ):
            subdf = subdf.sort_values("t_start").reset_index(drop=True)
            if subdf.shape[0] < 2:
                continue
            length = float(edge_lengths.loc[int(edge_id)])
            for idx in range(1, subdf.shape[0]):
                childward = subdf.iloc[idx - 1]
                parentward = subdf.iloc[idx]
                from_idx = int(parentward["state_idx"])
                to_idx = int(childward["state_idx"])
                if from_idx == to_idx:
                    continue
                time_from_child = float(parentward["t_start"])
                rows.append(
                    {
                        "map_id": int(map_id),
                        "edge_id": int(edge_id),
                        "child": int(parentward["child"]),
                        "parent": int(parentward["parent"]),
                        "from_state_idx": from_idx,
                        "to_state_idx": to_idx,
                        "from_state": labels[from_idx],
                        "to_state": labels[to_idx],
                        "time_from_parent": float(length - time_from_child),
                        "time_from_child": time_from_child,
                        "time_abs": float(parentward["time_abs_start"]),
                    }
                )
        return pd.DataFrame(
            rows,
            columns=[
                "map_id",
                "edge_id",
                "child",
                "parent",
                "from_state_idx",
                "to_state_idx",
                "from_state",
                "to_state",
                "time_from_parent",
                "time_from_child",
                "time_abs",
            ],
        )

    def _get_dwell(self) -> pd.DataFrame:
        """Build zero-filled whole-tree dwell times."""
        grouped = (
            self.segments.groupby(["map_id", "state_idx"], as_index=False)["duration"]
            .sum()
            .rename(columns={"duration": "total_time"})
        )
        base = pd.MultiIndex.from_product(
            [self._map_ids, self._state_frame["state_idx"]],
            names=["map_id", "state_idx"],
        ).to_frame(index=False)
        out = base.merge(grouped, on=["map_id", "state_idx"], how="left")
        out["total_time"] = out["total_time"].fillna(0.0)
        out = out.merge(self._state_frame, on="state_idx", how="left")
        return out[["map_id", "state_idx", "state", "total_time"]]

    def _get_transitions(self) -> pd.DataFrame:
        """Build zero-filled whole-tree transition counts."""
        pairs = self._transition_frame
        if pairs.empty:
            return pd.DataFrame(
                columns=[
                    "map_id",
                    "from_state_idx",
                    "to_state_idx",
                    "from_state",
                    "to_state",
                    "count",
                    "any_transition",
                ]
            )
        grouped = (
            self.events.groupby(
                ["map_id", "from_state_idx", "to_state_idx"],
                as_index=False,
            )
            .size()
            .rename(columns={"size": "count"})
        )
        base = pd.concat(
            [pairs.assign(map_id=map_id) for map_id in self._map_ids],
            ignore_index=True,
        )
        out = base.merge(
            grouped,
            on=["map_id", "from_state_idx", "to_state_idx"],
            how="left",
        )
        out["count"] = out["count"].fillna(0).astype(int)
        out["any_transition"] = out["count"].gt(0)
        return out[
            [
                "map_id",
                "from_state_idx",
                "to_state_idx",
                "from_state",
                "to_state",
                "count",
                "any_transition",
            ]
        ]

    def _get_edge_dwell(self) -> pd.DataFrame:
        """Build zero-filled edge-specific dwell times."""
        grouped = (
            self.segments.groupby(
                ["map_id", "edge_id", "state_idx"],
                as_index=False,
            )["duration"]
            .sum()
            .rename(columns={"duration": "total_time"})
        )
        base = pd.MultiIndex.from_product(
            [
                self._map_ids,
                self.edge_table["edge_id"],
                self._state_frame["state_idx"],
            ],
            names=["map_id", "edge_id", "state_idx"],
        ).to_frame(index=False)
        out = base.merge(grouped, on=["map_id", "edge_id", "state_idx"], how="left")
        out["total_time"] = out["total_time"].fillna(0.0)
        out = out.merge(self.edge_table, on="edge_id", how="left")
        out = out.merge(self._state_frame, on="state_idx", how="left")
        lengths = out["length"].to_numpy(dtype=float)
        out["prop_edge_time"] = np.where(
            lengths > 0.0,
            out["total_time"].to_numpy(dtype=float) / lengths,
            np.nan,
        )
        return out[
            [
                "map_id",
                "edge_id",
                "child",
                "parent",
                "state_idx",
                "state",
                "total_time",
                "prop_edge_time",
            ]
        ]

    def _get_edge_transitions(self) -> pd.DataFrame:
        """Build zero-filled edge-specific transition counts."""
        pairs = self._transition_frame
        if pairs.empty:
            return pd.DataFrame(
                columns=[
                    "map_id",
                    "edge_id",
                    "child",
                    "parent",
                    "from_state_idx",
                    "to_state_idx",
                    "from_state",
                    "to_state",
                    "count",
                    "any_transition",
                ]
            )
        grouped = (
            self.events.groupby(
                ["map_id", "edge_id", "from_state_idx", "to_state_idx"],
                as_index=False,
            )
            .size()
            .rename(columns={"size": "count"})
        )
        edge_pairs = self.edge_table.merge(pairs, how="cross")
        base = pd.concat(
            [edge_pairs.assign(map_id=map_id) for map_id in self._map_ids],
            ignore_index=True,
        )
        out = base.merge(
            grouped,
            on=["map_id", "edge_id", "from_state_idx", "to_state_idx"],
            how="left",
        )
        out["count"] = out["count"].fillna(0).astype(int)
        out["any_transition"] = out["count"].gt(0)
        return out[
            [
                "map_id",
                "edge_id",
                "child",
                "parent",
                "from_state_idx",
                "to_state_idx",
                "from_state",
                "to_state",
                "count",
                "any_transition",
            ]
        ]

    def _get_node_state_probs(self) -> pd.DataFrame:
        """Build zero-filled sampled node state probabilities."""
        grouped = (
            self.node_states.groupby(["node", "state_idx"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
        )
        nodes = sorted(self.node_states["node"].unique().tolist())
        base = pd.MultiIndex.from_product(
            [nodes, self._state_frame["state_idx"]],
            names=["node", "state_idx"],
        ).to_frame(index=False)
        out = base.merge(grouped, on=["node", "state_idx"], how="left")
        out["count"] = out["count"].fillna(0).astype(int)
        out["probability"] = out["count"] / float(self.nreplicates)
        out = out.merge(self._state_frame, on="state_idx", how="left")
        return out[["node", "state_idx", "state", "count", "probability"]]


def _summarize_replicates(
    data: pd.DataFrame,
    keys: list[str],
    value: str,
) -> pd.DataFrame:
    """Return replicate summary statistics for one value column."""
    prefix = "" if value == "count" else f"_{value}"
    grouped = data.groupby(keys, dropna=False)[value]
    out = grouped.agg(
        **{
            f"mean{prefix}": "mean",
            f"sd{prefix}": "std",
            f"q025{prefix}": lambda x: x.quantile(0.025),
            f"q50{prefix}": lambda x: x.quantile(0.5),
            f"q975{prefix}": lambda x: x.quantile(0.975),
            f"prob_nonzero{prefix}": lambda x: x.gt(0).mean(),
        }
    ).reset_index()
    return out


@add_subpackage_method(PhyloCompAPI)
def simulate_stochastic_map(
    tree,
    data: Union[str, pd.Series],
    model_fit: PCMDiscreteCTMCFitResult,
    nreplicates: int = 1,
    seed: Optional[int] = None,
    max_branch_attempts: int = 10_000,
    engine: Literal["uniformization", "rejection"] = "uniformization",
) -> PCMStochasticMapResult:
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

    Posterior vectors are input constraints only. The returned object stores
    stochastic-map branch intervals and lazily computed summary tables.

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
    model_fit : PCMDiscreteCTMCFitResult
        A fitted MK model result from ``fit_discrete_ctmc``.
    nreplicates : int, default=1
        Number of map replicates to sample.
    seed : int | None, default=None
        Seed for the random number generator.
    max_branch_attempts : int, default=10000
        Maximum attempts for the rejection engine and fallback behavior.
    engine : {"uniformization", "rejection"}, default="uniformization"
        Branch-history sampler. Uniformization is typically faster and is the
        default. Rejection is retained for fallback and validation.

    Returns
    -------
    PCMStochasticMapResult
        Stochastic-map result object containing the segment table, sampled node
        states, and cached summary-table properties.

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
    ...     name="X",
    ...     tips_only=True,
    ...     inplace=True,
    ...     seed=1,
    ... )
    >>> tip_data = tree.get_tip_data("X")
    >>> fit = tree.pcm.fit_discrete_ctmc(data=tip_data, nstates=3, model="ER")
    >>> result = tree.pcm.simulate_stochastic_map(data=tip_data, model_fit=fit, seed=2)
    >>> result.segments.head()

    Use posterior node constraints from ancestral-state inference:

    >>> result = tree.pcm.infer_ancestral_states_discrete_ctmc(
    ...     "X", nstates=3, model="ER"
    ... )
    >>> fit = result["model_fit"]
    >>> post = result["data"]["X_anc_posterior"]
    >>> result2 = tree.pcm.simulate_stochastic_map(data=post, model_fit=fit, seed=3)
    >>> result2.edge_transition_stats.head()
    """
    if not isinstance(model_fit, PCMDiscreteCTMCFitResult):
        raise ToytreeError(
            "model_fit is required and must be a PCMDiscreteCTMCFitResult "
            "(fit with fit_discrete_ctmc first)."
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

    edge_table = pd.DataFrame(
        {
            "edge_id": np.arange(edges.shape[0], dtype=int),
            "child": edges[:, 0].astype(int),
            "parent": edges[:, 1].astype(int),
            "length": dists[edges[:, 0].astype(int)].astype(float),
        }
    )

    rows: list[dict] = []
    node_rows: list[dict] = []
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

        for nidx, state_idx in enumerate(sampled_node_states):
            state_idx = int(state_idx)
            node_rows.append(
                {
                    "map_id": map_id,
                    "node": int(nidx),
                    "state_idx": state_idx,
                    "state": state_labels[state_idx],
                }
            )

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

    return PCMStochasticMapResult(
        segments=pd.DataFrame(rows),
        node_states=pd.DataFrame(node_rows),
        edge_table=edge_table,
        state_labels=tuple(state_labels),
        model=model_fit.model,
        engine=eng,
        nreplicates=int(nreplicates),
    )
