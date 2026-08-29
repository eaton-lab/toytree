#!/usr/bin/env python

"""Run the pinned penalized-pseudolikelihood validation study.

The full mode implements the committed study design. Smoke mode exercises the
same simulation, fitting, scoring, and artifact code on a deliberately tiny
subset and is not eligible to satisfy release gates.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import spearmanr

import toytree
from toytree.core import ToyTree
from toytree.mod._src.penalized_pseudolikelihood.model_selection import (
    _historical_cv_model_select,
)

toytree.set_log_level("WARNING")

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"


def _edge_array(tree):
    return np.asarray(tree.get_edges("idx"), dtype=int)


def _scale_true_tree(ntips: int, seed: int):
    tree = toytree.rtree.bdtree(ntips=ntips, b=1.0, d=0.2, seed=seed)
    root = tree.treenode
    while root.up is not None:
        root = root.up
    tree = ToyTree(root)
    tree = tree.mod.remove_unary_nodes()
    return tree.mod.edges_scale_to_root_height(1.0)


def _simulate_rates(tree, model: str, rng: np.random.Generator):
    edges = _edge_array(tree)
    nedges = edges.shape[0]
    baseline = 20.0
    if model == "clock":
        return np.repeat(baseline, nedges)
    if model == "discrete":
        return rng.choice([baseline * 0.6, baseline * 1.4], size=nedges)
    if model == "uncorrelated_lognormal":
        values = rng.normal(0.0, 0.65, size=nedges)
        return baseline * np.exp(values - values.mean())

    child_to_edge = {int(child): eidx for eidx, (child, _) in enumerate(edges)}
    log_rates = np.full(nedges, np.log(baseline), dtype=float)
    for node in tree.treenode.traverse("preorder"):
        if node.is_root():
            continue
        eidx = child_to_edge[node.idx]
        parent_edge = child_to_edge.get(node.up.idx)
        center = np.log(baseline) if parent_edge is None else log_rates[parent_edge]
        log_rates[eidx] = center + rng.normal(0.0, 0.30)
    log_rates -= log_rates.mean() - np.log(baseline)
    return np.exp(log_rates)


def _simulate_dataset(model: str, ntips: int, noise_shape: float, seed: int):
    rng = np.random.default_rng(seed)
    true_tree = _scale_true_tree(ntips, seed)
    edges = _edge_array(true_tree)
    ages = true_tree.get_node_data("height").to_numpy(dtype=float)
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    rates = _simulate_rates(true_tree, model, rng)
    means = times * rates
    noise = rng.gamma(shape=noise_shape, scale=1.0 / noise_shape, size=means.size)
    observed = means * noise
    observed_tree = true_tree.set_node_data(
        "dist", {int(child): float(observed[i]) for i, (child, _) in enumerate(edges)}
    )
    return true_tree, observed_tree, rates, means


def _calibrations(true_tree, regime: str):
    if regime == "root":
        return {-1: 1.0}
    candidates = [
        node
        for node in true_tree[true_tree.treenode.idx].traverse("preorder")
        if not node.is_root() and not node.is_leaf()
    ]
    node = max(candidates, key=lambda value: (value.height, value.idx))
    age = float(node.height)
    return {-1: 1.0, node.idx: (max(0.0, age * 0.9), age * 1.1)}


def _fit_configured(tree, model, calibrations, fit_config, seed):
    kwargs = dict(
        calibrations=calibrations,
        full=True,
        max_iter=fit_config["max_iter"],
        max_fun=fit_config["max_fun"],
        max_refine=fit_config["max_refine"],
        nstarts=fit_config["nstarts"],
        ncores=1,
        seed=seed,
    )
    if model == "discrete":
        kwargs["ncategories"] = fit_config["ncategories"]
    elif model in {"uncorrelated_lognormal", "correlated"}:
        kwargs["lam"] = fit_config["lambda"]
    return tree.mod.edges_make_ultrametric(method=model, **kwargs)


def _primary_worker(payload):
    model = payload["model"]
    seed = payload["seed"]
    try:
        true_tree, observed_tree, true_rates, _ = _simulate_dataset(
            model, payload["ntips"], payload["noise_shape"], seed
        )
        fit = _fit_configured(
            observed_tree,
            model,
            _calibrations(true_tree, payload["calibration"]),
            payload["fit_config"],
            seed,
        )
        truth = true_tree.get_node_data("height").to_numpy(dtype=float)
        estimate = fit["tree"].get_node_data("height").to_numpy(dtype=float)
        errors = estimate[true_tree.ntips :] - truth[true_tree.ntips :]
        mae = float(np.mean(np.abs(errors)))
        bias = float(np.mean(errors))
        rho = None
        if model in {"uncorrelated_lognormal", "correlated"}:
            rho = float(spearmanr(np.log(true_rates), np.log(fit["rates"])).statistic)
        return {
            **{key: payload[key] for key in ("cell", "replicate", "seed")},
            "converged": bool(fit["converged"]),
            "normalized_internal_age_mae": mae,
            "normalized_internal_age_bias": bias,
            "log_rate_spearman": rho,
            "message": str(fit.get("optimizer_message", "")),
        }
    except Exception as exc:
        return {
            **{key: payload[key] for key in ("cell", "replicate", "seed")},
            "converged": False,
            "normalized_internal_age_mae": None,
            "normalized_internal_age_bias": None,
            "log_rate_spearman": None,
            "message": f"{type(exc).__name__}: {exc}",
        }


def _pearson_mean(observed, expected):
    observed = np.asarray(observed, dtype=float)
    expected = np.asarray(expected, dtype=float)
    return float(np.mean((observed - expected) ** 2 / np.maximum(expected, 1e-12)))


def _cv_worker(payload):
    model = payload["model"]
    seed = payload["seed"]
    try:
        true_tree, observed_tree, _, means = _simulate_dataset(
            model, payload["ntips"], payload["noise_shape"], seed
        )
        rng = np.random.default_rng(seed + 10_000_000)
        shape = payload["noise_shape"]
        test_observed = means * rng.gamma(shape, 1.0 / shape, size=means.size)
        cals = _calibrations(true_tree, "root_and_internal_interval")
        selector = _historical_cv_model_select(
            observed_tree,
            calibrations=cals,
            candidate_configs=payload.get("candidate_configs"),
            ncategories=payload["ncategories"],
            lambdas=payload["lambdas"],
            max_iter=payload["fit_config"]["max_iter"],
            max_fun=payload["fit_config"]["max_fun"],
            max_refine=payload["fit_config"]["max_refine"],
            nstarts=1,
            ncores=1,
            seed=seed,
            selection_rule="minimum",
            score="pearson",
        )
        test_scores = []
        for candidate in selector["candidates"]:
            config = candidate["config"]
            try:
                fit = _fit_configured(
                    observed_tree,
                    config["method"],
                    cals,
                    {
                        **payload["fit_config"],
                        "lambda": config.get("lam", payload["fit_config"]["lambda"]),
                        "ncategories": config.get(
                            "ncategories", payload["fit_config"]["ncategories"]
                        ),
                    },
                    seed,
                )
                score = _pearson_mean(test_observed, fit["expected_branch_lengths"])
                if fit["converged"] and np.isfinite(score):
                    test_scores.append((config, score))
            except Exception:
                continue
        selected_score = _pearson_mean(
            test_observed, selector["selected_fit"]["expected_branch_lengths"]
        )
        oracle_score = min(score for _, score in test_scores)
        excess = max(0.0, (selected_score - oracle_score) / max(oracle_score, 1e-12))
        return {
            "family": model,
            "replicate": payload["replicate"],
            "seed": seed,
            "converged": True,
            "selected_config": selector["selected_config"],
            "selected_test_score": selected_score,
            "oracle_test_score": oracle_score,
            "oracle_excess": float(excess),
            "message": "",
        }
    except Exception as exc:
        return {
            "family": model,
            "replicate": payload["replicate"],
            "seed": seed,
            "converged": False,
            "selected_config": None,
            "selected_test_score": None,
            "oracle_test_score": None,
            "oracle_excess": None,
            "message": f"{type(exc).__name__}: {exc}",
        }


def _run_workers(worker, payloads, ncores):
    if ncores == 1:
        return [worker(payload) for payload in payloads]
    results = []
    with ProcessPoolExecutor(max_workers=min(ncores, len(payloads))) as pool:
        futures = [pool.submit(worker, payload) for payload in payloads]
        for future in as_completed(futures):
            results.append(future.result())
    return results


def _wilson_lower(successes, total, z=1.959963984540054):
    if total == 0:
        return 0.0
    p = successes / total
    denom = 1.0 + z * z / total
    center = p + z * z / (2.0 * total)
    spread = z * np.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total))
    return float((center - spread) / denom)


def _aggregate_primary(rows, config):
    gates = config["release_gates"]
    cells = []
    for cell in sorted({row["cell"] for row in rows}):
        subset = [row for row in rows if row["cell"] == cell]
        good = [row for row in subset if row["converged"]]
        noise = cell.split("|")[-1]
        maes = [row["normalized_internal_age_mae"] for row in good]
        biases = [row["normalized_internal_age_bias"] for row in good]
        rhos = [
            row["log_rate_spearman"]
            for row in good
            if row["log_rate_spearman"] is not None
        ]
        summary = {
            "cell": cell,
            "n": len(subset),
            "converged": len(good),
            "convergence_wilson_lower": _wilson_lower(len(good), len(subset)),
            "median_normalized_internal_age_mae": float(np.median(maes))
            if maes
            else None,
            "absolute_normalized_internal_age_bias": abs(float(np.mean(biases)))
            if biases
            else None,
            "median_low_noise_log_rate_spearman": float(np.median(rhos))
            if rhos and noise == "low"
            else None,
        }
        cells.append(summary)

    converged = [row for row in rows if row["converged"]]
    gate_summary = {
        "convergence_wilson_lower": _wilson_lower(len(converged), len(rows)),
        "noise": {},
    }
    checks = {
        "convergence": gate_summary["convergence_wilson_lower"]
        >= gates["convergence_wilson_lower"]
    }
    for noise in config["primary"]["noise"]:
        subset = [row for row in converged if row["cell"].endswith(f"|{noise}")]
        maes = [row["normalized_internal_age_mae"] for row in subset]
        biases = [row["normalized_internal_age_bias"] for row in subset]
        noise_summary = {
            "median_normalized_internal_age_mae": float(np.median(maes))
            if maes
            else None,
            "absolute_normalized_internal_age_bias": abs(float(np.mean(biases)))
            if biases
            else None,
        }
        gate_summary["noise"][noise] = noise_summary
        checks[f"{noise}_age_mae"] = (
            noise_summary["median_normalized_internal_age_mae"] is not None
            and noise_summary["median_normalized_internal_age_mae"]
            <= gates["normalized_internal_age_mae_median"][noise]
        )
        checks[f"{noise}_age_bias"] = (
            noise_summary["absolute_normalized_internal_age_bias"] is not None
            and noise_summary["absolute_normalized_internal_age_bias"]
            <= gates["normalized_internal_age_absolute_bias"][noise]
        )
    low_rhos = [
        row["log_rate_spearman"]
        for row in converged
        if row["cell"].endswith("|low") and row["log_rate_spearman"] is not None
    ]
    gate_summary["median_low_noise_log_rate_spearman"] = (
        float(np.median(low_rhos)) if low_rhos else None
    )
    checks["low_noise_rate_spearman"] = (
        gate_summary["median_low_noise_log_rate_spearman"] is not None
        and gate_summary["median_low_noise_log_rate_spearman"]
        >= gates["low_noise_log_rate_spearman_median"]
    )
    gate_summary["gate_checks"] = checks
    gate_summary["passed"] = all(checks.values())
    return {"gates": gate_summary, "cells": cells}, bool(gate_summary["passed"])


def _aggregate_cv(rows, config):
    good = [row for row in rows if row["converged"]]
    values = [row["oracle_excess"] for row in good]
    gates = config["release_gates"]
    summary = {
        "n": len(rows),
        "converged": len(good),
        "median_oracle_excess": float(np.median(values)) if values else None,
        "p90_oracle_excess": float(np.quantile(values, 0.9)) if values else None,
    }
    checks = {
        "all_datasets_scored": len(good) == len(rows),
        "median_oracle_excess": summary["median_oracle_excess"] is not None
        and summary["median_oracle_excess"] <= gates["cv_oracle_excess_median"],
        "p90_oracle_excess": summary["p90_oracle_excess"] is not None
        and summary["p90_oracle_excess"] <= gates["cv_oracle_excess_90th_percentile"],
    }
    summary["gate_checks"] = checks
    summary["passed"] = all(checks.values())
    return summary, bool(summary["passed"])


def _build_payloads(config, mode):
    primary = config["primary"]
    cv = config["cross_validation"]
    base = int(config["seed"])
    prep = 2 if mode == "smoke" else int(primary["replicates_per_cell"])
    crep = 1 if mode == "smoke" else int(cv["replicates_per_family"])
    ntips_values = [8] if mode == "smoke" else primary["ntips"]
    calibrations = ["root"] if mode == "smoke" else primary["calibrations"]
    noise_items = (
        [("low", primary["noise"]["low"])]
        if mode == "smoke"
        else list(primary["noise"].items())
    )
    primary_payloads = []
    seed_rows = []
    cursor = 0
    for model in primary["models"]:
        for ntips in ntips_values:
            for calibration in calibrations:
                for noise_name, noise in noise_items:
                    cell = f"{model}|{ntips}|{calibration}|{noise_name}"
                    for replicate in range(prep):
                        seed = base + cursor
                        cursor += 1
                        primary_payloads.append(
                            {
                                "cell": cell,
                                "model": model,
                                "ntips": ntips,
                                "calibration": calibration,
                                "noise_shape": noise["gamma_shape"],
                                "fit_config": primary["fit"],
                                "replicate": replicate,
                                "seed": seed,
                            }
                        )
                        seed_rows.append(
                            {
                                "study": "primary",
                                "cell": cell,
                                "replicate": replicate,
                                "seed": seed,
                            }
                        )
    cv_payloads = []
    for model in primary["models"]:
        for replicate in range(crep):
            seed = base + cursor
            cursor += 1
            payload = {
                "model": model,
                "ntips": cv["ntips"],
                "noise_shape": cv["noise_gamma_shape"],
                "ncategories": cv["ncategories"],
                "lambdas": cv["lambdas"],
                "fit_config": primary["fit"],
                "replicate": replicate,
                "seed": seed,
            }
            if mode == "smoke":
                payload["candidate_configs"] = [
                    {"method": "clock"},
                    {"method": "uncorrelated_lognormal", "lam": 1.0},
                ]
            cv_payloads.append(payload)
            seed_rows.append(
                {
                    "study": "cross_validation",
                    "family": model,
                    "replicate": replicate,
                    "seed": seed,
                }
            )
    return primary_payloads, cv_payloads, seed_rows


def _environment():
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "toytree": toytree.__version__,
    }


def main(argv=None):
    """Run the pinned version-1 validation study."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("full", "smoke"), default="full")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    args = parser.parse_args(argv)
    if args.ncores < 1:
        parser.error("--ncores must be positive")
    config = json.loads(CONFIG_PATH.read_text())
    primary_payloads, cv_payloads, seeds = _build_payloads(config, args.mode)
    primary_rows = _run_workers(_primary_worker, primary_payloads, args.ncores)
    cv_rows = _run_workers(_cv_worker, cv_payloads, args.ncores)
    primary_summary, primary_passed = _aggregate_primary(primary_rows, config)
    cv_summary, cv_passed = _aggregate_cv(cv_rows, config)
    release_eligible = args.mode == "full"
    results = {
        "study_version": config["study_version"],
        "mode": args.mode,
        "release_eligible": release_eligible,
        "primary": {"summary": primary_summary, "replicates": primary_rows},
        "cross_validation": {"summary": cv_summary, "datasets": cv_rows},
        "all_release_gates_passed": bool(
            release_eligible and primary_passed and cv_passed
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / f"seeds-{args.mode}.json").write_text(
        json.dumps(seeds, indent=2) + "\n"
    )
    (args.output_dir / f"environment-{args.mode}.json").write_text(
        json.dumps(_environment(), indent=2) + "\n"
    )
    (args.output_dir / f"results-{args.mode}.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {
                "mode": args.mode,
                "primary_passed": primary_passed,
                "cv_passed": cv_passed,
                "all_release_gates_passed": results["all_release_gates_passed"],
            }
        )
    )
    return 0 if (args.mode == "smoke" or results["all_release_gates_passed"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
