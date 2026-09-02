#!/usr/bin/env python

"""Discrete-mixture branch-length pseudolikelihood fitting."""

from numbers import Real
from typing import Any, Literal, Union

import numpy as np
from loguru import logger
from scipy.optimize import minimize
from scipy.special import gammaln, logsumexp

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_pseudolikelihood.clock import (
    edges_make_ultrametric_clock,
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
    _validate_observation_mask,
    get_tree_with_categorical_rates,
)
from toytree.utils import ToytreeError

__all__ = [
    "edges_make_ultrametric_discrete",
    "edges_make_ultrametric_discrete_gamma",
]
RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
INVALID_LOG_LIK_DROP = 1e6
DEFAULT_BRANCH_CV = 0.1
ObservationModel = Literal["fractional_poisson", "multiplicative_gamma"]


def _validate_branch_cv(branch_cv: Any) -> float:
    """Return a finite, strictly positive Gamma branch CV."""
    if isinstance(branch_cv, bool) or not isinstance(branch_cv, Real):
        raise ToytreeError("branch_cv must be a finite positive real number.")
    value = float(branch_cv)
    if not np.isfinite(value) or value <= 0.0:
        raise ToytreeError("branch_cv must be a finite positive real number.")
    return value


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
    observation_model: ObservationModel,
    gamma_shape: float | None,
) -> tuple[float, np.ndarray]:
    """Return joint negative mixture log-likelihood and analytic gradient."""
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

    if observation_model == "fractional_poisson":
        components = observed[None, :] * np.log(means) - means - edata[:, 1][None, :]
        dlog_dmean = observed[None, :] / means - 1.0
    else:
        if gamma_shape is None or np.any(observed <= 0.0):
            return -(valid_loglik - INVALID_LOG_LIK_DROP), np.zeros_like(params)
        shape = float(gamma_shape)
        components = (
            shape * np.log(observed)[None, :]
            - shape * observed[None, :] / means
            - gammaln(shape)
            - shape * np.log(means / shape)
        )
        dlog_dmean = shape * (observed[None, :] / means - 1.0) / means

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
        (
            rate_jac.T @ rate_score,
            age_jac.T @ age_score,
            weight_score,
        )
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
        bounds=[(-30.0, 30.0)] * len(x0),
        options={
            "maxiter": int(max_iter),
            "maxfun": int(max_fun),
            "ftol": 1e-12,
            "gtol": 1e-6,
        },
    )


def _select_best_discrete_start(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return the lowest finalized finite objective, independent of status."""
    finite = [
        result
        for result in results
        if np.isfinite(result.get("objective", float("inf")))
    ]
    if not finite:
        raise RuntimeError("all discrete multistarts failed")
    return min(finite, key=lambda result: float(result["objective"]))


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
        payload.get("observation_model", "fractional_poisson"),
        payload.get("gamma_shape"),
    )
    max_iter = int(payload["max_iter"])
    max_fun = int(payload["max_fun"])
    rsize = int(payload["rate_params_init"].size)
    asize = int(payload["ages_idxs"].size)
    fsize = int(payload["weight_params_init"].size)

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
        bounds=[(-30.0, 30.0)] * mixture_indices.size,
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
                bounds=[(-30.0, 30.0)] * current[block].size,
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
    retries = 0
    if not authoritative.success:
        retries = 1
        retry = _run_joint_fit(current, args, max_iter * 4, max_fun * 4)
        total_nfev += int(getattr(retry, "nfev", 0))
        total_nit += int(getattr(retry, "nit", 0))
        tolerance = 1e-10 * max(1.0, abs(float(authoritative.fun)))
        if (
            np.isfinite(retry.fun)
            and float(retry.fun) <= float(authoritative.fun) + tolerance
        ):
            authoritative = retry
            current = np.asarray(retry.x, dtype=float).copy()

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
    first_order_converged = bool(np.isfinite(objective) and gradient_max_abs <= 1e-4)
    converged = bool(
        np.isfinite(objective) and (authoritative.success or first_order_converged)
    )
    message = str(authoritative.message)
    if first_order_converged and not authoritative.success:
        message = (
            "first-order convergence after line-search termination "
            f"(max|gradient|={gradient_max_abs:.3g})"
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
        "nfev": total_nfev,
        "nit": total_nit,
        "refinement_cycles": cycles,
        "final_joint_converged": bool(authoritative.success or first_order_converged),
        "gradient_max_abs": gradient_max_abs,
        "optimizer_retries": retries,
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
    nstarts: int = 4,
    ncores: int = 1,
    seed: int | None = None,
    _observation_mask: np.ndarray | None = None,
    _observation_model: ObservationModel = "fractional_poisson",
    _branch_cv: float | None = None,
) -> Union[ToyTree, dict[str, Any]]:
    """Fit the chronos-compatible fractional-Poisson discrete mixture.

    Every branch likelihood is independently integrated over `ncategories`
    ordered rate categories using fitted simplex weights. Categories are not
    persistent assignments inherited along the tree. Input branches may use
    any consistent additive unit, and fitted rates use that input unit per
    calibration-time unit. This model is invariant to calibration-time units
    but not to numerical rescaling of input branches, whose magnitude controls
    fractional-Poisson working information. Use
    :func:`edges_make_ultrametric_discrete_gamma` when input-scale invariance
    is required.

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
    if _observation_model not in {"fractional_poisson", "multiplicative_gamma"}:
        raise ValueError(f"unknown observation model: {_observation_model}")
    gamma_shape = None
    if _observation_model == "multiplicative_gamma":
        _branch_cv = _validate_branch_cv(_branch_cv)
        gamma_shape = 1.0 / (_branch_cv * _branch_cv)
    if calibrations is None:
        calibrations = {}
    calibrations = _normalize_calibrations(
        tree,
        calibrations,
        dist_floor=DIST_FLOOR,
    )

    # strict identity with clock model when ncategories == 1.
    if int(ncategories) == 1 and _observation_model == "fractional_poisson":
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
        dres["calibration_time_unit_invariant"] = True
        dres["input_branch_scale_invariant"] = False
        return dres

    # Normalize Gamma input and calibration units internally. The transformed
    # optimization problem is identical under either supported unit change,
    # including its absolute stopping criteria and starting coordinates.
    dists_o = _validate_branch_lengths(tree)
    observation_scale = 1.0
    time_scale = 1.0
    fit_tree = tree
    if _observation_model == "multiplicative_gamma":
        if np.any(dists_o <= 0.0):
            raise ToytreeError(
                "method='discrete_gamma' requires strictly positive branch lengths."
            )
        observation_scale = float(np.exp(np.mean(np.log(dists_o))))
        normalized_dists = np.round(dists_o / observation_scale, 10)
        original_edges = tree.get_edges("idx")
        fit_tree = tree.set_node_data(
            "dist",
            {
                int(child): float(normalized_dists[index])
                for index, (child, _) in enumerate(original_edges)
            },
            inplace=False,
        )
        if calibrations:
            time_scale = max(float(upper) for _, upper in calibrations.values())
            calibrations = {
                int(idx): (
                    round(float(lower) / time_scale, 14),
                    round(float(upper) / time_scale, 14),
                )
                for idx, (lower, upper) in calibrations.items()
            }

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
            _observation_mask=_observation_mask,
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
    observation_mask = _validate_observation_mask(_observation_mask, fit_tree.nedges)

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
        _observation_model,
        gamma_shape,
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
                observation_model=_observation_model,
                gamma_shape=gamma_shape,
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
                _observation_model,
                gamma_shape,
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
        _observation_model,
        gamma_shape,
    )
    ages = ages_fit * time_scale
    rates = rates_fit * observation_scale / time_scale
    time_dists = ages[edges[:, 1]] - ages[edges[:, 0]]
    expected = time_dists * float(np.dot(weights, rates))
    stability = assess_solution_stability(starts, best, ntips=fit_tree.ntips)
    output_tree = tree.set_node_data("height", ages, inplace=inplace)

    # return as a tree or a dict
    if not full:
        return output_tree
    return {
        "model": (
            "discrete"
            if _observation_model == "fractional_poisson"
            else "discrete_gamma"
        ),
        "pseudologlik": pseudologlik,
        "penalized_pseudologlik": pseudologlik,
        "observation_model": _observation_model,
        # Keep the legacy key value until the V6-frozen shared metadata
        # migration can update every model and its tests together.
        "branch_length_units": (
            "substitutions_per_site"
            if _observation_model == "fractional_poisson"
            else "input_tree_units"
        ),
        "calibration_time_unit_invariant": True,
        "input_branch_scale_invariant": (_observation_model == "multiplicative_gamma"),
        **(
            {
                "branch_cv": float(_branch_cv),
                "gamma_shape": float(gamma_shape),
                "observation_scale": observation_scale,
                "time_scale": time_scale,
            }
            if _observation_model == "multiplicative_gamma"
            else {}
        ),
        "nparams": len(bounds),
        "ncategories": ncategories,
        "rates": list(rates),
        "weights": list(weights),
        "expected_branch_lengths": expected.tolist(),
        "observed_branch_lengths": dists_o.tolist(),
        "tree": output_tree,
        "converged": bool(best["converged"]),
        "optimizer_message": str(best["message"]),
        "nfev": int(best.get("nfev", -1)),
        "nit": int(best.get("nit", -1)),
        "gradient_max_abs": best.get("gradient_max_abs"),
        "optimizer_retries": int(best.get("optimizer_retries", 0)),
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
                "nfev": int(i.get("nfev", -1)),
                "nit": int(i.get("nit", -1)),
                "refinement_cycles": int(i.get("refinement_cycles", 0)),
                "final_joint_converged": bool(i.get("final_joint_converged", False)),
                "gradient_max_abs": i.get("gradient_max_abs"),
                "optimizer_retries": int(i.get("optimizer_retries", 0)),
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
    observation_model: ObservationModel = "fractional_poisson",
    gamma_shape: float | None = None,
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
        observation_model,
        gamma_shape,
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
    observation_model: ObservationModel = "fractional_poisson",
    gamma_shape: float | None = None,
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
    if observation_model == "fractional_poisson":
        category_loglik = (
            observed[np.newaxis, :] * np.log(pdists)
            - pdists
            - edata[:, 1][np.newaxis, :]
        )
    elif observation_model == "multiplicative_gamma":
        if gamma_shape is None or gamma_shape <= 0.0 or np.any(observed <= 0.0):
            return invalid_score
        shape = float(gamma_shape)
        category_loglik = (
            shape * np.log(observed)[np.newaxis, :]
            - shape * observed[np.newaxis, :] / pdists
            - gammaln(shape)
            - shape * np.log(pdists / shape)
        )
    else:
        raise ValueError(f"unknown observation model: {observation_model}")
    if np.any(~np.isfinite(category_loglik)):
        return invalid_score
    mask = _validate_observation_mask(observation_mask, edges.shape[0])
    branch_scores = logsumexp(
        category_loglik + np.log(weights_hat)[:, np.newaxis], axis=0
    )
    pseudologlik = np.sum(branch_scores[mask])
    return float(pseudologlik) if np.isfinite(pseudologlik) else invalid_score


def _discrete_gamma_branch_pseudologlik(
    rates_hat,
    ages_hat,
    edges,
    observed,
    weights_hat,
    branch_cv: float = DEFAULT_BRANCH_CV,
    valid_loglik=None,
    observation_mask=None,
) -> float:
    """Return the multiplicative-Gamma finite-mixture log-likelihood."""
    cv = _validate_branch_cv(branch_cv)
    values = np.asarray(observed, dtype=float)
    edata = np.vstack([values, np.zeros(values.size)]).T
    return _discrete_branch_pseudologlik(
        rates_hat,
        ages_hat,
        edges,
        edata,
        weights_hat,
        valid_loglik,
        observation_mask,
        observation_model="multiplicative_gamma",
        gamma_shape=1.0 / (cv * cv),
    )


@add_subpackage_method(TreeModAPI)
def edges_make_ultrametric_discrete_gamma(
    tree: ToyTree,
    ncategories: int,
    calibrations: Calibrations | None = None,
    branch_cv: float = DEFAULT_BRANCH_CV,
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 100_000,
    max_fun: int = 100_000,
    max_refine: int = 20,
    nstarts: int = 4,
    ncores: int = 1,
    seed: int | None = None,
    _observation_mask: np.ndarray | None = None,
) -> Union[ToyTree, dict[str, Any]]:
    """Fit a scale-free multiplicative-Gamma discrete-rate mixture.

    branch_cv is the fixed within-category coefficient of variation of an
    observed branch around rate times elapsed time. It describes branch-noise
    or estimation dispersion, not biological among-branch rate variation.
    The default is 0.1; estimate it from replicate/bootstrap branch lengths
    when possible, or assess sensitivity at 0.05, 0.1, 0.2, and 0.3.

    The reported score is `log f(x) + log(x)` per branch, which differs from
    the Gamma log-density only by a data-only term and has identical parameter
    estimates. This model is invariant to changes in both input-branch and
    calibration-time units. It is recommended for new finite-category
    analyses. Use UCLN
    instead when rates are better represented by a continuous iid lognormal
    distribution.
    """
    return edges_make_ultrametric_discrete(
        tree=tree,
        ncategories=ncategories,
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
        _observation_model="multiplicative_gamma",
        _branch_cv=branch_cv,
    )


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
