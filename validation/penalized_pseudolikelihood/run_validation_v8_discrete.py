#!/usr/bin/env python

"""Resumable V8 validation for discrete chronogram models."""

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
    edges_make_ultrametric_discrete,
    edges_make_ultrametric_discrete_gamma,
)
from validation.penalized_pseudolikelihood.run_validation_v2 import (
    _scale_true_tree,
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v8.json"
OUTPUT = HERE / "v8"
SCALE_FACTOR = 1e6
CACHE_SCHEMA = 1


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
        "optimizer_retries": int(fit.get("optimizer_retries", 0)),
        "solution_stable": fit.get("solution_stable"),
        "max_near_optimal_age_difference": fit.get("max_near_optimal_age_difference"),
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
        fit = edges_make_ultrametric_discrete_gamma(branch_cv=0.1, **common)
    return _slim(fit)


def _cache_path(payload: dict[str, Any]) -> Path:
    """Return a deterministic cache path."""
    cv = (
        "none"
        if payload["true_cv"] is None
        else str(payload["true_cv"]).replace(".", "p")
    )
    name = (
        f"{payload['model']}-k{payload['ncategories']}-n{payload['ntips']}-"
        f"{payload['calibration']}-cv{cv}-r{payload['replicate']:04d}.json"
    )
    return OUTPUT / "cache-v8" / payload["mode"] / name


def _worker(payload: dict[str, Any]) -> str:
    """Simulate, fit, and cache one dataset."""
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
    fixed = _fixed_calibrations(simulated["true_tree"])
    nstarts = int(payload["config"]["fit"]["nstarts"])
    main = _fit(simulated["observed_tree"], calibrations, payload, nstarts)
    fixed_fit = _fit(simulated["observed_tree"], fixed, payload, nstarts)
    stress = None
    if payload["replicate"] == 0:
        stress = _fit(
            simulated["observed_tree"],
            calibrations,
            payload,
            int(payload["config"]["fit"]["stress_nstarts"]),
        )

    input_scaled = None
    time_scaled = None
    if payload["model"] == "multiplicative_gamma":
        input_scaled = _fit(
            _scale_branches(simulated["observed_tree"], SCALE_FACTOR),
            calibrations,
            payload,
            nstarts,
        )
        time_scaled = _fit(
            simulated["observed_tree"],
            _scale_calibrations(calibrations, SCALE_FACTOR),
            payload,
            nstarts,
        )

    record = {
        "schema": CACHE_SCHEMA,
        "fingerprint": payload["fingerprint"],
        "seed": int(payload["seed"]),
        "scenario": payload["scenario"],
        "model": payload["model"],
        "ncategories": int(payload["ncategories"]),
        "ntips": int(payload["ntips"]),
        "calibration": payload["calibration"],
        "true_cv": payload["true_cv"],
        "true_ages": simulated["true_ages"].tolist(),
        "true_rates": simulated["true_rates"].tolist(),
        "true_weights": simulated["true_weights"].tolist(),
        "calibrations": {
            str(key): (
                float(value) if np.isscalar(value) else [float(item) for item in value]
            )
            for key, value in calibrations.items()
        },
        "main": main,
        "fixed_age": fixed_fit,
        "stress_eight": stress,
        "input_scaled": input_scaled,
        "time_scaled": time_scaled,
    }
    _atomic_json(path, record)
    return str(path)


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


def _score(records: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    """Score all prespecified gates."""
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
    checks["poisson_age_mae"] = poisson_mae <= float(gates["poisson_age_mae_median"])
    checks["poisson_age_bias"] = abs(poisson_bias) <= float(
        gates["maximum_absolute_age_bias"]
    )

    poisson_distances = [
        _mixture_distance(record, record["fixed_age"])
        for record in poisson
        if record["fixed_age"]["converged"]
    ]
    poisson_distance = _quantile(poisson_distances, 0.5)
    details["poisson_fixed_age_mixture_wasserstein_median"] = poisson_distance
    checks["poisson_mixture_recovery"] = poisson_distance <= float(
        gates["poisson_fixed_age_mixture_wasserstein_median"]
    )

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

    age_rmse = []
    objective_improvement = []
    for record in records:
        stress = record["stress_eight"]
        if stress is None or not record["main"]["converged"] or not stress["converged"]:
            continue
        ages4 = _normalized_internal_ages(record, record["main"])
        ages8 = _normalized_internal_ages(record, stress)
        age_rmse.append(float(np.sqrt(np.mean((ages4 - ages8) ** 2))))
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
                        payload["cache_path"] = str(_cache_path(payload))
                        payloads.append(payload)
    return payloads


def main() -> None:
    """Run simulation, caching, scoring, and output assembly."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=("smoke", "pilot", "confirmation"), default="smoke"
    )
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    config = json.loads(CONFIG_PATH.read_text())
    fingerprint = _source_hash(config)
    payloads = _payloads(args.mode, config, fingerprint, not args.no_resume)
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
        for payload in payloads
    ]
    _atomic_json(OUTPUT / f"seeds-v8-{args.mode}.json", seeds)
    _atomic_json(
        OUTPUT / f"environment-v8-{args.mode}.json",
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
                        "event": "dataset_complete",
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
                            "event": "dataset_complete",
                            "completed": index,
                            "total": len(payloads),
                            "elapsed_seconds": time.monotonic() - start,
                        }
                    ),
                    flush=True,
                )

    records = [json.loads(Path(path).read_text()) for path in sorted(paths)]
    summary = _score(records, config)
    result = {
        "mode": args.mode,
        "study_version": 8,
        "fingerprint": fingerprint,
        "datasets": records,
        "summary": summary,
        "diagnostic_only": args.mode != "confirmation",
        "all_release_gates_passed": (
            args.mode == "confirmation" and summary["gates_passed"]
        ),
    }
    output = OUTPUT / f"results-v8-{args.mode}.json"
    _atomic_json(output, result)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(records),
                "output": str(output),
                "gates_passed": summary["gates_passed"],
                "diagnostic_only": result["diagnostic_only"],
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
