#!/usr/bin/env python

from typing import Any, Union
from itertools import cycle
from loguru import logger
import numpy as np
from scipy.optimize import minimize
from scipy.special import factorial
from toytree.core import ToyTree
from toytree.mod._src.penalized_likelihood.pl_utils import (
    _get_init_ages,
    _get_params_bounds,
    Calibrations
)
from toytree.core.apis import TreeModAPI, add_subpackage_method


__all__ = ["edges_make_ultrametric_pl_relaxed"]


@add_subpackage_method(TreeModAPI)
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




def objective_relaxed(params, fixed_rates, fixed_ages, rates, ages, ages_idxs, edges, edata, lam, valid_loglik) -> float:
    """..."""


def log_likelihood_poisson_relaxed() -> float:
    # get likelihood of model parameters
    loglik = log_likelihood_poisson(rates, ages, edges, edata, valid_loglik)

    # get penalty under relaxed lambda weighting
    mu = np.mean(rates)
    return loglik - lamb * sum(...)



if __name__ == "__main__":

    import toytree
    import numpy as np
    toytree.set_log_level("DEBUG")

    tree = get_tree_with_relaxed_rates(ntips=50, nrates=2, seed=123)
    res = edges_make_ultrametric_pl_discrete(tree, calibrations={-1: 50}, ncategories=2, full=True, max_fun=1e6, max_iter=1e6, max_refine=50)
    print(res)

    # c1, _, _ = tree.draw(ts='s', use_edge_lengths=True, scale_bar=True)
    # tree.write("/tmp/test.nwk")
