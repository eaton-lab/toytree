#!/usr/bin/env python

"""Strict-clock branch-length pseudolikelihood fitting."""

from typing import Any, Union

import numpy as np
from loguru import logger
from scipy.optimize import minimize
from scipy.special import gammaln

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    Calibrations,
    _decode_age_params,
    _encode_age_params,
    _finalize_ultrametric_ages,
    _get_children_map_from_edges,
    _get_init_ages,
    _get_params_bounds,
    _normalize_calibrations,
    _pack_log_rates,
    _result_observation_metadata,
    _run_multistart,
    _select_best_multistart,
    _unpack_log_rates,
    _validate_branch_lengths,
    _validate_observation_mask,
    get_tree_with_categorical_rates,
)

__all__ = ["edges_make_ultrametric_clock"]
RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12


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
    observation_mask = payload["observation_mask"]
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
            observation_mask,
        ),
        method="L-BFGS-B",
        bounds=bounds,
        options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
    )

    current_loglik = fit.fun
    current_params = fit.x.copy()
    blocks = {
        "rates": [(False, True), slice(None, 1)],
    }
    if ages_idxs.size:
        blocks["ages"] = [(True, False), slice(1, None)]
    for _ in range(max(0, int(max_refine))):
        cycle_start = float(current_loglik)
        for fbools, fslice in blocks.values():
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
                observation_mask,
            )
            ifit = minimize(
                fun=objective_clock,
                x0=current_params[fslice],
                args=args,
                method="L-BFGS-B",
                bounds=bounds[fslice],
                options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
            )
            if float(ifit.fun) <= float(current_loglik):
                current_loglik = float(ifit.fun)
                current_params[fslice] = ifit.x
                fit = ifit
        if abs(cycle_start - float(current_loglik)) < 1e-9:
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
def edges_make_ultrametric_clock(
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
    _observation_mask: np.ndarray | None = None,
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
        working log-likelihood score, rate, and optimizer metadata.
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
        as well as statistics on the model fit including its working
        likelihood and rate.
    """
    if calibrations is None:
        calibrations = {}
    calibrations = _normalize_calibrations(
        tree,
        calibrations,
        dist_floor=DIST_FLOOR,
    )

    # get init and fixed node ages that make tree ultrametric
    ages_init, _ = _get_init_ages(tree, calibrations)

    # get bounds on params that need to be inferred; are not fixed
    rates_bounds, ages_bounds = _get_params_bounds(tree, calibrations)

    # get edges, dists and log-factorial-dists from rate-x-time edges
    edges = tree.get_edges("idx")
    dists_o = _validate_branch_lengths(tree)
    dists_lf = gammaln(dists_o + 1)
    # dists_lf = np.log(factorial(dists_o))
    edata = np.vstack([dists_o, dists_lf]).T
    observation_mask = _validate_observation_mask(_observation_mask, tree.nedges)

    # get starting rate in clock model as old/new treenode height
    rate_init = max(float(tree.treenode.height / ages_init[-1]), RATE_FLOOR)

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
    valid_loglik = _poisson_branch_pseudologlik(
        rate_init, ages_init, edges, edata, None, observation_mask
    )

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
                observation_mask=observation_mask,
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
        "clock multistart best objective="
        f"{best['objective']}, start={best['start']}, nstarts={nstarts}"
    )

    # transform tree with new ages
    ages = _decode_age_params(
        current_params[1:],
        ages_init,
        ages_idxs,
        ages_bounds,
        children_map,
        dist_floor=DIST_FLOOR,
    )
    ages = _finalize_ultrametric_ages(
        tree,
        ages,
        calibrations=calibrations,
        dist_floor=DIST_FLOOR,
    )
    tree = tree.set_node_data("height", ages, inplace=inplace)
    rate = float(_unpack_log_rates(current_params[:1])[0])

    pseudologlik = _poisson_branch_pseudologlik(
        rate, ages, edges, edata, valid_loglik, observation_mask
    )
    time_dists = ages[edges[:, 1]] - ages[edges[:, 0]]
    expected = time_dists * rate

    # return as a tree or a dict
    if not full:
        return tree
    return {
        "model": "clock",
        "pseudologlik": pseudologlik,
        "penalized_pseudologlik": pseudologlik,
        **_result_observation_metadata(),
        "nparams": len(bounds),
        "rate": rate,
        "expected_branch_lengths": expected.tolist(),
        "observed_branch_lengths": dists_o.tolist(),
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


def _poisson_branch_pseudologlik(
    rates_hat, ages_hat, edges, edata, valid_loglik, observation_mask=None
) -> float:
    """Return the fractional-Poisson branch-length pseudologlikelihood."""
    # get dists given the new age estimates
    dists_hat = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]

    # return high penalty as 2 x valid_loglik from starting params.
    if any(dists_hat < 0):
        return 2 * valid_loglik if valid_loglik is not None else -np.inf

    # get product of dists(time) and rates
    pdists = dists_hat * rates_hat

    # calculate loglik
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    terms = edata[:, 0] * np.log(pdists) - pdists - edata[:, 1]
    pseudologlik = np.sum(terms[mask])
    return float(pseudologlik) if np.isfinite(pseudologlik) else -np.inf


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
    observation_mask,
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
        )
    return -_poisson_branch_pseudologlik(
        rate_hat, ages_hat, edges, edata, valid_loglik, observation_mask
    )


if __name__ == "__main__":
    import numpy as np

    import toytree

    toytree.set_log_level("DEBUG")

    tree = get_tree_with_categorical_rates(ntips=50, nrates=1, seed=123)
    res = edges_make_ultrametric_clock(
        tree, calibrations={-1: 50}, full=True, max_fun=1e6, max_iter=1e6, max_refine=50
    )
    print(res)

    # c1, _, _ = tree.draw(ts='s', use_edge_lengths=True, scale_bar=True)
    # tree.write("/tmp/test.nwk")
