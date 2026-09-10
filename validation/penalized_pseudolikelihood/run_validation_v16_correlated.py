#!/usr/bin/env python

"""Replay V15 rate-gradient cases, then run a fresh V16 confirmation."""

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

from validation.penalized_pseudolikelihood import (
    run_validation_v13_correlated as v13,
)
from validation.penalized_pseudolikelihood import (
    run_validation_v14_correlated as v14,
)
from validation.penalized_pseudolikelihood import (
    run_validation_v15_correlated as v15,
)

CONFIG_PATH = HERE / "config-v16.json"
V15_CONFIG_PATH = HERE / "config-v15.json"
V15_RESULTS_PATH = HERE / "v15" / "results-v15-confirmation.json"
DEFAULT_OUTPUT = HERE / "v16"
CACHE_SCHEMA = 1
ROLES = v15.ROLES


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
        v15._worker,
        _datasets,
        _roles,
        _task_payloads,
        _worker,
    ):
        digest.update(function.__name__.encode())
        digest.update(inspect.getsource(function).encode())
    fit_config = {
        key: value
        for key, value in config.items()
        if key not in {"decision_gates", "replay_gates"}
    }
    digest.update(json.dumps(fit_config, sort_keys=True).encode())
    digest.update(str(CACHE_SCHEMA).encode())
    return digest.hexdigest()


def _scoring_hash(config: dict[str, Any]) -> str:
    """Hash scoring functions and frozen thresholds separately from fits."""
    digest = hashlib.sha256(_fit_source_hash(config).encode())
    for function in (
        v13._assemble,
        v13._score_record,
        v15._score_records,
        v15._summarize,
        _score_records,
        _replay_summary,
    ):
        digest.update(function.__name__.encode())
        digest.update(inspect.getsource(function).encode())
    digest.update(json.dumps(config["decision_gates"], sort_keys=True).encode())
    digest.update(json.dumps(config["replay_gates"], sort_keys=True).encode())
    return digest.hexdigest()


def _datasets(config: dict[str, Any], mode: str, resume: bool) -> list[dict[str, Any]]:
    """Enumerate smoke, targeted V15 replay, or fresh confirmation data."""
    source_hash = _fit_source_hash(config)
    if mode != "replay":
        datasets = v13._datasets(config, mode, resume)
        for payload in datasets:
            payload["source_hash"] = source_hash
        return datasets

    v15_config = json.loads(V15_CONFIG_PATH.read_text())
    source = {
        v13._dataset_id(payload): payload
        for payload in v15._datasets(v15_config, "confirmation", resume=True)
    }
    selected = [("target", value) for value in config["replay_targets"]]
    selected.extend(("control", value) for value in config["replay_controls"])
    missing = [identifier for _, identifier in selected if identifier not in source]
    if missing:
        raise RuntimeError(f"V15 replay datasets are unavailable: {missing}")
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


def _roles(payload: dict[str, Any]) -> tuple[str, ...]:
    """Return independently runnable roles for one dataset."""
    if payload["mode"] != "replay" and int(payload["replicate"]) == 0:
        return ROLES + ("time_scaled",)
    return ROLES


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    """Return the deterministic path for one V16 fit task."""
    return (
        output_dir
        / "cache-v16"
        / payload["mode"]
        / f"{v13._dataset_id(payload)}-{payload['role']}.json"
    )


def _task_fingerprint(payload: dict[str, Any]) -> str:
    """Return a strict fingerprint for one V16 fit task."""
    value = {
        key: item
        for key, item in payload.items()
        if key not in {"resume", "fingerprint", "cache_path"}
    } | {"cache_schema": CACHE_SCHEMA}
    return v14._json_hash(value)


def _task_payloads(
    datasets: list[dict[str, Any]], output_dir: Path
) -> list[dict[str, Any]]:
    """Expand datasets into globally parallel, independently cached fits."""
    tasks = []
    for dataset in datasets:
        for role in _roles(dataset):
            task = dict(dataset)
            task["role"] = role
            task["fingerprint"] = _task_fingerprint(task)
            task["cache_path"] = str(_cache_path(output_dir, task))
            tasks.append(task)
    return tasks


def _worker(payload: dict[str, Any]) -> str:
    """Fit and atomically cache one V16 role using the V15 worker."""
    return v15._worker(payload)


def _read_task_caches(tasks: list[dict[str, Any]]) -> list[Path]:
    """Require every V16 task cache to match the frozen fingerprint."""
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


def _score_records(
    datasets: list[dict[str, Any]], paths: list[Path]
) -> list[dict[str, Any]]:
    """Score fits and retain final-rate-polish diagnostics."""
    records = v13._assemble(datasets, paths)
    rows = v15._score_records(records)
    records_by_id = {record["dataset_id"]: record for record in records}
    cohorts = {v13._dataset_id(payload): payload.get("cohort") for payload in datasets}
    for row in rows:
        fits = records_by_id[row["dataset_id"]]["fits"]
        row.update(
            {
                "cohort": cohorts[row["dataset_id"]],
                "final_rate_polish_roles": [
                    role for role, fit in fits.items() if fit["final_rate_polish_used"]
                ],
                "all_used_final_rate_polishes_accepted": all(
                    fit["final_rate_polish_accepted"]
                    for fit in fits.values()
                    if fit["final_rate_polish_used"]
                ),
                "maximum_rate_gradient_before_final_polish": max(
                    float(fit["rate_gradient_before_final_polish"])
                    for fit in fits.values()
                ),
            }
        )
    return rows


def _replay_summary(
    rows: list[dict[str, Any]], config: dict[str, Any]
) -> dict[str, Any]:
    """Apply frozen targeted-replay gates and compare V15 controls."""
    gates = config["replay_gates"]
    baseline = {
        row["dataset_id"]: row
        for row in json.loads(V15_RESULTS_PATH.read_text())["datasets"]
    }
    targets = [row for row in rows if row["cohort"] == "target"]
    controls = [row for row in rows if row["cohort"] == "control"]

    def numerically_valid(row: dict[str, Any]) -> bool:
        return bool(
            row["default_converged"]
            and row["stress_converged"]
            and row["oracle_start_converged"]
            and row["fixed_age_converged"]
            and row["all_profile_rate_converged"]
            and row["maximum_projected_rate_gradient"]
            <= gates["maximum_projected_rate_gradient"]
            and row["relative_objective_gap"] <= gates["maximum_relative_objective_gap"]
            and row["default_reference_maximum_age_difference"]
            <= gates["maximum_default_reference_age_difference"]
            and row["calibration_valid"]
            and row["stress_solution_stable"]
        )

    control_age_increases = [
        row["age_mae"] - baseline[row["dataset_id"]]["age_mae"] for row in controls
    ]
    metrics = {
        "datasets": len(rows),
        "targets": len(targets),
        "controls": len(controls),
        "remaining_target_failures": sum(not numerically_valid(row) for row in targets),
        "new_control_failures": sum(not numerically_valid(row) for row in controls),
        "maximum_projected_rate_gradient": max(
            row["maximum_projected_rate_gradient"] for row in rows
        ),
        "maximum_relative_objective_gap": max(
            row["relative_objective_gap"] for row in rows
        ),
        "maximum_default_reference_age_difference": max(
            row["default_reference_maximum_age_difference"] for row in rows
        ),
        "maximum_control_age_mae_increase": max(control_age_increases, default=0.0),
        "datasets_using_final_rate_polish": sum(
            bool(row["final_rate_polish_roles"]) for row in rows
        ),
        "all_used_final_rate_polishes_accepted": all(
            row["all_used_final_rate_polishes_accepted"] for row in rows
        ),
    }
    checks = {
        "all_target_numerical_failures_resolved": (
            metrics["remaining_target_failures"] == 0
        ),
        "positive_controls_remain_valid": metrics["new_control_failures"] == 0,
        "profile_rate_gradient": metrics["maximum_projected_rate_gradient"]
        <= gates["maximum_projected_rate_gradient"],
        "objective_parity": metrics["maximum_relative_objective_gap"]
        <= gates["maximum_relative_objective_gap"],
        "chronogram_parity": metrics["maximum_default_reference_age_difference"]
        <= gates["maximum_default_reference_age_difference"],
        "control_age_recovery_noninferiority": metrics[
            "maximum_control_age_mae_increase"
        ]
        <= gates["maximum_control_age_mae_increase"],
        "used_polishes_accepted": metrics["all_used_final_rate_polishes_accepted"],
    }
    return {
        "metrics": metrics,
        "checks": checks,
        "gates_passed": bool(checks and all(checks.values())),
    }


def _run_tasks(tasks: list[dict[str, Any]], ncores: int) -> list[Path]:
    """Run or resume fit tasks with one global process pool."""
    started = time.monotonic()
    workers = max(1, min(int(ncores), len(tasks)))
    paths = []
    if workers == 1:
        iterator = enumerate(tasks, 1)
        for completed, task in iterator:
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
    """Run the targeted replay, smoke preflight, or fresh confirmation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("smoke", "replay", "confirmation"), default="smoke"
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
    v14._atomic_json(
        args.output_dir / f"environment-v16-{args.mode}.json",
        {
            "environment": v13._environment(),
            "fit_source_hash": _fit_source_hash(config),
            "scoring_hash": _scoring_hash(config),
            "config_hash": v14._json_hash(config),
            "config": config,
        },
    )
    v14._atomic_json(
        args.output_dir / f"seeds-v16-{args.mode}.json",
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
    rows = _score_records(datasets, paths)
    summary = (
        _replay_summary(rows, config)
        if args.mode == "replay"
        else v15._summarize(rows, config)
    )
    is_confirmation = args.mode == "confirmation"
    result = {
        "study_version": int(config["study_version"]),
        "fit_source_hash": _fit_source_hash(config),
        "scoring_hash": _scoring_hash(config),
        "config_hash": v14._json_hash(config),
        "mode": args.mode,
        "scope": "final_rate_polish_and_fixed_lambda_correlated_confirmation",
        "lambda_selection": False,
        "sequence_length_input": False,
        "diagnostic_only": not is_confirmation,
        "release_eligible": is_confirmation,
        "datasets": rows,
        "summary": summary,
        "all_release_gates_passed": bool(is_confirmation and summary["gates_passed"]),
    }
    result_path = args.output_dir / f"results-v16-{args.mode}.json"
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
    if args.mode in {"replay", "confirmation"} and not summary["gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
