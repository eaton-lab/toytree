#!/usr/bin/env python

"""Private optimizer helpers for penalized-pseudolikelihood models."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.special import expit

from toytree.utils import ToytreeError

SOLUTION_OBJECTIVE_ATOL = 1e-4
SOLUTION_OBJECTIVE_RTOL = 1e-6
SOLUTION_MAX_NORMALIZED_AGE_DIFFERENCE = 0.02


def decode_age_params_with_jacobian(
    age_params: np.ndarray,
    ages_base: np.ndarray,
    ages_idxs: np.ndarray,
    ages_bounds: list[tuple[float, float]],
    children_map: dict[int, np.ndarray],
    dist_floor: float = 1e-12,
) -> tuple[np.ndarray, np.ndarray]:
    """Decode valid node ages and their piecewise parameter Jacobian."""
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
                raise ToytreeError(
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


def assess_solution_stability(
    starts: list[dict[str, Any]],
    best: dict[str, Any],
    ntips: int,
    objective_atol: float = SOLUTION_OBJECTIVE_ATOL,
    objective_rtol: float = SOLUTION_OBJECTIVE_RTOL,
    age_tolerance: float = SOLUTION_MAX_NORMALIZED_AGE_DIFFERENCE,
    dist_floor: float = 1e-12,
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
    root_age = max(abs(float(best_ages[-1])), float(dist_floor))
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


def optimizer_stopped_at_limit(message: Any) -> bool:
    """Return whether an optimizer message reports an effort limit."""
    text = str(message).upper()
    markers = (
        "ITERATION",
        "EVALUATION",
        "MAXFUN",
        "MAXIMUM NUMBER",
        "EXCEEDS LIMIT",
    )
    return any(marker in text for marker in markers)
