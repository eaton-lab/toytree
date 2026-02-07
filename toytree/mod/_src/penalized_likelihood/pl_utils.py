#!/usr/bin/env python

"""General utilities for penalized likehood functions and testing.
"""

from typing import Dict, Tuple
import numpy as np
from loguru import logger
from toytree.core import ToyTree

Calibrations = Dict[int, Tuple[float, float]]
PARAM_MIN = 1e-8
PARAM_MAX = 1e8


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
        logger.debug(f"setting calibration: node {nidx} age to {ages[nidx]}")

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
                logger.debug(f"{path}, nidx={nidx}, cidx={cidx}, pidx={pidx}, nsplits={nsplits}, min_age={min_age:.2f}, max_age={max_age:.2f} | set {nidx} to {ages[nidx]:.2f}")

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
    """Return a list of tuples of (min, max) for every parameter that
    must be estimated.

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
