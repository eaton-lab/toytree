#!/usr/bin/env python

from typing import Any, Union
from itertools import cycle
import numpy as np
from loguru import logger
from scipy.optimize import minimize
from scipy.special import factorial
from toytree.core import ToyTree
from toytree.mod._src.penalized_likelihood.pl_utils import (
    _get_init_ages, _get_params_bounds,
    get_tree_with_categorical_rates, Calibrations
)
from toytree.core.apis import TreeModAPI, add_subpackage_method


__all__ = ["edges_make_ultrametric_pl_discrete"]


@add_subpackage_method(TreeModAPI)
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



if __name__ == "__main__":

    import toytree
    import numpy as np
    toytree.set_log_level("DEBUG")

    tree = get_tree_with_categorical_rates(ntips=50, nrates=2, seed=123)
    res = edges_make_ultrametric_pl_discrete(tree, calibrations={-1: 1}, ncategories=2, full=True, max_fun=1e6, max_iter=1e6, max_refine=50)
    print(res)
    tree._draw_browser(tmpdir="~")
    res['tree']._draw_browser(tmpdir="~")
    # c1, _, _ = tree.draw(ts='s', use_edge_lengths=True, scale_bar=True)
    # tree.write("/tmp/test.nwk")
