#!/usr/bin/env python

"""Run the focused correlated-rate lambda cross-validation study."""

# ruff: noqa: E402 -- thread limits must precede numerical imports.

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
from scipy.stats import spearmanr

import toytree
from toytree.mod._src.penalized_pseudolikelihood.correlated import (
    edges_make_ultrametric_correlated,
)
from toytree.mod._src.penalized_pseudolikelihood.lambda_cv import (
    edges_make_ultrametric_correlated_lambda_cv,
)
from validation.penalized_pseudolikelihood.run_validation_v2 import (
    _calibrations,
    _simulate_dataset,
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v3.json"
CACHE_SCHEMA_VERSION = 2


def _json_hash(value: Any) -> str:
    """Return a stable hash for JSON-native data."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _source_hash() -> str:
    """Hash estimator, CV, and simulation code that affects results."""
    digest = hashlib.sha256()
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    for name in ("correlated.py", "lambda_cv.py", "utils.py"):
        path = root / name
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    for function in (_simulate_dataset, _calibrations):
        digest.update(inspect.getsource(function).encode())
    return digest.hexdigest()


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    """Atomically write one JSON artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    """Return the cache path for one simulated dataset."""
    sigma = str(payload["sigma"]).replace(".", "p")
    name = f"{payload['scenario']}-sigma{sigma}-" f"r{payload['replicate']:04d}.json"
    return output_dir / "cache-v3" / payload["mode"] / name


def _slim_fit(fit: dict[str, Any]) -> dict[str, Any]:
    """Return JSON-native quantities needed for scoring."""
    return {
        "converged": bool(fit["converged"]),
        "optimizer_message": str(fit.get("optimizer_message", "")),
        "ages": fit["tree"].get_node_data("height").to_numpy(dtype=float).tolist(),
        "rates": [float(value) for value in fit["rates"]],
        "expected_branch_lengths": [
            float(value) for value in fit["expected_branch_lengths"]
        ],
        "pseudologlik": float(fit["pseudologlik"]),
        "penalized_pseudologlik": float(fit["penalized_pseudologlik"]),
        "penalty": float(fit["penalty"]),
        "nfev": int(fit.get("nfev", -1)),
        "nit": int(fit.get("nit", -1)),
        "refinement_cycles": int(fit.get("refinement_cycles", -1)),
        "final_joint_converged": bool(fit.get("final_joint_converged", False)),
        "gradient_max_abs": fit.get("gradient_max_abs"),
    }


def _fit_worker(payload: dict[str, Any]) -> str:
    """Simulate, cross-validate, and fit the lambda grid for one dataset."""
    path = Path(payload["cache_path"])
    if payload["resume"] and path.exists():
        try:
            cached = json.loads(path.read_text())
            if cached.get("fingerprint") == payload["fingerprint"]:
                return str(path)
        except (OSError, json.JSONDecodeError):
            pass

    record = {
        key: payload[key]
        for key in (
            "mode",
            "scenario",
            "track",
            "ntips",
            "calibration",
            "release_gate",
            "baseline_rate",
            "gamma_shape",
            "sigma",
            "replicate",
            "seed",
            "fingerprint",
        )
    }
    record["cache_schema_version"] = CACHE_SCHEMA_VERSION
    try:
        simulation = dict(payload["simulation"])
        simulation["correlated_log_sigma"] = float(payload["sigma"])
        true_tree, observed_tree, true_rates, true_means, observed = _simulate_dataset(
            "correlated",
            int(payload["ntips"]),
            payload["track"],
            int(payload["seed"]),
            simulation,
        )
        calibrations = _calibrations(true_tree, payload["calibration"])
        options = {
            "max_iter": int(payload["fit"]["max_iter"]),
            "max_fun": int(payload["fit"]["max_fun"]),
            "max_refine": int(payload["fit"]["max_refine"]),
            "nstarts": int(payload["fit"]["nstarts"]),
            "ncores": 1,
            "seed": int(payload["seed"]),
        }
        cv = edges_make_ultrametric_correlated_lambda_cv(
            observed_tree,
            lambdas=payload["lambdas"],
            calibrations=calibrations,
            **options,
        )
        full_fits = {}
        for lam in payload["lambdas"]:
            if float(lam) == float(cv["selected_lam"]):
                fit = cv["selected_fit"]
            else:
                fit = edges_make_ultrametric_correlated(
                    observed_tree,
                    lam=float(lam),
                    calibrations=calibrations,
                    full=True,
                    inplace=False,
                    **options,
                )
            full_fits[str(float(lam))] = _slim_fit(fit)

        candidates = []
        for candidate in cv["candidates"]:
            candidates.append(
                {
                    "lam": float(candidate["lam"]),
                    "valid": bool(candidate["valid"]),
                    "mean_score": float(candidate["mean_score"]),
                    "standard_error": float(candidate["standard_error"]),
                    "folds": [
                        {
                            "fold": int(fold["fold"]),
                            "edge_index": int(fold["edge_index"]),
                            "observed": float(fold["observed"]),
                            "predicted": float(fold["predicted"]),
                            "predicted_rate": float(fold["predicted_rate"]),
                            "ancestral_rate": (
                                None
                                if fold["ancestral_rate"] is None
                                else float(fold["ancestral_rate"])
                            ),
                            "score": float(fold["score"]),
                            "converged": bool(fold["converged"]),
                            "optimizer_message": str(fold["optimizer_message"]),
                        }
                        for fold in candidate["folds"]
                    ],
                }
            )
        record.update(
            {
                "status": "ok",
                "true_ages": true_tree.get_node_data("height")
                .to_numpy(dtype=float)
                .tolist(),
                "true_rates": true_rates.tolist(),
                "true_means": true_means.tolist(),
                "observed": observed.tolist(),
                "selected_lam": float(cv["selected_lam"]),
                "selected_at_boundary": bool(cv["selected_at_boundary"]),
                "candidates": candidates,
                "full_fits": full_fits,
            }
        )
    except Exception as exc:
        record.update({"status": "error", "message": f"{type(exc).__name__}: {exc}"})
    _atomic_json(path, record)
    return str(path)


def _population_loss(true_means: np.ndarray, predicted: np.ndarray) -> float:
    """Return mean Pearson loss against the known population means."""
    expected = np.clip(np.asarray(predicted, dtype=float), 1e-12, None)
    return float(np.mean((np.asarray(true_means) - expected) ** 2 / expected))


def _rate_spearman(true_rates: np.ndarray, fitted_rates: np.ndarray) -> float | None:
    """Return log-rate rank recovery, or None for a degenerate vector."""
    value = float(spearmanr(np.log(true_rates), np.log(fitted_rates)).statistic)
    return value if np.isfinite(value) else None


def _score_record(record: dict[str, Any]) -> dict[str, Any]:
    """Score selected lambda against the full-fit population-risk oracle."""
    base = {
        key: record[key]
        for key in (
            "status",
            "scenario",
            "track",
            "ntips",
            "calibration",
            "release_gate",
            "baseline_rate",
            "gamma_shape",
            "sigma",
            "replicate",
            "seed",
        )
    }
    if record["status"] != "ok":
        return {**base, "message": record.get("message", "")}

    true_means = np.asarray(record["true_means"], dtype=float)
    true_ages = np.asarray(record["true_ages"], dtype=float)
    true_rates = np.asarray(record["true_rates"], dtype=float)
    losses = {}
    for label, fit in record["full_fits"].items():
        if fit["converged"]:
            losses[float(label)] = _population_loss(
                true_means, np.asarray(fit["expected_branch_lengths"], dtype=float)
            )
    if not losses:
        return {**base, "status": "error", "message": "all full-grid fits failed"}

    oracle_loss = min(losses.values())
    tied = [lam for lam, loss in losses.items() if abs(loss - oracle_loss) <= 1e-12]
    oracle_lam = max(tied)
    selected_lam = float(record["selected_lam"])
    selected_fit = record["full_fits"][str(selected_lam)]
    oracle_fit = record["full_fits"][str(oracle_lam)]
    selected_loss = losses.get(selected_lam, float("inf"))
    internal = slice(int(record["ntips"]), None)
    selected_age_rmse = float(
        np.sqrt(
            np.mean(
                (np.asarray(selected_fit["ages"])[internal] - true_ages[internal]) ** 2
            )
        )
    )
    oracle_age_rmse = float(
        np.sqrt(
            np.mean(
                (np.asarray(oracle_fit["ages"])[internal] - true_ages[internal]) ** 2
            )
        )
    )
    selected_rho = _rate_spearman(
        true_rates, np.asarray(selected_fit["rates"], dtype=float)
    )
    oracle_rho = _rate_spearman(
        true_rates, np.asarray(oracle_fit["rates"], dtype=float)
    )
    fold_rows = [
        fold for candidate in record["candidates"] for fold in candidate["folds"]
    ]
    fixed_ages = record["calibration"] == "fixed_internal_ages"
    return {
        **base,
        "selected_lam": selected_lam,
        "oracle_lam": float(oracle_lam),
        "theoretical_lam": float(1.0 / (2.0 * float(record["sigma"]) ** 2)),
        "selected_at_boundary": bool(record["selected_at_boundary"]),
        "all_candidates_converged": bool(
            all(candidate["valid"] for candidate in record["candidates"])
            and all(fit["converged"] for fit in record["full_fits"].values())
        ),
        "folds_converged": int(sum(fold["converged"] for fold in fold_rows)),
        "folds_total": len(fold_rows),
        "selected_population_loss": float(selected_loss),
        "oracle_population_loss": float(oracle_loss),
        "population_excess_loss": float(selected_loss - oracle_loss),
        "population_regret": float(
            (selected_loss - oracle_loss) / max(oracle_loss, 1e-12)
        ),
        "selected_age_rmse": selected_age_rmse,
        "oracle_age_rmse": oracle_age_rmse,
        "age_rmse_ratio": (
            None
            if fixed_ages
            else float(selected_age_rmse / max(oracle_age_rmse, 1e-12))
        ),
        "selected_rate_spearman": selected_rho,
        "oracle_rate_spearman": oracle_rho,
        "rate_spearman_delta": (
            None
            if selected_rho is None or oracle_rho is None
            else float(selected_rho - oracle_rho)
        ),
        "observed_zero_fraction": float(
            np.mean(np.asarray(record["observed"], dtype=float) == 0.0)
        ),
    }


def _finite(rows: list[dict[str, Any]], key: str) -> np.ndarray:
    """Return finite metric values from successful rows."""
    values = [
        row.get(key)
        for row in rows
        if row.get("status") == "ok" and row.get(key) is not None
    ]
    array = np.asarray(values, dtype=float)
    return array[np.isfinite(array)]


def _summarize_cell(
    rows: list[dict[str, Any]], gates: dict[str, float]
) -> dict[str, Any]:
    """Summarize and gate one prespecified simulation cell."""
    successes = [row for row in rows if row.get("status") == "ok"]
    fold_total = sum(row.get("folds_total", 0) for row in successes)
    fold_ok = sum(row.get("folds_converged", 0) for row in successes)
    dataset_convergence = sum(
        row.get("all_candidates_converged", False) for row in successes
    ) / len(rows)
    fold_convergence = fold_ok / fold_total if fold_total else 0.0
    regret = _finite(rows, "population_regret")
    age_ratio = _finite(rows, "age_rmse_ratio")
    rate_delta = _finite(rows, "rate_spearman_delta")
    excess_loss = _finite(rows, "population_excess_loss")
    zero_fraction = _finite(rows, "observed_zero_fraction")
    boundary = sum(row.get("selected_at_boundary", False) for row in successes) / len(
        rows
    )
    metrics = {
        "datasets": len(rows),
        "dataset_convergence": float(dataset_convergence),
        "fold_convergence": float(fold_convergence),
        "population_regret_median": (float(np.median(regret)) if regret.size else None),
        "population_regret_90th_percentile": (
            float(np.quantile(regret, 0.9)) if regret.size else None
        ),
        "age_rmse_ratio_median": (
            float(np.median(age_ratio)) if age_ratio.size else None
        ),
        "rate_spearman_delta_median": (
            float(np.median(rate_delta)) if rate_delta.size else None
        ),
        "population_excess_loss_median": (
            float(np.median(excess_loss)) if excess_loss.size else None
        ),
        "population_excess_loss_90th_percentile": (
            float(np.quantile(excess_loss, 0.9)) if excess_loss.size else None
        ),
        "observed_zero_fraction_median": (
            float(np.median(zero_fraction)) if zero_fraction.size else None
        ),
        "boundary_selection_fraction": float(boundary),
    }
    checks = {
        "dataset_convergence": (
            metrics["dataset_convergence"] >= gates["dataset_convergence"]
        ),
        "fold_convergence": metrics["fold_convergence"] >= gates["fold_convergence"],
        "population_regret_median": (
            metrics["population_regret_median"] is not None
            and metrics["population_regret_median"] <= gates["population_regret_median"]
        ),
        "population_regret_90th_percentile": (
            metrics["population_regret_90th_percentile"] is not None
            and metrics["population_regret_90th_percentile"]
            <= gates["population_regret_90th_percentile"]
        ),
        "age_rmse_ratio_median": (
            metrics["age_rmse_ratio_median"] is None
            or metrics["age_rmse_ratio_median"] <= gates["age_rmse_ratio_median"]
        ),
        "rate_spearman_delta_median": (
            metrics["rate_spearman_delta_median"] is not None
            and metrics["rate_spearman_delta_median"]
            >= gates["rate_spearman_delta_median"]
        ),
        "boundary_selection_fraction": (
            metrics["boundary_selection_fraction"]
            <= gates["boundary_selection_fraction"]
        ),
    }
    return {**metrics, "checks": checks, "passed": bool(all(checks.values()))}


def _payloads(
    config: dict[str, Any],
    mode: str,
    output_dir: Path,
    resume: bool,
) -> tuple[list[dict[str, Any]], list[int]]:
    """Build deterministic dataset payloads for one study mode."""
    base_seed = (
        config["confirmation_seed"]
        if mode == "confirmation"
        else config["development_seed"]
    )
    source_hash = _source_hash()
    payloads = []
    seeds = []
    index = 0
    all_sigmas = config["simulation"]["correlated_log_sigmas"]
    for scenario in config[mode]:
        simulation = dict(config["simulation"])
        for key in ("baseline_rate", "gamma_shape"):
            if key in scenario:
                simulation[key] = scenario[key]
        sigmas = scenario.get("sigmas", all_sigmas)
        for sigma in sigmas:
            for replicate in range(int(scenario["replicates"])):
                seed = int(base_seed + index)
                index += 1
                core = {
                    "mode": mode,
                    "scenario": scenario["name"],
                    "track": scenario["track"],
                    "ntips": int(scenario["ntips"]),
                    "calibration": scenario["calibration"],
                    "release_gate": bool(scenario["release_gate"]),
                    "baseline_rate": float(simulation["baseline_rate"]),
                    "gamma_shape": float(simulation["gamma_shape"]),
                    "sigma": float(sigma),
                    "replicate": replicate,
                    "seed": seed,
                    "simulation": simulation,
                    "fit": config["fit"],
                    "lambdas": scenario.get("lambdas", config["lambdas"]),
                }
                fingerprint = _json_hash(
                    {
                        "cache_schema_version": CACHE_SCHEMA_VERSION,
                        "source_hash": source_hash,
                        **core,
                    }
                )
                payload = {
                    **core,
                    "fingerprint": fingerprint,
                    "resume": resume,
                }
                payload["cache_path"] = str(_cache_path(output_dir, payload))
                payloads.append(payload)
                seeds.append(seed)
    return payloads, seeds


def _progress(completed: int, total: int, started: float, path: str) -> None:
    """Print one machine-readable dataset progress record."""
    print(
        json.dumps(
            {
                "event": "dataset_complete",
                "completed": completed,
                "total": total,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "cache": path,
            }
        ),
        flush=True,
    )


def _run_workers(
    payloads: list[dict[str, Any]], ncores: int, progress_every: int = 1
) -> None:
    """Run dataset workers serially or in a process pool."""
    started = time.monotonic()
    total = len(payloads)
    if ncores == 1:
        for completed, payload in enumerate(payloads, start=1):
            path = _fit_worker(payload)
            if completed % progress_every == 0 or completed == total:
                _progress(completed, total, started, path)
        return
    with ProcessPoolExecutor(max_workers=min(ncores, len(payloads))) as pool:
        futures = [pool.submit(_fit_worker, payload) for payload in payloads]
        for completed, future in enumerate(as_completed(futures), start=1):
            path = future.result()
            if completed % progress_every == 0 or completed == total:
                _progress(completed, total, started, path)


def _read_records(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Read matching caches or raise when the fit stage is incomplete."""
    records = []
    for payload in payloads:
        path = Path(payload["cache_path"])
        if not path.exists():
            raise RuntimeError(f"missing cache: {path}")
        record = json.loads(path.read_text())
        if record.get("fingerprint") != payload["fingerprint"]:
            raise RuntimeError(f"stale cache: {path}")
        records.append(record)
    return records


def _aggregate(
    rows: list[dict[str, Any]], gates: dict[str, float]
) -> tuple[list[dict[str, Any]], bool]:
    """Aggregate prespecified cells and gate only cells marked for release."""
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            row["scenario"],
            row["track"],
            int(row["ntips"]),
            row["calibration"],
            float(row["sigma"]),
            bool(row["release_gate"]),
        )
        groups.setdefault(key, []).append(row)
    cells = []
    release_passes = []
    for key, values in sorted(groups.items()):
        scenario, track, ntips, calibration, sigma, release_gate = key
        summary = _summarize_cell(values, gates)
        cell = {
            "scenario": scenario,
            "track": track,
            "ntips": ntips,
            "calibration": calibration,
            "sigma": sigma,
            "release_gate": release_gate,
            **summary,
        }
        cells.append(cell)
        if release_gate:
            release_passes.append(bool(summary["passed"]))
    return cells, bool(release_passes and all(release_passes))


def _environment(config: dict[str, Any]) -> dict[str, Any]:
    """Return reproducibility metadata."""
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "toytree": toytree.__version__,
        "config_hash": _json_hash(config),
        "source_hash": _source_hash(),
        "cache_schema_version": CACHE_SCHEMA_VERSION,
    }


def main(argv: list[str] | None = None) -> int:
    """Run one fitting or scoring stage of validation study v3."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=("smoke", "pilot", "confirmation"), default="pilot"
    )
    parser.add_argument("--stage", choices=("all", "fit", "score"), default="all")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE / "v3")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--progress-every", type=int, default=1)
    args = parser.parse_args(argv)
    if args.ncores < 1:
        parser.error("--ncores must be positive")
    if args.progress_every < 1:
        parser.error("--progress-every must be positive")

    config = json.loads(CONFIG_PATH.read_text())
    payloads, seeds = _payloads(config, args.mode, args.output_dir, not args.no_resume)
    if args.stage in {"all", "fit"}:
        _run_workers(payloads, args.ncores, args.progress_every)
        _atomic_json(
            args.output_dir / f"seeds-v3-{args.mode}.json",
            {"study_version": 3, "seeds": seeds},
        )
        if args.stage == "fit":
            print(json.dumps({"mode": args.mode, "datasets": len(payloads)}))
            return 0

    records = _read_records(payloads)
    rows = [_score_record(record) for record in records]
    cells, gates_passed = _aggregate(rows, config["release_gates"])
    release_eligible = args.mode == "confirmation"
    all_passed = bool(release_eligible and gates_passed)
    result = {
        "study_version": 3,
        "mode": args.mode,
        "scope": "correlated_lambda_selection_only",
        "release_eligible": release_eligible,
        "cells": cells,
        "datasets": rows,
        "all_release_gates_passed": all_passed,
    }
    _atomic_json(args.output_dir / f"results-v3-{args.mode}.json", result)
    _atomic_json(
        args.output_dir / f"environment-v3-{args.mode}.json",
        _environment(config),
    )
    print(
        json.dumps(
            {
                "mode": args.mode,
                "gates_passed": gates_passed,
                "all_release_gates_passed": all_passed,
            }
        )
    )
    if not release_eligible:
        return 0
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
