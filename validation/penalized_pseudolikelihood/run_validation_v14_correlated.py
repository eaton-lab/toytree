#!/usr/bin/env python

"""Replay V13 numerical failures against the profiled correlated optimizer."""

# ruff: noqa: E402 -- numerical thread limits must precede NumPy/SciPy imports.

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
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

from toytree.mod._src.penalized_pseudolikelihood.correlated import (
    edges_make_ultrametric_correlated,
)
from validation.penalized_pseudolikelihood import (
    run_validation_v13_correlated as v13,
)

CONFIG_PATH = HERE / "config-v14.json"
V13_CONFIG_PATH = HERE / "config-v13.json"
V13_RESULTS_PATH = HERE / "v13" / "results-v13-pilot.json"
DEFAULT_OUTPUT = HERE / "v14"
CACHE_SCHEMA = 1
ROLES = ("default", "stress", "oracle_start", "fixed_age", "time_scaled")
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


def _fit_source_hash(config: dict[str, Any]) -> str:
    """Hash implementation and design inputs that affect fitted values."""
    digest = hashlib.sha256()
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    for name in ("correlated.py", "clock.py", "optimization.py", "utils.py"):
        source = root / name
        digest.update(source.name.encode())
        digest.update(source.read_bytes())
    for function in (
        v13._scale_true_tree,
        v13._simulate_rates,
        v13._calibrations,
        v13._fixed_calibrations,
        v13._scale_calibrations,
        v13._parent_edges,
        v13._matched_lambda,
        v13._simulate,
        _slim,
        _fit,
        _datasets,
        _task_payloads,
        _worker,
    ):
        digest.update(function.__name__.encode())
        digest.update(inspect.getsource(function).encode())
    fit_config = {
        key: value for key, value in config.items() if key != "decision_gates"
    }
    digest.update(json.dumps(fit_config, sort_keys=True).encode())
    digest.update(str(CACHE_SCHEMA).encode())
    return digest.hexdigest()


def _scoring_hash(config: dict[str, Any]) -> str:
    """Hash scoring code and thresholds separately from fit inputs."""
    digest = hashlib.sha256(_fit_source_hash(config).encode())
    for function in (_failure_reasons, _score_records, _summarize):
        digest.update(function.__name__.encode())
        digest.update(inspect.getsource(function).encode())
    digest.update(json.dumps(config["decision_gates"], sort_keys=True).encode())
    return digest.hexdigest()


def _slim(fit: dict[str, Any]) -> dict[str, Any]:
    """Return JSON-native values required for numerical replay scoring."""
    result = v13._slim(fit)
    result.update(
        {
            "optimizer_strategy": str(fit.get("optimizer_strategy", "")),
            "profile_rate_converged": bool(fit.get("profile_rate_converged", False)),
            "rate_gradient_max_abs": (
                None
                if fit.get("rate_gradient_max_abs") is None
                else float(fit["rate_gradient_max_abs"])
            ),
            "rate_gradient_before_final_polish": (
                None
                if fit.get("rate_gradient_before_final_polish") is None
                else float(fit["rate_gradient_before_final_polish"])
            ),
            "final_rate_polish_used": bool(fit.get("final_rate_polish_used", False)),
            "final_rate_polish_accepted": bool(
                fit.get("final_rate_polish_accepted", False)
            ),
            "final_rate_polish_message": fit.get("final_rate_polish_message"),
            "final_rate_polish_stationarity_steps": int(
                fit.get("final_rate_polish_stationarity_steps", 0)
            ),
            "outer_profile_converged": bool(fit.get("outer_profile_converged", False)),
            "zero_length_branch_count": int(fit.get("zero_length_branch_count", 0)),
            "evaluated_starts": int(fit.get("evaluated_starts", fit["nstarts"])),
            "basin_confirmation_run": bool(fit.get("basin_confirmation_run", False)),
            "best_basin_replicated": bool(fit.get("best_basin_replicated", False)),
        }
    )
    return result


def _fit(
    tree: Any,
    calibrations: dict[int, Any],
    payload: dict[str, Any],
    role: str,
    nstarts: int,
    true_ages: np.ndarray | None = None,
    true_rates: np.ndarray | None = None,
) -> dict[str, Any]:
    """Fit and slim one fixed-lambda correlated result."""
    options = payload["config"]["fit"]
    kwargs: dict[str, Any] = {}
    if role == "oracle_start":
        if true_ages is None or true_rates is None:
            raise ValueError("oracle_start requires true ages and rates")
        kwargs["_initial_ages"] = np.asarray(true_ages, dtype=float)
        kwargs["_initial_rates"] = np.asarray(true_rates, dtype=float)
    fit = edges_make_ultrametric_correlated(
        tree,
        lam=v13._matched_lambda(payload["sigma_log"]),
        calibrations=calibrations,
        full=True,
        inplace=False,
        max_iter=int(options["max_iter"]),
        max_fun=int(options["max_fun"]),
        max_refine=int(options["max_refine"]),
        nstarts=int(nstarts),
        ncores=1,
        seed=int(payload["fit_seed"]) + v13._role_seed_offset(role),
        _retry_multiplier=int(options["retry_multiplier"]),
        **kwargs,
    )
    return _slim(fit)


def _datasets(config: dict[str, Any], mode: str, resume: bool) -> list[dict[str, Any]]:
    """Reconstruct selected deterministic V13 pilot datasets."""
    v13_config = json.loads(V13_CONFIG_PATH.read_text())
    source = {
        v13._dataset_id(payload): payload
        for payload in v13._datasets(v13_config, "pilot", resume=True)
    }
    design = config["modes"][mode]
    selected = [
        ("target", value) for value in config["targets"][: int(design["target_count"])]
    ]
    selected.extend(
        ("control", value)
        for value in config["controls"][: int(design["control_count"])]
    )
    missing = [value for _, value in selected if value not in source]
    if missing:
        raise RuntimeError(f"V13 dataset identifiers are unavailable: {missing}")
    source_hash = _fit_source_hash(config)
    datasets = []
    for cohort, identifier in selected:
        payload = dict(source[identifier])
        payload.update(
            {
                "mode": mode,
                "cohort": cohort,
                "config": config,
                "source_hash": source_hash,
                "resume": bool(resume),
            }
        )
        datasets.append(payload)
    return datasets


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    """Return the deterministic path for one independent V14 fit."""
    return (
        output_dir
        / "cache-v14"
        / payload["mode"]
        / f"{v13._dataset_id(payload)}-{payload['role']}.json"
    )


def _task_payloads(
    datasets: list[dict[str, Any]], output_dir: Path
) -> list[dict[str, Any]]:
    """Expand selected datasets into globally parallel fit tasks."""
    tasks = []
    for dataset in datasets:
        for role in ROLES:
            task = dict(dataset)
            task["role"] = role
            fingerprint_value = {
                key: value
                for key, value in task.items()
                if key not in {"resume", "source_hash"}
            } | {
                "source_hash": task["source_hash"],
                "cache_schema": CACHE_SCHEMA,
            }
            task["fingerprint"] = _json_hash(fingerprint_value)
            task["cache_path"] = str(_cache_path(output_dir, task))
            tasks.append(task)
    return tasks


def _worker(payload: dict[str, Any]) -> str:
    """Simulate and atomically cache one profiled-optimizer fit."""
    path = Path(payload["cache_path"])
    if payload["resume"] and path.exists():
        try:
            cached = json.loads(path.read_text())
            if cached.get("fingerprint") == payload["fingerprint"]:
                return str(path)
        except (OSError, json.JSONDecodeError):
            pass

    simulated = v13._simulate(payload)
    calibrations = v13._calibrations(simulated["true_tree"], payload["calibration"])
    role = payload["role"]
    options = payload["config"]["fit"]
    nstarts = int(options["default_nstarts"])
    fit_calibrations = calibrations
    if role == "stress":
        nstarts = int(options["stress_nstarts"])
    elif role == "oracle_start":
        nstarts = int(options["oracle_nstarts"])
    elif role == "fixed_age":
        fit_calibrations = v13._fixed_calibrations(simulated["true_tree"])
    elif role == "time_scaled":
        fit_calibrations = v13._scale_calibrations(calibrations, v13.TIME_UNIT_FACTOR)

    fit = _fit(
        simulated["observed_tree"],
        fit_calibrations,
        payload,
        role,
        nstarts,
        true_ages=(simulated["true_ages"] if role == "oracle_start" else None),
        true_rates=(simulated["true_rates"] if role == "oracle_start" else None),
    )
    _atomic_json(
        path,
        {
            "cache_schema": CACHE_SCHEMA,
            "fingerprint": payload["fingerprint"],
            "dataset_id": v13._dataset_id(payload),
            "role": role,
            "fit": fit,
        },
    )
    return str(path)


def _read_task_caches(tasks: list[dict[str, Any]]) -> list[Path]:
    """Require every selected role cache to match the current fingerprint."""
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


def _failure_reasons(row: dict[str, Any], gates: dict[str, float]) -> list[str]:
    """Return prespecified numerical failures for one refitted dataset."""
    reasons = []
    for name in (
        "default_converged",
        "stress_converged",
        "oracle_start_converged",
        "fixed_age_converged",
    ):
        if not row[name]:
            reasons.append(name)
    if not row["stress_solution_stable"]:
        reasons.append("stress_solution_stable")
    if not row["calibration_valid"]:
        reasons.append("calibration_valid")
    if row["relative_objective_gap"] > gates["maximum_relative_objective_gap"]:
        reasons.append("objective_parity")
    if (
        row["default_reference_maximum_age_difference"]
        > gates["maximum_default_reference_age_difference"]
    ):
        reasons.append("chronogram_parity")
    scale = row["time_unit_scale"]
    if (
        scale is None
        or not scale["converged"]
        or not scale["calibration_valid"]
        or scale["maximum_normalized_age_difference"]
        > gates["maximum_time_unit_age_difference"]
        or scale["maximum_rate_relative_error"]
        > gates["maximum_time_unit_rate_relative_error"]
        or scale["penalty_relative_error"]
        > gates["maximum_time_unit_penalty_relative_error"]
    ):
        reasons.append("time_unit_invariance")
    if not row["all_profile_rate_converged"]:
        reasons.append("profile_rate_convergence")
    if (
        row["maximum_projected_rate_gradient"]
        > gates["maximum_projected_rate_gradient"]
    ):
        reasons.append("profile_rate_gradient")
    return reasons


def _score_records(
    records: list[dict[str, Any]],
    datasets: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Score refits and attach their frozen V13 baselines."""
    baselines = {
        row["dataset_id"]: row
        for row in json.loads(V13_RESULTS_PATH.read_text())["datasets"]
    }
    cohorts = {v13._dataset_id(item): item["cohort"] for item in datasets}
    rows = []
    for record in records:
        row = v13._score_record(record)
        identifier = row["dataset_id"]
        baseline = baselines[identifier]
        gradients = [
            float(fit["rate_gradient_max_abs"])
            for fit in record["fits"].values()
            if fit["rate_gradient_max_abs"] is not None
        ]
        row.update(
            {
                "cohort": cohorts[identifier],
                "all_profile_rate_converged": all(
                    fit["profile_rate_converged"] for fit in record["fits"].values()
                ),
                "maximum_projected_rate_gradient": max(gradients, default=float("inf")),
                "baseline_age_mae": float(baseline["age_mae"]),
                "baseline_fixed_age_rate_spearman": float(
                    baseline["fixed_age_rate_spearman"]
                ),
                "age_mae_change": float(row["age_mae"] - baseline["age_mae"]),
                "fixed_age_rate_spearman_change": float(
                    row["fixed_age_rate_spearman"] - baseline["fixed_age_rate_spearman"]
                ),
            }
        )
        row["failure_reasons"] = _failure_reasons(row, config["decision_gates"])
        row["numerical_gates_passed"] = not row["failure_reasons"]
        rows.append(row)
    return rows


def _summarize(rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    """Summarize targeted fixes and positive-control nonregression."""
    gates = config["decision_gates"]
    targets = [row for row in rows if row["cohort"] == "target"]
    controls = [row for row in rows if row["cohort"] == "control"]
    scale_rows = [row["time_unit_scale"] for row in rows]
    metrics = {
        "datasets": len(rows),
        "targets": len(targets),
        "controls": len(controls),
        "historical_target_failures": len(targets),
        "remaining_target_failures": sum(
            not row["numerical_gates_passed"] for row in targets
        ),
        "new_control_failures": sum(
            not row["numerical_gates_passed"] for row in controls
        ),
        "fit_convergence": float(
            np.mean(
                [
                    row[key]
                    for row in rows
                    for key in (
                        "default_converged",
                        "stress_converged",
                        "oracle_start_converged",
                        "fixed_age_converged",
                    )
                ]
            )
        ),
        "stress_solution_stability": float(
            np.mean([row["stress_solution_stable"] for row in rows])
        ),
        "calibration_validity": float(
            np.mean([row["calibration_valid"] for row in rows])
        ),
        "profile_rate_convergence": float(
            np.mean([row["all_profile_rate_converged"] for row in rows])
        ),
        "maximum_projected_rate_gradient": max(
            row["maximum_projected_rate_gradient"] for row in rows
        ),
        "maximum_relative_objective_gap": max(
            row["relative_objective_gap"] for row in rows
        ),
        "maximum_default_reference_age_difference": max(
            row["default_reference_maximum_age_difference"] for row in rows
        ),
        "maximum_time_unit_age_difference": max(
            item["maximum_normalized_age_difference"] for item in scale_rows
        ),
        "maximum_time_unit_rate_relative_error": max(
            item["maximum_rate_relative_error"] for item in scale_rows
        ),
        "maximum_time_unit_penalty_relative_error": max(
            item["penalty_relative_error"] for item in scale_rows
        ),
        "maximum_control_age_mae_increase": max(
            (row["age_mae_change"] for row in controls), default=0.0
        ),
        "maximum_control_rate_spearman_decrease": max(
            (-row["fixed_age_rate_spearman_change"] for row in controls),
            default=0.0,
        ),
    }
    checks = {
        "all_historical_numerical_failures_resolved": (
            metrics["remaining_target_failures"] == 0
        ),
        "positive_controls_remain_numerically_valid": (
            metrics["new_control_failures"] == 0
        ),
        "profile_rate_convergence": metrics["profile_rate_convergence"] == 1.0,
        "profile_rate_gradient": metrics["maximum_projected_rate_gradient"]
        <= gates["maximum_projected_rate_gradient"],
        "control_age_recovery_noninferiority": metrics[
            "maximum_control_age_mae_increase"
        ]
        <= gates["maximum_control_age_mae_increase"],
        "control_rate_recovery_noninferiority": metrics[
            "maximum_control_rate_spearman_decrease"
        ]
        <= gates["maximum_control_rate_spearman_decrease"],
    }
    return {
        "metrics": metrics,
        "checks": checks,
        "gates_passed": bool(checks and all(checks.values())),
        "failure_counts": {
            reason: sum(reason in row["failure_reasons"] for row in rows)
            for reason in sorted(
                {reason for row in rows for reason in row["failure_reasons"]}
            )
        },
    }


def _run_tasks(tasks: list[dict[str, Any]], ncores: int) -> list[Path]:
    """Run or resume fit-role tasks with machine-readable progress."""
    started = time.monotonic()
    workers = max(1, min(int(ncores), len(tasks)))
    paths = []
    if workers == 1:
        for completed, task in enumerate(tasks, 1):
            result = _worker(task)
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
    """Run fit tasks and/or cache-only scoring for the V14 replay."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "replay"), default="smoke")
    parser.add_argument("--stage", choices=("all", "fit", "score"), default="all")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    if args.ncores < 1:
        parser.error("--ncores must be positive")
    if not V13_RESULTS_PATH.exists():
        parser.error(f"required V13 pilot result is missing: {V13_RESULTS_PATH}")

    config = json.loads(CONFIG_PATH.read_text())
    datasets = _datasets(config, args.mode, resume=not args.no_resume)
    tasks = _task_payloads(datasets, args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(
        args.output_dir / f"environment-v14-{args.mode}.json",
        {
            "environment": v13._environment(),
            "fit_source_hash": _fit_source_hash(config),
            "scoring_hash": _scoring_hash(config),
            "config_hash": _json_hash(config),
            "config": config,
            "v13_results_hash": hashlib.sha256(
                V13_RESULTS_PATH.read_bytes()
            ).hexdigest(),
        },
    )
    _atomic_json(
        args.output_dir / f"seeds-v14-{args.mode}.json",
        [
            {
                "dataset_id": v13._dataset_id(dataset),
                "cohort": dataset["cohort"],
                **{
                    key: dataset[key]
                    for key in (
                        "ntips",
                        "calibration",
                        "observation_model",
                        "sigma_log",
                        "replicate",
                        "seed",
                        "fit_seed",
                    )
                },
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
    records = v13._assemble(datasets, paths)
    rows = _score_records(records, datasets, config)
    summary = _summarize(rows, config)
    result = {
        "study_version": int(config["study_version"]),
        "source_study": int(config["source_study"]),
        "fit_source_hash": _fit_source_hash(config),
        "scoring_hash": _scoring_hash(config),
        "config_hash": _json_hash(config),
        "mode": args.mode,
        "scope": "profiled_correlated_optimizer_targeted_numerical_replay",
        "lambda_selection": False,
        "diagnostic_only": True,
        "release_eligible": False,
        "datasets": rows,
        "summary": summary,
        "all_release_gates_passed": False,
    }
    result_path = args.output_dir / f"results-v14-{args.mode}.json"
    _atomic_json(result_path, result)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(rows),
                "fit_tasks": len(tasks),
                "output": str(result_path),
                "gates_passed": summary["gates_passed"],
                "diagnostic_only": True,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
