#!/usr/bin/env python

"""Correlated log-rate penalized branch-length pseudolikelihood."""

from typing import Any, Union

import numpy as np
from loguru import logger
from scipy.optimize import minimize
from scipy.special import expit, gammaln

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
    get_tree_with_correlated_rates,
)

__all__ = ["edges_make_ultrametric_correlated"]

RATE_FLOOR = 1e-12
DIST_FLOOR = 1e-12
INVALID_LOG_LIK_DROP = 1e6
SOLUTION_OBJECTIVE_ATOL = 1e-4
SOLUTION_OBJECTIVE_RTOL = 1e-6
SOLUTION_MAX_NORMALIZED_AGE_DIFFERENCE = 0.02
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


def _fit_correlated_start(payload: dict[str, Any]) -> dict[str, Any]:
    start = int(payload["start"])
    start_kind = str(payload.get("start_kind", f"start_{start}"))
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
    parent_edges = payload["parent_edges"]
    lam = payload["lam"]
    valid_loglik = payload["valid_loglik"]
    observation_mask = payload["observation_mask"]
    max_iter = payload["max_iter"]
    max_fun = payload["max_fun"]
    max_refine = payload["max_refine"]
    retry_multiplier = payload["retry_multiplier"]
    observation_loss = payload["observation_loss"]

    invalid_objective = _invalid_objective(valid_loglik)
    joint_args = (
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
        parent_edges,
        lam,
        valid_loglik,
        observation_mask,
        observation_loss,
    )
    fit = minimize(
        fun=objective_correlated_with_gradient,
        x0=params,
        args=joint_args,
        method="L-BFGS-B",
        jac=True,
        bounds=bounds,
        options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
    )
    total_nfev = int(getattr(fit, "nfev", 0))
    total_nit = int(getattr(fit, "nit", 0))
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
            fun=objective_correlated_with_gradient,
            x0=params_seed,
            args=joint_args,
            method="L-BFGS-B",
            jac=True,
            bounds=bounds,
            options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
        )
        total_nfev += int(getattr(refit, "nfev", 0))
        total_nit += int(getattr(refit, "nit", 0))
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
    refinement_cycles = 0
    for _ in range(max(0, int(max_refine))):
        refinement_cycles += 1
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
                parent_edges,
                lam,
                valid_loglik,
                observation_mask,
                observation_loss,
            )
            ifit = minimize(
                fun=objective_correlated_with_gradient,
                x0=current_params[fslice],
                args=args,
                method="L-BFGS-B",
                jac=True,
                bounds=bounds[fslice],
                options=dict(maxiter=int(max_iter), maxfun=int(max_fun)),
            )
            total_nfev += int(getattr(ifit, "nfev", 0))
            total_nit += int(getattr(ifit, "nit", 0))
            if float(ifit.fun) <= current_loglik:
                current_loglik = float(ifit.fun)
                current_params[fslice] = ifit.x
        if abs(cycle_start - current_loglik) < 1e-9:
            break

    # Block refinement does not establish convergence of the joint objective.
    # Always finish with a joint polish and make its status authoritative.
    pre_polish_objective = current_loglik
    polish = minimize(
        fun=objective_correlated_with_gradient,
        x0=current_params,
        args=joint_args,
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
    total_nfev += int(getattr(polish, "nfev", 0))
    total_nit += int(getattr(polish, "nit", 0))
    polish_objective = float(polish.fun)
    objective_tolerance = 1e-10 * max(1.0, abs(pre_polish_objective))
    polish_is_finite = bool(
        np.isfinite(polish_objective) and np.all(np.isfinite(polish.x))
    )
    polish_did_not_worsen = bool(
        polish_is_finite
        and polish_objective <= pre_polish_objective + objective_tolerance
    )
    if polish_did_not_worsen:
        current_loglik = polish_objective
        current_params = polish.x.copy()

    optimizer_retries = 0
    if (
        not polish.success
        and "ITERATIONS" in str(polish.message).upper()
        and int(retry_multiplier) > 1
    ):
        optimizer_retries = 1
        retry_start_objective = current_loglik
        retry = minimize(
            fun=objective_correlated_with_gradient,
            x0=current_params,
            args=joint_args,
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
            current_loglik = retry_objective
            current_params = retry.x.copy()

    jac = np.asarray(getattr(polish, "jac", np.array([])), dtype=float)
    gradient_max_abs = (
        float(np.max(np.abs(jac))) if jac.size and np.all(np.isfinite(jac)) else None
    )
    converged = bool(polish.success and polish_did_not_worsen)
    message = str(polish.message)
    if polish_is_finite and not polish_did_not_worsen:
        message = (
            "final joint polish worsened the objective beyond tolerance: "
            f"{pre_polish_objective:.12g} -> {polish_objective:.12g}"
        )
    if current_loglik >= invalid_objective - 1e-9:
        converged = False
        message = "invalid objective plateau from infeasible start"
    return {
        "start": start,
        "start_kind": start_kind,
        "objective": float(current_loglik),
        "converged": converged,
        "message": message,
        "nfev": total_nfev,
        "nit": total_nit,
        "refinement_cycles": refinement_cycles,
        "final_joint_converged": bool(polish.success),
        "gradient_max_abs": gradient_max_abs,
        "optimizer_retries": optimizer_retries,
        "params": current_params,
    }


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
    nstarts: int = 1,
    ncores: int = 1,
    seed: int | None = None,
    _observation_mask: np.ndarray | None = None,
    _observation_loss: str = "fractional_poisson",
    _initial_rates: Any = None,
    _initial_ages: Any = None,
    _retry_multiplier: int = 4,
) -> Union[ToyTree, dict[str, Any]]:
    """Return a tree made ultrametric under a correlated relaxed-clock model.

    This model estimates one rate per edge and penalizes abrupt changes
    between adjacent edges by minimizing differences among parent-child
    edge rates on a log scale. Basal edges are connected through a profiled
    root log-rate equal to their mean.
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
    if calibrations is None:
        calibrations = {}
    calibrations = _normalize_calibrations(
        tree,
        calibrations,
        dist_floor=DIST_FLOOR,
    )

    # get init and fixed node ages that make tree ultrametric
    ages_init, _ = _get_init_ages(tree, calibrations)
    continuation_ages = _validate_correlated_warm_start(
        _initial_ages, tree.nnodes, "_initial_ages", positive=False
    )

    # get bounds on params that need to be inferred; are not fixed
    rates_bounds, ages_bounds = _get_params_bounds(tree, calibrations)

    # get edges, dists and log-factorial-dists from rate-x-time edges
    edges = tree.get_edges("idx")
    dists_o = _validate_branch_lengths(tree)
    dists_lf = gammaln(dists_o + 1.0)
    edata = np.vstack([dists_o, dists_lf]).T
    observation_mask = _validate_observation_mask(_observation_mask, tree.nedges)
    if observation_loss == "multiplicative_gamma" and np.any(
        dists_o[observation_mask] <= 0.0
    ):
        raise ValueError(
            "multiplicative_gamma requires strictly positive observed branches."
        )

    # get starting rates as old/new edge dists.
    init_times = ages_init[edges[:, 1]] - ages_init[edges[:, 0]]
    rates_init = np.clip(dists_o / init_times, RATE_FLOOR, None)
    continuation_rates = _validate_correlated_warm_start(
        _initial_rates, tree.nedges, "_initial_rates", positive=True
    )
    # Strong smoothing is poorly conditioned when optimization starts from
    # raw edgewise rates. Center at the fixed-age common-rate estimate and
    # shrink only the initial log-rate deviations as lambda increases.
    observed_total = float(np.sum(dists_o[observation_mask]))
    time_total = float(np.sum(init_times[observation_mask]))
    common_rate = max(observed_total / time_total, RATE_FLOOR)
    log_deviations = np.log(rates_init) - np.mean(np.log(rates_init))
    init_shrinkage = 1.0 / (1.0 + np.sqrt(lam))
    rates_init = np.exp(np.log(common_rate) + init_shrinkage * log_deviations)
    has_continuation = continuation_rates is not None or continuation_ages is not None
    if continuation_ages is None:
        continuation_ages = ages_init
    if continuation_rates is None:
        continuation_times = (
            continuation_ages[edges[:, 1]] - continuation_ages[edges[:, 0]]
        )
        continuation_rates = np.clip(
            dists_o / continuation_times,
            RATE_FLOOR,
            None,
        )

    # map edges to their parent edge index for correlation penalty.
    child_to_eidx = {int(child): idx for idx, (child, _) in enumerate(edges)}
    parent_edges = np.array(
        [child_to_eidx.get(int(parent), -1) for _, parent in edges], dtype=int
    )

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

    # get loglik at a valid starting params to scale invalid-geometry penalty
    valid_loglik = _correlated_branch_pseudologlik(
        rates_init,
        ages_init,
        edges,
        edata,
        parent_edges,
        lam,
        None,
        observation_mask,
        observation_loss,
    )

    params = np.hstack(
        [_pack_log_rates(rates_init, rate_floor=RATE_FLOOR), age_params_init]
    )
    requested_nstarts = max(1, int(nstarts))
    ncores = max(1, int(ncores))
    rng = np.random.default_rng(seed)
    payloads = []
    base_starts = [("independent", params)]
    if has_continuation:
        continuation_age_params = _encode_age_params(
            continuation_ages,
            ages_idxs,
            ages_bounds,
            children_map,
            dist_floor=DIST_FLOOR,
        )
        continuation_params = np.hstack(
            [
                _pack_log_rates(continuation_rates, rate_floor=RATE_FLOOR),
                continuation_age_params,
            ]
        )
        base_starts.append(("continuation", continuation_params))
    nstarts = max(requested_nstarts, len(base_starts))
    rsize = rates_init.size
    asize = ages_idxs.size
    for start in range(nstarts):
        base_kind, base_params = base_starts[start % len(base_starts)]
        sparams = base_params.copy()
        direct_base = start < len(base_starts)
        if not direct_base:
            sparams[:rsize] += rng.normal(0.0, 0.25, size=rsize)
            if asize:
                sparams[rsize : rsize + asize] += rng.normal(0.0, 0.25, size=asize)
        payloads.append(
            dict(
                start_kind=base_kind if direct_base else f"{base_kind}_perturbed",
                start=start,
                params=sparams,
                bounds=bounds,
                rates_init=_unpack_log_rates(base_params[:rsize]),
                age_params_init=base_params[rsize : rsize + asize],
                ages_init=ages_init,
                ages_idxs=ages_idxs,
                ages_bounds=ages_bounds,
                children_map=children_map,
                edges=edges,
                edata=edata,
                parent_edges=parent_edges,
                lam=lam,
                valid_loglik=valid_loglik,
                observation_mask=observation_mask,
                max_iter=max_iter,
                max_fun=max_fun,
                max_refine=max_refine,
                retry_multiplier=retry_multiplier,
                observation_loss=observation_loss,
            )
        )
    starts = _run_multistart(_fit_correlated_start, payloads, ncores=ncores)
    for result in starts:
        if "params" not in result:
            continue
        try:
            result_ages = _decode_age_params(
                result["params"][rsize : rsize + asize],
                ages_init,
                ages_idxs,
                ages_bounds,
                children_map,
                dist_floor=DIST_FLOOR,
            )
            result["ages"] = _finalize_ultrametric_ages(
                tree,
                result_ages,
                calibrations=calibrations,
                dist_floor=DIST_FLOOR,
            )
        except ValueError as exc:
            result["objective"] = float("inf")
            result["converged"] = False
            result["message"] = (
                f"{result.get('message', '')}; invalid finalized ages: {exc}"
            ).lstrip("; ")
    best = _select_best_multistart(starts)
    stability = _assess_correlated_solution_stability(
        starts,
        best,
        ntips=tree.ntips,
    )
    current_params = best["params"]
    if not best["converged"]:
        logger.warning(f"Best multistart fit did not converge: {best['message']}")
    logger.debug(
        "correlated multistart best objective="
        f"{best['objective']}, start={best['start']}, nstarts={nstarts}"
    )

    ages = np.asarray(best["ages"], dtype=float)
    tree = tree.set_node_data("height", ages, inplace=inplace)
    rates = _unpack_log_rates(current_params[:rsize])

    penalized_pseudologlik = _correlated_branch_pseudologlik(
        rates,
        ages,
        edges,
        edata,
        parent_edges,
        lam,
        valid_loglik,
        observation_mask,
        observation_loss,
    )
    pseudologlik = _correlated_branch_pseudologlik(
        rates,
        ages,
        edges,
        edata,
        parent_edges,
        0.0,
        valid_loglik,
        observation_mask,
        observation_loss,
    )
    penalty = _correlated_penalty(rates, parent_edges)
    basal = parent_edges < 0
    profiled_root_rate = float(np.exp(np.log(rates[basal]).mean()))
    time_dists = ages[edges[:, 1]] - ages[edges[:, 0]]
    expected = time_dists * rates

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
                "branch_length_units": "substitutions_per_site",
            }
        ),
        "penalty": penalty,
        "penalty_model": "summed_log_rate_autocorrelation",
        "scale_invariant": True,
        "lam": lam,
        "nparams": len(bounds),
        "profiled_root_rate": profiled_root_rate,
        "rates": list(rates),
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
        "optimizer_retries": int(best.get("optimizer_retries", 0)),
        "observation_loss": observation_loss,
        "nstarts": nstarts,
        "requested_nstarts": requested_nstarts,
        "ncores": max(1, min(ncores, nstarts)),
        "best_start": int(best["start"]),
        "best_start_kind": str(best["start_kind"]),
        **stability,
        "starts": [
            {
                "start": int(i["start"]),
                "objective": float(i["objective"]),
                "start_kind": str(i.get("start_kind", f"start_{i['start']}")),
                "converged": bool(i["converged"]),
                "message": str(i["message"]),
                "nfev": int(i.get("nfev", -1)),
                "nit": int(i.get("nit", -1)),
                "refinement_cycles": int(i.get("refinement_cycles", -1)),
                "final_joint_converged": bool(i.get("final_joint_converged", False)),
                "gradient_max_abs": i.get("gradient_max_abs"),
                "optimizer_retries": int(i.get("optimizer_retries", 0)),
            }
            for i in starts
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
