#!/usr/bin/env python

"""V7 numerical and recovery pilot for the strict-clock estimator."""

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
from toytree.mod._src.penalized_pseudolikelihood.clock import (
    edges_make_ultrametric_clock,
)
from validation.penalized_pseudolikelihood.run_validation_v2 import (
    _scale_true_tree,
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v7.json"
CACHE_SCHEMA_VERSION = 1
EPS = 1e-12
TIME_UNIT_FACTOR = 1e6


def _atomic_json(path: Path, value: Any) -> None:
    """Write JSON atomically so interrupted workers leave no valid cache."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _json_hash(value: Any) -> str:
    """Return a stable digest for JSON-compatible data."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _source_hash() -> str:
    """Hash implementation and generator sources that affect fitted values."""
    digest = hashlib.sha256()
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    for name in ("clock.py", "optimization.py", "utils.py"):
        path = root / name
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    for function in (
        _scale_true_tree,
        _clock_calibrations,
        _simulate_dataset,
        _fit_worker,
    ):
        digest.update(inspect.getsource(function).encode())
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


def _clock_calibrations(tree: Any, regime: str) -> dict[int, Any]:
    """Return root-only or root-plus-internal truth-containing bounds."""
    if regime == "root":
        return {-1: 1.0}
    if regime != "root_and_internal_interval":
        raise ValueError(f"unknown calibration regime: {regime}")
    candidates = [
        node
        for node in tree.treenode.traverse("preorder")
        if not node.is_root() and not node.is_leaf()
    ]
    node = max(candidates, key=lambda value: (value.height, value.idx))
    age = float(node.height)
    return {-1: 1.0, int(node.idx): (max(0.0, 0.9 * age), 1.1 * age)}


def _calibration_records(calibrations: dict[int, Any]) -> list[dict[str, float]]:
    """Return JSON-native calibration bounds with resolved node indices."""
    records = []
    for idx, value in calibrations.items():
        if np.isscalar(value):
            lower = upper = float(value)
        else:
            lower, upper = map(float, value)
        records.append({"idx": int(idx), "lower": lower, "upper": upper})
    return records


def _scaled_calibrations(calibrations: dict[int, Any], factor: float) -> dict[int, Any]:
    """Express the same calibrations in a different time unit."""
    scaled = {}
    for idx, value in calibrations.items():
        if np.isscalar(value):
            scaled[int(idx)] = float(value) * factor
        else:
            scaled[int(idx)] = tuple(float(item) * factor for item in value)
    return scaled


def _simulate_dataset(
    ntips: int,
    observation_model: str,
    seed: int,
    config: dict[str, Any],
) -> tuple[Any, Any, np.ndarray, np.ndarray]:
    """Return a true chronogram and strict-clock phylogram observation."""
    rng = np.random.default_rng(seed)
    true_tree = _scale_true_tree(ntips, seed)
    edges = np.asarray(true_tree.get_edges("idx"), dtype=int)
    ages = true_tree.get_node_data("height").to_numpy(dtype=float)
    means = ages[edges[:, 1]] - ages[edges[:, 0]]
    if observation_model == "noiseless":
        observed = means.copy()
    elif observation_model == "gamma":
        shape = float(config["noise"]["gamma"]["shape"])
        observed = means * rng.gamma(shape, 1.0 / shape, size=means.size)
    elif observation_model == "lognormal":
        cv = float(config["noise"]["lognormal"]["coefficient_of_variation"])
        sigma = float(np.sqrt(np.log1p(cv * cv)))
        observed = means * np.exp(
            rng.normal(-0.5 * sigma * sigma, sigma, size=means.size)
        )
    else:
        raise ValueError(f"unknown observation model: {observation_model}")
    observed_tree = true_tree.set_node_data(
        "dist",
        {int(child): float(observed[index]) for index, (child, _) in enumerate(edges)},
        inplace=False,
    )
    return true_tree, observed_tree, means, observed


def _slim_fit(fit: dict[str, Any]) -> dict[str, Any]:
    """Return JSON-native fitted values needed by cache-only scoring."""
    return {
        "converged": bool(fit["converged"]),
        "optimizer_message": str(fit.get("optimizer_message", "")),
        "ages": fit["tree"].get_node_data("height").to_numpy(dtype=float).tolist(),
        "rate": float(fit["rate"]),
        "pseudologlik": float(fit["pseudologlik"]),
        "objective": float(-fit["pseudologlik"]),
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


def _fit_clock(
    tree: Any,
    calibrations: dict[int, Any],
    nstarts: int,
    seed: int,
    options: dict[str, Any],
) -> dict[str, Any]:
    """Fit and slim one strict-clock result."""
    fit = edges_make_ultrametric_clock(
        tree,
        calibrations=calibrations,
        full=True,
        inplace=False,
        max_iter=int(options["max_iter"]),
        max_fun=int(options["max_fun"]),
        nstarts=int(nstarts),
        ncores=1,
        seed=int(seed),
        _retry_multiplier=int(options["retry_multiplier"]),
    )
    return _slim_fit(fit)


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    """Return one deterministic resumable cache path."""
    name = (
        f"{payload['scenario']}-n{payload['ntips']}-{payload['calibration']}-"
        f"{payload['observation_model']}-r{payload['replicate']:04d}.json"
    )
    return output_dir / "cache-v7" / payload["mode"] / name


def _fit_worker(payload: dict[str, Any]) -> str:
    """Simulate and fit the paired one-start and four-start estimators."""
    path = Path(payload["cache_path"])
    if payload["resume"] and path.exists():
        try:
            cached = json.loads(path.read_text())
            if cached.get("fingerprint") == payload["fingerprint"]:
                return str(path)
        except (OSError, json.JSONDecodeError):
            pass

    true_tree, observed_tree, means, observed = _simulate_dataset(
        int(payload["ntips"]),
        str(payload["observation_model"]),
        int(payload["seed"]),
        payload["config"],
    )
    calibrations = _clock_calibrations(true_tree, payload["calibration"])
    starts = [int(value) for value in payload["fit"]["nstarts_comparison"]]
    fits = {
        str(nstarts): _fit_clock(
            observed_tree,
            calibrations,
            nstarts,
            int(payload["seed"]) + nstarts * 10_003,
            payload["fit"],
        )
        for nstarts in starts
    }
    scale_fit = None
    if payload["run_scale_check"]:
        scale_fit = _fit_clock(
            observed_tree,
            _scaled_calibrations(calibrations, TIME_UNIT_FACTOR),
            max(starts),
            int(payload["seed"]) + 900_001,
            payload["fit"],
        )
    record = {
        key: payload[key]
        for key in (
            "mode",
            "scenario",
            "ntips",
            "calibration",
            "observation_model",
            "replicate",
            "seed",
            "fingerprint",
        )
    }
    record.update(
        {
            "cache_schema_version": CACHE_SCHEMA_VERSION,
            "true_ages": true_tree.get_node_data("height")
            .to_numpy(dtype=float)
            .tolist(),
            "true_rate": 1.0,
            "expected_branch_lengths": means.tolist(),
            "observed_branch_lengths": observed.tolist(),
            "calibrations": _calibration_records(calibrations),
            "fits": fits,
            "time_unit_scale_factor": TIME_UNIT_FACTOR,
            "time_unit_scaled_fit": scale_fit,
        }
    )
    _atomic_json(path, record)
    return str(path)


def _calibrations_valid(
    ages: np.ndarray, calibrations: list[dict[str, float]], factor: float = 1.0
) -> bool:
    """Return whether fitted ages satisfy every calibration bound."""
    for item in calibrations:
        idx = int(item["idx"])
        idx = idx if idx >= 0 else ages.size + idx
        lower = float(item["lower"]) * factor
        upper = float(item["upper"]) * factor
        tolerance = 1e-8 * max(1.0, abs(lower), abs(upper))
        if ages[idx] < lower - tolerance or ages[idx] > upper + tolerance:
            return False
    return True


def _score_record(record: dict[str, Any]) -> dict[str, Any]:
    """Score one cache without repeating any optimization."""
    ntips = int(record["ntips"])
    truth = np.asarray(record["true_ages"], dtype=float)
    root_age = max(float(truth[-1]), EPS)
    one = record["fits"]["1"]
    four = record["fits"]["4"]
    one_ages = np.asarray(one["ages"], dtype=float)
    four_ages = np.asarray(four["ages"], dtype=float)
    normalized_truth = truth[ntips:] / root_age
    normalized_four = four_ages[ntips:] / max(float(four_ages[-1]), EPS)
    differences = normalized_four - normalized_truth
    objective_scale = max(1.0, abs(float(four["objective"])))
    objective_gap = max(
        0.0, (float(one["objective"]) - float(four["objective"])) / objective_scale
    )
    one_four_age_difference = float(
        np.max(np.abs(one_ages[ntips:] - four_ages[ntips:])) / root_age
    )
    calibration_valid = all(
        _calibrations_valid(np.asarray(fit["ages"]), record["calibrations"])
        for fit in (one, four)
    )

    scale = record.get("time_unit_scaled_fit")
    scale_score = None
    if scale is not None:
        scaled_ages = np.asarray(scale["ages"], dtype=float)
        factor = float(record["time_unit_scale_factor"])
        scale_score = {
            "converged": bool(scale["converged"]),
            "calibration_valid": _calibrations_valid(
                scaled_ages, record["calibrations"], factor=factor
            ),
            "maximum_normalized_age_difference": float(
                np.max(np.abs(scaled_ages / factor - four_ages)) / root_age
            ),
            "rate_relative_error": float(
                abs(float(scale["rate"]) * factor - float(four["rate"]))
                / max(abs(float(four["rate"])), EPS)
            ),
        }

    return {
        key: record[key]
        for key in (
            "scenario",
            "ntips",
            "calibration",
            "observation_model",
            "replicate",
            "seed",
        )
    } | {
        "one_start_converged": bool(one["converged"]),
        "four_start_converged": bool(four["converged"]),
        "four_start_solution_stable": four["solution_stable"] is True,
        "calibration_valid": calibration_valid,
        "relative_objective_gap": float(objective_gap),
        "one_four_maximum_age_difference": one_four_age_difference,
        "age_mae": float(np.mean(np.abs(differences))),
        "age_bias": float(np.mean(differences)),
        "rate_relative_error": float(abs(float(four["rate"]) - 1.0)),
        "optimizer_retries": int(one["optimizer_retries"])
        + int(four["optimizer_retries"]),
        "time_unit_scale": scale_score,
    }


def _summarize(rows: list[dict[str, Any]], gates: dict[str, float]) -> dict[str, Any]:
    """Aggregate prespecified strict-clock numerical and recovery gates."""
    fit_flags = [
        value
        for row in rows
        for value in (row["one_start_converged"], row["four_start_converged"])
    ]
    scale_rows = [row["time_unit_scale"] for row in rows if row["time_unit_scale"]]
    noiseless = [row for row in rows if row["observation_model"] == "noiseless"]
    noisy = [row for row in rows if row["observation_model"] != "noiseless"]
    by_observation = defaultdict(list)
    by_cell = defaultdict(list)
    for row in rows:
        by_observation[row["observation_model"]].append(row)
        by_cell[(row["ntips"], row["calibration"], row["observation_model"])].append(
            row
        )

    observation_summaries = {}
    for name, group in sorted(by_observation.items()):
        observation_summaries[name] = {
            "datasets": len(group),
            "age_mae_median": float(np.median([row["age_mae"] for row in group])),
            "age_bias_mean": float(np.mean([row["age_bias"] for row in group])),
            "rate_relative_error_median": float(
                np.median([row["rate_relative_error"] for row in group])
            ),
        }
    cells = [
        {
            "ntips": key[0],
            "calibration": key[1],
            "observation_model": key[2],
            "datasets": len(group),
            "age_mae_median": float(np.median([row["age_mae"] for row in group])),
            "age_bias_mean": float(np.mean([row["age_bias"] for row in group])),
            "convergence": float(
                np.mean(
                    [
                        value
                        for row in group
                        for value in (
                            row["one_start_converged"],
                            row["four_start_converged"],
                        )
                    ]
                )
            ),
        }
        for key, group in sorted(by_cell.items())
    ]

    metrics = {
        "fit_convergence": float(np.mean(fit_flags)) if fit_flags else 0.0,
        "four_start_solution_stability": float(
            np.mean([row["four_start_solution_stable"] for row in rows])
        )
        if rows
        else 0.0,
        "calibration_validity": float(
            np.mean([row["calibration_valid"] for row in rows])
        )
        if rows
        else 0.0,
        "maximum_relative_objective_gap": float(
            max((row["relative_objective_gap"] for row in rows), default=np.inf)
        ),
        "maximum_one_four_age_difference": float(
            max(
                (row["one_four_maximum_age_difference"] for row in rows),
                default=np.inf,
            )
        ),
        "maximum_time_unit_age_difference": float(
            max(
                (
                    item["maximum_normalized_age_difference"]
                    for item in scale_rows
                    if item["converged"] and item["calibration_valid"]
                ),
                default=np.inf,
            )
        ),
        "maximum_time_unit_rate_relative_error": float(
            max(
                (
                    item["rate_relative_error"]
                    for item in scale_rows
                    if item["converged"] and item["calibration_valid"]
                ),
                default=np.inf,
            )
        ),
        "time_unit_checks_valid": bool(
            scale_rows
            and all(
                item["converged"] and item["calibration_valid"] for item in scale_rows
            )
        ),
        "noiseless_age_mae_median": float(
            np.median([row["age_mae"] for row in noiseless])
        )
        if noiseless
        else float("inf"),
        "noisy_age_mae_median": float(np.median([row["age_mae"] for row in noisy]))
        if noisy
        else float("inf"),
        "maximum_absolute_age_bias": float(
            max(
                (
                    abs(summary["age_bias_mean"])
                    for summary in observation_summaries.values()
                ),
                default=np.inf,
            )
        ),
        "optimizer_retries": int(sum(row["optimizer_retries"] for row in rows)),
    }
    checks = {
        "fit_convergence": metrics["fit_convergence"] >= gates["fit_convergence"],
        "four_start_solution_stability": metrics["four_start_solution_stability"]
        >= gates["four_start_solution_stability"],
        "calibration_validity": metrics["calibration_validity"]
        >= gates["calibration_validity"],
        "objective_parity": metrics["maximum_relative_objective_gap"]
        <= gates["maximum_relative_objective_gap"],
        "chronogram_parity": metrics["maximum_one_four_age_difference"]
        <= gates["maximum_one_four_age_difference"],
        "time_unit_invariance": bool(
            metrics["time_unit_checks_valid"]
            and metrics["maximum_time_unit_age_difference"]
            <= gates["maximum_time_unit_age_difference"]
            and metrics["maximum_time_unit_rate_relative_error"]
            <= gates["maximum_time_unit_rate_relative_error"]
        ),
        "noiseless_recovery": metrics["noiseless_age_mae_median"]
        <= gates["noiseless_age_mae_median"],
        "noisy_recovery": metrics["noisy_age_mae_median"]
        <= gates["noisy_age_mae_median"],
        "age_bias": metrics["maximum_absolute_age_bias"]
        <= gates["maximum_absolute_age_bias"],
    }
    return {
        "metrics": metrics,
        "checks": checks,
        "gates_passed": bool(all(checks.values())),
        "observations": observation_summaries,
        "cells": cells,
    }


def _payloads(
    config: dict[str, Any], mode: str, output_dir: Path, resume: bool
) -> list[dict[str, Any]]:
    """Expand one configured mode into deterministic paired datasets."""
    source_hash = _source_hash()
    payloads = []
    index = 0
    for scenario in config[mode]:
        for ntips in scenario["ntips"]:
            for calibration in scenario["calibrations"]:
                for observation_model in scenario["observation_models"]:
                    for replicate in range(int(scenario["replicates"])):
                        payload = {
                            "mode": mode,
                            "scenario": scenario["name"],
                            "ntips": int(ntips),
                            "calibration": calibration,
                            "observation_model": observation_model,
                            "replicate": replicate,
                            "seed": int(
                                config[
                                    "confirmation_seed"
                                    if mode == "confirmation"
                                    else "development_seed"
                                ]
                            )
                            + index * 100_003,
                            "fit": config["fit"],
                            "config": config,
                            "resume": resume,
                            "run_scale_check": replicate == 0,
                        }
                        fingerprint_value = {
                            key: value
                            for key, value in payload.items()
                            if key not in {"resume"}
                        } | {
                            "source_hash": source_hash,
                            "cache_schema_version": CACHE_SCHEMA_VERSION,
                        }
                        payload["fingerprint"] = _json_hash(fingerprint_value)
                        payload["cache_path"] = str(_cache_path(output_dir, payload))
                        payloads.append(payload)
                        index += 1
    return payloads


def _run_workers(payloads: list[dict[str, Any]], ncores: int) -> list[Path]:
    """Run or resume workers and print machine-readable progress."""
    started = time.monotonic()
    paths = []
    if ncores == 1:
        for completed, payload in enumerate(payloads, 1):
            result = _fit_worker(payload)
            paths.append(Path(result))
            print(
                json.dumps(
                    {
                        "event": "dataset_complete",
                        "completed": completed,
                        "total": len(payloads),
                        "elapsed_seconds": time.monotonic() - started,
                        "cache": result,
                    }
                ),
                flush=True,
            )
        return paths
    with ProcessPoolExecutor(max_workers=ncores) as executor:
        futures = [executor.submit(_fit_worker, payload) for payload in payloads]
        for completed, future in enumerate(as_completed(futures), 1):
            result = future.result()
            paths.append(Path(result))
            print(
                json.dumps(
                    {
                        "event": "dataset_complete",
                        "completed": completed,
                        "total": len(payloads),
                        "elapsed_seconds": time.monotonic() - started,
                        "cache": result,
                    }
                ),
                flush=True,
            )
    return sorted(paths)


def _read_records(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Read all fingerprint-matched caches required for scoring."""
    records = []
    for payload in payloads:
        path = Path(payload["cache_path"])
        if not path.exists():
            raise FileNotFoundError(f"missing cache: {path}")
        record = json.loads(path.read_text())
        if record.get("fingerprint") != payload["fingerprint"]:
            raise RuntimeError(f"stale cache fingerprint: {path}")
        records.append(record)
    return records


def main() -> None:
    """Run fit and/or cache-only scoring for the v7 clock study."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("smoke", "pilot", "confirmation"), default="smoke"
    )
    parser.add_argument("--stage", choices=("all", "fit", "score"), default="all")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE / "v7")
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    if args.ncores < 1:
        parser.error("--ncores must be positive")

    config = json.loads(CONFIG_PATH.read_text())
    payloads = _payloads(config, args.mode, args.output_dir, resume=not args.no_resume)
    if args.stage in {"all", "fit"}:
        _run_workers(payloads, args.ncores)
    if args.stage == "fit":
        print(json.dumps({"mode": args.mode, "datasets": len(payloads)}))
        return

    records = _read_records(payloads)
    rows = [_score_record(record) for record in records]
    summary = _summarize(rows, config["decision_gates"])
    is_confirmation = args.mode == "confirmation"
    result = {
        "study_version": int(config["study_version"]),
        "source_hash": _source_hash(),
        "config_hash": _json_hash(config),
        "mode": args.mode,
        "scope": "strict_clock_numerical_and_recovery_validation",
        "diagnostic_only": not is_confirmation,
        "release_eligible": is_confirmation,
        "sequence_length_input": False,
        "datasets": rows,
        "summary": summary,
        "all_release_gates_passed": bool(is_confirmation and summary["gates_passed"]),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / f"results-v7-{args.mode}.json"
    environment_path = args.output_dir / f"environment-v7-{args.mode}.json"
    seeds_path = args.output_dir / f"seeds-v7-{args.mode}.json"
    _atomic_json(result_path, result)
    _atomic_json(environment_path, _environment())
    _atomic_json(
        seeds_path,
        [
            {
                key: payload[key]
                for key in (
                    "scenario",
                    "ntips",
                    "calibration",
                    "observation_model",
                    "replicate",
                    "seed",
                )
            }
            for payload in payloads
        ],
    )
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(rows),
                "output": str(result_path),
                "gates_passed": summary["gates_passed"],
                "diagnostic_only": not is_confirmation,
            }
        )
    )
    if is_confirmation and not summary["gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
