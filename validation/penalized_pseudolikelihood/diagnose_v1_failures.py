#!/usr/bin/env python

"""Recheck version-1 optimizer failures and fixed-age rate identifiability."""

from __future__ import annotations

import argparse
import importlib.util
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
V1_RUNNER = HERE / "run_validation.py"
V1_CONFIG = HERE / "config.json"
V1_RESULTS = HERE / "results-full.json"


def _load_v1():
    spec = importlib.util.spec_from_file_location("toytree_pl_validation_v1", V1_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {V1_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _discrete_worker(payload):
    module = _load_v1()
    config = json.loads(V1_CONFIG.read_text())
    family, ntips, calibration, noise_name = payload["cell"].split("|")
    noise_shape = config["primary"]["noise"][noise_name]["gamma_shape"]
    true_tree, observed_tree, _, _ = module._simulate_dataset(
        family, int(ntips), noise_shape, payload["seed"]
    )
    calibrations = module._calibrations(true_tree, calibration)
    fits = []
    for nstarts in payload["starts"]:
        fit_config = deepcopy(config["primary"]["fit"])
        fit_config["nstarts"] = int(nstarts)
        try:
            fit = module._fit_configured(
                observed_tree,
                family,
                calibrations,
                fit_config,
                payload["seed"],
            )
            fits.append(
                {
                    "nstarts": int(nstarts),
                    "converged": bool(fit["converged"]),
                    "pseudologlik": float(fit["pseudologlik"]),
                    "message": str(fit.get("optimizer_message", "")),
                    "best_start": int(fit.get("best_start", 0)),
                }
            )
        except Exception as exc:
            fits.append(
                {
                    "nstarts": int(nstarts),
                    "converged": False,
                    "message": f"{type(exc).__name__}: {exc}",
                }
            )
    return {
        "cell": payload["cell"],
        "replicate": int(payload["replicate"]),
        "seed": int(payload["seed"]),
        "fits": fits,
    }


def _uncorrelated_worker(payload):
    module = _load_v1()
    config = json.loads(V1_CONFIG.read_text())
    family, ntips, _, noise_name = payload["cell"].split("|")
    noise_shape = config["primary"]["noise"][noise_name]["gamma_shape"]
    true_tree, observed_tree, true_rates, _ = module._simulate_dataset(
        family, int(ntips), noise_shape, payload["seed"]
    )
    calibrations = {
        int(node.idx): float(node.height)
        for node in true_tree.treenode.traverse("preorder")
        if not node.is_leaf()
    }
    fit_config = deepcopy(config["primary"]["fit"])
    fit_config["lambda"] = 1.0 / (2.0 * 0.65**2)
    try:
        fit = module._fit_configured(
            observed_tree,
            family,
            calibrations,
            fit_config,
            payload["seed"],
        )
        rho = float(
            spearmanr(np.log(true_rates), np.log(np.asarray(fit["rates"]))).statistic
        )
        return {
            "cell": payload["cell"],
            "replicate": int(payload["replicate"]),
            "seed": int(payload["seed"]),
            "converged": bool(fit["converged"]),
            "log_rate_spearman": rho,
            "message": str(fit.get("optimizer_message", "")),
        }
    except Exception as exc:
        return {
            "cell": payload["cell"],
            "replicate": int(payload["replicate"]),
            "seed": int(payload["seed"]),
            "converged": False,
            "log_rate_spearman": None,
            "message": f"{type(exc).__name__}: {exc}",
        }


def _run(worker, payloads, ncores):
    if ncores == 1:
        return [worker(payload) for payload in payloads]
    rows = []
    with ProcessPoolExecutor(max_workers=min(ncores, len(payloads))) as pool:
        futures = [pool.submit(worker, payload) for payload in payloads]
        for future in as_completed(futures):
            rows.append(future.result())
    return rows


def main(argv=None):
    """Run targeted diagnostics against the completed v1 artifact."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=V1_RESULTS)
    parser.add_argument("--output", type=Path, default=HERE / "diagnostics-v1.json")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--starts", type=int, nargs="+", default=[1, 4, 8])
    parser.add_argument("--discrete-limit", type=int)
    parser.add_argument("--uncorrelated-limit", type=int, default=20)
    args = parser.parse_args(argv)
    if args.ncores < 1:
        parser.error("--ncores must be positive")
    if any(value < 1 for value in args.starts):
        parser.error("--starts values must be positive")

    results = json.loads(args.results.read_text())
    replicates = results["primary"]["replicates"]
    discrete_payloads = [
        {
            "cell": row["cell"],
            "replicate": row["replicate"],
            "seed": row["seed"],
            "starts": args.starts,
        }
        for row in replicates
        if row["cell"].startswith("discrete|") and not row["converged"]
    ]
    if args.discrete_limit is not None:
        discrete_payloads = discrete_payloads[: args.discrete_limit]
    uncorrelated_payloads = [
        {
            "cell": row["cell"],
            "replicate": row["replicate"],
            "seed": row["seed"],
        }
        for row in replicates
        if row["cell"].startswith(("uncorrelated|", "uncorrelated_lognormal|"))
        and row["cell"].endswith("|low")
        and row["converged"]
    ][: args.uncorrelated_limit]

    discrete = _run(_discrete_worker, discrete_payloads, args.ncores)
    uncorrelated = _run(_uncorrelated_worker, uncorrelated_payloads, args.ncores)
    rhos = [
        row["log_rate_spearman"]
        for row in uncorrelated
        if row["converged"] and row["log_rate_spearman"] is not None
    ]
    output = {
        "discrete_failed_seeds": len(discrete_payloads),
        "discrete": sorted(discrete, key=lambda row: (row["cell"], row["replicate"])),
        "uncorrelated_fixed_age": {
            "n": len(uncorrelated),
            "median_log_rate_spearman": float(np.median(rhos)) if rhos else None,
            "rows": sorted(
                uncorrelated, key=lambda row: (row["cell"], row["replicate"])
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "discrete_failed_seeds": len(discrete_payloads),
                "uncorrelated_fixed_age_n": len(uncorrelated),
                "uncorrelated_fixed_age_median_spearman": (
                    float(np.median(rhos)) if rhos else None
                ),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
