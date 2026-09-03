#!/usr/bin/env python

"""Compare V9 correlated-lambda selectors without refitting likelihoods."""

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

import toytree
from validation.penalized_pseudolikelihood import (
    run_validation_v9_uncertainty as study,
)

EPS = 1e-12
RULES = {
    "mean_minimum": {
        "aggregation": "mean",
        "selection": "minimum",
    },
    "paired_one_se_stronger": {
        "aggregation": "mean",
        "selection": "paired_one_se_stronger",
    },
    "trimmed_mean_10_percent_minimum": {
        "aggregation": "trimmed_mean_10_percent",
        "selection": "minimum",
    },
    "median_minimum": {
        "aggregation": "median",
        "selection": "minimum",
    },
}


def _aggregate(matrix: np.ndarray, method: str) -> np.ndarray:
    """Aggregate candidate-by-fold losses for one selection rule."""
    if method == "mean":
        return np.mean(matrix, axis=1)
    if method == "median":
        return np.median(matrix, axis=1)
    if method == "trimmed_mean_10_percent":
        ordered = np.sort(matrix, axis=1)
        trim = int(np.floor(0.1 * ordered.shape[1]))
        if trim:
            ordered = ordered[:, trim:-trim]
        return np.mean(ordered, axis=1)
    raise ValueError(f"unknown aggregation: {method}")


def _minimum_index(values: np.ndarray, valid: np.ndarray, lambdas: np.ndarray) -> int:
    """Select the finite minimum, favoring stronger smoothing on exact ties."""
    summaries = np.where(valid, values, np.inf)
    minimum = float(np.min(summaries))
    if not np.isfinite(minimum):
        raise RuntimeError("all lambda candidates are invalid")
    tied = np.flatnonzero(valid & (np.abs(summaries - minimum) <= EPS))
    return int(tied[np.argmax(lambdas[tied])])


def _select_index(
    matrix: np.ndarray,
    valid: np.ndarray,
    lambdas: np.ndarray,
    rule: dict[str, str],
) -> tuple[int, np.ndarray]:
    """Select one lambda using paired folds and a prespecified rule."""
    summaries = _aggregate(matrix, rule["aggregation"])
    minimum_idx = _minimum_index(summaries, valid, lambdas)
    if rule["selection"] == "minimum":
        return minimum_idx, summaries
    if rule["selection"] != "paired_one_se_stronger":
        raise ValueError(f"unknown selection rule: {rule['selection']}")

    reference = matrix[minimum_idx]
    eligible = []
    for idx in np.flatnonzero(valid):
        differences = matrix[idx] - reference
        excess = float(np.mean(differences))
        standard_error = (
            float(np.std(differences, ddof=1) / np.sqrt(differences.size))
            if differences.size > 1
            else 0.0
        )
        if excess <= standard_error + EPS:
            eligible.append(int(idx))
    return max(eligible, key=lambda idx: float(lambdas[idx])), summaries


def _candidate_arrays(
    model: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return sorted lambda, validity, and cached candidate-by-fold losses."""
    candidates = sorted(model["candidates"], key=lambda item: float(item["lam"]))
    lambdas = np.asarray([item["lam"] for item in candidates], dtype=float)
    fold_counts = {len(item["folds"]) for item in candidates}
    if len(fold_counts) != 1 or not fold_counts or next(iter(fold_counts)) < 2:
        raise RuntimeError("candidate caches do not share at least two folds")
    matrix = np.asarray(
        [[float(fold["score"]) for fold in item["folds"]] for item in candidates],
        dtype=float,
    )
    valid = np.asarray(
        [
            bool(item["valid"])
            and all(bool(fold["converged"]) for fold in item["folds"])
            for item in candidates
        ],
        dtype=bool,
    )
    valid &= np.all(np.isfinite(matrix), axis=1)
    return lambdas, valid, matrix


def _age_rmse(fit: dict[str, Any], record: dict[str, Any]) -> float:
    """Return root-normalized internal-age RMSE."""
    ntips = int(record["ntips"])
    truth = np.asarray(record["true_ages"], dtype=float)
    ages = np.asarray(fit["ages"], dtype=float)
    root_age = max(float(truth[-1]), EPS)
    return float(np.sqrt(np.mean(((ages[ntips:] - truth[ntips:]) / root_age) ** 2)))


def _bootstrap_rule(
    matrix: np.ndarray,
    valid: np.ndarray,
    lambdas: np.ndarray,
    rule: dict[str, str],
    full_fits: dict[str, Any],
    ntips: int,
    root_age: float,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    """Bootstrap one rule and measure its supported-chronogram spread."""
    rng = np.random.default_rng(seed)
    selected = np.empty(replicates, dtype=float)
    for index in range(replicates):
        columns = rng.integers(0, matrix.shape[1], size=matrix.shape[1])
        choice, _ = _select_index(matrix[:, columns], valid, lambdas, rule)
        selected[index] = lambdas[choice]
    counts = Counter(float(value) for value in selected)
    supported = sorted(
        lam for lam, count in counts.items() if count / replicates >= 0.05
    )
    if not supported:
        supported = [max(counts, key=lambda value: (counts[value], value))]
    supported_fits = {lam: full_fits[str(float(lam))] for lam in supported}
    supported_valid = all(
        fit.get("converged") and fit.get("solution_stable") is True
        for fit in supported_fits.values()
    )
    age_rows = [
        np.asarray(fit["ages"], dtype=float)[ntips:]
        for fit in supported_fits.values()
        if fit.get("converged")
    ]
    if age_rows:
        spread = np.ptp(np.vstack(age_rows), axis=0) / max(root_age, EPS)
        between = float(np.max(spread))
    else:
        between = None
    within = max(
        (
            float(fit.get("max_near_optimal_age_difference") or 0.0)
            for fit in supported_fits.values()
            if fit.get("converged")
        ),
        default=0.0,
    )
    log_values = np.log10(selected)
    return {
        "selection_frequencies": {
            str(lam): float(count / replicates) for lam, count in sorted(counts.items())
        },
        "supported_lambdas": supported,
        "supported_full_fits_valid": bool(supported_valid),
        "invalid_supported_lambdas": [
            float(lam)
            for lam, fit in supported_fits.items()
            if not (fit.get("converged") and fit.get("solution_stable") is True)
        ],
        "modal_lam": float(max(counts, key=lambda value: (counts[value], value))),
        "modal_frequency": float(max(counts.values()) / replicates),
        "log10_lam_80_percent_width": float(
            np.quantile(log_values, 0.9) - np.quantile(log_values, 0.1)
        ),
        "maximum_between_lambda_age_spread": between,
        "maximum_within_lambda_age_difference": within,
        "maximum_total_normalized_age_uncertainty": max(between or 0.0, within),
    }


def _score_model(
    record: dict[str, Any],
    loss: str,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    """Compare all selector rules for one cached dataset and loss."""
    model = record["models"][loss]
    lambdas, valid, matrix = _candidate_arrays(model)
    fits = model["full_fits"]
    errors = {
        float(label): _age_rmse(fit, record)
        for label, fit in fits.items()
        if fit.get("converged") and fit.get("solution_stable") is True
    }
    if not errors:
        raise RuntimeError("no stable full-data fit is available")
    oracle_error = min(errors.values())
    oracle_lam = max(
        lam for lam, error in errors.items() if abs(error - oracle_error) <= EPS
    )
    root_age = float(record["true_ages"][-1])
    rules = {}
    for name, rule in RULES.items():
        selected_idx, summaries = _select_index(matrix, valid, lambdas, rule)
        selected_lam = float(lambdas[selected_idx])
        selected_fit = fits.get(str(selected_lam), {})
        selected_fit_valid = bool(
            selected_fit.get("converged")
            and selected_fit.get("solution_stable") is True
        )
        selected_error = errors.get(selected_lam)
        bootstrap = _bootstrap_rule(
            matrix,
            valid,
            lambdas,
            rule,
            fits,
            int(record["ntips"]),
            root_age,
            replicates,
            seed,
        )
        rules[name] = {
            "status": "ok" if selected_fit_valid else "error",
            "selected_fit_valid": selected_fit_valid,
            "selected_lam": selected_lam,
            "selected_at_boundary": selected_lam in {lambdas[0], lambdas[-1]},
            "selected_mean_fold_loss": float(np.mean(matrix[selected_idx])),
            "selected_aggregate_fold_loss": float(summaries[selected_idx]),
            "selected_age_rmse": selected_error,
            "oracle_lam": float(oracle_lam),
            "oracle_age_rmse": oracle_error,
            "selected_age_oracle_ratio": (
                None
                if selected_error is None
                else float(selected_error / max(oracle_error, EPS))
            ),
            "bootstrap": bootstrap,
        }
    current = rules["mean_minimum"]["selected_lam"]
    if current != float(model["selected_lam"]):
        raise RuntimeError(
            "mean-minimum rule did not reproduce V9 selection: "
            f"{current} != {model['selected_lam']}"
        )
    return {
        "observation_loss": loss,
        "valid_candidates": int(np.sum(valid)),
        "rules": rules,
    }


def _score_record(
    record: dict[str, Any], replicates: int, bootstrap_seed: int
) -> dict[str, Any]:
    """Score every rule for both cached observation losses."""
    base = {
        key: record.get(key)
        for key in (
            "status",
            "scenario",
            "ntips",
            "calibration",
            "rate_sigma",
            "noise_model",
            "seed",
        )
    }
    if record.get("status") != "ok":
        return {**base, "message": record.get("message", "cached fit failed")}
    try:
        models = {
            loss: _score_model(
                record,
                loss,
                replicates,
                bootstrap_seed + int(record["seed"]) + index * 1_000_003,
            )
            for index, loss in enumerate(study.LOSS_SCORE)
        }
        return {**base, "models": models}
    except Exception as exc:
        return {**base, "status": "error", "message": f"{type(exc).__name__}: {exc}"}


def _finite(values: list[Any]) -> np.ndarray:
    """Return finite numeric values from a collection."""
    return np.asarray(
        [float(value) for value in values if value is not None and np.isfinite(value)],
        dtype=float,
    )


def _summarize_rule(rows: list[dict[str, Any]], loss: str, rule: str) -> dict[str, Any]:
    """Aggregate recovery and uncertainty for one loss-rule combination."""
    values = [
        row["models"][loss]["rules"][rule] for row in rows if row.get("status") == "ok"
    ]
    ratios = _finite([value["selected_age_oracle_ratio"] for value in values])
    errors = _finite([value["selected_age_rmse"] for value in values])
    uncertainty = _finite(
        [
            value["bootstrap"]["maximum_total_normalized_age_uncertainty"]
            for value in values
        ]
    )
    widths = _finite(
        [value["bootstrap"]["log10_lam_80_percent_width"] for value in values]
    )
    return {
        "datasets": len(values),
        "successful_selected_fits": int(
            sum(value.get("status", "ok") == "ok" for value in values)
        ),
        "all_supported_full_fits_valid": bool(
            values
            and all(
                value["bootstrap"].get("supported_full_fits_valid", True)
                for value in values
            )
        ),
        "selected_age_rmse_median": float(np.median(errors)) if errors.size else None,
        "selected_age_oracle_ratio_median": (
            float(np.median(ratios)) if ratios.size else None
        ),
        "selected_age_oracle_ratio_p90": (
            float(np.quantile(ratios, 0.9)) if ratios.size else None
        ),
        "maximum_total_age_uncertainty": (
            float(np.max(uncertainty)) if uncertainty.size else None
        ),
        "total_age_uncertainty_median": (
            float(np.median(uncertainty)) if uncertainty.size else None
        ),
        "total_age_uncertainty_p90": (
            float(np.quantile(uncertainty, 0.9)) if uncertainty.size else None
        ),
        "log10_lambda_width_median": (
            float(np.median(widths)) if widths.size else None
        ),
        "boundary_selection_fraction": (
            float(np.mean([value["selected_at_boundary"] for value in values]))
            if values
            else None
        ),
    }


def _summarize(rows: list[dict[str, Any]], gates: dict[str, Any]) -> dict[str, Any]:
    """Compare rules and mark targeted Gamma criteria without release claims."""
    successful = [row for row in rows if row.get("status") == "ok"]
    summaries = {
        loss: {rule: _summarize_rule(successful, loss, rule) for rule in RULES}
        for loss in study.LOSS_SCORE
    }
    comparisons = {}
    checks = {}
    for rule in RULES:
        gamma = summaries["multiplicative_gamma"][rule]
        paired_errors = [
            (
                row["models"]["multiplicative_gamma"]["rules"]["mean_minimum"][
                    "selected_age_rmse"
                ],
                row["models"]["multiplicative_gamma"]["rules"][rule][
                    "selected_age_rmse"
                ],
            )
            for row in successful
            if row["models"]["multiplicative_gamma"]["rules"]["mean_minimum"][
                "selected_age_rmse"
            ]
            is not None
            and row["models"]["multiplicative_gamma"]["rules"][rule][
                "selected_age_rmse"
            ]
            is not None
        ]
        current_errors = np.asarray([pair[0] for pair in paired_errors], dtype=float)
        rule_errors = np.asarray([pair[1] for pair in paired_errors], dtype=float)
        comparisons[rule] = {
            "paired_datasets": len(paired_errors),
            "gamma_age_rmse_improved_fraction_vs_current": (
                float(np.mean(rule_errors < current_errors - EPS))
                if rule_errors.size
                else None
            ),
            "gamma_age_rmse_ratio_to_current_median": (
                float(np.median(rule_errors / np.clip(current_errors, EPS, None)))
                if rule_errors.size
                else None
            ),
        }
        checks[rule] = {
            "all_selected_and_supported_fits_valid": bool(
                gamma["successful_selected_fits"] == len(rows)
                and gamma["all_supported_full_fits_valid"]
            ),
            "maximum_total_age_uncertainty": bool(
                gamma["maximum_total_age_uncertainty"] is not None
                and gamma["maximum_total_age_uncertainty"]
                <= float(gates["gamma_maximum_total_age_uncertainty"])
            ),
            "selected_age_oracle_ratio_median": bool(
                gamma["selected_age_oracle_ratio_median"] is not None
                and gamma["selected_age_oracle_ratio_median"]
                <= float(gates["gamma_selected_age_oracle_ratio_median"])
            ),
            "selected_age_oracle_ratio_p90": bool(
                gamma["selected_age_oracle_ratio_p90"] is not None
                and gamma["selected_age_oracle_ratio_p90"]
                <= float(gates["gamma_selected_age_oracle_ratio_p90"])
            ),
        }
        checks[rule]["targeted_criteria_passed"] = bool(
            all(checks[rule].values()) and len(successful) == len(rows)
        )
    return {
        "datasets": len(rows),
        "successful_datasets": len(successful),
        "rules": summaries,
        "comparisons": comparisons,
        "targeted_gamma_checks": checks,
    }


def _environment() -> dict[str, Any]:
    """Return compact provenance for the cache-only diagnostic."""
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "toytree": getattr(toytree, "__version__", "unknown"),
    }


def main() -> None:
    """Read V9 task caches and compare selectors without fitting."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("smoke", "uncertainty-replay"),
        default="uncertainty-replay",
    )
    parser.add_argument("--output-dir", type=Path, default=HERE / "v9")
    parser.add_argument("--bootstrap-replicates", type=int)
    args = parser.parse_args()

    config = json.loads(study.CONFIG_PATH.read_text())
    replicates = (
        int(config["bootstrap_replicates"])
        if args.bootstrap_replicates is None
        else int(args.bootstrap_replicates)
    )
    if replicates < 1:
        parser.error("--bootstrap-replicates must be positive")
    contexts = study._build_contexts(config, args.mode, args.output_dir)
    tasks = study._fold_tasks(contexts, True)
    grouped = study._group_fold_tasks(tasks, contexts)
    records = study._build_records(contexts, grouped)
    rows = [
        _score_record(record, replicates, int(config["bootstrap_seed"]))
        for record in records
    ]
    summary = _summarize(rows, config["decision_gates"])
    result = {
        "study_version": 9,
        "mode": args.mode,
        "scope": "cache_only_correlated_lambda_selector_diagnostic",
        "diagnostic_only": True,
        "release_eligible": False,
        "refits_likelihood": False,
        "selected_historical_cases": True,
        "bootstrap_replicates": replicates,
        "bootstrap_design": (
            "common paired-fold resamples across rules using the V9 seeds"
        ),
        "rules": RULES,
        "datasets": rows,
        "summary": summary,
        "environment": _environment(),
    }
    path = args.output_dir / f"diagnostics-v9-selectors-{args.mode}.json"
    study._atomic_json(path, result)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "datasets": len(rows),
                "output": str(path),
                "refits_likelihood": False,
                "diagnostic_only": True,
            }
        )
    )


if __name__ == "__main__":
    main()
