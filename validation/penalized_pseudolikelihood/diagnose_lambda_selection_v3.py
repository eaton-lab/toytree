#!/usr/bin/env python

"""Diagnose validation-v3 lambda selection from existing fit caches."""

# ruff: noqa: E402 -- repository root must precede validation imports.

from __future__ import annotations

import argparse
import json
import platform
import sys
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import numpy as np
import scipy
from scipy.stats import spearmanr

import toytree
from validation.penalized_pseudolikelihood import run_validation_v3 as study

EPS = 1e-12
DEFAULT_BOOTSTRAP_SEED = 80260829
DEFAULT_BOOTSTRAP_REPLICATES = 2_000

RULES = {
    "pearson_mean_minimum": {
        "score": "pearson",
        "aggregation": "mean",
        "selection": "minimum",
    },
    "pearson_paired_one_se": {
        "score": "pearson",
        "aggregation": "mean",
        "selection": "paired_one_se_stronger_smoothing",
    },
    "relative_squared_mean_minimum": {
        "score": "relative_squared",
        "aggregation": "mean",
        "selection": "minimum",
    },
    "relative_squared_median_minimum": {
        "score": "relative_squared",
        "aggregation": "median",
        "selection": "minimum",
    },
    "relative_squared_trimmed_mean_minimum": {
        "score": "relative_squared",
        "aggregation": "trimmed_mean_10_percent",
        "selection": "minimum",
    },
}


def _prediction_scores(
    observed: np.ndarray,
    predicted: np.ndarray,
    score: str,
) -> np.ndarray:
    """Return fold prediction scores for one candidate."""
    expected = np.clip(np.asarray(predicted, dtype=float), EPS, None)
    values = np.asarray(observed, dtype=float)
    if score == "pearson":
        return (values - expected) ** 2 / expected
    if score == "relative_squared":
        return (values - expected) ** 2 / expected**2
    raise ValueError(f"unknown prediction score: {score}")


def _aggregate_scores(values: np.ndarray, aggregation: str) -> np.ndarray:
    """Aggregate candidate-by-fold scores along the fold axis."""
    if aggregation == "mean":
        return np.mean(values, axis=1)
    if aggregation == "median":
        return np.median(values, axis=1)
    if aggregation == "trimmed_mean_10_percent":
        ordered = np.sort(values, axis=1)
        trim = int(np.floor(0.1 * ordered.shape[1]))
        if trim:
            ordered = ordered[:, trim:-trim]
        return np.mean(ordered, axis=1)
    raise ValueError(f"unknown score aggregation: {aggregation}")


def _minimum_index(values: np.ndarray, lambdas: np.ndarray) -> int:
    """Return the minimum finite index, favoring stronger exact ties."""
    finite = np.isfinite(values)
    if not np.any(finite):
        raise RuntimeError("all lambda candidates have invalid diagnostic scores")
    minimum = float(np.min(values[finite]))
    tied = np.flatnonzero(finite & (np.abs(values - minimum) <= EPS))
    return int(tied[np.argmax(lambdas[tied])])


def _select_index(
    score_matrix: np.ndarray,
    valid: np.ndarray,
    lambdas: np.ndarray,
    rule: dict[str, str],
) -> tuple[int, np.ndarray]:
    """Select one candidate from paired candidate-by-fold scores."""
    summaries = _aggregate_scores(score_matrix, rule["aggregation"])
    summaries = np.where(valid, summaries, np.inf)
    minimum_idx = _minimum_index(summaries, lambdas)
    if rule["selection"] == "minimum":
        return minimum_idx, summaries

    minimum_scores = score_matrix[minimum_idx]
    eligible = []
    for idx in np.flatnonzero(valid):
        differences = score_matrix[idx] - minimum_scores
        paired_excess = float(np.mean(differences))
        paired_se = (
            float(np.std(differences, ddof=1) / np.sqrt(differences.size))
            if differences.size > 1
            else 0.0
        )
        if paired_excess <= paired_se + EPS:
            eligible.append(int(idx))
    selected_idx = max(eligible, key=lambda idx: float(lambdas[idx]))
    return selected_idx, summaries


def _candidate_arrays(
    record: dict[str, Any], score: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return sorted lambdas, validity, and candidate-by-fold scores."""
    candidates = sorted(record["candidates"], key=lambda item: float(item["lam"]))
    lambdas = np.asarray([item["lam"] for item in candidates], dtype=float)
    nfolds = {len(item["folds"]) for item in candidates}
    if len(nfolds) != 1 or not nfolds or next(iter(nfolds)) < 2:
        raise RuntimeError("candidate caches do not share at least two folds")
    valid = np.asarray(
        [
            bool(item["valid"])
            and all(bool(fold["converged"]) for fold in item["folds"])
            for item in candidates
        ],
        dtype=bool,
    )
    scores = []
    for item in candidates:
        observed = np.asarray([fold["observed"] for fold in item["folds"]])
        predicted = np.asarray([fold["predicted"] for fold in item["folds"]])
        values = _prediction_scores(observed, predicted, score)
        scores.append(values)
    matrix = np.asarray(scores, dtype=float)
    valid &= np.all(np.isfinite(matrix), axis=1)
    return lambdas, valid, matrix


def _population_risk(
    predicted: np.ndarray,
    true_means: np.ndarray,
    track: str,
    gamma_shape: float,
) -> float:
    """Return risk standardized by the data-generating variance."""
    means = np.asarray(true_means, dtype=float)
    estimates = np.asarray(predicted, dtype=float)
    if track == "gamma":
        variance = means**2 / float(gamma_shape)
    elif track == "count":
        variance = means
    else:
        raise ValueError(f"unknown simulation track: {track}")
    return float(np.mean((estimates - means) ** 2 / np.clip(variance, EPS, None)))


def _rate_spearman(true_rates: np.ndarray, fitted_rates: np.ndarray) -> float | None:
    """Return finite log-rate rank correlation or None."""
    value = float(spearmanr(np.log(true_rates), np.log(fitted_rates)).statistic)
    return value if np.isfinite(value) else None


def _fit_recovery(
    fit: dict[str, Any],
    oracle_fit: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, float | None]:
    """Return selected-versus-oracle age and rate recovery diagnostics."""
    ntips = int(record["ntips"])
    true_ages = np.asarray(record["true_ages"], dtype=float)
    selected_ages = np.asarray(fit["ages"], dtype=float)
    oracle_ages = np.asarray(oracle_fit["ages"], dtype=float)
    selected_age_rmse = float(
        np.sqrt(np.mean((selected_ages[ntips:] - true_ages[ntips:]) ** 2))
    )
    oracle_age_rmse = float(
        np.sqrt(np.mean((oracle_ages[ntips:] - true_ages[ntips:]) ** 2))
    )
    true_rates = np.asarray(record["true_rates"], dtype=float)
    selected_rho = _rate_spearman(true_rates, np.asarray(fit["rates"], dtype=float))
    oracle_rho = _rate_spearman(
        true_rates, np.asarray(oracle_fit["rates"], dtype=float)
    )
    return {
        "selected_age_rmse": selected_age_rmse,
        "oracle_age_rmse": oracle_age_rmse,
        "age_rmse_ratio": (
            None
            if record["calibration"] == "fixed_internal_ages"
            else selected_age_rmse / max(oracle_age_rmse, EPS)
        ),
        "selected_rate_spearman": selected_rho,
        "oracle_rate_spearman": oracle_rho,
        "rate_spearman_delta": (
            None
            if selected_rho is None or oracle_rho is None
            else selected_rho - oracle_rho
        ),
    }


def _bootstrap_selection(
    score_matrix: np.ndarray,
    valid: np.ndarray,
    lambdas: np.ndarray,
    rule: dict[str, str],
    selected_lam: float,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    """Return paired-fold bootstrap stability for one selection rule."""
    rng = np.random.default_rng(seed)
    selections = np.empty(replicates, dtype=float)
    nfolds = score_matrix.shape[1]
    for replicate in range(replicates):
        indices = rng.integers(0, nfolds, size=nfolds)
        selected_idx, _ = _select_index(score_matrix[:, indices], valid, lambdas, rule)
        selections[replicate] = lambdas[selected_idx]
    counts = Counter(float(value) for value in selections)
    modal_lam, modal_count = max(counts.items(), key=lambda item: (item[1], item[0]))
    boundaries = {float(lambdas[0]), float(lambdas[-1])}
    log_values = np.log10(selections)
    return {
        "selected_frequency": float(np.mean(selections == selected_lam)),
        "modal_lam": modal_lam,
        "modal_frequency": float(modal_count / replicates),
        "boundary_frequency": float(
            np.mean([float(value) in boundaries for value in selections])
        ),
        "log10_lam_10th_percentile": float(np.quantile(log_values, 0.1)),
        "log10_lam_90th_percentile": float(np.quantile(log_values, 0.9)),
    }


def _score_record(
    record: dict[str, Any],
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Diagnose all prespecified selection rules for one cached dataset."""
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
        return {**base, "message": record.get("message", "cached fit failed")}

    true_means = np.asarray(record["true_means"], dtype=float)
    risks = {}
    fits = {}
    for label, fit in record["full_fits"].items():
        lam = float(label)
        if fit["converged"]:
            fits[lam] = fit
            risks[lam] = _population_risk(
                np.asarray(fit["expected_branch_lengths"], dtype=float),
                true_means,
                record["track"],
                float(record["gamma_shape"]),
            )
    if not risks:
        return {**base, "status": "error", "message": "all full fits failed"}
    oracle_risk = min(risks.values())
    oracle_lam = max(
        lam for lam, risk in risks.items() if abs(risk - oracle_risk) <= EPS
    )
    oracle_fit = fits[oracle_lam]
    boundaries = {
        min(float(value) for value in record["full_fits"]),
        max(float(value) for value in record["full_fits"]),
    }

    rule_results = {}
    cached_selected = float(record["selected_lam"])
    for rule_index, (name, rule) in enumerate(RULES.items()):
        lambdas, valid, score_matrix = _candidate_arrays(record, rule["score"])
        selected_idx, summaries = _select_index(score_matrix, valid, lambdas, rule)
        selected_lam = float(lambdas[selected_idx])
        fit = fits.get(selected_lam)
        if fit is None:
            rule_results[name] = {
                "status": "error",
                "selected_lam": selected_lam,
                "message": "selected full fit did not converge",
            }
            continue
        selected_risk = risks[selected_lam]
        finite = np.asarray(
            [idx for idx, lam in enumerate(lambdas) if valid[idx] and lam in risks],
            dtype=int,
        )
        risk_order = np.asarray([risks[float(lambdas[idx])] for idx in finite])
        correlation = float(spearmanr(summaries[finite], risk_order).statistic)
        if not np.isfinite(correlation):
            correlation = None
        selected_scores = score_matrix[selected_idx]
        score_total = float(np.sum(selected_scores))
        recovery = _fit_recovery(fit, oracle_fit, record)
        rule_results[name] = {
            "status": "ok",
            "selected_lam": selected_lam,
            "selected_at_boundary": selected_lam in boundaries,
            "oracle_lam": oracle_lam,
            "log10_lam_distance": abs(np.log10(selected_lam) - np.log10(oracle_lam)),
            "selected_population_risk": selected_risk,
            "oracle_population_risk": oracle_risk,
            "absolute_excess_risk": selected_risk - oracle_risk,
            "relative_regret": (selected_risk - oracle_risk) / max(oracle_risk, EPS),
            "cv_population_risk_spearman": correlation,
            "largest_fold_score_fraction": (
                float(np.max(selected_scores) / score_total)
                if score_total > 0.0
                else 0.0
            ),
            "bootstrap": _bootstrap_selection(
                score_matrix,
                valid,
                lambdas,
                rule,
                selected_lam,
                bootstrap_replicates,
                bootstrap_seed + int(record["seed"]) + rule_index * 1_000_003,
            ),
            **recovery,
        }

    current = rule_results["pearson_mean_minimum"]
    if current.get("status") == "ok" and current["selected_lam"] != cached_selected:
        raise RuntimeError(
            "diagnostic current-rule selection does not reproduce cached selection: "
            f"{current['selected_lam']} != {cached_selected}"
        )
    return {
        **base,
        "cached_selected_lam": cached_selected,
        "dgp_matched_oracle_lam": oracle_lam,
        "dgp_matched_oracle_risk": oracle_risk,
        "valid_cv_candidates": int(
            sum(bool(item["valid"]) for item in record["candidates"])
        ),
        "total_cv_candidates": len(record["candidates"]),
        "converged_full_fits": len(fits),
        "total_full_fits": len(record["full_fits"]),
        "rules": rule_results,
    }


def _finite(rows: list[dict[str, Any]], rule: str, key: str) -> np.ndarray:
    """Return finite per-rule values from successful datasets."""
    values = []
    for row in rows:
        result = row.get("rules", {}).get(rule, {})
        value = result.get(key)
        if result.get("status") == "ok" and value is not None and np.isfinite(value):
            values.append(float(value))
    return np.asarray(values, dtype=float)


def _summarize_rule(rows: list[dict[str, Any]], rule: str) -> dict[str, Any]:
    """Aggregate one selection rule within a scenario-by-sigma cell."""
    successful = [
        row for row in rows if row.get("rules", {}).get(rule, {}).get("status") == "ok"
    ]
    excess = _finite(rows, rule, "absolute_excess_risk")
    relative = _finite(rows, rule, "relative_regret")
    distance = _finite(rows, rule, "log10_lam_distance")
    correlation = _finite(rows, rule, "cv_population_risk_spearman")
    concentration = _finite(rows, rule, "largest_fold_score_fraction")
    age_ratio = _finite(rows, rule, "age_rmse_ratio")
    rate_delta = _finite(rows, rule, "rate_spearman_delta")
    bootstrap_selected = np.asarray(
        [row["rules"][rule]["bootstrap"]["selected_frequency"] for row in successful]
    )
    bootstrap_boundary = np.asarray(
        [row["rules"][rule]["bootstrap"]["boundary_frequency"] for row in successful]
    )
    return {
        "datasets": len(rows),
        "successful_datasets": len(successful),
        "boundary_selection_fraction": float(
            np.mean([row["rules"][rule]["selected_at_boundary"] for row in successful])
        )
        if successful
        else None,
        "absolute_excess_risk_median": float(np.median(excess))
        if excess.size
        else None,
        "absolute_excess_risk_90th_percentile": (
            float(np.quantile(excess, 0.9)) if excess.size else None
        ),
        "relative_regret_median": (
            float(np.median(relative)) if relative.size else None
        ),
        "relative_regret_90th_percentile": (
            float(np.quantile(relative, 0.9)) if relative.size else None
        ),
        "log10_lam_distance_median": (
            float(np.median(distance)) if distance.size else None
        ),
        "cv_population_risk_spearman_median": (
            float(np.median(correlation)) if correlation.size else None
        ),
        "largest_fold_score_fraction_median": (
            float(np.median(concentration)) if concentration.size else None
        ),
        "bootstrap_selected_frequency_median": (
            float(np.median(bootstrap_selected)) if bootstrap_selected.size else None
        ),
        "bootstrap_boundary_frequency_median": (
            float(np.median(bootstrap_boundary)) if bootstrap_boundary.size else None
        ),
        "age_rmse_ratio_median": (
            float(np.median(age_ratio)) if age_ratio.size else None
        ),
        "rate_spearman_delta_median": (
            float(np.median(rate_delta)) if rate_delta.size else None
        ),
    }


def _aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return scenario-by-sigma summaries for every diagnostic rule."""
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
    for key, values in sorted(groups.items()):
        scenario, track, ntips, calibration, sigma, release_gate = key
        cells.append(
            {
                "scenario": scenario,
                "track": track,
                "ntips": ntips,
                "calibration": calibration,
                "sigma": sigma,
                "release_gate": release_gate,
                "rules": {rule: _summarize_rule(values, rule) for rule in RULES},
            }
        )
    return cells


def _diagnose_records(
    records: list[dict[str, Any]],
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Return a compact diagnostic artifact from existing cache records."""
    rows = [
        _score_record(record, bootstrap_replicates, bootstrap_seed)
        for record in records
    ]
    return {
        "study_version": 3,
        "kind": "lambda_selection_cache_diagnostic",
        "diagnostic_only": True,
        "changes_public_selector": False,
        "bootstrap_replicates": bootstrap_replicates,
        "bootstrap_seed": bootstrap_seed,
        "rules": RULES,
        "cells": _aggregate(rows),
        "datasets": rows,
    }


def main(argv: list[str] | None = None) -> int:
    """Read matching v3 caches and write a compact diagnostic artifact."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=("smoke", "pilot", "confirmation"), default="confirmation"
    )
    parser.add_argument("--output-dir", type=Path, default=study.HERE / "v3")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--bootstrap-replicates", type=int, default=DEFAULT_BOOTSTRAP_REPLICATES
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    args = parser.parse_args(argv)
    if args.bootstrap_replicates < 1:
        parser.error("--bootstrap-replicates must be positive")

    config = json.loads(study.CONFIG_PATH.read_text())
    payloads, _ = study._payloads(config, args.mode, args.output_dir, resume=True)
    records = study._read_records(payloads)
    result = _diagnose_records(records, args.bootstrap_replicates, args.seed)
    result.update(
        {
            "mode": args.mode,
            "config_hash": study._json_hash(config),
            "source_hash": study._source_hash(),
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "numpy": np.__version__,
                "scipy": scipy.__version__,
                "toytree": toytree.__version__,
            },
        }
    )
    output = args.output or args.output_dir / f"diagnostics-v3-{args.mode}.json"
    study._atomic_json(output, result)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(result["datasets"]),
                "output": str(output),
                "diagnostic_only": True,
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
