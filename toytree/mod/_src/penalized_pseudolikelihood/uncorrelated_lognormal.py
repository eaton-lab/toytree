#!/usr/bin/env python

"""Independent branch-rate penalized branch-length pseudolikelihoods."""

from typing import Any, Union

import numpy as np
from loguru import logger
from scipy.optimize import OptimizeResult, minimize
from scipy.special import gammaln

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_pseudolikelihood.clock import (
    _edges_make_ultrametric_clock as edges_make_ultrametric_clock,
)
from toytree.mod._src.penalized_pseudolikelihood.optimization import (
    assess_solution_stability,
    decode_age_params_with_jacobian,
    direct_age_linear_constraint,
    minimize_profiled_ages,
    optimizer_stopped_at_limit,
    projected_gradient_max_abs,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    Calibrations,
    _decode_age_params,
    _encode_age_params,
    _finalize_fit_result,
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
)
from toytree.utils import ToytreeError

__all__ = [
    "edges_make_ultrametric_uncorrelated_lognormal",
]

RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
INVALID_LOG_LIK_DROP = 1e6


def _validate_ucln_warm_start(
    values: Any,
    size: int,
    name: str,
    *,
    positive: bool,
) -> np.ndarray | None:
    """Return one validated private continuation vector."""
    if values is None:
        return None
    array = np.asarray(values, dtype=float)
    if array.shape != (size,) or np.any(~np.isfinite(array)):
        raise ValueError(f"{name} must contain {size} finite values.")
    if positive and np.any(array <= 0.0):
        raise ValueError(f"{name} values must be strictly positive.")
    return array.copy()


def _invalid_objective(valid_loglik: float) -> float:
    """Return the finite objective value used for invalid fits."""
    return float(-(valid_loglik - INVALID_LOG_LIK_DROP))


def _ucln_penalty_gradient(log_rates: np.ndarray) -> np.ndarray:
    """Return the centered log-rate penalty gradient by log rate."""
    values = np.asarray(log_rates, dtype=float)
    return 2.0 * (values - float(np.mean(values)))


def _ucln_rate_objective_with_gradient(
    log_rates: np.ndarray,
    ages_hat: np.ndarray,
    edges: np.ndarray,
    edata: np.ndarray,
    lam: float,
    valid_loglik: float,
    observation_mask: np.ndarray,
) -> tuple[float, np.ndarray]:
    """Return the fixed-chronogram UCLN objective and log-rate gradient."""
    log_rates = np.asarray(log_rates, dtype=float)
    rates_hat = _unpack_log_rates(log_rates)
    objective = -_independent_branch_pseudologlik(
        rates_hat,
        ages_hat,
        edges,
        edata,
        lam,
        valid_loglik,
        observation_mask,
    )
    times = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    expected = rates_hat * times
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    if (
        not np.isfinite(objective)
        or np.any(times < DIST_FLOOR)
        or np.any(expected <= 0.0)
        or np.any(~np.isfinite(expected))
    ):
        return float(objective), np.zeros_like(log_rates)
    data_gradient = np.zeros(log_rates.size, dtype=float)
    data_gradient[mask] = expected[mask] - edata[mask, 0]
    gradient = data_gradient + lam * _ucln_penalty_gradient(log_rates)
    return float(objective), gradient


def _fit_profiled_ucln_rates(
    log_rates_init: np.ndarray,
    ages_hat: np.ndarray,
    rate_bounds: list[tuple[float | None, float | None]],
    edges: np.ndarray,
    edata: np.ndarray,
    lam: float,
    valid_loglik: float,
    observation_mask: np.ndarray,
    max_iter: int,
    max_fun: int,
) -> dict[str, Any]:
    """Solve the strictly convex conditional UCLN log-rate problem."""
    lower = np.array(
        [-np.inf if bound[0] is None else float(bound[0]) for bound in rate_bounds]
    )
    upper = np.array(
        [np.inf if bound[1] is None else float(bound[1]) for bound in rate_bounds]
    )
    params = np.clip(np.asarray(log_rates_init, dtype=float), lower, upper)
    objective, gradient = _ucln_rate_objective_with_gradient(
        params,
        ages_hat,
        edges,
        edata,
        lam,
        valid_loglik,
        observation_mask,
    )
    nfev = 1
    nit = 0
    message = "conditional rate Newton iteration limit reached"
    converged = False
    times = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    max_newton_iter = max(1, min(int(max_iter), int(max_fun), 500))
    for iteration in range(max_newton_iter):
        nit = iteration + 1
        projected = projected_gradient_max_abs(params, gradient, rate_bounds)
        if projected <= 1e-8:
            converged = True
            message = "conditional rate projected gradient converged"
            break

        at_lower = (params <= lower + 1e-10) & (gradient > 0.0)
        at_upper = (params >= upper - 1e-10) & (gradient < 0.0)
        free = ~(at_lower | at_upper)
        direction = np.zeros_like(params)
        if np.any(free):
            expected = np.exp(params) * times
            diagonal = 2.0 * lam + np.where(mask, expected, 0.0)
            inv_diagonal = 1.0 / diagonal[free]
            free_gradient = gradient[free]
            coefficient = 2.0 * lam / params.size
            denominator = 1.0 - coefficient * float(np.sum(inv_diagonal))
            base = inv_diagonal * free_gradient
            if denominator > 1e-12:
                solved = base + (
                    coefficient * inv_diagonal * float(np.sum(base)) / denominator
                )
                direction[free] = -solved
            else:
                direction[free] = -free_gradient / diagonal[free]

        slope = float(np.dot(gradient, direction))
        if not np.isfinite(slope) or slope >= 0.0:
            scale = np.maximum(
                1.0,
                2.0 * lam + np.where(mask, np.exp(params) * times, 0.0),
            )
            direction = -gradient / scale
            direction[at_lower | at_upper] = 0.0

        accepted = False
        step_scale = 1.0
        for _ in range(60):
            candidate = np.clip(params + step_scale * direction, lower, upper)
            step = candidate - params
            if float(np.max(np.abs(step))) <= 1e-14:
                break
            candidate_objective, candidate_gradient = (
                _ucln_rate_objective_with_gradient(
                    candidate,
                    ages_hat,
                    edges,
                    edata,
                    lam,
                    valid_loglik,
                    observation_mask,
                )
            )
            nfev += 1
            armijo = objective + 1e-4 * float(np.dot(gradient, step))
            if np.isfinite(candidate_objective) and candidate_objective <= armijo:
                params = candidate
                objective = float(candidate_objective)
                gradient = np.asarray(candidate_gradient, dtype=float)
                accepted = True
                break
            step_scale *= 0.5
        if not accepted:
            message = "conditional rate Newton line search stalled"
            break

    projected = projected_gradient_max_abs(params, gradient, rate_bounds)
    if projected <= 1e-6:
        converged = True
        if "converged" not in message:
            message = "conditional rate projected gradient converged"
    return {
        "params": params,
        "objective": float(objective),
        "converged": bool(converged),
        "message": message,
        "projected_gradient_max_abs": float(projected),
        "nfev": int(nfev),
        "nit": int(nit),
    }


class _ProfiledUCLNObjective:
    """Profile rates while optimizing node ages under linear constraints."""

    def __init__(
        self,
        log_rates_init: np.ndarray,
        rate_bounds: list[tuple[float | None, float | None]],
        ages_base: np.ndarray,
        ages_idxs: np.ndarray,
        edges: np.ndarray,
        edata: np.ndarray,
        lam: float,
        valid_loglik: float,
        observation_mask: np.ndarray,
        max_iter: int,
        max_fun: int,
    ) -> None:
        self.log_rates = np.asarray(log_rates_init, dtype=float).copy()
        self.rate_bounds = rate_bounds
        self.ages_base = ages_base
        self.ages_idxs = ages_idxs
        self.edges = edges
        self.edata = edata
        self.lam = lam
        self.valid_loglik = valid_loglik
        self.observation_mask = observation_mask
        self.max_iter = max_iter
        self.max_fun = max_fun
        self.total_rate_nfev = 0
        self.total_rate_nit = 0
        self.evaluations = 0
        self.all_rate_solves_converged = True
        self.rate_gradient_max_abs = float("inf")
        self._cached_age_values: np.ndarray | None = None
        self._cached_result: tuple[float, np.ndarray] | None = None

    def __call__(self, age_values: np.ndarray) -> tuple[float, np.ndarray]:
        """Return the rate-profiled objective and raw-age gradient."""
        age_values = np.asarray(age_values, dtype=float)
        if self._cached_age_values is not None and np.array_equal(
            age_values, self._cached_age_values
        ):
            assert self._cached_result is not None
            return self._cached_result
        ages_hat = np.asarray(self.ages_base, dtype=float).copy()
        ages_hat[self.ages_idxs] = age_values
        rate_fit = _fit_profiled_ucln_rates(
            self.log_rates,
            ages_hat,
            self.rate_bounds,
            self.edges,
            self.edata,
            self.lam,
            self.valid_loglik,
            self.observation_mask,
            self.max_iter,
            self.max_fun,
        )
        self.evaluations += 1
        self.total_rate_nfev += int(rate_fit["nfev"])
        self.total_rate_nit += int(rate_fit["nit"])
        self.all_rate_solves_converged &= bool(rate_fit["converged"])
        self.rate_gradient_max_abs = float(rate_fit["projected_gradient_max_abs"])
        self.log_rates = np.asarray(rate_fit["params"], dtype=float)
        rates_hat = _unpack_log_rates(self.log_rates)
        objective = float(rate_fit["objective"])
        times = ages_hat[self.edges[:, 1]] - ages_hat[self.edges[:, 0]]
        expected = rates_hat * times
        mask = _validate_observation_mask(
            self.observation_mask,
            self.edges.shape[0],
        )
        if (
            not np.isfinite(objective)
            or np.any(times < DIST_FLOOR)
            or np.any(expected <= 0.0)
        ):
            gradient = np.zeros(age_values.size, dtype=float)
        else:
            data_gradient = np.zeros(self.edges.shape[0], dtype=float)
            data_gradient[mask] = expected[mask] - self.edata[mask, 0]
            time_gradient = np.zeros(self.edges.shape[0], dtype=float)
            time_gradient[mask] = data_gradient[mask] / times[mask]
            age_gradient = np.zeros(ages_hat.size, dtype=float)
            np.add.at(age_gradient, self.edges[:, 1], time_gradient)
            np.add.at(age_gradient, self.edges[:, 0], -time_gradient)
            gradient = age_gradient[self.ages_idxs]
        self._cached_age_values = age_values.copy()
        self._cached_result = (objective, np.asarray(gradient, dtype=float))
        return self._cached_result


def objective_ucln_with_gradient(
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
):
    """Return the UCLN negative objective and its analytic gradient."""
    rsize = rates.size
    asize = ages_idxs.size
    age_jacobian = None
    if fixed_ages and not fixed_rates:
        log_rates = np.asarray(params, dtype=float)
        rates_hat = _unpack_log_rates(log_rates)
        ages_hat = _decode_age_params(
            age_params,
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
    elif fixed_rates and not fixed_ages:
        log_rates = np.log(np.clip(rates, RATE_FLOOR, None))
        rates_hat = rates
        ages_hat, age_jacobian = decode_age_params_with_jacobian(
            params,
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
    else:
        log_rates = np.asarray(params[:rsize], dtype=float)
        rates_hat = _unpack_log_rates(log_rates)
        ages_hat, age_jacobian = decode_age_params_with_jacobian(
            params[rsize : rsize + asize],
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )

    objective = -_independent_branch_pseudologlik(
        rates_hat,
        ages_hat,
        edges,
        edata,
        lam,
        valid_loglik,
        observation_mask,
    )
    times = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    expected = rates_hat * times
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    if (
        not np.isfinite(objective)
        or np.any(times < DIST_FLOOR)
        or np.any(expected <= 0.0)
        or np.any(~np.isfinite(expected))
    ):
        return float(objective), np.zeros_like(params, dtype=float)

    data_gradient = np.zeros(rsize, dtype=float)
    data_gradient[mask] = expected[mask] - edata[mask, 0]
    rate_gradient = data_gradient + lam * _ucln_penalty_gradient(log_rates)
    if fixed_ages and not fixed_rates:
        return float(objective), rate_gradient

    time_gradient = np.zeros(rsize, dtype=float)
    time_gradient[mask] = data_gradient[mask] / times[mask]
    age_gradient = np.zeros(ages_hat.size, dtype=float)
    np.add.at(age_gradient, edges[:, 1], time_gradient)
    np.add.at(age_gradient, edges[:, 0], -time_gradient)
    age_param_gradient = age_jacobian.T @ age_gradient
    if fixed_rates and not fixed_ages:
        return float(objective), age_param_gradient
    return float(objective), np.hstack([rate_gradient, age_param_gradient])


def _fit_ucln_start(payload: dict[str, Any]) -> dict[str, Any]:
    """Fit one UCLN start by profiling rates before a joint polish."""
    start = int(payload["start"])
    params = np.asarray(payload["params"], dtype=float)
    bounds = payload["bounds"]
    rates_init = payload["rates_init"]
    ages_init = payload["ages_init"]
    ages_idxs = payload["ages_idxs"]
    ages_bounds = payload["ages_bounds"]
    children_map = payload["children_map"]
    edges = payload["edges"]
    edata = payload["edata"]
    lam = payload["lam"]
    valid_loglik = payload["valid_loglik"]
    observation_mask = payload["observation_mask"]
    max_iter = int(payload["max_iter"])
    max_fun = int(payload["max_fun"])
    retry_multiplier = int(payload["retry_multiplier"])
    rsize = rates_init.size
    asize = ages_idxs.size
    rate_bounds = bounds[:rsize]
    # Start ages are constructed and validated in the parent process. Do not
    # round-trip them through the legacy unconstrained transform here. On
    # zero-rich trees, an otherwise valid near-boundary age can saturate the
    # sigmoid during that round trip and make an ancestor interval appear
    # empty before the profiled optimizer performs a single evaluation.
    age_start_full = np.asarray(payload["age_start_ages"], dtype=float)
    age_start = age_start_full[ages_idxs]
    profile = _ProfiledUCLNObjective(
        params[:rsize],
        rate_bounds,
        ages_init,
        ages_idxs,
        edges,
        edata,
        lam,
        valid_loglik,
        observation_mask,
        max_iter,
        max_fun,
    )
    linear_constraint = direct_age_linear_constraint(
        ages_init,
        ages_idxs,
        edges,
    )
    constraints = () if linear_constraint == () else (linear_constraint,)

    optimizer_retries = 0
    outer_nfev = 0
    outer_nit = 0
    if asize:
        outer = minimize_profiled_ages(
            profile,
            age_start,
            ages_bounds,
            constraints,
            max_iter,
            1e-10,
        )
        outer_nfev += int(getattr(outer, "nfev", 0))
        outer_nit += int(getattr(outer, "nit", 0))
        if not outer.success and retry_multiplier > 1:
            optimizer_retries += 1
            retry = minimize_profiled_ages(
                profile,
                np.asarray(outer.x, dtype=float),
                ages_bounds,
                constraints,
                max_iter * retry_multiplier,
                1e-12,
            )
            outer_nfev += int(getattr(retry, "nfev", 0))
            outer_nit += int(getattr(retry, "nit", 0))
            if np.isfinite(retry.fun) and float(retry.fun) <= float(outer.fun):
                outer = retry
        age_values = np.asarray(outer.x, dtype=float)
        profiled_objective, _ = profile(age_values)
        outer_success = bool(outer.success)
        outer_message = str(outer.message)
    else:
        age_values = age_start
        profiled_objective, _ = profile(age_values)
        outer_success = bool(profile.rate_gradient_max_abs <= 1e-6)
        outer_message = "all ages fixed; optimized conditional rates"
    profiled_ages = np.asarray(ages_init, dtype=float).copy()
    profiled_ages[ages_idxs] = age_values
    age_params_hat = _encode_age_params(
        profiled_ages,
        ages_idxs,
        ages_bounds,
        children_map,
        dist_floor=DIST_FLOOR,
    )

    current_params = np.hstack([profile.log_rates, age_params_hat])
    current_objective = float(profiled_objective)
    joint_args = (
        False,
        False,
        rates_init,
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
    )
    joint_polish_error = None
    try:
        polish = minimize(
            fun=objective_ucln_with_gradient,
            x0=current_params,
            args=joint_args,
            method="L-BFGS-B",
            jac=True,
            bounds=bounds,
            options=dict(
                maxiter=max_iter,
                maxfun=max_fun,
                ftol=np.finfo(float).eps,
                gtol=1e-7,
                maxls=100,
            ),
        )
    except ToytreeError as exc:
        # A line-search trial can saturate the legacy transformed-age
        # coordinates even though the direct-age profiled solution is valid.
        # Treat this only as an unavailable optional polish, not as a failed
        # profiled fit.
        joint_polish_error = str(exc)
        polish = OptimizeResult(
            x=current_params.copy(),
            fun=current_objective,
            success=False,
            message=f"joint-polish age transform was unavailable: {exc}",
            nfev=0,
            nit=0,
            jac=np.array([], dtype=float),
        )
    joint_nfev = int(getattr(polish, "nfev", 0))
    joint_nit = int(getattr(polish, "nit", 0))
    polish_objective = float(polish.fun)
    tolerance = 1e-10 * max(1.0, abs(current_objective))
    polish_is_finite = bool(
        np.isfinite(polish_objective) and np.all(np.isfinite(polish.x))
    )
    polish_did_not_worsen = bool(
        polish_is_finite and polish_objective <= current_objective + tolerance
    )
    if polish_did_not_worsen:
        current_objective = polish_objective
        current_params = np.asarray(polish.x, dtype=float).copy()

    if (
        not polish.success
        and (
            optimizer_stopped_at_limit(polish.message)
            or "ABNORMAL" in str(polish.message).upper()
        )
        and retry_multiplier > 1
    ):
        optimizer_retries += 1
        retry_start_objective = current_objective
        retry = minimize(
            fun=objective_ucln_with_gradient,
            x0=current_params,
            args=joint_args,
            method="L-BFGS-B",
            jac=True,
            bounds=bounds,
            options=dict(
                maxiter=max_iter * retry_multiplier,
                maxfun=max_fun * retry_multiplier,
                ftol=np.finfo(float).eps,
                gtol=1e-8,
                maxls=200,
            ),
        )
        joint_nfev += int(getattr(retry, "nfev", 0))
        joint_nit += int(getattr(retry, "nit", 0))
        retry_objective = float(retry.fun)
        retry_tolerance = 1e-10 * max(1.0, abs(retry_start_objective))
        retry_is_finite = bool(
            np.isfinite(retry_objective) and np.all(np.isfinite(retry.x))
        )
        if (
            retry_is_finite
            and retry_objective <= retry_start_objective + retry_tolerance
        ):
            polish = retry
            polish_objective = retry_objective
            polish_is_finite = True
            polish_did_not_worsen = True
            current_objective = retry_objective
            current_params = np.asarray(retry.x, dtype=float).copy()

    final_age_params = current_params[rsize : rsize + asize]
    joint_decode_error = None
    try:
        final_ages = _decode_age_params(
            final_age_params,
            ages_init,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
    except ToytreeError as exc:
        # The direct-age profiled solution remains valid when the optional
        # unconstrained joint-polish transform saturates at a near-boundary
        # optimum. Fall back to that solution instead of discarding an entire
        # multistart replicate for a representational round-trip failure.
        joint_decode_error = str(exc)
        final_ages = profiled_ages.copy()
        current_params = np.hstack([profile.log_rates, age_params_hat])
        current_objective = float(profiled_objective)
    final_rate_fit = _fit_profiled_ucln_rates(
        current_params[:rsize],
        final_ages,
        rate_bounds,
        edges,
        edata,
        lam,
        valid_loglik,
        observation_mask,
        max_iter,
        max_fun,
    )
    profile.total_rate_nfev += int(final_rate_fit["nfev"])
    profile.total_rate_nit += int(final_rate_fit["nit"])
    final_rate_objective = float(final_rate_fit["objective"])
    if (
        np.isfinite(final_rate_objective)
        and final_rate_objective <= current_objective + tolerance
    ):
        current_objective = final_rate_objective
        current_params[:rsize] = np.asarray(final_rate_fit["params"], dtype=float)
    rate_gradient_max_abs = float(final_rate_fit["projected_gradient_max_abs"])
    joint_gradient = np.asarray(
        getattr(polish, "jac", np.array([])),
        dtype=float,
    )
    gradient_max_abs = (
        float(np.max(np.abs(joint_gradient)))
        if joint_gradient.size and np.all(np.isfinite(joint_gradient))
        else None
    )
    profile_rate_converged = bool(rate_gradient_max_abs <= 1e-6)
    joint_polish_usable = bool(
        joint_polish_error is not None
        or joint_decode_error is not None
        or (polish.success and polish_did_not_worsen)
    )
    converged = bool(outer_success and profile_rate_converged and joint_polish_usable)
    message = str(polish.message)
    if not outer_success:
        message = f"profiled age optimization failed: {outer_message}"
    elif not profile_rate_converged:
        message = (
            "conditional rate solution failed projected-gradient tolerance: "
            f"{rate_gradient_max_abs:.6g}"
        )
    elif joint_polish_error is not None or joint_decode_error is not None:
        transform_error = joint_polish_error or joint_decode_error
        message = (
            "profiled solution converged; joint-polish age transform was "
            f"unavailable: {transform_error}"
        )
    elif polish_is_finite and not polish_did_not_worsen:
        message = (
            "final joint polish worsened the objective beyond tolerance: "
            f"{profiled_objective:.12g} -> {polish_objective:.12g}"
        )
    invalid_objective = _invalid_objective(valid_loglik)
    if current_objective >= invalid_objective - 1e-9:
        converged = False
        message = "invalid objective plateau from infeasible start"
    return {
        "start": start,
        "start_kind": str(payload.get("start_kind", f"start_{start}")),
        "objective": float(current_objective),
        "converged": converged,
        "message": message,
        "nfev": (outer_nfev + profile.total_rate_nfev + joint_nfev),
        "nit": (outer_nit + profile.total_rate_nit + joint_nit),
        "refinement_cycles": int(profile.evaluations),
        "profile_evaluations": int(profile.evaluations),
        "outer_profile_converged": bool(outer_success),
        "all_profile_rate_solves_converged": bool(profile.all_rate_solves_converged),
        "profile_rate_converged": profile_rate_converged,
        "rate_gradient_max_abs": float(rate_gradient_max_abs),
        "final_joint_converged": bool(
            polish.success and joint_polish_error is None and joint_decode_error is None
        ),
        "gradient_max_abs": gradient_max_abs,
        "optimizer_retries": optimizer_retries,
        "params": current_params,
        "ages": final_ages,
        "rates": _unpack_log_rates(current_params[:rsize]),
    }


def _ucln_input_branch_diagnostics(
    tree: ToyTree,
    branch_lengths: np.ndarray,
) -> dict[str, Any]:
    """Return threshold-free diagnostics for zero and small input edges."""
    values = np.asarray(branch_lengths, dtype=float)
    child_idxs = np.asarray(tree.get_edges("idx")[:, 0], dtype=int)
    zeros = values == 0.0
    terminal = child_idxs < int(tree.ntips)
    positive = values[values > 0.0]
    minimum_positive = float(np.min(positive)) if positive.size else None
    median_positive = float(np.median(positive)) if positive.size else None
    relative_minimum = (
        float(minimum_positive / median_positive)
        if minimum_positive is not None
        and median_positive is not None
        and median_positive > 0.0
        else None
    )
    return {
        "zero_length_branch_count": int(np.sum(zeros)),
        "zero_length_branch_fraction": float(np.mean(zeros)),
        "zero_length_terminal_branch_count": int(np.sum(zeros & terminal)),
        "zero_length_internal_branch_count": int(np.sum(zeros & ~terminal)),
        "minimum_positive_branch_length": minimum_positive,
        "median_positive_branch_length": median_positive,
        "minimum_positive_to_median_ratio": relative_minimum,
    }


def _edges_make_ultrametric_ucln(
    tree: ToyTree,
    lam: float,
    calibrations: Calibrations | None = None,
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 100_000,
    max_fun: int = 100_000,
    max_refine: int = 20,
    nstarts: int = 4,
    ncores: int = 1,
    seed: int | None = None,
    _observation_mask: np.ndarray | None = None,
    _retry_multiplier: int = 4,
    _initial_rates: Any = None,
    _initial_ages: Any = None,
) -> Union[ToyTree, dict[str, Any]]:
    """Fit the hardened centered-log-rate UCLN model."""
    lam = _validate_lambda(lam)
    if isinstance(_retry_multiplier, bool) or not isinstance(
        _retry_multiplier, (int, np.integer)
    ):
        raise ValueError("_retry_multiplier must be a positive integer.")
    retry_multiplier = int(_retry_multiplier)
    if retry_multiplier < 1:
        raise ValueError("_retry_multiplier must be a positive integer.")
    if calibrations is None:
        calibrations = {}
    calibrations = _normalize_calibrations(
        tree,
        calibrations,
        dist_floor=DIST_FLOOR,
    )
    # Normalize calibration magnitudes so the numerical problem is identical
    # whether the user expresses the same ages in years, Myr, or another
    # common time unit. Returned ages and rates are transformed back below.
    calibration_time_scale = 1.0
    if calibrations:
        calibration_time_scale = max(float(upper) for _, upper in calibrations.values())
        if calibration_time_scale <= 0.0:
            calibration_time_scale = 1.0
        calibrations = {
            int(idx): (
                float(lower) / calibration_time_scale,
                float(upper) / calibration_time_scale,
            )
            for idx, (lower, upper) in calibrations.items()
        }

    continuation_ages = _validate_ucln_warm_start(
        _initial_ages, tree.nnodes, "_initial_ages", positive=False
    )
    if continuation_ages is not None:
        continuation_ages /= calibration_time_scale
    continuation_rates = _validate_ucln_warm_start(
        _initial_rates, tree.nedges, "_initial_rates", positive=True
    )
    if continuation_rates is not None:
        continuation_rates *= calibration_time_scale

    ages_init, _ = _get_init_ages(tree, calibrations)
    interior_ages_init = np.asarray(ages_init, dtype=float).copy()
    dists_o = _validate_branch_lengths(tree)
    branch_diagnostics = _ucln_input_branch_diagnostics(tree, dists_o)
    if branch_diagnostics["zero_length_branch_count"]:
        logger.warning(
            "UCLN input contains "
            f"{branch_diagnostics['zero_length_branch_count']} exact-zero edges "
            f"({branch_diagnostics['zero_length_internal_branch_count']} internal, "
            f"{branch_diagnostics['zero_length_terminal_branch_count']} terminal). "
            "Zeros are retained as valid observations, but can weaken rate-time "
            "identifiability. Consider collapsing unresolved zero-length internal "
            "edges and inspect multistart stability diagnostics."
        )
    try:
        clock_start = edges_make_ultrametric_clock(
            tree,
            calibrations=calibrations,
            full=True,
            inplace=False,
            max_iter=min(max_iter, 200),
            max_fun=min(max_fun, 500),
            max_refine=0,
            nstarts=1,
            ncores=1,
            seed=seed,
            _observation_mask=_observation_mask,
            _retry_multiplier=1,
            _direct_age_fallback=False,
        )
        if clock_start["converged"]:
            ages_init = (
                clock_start["tree"].get_node_data("height").to_numpy(dtype=float)
            )
    except (ToytreeError, RuntimeError, ValueError):
        pass

    rates_bounds, ages_bounds_map = _get_params_bounds(tree, calibrations)
    edges = tree.get_edges("idx")
    ages_idxs = np.array(sorted(ages_bounds_map), dtype=int)
    children_map = _get_children_map_from_edges(edges)
    ages_bounds = [ages_bounds_map[i] for i in ages_idxs]
    warm_ages_init = np.asarray(ages_init, dtype=float).copy()
    ages_init = interior_ages_init
    interior_age_params = _encode_age_params(
        ages_init,
        ages_idxs,
        ages_bounds,
        children_map,
        dist_floor=DIST_FLOOR,
    )
    clock_warm_start_used = False
    try:
        age_params_init = _encode_age_params(
            warm_ages_init,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
        clock_warm_start_used = bool(
            np.any(np.abs(warm_ages_init - interior_ages_init) > 1e-12)
        )
    except ToytreeError:
        # A valid clock optimum can lie exactly on a topology/calibration
        # boundary that the legacy unconstrained transform cannot represent.
        # The profiled optimizer works in direct age coordinates, so retain the
        # guaranteed-interior initializer rather than rejecting valid input.
        warm_ages_init = interior_ages_init
        age_params_init = interior_age_params.copy()
    dists_lf = gammaln(dists_o + 1.0)
    edata = np.vstack([dists_o, dists_lf]).T
    observation_mask = _validate_observation_mask(_observation_mask, tree.nedges)

    init_times = warm_ages_init[edges[:, 1]] - warm_ages_init[edges[:, 0]]
    rates_init = np.clip(dists_o / init_times, RATE_FLOOR, None)
    observed_total = float(np.sum(dists_o[observation_mask]))
    time_total = float(np.sum(init_times[observation_mask]))
    common_rate = max(observed_total / time_total, RATE_FLOOR)
    log_deviations = np.log(rates_init) - float(np.mean(np.log(rates_init)))
    init_shrinkage = 1.0 / (1.0 + np.sqrt(lam))
    rates_init = np.exp(np.log(common_rate) + init_shrinkage * log_deviations)

    log_rate_bounds = [
        (np.log(max(lo, RATE_FLOOR)), np.log(max(hi, RATE_FLOOR)))
        for lo, hi in (rates_bounds[i] for i in range(tree.nedges))
    ]
    bounds = log_rate_bounds + [(None, None)] * age_params_init.size
    valid_loglik = _independent_branch_pseudologlik(
        rates_init,
        warm_ages_init,
        edges,
        edata,
        lam,
        None,
        observation_mask,
    )
    requested_nstarts = max(1, int(nstarts))
    base_starts: list[tuple[str, np.ndarray, np.ndarray, np.ndarray]] = [
        (
            "clock" if clock_warm_start_used else "interior",
            warm_ages_init,
            rates_init,
            age_params_init,
        )
    ]
    has_continuation = continuation_ages is not None or continuation_rates is not None
    if has_continuation:
        continued_ages = (
            warm_ages_init
            if continuation_ages is None
            else np.asarray(continuation_ages, dtype=float)
        )
        continued_rates = (
            np.clip(
                dists_o
                / np.maximum(
                    continued_ages[edges[:, 1]] - continued_ages[edges[:, 0]],
                    DIST_FLOOR,
                ),
                RATE_FLOOR,
                None,
            )
            if continuation_rates is None
            else np.asarray(continuation_rates, dtype=float)
        )
        try:
            continued_params = _encode_age_params(
                continued_ages,
                ages_idxs,
                ages_bounds,
                children_map,
                dist_floor=DIST_FLOOR,
            )
            base_starts.append(
                ("continuation", continued_ages, continued_rates, continued_params)
            )
        except ToytreeError:
            pass
    elif clock_warm_start_used and requested_nstarts >= 2:
        base_starts.append(
            ("interior", interior_ages_init, rates_init, interior_age_params)
        )

    effective_nstarts = max(requested_nstarts, len(base_starts))
    effective_ncores = max(1, int(ncores))
    rng = np.random.default_rng(seed)
    rsize = rates_init.size
    asize = ages_idxs.size
    payloads = []
    for start in range(effective_nstarts):
        if start < len(base_starts):
            start_kind, age_start_ages, rate_start, start_age_params = base_starts[
                start
            ]
            start_params = np.hstack(
                [
                    _pack_log_rates(rate_start, rate_floor=RATE_FLOOR),
                    start_age_params,
                ]
            )
            age_start_ages = np.asarray(age_start_ages, dtype=float).copy()
        else:
            base_index = start % len(base_starts) if has_continuation else 0
            base_kind, base_ages, base_rates, _ = base_starts[base_index]
            start_kind = f"{base_kind}_perturbed"
            start_params = np.hstack(
                [
                    _pack_log_rates(base_rates, rate_floor=RATE_FLOOR),
                    interior_age_params,
                ]
            )
            age_start_ages = np.asarray(base_ages, dtype=float).copy()
            start_params[:rsize] += rng.normal(0.0, 0.25, size=rsize)
            if asize:
                # Pull transformed ages away from saturated interval edges
                # before perturbing them. This creates genuinely distinct,
                # feasible direct-age starts even when many observed branch
                # lengths are exactly zero. If a highly constrained tree still
                # rejects the draw, retain the guaranteed-interior ages; the
                # independently perturbed rates remain a valid numerical start.
                age_params = np.clip(interior_age_params, -6.0, 6.0)
                age_params += rng.normal(0.0, 0.25, size=asize)
                start_params[rsize:] = age_params
                try:
                    age_start_ages = _decode_age_params(
                        age_params,
                        ages_init,
                        ages_idxs,
                        ages_bounds,
                        children_map,
                        dist_floor=DIST_FLOOR,
                    )
                except ToytreeError:
                    start_params[rsize:] = interior_age_params
                    age_start_ages = interior_ages_init.copy()
        payloads.append(
            {
                "start": start,
                "start_kind": start_kind,
                "params": start_params,
                "bounds": bounds,
                "rates_init": rates_init,
                "age_params_init": age_params_init,
                "ages_init": ages_init,
                "age_start_ages": age_start_ages,
                "ages_idxs": ages_idxs,
                "ages_bounds": ages_bounds,
                "children_map": children_map,
                "edges": edges,
                "edata": edata,
                "lam": lam,
                "valid_loglik": valid_loglik,
                "observation_mask": observation_mask,
                "max_iter": max_iter,
                "max_fun": max_fun,
                "max_refine": max_refine,
                "retry_multiplier": retry_multiplier,
            }
        )

    starts = _run_multistart(
        _fit_ucln_start,
        payloads,
        ncores=effective_ncores,
    )

    def finalize_start(result: dict[str, Any]) -> None:
        """Repair and rescore one direct-age profiled result in place."""
        if "params" not in result:
            return
        try:
            result_ages = np.asarray(result["ages"], dtype=float)
            result_ages = _finalize_ultrametric_ages(
                tree,
                result_ages,
                calibrations=calibrations,
                dist_floor=DIST_FLOOR,
            )
            result_rates = np.asarray(result["rates"], dtype=float)
            rescored = _independent_branch_pseudologlik(
                result_rates,
                result_ages,
                edges,
                edata,
                lam,
                valid_loglik,
                observation_mask,
            )
            result["ages"] = result_ages
            result["rates"] = result_rates
            result["objective"] = float(-rescored)
        except (ToytreeError, ValueError) as exc:
            result["objective"] = float("inf")
            result["converged"] = False
            result["message"] = f"invalid finalized ages: {exc}"

    for result in starts:
        finalize_start(result)

    preliminary_best = _select_best_multistart(starts)
    preliminary_stability = assess_solution_stability(
        starts,
        preliminary_best,
        ntips=tree.ntips,
    )
    basin_confirmation_run = False
    if (
        effective_nstarts >= 2
        and preliminary_best.get("converged", False)
        and int(preliminary_stability["near_optimal_starts"]) < 2
    ):
        # Confirm a singly observed winning basin from a nearby but distinct
        # feasible chronogram. A convex combination of two feasible age vectors
        # preserves all linear topology and calibration constraints.
        confirmation_ages = (
            0.95 * np.asarray(preliminary_best["ages"], dtype=float)
            + 0.05 * interior_ages_init
        )
        confirmation_params = np.asarray(preliminary_best["params"], dtype=float).copy()
        confirmation_params[:rsize] = np.log(
            np.clip(preliminary_best["rates"], RATE_FLOOR, None)
        ) + rng.normal(0.0, 0.05, size=rsize)
        confirmation_params[rsize:] = interior_age_params
        confirmation_payload = dict(payloads[0])
        confirmation_payload.update(
            {
                "start": effective_nstarts,
                "params": confirmation_params,
                "age_start_ages": confirmation_ages,
            }
        )
        confirmation = _run_multistart(
            _fit_ucln_start,
            [confirmation_payload],
            ncores=1,
        )[0]
        finalize_start(confirmation)
        starts.append(confirmation)
        basin_confirmation_run = True

    best = _select_best_multistart(starts)
    stability = assess_solution_stability(starts, best, ntips=tree.ntips)
    best_basin_replicates = int(stability["near_optimal_starts"])
    best_basin_replicated = best_basin_replicates >= 2
    stability["best_basin_replicates"] = best_basin_replicates
    stability["best_basin_replicated"] = best_basin_replicated
    if stability["stability_assessed"]:
        stability["solution_stable"] = bool(
            stability["solution_stable"] and best_basin_replicated
        )
    if not best["converged"]:
        logger.warning(f"Best multistart fit did not converge: {best['message']}")
    logger.debug(
        "uncorrelated_lognormal multistart best objective="
        f"{best['objective']}, start={best['start']}, nstarts={effective_nstarts}"
    )

    fit_ages = np.asarray(best["ages"], dtype=float)
    fit_rates = np.asarray(best["rates"], dtype=float)
    penalized_pseudologlik = _independent_branch_pseudologlik(
        fit_rates,
        fit_ages,
        edges,
        edata,
        lam,
        valid_loglik,
        observation_mask,
    )
    pseudologlik = _independent_branch_pseudologlik(
        fit_rates,
        fit_ages,
        edges,
        edata,
        0.0,
        valid_loglik,
        observation_mask,
    )
    penalty = _uncorrelated_lognormal_penalty(fit_rates)
    time_dists = fit_ages[edges[:, 1]] - fit_ages[edges[:, 0]]
    expected = time_dists * fit_rates
    ages = fit_ages * calibration_time_scale
    rates = fit_rates / calibration_time_scale
    output_tree = tree.set_node_data("height", ages, inplace=False)
    result = {
        "model": "uncorrelated_lognormal",
        "pseudologlik": pseudologlik,
        "penalized_pseudologlik": penalized_pseudologlik,
        **_result_observation_metadata(),
        "penalty": penalty,
        "penalty_model": "summed_centered_log_rate_dispersion",
        "scale_invariant": True,
        "calibration_time_unit_invariant": True,
        "internal_calibration_time_scale": calibration_time_scale,
        "clock_warm_start_used": clock_warm_start_used,
        "interior_multistart_included": bool(
            not clock_warm_start_used or effective_nstarts >= 2
        ),
        "lam": lam,
        "implied_sigma_log": float(np.sqrt(1.0 / (2.0 * lam))),
        "nparams": len(bounds),
        "optimizer_strategy": "profiled_rates_joint_polish",
        "rates": list(rates),
        "profiled_mean_rate": float(np.exp(np.mean(np.log(rates)))),
        "expected_branch_lengths": expected.tolist(),
        "observed_branch_lengths": dists_o.tolist(),
        "tree": output_tree,
        "converged": bool(best["converged"]),
        "optimizer_message": str(best["message"]),
        "nfev": int(best.get("nfev", -1)),
        "nit": int(best.get("nit", -1)),
        "refinement_cycles": int(best.get("refinement_cycles", -1)),
        "final_joint_converged": bool(best.get("final_joint_converged", False)),
        "gradient_max_abs": best.get("gradient_max_abs"),
        "rate_gradient_max_abs": best.get("rate_gradient_max_abs"),
        "profile_evaluations": int(best.get("profile_evaluations", -1)),
        "outer_profile_converged": bool(best.get("outer_profile_converged", False)),
        "profile_rate_converged": bool(best.get("profile_rate_converged", False)),
        "optimizer_retries": int(best.get("optimizer_retries", 0)),
        **branch_diagnostics,
        "nstarts": effective_nstarts,
        "evaluated_starts": len(starts),
        "basin_confirmation_run": basin_confirmation_run,
        "requested_nstarts": requested_nstarts,
        "ncores": max(1, min(effective_ncores, effective_nstarts)),
        "best_start": int(best["start"]),
        "best_start_kind": str(
            best.get("start_kind", f"start_{int(best.get('start', -1))}")
        ),
        **stability,
        "starts": [
            {
                "start": int(item["start"]),
                "start_kind": str(
                    item.get("start_kind", f"start_{int(item.get('start', -1))}")
                ),
                "objective": float(item["objective"]),
                "converged": bool(item["converged"]),
                "message": str(item["message"]),
                "nfev": int(item.get("nfev", -1)),
                "nit": int(item.get("nit", -1)),
                "refinement_cycles": int(item.get("refinement_cycles", -1)),
                "final_joint_converged": bool(item.get("final_joint_converged", False)),
                "gradient_max_abs": item.get("gradient_max_abs"),
                "rate_gradient_max_abs": item.get("rate_gradient_max_abs"),
                "profile_evaluations": int(item.get("profile_evaluations", -1)),
                "outer_profile_converged": bool(
                    item.get("outer_profile_converged", False)
                ),
                "profile_rate_converged": bool(
                    item.get("profile_rate_converged", False)
                ),
                "optimizer_retries": int(item.get("optimizer_retries", 0)),
            }
            for item in starts
        ],
    }
    return _finalize_fit_result(result, tree, full=full, inplace=inplace)


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
    nstarts: int = 4,
    ncores: int = 1,
    seed: int | None = None,
) -> Union[ToyTree, dict[str, Any]]:
    """Fit independent branch rates with a centered lognormal penalty.

    This penalized/MAP-like model estimates one rate per branch and profiles
    their common mean on the log scale. Its centered log-rate penalty is
    invariant to the common rate rescaling caused by changing calibration time
    units. Input edges may use any consistent, finite, non-negative additive
    unit for which branch length equals elapsed time multiplied by rate;
    expected substitutions per site are common but not required. Calibration
    ages define the output-tree time unit, and fitted rates are in input-edge
    units per calibration unit. Without calibrations, the root age is fixed to
    1, the output is relative time, and rates are in input-edge units per
    relative root-age unit. This is ToyTree's recommended uncorrelated-rate
    model. ``lam`` is a fixed smoothing assumption: under the corresponding
    iid-lognormal penalty interpretation,
    ``implied_sigma_log = sqrt(1 / (2 * lam))``. This value is returned with
    ``full=True`` but is not estimated from the tree. Conditional rates are
    profiled with a strictly convex solver while node ages are optimized
    directly under linear topology and calibration constraints. Exact-zero
    input edges are retained as valid observations, not replaced by arbitrary
    pseudo-lengths. They can weaken rate-time identifiability, so full results
    report zero-edge and independent best-basin replication diagnostics. Four
    starts are used by default; a basin reached by only one start is not
    reported as stable. By default, only a usable tree is returned;
    nonconvergence or explicitly unstable multistart diagnostics raise
    :class:`ToytreeError`. Set ``full=True`` to always receive the candidate
    tree and diagnostics, including ``fit_usable`` and ``failure_reasons``.
    ``inplace=True`` mutates the input only after the fit is declared usable.
    """
    return _edges_make_ultrametric_ucln(
        tree=tree,
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
    )


def _uncorrelated_lognormal_penalty(rates_hat: np.ndarray) -> float:
    """Return summed centered log-rate dispersion."""
    log_rates = np.log(np.clip(np.asarray(rates_hat, dtype=float), RATE_FLOOR, None))
    centered = log_rates - float(np.mean(log_rates))
    return float(np.sum(centered * centered))


def _independent_branch_pseudologlik(
    rates_hat,
    ages_hat,
    edges,
    edata,
    lam,
    valid_loglik,
    observation_mask=None,
) -> float:
    """Return the UCLN penalized branch-length pseudologlikelihood."""
    if valid_loglik is None:
        valid_loglik = -1.0
    times = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    if np.any(times < DIST_FLOOR):
        return valid_loglik - INVALID_LOG_LIK_DROP
    rates_hat = np.clip(np.asarray(rates_hat, dtype=float), RATE_FLOOR, None)
    expected = times * rates_hat
    if np.any(expected <= 0.0) or np.any(~np.isfinite(expected)):
        return valid_loglik - INVALID_LOG_LIK_DROP
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    terms = edata[:, 0] * np.log(expected) - expected - edata[:, 1]
    pseudologlik = float(np.sum(terms[mask]))
    penalty = _uncorrelated_lognormal_penalty(rates_hat)
    if not np.isfinite(pseudologlik) or not np.isfinite(penalty):
        return valid_loglik - INVALID_LOG_LIK_DROP
    return float(pseudologlik - lam * penalty)
