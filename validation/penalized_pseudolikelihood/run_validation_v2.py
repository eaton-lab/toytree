#!/usr/bin/env python

"""Run resumable version-2 validation for ultrametric pseudolikelihood models."""

# ruff: noqa: E402 -- thread limits must be set before numerical imports.

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import platform
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

# Dataset-level process parallelism is already controlled by --ncores.
# Prevent BLAS/OpenMP from multiplying that parallelism in every worker.
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
from toytree.core import ToyTree
from toytree.mod._src.penalized_pseudolikelihood.model_selection import (
    _fit_candidate,
    _fit_cv_fold,
    _historical_cv_model_select,
    _normalize_candidates,
    _prediction_score,
    _select_candidate_summaries,
)

toytree.set_log_level("WARNING")

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CONFIG_PATH = HERE / "config-v2.json"
CACHE_SCHEMA_VERSION = 1
CV_EPS = 1e-12


def _json_hash(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def _source_hash() -> str:
    """Hash only code that can change fitted values or fold predictions."""
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    digest = hashlib.sha256()
    for name in (
        "clock.py",
        "correlated.py",
        "discrete.py",
        "uncorrelated_lognormal.py",
        "utils.py",
    ):
        path = root / name
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    digest.update(inspect.getsource(_fit_candidate).encode())
    digest.update(inspect.getsource(_fit_cv_fold).encode())
    for function in (
        _scale_true_tree,
        _simulate_rates,
        _simulate_dataset,
        _calibrations,
        _fit_configured,
    ):
        digest.update(inspect.getsource(function).encode())
    return digest.hexdigest()


def _edge_array(tree: ToyTree) -> np.ndarray:
    return np.asarray(tree.get_edges("idx"), dtype=int)


def _scale_true_tree(ntips: int, seed: int) -> ToyTree:
    tree = toytree.rtree.bdtree(ntips=ntips, b=1.0, d=0.2, seed=seed)
    root = tree.treenode
    while root.up is not None:
        root = root.up
    tree = ToyTree(root).mod.remove_unary_nodes()
    return tree.mod.edges_scale_to_root_height(1.0)


def _simulate_rates(
    tree: ToyTree,
    model: str,
    rng: np.random.Generator,
    simulation: dict[str, Any],
) -> np.ndarray:
    edges = _edge_array(tree)
    nedges = edges.shape[0]
    baseline = float(simulation["baseline_rate"])
    if model == "clock":
        return np.repeat(baseline, nedges)
    if model == "discrete":
        multipliers = np.asarray(simulation["discrete_multipliers"], dtype=float)
        return baseline * rng.choice(multipliers, size=nedges)
    if model == "uncorrelated_lognormal":
        sigma = float(simulation["uncorrelated_log_sigma"])
        values = rng.normal(0.0, sigma, size=nedges)
        return baseline * np.exp(values - values.mean())

    sigma = float(simulation["correlated_log_sigma"])
    child_to_edge = {int(child): eidx for eidx, (child, _) in enumerate(edges)}
    log_rates = np.full(nedges, np.log(baseline), dtype=float)
    for node in tree.treenode.traverse("preorder"):
        if node.is_root():
            continue
        eidx = child_to_edge[node.idx]
        parent_edge = child_to_edge.get(node.up.idx)
        center = np.log(baseline) if parent_edge is None else log_rates[parent_edge]
        log_rates[eidx] = center + rng.normal(0.0, sigma)
    log_rates -= log_rates.mean() - np.log(baseline)
    return np.exp(log_rates)


def _simulate_dataset(
    model: str,
    ntips: int,
    track: str,
    seed: int,
    simulation: dict[str, Any],
) -> tuple[ToyTree, ToyTree, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    true_tree = _scale_true_tree(ntips, seed)
    edges = _edge_array(true_tree)
    ages = true_tree.get_node_data("height").to_numpy(dtype=float)
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    rates = _simulate_rates(true_tree, model, rng, simulation)
    means = times * rates
    if track == "count":
        observed = rng.poisson(means).astype(float)
    elif track == "gamma":
        shape = float(simulation["gamma_shape"])
        observed = means * rng.gamma(shape, 1.0 / shape, size=means.size)
    else:
        raise ValueError(f"unknown simulation track: {track}")
    observed_tree = true_tree.set_node_data(
        "dist", {int(child): float(observed[i]) for i, (child, _) in enumerate(edges)}
    )
    return true_tree, observed_tree, rates, means, observed


def _calibrations(true_tree: ToyTree, regime: str) -> dict[int, Any]:
    if regime == "fixed_internal_ages":
        return {
            int(node.idx): float(node.height)
            for node in true_tree.treenode.traverse("preorder")
            if not node.is_leaf()
        }
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


def _true_lambda(model: str, simulation: dict[str, Any]) -> float:
    if model == "uncorrelated_lognormal":
        sigma = float(simulation["uncorrelated_log_sigma"])
    elif model == "correlated":
        sigma = float(simulation["correlated_log_sigma"])
    else:
        return 0.0
    return float(1.0 / (2.0 * sigma * sigma))


def _fit_options(fit_config: dict[str, Any], seed: int) -> dict[str, Any]:
    return {
        "max_iter": int(fit_config["max_iter"]),
        "max_fun": int(fit_config["max_fun"]),
        "max_refine": int(fit_config["max_refine"]),
        "nstarts": (
            None if fit_config.get("nstarts") is None else int(fit_config["nstarts"])
        ),
        "ncores": 1,
        "seed": int(seed),
    }


def _fit_configured(
    tree: ToyTree,
    config: dict[str, Any],
    calibrations: dict[int, Any],
    fit_config: dict[str, Any],
    seed: int,
) -> dict[str, Any]:
    return _fit_candidate(
        tree,
        config,
        calibrations,
        None,
        _fit_options(fit_config, seed),
    )


def _slim_fit(fit: dict[str, Any]) -> dict[str, Any]:
    tree = fit["tree"]
    result = {
        "converged": bool(fit["converged"]),
        "optimizer_message": str(fit.get("optimizer_message", "")),
        "pseudologlik": float(fit["pseudologlik"]),
        "penalized_pseudologlik": float(fit["penalized_pseudologlik"]),
        "nparams": int(fit["nparams"]),
        "expected_branch_lengths": [
            float(value) for value in fit["expected_branch_lengths"]
        ],
        "ages": tree.get_node_data("height").to_numpy(dtype=float).tolist(),
    }
    if "penalty" in fit:
        result["penalty"] = float(fit["penalty"])
    if "rate" in fit:
        result["rates"] = [float(fit["rate"])]
    elif "rates" in fit:
        result["rates"] = [float(value) for value in fit["rates"]]
    if "weights" in fit:
        result["weights"] = [float(value) for value in fit["weights"]]
    return result


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    control = "fixed" if payload.get("fixed_ages", False) else "free"
    name = (
        f"{payload['kind']}-{payload['family']}-{payload['track']}-"
        f"n{payload['ntips']}-{control}-r{payload['replicate']:04d}.json"
    )
    return output_dir / "cache-v2" / payload["mode"] / payload["kind"] / name


def _load_matching_cache(path: Path, fingerprint: str) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        record = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if (
        record.get("cache_schema_version") == CACHE_SCHEMA_VERSION
        and record.get("fingerprint") == fingerprint
    ):
        return record
    return None


def _record_base(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "cache_schema_version": CACHE_SCHEMA_VERSION,
        "fingerprint": payload["fingerprint"],
        "kind": payload["kind"],
        "mode": payload["mode"],
        "family": payload["family"],
        "track": payload["track"],
        "ntips": int(payload["ntips"]),
        "calibration": payload["calibration"],
        "fixed_ages": bool(payload.get("fixed_ages", False)),
        "replicate": int(payload["replicate"]),
        "seed": int(payload["seed"]),
    }


def _primary_worker(payload: dict[str, Any]) -> str:
    path = Path(payload["cache_path"])
    if payload["resume"] and _load_matching_cache(path, payload["fingerprint"]):
        return str(path)
    record = _record_base(payload)
    try:
        true_tree, observed_tree, true_rates, means, observed = _simulate_dataset(
            payload["family"],
            payload["ntips"],
            payload["track"],
            payload["seed"],
            payload["simulation"],
        )
        calibrations = _calibrations(true_tree, payload["calibration"])
        config: dict[str, Any] = {"method": payload["family"]}
        if payload["family"] == "discrete":
            config["ncategories"] = int(payload["fit_config"]["ncategories"])
        elif payload["family"] in {"uncorrelated_lognormal", "correlated"}:
            config["lam"] = _true_lambda(payload["family"], payload["simulation"])
        fit = _fit_configured(
            observed_tree,
            config,
            calibrations,
            payload["fit_config"],
            payload["seed"],
        )
        record.update(
            {
                "status": "ok",
                "config": config,
                "true_ages": true_tree.get_node_data("height")
                .to_numpy(dtype=float)
                .tolist(),
                "true_rates": true_rates.tolist(),
                "true_means": means.tolist(),
                "observed": observed.tolist(),
                "fit": _slim_fit(fit),
            }
        )
    except Exception as exc:
        record.update({"status": "error", "message": f"{type(exc).__name__}: {exc}"})
    _atomic_json(path, record)
    return str(path)


def _fold_cache(candidate: dict[str, Any]) -> dict[str, Any]:
    """Return JSON-native fold diagnostics for one candidate."""
    folds = []
    for raw in candidate["folds"]:
        folds.append(
            {
                "fold": int(raw["fold"]),
                "edge_index": int(raw["edge_index"]),
                "child_index": int(raw["child_index"]),
                "observed": float(raw["observed"]),
                "predicted": float(raw["predicted"]),
                "score": float(raw["score"]),
                "pseudologlik": (
                    None if raw["pseudologlik"] is None else float(raw["pseudologlik"])
                ),
                "penalized_pseudologlik": (
                    None
                    if raw["penalized_pseudologlik"] is None
                    else float(raw["penalized_pseudologlik"])
                ),
                "penalty": (None if raw["penalty"] is None else float(raw["penalty"])),
                "converged": bool(raw["converged"]),
                "optimizer_message": str(raw["optimizer_message"]),
                "nparams": int(raw["nparams"]),
            }
        )
    return {
        "config": dict(candidate["config"]),
        "label": str(candidate["label"]),
        "nparams": int(candidate["nparams"]),
        "folds": folds,
    }


def _cv_worker(payload: dict[str, Any]) -> str:
    path = Path(payload["cache_path"])
    if payload["resume"] and _load_matching_cache(path, payload["fingerprint"]):
        return str(path)
    record = _record_base(payload)
    try:
        true_tree, observed_tree, true_rates, means, observed = _simulate_dataset(
            payload["family"],
            payload["ntips"],
            payload["track"],
            payload["seed"],
            payload["simulation"],
        )
        calibrations = _calibrations(true_tree, payload["calibration"])
        selector = _historical_cv_model_select(
            observed_tree,
            calibrations=calibrations,
            candidate_configs=payload["candidate_configs"],
            max_iter=payload["fit_config"]["max_iter"],
            max_fun=payload["fit_config"]["max_fun"],
            max_refine=payload["fit_config"]["max_refine"],
            nstarts=payload["fit_config"]["nstarts"],
            ncores=1,
            seed=payload["seed"],
            selection_rule="one_se",
            score="pearson",
        )
        candidates = []
        for candidate in selector["candidates"]:
            cached = _fold_cache(candidate)
            try:
                fit = _fit_configured(
                    observed_tree,
                    candidate["config"],
                    calibrations,
                    payload["fit_config"],
                    payload["seed"],
                )
                cached["full_fit"] = _slim_fit(fit)
            except Exception as exc:
                cached["full_fit"] = {
                    "converged": False,
                    "optimizer_message": f"{type(exc).__name__}: {exc}",
                }
            candidates.append(cached)
        record.update(
            {
                "status": "ok",
                "true_ages": true_tree.get_node_data("height")
                .to_numpy(dtype=float)
                .tolist(),
                "true_rates": true_rates.tolist(),
                "true_means": means.tolist(),
                "observed": observed.tolist(),
                "candidates": candidates,
            }
        )
    except Exception as exc:
        record.update({"status": "error", "message": f"{type(exc).__name__}: {exc}"})
    _atomic_json(path, record)
    return str(path)


def _run_workers(worker, payloads: list[dict[str, Any]], ncores: int) -> list[str]:
    if ncores == 1:
        return [worker(payload) for payload in payloads]
    paths = []
    with ProcessPoolExecutor(max_workers=min(ncores, len(payloads))) as pool:
        futures = [pool.submit(worker, payload) for payload in payloads]
        for future in as_completed(futures):
            paths.append(future.result())
    return paths


def _candidate_configs(config: dict[str, Any], smoke: bool) -> list[dict[str, Any]]:
    if smoke:
        return [
            {"method": "clock"},
            {"method": "uncorrelated_lognormal", "lam": 1.0},
        ]
    probe = toytree.rtree.unittree(24)
    return _normalize_candidates(
        probe,
        None,
        config["candidates"]["ncategories"],
        config["candidates"]["lambdas"],
    )


def _payloads(
    config: dict[str, Any],
    mode: str,
    output_dir: Path,
    resume: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    simulation = config["simulation"]
    models = simulation["models"]
    tracks = simulation["tracks"]
    source_hash = _source_hash()
    if mode == "smoke":
        base_seed = int(config["development_seed"]) - 1000
        primary_reps = 1
        primary_ntips = [4]
        primary_calibrations = ["root"]
        cv_reps = 1
        cv_ntips = [4]
        cv_calibration = "root"
        fixed_controls = 0
        fit_config = {
            **config["fit"],
            "max_iter": 500,
            "max_fun": 1000,
            "max_refine": 2,
        }
    elif mode == "pilot":
        base_seed = int(config["development_seed"])
        primary_reps = int(config["pilot"]["replicates"])
        primary_ntips = list(config["pilot"]["ntips"])
        primary_calibrations = [config["pilot"]["calibration"]]
        cv_reps = int(config["pilot"]["replicates"])
        cv_ntips = list(config["pilot"]["ntips"])
        cv_calibration = config["pilot"]["calibration"]
        fixed_controls = int(config["pilot"]["fixed_age_controls"])
        fit_config = dict(config["fit"])
    else:
        base_seed = int(config["confirmation_seed"])
        primary_reps = int(config["confirmation"]["primary_replicates"])
        primary_ntips = list(config["confirmation"]["primary_ntips"])
        primary_calibrations = list(config["confirmation"]["primary_calibrations"])
        cv_reps = int(config["confirmation"]["cv_replicates"])
        cv_ntips = [int(config["confirmation"]["cv_ntips"])]
        cv_calibration = config["confirmation"]["cv_calibration"]
        fixed_controls = 0
        fit_config = dict(config["fit"])

    candidates = _candidate_configs(config, mode == "smoke")
    primary_payloads = []
    cv_payloads = []
    seeds = []
    cursor = 0

    def add_payload(kind, family, track, ntips, calibration, replicate, fixed):
        nonlocal cursor
        seed = base_seed + cursor
        cursor += 1
        payload = {
            "kind": kind,
            "mode": mode,
            "family": family,
            "track": track,
            "ntips": int(ntips),
            "calibration": "fixed_internal_ages" if fixed else calibration,
            "fixed_ages": bool(fixed),
            "replicate": int(replicate),
            "seed": int(seed),
            "simulation": simulation,
            "fit_config": fit_config,
            "candidate_configs": candidates,
            "resume": bool(resume),
            "source_hash": source_hash,
        }
        identity = {key: value for key, value in payload.items() if key != "resume"}
        payload["fingerprint"] = _json_hash(identity)
        payload["cache_path"] = str(_cache_path(output_dir, payload))
        seeds.append(
            {
                "kind": kind,
                "family": family,
                "track": track,
                "ntips": int(ntips),
                "fixed_ages": bool(fixed),
                "replicate": int(replicate),
                "seed": int(seed),
            }
        )
        return payload

    for family in models:
        for track in tracks:
            for ntips in primary_ntips:
                for calibration in primary_calibrations:
                    for replicate in range(primary_reps):
                        primary_payloads.append(
                            add_payload(
                                "primary",
                                family,
                                track,
                                ntips,
                                calibration,
                                replicate,
                                False,
                            )
                        )
    for family in models:
        for track in tracks:
            for ntips in cv_ntips:
                for replicate in range(cv_reps):
                    cv_payloads.append(
                        add_payload(
                            "cv",
                            family,
                            track,
                            ntips,
                            cv_calibration,
                            replicate,
                            False,
                        )
                    )
            if mode == "pilot":
                for replicate in range(fixed_controls):
                    primary_payloads.append(
                        add_payload(
                            "primary",
                            family,
                            track,
                            12,
                            cv_calibration,
                            replicate,
                            True,
                        )
                    )
                    cv_payloads.append(
                        add_payload(
                            "cv",
                            family,
                            track,
                            12,
                            cv_calibration,
                            replicate,
                            True,
                        )
                    )
    return primary_payloads, cv_payloads, seeds


def _read_records(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for payload in payloads:
        path = Path(payload["cache_path"])
        record = _load_matching_cache(path, payload["fingerprint"])
        if record is None:
            raise RuntimeError(f"missing or stale validation cache: {path}")
        records.append(record)
    return records


def _rescore_candidates(
    record: dict[str, Any],
    score: str,
    selection_rule: str,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    summaries = []
    for cached in record["candidates"]:
        folds = []
        for raw in cached["folds"]:
            fold = dict(raw)
            if fold["converged"]:
                fold["score"] = _prediction_score(
                    fold["observed"], fold["predicted"], score
                )
            else:
                fold["score"] = float("inf")
            folds.append(fold)
        values = np.asarray([fold["score"] for fold in folds], dtype=float)
        valid = bool(
            len(folds) > 1
            and all(fold["converged"] for fold in folds)
            and np.all(np.isfinite(values))
        )
        summaries.append(
            {
                "config": dict(cached["config"]),
                "label": cached["label"],
                "valid": valid,
                "mean_score": float(np.mean(values)) if valid else float("inf"),
                "standard_error": (
                    float(np.std(values, ddof=1) / np.sqrt(values.size))
                    if valid
                    else float("inf")
                ),
                "nparams": int(cached["nparams"]),
                "folds": folds,
            }
        )
    winner, minimum = _select_candidate_summaries(summaries, selection_rule)
    return winner, minimum, summaries


def _population_risk(
    predicted: list[float],
    true_means: np.ndarray,
    track: str,
    gamma_shape: float,
) -> float:
    values = np.asarray(predicted, dtype=float)
    if track == "count":
        variance = np.maximum(true_means, CV_EPS)
    else:
        variance = np.maximum(true_means * true_means / gamma_shape, CV_EPS)
    return float(np.mean((values - true_means) ** 2 / variance))


def _score_cv_record(
    record: dict[str, Any],
    simulation: dict[str, Any],
) -> dict[str, Any]:
    base = {
        key: record[key]
        for key in (
            "family",
            "track",
            "ntips",
            "fixed_ages",
            "replicate",
            "seed",
        )
    }
    if record["status"] != "ok":
        return {
            **base,
            "converged": False,
            "message": record.get("message", "fit cache failed"),
        }
    try:
        winner, minimum, summaries = _rescore_candidates(record, "pearson", "one_se")
        full_by_label = {
            candidate["label"]: candidate["full_fit"]
            for candidate in record["candidates"]
        }
        true_means = np.asarray(record["true_means"], dtype=float)
        risks = {}
        for candidate in summaries:
            fit = full_by_label[candidate["label"]]
            if fit.get("converged", False):
                risks[candidate["label"]] = _population_risk(
                    fit["expected_branch_lengths"],
                    true_means,
                    record["track"],
                    float(simulation["gamma_shape"]),
                )
        selected_label = winner["label"]
        if selected_label not in risks:
            raise RuntimeError("selected candidate full fit did not converge")
        oracle_label = min(risks, key=risks.get)
        selected_risk = float(risks[selected_label])
        oracle_risk = float(risks[oracle_label])
        return {
            **base,
            "converged": True,
            "selected_config": winner["config"],
            "minimum_cv_config": minimum["config"],
            "selected_population_risk": selected_risk,
            "oracle_population_risk": oracle_risk,
            "population_regret": max(0.0, selected_risk - oracle_risk),
            "oracle_label": oracle_label,
            "true_family_is_oracle": oracle_label.startswith(record["family"]),
            "message": "",
        }
    except Exception as exc:
        return {
            **base,
            "converged": False,
            "message": f"{type(exc).__name__}: {exc}",
        }


def _wilson_lower(successes: int, total: int, z: float = 1.959963984540054) -> float:
    if total == 0:
        return 0.0
    p = successes / total
    denom = 1.0 + z * z / total
    center = p + z * z / (2.0 * total)
    spread = z * np.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total))
    return float((center - spread) / denom)


def _score_primary_record(record: dict[str, Any]) -> dict[str, Any]:
    base = {
        key: record[key]
        for key in (
            "family",
            "track",
            "ntips",
            "calibration",
            "fixed_ages",
            "replicate",
            "seed",
        )
    }
    if record["status"] != "ok":
        return {
            **base,
            "converged": False,
            "age_mae": None,
            "age_bias": None,
            "log_rate_spearman": None,
            "message": record.get("message", "fit cache failed"),
        }
    fit = record["fit"]
    converged = bool(fit["converged"])
    true_ages = np.asarray(record["true_ages"], dtype=float)
    ages = np.asarray(fit["ages"], dtype=float)
    ntips = int(record["ntips"])
    errors = ages[ntips:] - true_ages[ntips:]
    rho = None
    if record["family"] in {"uncorrelated_lognormal", "correlated"}:
        fitted_rates = np.asarray(fit.get("rates", []), dtype=float)
        true_rates = np.asarray(record["true_rates"], dtype=float)
        if fitted_rates.shape == true_rates.shape:
            rho = float(spearmanr(np.log(true_rates), np.log(fitted_rates)).statistic)
    return {
        **base,
        "converged": converged,
        "age_mae": float(np.mean(np.abs(errors))),
        "age_bias": float(np.mean(errors)),
        "log_rate_spearman": rho,
        "message": str(fit.get("optimizer_message", "")),
    }


def _aggregate_primary(
    rows: list[dict[str, Any]],
    gates: dict[str, Any],
) -> tuple[dict[str, Any], bool]:
    methods = {}
    passed = True
    for family in sorted({row["family"] for row in rows}):
        subset = [
            row for row in rows if row["family"] == family and not row["fixed_ages"]
        ]
        good = [row for row in subset if row["converged"]]
        maes = [row["age_mae"] for row in good]
        biases = [row["age_bias"] for row in good]
        rhos = [
            row["log_rate_spearman"]
            for row in good
            if row["log_rate_spearman"] is not None
        ]
        summary = {
            "n": len(subset),
            "converged": len(good),
            "convergence_wilson_lower": _wilson_lower(len(good), len(subset)),
            "median_age_mae": float(np.median(maes)) if maes else None,
            "absolute_age_bias": abs(float(np.mean(biases))) if biases else None,
            "median_log_rate_spearman": float(np.median(rhos)) if rhos else None,
        }
        checks = {
            "convergence": summary["convergence_wilson_lower"]
            >= gates["convergence_wilson_lower"],
            "age_mae": summary["median_age_mae"] is not None
            and summary["median_age_mae"]
            <= gates["normalized_internal_age_mae_median"],
            "age_bias": summary["absolute_age_bias"] is not None
            and summary["absolute_age_bias"]
            <= gates["normalized_internal_age_absolute_bias"],
        }
        if family in {"uncorrelated_lognormal", "correlated"}:
            checks["rate_spearman"] = (
                summary["median_log_rate_spearman"] is not None
                and summary["median_log_rate_spearman"]
                >= gates["log_rate_spearman_median"]
            )
        summary["gate_checks"] = checks
        summary["passed"] = all(checks.values())
        passed = passed and summary["passed"]
        methods[family] = summary
    controls = [row for row in rows if row["fixed_ages"]]
    control_summary = {}
    for family in sorted({row["family"] for row in controls}):
        rhos = [
            row["log_rate_spearman"]
            for row in controls
            if row["family"] == family
            and row["converged"]
            and row["log_rate_spearman"] is not None
        ]
        control_summary[family] = {
            "n": sum(row["family"] == family for row in controls),
            "median_log_rate_spearman": float(np.median(rhos)) if rhos else None,
        }
    return {"methods": methods, "fixed_age_controls": control_summary}, bool(passed)


def _aggregate_cv(
    rows: list[dict[str, Any]],
    gates: dict[str, Any],
) -> tuple[dict[str, Any], bool]:
    methods = {}
    passed = True
    for family in sorted({row["family"] for row in rows}):
        subset = [
            row for row in rows if row["family"] == family and not row["fixed_ages"]
        ]
        good = [row for row in subset if row["converged"]]
        regrets = [row["population_regret"] for row in good]
        summary = {
            "n": len(subset),
            "converged": len(good),
            "median_population_regret": float(np.median(regrets)) if regrets else None,
            "p90_population_regret": float(np.quantile(regrets, 0.9))
            if regrets
            else None,
            "true_family_oracle_rate": (
                float(np.mean([row["true_family_is_oracle"] for row in good]))
                if good
                else None
            ),
        }
        checks = {
            "all_datasets_scored": len(good) == len(subset),
            "median_population_regret": summary["median_population_regret"] is not None
            and summary["median_population_regret"]
            <= gates["population_regret_median"],
            "p90_population_regret": summary["p90_population_regret"] is not None
            and summary["p90_population_regret"]
            <= gates["population_regret_90th_percentile"],
        }
        summary["gate_checks"] = checks
        summary["passed"] = all(checks.values())
        passed = passed and summary["passed"]
        methods[family] = summary
    controls = [row for row in rows if row["fixed_ages"]]
    return {
        "methods": methods,
        "fixed_age_controls": controls,
    }, bool(passed)


def _environment(config_hash: str, source_hash: str) -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "toytree": toytree.__version__,
        "config_hash": config_hash,
        "source_hash": source_hash,
        "cache_schema_version": CACHE_SCHEMA_VERSION,
    }


def main(argv=None) -> int:
    """Run one fitting or scoring stage of validation study v2."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("smoke", "pilot", "confirmation"),
        default="pilot",
    )
    parser.add_argument("--stage", choices=("all", "fit", "score"), default="all")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE / "v2")
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args(argv)
    if args.ncores < 1:
        parser.error("--ncores must be positive")

    config = json.loads(CONFIG_PATH.read_text())
    primary_payloads, cv_payloads, seeds = _payloads(
        config,
        args.mode,
        args.output_dir,
        not args.no_resume,
    )
    if args.stage in {"all", "fit"}:
        _run_workers(_primary_worker, primary_payloads, args.ncores)
        _run_workers(_cv_worker, cv_payloads, args.ncores)
        _atomic_json(
            args.output_dir / f"seeds-v2-{args.mode}.json",
            {"study_version": 2, "seeds": seeds},
        )
        if args.stage == "fit":
            print(
                json.dumps(
                    {
                        "mode": args.mode,
                        "stage": "fit",
                        "primary_caches": len(primary_payloads),
                        "cv_caches": len(cv_payloads),
                    }
                )
            )
            return 0

    primary_records = _read_records(primary_payloads)
    cv_records = _read_records(cv_payloads)
    primary_rows = [_score_primary_record(record) for record in primary_records]
    cv_rows = [_score_cv_record(record, config["simulation"]) for record in cv_records]
    primary_summary, primary_passed = _aggregate_primary(
        primary_rows, config["release_gates"]
    )
    cv_summary, cv_passed = _aggregate_cv(cv_rows, config["release_gates"])
    release_eligible = args.mode == "confirmation"
    all_passed = bool(release_eligible and primary_passed and cv_passed)
    results = {
        "study_version": 2,
        "mode": args.mode,
        "release_eligible": release_eligible,
        "primary": {"summary": primary_summary, "replicates": primary_rows},
        "cross_validation": {"summary": cv_summary, "datasets": cv_rows},
        "all_release_gates_passed": all_passed,
    }
    _atomic_json(args.output_dir / f"results-v2-{args.mode}.json", results)
    config_hash = _json_hash(config)
    _atomic_json(
        args.output_dir / f"environment-v2-{args.mode}.json",
        _environment(config_hash, _source_hash()),
    )
    print(
        json.dumps(
            {
                "mode": args.mode,
                "primary_passed": primary_passed,
                "cv_passed": cv_passed,
                "all_release_gates_passed": all_passed,
            }
        )
    )
    if args.mode != "confirmation":
        return 0
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
