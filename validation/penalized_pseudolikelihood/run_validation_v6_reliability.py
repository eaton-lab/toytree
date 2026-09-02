#!/usr/bin/env python

"""V6 paired reliability study for the correlated penalized model."""

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
from collections import Counter, defaultdict
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
    _scale_true_tree,
    _simulate_rates,
)
from validation.penalized_pseudolikelihood.run_validation_v5_identifiability import (
    _calibrations,
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v6.json"
CACHE_SCHEMA_VERSION = 1
EPS = 1e-12
LOSS_SCORE = {
    "fractional_poisson": "pearson",
    "multiplicative_gamma": "gamma_deviance",
}


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


def _simulate_dataset(
    ntips: int,
    rate_sigma: float,
    noise_model: str,
    seed: int,
    config: dict[str, Any],
) -> tuple[Any, Any, np.ndarray, np.ndarray, np.ndarray]:
    """Return paired truth and positive observed branch-length estimates."""
    rng = np.random.default_rng(seed)
    true_tree = _scale_true_tree(ntips, seed)
    edges = np.asarray(true_tree.get_edges("idx"), dtype=int)
    ages = true_tree.get_node_data("height").to_numpy(dtype=float)
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    simulation = {
        "baseline_rate": 1.0,
        "correlated_log_sigma": float(rate_sigma),
    }
    rates = _simulate_rates(true_tree, "correlated", rng, simulation)
    means = times * rates
    if noise_model == "gamma":
        shape = float(config["noise"]["gamma"]["shape"])
        observed = means * rng.gamma(shape, 1.0 / shape, size=means.size)
    elif noise_model == "lognormal":
        cv = float(config["noise"]["lognormal"]["coefficient_of_variation"])
        sigma = float(np.sqrt(np.log1p(cv * cv)))
        observed = means * np.exp(rng.normal(-0.5 * sigma * sigma, sigma, means.size))
    else:
        raise ValueError(f"unknown noise model: {noise_model}")
    observed_tree = true_tree.set_node_data(
        "dist",
        {int(child): float(observed[idx]) for idx, (child, _) in enumerate(edges)},
        inplace=False,
    )
    return true_tree, observed_tree, rates, means, observed


def _slim_fit(fit: dict[str, Any]) -> dict[str, Any]:
    """Return JSON-native fitted values needed by every later diagnostic."""
    return {
        "converged": bool(fit["converged"]),
        "optimizer_message": str(fit.get("optimizer_message", "")),
        "optimizer_retries": int(fit.get("optimizer_retries", 0)),
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
        "gradient_max_abs": fit.get("gradient_max_abs"),
    }


def _fit_full_path(
    tree: Any,
    lambdas: list[float],
    calibrations: dict[int, Any],
    observation_loss: str,
    options: dict[str, Any],
    seed: int,
) -> dict[str, dict[str, Any]]:
    """Fit a full-data lambda path with strong-to-weak warm starts."""
    warm_rates = None
    warm_ages = None
    results: dict[str, dict[str, Any]] = {}
    ordered = sorted((float(value) for value in lambdas), reverse=True)
    for index, lam in enumerate(ordered):
        kwargs = dict(options)
        kwargs["seed"] = int(seed) + index
        if warm_rates is not None:
            kwargs["_initial_rates"] = warm_rates
            kwargs["_initial_ages"] = warm_ages
        fit = edges_make_ultrametric_correlated(
            tree,
            lam=lam,
            calibrations=calibrations,
            full=True,
            inplace=False,
            _observation_loss=observation_loss,
            **kwargs,
        )
        results[str(lam)] = _slim_fit(fit)
        if fit["converged"]:
            warm_rates = list(fit["rates"])
            warm_ages = (
                fit["tree"].get_node_data("height").to_numpy(dtype=float).tolist()
            )
    return results


def _scale_check(
    tree: Any,
    calibrations: dict[int, Any],
    options: dict[str, Any],
    seed: int,
) -> dict[str, Any]:
    """Fit the Gamma working loss after common phylogram rescaling."""
    dists = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
    fits = {}
    for index, factor in enumerate((1e-3, 1.0, 1e3)):
        scaled = tree.set_node_data(
            "dist",
            {int(node.idx): float(dists[node.idx] * factor) for node in tree[:-1]},
            inplace=False,
        )
        fit = edges_make_ultrametric_correlated(
            scaled,
            lam=1.0,
            calibrations=calibrations,
            full=True,
            inplace=False,
            _observation_loss="multiplicative_gamma",
            **{**options, "seed": int(seed) + index},
        )
        fits[str(factor)] = _slim_fit(fit)
    return fits


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    """Return one deterministic resumable cache path."""
    sigma = str(payload["rate_sigma"]).replace(".", "p")
    name = (
        f"{payload['scenario']}-n{payload['ntips']}-{payload['calibration']}-"
        f"{payload['noise_model']}-sigma{sigma}-r{payload['replicate']:04d}.json"
    )
    return output_dir / "cache-v6" / payload["mode"] / name


def _fit_worker(payload: dict[str, Any]) -> str:
    """Simulate and fit both observation losses for one paired dataset."""
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
            "ntips",
            "calibration",
            "rate_sigma",
            "noise_model",
            "replicate",
            "seed",
            "fingerprint",
        )
    }
    record["cache_schema_version"] = CACHE_SCHEMA_VERSION
    try:
        true_tree, observed_tree, true_rates, true_means, observed = _simulate_dataset(
            int(payload["ntips"]),
            float(payload["rate_sigma"]),
            payload["noise_model"],
            int(payload["seed"]),
            payload["config"],
        )
        calibrations = _calibrations(true_tree, payload["calibration"])
        options = {
            "max_iter": int(payload["fit"]["max_iter"]),
            "max_fun": int(payload["fit"]["max_fun"]),
            "max_refine": int(payload["fit"]["max_refine"]),
            "nstarts": int(payload["fit"]["nstarts"]),
            "ncores": 1,
            "_retry_multiplier": int(payload["fit"]["retry_multiplier"]),
        }
        models = {}
        for loss_index, observation_loss in enumerate(payload["observation_losses"]):
            cv = edges_make_ultrametric_correlated_lambda_cv(
                observed_tree,
                lambdas=payload["lambdas"],
                calibrations=calibrations,
                max_iter=options["max_iter"],
                max_fun=options["max_fun"],
                max_refine=options["max_refine"],
                nstarts=options["nstarts"],
                ncores=1,
                seed=int(payload["seed"]) + loss_index * 1_000_003,
                _observation_loss=observation_loss,
            )
            full_fits = _fit_full_path(
                observed_tree,
                payload["lambdas"],
                calibrations,
                observation_loss,
                options,
                int(payload["seed"]) + loss_index * 2_000_003,
            )
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
                                "optimizer_message": str(
                                    fold.get("optimizer_message", "")
                                ),
                                "optimizer_retries": int(
                                    fold.get("optimizer_retries", 0)
                                ),
                            }
                            for fold in candidate["folds"]
                        ],
                    }
                )
            selected_label = str(float(cv["selected_lam"]))
            models[observation_loss] = {
                "selected_lam": float(cv["selected_lam"]),
                "cold_selected_fit": _slim_fit(cv["selected_fit"]),
                "full_fits": full_fits,
                "candidates": candidates,
                "warm_cold_objective_delta": float(
                    -full_fits[selected_label]["penalized_pseudologlik"]
                    + cv["selected_fit"]["penalized_pseudologlik"]
                ),
            }
        record.update(
            {
                "status": "ok",
                "true_ages": true_tree.get_node_data("height")
                .to_numpy(dtype=float)
                .tolist(),
                "true_rates": true_rates.tolist(),
                "true_means": true_means.tolist(),
                "observed": observed.tolist(),
                "models": models,
            }
        )
        if payload["run_scale_check"]:
            record["scale_check"] = _scale_check(
                observed_tree,
                calibrations,
                options,
                int(payload["seed"]) + 9_000_001,
            )
    except Exception as exc:
        record.update({"status": "error", "message": f"{type(exc).__name__}: {exc}"})
    _atomic_json(path, record)
    return str(path)


def _prediction_scores(
    observed: np.ndarray, predicted: np.ndarray, score: str
) -> np.ndarray:
    """Return paired held-branch scores without refitting."""
    values = np.clip(np.asarray(observed, dtype=float), EPS, None)
    expected = np.clip(np.asarray(predicted, dtype=float), EPS, None)
    if score == "pearson":
        return (values - expected) ** 2 / expected
    if score == "gamma_deviance":
        ratio = values / expected
        return 2.0 * (ratio - np.log(ratio) - 1.0)
    raise ValueError(f"unknown score: {score}")


def _candidate_arrays(
    model: dict[str, Any], score: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return sorted lambda, validity, and candidate-by-fold score arrays."""
    candidates = sorted(model["candidates"], key=lambda item: float(item["lam"]))
    lambdas = np.asarray([item["lam"] for item in candidates], dtype=float)
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


def _select_index(matrix: np.ndarray, valid: np.ndarray, lambdas: np.ndarray) -> int:
    """Select minimum mean score, favoring stronger smoothing on exact ties."""
    summaries = np.where(valid, np.mean(matrix, axis=1), np.inf)
    minimum = float(np.min(summaries))
    if not np.isfinite(minimum):
        raise RuntimeError("all lambda candidates are invalid")
    tied = np.flatnonzero(np.abs(summaries - minimum) <= EPS)
    return int(tied[np.argmax(lambdas[tied])])


def _age_rmse(ages: np.ndarray, truth: np.ndarray, ntips: int) -> float:
    """Return root-normalized internal-node age RMSE."""
    root_age = max(float(truth[-1]), EPS)
    return float(np.sqrt(np.mean(((ages[ntips:] - truth[ntips:]) / root_age) ** 2)))


def _rate_spearman(truth: np.ndarray, fitted: np.ndarray) -> float | None:
    """Return finite log-rate rank correlation."""
    if np.ptp(np.log(truth)) <= EPS or np.ptp(np.log(fitted)) <= EPS:
        return None
    value = float(spearmanr(np.log(truth), np.log(fitted)).statistic)
    return value if np.isfinite(value) else None


def _bootstrap_support(
    model: dict[str, Any],
    score: str,
    full_fits: dict[str, Any],
    ntips: int,
    root_age: float,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    """Return selection frequencies and chronogram spread over supported lambda."""
    lambdas, valid, matrix = _candidate_arrays(model, score)
    rng = np.random.default_rng(seed)
    selected = np.empty(replicates, dtype=float)
    for index in range(replicates):
        columns = rng.integers(0, matrix.shape[1], size=matrix.shape[1])
        selected[index] = lambdas[_select_index(matrix[:, columns], valid, lambdas)]
    counts = Counter(float(value) for value in selected)
    supported = sorted(
        lam for lam, count in counts.items() if count / replicates >= 0.05
    )
    if not supported:
        supported = [max(counts, key=lambda value: (counts[value], value))]
    age_rows = [
        np.asarray(full_fits[str(float(lam))]["ages"], dtype=float)[ntips:]
        for lam in supported
        if full_fits[str(float(lam))]["converged"]
    ]
    if age_rows:
        spread = np.ptp(np.vstack(age_rows), axis=0) / max(root_age, EPS)
        median_spread = float(np.median(spread))
        maximum_spread = float(np.max(spread))
    else:
        median_spread = None
        maximum_spread = None
    log_values = np.log10(selected)
    return {
        "selection_frequencies": {
            str(lam): float(count / replicates) for lam, count in sorted(counts.items())
        },
        "supported_lambdas": supported,
        "log10_lam_80_percent_width": float(
            np.quantile(log_values, 0.9) - np.quantile(log_values, 0.1)
        ),
        "median_normalized_age_spread": median_spread,
        "maximum_normalized_age_spread": maximum_spread,
    }


def _score_model(
    record: dict[str, Any],
    observation_loss: str,
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Score one fitted loss against truth and both held-edge criteria."""
    model = record["models"][observation_loss]
    ntips = int(record["ntips"])
    truth_ages = np.asarray(record["true_ages"], dtype=float)
    truth_rates = np.asarray(record["true_rates"], dtype=float)
    full_fits = model["full_fits"]
    errors = {
        float(label): _age_rmse(np.asarray(fit["ages"]), truth_ages, ntips)
        for label, fit in full_fits.items()
        if fit["converged"]
    }
    if not errors:
        raise RuntimeError("all full-grid fits failed")
    selected_lam = float(model["selected_lam"])
    warm_fit = full_fits[str(selected_lam)]
    selected_fit = model["cold_selected_fit"]
    selected_error = _age_rmse(
        np.asarray(selected_fit["ages"], dtype=float), truth_ages, ntips
    )
    oracle_errors = dict(errors)
    oracle_errors[selected_lam] = min(errors[selected_lam], selected_error)
    oracle_error = min(oracle_errors.values())
    oracle_lam = max(
        lam
        for lam, error in oracle_errors.items()
        if abs(error - oracle_error) <= EPS
    )
    folds = [fold for candidate in model["candidates"] for fold in candidate["folds"]]
    matching_score = LOSS_SCORE[observation_loss]
    cross_score = "gamma_deviance" if matching_score == "pearson" else "pearson"
    lambdas, valid, cross_matrix = _candidate_arrays(model, cross_score)
    cross_lam = float(lambdas[_select_index(cross_matrix, valid, lambdas)])
    bootstrap = _bootstrap_support(
        model,
        matching_score,
        full_fits,
        ntips,
        float(truth_ages[-1]),
        bootstrap_replicates,
        bootstrap_seed,
    )
    fixed_ages = record["calibration"] == "fixed_internal_ages"
    warm_ages = np.asarray(warm_fit["ages"], dtype=float)[ntips:]
    cold_ages = np.asarray(selected_fit["ages"], dtype=float)[ntips:]
    root_age = max(float(truth_ages[-1]), EPS)
    normalized_age_delta = (warm_ages - cold_ages) / root_age
    objective_delta = float(model["warm_cold_objective_delta"])
    objective_scale = max(
        abs(float(warm_fit["penalized_pseudologlik"])),
        abs(float(selected_fit["penalized_pseudologlik"])),
        EPS,
    )
    return {
        "observation_loss": observation_loss,
        "matching_score": matching_score,
        "selected_lam": selected_lam,
        "cross_score_selected_lam": cross_lam,
        "oracle_age_lam": float(oracle_lam),
        "selected_age_rmse": selected_error,
        "oracle_age_rmse": oracle_error,
        "selected_age_oracle_ratio": (
            None if fixed_ages else float(selected_error / max(oracle_error, EPS))
        ),
        "selected_rate_spearman": _rate_spearman(
            truth_rates, np.asarray(selected_fit["rates"], dtype=float)
        ),
        "all_candidates_converged": bool(
            all(item["valid"] for item in model["candidates"])
            and all(item["converged"] for item in full_fits.values())
        ),
        "folds_converged": int(sum(bool(fold["converged"]) for fold in folds)),
        "folds_total": len(folds),
        "optimizer_retries": int(
            sum(int(fold.get("optimizer_retries", 0)) for fold in folds)
            + sum(int(fit.get("optimizer_retries", 0)) for fit in full_fits.values())
        ),
        "warm_cold_objective_delta": objective_delta,
        "warm_cold_relative_objective_delta": float(
            objective_delta / objective_scale
        ),
        "warm_cold_normalized_age_rmse": float(
            np.sqrt(np.mean(normalized_age_delta**2))
        ),
        "warm_cold_max_normalized_age_difference": float(
            np.max(np.abs(normalized_age_delta))
        ),
        "bootstrap": bootstrap,
    }


def _score_record(
    record: dict[str, Any],
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Return truth-based metrics for both paired fits of one dataset."""
    base = {
        key: record.get(key)
        for key in (
            "status",
            "scenario",
            "ntips",
            "calibration",
            "rate_sigma",
            "noise_model",
            "replicate",
            "seed",
        )
    }
    if record.get("status") != "ok":
        return {**base, "message": record.get("message", "")}
    try:
        models = {
            loss: _score_model(
                record,
                loss,
                bootstrap_replicates,
                bootstrap_seed + int(record["seed"]) + index * 1_000_003,
            )
            for index, loss in enumerate(LOSS_SCORE)
        }
        return {**base, "models": models, "scale_check": record.get("scale_check")}
    except Exception as exc:
        return {**base, "status": "error", "message": f"{type(exc).__name__}: {exc}"}


def _finite(values: list[Any]) -> np.ndarray:
    """Return finite numeric values from an iterable."""
    return np.asarray(
        [float(value) for value in values if value is not None and np.isfinite(value)],
        dtype=float,
    )


def _bootstrap_ratio(
    numerator: np.ndarray,
    denominator: np.ndarray,
    seed: int,
    replicates: int = 5000,
) -> dict[str, float | None]:
    """Return a paired bootstrap interval for the median error ratio."""
    if not numerator.size:
        return {"median": None, "upper_95": None}
    ratios = numerator / np.clip(denominator, EPS, None)
    rng = np.random.default_rng(seed)
    values = np.empty(replicates)
    for index in range(replicates):
        sample = rng.integers(0, ratios.size, size=ratios.size)
        values[index] = np.median(ratios[sample])
    return {
        "median": float(np.median(ratios)),
        "upper_95": float(np.quantile(values, 0.95)),
    }


def _summarize(
    rows: list[dict[str, Any]],
    gates: dict[str, float],
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Aggregate convergence, recovery, stability, and paired comparisons."""
    successful = [row for row in rows if row.get("status") == "ok"]
    cells = []
    cell_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in successful:
        key = (
            row["scenario"],
            row["calibration"],
            row["ntips"],
            row["noise_model"],
            row["rate_sigma"],
        )
        cell_groups[key].append(row)

    loss_summaries = {}
    for loss in LOSS_SCORE:
        model_rows = [row["models"][loss] for row in successful]
        fold_total = sum(item["folds_total"] for item in model_rows)
        fold_ok = sum(item["folds_converged"] for item in model_rows)
        ratios = _finite([item["selected_age_oracle_ratio"] for item in model_rows])
        spreads = _finite(
            [
                item["bootstrap"]["median_normalized_age_spread"]
                for item in model_rows
                if item["selected_age_oracle_ratio"] is not None
            ]
        )
        loss_summaries[loss] = {
            "datasets": len(model_rows),
            "dataset_convergence": float(
                np.mean([item["all_candidates_converged"] for item in model_rows])
            )
            if model_rows
            else 0.0,
            "fold_convergence": float(fold_ok / fold_total) if fold_total else 0.0,
            "selected_age_oracle_ratio_median": (
                float(np.median(ratios)) if ratios.size else None
            ),
            "selected_age_oracle_ratio_p90": (
                float(np.quantile(ratios, 0.9)) if ratios.size else None
            ),
            "supported_age_spread_median": (
                float(np.median(spreads)) if spreads.size else None
            ),
            "supported_age_spread_p90": (
                float(np.quantile(spreads, 0.9)) if spreads.size else None
            ),
            "optimizer_retries": int(
                sum(item["optimizer_retries"] for item in model_rows)
            ),
            "maximum_warm_cold_objective_delta": (
                float(
                    max(
                        (item["warm_cold_objective_delta"] for item in model_rows),
                        default=0.0,
                    )
                )
            ),
            "maximum_warm_cold_relative_objective_delta": float(
                max(
                    (
                        item["warm_cold_relative_objective_delta"]
                        for item in model_rows
                    ),
                    default=0.0,
                )
            ),
            "maximum_warm_cold_normalized_age_difference": float(
                max(
                    (
                        item["warm_cold_max_normalized_age_difference"]
                        for item in model_rows
                    ),
                    default=0.0,
                )
            ),
            "p90_warm_cold_normalized_age_rmse": (
                float(
                    np.quantile(
                        [
                            item["warm_cold_normalized_age_rmse"]
                            for item in model_rows
                        ],
                        0.9,
                    )
                )
                if model_rows
                else 0.0
            ),
        }

    for key, group in sorted(cell_groups.items()):
        for loss in LOSS_SCORE:
            models = [row["models"][loss] for row in group]
            cells.append(
                {
                    "scenario": key[0],
                    "calibration": key[1],
                    "ntips": key[2],
                    "noise_model": key[3],
                    "rate_sigma": key[4],
                    "observation_loss": loss,
                    "datasets": len(models),
                    "dataset_convergence": float(
                        np.mean([item["all_candidates_converged"] for item in models])
                    ),
                    "fold_convergence": float(
                        sum(item["folds_converged"] for item in models)
                        / max(sum(item["folds_total"] for item in models), 1)
                    ),
                    "selected_age_rmse_median": float(
                        np.median([item["selected_age_rmse"] for item in models])
                    ),
                }
            )

    paired = {}
    for noise_model in sorted({row["noise_model"] for row in successful}):
        group = [
            row
            for row in successful
            if row["noise_model"] == noise_model
            and row["calibration"] != "fixed_internal_ages"
        ]
        gamma = np.asarray(
            [
                row["models"]["multiplicative_gamma"]["selected_age_rmse"]
                for row in group
            ]
        )
        poisson = np.asarray(
            [row["models"]["fractional_poisson"]["selected_age_rmse"] for row in group]
        )
        paired[noise_model] = _bootstrap_ratio(
            gamma, poisson, bootstrap_seed + len(paired) * 1_000_003
        )

    scale_checks = [row["scale_check"] for row in successful if row.get("scale_check")]
    scale_converged = bool(
        scale_checks
        and all(fit["converged"] for check in scale_checks for fit in check.values())
    )
    scale_summary = {
        "datasets": len(scale_checks),
        "all_converged": scale_converged,
        "max_age_difference": None,
    }
    if scale_converged:
        maxima = []
        for check in scale_checks:
            base = np.asarray(check["1.0"]["ages"], dtype=float)
            root = max(float(base[-1]), EPS)
            for factor in ("0.001", "1000.0"):
                ages = np.asarray(check[factor]["ages"], dtype=float)
                maxima.append(float(np.max(np.abs(ages - base)) / root))
        scale_summary["max_age_difference"] = float(max(maxima, default=0.0))

    gamma_summary = loss_summaries["multiplicative_gamma"]
    minimum_cell = min(
        (
            min(cell["dataset_convergence"], cell["fold_convergence"])
            for cell in cells
            if cell["observation_loss"] == "multiplicative_gamma"
        ),
        default=0.0,
    )
    checks = {
        "overall_convergence": bool(
            min(
                gamma_summary["dataset_convergence"],
                gamma_summary["fold_convergence"],
            )
            >= gates["overall_convergence"]
        ),
        "minimum_cell_convergence": bool(
            minimum_cell >= gates["minimum_cell_convergence"]
        ),
        "selected_age_oracle_ratio_median": bool(
            gamma_summary["selected_age_oracle_ratio_median"] is not None
            and gamma_summary["selected_age_oracle_ratio_median"]
            <= gates["selected_age_oracle_ratio_median"]
        ),
        "selected_age_oracle_ratio_p90": bool(
            gamma_summary["selected_age_oracle_ratio_p90"] is not None
            and gamma_summary["selected_age_oracle_ratio_p90"]
            <= gates["selected_age_oracle_ratio_p90"]
        ),
        "noise_family_noninferiority": bool(
            paired
            and all(
                item["upper_95"] is not None
                and item["upper_95"] <= gates["maximum_noise_family_error_ratio"]
                for item in paired.values()
            )
        ),
        "supported_age_spread_median": bool(
            gamma_summary["supported_age_spread_median"] is not None
            and gamma_summary["supported_age_spread_median"]
            <= gates["supported_age_spread_median"]
        ),
        "supported_age_spread_p90": bool(
            gamma_summary["supported_age_spread_p90"] is not None
            and gamma_summary["supported_age_spread_p90"]
            <= gates["supported_age_spread_p90"]
        ),
        "scale_invariance": bool(
            scale_summary["all_converged"]
            and scale_summary["max_age_difference"] is not None
            and scale_summary["max_age_difference"]
            <= gates["scale_invariance_tolerance"]
        ),
        "warm_start_objective_parity": bool(
            gamma_summary["maximum_warm_cold_objective_delta"] <= 1e-8
            and loss_summaries["fractional_poisson"][
                "maximum_warm_cold_objective_delta"
            ]
            <= 1e-8
        ),
    }
    return {
        "losses": loss_summaries,
        "cells": cells,
        "paired_gamma_to_poisson_age_error": paired,
        "scale_invariance": scale_summary,
        "checks": checks,
        "gates_passed": bool(all(checks.values())),
    }


def _payloads(
    config: dict[str, Any],
    mode: str,
    output_dir: Path,
    resume: bool,
) -> list[dict[str, Any]]:
    """Expand one configured study mode into deterministic paired datasets."""
    config_key = "optimizer_stress" if mode == "optimizer-stress" else mode
    source_hash = _source_hash()
    payloads = []
    index = 0
    for scenario in config[config_key]:
        lambdas = scenario.get("lambdas", config["lambdas"])
        for ntips in scenario["ntips"]:
            for calibration in scenario["calibrations"]:
                for rate_sigma in scenario["rate_sigmas"]:
                    for noise_model in scenario["noise_models"]:
                        for replicate in range(int(scenario["replicates"])):
                            seed_key = f"{calibration}|{float(rate_sigma)}|{replicate}"
                            seed = int(
                                scenario.get("replay_seeds", {}).get(
                                    seed_key,
                                    int(config["development_seed"]) + index * 100_003,
                                )
                            )
                            payload = {
                                "mode": mode,
                                "scenario": scenario["name"],
                                "ntips": int(ntips),
                                "calibration": calibration,
                                "rate_sigma": float(rate_sigma),
                                "noise_model": noise_model,
                                "replicate": replicate,
                                "seed": seed,
                                "fit": config["fit"],
                                "lambdas": [float(value) for value in lambdas],
                                "observation_losses": list(
                                    config["observation_losses"]
                                ),
                                "config": config,
                                "resume": resume,
                                "run_scale_check": False,
                            }
                            payload["fingerprint"] = _json_hash(
                                {
                                    key: value
                                    for key, value in payload.items()
                                    if key not in {"resume", "run_scale_check"}
                                }
                                | {
                                    "source_hash": source_hash,
                                    "cache_schema_version": CACHE_SCHEMA_VERSION,
                                }
                            )
                            payload["cache_path"] = str(
                                _cache_path(output_dir, payload)
                            )
                            payloads.append(payload)
                            index += 1
    for payload in payloads:
        if payload["calibration"] != "fixed_internal_ages":
            payload["run_scale_check"] = True
            break
    if payloads and not any(item["run_scale_check"] for item in payloads):
        payloads[0]["run_scale_check"] = True
    # Scale-check assignment affects cache contents and must be fingerprinted.
    for payload in payloads:
        payload["fingerprint"] = _json_hash(
            {
                key: value
                for key, value in payload.items()
                if key not in {"resume", "cache_path", "fingerprint"}
            }
            | {
                "source_hash": source_hash,
                "cache_schema_version": CACHE_SCHEMA_VERSION,
            }
        )
    return payloads


def _run_workers(payloads: list[dict[str, Any]], ncores: int) -> list[Path]:
    """Run resumable dataset workers and print machine-readable progress."""
    started = time.monotonic()
    paths = []
    if ncores == 1:
        iterator = (_fit_worker(payload) for payload in payloads)
        for completed, result in enumerate(iterator, 1):
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

    with ProcessPoolExecutor(max_workers=min(ncores, len(payloads))) as pool:
        futures = [pool.submit(_fit_worker, payload) for payload in payloads]
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
    """Run fit and/or cache-only scoring for the v6 study."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("smoke", "pilot", "optimizer-stress"),
        default="smoke",
    )
    parser.add_argument("--stage", choices=("all", "fit", "score"), default="all")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE / "v6")
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
    payloads = _payloads(
        config,
        args.mode,
        args.output_dir,
        resume=not args.no_resume,
    )

    if args.stage in {"all", "fit"}:
        _run_workers(payloads, args.ncores)
    if args.stage == "fit":
        print(json.dumps({"mode": args.mode, "datasets": len(payloads)}))
        return

    records = _read_records(payloads)
    rows = [
        _score_record(
            record,
            bootstrap_replicates,
            int(config["bootstrap_seed"]),
        )
        for record in records
    ]
    summary = _summarize(
        rows,
        config["decision_gates"],
        int(config["bootstrap_seed"]),
    )
    result = {
        "study_version": int(config["study_version"]),
        "mode": args.mode,
        "scope": "correlated_optimizer_and_observation_loss_reliability",
        "diagnostic_only": True,
        "release_eligible": False,
        "changes_public_api": False,
        "sequence_length_input": False,
        "bootstrap_replicates": bootstrap_replicates,
        "datasets": rows,
        "summary": summary,
        "all_release_gates_passed": False,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / f"results-v6-{args.mode}.json"
    environment_path = args.output_dir / f"environment-v6-{args.mode}.json"
    seeds_path = args.output_dir / f"seeds-v6-{args.mode}.json"
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
                    "rate_sigma",
                    "noise_model",
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
                "diagnostic_only": True,
            }
        )
    )


if __name__ == "__main__":
    main()
