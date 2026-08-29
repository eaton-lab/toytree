#!/usr/bin/env python

"""Independent branch-rate penalized branch-length pseudolikelihoods."""

from typing import Any, Union

import numpy as np
from loguru import logger
from scipy import stats
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
    _validate_lambda,
    _validate_observation_mask,
    get_tree_with_uncorrelated_rates,
)

__all__ = [
    "edges_make_ultrametric_relaxed",
    "edges_make_ultrametric_uncorrelated_lognormal",
]

RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
INVALID_LOG_LIK_DROP = 1e6


def _invalid_objective(valid_loglik: float) -> float:
    """Return the finite objective value used for invalid fits."""
    return float(-(valid_loglik - INVALID_LOG_LIK_DROP))


def _fit_independent_start(payload: dict[str, Any]) -> dict[str, Any]:
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
    lam = payload["lam"]
    valid_loglik = payload["valid_loglik"]
    observation_mask = payload["observation_mask"]
    max_iter = payload["max_iter"]
    max_fun = payload["max_fun"]
    max_refine = payload["max_refine"]
    model = payload["model"]

    invalid_objective = _invalid_objective(valid_loglik)
    fit = minimize(
        fun=objective_independent,
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
            lam,
            valid_loglik,
            observation_mask,
            model,
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
        age_seed = age_params_init + rng.normal(0.0, 0.25, size=age_params_init.size)
        params_seed = np.hstack(
            [_pack_log_rates(rates_seed, rate_floor=RATE_FLOOR), age_seed]
        )
        refit = minimize(
            fun=objective_independent,
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
                lam,
                valid_loglik,
                observation_mask,
                model,
            ),
            method="L-BFGS-B",
            bounds=bounds,
            options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
        )
        if refit.fun < fit.fun:
            fit = refit

    current_loglik = float(fit.fun)
    current_params = fit.x.copy()
    rsize = rates_init.size
    asize = ages_idxs.size
    blocks = {
        "rates": [(False, True), slice(None, rsize)],
    }
    if asize:
        blocks["ages"] = [(True, False), slice(rsize, rsize + asize)]
    for _ in range(max(0, int(max_refine))):
        cycle_start = current_loglik
        for fbools, fslice in blocks.values():
            rates_hat = _unpack_log_rates(current_params[:rsize])
            age_params_hat = current_params[rsize : rsize + asize]
            args = fbools + (
                rates_hat,
                age_params_hat,
                ages_init,
                ages_idxs,
                ages_bounds,
                children_map,
                edges,
                edata,
                lam,
                valid_loglik,
                observation_mask,
                model,
            )
            ifit = minimize(
                fun=objective_independent,
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


def _edges_make_ultrametric_independent(
    tree: ToyTree,
    model: str,
    lam: float,
    calibrations: Calibrations | None = None,
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 1e5,
    max_fun: int = 1e5,
    max_refine: int = 20,
    nstarts: int = 1,
    ncores: int = 1,
    seed: int | None = None,
    _observation_mask: np.ndarray | None = None,
) -> Union[ToyTree, dict[str, Any]]:
    """Return a tree fitted with the selected independent-rate penalty.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree with non-ultrametric edge lengths.
    model: {"relaxed", "uncorrelated_lognormal"}
        Independent branch-rate penalty model.
    lam: float
        Positive multiplier on the selected rate-distribution penalty.
    calibrations: dict[int, (float, float)]
        A dict mapping node selectors (e.g., idx labels) to calibrated
        ages as a single value or a tuple of (min, max) age.
    full: bool
        If full=True a dictionary is returned with the modified tree,
        raw and penalized working log-likelihoods and penalty metadata.
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
        raw and penalized working log-likelihoods, penalty, and rates.
    """
    lam = _validate_lambda(lam)
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
    dists_lf = gammaln(dists_o + 1.0)
    edata = np.vstack([dists_o, dists_lf]).T
    observation_mask = _validate_observation_mask(_observation_mask, tree.nedges)

    # get starting rates as old/new edge dists.
    rates_init = dists_o / (ages_init[edges[:, 1]] - ages_init[edges[:, 0]])
    rates_init = np.clip(rates_init, RATE_FLOOR, None)

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
        ages_init,
        ages_idxs,
        ages_bounds,
        children_map,
        dist_floor=DIST_FLOOR,
    )
    bounds = rates_bounds + [(None, None)] * age_params_init.size

    # get loglik at a valid starting params to scale neg dist penalty
    valid_loglik = _independent_branch_pseudologlik(
        rates_init, ages_init, edges, edata, lam, None, observation_mask, model
    )

    params = np.hstack(
        [_pack_log_rates(rates_init, rate_floor=RATE_FLOOR), age_params_init]
    )
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
                sparams[rsize : rsize + asize] += rng.normal(0.0, 0.25, size=asize)
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
                lam=lam,
                valid_loglik=valid_loglik,
                observation_mask=observation_mask,
                max_iter=max_iter,
                max_fun=max_fun,
                max_refine=max_refine,
                model=model,
            )
        )
    starts = _run_multistart(_fit_independent_start, payloads, ncores=ncores)
    best = _select_best_multistart(starts)
    current_params = best["params"]
    if not best["converged"]:
        logger.warning(f"Best multistart fit did not converge: {best['message']}")
    logger.debug(
        f"{model} multistart best objective="
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

    # get rates params
    rates = _unpack_log_rates(current_params[:rsize])

    penalized_pseudologlik = _independent_branch_pseudologlik(
        rates, ages, edges, edata, lam, valid_loglik, observation_mask, model
    )
    pseudologlik = _independent_branch_pseudologlik(
        rates, ages, edges, edata, 0.0, valid_loglik, observation_mask, model
    )
    penalty = _rate_penalty(rates, model)
    time_dists = ages[edges[:, 1]] - ages[edges[:, 0]]
    expected = time_dists * rates

    # return as a tree or a dict
    if not full:
        return tree
    return {
        "model": model,
        "pseudologlik": pseudologlik,
        "penalized_pseudologlik": penalized_pseudologlik,
        **_result_observation_metadata(),
        "penalty": penalty,
        "penalty_model": (
            "summed_centered_log_rate_dispersion"
            if model == "uncorrelated_lognormal"
            else "chronos_gamma_cdf"
        ),
        "scale_invariant": model == "uncorrelated_lognormal",
        "lam": lam,
        "nparams": len(bounds),
        "rates": list(rates),
        "profiled_mean_rate": (
            float(np.exp(np.mean(np.log(rates))))
            if model == "uncorrelated_lognormal"
            else float(np.mean(rates))
        ),
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


@add_subpackage_method(TreeModAPI)
def edges_make_ultrametric_uncorrelated_lognormal(
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
    _observation_mask: np.ndarray | None = None,
) -> Union[ToyTree, dict[str, Any]]:
    """Fit independent branch rates with a centered lognormal penalty.

    This scale-invariant penalized/MAP-like model estimates one rate per
    branch and profiles their common mean on the log scale.
    """
    return _edges_make_ultrametric_independent(
        tree=tree,
        model="uncorrelated_lognormal",
        lam=lam,
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


@add_subpackage_method(TreeModAPI)
def edges_make_ultrametric_relaxed(
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
    _observation_mask: np.ndarray | None = None,
) -> Union[ToyTree, dict[str, Any]]:
    """Fit ape::chronos-compatible non-correlated relaxed rates.

    The penalty compares the empirical CDF of raw branch rates with a Gamma
    CDF whose shape is the mean raw rate and whose scale is one. Consequently,
    this model is intentionally not invariant to a change of time units.
    """
    return _edges_make_ultrametric_independent(
        tree=tree,
        model="relaxed",
        lam=lam,
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


def _uncorrelated_lognormal_penalty(rates_hat: np.ndarray) -> float:
    """Return summed centered log-rate dispersion."""
    log_rates = np.log(np.clip(np.asarray(rates_hat, dtype=float), RATE_FLOOR, None))
    centered = log_rates - float(np.mean(log_rates))
    return float(np.sum(centered * centered))


def _relaxed_penalty(rates_hat: np.ndarray) -> float:
    """Return the Gamma-CDF penalty used by ape::chronos model=relaxed."""
    rates = np.clip(np.asarray(rates_hat, dtype=float), RATE_FLOOR, None)
    alpha = max(float(np.mean(rates)), RATE_FLOOR)
    pcdf = stats.gamma.cdf(np.sort(rates), a=alpha, scale=1.0)
    ecdf = np.arange(1, rates.size + 1, dtype=float) / rates.size
    return float(np.sum((ecdf - pcdf) ** 2))


def _rate_penalty(rates_hat: np.ndarray, model: str) -> float:
    """Return the configured independent-rate penalty."""
    if model == "uncorrelated_lognormal":
        return _uncorrelated_lognormal_penalty(rates_hat)
    if model == "relaxed":
        return _relaxed_penalty(rates_hat)
    raise ValueError(f"unsupported independent-rate model: {model!r}")


def _independent_branch_pseudologlik(
    rates_hat,
    ages_hat,
    edges,
    edata,
    lam,
    valid_loglik,
    observation_mask=None,
    model="uncorrelated_lognormal",
) -> float:
    """Return independent-rate penalized branch-length pseudologlikelihood."""
    if valid_loglik is None:
        valid_loglik = -1.0

    # get dists given the new age estimates
    dists_hat = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]

    # Return very poor likelihood for invalid geometry to keep objective finite.
    if np.any(dists_hat <= DIST_FLOOR):
        return valid_loglik - INVALID_LOG_LIK_DROP

    # get product of dists(time) and rates
    rates_hat = np.clip(rates_hat, RATE_FLOOR, None)
    pdists = dists_hat * rates_hat
    if np.any(pdists <= RATE_FLOOR) or np.any(~np.isfinite(pdists)):
        return valid_loglik - INVALID_LOG_LIK_DROP

    # calculate loglik
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    terms = edata[:, 0] * np.log(pdists) - pdists - edata[:, 1]
    pseudologlik = np.sum(terms[mask])
    if not np.isfinite(pseudologlik):
        return valid_loglik - INVALID_LOG_LIK_DROP
    penalty = _rate_penalty(rates_hat, model)
    if not np.isfinite(penalty):
        return valid_loglik - INVALID_LOG_LIK_DROP
    return float(pseudologlik - lam * penalty)


def objective_independent(
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
    lam,
    valid_loglik,
    observation_mask,
    model,
):
    """Return negative penalized pseudologlikelihood under this model."""
    # [RATES] optimize rates while keeping ages fixed
    if fixed_ages and not fixed_rates:
        assert params.size == rates.size
        ages_hat = _decode_age_params(
            age_params,
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
        rates_hat = _unpack_log_rates(params)
    # [AGES] optimize ages while keeping rates fixed
    elif fixed_rates and not fixed_ages:
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
    # joint optimize rates and ages
    else:
        assert params.size == ages_idxs.size + rates.size
        rates_hat = _unpack_log_rates(params[: rates.size])
        ages_hat = _decode_age_params(
            params[rates.size :],
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
    return -_independent_branch_pseudologlik(
        rates_hat,
        ages_hat,
        edges,
        edata,
        lam,
        valid_loglik,
        observation_mask,
        model,
    )


if __name__ == "__main__":
    import numpy as np

    import toytree

    toytree.set_log_level("DEBUG")

    tree = get_tree_with_uncorrelated_rates(ntips=50, mean=3, sigma=3, seed=123)
    res = edges_make_ultrametric_uncorrelated_lognormal(
        tree,
        lam=0.5,
        calibrations={-1: 50},
        full=True,
        max_fun=1e6,
        max_iter=1e6,
        max_refine=50,
    )
    print(res)

    tree._draw_browser(tmpdir="~")
    res["tree"]._draw_browser(tmpdir="~")
