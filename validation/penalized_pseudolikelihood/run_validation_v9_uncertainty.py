#!/usr/bin/env python

"""V9 task-parallel replay of correlated-model uncertainty failures.

This diagnostic schedules one process per held-tip lambda path across every
dataset and observation loss. The lambda sequence within a path remains serial
so its strong-to-weak warm starts retain their meaning.
"""

# ruff: noqa: E402 -- numerical thread limits must precede NumPy/SciPy imports.

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

for _thread_env in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ[_thread_env] = "1"

import numpy as np
import scipy

import toytree
from toytree.mod._src.penalized_pseudolikelihood.lambda_cv import (
    _assemble_correlated_cv_candidates,
    _complete_correlated_cv_problem,
    _fit_correlated_cv_path,
    _prepare_correlated_cv_problem,
)
from validation.penalized_pseudolikelihood.run_validation_v2 import (
    _scale_true_tree,
    _simulate_rates,
)
from validation.penalized_pseudolikelihood.run_validation_v5_identifiability import (
    _calibrations,
)
from validation.penalized_pseudolikelihood.run_validation_v6_reliability import (
    LOSS_SCORE,
    _bootstrap_support,
    _fit_full_path,
    _score_model,
    _score_record,
    _simulate_dataset,
    _slim_fit,
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v9.json"
CACHE_SCHEMA_VERSION = 1
EPS = 1e-12


def _json_default(value: Any) -> Any:
    """Convert NumPy scalars and paths at the cache serialization boundary."""
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _atomic_json(path: Path, value: Any) -> None:
    """Write JSON atomically so interrupted work never looks complete."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=_json_default) + "\n"
    )
    temporary.replace(path)


def _json_hash(value: Any) -> str:
    """Return a stable digest for JSON-compatible data."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _fit_source_hash() -> str:
    """Hash only implementation and simulation sources that affect fits."""
    digest = hashlib.sha256()
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    for name in ("correlated.py", "lambda_cv.py", "utils.py"):
        path = root / name
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    for function in (
        _scale_true_tree,
        _simulate_rates,
        _calibrations,
        _simulate_dataset,
        _fit_full_path,
        _slim_fit,
    ):
        digest.update(inspect.getsource(function).encode())
    return digest.hexdigest()


def _scoring_fingerprint(config: dict[str, Any], bootstrap_replicates: int) -> str:
    """Hash scoring independently so scoring edits never stale fit caches."""
    return _json_hash(
        {
            "bootstrap_replicates": int(bootstrap_replicates),
            "bootstrap_seed": int(config["bootstrap_seed"]),
            "decision_gates": config["decision_gates"],
            "sources": [
                inspect.getsource(function)
                for function in (
                    _bootstrap_support,
                    _score_model,
                    _score_record,
                    _summarize_v9,
                )
            ],
        }
    )


def _environment() -> dict[str, Any]:
    """Return compact software and platform provenance."""
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "toytree": getattr(toytree, "__version__", "unknown"),
    }


def _effective_workers(ncores: int, pending_tasks: int) -> int:
    """Return the number of global workers used by one task phase."""
    return min(int(ncores), int(pending_tasks)) if pending_tasks else 0


def _cache_matches(path: Path, fingerprint: str) -> bool:
    """Return whether a task cache is complete and fingerprint-compatible."""
    if not path.exists():
        return False
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    return value.get("fingerprint") == fingerprint and value.get("status") == "ok"


def _dataset_fingerprint(
    spec: dict[str, Any],
    loss: str,
    lambdas: list[float],
    fit: dict[str, Any],
    noise: dict[str, Any],
    source_hash: str,
) -> str:
    """Return a fit-only fingerprint for one dataset and loss."""
    return _json_hash(
        {
            "cache_schema_version": CACHE_SCHEMA_VERSION,
            "spec": spec,
            "observation_loss": loss,
            "lambdas": [float(value) for value in lambdas],
            "fit": fit,
            "noise": noise,
            "source_hash": source_hash,
        }
    )


def _context_name(spec: dict[str, Any]) -> str:
    """Return a filesystem-safe deterministic dataset label."""
    return "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in str(spec["name"])
    )


def _build_contexts(
    config: dict[str, Any], mode: str, output_dir: Path
) -> list[dict[str, Any]]:
    """Simulate datasets and prepare all independent CV path problems."""
    source_hash = _fit_source_hash()
    contexts = []
    for spec in config["modes"][mode]:
        true_tree, observed_tree, true_rates, true_means, observed = _simulate_dataset(
            int(spec["ntips"]),
            float(spec["rate_sigma"]),
            str(spec["noise_model"]),
            int(spec["seed"]),
            config,
        )
        calibrations = _calibrations(true_tree, str(spec["calibration"]))
        lambdas = [float(value) for value in spec.get("lambdas", config["lambdas"])]
        for loss_index, loss in enumerate(config["observation_losses"]):
            seed = int(spec["seed"])
            problem = _prepare_correlated_cv_problem(
                tree=observed_tree,
                lambdas=lambdas,
                calibrations=calibrations,
                max_iter=int(config["fit"]["max_iter"]),
                max_fun=int(config["fit"]["max_fun"]),
                max_refine=int(config["fit"]["max_refine"]),
                nstarts=int(config["fit"]["nstarts"]),
                seed=seed + loss_index * 1_000_003,
                observation_loss=str(loss),
            )
            fingerprint = _dataset_fingerprint(
                spec,
                str(loss),
                lambdas,
                config["fit"],
                config["noise"],
                source_hash,
            )
            cache_root = (
                output_dir / "cache-v9" / mode / _context_name(spec) / str(loss)
            )
            contexts.append(
                {
                    "mode": mode,
                    "spec": spec,
                    "loss": str(loss),
                    "loss_index": loss_index,
                    "fingerprint": fingerprint,
                    "cache_root": cache_root,
                    "true_tree": true_tree,
                    "observed_tree": observed_tree,
                    "true_rates": true_rates,
                    "true_means": true_means,
                    "observed": observed,
                    "calibrations": calibrations,
                    "lambdas": lambdas,
                    "problem": problem,
                }
            )
    return contexts


def _fold_tasks(contexts: list[dict[str, Any]], resume: bool) -> list[dict[str, Any]]:
    """Return one cacheable worker task per dataset-loss held-tip path."""
    tasks = []
    for context_index, context in enumerate(contexts):
        for fold, path in enumerate(context["problem"]["paths"]):
            tasks.append(
                {
                    "kind": "fold_path",
                    "context_index": context_index,
                    "fold": fold,
                    "path": path,
                    "cache_path": str(
                        context["cache_root"] / "folds" / f"fold-{fold:04d}.json"
                    ),
                    "fingerprint": _json_hash(
                        {
                            "dataset": context["fingerprint"],
                            "kind": "fold_path",
                            "fold": fold,
                        }
                    ),
                    "resume": resume,
                }
            )
    return tasks


def _fit_fold_task(task: dict[str, Any]) -> str:
    """Fit and atomically cache one complete strong-to-weak lambda path."""
    path = Path(task["cache_path"])
    if task["resume"] and _cache_matches(path, task["fingerprint"]):
        return str(path)
    try:
        results = _fit_correlated_cv_path(task["path"])
        value = {
            "status": "ok",
            "fingerprint": task["fingerprint"],
            "context_index": int(task["context_index"]),
            "fold": int(task["fold"]),
            "results": results,
        }
    except Exception as exc:
        value = {
            "status": "error",
            "fingerprint": task["fingerprint"],
            "context_index": int(task["context_index"]),
            "fold": int(task["fold"]),
            "message": f"{type(exc).__name__}: {exc}",
        }
    _atomic_json(path, value)
    return str(path)


def _read_fold_results(
    context: dict[str, Any], fold_tasks: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Return fingerprint-checked fold results for one context."""
    results = []
    for task in fold_tasks:
        path = Path(task["cache_path"])
        if not _cache_matches(path, task["fingerprint"]):
            raise RuntimeError(f"missing or stale task cache: {path}")
        value = json.loads(path.read_text())
        if value.get("status") != "ok":
            raise RuntimeError(f"failed fold task {path}: {value.get('message', '')}")
        results.extend(value["results"])
    expected = len(context["problem"]["paths"]) * len(context["lambdas"])
    if len(results) != expected:
        raise RuntimeError(
            f"fold cache count mismatch: expected {expected}, observed {len(results)}"
        )
    return results


def _postfit_tasks(
    contexts: list[dict[str, Any]],
    grouped_folds: dict[int, list[dict[str, Any]]],
    resume: bool,
    fit_options: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return independent selected-fit and full-grid path tasks."""
    tasks = []
    for context_index, context in enumerate(contexts):
        fold_results = _read_fold_results(context, grouped_folds[context_index])
        for kind in ("selected", "full_grid"):
            tasks.append(
                {
                    "kind": kind,
                    "context_index": context_index,
                    "cache_path": str(context["cache_root"] / f"{kind}.json"),
                    "fingerprint": _json_hash(
                        {"dataset": context["fingerprint"], "kind": kind}
                    ),
                    "resume": resume,
                    "problem": context["problem"],
                    "fold_results": fold_results,
                    "tree": context["observed_tree"],
                    "lambdas": context["lambdas"],
                    "calibrations": context["calibrations"],
                    "loss": context["loss"],
                    "fit_options": fit_options,
                    "seed": int(context["spec"]["seed"])
                    + int(context["loss_index"]) * 2_000_003,
                }
            )
    return tasks


def _fit_postfit_task(task: dict[str, Any]) -> str:
    """Fit either the independently safeguarded selection or full grid."""
    path = Path(task["cache_path"])
    if task["resume"] and _cache_matches(path, task["fingerprint"]):
        return str(path)
    value: dict[str, Any] = {
        "fingerprint": task["fingerprint"],
        "context_index": int(task["context_index"]),
        "kind": task["kind"],
    }
    try:
        if task["kind"] == "selected":
            result = _complete_correlated_cv_problem(
                task["problem"], task["fold_results"], ncores=1
            )
            value.update(
                {
                    "status": "ok",
                    "selected_lam": float(result["selected_lam"]),
                    "selected_at_boundary": bool(result["selected_at_boundary"]),
                    "mean_score": float(result["mean_score"]),
                    "standard_error": float(result["standard_error"]),
                    "selected_fit": _slim_fit(result["selected_fit"]),
                    "final_fit_path": result["final_fit_path"],
                }
            )
        elif task["kind"] == "full_grid":
            fits = _fit_full_path(
                task["tree"],
                task["lambdas"],
                task["calibrations"],
                task["loss"],
                task["fit_options"],
                int(task["seed"]),
            )
            value.update({"status": "ok", "full_fits": fits})
        else:  # pragma: no cover - tasks are built internally
            raise ValueError(f"unknown post-fit task: {task['kind']}")
    except Exception as exc:
        value.update({"status": "error", "message": f"{type(exc).__name__}: {exc}"})
    _atomic_json(path, value)
    return str(path)


def _run_tasks(
    tasks: list[dict[str, Any]],
    worker: Callable[[dict[str, Any]], str],
    ncores: int,
    phase: str,
) -> list[Path]:
    """Run one globally pooled task phase with resume and ETA reporting."""
    cached = [
        task
        for task in tasks
        if task["resume"]
        and _cache_matches(Path(task["cache_path"]), task["fingerprint"])
    ]
    cached_paths = {task["cache_path"] for task in cached}
    pending = [task for task in tasks if task["cache_path"] not in cached_paths]
    workers = _effective_workers(ncores, len(pending))
    print(
        json.dumps(
            {
                "event": "phase_start",
                "phase": phase,
                "tasks": len(tasks),
                "cached": len(cached),
                "pending": len(pending),
                "requested_cores": int(ncores),
                "worker_processes": workers,
            }
        ),
        flush=True,
    )
    paths = [Path(task["cache_path"]) for task in cached]
    if not pending:
        return sorted(paths)
    started = time.monotonic()

    def report(completed: int, result: str) -> None:
        elapsed = time.monotonic() - started
        eta = elapsed / completed * (len(pending) - completed) if completed else None
        print(
            json.dumps(
                {
                    "event": "task_complete",
                    "phase": phase,
                    "completed": completed,
                    "total": len(pending),
                    "elapsed_seconds": elapsed,
                    "estimated_remaining_seconds": eta,
                    "cache": result,
                }
            ),
            flush=True,
        )

    if workers == 1:
        for completed, task in enumerate(pending, 1):
            result = worker(task)
            paths.append(Path(result))
            report(completed, result)
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(worker, task) for task in pending]
            for completed, future in enumerate(as_completed(futures), 1):
                result = future.result()
                paths.append(Path(result))
                report(completed, result)
    return sorted(paths)


def _group_fold_tasks(
    tasks: list[dict[str, Any]], contexts: list[dict[str, Any]]
) -> dict[int, list[dict[str, Any]]]:
    """Group task metadata by context in stable fold order."""
    grouped = {index: [] for index in range(len(contexts))}
    for task in tasks:
        grouped[int(task["context_index"])].append(task)
    for values in grouped.values():
        values.sort(key=lambda task: int(task["fold"]))
    return grouped


def _read_task(path: Path, fingerprint: str) -> dict[str, Any]:
    """Read one required post-fit cache after validating its fingerprint."""
    if not _cache_matches(path, fingerprint):
        raise RuntimeError(f"missing or stale task cache: {path}")
    value = json.loads(path.read_text())
    if value.get("status") != "ok":
        raise RuntimeError(f"failed task {path}: {value.get('message', '')}")
    return value


def _slim_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Retain the fold diagnostics consumed by the cache-only scorer."""
    return {
        "lam": float(candidate["lam"]),
        "valid": bool(candidate["valid"]),
        "stable": bool(candidate.get("stable", False)),
        "mean_score": float(candidate["mean_score"]),
        "standard_error": float(candidate["standard_error"]),
        "folds": [
            {
                "fold": int(fold["fold"]),
                "edge_index": int(fold["edge_index"]),
                "observed": float(fold["observed"]),
                "predicted": float(fold["predicted"]),
                "score": float(fold["score"]),
                "converged": bool(fold["converged"]),
                "optimizer_message": str(fold.get("optimizer_message", "")),
                "optimizer_retries": int(fold.get("optimizer_retries", 0)),
                "stability_assessed": bool(fold.get("stability_assessed", False)),
                "solution_stable": fold.get("solution_stable"),
                "max_near_optimal_age_difference": fold.get(
                    "max_near_optimal_age_difference"
                ),
            }
            for fold in candidate["folds"]
        ],
    }


def _build_records(
    contexts: list[dict[str, Any]],
    grouped_folds: dict[int, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Assemble paired-loss V6-compatible records entirely from task caches."""
    records_by_name: dict[str, dict[str, Any]] = {}
    for context_index, context in enumerate(contexts):
        spec = context["spec"]
        name = str(spec["name"])
        if name not in records_by_name:
            records_by_name[name] = {
                "status": "ok",
                "mode": context["mode"],
                "scenario": name,
                "ntips": int(spec["ntips"]),
                "calibration": str(spec["calibration"]),
                "rate_sigma": float(spec["rate_sigma"]),
                "noise_model": str(spec["noise_model"]),
                "replicate": 0,
                "seed": int(spec["seed"]),
                "true_ages": context["true_tree"]
                .get_node_data("height")
                .to_numpy(dtype=float)
                .tolist(),
                "true_rates": context["true_rates"].tolist(),
                "true_means": context["true_means"].tolist(),
                "observed": context["observed"].tolist(),
                "models": {},
            }
        record = records_by_name[name]
        try:
            fold_results = _read_fold_results(context, grouped_folds[context_index])
            selection = _assemble_correlated_cv_candidates(
                context["problem"], fold_results
            )
            selected_path = context["cache_root"] / "selected.json"
            full_path = context["cache_root"] / "full_grid.json"
            selected = _read_task(
                selected_path,
                _json_hash({"dataset": context["fingerprint"], "kind": "selected"}),
            )
            full = _read_task(
                full_path,
                _json_hash({"dataset": context["fingerprint"], "kind": "full_grid"}),
            )
            selected_lam = float(selected["selected_lam"])
            full_fits = full["full_fits"]
            label = str(selected_lam)
            record["models"][context["loss"]] = {
                "selected_lam": selected_lam,
                "selected_fit": selected["selected_fit"],
                "full_fits": full_fits,
                "candidates": [
                    _slim_candidate(candidate) for candidate in selection["candidates"]
                ],
                "warm_cold_objective_delta": float(
                    selected["selected_fit"]["penalized_pseudologlik"]
                    - full_fits[label]["penalized_pseudologlik"]
                ),
            }
        except Exception as exc:
            record["status"] = "error"
            record["message"] = f"{type(exc).__name__}: {exc}"
    return [records_by_name[key] for key in sorted(records_by_name)]


def _score_records(
    records: list[dict[str, Any]],
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> list[dict[str, Any]]:
    """Score records and annotate validity of every supported full-grid fit."""
    rows = []
    for record in records:
        row = _score_record(record, bootstrap_replicates, bootstrap_seed)
        if row.get("status") == "ok":
            for loss in LOSS_SCORE:
                raw = record["models"][loss]
                candidates = {
                    float(value["lam"]): bool(value["valid"])
                    for value in raw["candidates"]
                }
                supported = row["models"][loss]["bootstrap"]["supported_lambdas"]
                row["models"][loss]["all_supported_lambdas_valid"] = all(
                    candidates.get(float(lam), False)
                    and raw["full_fits"][str(float(lam))]["converged"]
                    and raw["full_fits"][str(float(lam))].get("solution_stable") is True
                    for lam in supported
                )
        rows.append(row)
    return rows


def _finite(values: list[Any]) -> np.ndarray:
    """Return the finite numeric values from a collection."""
    return np.asarray(
        [float(value) for value in values if value is not None and np.isfinite(value)],
        dtype=float,
    )


def _summarize_v9(rows: list[dict[str, Any]], gates: dict[str, Any]) -> dict[str, Any]:
    """Summarize replay behavior and apply the prespecified Gamma gates."""
    successful = [row for row in rows if row.get("status") == "ok"]
    losses = {}
    for loss in LOSS_SCORE:
        models = [row["models"][loss] for row in successful]
        ratios = _finite([model["selected_age_oracle_ratio"] for model in models])
        uncertainties = _finite(
            [
                model["bootstrap"]["maximum_total_normalized_age_uncertainty"]
                for model in models
            ]
        )
        losses[loss] = {
            "datasets": len(models),
            "selected_fit_stability": (
                float(np.mean([model["selected_fit_stable"] for model in models]))
                if models
                else 0.0
            ),
            "selected_fit_objective_competitiveness": (
                float(
                    np.mean(
                        [
                            model["selected_fit_objective_competitive"]
                            for model in models
                        ]
                    )
                )
                if models
                else 0.0
            ),
            "all_supported_lambdas_valid": bool(
                models and all(model["all_supported_lambdas_valid"] for model in models)
            ),
            "minimum_valid_candidates": min(
                (model["valid_candidates"] for model in models), default=0
            ),
            "maximum_total_age_uncertainty": (
                float(np.max(uncertainties)) if uncertainties.size else None
            ),
            "total_age_uncertainty_median": (
                float(np.median(uncertainties)) if uncertainties.size else None
            ),
            "total_age_uncertainty_p90": (
                float(np.quantile(uncertainties, 0.9)) if uncertainties.size else None
            ),
            "selected_age_oracle_ratio_median": (
                float(np.median(ratios)) if ratios.size else None
            ),
            "selected_age_oracle_ratio_p90": (
                float(np.quantile(ratios, 0.9)) if ratios.size else None
            ),
            "fold_stability": (
                float(
                    sum(model["folds_stable"] for model in models)
                    / max(sum(model["folds_total"] for model in models), 1)
                )
                if models
                else 0.0
            ),
        }

    gamma = losses["multiplicative_gamma"]
    selected_stable = (
        gamma["selected_fit_stability"] == 1.0
        and gamma["selected_fit_objective_competitiveness"] == 1.0
    )
    checks = {
        "gamma_all_selected_fits_stable": bool(selected_stable),
        "gamma_all_supported_lambdas_valid": bool(gamma["all_supported_lambdas_valid"]),
        "gamma_minimum_valid_candidates": bool(
            gamma["minimum_valid_candidates"]
            >= int(gates["gamma_minimum_valid_candidates"])
        ),
        "gamma_maximum_total_age_uncertainty": bool(
            gamma["maximum_total_age_uncertainty"] is not None
            and gamma["maximum_total_age_uncertainty"]
            <= float(gates["gamma_maximum_total_age_uncertainty"])
        ),
        "gamma_selected_age_oracle_ratio_median": bool(
            gamma["selected_age_oracle_ratio_median"] is not None
            and gamma["selected_age_oracle_ratio_median"]
            <= float(gates["gamma_selected_age_oracle_ratio_median"])
        ),
        "gamma_selected_age_oracle_ratio_p90": bool(
            gamma["selected_age_oracle_ratio_p90"] is not None
            and gamma["selected_age_oracle_ratio_p90"]
            <= float(gates["gamma_selected_age_oracle_ratio_p90"])
        ),
    }
    return {
        "datasets": len(rows),
        "successful_datasets": len(successful),
        "losses": losses,
        "checks": checks,
        "gates_passed": bool(len(successful) == len(rows) and all(checks.values())),
    }


def _combined_v6_v9_descriptive(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Combine comparable current-estimator replay rows for context, not gates."""
    sources: list[tuple[str, list[dict[str, Any]]]] = [("v9", rows)]
    v6_path = HERE / "v6" / "results-v6-stability-stress.json"
    if v6_path.exists():
        value = json.loads(v6_path.read_text())
        sources.append(("v6-stability-stress", value.get("datasets", [])))
    result: dict[str, Any] = {"sources": [name for name, _ in sources], "losses": {}}
    for loss in LOSS_SCORE:
        values = _finite(
            [
                row["models"][loss]["bootstrap"][
                    "maximum_total_normalized_age_uncertainty"
                ]
                for _, source_rows in sources
                for row in source_rows
                if row.get("status") == "ok" and loss in row.get("models", {})
            ]
        )
        result["losses"][loss] = {
            "datasets": int(values.size),
            "median": float(np.median(values)) if values.size else None,
            "p90": float(np.quantile(values, 0.9)) if values.size else None,
            "maximum": float(np.max(values)) if values.size else None,
        }
    result["release_gating"] = False
    return result


def _fit_options(config: dict[str, Any]) -> dict[str, Any]:
    """Return serial options for each independently scheduled full path."""
    return {
        "max_iter": int(config["fit"]["max_iter"]),
        "max_fun": int(config["fit"]["max_fun"]),
        "max_refine": int(config["fit"]["max_refine"]),
        "nstarts": int(config["fit"]["nstarts"]),
        "ncores": 1,
        "_retry_multiplier": int(config["fit"]["retry_multiplier"]),
    }


def main() -> None:
    """Run fit and/or cache-only scoring for the V9 replay."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("smoke", "uncertainty-replay"), default="smoke"
    )
    parser.add_argument("--stage", choices=("all", "fit", "score"), default="all")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE / "v9")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--bootstrap-replicates", type=int)
    args = parser.parse_args()
    if args.ncores < 1:
        parser.error("--ncores must be positive")

    config = json.loads(CONFIG_PATH.read_text())
    bootstrap_replicates = (
        int(config["bootstrap_replicates"])
        if args.bootstrap_replicates is None
        else int(args.bootstrap_replicates)
    )
    if bootstrap_replicates < 1:
        parser.error("--bootstrap-replicates must be positive")

    contexts = _build_contexts(config, args.mode, args.output_dir)
    resume = not args.no_resume
    fold_tasks = _fold_tasks(contexts, resume)
    grouped_folds = _group_fold_tasks(fold_tasks, contexts)
    postfit_tasks = (
        _postfit_tasks(
            contexts,
            grouped_folds,
            resume,
            _fit_options(config),
        )
        if all(
            _cache_matches(Path(task["cache_path"]), task["fingerprint"])
            for task in fold_tasks
        )
        else []
    )

    if args.stage in {"all", "fit"}:
        _run_tasks(fold_tasks, _fit_fold_task, args.ncores, "held_tip_paths")
        postfit_tasks = _postfit_tasks(
            contexts,
            grouped_folds,
            resume,
            _fit_options(config),
        )
        _run_tasks(
            postfit_tasks,
            _fit_postfit_task,
            args.ncores,
            "selected_and_full_paths",
        )
    if args.stage == "fit":
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "datasets": len(config["modes"][args.mode]),
                    "fold_path_tasks": len(fold_tasks),
                    "postfit_tasks": len(postfit_tasks),
                }
            )
        )
        return

    if not postfit_tasks:
        postfit_tasks = _postfit_tasks(
            contexts,
            grouped_folds,
            True,
            _fit_options(config),
        )
    records = _build_records(contexts, grouped_folds)
    rows = _score_records(
        records,
        bootstrap_replicates,
        int(config["bootstrap_seed"]),
    )
    summary = _summarize_v9(rows, config["decision_gates"])
    result = {
        "study_version": int(config["study_version"]),
        "mode": args.mode,
        "scope": "correlated_lambda_uncertainty_replay",
        "diagnostic_only": True,
        "release_eligible": False,
        "changes_public_api": False,
        "sequence_length_input": False,
        "selection_method": "leave_one_terminal_edge_out",
        "parallelism": {
            "unit": "held_tip_lambda_path",
            "lambda_path_order": "strong_to_weak_serial",
            "fold_path_tasks": len(fold_tasks),
            "postfit_tasks": len(postfit_tasks),
            "requested_cores": int(args.ncores),
        },
        "fit_source_hash": _fit_source_hash(),
        "scoring_fingerprint": _scoring_fingerprint(config, bootstrap_replicates),
        "bootstrap_replicates": bootstrap_replicates,
        "datasets": rows,
        "summary": summary,
        "combined_current_estimator_descriptive": _combined_v6_v9_descriptive(rows),
        "all_release_gates_passed": False,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / f"results-v9-{args.mode}.json"
    environment_path = args.output_dir / f"environment-v9-{args.mode}.json"
    seeds_path = args.output_dir / f"seeds-v9-{args.mode}.json"
    _atomic_json(result_path, result)
    _atomic_json(environment_path, _environment())
    _atomic_json(
        seeds_path,
        [
            {
                key: spec[key]
                for key in (
                    "name",
                    "ntips",
                    "calibration",
                    "rate_sigma",
                    "noise_model",
                    "seed",
                )
            }
            for spec in config["modes"][args.mode]
        ],
    )
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(rows),
                "output": str(result_path),
                "gates_passed": summary["gates_passed"],
                "diagnostic_only": True,
            }
        )
    )


if __name__ == "__main__":
    main()
