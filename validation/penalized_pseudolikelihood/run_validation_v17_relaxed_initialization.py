#!/usr/bin/env python

"""Replay the V17 relaxed pilot with data-informed clock initialization."""

# ruff: noqa: E402 -- thread limits must precede NumPy/SciPy imports.

from __future__ import annotations

import argparse
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
    run_validation_v17_benchmark as v17,
)

DEFAULT_OUTPUT = HERE / "v17"
REPLAY_SCHEMA = 1


def _read_json(path: Path) -> dict[str, Any]:
    """Read one JSON object."""
    return json.loads(path.read_text())


def _target_ids(result: dict[str, Any]) -> list[str]:
    """Return every relaxed dataset represented in a paired V17 result."""
    return sorted(
        {
            row["dataset_id"]
            for row in result["pairs"]
            if row["scenario"] == "relaxed_gamma_shape4"
        }
    )


def _cache_path(output_dir: Path, mode: str, dataset_id: str) -> Path:
    """Return the independent clock-initialized replay cache path."""
    return (
        output_dir
        / "cache-v17"
        / mode
        / "relaxed-clock-initialization"
        / f"{dataset_id}.json"
    )


def _payloads(
    result: dict[str, Any],
    config: dict[str, Any],
    output_dir: Path,
    mode: str,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Create fingerprinted relaxed replay tasks without touching V17 caches."""
    dataset_ids = _target_ids(result)
    if limit is not None:
        dataset_ids = dataset_ids[:limit]
    payloads = []
    for dataset_id in dataset_ids:
        manifest_path = v17._manifest_path(output_dir, mode, dataset_id)
        if not manifest_path.exists():
            raise RuntimeError(
                "V17 dataset caches are required for this replay; run it in the "
                f"checkout that produced the benchmark fits. Missing: {manifest_path}"
            )
        manifest = _read_json(manifest_path)
        fingerprint = v17._json_hash(
            {
                "schema": REPLAY_SCHEMA,
                "dataset_fingerprint": manifest["fingerprint"],
                "solver_hash": v17._solver_hash("relaxed"),
                "fit_options": config["fit"],
                "initialization": "profiled_clock_chronogram",
            }
        )
        payloads.append(
            {
                "dataset_id": dataset_id,
                "manifest_path": str(manifest_path),
                "cache_path": str(_cache_path(output_dir, mode, dataset_id)),
                "fit_options": config["fit"],
                "fingerprint": fingerprint,
            }
        )
    return payloads


def _worker(payload: dict[str, Any]) -> dict[str, Any]:
    """Fit one relaxed dataset using the current production implementation."""
    cache_path = Path(payload["cache_path"])
    if cache_path.exists():
        cached = _read_json(cache_path)
        if cached.get("fingerprint") != payload["fingerprint"]:
            raise RuntimeError(f"stale relaxed initialization cache: {cache_path}")
        return {"cache_path": str(cache_path), "resumed": True}
    dataset = _read_json(Path(payload["manifest_path"]))
    if dataset["fit_model"] != "relaxed":
        raise RuntimeError(f"unexpected replay model: {dataset['fit_model']!r}")
    fit = v17._fit_toytree(dataset, payload["fit_options"])
    record = {
        "replay_schema": REPLAY_SCHEMA,
        "dataset_id": payload["dataset_id"],
        "fingerprint": payload["fingerprint"],
        "fit": fit,
    }
    v17._atomic_json(cache_path, record)
    return {"cache_path": str(cache_path), "resumed": False}


def _run(payloads: list[dict[str, Any]], ncores: int) -> None:
    """Run independent replay fits in a global process pool."""
    started = time.perf_counter()
    completed = 0
    with ProcessPoolExecutor(max_workers=ncores) as pool:
        futures = {pool.submit(_worker, payload): payload for payload in payloads}
        for future in as_completed(futures):
            future.result()
            completed += 1
            print(
                json.dumps(
                    {
                        "event": "relaxed_initialization_fit_complete",
                        "completed": completed,
                        "total": len(payloads),
                        "elapsed_seconds": time.perf_counter() - started,
                    }
                ),
                flush=True,
            )


def _fraction(values: list[bool]) -> float | None:
    """Return a Boolean fraction or None for an empty collection."""
    return float(np.mean(values)) if values else None


def _paired_difference(
    records: list[dict[str, Any]],
    left: str,
    right: str,
    bootstrap_replicates: int,
    seed: int,
) -> dict[str, float | int | None]:
    """Bootstrap the mean paired normalized-age-MAE difference."""
    eligible = [
        row
        for row in records
        if row[left]["accuracy_eligible"] and row[right]["accuracy_eligible"]
    ]
    return v17._bootstrap_interval(
        eligible,
        lambda sample: float(
            np.mean(
                [
                    row[left]["normalized_age_mae"] - row[right]["normalized_age_mae"]
                    for row in sample
                ]
            )
        ),
        bootstrap_replicates,
        seed,
    )


def _score(
    result: dict[str, Any],
    payloads: list[dict[str, Any]],
    output_dir: Path,
    mode: str,
    bootstrap_replicates: int,
) -> dict[str, Any]:
    """Compare clock-initialized fits with frozen ToyTree and ape fits."""
    prior = {
        (row["dataset_id"], row["engine"]): row
        for row in result["rows"]
        if row["scenario"] == "relaxed_gamma_shape4"
    }
    records = []
    for payload in payloads:
        dataset = _read_json(Path(payload["manifest_path"]))
        replay = _read_json(Path(payload["cache_path"]))
        current = v17._score_fit(
            dataset,
            {
                "engine": "toytree_clock_initialized",
                "fit": replay["fit"],
            },
        )
        previous = prior[(dataset["dataset_id"], "toytree")]
        ape = prior[(dataset["dataset_id"], "ape")]
        current_objective = current["penalized_pseudologlik"]
        previous_objective = previous["penalized_pseudologlik"]
        ape_objective = ape["penalized_pseudologlik"]
        records.append(
            {
                "dataset_id": dataset["dataset_id"],
                "ntips": dataset["ntips"],
                "calibration": dataset["calibration"],
                "observation_model": dataset["observation_model"],
                "current": current,
                "previous": previous,
                "ape": ape,
                "current_minus_previous_objective": (
                    None
                    if current_objective is None or previous_objective is None
                    else float(current_objective - previous_objective)
                ),
                "current_minus_ape_objective": (
                    None
                    if current_objective is None or ape_objective is None
                    else float(current_objective - ape_objective)
                ),
            }
        )

    current_eligible = [row for row in records if row["current"]["accuracy_eligible"]]
    objective_improvements = [
        row["current_minus_previous_objective"]
        for row in records
        if row["current_minus_previous_objective"] is not None
    ]
    objective_vs_ape = [
        row["current_minus_ape_objective"]
        for row in records
        if row["current_minus_ape_objective"] is not None
    ]
    summary = {
        "datasets": len(records),
        "current_convergence_fraction": _fraction(
            [row["current"]["converged"] for row in records]
        ),
        "current_calibration_validity_fraction": _fraction(
            [row["current"]["calibrations_valid"] for row in records]
        ),
        "current_normalized_age_mae": v17._summary_stats(
            [row["current"]["normalized_age_mae"] for row in current_eligible]
        ),
        "previous_normalized_age_mae": v17._summary_stats(
            [
                row["previous"]["normalized_age_mae"]
                for row in records
                if row["previous"]["accuracy_eligible"]
            ]
        ),
        "ape_normalized_age_mae": v17._summary_stats(
            [
                row["ape"]["normalized_age_mae"]
                for row in records
                if row["ape"]["accuracy_eligible"]
            ]
        ),
        "current_minus_previous_objective": v17._summary_stats(objective_improvements),
        "current_minus_ape_objective": v17._summary_stats(objective_vs_ape),
        "objective_improved_over_previous_fraction": _fraction(
            [value > 1e-8 for value in objective_improvements]
        ),
        "objective_at_least_ape_fraction": _fraction(
            [value >= -1e-6 for value in objective_vs_ape]
        ),
        "age_mae_difference_vs_previous_bootstrap": _paired_difference(
            records,
            "current",
            "previous",
            bootstrap_replicates,
            17_100_001,
        ),
        "age_mae_difference_vs_ape_bootstrap": _paired_difference(
            records,
            "current",
            "ape",
            bootstrap_replicates,
            17_100_002,
        ),
    }
    report = {
        "study_version": 17,
        "replay_schema": REPLAY_SCHEMA,
        "mode": mode,
        "diagnostic_only": True,
        "fit_tasks": len(payloads),
        "summary": summary,
        "records": records,
    }
    target = output_dir / f"relaxed-initialization-v17-{mode}.json"
    v17._atomic_json(target, report)
    return report


def main() -> None:
    """Run or score the non-destructive relaxed initialization replay."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("pilot", "confirmation"), default="pilot")
    parser.add_argument("--stage", choices=("fit", "score", "all"), default="all")
    parser.add_argument("--ncores", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    config = _read_json(v17.CONFIG_PATH)
    result = _read_json(args.output_dir / f"results-v17-{args.mode}.json")
    payloads = _payloads(result, config, args.output_dir, args.mode, args.limit)
    if args.stage in {"fit", "all"}:
        ncores = (os.cpu_count() or 1) if args.ncores == 0 else args.ncores
        _run(payloads, max(1, min(int(ncores), len(payloads))))
    if args.stage in {"score", "all"}:
        bootstrap_replicates = int(config["modes"][args.mode]["bootstrap_replicates"])
        report = _score(
            result,
            payloads,
            args.output_dir,
            args.mode,
            bootstrap_replicates,
        )
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "fit_tasks": report["fit_tasks"],
                    "output": str(
                        args.output_dir / f"relaxed-initialization-v17-{args.mode}.json"
                    ),
                    "diagnostic_only": True,
                }
            )
        )


if __name__ == "__main__":
    main()
