#!/usr/bin/env python

"""Correlated log-rate penalized branch-length pseudolikelihood."""

from typing import Any, Union

import numpy as np
from loguru import logger
from scipy.optimize import OptimizeResult, minimize
from scipy.special import expit, gammaln

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_pseudolikelihood.clock import (
    edges_make_ultrametric_clock,
)
from toytree.mod._src.penalized_pseudolikelihood.optimization import (
    direct_age_linear_constraint,
    minimize_profiled_ages,
    optimizer_stopped_at_limit,
    projected_gradient_max_abs,
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
    _result_observation_metadata,
    _run_multistart,
    _select_best_multistart,
    _unpack_log_rates,
    _validate_branch_lengths,
    _validate_lambda,
    _validate_observation_mask,
    get_tree_with_correlated_rates,
)
from toytree.utils import ToytreeError

__all__ = ["edges_make_ultrametric_correlated"]

RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
INVALID_LOG_LIK_DROP = 1e6
SOLUTION_OBJECTIVE_ATOL = 1e-4
SOLUTION_OBJECTIVE_RTOL = 1e-6
SOLUTION_MAX_NORMALIZED_AGE_DIFFERENCE = 0.02
RATE_GRADIENT_TARGET = 1e-8
RATE_GRADIENT_TOL = 1e-6
CORRELATED_OBSERVATION_LOSSES = frozenset(
    {"fractional_poisson", "multiplicative_gamma"}
)


def _invalid_objective(valid_loglik: float) -> float:
    """Return the finite objective value used for invalid fits."""
    return float(-(valid_loglik - INVALID_LOG_LIK_DROP))


def _validate_correlated_observation_loss(value: str) -> str:
    """Return a supported private correlated branch-observation loss."""
    if value not in CORRELATED_OBSERVATION_LOSSES:
        choices = ", ".join(sorted(CORRELATED_OBSERVATION_LOSSES))
        raise ValueError(f"_observation_loss must be one of: {choices}.")
    return value


def _validate_correlated_warm_start(
    values: Any,
    size: int,
    name: str,
    *,
    positive: bool,
) -> np.ndarray | None:
    """Return one validated private warm-start vector."""
    if values is None:
        return None
    array = np.asarray(values, dtype=float)
    if array.shape != (size,) or np.any(~np.isfinite(array)):
        raise ValueError(f"{name} must contain {size} finite values.")
    if positive and np.any(array <= 0.0):
        raise ValueError(f"{name} values must be strictly positive.")
    return array.copy()


def _assess_correlated_solution_stability(
    starts: list[dict[str, Any]],
    best: dict[str, Any],
    ntips: int,
    objective_atol: float = SOLUTION_OBJECTIVE_ATOL,
    objective_rtol: float = SOLUTION_OBJECTIVE_RTOL,
    age_tolerance: float = SOLUTION_MAX_NORMALIZED_AGE_DIFFERENCE,
) -> dict[str, Any]:
    """Compare chronograms from converged, near-optimal multistarts."""
    converged = [
        result
        for result in starts
        if result.get("converged", False)
        and np.isfinite(result.get("objective", np.inf))
        and "ages" in result
    ]
    assessed = len(converged) >= 2
    best_objective = float(best["objective"])
    objective_tolerance = float(objective_atol) + float(objective_rtol) * max(
        1.0, abs(best_objective)
    )
    near_optimal = [
        result
        for result in converged
        if float(result["objective"]) - best_objective <= objective_tolerance
    ]
    best_ages = np.asarray(best["ages"], dtype=float)
    root_age = max(abs(float(best_ages[-1])), DIST_FLOOR)
    differences = [
        float(
            np.max(
                np.abs(
                    np.asarray(result["ages"], dtype=float)[ntips:] - best_ages[ntips:]
                )
            )
            / root_age
        )
        for result in near_optimal
    ]
    maximum = max(differences, default=0.0)
    stable = None if not assessed else bool(maximum <= float(age_tolerance))
    return {
        "stability_assessed": assessed,
        "solution_stable": stable,
        "converged_starts": len(converged),
        "near_optimal_starts": len(near_optimal),
        "objective_equivalence_tolerance": objective_tolerance,
        "maximum_age_difference_tolerance": float(age_tolerance),
        "max_near_optimal_age_difference": float(maximum),
    }


def _correlated_penalty_hessian(parent_edges: np.ndarray) -> np.ndarray:
    """Return the Hessian of complete-tree log-rate roughness."""
    parent_edges = np.asarray(parent_edges, dtype=int)
    matrix = np.zeros((parent_edges.size, parent_edges.size), dtype=float)
    for child in np.flatnonzero(parent_edges >= 0):
        parent = int(parent_edges[child])
        matrix[child, child] += 2.0
        matrix[parent, parent] += 2.0
        matrix[child, parent] -= 2.0
        matrix[parent, child] -= 2.0
    basal = np.flatnonzero(parent_edges < 0)
    if basal.size:
        centered = np.eye(basal.size) - np.full(
            (basal.size, basal.size), 1.0 / basal.size
        )
        matrix[np.ix_(basal, basal)] += 2.0 * centered
    return matrix


def _correlated_rate_objective_with_gradient(
    log_rates: np.ndarray,
    ages_hat: np.ndarray,
    edges: np.ndarray,
    edata: np.ndarray,
    parent_edges: np.ndarray,
    lam: float,
    valid_loglik: float,
    observation_mask: np.ndarray,
    observation_loss: str,
) -> tuple[float, np.ndarray]:
    """Return the fixed-chronogram objective and log-rate gradient."""
    log_rates = np.asarray(log_rates, dtype=float)
    rates_hat = _unpack_log_rates(log_rates)
    objective = -_correlated_branch_pseudologlik(
        rates_hat,
        ages_hat,
        edges,
        edata,
        parent_edges,
        lam,
        valid_loglik,
        observation_mask,
        observation_loss,
    )
    times = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    expected = rates_hat * times
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    if (
        not np.isfinite(objective)
        or np.any(times <= DIST_FLOOR)
        or np.any(expected <= 0.0)
        or np.any(~np.isfinite(expected))
    ):
        return float(objective), np.zeros_like(log_rates)
    data_gradient = np.zeros(log_rates.size, dtype=float)
    if observation_loss == "fractional_poisson":
        data_gradient[mask] = expected[mask] - edata[mask, 0]
    else:
        data_gradient[mask] = 1.0 - edata[mask, 0] / expected[mask]
    gradient = data_gradient + lam * _correlated_penalty_gradient(
        log_rates, parent_edges
    )
    return float(objective), gradient


def _correlated_rate_newton_direction(
    params: np.ndarray,
    gradient: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    penalty_hessian: np.ndarray,
    times: np.ndarray,
    edata: np.ndarray,
    mask: np.ndarray,
    observation_loss: str,
) -> np.ndarray:
    """Return a bound-aware Newton direction for conditional log rates."""
    at_lower = (params <= lower + 1e-10) & (gradient > 0.0)
    at_upper = (params >= upper - 1e-10) & (gradient < 0.0)
    free = ~(at_lower | at_upper)
    direction = np.zeros_like(params)
    if np.any(free):
        expected = np.exp(params) * times
        curvature = np.zeros(params.size, dtype=float)
        if observation_loss == "fractional_poisson":
            curvature[mask] = expected[mask]
        else:
            curvature[mask] = edata[mask, 0] / expected[mask]
        free_idxs = np.flatnonzero(free)
        hessian = penalty_hessian[np.ix_(free_idxs, free_idxs)].copy()
        hessian.flat[:: hessian.shape[0] + 1] += curvature[free]
        try:
            direction[free] = -np.linalg.solve(hessian, gradient[free])
        except np.linalg.LinAlgError:
            ridge = 1e-10 * max(1.0, float(np.max(np.diag(hessian))))
            hessian.flat[:: hessian.shape[0] + 1] += ridge
            direction[free] = -np.linalg.lstsq(hessian, gradient[free], rcond=None)[0]

    slope = float(np.dot(gradient, direction))
    if not np.isfinite(slope) or slope >= 0.0:
        scale = np.maximum(1.0, np.diag(penalty_hessian))
        direction = -gradient / scale
        direction[at_lower | at_upper] = 0.0
    return direction


def _fit_profiled_correlated_rates(
    log_rates_init: np.ndarray,
    ages_hat: np.ndarray,
    rate_bounds: list[tuple[float | None, float | None]],
    edges: np.ndarray,
    edata: np.ndarray,
    parent_edges: np.ndarray,
    lam: float,
    valid_loglik: float,
    observation_mask: np.ndarray,
    observation_loss: str,
    max_iter: int,
    max_fun: int,
    *,
    final_polish: bool = False,
    retry_multiplier: int = 1,
) -> dict[str, Any]:
    """Solve the convex conditional correlated log-rate problem.

    The Newton solve is used for every age-profile evaluation. A bounded
    L-BFGS-B polish can be requested for the final fixed-chronogram solve only;
    this avoids multiplying the cost of every outer objective evaluation.
    """
    lower = np.asarray(
        [-np.inf if bound[0] is None else float(bound[0]) for bound in rate_bounds]
    )
    upper = np.asarray(
        [np.inf if bound[1] is None else float(bound[1]) for bound in rate_bounds]
    )
    params = np.clip(np.asarray(log_rates_init, dtype=float), lower, upper)
    objective, gradient = _correlated_rate_objective_with_gradient(
        params,
        ages_hat,
        edges,
        edata,
        parent_edges,
        lam,
        valid_loglik,
        observation_mask,
        observation_loss,
    )
    penalty_hessian = lam * _correlated_penalty_hessian(parent_edges)
    times = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    nfev = 1
    nit = 0
    message = "conditional rate Newton iteration limit reached"
    converged = False
    max_newton_iter = max(1, min(int(max_iter), int(max_fun), 500))
    for iteration in range(max_newton_iter):
        nit = iteration + 1
        projected = projected_gradient_max_abs(params, gradient, rate_bounds)
        if projected <= RATE_GRADIENT_TARGET:
            converged = True
            message = "conditional rate projected gradient converged"
            break

        direction = _correlated_rate_newton_direction(
            params,
            gradient,
            lower,
            upper,
            penalty_hessian,
            times,
            edata,
            mask,
            observation_loss,
        )

        accepted = False
        step_scale = 1.0
        for _ in range(60):
            candidate = np.clip(params + step_scale * direction, lower, upper)
            step = candidate - params
            if float(np.max(np.abs(step))) <= 1e-14:
                break
            candidate_objective, candidate_gradient = (
                _correlated_rate_objective_with_gradient(
                    candidate,
                    ages_hat,
                    edges,
                    edata,
                    parent_edges,
                    lam,
                    valid_loglik,
                    observation_mask,
                    observation_loss,
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
    gradient_before_polish = float(projected)
    polish_used = bool(final_polish and projected > RATE_GRADIENT_TOL)
    polish_accepted = False
    polish_message = None
    stationarity_steps = 0
    if polish_used:
        polish_args = (
            ages_hat,
            edges,
            edata,
            parent_edges,
            lam,
            valid_loglik,
            observation_mask,
            observation_loss,
        )
        try:
            polish = minimize(
                fun=_correlated_rate_objective_with_gradient,
                x0=params,
                args=polish_args,
                method="L-BFGS-B",
                jac=True,
                bounds=rate_bounds,
                options=dict(
                    maxiter=max(1, int(max_iter) * int(retry_multiplier)),
                    maxfun=max(1, int(max_fun) * int(retry_multiplier)),
                    ftol=np.finfo(float).eps,
                    gtol=RATE_GRADIENT_TARGET,
                    maxls=200,
                ),
            )
            nfev += int(getattr(polish, "nfev", 0))
            nit += int(getattr(polish, "nit", 0))
            candidate = np.clip(np.asarray(polish.x, dtype=float), lower, upper)
            candidate_objective, candidate_gradient = (
                _correlated_rate_objective_with_gradient(candidate, *polish_args)
            )
            nfev += 1
            candidate_projected = projected_gradient_max_abs(
                candidate, candidate_gradient, rate_bounds
            )
            objective_tolerance = (
                128.0 * np.finfo(float).eps * max(1.0, abs(float(objective)))
            )
            polish_accepted = bool(
                np.isfinite(candidate_objective)
                and np.all(np.isfinite(candidate))
                and candidate_objective <= objective + objective_tolerance
                and candidate_projected <= projected
            )
            polish_message = str(polish.message)
            if polish_accepted:
                params = candidate
                objective = float(candidate_objective)
                gradient = np.asarray(candidate_gradient, dtype=float)
                projected = float(candidate_projected)
                message = f"conditional rate final polish: {polish.message}"
        except (FloatingPointError, RuntimeError, ValueError) as exc:
            polish_message = f"{type(exc).__name__}: {exc}"

        # Near a conditional optimum, the objective improvement from a Newton
        # step can be smaller than double-precision resolution even while the
        # absolute projected gradient remains just above its release gate.
        # Refine stationarity directly, but accept a step only when its exact
        # objective is non-worsening to floating-point precision and its
        # projected gradient strictly decreases.
        for _ in range(20):
            if projected <= RATE_GRADIENT_TARGET:
                break
            direction = _correlated_rate_newton_direction(
                params,
                gradient,
                lower,
                upper,
                penalty_hessian,
                times,
                edata,
                mask,
                observation_loss,
            )
            accepted = False
            step_scale = 1.0
            for _ in range(60):
                candidate = np.clip(params + step_scale * direction, lower, upper)
                step = candidate - params
                if not np.any(step):
                    break
                candidate_objective, candidate_gradient = (
                    _correlated_rate_objective_with_gradient(
                        candidate,
                        ages_hat,
                        edges,
                        edata,
                        parent_edges,
                        lam,
                        valid_loglik,
                        observation_mask,
                        observation_loss,
                    )
                )
                nfev += 1
                candidate_projected = projected_gradient_max_abs(
                    candidate, candidate_gradient, rate_bounds
                )
                objective_tolerance = (
                    128.0 * np.finfo(float).eps * max(1.0, abs(float(objective)))
                )
                if (
                    np.isfinite(candidate_objective)
                    and candidate_objective <= objective + objective_tolerance
                    and candidate_projected < projected
                ):
                    params = candidate
                    objective = float(candidate_objective)
                    gradient = np.asarray(candidate_gradient, dtype=float)
                    projected = float(candidate_projected)
                    stationarity_steps += 1
                    nit += 1
                    polish_accepted = True
                    accepted = True
                    break
                step_scale *= 0.5
            if not accepted:
                break
        if stationarity_steps:
            suffix = f"{stationarity_steps} Newton stationarity refinement step(s)"
            polish_message = (
                suffix if polish_message is None else f"{polish_message}; {suffix}"
            )
            message = f"conditional rate final polish: {polish_message}"

    if projected <= RATE_GRADIENT_TOL:
        converged = True
        if "converged" not in message:
            message = "conditional rate projected gradient converged"
    return {
        "params": params,
        "objective": float(objective),
        "converged": bool(converged),
        "message": message,
        "projected_gradient_max_abs": float(projected),
        "gradient_before_final_polish": gradient_before_polish,
        "final_polish_used": polish_used,
        "final_polish_accepted": polish_accepted,
        "final_polish_message": polish_message,
        "final_polish_stationarity_steps": stationarity_steps,
        "nfev": int(nfev),
        "nit": int(nit),
    }


class _ProfiledCorrelatedObjective:
    """Profile correlated rates while optimizing direct node ages."""

    def __init__(
        self,
        log_rates_init: np.ndarray,
        rate_bounds: list[tuple[float | None, float | None]],
        ages_base: np.ndarray,
        ages_idxs: np.ndarray,
        edges: np.ndarray,
        edata: np.ndarray,
        parent_edges: np.ndarray,
        lam: float,
        valid_loglik: float,
        observation_mask: np.ndarray,
        observation_loss: str,
        max_iter: int,
        max_fun: int,
    ) -> None:
        self.log_rates = np.asarray(log_rates_init, dtype=float).copy()
        self.rate_bounds = rate_bounds
        self.ages_base = np.asarray(ages_base, dtype=float)
        self.ages_idxs = np.asarray(ages_idxs, dtype=int)
        self.edges = np.asarray(edges, dtype=int)
        self.edata = np.asarray(edata, dtype=float)
        self.parent_edges = np.asarray(parent_edges, dtype=int)
        self.lam = float(lam)
        self.valid_loglik = float(valid_loglik)
        self.observation_mask = np.asarray(observation_mask, dtype=bool)
        self.observation_loss = str(observation_loss)
        self.max_iter = int(max_iter)
        self.max_fun = int(max_fun)
        self.total_rate_nfev = 0
        self.total_rate_nit = 0
        self.evaluations = 0
        self.all_rate_solves_converged = True
        self.rate_gradient_max_abs = float("inf")
        self._cached_age_values: np.ndarray | None = None
        self._cached_result: tuple[float, np.ndarray] | None = None

    def __call__(self, age_values: np.ndarray) -> tuple[float, np.ndarray]:
        """Return the rate-profiled objective and direct-age gradient."""
        age_values = np.asarray(age_values, dtype=float)
        if self._cached_age_values is not None and np.array_equal(
            age_values, self._cached_age_values
        ):
            assert self._cached_result is not None
            return self._cached_result
        ages_hat = self.ages_base.copy()
        ages_hat[self.ages_idxs] = age_values
        rate_fit = _fit_profiled_correlated_rates(
            self.log_rates,
            ages_hat,
            self.rate_bounds,
            self.edges,
            self.edata,
            self.parent_edges,
            self.lam,
            self.valid_loglik,
            self.observation_mask,
            self.observation_loss,
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
        if (
            not np.isfinite(objective)
            or np.any(times <= DIST_FLOOR)
            or np.any(expected <= 0.0)
        ):
            gradient = np.zeros(age_values.size, dtype=float)
        else:
            data_gradient = np.zeros(self.edges.shape[0], dtype=float)
            if self.observation_loss == "fractional_poisson":
                data_gradient[self.observation_mask] = (
                    expected[self.observation_mask]
                    - self.edata[self.observation_mask, 0]
                )
            else:
                data_gradient[self.observation_mask] = (
                    1.0
                    - self.edata[self.observation_mask, 0]
                    / expected[self.observation_mask]
                )
            time_gradient = np.zeros(self.edges.shape[0], dtype=float)
            time_gradient[self.observation_mask] = (
                data_gradient[self.observation_mask] / times[self.observation_mask]
            )
            age_gradient = np.zeros(ages_hat.size, dtype=float)
            np.add.at(age_gradient, self.edges[:, 1], time_gradient)
            np.add.at(age_gradient, self.edges[:, 0], -time_gradient)
            gradient = age_gradient[self.ages_idxs]
        self._cached_age_values = age_values.copy()
        self._cached_result = (objective, np.asarray(gradient, dtype=float))
        return self._cached_result


def _fit_correlated_start(payload: dict[str, Any]) -> dict[str, Any]:
    """Fit one correlated start by profiling rates before a joint polish."""
    start = int(payload["start"])
    start_kind = str(payload.get("start_kind", f"start_{start}"))
    params = np.asarray(payload["params"], dtype=float)
    bounds = payload["bounds"]
    rates_init = np.asarray(payload["rates_init"], dtype=float)
    ages_init = np.asarray(payload["ages_init"], dtype=float)
    ages_idxs = np.asarray(payload["ages_idxs"], dtype=int)
    ages_bounds = payload["ages_bounds"]
    children_map = payload["children_map"]
    edges = np.asarray(payload["edges"], dtype=int)
    edata = np.asarray(payload["edata"], dtype=float)
    parent_edges = np.asarray(payload["parent_edges"], dtype=int)
    lam = float(payload["lam"])
    valid_loglik = float(payload["valid_loglik"])
    observation_mask = np.asarray(payload["observation_mask"], dtype=bool)
    observation_loss = str(payload["observation_loss"])
    max_iter = int(payload["max_iter"])
    max_fun = int(payload["max_fun"])
    retry_multiplier = int(payload["retry_multiplier"])
    rsize = rates_init.size
    asize = ages_idxs.size
    rate_bounds = bounds[:rsize]
    age_start_full = np.asarray(payload["age_start_ages"], dtype=float)
    age_start = age_start_full[ages_idxs]
    profile = _ProfiledCorrelatedObjective(
        params[:rsize],
        rate_bounds,
        ages_init,
        ages_idxs,
        edges,
        edata,
        parent_edges,
        lam,
        valid_loglik,
        observation_mask,
        observation_loss,
        max_iter,
        max_fun,
    )
    linear_constraint = direct_age_linear_constraint(
        ages_init, ages_idxs, edges, dist_floor=DIST_FLOOR
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

    profiled_ages = ages_init.copy()
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
        parent_edges,
        lam,
        valid_loglik,
        observation_mask,
        observation_loss,
    )
    joint_polish_error = None
    try:
        polish = minimize(
            fun=objective_correlated_with_gradient,
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
    except (ToytreeError, ValueError) as exc:
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
            fun=objective_correlated_with_gradient,
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
    except (ToytreeError, ValueError) as exc:
        joint_decode_error = str(exc)
        final_ages = profiled_ages.copy()
        current_params = np.hstack([profile.log_rates, age_params_hat])
        current_objective = float(profiled_objective)
    final_rate_fit = _fit_profiled_correlated_rates(
        current_params[:rsize],
        final_ages,
        rate_bounds,
        edges,
        edata,
        parent_edges,
        lam,
        valid_loglik,
        observation_mask,
        observation_loss,
        max_iter,
        max_fun,
        final_polish=retry_multiplier > 1,
        retry_multiplier=retry_multiplier,
    )
    if final_rate_fit["final_polish_used"]:
        optimizer_retries += 1
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
    joint_gradient = np.asarray(getattr(polish, "jac", np.array([])), dtype=float)
    gradient_max_abs = (
        float(np.max(np.abs(joint_gradient)))
        if joint_gradient.size and np.all(np.isfinite(joint_gradient))
        else None
    )
    profile_rate_converged = bool(rate_gradient_max_abs <= RATE_GRADIENT_TOL)
    if not asize:
        outer_success = profile_rate_converged
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
        "start_kind": start_kind,
        "objective": float(current_objective),
        "converged": converged,
        "message": message,
        "nfev": outer_nfev + profile.total_rate_nfev + joint_nfev,
        "nit": outer_nit + profile.total_rate_nit + joint_nit,
        "refinement_cycles": int(profile.evaluations),
        "profile_evaluations": int(profile.evaluations),
        "outer_profile_converged": bool(outer_success),
        "all_profile_rate_solves_converged": bool(profile.all_rate_solves_converged),
        "profile_rate_converged": profile_rate_converged,
        "rate_gradient_max_abs": rate_gradient_max_abs,
        "rate_gradient_before_final_polish": float(
            final_rate_fit["gradient_before_final_polish"]
        ),
        "final_rate_polish_used": bool(final_rate_fit["final_polish_used"]),
        "final_rate_polish_accepted": bool(final_rate_fit["final_polish_accepted"]),
        "final_rate_polish_message": final_rate_fit["final_polish_message"],
        "final_rate_polish_stationarity_steps": int(
            final_rate_fit["final_polish_stationarity_steps"]
        ),
        "final_joint_converged": bool(
            polish.success and joint_polish_error is None and joint_decode_error is None
        ),
        "gradient_max_abs": gradient_max_abs,
        "optimizer_retries": optimizer_retries,
        "params": current_params,
        "ages": final_ages,
        "rates": _unpack_log_rates(current_params[:rsize]),
    }


def _correlated_input_branch_diagnostics(
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


def _canonical_calibration_ratio(value: float, scale: float) -> float:
    """Return a unit-independent finite calibration ratio.

    Mathematically equivalent inputs such as ``x / y`` and
    ``(1e6 * x) / (1e6 * y)`` can differ by one floating-point bit. Fifteen
    significant digits remove that path dependence while retaining much more
    precision than the optimizer or calibration tolerances use.
    """
    ratio = float(value) / float(scale)
    if not np.isfinite(ratio):
        return ratio
    return float(f"{ratio:.15g}")


@add_subpackage_method(TreeModAPI)
def edges_make_ultrametric_correlated(
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
    _observation_loss: str = "fractional_poisson",
    _initial_rates: Any = None,
    _initial_ages: Any = None,
    _retry_multiplier: int = 4,
) -> Union[ToyTree, dict[str, Any]]:
    """Return a tree fitted under complete-tree correlated log-rate smoothing.

    This model estimates one rate per edge and penalizes squared differences
    between adjacent log rates. Basal edges are connected through their
    profiled mean log rate, so smoothing covers the complete rooted tree.
    ``lam`` controls the strength of smoothing and must be selected or supplied
    by the user; it is not an ordinary model parameter.

    Branch lengths may use any finite, nonnegative additive unit. Returned
    rates use input-branch-length units per calibration-time unit. With no
    calibrations, root age is fixed to one and rates are per relative root-age
    unit.

    Rates are conditionally profiled for every directly constrained age
    evaluation. Exact-zero input edges remain zero observations. Calibration
    ages are normalized internally, so changing only their common time unit
    rescales returned ages and rates without changing the fitted chronogram.
    Four starts are evaluated by default; full results report convergence,
    profile-gradient, basin-replication, and zero-edge diagnostics.

    Parameters
    ----------
    tree : ToyTree
        Rooted tree with finite, nonnegative additive branch lengths.
    lam : float
        Finite positive log-rate smoothing multiplier.
    calibrations : dict or None
        Internal-node age constraints. Scalars fix ages and two-tuples define
        inclusive lower and upper bounds.
    full, inplace : bool
        Return fit metadata instead of only a tree, and optionally modify the
        input tree.
    max_iter, max_fun : int
        Optimizer iteration and objective-evaluation budgets.
    max_refine : int
        Retained for the common ultrametric-model API. Conditional profiling
        supersedes block-refinement cycles for this model.
    nstarts, ncores : int
        Number of optimizer starts and worker processes.
    seed : int or None
        Random seed for perturbed starts.

    Returns
    -------
    ToyTree or dict[str, Any]
        Fitted ultrametric tree, or a result dictionary when ``full=True``.
    """
    lam = _validate_lambda(lam)
    observation_loss = _validate_correlated_observation_loss(_observation_loss)
    if isinstance(_retry_multiplier, bool) or not isinstance(
        _retry_multiplier, (int, np.integer)
    ):
        raise ValueError("_retry_multiplier must be a positive integer.")
    retry_multiplier = int(_retry_multiplier)
    if retry_multiplier < 1:
        raise ValueError("_retry_multiplier must be a positive integer.")
    calibrations = {} if calibrations is None else calibrations
    calibrations = _normalize_calibrations(tree, calibrations, dist_floor=DIST_FLOOR)

    calibration_time_scale = 1.0
    if calibrations:
        finite_upper = [
            float(upper)
            for _, upper in calibrations.values()
            if np.isfinite(upper) and float(upper) > 0.0
        ]
        positive_lower = [
            float(lower)
            for lower, _ in calibrations.values()
            if np.isfinite(lower) and float(lower) > 0.0
        ]
        if finite_upper:
            calibration_time_scale = max(finite_upper)
        elif positive_lower:
            calibration_time_scale = max(positive_lower)
        calibrations = {
            int(idx): (
                _canonical_calibration_ratio(lower, calibration_time_scale),
                _canonical_calibration_ratio(upper, calibration_time_scale),
            )
            for idx, (lower, upper) in calibrations.items()
        }

    continuation_ages = _validate_correlated_warm_start(
        _initial_ages, tree.nnodes, "_initial_ages", positive=False
    )
    if continuation_ages is not None:
        continuation_ages /= calibration_time_scale
    continuation_rates = _validate_correlated_warm_start(
        _initial_rates, tree.nedges, "_initial_rates", positive=True
    )
    if continuation_rates is not None:
        continuation_rates *= calibration_time_scale

    interior_ages, _ = _get_init_ages(tree, calibrations)
    dists_o = _validate_branch_lengths(tree)
    branch_diagnostics = _correlated_input_branch_diagnostics(tree, dists_o)
    if branch_diagnostics["zero_length_branch_count"]:
        logger.warning(
            "Correlated-rate input contains "
            f"{branch_diagnostics['zero_length_branch_count']} exact-zero edges "
            f"({branch_diagnostics['zero_length_internal_branch_count']} internal, "
            f"{branch_diagnostics['zero_length_terminal_branch_count']} terminal). "
            "Zeros are retained as observations, but can weaken rate-time "
            "identifiability; inspect multistart stability diagnostics."
        )

    independent_ages = np.asarray(interior_ages, dtype=float).copy()
    clock_warm_start_used = False
    try:
        clock = edges_make_ultrametric_clock(
            tree,
            calibrations=calibrations,
            full=True,
            inplace=False,
            max_iter=min(int(max_iter), 200),
            max_fun=min(int(max_fun), 500),
            max_refine=0,
            nstarts=1,
            ncores=1,
            seed=seed,
            _observation_mask=_observation_mask,
            _retry_multiplier=1,
            _direct_age_fallback=False,
        )
        if clock["converged"]:
            independent_ages = (
                clock["tree"].get_node_data("height").to_numpy(dtype=float)
            )
            clock_warm_start_used = True
    except (ToytreeError, RuntimeError, ValueError):
        pass

    rates_bounds, ages_bounds_map = _get_params_bounds(tree, calibrations)
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    ages_idxs = np.asarray(sorted(ages_bounds_map), dtype=int)
    ages_bounds = [ages_bounds_map[idx] for idx in ages_idxs]
    children_map = _get_children_map_from_edges(edges)
    observation_mask = _validate_observation_mask(_observation_mask, tree.nedges)
    if observation_loss == "multiplicative_gamma" and np.any(
        dists_o[observation_mask] <= 0.0
    ):
        raise ValueError(
            "multiplicative_gamma requires strictly positive observed branches."
        )
    edata = np.column_stack([dists_o, gammaln(dists_o + 1.0)])
    child_to_eidx = {int(child): idx for idx, (child, _) in enumerate(edges)}
    parent_edges = np.asarray(
        [child_to_eidx.get(int(parent), -1) for _, parent in edges], dtype=int
    )
    log_rate_bounds = [
        (np.log(max(lo, RATE_FLOOR)), np.log(max(hi, RATE_FLOOR)))
        for lo, hi in (rates_bounds[idx] for idx in range(tree.nedges))
    ]

    def rates_from_ages(ages: np.ndarray) -> np.ndarray:
        times = ages[edges[:, 1]] - ages[edges[:, 0]]
        raw = np.clip(dists_o / times, RATE_FLOOR, None)
        observed_total = float(np.sum(dists_o[observation_mask]))
        time_total = float(np.sum(times[observation_mask]))
        common = max(observed_total / time_total, RATE_FLOOR)
        deviations = np.log(raw) - float(np.mean(np.log(raw)))
        shrinkage = 1.0 / (1.0 + np.sqrt(lam))
        return np.exp(np.log(common) + shrinkage * deviations)

    independent_rates = rates_from_ages(independent_ages)
    base_starts: list[tuple[str, np.ndarray, np.ndarray]] = [
        ("independent", independent_ages, independent_rates)
    ]
    has_continuation = continuation_ages is not None or continuation_rates is not None
    if has_continuation:
        continued_ages = (
            independent_ages
            if continuation_ages is None
            else np.asarray(continuation_ages, dtype=float)
        )
        continued_rates = (
            rates_from_ages(continued_ages)
            if continuation_rates is None
            else np.asarray(continuation_rates, dtype=float)
        )
        base_starts.append(("continuation", continued_ages, continued_rates))
    elif clock_warm_start_used:
        base_starts.append(
            (
                "interior",
                np.asarray(interior_ages, dtype=float),
                rates_from_ages(interior_ages),
            )
        )

    valid_loglik = _correlated_branch_pseudologlik(
        independent_rates,
        independent_ages,
        edges,
        edata,
        parent_edges,
        lam,
        None,
        observation_mask,
        observation_loss,
    )
    interior_age_params = _encode_age_params(
        interior_ages,
        ages_idxs,
        ages_bounds,
        children_map,
        dist_floor=DIST_FLOOR,
    )
    requested_nstarts = max(1, int(nstarts))
    effective_nstarts = max(requested_nstarts, len(base_starts))
    effective_ncores = max(1, int(ncores))
    rng = np.random.default_rng(seed)
    rsize = tree.nedges
    asize = ages_idxs.size
    bounds = log_rate_bounds + [(None, None)] * asize
    payloads = []
    for start in range(effective_nstarts):
        if start < len(base_starts):
            start_kind, age_start, rate_start = base_starts[start]
        else:
            base_kind, base_ages, base_rates = base_starts[start % len(base_starts)]
            start_kind = f"{base_kind}_perturbed"
            rate_start = np.asarray(base_rates, dtype=float) * np.exp(
                rng.normal(0.0, 0.25, size=rsize)
            )
            age_params = np.clip(interior_age_params, -6.0, 6.0)
            age_params += rng.normal(0.0, 0.25, size=asize)
            try:
                age_start = _decode_age_params(
                    age_params,
                    interior_ages,
                    ages_idxs,
                    ages_bounds,
                    children_map,
                    dist_floor=DIST_FLOOR,
                )
            except (ToytreeError, ValueError):
                age_start = np.asarray(base_ages, dtype=float)
        try:
            encoded_ages = _encode_age_params(
                age_start,
                ages_idxs,
                ages_bounds,
                children_map,
                dist_floor=DIST_FLOOR,
            )
        except (ToytreeError, ValueError):
            age_start = np.asarray(interior_ages, dtype=float)
            encoded_ages = interior_age_params.copy()
        start_params = np.hstack(
            [np.log(np.clip(rate_start, RATE_FLOOR, None)), encoded_ages]
        )
        payloads.append(
            {
                "start": start,
                "start_kind": start_kind,
                "params": start_params,
                "bounds": bounds,
                "rates_init": np.asarray(rate_start, dtype=float),
                "ages_init": np.asarray(interior_ages, dtype=float),
                "age_start_ages": np.asarray(age_start, dtype=float),
                "ages_idxs": ages_idxs,
                "ages_bounds": ages_bounds,
                "children_map": children_map,
                "edges": edges,
                "edata": edata,
                "parent_edges": parent_edges,
                "lam": lam,
                "valid_loglik": valid_loglik,
                "observation_mask": observation_mask,
                "observation_loss": observation_loss,
                "max_iter": int(max_iter),
                "max_fun": int(max_fun),
                "max_refine": int(max_refine),
                "retry_multiplier": retry_multiplier,
            }
        )

    starts = _run_multistart(_fit_correlated_start, payloads, ncores=effective_ncores)

    def finalize_start(result: dict[str, Any]) -> None:
        if "ages" not in result or "rates" not in result:
            return
        try:
            result_ages = _finalize_ultrametric_ages(
                tree,
                np.asarray(result["ages"], dtype=float),
                calibrations=calibrations,
                dist_floor=DIST_FLOOR,
            )
            result_rates = np.asarray(result["rates"], dtype=float)
            rescored = _correlated_branch_pseudologlik(
                result_rates,
                result_ages,
                edges,
                edata,
                parent_edges,
                lam,
                valid_loglik,
                observation_mask,
                observation_loss,
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
    preliminary_stability = _assess_correlated_solution_stability(
        starts, preliminary_best, ntips=tree.ntips
    )
    basin_confirmation_run = False
    if (
        effective_nstarts >= 2
        and preliminary_best.get("converged", False)
        and int(preliminary_stability["near_optimal_starts"]) < 2
    ):
        confirmation_ages = 0.95 * np.asarray(
            preliminary_best["ages"], dtype=float
        ) + 0.05 * np.asarray(interior_ages, dtype=float)
        confirmation_rates = np.asarray(
            preliminary_best["rates"], dtype=float
        ) * np.exp(rng.normal(0.0, 0.05, size=rsize))
        confirmation_payload = dict(payloads[0])
        confirmation_payload.update(
            {
                "start": effective_nstarts,
                "start_kind": "basin_confirmation",
                "params": np.hstack([np.log(confirmation_rates), interior_age_params]),
                "rates_init": confirmation_rates,
                "age_start_ages": confirmation_ages,
            }
        )
        confirmation = _run_multistart(
            _fit_correlated_start, [confirmation_payload], ncores=1
        )[0]
        finalize_start(confirmation)
        starts.append(confirmation)
        basin_confirmation_run = True

    best = _select_best_multistart(starts)
    stability = _assess_correlated_solution_stability(starts, best, ntips=tree.ntips)
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

    fit_ages = np.asarray(best["ages"], dtype=float)
    fit_rates = np.asarray(best["rates"], dtype=float)
    penalized_pseudologlik = _correlated_branch_pseudologlik(
        fit_rates,
        fit_ages,
        edges,
        edata,
        parent_edges,
        lam,
        valid_loglik,
        observation_mask,
        observation_loss,
    )
    pseudologlik = _correlated_branch_pseudologlik(
        fit_rates,
        fit_ages,
        edges,
        edata,
        parent_edges,
        0.0,
        valid_loglik,
        observation_mask,
        observation_loss,
    )
    penalty = _correlated_penalty(fit_rates, parent_edges)
    basal = parent_edges < 0
    profiled_root_rate = float(np.exp(np.mean(np.log(fit_rates[basal]))))
    time_dists = fit_ages[edges[:, 1]] - fit_ages[edges[:, 0]]
    expected = time_dists * fit_rates
    ages = fit_ages * calibration_time_scale
    rates = fit_rates / calibration_time_scale
    tree = tree.set_node_data("height", ages, inplace=inplace)
    if not full:
        return tree
    return {
        "model": "correlated",
        "pseudologlik": pseudologlik,
        "penalized_pseudologlik": penalized_pseudologlik,
        **(
            _result_observation_metadata()
            if observation_loss == "fractional_poisson"
            else {
                "observation_model": "multiplicative_gamma_working_loss",
                "branch_length_units": "input_tree_units",
            }
        ),
        "penalty": penalty,
        "penalty_model": "summed_log_rate_autocorrelation",
        "scale_invariant": True,
        "calibration_time_unit_invariant": True,
        "internal_calibration_time_scale": calibration_time_scale,
        "clock_warm_start_used": clock_warm_start_used,
        "interior_multistart_included": bool(
            not clock_warm_start_used
            or any(
                str(item.get("start_kind", "")).startswith("interior")
                for item in starts
            )
        ),
        "optimizer_strategy": "profiled_rates_joint_polish",
        "lam": lam,
        "nparams": len(bounds),
        "profiled_root_rate": profiled_root_rate / calibration_time_scale,
        "rates": list(rates),
        "expected_branch_lengths": expected.tolist(),
        "observed_branch_lengths": dists_o.tolist(),
        "tree": tree,
        "converged": bool(best["converged"]),
        "optimizer_message": str(best["message"]),
        "nfev": int(best.get("nfev", -1)),
        "nit": int(best.get("nit", -1)),
        "refinement_cycles": int(best.get("refinement_cycles", -1)),
        "profile_evaluations": int(best.get("profile_evaluations", -1)),
        "outer_profile_converged": bool(best.get("outer_profile_converged", False)),
        "profile_rate_converged": bool(best.get("profile_rate_converged", False)),
        "rate_gradient_max_abs": best.get("rate_gradient_max_abs"),
        "rate_gradient_before_final_polish": best.get(
            "rate_gradient_before_final_polish"
        ),
        "final_rate_polish_used": bool(best.get("final_rate_polish_used", False)),
        "final_rate_polish_accepted": bool(
            best.get("final_rate_polish_accepted", False)
        ),
        "final_rate_polish_message": best.get("final_rate_polish_message"),
        "final_rate_polish_stationarity_steps": int(
            best.get("final_rate_polish_stationarity_steps", 0)
        ),
        "final_joint_converged": bool(best.get("final_joint_converged", False)),
        "gradient_max_abs": best.get("gradient_max_abs"),
        "optimizer_retries": int(best.get("optimizer_retries", 0)),
        "observation_loss": observation_loss,
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
                "profile_evaluations": int(item.get("profile_evaluations", -1)),
                "outer_profile_converged": bool(
                    item.get("outer_profile_converged", False)
                ),
                "profile_rate_converged": bool(
                    item.get("profile_rate_converged", False)
                ),
                "rate_gradient_max_abs": item.get("rate_gradient_max_abs"),
                "rate_gradient_before_final_polish": item.get(
                    "rate_gradient_before_final_polish"
                ),
                "final_rate_polish_used": bool(
                    item.get("final_rate_polish_used", False)
                ),
                "final_rate_polish_accepted": bool(
                    item.get("final_rate_polish_accepted", False)
                ),
                "final_rate_polish_message": item.get("final_rate_polish_message"),
                "final_rate_polish_stationarity_steps": int(
                    item.get("final_rate_polish_stationarity_steps", 0)
                ),
                "final_joint_converged": bool(item.get("final_joint_converged", False)),
                "gradient_max_abs": item.get("gradient_max_abs"),
                "optimizer_retries": int(item.get("optimizer_retries", 0)),
            }
            for item in starts
        ],
    }


def _correlated_penalty(rates_hat: np.ndarray, parent_edges: np.ndarray) -> float:
    """Return summed log-rate roughness including a profiled root rate."""
    rates_hat = np.clip(np.asarray(rates_hat, dtype=float), RATE_FLOOR, None)
    log_rates = np.log(rates_hat)
    nonbasal = parent_edges >= 0
    basal = ~nonbasal

    penalty = 0.0
    if np.any(nonbasal):
        diffs = log_rates[nonbasal] - log_rates[parent_edges[nonbasal]]
        penalty += float(np.sum(diffs * diffs))
    if np.any(basal):
        root_log_rate = float(np.mean(log_rates[basal]))
        basal_diffs = log_rates[basal] - root_log_rate
        penalty += float(np.sum(basal_diffs * basal_diffs))
    return penalty


def _correlated_branch_pseudologlik(
    rates_hat,
    ages_hat,
    edges,
    edata,
    parent_edges,
    lam,
    valid_loglik,
    observation_mask=None,
    observation_loss="fractional_poisson",
) -> float:
    """Return correlated penalized branch-length pseudologlikelihood."""
    if valid_loglik is None:
        valid_loglik = -1.0

    dists_hat = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    if np.any(dists_hat <= DIST_FLOOR):
        return valid_loglik - INVALID_LOG_LIK_DROP

    rates_hat = np.clip(rates_hat, RATE_FLOOR, None)
    pdists = dists_hat * rates_hat
    if np.any(pdists <= RATE_FLOOR) or np.any(~np.isfinite(pdists)):
        return valid_loglik - INVALID_LOG_LIK_DROP

    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    observation_loss = _validate_correlated_observation_loss(observation_loss)
    if observation_loss == "fractional_poisson":
        terms = edata[:, 0] * np.log(pdists) - pdists - edata[:, 1]
    else:
        if np.any(edata[mask, 0] <= 0.0):
            return valid_loglik - INVALID_LOG_LIK_DROP
        ratio = edata[:, 0] / pdists
        terms = -(ratio - np.log(ratio) - 1.0)
    pseudologlik = np.sum(terms[mask])
    if not np.isfinite(pseudologlik):
        return valid_loglik - INVALID_LOG_LIK_DROP

    penalty = _correlated_penalty(rates_hat, parent_edges)
    if not np.isfinite(penalty):
        return valid_loglik - INVALID_LOG_LIK_DROP
    return float(pseudologlik - lam * penalty)


def _decode_age_params_with_jacobian(
    age_params: np.ndarray,
    ages_base: np.ndarray,
    ages_idxs: np.ndarray,
    ages_bounds: list[tuple[float, float]],
    children_map: dict[int, np.ndarray],
    dist_floor: float = DIST_FLOOR,
) -> tuple[np.ndarray, np.ndarray]:
    """Decode ages and their piecewise Jacobian with respect to parameters."""
    ages_hat = np.asarray(ages_base, dtype=float).copy()
    nparams = age_params.size
    jacobian = np.zeros((ages_hat.size, nparams), dtype=float)
    for pidx, (z, nidx, (lo, hi)) in enumerate(zip(age_params, ages_idxs, ages_bounds)):
        nidx = int(nidx)
        child_idxs = children_map.get(nidx, np.array([], dtype=int))
        child_max = float(ages_hat[child_idxs].max()) if child_idxs.size else 0.0
        lo_eff = max(float(lo), child_max + dist_floor)
        lo_jac = np.zeros(nparams, dtype=float)
        if child_idxs.size and child_max + dist_floor > float(lo):
            child_idx = int(child_idxs[np.argmax(ages_hat[child_idxs])])
            lo_jac = jacobian[child_idx].copy()
        if np.isfinite(hi):
            if lo_eff >= float(hi):
                raise ValueError(
                    f"cannot decode node {nidx} age: effective lower bound "
                    f"{lo_eff:.6g} is not below upper bound {float(hi):.6g}."
                )
            width = float(hi) - lo_eff
            absolute_margin = max(
                2.0 * dist_floor,
                8.0 * np.spacing(max(abs(lo_eff), abs(float(hi)), 1.0)),
            )
            fraction_margin = min(0.25, absolute_margin / width)
            raw_fraction = float(expit(z))
            fraction = float(
                np.clip(raw_fraction, fraction_margin, 1.0 - fraction_margin)
            )
            age = lo_eff + width * fraction
            jacobian[nidx] = (1.0 - fraction) * lo_jac
            if fraction == raw_fraction:
                jacobian[nidx, pidx] += width * fraction * (1.0 - fraction)
        else:
            clipped = float(np.clip(z, -700.0, 700.0))
            offset = float(np.exp(clipped))
            age = lo_eff + offset
            jacobian[nidx] = lo_jac
            if -700.0 < z < 700.0:
                jacobian[nidx, pidx] += offset
        ages_hat[nidx] = age
    return ages_hat, jacobian


def _correlated_penalty_gradient(
    log_rates: np.ndarray, parent_edges: np.ndarray
) -> np.ndarray:
    """Return the gradient of log-rate roughness by log edge rate."""
    gradient = np.zeros_like(log_rates, dtype=float)
    nonbasal_idxs = np.flatnonzero(parent_edges >= 0)
    if nonbasal_idxs.size:
        parent_idxs = parent_edges[nonbasal_idxs]
        diffs = log_rates[nonbasal_idxs] - log_rates[parent_idxs]
        np.add.at(gradient, nonbasal_idxs, 2.0 * diffs)
        np.add.at(gradient, parent_idxs, -2.0 * diffs)
    basal_idxs = np.flatnonzero(parent_edges < 0)
    if basal_idxs.size:
        centered = log_rates[basal_idxs] - np.mean(log_rates[basal_idxs])
        np.add.at(gradient, basal_idxs, 2.0 * centered)
    return gradient


def objective_correlated_with_gradient(
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
    observation_mask,
    observation_loss,
):
    """Return the correlated negative objective and its analytic gradient."""
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
        ages_hat, age_jacobian = _decode_age_params_with_jacobian(
            params,
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
        )
    else:
        log_rates = np.asarray(params[:rsize], dtype=float)
        rates_hat = _unpack_log_rates(log_rates)
        ages_hat, age_jacobian = _decode_age_params_with_jacobian(
            params[rsize : rsize + asize],
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
        )

    objective = -_correlated_branch_pseudologlik(
        rates_hat,
        ages_hat,
        edges,
        edata,
        parent_edges,
        lam,
        valid_loglik,
        observation_mask,
        observation_loss,
    )
    times = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    expected = rates_hat * times
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    if (
        not np.isfinite(objective)
        or np.any(times <= DIST_FLOOR)
        or np.any(expected <= RATE_FLOOR)
        or np.any(~np.isfinite(expected))
    ):
        return float(objective), np.zeros_like(params, dtype=float)

    data_gradient = np.zeros(rsize, dtype=float)
    if observation_loss == "fractional_poisson":
        data_gradient[mask] = expected[mask] - edata[mask, 0]
    else:
        data_gradient[mask] = 1.0 - edata[mask, 0] / expected[mask]
    rate_gradient = data_gradient + lam * _correlated_penalty_gradient(
        log_rates, parent_edges
    )

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
    observation_mask,
    observation_loss,
):
    """Return negative penalized log-likelihood under correlated model."""
    objective, _ = objective_correlated_with_gradient(
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
        observation_mask,
        observation_loss,
    )
    return objective


if __name__ == "__main__":
    import toytree

    toytree.set_log_level("DEBUG")

    tree = get_tree_with_correlated_rates(ntips=40, mean=3, sigma=2, seed=123)
    res = edges_make_ultrametric_correlated(
        tree,
        lam=0.5,
        calibrations={-1: 20.0},
        full=True,
        max_iter=2000,
        max_fun=2000,
        max_refine=4,
    )
    print(res)
