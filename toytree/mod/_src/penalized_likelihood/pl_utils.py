#!/usr/bin/env python

"""General utilities for penalized likehood functions and testing."""

from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Callable, Dict, Tuple

import numpy as np
from loguru import logger

from toytree.core import ToyTree

Calibrations = Dict[int, Tuple[float, float]]
PARAM_MIN = 1e-8
PARAM_MAX = 1e8


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
            fut_to_start = {pool.submit(worker, payload): int(payload.get("start", -1)) for payload in payloads}
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
        logger.warning(f"ProcessPool unavailable; falling back to serial multistart: {exc}")
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
    return 1.0 / (1.0 + np.exp(-x))


def _logit(p: np.ndarray) -> np.ndarray:
    return np.log(p / (1.0 - p))


def _age_has_upper(lo: float, hi: float, dist_floor: float, age_upper_switch: float) -> bool:
    return np.isfinite(hi) and (hi < age_upper_switch) and (hi > lo + dist_floor)


def _encode_age_params(
    ages: np.ndarray,
    ages_idxs: np.ndarray,
    ages_bounds: list[tuple[float, float]],
    children_map: Dict[int, np.ndarray],
    dist_floor: float = 1e-12,
    age_upper_switch: float = 1e6,
) -> np.ndarray:
    """Encode ages as unconstrained parameters using monotone transforms."""
    params = []
    ages_hat = np.asarray(ages, dtype=float).copy()
    for nidx, (lo, hi) in zip(ages_idxs, ages_bounds):
        child_idxs = children_map.get(int(nidx), np.array([], dtype=int))
        child_max = float(ages_hat[child_idxs].max()) if child_idxs.size else 0.0
        lo_eff = max(float(lo), child_max + dist_floor)
        age = max(float(ages_hat[int(nidx)]), lo_eff + dist_floor)
        if _age_has_upper(lo_eff, float(hi), dist_floor, age_upper_switch):
            p = np.clip((age - lo_eff) / (float(hi) - lo_eff), 1e-8, 1 - 1e-8)
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
    age_upper_switch: float = 1e6,
) -> np.ndarray:
    """Decode unconstrained age params to valid ages in postorder."""
    ages_hat = np.asarray(ages_base, dtype=float).copy()
    for z, nidx, (lo, hi) in zip(age_params, ages_idxs, ages_bounds):
        child_idxs = children_map.get(int(nidx), np.array([], dtype=int))
        child_max = float(ages_hat[child_idxs].max()) if child_idxs.size else 0.0
        lo_eff = max(float(lo), child_max + dist_floor)
        if _age_has_upper(lo_eff, float(hi), dist_floor, age_upper_switch):
            age = lo_eff + (float(hi) - lo_eff) * float(_sigmoid(np.array([z]))[0])
        else:
            age = lo_eff + float(np.exp(z))
        ages_hat[int(nidx)] = age
    return ages_hat


def _get_init_ages(tree: ToyTree, calibrations: Calibrations, mult: float = 1.5) -> Tuple[np.ndarray, np.ndarray]:
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
    # get edge idx array
    edges = tree.get_edges("idx")

    # get array with tips at zero and internal at nan
    ages = np.zeros(tree.nnodes)
    ages[tree.ntips:] = np.nan

    # set internal nodes to their calibration midpoints
    if not calibrations:
        calibrations = {tree[-1].idx: (1., 1.)}
    for nidx, calib in calibrations.items():
        if isinstance(calib, (float, int)):
            calib = (float(calib), float(calib))
        span = calib[1] - calib[0]
        ages[nidx] = calib[0] + span / 2.
        # logger.debug(f"setting calibration: node {nidx} age to {ages[nidx]}")

    # set root age (if not calibrated) to mult of max internal age
    if np.isnan(ages[-1]):
        ages[-1] = mult * max(ages[:-1])

    # sort edge paths (e.g., (node, node.up, node.up.up)) so that
    # the paths with more calibrations are done first, and when tied,
    # the longer path is selected first.
    paths = [i.iter_ancestors(include_self=True) for i in tree[:tree.ntips]]
    paths = [tuple(i._idx for i in j) for j in paths]
    spaths = sorted(
        paths,
        key=lambda x: (np.sum(~np.isnan([ages[i] for i in x])), len),
        reverse=True,
    )

    # iterate over path to set init age of nodes, e.g., [(5, 9, 10), (4, 7, 9, 10), ...]
    for path in spaths:
        for nidx in path[::-1]:
            idx = path.index(nidx)
            age = ages[nidx]
            if np.isnan(age):
                # get age of first calibrated ancestor
                idx_p = path.index(nidx) + 1
                pidx = path[idx_p]
                idx_c = np.nanargmax([ages[i] for i in path[:idx]])
                cidx = path[idx_c]
                max_age = ages[pidx]
                min_age = ages[cidx]
                # number of nodes between cidx and pidx
                nsplits = idx_p - idx_c

                # divide span into nnodes on path intervals
                span = max_age - min_age
                ages[nidx] = max_age - span / nsplits
                # logger.debug(f"{path}, nidx={nidx}, cidx={cidx}, pidx={pidx}, nsplits={nsplits}, min_age={min_age:.2f}, max_age={max_age:.2f} | set {nidx} to {ages[nidx]:.2f}")

    # get age edge lengths
    children = edges[:, 0]
    parents = edges[:, 1]
    dists = ages[parents] - ages[children]

    # success, return results
    if all(dists >= 0):
        return ages, dists
    if mult > 100:
        raise Exception("cannot find good starting values")
    return _get_init_ages(tree, calibrations, mult * 1.5)


def _get_params_bounds(tree: ToyTree, calibrations: Dict[int, Tuple[float, float]]) -> Tuple[dict[int, Tuple[float, float]]]:
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
    # if no calibrations set the treenode to 1.
    if not calibrations:
        calibrations = {tree[-1].idx: (1., 1.)}

    # set bounds for all internal nodes to min,max
    ages_bounds = {}
    for node in tree[tree.ntips:]:
        ages_bounds[node._idx] = (PARAM_MIN, PARAM_MAX)

    # set stricter bounds on calibrated nodes, unless fixed age, then remove.
    fixed = []
    for selector, calib in calibrations.items():
        node = tree.get_nodes(selector)[0]
        nidx = node._idx
        if isinstance(calib, (float, int)):
            calib = (float(calib), float(calib))
        cmin, cmax = calib
        if cmin != cmax:
            ages_bounds[nidx] = (cmin, cmax)
        else:
            fixed.append(nidx)
    ages_bounds = {i: j for (i, j) in ages_bounds.items() if i not in fixed}

    # get indices of edge rates that need to be estimated (all)
    rates_bounds = {i: (PARAM_MIN, PARAM_MAX) for i in np.arange(tree.nnodes - 1)}
    return rates_bounds, ages_bounds


def get_tree_with_categorical_rates(ntips: int, nrates: int, seed: int) -> ToyTree:
    """Return a ToyTree with edge dists scaled to reflect randomly
    assigned categorical rate variation.

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


def get_tree_with_uncorrelated_relaxed_rates(ntips: int, mean: float=1.0, sigma: float=1.0, seed: int=None) -> ToyTree:
    """Return a ToyTree with edge dists scaled to reflect uncorrelated
    relaxed clock rates.

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
    scale = sigma ** 2 / mean
    rates = rng.gamma(shape=shape, scale=scale, size=tree.nnodes)
    for node in tree:
        node._dist = node._dist * rates[node.idx]
    tree._update()
    return tree


def get_tree_with_correlated_relaxed_rates(ntips: int, mean: float=0.0, sigma: float=1.0, seed: int=None) -> ToyTree:
    """Return a ToyTree with edge dists scaled to reflect uncorrelated
    relaxed clock rates.

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
    scale = sigma ** 2 / mean
    rates = rng.gamma(shape=shape, scale=scale, size=tree.nnodes)
    for node in tree:
        node._dist = node._dist * rates[node.idx]
    return tree



if __name__ == "__main__":

    rng = np.random.default_rng(123)

    t = get_tree_with_uncorrelated_relaxed_rates(ntips=50, mean=3, sigma=3)
    t._draw_browser(tmpdir="~")
