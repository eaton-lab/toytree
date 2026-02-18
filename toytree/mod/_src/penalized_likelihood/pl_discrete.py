#!/usr/bin/env python

from typing import Any, Union
from itertools import cycle
import numpy as np
from loguru import logger
from scipy.optimize import minimize
from scipy.special import gammaln
from toytree.core import ToyTree
from toytree.mod._src.penalized_likelihood.pl_clock import edges_make_ultrametric_pl_clock
from toytree.mod._src.penalized_likelihood.pl_utils import (
    _get_init_ages,
    _get_params_bounds,
    _pack_log_rates,
    _unpack_log_rates,
    _get_children_map_from_edges,
    _encode_age_params,
    _decode_age_params,
    _run_multistart,
    _select_best_multistart,
    get_tree_with_categorical_rates,
    Calibrations,
)
from toytree.core.apis import TreeModAPI, add_subpackage_method


__all__ = ["edges_make_ultrametric_pl_discrete"]
RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
AGE_UPPER_SWITCH = 1e6
INVALID_LOG_LIK_DROP = 1e6


def _fit_discrete_start(payload: dict[str, Any]) -> dict[str, Any]:
    start = int(payload["start"])
    params = payload["params"]
    bounds = payload["bounds"]
    rates_init = payload["rates_init"]
    age_params_init = payload["age_params_init"]
    ages_init = payload["ages_init"]
    ages_idxs = payload["ages_idxs"]
    ages_bounds = payload["ages_bounds"]
    children_map = payload["children_map"]
    edges = payload["edges"]
    edata = payload["edata"]
    freqs_init = payload["freqs_init"]
    valid_loglik = payload["valid_loglik"]
    max_iter = payload["max_iter"]
    max_fun = payload["max_fun"]
    max_refine = payload["max_refine"]

    fit = minimize(
        fun=objective_discrete,
        x0=params,
        args=(False, False, False, rates_init, age_params_init, ages_init, ages_idxs, ages_bounds, children_map, edges, edata, freqs_init, valid_loglik),
        method="L-BFGS-B",
        bounds=bounds,
        options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
    )

    current_loglik = fit.fun
    current_params = fit.x.copy()
    rsize = rates_init.size
    asize = ages_idxs.size
    fsize = freqs_init.size
    fix_dict = {
        "rates": [(False, True, True), slice(None, rsize)],
        "ages": [(True, False, True), slice(rsize, rsize + asize)],
    }
    if fsize:
        fix_dict["freqs"] = [(True, True, False), slice(-fsize, None)]
    iter_fixed = cycle(fix_dict)
    iter_refine = 0
    while 1:
        fixed = next(iter_fixed)
        fbools, fslice = fix_dict[fixed]
        rates_hat = _unpack_log_rates(current_params[:rsize])
        age_params_hat = current_params[rsize:rsize + asize]
        freqs_hat = current_params[-fsize:] if fsize else np.array([], dtype=float)
        args = fbools + (
            rates_hat,
            age_params_hat,
            ages_init,
            ages_idxs,
            ages_bounds,
            children_map,
            edges,
            edata,
            freqs_hat,
            valid_loglik,
        )
        ifit = minimize(
            fun=objective_discrete,
            x0=current_params[fslice],
            args=args,
            method="L-BFGS-B",
            bounds=bounds[fslice],
            options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
        )
        delta = ifit.fun - current_loglik
        if delta <= 0:
            current_loglik = ifit.fun
            current_params[fslice] = ifit.x
            fit = ifit
            if abs(delta) < 1e-9:
                break
        iter_refine += 1
        if iter_refine > max_refine:
            break
    return {
        "start": start,
        "objective": float(current_loglik),
        "converged": bool(fit.success),
        "message": str(fit.message),
        "nfev": int(getattr(fit, "nfev", -1)),
        "nit": int(getattr(fit, "nit", -1)),
        "params": current_params,
    }


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
    nstarts: int = 1,
    ncores: int = 1,
    seed: int | None = None,
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
    nstarts: int
        Number of random starting points; best objective is retained.
    ncores: int
        Number of worker processes for multistart; used if nstarts > 1.
    seed: int or None
        Random seed for multistart reproducibility.

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

    # strict identity with clock model when ncategories == 1.
    if int(ncategories) == 1:
        cres = edges_make_ultrametric_pl_clock(
            tree=tree,
            calibrations=calibrations,
            full=full,
            inplace=inplace,
            max_iter=max_iter,
            max_fun=max_fun,
            max_refine=max_refine,
            nstarts=nstarts,
            ncores=ncores,
            seed=seed,
        )
        if not full:
            return cres
        dres = dict(cres)
        dres["rates"] = [float(cres["rate"])]
        dres["freqs"] = [1.0]
        dres["model_alias"] = "clock"
        return dres

    # get init and fixed node ages that make tree ultrametric
    ages_init, _ = _get_init_ages(tree, calibrations)

    # get bounds on params that need to be inferred; are not fixed
    rates_bounds, ages_bounds = _get_params_bounds(tree, calibrations)

    # get edges, dists and log-factorial-dists from rate-x-time edges
    edges = tree.get_edges("idx")
    dists_o = tree.get_node_data("dist").values[:-1]
    dists_lf = gammaln(dists_o + 1.0)
    edata = np.vstack([dists_o, dists_lf]).T

    # get starting rates as old/new edge dists. Then bin the rates into
    # ncategories, as we will infer N rates and assign edges to bins.
    rates_init = dists_o / (ages_init[edges[:, 1]] - ages_init[edges[:, 0]])
    rates_init = np.clip(rates_init, RATE_FLOOR, None)
    _div = 1 / (2 * ncategories)
    _cats = np.linspace(_div, 1 - _div, ncategories)
    rates_init = np.quantile(rates_init, _cats)

    # get initial freqs (weights) of assignment of edges to categories
    freqs_init = np.repeat(1 / ncategories, ncategories - 1)

    # get indices of which node ages will be estimated
    ages_idxs = np.array(sorted(ages_bounds))
    children_map = _get_children_map_from_edges(edges)

    # slim bounds to only those needing to be estimated
    ages_bounds = [ages_bounds[i] for i in ages_idxs]
    rates_bounds = [rates_bounds[i] for i in range(ncategories)]
    rates_bounds = [
        (np.log(max(lo, RATE_FLOOR)), np.log(max(hi, RATE_FLOOR)))
        for (lo, hi) in rates_bounds
    ]
    age_params_init = _encode_age_params(
        ages_init, ages_idxs, ages_bounds, children_map, dist_floor=DIST_FLOOR, age_upper_switch=AGE_UPPER_SWITCH
    )
    freqs_bounds = [(0, 1) for i in range(ncategories - 1)]
    bounds = rates_bounds + [(None, None)] * age_params_init.size + freqs_bounds

    # get loglik at a valid starting params to scale neg dist penalty
    _freqs_hat = np.append(freqs_init, 1 - freqs_init.sum())
    valid_loglik = log_likelihood_poisson_discrete(rates_init, ages_init, edges, edata, _freqs_hat, None)

    params = np.hstack([
        _pack_log_rates(rates_init, rate_floor=RATE_FLOOR),
        age_params_init,
        freqs_init,
    ])
    nstarts = max(1, int(nstarts))
    ncores = max(1, int(ncores))
    rng = np.random.default_rng(seed)
    payloads = []
    rsize = rates_init.size
    asize = ages_idxs.size
    fsize = freqs_init.size
    for start in range(nstarts):
        sparams = params.copy()
        if start:
            sparams[:rsize] += rng.normal(0.0, 0.25, size=rsize)
            if asize:
                sparams[rsize:rsize + asize] += rng.normal(0.0, 0.25, size=asize)
            if fsize:
                freq_j = sparams[-fsize:] + rng.normal(0.0, 0.05, size=fsize)
                sparams[-fsize:] = np.clip(freq_j, 1e-6, 1 - 1e-6)
        payloads.append(
            dict(
                start=start,
                params=sparams,
                bounds=bounds,
                rates_init=rates_init,
                age_params_init=age_params_init,
                ages_init=ages_init,
                ages_idxs=ages_idxs,
                ages_bounds=ages_bounds,
                children_map=children_map,
                edges=edges,
                edata=edata,
                freqs_init=freqs_init,
                valid_loglik=valid_loglik,
                max_iter=max_iter,
                max_fun=max_fun,
                max_refine=max_refine,
            )
        )
    starts = _run_multistart(_fit_discrete_start, payloads, ncores=ncores)
    best = _select_best_multistart(starts)
    current_params = best["params"]
    if not best["converged"]:
        logger.warning(f"Best multistart fit did not converge: {best['message']}")
    logger.debug(
        f"discrete multistart best objective={best['objective']}, start={best['start']}, nstarts={nstarts}"
    )

    # transform tree with new ages
    ages = _decode_age_params(
        current_params[rsize:rsize + asize], ages_init, ages_idxs, ages_bounds, children_map, dist_floor=DIST_FLOOR, age_upper_switch=AGE_UPPER_SWITCH
    )
    tree = tree.set_node_data("height", ages, inplace=inplace)

    # get rates and freqs params
    rates = _unpack_log_rates(current_params[:rsize])
    freqs = current_params[-fsize:]

    # Final fit for PHIIC calculation (Penalized Hierarchical Information Criterion)
    _freqs = np.append(freqs, 1. - freqs.sum())
    loglik = log_likelihood_poisson_discrete(rates, ages, edges, edata, _freqs, valid_loglik)
    k = len(bounds)
    PHIIC = -2 * loglik + 2 * k

    # return as a tree or a dict
    if not full:
        return tree
    return {
        "loglik": loglik,
        "PHIIC": PHIIC,
        "rates": list(rates),
        "freqs": list(_freqs),
        "tree": tree,
        "converged": bool(best["converged"]),
        "nstarts": nstarts,
        "ncores": max(1, min(ncores, nstarts)),
        "best_start": int(best["start"]),
        "starts": [
            {
                "start": int(i["start"]),
                "objective": float(i["objective"]),
                "converged": bool(i["converged"]),
                "message": str(i["message"]),
                "nfev": int(i.get("nfev", -1)),
                "nit": int(i.get("nit", -1)),
            }
            for i in starts
        ],
    }



def objective_discrete(
    params,
    fixed_rates,
    fixed_ages,
    fixed_freqs,
    rates,
    age_params,
    ages_base,
    ages_idxs,
    ages_bounds,
    children_map,
    edges,
    edata,
    freqs,
    valid_loglik,
):
    """Return neg log-likelihood under discrete model.
    """
    # [RATES]
    if fixed_ages and fixed_freqs and not fixed_rates:
        assert params.size == rates.size
        ages_hat = _decode_age_params(
            age_params, ages_base, ages_idxs, ages_bounds, children_map, dist_floor=DIST_FLOOR, age_upper_switch=AGE_UPPER_SWITCH
        )
        rates_hat = _unpack_log_rates(params)
        freqs_hat = freqs
    # [AGES]
    elif fixed_rates and fixed_freqs and not fixed_ages:
        assert params.size == ages_idxs.size
        rates_hat = rates
        ages_hat = _decode_age_params(
            params, ages_base, ages_idxs, ages_bounds, children_map, dist_floor=DIST_FLOOR, age_upper_switch=AGE_UPPER_SWITCH
        )
        freqs_hat = freqs
    # [FREQS]
    elif fixed_rates and fixed_ages and not fixed_freqs:
        assert params.size == freqs.size
        ages_hat = _decode_age_params(
            age_params, ages_base, ages_idxs, ages_bounds, children_map, dist_floor=DIST_FLOOR, age_upper_switch=AGE_UPPER_SWITCH
        )
        rates_hat = rates
        freqs_hat = params
    else:
        assert params.size == ages_idxs.size + rates.size + freqs.size
        rates_hat = _unpack_log_rates(params[:rates.size])
        ages_hat = _decode_age_params(
            params[rates.size:rates.size + ages_idxs.size],
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
            age_upper_switch=AGE_UPPER_SWITCH,
        )
        freqs_hat = params[-freqs.size:]

    # add final freq category for the remainder
    freqs_hat = np.append(freqs_hat, 1. - freqs_hat.sum())

    # calculate log-likelihood
    args = (rates_hat, ages_hat, edges, edata, freqs_hat, valid_loglik)
    return -log_likelihood_poisson_discrete(*args)



def log_likelihood_poisson_discrete(rates_hat, ages_hat, edges, edata, freqs_hat, valid_loglik) -> float:
    """Return the log-likelihood of the rates x ages params"""
    if valid_loglik is None:
        valid_loglik = -1.0
    invalid_score = valid_loglik - INVALID_LOG_LIK_DROP

    # get dists given the new age estimates
    dists_hat = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]

    # return a poor but finite score for invalid geometry/weights.
    if np.any(dists_hat <= DIST_FLOOR):
        return invalid_score
    if np.any(freqs_hat < 0):
        return invalid_score
    if np.sum(freqs_hat) > 1.0 + 1e-8:
        return invalid_score

    # get product of dists(time) and rates
    rates_hat = np.clip(np.asarray(rates_hat, dtype=float), RATE_FLOOR, None)
    pdists = dists_hat * rates_hat[:, np.newaxis]
    if np.any(pdists <= RATE_FLOOR) or np.any(~np.isfinite(pdists)):
        return invalid_score

    # calculate loglik
    prob = np.exp(edata[:, 0] * np.log(pdists) - pdists - edata[:, 1])
    if np.any(~np.isfinite(prob)):
        return invalid_score

    # multiply each by its weight in each category
    mix = prob.T @ freqs_hat
    if np.any(mix <= 0) or np.any(~np.isfinite(mix)):
        return invalid_score
    loglik = np.sum(np.log(mix))
    return float(loglik) if np.isfinite(loglik) else invalid_score



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
