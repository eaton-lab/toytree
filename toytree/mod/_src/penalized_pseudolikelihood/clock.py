#!/usr/bin/env python

"""Strict-clock branch-length pseudolikelihood fitting."""

from typing import Any, Union

import numpy as np
from loguru import logger
from scipy.optimize import minimize
from scipy.special import gammaln

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_pseudolikelihood.optimization import (
    assess_solution_stability,
    decode_age_params_with_jacobian,
    direct_age_linear_constraint,
    minimize_profiled_ages,
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
    _result_observation_metadata,
    _run_multistart,
    _select_best_multistart,
    _unpack_log_rates,
    _validate_branch_lengths,
    _validate_observation_mask,
    get_tree_with_categorical_rates,
)
from toytree.utils import ToytreeError

__all__ = ["edges_make_ultrametric_clock"]
RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
INVALID_LOG_LIK_DROP = 1e6


def _invalid_objective(valid_loglik: float) -> float:
    """Return the finite objective value used for invalid age vectors."""
    return float(-(valid_loglik - INVALID_LOG_LIK_DROP))


def _profile_clock_rate(
    ages: np.ndarray,
    edges: np.ndarray,
    observed: np.ndarray,
    observation_mask: np.ndarray,
    rate_bounds: tuple[float, float],
) -> float:
    """Return the exact conditional clock-rate estimate for fixed ages."""
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    denominator = float(np.sum(times[observation_mask]))
    if not np.isfinite(denominator) or denominator <= 0.0:
        return float("nan")
    numerator = float(np.sum(observed[observation_mask]))
    raw_rate = numerator / denominator
    return float(np.clip(raw_rate, rate_bounds[0], rate_bounds[1]))


def objective_clock_profiled_with_gradient(
    age_params: np.ndarray,
    ages_base: np.ndarray,
    ages_idxs: np.ndarray,
    ages_bounds: list[tuple[float, float]],
    children_map: dict[int, np.ndarray],
    edges: np.ndarray,
    edata: np.ndarray,
    rate_bounds: tuple[float, float],
    valid_loglik: float,
    observation_mask: np.ndarray,
) -> tuple[float, np.ndarray]:
    """Return the profiled clock objective and analytic age gradient."""
    try:
        ages_hat, age_jacobian = decode_age_params_with_jacobian(
            age_params,
            ages_base,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
    except (ToytreeError, ValueError):
        return _invalid_objective(valid_loglik), np.zeros_like(age_params)

    times = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    rate_hat = _profile_clock_rate(
        ages_hat,
        edges,
        edata[:, 0],
        observation_mask,
        rate_bounds,
    )
    if (
        not np.isfinite(rate_hat)
        or np.any(times <= DIST_FLOOR)
        or np.any(~np.isfinite(times))
    ):
        return _invalid_objective(valid_loglik), np.zeros_like(age_params)

    objective = -_poisson_branch_pseudologlik(
        rate_hat,
        ages_hat,
        edges,
        edata,
        valid_loglik,
        observation_mask,
    )
    if not np.isfinite(objective):
        return _invalid_objective(valid_loglik), np.zeros_like(age_params)

    expected = rate_hat * times
    time_gradient = np.zeros(edges.shape[0], dtype=float)
    time_gradient[observation_mask] = (
        expected[observation_mask] - edata[observation_mask, 0]
    ) / times[observation_mask]
    age_gradient = np.zeros(ages_hat.size, dtype=float)
    np.add.at(age_gradient, edges[:, 1], time_gradient)
    np.add.at(age_gradient, edges[:, 0], -time_gradient)
    return float(objective), age_jacobian.T @ age_gradient


def objective_clock_direct_with_gradient(
    free_ages: np.ndarray,
    ages_base: np.ndarray,
    ages_idxs: np.ndarray,
    edges: np.ndarray,
    edata: np.ndarray,
    rate_bounds: tuple[float, float],
    valid_loglik: float,
    observation_mask: np.ndarray,
) -> tuple[float, np.ndarray]:
    """Return the profiled clock objective in constrained direct ages."""
    ages_hat = np.asarray(ages_base, dtype=float).copy()
    ages_hat[ages_idxs] = np.asarray(free_ages, dtype=float)
    times = ages_hat[edges[:, 1]] - ages_hat[edges[:, 0]]
    rate_hat = _profile_clock_rate(
        ages_hat,
        edges,
        edata[:, 0],
        observation_mask,
        rate_bounds,
    )
    if (
        not np.isfinite(rate_hat)
        or np.any(times < DIST_FLOOR)
        or np.any(~np.isfinite(times))
    ):
        return _invalid_objective(valid_loglik), np.zeros_like(free_ages)

    objective = -_poisson_branch_pseudologlik(
        rate_hat,
        ages_hat,
        edges,
        edata,
        valid_loglik,
        observation_mask,
    )
    if not np.isfinite(objective):
        return _invalid_objective(valid_loglik), np.zeros_like(free_ages)

    expected = rate_hat * times
    time_gradient = np.zeros(edges.shape[0], dtype=float)
    time_gradient[observation_mask] = (
        expected[observation_mask] - edata[observation_mask, 0]
    ) / times[observation_mask]
    age_gradient = np.zeros(ages_hat.size, dtype=float)
    np.add.at(age_gradient, edges[:, 1], time_gradient)
    np.add.at(age_gradient, edges[:, 0], -time_gradient)
    return float(objective), age_gradient[ages_idxs]


def _fit_clock_start(payload: dict[str, Any]) -> dict[str, Any]:
    """Optimize one profiled-rate clock start and return diagnostics."""
    start = int(payload["start"])
    params = payload["params"]
    bounds = payload["bounds"]
    ages_init = payload["ages_init"]
    ages_idxs = payload["ages_idxs"]
    ages_bounds = payload["ages_bounds"]
    children_map = payload["children_map"]
    edges = payload["edges"]
    edata = payload["edata"]
    rate_bounds = payload["rate_bounds"]
    valid_loglik = payload["valid_loglik"]
    observation_mask = payload["observation_mask"]
    max_iter = payload["max_iter"]
    max_fun = payload["max_fun"]
    retry_multiplier = payload["retry_multiplier"]
    direct_age_fallback = payload.get("direct_age_fallback", True)

    args = (
        ages_init,
        ages_idxs,
        ages_bounds,
        children_map,
        edges,
        edata,
        rate_bounds,
        valid_loglik,
        observation_mask,
    )
    if not params.size:
        objective, _ = objective_clock_profiled_with_gradient(params, *args)
        converged = bool(np.isfinite(objective))
        return {
            "start": start,
            "objective": float(objective),
            "converged": converged,
            "message": "all node ages fixed; profiled rate solved analytically",
            "nfev": 1,
            "nit": 0,
            "refinement_cycles": 0,
            "final_joint_converged": converged,
            "gradient_max_abs": 0.0,
            "optimizer_retries": 0,
            "params": params.copy(),
        }

    fit = minimize(
        fun=objective_clock_profiled_with_gradient,
        x0=params,
        args=args,
        method="L-BFGS-B",
        jac=True,
        bounds=bounds,
        options=dict(
            maxiter=int(max_iter),
            maxfun=int(max_fun),
            ftol=1e-12,
            gtol=1e-6,
        ),
    )
    total_nfev = int(getattr(fit, "nfev", 0))
    total_nit = int(getattr(fit, "nit", 0))
    current_objective = float(fit.fun)
    current_params = np.asarray(fit.x, dtype=float).copy()
    authoritative = fit
    optimizer_retries = 0

    if (
        not fit.success
        and optimizer_stopped_at_limit(fit.message)
        and int(retry_multiplier) > 1
    ):
        optimizer_retries = 1
        retry = minimize(
            fun=objective_clock_profiled_with_gradient,
            x0=current_params,
            args=args,
            method="L-BFGS-B",
            jac=True,
            bounds=bounds,
            options=dict(
                maxiter=int(max_iter) * int(retry_multiplier),
                maxfun=int(max_fun) * int(retry_multiplier),
                ftol=1e-12,
                gtol=1e-6,
            ),
        )
        total_nfev += int(getattr(retry, "nfev", 0))
        total_nit += int(getattr(retry, "nit", 0))
        retry_objective = float(retry.fun)
        tolerance = 1e-10 * max(1.0, abs(current_objective))
        if (
            np.isfinite(retry_objective)
            and np.all(np.isfinite(retry.x))
            and retry_objective <= current_objective + tolerance
        ):
            authoritative = retry
            current_objective = retry_objective
            current_params = np.asarray(retry.x, dtype=float).copy()

    direct_age_fallback_used = False
    direct_age_fallback_converged = False
    direct_age_fallback_accepted = False
    if (
        direct_age_fallback
        and not authoritative.success
        and not optimizer_stopped_at_limit(authoritative.message)
    ):
        direct_age_fallback_used = True
        try:
            current_ages = _decode_age_params(
                current_params,
                ages_init,
                ages_idxs,
                ages_bounds,
                children_map,
                dist_floor=DIST_FLOOR,
            )
            constraints = direct_age_linear_constraint(
                ages_init,
                ages_idxs,
                edges,
                dist_floor=DIST_FLOOR,
            )
            direct = minimize_profiled_ages(
                objective_clock_direct_with_gradient,
                current_ages[ages_idxs],
                ages_bounds,
                constraints,
                max_iter=max_iter,
                ftol=1e-12,
                args=(
                    ages_init,
                    ages_idxs,
                    edges,
                    edata,
                    rate_bounds,
                    valid_loglik,
                    observation_mask,
                ),
            )
            total_nfev += int(getattr(direct, "nfev", 0))
            total_nit += int(getattr(direct, "nit", 0))
            direct_age_fallback_converged = bool(direct.success)
            direct_ages = np.asarray(ages_init, dtype=float).copy()
            direct_ages[ages_idxs] = np.asarray(direct.x, dtype=float)
            direct_params = _encode_age_params(
                direct_ages,
                ages_idxs,
                ages_bounds,
                children_map,
                dist_floor=DIST_FLOOR,
            )
            direct_objective, _ = objective_clock_profiled_with_gradient(
                direct_params,
                *args,
            )
            tolerance = 1e-10 * max(1.0, abs(current_objective))
            if (
                np.isfinite(direct_objective)
                and np.all(np.isfinite(direct_params))
                and direct_objective <= current_objective + tolerance
            ):
                direct_age_fallback_accepted = True
                authoritative = direct
                current_objective = float(direct_objective)
                current_params = direct_params
        except (ToytreeError, ValueError):
            direct_age_fallback_converged = False

    jac = np.asarray(getattr(authoritative, "jac", np.array([])), dtype=float)
    gradient_max_abs = (
        None
        if direct_age_fallback_accepted
        else (
            float(np.max(np.abs(jac)))
            if jac.size and np.all(np.isfinite(jac))
            else None
        )
    )
    converged = bool(authoritative.success and np.isfinite(current_objective))
    message = str(authoritative.message)
    if direct_age_fallback_accepted:
        message = f"direct-age constrained fallback: {message}"
    if current_objective >= _invalid_objective(valid_loglik) - 1e-9:
        converged = False
        message = "invalid objective plateau from infeasible start"

    return {
        "start": start,
        "objective": float(current_objective),
        "converged": converged,
        "message": message,
        "nfev": total_nfev,
        "nit": total_nit,
        "refinement_cycles": 0,
        "final_joint_converged": bool(authoritative.success),
        "gradient_max_abs": gradient_max_abs,
        "optimizer_retries": optimizer_retries,
        "direct_age_fallback_used": direct_age_fallback_used,
        "direct_age_fallback_converged": direct_age_fallback_converged,
        "direct_age_fallback_accepted": direct_age_fallback_accepted,
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
    _retry_multiplier: int = 4,
    _direct_age_fallback: bool = True,
) -> Union[ToyTree, dict[str, Any]]:
    """Return a tree made ultrametric under a molecular clock.

    Edges are scaled while assuming one shared rate. Input edge lengths may
    use any finite, non-negative additive unit for which branch length equals
    elapsed time multiplied by rate; expected substitutions per site are
    common but are not required. Calibrations define the returned time unit,
    and the fitted rate is in input-edge units per calibration unit. Without
    calibrations, the root age is fixed to 1, returned edge lengths are
    relative time, and the rate is in input-edge units per relative root-age
    unit.

    Parameters
    ----------
    tree:
        A ToyTree with finite, non-negative edge lengths in a consistent
        additive unit. The values must not be support values or unrelated
        edge weights.
    calibrations: dict[int, (float, float)]
        A dict mapping node selectors (e.g., idx labels) to calibrated ages
        as a single value or a tuple of (min, max) age. Their unit becomes
        the output-tree time unit. If empty, the root is fixed to age 1 and
        the output is a relative-time chronogram.
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
        Retained for wrapper compatibility; unused because the clock rate
        is profiled analytically rather than optimized in alternating blocks.
    nstarts: int
        Number of random starting points; best objective is retained.
    ncores: int
        Number of worker processes for multistart; used if nstarts > 1.
    seed: int or None
        Random seed for multistart reproducibility.

    Returns
    -------
    ToyTree
        The default return is an ultrametric ToyTree whose edge lengths use
        the calibration time unit, or relative time with root age 1 when no
        calibration is supplied. If inplace=True this overwrites the input
        tree.
    dict
        With full=True, a dict containing the scaled tree, working likelihood,
        and rate. The rate is expressed in input-edge units per calibration
        unit, or per relative root-age unit for an uncalibrated fit.
    """
    if isinstance(_retry_multiplier, bool) or not isinstance(
        _retry_multiplier, (int, np.integer)
    ):
        raise ValueError("_retry_multiplier must be a positive integer.")
    retry_multiplier = int(_retry_multiplier)
    if retry_multiplier < 1:
        raise ValueError("_retry_multiplier must be a positive integer.")
    if not isinstance(_direct_age_fallback, (bool, np.bool_)):
        raise ValueError("_direct_age_fallback must be a boolean.")
    direct_age_fallback = bool(_direct_age_fallback)
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
    bounds = [(None, None)] * age_params_init.size
    params = age_params_init.copy()

    # Profile the one clock rate exactly for every age vector.
    rate_init = _profile_clock_rate(
        ages_init, edges, dists_o, observation_mask, rate_bounds
    )
    valid_loglik = _poisson_branch_pseudologlik(
        rate_init, ages_init, edges, edata, None, observation_mask
    )

    requested_nstarts = max(1, int(nstarts))
    nstarts = requested_nstarts if age_params_init.size else 1
    ncores = max(1, int(ncores))
    rng = np.random.default_rng(seed)
    payloads = []
    for start in range(nstarts):
        sparams = params.copy()
        if start:
            sparams += rng.normal(0.0, 0.25, size=sparams.size)
        payloads.append(
            dict(
                start=start,
                params=sparams,
                bounds=bounds,
                ages_init=ages_init,
                ages_idxs=ages_idxs,
                ages_bounds=ages_bounds,
                children_map=children_map,
                edges=edges,
                edata=edata,
                rate_bounds=rate_bounds,
                valid_loglik=valid_loglik,
                observation_mask=observation_mask,
                max_iter=max_iter,
                max_fun=max_fun,
                retry_multiplier=retry_multiplier,
                direct_age_fallback=direct_age_fallback,
            )
        )
    starts = _run_multistart(_fit_clock_start, payloads, ncores=ncores)
    for result in starts:
        if "params" not in result:
            continue
        try:
            result_ages = _decode_age_params(
                result["params"],
                ages_init,
                ages_idxs,
                ages_bounds,
                children_map,
                dist_floor=DIST_FLOOR,
            )
            result_ages = _finalize_ultrametric_ages(
                tree,
                result_ages,
                calibrations=calibrations,
                dist_floor=DIST_FLOOR,
            )
            result_rate = _profile_clock_rate(
                result_ages, edges, dists_o, observation_mask, rate_bounds
            )
            result_loglik = _poisson_branch_pseudologlik(
                result_rate,
                result_ages,
                edges,
                edata,
                valid_loglik,
                observation_mask,
            )
            result["ages"] = result_ages
            result["rate"] = result_rate
            result["objective"] = float(-result_loglik)
        except (ToytreeError, ValueError) as exc:
            result["objective"] = float("inf")
            result["converged"] = False
            result["message"] = f"invalid finalized ages: {exc}"
    best = _select_best_multistart(starts)
    stability = assess_solution_stability(starts, best, ntips=tree.ntips)
    if not best["converged"]:
        logger.warning(f"Best multistart fit did not converge: {best['message']}")
    logger.debug(
        "clock multistart best objective="
        f"{best['objective']}, start={best['start']}, nstarts={nstarts}"
    )

    ages = np.asarray(best["ages"], dtype=float)
    tree = tree.set_node_data("height", ages, inplace=inplace)
    rate = float(best["rate"])

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
        "nparams": 1 + len(bounds),
        "optimizer_strategy": "profiled_clock_rate",
        "rate_profiled": True,
        "max_refine_used": 0,
        "rate": rate,
        "expected_branch_lengths": expected.tolist(),
        "observed_branch_lengths": dists_o.tolist(),
        "tree": tree,
        "converged": bool(best["converged"]),
        "optimizer_message": str(best["message"]),
        "nfev": int(best.get("nfev", -1)),
        "nit": int(best.get("nit", -1)),
        "refinement_cycles": 0,
        "final_joint_converged": bool(best.get("final_joint_converged", False)),
        "gradient_max_abs": best.get("gradient_max_abs"),
        "optimizer_retries": int(best.get("optimizer_retries", 0)),
        "direct_age_fallback_used": bool(best.get("direct_age_fallback_used", False)),
        "direct_age_fallback_converged": bool(
            best.get("direct_age_fallback_converged", False)
        ),
        "direct_age_fallback_accepted": bool(
            best.get("direct_age_fallback_accepted", False)
        ),
        "nstarts": nstarts,
        "requested_nstarts": requested_nstarts,
        "ncores": max(1, min(ncores, nstarts)),
        "best_start": int(best["start"]),
        **stability,
        "starts": [
            {
                "start": int(i["start"]),
                "objective": float(i["objective"]),
                "converged": bool(i["converged"]),
                "message": str(i["message"]),
                "nfev": int(i.get("nfev", -1)),
                "nit": int(i.get("nit", -1)),
                "refinement_cycles": 0,
                "final_joint_converged": bool(i.get("final_joint_converged", False)),
                "gradient_max_abs": i.get("gradient_max_abs"),
                "optimizer_retries": int(i.get("optimizer_retries", 0)),
                "direct_age_fallback_used": bool(
                    i.get("direct_age_fallback_used", False)
                ),
                "direct_age_fallback_converged": bool(
                    i.get("direct_age_fallback_converged", False)
                ),
                "direct_age_fallback_accepted": bool(
                    i.get("direct_age_fallback_accepted", False)
                ),
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
