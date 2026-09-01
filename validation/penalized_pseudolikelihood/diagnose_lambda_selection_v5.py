#!/usr/bin/env python

"""Compare lambda-selection scores using existing validation-v5 caches."""

# ruff: noqa: E402 -- repository root must precede validation imports.

from __future__ import annotations

import argparse
import hashlib
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
from validation.penalized_pseudolikelihood import (
    run_validation_v5_identifiability as study,
)

EPS = 1e-12
DEFAULT_BOOTSTRAP_REPLICATES = 2_000
DEFAULT_BOOTSTRAP_SEED = 92260829
RISK_THRESHOLDS = (0.15, 0.50)
RULES = {
    "pearson_mean_minimum": "pearson",
    "relative_squared_mean_minimum": "relative_squared",
    "gamma_deviance_mean_minimum": "gamma_deviance",
}


def _prediction_scores(
    observed: np.ndarray, predicted: np.ndarray, score: str
) -> np.ndarray:
    """Return per-fold prediction scores for one candidate."""
    values = np.clip(np.asarray(observed, dtype=float), EPS, None)
    expected = np.clip(np.asarray(predicted, dtype=float), EPS, None)
    if score == "pearson":
        return (values - expected) ** 2 / expected
    if score == "relative_squared":
        return (values - expected) ** 2 / expected**2
    if score == "gamma_deviance":
        ratio = values / expected
        return 2.0 * (ratio - np.log(ratio) - 1.0)
    raise ValueError(f"unknown prediction score: {score}")


def _candidate_arrays(
    record: dict[str, Any], score: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return sorted lambdas, validity, and paired candidate-by-fold scores."""
    candidates = sorted(record["candidates"], key=lambda item: float(item["lam"]))
    lambdas = np.asarray([item["lam"] for item in candidates], dtype=float)
    counts = {len(item["folds"]) for item in candidates}
    if len(counts) != 1 or not counts or next(iter(counts)) < 2:
        raise RuntimeError("candidate caches do not share at least two folds")
    valid = np.asarray(
        [
            bool(item["valid"])
            and all(bool(fold["converged"]) for fold in item["folds"])
            for item in candidates
        ],
        dtype=bool,
    )
    rows = []
    for item in candidates:
        observed = np.asarray([fold["observed"] for fold in item["folds"]])
        predicted = np.asarray([fold["predicted"] for fold in item["folds"]])
        rows.append(_prediction_scores(observed, predicted, score))
    matrix = np.asarray(rows, dtype=float)
    valid &= np.all(np.isfinite(matrix), axis=1)
    return lambdas, valid, matrix


def _minimum_index(values: np.ndarray, lambdas: np.ndarray) -> int:
    """Return the minimum finite index, favoring stronger smoothing on ties."""
    finite = np.isfinite(values)
    if not np.any(finite):
        raise RuntimeError("all lambda candidates have invalid scores")
    minimum = float(np.min(values[finite]))
    tied = np.flatnonzero(finite & (np.abs(values - minimum) <= EPS))
    return int(tied[np.argmax(lambdas[tied])])


def _select(
    score_matrix: np.ndarray, valid: np.ndarray, lambdas: np.ndarray
) -> tuple[int, np.ndarray]:
    """Select the minimum mean score among valid candidates."""
    summaries = np.mean(score_matrix, axis=1)
    summaries = np.where(valid, summaries, np.inf)
    return _minimum_index(summaries, lambdas), summaries


def _bootstrap_selection(
    score_matrix: np.ndarray,
    valid: np.ndarray,
    lambdas: np.ndarray,
    selected_lam: float,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    """Return deterministic paired-fold bootstrap uncertainty."""
    rng = np.random.default_rng(seed)
    selections = np.empty(replicates, dtype=float)
    for idx in range(replicates):
        columns = rng.integers(0, score_matrix.shape[1], size=score_matrix.shape[1])
        selected, _ = _select(score_matrix[:, columns], valid, lambdas)
        selections[idx] = lambdas[selected]
    counts = Counter(float(value) for value in selections)
    modal_lam, modal_count = max(counts.items(), key=lambda item: (item[1], item[0]))
    log_values = np.log10(selections)
    lower = float(np.quantile(log_values, 0.1))
    upper = float(np.quantile(log_values, 0.9))
    boundaries = {float(lambdas[0]), float(lambdas[-1])}
    return {
        "selected_frequency": float(np.mean(selections == selected_lam)),
        "modal_lam": float(modal_lam),
        "modal_frequency": float(modal_count / replicates),
        "boundary_frequency": float(
            np.mean([float(value) in boundaries for value in selections])
        ),
        "log10_lam_10th_percentile": lower,
        "log10_lam_90th_percentile": upper,
        "log10_lam_80_percent_width": upper - lower,
    }


def _population_risks(record: dict[str, Any]) -> dict[float, float]:
    """Return matched Gamma population risks for converged full-grid fits."""
    truth = np.asarray(record["true_means"], dtype=float)
    risks = {}
    for label, fit in record["full_fits"].items():
        if fit["converged"]:
            risks[float(label)] = study._population_risk(
                np.asarray(fit["expected_branch_lengths"], dtype=float),
                truth,
                float(record["gamma_shape"]),
            )
    return risks


def _risk_equivalent_ranges(
    risks: dict[float, float], thresholds: tuple[float, ...] = RISK_THRESHOLDS
) -> dict[str, Any]:
    """Return lambda ranges within each relative-regret threshold."""
    oracle = min(risks.values())
    result = {}
    for threshold in thresholds:
        eligible = sorted(
            lam
            for lam, risk in risks.items()
            if (risk - oracle) / max(oracle, EPS) <= threshold + EPS
        )
        lower = float(eligible[0])
        upper = float(eligible[-1])
        result[f"relative_regret_{threshold:.2f}"] = {
            "count": len(eligible),
            "min_lam": lower,
            "max_lam": upper,
            "log10_width": float(np.log10(upper) - np.log10(lower)),
        }
    return result


def _fit_recovery(
    fit: dict[str, Any], oracle_fit: dict[str, Any], record: dict[str, Any]
) -> dict[str, float | None]:
    """Return age and rate recovery relative to the population-risk oracle."""
    ntips = int(record["ntips"])
    truth_ages = np.asarray(record["true_ages"], dtype=float)
    selected_ages = np.asarray(fit["ages"], dtype=float)
    oracle_ages = np.asarray(oracle_fit["ages"], dtype=float)
    selected_age_rmse = float(
        np.sqrt(np.mean((selected_ages[ntips:] - truth_ages[ntips:]) ** 2))
    )
    oracle_age_rmse = float(
        np.sqrt(np.mean((oracle_ages[ntips:] - truth_ages[ntips:]) ** 2))
    )
    truth_rates = np.asarray(record["true_rates"], dtype=float)
    selected_rho = study._rate_spearman(
        truth_rates, np.asarray(fit["rates"], dtype=float)
    )
    oracle_rho = study._rate_spearman(
        truth_rates, np.asarray(oracle_fit["rates"], dtype=float)
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


def _score_rule(
    record: dict[str, Any],
    score: str,
    risks: dict[float, float],
    oracle_lam: float,
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Score one selection rule against the shared full-fit oracle."""
    lambdas, valid, matrix = _candidate_arrays(record, score)
    selected_idx, summaries = _select(matrix, valid, lambdas)
    selected_lam = float(lambdas[selected_idx])
    fit = record["full_fits"].get(str(selected_lam))
    if fit is None or not fit["converged"] or selected_lam not in risks:
        return {
            "status": "error",
            "selected_lam": selected_lam,
            "message": "selected full-grid fit did not converge",
        }
    finite = np.asarray(
        [idx for idx, lam in enumerate(lambdas) if valid[idx] and lam in risks],
        dtype=int,
    )
    risk_order = np.asarray([risks[float(lambdas[idx])] for idx in finite])
    correlation = None
    if finite.size > 1 and np.ptp(summaries[finite]) > EPS and np.ptp(risk_order) > EPS:
        value = float(spearmanr(summaries[finite], risk_order).statistic)
        correlation = value if np.isfinite(value) else None
    oracle_risk = risks[oracle_lam]
    selected_risk = risks[selected_lam]
    return {
        "status": "ok",
        "score": score,
        "selected_lam": selected_lam,
        "selected_boundary": study._boundary_label(selected_lam, lambdas),
        "oracle_lam": float(oracle_lam),
        "oracle_boundary": study._boundary_label(oracle_lam, lambdas),
        "selected_population_risk": float(selected_risk),
        "oracle_population_risk": float(oracle_risk),
        "population_excess_risk": float(selected_risk - oracle_risk),
        "population_regret": float(
            (selected_risk - oracle_risk) / max(oracle_risk, EPS)
        ),
        "within_15_percent_oracle_risk": bool(
            (selected_risk - oracle_risk) / max(oracle_risk, EPS) <= 0.15 + EPS
        ),
        "within_50_percent_oracle_risk": bool(
            (selected_risk - oracle_risk) / max(oracle_risk, EPS) <= 0.50 + EPS
        ),
        "cv_population_risk_spearman": correlation,
        "bootstrap": _bootstrap_selection(
            matrix,
            valid,
            lambdas,
            selected_lam,
            bootstrap_replicates,
            bootstrap_seed,
        ),
        **_fit_recovery(fit, record["full_fits"][str(oracle_lam)], record),
    }


def _score_record(
    record: dict[str, Any], bootstrap_replicates: int, bootstrap_seed: int
) -> dict[str, Any]:
    """Apply every cache-only rule to one fitted dataset."""
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
    risks = _population_risks(record)
    if not risks:
        return {**base, "status": "error", "message": "all full-grid fits failed"}
    oracle_risk = min(risks.values())
    oracle_lam = max(
        lam for lam, risk in risks.items() if abs(risk - oracle_risk) <= EPS
    )
    rule_results = {}
    for index, (name, score) in enumerate(RULES.items()):
        rule_results[name] = _score_rule(
            record,
            score,
            risks,
            oracle_lam,
            bootstrap_replicates,
            bootstrap_seed + int(record["seed"]) + index * 1_000_003,
        )
    pearson = rule_results["pearson_mean_minimum"]
    if pearson.get("status") == "ok" and pearson["selected_lam"] != float(
        record["selected_lam"]
    ):
        raise RuntimeError("Pearson diagnostic does not reproduce cached selection")
    folds = [fold for item in record["candidates"] for fold in item["folds"]]
    return {
        **base,
        "oracle_lam": float(oracle_lam),
        "oracle_population_risk": float(oracle_risk),
        "risk_equivalent_ranges": _risk_equivalent_ranges(risks),
        "all_candidates_converged": bool(
            all(item["valid"] for item in record["candidates"])
            and all(fit["converged"] for fit in record["full_fits"].values())
        ),
        "folds_converged": int(sum(fold["converged"] for fold in folds)),
        "folds_total": len(folds),
        "rules": rule_results,
    }


def _finite(rows: list[dict[str, Any]], rule: str, key: str) -> np.ndarray:
    """Return finite values for one rule metric."""
    values = []
    for row in rows:
        result = row.get("rules", {}).get(rule, {})
        value = result.get(key)
        if result.get("status") == "ok" and value is not None and np.isfinite(value):
            values.append(float(value))
    return np.asarray(values, dtype=float)


def _summarize_rule(
    rows: list[dict[str, Any]], rule: str, gates: dict[str, float]
) -> dict[str, Any]:
    """Summarize and gate one rule within a factorial cell."""
    successful = [
        row for row in rows if row.get("rules", {}).get(rule, {}).get("status") == "ok"
    ]
    fold_total = sum(row.get("folds_total", 0) for row in successful)
    fold_ok = sum(row.get("folds_converged", 0) for row in successful)
    dataset_convergence = sum(
        row.get("all_candidates_converged", False) for row in successful
    ) / len(rows)
    regret = _finite(rows, rule, "population_regret")
    age_ratio = _finite(rows, rule, "age_rmse_ratio")
    rate_delta = _finite(rows, rule, "rate_spearman_delta")
    correlation = _finite(rows, rule, "cv_population_risk_spearman")
    widths = np.asarray(
        [
            row["rules"][rule]["bootstrap"]["log10_lam_80_percent_width"]
            for row in successful
        ]
    )
    selected_frequency = np.asarray(
        [row["rules"][rule]["bootstrap"]["selected_frequency"] for row in successful]
    )
    equivalent_width = np.asarray(
        [
            row["risk_equivalent_ranges"]["relative_regret_0.15"]["log10_width"]
            for row in successful
        ]
    )
    metrics = {
        "datasets": len(rows),
        "successful_datasets": len(successful),
        "dataset_convergence": float(dataset_convergence),
        "fold_convergence": float(fold_ok / fold_total) if fold_total else 0.0,
        "population_regret_median": float(np.median(regret)) if regret.size else None,
        "population_regret_90th_percentile": (
            float(np.quantile(regret, 0.9)) if regret.size else None
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
            float(np.median(widths)) if widths.size else None
        ),
        "bootstrap_selected_frequency_median": (
            float(np.median(selected_frequency)) if selected_frequency.size else None
        ),
        "risk_equivalent_15pct_log10_width_median": (
            float(np.median(equivalent_width)) if equivalent_width.size else None
        ),
        "within_15_percent_oracle_fraction": float(
            np.mean(
                [
                    row["rules"][rule]["within_15_percent_oracle_risk"]
                    for row in successful
                ]
            )
        )
        if successful
        else None,
        "within_50_percent_oracle_fraction": float(
            np.mean(
                [
                    row["rules"][rule]["within_50_percent_oracle_risk"]
                    for row in successful
                ]
            )
        )
        if successful
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


def _aggregate(
    rows: list[dict[str, Any]], gates: dict[str, float]
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    """Aggregate every score within each factorial cell."""
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
    candidates = {rule: [] for rule in RULES}
    for key, values in sorted(groups.items()):
        scenario, ntips, calibration, gamma_shape, sigma = key
        summaries = {rule: _summarize_rule(values, rule, gates) for rule in RULES}
        cell = {
            "scenario": scenario,
            "ntips": ntips,
            "calibration": calibration,
            "gamma_shape": gamma_shape,
            "sigma": sigma,
            "rules": summaries,
        }
        cells.append(cell)
        for rule, summary in summaries.items():
            if summary["passed"]:
                candidates[rule].append(
                    {
                        "scenario": scenario,
                        "ntips": ntips,
                        "calibration": calibration,
                        "gamma_shape": gamma_shape,
                        "sigma": sigma,
                    }
                )
    return cells, candidates


def _failure_diagnostics(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize failed candidates, folds, full fits, and optimizer messages."""
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for record in records:
        key = (
            record["scenario"],
            int(record["ntips"]),
            record["calibration"],
            float(record["gamma_shape"]),
            float(record["sigma"]),
        )
        groups.setdefault(key, []).append(record)
    summaries = []
    for key, values in sorted(groups.items()):
        scenario, ntips, calibration, gamma_shape, sigma = key
        per_lambda: dict[float, Counter] = {}
        messages: Counter[str] = Counter()
        dataset_errors = 0
        total_candidates = invalid_candidates = 0
        total_folds = failed_folds = 0
        total_full_fits = failed_full_fits = 0
        for record in values:
            if record.get("status") != "ok":
                dataset_errors += 1
                messages[record.get("message", "dataset error")] += 1
                continue
            for candidate in record["candidates"]:
                lam = float(candidate["lam"])
                counts = per_lambda.setdefault(lam, Counter())
                total_candidates += 1
                if not candidate["valid"]:
                    invalid_candidates += 1
                    counts["invalid_datasets"] += 1
                for fold in candidate["folds"]:
                    total_folds += 1
                    if not fold["converged"]:
                        failed_folds += 1
                        counts["failed_folds"] += 1
                        messages[str(fold.get("optimizer_message", ""))] += 1
            for label, fit in record["full_fits"].items():
                lam = float(label)
                counts = per_lambda.setdefault(lam, Counter())
                total_full_fits += 1
                if not fit["converged"]:
                    failed_full_fits += 1
                    counts["failed_full_fits"] += 1
                    messages[str(fit.get("optimizer_message", ""))] += 1
        if not any(
            (dataset_errors, invalid_candidates, failed_folds, failed_full_fits)
        ):
            continue
        summaries.append(
            {
                "scenario": scenario,
                "ntips": ntips,
                "calibration": calibration,
                "gamma_shape": gamma_shape,
                "sigma": sigma,
                "datasets": len(values),
                "dataset_errors": dataset_errors,
                "invalid_candidates": invalid_candidates,
                "total_candidates": total_candidates,
                "failed_folds": failed_folds,
                "total_folds": total_folds,
                "failed_full_fits": failed_full_fits,
                "total_full_fits": total_full_fits,
                "failures_by_lambda": [
                    {"lam": lam, **dict(counts)}
                    for lam, counts in sorted(per_lambda.items())
                    if counts
                ],
                "optimizer_messages": [
                    {"message": message, "count": count}
                    for message, count in messages.most_common(10)
                    if message
                ],
            }
        )
    return summaries


def _diagnostic_source_hash() -> str:
    """Return the hash of this cache-only analysis implementation."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _environment(config: dict[str, Any]) -> dict[str, Any]:
    """Return reproducibility metadata for cache-only rescoring."""
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "toytree": toytree.__version__,
        "config_hash": study._json_hash(config),
        "fit_source_hash": study._source_hash(),
        "diagnostic_source_hash": _diagnostic_source_hash(),
    }


def main(argv: list[str] | None = None) -> int:
    """Run cache-only score and optimizer-failure diagnostics."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("smoke", "pilot"), default="pilot")
    parser.add_argument("--output-dir", type=Path, default=HERE / "v5")
    parser.add_argument(
        "--bootstrap-replicates", type=int, default=DEFAULT_BOOTSTRAP_REPLICATES
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    args = parser.parse_args(argv)
    if args.bootstrap_replicates < 1:
        parser.error("--bootstrap-replicates must be positive")

    config = json.loads(study.CONFIG_PATH.read_text())
    payloads, _ = study._payloads(config, args.mode, args.output_dir, True)
    records = study._read_records(payloads)
    rows = [
        _score_record(record, args.bootstrap_replicates, args.seed)
        for record in records
    ]
    cells, candidates = _aggregate(rows, config["decision_gates"])
    result = {
        "study_version": 5,
        "mode": args.mode,
        "kind": "lambda_selection_score_and_failure_diagnostic",
        "diagnostic_only": True,
        "changes_public_selector": False,
        "reuses_cached_fits": True,
        "bootstrap_replicates": int(args.bootstrap_replicates),
        "bootstrap_seed": int(args.seed),
        "risk_thresholds": list(RISK_THRESHOLDS),
        "rules": RULES,
        "cells": cells,
        "candidate_cells_by_rule": candidates,
        "failure_diagnostics": _failure_diagnostics(records),
        "datasets": rows,
        "environment": _environment(config),
    }
    path = args.output_dir / f"diagnostics-v5-{args.mode}.json"
    study._atomic_json(path, result)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(rows),
                "output": str(path),
                "diagnostic_only": True,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
