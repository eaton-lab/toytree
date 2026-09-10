#!/usr/bin/env python

"""Independently seeded confirmation of fixed-lambda correlated fitting."""

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

from validation.penalized_pseudolikelihood import (
    run_validation_v13_correlated as v13,
)
from validation.penalized_pseudolikelihood import (
    run_validation_v14_correlated as v14,
)

CONFIG_PATH = HERE / "config-v15.json"
DEFAULT_OUTPUT = HERE / "v15"
CACHE_SCHEMA = 1
ROLES = ("default", "stress", "oracle_start", "fixed_age")
COMPATIBLE_FIT_SOURCE_HASHES = {
    # V15 was already running remotely when a reporting-only KeyError was
    # found for failed multistart records. Successful caches produced by this
    # source remain numerically compatible with the repaired implementation.
    "5a7a517aba69be977ac2bc9f8ccb066febfa88922853c219d1828dba1080149b": (
        "pre-fix V15 source; failed-start metadata schema only"
    ),
}


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
        v13._role_seed_offset,
        v14._slim,
        v14._fit,
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
    """Hash scoring and thresholds without invalidating compatible fits."""
    digest = hashlib.sha256(_fit_source_hash(config).encode())
    for function in (
        v13._assemble,
        v13._calibration_records,
        v13._calibrations_valid,
        v13._center_log_rates,
        v13._rate_increments,
        v13._safe_spearman,
        v13._reference_fit,
        v13._score_record,
        v13._finite_median,
        v13._summarize,
        _score_records,
        _quantile,
        _summarize,
    ):
        digest.update(function.__name__.encode())
        digest.update(inspect.getsource(function).encode())
    digest.update(json.dumps(config["decision_gates"], sort_keys=True).encode())
    return digest.hexdigest()


def _datasets(config: dict[str, Any], mode: str, resume: bool) -> list[dict[str, Any]]:
    """Enumerate the deterministic smoke or untouched confirmation stream."""
    datasets = v13._datasets(config, mode, resume)
    source_hash = _fit_source_hash(config)
    for payload in datasets:
        payload["source_hash"] = source_hash
    return datasets


def _roles(payload: dict[str, Any]) -> tuple[str, ...]:
    """Return independent fit roles for one confirmation dataset."""
    if int(payload["replicate"]) == 0:
        return ROLES + ("time_scaled",)
    return ROLES


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    """Return the deterministic path for one independent V15 fit."""
    return (
        output_dir
        / "cache-v15"
        / payload["mode"]
        / f"{v13._dataset_id(payload)}-{payload['role']}.json"
    )


def _task_payloads(
    datasets: list[dict[str, Any]], output_dir: Path
) -> list[dict[str, Any]]:
    """Expand datasets into globally parallel, independently cached fits."""
    tasks = []
    for dataset in datasets:
        for role in _roles(dataset):
            task = dict(dataset)
            task["role"] = role
            task["fingerprint"] = _task_fingerprint(task, task["source_hash"])
            task["cache_path"] = str(_cache_path(output_dir, task))
            tasks.append(task)
    return tasks


def _task_fingerprint(payload: dict[str, Any], source_hash: str) -> str:
    """Return one fit-task fingerprint for an explicit source hash."""
    fingerprint_value = {
        key: value
        for key, value in payload.items()
        if key
        not in {
            "resume",
            "source_hash",
            "fingerprint",
            "cache_path",
        }
    } | {
        "source_hash": source_hash,
        "cache_schema": CACHE_SCHEMA,
    }
    return v14._json_hash(fingerprint_value)


def _accepted_task_fingerprints(payload: dict[str, Any]) -> set[str]:
    """Return current and explicitly audited compatible fingerprints."""
    source_hashes = {payload["source_hash"], *COMPATIBLE_FIT_SOURCE_HASHES}
    return {_task_fingerprint(payload, value) for value in source_hashes}


def _worker(payload: dict[str, Any]) -> str:
    """Simulate and atomically cache one confirmation fit."""
    path = Path(payload["cache_path"])
    if payload["resume"] and path.exists():
        try:
            cached = json.loads(path.read_text())
            if cached.get("fingerprint") in _accepted_task_fingerprints(payload):
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

    fit = v14._fit(
        simulated["observed_tree"],
        fit_calibrations,
        payload,
        role,
        nstarts,
        true_ages=(simulated["true_ages"] if role == "oracle_start" else None),
        true_rates=(simulated["true_rates"] if role == "oracle_start" else None),
    )
    v14._atomic_json(
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
    """Require all role caches and their fit fingerprints to match."""
    paths = []
    for task in tasks:
        path = Path(task["cache_path"])
        if not path.exists():
            raise FileNotFoundError(f"missing cache: {path}")
        cached = json.loads(path.read_text())
        if cached.get("fingerprint") not in _accepted_task_fingerprints(task):
            raise RuntimeError(f"stale cache fingerprint: {path}")
        paths.append(path)
    return paths


def _score_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Score confirmation records and retain profiled-optimizer diagnostics."""
    rows = []
    for record in records:
        row = v13._score_record(record)
        fits = record["fits"]
        primary = [fits[name] for name in ROLES]
        all_fits = list(fits.values())
        gradients = [
            float(fit["rate_gradient_max_abs"])
            for fit in all_fits
            if fit["rate_gradient_max_abs"] is not None
        ]
        row.update(
            {
                "all_profile_rate_converged": all(
                    fit["profile_rate_converged"] for fit in all_fits
                ),
                "maximum_projected_rate_gradient": max(gradients, default=float("inf")),
                "default_best_basin_replicated": bool(
                    fits["default"]["best_basin_replicated"]
                ),
                "stress_best_basin_replicated": bool(
                    fits["stress"]["best_basin_replicated"]
                ),
                "all_primary_outer_profiles_converged": all(
                    fit["outer_profile_converged"] for fit in primary
                ),
            }
        )
        rows.append(row)
    return rows


def _quantile(values: list[float], probability: float) -> float:
    """Return a finite quantile or positive infinity."""
    array = np.asarray(values, dtype=float)
    array = array[np.isfinite(array)]
    return float(np.quantile(array, probability)) if array.size else float("inf")


def _summarize(rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    """Apply frozen statistical and numerical confirmation gates."""
    gates = config["decision_gates"]
    inherited_gates = dict(gates)
    inherited_gates["fixed_age_increment_spearman_median"] = -1.0
    summary = v13._summarize(rows, inherited_gates)
    summary["checks"].pop("fixed_age_increment_recovery")

    positive = [
        row
        for row in rows
        if row["observation_model"] in {"expected_branch", "continuous_gamma"}
    ]
    metrics = summary["metrics"]
    metrics.update(
        {
            "age_mae_p90": _quantile([row["age_mae"] for row in rows], 0.9),
            "positive_continuous_age_mae_p90": _quantile(
                [row["age_mae"] for row in positive], 0.9
            ),
            "profile_rate_convergence": float(
                np.mean([row["all_profile_rate_converged"] for row in rows])
            ),
            "maximum_projected_rate_gradient": max(
                (row["maximum_projected_rate_gradient"] for row in rows),
                default=float("inf"),
            ),
            "default_best_basin_replication": float(
                np.mean([row["default_best_basin_replicated"] for row in rows])
            ),
            "stress_best_basin_replication": float(
                np.mean([row["stress_best_basin_replicated"] for row in rows])
            ),
            "primary_outer_profile_convergence": float(
                np.mean([row["all_primary_outer_profiles_converged"] for row in rows])
            ),
        }
    )
    summary["checks"].update(
        {
            "age_recovery_p90": metrics["age_mae_p90"] <= gates["age_mae_p90"],
            "positive_continuous_age_recovery_p90": metrics[
                "positive_continuous_age_mae_p90"
            ]
            <= gates["positive_continuous_age_mae_p90"],
            "profile_rate_convergence": metrics["profile_rate_convergence"]
            >= gates["profile_rate_convergence"],
            "profile_rate_gradient": metrics["maximum_projected_rate_gradient"]
            <= gates["maximum_projected_rate_gradient"],
            "default_basin_replication": metrics["default_best_basin_replication"]
            >= gates["best_basin_replication"],
            "stress_basin_replication": metrics["stress_best_basin_replication"]
            >= gates["best_basin_replication"],
        }
    )
    summary["diagnostics"] = {
        "fixed_age_increment_spearman_median": metrics[
            "fixed_age_increment_spearman_median"
        ],
        "fixed_age_increment_rmse_median": metrics["fixed_age_increment_rmse_median"],
        "primary_outer_profile_convergence": metrics[
            "primary_outer_profile_convergence"
        ],
    }
    summary["gates_passed"] = bool(
        summary["checks"] and all(summary["checks"].values())
    )
    return summary


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
    """Run smoke preflight or the frozen V15 confirmation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "confirmation"), default="smoke")
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
    v14._atomic_json(
        args.output_dir / f"environment-v15-{args.mode}.json",
        {
            "environment": v13._environment(),
            "fit_source_hash": _fit_source_hash(config),
            "compatible_fit_source_hashes": COMPATIBLE_FIT_SOURCE_HASHES,
            "scoring_hash": _scoring_hash(config),
            "config_hash": v14._json_hash(config),
            "config": config,
        },
    )
    v14._atomic_json(
        args.output_dir / f"seeds-v15-{args.mode}.json",
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
    records = v13._assemble(datasets, paths)
    rows = _score_records(records)
    summary = _summarize(rows, config)
    is_confirmation = args.mode == "confirmation"
    result = {
        "study_version": int(config["study_version"]),
        "fit_source_hash": _fit_source_hash(config),
        "compatible_fit_source_hashes": COMPATIBLE_FIT_SOURCE_HASHES,
        "scoring_hash": _scoring_hash(config),
        "config_hash": v14._json_hash(config),
        "mode": args.mode,
        "scope": "fixed_lambda_correlated_profiled_optimizer_confirmation",
        "lambda_selection": False,
        "sequence_length_input": False,
        "diagnostic_only": not is_confirmation,
        "release_eligible": is_confirmation,
        "datasets": rows,
        "summary": summary,
        "all_release_gates_passed": bool(is_confirmation and summary["gates_passed"]),
    }
    result_path = args.output_dir / f"results-v15-{args.mode}.json"
    v14._atomic_json(result_path, result)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(rows),
                "fit_tasks": len(tasks),
                "output": str(result_path),
                "gates_passed": summary["gates_passed"],
                "all_release_gates_passed": result["all_release_gates_passed"],
            }
        ),
        flush=True,
    )
    if is_confirmation and not summary["gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
