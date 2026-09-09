#!/usr/bin/env python

"""Independent branch-rate penalized branch-length pseudolikelihoods."""

import warnings
from typing import Any, Union

import numpy as np
from loguru import logger
from scipy import stats
from scipy.optimize import LinearConstraint, OptimizeResult, minimize
from scipy.special import gammaln

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_pseudolikelihood.clock import (
    edges_make_ultrametric_clock,
)
from toytree.mod._src.penalized_pseudolikelihood.optimization import (
    assess_solution_stability,
    decode_age_params_with_jacobian,
    optimizer_stopped_at_limit,
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
from toytree.utils import ToytreeError

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


def _ucln_penalty_gradient(log_rates: np.ndarray) -> np.ndarray:
    """Return the centered log-rate penalty gradient by log rate."""
    values = np.asarray(log_rates, dtype=float)
    return 2.0 * (values - float(np.mean(values)))


def _projected_gradient_max_abs(
    params: np.ndarray,
    gradient: np.ndarray,
    bounds: list[tuple[float | None, float | None]],
    tolerance: float = 1e-10,
) -> float:
    """Return the largest feasible first-order gradient component."""
    values = np.asarray(params, dtype=float)
    projected = np.asarray(gradient, dtype=float).copy()
    for idx, (lower, upper) in enumerate(bounds):
        if lower is not None and values[idx] <= float(lower) + tolerance:
            if projected[idx] > 0.0:
                projected[idx] = 0.0
        if upper is not None and values[idx] >= float(upper) - tolerance:
            if projected[idx] < 0.0:
                projected[idx] = 0.0
    return float(np.max(np.abs(projected))) if projected.size else 0.0


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
        "uncorrelated_lognormal",
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
        projected = _projected_gradient_max_abs(params, gradient, rate_bounds)
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

    projected = _projected_gradient_max_abs(params, gradient, rate_bounds)
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


def _direct_age_linear_constraint(
    ages_base: np.ndarray,
    ages_idxs: np.ndarray,
    edges: np.ndarray,
) -> LinearConstraint | tuple[()]:
    """Return linear parent-older-than-child constraints for free ages."""
    positions = {int(nidx): pos for pos, nidx in enumerate(ages_idxs)}
    rows = []
    lower = []
    for child, parent in np.asarray(edges, dtype=int):
        row = np.zeros(ages_idxs.size, dtype=float)
        constant = 0.0
        if int(parent) in positions:
            row[positions[int(parent)]] += 1.0
        else:
            constant += float(ages_base[int(parent)])
        if int(child) in positions:
            row[positions[int(child)]] -= 1.0
        else:
            constant -= float(ages_base[int(child)])
        if np.any(row):
            rows.append(row)
            lower.append(DIST_FLOOR - constant)
        elif constant < DIST_FLOOR:
            raise ToytreeError("fixed node ages violate positive branch lengths.")
    if not rows:
        return ()
    matrix = np.vstack(rows)
    return LinearConstraint(
        matrix,
        np.asarray(lower, dtype=float),
        np.full(len(rows), np.inf),
    )


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
        "uncorrelated_lognormal",
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


def _minimize_profiled_ucln_ages(
    objective: _ProfiledUCLNObjective,
    initial: np.ndarray,
    bounds: list[tuple[float, float]],
    constraints: tuple,
    max_iter: int,
    ftol: float,
):
    """Run SLSQP while suppressing its benign trial-point clipping warning."""
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Values in x were outside bounds during a minimize step",
            category=RuntimeWarning,
            module=r"scipy\.optimize\._slsqp_py",
        )
        return minimize(
            fun=objective,
            args=(),
            x0=initial,
            method="SLSQP",
            jac=True,
            bounds=bounds,
            constraints=constraints,
            options=dict(maxiter=max_iter, ftol=ftol, disp=False),
        )


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
    linear_constraint = _direct_age_linear_constraint(
        ages_init,
        ages_idxs,
        edges,
    )
    constraints = () if linear_constraint == () else (linear_constraint,)

    optimizer_retries = 0
    outer_nfev = 0
    outer_nit = 0
    if asize:
        outer = _minimize_profiled_ucln_ages(
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
            retry = _minimize_profiled_ucln_ages(
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
        "uncorrelated_lognormal",
    )
    params = np.hstack(
        [_pack_log_rates(rates_init, rate_floor=RATE_FLOOR), age_params_init]
    )

    requested_nstarts = max(1, int(nstarts))
    effective_nstarts = requested_nstarts
    effective_ncores = max(1, int(ncores))
    rng = np.random.default_rng(seed)
    rsize = rates_init.size
    asize = ages_idxs.size
    payloads = []
    for start in range(effective_nstarts):
        start_params = params.copy()
        age_start_ages = warm_ages_init.copy()
        if clock_warm_start_used and start == 1:
            start_params[rsize:] = interior_age_params
            age_start_ages = interior_ages_init.copy()
        elif start:
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
                "uncorrelated_lognormal",
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
        "uncorrelated_lognormal",
    )
    pseudologlik = _independent_branch_pseudologlik(
        fit_rates,
        fit_ages,
        edges,
        edata,
        0.0,
        valid_loglik,
        observation_mask,
        "uncorrelated_lognormal",
    )
    penalty = _uncorrelated_lognormal_penalty(fit_rates)
    time_dists = fit_ages[edges[:, 1]] - fit_ages[edges[:, 0]]
    expected = time_dists * fit_rates
    ages = fit_ages * calibration_time_scale
    rates = fit_rates / calibration_time_scale
    tree = tree.set_node_data("height", ages, inplace=inplace)
    if not full:
        return tree
    return {
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
        "tree": tree,
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
        **stability,
        "starts": [
            {
                "start": int(item["start"]),
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
    _observation_mask: np.ndarray | None = None,
    _retry_multiplier: int = 4,
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
    reported as stable.
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
        _observation_mask=_observation_mask,
        _retry_multiplier=_retry_multiplier,
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
    """Fit non-correlated relaxed rates for parity with ape::chronos.

    The penalty compares the empirical CDF of raw branch rates with a Gamma
    CDF whose shape is the mean raw rate and whose scale is one. Consequently,
    this model is intentionally sensitive to the calibration time unit. It is
    provided for ape::chronos parity; use ``uncorrelated_lognormal`` for new
    uncorrelated-rate analyses.

    Input edges may use any consistent, finite, non-negative additive unit for
    which branch length equals elapsed time multiplied by rate; expected
    substitutions per site are common but not required. Calibration ages
    define the output-tree time unit, and fitted rates are in input-edge units
    per calibration unit. Without calibrations, the root age is fixed to 1,
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
    if np.any(dists_hat < DIST_FLOOR):
        return valid_loglik - INVALID_LOG_LIK_DROP

    # get product of dists(time) and rates
    rates_hat = np.clip(rates_hat, RATE_FLOOR, None)
    pdists = dists_hat * rates_hat
    if np.any(pdists <= 0.0) or np.any(~np.isfinite(pdists)):
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
