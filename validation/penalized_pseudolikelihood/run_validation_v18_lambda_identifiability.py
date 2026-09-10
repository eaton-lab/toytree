#!/usr/bin/env python
"""V18 matched per-tree lambda-CV validation for correlated and UCLN models."""

# ruff: noqa: E402 -- numerical thread limits precede NumPy/SciPy imports.
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import platform
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

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

import toytree
from toytree.mod._src.penalized_pseudolikelihood.correlated import (
    edges_make_ultrametric_correlated,
)
from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    _edges_make_ultrametric_ucln,
)
from validation.penalized_pseudolikelihood.run_validation_v2 import (
    _scale_true_tree,
    _simulate_rates,
)

toytree.set_log_level("WARNING")
CONFIG_PATH = HERE / "config-v18.json"
DEFAULT_OUTPUT = HERE / "v18"
FIT_CACHE_SCHEMA = 1
RESULT_SCHEMA = 1
EPS = 1e-12
MODELS = ("correlated", "uncorrelated_lognormal")


def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=_json_default) + "\n"
    )
    temporary.replace(path)


def _json_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _function_hash(*functions: Callable[..., Any]) -> str:
    digest = hashlib.sha256()
    for function in functions:
        digest.update(function.__name__.encode())
        digest.update(inspect.getsource(function).encode())
    return digest.hexdigest()


def _fit_source_hash(config: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    for name in ("correlated.py", "uncorrelated_lognormal.py", "utils.py"):
        source = root / name
        digest.update(source.name.encode())
        digest.update(source.read_bytes())
    digest.update(
        _function_hash(
            _calibrations, _simulate, _fit_one, _fit_lambda_path, _fit_task
        ).encode()
    )
    digest.update(
        json.dumps(
            {
                "fit": config["fit"],
                "simulation": config["simulation"],
                "lambdas": config["lambdas"],
                "schema": FIT_CACHE_SCHEMA,
            },
            sort_keys=True,
        ).encode()
    )
    return digest.hexdigest()


def _scoring_hash(config: dict[str, Any], bootstrap_replicates: int) -> str:
    return _json_hash(
        {
            "bootstrap_replicates": int(bootstrap_replicates),
            "bootstrap_seed": int(config["bootstrap_seed"]),
            "decision_gates": config["decision_gates"],
            "sources": _function_hash(
                _select_index,
                _bootstrap_fold_selection,
                _score_context,
                _summarize,
            ),
        }
    )


def _environment() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "toytree": getattr(toytree, "__version__", "unknown"),
    }


def _matched_lambda(sigma_log: float) -> float:
    sigma = float(sigma_log)
    if not np.isfinite(sigma) or sigma <= 0.0:
        raise ValueError("sigma_log must be finite and positive")
    return float(1.0 / (2.0 * sigma * sigma))


def _calibrations(tree: Any, regime: str) -> dict[int, Any]:
    result: dict[int, Any] = {-1: 1.0}
    if regime == "root":
        return result
    if regime != "root_and_three_internal_intervals":
        raise ValueError(f"unknown calibration regime: {regime}")
    candidates = [
        node
        for node in tree[tree.ntips : -1]
        if not node.is_leaf() and not node.is_root()
    ]
    if len(candidates) < 3:
        raise ValueError("three internal calibrations require at least three nodes")
    root_age = float(tree[-1].height)
    chosen: list[Any] = []
    for target in (0.25, 0.5, 0.75):
        available = [node for node in candidates if node not in chosen]
        node = min(
            available,
            key=lambda item: (abs(float(item.height) / root_age - target), item.idx),
        )
        chosen.append(node)
    for node in chosen:
        age = float(node.height)
        result[int(node.idx)] = (0.9 * age, 1.1 * age)
    return result


def _calibration_records(values: dict[int, Any]) -> list[dict[str, float]]:
    records = []
    for key, value in sorted(values.items()):
        lower, upper = (value, value) if np.isscalar(value) else value
        records.append({"idx": int(key), "lower": float(lower), "upper": float(upper)})
    return records


def _resolve_calibrations(records: list[dict[str, float]]) -> dict[int, Any]:
    result = {}
    for record in records:
        lower, upper = float(record["lower"]), float(record["upper"])
        result[int(record["idx"])] = lower if lower == upper else (lower, upper)
    return result


def _simulate(spec: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    tree = _scale_true_tree(int(spec["ntips"]), int(spec["topology_seed"]))
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    ages = tree.get_node_data("height").to_numpy(dtype=float)
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    sigma = float(spec["sigma_log"])
    baseline = float(config["simulation"]["baseline_rate"])
    rate_rng = np.random.default_rng(int(spec["rate_seed"]))
    if spec["model"] == "correlated":
        rates = _simulate_rates(
            tree,
            "correlated",
            rate_rng,
            {"baseline_rate": baseline, "correlated_log_sigma": sigma},
        )
    elif spec["model"] == "uncorrelated_lognormal":
        log_rates = rate_rng.normal(0.0, sigma, size=tree.nedges)
        rates = baseline * np.exp(log_rates - float(np.mean(log_rates)))
    else:
        raise ValueError(f"unknown model: {spec['model']}")
    expected = times * rates
    observation_model = str(spec["observation_model"])
    if observation_model == "expected_branch":
        observed = expected.copy()
    elif observation_model == "continuous_gamma":
        shape = float(config["simulation"]["observation_gamma_shape"])
        multiplier = np.random.default_rng(int(spec["observation_seed"])).gamma(
            shape, 1.0 / shape, size=tree.nedges
        )
        observed = expected * multiplier
    else:
        raise ValueError(f"unknown observation model: {observation_model}")
    observed_tree = tree.set_node_data(
        "dist",
        {int(child): float(observed[idx]) for idx, (child, _) in enumerate(edges)},
        inplace=False,
    )
    return {
        "true_tree": tree,
        "observed_tree": observed_tree,
        "true_ages": ages,
        "true_rates": np.asarray(rates, dtype=float),
        "expected": np.asarray(expected, dtype=float),
        "observed": np.asarray(observed, dtype=float),
        "calibrations": _calibrations(tree, str(spec["calibration"])),
    }


def _mode_seed(config: dict[str, Any], mode: str) -> int:
    if mode == "smoke":
        return int(config["development_seed"]) - 10_000_000
    if mode == "pilot":
        return int(config["development_seed"])
    if mode == "confirmation":
        return int(config["confirmation_seed"])
    raise ValueError(f"unknown mode: {mode}")


def _build_specs(config: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    design = config["modes"][mode]
    root_seed = _mode_seed(config, mode)
    specs = []
    pair = 0
    for ntips in design["ntips"]:
        for sigma in design["sigma_log"]:
            for calibration in design["calibrations"]:
                for observation in design["observation_models"]:
                    for replicate in range(int(design["replicates"])):
                        shared = {
                            "pair_id": pair,
                            "ntips": int(ntips),
                            "sigma_log": float(sigma),
                            "matched_lambda": _matched_lambda(float(sigma)),
                            "calibration": str(calibration),
                            "observation_model": str(observation),
                            "replicate": replicate,
                            "topology_seed": root_seed + pair * 10_007 + 11,
                            "rate_seed": root_seed + pair * 10_007 + 23,
                            "observation_seed": root_seed + pair * 10_007 + 37,
                        }
                        for model_index, model in enumerate(MODELS):
                            name = (
                                f"{model}-n{ntips}-{calibration}-{observation}-"
                                f"sigma{float(sigma):g}-r{replicate:04d}"
                            ).replace(".", "p")
                            specs.append(
                                {
                                    **shared,
                                    "dataset_id": name,
                                    "model": model,
                                    "fit_seed": root_seed
                                    + pair * 10_007
                                    + 101
                                    + model_index,
                                }
                            )
                        pair += 1
    return specs


def _slim_fit(fit: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": str(fit["model"]),
        "lam": float(fit["lam"]),
        "converged": bool(fit["converged"]),
        "solution_stable": fit.get("solution_stable"),
        "stability_assessed": bool(fit.get("stability_assessed", False)),
        "optimizer_message": str(fit.get("optimizer_message", "")),
        "optimizer_retries": int(fit.get("optimizer_retries", 0)),
        "best_start_kind": str(fit.get("best_start_kind", "")),
        "ages": fit["tree"].get_node_data("height").to_numpy(dtype=float).tolist(),
        "rates": [float(value) for value in fit["rates"]],
        "expected_branch_lengths": [
            float(value) for value in fit["expected_branch_lengths"]
        ],
        "pseudologlik": float(fit["pseudologlik"]),
        "penalized_pseudologlik": float(fit["penalized_pseudologlik"]),
        "penalty": float(fit["penalty"]),
        "max_near_optimal_age_difference": fit.get("max_near_optimal_age_difference"),
    }


def _fit_one(
    model: str,
    tree: Any,
    lam: float,
    calibrations: dict[int, Any],
    mask: np.ndarray,
    fit_options: dict[str, Any],
    seed: int,
    initial_rates: list[float] | None,
    initial_ages: list[float] | None,
) -> dict[str, Any]:
    options = {
        "lam": float(lam),
        "calibrations": calibrations,
        "full": True,
        "inplace": False,
        "max_iter": int(fit_options["max_iter"]),
        "max_fun": int(fit_options["max_fun"]),
        "max_refine": int(fit_options["max_refine"]),
        "nstarts": int(fit_options["nstarts"]),
        "ncores": 1,
        "seed": int(seed),
        "_observation_mask": mask,
        "_retry_multiplier": int(fit_options["retry_multiplier"]),
        "_initial_rates": initial_rates,
        "_initial_ages": initial_ages,
    }
    if model == "correlated":
        fit = edges_make_ultrametric_correlated(tree, **options)
    elif model == "uncorrelated_lognormal":
        fit = _edges_make_ultrametric_ucln(tree, **options)
    else:
        raise ValueError(f"unknown model: {model}")
    return _slim_fit(fit)


def _prediction_score(observed: float, predicted: float) -> float:
    expected = max(float(predicted), EPS)
    value = max(float(observed), EPS)
    return float((value - expected) ** 2 / expected)


def _fit_lambda_path(task: dict[str, Any]) -> list[dict[str, Any]]:
    tree = toytree.tree(task["observed_tree_newick"])
    calibrations = _resolve_calibrations(task["calibrations"])
    observed = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    held_edge = task.get("held_edge")
    mask = np.ones(tree.nedges, dtype=bool)
    fit_tree = tree
    if held_edge is not None:
        held_edge = int(held_edge)
        mask[held_edge] = False
        positive = observed[mask][observed[mask] > 0.0]
        replacement = float(np.median(positive)) if positive.size else 1.0
        fit_tree = tree.set_node_data(
            "dist", {int(edges[held_edge, 0]): replacement}, inplace=False
        )
    warm_rates = None
    warm_ages = None
    results = []
    grid = [float(value) for value in task["lambdas"]]
    for rank, lam in enumerate(sorted(grid, reverse=True)):
        candidate_index = grid.index(lam)
        try:
            fit = _fit_one(
                str(task["model"]),
                fit_tree,
                lam,
                calibrations,
                mask,
                task["fit_options"],
                int(task["fit_seed"]) + candidate_index * 1_000_003,
                warm_rates,
                warm_ages,
            )
            stable = bool(fit["converged"] and fit.get("solution_stable") is True)
            record = {
                "candidate_index": candidate_index,
                "path_rank": rank,
                "lam": lam,
                "valid": stable,
                "fit": fit,
            }
            if held_edge is not None:
                predicted = float(fit["expected_branch_lengths"][held_edge])
                record.update(
                    {
                        "fold": int(task["fold"]),
                        "edge_index": held_edge,
                        "observed": float(observed[held_edge]),
                        "predicted": predicted,
                        "score": _prediction_score(observed[held_edge], predicted)
                        if stable and np.isfinite(predicted)
                        else float("inf"),
                    }
                )
            if stable:
                warm_rates, warm_ages = fit["rates"], fit["ages"]
            else:
                warm_rates = warm_ages = None
        except Exception as exc:
            record = {
                "candidate_index": candidate_index,
                "path_rank": rank,
                "lam": lam,
                "valid": False,
                "message": f"{type(exc).__name__}: {exc}",
            }
            if held_edge is not None:
                record.update(
                    {
                        "fold": int(task["fold"]),
                        "edge_index": held_edge,
                        "observed": float(observed[held_edge]),
                        "predicted": None,
                        "score": float("inf"),
                    }
                )
            warm_rates = warm_ages = None
        results.append(record)
    return sorted(results, key=lambda item: int(item["candidate_index"]))


def _cache_matches(path: Path, fingerprint: str) -> bool:
    if not path.exists():
        return False
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    return value.get("status") == "ok" and value.get("fingerprint") == fingerprint


def _fit_task(task: dict[str, Any]) -> str:
    path = Path(task["cache_path"])
    if task["resume"] and _cache_matches(path, task["fingerprint"]):
        return str(path)
    try:
        value = {
            "status": "ok",
            "fingerprint": task["fingerprint"],
            "dataset_id": task["dataset_id"],
            "kind": task["kind"],
            "fold": task.get("fold"),
            "results": _fit_lambda_path(task),
        }
    except Exception as exc:
        value = {
            "status": "error",
            "fingerprint": task["fingerprint"],
            "dataset_id": task["dataset_id"],
            "kind": task["kind"],
            "message": f"{type(exc).__name__}: {exc}",
        }
    _atomic_json(path, value)
    return str(path)


def _dataset_fingerprint(
    spec: dict[str, Any], config: dict[str, Any], source_hash: str
) -> str:
    return _json_hash(
        {
            "schema": FIT_CACHE_SCHEMA,
            "spec": spec,
            "simulation": config["simulation"],
            "fit": config["fit"],
            "lambdas": config["lambdas"],
            "fit_source_hash": source_hash,
        }
    )


def _context(
    spec: dict[str, Any],
    config: dict[str, Any],
    mode: str,
    output_dir: Path,
    source_hash: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "spec": spec,
        "simulated": _simulate(spec, config),
        "fingerprint": _dataset_fingerprint(spec, config, source_hash),
        "cache_root": output_dir / "cache-v18" / mode / spec["dataset_id"],
    }


def _tasks_for_context(
    context: dict[str, Any], config: dict[str, Any], resume: bool
) -> list[dict[str, Any]]:
    spec = context["spec"]
    simulated = context["simulated"]
    tree = simulated["observed_tree"]
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    edge_indexes = [
        idx for idx, (child, _) in enumerate(edges) if int(child) < tree.ntips
    ]
    common = {
        "dataset_id": spec["dataset_id"],
        "model": spec["model"],
        "observed_tree_newick": tree.write(
            dist_formatter="%.17g", internal_labels=None
        ),
        "calibrations": _calibration_records(simulated["calibrations"]),
        "lambdas": [
            float(value)
            for value in config["modes"][context["mode"]].get(
                "lambdas", config["lambdas"]
            )
        ],
        "fit_options": config["fit"],
        "fit_seed": int(spec["fit_seed"]),
        "resume": bool(resume),
    }
    tasks = []
    for fold, edge_index in enumerate(edge_indexes):
        fingerprint = _json_hash(
            {"dataset": context["fingerprint"], "kind": "fold", "fold": fold}
        )
        tasks.append(
            {
                **common,
                "kind": "fold",
                "fold": fold,
                "held_edge": edge_index,
                "fingerprint": fingerprint,
                "cache_path": str(context["cache_root"] / f"fold-{fold:04d}.json"),
            }
        )
    fingerprint = _json_hash({"dataset": context["fingerprint"], "kind": "full"})
    tasks.append(
        {
            **common,
            "kind": "full",
            "held_edge": None,
            "fingerprint": fingerprint,
            "cache_path": str(context["cache_root"] / "full.json"),
        }
    )
    return tasks


def _run_tasks(tasks: list[dict[str, Any]], ncores: int) -> None:
    pending = [
        task
        for task in tasks
        if not (
            task["resume"]
            and _cache_matches(Path(task["cache_path"]), task["fingerprint"])
        )
    ]
    workers = min(max(1, int(ncores)), len(pending)) if pending else 0
    print(
        json.dumps(
            {
                "event": "fit_phase_start",
                "tasks": len(tasks),
                "cached": len(tasks) - len(pending),
                "pending": len(pending),
                "worker_processes": workers,
            }
        ),
        flush=True,
    )
    if not pending:
        return
    started = time.monotonic()

    def report(completed: int, cache: str) -> None:
        elapsed = time.monotonic() - started
        print(
            json.dumps(
                {
                    "event": "fit_task_complete",
                    "completed": completed,
                    "total": len(pending),
                    "elapsed_seconds": elapsed,
                    "estimated_remaining_seconds": elapsed
                    / completed
                    * (len(pending) - completed),
                    "cache": cache,
                }
            ),
            flush=True,
        )

    if workers == 1:
        for completed, task in enumerate(pending, 1):
            report(completed, _fit_task(task))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_fit_task, task) for task in pending]
            for completed, future in enumerate(as_completed(futures), 1):
                report(completed, future.result())


def _read_cache(task: dict[str, Any]) -> dict[str, Any]:
    path = Path(task["cache_path"])
    if not _cache_matches(path, task["fingerprint"]):
        raise RuntimeError(f"missing or stale fit cache: {path}")
    value = json.loads(path.read_text())
    if value.get("status") != "ok":
        raise RuntimeError(f"fit task failed: {path}: {value.get('message', '')}")
    return value


def _select_index(scores: np.ndarray, valid: np.ndarray, lambdas: np.ndarray) -> int:
    means = np.where(valid, np.mean(scores, axis=1), np.inf)
    minimum = float(np.min(means))
    if not np.isfinite(minimum):
        raise RuntimeError("no lambda candidate has valid fold paths")
    tied = np.flatnonzero(valid & (np.abs(means - minimum) <= EPS))
    return int(tied[np.argmax(lambdas[tied])])


def _bootstrap_fold_selection(
    scores: np.ndarray,
    valid: np.ndarray,
    lambdas: np.ndarray,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(int(seed))
    selected = np.empty(int(replicates), dtype=float)
    for idx in range(int(replicates)):
        columns = rng.integers(0, scores.shape[1], size=scores.shape[1])
        selected[idx] = lambdas[_select_index(scores[:, columns], valid, lambdas)]
    counts = Counter(float(value) for value in selected)
    logs = np.log10(selected)
    lower, upper = np.quantile(logs, (0.025, 0.975))
    supported = [
        float(value)
        for value in lambdas[valid]
        if lower - EPS <= np.log10(value) <= upper + EPS
    ]
    return {
        "replicates": int(replicates),
        "selection_frequencies": {
            str(value): float(count / replicates)
            for value, count in sorted(counts.items())
        },
        "selected_log10_lambda_interval": [float(lower), float(upper)],
        "selected_log10_lambda_width": float(upper - lower),
        "supported_lambdas": supported,
    }


def _age_rmse(fit: dict[str, Any], truth: np.ndarray, ntips: int) -> float:
    ages = np.asarray(fit["ages"], dtype=float)
    root_age = max(float(truth[-1]), EPS)
    return float(np.sqrt(np.mean(((ages[ntips:] - truth[ntips:]) / root_age) ** 2)))


def _calibrations_valid(fit: dict[str, Any], calibrations: dict[int, Any]) -> bool:
    ages = np.asarray(fit["ages"], dtype=float)
    for key, value in calibrations.items():
        idx = int(key) % ages.size
        lower, upper = (value, value) if np.isscalar(value) else value
        if ages[idx] < float(lower) - 1e-8 or ages[idx] > float(upper) + 1e-8:
            return False
    return True


def _score_context(
    context: dict[str, Any],
    tasks: list[dict[str, Any]],
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    spec = context["spec"]
    fold_tasks = sorted(
        (task for task in tasks if task["kind"] == "fold"),
        key=lambda item: int(item["fold"]),
    )
    full_task = next(task for task in tasks if task["kind"] == "full")
    fold_paths = [_read_cache(task)["results"] for task in fold_tasks]
    full_path = _read_cache(full_task)["results"]
    lambdas = np.asarray([float(item["lam"]) for item in full_path])
    scores = np.asarray(
        [
            [float(path[idx]["score"]) for path in fold_paths]
            for idx in range(len(lambdas))
        ]
    )
    valid = np.asarray(
        [
            all(bool(path[idx]["valid"]) for path in fold_paths)
            and np.all(np.isfinite(scores[idx]))
            for idx in range(len(lambdas))
        ]
    )
    selected_index = _select_index(scores, valid, lambdas)
    selected_lam = float(lambdas[selected_index])
    full_fits = {
        float(item["lam"]): item["fit"]
        for item in full_path
        if item.get("valid") and item.get("fit") is not None
    }
    selected_fit = full_fits.get(selected_lam)
    selected_fit_valid = bool(
        selected_fit is not None
        and selected_fit.get("converged")
        and selected_fit.get("solution_stable") is True
    )
    truth = np.asarray(context["simulated"]["true_ages"])
    errors = {
        lam: _age_rmse(fit, truth, int(spec["ntips"])) for lam, fit in full_fits.items()
    }
    if not errors:
        raise RuntimeError("no stable full-data lambda fit")
    oracle_error = min(errors.values())
    oracle_lam = max(
        lam for lam, error in errors.items() if abs(error - oracle_error) <= EPS
    )
    selected_error = errors.get(selected_lam)
    bootstrap = _bootstrap_fold_selection(
        scores,
        valid,
        lambdas,
        bootstrap_replicates,
        int(bootstrap_seed) + int(spec["fit_seed"]),
    )
    supported_fits = [
        full_fits[lam] for lam in bootstrap["supported_lambdas"] if lam in full_fits
    ]
    all_supported_valid = len(supported_fits) == len(bootstrap["supported_lambdas"])
    if supported_fits:
        age_matrix = np.vstack(
            [np.asarray(fit["ages"])[int(spec["ntips"]) :] for fit in supported_fits]
        )
        chronogram_spread = float(
            np.max(np.ptp(age_matrix, axis=0)) / max(float(truth[-1]), EPS)
        )
    else:
        chronogram_spread = None
    candidates = []
    for idx, lam in enumerate(lambdas):
        candidates.append(
            {
                "lam": float(lam),
                "valid": bool(valid[idx]),
                "mean_score": float(np.mean(scores[idx])) if valid[idx] else None,
                "standard_error": float(
                    np.std(scores[idx], ddof=1) / np.sqrt(scores.shape[1])
                )
                if valid[idx] and scores.shape[1] > 1
                else (0.0 if valid[idx] else None),
                "folds": [
                    {
                        key: path[idx].get(key)
                        for key in (
                            "fold",
                            "edge_index",
                            "observed",
                            "predicted",
                            "score",
                            "valid",
                            "message",
                        )
                    }
                    for path in fold_paths
                ],
            }
        )
    return {
        **spec,
        "status": "ok",
        "selected_lam": selected_lam,
        "selected_at_boundary": selected_index in {0, len(lambdas) - 1},
        "selected_fit_valid": selected_fit_valid,
        "calibrations_valid": bool(
            selected_fit_valid
            and _calibrations_valid(selected_fit, context["simulated"]["calibrations"])
        ),
        "selected_age_rmse": selected_error,
        "oracle_lam": float(oracle_lam),
        "oracle_age_rmse": float(oracle_error),
        "selected_age_oracle_ratio": float(
            (selected_error + EPS) / (oracle_error + EPS)
        )
        if selected_error is not None
        else None,
        "supported_chronogram_spread": chronogram_spread,
        "all_supported_lambdas_valid": all_supported_valid,
        "bootstrap": bootstrap,
        "candidates": candidates,
        "full_fit_path": full_path,
        "full_fits": {str(lam): fit for lam, fit in sorted(full_fits.items())},
    }


def _finite(values: list[Any]) -> np.ndarray:
    return np.asarray(
        [float(value) for value in values if value is not None and np.isfinite(value)]
    )


def _summarize(rows: list[dict[str, Any]], gates: dict[str, Any]) -> dict[str, Any]:
    models = {}
    all_passed = True
    for model in MODELS:
        model_rows = [row for row in rows if row["model"] == model]
        current = [row for row in model_rows if row.get("status") == "ok"]
        ratios = _finite([row["selected_age_oracle_ratio"] for row in current])
        spreads = _finite([row["supported_chronogram_spread"] for row in current])
        metrics = {
            "expected_datasets": len(model_rows),
            "datasets": len(current),
            "valid_stable_selected_fit_fraction": float(
                np.mean([row["selected_fit_valid"] for row in current])
            )
            if current
            else 0.0,
            "calibration_validity_fraction": float(
                np.mean([row["calibrations_valid"] for row in current])
            )
            if current
            else 0.0,
            "boundary_selection_fraction": float(
                np.mean([row["selected_at_boundary"] for row in current])
            )
            if current
            else 1.0,
            "selected_age_oracle_ratio_median": float(np.median(ratios))
            if ratios.size
            else None,
            "selected_age_oracle_ratio_p90": float(np.quantile(ratios, 0.9))
            if ratios.size
            else None,
            "supported_chronogram_spread_median": float(np.median(spreads))
            if spreads.size
            else None,
            "supported_chronogram_spread_p90": float(np.quantile(spreads, 0.9))
            if spreads.size
            else None,
            "all_supported_lambdas_valid_fraction": float(
                np.mean([row["all_supported_lambdas_valid"] for row in current])
            )
            if current
            else 0.0,
        }
        checks = {
            "all_datasets_scored": len(current) == len(model_rows) and bool(model_rows),
            "valid_stable_selected_fits": metrics["valid_stable_selected_fit_fraction"]
            >= float(gates["valid_stable_selected_fit_fraction"]),
            "calibration_validity": metrics["calibration_validity_fraction"]
            >= float(gates["calibration_validity_fraction"]),
            "boundary_selection": metrics["boundary_selection_fraction"]
            <= float(gates["maximum_boundary_selection_fraction"]),
            "selected_age_oracle_ratio_median": ratios.size > 0
            and metrics["selected_age_oracle_ratio_median"]
            <= float(gates["maximum_selected_age_oracle_ratio_median"]),
            "selected_age_oracle_ratio_p90": ratios.size > 0
            and metrics["selected_age_oracle_ratio_p90"]
            <= float(gates["maximum_selected_age_oracle_ratio_p90"]),
            "supported_chronogram_spread_median": spreads.size > 0
            and metrics["supported_chronogram_spread_median"]
            <= float(gates["maximum_supported_chronogram_spread_median"]),
            "supported_chronogram_spread_p90": spreads.size > 0
            and metrics["supported_chronogram_spread_p90"]
            <= float(gates["maximum_supported_chronogram_spread_p90"]),
        }
        passed = bool(current and all(checks.values()))
        all_passed &= passed
        models[model] = {
            "metrics": metrics,
            "checks": checks,
            "gates_passed": passed,
        }
    return {"models": models, "all_models_passed": bool(all_passed)}


def _write_provenance(
    output_dir: Path,
    mode: str,
    specs: list[dict[str, Any]],
    fit_hash: str,
    scoring_hash: str,
) -> None:
    _atomic_json(
        output_dir / f"environment-v18-{mode}.json",
        {
            "environment": _environment(),
            "fit_source_hash": fit_hash,
            "scoring_hash": scoring_hash,
        },
    )
    _atomic_json(
        output_dir / f"seeds-v18-{mode}.json",
        {
            "mode": mode,
            "datasets": [
                {
                    key: spec[key]
                    for key in (
                        "dataset_id",
                        "pair_id",
                        "topology_seed",
                        "rate_seed",
                        "observation_seed",
                        "fit_seed",
                    )
                }
                for spec in specs
            ],
        },
    )


def main() -> None:
    """Run or score one frozen V18 study mode."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("smoke", "pilot", "confirmation"), default="smoke"
    )
    parser.add_argument("--stage", choices=("fit", "score", "all"), default="all")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--bootstrap-replicates", type=int)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    if args.ncores < 1:
        parser.error("--ncores must be positive")
    config = json.loads(CONFIG_PATH.read_text())
    design = config["modes"][args.mode]
    bootstrap_replicates = int(
        args.bootstrap_replicates
        if args.bootstrap_replicates is not None
        else design["bootstrap_replicates"]
    )
    specs = _build_specs(config, args.mode)
    fit_hash = _fit_source_hash(config)
    scoring_hash = _scoring_hash(config, bootstrap_replicates)
    contexts = [
        _context(spec, config, args.mode, args.output_dir, fit_hash) for spec in specs
    ]
    tasks_by_dataset = {
        context["spec"]["dataset_id"]: _tasks_for_context(
            context, config, not args.no_resume
        )
        for context in contexts
    }
    tasks = [task for values in tasks_by_dataset.values() for task in values]
    _write_provenance(args.output_dir, args.mode, specs, fit_hash, scoring_hash)
    if args.stage in {"fit", "all"}:
        _run_tasks(tasks, args.ncores)
        print(
            json.dumps(
                {"mode": args.mode, "datasets": len(contexts), "fit_tasks": len(tasks)}
            ),
            flush=True,
        )
    if args.stage in {"score", "all"}:
        rows = []
        for context in contexts:
            dataset_id = context["spec"]["dataset_id"]
            try:
                rows.append(
                    _score_context(
                        context,
                        tasks_by_dataset[dataset_id],
                        bootstrap_replicates,
                        int(config["bootstrap_seed"]),
                    )
                )
            except Exception as exc:
                rows.append(
                    {
                        **context["spec"],
                        "status": "error",
                        "message": f"{type(exc).__name__}: {exc}",
                    }
                )
        summary = _summarize(rows, config["decision_gates"])
        result = {
            "result_schema": RESULT_SCHEMA,
            "study_version": 18,
            "study_name": "paired-per-tree-lambda-identifiability",
            "mode": args.mode,
            "diagnostic_only": True,
            "public_api_changed": False,
            "fixed_topology": True,
            "fit_source_hash": fit_hash,
            "scoring_hash": scoring_hash,
            "datasets": rows,
            "summary": summary,
            "next_stage": "independent_n96_confirmation"
            if args.mode == "pilot"
            and summary["models"]["uncorrelated_lognormal"]["gates_passed"]
            else "retain_supplied_lambda_and_sensitivity_analysis",
        }
        output = args.output_dir / f"results-v18-{args.mode}.json"
        _atomic_json(output, result)
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "datasets": len(rows),
                    "output": str(output),
                    "all_models_passed": summary["all_models_passed"],
                    "ucln_gates_passed": summary["models"]["uncorrelated_lognormal"][
                        "gates_passed"
                    ],
                    "diagnostic_only": True,
                }
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
