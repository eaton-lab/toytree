#!/usr/bin/env python

from typing import Any, Union
from itertools import cycle
from loguru import logger
import numpy as np
from scipy.optimize import minimize
from scipy.special import factorial
from scipy import stats
from toytree.core import ToyTree
from toytree.mod._src.penalized_likelihood.pl_utils import (
    _get_init_ages, _get_params_bounds,
    get_tree_with_uncorrelated_relaxed_rates, Calibrations
)

logger = logger.bind(name="toytree")


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

    Edges are scaled while allowing each edge to have its own rate,
    and a penalty is applied to discourage excessive variation away
    from a gamma distribution of rates.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree with non-ultrametric edge lengths.
    lam: float
        Lambda rate variation penalty parameter of Sanderson's
        relaxed model. Lower values allow more rate variation.
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
        PHIIC, and rates.
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

    # get starting rates as old/new edge dists.
    rates_init = dists_o / (ages_init[edges[:, 1]] - ages_init[edges[:, 0]])

    # get indices of which node ages will be estimated
    ages_idxs = np.array(sorted(ages_bounds))

    # slim bounds to only those needing to be estimated
    ages_bounds = [ages_bounds[i] for i in ages_idxs]
    rates_bounds = [rates_bounds[i] for i in range(tree.nnodes - 1)]
    bounds = rates_bounds + ages_bounds

    # get loglik at a valid starting params to scale neg dist penalty
    valid_loglik = log_likelihood_poisson_relaxed(rates_init, ages_init, edges, edata, lam, None)

    # fit joint model
    params = np.hstack([rates_init, ages_init[ages_idxs]])
    fit = minimize(
        fun=objective_relaxed,
        x0=params,
        args=(False, False, rates_init, ages_init, ages_idxs, edges, edata, lam, valid_loglik),
        method="L-BFGS-B",
        bounds=bounds,
        options=dict(maxiter=int(max_iter), maxfun=int(max_fun))
    )
    # log success/fail report
    if not fit.success:
        logger.warning(f"Failed to converge. Consider increasing max_iter & max_fun:\n{fit}")
    else:
        logger.debug(f"Initial fit penalized loglik={-fit.fun}")

    # iterative optimization while alternately fixing rates or ages
    current_loglik = fit.fun
    current_params = fit.x
    iter_refine = 0
    rsize = rates_init.size
    asize = ages_idxs.size

    # dict mapping fixed param type to fixed bool selector, and param subset slice
    fix_dict = {
        "rates": [(False, True), slice(None, rsize)],
        "ages": [(True, False), slice(rsize, rsize + asize)],
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
        args = fbools + (rates_hat, ages_hat, ages_idxs, edges, edata, lam, valid_loglik)
        ifit = minimize(
            fun=objective_relaxed,
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
            logger.debug(f"fixed {fixed:<5} penalized loglik={-current_loglik}; Δloglik={Δ_loglik}")
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

    # get rates params
    rates = current_params[:rsize]

    # Final fit for PHIIC calculation (Penalized Hierarchical Information Criterion)
    loglik = log_likelihood_poisson_relaxed(rates, ages, edges, edata, lam, valid_loglik)
    k = len(bounds)
    PHIIC = -2 * loglik + 2 * k

    # return as a tree or a dict
    if not full:
        return tree
    raw_loglik = log_likelihood_poisson_relaxed(rates, ages, edges, edata, 0.0, valid_loglik)
    penalty = _relaxed_penalty(rates)
    return {
        "loglik": loglik,
        "raw_loglik": raw_loglik,
        "penalty": penalty,
        "PHIIC": PHIIC,
        "rates": list(rates),
        "tree": tree,
        "converged": fit.success,
    }


def _relaxed_penalty(rates_hat: np.ndarray) -> float:
    """Return the relaxed clock penalty score for rates."""
    alpha = rates_hat.mean()
    pcdf = np.sort(stats.gamma.cdf(rates_hat, a=alpha))
    ecdf = np.arange(1, rates_hat.size + 1) / rates_hat.size
    return float(np.sum((ecdf - pcdf) ** 2))


def log_likelihood_poisson_relaxed(rates_hat, ages_hat, edges, edata, lam, valid_loglik) -> float:
    """Return the penalized log-likelihood of the relaxed model."""
    # get dists given the new age estimates
    dists_hat = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]

    # return high penalty as 2 x valid_loglik from starting params.
    if any(dists_hat < 0):
        return 2 * valid_loglik

    # get product of dists(time) and rates
    pdists = dists_hat * rates_hat

    # calculate loglik
    loglik = np.sum(edata[:, 0] * np.log(pdists) - pdists - edata[:, 1])
    penalty = _relaxed_penalty(rates_hat)
    return loglik - lam * penalty


def objective_relaxed(params, fixed_rates, fixed_ages, rates, ages, ages_idxs, edges, edata, lam, valid_loglik):
    """Return neg log-likelihood under relaxed clock model."""
    # [RATES] optimize rates while keeping ages fixed
    if fixed_ages and not fixed_rates:
        assert params.size == rates.size
        ages_hat = ages
        rates_hat = params
    # [AGES] optimize ages while keeping rates fixed
    elif fixed_rates and not fixed_ages:
        assert params.size == ages_idxs.size
        rates_hat = rates
        ages_hat = ages.copy()
        ages_hat[ages_idxs] = params
    # joint optimize rates and ages
    else:
        assert params.size == ages_idxs.size + rates.size
        rates_hat = params[:rates.size]
        ages_hat = ages.copy()
        ages_hat[ages_idxs] = params[rates.size:]
    return -log_likelihood_poisson_relaxed(rates_hat, ages_hat, edges, edata, lam, valid_loglik)


if __name__ == "__main__":

    import toytree
    import numpy as np
    toytree.set_log_level("DEBUG")

    tree = get_tree_with_uncorrelated_relaxed_rates(ntips=50, mean=3, sigma=3, seed=123)
    res = edges_make_ultrametric_pl_relaxed(tree, lam=0.5, calibrations={-1: 50}, full=True, max_fun=1e6, max_iter=1e6, max_refine=50)
    print(res)
