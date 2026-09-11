#!/usr/bin/env python

"""Task-parallel V13 validation of the fixed-lambda correlated estimator."""

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
from toytree.mod._src.penalized_pseudolikelihood.correlated import (
    _edges_make_ultrametric_correlated as edges_make_ultrametric_correlated,
)
from validation.penalized_pseudolikelihood.simulation_helpers import (
    _scale_true_tree,
    _simulate_rates,
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v13.json"
DEFAULT_OUTPUT = HERE / "v13"
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


def _fit_source_hash(config: dict[str, Any]) -> str:
    """Hash only implementation and design inputs affecting fitted values."""
    digest = hashlib.sha256()
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    for name in ("correlated.py", "clock.py", "optimization.py", "utils.py"):
        source = root / name
        digest.update(source.name.encode())
        digest.update(source.read_bytes())
    for function in (
        _scale_true_tree,
        _simulate_rates,
        _calibrations,
        _fixed_calibrations,
        _scale_calibrations,
        _parent_edges,
        _matched_lambda,
        _simulate,
        _slim,
        _fit,
        _role_seed_offset,
        _dataset_id,
        _roles,
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
    """Hash scoring code and thresholds without changing fit fingerprints."""
    digest = hashlib.sha256(_fit_source_hash(config).encode())
    for function in (
        _assemble,
        _calibration_records,
        _calibrations_valid,
        _center_log_rates,
        _rate_increments,
        _safe_spearman,
        _reference_fit,
        _score_record,
        _finite_median,
        _summarize,
    ):
        digest.update(function.__name__.encode())
        digest.update(inspect.getsource(function).encode())
    digest.update(json.dumps(config["decision_gates"], sort_keys=True).encode())
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


def _parent_edges(tree: Any) -> np.ndarray:
    """Map every edge to its parent edge, using -1 for basal edges."""
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    child_to_edge = {int(child): index for index, (child, _) in enumerate(edges)}
    return np.asarray(
        [child_to_edge.get(int(parent), -1) for _, parent in edges], dtype=int
    )


def _matched_lambda(sigma_log: float) -> float:
    """Return the Gaussian-increment penalty coefficient."""
    sigma_log = float(sigma_log)
    if not np.isfinite(sigma_log) or sigma_log <= 0.0:
        raise ValueError("sigma_log must be finite and positive")
    return float(1.0 / (2.0 * sigma_log * sigma_log))


def _simulate(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate a Gaussian-increment correlated chronogram and phylogram."""
    seed = int(payload["seed"])
    rng = np.random.default_rng(seed)
    true_tree = _scale_true_tree(int(payload["ntips"]), seed)
    edges = np.asarray(true_tree.get_edges("idx"), dtype=int)
    ages = true_tree.get_node_data("height").to_numpy(dtype=float)
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    simulation = {
        "baseline_rate": float(payload["config"]["simulation"]["baseline_rate"]),
        "correlated_log_sigma": float(payload["sigma_log"]),
    }
    rates = _simulate_rates(true_tree, "correlated", rng, simulation)
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
        "parent_edges": _parent_edges(true_tree),
    }


def _slim(fit: dict[str, Any]) -> dict[str, Any]:
    """Return JSON-native fitted values needed by cache-only scoring."""
    return {
        "converged": bool(fit["converged"]),
        "optimizer_message": str(fit.get("optimizer_message", "")),
        "ages": fit["tree"].get_node_data("height").to_numpy(dtype=float).tolist(),
        "rates": [float(value) for value in fit["rates"]],
        "pseudologlik": float(fit["pseudologlik"]),
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
        "best_start_kind": str(fit.get("best_start_kind", "")),
    }


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
        lam=_matched_lambda(payload["sigma_log"]),
        calibrations=calibrations,
        full=True,
        inplace=False,
        max_iter=int(options["max_iter"]),
        max_fun=int(options["max_fun"]),
        max_refine=int(options["max_refine"]),
        nstarts=int(nstarts),
        ncores=1,
        seed=int(payload["fit_seed"]) + _role_seed_offset(role),
        _retry_multiplier=int(options["retry_multiplier"]),
        **kwargs,
    )
    return _slim(fit)


def _role_seed_offset(role: str) -> int:
    """Return deterministic, independent optimizer-seed offsets."""
    return {
        "default": 0,
        "stress": 10_000,
        "oracle_start": 20_000,
        "fixed_age": 30_000,
        # Match default exactly so this tests units, not random starts.
        "time_scaled": 0,
    }[role]


def _dataset_id(payload: dict[str, Any]) -> str:
    """Return the stable identifier shared by all tasks for one dataset."""
    sigma = str(payload["sigma_log"]).replace(".", "p")
    return (
        f"correlated-n{payload['ntips']}-{payload['calibration']}-"
        f"{payload['observation_model']}-sigma{sigma}-r"
        f"{payload['replicate']:04d}"
    )


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    """Return the deterministic path for one independently runnable fit."""
    return (
        output_dir
        / "cache-v13"
        / payload["mode"]
        / f"{_dataset_id(payload)}-{payload['role']}.json"
    )


def _roles(payload: dict[str, Any]) -> list[str]:
    """Return independent fit roles for one simulated dataset."""
    roles = ["default", "stress", "oracle_start", "fixed_age"]
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
    options = payload["config"]["fit"]
    nstarts = int(options["default_nstarts"])
    fit_calibrations = calibrations
    if role == "stress":
        nstarts = int(options["stress_nstarts"])
    elif role == "oracle_start":
        nstarts = int(options["oracle_nstarts"])
    elif role == "fixed_age":
        fit_calibrations = _fixed_calibrations(simulated["true_tree"])
    elif role == "time_scaled":
        fit_calibrations = _scale_calibrations(calibrations, TIME_UNIT_FACTOR)

    initial_ages = simulated["true_ages"] if role == "oracle_start" else None
    initial_rates = simulated["true_rates"] if role == "oracle_start" else None
    fit = _fit(
        simulated["observed_tree"],
        fit_calibrations,
        payload,
        role,
        nstarts,
        true_ages=initial_ages,
        true_rates=initial_rates,
    )
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
    """Require all task caches and fingerprints to match without fitting."""
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
                "lam": _matched_lambda(payload["sigma_log"]),
                "replicate": int(payload["replicate"]),
                "seed": int(payload["seed"]),
                "true_ages": simulated["true_ages"].tolist(),
                "true_rates": simulated["true_rates"].tolist(),
                "parent_edges": simulated["parent_edges"].tolist(),
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
    """Remove the common log-rate scale."""
    logs = np.log(np.clip(np.asarray(values, dtype=float), EPS, None))
    return logs - float(np.mean(logs))


def _rate_increments(values: np.ndarray, parent_edges: np.ndarray) -> np.ndarray:
    """Return nonbasal parent-child and centered basal log-rate contrasts."""
    logs = np.log(np.clip(np.asarray(values, dtype=float), EPS, None))
    parent_edges = np.asarray(parent_edges, dtype=int)
    increments = np.empty_like(logs)
    nonbasal = parent_edges >= 0
    increments[nonbasal] = logs[nonbasal] - logs[parent_edges[nonbasal]]
    basal = ~nonbasal
    increments[basal] = logs[basal] - float(np.mean(logs[basal]))
    return increments


def _safe_spearman(left: np.ndarray, right: np.ndarray) -> float:
    """Return Spearman correlation, or NaN for a constant input."""
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    if left.size < 2 or np.ptp(left) == 0.0 or np.ptp(right) == 0.0:
        return float("nan")
    return float(spearmanr(left, right).statistic)


def _reference_fit(fits: dict[str, dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    """Return the best converged independently initialized reference fit."""
    candidates = [
        (name, fits[name])
        for name in ("stress", "oracle_start")
        if fits[name]["converged"] and np.isfinite(fits[name]["objective"])
    ]
    if not candidates:
        return "stress", fits["stress"]
    return min(candidates, key=lambda item: float(item[1]["objective"]))


def _score_record(record: dict[str, Any]) -> dict[str, Any]:
    """Score one assembled dataset without calling any fitter."""
    fits = record["fits"]
    default = fits["default"]
    stress = fits["stress"]
    oracle = fits["oracle_start"]
    fixed = fits["fixed_age"]
    reference_role, reference = _reference_fit(fits)
    ntips = int(record["ntips"])
    truth = np.asarray(record["true_ages"], dtype=float)
    root_age = max(abs(float(truth[-1])), EPS)
    true_internal = truth[ntips:] / root_age
    default_ages = np.asarray(default["ages"], dtype=float)
    reference_ages = np.asarray(reference["ages"], dtype=float)
    fitted_internal = default_ages[ntips:] / max(abs(float(default_ages[-1])), EPS)
    age_delta = fitted_internal - true_internal
    objective_scale = max(1.0, abs(float(reference["objective"])))
    objective_gap = max(
        0.0,
        (float(default["objective"]) - float(reference["objective"])) / objective_scale,
    )
    default_reference_age_difference = float(
        np.max(np.abs(default_ages[ntips:] - reference_ages[ntips:])) / root_age
    )
    calibration_valid = all(
        _calibrations_valid(np.asarray(fit["ages"]), record["calibrations"])
        for fit in (default, stress, oracle)
    )

    true_rates = np.asarray(record["true_rates"], dtype=float)
    fixed_rates = np.asarray(fixed["rates"], dtype=float)
    centered_error = _center_log_rates(fixed_rates) - _center_log_rates(true_rates)
    parent_edges = np.asarray(record["parent_edges"], dtype=int)
    true_increments = _rate_increments(true_rates, parent_edges)
    fitted_increments = _rate_increments(fixed_rates, parent_edges)
    increment_error = fitted_increments - true_increments

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

    observed = np.asarray(record["observed_branch_lengths"], dtype=float)
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
        "oracle_start_converged": bool(oracle["converged"]),
        "fixed_age_converged": bool(fixed["converged"]),
        "stress_solution_stable": stress["solution_stable"] is True,
        "reference_role": reference_role,
        "calibration_valid": calibration_valid,
        "relative_objective_gap": objective_gap,
        "default_reference_maximum_age_difference": (default_reference_age_difference),
        "age_mae": float(np.mean(np.abs(age_delta))),
        "age_bias": float(np.mean(age_delta)),
        "fixed_age_rate_spearman": _safe_spearman(true_rates, fixed_rates),
        "fixed_age_centered_log_rate_rmse": float(
            np.sqrt(np.mean(centered_error * centered_error))
        ),
        "fixed_age_increment_spearman": _safe_spearman(
            true_increments, fitted_increments
        ),
        "fixed_age_increment_rmse": float(
            np.sqrt(np.mean(increment_error * increment_error))
        ),
        "optimizer_retries": sum(
            int(fit["optimizer_retries"]) for fit in (default, stress, oracle, fixed)
        ),
        "zero_length_branch_count": int(np.sum(observed == 0.0)),
        "zero_length_branch_fraction": float(np.mean(observed == 0.0)),
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
            row["oracle_start_converged"],
            row["fixed_age_converged"],
        )
    ]
    scale_rows = [row["time_unit_scale"] for row in rows if row["time_unit_scale"]]
    by_observation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_sigma: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_calibration: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_observation[row["observation_model"]].append(row)
        by_sigma[str(row["sigma_log"])].append(row)
        by_calibration[row["calibration"]].append(row)

    def summarize_group(group: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "datasets": len(group),
            "age_mae_median": _finite_median([row["age_mae"] for row in group]),
            "age_bias_mean": float(np.mean([row["age_bias"] for row in group])),
            "fixed_age_rate_spearman_median": _finite_median(
                [row["fixed_age_rate_spearman"] for row in group]
            ),
            "fixed_age_increment_spearman_median": _finite_median(
                [row["fixed_age_increment_spearman"] for row in group]
            ),
        }

    observation_summaries = {
        name: summarize_group(group) for name, group in sorted(by_observation.items())
    }
    sigma_summaries = {
        name: summarize_group(group) for name, group in sorted(by_sigma.items())
    }
    calibration_summaries = {
        name: summarize_group(group) for name, group in sorted(by_calibration.items())
    }
    identifiable = [
        row
        for row in rows
        if row["observation_model"] == "expected_branch"
        and float(row["sigma_log"]) >= 0.3
    ]
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
        "maximum_default_reference_age_difference": max(
            (row["default_reference_maximum_age_difference"] for row in rows),
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
            [row["fixed_age_rate_spearman"] for row in identifiable]
        ),
        "fixed_age_increment_spearman_median": _finite_median(
            [row["fixed_age_increment_spearman"] for row in identifiable]
        ),
        "fixed_age_centered_log_rate_rmse_median": _finite_median(
            [row["fixed_age_centered_log_rate_rmse"] for row in rows]
        ),
        "fixed_age_increment_rmse_median": _finite_median(
            [row["fixed_age_increment_rmse"] for row in rows]
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
        "zero_containing_dataset_fraction": float(
            np.mean([row["zero_length_branch_count"] > 0 for row in rows])
        )
        if rows
        else 0.0,
        "maximum_zero_length_branch_fraction": max(
            (row["zero_length_branch_fraction"] for row in rows), default=0.0
        ),
    }
    checks = {
        "fit_convergence": metrics["fit_convergence"] >= gates["fit_convergence"],
        "stress_solution_stability": metrics["stress_solution_stability"]
        >= gates["stress_solution_stability"],
        "calibration_validity": metrics["calibration_validity"]
        >= gates["calibration_validity"],
        "objective_parity": metrics["maximum_relative_objective_gap"]
        <= gates["maximum_relative_objective_gap"],
        "chronogram_parity": metrics["maximum_default_reference_age_difference"]
        <= gates["maximum_default_reference_age_difference"],
        "age_recovery": metrics["age_mae_median"] <= gates["age_mae_median"],
        "age_bias": metrics["maximum_absolute_age_bias"]
        <= gates["maximum_absolute_age_bias"],
        "fixed_age_rate_recovery": metrics["fixed_age_rate_spearman_median"]
        >= gates["fixed_age_rate_spearman_median"],
        "fixed_age_increment_recovery": metrics["fixed_age_increment_spearman_median"]
        >= gates["fixed_age_increment_spearman_median"],
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
        "calibrations": calibration_summaries,
    }


def _datasets(config: dict[str, Any], mode: str, resume: bool) -> list[dict[str, Any]]:
    """Enumerate deterministic study cells and independent seed streams."""
    design = config["modes"][mode]
    base_seed = int(
        config["confirmation_seed"]
        if mode == "confirmation"
        else config["development_seed"]
    )
    source_hash = _fit_source_hash(config)
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
                                "scenario": "fixed-lambda-correlated-recovery",
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
    """Run fit tasks and/or cache-only scoring for the V13 study."""
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
        args.output_dir / f"environment-v13-{args.mode}.json",
        {
            "environment": _environment(),
            "fit_source_hash": _fit_source_hash(config),
            "scoring_hash": _scoring_hash(config),
            "config_hash": _json_hash(config),
            "config": config,
        },
    )
    _atomic_json(
        args.output_dir / f"seeds-v13-{args.mode}.json",
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
        "fit_source_hash": _fit_source_hash(config),
        "scoring_hash": _scoring_hash(config),
        "config_hash": _json_hash(config),
        "mode": args.mode,
        "scope": "fixed_lambda_correlated_numerical_and_recovery_validation",
        "lambda_selection": False,
        "sequence_length_input": False,
        "diagnostic_only": not is_confirmation,
        "release_eligible": is_confirmation,
        "datasets": rows,
        "summary": summary,
        "all_release_gates_passed": bool(is_confirmation and summary["gates_passed"]),
    }
    result_path = args.output_dir / f"results-v13-{args.mode}.json"
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
