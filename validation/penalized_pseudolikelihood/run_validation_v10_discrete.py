#!/usr/bin/env python

"""Task-parallel V10 validation for discrete chronogram models."""

# ruff: noqa: E402 -- numerical thread limits must precede NumPy/SciPy imports.

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

for _name in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ[_name] = "1"

import numpy as np
import scipy
from scipy.stats import wasserstein_distance

import toytree
from toytree.mod._src.penalized_pseudolikelihood.discrete import (
    _edges_make_ultrametric_discrete_gamma_experimental,
    edges_make_ultrametric_discrete,
)
from validation.penalized_pseudolikelihood.run_validation_v2 import (
    _scale_true_tree,
)

edges_make_ultrametric_discrete_gamma = (
    _edges_make_ultrametric_discrete_gamma_experimental
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v10.json"
OUTPUT = HERE / "v10"
SCALE_FACTOR = 1e6
CACHE_SCHEMA = 2


def _atomic_json(path: Path, value: Any) -> None:
    """Write JSON atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _hash_bytes(*values: bytes) -> str:
    """Return one stable SHA256 digest."""
    digest = hashlib.sha256()
    for value in values:
        digest.update(value)
    return digest.hexdigest()


def _source_hash(config: dict[str, Any]) -> str:
    """Hash all implementation and configuration inputs."""
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    values = [
        (root / name).read_bytes()
        for name in ("discrete.py", "optimization.py", "utils.py")
    ]
    values.append(Path(__file__).read_bytes())
    values.append(json.dumps(config, sort_keys=True).encode())
    return _hash_bytes(*values)


def _environment() -> dict[str, Any]:
    """Return compact software provenance."""
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "toytree": getattr(toytree, "__version__", "unknown"),
    }


def _calibrations(tree: Any, regime: str) -> dict[int, Any]:
    """Return truth-containing calibration constraints."""
    if regime == "root":
        return {-1: 1.0}
    candidates = [
        node
        for node in tree.treenode.traverse("preorder")
        if not node.is_root() and not node.is_leaf()
    ]
    node = max(candidates, key=lambda item: (item.height, item.idx))
    age = float(node.height)
    return {-1: 1.0, int(node.idx): (0.9 * age, 1.1 * age)}


def _fixed_calibrations(tree: Any) -> dict[int, float]:
    """Fix every internal node to its true age."""
    return {int(node.idx): float(node.height) for node in tree[tree.ntips :]}


def _scale_calibrations(values: dict[int, Any], factor: float) -> dict[int, Any]:
    """Express calibrations in another time unit."""
    result = {}
    for key, value in values.items():
        if np.isscalar(value):
            result[int(key)] = float(value) * factor
        else:
            result[int(key)] = tuple(float(item) * factor for item in value)
    return result


def _scale_branches(tree: Any, factor: float) -> Any:
    """Return a tree with all observed branches multiplied by factor."""
    edges = tree.get_edges("idx")
    values = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
    return tree.set_node_data(
        "dist",
        {
            int(child): float(values[index] * factor)
            for index, (child, _) in enumerate(edges)
        },
        inplace=False,
    )


def _true_rates(ncategories: int, model: str) -> np.ndarray:
    """Return separated category rates for one simulation family."""
    if model == "fractional_poisson":
        return (
            np.array([20.0, 50.0]) if ncategories == 2 else np.array([15.0, 30.0, 60.0])
        )
    return np.array([0.5, 1.5]) if ncategories == 2 else np.array([0.5, 1.0, 2.0])


def _simulate(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate one categorical-rate phylogram."""
    rng = np.random.default_rng(int(payload["seed"]))
    tree = _scale_true_tree(int(payload["ntips"]), int(payload["seed"]))
    edges = tree.get_edges("idx")
    ages = tree.get_node_data("height").to_numpy(dtype=float)
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    rates = _true_rates(int(payload["ncategories"]), payload["model"])
    categories = np.arange(tree.nedges) % rates.size
    rng.shuffle(categories)
    branch_rates = rates[categories]
    means = times * branch_rates
    if payload["model"] == "fractional_poisson":
        observed = rng.poisson(means).astype(float)
    else:
        cv = float(payload["true_cv"])
        shape = 1.0 / (cv * cv)
        observed = rng.gamma(shape, means / shape)
    observed_tree = tree.set_node_data(
        "dist",
        {int(child): float(observed[index]) for index, (child, _) in enumerate(edges)},
        inplace=False,
    )
    counts = np.bincount(categories, minlength=rates.size).astype(float)
    return {
        "true_tree": tree,
        "observed_tree": observed_tree,
        "true_ages": ages,
        "true_rates": rates,
        "true_weights": counts / counts.sum(),
    }


def _slim(fit: dict[str, Any]) -> dict[str, Any]:
    """Return JSON-native fitted values."""
    return {
        "converged": bool(fit["converged"]),
        "optimizer_message": str(fit.get("optimizer_message", "")),
        "ages": fit["tree"].get_node_data("height").to_numpy(dtype=float).tolist(),
        "rates": [float(value) for value in fit["rates"]],
        "weights": [float(value) for value in fit["weights"]],
        "pseudologlik": float(fit["pseudologlik"]),
        "objective": float(-fit["pseudologlik"]),
        "nfev": int(fit.get("nfev", -1)),
        "nit": int(fit.get("nit", -1)),
        "gradient_max_abs": fit.get("gradient_max_abs"),
        "projected_gradient_max_abs": fit.get("projected_gradient_max_abs"),
        "optimizer_method": fit.get("optimizer_method"),
        "optimizer_retries": int(fit.get("optimizer_retries", 0)),
        "stability_assessed": fit.get("stability_assessed"),
        "solution_stable": fit.get("solution_stable"),
        "optimum_replicated": fit.get("optimum_replicated"),
        "converged_starts": fit.get("converged_starts"),
        "near_optimal_starts": fit.get("near_optimal_starts"),
        "max_near_optimal_age_difference": fit.get("max_near_optimal_age_difference"),
        "mixture_identified": fit.get("mixture_identified"),
        "effective_ncategories": fit.get("effective_ncategories"),
        "boundary_solution": fit.get("boundary_solution"),
        "boundary_reasons": fit.get("boundary_reasons", []),
        "minimum_weight": fit.get("minimum_weight"),
        "minimum_adjacent_log_rate_gap": fit.get("minimum_adjacent_log_rate_gap"),
        "minimum_normalized_branch_time": fit.get("minimum_normalized_branch_time"),
    }


def _fit(
    tree: Any,
    calibrations: dict[int, Any],
    payload: dict[str, Any],
    nstarts: int,
) -> dict[str, Any]:
    """Fit the matching discrete model."""
    options = payload["config"]["fit"]
    common = {
        "tree": tree,
        "ncategories": int(payload["ncategories"]),
        "calibrations": calibrations,
        "full": True,
        "max_iter": int(options["max_iter"]),
        "max_fun": int(options["max_fun"]),
        "max_refine": int(options["max_refine"]),
        "nstarts": int(nstarts),
        "ncores": 1,
        "seed": int(payload["fit_seed"]),
    }
    if payload["model"] == "fractional_poisson":
        fit = edges_make_ultrametric_discrete(**common)
    else:
        branch_cv = payload.get("fit_cv")
        if branch_cv is None:
            branch_cv = payload.get("true_cv", 0.1)
        fit = edges_make_ultrametric_discrete_gamma(
            branch_cv=float(branch_cv), **common
        )
    return _slim(fit)


def _dataset_id(payload: dict[str, Any]) -> str:
    """Return the stable identifier shared by all fits of one dataset."""
    cv = (
        "none"
        if payload["true_cv"] is None
        else str(payload["true_cv"]).replace(".", "p")
    )
    return (
        f"{payload['model']}-k{payload['ncategories']}-n{payload['ntips']}-"
        f"{payload['calibration']}-cv{cv}-r{payload['replicate']:04d}"
    )


def _cache_path(payload: dict[str, Any]) -> Path:
    """Return a deterministic cache path for one independently runnable fit."""
    name = f"{_dataset_id(payload)}-{payload['role']}.json"
    return OUTPUT / "cache-v10" / payload["mode"] / name


def _fit_roles(payload: dict[str, Any]) -> list[str]:
    """Return all independent fits required for one simulated dataset."""
    roles = ["main", "fixed_age"]
    if payload["replicate"] == 0 or payload["mode"] == "failure-replay":
        roles.append("stress_reference")
    if payload["model"] == "multiplicative_gamma":
        roles.extend(("input_scaled", "time_scaled"))
        if not np.isclose(float(payload["true_cv"]), 0.1):
            roles.append("misspecified_default_cv")
    return roles


def _fit_payloads(datasets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Expand dataset specifications into independently cached fit tasks."""
    tasks = []
    for dataset in datasets:
        for role in _fit_roles(dataset):
            task = dict(dataset)
            task["role"] = role
            task["cache_path"] = str(_cache_path(task))
            tasks.append(task)
    return tasks


def _worker(payload: dict[str, Any]) -> str:
    """Simulate and cache one fit task."""
    path = Path(payload["cache_path"])
    if payload["resume"] and path.exists():
        try:
            cached = json.loads(path.read_text())
            if cached.get("fingerprint") == payload["fingerprint"]:
                return str(path)
        except (OSError, json.JSONDecodeError):
            pass

    simulated = _simulate(payload)
    calibrations = _calibrations(simulated["true_tree"], payload["calibration"])
    role = payload["role"]
    fit_tree = simulated["observed_tree"]
    fit_calibrations = calibrations
    fit_options = payload["config"]["fit"]
    model = payload["model"]
    nstarts = int(fit_options["nstarts_by_model"][model])
    fit_payload = dict(payload)
    if role == "fixed_age":
        fit_calibrations = _fixed_calibrations(simulated["true_tree"])
    elif role == "stress_reference":
        nstarts = int(fit_options["stress_nstarts_by_model"][model])
    elif role == "input_scaled":
        fit_tree = _scale_branches(fit_tree, SCALE_FACTOR)
    elif role == "time_scaled":
        fit_calibrations = _scale_calibrations(calibrations, SCALE_FACTOR)
    elif role == "misspecified_default_cv":
        fit_payload["fit_cv"] = 0.1

    fit = _fit(
        fit_tree,
        fit_calibrations,
        fit_payload,
        nstarts,
    )
    _atomic_json(
        path,
        {
            "schema": CACHE_SCHEMA,
            "fingerprint": payload["fingerprint"],
            "dataset_id": _dataset_id(payload),
            "role": role,
            "fit": fit,
        },
    )
    return str(path)


def _assemble_records(
    datasets: list[dict[str, Any]], paths: list[str]
) -> list[dict[str, Any]]:
    """Assemble independently cached fits into dataset-level records."""
    fitted: dict[str, dict[str, Any]] = {}
    for path in paths:
        task = json.loads(Path(path).read_text())
        fitted.setdefault(task["dataset_id"], {})[task["role"]] = task["fit"]

    records = []
    for payload in datasets:
        simulated = _simulate(payload)
        calibrations = _calibrations(simulated["true_tree"], payload["calibration"])
        fits = fitted[_dataset_id(payload)]
        records.append(
            {
                "schema": CACHE_SCHEMA,
                "fingerprint": payload["fingerprint"],
                "seed": int(payload["seed"]),
                "scenario": payload["scenario"],
                "model": payload["model"],
                "ncategories": int(payload["ncategories"]),
                "ntips": int(payload["ntips"]),
                "calibration": payload["calibration"],
                "true_cv": payload["true_cv"],
                "fit_cv": (
                    payload["true_cv"]
                    if payload["model"] == "multiplicative_gamma"
                    else None
                ),
                "true_ages": simulated["true_ages"].tolist(),
                "true_rates": simulated["true_rates"].tolist(),
                "true_weights": simulated["true_weights"].tolist(),
                "calibrations": {
                    str(key): (
                        float(value)
                        if np.isscalar(value)
                        else [float(item) for item in value]
                    )
                    for key, value in calibrations.items()
                },
                "main": fits["main"],
                "fixed_age": fits["fixed_age"],
                "stress_reference": fits.get("stress_reference"),
                "input_scaled": fits.get("input_scaled"),
                "time_scaled": fits.get("time_scaled"),
                "misspecified_default_cv": fits.get("misspecified_default_cv"),
            }
        )
    return records


def _normalized_internal_ages(
    record: dict[str, Any], fit: dict[str, Any]
) -> np.ndarray:
    """Return fitted internal ages divided by fitted root age."""
    ages = np.asarray(fit["ages"], dtype=float)
    return ages[int(record["ntips"]) :] / ages[-1]


def _age_metrics(record: dict[str, Any], fit: dict[str, Any]) -> tuple[float, float]:
    """Return root-normalized internal age MAE and bias."""
    fitted = _normalized_internal_ages(record, fit)
    truth = np.asarray(record["true_ages"], dtype=float)[int(record["ntips"]) :]
    truth = truth / truth[-1]
    delta = fitted - truth
    return float(np.mean(np.abs(delta))), float(np.mean(delta))


def _mixture_distance(record: dict[str, Any], fit: dict[str, Any]) -> float:
    """Return normalized weighted rate-distribution Wasserstein distance."""
    true_rates = np.asarray(record["true_rates"], dtype=float)
    true_weights = np.asarray(record["true_weights"], dtype=float)
    fit_rates = np.asarray(fit["rates"], dtype=float)
    fit_weights = np.asarray(fit["weights"], dtype=float)
    true_rates = true_rates / np.dot(true_weights, true_rates)
    fit_rates = fit_rates / np.dot(fit_weights, fit_rates)
    return float(
        wasserstein_distance(
            true_rates,
            fit_rates,
            u_weights=true_weights,
            v_weights=fit_weights,
        )
    )


def _calibrations_valid(record: dict[str, Any], fit: dict[str, Any]) -> bool:
    """Return whether fitted ages obey every supplied constraint."""
    ages = np.asarray(fit["ages"], dtype=float)
    for key, value in record["calibrations"].items():
        idx = int(key)
        if idx == -1:
            idx = ages.size - 1
        lower, upper = (value, value) if np.isscalar(value) else value
        if ages[idx] < float(lower) - 1e-8 or ages[idx] > float(upper) + 1e-8:
            return False
    return True


def _wilson_lower(successes: int, total: int) -> float:
    """Return the 95% Wilson lower confidence bound."""
    if total == 0:
        return float("nan")
    z = 1.959963984540054
    p = successes / total
    denominator = 1.0 + z * z / total
    center = p + z * z / (2.0 * total)
    margin = z * np.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total))
    return float((center - margin) / denominator)


def _quantile(values: list[float], q: float) -> float:
    """Return a finite quantile or NaN."""
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    return float(np.quantile(finite, q)) if finite.size else float("nan")


def _relative_rate_error(reference: np.ndarray, candidate: np.ndarray) -> float:
    """Return maximum componentwise relative rate error."""
    denominator = np.maximum(np.abs(reference), 1e-12)
    return float(np.max(np.abs(candidate - reference) / denominator))


def _score(
    records: list[dict[str, Any]],
    config: dict[str, Any],
    mode: str | None = None,
) -> dict[str, Any]:
    """Score all prespecified gates or the targeted failure replay."""
    gates = config["decision_gates"]
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}
    for model in ("fractional_poisson", "multiplicative_gamma"):
        subset = [record for record in records if record["model"] == model]
        converged = sum(record["main"]["converged"] for record in subset)
        lower = _wilson_lower(converged, len(subset))
        details[f"{model}_convergence"] = {
            "successes": converged,
            "total": len(subset),
            "wilson_lower": lower,
        }
        checks[f"{model}_convergence"] = bool(
            lower >= float(gates["convergence_wilson_lower"])
            if mode == "confirmation"
            else converged == len(subset)
        )

    validity = [
        _calibrations_valid(record, record["main"])
        for record in records
        if record["main"]["converged"]
    ]
    validity_fraction = float(np.mean(validity)) if validity else 0.0
    details["calibration_validity"] = validity_fraction
    checks["calibration_validity"] = validity_fraction >= float(
        gates["calibration_validity"]
    )

    boundary_metadata = [
        all(
            key in record["main"]
            for key in (
                "boundary_solution",
                "boundary_reasons",
                "effective_ncategories",
                "mixture_identified",
            )
        )
        for record in records
    ]
    boundary_metadata_fraction = (
        float(np.mean(boundary_metadata)) if boundary_metadata else 0.0
    )
    details["boundary_metadata_fraction"] = boundary_metadata_fraction
    details["boundary_solution_fraction"] = (
        float(np.mean([record["main"]["boundary_solution"] for record in records]))
        if records
        else float("nan")
    )
    checks["boundary_metadata"] = bool(boundary_metadata_fraction == 1.0)

    identified_primary = [
        record["main"]
        for record in records
        if record["main"].get("mixture_identified", False)
    ]
    replication_fraction = (
        float(
            np.mean(
                [fit.get("optimum_replicated", False) for fit in identified_primary]
            )
        )
        if identified_primary
        else 0.0
    )
    details["identified_optimum_replication_fraction"] = replication_fraction

    poisson = [
        record
        for record in records
        if record["model"] == "fractional_poisson" and record["main"]["converged"]
    ]
    poisson_age = [_age_metrics(record, record["main"]) for record in poisson]
    poisson_mae = _quantile([value[0] for value in poisson_age], 0.5)
    poisson_bias = (
        float(np.mean([value[1] for value in poisson_age]))
        if poisson_age
        else float("nan")
    )
    details["poisson_age_mae_median"] = poisson_mae
    details["poisson_age_bias"] = poisson_bias

    poisson_distances = [
        _mixture_distance(record, record["fixed_age"])
        for record in poisson
        if record["fixed_age"]["converged"]
    ]
    poisson_distance = _quantile(poisson_distances, 0.5)
    details["poisson_fixed_age_mixture_wasserstein_median"] = poisson_distance

    gamma_details = {}
    for cv_text, age_limit in gates["gamma_age_mae_median_by_true_cv"].items():
        cv = float(cv_text)
        subset = [
            record
            for record in records
            if record["model"] == "multiplicative_gamma"
            and np.isclose(float(record["true_cv"]), cv)
            and record["main"]["converged"]
        ]
        metrics = [_age_metrics(record, record["main"]) for record in subset]
        mae = _quantile([value[0] for value in metrics], 0.5)
        bias = (
            float(np.mean([value[1] for value in metrics])) if metrics else float("nan")
        )
        distances = [
            _mixture_distance(record, record["fixed_age"])
            for record in subset
            if record["fixed_age"]["converged"]
        ]
        distance = _quantile(distances, 0.5)
        distance_limit = float(
            gates["gamma_fixed_age_mixture_wasserstein_median_by_true_cv"][cv_text]
        )
        gamma_details[cv_text] = {
            "age_mae_median": mae,
            "age_bias": bias,
            "fixed_age_mixture_wasserstein_median": distance,
        }
        checks[f"gamma_cv_{cv_text}_age_mae"] = mae <= float(age_limit)
        checks[f"gamma_cv_{cv_text}_age_bias"] = abs(bias) <= float(
            gates["maximum_absolute_age_bias"]
        )
        checks[f"gamma_cv_{cv_text}_mixture_recovery"] = distance <= distance_limit
    details["gamma_by_true_cv"] = gamma_details

    misspecified = {}
    for cv in (0.05, 0.2):
        subset = [
            record
            for record in records
            if record["model"] == "multiplicative_gamma"
            and np.isclose(float(record["true_cv"]), cv)
            and record["misspecified_default_cv"] is not None
            and record["misspecified_default_cv"]["converged"]
        ]
        metrics = [
            _age_metrics(record, record["misspecified_default_cv"]) for record in subset
        ]
        misspecified[str(cv)] = {
            "datasets": len(subset),
            "age_mae_median": _quantile([value[0] for value in metrics], 0.5),
            "age_bias": (
                float(np.mean([value[1] for value in metrics]))
                if metrics
                else float("nan")
            ),
        }
    details["gamma_default_cv_misspecification"] = misspecified

    age_rmse = []
    objective_improvement = []
    excluded_unidentified = 0
    for record in records:
        stress = record["stress_reference"]
        if stress is None or not record["main"]["converged"] or not stress["converged"]:
            continue
        # A collapsed K-category solution lies on a singular mixture surface.
        # It warns users to refit a smaller K and is not evidence about the
        # optimizer stability of an identified K-category model.
        if not (
            record["main"].get("mixture_identified", False)
            and stress.get("mixture_identified", False)
        ):
            excluded_unidentified += 1
            continue
        ages_main = _normalized_internal_ages(record, record["main"])
        ages_stress = _normalized_internal_ages(record, stress)
        age_rmse.append(float(np.sqrt(np.mean((ages_main - ages_stress) ** 2))))
        objective_improvement.append(
            max(
                0.0,
                (float(record["main"]["objective"]) - float(stress["objective"]))
                / max(1.0, abs(float(stress["objective"]))),
            )
        )
    stress_p90 = _quantile(age_rmse, 0.9)
    stress_max = max(age_rmse, default=float("nan"))
    objective_max = max(objective_improvement, default=float("nan"))
    details["optimizer_stress"] = {
        "age_rmse_p90": stress_p90,
        "age_rmse_maximum": stress_max,
        "relative_objective_improvement_maximum": objective_max,
        "identified_pairs": len(age_rmse),
        "excluded_unidentified_pairs": excluded_unidentified,
    }
    checks["stress_age_rmse_p90"] = stress_p90 <= float(gates["stress_age_rmse_p90"])
    checks["stress_age_rmse_maximum"] = stress_max <= float(
        gates["stress_age_rmse_maximum"]
    )
    checks["stress_objective"] = objective_max <= float(
        gates["stress_relative_objective_improvement_maximum"]
    )

    scale_age = []
    scale_rate = []
    scale_weight = []
    for record in records:
        if record["model"] != "multiplicative_gamma":
            continue
        base = record["main"]
        input_fit = record["input_scaled"]
        time_fit = record["time_scaled"]
        if not all(item["converged"] for item in (base, input_fit, time_fit)):
            continue
        base_ages = _normalized_internal_ages(record, base)
        input_ages = _normalized_internal_ages(record, input_fit)
        time_ages = _normalized_internal_ages(record, time_fit)
        scale_age.extend(
            [
                float(np.max(np.abs(input_ages - base_ages))),
                float(np.max(np.abs(time_ages - base_ages))),
            ]
        )
        base_rates = np.asarray(base["rates"])
        scale_rate.extend(
            [
                _relative_rate_error(
                    base_rates, np.asarray(input_fit["rates"]) / SCALE_FACTOR
                ),
                _relative_rate_error(
                    base_rates, np.asarray(time_fit["rates"]) * SCALE_FACTOR
                ),
            ]
        )
        base_weights = np.asarray(base["weights"])
        scale_weight.extend(
            [
                float(np.max(np.abs(np.asarray(input_fit["weights"]) - base_weights))),
                float(np.max(np.abs(np.asarray(time_fit["weights"]) - base_weights))),
            ]
        )
    age_max = max(scale_age, default=float("nan"))
    rate_max = max(scale_rate, default=float("nan"))
    weight_max = max(scale_weight, default=float("nan"))
    details["gamma_scale"] = {
        "normalized_age_maximum": age_max,
        "relative_rate_maximum": rate_max,
        "weight_maximum": weight_max,
    }
    checks["gamma_scale_age"] = age_max <= float(
        gates["gamma_scale_normalized_age_maximum"]
    )
    checks["gamma_scale_rate"] = rate_max <= float(
        gates["gamma_scale_relative_rate_maximum"]
    )
    checks["gamma_scale_weight"] = weight_max <= float(
        gates["gamma_scale_weight_maximum"]
    )
    if mode in {"failure-replay", "smoke"}:
        all_checks = checks
        checks = {
            "all_primary_converged": all(
                record["main"]["converged"] for record in records
            ),
            "all_stress_converged": all(
                record["stress_reference"] is not None
                and record["stress_reference"]["converged"]
                for record in records
            ),
            "calibration_validity": all_checks["calibration_validity"],
            "boundary_metadata": all_checks["boundary_metadata"],
            "stress_age_rmse_p90": all_checks["stress_age_rmse_p90"],
            "stress_age_rmse_maximum": all_checks["stress_age_rmse_maximum"],
            "stress_objective": all_checks["stress_objective"],
        }
        if mode == "smoke":
            checks.update(
                {
                    "gamma_scale_age": all_checks["gamma_scale_age"],
                    "gamma_scale_rate": all_checks["gamma_scale_rate"],
                    "gamma_scale_weight": all_checks["gamma_scale_weight"],
                }
            )
    return {
        "checks": checks,
        "details": details,
        "gates_passed": bool(checks and all(checks.values())),
    }


def _payloads(
    mode: str,
    config: dict[str, Any],
    fingerprint: str,
    resume: bool,
) -> list[dict[str, Any]]:
    """Enumerate deterministic study cells and seeds."""
    design = config["modes"][mode]
    if mode == "failure-replay":
        payloads = []
        for cell in design["cells"]:
            payload = dict(cell)
            payload.update(
                {
                    "mode": mode,
                    "scenario": "v8-failure-replay",
                    "config": config,
                    "fingerprint": fingerprint,
                    "resume": resume,
                }
            )
            payloads.append(payload)
        return payloads

    base_seed = (
        int(config["confirmation_seed"])
        if mode == "confirmation"
        else int(config["development_seed"])
    )
    rng = np.random.default_rng(base_seed)
    payloads = []
    families = [("fractional_poisson", None, int(design["poisson_replicates"]))]
    families.extend(
        ("multiplicative_gamma", float(cv), int(design["gamma_replicates"]))
        for cv in design["gamma_true_cv"]
    )
    for model, true_cv, replicates in families:
        for ncategories in design["ncategories"]:
            for ntips in design["ntips"]:
                for calibration in design["calibrations"]:
                    for replicate in range(replicates):
                        seed = int(rng.integers(1, 2**31 - 1))
                        payload = {
                            "mode": mode,
                            "scenario": "discrete-recovery",
                            "model": model,
                            "true_cv": true_cv,
                            "ncategories": int(ncategories),
                            "ntips": int(ntips),
                            "calibration": calibration,
                            "replicate": replicate,
                            "seed": seed,
                            "fit_seed": seed + 700_001,
                            "config": config,
                            "fingerprint": fingerprint,
                            "resume": resume,
                        }
                        payloads.append(payload)
    return payloads


def main() -> None:
    """Run simulation, fit-task caching, scoring, and output assembly."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("failure-replay", "smoke", "pilot", "confirmation"),
        default="smoke",
    )
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    config = json.loads(CONFIG_PATH.read_text())
    fingerprint = _source_hash(config)
    datasets = _payloads(args.mode, config, fingerprint, not args.no_resume)
    payloads = _fit_payloads(datasets)
    seeds = [
        {
            key: payload[key]
            for key in (
                "model",
                "true_cv",
                "ncategories",
                "ntips",
                "calibration",
                "replicate",
                "seed",
                "fit_seed",
            )
        }
        for payload in datasets
    ]
    _atomic_json(OUTPUT / f"seeds-v10-{args.mode}.json", seeds)
    _atomic_json(
        OUTPUT / f"environment-v10-{args.mode}.json",
        {
            "environment": _environment(),
            "fingerprint": fingerprint,
            "config": config,
        },
    )

    start = time.monotonic()
    paths = []
    workers = max(1, min(int(args.ncores), len(payloads)))
    if workers == 1:
        for index, payload in enumerate(payloads, 1):
            paths.append(_worker(payload))
            print(
                json.dumps(
                    {
                        "event": "fit_complete",
                        "completed": index,
                        "total": len(payloads),
                        "elapsed_seconds": time.monotonic() - start,
                    }
                ),
                flush=True,
            )
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_worker, payload) for payload in payloads]
            for index, future in enumerate(as_completed(futures), 1):
                paths.append(future.result())
                print(
                    json.dumps(
                        {
                            "event": "fit_complete",
                            "completed": index,
                            "total": len(payloads),
                            "elapsed_seconds": time.monotonic() - start,
                        }
                    ),
                    flush=True,
                )

    records = _assemble_records(datasets, paths)
    summary = _score(records, config, args.mode)
    result = {
        "mode": args.mode,
        "study_version": 10,
        "fingerprint": fingerprint,
        "datasets": records,
        "summary": summary,
        "diagnostic_only": args.mode != "confirmation",
        "all_release_gates_passed": (
            args.mode == "confirmation" and summary["gates_passed"]
        ),
    }
    output = OUTPUT / f"results-v10-{args.mode}.json"
    _atomic_json(output, result)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(records),
                "fit_tasks": len(payloads),
                "workers": workers,
                "output": str(output),
                "gates_passed": summary["gates_passed"],
                "diagnostic_only": result["diagnostic_only"],
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
