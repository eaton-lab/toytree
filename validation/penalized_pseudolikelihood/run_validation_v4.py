#!/usr/bin/env python

"""Validate chronos-relaxed parity and uncorrelated-lognormal utility."""

# ruff: noqa: E402 -- thread limits must precede numerical imports.

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
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
from toytree.mod._src.penalized_pseudolikelihood.relaxed import (
    edges_make_ultrametric_relaxed,
)
from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    edges_make_ultrametric_uncorrelated_lognormal,
)
from validation.penalized_pseudolikelihood.run_validation_v2 import (
    _edge_array,
    _scale_true_tree,
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v4.json"
CACHE_SCHEMA_VERSION = 1
METHODS = ("relaxed", "uncorrelated_lognormal")
RATE_PROCESSES = ("gamma", "lognormal")


def _json_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _source_hash() -> str:
    digest = hashlib.sha256()
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    for name in ("uncorrelated_lognormal.py", "relaxed.py", "utils.py"):
        path = root / name
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest()


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _simulate_dataset(
    rate_process: str,
    ntips: int,
    track: str,
    seed: int,
    simulation: dict[str, Any],
):
    rng = np.random.default_rng(seed)
    true_tree = _scale_true_tree(ntips, seed)
    edges = _edge_array(true_tree)
    ages = true_tree.get_node_data("height").to_numpy(dtype=float)
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    baseline = float(simulation["baseline_rate"])
    if rate_process == "lognormal":
        sigma = float(simulation["lognormal_log_sigma"])
        values = rng.normal(0.0, sigma, size=edges.shape[0])
        rates = baseline * np.exp(values - values.mean())
    elif rate_process == "gamma":
        rates = rng.gamma(shape=baseline, scale=1.0, size=edges.shape[0])
    else:
        raise ValueError(f"unknown rate process: {rate_process}")
    means = times * rates
    if track == "count":
        observed = rng.poisson(means).astype(float)
    elif track == "gamma":
        shape = float(simulation["gamma_shape"])
        observed = means * rng.gamma(shape, 1.0 / shape, size=means.size)
    else:
        raise ValueError(f"unknown observation track: {track}")
    observed_tree = true_tree.set_node_data(
        "dist", {int(child): float(observed[i]) for i, (child, _) in enumerate(edges)}
    )
    return true_tree, observed_tree, rates, means, observed


def _calibrations(tree, regime):
    """Return feasible root, interior-node, or fixed-age calibrations."""
    root_age = float(tree.treenode.height)
    if regime == "fixed_internal_ages":
        return {
            int(node.idx): float(node.height)
            for node in tree.treenode.traverse("preorder")
            if not node.is_leaf()
        }
    if regime == "root":
        return {-1: root_age}
    candidates = [
        node
        for node in tree.treenode.traverse("preorder")
        if not node.is_root()
        and not node.is_leaf()
        and float(node.height) <= 0.8 * root_age
    ]
    if not candidates:
        raise RuntimeError("simulated tree has no suitable interior calibration node")
    node = max(candidates, key=lambda value: (value.height, value.idx))
    age = float(node.height)
    return {
        -1: root_age,
        int(node.idx): (0.9 * age, min(1.1 * age, 0.9 * root_age)),
    }


def _fit(method: str, tree, lam: float, calibrations, payload):
    function = (
        edges_make_ultrametric_relaxed
        if method == "relaxed"
        else edges_make_ultrametric_uncorrelated_lognormal
    )
    fit = function(
        tree,
        lam=float(lam),
        calibrations=calibrations,
        full=True,
        inplace=False,
        max_iter=int(payload["fit"]["max_iter"]),
        max_fun=int(payload["fit"]["max_fun"]),
        max_refine=int(payload["fit"]["max_refine"]),
        nstarts=int(payload["fit"]["nstarts"]),
        ncores=1,
        seed=int(payload["seed"]),
    )
    return {
        "converged": bool(fit["converged"]),
        "optimizer_message": str(fit.get("optimizer_message", "")),
        "ages": fit["tree"].get_node_data("height").to_numpy(dtype=float).tolist(),
        "rates": [float(value) for value in fit["rates"]],
        "pseudologlik": float(fit["pseudologlik"]),
        "penalized_pseudologlik": float(fit["penalized_pseudologlik"]),
        "penalty": float(fit["penalty"]),
    }


def _cache_path(output_dir: Path, payload: dict[str, Any]) -> Path:
    fixed = "fixed" if payload["fixed_ages"] else "free"
    name = (
        f"{payload['rate_process']}-{payload['track']}-n{payload['ntips']}-"
        f"{payload['calibration']}-{fixed}-r{payload['replicate']:04d}.json"
    )
    return output_dir / "cache-v4" / payload["mode"] / name


def _worker(payload: dict[str, Any]) -> str:
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
            "rate_process",
            "track",
            "ntips",
            "calibration",
            "fixed_ages",
            "replicate",
            "seed",
            "fingerprint",
        )
    }
    record["cache_schema_version"] = CACHE_SCHEMA_VERSION
    try:
        true_tree, observed_tree, true_rates, means, observed = _simulate_dataset(
            payload["rate_process"],
            int(payload["ntips"]),
            payload["track"],
            int(payload["seed"]),
            payload["simulation"],
        )
        calibrations = _calibrations(
            true_tree,
            "fixed_internal_ages" if payload["fixed_ages"] else payload["calibration"],
        )
        fits = {}
        for method in METHODS:
            fits[method] = {}
            for lam in payload["lambdas"][method]:
                fits[method][str(float(lam))] = _fit(
                    method, observed_tree, float(lam), calibrations, payload
                )
        record.update(
            {
                "status": "ok",
                "true_ages": true_tree.get_node_data("height")
                .to_numpy(dtype=float)
                .tolist(),
                "true_rates": true_rates.tolist(),
                "true_means": means.tolist(),
                "observed": observed.tolist(),
                "fits": fits,
            }
        )
    except Exception as exc:
        record.update({"status": "error", "message": f"{type(exc).__name__}: {exc}"})
    _atomic_json(path, record)
    return str(path)


def _payloads(config, mode, output_dir, resume, selected):
    if mode == "smoke":
        base_seed = int(config["development_seed"]) - 1000
        cells = [(process, "count", 8, "root_and_internal_interval", False, 1)
                 for process in RATE_PROCESSES]
        lambdas = {method: [0.1, 1.0] for method in METHODS}
        fit = {**config["fit"], "max_iter": 300, "max_fun": 600, "max_refine": 2}
    elif mode == "pilot":
        base_seed = int(config["development_seed"])
        pilot = config["pilot"]
        cells = [
            (
                process,
                "count",
                int(pilot["ntips"]),
                pilot["calibration"],
                False,
                int(pilot["replicates"]),
            )
            for process in RATE_PROCESSES
        ]
        lambdas = {method: list(pilot["lambdas"]) for method in METHODS}
        fit = config["fit"]
    else:
        base_seed = int(config["confirmation_seed"])
        confirmation = config["confirmation"]
        cells = []
        for process in RATE_PROCESSES:
            for track in confirmation["tracks"]:
                for ntips in confirmation["ntips"]:
                    for calibration in confirmation["calibrations"]:
                        cells.append(
                            (
                                process,
                                track,
                                int(ntips),
                                calibration,
                                False,
                                int(confirmation["replicates"]),
                            )
                        )
            cells.append(
                (
                    process,
                    "count",
                    24,
                    "fixed_internal_ages",
                    True,
                    int(confirmation["fixed_age_controls"]),
                )
            )
        lambdas = {}
        fit = config["fit"]

    source_hash = _source_hash()
    payloads = []
    counter = 0
    for process, track, ntips, calibration, fixed, reps in cells:
        if mode == "confirmation":
            cell_lambdas = {
                method: [float(selected[process][method])] for method in METHODS
            }
        else:
            cell_lambdas = lambdas
        for replicate in range(reps):
            seed = base_seed + counter
            counter += 1
            payload = {
                "mode": mode,
                "rate_process": process,
                "track": track,
                "ntips": ntips,
                "calibration": calibration,
                "fixed_ages": fixed,
                "replicate": replicate,
                "seed": seed,
                "simulation": config["simulation"],
                "fit": fit,
                "lambdas": cell_lambdas,
                "resume": resume,
            }
            payload["fingerprint"] = _json_hash(
                {
                    "schema": CACHE_SCHEMA_VERSION,
                    "source": source_hash,
                    "payload": {k: v for k, v in payload.items() if k != "resume"},
                }
            )
            payload["cache_path"] = str(_cache_path(output_dir, payload))
            payloads.append(payload)
    return payloads


def _run(payloads, ncores):
    if ncores == 1:
        return [_worker(payload) for payload in payloads]
    paths = []
    with ProcessPoolExecutor(max_workers=min(ncores, len(payloads))) as pool:
        futures = [pool.submit(_worker, payload) for payload in payloads]
        for future in as_completed(futures):
            paths.append(future.result())
    return paths


def _metrics(record, method, lam):
    fit = record["fits"][method][str(float(lam))]
    true_ages = np.asarray(record["true_ages"], dtype=float)
    fitted_ages = np.asarray(fit["ages"], dtype=float)
    ntips = int(record["ntips"])
    scale = max(float(true_ages[-1]), 1e-12)
    errors = (fitted_ages[ntips:] - true_ages[ntips:]) / scale
    true_rates = np.asarray(record["true_rates"], dtype=float)
    fitted_rates = np.asarray(fit["rates"], dtype=float)
    rho = float(spearmanr(np.log(true_rates), np.log(fitted_rates)).statistic)
    return {
        "converged": bool(fit["converged"]),
        "age_mae": float(np.mean(np.abs(errors))),
        "age_bias": float(np.mean(errors)),
        "log_rate_spearman": rho if np.isfinite(rho) else None,
    }


def _pilot_summary(records):
    summary = {}
    selected = {}
    for process in RATE_PROCESSES:
        summary[process] = {}
        selected[process] = {}
        subset = [r for r in records if r["rate_process"] == process]
        for method in METHODS:
            candidates = {}
            lambdas = sorted(float(value) for value in subset[0]["fits"][method])
            for lam in lambdas:
                rows = [_metrics(record, method, lam) for record in subset]
                good = [row for row in rows if row["converged"]]
                candidates[str(float(lam))] = {
                    "n": len(rows),
                    "converged": len(good),
                    "median_age_mae": (
                        float(np.median([row["age_mae"] for row in good]))
                        if good
                        else None
                    ),
                }
            valid = [
                (value["median_age_mae"], -float(lam), float(lam))
                for lam, value in candidates.items()
                if value["median_age_mae"] is not None
            ]
            chosen = min(valid)[2]
            selected[process][method] = chosen
            summary[process][method] = {
                "selected_lam": chosen,
                "candidates": candidates,
            }
    return summary, selected


def _bootstrap_ratio(pairs, gates):
    values = np.asarray(pairs, dtype=float)
    rng = np.random.default_rng(int(gates["bootstrap_seed"]))
    ratios = np.empty(int(gates["bootstrap_replicates"]), dtype=float)
    for idx in range(ratios.size):
        sample = values[rng.integers(0, values.shape[0], values.shape[0])]
        ratios[idx] = np.median(sample[:, 0]) / max(np.median(sample[:, 1]), 1e-12)
    return {
        "estimate": float(np.median(values[:, 0]) / np.median(values[:, 1])),
        "upper_95": float(np.quantile(ratios, 0.95)),
    }


def _confirmation_summary(records, selected, gates):
    summaries = {}
    for process, target in (
        ("gamma", "relaxed"),
        ("lognormal", "uncorrelated_lognormal"),
    ):
        summaries[process] = {}
        subset = [
            r
            for r in records
            if r["rate_process"] == process
            and r["track"] == "count"
            and not r["fixed_ages"]
        ]
        for method in METHODS:
            rows = [_metrics(r, method, selected[process][method]) for r in subset]
            good = [row for row in rows if row["converged"]]
            summaries[process][method] = {
                "n": len(rows),
                "converged": len(good),
                "convergence_rate": len(good) / len(rows),
                "median_age_mae": float(np.median([r["age_mae"] for r in good])),
                "absolute_age_bias": abs(float(np.mean([r["age_bias"] for r in good]))),
            }
        primary = summaries[process][target]
        primary["gate_checks"] = {
            "convergence": primary["convergence_rate"] >= gates["convergence_rate"],
            "age_mae": primary["median_age_mae"]
            <= gates["normalized_internal_age_mae_median"],
            "age_bias": primary["absolute_age_bias"]
            <= gates["normalized_internal_age_absolute_bias"],
        }

    controls = [
        r
        for r in records
        if r["rate_process"] == "lognormal" and r["fixed_ages"]
    ]
    control_rows = [
        _metrics(
            r,
            "uncorrelated_lognormal",
            selected["lognormal"]["uncorrelated_lognormal"],
        )
        for r in controls
    ]
    control_rho = float(
        np.median(
            [
                r["log_rate_spearman"]
                for r in control_rows
                if r["converged"] and r["log_rate_spearman"] is not None
            ]
        )
    )
    pairs = []
    for record in records:
        if (
            record["rate_process"] == "lognormal"
            and record["track"] == "count"
            and not record["fixed_ages"]
        ):
            uln = _metrics(
                record,
                "uncorrelated_lognormal",
                selected["lognormal"]["uncorrelated_lognormal"],
            )
            relaxed = _metrics(
                record, "relaxed", selected["lognormal"]["relaxed"]
            )
            if uln["converged"] and relaxed["converged"]:
                pairs.append((uln["age_mae"], relaxed["age_mae"]))
    noninferiority = _bootstrap_ratio(pairs, gates)
    lognormal = summaries["lognormal"]["uncorrelated_lognormal"]
    lognormal["fixed_age_median_log_rate_spearman"] = control_rho
    lognormal["noninferiority"] = noninferiority
    lognormal["gate_checks"].update(
        {
            "fixed_age_rate_recovery": control_rho
            >= gates["fixed_age_log_rate_spearman_median"],
            "noninferiority": noninferiority["upper_95"]
            <= gates["noninferiority_ratio"],
        }
    )
    passed = all(
        summaries[process][method]["gate_checks"]
        and all(summaries[process][method]["gate_checks"].values())
        for process, method in (
            ("gamma", "relaxed"),
            ("lognormal", "uncorrelated_lognormal"),
        )
    )
    return summaries, bool(passed)


def _read_records(payloads):
    records = []
    for payload in payloads:
        record = json.loads(Path(payload["cache_path"]).read_text())
        if record.get("status") != "ok":
            raise RuntimeError(
                f"failed validation cache {payload['cache_path']}: "
                f"{record.get('message', 'unknown error')}"
            )
        records.append(record)
    return records


def main(argv=None):
    """Run one resumable stage of validation study v4."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=("smoke", "pilot", "confirmation"), required=True
    )
    parser.add_argument("--stage", choices=("fit", "score", "all"), default="all")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE / "v4")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--selected-lambdas", type=Path)
    args = parser.parse_args(argv)

    config = json.loads(CONFIG_PATH.read_text())
    selected = None
    selected_path = args.selected_lambdas or (
        args.output_dir / "selected-lambdas-v4-pilot.json"
    )
    if args.mode == "confirmation":
        if not selected_path.exists():
            raise SystemExit(
                "confirmation requires frozen pilot lambdas; run pilot first or "
                "pass --selected-lambdas"
            )
        selected = json.loads(selected_path.read_text())["selected_lambdas"]

    payloads = _payloads(
        config, args.mode, args.output_dir, not args.no_resume, selected
    )
    if args.stage in {"fit", "all"}:
        _run(payloads, max(1, int(args.ncores)))
    if args.stage == "fit":
        return 0

    records = _read_records(payloads)
    if args.mode in {"smoke", "pilot"}:
        summary, frozen = _pilot_summary(records)
        result = {
            "study_version": 4,
            "mode": args.mode,
            "summary": summary,
            "selected_lambdas": frozen,
            "passed": True,
        }
        if args.mode == "pilot":
            _atomic_json(selected_path, {"selected_lambdas": frozen})
    else:
        summary, passed = _confirmation_summary(
            records, selected, config["release_gates"]
        )
        result = {
            "study_version": 4,
            "mode": args.mode,
            "selected_lambdas": selected,
            "release_gates": config["release_gates"],
            "summary": summary,
            "passed": passed,
        }
    _atomic_json(args.output_dir / f"results-v4-{args.mode}.json", result)
    _atomic_json(
        args.output_dir / f"environment-v4-{args.mode}.json",
        {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "toytree": toytree.__version__,
            "config_hash": _json_hash(config),
            "source_hash": _source_hash(),
        },
    )
    _atomic_json(
        args.output_dir / f"seeds-v4-{args.mode}.json",
        {
            "seeds": [
                {
                    "rate_process": p["rate_process"],
                    "track": p["track"],
                    "ntips": p["ntips"],
                    "calibration": p["calibration"],
                    "fixed_ages": p["fixed_ages"],
                    "replicate": p["replicate"],
                    "seed": p["seed"],
                }
                for p in payloads
            ]
        },
    )
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
