#!/usr/bin/env python

"""Replay only nonconverged ToyTree V17 fits with production budgets."""

# ruff: noqa: E402 -- thread limits must precede NumPy/SciPy imports.

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
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
    run_validation_v17_benchmark as v17,
)

DEFAULT_OUTPUT = HERE / "v17"
REPLAY_SCHEMA = 1
PRODUCTION_BUDGET = {
    "max_iter": 100_000,
    "max_fun": 100_000,
    "max_refine": 20,
}


def _read_json(path: Path) -> dict[str, Any]:
    """Read one JSON object."""
    return json.loads(path.read_text())


def _target_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Return nonconverged or otherwise ineligible ToyTree result rows."""
    return sorted(
        (
            row
            for row in result["rows"]
            if row["engine"] == "toytree" and not row["accuracy_eligible"]
        ),
        key=lambda row: row["dataset_id"],
    )


def _cache_path(output_dir: Path, mode: str, dataset_id: str) -> Path:
    """Return the independent production-budget replay cache path."""
    return (
        output_dir
        / "cache-v17"
        / mode
        / "failure-production-budget"
        / f"{dataset_id}.json"
    )


def _fit_options(config: dict[str, Any]) -> dict[str, Any]:
    """Return V17 options with public production budgets restored."""
    options = deepcopy(config["fit"])
    options.update(PRODUCTION_BUDGET)
    return options


def _payloads(
    result: dict[str, Any],
    config: dict[str, Any],
    output_dir: Path,
    mode: str,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Create fingerprinted tasks for only failed ToyTree fits."""
    targets = _target_rows(result)
    if limit is not None:
        targets = targets[:limit]
    options = _fit_options(config)
    payloads = []
    for baseline in targets:
        dataset_id = baseline["dataset_id"]
        manifest_path = v17._manifest_path(output_dir, mode, dataset_id)
        if not manifest_path.exists():
            raise RuntimeError(
                "V17 dataset caches are required for this replay; run it in the "
                f"checkout that produced the benchmark fits. Missing: {manifest_path}"
            )
        manifest = _read_json(manifest_path)
        model = manifest["fit_model"]
        fingerprint = v17._json_hash(
            {
                "schema": REPLAY_SCHEMA,
                "dataset_fingerprint": manifest["fingerprint"],
                "solver_hash": v17._solver_hash(model),
                "fit_options": options,
                "selection": "ineligible_toytree_v17_confirmation_fit",
            }
        )
        payloads.append(
            {
                "dataset_id": dataset_id,
                "manifest_path": str(manifest_path),
                "cache_path": str(_cache_path(output_dir, mode, dataset_id)),
                "fit_options": options,
                "fingerprint": fingerprint,
            }
        )
    return payloads


def _worker(payload: dict[str, Any]) -> dict[str, Any]:
    """Refit one failed dataset without modifying its original cache."""
    cache_path = Path(payload["cache_path"])
    if cache_path.exists():
        cached = _read_json(cache_path)
        if cached.get("fingerprint") != payload["fingerprint"]:
            raise RuntimeError(f"stale V17 failure-replay cache: {cache_path}")
        return {"cache_path": str(cache_path), "resumed": True}
    dataset = _read_json(Path(payload["manifest_path"]))
    fit = v17._fit_toytree(dataset, payload["fit_options"])
    v17._atomic_json(
        cache_path,
        {
            "replay_schema": REPLAY_SCHEMA,
            "dataset_id": payload["dataset_id"],
            "fingerprint": payload["fingerprint"],
            "fit": fit,
        },
    )
    return {"cache_path": str(cache_path), "resumed": False}


def _run(payloads: list[dict[str, Any]], ncores: int) -> None:
    """Run independent failed-fit replays in a global process pool."""
    started = time.perf_counter()
    completed = 0
    with ProcessPoolExecutor(max_workers=ncores) as pool:
        futures = {pool.submit(_worker, payload): payload for payload in payloads}
        for future in as_completed(futures):
            result = future.result()
            completed += 1
            print(
                json.dumps(
                    {
                        "event": "failure_replay_fit_complete",
                        "completed": completed,
                        "total": len(payloads),
                        "dataset_id": Path(result["cache_path"]).stem,
                        "resumed": result["resumed"],
                        "elapsed_seconds": time.perf_counter() - started,
                    }
                ),
                flush=True,
            )


def _objective(row: dict[str, Any]) -> float | None:
    """Return the model-compatible maximized objective from a scored row."""
    key = "pseudologlik" if row["scenario"] == "clock" else "penalized_pseudologlik"
    value = row.get(key)
    return None if value is None else float(value)


def _fraction(values: list[bool]) -> float | None:
    """Return a Boolean fraction or None for an empty collection."""
    return float(np.mean(values)) if values else None


def _score(
    result: dict[str, Any],
    payloads: list[dict[str, Any]],
    output_dir: Path,
    mode: str,
) -> dict[str, Any]:
    """Compare production-budget replays with their frozen V17 results."""
    baseline = {row["dataset_id"]: row for row in _target_rows(result)}
    records = []
    for payload in payloads:
        dataset = _read_json(Path(payload["manifest_path"]))
        replay = _read_json(Path(payload["cache_path"]))
        current = v17._score_fit(
            dataset,
            {"engine": "toytree_production_budget", "fit": replay["fit"]},
        )
        previous = baseline[dataset["dataset_id"]]
        current_objective = _objective(current)
        previous_objective = _objective(previous)
        objective_delta = (
            None
            if current_objective is None or previous_objective is None
            else float(current_objective - previous_objective)
        )
        current_age = current.get("normalized_age_mae")
        previous_age = previous.get("normalized_age_mae")
        age_delta = (
            None
            if current_age is None or previous_age is None
            else float(current_age - previous_age)
        )
        records.append(
            {
                "dataset_id": dataset["dataset_id"],
                "scenario": dataset["scenario"],
                "ntips": dataset["ntips"],
                "calibration": dataset["calibration"],
                "observation_model": dataset["observation_model"],
                "current": current,
                "previous": previous,
                "objective_delta": objective_delta,
                "normalized_age_mae_delta": age_delta,
                "cumulative_elapsed_seconds": float(
                    previous["elapsed_seconds"] + current["elapsed_seconds"]
                ),
            }
        )

    objective_deltas = [
        row["objective_delta"] for row in records if row["objective_delta"] is not None
    ]
    age_deltas = [
        row["normalized_age_mae_delta"]
        for row in records
        if row["normalized_age_mae_delta"] is not None
    ]
    checks = {
        "all_targets_converged": all(row["current"]["converged"] for row in records),
        "all_calibrations_valid": all(
            row["current"]["calibrations_valid"] for row in records
        ),
        "objective_noninferiority": bool(objective_deltas)
        and min(objective_deltas) >= -1e-6,
        "age_recovery_noninferiority": bool(age_deltas) and max(age_deltas) <= 0.005,
    }
    by_scenario = {}
    for scenario in sorted({row["scenario"] for row in records}):
        selected = [row for row in records if row["scenario"] == scenario]
        by_scenario[scenario] = {
            "datasets": len(selected),
            "convergence_fraction": _fraction(
                [row["current"]["converged"] for row in selected]
            ),
            "calibration_validity_fraction": _fraction(
                [row["current"]["calibrations_valid"] for row in selected]
            ),
            "normalized_age_mae": v17._summary_stats(
                [row["current"]["normalized_age_mae"] for row in selected]
            ),
            "replay_elapsed_seconds": v17._summary_stats(
                [row["current"]["elapsed_seconds"] for row in selected]
            ),
            "cumulative_elapsed_seconds": v17._summary_stats(
                [row["cumulative_elapsed_seconds"] for row in selected]
            ),
        }
    summary = {
        "checks": checks,
        "gates_passed": all(checks.values()),
        "targets": len(records),
        "remaining_failures": sum(
            not row["current"]["accuracy_eligible"] for row in records
        ),
        "minimum_objective_delta": (
            min(objective_deltas) if objective_deltas else None
        ),
        "maximum_age_mae_increase": max(age_deltas) if age_deltas else None,
        "by_scenario": by_scenario,
    }
    report = {
        "study_version": 17,
        "replay_schema": REPLAY_SCHEMA,
        "mode": mode,
        "diagnostic_only": True,
        "production_budget": PRODUCTION_BUDGET,
        "summary": summary,
        "records": records,
    }
    target = output_dir / f"failure-replay-v17-{mode}.json"
    v17._atomic_json(target, report)
    return report


def main() -> None:
    """Run or score the non-destructive failed-fit replay."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("pilot", "confirmation"), required=True)
    parser.add_argument("--stage", choices=("fit", "score", "all"), default="all")
    parser.add_argument("--ncores", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.ncores < 0:
        parser.error("--ncores must be non-negative")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")

    config = _read_json(v17.CONFIG_PATH)
    result = _read_json(args.output_dir / f"results-v17-{args.mode}.json")
    payloads = _payloads(result, config, args.output_dir, args.mode, limit=args.limit)
    if not payloads:
        raise RuntimeError("V17 contains no ineligible ToyTree fits to replay")
    if args.stage in {"fit", "all"}:
        ncores = (os.cpu_count() or 1) if args.ncores == 0 else args.ncores
        _run(payloads, max(1, min(int(ncores), len(payloads))))
    if args.stage in {"score", "all"}:
        report = _score(result, payloads, args.output_dir, args.mode)
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "fit_tasks": len(payloads),
                    "output": str(
                        args.output_dir / f"failure-replay-v17-{args.mode}.json"
                    ),
                    "gates_passed": report["summary"]["gates_passed"],
                    "diagnostic_only": True,
                }
            )
        )


if __name__ == "__main__":
    main()
