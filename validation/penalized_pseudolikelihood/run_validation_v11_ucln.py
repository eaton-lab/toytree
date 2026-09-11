#!/usr/bin/env python

"""Task-parallel V11 validation of the fixed-lambda UCLN estimator."""

# ruff: noqa: E402 -- numerical thread limits must precede NumPy/SciPy imports.

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from collections import defaultdict
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
from scipy.stats import spearmanr

import toytree
from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    _edges_make_ultrametric_ucln as edges_make_ultrametric_uncorrelated_lognormal,
)
from validation.penalized_pseudolikelihood.simulation_helpers import (
    _scale_true_tree,
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v11.json"
DEFAULT_OUTPUT = HERE / "v11"
CACHE_SCHEMA = 1
TIME_UNIT_FACTOR = 1e6
EPS = 1e-12


def _atomic_json(path: Path, value: Any) -> None:
    """Write JSON atomically so interrupted tasks leave no valid cache."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _json_hash(value: Any) -> str:
    """Return a stable hash of JSON-compatible content."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _source_hash(config: dict[str, Any]) -> str:
    """Hash every implementation and design input affecting fitted values."""
    digest = hashlib.sha256()
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    for name in (
        "uncorrelated_lognormal.py",
        "clock.py",
        "optimization.py",
        "utils.py",
    ):
        source = root / name
        digest.update(source.name.encode())
        digest.update(source.read_bytes())
    digest.update(Path(__file__).read_bytes())
    digest.update(json.dumps(config, sort_keys=True).encode())
    return digest.hexdigest()


def _environment() -> dict[str, Any]:
    """Return compact software and platform provenance."""
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "toytree": getattr(toytree, "__version__", "unknown"),
    }


def _calibrations(tree: Any, regime: str) -> dict[int, Any]:
    """Return truth-containing root or root-plus-internal calibrations."""
    if regime == "root":
        return {-1: 1.0}
    if regime != "root_and_internal_interval":
        raise ValueError(f"unknown calibration regime: {regime}")
    candidates = [
        node
        for node in tree.treenode.traverse("preorder")
        if not node.is_root() and not node.is_leaf()
    ]
    node = max(candidates, key=lambda item: (item.height, item.idx))
    age = float(node.height)
    return {-1: 1.0, int(node.idx): (0.9 * age, 1.1 * age)}


def _fixed_calibrations(tree: Any) -> dict[int, float]:
    """Fix every internal age to its simulated value."""
    return {int(node.idx): float(node.height) for node in tree[tree.ntips :]}


def _scale_calibrations(values: dict[int, Any], factor: float) -> dict[int, Any]:
    """Express calibration ages in another time unit."""
    result = {}
    for key, value in values.items():
        if np.isscalar(value):
            result[int(key)] = float(value) * factor
        else:
            result[int(key)] = tuple(float(item) * factor for item in value)
    return result


def _calibration_records(values: dict[int, Any]) -> list[dict[str, float]]:
    """Return JSON-native calibration bounds."""
    records = []
    for key, value in values.items():
        lower, upper = (value, value) if np.isscalar(value) else value
        records.append({"idx": int(key), "lower": float(lower), "upper": float(upper)})
    return records


def _simulate(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate one iid-lognormal-rate chronogram and observed phylogram."""
    seed = int(payload["seed"])
    rng = np.random.default_rng(seed)
    true_tree = _scale_true_tree(int(payload["ntips"]), seed)
    edges = np.asarray(true_tree.get_edges("idx"), dtype=int)
    ages = true_tree.get_node_data("height").to_numpy(dtype=float)
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    sigma_log = float(payload["sigma_log"])
    log_rates = rng.normal(0.0, sigma_log, size=tree_nedges(true_tree))
    log_rates -= float(np.mean(log_rates))
    rates = float(payload["config"]["simulation"]["baseline_rate"]) * np.exp(log_rates)
    expected = times * rates
    observation_model = payload["observation_model"]
    if observation_model == "expected_branch":
        observed = expected.copy()
    elif observation_model == "fractional_poisson":
        observed = rng.poisson(expected).astype(float)
    elif observation_model == "continuous_gamma":
        shape = float(payload["config"]["noise"]["gamma_shape"])
        observed = expected * rng.gamma(shape, 1.0 / shape, size=expected.size)
    else:
        raise ValueError(f"unknown observation model: {observation_model}")
    observed_tree = true_tree.set_node_data(
        "dist",
        {int(child): float(observed[index]) for index, (child, _) in enumerate(edges)},
        inplace=False,
    )
    return {
        "true_tree": true_tree,
        "observed_tree": observed_tree,
        "true_ages": ages,
        "true_rates": rates,
        "expected": expected,
        "observed": observed,
    }


def tree_nedges(tree: Any) -> int:
    """Return edge count without depending on a private simulator detail."""
    return int(tree.nedges)


def _slim(fit: dict[str, Any]) -> dict[str, Any]:
    """Return JSON-native fitted values needed by cache-only scoring."""
    return {
        "converged": bool(fit["converged"]),
        "optimizer_message": str(fit.get("optimizer_message", "")),
        "ages": fit["tree"].get_node_data("height").to_numpy(dtype=float).tolist(),
        "rates": [float(value) for value in fit["rates"]],
        "penalized_pseudologlik": float(fit["penalized_pseudologlik"]),
        "objective": float(-fit["penalized_pseudologlik"]),
        "penalty": float(fit["penalty"]),
        "nfev": int(fit.get("nfev", -1)),
        "nit": int(fit.get("nit", -1)),
        "gradient_max_abs": fit.get("gradient_max_abs"),
        "optimizer_retries": int(fit.get("optimizer_retries", 0)),
        "requested_nstarts": int(fit.get("requested_nstarts", fit["nstarts"])),
        "effective_nstarts": int(fit["nstarts"]),
        "converged_starts": int(fit.get("converged_starts", 0)),
        "near_optimal_starts": int(fit.get("near_optimal_starts", 0)),
        "stability_assessed": bool(fit.get("stability_assessed", False)),
        "solution_stable": fit.get("solution_stable"),
        "max_near_optimal_age_difference": fit.get("max_near_optimal_age_difference"),
    }


def _fit(
    tree: Any,
    calibrations: dict[int, Any],
    payload: dict[str, Any],
    nstarts: int,
) -> dict[str, Any]:
    """Fit and slim one fixed-lambda UCLN result."""
    options = payload["config"]["fit"]
    sigma_log = float(payload["sigma_log"])
    lam = 1.0 / (2.0 * sigma_log * sigma_log)
    fit = edges_make_ultrametric_uncorrelated_lognormal(
        tree,
        lam=lam,
        calibrations=calibrations,
        full=True,
        inplace=False,
        max_iter=int(options["max_iter"]),
        max_fun=int(options["max_fun"]),
        max_refine=int(options["max_refine"]),
        nstarts=int(nstarts),
        ncores=1,
        seed=int(payload["fit_seed"]),
        _retry_multiplier=int(options["retry_multiplier"]),
    )
    return _slim(fit)


def _dataset_id(payload: dict[str, Any]) -> str:
    """Return the stable identifier shared by all tasks for one dataset."""
    sigma = str(payload["sigma_log"]).replace(".", "p")
    return (
        f"ucln-n{payload['ntips']}-{payload['calibration']}-"
        f"{payload['observation_model']}-sigma{sigma}-r{payload['replicate']:04d}"
    )


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    """Return the deterministic path for one independently runnable fit."""
    return (
        output_dir
        / "cache-v11"
        / payload["mode"]
        / f"{_dataset_id(payload)}-{payload['role']}.json"
    )


def _roles(payload: dict[str, Any]) -> list[str]:
    """Return independent fit roles for one simulated dataset."""
    roles = ["default", "stress", "fixed_age"]
    if int(payload["replicate"]) == 0:
        roles.append("time_scaled")
    return roles


def _task_payloads(
    datasets: list[dict[str, Any]], output_dir: Path
) -> list[dict[str, Any]]:
    """Expand dataset specifications into independently cached fit tasks."""
    tasks = []
    for dataset in datasets:
        for role in _roles(dataset):
            task = dict(dataset)
            task["role"] = role
            fingerprint_value = {
                key: value
                for key, value in task.items()
                if key not in {"resume", "source_hash"}
            } | {
                "role": role,
                "source_hash": task["source_hash"],
                "cache_schema": CACHE_SCHEMA,
            }
            task["fingerprint"] = _json_hash(fingerprint_value)
            task["cache_path"] = str(_cache_path(output_dir, task))
            tasks.append(task)
    return tasks


def _worker(payload: dict[str, Any]) -> str:
    """Simulate and atomically cache one fit task."""
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
    nstarts = int(payload["config"]["fit"]["default_nstarts"])
    if role == "stress":
        nstarts = int(payload["config"]["fit"]["stress_nstarts"])
    fit_calibrations = calibrations
    if role == "fixed_age":
        fit_calibrations = _fixed_calibrations(simulated["true_tree"])
    elif role == "time_scaled":
        fit_calibrations = _scale_calibrations(calibrations, TIME_UNIT_FACTOR)
    fit = _fit(simulated["observed_tree"], fit_calibrations, payload, nstarts)
    _atomic_json(
        path,
        {
            "cache_schema": CACHE_SCHEMA,
            "fingerprint": payload["fingerprint"],
            "dataset_id": _dataset_id(payload),
            "role": role,
            "fit": fit,
        },
    )
    return str(path)


def _read_task_caches(tasks: list[dict[str, Any]]) -> list[Path]:
    """Read no fits, but require all task caches and fingerprints to match."""
    paths = []
    for task in tasks:
        path = Path(task["cache_path"])
        if not path.exists():
            raise FileNotFoundError(f"missing cache: {path}")
        cached = json.loads(path.read_text())
        if cached.get("fingerprint") != task["fingerprint"]:
            raise RuntimeError(f"stale cache fingerprint: {path}")
        paths.append(path)
    return paths


def _assemble(
    datasets: list[dict[str, Any]], paths: list[Path]
) -> list[dict[str, Any]]:
    """Assemble task caches into dataset records without fitting."""
    fitted: dict[str, dict[str, Any]] = defaultdict(dict)
    for path in paths:
        task = json.loads(path.read_text())
        fitted[task["dataset_id"]][task["role"]] = task["fit"]
    records = []
    for payload in datasets:
        simulated = _simulate(payload)
        calibrations = _calibrations(simulated["true_tree"], payload["calibration"])
        records.append(
            {
                "dataset_id": _dataset_id(payload),
                "scenario": payload["scenario"],
                "ntips": int(payload["ntips"]),
                "calibration": payload["calibration"],
                "observation_model": payload["observation_model"],
                "sigma_log": float(payload["sigma_log"]),
                "lam": float(1.0 / (2.0 * float(payload["sigma_log"]) ** 2)),
                "replicate": int(payload["replicate"]),
                "seed": int(payload["seed"]),
                "true_ages": simulated["true_ages"].tolist(),
                "true_rates": simulated["true_rates"].tolist(),
                "expected_branch_lengths": simulated["expected"].tolist(),
                "observed_branch_lengths": simulated["observed"].tolist(),
                "calibrations": _calibration_records(calibrations),
                "fits": fitted[_dataset_id(payload)],
            }
        )
    return records


def _calibrations_valid(
    ages: np.ndarray,
    calibrations: list[dict[str, float]],
    factor: float = 1.0,
) -> bool:
    """Return whether a fitted chronogram satisfies every calibration."""
    for item in calibrations:
        idx = int(item["idx"])
        idx = idx if idx >= 0 else ages.size + idx
        lower = float(item["lower"]) * factor
        upper = float(item["upper"]) * factor
        tolerance = 1e-8 * max(1.0, abs(lower), abs(upper))
        if ages[idx] < lower - tolerance or ages[idx] > upper + tolerance:
            return False
    return True


def _center_log_rates(values: np.ndarray) -> np.ndarray:
    """Remove the unidentifiable common log-rate scale."""
    logs = np.log(np.clip(np.asarray(values, dtype=float), EPS, None))
    return logs - float(np.mean(logs))


def _score_record(record: dict[str, Any]) -> dict[str, Any]:
    """Score one assembled dataset without calling any fitter."""
    fits = record["fits"]
    default = fits["default"]
    stress = fits["stress"]
    fixed = fits["fixed_age"]
    ntips = int(record["ntips"])
    truth = np.asarray(record["true_ages"], dtype=float)
    root_age = max(float(truth[-1]), EPS)
    true_internal = truth[ntips:] / root_age
    default_ages = np.asarray(default["ages"], dtype=float)
    stress_ages = np.asarray(stress["ages"], dtype=float)
    fitted_internal = default_ages[ntips:] / max(float(default_ages[-1]), EPS)
    age_delta = fitted_internal - true_internal
    objective_scale = max(1.0, abs(float(stress["objective"])))
    objective_gap = max(
        0.0,
        (float(default["objective"]) - float(stress["objective"])) / objective_scale,
    )
    default_stress_age_difference = float(
        np.max(np.abs(default_ages[ntips:] - stress_ages[ntips:])) / root_age
    )
    calibration_valid = all(
        _calibrations_valid(np.asarray(fit["ages"]), record["calibrations"])
        for fit in (default, stress)
    )

    true_rates = np.asarray(record["true_rates"], dtype=float)
    fixed_rates = np.asarray(fixed["rates"], dtype=float)
    correlation = float(spearmanr(true_rates, fixed_rates).statistic)
    centered_error = _center_log_rates(fixed_rates) - _center_log_rates(true_rates)

    scale_score = None
    if "time_scaled" in fits:
        scaled = fits["time_scaled"]
        scaled_ages = np.asarray(scaled["ages"], dtype=float)
        scaled_rates = np.asarray(scaled["rates"], dtype=float)
        base_rates = np.asarray(default["rates"], dtype=float)
        scale_score = {
            "converged": bool(scaled["converged"]),
            "calibration_valid": _calibrations_valid(
                scaled_ages, record["calibrations"], factor=TIME_UNIT_FACTOR
            ),
            "maximum_normalized_age_difference": float(
                np.max(np.abs(scaled_ages / TIME_UNIT_FACTOR - default_ages)) / root_age
            ),
            "maximum_rate_relative_error": float(
                np.max(
                    np.abs(scaled_rates * TIME_UNIT_FACTOR - base_rates)
                    / np.maximum(np.abs(base_rates), EPS)
                )
            ),
            "penalty_relative_error": float(
                abs(float(scaled["penalty"]) - float(default["penalty"]))
                / max(abs(float(default["penalty"])), 1.0)
            ),
        }

    return {
        key: record[key]
        for key in (
            "dataset_id",
            "scenario",
            "ntips",
            "calibration",
            "observation_model",
            "sigma_log",
            "lam",
            "replicate",
            "seed",
        )
    } | {
        "default_converged": bool(default["converged"]),
        "stress_converged": bool(stress["converged"]),
        "fixed_age_converged": bool(fixed["converged"]),
        "stress_solution_stable": stress["solution_stable"] is True,
        "calibration_valid": calibration_valid,
        "relative_objective_gap": objective_gap,
        "default_stress_maximum_age_difference": default_stress_age_difference,
        "age_mae": float(np.mean(np.abs(age_delta))),
        "age_bias": float(np.mean(age_delta)),
        "fixed_age_rate_spearman": correlation,
        "fixed_age_centered_log_rate_rmse": float(
            np.sqrt(np.mean(centered_error * centered_error))
        ),
        "optimizer_retries": int(default["optimizer_retries"])
        + int(stress["optimizer_retries"])
        + int(fixed["optimizer_retries"]),
        "time_unit_scale": scale_score,
    }


def _finite_median(values: list[float]) -> float:
    """Return the median of finite values or positive infinity."""
    array = np.asarray(values, dtype=float)
    array = array[np.isfinite(array)]
    return float(np.median(array)) if array.size else float("inf")


def _summarize(rows: list[dict[str, Any]], gates: dict[str, float]) -> dict[str, Any]:
    """Aggregate prespecified optimizer, recovery, and invariance gates."""
    fit_flags = [
        value
        for row in rows
        for value in (
            row["default_converged"],
            row["stress_converged"],
            row["fixed_age_converged"],
        )
    ]
    scale_rows = [row["time_unit_scale"] for row in rows if row["time_unit_scale"]]
    by_observation = defaultdict(list)
    by_sigma = defaultdict(list)
    for row in rows:
        by_observation[row["observation_model"]].append(row)
        by_sigma[str(row["sigma_log"])].append(row)

    observation_summaries = {
        name: {
            "datasets": len(group),
            "age_mae_median": _finite_median([row["age_mae"] for row in group]),
            "age_bias_mean": float(np.mean([row["age_bias"] for row in group])),
            "fixed_age_rate_spearman_median": _finite_median(
                [row["fixed_age_rate_spearman"] for row in group]
            ),
        }
        for name, group in sorted(by_observation.items())
    }
    sigma_summaries = {
        name: {
            "datasets": len(group),
            "age_mae_median": _finite_median([row["age_mae"] for row in group]),
            "fixed_age_rate_spearman_median": _finite_median(
                [row["fixed_age_rate_spearman"] for row in group]
            ),
        }
        for name, group in sorted(by_sigma.items())
    }
    metrics = {
        "fit_convergence": float(np.mean(fit_flags)) if fit_flags else 0.0,
        "stress_solution_stability": float(
            np.mean([row["stress_solution_stable"] for row in rows])
        )
        if rows
        else 0.0,
        "calibration_validity": float(
            np.mean([row["calibration_valid"] for row in rows])
        )
        if rows
        else 0.0,
        "maximum_relative_objective_gap": max(
            (row["relative_objective_gap"] for row in rows), default=float("inf")
        ),
        "maximum_default_stress_age_difference": max(
            (row["default_stress_maximum_age_difference"] for row in rows),
            default=float("inf"),
        ),
        "age_mae_median": _finite_median([row["age_mae"] for row in rows]),
        "maximum_absolute_age_bias": max(
            (
                abs(summary["age_bias_mean"])
                for summary in observation_summaries.values()
            ),
            default=float("inf"),
        ),
        "fixed_age_rate_spearman_median": _finite_median(
            [row["fixed_age_rate_spearman"] for row in rows]
        ),
        "identifiable_fixed_age_rate_spearman_median": _finite_median(
            [
                row["fixed_age_rate_spearman"]
                for row in rows
                if row["observation_model"] == "expected_branch"
                and float(row["sigma_log"]) >= 0.3
            ]
        ),
        "fixed_age_centered_log_rate_rmse_median": _finite_median(
            [row["fixed_age_centered_log_rate_rmse"] for row in rows]
        ),
        "maximum_time_unit_age_difference": max(
            (
                item["maximum_normalized_age_difference"]
                for item in scale_rows
                if item["converged"] and item["calibration_valid"]
            ),
            default=float("inf"),
        ),
        "maximum_time_unit_rate_relative_error": max(
            (
                item["maximum_rate_relative_error"]
                for item in scale_rows
                if item["converged"] and item["calibration_valid"]
            ),
            default=float("inf"),
        ),
        "maximum_time_unit_penalty_relative_error": max(
            (
                item["penalty_relative_error"]
                for item in scale_rows
                if item["converged"] and item["calibration_valid"]
            ),
            default=float("inf"),
        ),
        "time_unit_checks_valid": bool(
            scale_rows
            and all(
                item["converged"] and item["calibration_valid"] for item in scale_rows
            )
        ),
        "optimizer_retries": int(sum(row["optimizer_retries"] for row in rows)),
    }
    checks = {
        "fit_convergence": metrics["fit_convergence"] >= gates["fit_convergence"],
        "stress_solution_stability": metrics["stress_solution_stability"]
        >= gates["stress_solution_stability"],
        "calibration_validity": metrics["calibration_validity"]
        >= gates["calibration_validity"],
        "objective_parity": metrics["maximum_relative_objective_gap"]
        <= gates["maximum_relative_objective_gap"],
        "chronogram_parity": metrics["maximum_default_stress_age_difference"]
        <= gates["maximum_default_stress_age_difference"],
        "age_recovery": metrics["age_mae_median"] <= gates["age_mae_median"],
        "age_bias": metrics["maximum_absolute_age_bias"]
        <= gates["maximum_absolute_age_bias"],
        "fixed_age_rate_recovery": metrics[
            "identifiable_fixed_age_rate_spearman_median"
        ]
        >= gates["fixed_age_rate_spearman_median"],
        "time_unit_invariance": bool(
            metrics["time_unit_checks_valid"]
            and metrics["maximum_time_unit_age_difference"]
            <= gates["maximum_time_unit_age_difference"]
            and metrics["maximum_time_unit_rate_relative_error"]
            <= gates["maximum_time_unit_rate_relative_error"]
            and metrics["maximum_time_unit_penalty_relative_error"]
            <= gates["maximum_time_unit_penalty_relative_error"]
        ),
    }
    return {
        "metrics": metrics,
        "checks": checks,
        "gates_passed": bool(checks and all(checks.values())),
        "observations": observation_summaries,
        "sigma_log": sigma_summaries,
    }


def _datasets(config: dict[str, Any], mode: str, resume: bool) -> list[dict[str, Any]]:
    """Enumerate deterministic study cells and independent seed streams."""
    design = config["modes"][mode]
    base_seed = int(
        config["confirmation_seed"]
        if mode == "confirmation"
        else config["development_seed"]
    )
    source_hash = _source_hash(config)
    datasets = []
    index = 0
    for ntips in design["ntips"]:
        for calibration in design["calibrations"]:
            for observation_model in design["observation_models"]:
                for sigma_log in design["sigma_log"]:
                    for replicate in range(int(design["replicates"])):
                        seed = base_seed + index * 100_003
                        datasets.append(
                            {
                                "mode": mode,
                                "scenario": "fixed-lambda-ucln-recovery",
                                "ntips": int(ntips),
                                "calibration": calibration,
                                "observation_model": observation_model,
                                "sigma_log": float(sigma_log),
                                "replicate": replicate,
                                "seed": seed,
                                "fit_seed": seed + 700_001,
                                "config": config,
                                "source_hash": source_hash,
                                "resume": resume,
                            }
                        )
                        index += 1
    return datasets


def _run_tasks(tasks: list[dict[str, Any]], ncores: int) -> list[Path]:
    """Run or resume independent fit tasks with machine-readable progress."""
    started = time.monotonic()
    workers = max(1, min(int(ncores), len(tasks)))
    paths = []
    if workers == 1:
        iterator = enumerate((_worker(task) for task in tasks), 1)
        for completed, result in iterator:
            paths.append(Path(result))
            print(
                json.dumps(
                    {
                        "event": "fit_task_complete",
                        "completed": completed,
                        "total": len(tasks),
                        "workers": workers,
                        "elapsed_seconds": time.monotonic() - started,
                        "cache": result,
                    }
                ),
                flush=True,
            )
        return paths
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_worker, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), 1):
            result = future.result()
            paths.append(Path(result))
            print(
                json.dumps(
                    {
                        "event": "fit_task_complete",
                        "completed": completed,
                        "total": len(tasks),
                        "workers": workers,
                        "elapsed_seconds": time.monotonic() - started,
                        "cache": result,
                    }
                ),
                flush=True,
            )
    return sorted(paths)


def main() -> None:
    """Run fit tasks and/or cache-only scoring for the V11 UCLN study."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("smoke", "pilot", "confirmation"), default="smoke"
    )
    parser.add_argument("--stage", choices=("all", "fit", "score"), default="all")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    if args.ncores < 1:
        parser.error("--ncores must be positive")

    config = json.loads(CONFIG_PATH.read_text())
    datasets = _datasets(config, args.mode, resume=not args.no_resume)
    tasks = _task_payloads(datasets, args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(
        args.output_dir / f"environment-v11-{args.mode}.json",
        {
            "environment": _environment(),
            "source_hash": _source_hash(config),
            "config_hash": _json_hash(config),
            "config": config,
        },
    )
    _atomic_json(
        args.output_dir / f"seeds-v11-{args.mode}.json",
        [
            {
                key: dataset[key]
                for key in (
                    "scenario",
                    "ntips",
                    "calibration",
                    "observation_model",
                    "sigma_log",
                    "replicate",
                    "seed",
                    "fit_seed",
                )
            }
            for dataset in datasets
        ],
    )

    if args.stage in {"all", "fit"}:
        _run_tasks(tasks, args.ncores)
    if args.stage == "fit":
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "datasets": len(datasets),
                    "fit_tasks": len(tasks),
                }
            )
        )
        return

    paths = _read_task_caches(tasks)
    records = _assemble(datasets, paths)
    rows = [_score_record(record) for record in records]
    summary = _summarize(rows, config["decision_gates"])
    is_confirmation = args.mode == "confirmation"
    result = {
        "study_version": int(config["study_version"]),
        "source_hash": _source_hash(config),
        "config_hash": _json_hash(config),
        "mode": args.mode,
        "scope": "fixed_lambda_ucln_numerical_and_recovery_validation",
        "lambda_selection": False,
        "sequence_length_input": False,
        "diagnostic_only": not is_confirmation,
        "release_eligible": is_confirmation,
        "datasets": rows,
        "summary": summary,
        "all_release_gates_passed": bool(is_confirmation and summary["gates_passed"]),
    }
    result_path = args.output_dir / f"results-v11-{args.mode}.json"
    _atomic_json(result_path, result)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(rows),
                "fit_tasks": len(tasks),
                "output": str(result_path),
                "gates_passed": summary["gates_passed"],
                "diagnostic_only": not is_confirmation,
            }
        ),
        flush=True,
    )
    if is_confirmation and not summary["gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
