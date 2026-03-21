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
    get_tree_with_categorical_rates,
)

__all__ = ["edges_make_ultrametric_pl_clock"]
RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
AGE_UPPER_SWITCH = 1e6


def _fit_clock_start(payload: dict[str, Any]) -> dict[str, Any]:
    """Optimize one clock-model start and return fit summary + params."""
    start = int(payload["start"])
    params = payload["params"]
    bounds = payload["bounds"]
    rate_init = payload["rate_init"]
    age_params_init = payload["age_params_init"]
    ages_init = payload["ages_init"]
    ages_idxs = payload["ages_idxs"]
    ages_bounds = payload["ages_bounds"]
    children_map = payload["children_map"]
    edges = payload["edges"]
    edata = payload["edata"]
    valid_loglik = payload["valid_loglik"]
    max_iter = payload["max_iter"]
    max_fun = payload["max_fun"]
    max_refine = payload["max_refine"]

    fit = minimize(
        fun=objective_clock,
        x0=params,
        args=(
            False,
            False,
            rate_init,
            age_params_init,
            ages_init,
            ages_idxs,
            ages_bounds,
            children_map,
            edges,
            edata,
            valid_loglik,
        ),
        method="L-BFGS-B",
        bounds=bounds,
        options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
    )

    current_loglik = fit.fun
    current_params = fit.x.copy()
    iter_refine = 0
    fix_dict = {
        "rates": [(False, True), slice(None, 1)],
        "ages": [(True, False), slice(1, None)],
    }
    iter_fixed = cycle(fix_dict)
    while 1:
        fixed = next(iter_fixed)
        fbools, fslice = fix_dict[fixed]
        rates_hat = _unpack_log_rates(current_params[:1])
        age_params_hat = current_params[1:]
        args = fbools + (
            rates_hat,
            age_params_hat,
            ages_init,
            ages_idxs,
            ages_bounds,
            children_map,
            edges,
            edata,
            valid_loglik,
        )
        ifit = minimize(
            fun=objective_clock,
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
def edges_make_ultrametric_pl_clock(
    tree: ToyTree,
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
    children_map = _get_children_map_from_edges(edges)

    # slim bounds to only those needing to be estimated
    ages_bounds = [ages_bounds[i] for i in ages_idxs]
    rate_bounds = rates_bounds[0]
    age_params_init = _encode_age_params(
        ages_init,
        ages_idxs,
        ages_bounds,
        children_map,
        dist_floor=DIST_FLOOR,
        age_upper_switch=AGE_UPPER_SWITCH,
    )

    bounds = [
        (
            np.log(max(rate_bounds[0], RATE_FLOOR)),
            np.log(max(rate_bounds[1], RATE_FLOOR)),
        )
    ] + [(None, None)] * age_params_init.size

    params = np.hstack(
        [
            _pack_log_rates(np.array([rate_init], dtype=float), rate_floor=RATE_FLOOR),
            age_params_init,
        ]
    )

    # get loglik at a valid starting params to scale neg dist penalty
    valid_loglik = log_likelihood_poisson(rate_init, ages_init, edges, edata, None)

    nstarts = max(1, int(nstarts))
    ncores = max(1, int(ncores))
    rng = np.random.default_rng(seed)
    payloads = []
    for start in range(nstarts):
        sparams = params.copy()
        if start:
            sparams[:1] += rng.normal(0.0, 0.25, size=1)
            if sparams.size > 1:
                sparams[1:] += rng.normal(0.0, 0.25, size=sparams.size - 1)
        payloads.append(
            dict(
                start=start,
                params=sparams,
                bounds=bounds,
                rate_init=rate_init,
                age_params_init=age_params_init,
                ages_init=ages_init,
                ages_idxs=ages_idxs,
                ages_bounds=ages_bounds,
                children_map=children_map,
                edges=edges,
                edata=edata,
                valid_loglik=valid_loglik,
                max_iter=max_iter,
                max_fun=max_fun,
                max_refine=max_refine,
            )
        )
    starts = _run_multistart(_fit_clock_start, payloads, ncores=ncores)
    best = _select_best_multistart(starts)
    current_params = best["params"]
    if not best["converged"]:
        logger.warning(f"Best multistart fit did not converge: {best['message']}")
    logger.debug(
        f"clock multistart best objective={best['objective']}, start={best['start']}, nstarts={nstarts}"
    )

    # transform tree with new ages
    ages = _decode_age_params(
        current_params[1:],
        ages_init,
        ages_idxs,
        ages_bounds,
        children_map,
        dist_floor=DIST_FLOOR,
        age_upper_switch=AGE_UPPER_SWITCH,
    )
    tree = tree.set_node_data("height", ages, inplace=inplace)
    rate = float(_unpack_log_rates(current_params[:1])[0])

    # Final fit for PHIIC calculation (Penalized Hierarchical Information Criterion)
    loglik = log_likelihood_poisson(rate, ages, edges, edata, valid_loglik)
    k = len(bounds)
    PHIIC = -2 * loglik + 2 * k

    # return as a tree or a dict
    if not full:
        return tree
    return {
        "loglik": loglik,
        "PHIIC": PHIIC,
        "rate": rate,
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


def log_likelihood_poisson(rates_hat, ages_hat, edges, edata, valid_loglik) -> float:
    """Return the log-likelihood of the rates x ages params."""
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


def objective_clock(
    params,
    fixed_rate,
    fixed_ages,
    rate,
    age_params,
    ages_base,
    ages_idxs,
    ages_bounds,
    children_map,
    edges,
    edata,
    valid_loglik,
):
    """Return neg log-likelihood under clock model."""
    # [AGES] optimize ages while keeping rate fixed
    if fixed_rate and not fixed_ages:
        assert params.size == ages_idxs.size
        rate_hat = rate
        ages_hat = _decode_age_params(
            params,
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
            age_upper_switch=AGE_UPPER_SWITCH,
        )
    # [RATE] optimize rate while keeping ages fixed
    elif fixed_ages and not fixed_rate:
        assert params.size == 1
        ages_hat = _decode_age_params(
            age_params,
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
            age_upper_switch=AGE_UPPER_SWITCH,
        )
        rate_hat = _unpack_log_rates(params)
    # joint optimize rate and ages
    else:
        assert params.size == ages_idxs.size + 1
        rate_hat = _unpack_log_rates(params[:1])
        ages_hat = _decode_age_params(
            params[1:],
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
            age_upper_switch=AGE_UPPER_SWITCH,
        )
    return -log_likelihood_poisson(rate_hat, ages_hat, edges, edata, valid_loglik)


if __name__ == "__main__":
    import numpy as np

    import toytree

    toytree.set_log_level("DEBUG")

    tree = get_tree_with_categorical_rates(ntips=50, nrates=1, seed=123)
    res = edges_make_ultrametric_pl_clock(
        tree, calibrations={-1: 50}, full=True, max_fun=1e6, max_iter=1e6, max_refine=50
    )
    print(res)

    # c1, _, _ = tree.draw(ts='s', use_edge_lengths=True, scale_bar=True)
    # tree.write("/tmp/test.nwk")
