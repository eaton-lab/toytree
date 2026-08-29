#!/usr/bin/env python

"""Utilities for branch-length penalized pseudolikelihood fitting."""

from concurrent.futures import ProcessPoolExecutor, as_completed
from numbers import Real
from typing import Any, Callable, Dict, Tuple

import numpy as np
from loguru import logger

from toytree.core import ToyTree
from toytree.utils import ToytreeError

Calibrations = Dict[int, Tuple[float, float]]
PARAM_MIN = 1e-8
PARAM_MAX = 1e8
FINAL_AGE_NEGATIVE_TOL = 1e-8


def _pack_log_rates(rates: np.ndarray, rate_floor: float = 1e-12) -> np.ndarray:
    """Pack positive rate vector in log-space."""
    return np.log(np.clip(np.asarray(rates, dtype=float), rate_floor, None))


def _unpack_log_rates(log_rates: np.ndarray) -> np.ndarray:
    """Unpack positive rate vector from log-space."""
    return np.exp(np.asarray(log_rates, dtype=float))


def _run_multistart(
    worker: Callable[[dict[str, Any]], dict[str, Any]],
    payloads: list[dict[str, Any]],
    ncores: int = 1,
) -> list[dict[str, Any]]:
    """Run multistart fits serially or in parallel and collect results.

    Worker must return a dict containing at least:
    - start: int
    - objective: float
    - converged: bool
    - message: str
    """
    if not payloads:
        return []
    workers = max(1, min(int(ncores), len(payloads)))
    results: list[dict[str, Any]] = []

    if workers == 1:
        for payload in payloads:
            try:
                results.append(worker(payload))
            except Exception as exc:  # pragma: no cover
                results.append(
                    {
                        "start": int(payload.get("start", -1)),
                        "objective": float("inf"),
                        "converged": False,
                        "message": f"{type(exc).__name__}: {exc}",
                        "error": True,
                    }
                )
        return sorted(results, key=lambda x: x["start"])

    try:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            fut_to_start = {
                pool.submit(worker, payload): int(payload.get("start", -1))
                for payload in payloads
            }
            for fut in as_completed(fut_to_start):
                start = fut_to_start[fut]
                try:
                    results.append(fut.result())
                except Exception as exc:
                    results.append(
                        {
                            "start": start,
                            "objective": float("inf"),
                            "converged": False,
                            "message": f"{type(exc).__name__}: {exc}",
                            "error": True,
                        }
                    )
        return sorted(results, key=lambda x: x["start"])
    except (PermissionError, OSError) as exc:
        logger.warning(
            f"ProcessPool unavailable; falling back to serial multistart: {exc}"
        )
        return _run_multistart(worker, payloads, ncores=1)


def _select_best_multistart(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Return best multistart result preferring converged finite objectives."""
    if not results:
        raise ValueError("no multistart results were produced")
    finite = [i for i in results if np.isfinite(i.get("objective", float("inf")))]
    if not finite:
        msgs = "; ".join(i.get("message", "unknown failure") for i in results[:3])
        raise RuntimeError(f"all starts failed with non-finite objective: {msgs}")
    conv = [i for i in finite if i.get("converged", False)]
    pool = conv if conv else finite
    return min(pool, key=lambda x: float(x["objective"]))


def _get_children_map_from_edges(edges: np.ndarray) -> Dict[int, np.ndarray]:
    """Return mapping parent_idx -> child_idxs from edge array."""
    children_map: Dict[int, list[int]] = {}
    for child, parent in edges:
        children_map.setdefault(int(parent), []).append(int(child))
    return {k: np.array(v, dtype=int) for k, v in children_map.items()}


def _sigmoid(x: np.ndarray) -> np.ndarray:
    values = np.asarray(x, dtype=float)
    result = np.empty_like(values)
    positive = values >= 0.0
    result[positive] = 1.0 / (1.0 + np.exp(-values[positive]))
    exp_values = np.exp(values[~positive])
    result[~positive] = exp_values / (1.0 + exp_values)
    return result


def _logit(p: np.ndarray) -> np.ndarray:
    return np.log(p / (1.0 - p))


def _validate_branch_lengths(tree: ToyTree) -> np.ndarray:
    """Return edge lengths after validating the PL working likelihood input."""
    dists = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
    if np.any(~np.isfinite(dists)):
        raise ToytreeError("branch lengths must be finite for penalized likelihood.")
    if np.any(dists < 0.0):
        raise ToytreeError(
            "branch lengths must be non-negative for penalized likelihood."
        )
    return dists


def _validate_lambda(lam: Any) -> float:
    """Return a finite, strictly positive smoothing parameter."""
    if isinstance(lam, bool) or not isinstance(lam, Real):
        raise ToytreeError("lam must be a finite positive real number.")
    value = float(lam)
    if not np.isfinite(value) or value <= 0.0:
        raise ToytreeError("lam must be a finite positive real number.")
    return value


def _validate_ncategories(ncategories: Any, nedges: int) -> int:
    """Return a validated scalar discrete-category count."""
    if isinstance(ncategories, bool) or not isinstance(ncategories, (int, np.integer)):
        raise ToytreeError("ncategories must be a positive integer.")
    value = int(ncategories)
    if value < 1:
        raise ToytreeError("ncategories must be >= 1.")
    if value > int(nedges):
        raise ToytreeError(
            f"ncategories ({value}) cannot exceed the number of edges ({nedges})."
        )
    return value


def _validate_observation_mask(mask: Any, nedges: int) -> np.ndarray:
    """Return a Boolean mask selecting observed branch lengths.

    This is private machinery for terminal-edge cross-validation. Excluded
    branches remain in the topology and smoothing penalty but make no
    contribution to the fractional-Poisson pseudolikelihood.
    """
    if mask is None:
        return np.ones(int(nedges), dtype=bool)
    values = np.asarray(mask)
    if values.shape != (int(nedges),):
        raise ToytreeError(
            f"observation mask must have shape ({nedges},), not {values.shape}."
        )
    if values.dtype != np.bool_:
        raise ToytreeError("observation mask must contain only Boolean values.")
    if not np.any(values):
        raise ToytreeError("observation mask must retain at least one edge.")
    return values.copy()


def _result_observation_metadata() -> dict[str, str]:
    """Return the declared branch-length pseudolikelihood observation model."""
    return {
        "observation_model": "fractional_poisson",
        "branch_length_units": "substitutions_per_site",
    }


def _coerce_calibration_interval(calib: Any) -> tuple[float, float]:
    """Return one calibration coerced to a finite closed interval."""
    if isinstance(calib, bool):
        raise ToytreeError("calibration ages must be numeric, not boolean.")
    if isinstance(calib, Real):
        lo = hi = float(calib)
    else:
        try:
            lo, hi = calib
        except Exception as exc:  # pragma: no cover
            raise ToytreeError(
                "calibrations must be numeric ages or (min_age, max_age) pairs."
            ) from exc
        lo = float(lo)
        hi = float(hi)
    if not (np.isfinite(lo) and np.isfinite(hi)):
        raise ToytreeError("calibrations must contain only finite numeric ages.")
    if lo < 0.0 or hi < 0.0:
        raise ToytreeError("calibration ages must be non-negative.")
    if lo > hi:
        raise ToytreeError(
            f"invalid calibration interval ({lo}, {hi}): min_age cannot exceed max_age."
        )
    return lo, hi


def _normalize_calibrations(
    tree: ToyTree,
    calibrations: dict[Any, Any] | None,
    dist_floor: float = 1e-12,
) -> dict[int, tuple[float, float]]:
    """Return calibrations normalized to node idx keys after validation."""
    if not calibrations:
        return {}

    normalized: dict[int, tuple[float, float]] = {}
    for selector, calib in calibrations.items():
        nodes = tree.get_nodes(selector)
        if len(nodes) != 1:
            raise ToytreeError(
                f"calibration selector {selector!r} matched {len(nodes)} nodes; "
                "selectors must match exactly one internal node."
            )
        node = nodes[0]
        if node.is_leaf():
            raise ToytreeError(
                "tip calibrations are not supported; heterochronous tips are "
                "not implemented."
            )
        if node.idx in normalized:
            raise ToytreeError(
                f"multiple calibration selectors resolve to node {node.idx}."
            )
        normalized[node.idx] = _coerce_calibration_interval(calib)

    for desc_idx, (desc_min, _) in normalized.items():
        for anc in tree[desc_idx].iter_ancestors():
            anc_bounds = normalized.get(anc.idx)
            if anc_bounds is None:
                continue
            if desc_min + dist_floor > anc_bounds[1]:
                raise ToytreeError(
                    "incompatible calibrations: descendant node "
                    f"{desc_idx} minimum age {desc_min} exceeds ancestor node "
                    f"{anc.idx} maximum age {anc_bounds[1]} after enforcing "
                    "positive branch lengths."
                )
    return normalized


def _get_effective_age_bounds(
    tree: ToyTree,
    calibrations: Calibrations,
    dist_floor: float = 1e-12,
) -> tuple[np.ndarray, np.ndarray, set[int]]:
    """Return topology-propagated lower/upper bounds and fixed node indices."""
    active = dict(calibrations)
    if not active:
        active[tree.treenode.idx] = (1.0, 1.0)

    lower = np.zeros(tree.nnodes, dtype=float)
    upper = np.full(tree.nnodes, np.inf, dtype=float)
    fixed: set[int] = set()
    for nidx, (lo, hi) in active.items():
        lower[int(nidx)] = float(lo)
        upper[int(nidx)] = float(hi)
        if np.isclose(lo, hi, atol=0.0, rtol=0.0):
            fixed.add(int(nidx))

    # Minimum feasible ages flow from tips toward the root.
    for node in tree.treenode.traverse("postorder"):
        if node.is_leaf():
            continue
        child_min = max(lower[child.idx] for child in node.children) + dist_floor
        lower[node.idx] = max(lower[node.idx], child_min)

    # Maximum feasible ages flow from calibrated ancestors toward descendants.
    for node in tree.treenode.traverse("preorder"):
        if node.is_root() or node.is_leaf():
            continue
        parent_upper = upper[node.up.idx]
        if np.isfinite(parent_upper):
            upper[node.idx] = min(upper[node.idx], parent_upper - dist_floor)

    for node in tree[tree.ntips :]:
        nidx = node.idx
        lo = float(lower[nidx])
        hi = float(upper[nidx])
        if nidx in fixed:
            requested = float(active[nidx][0])
            tol = max(1e-12, abs(requested) * 1e-12)
            if lo > requested + tol or hi < requested - tol:
                raise ToytreeError(
                    f"infeasible fixed calibration at node {nidx}: age "
                    f"{requested:.6g} conflicts with topology or another calibration."
                )
            lower[nidx] = requested
            upper[nidx] = requested
        elif np.isfinite(hi) and lo >= hi:
            raise ToytreeError(
                f"infeasible calibration interval at node {nidx}: effective "
                f"lower bound {lo:.6g} is not below upper bound {hi:.6g}."
            )
    return lower, upper, fixed


def _raise_invalid_final_ages(
    edges: np.ndarray,
    dists: np.ndarray,
    reason: str,
) -> None:
    """Raise a consistent error for invalid finalized ages."""
    bad = np.where(~np.isfinite(dists) | (dists <= 0))[0]
    if bad.size:
        eidx = int(bad[0])
    else:
        eidx = int(np.argmin(dists))
    child, parent = [int(i) for i in edges[eidx]]
    dist = float(dists[eidx])
    raise ToytreeError(
        "ultrametric fit produced invalid final node ages: "
        f"branch {child}->{parent} has length {dist:.6g}. {reason}"
    )


def _finalize_ultrametric_ages(
    tree: ToyTree,
    ages: np.ndarray,
    calibrations: dict[int, tuple[float, float]] | None = None,
    dist_floor: float = 1e-12,
    negative_tol: float = FINAL_AGE_NEGATIVE_TOL,
) -> np.ndarray:
    """Return finalized ages with tiny topology jitter repaired."""
    ages_hat = np.asarray(ages, dtype=float).copy()
    if np.any(~np.isfinite(ages_hat)):
        raise ToytreeError("ultrametric fit produced non-finite node ages.")

    edges = tree.get_edges("idx")
    children = edges[:, 0]
    parents = edges[:, 1]
    dists = ages_hat[parents] - ages_hat[children]
    min_dist = float(dists.min()) if dists.size else np.inf
    if min_dist < -negative_tol:
        _raise_invalid_final_ages(
            edges,
            dists,
            "This usually indicates incompatible calibrations or optimizer failure.",
        )

    if np.any(dists <= dist_floor):
        # Project small post-fit violations back onto a strictly positive tree.
        for node in tree[tree.ntips :]:
            child_idxs = np.fromiter((i.idx for i in node.children), dtype=int)
            if not child_idxs.size:
                continue
            min_age = np.nextafter(
                float(ages_hat[child_idxs].max()) + dist_floor,
                np.inf,
            )
            if ages_hat[node.idx] < min_age:
                ages_hat[node.idx] = min_age

    if calibrations:
        for nidx, (lo, hi) in calibrations.items():
            age = float(ages_hat[nidx])
            if age < lo - negative_tol or age > hi + negative_tol:
                raise ToytreeError(
                    "ultrametric fit repair would violate calibration bounds at "
                    f"node {nidx}: repaired age {age:.6g} is outside "
                    f"[{lo:.6g}, {hi:.6g}]."
                )

    dists = ages_hat[parents] - ages_hat[children]
    if np.any(~np.isfinite(dists)) or np.any(dists <= dist_floor):
        _raise_invalid_final_ages(
            edges,
            dists,
            "Final age repair could not recover a strictly positive ultrametric tree.",
        )
    return ages_hat


def _encode_age_params(
    ages: np.ndarray,
    ages_idxs: np.ndarray,
    ages_bounds: list[tuple[float, float]],
    children_map: Dict[int, np.ndarray],
    dist_floor: float = 1e-12,
) -> np.ndarray:
    """Encode ages as unconstrained parameters using monotone transforms."""
    params = []
    ages_hat = np.asarray(ages, dtype=float).copy()
    for nidx, (lo, hi) in zip(ages_idxs, ages_bounds):
        child_idxs = children_map.get(int(nidx), np.array([], dtype=int))
        child_max = float(ages_hat[child_idxs].max()) if child_idxs.size else 0.0
        lo_eff = max(float(lo), child_max + dist_floor)
        age = max(float(ages_hat[int(nidx)]), lo_eff + dist_floor)
        if np.isfinite(hi):
            if lo_eff >= float(hi):
                raise ToytreeError(
                    f"cannot encode node {int(nidx)} age: effective lower bound "
                    f"{lo_eff:.6g} is not below upper bound {float(hi):.6g}."
                )
            width = float(hi) - lo_eff
            # Keep the transform materially inside its open interval. A plain
            # machine-epsilon clip is too small: at large optimizer values the
            # sigmoid rounds to one, so a descendant can equal its propagated
            # upper bound and collapse its ancestor's feasible interval.
            absolute_margin = max(
                2.0 * dist_floor,
                8.0 * np.spacing(max(abs(lo_eff), abs(float(hi)), 1.0)),
            )
            fraction_margin = min(0.25, absolute_margin / width)
            p = np.clip(
                (age - lo_eff) / width,
                fraction_margin,
                1.0 - fraction_margin,
            )
            z = float(_logit(np.array([p]))[0])
        else:
            z = float(np.log(max(age - lo_eff, dist_floor)))
        params.append(z)
        ages_hat[int(nidx)] = age
    return np.array(params, dtype=float)


def _decode_age_params(
    age_params: np.ndarray,
    ages_base: np.ndarray,
    ages_idxs: np.ndarray,
    ages_bounds: list[tuple[float, float]],
    children_map: Dict[int, np.ndarray],
    dist_floor: float = 1e-12,
) -> np.ndarray:
    """Decode unconstrained age params to valid ages in postorder."""
    ages_hat = np.asarray(ages_base, dtype=float).copy()
    for z, nidx, (lo, hi) in zip(age_params, ages_idxs, ages_bounds):
        child_idxs = children_map.get(int(nidx), np.array([], dtype=int))
        child_max = float(ages_hat[child_idxs].max()) if child_idxs.size else 0.0
        lo_eff = max(float(lo), child_max + dist_floor)
        if np.isfinite(hi):
            if lo_eff >= float(hi):
                raise ToytreeError(
                    f"cannot decode node {int(nidx)} age: effective lower bound "
                    f"{lo_eff:.6g} is not below upper bound {float(hi):.6g}."
                )
            width = float(hi) - lo_eff
            absolute_margin = max(
                2.0 * dist_floor,
                8.0 * np.spacing(max(abs(lo_eff), abs(float(hi)), 1.0)),
            )
            fraction_margin = min(0.25, absolute_margin / width)
            fraction = float(_sigmoid(np.array([z]))[0])
            fraction = float(
                np.clip(fraction, fraction_margin, 1.0 - fraction_margin)
            )
            age = lo_eff + width * fraction
        else:
            age = lo_eff + float(np.exp(np.clip(z, -700.0, 700.0)))
        ages_hat[int(nidx)] = age
    return ages_hat


def _get_init_ages(
    tree: ToyTree, calibrations: Calibrations, mult: float = 1.5
) -> Tuple[np.ndarray, np.ndarray]:
    """Return an array with starting ages set to internal nodes.

    Note that mult has no effect if root is calibrated. This method
    sets reasonable starting values for internal nodes that can
    accommodate the calibrations of other nodes.

    Parameters
    ----------
    tree: ToyTree
        A tree with edge lengths.
    calibrations: Dict[tuple[float, float]]
        An optional dict of calibrations for one or more nodes as a
        lower and upper bound.
    mult: float
        A root multiplier to help fit starting internal age values.
    """
    edges = tree.get_edges("idx")
    lower, upper, fixed = _get_effective_age_bounds(tree, calibrations)
    active = dict(calibrations)
    if not active:
        active[tree.treenode.idx] = (1.0, 1.0)

    ages = np.zeros(tree.nnodes, dtype=float)
    for node in tree.treenode.traverse("postorder"):
        if node.is_leaf():
            continue
        nidx = node.idx
        child_max = max(float(ages[child.idx]) for child in node.children)
        lo_eff = max(float(lower[nidx]), child_max + 1e-12)
        hi = float(upper[nidx])
        if nidx in fixed:
            age = float(active[nidx][0])
            if age < lo_eff:
                raise ToytreeError(
                    f"fixed calibration at node {nidx} is not older than its children."
                )
        elif np.isfinite(hi):
            if lo_eff >= hi:
                raise ToytreeError(
                    f"cannot initialize node {nidx}: no feasible age interval."
                )
            age = lo_eff + 0.5 * (hi - lo_eff)
        else:
            increment = max(1.0, abs(lo_eff) * max(mult - 1.0, 0.5))
            age = lo_eff + increment
        ages[nidx] = age

    children = edges[:, 0]
    parents = edges[:, 1]
    dists = ages[parents] - ages[children]
    if np.any(dists <= 0.0):
        raise ToytreeError("cannot construct feasible initial node ages.")
    return ages, dists


def _get_params_bounds(
    tree: ToyTree, calibrations: Dict[int, Tuple[float, float]]
) -> Tuple[dict[int, Tuple[float, float]]]:
    """Return a list of tuples of (min, max) for every parameter that must be estimated.

    The num parameters is (2 * ninternal_nodes - 1) = ninodes ages and
    ninodes - 1 rates. For nodes with a fixed age from calibrations the
    age and rate parameters are still estimated, but slightly or highly
    constrained.

    Parameters
    ----------
    tree: ToyTree
        A tree with edge lengths.
    calibrations
        ...
    """
    lower, upper, fixed = _get_effective_age_bounds(tree, calibrations)
    ages_bounds = {
        node.idx: (float(lower[node.idx]), float(upper[node.idx]))
        for node in tree[tree.ntips :]
        if node.idx not in fixed
    }

    # get indices of edge rates that need to be estimated (all)
    rates_bounds = {i: (PARAM_MIN, PARAM_MAX) for i in np.arange(tree.nnodes - 1)}
    return rates_bounds, ages_bounds


def get_tree_with_categorical_rates(ntips: int, nrates: int, seed: int) -> ToyTree:
    """Return a ToyTree with edges scaled by categorical rate variation.

    Rate categories are evenly assigned (linspace) between 1 and 10
    and each edge is randomly assigned to a category. The rate scaler
    for that edge is then sampled from a gamma distribution with
    G(3, RATE) where the alpha=3 sets mean == stderr. Example,
    nrates=2 will generate the rate distributions:
        - G(3, 1)    [mean=3, std=1.73]
        - G(3, 10)   [mean=30, std=17.25]
    """
    import toytree

    rng = np.random.default_rng(seed=seed)
    tree = toytree.rtree.unittree(ntips, seed=123)
    rates = np.linspace(1, 10, nrates)
    for node in tree:
        gidx = rng.choice(nrates)
        node._dist = node._dist * rng.gamma(shape=3, scale=rates[gidx])
    tree._update()
    return tree


def get_tree_with_uncorrelated_rates(
    ntips: int, mean: float = 1.0, sigma: float = 1.0, seed: int = None
) -> ToyTree:
    """Return a ToyTree with edges scaled by uncorrelated relaxed-clock rates.

    A gamma distribution is parameterized with a shape and scale to
    match the desired mean and sigma values, and each branch dist
    value is multiplied by a randomly sampled rate parameter from this
    distribution.

    Rate categories are evenly assigned (linspace) between 1 and 10
    and each edge is randomly assigned to a category. The rate scaler
    for that edge is then sampled from a gamma distribution with
    G(3, RATE).
    """
    import toytree

    rng = np.random.default_rng(seed=seed)
    tree = toytree.rtree.unittree(ntips, seed=123)
    shape = (mean / sigma) ** 2
    scale = sigma**2 / mean
    rates = rng.gamma(shape=shape, scale=scale, size=tree.nnodes)
    for node in tree:
        node._dist = node._dist * rates[node.idx]
    tree._update()
    return tree


def get_tree_with_correlated_rates(
    ntips: int, mean: float = 0.0, sigma: float = 1.0, seed: int = None
) -> ToyTree:
    """Return a ToyTree with edges scaled by correlated relaxed-clock rates.

    A gamma distribution is parameterized with a shape and scale to
    match the desired mean and sigma values, and each branch dist
    value is multiplied by a randomly sampled rate parameter from this
    distribution.

    Rate categories are evenly assigned (linspace) between 1 and 10
    and each edge is randomly assigned to a category. The rate scaler
    for that edge is then sampled from a gamma distribution with
    G(3, RATE).
    """
    import toytree

    rng = np.random.default_rng(seed=seed)
    tree = toytree.rtree.unittree(ntips, seed=123)
    shape = (mean / sigma) ** 2
    scale = sigma**2 / mean
    rates = rng.gamma(shape=shape, scale=scale, size=tree.nnodes)
    for node in tree:
        node._dist = node._dist * rates[node.idx]
    return tree


if __name__ == "__main__":
    rng = np.random.default_rng(123)

    t = get_tree_with_uncorrelated_rates(ntips=50, mean=3, sigma=3)
    t._draw_browser(tmpdir="~")
