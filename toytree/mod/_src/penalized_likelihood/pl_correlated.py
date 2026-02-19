#!/usr/bin/env python

from itertools import cycle
from typing import Any, Union

import numpy as np
from loguru import logger
from scipy.optimize import minimize
from scipy.special import gammaln

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_likelihood.pl_utils import (
    Calibrations,
    _decode_age_params,
    _encode_age_params,
    _get_children_map_from_edges,
    _get_init_ages,
    _get_params_bounds,
    _pack_log_rates,
    _run_multistart,
    _select_best_multistart,
    _unpack_log_rates,
    get_tree_with_correlated_relaxed_rates,
)

__all__ = ["edges_make_ultrametric_pl_correlated"]

RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
INVALID_LOG_LIK_DROP = 1e6
AGE_UPPER_SWITCH = 1e6


def _fit_correlated_start(payload: dict[str, Any]) -> dict[str, Any]:
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
    parent_edges = payload["parent_edges"]
    lam = payload["lam"]
    valid_loglik = payload["valid_loglik"]
    max_iter = payload["max_iter"]
    max_fun = payload["max_fun"]
    max_refine = payload["max_refine"]

    fit = minimize(
        fun=objective_correlated,
        x0=params,
        args=(
            False,
            False,
            rates_init,
            age_params_init,
            ages_init,
            ages_idxs,
            ages_bounds,
            children_map,
            edges,
            edata,
            parent_edges,
            lam,
            valid_loglik,
        ),
        method="L-BFGS-B",
        bounds=bounds,
        options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
    )
    if not fit.success:
        rng = np.random.default_rng(123 + start)
        rates_seed = np.clip(
            rates_init * np.exp(rng.normal(0.0, 0.25, size=rates_init.size)),
            RATE_FLOOR,
            None,
        )
        params_seed = np.hstack([_pack_log_rates(rates_seed, rate_floor=RATE_FLOOR), age_params_init])
        refit = minimize(
            fun=objective_correlated,
            x0=params_seed,
            args=(
                False,
                False,
                rates_seed,
                age_params_init,
                ages_init,
                ages_idxs,
                ages_bounds,
                children_map,
                edges,
                edata,
                parent_edges,
                lam,
                valid_loglik,
            ),
            method="L-BFGS-B",
            bounds=bounds,
            options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
        )
        if refit.fun < fit.fun:
            fit = refit

    current_loglik = fit.fun
    current_params = fit.x.copy()
    rsize = rates_init.size
    asize = ages_idxs.size
    fix_dict = {
        "rates": [(False, True), slice(None, rsize)],
        "ages": [(True, False), slice(rsize, rsize + asize)],
    }
    iter_fixed = cycle(fix_dict)
    iter_refine = 0
    while 1:
        fixed = next(iter_fixed)
        fbools, fslice = fix_dict[fixed]
        rates_hat = _unpack_log_rates(current_params[:rsize])
        age_params_hat = current_params[rsize:rsize + asize]
        args = fbools + (
            rates_hat,
            age_params_hat,
            ages_init,
            ages_idxs,
            ages_bounds,
            children_map,
            edges,
            edata,
            parent_edges,
            lam,
            valid_loglik,
        )
        ifit = minimize(
            fun=objective_correlated,
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
def edges_make_ultrametric_pl_correlated(
    tree: ToyTree,
    lam: float,
    calibrations: Calibrations | None = None,
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 100_000,
    max_fun: int = 100_000,
    max_refine: int = 20,
    nstarts: int = 1,
    ncores: int = 1,
    seed: int | None = None,
) -> Union[ToyTree, dict[str, Any]]:
    """Return a tree made ultrametric under a correlated relaxed-clock model.

    This model estimates one rate per edge and penalizes abrupt changes
    between adjacent edges by minimizing differences among parent-child
    edge rates on a log scale.
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
    dists_lf = gammaln(dists_o + 1.0)
    edata = np.vstack([dists_o, dists_lf]).T

    # get starting rates as old/new edge dists.
    rates_init = dists_o / (ages_init[edges[:, 1]] - ages_init[edges[:, 0]])
    rates_init = np.clip(rates_init, RATE_FLOOR, None)

    # map edges to their parent edge index for correlation penalty.
    child_to_eidx = {int(child): idx for idx, (child, _) in enumerate(edges)}
    parent_edges = np.array([child_to_eidx.get(int(parent), -1) for _, parent in edges], dtype=int)

    # get indices of which node ages will be estimated
    ages_idxs = np.array(sorted(ages_bounds))
    children_map = _get_children_map_from_edges(edges)

    # slim bounds to only those needing to be estimated
    ages_bounds = [ages_bounds[i] for i in ages_idxs]
    rates_bounds = [rates_bounds[i] for i in range(tree.nnodes - 1)]
    rates_bounds = [
        (np.log(max(lo, RATE_FLOOR)), np.log(max(hi, RATE_FLOOR)))
        for (lo, hi) in rates_bounds
    ]
    age_params_init = _encode_age_params(
        ages_init, ages_idxs, ages_bounds, children_map,
        dist_floor=DIST_FLOOR, age_upper_switch=AGE_UPPER_SWITCH
    )
    bounds = rates_bounds + [(None, None)] * age_params_init.size

    # get loglik at a valid starting params to scale invalid-geometry penalty
    valid_loglik = log_likelihood_poisson_correlated(
        rates_init, ages_init, edges, edata, parent_edges, lam, None
    )

    params = np.hstack([_pack_log_rates(rates_init, rate_floor=RATE_FLOOR), age_params_init])
    nstarts = max(1, int(nstarts))
    ncores = max(1, int(ncores))
    rng = np.random.default_rng(seed)
    payloads = []
    rsize = rates_init.size
    asize = ages_idxs.size
    for start in range(nstarts):
        sparams = params.copy()
        if start:
            sparams[:rsize] += rng.normal(0.0, 0.25, size=rsize)
            if asize:
                sparams[rsize:rsize + asize] += rng.normal(0.0, 0.25, size=asize)
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
                parent_edges=parent_edges,
                lam=lam,
                valid_loglik=valid_loglik,
                max_iter=max_iter,
                max_fun=max_fun,
                max_refine=max_refine,
            )
        )
    starts = _run_multistart(_fit_correlated_start, payloads, ncores=ncores)
    best = _select_best_multistart(starts)
    current_params = best["params"]
    if not best["converged"]:
        logger.warning(f"Best multistart fit did not converge: {best['message']}")
    logger.debug(
        f"correlated multistart best objective={best['objective']}, start={best['start']}, nstarts={nstarts}"
    )

    ages = _decode_age_params(
        current_params[rsize:rsize + asize], ages_init, ages_idxs, ages_bounds, children_map, dist_floor=DIST_FLOOR, age_upper_switch=AGE_UPPER_SWITCH
    )
    tree = tree.set_node_data("height", ages, inplace=inplace)
    rates = _unpack_log_rates(current_params[:rsize])

    loglik = log_likelihood_poisson_correlated(rates, ages, edges, edata, parent_edges, lam, valid_loglik)
    k = len(bounds)
    phiic = -2 * loglik + 2 * k

    if not full:
        return tree

    raw_loglik = log_likelihood_poisson_correlated(
        rates, ages, edges, edata, parent_edges, 0.0, valid_loglik
    )
    penalty = _correlated_penalty(rates, parent_edges)
    return {
        "loglik": loglik,
        "raw_loglik": raw_loglik,
        "penalty": penalty,
        "PHIIC": phiic,
        "rates": list(rates),
        "tree": tree,
        "converged": bool(best["converged"]),
        "optimizer_message": str(best["message"]),
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


def _correlated_penalty(rates_hat: np.ndarray, parent_edges: np.ndarray) -> float:
    """Return autocorrelation penalty from parent-child edge log-rate changes."""
    rates_hat = np.clip(np.asarray(rates_hat, dtype=float), RATE_FLOOR, None)
    valid = parent_edges >= 0
    if not np.any(valid):
        return 0.0
    child_log = np.log(rates_hat[valid])
    parent_log = np.log(rates_hat[parent_edges[valid]])
    diffs = child_log - parent_log
    return float(np.mean(diffs * diffs))


def log_likelihood_poisson_correlated(
    rates_hat,
    ages_hat,
    edges,
    edata,
    parent_edges,
    lam,
    valid_loglik,
) -> float:
    """Return penalized log-likelihood for correlated relaxed-clock model."""
    if valid_loglik is None:
        valid_loglik = -1.0

    dists_hat = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    if np.any(dists_hat <= DIST_FLOOR):
        return valid_loglik - INVALID_LOG_LIK_DROP

    rates_hat = np.clip(rates_hat, RATE_FLOOR, None)
    pdists = dists_hat * rates_hat
    if np.any(pdists <= RATE_FLOOR) or np.any(~np.isfinite(pdists)):
        return valid_loglik - INVALID_LOG_LIK_DROP

    loglik = np.sum(edata[:, 0] * np.log(pdists) - pdists - edata[:, 1])
    if not np.isfinite(loglik):
        return valid_loglik - INVALID_LOG_LIK_DROP

    penalty = _correlated_penalty(rates_hat, parent_edges)
    if not np.isfinite(penalty):
        return valid_loglik - INVALID_LOG_LIK_DROP
    return loglik - lam * penalty


def objective_correlated(
    params,
    fixed_rates,
    fixed_ages,
    rates,
    age_params,
    ages_base,
    ages_idxs,
    ages_bounds,
    children_map,
    edges,
    edata,
    parent_edges,
    lam,
    valid_loglik,
):
    """Return negative penalized log-likelihood under correlated model."""
    if fixed_ages and not fixed_rates:
        assert params.size == rates.size
        ages_hat = _decode_age_params(
            age_params, ages_base, ages_idxs, ages_bounds, children_map,
            dist_floor=DIST_FLOOR, age_upper_switch=AGE_UPPER_SWITCH
        )
        rates_hat = _unpack_log_rates(params)
    elif fixed_rates and not fixed_ages:
        assert params.size == ages_idxs.size
        rates_hat = rates
        ages_hat = _decode_age_params(
            params, ages_base, ages_idxs, ages_bounds, children_map,
            dist_floor=DIST_FLOOR, age_upper_switch=AGE_UPPER_SWITCH
        )
    else:
        assert params.size == ages_idxs.size + rates.size
        rates_hat = _unpack_log_rates(params[:rates.size])
        ages_hat = _decode_age_params(
            params[rates.size:], ages_base, ages_idxs, ages_bounds, children_map,
            dist_floor=DIST_FLOOR, age_upper_switch=AGE_UPPER_SWITCH
        )
    return -log_likelihood_poisson_correlated(
        rates_hat, ages_hat, edges, edata, parent_edges, lam, valid_loglik
    )


if __name__ == "__main__":
    import toytree
    toytree.set_log_level("DEBUG")

    tree = get_tree_with_correlated_relaxed_rates(ntips=40, mean=3, sigma=2, seed=123)
    res = edges_make_ultrametric_pl_correlated(
        tree,
        lam=0.5,
        calibrations={-1: 20.0},
        full=True,
        max_iter=2000,
        max_fun=2000,
        max_refine=4,
    )
    print(res)
