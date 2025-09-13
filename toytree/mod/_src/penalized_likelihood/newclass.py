#!/usr/bin/env python

"""Penalized likelihood classes

Optimization Notes
------------------
Convergence sometimes requires better starting ages. Implement an 
option to try multiple different starting values generated under diff
models. Also try different models ("relaxed", "discrete", ...), and
adjust the tolerance and max-iter for convergence. Also it is best
to avoid zero branch lengths. If you set lambda try diff values.

Models
------
clock
    A single rate is estimated.
discrete
    Each branch rate can be from a different distribution (up to nedges
    rate distributions). When ncategories=1 this is equal to the fixed
    clock model. The conditional probability of each branch belonging
    to each rate category is calculated and used to calculate the 
    log-likelihood as a weighted mean across categories.
correlated
    ...
    Here we define a gradient (Jabobian) argument when optimizing...
    ...
relaxed
    ...
    Here we define a gradient (Jabobian) argument when optimizing...
    ...

Notes on model fitting
----------------------
Given an input non-ultrametric tree with edges as rate x time, the 
edges will be scaled so that tips align at zero and internal nodes are
equally spaced (init_ages), and the rates will be estimated from the
new edges lengths compared to their initial lengths (init_rates). We
then perform a bounded maximum likelihood optimization in scipy using
the L-BFGS-B algorithm. A rate is estimated for every edge on the tree,
and ages are estimated for all nodes that are not fixed by an exact
calibration. Bounds are set between a global min and max for each 
parameter, except calibrated node ages, which can be further 
constrained.

Methods
--------
- make_ultrametric()                  # implements all models and returns best fit result.
- make_ultrametric_pl_clock()
- make_ultrametric_pl_discrete()
- make_ultrametric_pl_correlated()
- make_ultrametric_pl_relaxed()
- TODO: make_ultrametric_pl_lasso()   # minimize the L1 penalty
- TODO: make_ultrametric_pl_ridge()   # minimize the L2 norm
- TODO: make_ultrametric_pl_elastic() # minimize L1 + L2
- TODO: make_ultrametric_pl_bayes()   # Bayesian regularization

Examples
--------
>>> tree = toytree.rtree.rtree(ntips=20, seed=123)
>>> utree = toytree.mod.make_ultrametric(tree, model="clock")
>>> toytree.mtree([tree, utree]).draw(ts='o')

References
----------
Kim, J. and Sanderson, M. J. (2008) Penalized likelihood phylogenetic
inference: bridging the parsimony-likelihood gap. Systematic Biology,
*57*, 665-674.

Paradis, E. (2013) Molecular dating of phylogenies by likelihood 
methods: a comparison of models and a new information criterion. 
Molecular Phylogenetics and Evolution, *67*, 436-444.

Sanderson, M. J. (2002) Estimating absolute rates of molecular 
evolution and divergence times: a penalized likelihood approach.
Molecular Biology and Evolution, *19*, 101-109.

http://blog.phytools.org/2024/07/obtaining-time-calibrated-ultrametric.html

TODO
-----
- can we set non-zero calibrations on tip nodes?
    Either yes, or we can stick in a unary node that extends to 0.
- find edge cases of conflicting calibrations
- test edge cases of non bifurcating trees
- could be [if available] numba-fied
"""

from typing import Dict, Tuple, Any, Union
from itertools import cycle
from loguru import logger
import numpy as np
import scipy.stats as stats
from scipy.optimize import minimize
from scipy.special import factorial
from toytree.core import ToyTree

logger = logger.bind(name="toytree")
Calibrations = Dict[int, Tuple[float, float]]
PARAM_MIN = 1e-8
PARAM_MAX = 1e8

__all__ = [
    "edges_make_ultrametric_pl_clock",
    "edges_make_ultrametric_pl_discrete",
    "edges_make_ultrametric_pl_relaxed"
    # "edges_make_ultrametric_pl_uncorrelated"
]


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


# NOT CURRENTLY USED
def _get_mean_rooted_path_distance(tree) -> float:
    """Return the mena distance between tips on either side of the treenode.
    """
    import itertools
    mat = tree.distance.get_tip_distance_matrix()
    tips_l = tree.treenode.children[0].get_leaves()
    tips_r = tree.treenode.children[1].get_leaves()
    return np.mean([mat[i._idx, j._idx] for i, j in itertools.product(tips_l, tips_r)])


def edges_make_ultrametric_pl_clock(
    tree: ToyTree,
    calibrations: Calibrations = {},
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 1e5,
    max_fun: int = 1e5,
    max_refine: int = 20,
) -> Union[ToyTree, dict[str, Any]]:
    """Return a tree made ultrametric under a molecular clock.

    Edges are scaled while assuming a molecular clock with a single 
    rate that is estimated.

    Parameters
    ----------
    tree: 
        A ToyTree with non-ultrametric edge lengths.
    calibrations: dict[int, (float, float)]
        A dict mapping node selectors (e.g., idx labels) to calibrated
        ages as a single value or a tuple of (min, max) age.
    full: bool
        If full=True a dictionary is returned with the modified tree,
        log-likelihood score, and PHIIC score.
    inplace: bool
        If True the tree is modified in-place and returned, else a
        copy is returned.
    max_iter: int
        Max number of iterations for optimization.
    max_fun: int
        Max number of function calls for optimization.
    max_refine: int
        Number of iterative refining steps performed to alternately fit
        model rates while keeping ages fixed, or vice-versa, to search
        for improvements on the joint fit model.

    Returns
    -------
    ToyTree
        The default return is a ToyTree with node dist values scaled
        so that the tree is ultrametric. If inplace=True this 
        overwrites the original tree and the returned tree does not 
        need to be stored.
    dict
        An alternative option to return a dict with the new scaled tree
        as well as statistics on the model fit including likelihood, 
        PHIIC, and rate.
    """
    # get init and fixed node ages that make tree ultrametric
    ages_init, _ = _get_init_ages(tree, calibrations)

    # get bounds on params that need to be inferred; are not fixed
    rates_bounds, ages_bounds = _get_params_bounds(tree, calibrations)

    # get edges, dists and log-factorial-dists from rate-x-time edges
    edges = tree.get_edges("idx")
    dists_o = tree.get_node_data("dist").values[:-1]
    dists_lf = np.log(factorial(dists_o))
    edata = np.vstack([dists_o, dists_lf]).T

    # get starting rate in clock model as old/new treenode height
    rate_init = tree.treenode.height / ages_init[-1]

    # get indices of which node ages will be estimated
    ages_idxs = np.array(sorted(ages_bounds))

    # slim bounds to only those needing to be estimated
    ages_bounds = [ages_bounds[i] for i in ages_idxs]
    bounds = [rates_bounds[0]] + ages_bounds
    params = np.hstack([rate_init, ages_init[ages_idxs]])

    # get loglik at a valid starting params to scale neg dist penalty
    valid_loglik = log_likelihood_poisson(rate_init, ages_init, edges, edata, None)

    # get clock model log-likelihood
    fit = minimize(
        fun=objective_clock,
        x0=params,
        args=(False, False, rate_init, ages_init, ages_idxs, edges, edata, valid_loglik),
        method="L-BFGS-B",
        bounds=bounds,
        options=dict(maxiter=int(max_iter), maxfun=int(max_fun))
    )
    # log success/fail report
    if not fit.success:
        logger.warning(f"Failed to converge. Consider increasing max_iter & max_fun:\n{fit}")
    else:
        logger.debug(f"Initial fit loglik={-fit.fun}")

   # iterative optimization while alternately fixing rates or ages
    current_loglik = fit.fun
    current_params = fit.x
    iter_refine = 0

    # dict mapping fixed param type to fixed bool selector, and param subset slice
    fix_dict = {
        "rates": [(False, True), slice(None, 1)],
        "ages": [(True, False), slice(1, None)],
    }

    # iterator to cycle through this dict infinitely
    iter_fixed = cycle(fix_dict)

    # loop to optimize one param type at a time
    while 1:

        # get a fixed param and its info
        fixed = next(iter_fixed)
        fbools, fslice = fix_dict[fixed]

        # update params from current accepted values
        rates_hat = current_params[:1]
        ages_hat = ages_init.copy()
        ages_hat[ages_idxs] = current_params[1:]

        # optimize the subset of non-fixed params
        args = fbools + (rates_hat, ages_hat, ages_idxs, edges, edata, valid_loglik)
        ifit = minimize(
            fun=objective_clock,
            x0=current_params[fslice],
            args=args,
            method="L-BFGS-B",
            bounds=bounds[fslice],
            options=dict(maxiter=int(max_iter), maxfun=int(max_fun))
        )

        # if improvement is negative and abs() > 1e-9 then accept
        Δ_loglik = ifit.fun - current_loglik
        if Δ_loglik <= 0:
            current_loglik = ifit.fun
            current_params[fslice] = ifit.x
            logger.debug(f"fixed {fixed:<5} loglik={-current_loglik}; Δloglik={Δ_loglik}")
            if abs(Δ_loglik) < 1e-9:
                fit = ifit
                break

        # break on max_refine
        iter_refine += 1
        if iter_refine > max_refine:
            break

    # transform tree with new ages
    ages = ages_init.copy()
    ages[ages_idxs] = current_params[1:]
    tree = tree.set_node_data("height", ages, inplace=inplace)
    rate = current_params[0]

    # Final fit for PHIIC calculation (Penalized Hierarchical Information Criterion)
    loglik = log_likelihood_poisson(rate, ages, edges, edata, valid_loglik)
    k = len(bounds)
    PHIIC = -2 * loglik + 2 * k

    # return as a tree or a dict
    if not full:
        return tree
    return {"loglik": loglik, "PHIIC": PHIIC, "rate": rate, "tree": tree, "converged": fit.success}


def edges_make_ultrametric_pl_discrete(
    tree: ToyTree,
    ncategories: int,
    calibrations: Calibrations = {},
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 1e5,
    max_fun: int = 1e5,
    max_refine: int = 20,
) -> Union[ToyTree, dict[str, Any]]:
    """Return a tree made ultrametric under a discrete model with N
    rate categories under penalized likelihood.

    Edges are scaled while assuming a edge rates are drawn from N 
    discrete distributions. The number of parameters in this model is
    n_categories rates + n_non_fixed_nodes ages + n_categories - 1
    frequencies (weights). A rate is estimated for each category and
    weights are also fit to assign the path lengths from tip to root
    for all edges as a proportion to each rate.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree with non-ultrametric edge lengths.
    ncategories: int
        The number of discrete rate categories. If greater than the
        number of edges it is set to nedges.
    calibrations: dict[int, (float, float)]
        A dict mapping node selectors (e.g., idx labels) to calibrated
        ages as a single value or a tuple of (min, max) age.
    full: bool
        If full=True a dictionary is returned with the modified tree,
        log-likelihood score, and PHIIC score.
    inplace: bool
        If True the tree is modified in-place and returned, else a
        copy is returned.
    max_iter: int
        Max number of iterations for optimization.
    max_fun: int
        Max number of function calls for optimization.
    max_refine: int
        Number of iterative refining steps performed to alternately fit
        model rates while keeping ages fixed, or vice-versa, to search
        for improvements on the joint fit model.

    Returns
    -------
    ToyTree
        The default return is a ToyTree with node dist values scaled
        so that the tree is ultrametric. If inplace=True this 
        overwrites the original tree and the returned tree does not 
        need to be stored.
    dict
        An alternative option to return a dict with the new scaled tree
        as well as statistics on the model fit including likelihood, 
        PHIIC, and rate.

    Example
    -------
    >>> # create tree with edge rates from two discrete rates
    >>> rng = np.random.default_rng(seed=123)
    >>> tree = toytree.rtree.unittree(25, seed=123)
    >>> for node in tree:
    >>>     if rng.binomial(n=1, p=0.5):
    >>>         node._dist = node._dist * rng.gamma(shape=3, scale=1.0)
    >>>     else:
    >>>         node._dist = node._dist * rng.gamma(shape=3, scale=5.0)
    >>> tree.mod.edges_make_ultrametric_pl_discrete(tree, 2, full=True)
    >>> # {'loglik': -82.42541, 'PHIIC': 216.85082, 'rates': [4.12272, 17.56474], 'freqs': [0.53751, 0.46248], 'tree': <toytree.ToyTree at 0x791451cb5190>, 'converged': True}

    """
    # ncategories cannot exceed number of edges
    ncategories = min(ncategories, tree.nedges)

    # get init and fixed node ages that make tree ultrametric
    ages_init, dists_init = _get_init_ages(tree, calibrations)

    # get bounds on params that need to be inferred; are not fixed
    rates_bounds, ages_bounds = _get_params_bounds(tree, calibrations)

    # get edges, dists and log-factorial-dists from rate-x-time edges
    edges = tree.get_edges("idx")
    dists_o = tree.get_node_data("dist").values[:-1]
    dists_lf = np.log(factorial(dists_o))
    edata = np.vstack([dists_o, dists_lf]).T

    # get starting rates as old/new edge dists. Then bin the rates into
    # ncategories, as we will infer N rates and assign edges to bins.
    rates_init = dists_o / (ages_init[edges[:, 1]] - ages_init[edges[:, 0]])
    _div = 1 / (2 * ncategories)
    _cats = np.linspace(_div, 1 - _div, ncategories)
    rates_init = np.quantile(rates_init, _cats)

    # get initial freqs (weights) of assignment of edges to categories
    freqs_init = np.repeat(1 / ncategories, ncategories - 1)

    # get indices of which node ages will be estimated
    ages_idxs = np.array(sorted(ages_bounds))

    # slim bounds to only those needing to be estimated
    ages_bounds = [ages_bounds[i] for i in ages_idxs]
    rates_bounds = [rates_bounds[i] for i in range(ncategories)]
    freqs_bounds = [(0, 1) for i in range(ncategories - 1)]
    bounds = rates_bounds + ages_bounds + freqs_bounds

    # get loglik at a valid starting params to scale neg dist penalty
    _freqs_hat = np.append(freqs_init, 1 - freqs_init.sum())    
    valid_loglik = log_likelihood_poisson_discrete(rates_init, ages_init, edges, edata, _freqs_hat, None)

    # fit joint model
    params = np.hstack([rates_init, ages_init[ages_idxs], freqs_init])
    fit = minimize(
        fun=objective_discrete,
        x0=params,
        args=(False, False, False, rates_init, ages_init, ages_idxs, edges, edata, freqs_init, valid_loglik),
        method="L-BFGS-B",
        bounds=bounds,
        options=dict(maxiter=int(max_iter), maxfun=int(max_fun))
    )
    # log success/fail report
    if not fit.success:
        logger.warning(f"Failed to converge. Consider increasing max_iter & max_fun, or reducing ncategories.\n{fit}")
    else:
        logger.debug(f"Initial fit loglik={-fit.fun}")

    # iterative optimization while alternately fixing rates or ages
    current_loglik = fit.fun
    current_params = fit.x
    iter_refine = 0
    rsize = rates_init.size
    asize = ages_idxs.size
    fsize = freqs_init.size

    # dict mapping fixed param type to fixed bool selector, and param subset slice
    fix_dict = {
        "rates": [(False, True, True), slice(None, rsize)],
        "ages": [(True, False, True), slice(rsize, rsize + asize)],
        "freqs": [(True, True, False), slice(-fsize, None)],
    }

    # iterator to cycle through this dict infinitely
    iter_fixed = cycle(fix_dict)

    # loop to optimize one param type at a time until no further improvement
    # or the max_refine number is reached.
    while 1:

        # get a fixed param and its info
        fixed = next(iter_fixed)
        fbools, fslice = fix_dict[fixed]

        # update params from current accepted values
        rates_hat = current_params[:rsize]
        ages_hat = ages_init.copy()
        ages_hat[ages_idxs] = current_params[rsize:rsize + asize]
        freqs_hat = current_params[-fsize:]

        # optimize the subset of non-fixed params
        args = fbools + (rates_hat, ages_hat, ages_idxs, edges, edata, freqs_hat, valid_loglik)
        ifit = minimize(
            fun=objective_discrete,
            x0=current_params[fslice],
            args=args,
            method="L-BFGS-B",
            bounds=bounds[fslice],
            options=dict(maxiter=int(max_iter), maxfun=int(max_fun))
        )

        # if improvement is negative and abs() > 1e-9 then accept
        Δ_loglik = ifit.fun - current_loglik
        if Δ_loglik <= 0:
            current_loglik = ifit.fun
            current_params[fslice] = ifit.x
            logger.debug(f"fixed {fixed:<5} loglik={-current_loglik}; Δloglik={Δ_loglik}")
            if abs(Δ_loglik) < 1e-9:
                fit = ifit
                break

        # break on max_refine
        iter_refine += 1
        if iter_refine > max_refine:
            break

    # transform tree with new ages
    ages = ages_init.copy()
    ages[ages_idxs] = current_params[rsize:rsize + asize]
    tree = tree.set_node_data("height", ages, inplace=inplace)

    # get rates and freqs params
    rates = current_params[:rsize]
    freqs = current_params[-fsize:]

    # Final fit for PHIIC calculation (Penalized Hierarchical Information Criterion)
    _freqs = np.append(freqs, 1. - freqs.sum())
    loglik = log_likelihood_poisson_discrete(rates, ages, edges, edata, _freqs, valid_loglik)
    k = len(bounds)
    PHIIC = -2 * loglik + 2 * k

    # return as a tree or a dict
    if not full:
        return tree
    return {"loglik": loglik, "PHIIC": PHIIC, "rates": list(rates), "freqs": list(_freqs), "tree": tree, "converged": fit.success}


def edges_make_ultrametric_pl_relaxed(
    tree: ToyTree,
    lam: float,
    calibrations: Calibrations = {},
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 1e5,
    max_fun: int = 1e5,
    max_refine: int = 20,
) -> Union[ToyTree, dict[str, Any]]:
    """Return a tree made ultrametric under a relaxed clock model with
    rate variation among edges under penalized likelihood.

    Edges are scaled while assuming ...

    Parameters
    ----------
    tree: ToyTree
        A ToyTree with non-ultrametric edge lengths.
    lam: float
        Lambda rate variation penalty parameter of Sanderson's
        relaxed model. Lower values allow less rate variation.
    calibrations: dict[int, (float, float)]
        A dict mapping node selectors (e.g., idx labels) to calibrated
        ages as a single value or a tuple of (min, max) age.
    full: bool
        If full=True a dictionary is returned with the modified tree,
        log-likelihood score, and PHIIC score.
    inplace: bool
        If True the tree is modified in-place and returned, else a
        copy is returned.
    max_iter: int
        Max number of iterations for optimization.
    max_fun: int
        Max number of function calls for optimization.
    max_refine: int
        Number of iterative refining steps performed to alternately fit
        model rates while keeping ages fixed, or vice-versa, to search
        for improvements on the joint fit model.

    Returns
    -------
    ToyTree
        The default return is a ToyTree with node dist values scaled
        so that the tree is ultrametric. If inplace=True this
        overwrites the original tree and the returned tree does not
        need to be stored.
    dict
        An alternative option to return a dict with the new scaled tree
        as well as statistics on the model fit including likelihood,
        PHIIC, and rate.

    Example
    -------
    >>> # create tree with edge rates from two discrete rates
    >>> rng = np.random.default_rng(seed=123)
    >>> tree = toytree.rtree.unittree(25, seed=123)
    >>> for node in tree:
    >>>     if rng.binomial(n=1, p=0.5):
    >>>         node._dist = node._dist * rng.gamma(shape=3, scale=1.0)
    >>>     else:
    >>>         node._dist = node._dist * rng.gamma(shape=3, scale=5.0)
    >>> tree.mod.edges_make_ultrametric_pl_discrete(tree, 2, full=True)
    >>> # {'loglik': -82.42541, 'PHIIC': 216.85082, 'rates': [4.12272, 17.56474], 'freqs': [0.53751, 0.46248], 'tree': <toytree.ToyTree at 0x791451cb5190>, 'converged': True}
    """
    # get init and fixed node ages that make tree ultrametric
    ages_init, dists_init = _get_init_ages(tree, calibrations)

    # get bounds on params that need to be inferred; are not fixed
    rates_bounds, ages_bounds = _get_params_bounds(tree, calibrations)

    # get edges, dists and log-factorial-dists from rate-x-time edges
    edges = tree.get_edges("idx")
    dists_o = tree.get_node_data("dist").values[:-1]
    dists_lf = np.log(factorial(dists_o))
    edata = np.vstack([dists_o, dists_lf]).T

    # get starting rates as old/new edge dists.
    rates_init = dists_o / (ages_init[edges[:, 1]] - ages_init[edges[:, 0]])

    # get indices of which node ages will be estimated
    ages_idxs = np.array(sorted(ages_bounds))

    # gradient incidence matrices for relaxed model
    mat_a = np.array([edges[:, 1] == i for i in ages_idxs])
    mat_d = np.array([edges[:, 0] == i for i in ages_idxs])

    # slim bounds to only those needing to be estimated
    ages_bounds = [ages_bounds[i] for i in ages_idxs]
    bounds = rates_bounds + ages_bounds

    # get loglik at a valid starting params to scale neg dist penalty
    valid_loglik = log_likelihood_poisson_relaxed(rates_init, ages_init, edges, edata, None)

    # fit joint model
    params = np.hstack([rates_init, ages_init[ages_idxs]])
    fit = minimize(
        fun=objective_relaxed,
        x0=params,
        args=(False, False, rates_init, ages_init, ages_idxs, edges, edata, valid_loglik),
        method="L-BFGS-B",
        bounds=bounds,
        options=dict(maxiter=int(max_iter), maxfun=int(max_fun))
    )
    # log success/fail report
    if not fit.success:
        logger.warning(f"Failed to converge. Consider increasing max_iter & max_fun:\n{fit}")
    else:
        logger.debug(f"Initial fit loglik={-fit.fun}")

    # iterative optimization while alternately fixing rates or ages
    current_loglik = fit.fun
    current_params = fit.x
    iter_refine = 0
    rsize = rates_init.size
    asize = ages_idxs.size

    # dict mapping fixed param type to fixed bool selector, and param subset slice
    fix_dict = {
        "rates": [(False, True, True), slice(None, rsize)],
        "ages": [(True, False, True), slice(rsize, rsize + asize)],
    }

    # iterator to cycle through this dict infinitely
    iter_fixed = cycle(fix_dict)

    # loop to optimize one param type at a time until no further improvement
    # or the max_refine number is reached.
    while 1:

        # get a fixed param and its info
        fixed = next(iter_fixed)
        fbools, fslice = fix_dict[fixed]

        # update params from current accepted values
        rates_hat = current_params[:rsize]
        ages_hat = ages_init.copy()
        ages_hat[ages_idxs] = current_params[rsize:rsize + asize]

        # optimize the subset of non-fixed params
        args = fbools + (rates_hat, ages_hat, ages_idxs, edges, edata, valid_loglik)
        ifit = minimize(
            fun=objective_discrete,
            x0=current_params[fslice],
            args=args,
            method="L-BFGS-B",
            bounds=bounds[fslice],
            options=dict(maxiter=int(max_iter), maxfun=int(max_fun))
        )

        # if improvement is negative and abs() > 1e-9 then accept
        Δ_loglik = ifit.fun - current_loglik
        if Δ_loglik <= 0:
            current_loglik = ifit.fun
            current_params[fslice] = ifit.x
            logger.debug(f"fixed {fixed:<5} loglik={-current_loglik}; Δloglik={Δ_loglik}")
            if abs(Δ_loglik) < 1e-9:
                fit = ifit
                break

        # break on max_refine
        iter_refine += 1
        if iter_refine > max_refine:
            break

    # transform tree with new ages
    ages = ages_init.copy()
    ages[ages_idxs] = current_params[rsize:rsize + asize]
    tree = tree.set_node_data("height", ages, inplace=inplace)

    # get rates and freqs params
    rates = current_params[:rsize]

    # Final fit for PHIIC calculation (Penalized Hierarchical Information Criterion)
    loglik = log_likelihood_poisson_discrete(rates, ages, edges, edata, valid_loglik)
    k = len(bounds)
    PHIIC = -2 * loglik + 2 * k

    # return as a tree or a dict
    if not full:
        return tree
    return {"loglik": loglik, "PHIIC": PHIIC, "rates": list(rates), "tree": tree, "converged": fit.success}



def objective_clock(params, fixed_rate, fixed_ages, rate, ages, ages_idxs, edges, edata, valid_loglik):
    """Return neg log-likelihood under clock model."""
    # [AGES] optimize ages while keeping rate fixed
    if fixed_rate and not fixed_ages:
        assert params.size == ages_idxs.size
        rate_hat = rate
        ages_hat = ages.copy()
        ages_hat[ages_idxs] = params
    # [RATE] optimize rate while keeping ages fixed
    elif fixed_ages and not fixed_rate:
        assert params.size == 1
        ages_hat = ages
        rate_hat = params
    # joint optimize rate and ages
    else:
        assert params.size == ages_idxs.size + 1
        rate_hat = params[:1]
        ages_hat = ages.copy()
        ages_hat[ages_idxs] = params[1:]
    return -log_likelihood_poisson(rate_hat, ages_hat, edges, edata, valid_loglik)


def log_likelihood_poisson(rates_hat, ages_hat, edges, edata, valid_loglik) -> float:
    """Return the log-likelihood of the rates x ages params"""
    # get dists given the new age estimates
    dists_hat = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]

    # return high penalty as 2 x valid_loglik from starting params.
    if any(dists_hat < 0):
        return 2 * valid_loglik

    # get product of dists(time) and rates
    pdists = dists_hat * rates_hat

    # calculate loglik
    loglik = np.sum(edata[:, 0] * np.log(pdists) - pdists - edata[:, 1])
    return loglik


def objective_discrete(params, fixed_rates, fixed_ages, fixed_freqs, rates, ages, ages_idxs, edges, edata, freqs, valid_loglik):
    """Return neg log-likelihood under discrete model.
    """
    # [RATES]
    if fixed_ages and fixed_freqs and not fixed_rates:
        assert params.size == rates.size
        ages_hat = ages
        rates_hat = params
        freqs_hat = freqs
    # [AGES]
    elif fixed_rates and fixed_freqs and not fixed_ages:
        assert params.size == ages_idxs.size
        rates_hat = rates
        ages_hat = ages.copy()
        ages_hat[ages_idxs] = params
        freqs_hat = freqs        
    # [FREQS]
    elif fixed_rates and fixed_ages and not fixed_freqs:
        assert params.size == freqs.size
        ages_hat = ages
        rates_hat = rates
        freqs_hat = params
    else:
        assert params.size == ages_idxs.size + rates.size + freqs.size 
        rates_hat = params[:rates.size]
        ages_hat = ages.copy()
        ages_hat[ages_idxs] = params[rates.size:rates.size + ages_idxs.size]
        freqs_hat = params[-freqs.size:]

    # add final freq category for the remainder
    freqs_hat = np.append(freqs_hat, 1. - freqs_hat.sum())

    # calculate log-likelihood
    args = (rates_hat, ages_hat, edges, edata, freqs_hat, valid_loglik)
    return -log_likelihood_poisson_discrete(*args)


def log_likelihood_poisson_discrete(rates_hat, ages_hat, edges, edata, freqs_hat, valid_loglik) -> float:
    """Return the log-likelihood of the rates x ages params"""
    # get dists given the new age estimates
    dists_hat = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]

    # return high penalty as 2 x valid_loglik from starting params.
    if any(dists_hat < 0):
        return 2 * valid_loglik
    if sum(freqs_hat) > 1:
        return 2 * valid_loglik
    # NB: for some reason this still gets searched sometimes despite bounds (0, 1)
    if any(freqs_hat < 0):
        return 2 * valid_loglik

    # get product of dists(time) and rates
    pdists = dists_hat * rates_hat[:, np.newaxis]

    # calculate loglik
    prob = np.exp(edata[:, 0] * np.log(pdists) - pdists - edata[:, 1])

    # multiply each by its weight in each category
    loglik = np.sum(np.log(prob.T @ freqs_hat))
    return loglik


def objective_relaxed(params, fixed_rates, fixed_ages, rates, ages, ages_idxs, edges, edata, lam, valid_loglik) -> float:
    """..."""


def log_likelihood_poisson_relaxed() -> float:
    # get likelihood of model parameters
    loglik = log_likelihood_poisson(rates, ages, edges, edata, valid_loglik)

    # get penalty under relaxed lambda weighting
    mu = np.mean(rates)
    return loglik - lamb * sum(...)


def objective_relaxed():
    pass


def gradient_poisson(ages, rates, edges, einfo, mat_a, mat_d):
    """Gradient function for the Poisson component."""
    # get edge lengths between node ages
    age_lens = ages[edges[:, 0]] - ages[edges[:, 1]]

    # gradient for the rates
    rates_gr = (einfo[:, 0] / rates) - age_lens

    # gradient for the dates
    inner = (einfo[:, 0] / age_lens) - rates
    dates_gr = np.sum((inner * mat_a) - (inner * mat_d), axis=1)

    # return as a concatenated array
    return np.concatenate([rates_gr, dates_gr])


def _gradient_poisson_relaxed(rates: np.ndarray, ages: np.ndarray):

    gradient = gradient_poisson(rates, ages)
    mean_rate = np.mean(rates)
    # penalty = lam * 2. * dgamma(rate, mean.rate) * (rank(rate) / Nb.rates - pgamma(rate, mean.rate))
    gradient[...] = gradient[...] + penalty


def gradient_penalty_relaxed(self):
    """Gradient function for the relaxed model penalty component
    """
    alpha = self.rates_hat.mean()
    a = stats.gamma.pdf(self.rates_hat, alpha)
    b = np.argsort(self.rates_hat) / self.rates_hat.size
    c = stats.gamma.cdf(self.rates_hat, alpha)
    gradient = 2 * a * (b - c)
    return self.weight * gradient


def get_tree_with_categorical_rates(ntips: int, nrates: int, seed: int) -> ToyTree:
    """FOR TESTING"""
    import toytree
    rng = np.random.default_rng(seed=seed)
    tree = toytree.rtree.unittree(ntips, seed=123)
    rates = np.linspace(1, 10, nrates)
    for node in tree:
        gidx = rng.choice(nrates)
        node._dist = node._dist * rng.gamma(shape=3, scale=rates[gidx])
    return tree


if __name__ == "__main__":

    import toytree
    import numpy as np
    toytree.set_log_level("DEBUG")

    tree = get_tree_with_categorical_rates(ntips=50, nrates=3, seed=123)
    c1, _, _ = tree.draw(ts='s', use_edge_lengths=True, scale_bar=True)
    tree.write("/tmp/test.nwk")

    res = edges_make_ultrametric_pl_clock(tree, {-1: 50}, full=True, max_fun=1e6, max_iter=1e6, max_refine=50)
    print(res)
    res = edges_make_ultrametric_pl_discrete(tree, 3, {-1: 35}, full=True, max_fun=1e6, max_iter=1e6, max_refine=50)
    print(res)
    # res["tree"].set_node_data("fixed", {-1: 'red'}, default="lightgrey", inplace=True)
    # c, a, m = res["tree"]._draw_browser(ts="s", use_edge_lengths=True, tmpdir="~", scale_bar=True, node_colors="fixed")

    # res = edges_make_ultrametric_pl_discrete(tree, 3, {}, full=True)
    # print(res)
    # res = edges_make_ultrametric_pl_discrete(tree, 4, {}, full=True)
    # print(res)
    # res = edges_make_ultrametric_pl_discrete(tree, 100, {}, full=True)
    # print(res)

    # ...
    # calibs = {} # 15: (0.25, 0.25)}
    # ages, dists = _get_init_ages(tree, {})
    # new = tree.set_node_data("height", ages)
    # c2, _, _ = new.draw(ts='s', use_edge_lengths=True, scale_bar=True)

    # print(_get_edge_data(new))
    # raise SystemExit(0)

    # print(ages)   # size nnodes
    # print(dists)  # size nnodes - 1
    # pen = PenLik(tree)
    # todo, ages, dists = pen._get_init_ages()
    # _get_bounds(tree, ages, dists)

    # calib = {18: (1, 5), 13: 0.1})
    # result = edges_make_ultrametric_pl_clock(tree, {-1: 15}, full=True)
    # utree = result["tree"]
    # print(result)
    # c3, _, _ = utree.draw(ts='s', use_edge_lengths=True, scale_bar=True)

    # draw it
    # toytree.utils.show([c1, c2, c3], tmpdir="~")


    # generate a tree under a molecular clock.


    # generate a tree with edge rates in 4 discrete rate categories


    # generate a tree 