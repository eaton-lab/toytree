#!/usr/bin/env python

from typing import Any, Union
from itertools import cycle
import numpy as np
from loguru import logger
from scipy.optimize import minimize
from scipy.special import gammaln
from toytree.core import ToyTree
from toytree.mod._src.penalized_likelihood.pl_utils import (
    _get_init_ages,
    _get_params_bounds,
    get_tree_with_categorical_rates,
    Calibrations
)
from toytree.core.apis import TreeModAPI, add_subpackage_method


__all__ = ["edges_make_ultrametric_pl_clock"]


@add_subpackage_method(TreeModAPI)
def edges_make_ultrametric_pl_clock(
    tree: ToyTree,
    calibrations: Calibrations | None = None,
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 100_000,
    max_fun: int = 100_000,
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
    if calibrations is None:
        calibrations = {}

    # get init and fixed node ages that make tree ultrametric
    ages_init, _ = _get_init_ages(tree, calibrations)

    # get bounds on params that need to be inferred; are not fixed
    rates_bounds, ages_bounds = _get_params_bounds(tree, calibrations)

    # get edges, dists and log-factorial-dists from rate-x-time edges
    edges = tree.get_edges("idx")
    dists_o = tree.get_node_data("dist").values[:-1]
    dists_lf = gammaln(dists_o + 1)
    # dists_lf = np.log(factorial(dists_o))
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


def log_likelihood_poisson(rates_hat, ages_hat, edges, edata, valid_loglik) -> float:
    """Return the log-likelihood of the rates x ages params"""
    # get dists given the new age estimates
    dists_hat = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]

    # return high penalty as 2 x valid_loglik from starting params.
    if any(dists_hat < 0):
        return 2 * valid_loglik if valid_loglik is not None else -np.inf

    # get product of dists(time) and rates
    pdists = dists_hat * rates_hat

    # calculate loglik
    loglik = np.sum(edata[:, 0] * np.log(pdists) - pdists - edata[:, 1])
    return loglik if loglik is not None else -np.inf


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


if __name__ == "__main__":

    import toytree
    import numpy as np
    toytree.set_log_level("DEBUG")


    tree = get_tree_with_categorical_rates(ntips=50, nrates=1, seed=123)
    res = edges_make_ultrametric_pl_clock(tree, calibrations={-1: 50}, full=True, max_fun=1e6, max_iter=1e6, max_refine=50)
    print(res)

    # c1, _, _ = tree.draw(ts='s', use_edge_lengths=True, scale_bar=True)
    # tree.write("/tmp/test.nwk")
