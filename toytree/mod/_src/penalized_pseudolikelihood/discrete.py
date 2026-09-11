#!/usr/bin/env python

"""Discrete-mixture branch-length pseudolikelihood fitting."""

import warnings
from typing import Any, Union

import numpy as np
from loguru import logger
from scipy.optimize import minimize
from scipy.special import gammaln, logsumexp

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_pseudolikelihood.clock import (
    _edges_make_ultrametric_clock as edges_make_ultrametric_clock,
)
from toytree.mod._src.penalized_pseudolikelihood.optimization import (
    assess_solution_stability,
    decode_age_params_with_jacobian,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    Calibrations,
    _decode_age_params,
    _encode_age_params,
    _finalize_ultrametric_ages,
    _get_children_map_from_edges,
    _get_init_ages,
    _get_params_bounds,
    _normalize_calibrations,
    _run_multistart,
    _validate_branch_lengths,
    _validate_ncategories,
)
from toytree.utils import ToytreeError

__all__ = ["edges_make_ultrametric_discrete"]
RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
INVALID_LOG_LIK_DROP = 1e6
MIXTURE_WEIGHT_BOUNDARY = 1e-6
MIXTURE_LOG_RATE_GAP_BOUNDARY = 1e-4
NORMALIZED_TIME_BOUNDARY = 100.0 * DIST_FLOOR
PROJECTED_GRADIENT_TOL = 1e-4
PARAMETER_BOUND = 30.0


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
    """Map a base log-rate and positive log gaps to ordered rates."""
    values = np.asarray(params, dtype=float)
    log_rates = np.empty(values.size, dtype=float)
    log_rates[0] = values[0]
    if values.size > 1:
        gaps = np.logaddexp(0.0, values[1:])
        log_rates[1:] = values[0] + np.cumsum(gaps)
    return np.exp(np.clip(log_rates, -700.0, 700.0))


def _unpack_ordered_rates_with_jacobian(
    params: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ordered rates and their scale-equivariant Jacobian."""
    values = np.asarray(params, dtype=float)
    rates = _unpack_ordered_rate_params(values)
    jacobian = np.zeros((values.size, values.size), dtype=float)
    jacobian[:, 0] = rates
    if values.size > 1:
        sigmoid = np.empty(values.size - 1, dtype=float)
        positive = values[1:] >= 0.0
        sigmoid[positive] = 1.0 / (1.0 + np.exp(-values[1:][positive]))
        exp_values = np.exp(values[1:][~positive])
        sigmoid[~positive] = exp_values / (1.0 + exp_values)
        for column, derivative in enumerate(sigmoid, start=1):
            jacobian[column:, column] = rates[column:] * derivative
    return rates, jacobian


def _pack_ordered_rates(rates: np.ndarray) -> np.ndarray:
    """Map sorted positive rates to base-log and log-gap parameters."""
    values = np.sort(np.asarray(rates, dtype=float))
    logs = np.log(np.clip(values, RATE_FLOOR, None))
    params = np.empty(values.size, dtype=float)
    params[0] = logs[0]
    if values.size > 1:
        gaps = np.clip(np.diff(logs), np.finfo(float).eps, None)
        params[1:] = gaps + np.log(-np.expm1(-gaps))
    return params


def _projected_gradient(
    params: np.ndarray,
    gradient: np.ndarray,
    bound: float = PARAMETER_BOUND,
) -> np.ndarray:
    """Return the gradient projected onto the optimizer's feasible box."""
    values = np.asarray(params, dtype=float)
    projected = np.asarray(gradient, dtype=float).copy()
    tolerance = 1e-8 * max(1.0, abs(float(bound)))
    at_lower = values <= -float(bound) + tolerance
    at_upper = values >= float(bound) - tolerance
    projected[at_lower & (projected > 0.0)] = 0.0
    projected[at_upper & (projected < 0.0)] = 0.0
    return projected


def _em_initialize_mixture(
    rates: np.ndarray,
    weights: np.ndarray,
    ages: np.ndarray,
    edges: np.ndarray,
    edata: np.ndarray,
    observation_mask: np.ndarray,
    max_iter: int = 250,
    tolerance: float = 1e-10,
) -> tuple[np.ndarray, np.ndarray, int, float]:
    """Optimize fractional-Poisson rates and weights at fixed node ages."""
    rates_hat = np.sort(np.clip(np.asarray(rates, dtype=float), RATE_FLOOR, None))
    weights_hat = np.clip(np.asarray(weights, dtype=float), np.finfo(float).tiny, None)
    weights_hat = weights_hat / weights_hat.sum()
    mask = np.asarray(observation_mask, dtype=bool)
    observed = np.asarray(edata[:, 0], dtype=float)[mask]
    log_factorials = np.asarray(edata[:, 1], dtype=float)[mask]
    times = (ages[edges[:, 1]] - ages[edges[:, 0]])[mask]
    if not observed.size or np.any(times <= DIST_FLOOR):
        return rates_hat, weights_hat, 0, -np.inf

    previous = -np.inf
    iterations = 0
    for iterations in range(1, max(1, int(max_iter)) + 1):
        means = rates_hat[:, None] * times[None, :]
        components = observed[None, :] * np.log(means) - means - log_factorials[None, :]
        log_joint = components + np.log(weights_hat)[:, None]
        branch_scores = logsumexp(log_joint, axis=0)
        responsibilities = np.exp(log_joint - branch_scores[None, :])

        component_mass = responsibilities.sum(axis=1)
        weights_new = np.clip(
            component_mass / observed.size, np.finfo(float).tiny, None
        )
        weights_new = weights_new / weights_new.sum()
        numerator = np.sum(responsibilities * observed[None, :], axis=1)
        denominator = np.sum(responsibilities * times[None, :], axis=1)
        rates_new = numerator / np.maximum(denominator, RATE_FLOOR)
        rates_new = np.clip(rates_new, RATE_FLOOR, None)
        order = np.argsort(rates_new, kind="stable")
        rates_hat = rates_new[order]
        weights_hat = weights_new[order]

        means = rates_hat[:, None] * times[None, :]
        components = observed[None, :] * np.log(means) - means - log_factorials[None, :]
        score = float(
            np.sum(
                logsumexp(
                    components + np.log(weights_hat)[:, None],
                    axis=0,
                )
            )
        )
        if np.isfinite(previous) and score - previous <= (
            float(tolerance) * max(1.0, abs(previous))
        ):
            previous = score
            break
        previous = score
    return rates_hat, weights_hat, iterations, float(previous)


def _mixture_boundary_diagnostics(
    rates: np.ndarray,
    weights: np.ndarray,
    ages: np.ndarray,
    edges: np.ndarray,
) -> dict[str, Any]:
    """Describe numerical category or branch-time boundary solutions."""
    rates_hat = np.asarray(rates, dtype=float)
    weights_hat = np.asarray(weights, dtype=float)
    log_rates = np.log(np.clip(rates_hat, RATE_FLOOR, None))
    gaps = np.diff(log_rates)
    minimum_weight = float(weights_hat.min())
    minimum_gap = float(gaps.min()) if gaps.size else None

    active_logs = log_rates[weights_hat > MIXTURE_WEIGHT_BOUNDARY]
    effective = 0
    previous = None
    for value in active_logs:
        if previous is None or float(value - previous) > MIXTURE_LOG_RATE_GAP_BOUNDARY:
            effective += 1
        previous = float(value)

    age_values = np.asarray(ages, dtype=float)
    times = age_values[edges[:, 1]] - age_values[edges[:, 0]]
    root_age = max(abs(float(age_values[-1])), DIST_FLOOR)
    minimum_normalized_time = float(times.min() / root_age)
    reasons = []
    if minimum_weight <= MIXTURE_WEIGHT_BOUNDARY:
        reasons.append("near_zero_weight")
    if gaps.size and float(minimum_gap) <= MIXTURE_LOG_RATE_GAP_BOUNDARY:
        reasons.append("coincident_rates")
    if minimum_normalized_time <= NORMALIZED_TIME_BOUNDARY:
        reasons.append("near_zero_branch_time")
    return {
        "mixture_identified": bool(effective == rates_hat.size),
        "effective_ncategories": int(effective),
        "boundary_solution": bool(reasons),
        "boundary_reasons": reasons,
        "minimum_weight": minimum_weight,
        "minimum_adjacent_log_rate_gap": minimum_gap,
        "minimum_normalized_branch_time": minimum_normalized_time,
        "mixture_weight_boundary": MIXTURE_WEIGHT_BOUNDARY,
        "mixture_log_rate_gap_boundary": MIXTURE_LOG_RATE_GAP_BOUNDARY,
        "normalized_time_boundary": NORMALIZED_TIME_BOUNDARY,
    }


def _mixture_objective_with_gradient(
    params: np.ndarray,
    ages_base: np.ndarray,
    ages_idxs: np.ndarray,
    ages_bounds: list[tuple[float, float]],
    children_map: dict[int, np.ndarray],
    edges: np.ndarray,
    edata: np.ndarray,
    observation_mask: np.ndarray,
    ncategories: int,
    valid_loglik: float,
) -> tuple[float, np.ndarray]:
    """Return joint fractional-Poisson mixture objective and gradient."""
    rsize = int(ncategories)
    asize = int(ages_idxs.size)
    rates, rate_jac = _unpack_ordered_rates_with_jacobian(params[:rsize])
    weights, _ = _unpack_simplex_logits(params[rsize + asize :])
    try:
        ages, age_jac = decode_age_params_with_jacobian(
            params[rsize : rsize + asize],
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
    except (ToytreeError, ValueError):
        return -(valid_loglik - INVALID_LOG_LIK_DROP), np.zeros_like(params)

    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    observed = edata[:, 0]
    means = rates[:, None] * times[None, :]
    if (
        np.any(times <= DIST_FLOOR)
        or np.any(means <= 0.0)
        or np.any(~np.isfinite(means))
        or np.any(weights <= 0.0)
    ):
        return -(valid_loglik - INVALID_LOG_LIK_DROP), np.zeros_like(params)

    components = observed[None, :] * np.log(means) - means - edata[:, 1][None, :]
    dlog_dmean = observed[None, :] / means - 1.0
    log_joint = components + np.log(weights)[:, None]
    branch_scores = logsumexp(log_joint, axis=0)
    responsibilities = np.exp(log_joint - branch_scores[None, :])
    mask = np.asarray(observation_mask, dtype=bool)
    loglik = float(np.sum(branch_scores[mask]))
    responsibilities[:, ~mask] = 0.0
    dlog_dmean[:, ~mask] = 0.0
    weighted_score = responsibilities * dlog_dmean

    rate_score = np.sum(weighted_score * times[None, :], axis=1)
    time_score = np.sum(weighted_score * rates[:, None], axis=0)
    age_score = np.zeros(ages.size, dtype=float)
    np.add.at(age_score, edges[:, 1], time_score)
    np.add.at(age_score, edges[:, 0], -time_score)
    weight_score = (
        np.sum(responsibilities[:-1], axis=1) - int(mask.sum()) * weights[:-1]
    )
    gradient = -np.concatenate(
        (rate_jac.T @ rate_score, age_jac.T @ age_score, weight_score)
    )
    if not np.isfinite(loglik) or np.any(~np.isfinite(gradient)):
        return -(valid_loglik - INVALID_LOG_LIK_DROP), np.zeros_like(params)
    return -loglik, gradient


def _run_joint_fit(x0, args, max_iter, max_fun):
    """Run the common unconstrained L-BFGS-B joint optimization."""
    return minimize(
        _mixture_objective_with_gradient,
        np.asarray(x0, dtype=float),
        args=args,
        method="L-BFGS-B",
        jac=True,
        bounds=[(-PARAMETER_BOUND, PARAMETER_BOUND)] * len(x0),
        options={
            "maxiter": int(max_iter),
            "maxfun": int(max_fun),
            "ftol": 1e-12,
            "gtol": 1e-6,
        },
    )


def _run_joint_fallback(x0, args, max_iter):
    """Run SLSQP after an unresolved L-BFGS-B line-search failure."""
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Values in x were outside bounds during a minimize step",
            category=RuntimeWarning,
            module="scipy.optimize._slsqp_py",
        )
        return minimize(
            _mixture_objective_with_gradient,
            np.asarray(x0, dtype=float),
            args=args,
            method="SLSQP",
            jac=True,
            bounds=[(-PARAMETER_BOUND, PARAMETER_BOUND)] * len(x0),
            options={
                "maxiter": int(max_iter),
                "ftol": 1e-10,
            },
        )


def _select_best_discrete_start(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return the best stationary fit unless a lower fit is unresolved."""
    finite = [
        result
        for result in results
        if np.isfinite(result.get("objective", float("inf")))
    ]
    if not finite:
        raise RuntimeError("all discrete multistarts failed")
    best_finite = min(finite, key=lambda result: float(result["objective"]))
    stationary = [result for result in finite if result.get("converged", False)]
    if not stationary:
        best_finite["unresolved_better_start"] = True
        return best_finite

    best_stationary = min(stationary, key=lambda result: float(result["objective"]))
    tolerance = 1e-4 + 1e-6 * max(1.0, abs(float(best_stationary["objective"])))
    if (
        not best_finite.get("converged", False)
        and float(best_finite["objective"])
        < float(best_stationary["objective"]) - tolerance
    ):
        best_finite["unresolved_better_start"] = True
        best_finite["message"] = (
            f"{best_finite['message']}; a nonstationary start has a "
            "materially better finalized objective"
        )
        return best_finite
    best_stationary["unresolved_better_start"] = False
    return best_stationary


def _fit_discrete_start(payload: dict[str, Any]) -> dict[str, Any]:
    """Optimize one start and define convergence by a final joint fit."""
    params = np.asarray(payload["params"], dtype=float)
    args = (
        payload["ages_init"],
        payload["ages_idxs"],
        payload["ages_bounds"],
        payload["children_map"],
        payload["edges"],
        payload["edata"],
        payload["observation_mask"],
        int(payload["rate_params_init"].size),
        float(payload["valid_loglik"]),
    )
    max_iter = int(payload["max_iter"])
    max_fun = int(payload["max_fun"])
    rsize = int(payload["rate_params_init"].size)
    asize = int(payload["ages_idxs"].size)
    fsize = int(payload["weight_params_init"].size)

    try:
        initial_ages = _decode_age_params(
            params[rsize : rsize + asize],
            payload["ages_init"],
            payload["ages_idxs"],
            payload["ages_bounds"],
            payload["children_map"],
            dist_floor=DIST_FLOOR,
        )
    except (ToytreeError, ValueError):
        initial_ages = np.asarray(payload["ages_init"], dtype=float)
    initial_rates = _unpack_ordered_rate_params(params[:rsize])
    initial_weights, _ = _unpack_simplex_logits(params[rsize + asize :])
    em_rates, em_weights, em_iterations, em_loglik = _em_initialize_mixture(
        initial_rates,
        initial_weights,
        initial_ages,
        payload["edges"],
        payload["edata"],
        payload["observation_mask"],
    )
    params[:rsize] = _pack_ordered_rates(em_rates)
    if fsize:
        params[rsize + asize :] = _pack_simplex_weights(em_weights)

    # First identify the mixture conditional on the starting chronogram. This
    # prevents a joint step from distorting ages before categories separate.
    mixture_indices = np.concatenate(
        (
            np.arange(rsize, dtype=int),
            np.arange(rsize + asize, rsize + asize + fsize, dtype=int),
        )
    )
    base = params.copy()

    def mixture_objective(values):
        candidate = base.copy()
        candidate[mixture_indices] = values
        value, gradient = _mixture_objective_with_gradient(candidate, *args)
        return value, gradient[mixture_indices]

    prefit = minimize(
        mixture_objective,
        params[mixture_indices],
        method="L-BFGS-B",
        jac=True,
        bounds=[(-PARAMETER_BOUND, PARAMETER_BOUND)] * mixture_indices.size,
        options={
            "maxiter": max_iter,
            "maxfun": max_fun,
            "ftol": 1e-12,
            "gtol": 1e-6,
        },
    )
    current = params.copy()
    if np.isfinite(prefit.fun):
        current[mixture_indices] = prefit.x
    fit = _run_joint_fit(current, args, max_iter, max_fun)
    total_nfev = int(getattr(prefit, "nfev", 0)) + int(getattr(fit, "nfev", 0))
    total_nit = int(getattr(prefit, "nit", 0)) + int(getattr(fit, "nit", 0))
    current = np.asarray(fit.x, dtype=float).copy()
    current_objective = float(fit.fun)
    blocks = [slice(0, rsize)]
    if asize:
        blocks.append(slice(rsize, rsize + asize))
    if fsize:
        blocks.append(slice(rsize + asize, rsize + asize + fsize))

    cycles = 0
    for _ in range(max(0, int(payload["max_refine"]))):
        cycle_start = current_objective
        for block in blocks:
            base = current.copy()

            def block_objective(values):
                candidate = base.copy()
                candidate[block] = values
                value, gradient = _mixture_objective_with_gradient(candidate, *args)
                return value, gradient[block]

            block_fit = minimize(
                block_objective,
                current[block],
                method="L-BFGS-B",
                jac=True,
                bounds=[(-PARAMETER_BOUND, PARAMETER_BOUND)] * current[block].size,
                options={
                    "maxiter": max_iter,
                    "maxfun": max_fun,
                    "ftol": 1e-12,
                    "gtol": 1e-6,
                },
            )
            total_nfev += int(getattr(block_fit, "nfev", 0))
            total_nit += int(getattr(block_fit, "nit", 0))
            tolerance = 1e-10 * max(1.0, abs(current_objective))
            if (
                np.isfinite(block_fit.fun)
                and float(block_fit.fun) <= current_objective + tolerance
            ):
                current[block] = block_fit.x
                current_objective = float(block_fit.fun)
        cycles += 1
        if abs(cycle_start - current_objective) <= 1e-9 * max(1.0, abs(cycle_start)):
            break

    authoritative = _run_joint_fit(current, args, max_iter, max_fun)
    total_nfev += int(getattr(authoritative, "nfev", 0))
    total_nit += int(getattr(authoritative, "nit", 0))
    current = np.asarray(authoritative.x, dtype=float).copy()
    attempts = [("L-BFGS-B", authoritative)]
    if not authoritative.success:
        retry = _run_joint_fit(current, args, max_iter * 4, max_fun * 4)
        total_nfev += int(getattr(retry, "nfev", 0))
        total_nit += int(getattr(retry, "nit", 0))
        attempts.append(("L-BFGS-B retry", retry))
        finite_attempts = [item for item in attempts if np.isfinite(item[1].fun)]
        if not any(item[1].success for item in finite_attempts):
            fallback_start = min(finite_attempts, key=lambda item: float(item[1].fun))[
                1
            ]
            fallback = _run_joint_fallback(
                np.asarray(fallback_start.x, dtype=float),
                args,
                max_iter * 4,
            )
            total_nfev += int(getattr(fallback, "nfev", 0))
            total_nit += int(getattr(fallback, "nit", 0))
            attempts.append(("SLSQP", fallback))

        finite_attempts = [item for item in attempts if np.isfinite(item[1].fun)]
        best_finite_method, best_finite = min(
            finite_attempts, key=lambda item: float(item[1].fun)
        )
        successful = [item for item in finite_attempts if item[1].success]
        if successful:
            best_success_method, best_success = min(
                successful, key=lambda item: float(item[1].fun)
            )
            tolerance = 1e-4 + 1e-6 * max(1.0, abs(float(best_success.fun)))
            if float(best_success.fun) <= float(best_finite.fun) + tolerance:
                optimizer_method = best_success_method
                authoritative = best_success
            else:
                optimizer_method = best_finite_method
                authoritative = best_finite
        else:
            optimizer_method = best_finite_method
            authoritative = best_finite
        current = np.asarray(authoritative.x, dtype=float).copy()
    else:
        optimizer_method = "L-BFGS-B"
    retries = len(attempts) - 1

    objective, gradient = _mixture_objective_with_gradient(current, *args)
    try:
        ages, _ = decode_age_params_with_jacobian(
            current[rsize : rsize + asize],
            payload["ages_init"],
            payload["ages_idxs"],
            payload["ages_bounds"],
            payload["children_map"],
            dist_floor=DIST_FLOOR,
        )
    except (ToytreeError, ValueError):
        ages = np.asarray(payload["ages_init"], dtype=float)
        objective = -(float(payload["valid_loglik"]) - INVALID_LOG_LIK_DROP)

    gradient_max_abs = float(np.max(np.abs(gradient))) if gradient.size else 0.0
    projected = _projected_gradient(current, gradient)
    projected_gradient_max_abs = (
        float(np.max(np.abs(projected))) if projected.size else 0.0
    )
    first_order_converged = bool(
        np.isfinite(objective) and projected_gradient_max_abs <= PROJECTED_GRADIENT_TOL
    )
    converged = bool(
        np.isfinite(objective) and (authoritative.success or first_order_converged)
    )
    message = str(authoritative.message)
    if first_order_converged and not authoritative.success:
        message = (
            "projected first-order convergence after line-search termination "
            f"(max|projected gradient|={projected_gradient_max_abs:.3g})"
        )
    invalid_objective = -(float(payload["valid_loglik"]) - INVALID_LOG_LIK_DROP)
    if objective >= invalid_objective - 1e-9:
        converged = False
        message = "invalid objective plateau from infeasible start"
    return {
        "start": int(payload["start"]),
        "objective": float(objective),
        "converged": converged,
        "message": message,
        "optimizer_method": optimizer_method,
        "nfev": total_nfev,
        "nit": total_nit,
        "refinement_cycles": cycles,
        "final_joint_converged": bool(authoritative.success or first_order_converged),
        "gradient_max_abs": gradient_max_abs,
        "projected_gradient_max_abs": projected_gradient_max_abs,
        "optimizer_retries": retries,
        "em_iterations": int(em_iterations),
        "em_loglik": float(em_loglik),
        "unresolved_better_start": False,
        "params": current,
        "ages": ages,
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
    nstarts: int = 8,
    ncores: int = 1,
    seed: int | None = None,
) -> Union[ToyTree, dict[str, Any]]:
    """Fit the chronos-compatible fractional-Poisson discrete mixture.

    Every branch likelihood is independently integrated over `ncategories`
    ordered rate categories using fitted simplex weights. Categories are not
    persistent assignments inherited along the tree. A fitted component can
    collapse to zero weight or coincide with another rate when the data
    support fewer than the requested number of categories. This is returned
    as a converged boundary solution with explicit diagnostics and a warning,
    rather than interpreted as support for all requested categories.

    Input branches may use any consistent additive unit, and fitted rates use
    that input unit per
    calibration-time unit. This model is invariant to calibration-time units
    but not to numerical rescaling of input branches, whose magnitude controls
    fractional-Poisson working information. For new analyses requiring an
    uncorrelated, scale-invariant rate model, use
    :func:`edges_make_ultrametric_uncorrelated_lognormal`.

    Parameters
    ----------
    tree: ToyTree
        A tree with finite, non-negative branch lengths in any consistent
        additive unit for which length is modeled as elapsed time times rate.
    ncategories: int
        The number of discrete rate categories; cannot exceed the number
        of edges.
    calibrations: dict[int, (float, float)]
        Internal-node ages or finite age intervals. Their unit becomes the
        output-tree time unit. Without calibrations, root age is fixed to one.
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
        )
        if not full:
            return cres
        dres = dict(cres)
        dres["model"] = "discrete"
        dres["ncategories"] = 1
        dres["requested_ncategories"] = 1
        dres["rates"] = [float(dres.pop("rate"))]
        dres["weights"] = [1.0]
        dres["branch_length_units"] = "input_tree_units"
        dres["calibration_time_unit_invariant"] = True
        dres["input_branch_scale_invariant"] = False
        ages = dres["tree"].get_node_data("height").to_numpy(dtype=float)
        dres.update(
            _mixture_boundary_diagnostics(
                np.asarray(dres["rates"]),
                np.asarray(dres["weights"]),
                ages,
                tree.get_edges("idx"),
            )
        )
        if dres["boundary_solution"]:
            logger.warning("One-category discrete fit reached a branch-time boundary.")
        return dres

    dists_o = _validate_branch_lengths(tree)
    fit_tree = tree

    # Initialize with a profiled strict-clock chronogram. This uses branch
    # information and is equivariant to both supported unit changes.
    ages_init, _ = _get_init_ages(fit_tree, calibrations)
    try:
        clock_start = edges_make_ultrametric_clock(
            fit_tree,
            calibrations=calibrations,
            full=True,
            inplace=False,
            max_iter=max_iter,
            max_fun=max_fun,
            max_refine=0,
            nstarts=1,
            ncores=1,
            seed=seed,
            _direct_age_fallback=False,
        )
        if clock_start["converged"]:
            ages_init = (
                clock_start["tree"].get_node_data("height").to_numpy(dtype=float)
            )
    except (ToytreeError, RuntimeError, ValueError):
        pass

    # Get age parameters, topology, and normalized working observations.
    _, ages_bounds = _get_params_bounds(fit_tree, calibrations)
    edges = fit_tree.get_edges("idx")
    dists_fit = _validate_branch_lengths(fit_tree)
    dists_lf = gammaln(dists_fit + 1.0)
    edata = np.vstack([dists_fit, dists_lf]).T
    observation_mask = np.ones(fit_tree.nedges, dtype=bool)

    # get starting rates as old/new edge dists. Then bin the rates into
    # ncategories, as we will infer N rates and assign edges to bins.
    times_init = ages_init[edges[:, 1]] - ages_init[edges[:, 0]]
    rates_init = dists_fit / times_init
    init_rate_floor = max(1e-8, 10.0 * RATE_FLOOR / float(times_init.min()))
    rates_init = np.clip(rates_init, init_rate_floor, None)
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
            # The first four starts deliberately emphasize different blocks;
            # later starts continue the same seeded stream with broad draws.
            schedules = (
                (0.75, 0.25, 0.75),
                (0.25, 0.75, 1.00),
                (1.00, 1.00, 1.00),
            )
            rate_scale, age_scale, weight_scale = (
                schedules[start - 1] if start <= len(schedules) else (1.00, 1.00, 1.00)
            )
            sparams[:rsize] += rng.normal(0.0, rate_scale, size=rsize)
            if asize:
                sparams[rsize : rsize + asize] += rng.normal(0.0, age_scale, size=asize)
            if fsize:
                sparams[rsize + asize :] += rng.normal(0.0, weight_scale, size=fsize)
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

    # Finalize and rescore every start before selecting the winner.
    for result in starts:
        if "ages" not in result or "params" not in result:
            continue
        try:
            finalized = _finalize_ultrametric_ages(
                fit_tree,
                result["ages"],
                calibrations=calibrations,
                dist_floor=DIST_FLOOR,
            )
            candidate = np.asarray(result["params"], dtype=float)
            candidate_rates = _unpack_ordered_rate_params(candidate[:rsize])
            candidate_weights, _ = _unpack_simplex_logits(candidate[rsize + asize :])
            candidate_loglik = _discrete_branch_pseudologlik(
                candidate_rates,
                finalized,
                edges,
                edata,
                candidate_weights,
                valid_loglik,
                observation_mask,
            )
            result["ages"] = finalized
            result["objective"] = -float(candidate_loglik)
        except (ToytreeError, ValueError) as exc:
            result["converged"] = False
            result["objective"] = float("inf")
            result["message"] = f"finalization failed: {exc}"

    best = _select_best_discrete_start(starts)
    current_params = best["params"]
    if not best["converged"]:
        logger.warning(f"Best multistart fit did not converge: {best['message']}")
    logger.debug(
        "discrete multistart best objective="
        f"{best['objective']}, start={best['start']}, nstarts={nstarts}"
    )

    # Every start has already been finalized and rescored in normalized units.
    ages_fit = np.asarray(best["ages"], dtype=float)
    rates_fit = _unpack_ordered_rate_params(current_params[:rsize])
    weights, _ = _unpack_simplex_logits(current_params[rsize + asize :])
    pseudologlik = _discrete_branch_pseudologlik(
        rates_fit,
        ages_fit,
        edges,
        edata,
        weights,
        valid_loglik,
        observation_mask,
    )
    ages = ages_fit
    rates = rates_fit
    time_dists = ages[edges[:, 1]] - ages[edges[:, 0]]
    expected = time_dists * float(np.dot(weights, rates))
    stability = assess_solution_stability(starts, best, ntips=fit_tree.ntips)
    stability["optimum_replicated"] = bool(stability["near_optimal_starts"] >= 2)
    if nstarts > 1 and not stability["optimum_replicated"]:
        logger.warning(
            "The best discrete-mixture optimum was found by only one start; "
            "increase nstarts before relying on this fit."
        )
    boundary = _mixture_boundary_diagnostics(
        rates_fit,
        weights,
        ages_fit,
        edges,
    )
    if boundary["boundary_solution"]:
        logger.warning(
            "Discrete mixture reached a numerical boundary "
            f"({', '.join(boundary['boundary_reasons'])}); "
            f"requested K={ncategories}, effective K="
            f"{boundary['effective_ncategories']}."
        )

    output_tree = tree.set_node_data("height", ages, inplace=inplace)

    # return as a tree or a dict
    if not full:
        return output_tree
    return {
        "model": "discrete",
        "pseudologlik": pseudologlik,
        "penalized_pseudologlik": pseudologlik,
        "observation_model": "fractional_poisson",
        "branch_length_units": "input_tree_units",
        "calibration_time_unit_invariant": True,
        "input_branch_scale_invariant": False,
        "nparams": len(bounds),
        "ncategories": ncategories,
        "requested_ncategories": ncategories,
        **boundary,
        "rates": list(rates),
        "weights": list(weights),
        "expected_branch_lengths": expected.tolist(),
        "observed_branch_lengths": dists_o.tolist(),
        "tree": output_tree,
        "converged": bool(best["converged"]),
        "optimizer_message": str(best["message"]),
        "optimizer_method": str(best.get("optimizer_method", "unknown")),
        "nfev": int(best.get("nfev", -1)),
        "nit": int(best.get("nit", -1)),
        "gradient_max_abs": best.get("gradient_max_abs"),
        "projected_gradient_max_abs": best.get("projected_gradient_max_abs"),
        "optimizer_retries": int(best.get("optimizer_retries", 0)),
        "em_iterations": int(best.get("em_iterations", 0)),
        "em_loglik": best.get("em_loglik"),
        "unresolved_better_start": bool(best.get("unresolved_better_start", False)),
        "refinement_cycles": int(best.get("refinement_cycles", 0)),
        "final_joint_converged": bool(best.get("final_joint_converged", False)),
        **stability,
        "nstarts": nstarts,
        "ncores": max(1, min(ncores, nstarts)),
        "best_start": int(best["start"]),
        "starts": [
            {
                "start": int(i["start"]),
                "objective": float(i["objective"]),
                "converged": bool(i["converged"]),
                "message": str(i["message"]),
                "optimizer_method": str(i.get("optimizer_method", "unknown")),
                "nfev": int(i.get("nfev", -1)),
                "nit": int(i.get("nit", -1)),
                "refinement_cycles": int(i.get("refinement_cycles", 0)),
                "final_joint_converged": bool(i.get("final_joint_converged", False)),
                "gradient_max_abs": i.get("gradient_max_abs"),
                "projected_gradient_max_abs": i.get("projected_gradient_max_abs"),
                "optimizer_retries": int(i.get("optimizer_retries", 0)),
                "em_iterations": int(i.get("em_iterations", 0)),
                "em_loglik": i.get("em_loglik"),
                "unresolved_better_start": bool(
                    i.get("unresolved_better_start", False)
                ),
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
    if np.any(pdists <= 0.0) or np.any(~np.isfinite(pdists)):
        return invalid_score

    observed = edata[:, 0]
    category_loglik = (
        observed[np.newaxis, :] * np.log(pdists) - pdists - edata[:, 1][np.newaxis, :]
    )
    if np.any(~np.isfinite(category_loglik)):
        return invalid_score
    mask = (
        np.ones(edges.shape[0], dtype=bool)
        if observation_mask is None
        else np.asarray(observation_mask, dtype=bool)
    )
    branch_scores = logsumexp(
        category_loglik + np.log(weights_hat)[:, np.newaxis], axis=0
    )
    pseudologlik = np.sum(branch_scores[mask])
    return float(pseudologlik) if np.isfinite(pseudologlik) else invalid_score
