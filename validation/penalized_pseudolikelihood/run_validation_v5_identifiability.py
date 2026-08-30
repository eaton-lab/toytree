#!/usr/bin/env python

"""Diagnose when correlated-rate lambda is identifiable by terminal LOOCV."""

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
from collections import Counter
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
    _simulate_dataset,
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v5.json"
CACHE_SCHEMA_VERSION = 1
EPS = 1e-12


def _json_hash(value: Any) -> str:
    """Return a stable hash for JSON-native data."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    """Write JSON atomically so interrupted workers cannot leave valid caches."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _calibrations(true_tree: toytree.ToyTree, regime: str) -> dict[int, Any]:
    """Return deterministic calibration controls for the v5 study."""
    if regime == "fixed_internal_ages":
        return {
            int(node.idx): float(node.height)
            for node in true_tree.treenode.traverse("preorder")
            if not node.is_leaf()
        }
    if regime == "root_and_internal_interval":
        candidates = [
            node
            for node in true_tree.treenode.traverse("preorder")
            if not node.is_root() and not node.is_leaf()
        ]
        node = max(candidates, key=lambda value: (value.height, value.idx))
        age = float(node.height)
        return {-1: 1.0, int(node.idx): (age * 0.9, age * 1.1)}
    if regime == "root_and_three_internal_intervals":
        available = [
            node
            for node in true_tree.treenode.traverse("preorder")
            if not node.is_root() and not node.is_leaf()
        ]
        if len(available) < 3:
            raise ValueError("three-interval calibration requires three internal nodes")
        calibrations: dict[int, Any] = {-1: 1.0}
        for target in (0.25, 0.50, 0.75):
            node = min(
                available,
                key=lambda value: (abs(float(value.height) - target), value.idx),
            )
            available.remove(node)
            age = float(node.height)
            calibrations[int(node.idx)] = (age * 0.9, age * 1.1)
        return calibrations
    raise ValueError(f"unknown calibration regime: {regime}")


def _source_hash() -> str:
    """Hash only estimator and data-generation code that affects fitted values."""
    digest = hashlib.sha256()
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    for name in ("correlated.py", "lambda_cv.py", "utils.py"):
        path = root / name
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    for function in (_simulate_dataset, _calibrations, _slim_fit, _fit_worker):
        digest.update(inspect.getsource(function).encode())
    return digest.hexdigest()


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    """Return the unique cache path for one factorial dataset."""
    sigma = str(payload["sigma"]).replace(".", "p")
    shape = str(payload["gamma_shape"]).replace(".", "p")
    name = (
        f"{payload['scenario']}-n{payload['ntips']}-{payload['calibration']}-"
        f"shape{shape}-sigma{sigma}-r{payload['replicate']:04d}.json"
    )
    return output_dir / "cache-v5" / payload["mode"] / name


def _slim_fit(fit: dict[str, Any]) -> dict[str, Any]:
    """Return JSON-native fitted quantities needed for later rescoring."""
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
    """Simulate, cross-validate, and fit the full lambda grid for one dataset."""
    path = Path(payload["cache_path"])
    if payload["resume"] and path.exists():
        try:
            cached = json.loads(path.read_text())
            if cached.get("fingerprint") == payload["fingerprint"]:
                return str(path)
        except (OSError, json.JSONDecodeError):
            pass

    keys = (
        "mode",
        "scenario",
        "ntips",
        "calibration",
        "baseline_rate",
        "gamma_shape",
        "sigma",
        "replicate",
        "seed",
        "fingerprint",
    )
    record = {key: payload[key] for key in keys}
    record["cache_schema_version"] = CACHE_SCHEMA_VERSION
    try:
        simulation = dict(payload["simulation"])
        simulation["correlated_log_sigma"] = float(payload["sigma"])
        true_tree, observed_tree, true_rates, true_means, observed = _simulate_dataset(
            "correlated",
            int(payload["ntips"]),
            "gamma",
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
                "candidates": candidates,
                "full_fits": full_fits,
            }
        )
    except Exception as exc:
        record.update({"status": "error", "message": f"{type(exc).__name__}: {exc}"})
    _atomic_json(path, record)
    return str(path)


def _population_risk(
    predicted: np.ndarray, true_means: np.ndarray, gamma_shape: float
) -> float:
    """Return squared prediction error standardized by Gamma variance."""
    means = np.asarray(true_means, dtype=float)
    estimates = np.asarray(predicted, dtype=float)
    variance = means**2 / float(gamma_shape)
    return float(np.mean((estimates - means) ** 2 / np.clip(variance, EPS, None)))


def _rate_spearman(true_rates: np.ndarray, fitted_rates: np.ndarray) -> float | None:
    """Return finite log-rate rank correlation, or None when degenerate."""
    truth = np.log(np.asarray(true_rates, dtype=float))
    fitted = np.log(np.asarray(fitted_rates, dtype=float))
    if np.ptp(truth) <= EPS or np.ptp(fitted) <= EPS:
        return None
    value = float(spearmanr(truth, fitted).statistic)
    return value if np.isfinite(value) else None


def _boundary_label(value: float, lambdas: np.ndarray) -> str:
    """Label a candidate as the lower boundary, upper boundary, or interior."""
    if value == float(lambdas[0]):
        return "lower"
    if value == float(lambdas[-1]):
        return "upper"
    return "interior"


def _candidate_arrays(
    record: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return sorted lambdas, valid flags, and paired Pearson fold scores."""
    candidates = sorted(record["candidates"], key=lambda value: value["lam"])
    lambdas = np.asarray([value["lam"] for value in candidates], dtype=float)
    valid = np.asarray(
        [
            bool(value["valid"])
            and all(bool(fold["converged"]) for fold in value["folds"])
            for value in candidates
        ],
        dtype=bool,
    )
    counts = {len(value["folds"]) for value in candidates}
    if len(counts) != 1 or not counts or next(iter(counts)) < 2:
        raise RuntimeError("candidate caches do not share at least two folds")
    matrix = np.asarray(
        [[float(fold["score"]) for fold in value["folds"]] for value in candidates],
        dtype=float,
    )
    valid &= np.all(np.isfinite(matrix), axis=1)
    return lambdas, valid, matrix


def _bootstrap_selection(
    record: dict[str, Any], replicates: int, seed: int
) -> dict[str, Any]:
    """Measure paired-fold selection uncertainty without refitting."""
    lambdas, valid, matrix = _candidate_arrays(record)
    if not np.any(valid):
        raise RuntimeError("all lambda candidates have invalid fold scores")
    rng = np.random.default_rng(seed)
    selections = np.empty(replicates, dtype=float)
    for idx in range(replicates):
        columns = rng.integers(0, matrix.shape[1], size=matrix.shape[1])
        scores = np.mean(matrix[:, columns], axis=1)
        scores = np.where(valid, scores, np.inf)
        minimum = float(np.min(scores))
        tied = np.flatnonzero(np.abs(scores - minimum) <= EPS)
        selections[idx] = float(lambdas[tied[np.argmax(lambdas[tied])]])
    counts = Counter(float(value) for value in selections)
    modal_lam, modal_count = max(counts.items(), key=lambda value: (value[1], value[0]))
    log_values = np.log10(selections)
    lower = float(np.quantile(log_values, 0.1))
    upper = float(np.quantile(log_values, 0.9))
    selected = float(record["selected_lam"])
    boundaries = {float(lambdas[0]), float(lambdas[-1])}
    return {
        "replicates": int(replicates),
        "selected_frequency": float(np.mean(selections == selected)),
        "modal_lam": float(modal_lam),
        "modal_frequency": float(modal_count / replicates),
        "boundary_frequency": float(
            np.mean([float(value) in boundaries for value in selections])
        ),
        "log10_lam_10th_percentile": lower,
        "log10_lam_90th_percentile": upper,
        "log10_lam_80_percent_width": upper - lower,
    }


def _score_record(
    record: dict[str, Any], bootstrap_replicates: int, bootstrap_seed: int
) -> dict[str, Any]:
    """Score one selected lambda against its population-risk grid oracle."""
    base_keys = (
        "status",
        "scenario",
        "ntips",
        "calibration",
        "baseline_rate",
        "gamma_shape",
        "sigma",
        "replicate",
        "seed",
    )
    base = {key: record[key] for key in base_keys}
    if record["status"] != "ok":
        return {**base, "message": record.get("message", "")}

    true_means = np.asarray(record["true_means"], dtype=float)
    true_ages = np.asarray(record["true_ages"], dtype=float)
    true_rates = np.asarray(record["true_rates"], dtype=float)
    risks = {}
    for label, fit in record["full_fits"].items():
        if fit["converged"]:
            risks[float(label)] = _population_risk(
                np.asarray(fit["expected_branch_lengths"], dtype=float),
                true_means,
                float(record["gamma_shape"]),
            )
    if not risks:
        return {**base, "status": "error", "message": "all full-grid fits failed"}

    oracle_risk = min(risks.values())
    oracle_lam = max(
        lam for lam, risk in risks.items() if abs(risk - oracle_risk) <= EPS
    )
    selected_lam = float(record["selected_lam"])
    selected_fit = record["full_fits"].get(str(selected_lam))
    oracle_fit = record["full_fits"][str(oracle_lam)]
    if selected_fit is None or not selected_fit["converged"]:
        return {
            **base,
            "status": "error",
            "message": "selected full-grid fit did not converge",
        }

    lambdas, valid, matrix = _candidate_arrays(record)
    summaries = np.mean(matrix, axis=1)
    common = np.asarray(
        [idx for idx, lam in enumerate(lambdas) if valid[idx] and lam in risks],
        dtype=int,
    )
    risk_order = np.asarray([risks[float(lambdas[idx])] for idx in common])
    correlation = None
    if common.size > 1 and np.ptp(summaries[common]) > EPS and np.ptp(risk_order) > EPS:
        value = float(spearmanr(summaries[common], risk_order).statistic)
        correlation = value if np.isfinite(value) else None

    internal = slice(int(record["ntips"]), None)
    selected_ages = np.asarray(selected_fit["ages"], dtype=float)
    oracle_ages = np.asarray(oracle_fit["ages"], dtype=float)
    selected_age_rmse = float(
        np.sqrt(np.mean((selected_ages[internal] - true_ages[internal]) ** 2))
    )
    oracle_age_rmse = float(
        np.sqrt(np.mean((oracle_ages[internal] - true_ages[internal]) ** 2))
    )
    selected_rho = _rate_spearman(
        true_rates, np.asarray(selected_fit["rates"], dtype=float)
    )
    oracle_rho = _rate_spearman(
        true_rates, np.asarray(oracle_fit["rates"], dtype=float)
    )
    selected_risk = risks[selected_lam]
    selected_boundary = _boundary_label(selected_lam, lambdas)
    oracle_boundary = _boundary_label(float(oracle_lam), lambdas)
    folds = [fold for value in record["candidates"] for fold in value["folds"]]
    fixed_ages = record["calibration"] == "fixed_internal_ages"
    return {
        **base,
        "selected_lam": selected_lam,
        "oracle_lam": float(oracle_lam),
        "theoretical_lam": float(1.0 / (2.0 * float(record["sigma"]) ** 2)),
        "selected_boundary": selected_boundary,
        "oracle_boundary": oracle_boundary,
        "boundary_disagreement": bool(
            selected_boundary != oracle_boundary
            and (
                "interior" in {selected_boundary, oracle_boundary}
                or {selected_boundary, oracle_boundary} == {"lower", "upper"}
            )
        ),
        "all_candidates_converged": bool(
            all(value["valid"] for value in record["candidates"])
            and all(value["converged"] for value in record["full_fits"].values())
        ),
        "folds_converged": int(sum(fold["converged"] for fold in folds)),
        "folds_total": len(folds),
        "selected_population_risk": float(selected_risk),
        "oracle_population_risk": float(oracle_risk),
        "population_excess_risk": float(selected_risk - oracle_risk),
        "population_regret": float(
            (selected_risk - oracle_risk) / max(oracle_risk, EPS)
        ),
        "cv_population_risk_spearman": correlation,
        "selected_age_rmse": selected_age_rmse,
        "oracle_age_rmse": oracle_age_rmse,
        "age_rmse_ratio": (
            None if fixed_ages else float(selected_age_rmse / max(oracle_age_rmse, EPS))
        ),
        "selected_rate_spearman": selected_rho,
        "oracle_rate_spearman": oracle_rho,
        "rate_spearman_delta": (
            None
            if selected_rho is None or oracle_rho is None
            else float(selected_rho - oracle_rho)
        ),
        "bootstrap": _bootstrap_selection(
            record,
            bootstrap_replicates,
            bootstrap_seed + int(record["seed"]),
        ),
    }


def _finite(rows: list[dict[str, Any]], key: str) -> np.ndarray:
    """Return finite values for a metric from successful dataset rows."""
    values = [
        value
        for row in rows
        if row.get("status") == "ok"
        and (value := row.get(key)) is not None
        and np.isfinite(value)
    ]
    return np.asarray(values, dtype=float)


def _summarize_cell(
    rows: list[dict[str, Any]], gates: dict[str, float]
) -> dict[str, Any]:
    """Summarize one factorial cell and apply development decision gates."""
    successes = [row for row in rows if row.get("status") == "ok"]
    fold_total = sum(row.get("folds_total", 0) for row in successes)
    fold_ok = sum(row.get("folds_converged", 0) for row in successes)
    dataset_convergence = sum(
        row.get("all_candidates_converged", False) for row in successes
    ) / len(rows)
    regret = _finite(rows, "population_regret")
    age_ratio = _finite(rows, "age_rmse_ratio")
    rate_delta = _finite(rows, "rate_spearman_delta")
    excess = _finite(rows, "population_excess_risk")
    correlation = _finite(rows, "cv_population_risk_spearman")
    bootstrap_width = np.asarray(
        [row["bootstrap"]["log10_lam_80_percent_width"] for row in successes],
        dtype=float,
    )
    bootstrap_selected = np.asarray(
        [row["bootstrap"]["selected_frequency"] for row in successes], dtype=float
    )
    metrics = {
        "datasets": len(rows),
        "dataset_convergence": float(dataset_convergence),
        "fold_convergence": float(fold_ok / fold_total) if fold_total else 0.0,
        "population_regret_median": float(np.median(regret)) if regret.size else None,
        "population_regret_90th_percentile": (
            float(np.quantile(regret, 0.9)) if regret.size else None
        ),
        "population_excess_risk_median": (
            float(np.median(excess)) if excess.size else None
        ),
        "population_excess_risk_90th_percentile": (
            float(np.quantile(excess, 0.9)) if excess.size else None
        ),
        "age_rmse_ratio_median": (
            float(np.median(age_ratio)) if age_ratio.size else None
        ),
        "rate_spearman_delta_median": (
            float(np.median(rate_delta)) if rate_delta.size else None
        ),
        "cv_population_risk_spearman_median": (
            float(np.median(correlation)) if correlation.size else None
        ),
        "bootstrap_log10_width_median": (
            float(np.median(bootstrap_width)) if bootstrap_width.size else None
        ),
        "bootstrap_selected_frequency_median": (
            float(np.median(bootstrap_selected)) if bootstrap_selected.size else None
        ),
        "selected_lower_boundary_fraction": float(
            np.mean([row["selected_boundary"] == "lower" for row in successes])
        )
        if successes
        else None,
        "oracle_lower_boundary_fraction": float(
            np.mean([row["oracle_boundary"] == "lower" for row in successes])
        )
        if successes
        else None,
        "boundary_disagreement_fraction": float(
            np.mean([row["boundary_disagreement"] for row in successes])
        )
        if successes
        else None,
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
    }
    return {**metrics, "checks": checks, "passed": bool(all(checks.values()))}


def _payloads(
    config: dict[str, Any], mode: str, output_dir: Path, resume: bool
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Expand the factorial design into deterministic dataset payloads."""
    source_hash = _source_hash()
    payloads = []
    seed_rows = []
    index = 0
    for scenario in config[mode]:
        for ntips in scenario["ntips"]:
            for calibration in scenario["calibrations"]:
                for gamma_shape in scenario["gamma_shapes"]:
                    for sigma in scenario["sigmas"]:
                        for replicate in range(int(scenario["replicates"])):
                            seed = int(config["development_seed"] + index)
                            index += 1
                            simulation = {
                                **config["simulation"],
                                "gamma_shape": float(gamma_shape),
                            }
                            core = {
                                "mode": mode,
                                "scenario": scenario["name"],
                                "ntips": int(ntips),
                                "calibration": calibration,
                                "baseline_rate": float(simulation["baseline_rate"]),
                                "gamma_shape": float(gamma_shape),
                                "sigma": float(sigma),
                                "replicate": int(replicate),
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
                                "resume": bool(resume),
                            }
                            payload["cache_path"] = str(
                                _cache_path(output_dir, payload)
                            )
                            payloads.append(payload)
                            seed_rows.append(
                                {
                                    "scenario": scenario["name"],
                                    "ntips": int(ntips),
                                    "calibration": calibration,
                                    "gamma_shape": float(gamma_shape),
                                    "sigma": float(sigma),
                                    "replicate": int(replicate),
                                    "seed": seed,
                                }
                            )
    return payloads, seed_rows


def _progress(completed: int, total: int, started: float, path: str) -> None:
    """Print one machine-readable dataset completion record."""
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
    payloads: list[dict[str, Any]], ncores: int, progress_every: int
) -> None:
    """Run independent datasets serially or in a deterministic process pool."""
    started = time.monotonic()
    total = len(payloads)
    if ncores == 1:
        for completed, payload in enumerate(payloads, start=1):
            path = _fit_worker(payload)
            if completed % progress_every == 0 or completed == total:
                _progress(completed, total, started, path)
        return
    with ProcessPoolExecutor(max_workers=min(ncores, total)) as pool:
        futures = [pool.submit(_fit_worker, payload) for payload in payloads]
        for completed, future in enumerate(as_completed(futures), start=1):
            path = future.result()
            if completed % progress_every == 0 or completed == total:
                _progress(completed, total, started, path)


def _read_records(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Read matching caches or reject an incomplete or stale fit stage."""
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
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Aggregate factorial cells and identify development candidates."""
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            row["scenario"],
            int(row["ntips"]),
            row["calibration"],
            float(row["gamma_shape"]),
            float(row["sigma"]),
        )
        groups.setdefault(key, []).append(row)
    cells = []
    candidates = []
    for key, values in sorted(groups.items()):
        scenario, ntips, calibration, gamma_shape, sigma = key
        summary = _summarize_cell(values, gates)
        cell = {
            "scenario": scenario,
            "ntips": ntips,
            "calibration": calibration,
            "gamma_shape": gamma_shape,
            "sigma": sigma,
            **summary,
        }
        cells.append(cell)
        if summary["passed"]:
            candidates.append(
                {
                    "scenario": scenario,
                    "ntips": ntips,
                    "calibration": calibration,
                    "gamma_shape": gamma_shape,
                    "sigma": sigma,
                }
            )
    return cells, candidates


def _environment(config: dict[str, Any]) -> dict[str, Any]:
    """Return reproducibility metadata for the development study."""
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
    """Run a fit or score stage of the v5 identifiability pilot."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("smoke", "pilot"), default="pilot")
    parser.add_argument("--stage", choices=("all", "fit", "score"), default="all")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE / "v5")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument("--bootstrap-replicates", type=int)
    args = parser.parse_args(argv)
    if args.ncores < 1:
        parser.error("--ncores must be positive")
    if args.progress_every < 1:
        parser.error("--progress-every must be positive")

    config = json.loads(CONFIG_PATH.read_text())
    bootstrap_replicates = (
        int(config["bootstrap_replicates"])
        if args.bootstrap_replicates is None
        else int(args.bootstrap_replicates)
    )
    if bootstrap_replicates < 1:
        parser.error("--bootstrap-replicates must be positive")
    payloads, seed_rows = _payloads(
        config, args.mode, args.output_dir, not args.no_resume
    )
    if args.stage in {"all", "fit"}:
        _run_workers(payloads, args.ncores, args.progress_every)
        _atomic_json(
            args.output_dir / f"seeds-v5-{args.mode}.json",
            {"study_version": 5, "mode": args.mode, "datasets": seed_rows},
        )
        if args.stage == "fit":
            print(json.dumps({"mode": args.mode, "datasets": len(payloads)}))
            return 0

    records = _read_records(payloads)
    rows = [
        _score_record(
            record,
            bootstrap_replicates,
            int(config["bootstrap_seed"]),
        )
        for record in records
    ]
    cells, candidates = _aggregate(rows, config["decision_gates"])
    result = {
        "study_version": 5,
        "mode": args.mode,
        "scope": "correlated_lambda_identifiability",
        "diagnostic_only": True,
        "release_eligible": False,
        "changes_public_selector": False,
        "rscv_in_scope": False,
        "bootstrap_replicates": bootstrap_replicates,
        "cells": cells,
        "confirmation_candidates": candidates,
        "datasets": rows,
        "all_release_gates_passed": False,
    }
    _atomic_json(args.output_dir / f"results-v5-{args.mode}.json", result)
    _atomic_json(
        args.output_dir / f"environment-v5-{args.mode}.json", _environment(config)
    )
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(rows),
                "confirmation_candidates": len(candidates),
                "diagnostic_only": True,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
