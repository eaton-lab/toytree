#!/usr/bin/env python

"""Discrete-mixture branch-length pseudolikelihood fitting."""

from typing import Any, Union

import numpy as np
from loguru import logger
from scipy.optimize import minimize
from scipy.special import gammaln, logsumexp

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_pseudolikelihood.clock import (
    edges_make_ultrametric_clock,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    PARAM_MAX,
    PARAM_MIN,
    Calibrations,
    _decode_age_params,
    _encode_age_params,
    _finalize_ultrametric_ages,
    _get_children_map_from_edges,
    _get_init_ages,
    _get_params_bounds,
    _normalize_calibrations,
    _result_observation_metadata,
    _run_multistart,
    _select_best_multistart,
    _validate_branch_lengths,
    _validate_ncategories,
    _validate_observation_mask,
    get_tree_with_categorical_rates,
)

__all__ = ["edges_make_ultrametric_discrete"]
RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
INVALID_LOG_LIK_DROP = 1e6


def _unpack_simplex_logits(logits: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return simplex weights and log-weights from K-1 reference logits."""
    full = np.append(np.asarray(logits, dtype=float), 0.0)
    log_weights = full - logsumexp(full)
    return np.exp(log_weights), log_weights


def _pack_simplex_weights(weights: np.ndarray) -> np.ndarray:
    """Return K-1 reference logits for strictly positive simplex weights."""
    values = np.asarray(weights, dtype=float)
    values = values / values.sum()
    return np.log(values[:-1]) - np.log(values[-1])


def _unpack_ordered_rate_params(params: np.ndarray) -> np.ndarray:
    """Map K unconstrained gap logits to K strictly ordered positive rates."""
    full = np.append(np.asarray(params, dtype=float), 0.0)
    log_gaps = full - logsumexp(full)
    positions = np.cumsum(np.exp(log_gaps)[:-1])
    lo = float(np.log(PARAM_MIN))
    hi = float(np.log(PARAM_MAX))
    return np.exp(lo + (hi - lo) * positions)


def _pack_ordered_rates(rates: np.ndarray) -> np.ndarray:
    """Map K sorted rates to unconstrained gap logits."""
    values = np.sort(np.asarray(rates, dtype=float))
    lo = float(np.log(PARAM_MIN))
    hi = float(np.log(PARAM_MAX))
    eps = np.finfo(float).eps
    positions = np.clip((np.log(values) - lo) / (hi - lo), eps, 1.0 - eps)
    positions = np.maximum.accumulate(positions)
    gaps = np.diff(np.concatenate(([0.0], positions, [1.0])))
    gaps = np.clip(gaps, eps, None)
    gaps /= gaps.sum()
    return np.log(gaps[:-1]) - np.log(gaps[-1])


def _fit_discrete_start(payload: dict[str, Any]) -> dict[str, Any]:
    start = int(payload["start"])
    params = payload["params"]
    bounds = payload["bounds"]
    rates_init = payload["rates_init"]
    rate_params_init = payload["rate_params_init"]
    age_params_init = payload["age_params_init"]
    ages_init = payload["ages_init"]
    ages_idxs = payload["ages_idxs"]
    ages_bounds = payload["ages_bounds"]
    children_map = payload["children_map"]
    edges = payload["edges"]
    edata = payload["edata"]
    weights_init = payload["weights_init"]
    weight_params_init = payload["weight_params_init"]
    valid_loglik = payload["valid_loglik"]
    observation_mask = payload["observation_mask"]
    max_iter = payload["max_iter"]
    max_fun = payload["max_fun"]
    max_refine = payload["max_refine"]

    fit = minimize(
        fun=objective_discrete,
        x0=params,
        args=(
            False,
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
            weights_init,
            valid_loglik,
            observation_mask,
        ),
        method="L-BFGS-B",
        bounds=bounds,
        options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
    )

    current_loglik = float(fit.fun)
    current_params = fit.x.copy()
    rsize = rate_params_init.size
    asize = ages_idxs.size
    fsize = weight_params_init.size
    blocks = {
        "rates": [(False, True, True), slice(None, rsize)],
    }
    if asize:
        blocks["ages"] = [(True, False, True), slice(rsize, rsize + asize)]
    if fsize:
        blocks["weights"] = [
            (True, True, False),
            slice(rsize + asize, rsize + asize + fsize),
        ]

    for _ in range(max(0, int(max_refine))):
        cycle_start = current_loglik
        for fbools, fslice in blocks.values():
            rates_hat = _unpack_ordered_rate_params(current_params[:rsize])
            age_params_hat = current_params[rsize : rsize + asize]
            weights_hat, _ = _unpack_simplex_logits(
                current_params[rsize + asize : rsize + asize + fsize]
            )
            args = fbools + (
                rates_hat,
                age_params_hat,
                ages_init,
                ages_idxs,
                ages_bounds,
                children_map,
                edges,
                edata,
                weights_hat,
                valid_loglik,
                observation_mask,
            )
            ifit = minimize(
                fun=objective_discrete,
                x0=current_params[fslice],
                args=args,
                method="L-BFGS-B",
                bounds=bounds[fslice],
                options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
            )
            if float(ifit.fun) <= current_loglik:
                current_loglik = float(ifit.fun)
                current_params[fslice] = ifit.x
                fit = ifit
        if abs(cycle_start - current_loglik) < 1e-9:
            break
    converged = bool(fit.success)
    message = str(fit.message)
    invalid_objective = float(-(valid_loglik - INVALID_LOG_LIK_DROP))
    if current_loglik >= invalid_objective - 1e-9:
        converged = False
        message = "invalid objective plateau from infeasible start"
    return {
        "start": start,
        "objective": float(current_loglik),
        "converged": converged,
        "message": message,
        "nfev": int(getattr(fit, "nfev", -1)),
        "nit": int(getattr(fit, "nit", -1)),
        "params": current_params,
    }


@add_subpackage_method(TreeModAPI)
def edges_make_ultrametric_discrete(
    tree: ToyTree,
    ncategories: int,
    calibrations: Calibrations | None = None,
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 1e5,
    max_fun: int = 1e5,
    max_refine: int = 20,
    nstarts: int = 4,
    ncores: int = 1,
    seed: int | None = None,
    _observation_mask: np.ndarray | None = None,
) -> Union[ToyTree, dict[str, Any]]:
    """Return a tree made ultrametric under a branchwise finite-rate mixture.

    This variant fits ``ncategories`` discrete rate categories.

    Every branch likelihood is independently integrated over ordered rate
    categories using fitted simplex weights. Categories are not persistent
    assignments inherited along the tree.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree with non-ultrametric edge lengths.
    ncategories: int
        The number of discrete rate categories; cannot exceed the number
        of edges.
    calibrations: dict[int, (float, float)]
        A dict mapping node selectors (e.g., idx labels) to calibrated
        ages as a single value or a tuple of (min, max) age.
    full: bool
        If full=True a dictionary is returned with the modified tree,
        working log-likelihood, rates, weights, and optimizer metadata.
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
        as well as statistics on the model fit.

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
    >>> tree.mod.edges_make_ultrametric_discrete(tree, 2, full=True)
    >>> # {'model': 'discrete', 'pseudologlik': -82.42541, ...}

    """
    ncategories = _validate_ncategories(ncategories, tree.nedges)
    if calibrations is None:
        calibrations = {}
    calibrations = _normalize_calibrations(
        tree,
        calibrations,
        dist_floor=DIST_FLOOR,
    )

    # strict identity with clock model when ncategories == 1.
    if int(ncategories) == 1:
        cres = edges_make_ultrametric_clock(
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
            _observation_mask=_observation_mask,
        )
        if not full:
            return cres
        dres = dict(cres)
        dres["model"] = "discrete"
        dres["ncategories"] = 1
        dres["rates"] = [float(dres.pop("rate"))]
        dres["weights"] = [1.0]
        return dres

    # get init and fixed node ages that make tree ultrametric
    ages_init, _ = _get_init_ages(tree, calibrations)

    # get bounds on params that need to be inferred; are not fixed
    _, ages_bounds = _get_params_bounds(tree, calibrations)

    # get edges, dists and log-factorial-dists from rate-x-time edges
    edges = tree.get_edges("idx")
    dists_o = _validate_branch_lengths(tree)
    dists_lf = gammaln(dists_o + 1.0)
    edata = np.vstack([dists_o, dists_lf]).T
    observation_mask = _validate_observation_mask(_observation_mask, tree.nedges)

    # get starting rates as old/new edge dists. Then bin the rates into
    # ncategories, as we will infer N rates and assign edges to bins.
    rates_init = dists_o / (ages_init[edges[:, 1]] - ages_init[edges[:, 0]])
    rates_init = np.clip(rates_init, RATE_FLOOR, None)
    _div = 1 / (2 * ncategories)
    _cats = np.linspace(_div, 1 - _div, ncategories)
    rates_init = np.quantile(rates_init, _cats)

    weights_init = np.repeat(1 / ncategories, ncategories)

    # get indices of which node ages will be estimated
    ages_idxs = np.array(sorted(ages_bounds))
    children_map = _get_children_map_from_edges(edges)

    # slim bounds to only those needing to be estimated
    ages_bounds = [ages_bounds[i] for i in ages_idxs]
    age_params_init = _encode_age_params(
        ages_init,
        ages_idxs,
        ages_bounds,
        children_map,
        dist_floor=DIST_FLOOR,
    )
    rate_params_init = _pack_ordered_rates(rates_init)
    weight_params_init = _pack_simplex_weights(weights_init)
    bounds = [(None, None)] * (
        rate_params_init.size + age_params_init.size + weight_params_init.size
    )

    # get loglik at a valid starting params to scale neg dist penalty
    valid_loglik = _discrete_branch_pseudologlik(
        rates_init,
        ages_init,
        edges,
        edata,
        weights_init,
        None,
        observation_mask,
    )

    params = np.hstack(
        [
            rate_params_init,
            age_params_init,
            weight_params_init,
        ]
    )
    nstarts = max(1, int(nstarts))
    ncores = max(1, int(ncores))
    rng = np.random.default_rng(seed)
    payloads = []
    rsize = rate_params_init.size
    asize = ages_idxs.size
    fsize = weight_params_init.size
    for start in range(nstarts):
        sparams = params.copy()
        if start:
            sparams[:rsize] += rng.normal(0.0, 0.25, size=rsize)
            if asize:
                sparams[rsize : rsize + asize] += rng.normal(0.0, 0.25, size=asize)
            if fsize:
                sparams[rsize + asize :] += rng.normal(0.0, 0.25, size=fsize)
        payloads.append(
            dict(
                start=start,
                params=sparams,
                bounds=bounds,
                rates_init=rates_init,
                rate_params_init=rate_params_init,
                age_params_init=age_params_init,
                ages_init=ages_init,
                ages_idxs=ages_idxs,
                ages_bounds=ages_bounds,
                children_map=children_map,
                edges=edges,
                edata=edata,
                weights_init=weights_init,
                weight_params_init=weight_params_init,
                valid_loglik=valid_loglik,
                observation_mask=observation_mask,
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
        "discrete multistart best objective="
        f"{best['objective']}, start={best['start']}, nstarts={nstarts}"
    )

    # transform tree with new ages
    ages = _decode_age_params(
        current_params[rsize : rsize + asize],
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

    rates = _unpack_ordered_rate_params(current_params[:rsize])
    weights, _ = _unpack_simplex_logits(current_params[rsize + asize :])
    pseudologlik = _discrete_branch_pseudologlik(
        rates, ages, edges, edata, weights, valid_loglik, observation_mask
    )
    time_dists = ages[edges[:, 1]] - ages[edges[:, 0]]
    expected = time_dists * float(np.dot(weights, rates))

    # return as a tree or a dict
    if not full:
        return tree
    return {
        "model": "discrete",
        "pseudologlik": pseudologlik,
        "penalized_pseudologlik": pseudologlik,
        **_result_observation_metadata(),
        "nparams": len(bounds),
        "ncategories": ncategories,
        "rates": list(rates),
        "weights": list(weights),
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


def objective_discrete(
    params,
    fixed_rates,
    fixed_ages,
    fixed_weights,
    rates,
    age_params,
    ages_base,
    ages_idxs,
    ages_bounds,
    children_map,
    edges,
    edata,
    weights,
    valid_loglik,
    observation_mask,
):
    """Return neg log-likelihood under discrete model."""
    # [RATES]
    if fixed_ages and fixed_weights and not fixed_rates:
        assert params.size == rates.size
        ages_hat = _decode_age_params(
            age_params,
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
        rates_hat = _unpack_ordered_rate_params(params)
        weights_hat = weights
    # [AGES]
    elif fixed_rates and fixed_weights and not fixed_ages:
        assert params.size == ages_idxs.size
        rates_hat = rates
        ages_hat = _decode_age_params(
            params,
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
        weights_hat = weights
    # [WEIGHTS]
    elif fixed_rates and fixed_ages and not fixed_weights:
        assert params.size == weights.size - 1
        ages_hat = _decode_age_params(
            age_params,
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
        rates_hat = rates
        weights_hat, _ = _unpack_simplex_logits(params)
    else:
        wsize = weights.size - 1
        assert params.size == ages_idxs.size + rates.size + wsize
        rates_hat = _unpack_ordered_rate_params(params[: rates.size])
        ages_hat = _decode_age_params(
            params[rates.size : rates.size + ages_idxs.size],
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
        weights_hat, _ = _unpack_simplex_logits(params[-wsize:])

    # calculate log-likelihood
    args = (
        rates_hat,
        ages_hat,
        edges,
        edata,
        weights_hat,
        valid_loglik,
        observation_mask,
    )
    return -_discrete_branch_pseudologlik(*args)


def _discrete_branch_pseudologlik(
    rates_hat,
    ages_hat,
    edges,
    edata,
    weights_hat,
    valid_loglik,
    observation_mask=None,
) -> float:
    """Return the stable branchwise finite-mixture pseudologlikelihood."""
    if valid_loglik is None:
        valid_loglik = -1.0
    invalid_score = valid_loglik - INVALID_LOG_LIK_DROP

    # get dists given the new age estimates
    dists_hat = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]

    # return a poor but finite score for invalid geometry/weights.
    if np.any(dists_hat <= DIST_FLOOR):
        return invalid_score
    weights_hat = np.asarray(weights_hat, dtype=float)
    if np.any(~np.isfinite(weights_hat)) or np.any(weights_hat <= 0.0):
        return invalid_score
    if not np.isclose(weights_hat.sum(), 1.0, atol=1e-10, rtol=0.0):
        return invalid_score

    # get product of dists(time) and rates
    rates_hat = np.clip(np.asarray(rates_hat, dtype=float), RATE_FLOOR, None)
    pdists = dists_hat * rates_hat[:, np.newaxis]
    if np.any(pdists <= RATE_FLOOR) or np.any(~np.isfinite(pdists)):
        return invalid_score

    category_loglik = (
        edata[:, 0][np.newaxis, :] * np.log(pdists)
        - pdists
        - edata[:, 1][np.newaxis, :]
    )
    if np.any(~np.isfinite(category_loglik)):
        return invalid_score
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    branch_scores = logsumexp(
        category_loglik + np.log(weights_hat)[:, np.newaxis], axis=0
    )
    pseudologlik = np.sum(branch_scores[mask])
    return float(pseudologlik) if np.isfinite(pseudologlik) else invalid_score


if __name__ == "__main__":
    import numpy as np

    import toytree

    toytree.set_log_level("DEBUG")

    tree = get_tree_with_categorical_rates(ntips=50, nrates=2, seed=123)
    res = edges_make_ultrametric_discrete(
        tree,
        calibrations={-1: 1},
        ncategories=2,
        full=True,
        max_fun=1e6,
        max_iter=1e6,
        max_refine=50,
    )
    print(res)
    tree._draw_browser(tmpdir="~")
    res["tree"]._draw_browser(tmpdir="~")
    # c1, _, _ = tree.draw(ts='s', use_edge_lengths=True, scale_bar=True)
    # tree.write("/tmp/test.nwk")
