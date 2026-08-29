#!/usr/bin/env python

"""Compare one- and four-start correlated fits before validation v3."""

# ruff: noqa: E402 -- thread limits must precede numerical imports.

from __future__ import annotations

import argparse
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

import toytree
from toytree.mod._src.penalized_pseudolikelihood.correlated import (
    edges_make_ultrametric_correlated,
)
from validation.penalized_pseudolikelihood.run_validation_v2 import (
    _calibrations,
    _simulate_dataset,
)
from validation.penalized_pseudolikelihood.run_validation_v3 import (
    CONFIG_PATH,
    _atomic_json,
    _json_hash,
    _source_hash,
)

toytree.set_log_level("WARNING")


def _nearest_grid_lambda(grid: list[float], target: float) -> float:
    """Return the grid value nearest a target on the log scale."""
    return float(min(grid, key=lambda value: abs(np.log(value) - np.log(target))))


def _cases(config: dict[str, Any], quick: bool) -> list[dict[str, Any]]:
    """Build deterministic representative optimizer cases."""
    diagnostic = config["optimizer_diagnostic"]
    sigmas = [0.3] if quick else diagnostic["sigmas"]
    tracks = ["gamma"] if quick else diagnostic["tracks"]
    grid = [float(value) for value in config["lambdas"]]
    seed = int(config["optimizer_diagnostic_seed"])
    cases = []
    index = 0
    for track in tracks:
        for sigma in sigmas:
            theoretical = 1.0 / (2.0 * float(sigma) ** 2)
            lambdas = [grid[0], _nearest_grid_lambda(grid, theoretical), grid[-1]]
            for lam in dict.fromkeys(lambdas):
                cases.append(
                    {
                        "case": index,
                        "seed": seed + index,
                        "track": track,
                        "ntips": 24 if track == "gamma" else 12,
                        "baseline_rate": 1.0 if track == "gamma" else 50.0,
                        "sigma": float(sigma),
                        "lam": float(lam),
                    }
                )
                index += 1
    return cases


def _fit_case(case: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Simulate one dataset and compare one- and four-start objectives."""
    simulation = dict(config["simulation"])
    simulation["baseline_rate"] = float(case["baseline_rate"])
    simulation["correlated_log_sigma"] = float(case["sigma"])
    true_tree, observed_tree, _, _, observed = _simulate_dataset(
        "correlated",
        int(case["ntips"]),
        case["track"],
        int(case["seed"]),
        simulation,
    )
    calibrations = _calibrations(true_tree, "root_and_internal_interval")
    common = {
        "lam": float(case["lam"]),
        "calibrations": calibrations,
        "full": True,
        "inplace": False,
        "max_iter": int(config["fit"]["max_iter"]),
        "max_fun": int(config["fit"]["max_fun"]),
        "max_refine": int(config["fit"]["max_refine"]),
        "ncores": 1,
        "seed": int(case["seed"]),
    }
    one = edges_make_ultrametric_correlated(observed_tree, nstarts=1, **common)
    four = edges_make_ultrametric_correlated(observed_tree, nstarts=4, **common)
    one_objective = float(-one["penalized_pseudologlik"])
    four_objective = float(-four["penalized_pseudologlik"])
    gap = max(0.0, one_objective - four_objective) / max(1.0, abs(four_objective))
    return {
        **case,
        "observed_zero_fraction": float(np.mean(observed == 0.0)),
        "one_start": {
            "converged": bool(one["converged"]),
            "objective": one_objective,
            "nfev": int(one["nfev"]),
            "gradient_max_abs": one["gradient_max_abs"],
            "message": str(one["optimizer_message"]),
        },
        "four_start": {
            "converged": bool(four["converged"]),
            "objective": four_objective,
            "nfev": int(four["nfev"]),
            "best_start": int(four["best_start"]),
            "gradient_max_abs": four["gradient_max_abs"],
            "message": str(four["optimizer_message"]),
        },
        "normalized_objective_gap": float(gap),
    }


def _worker(payload: tuple[dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """Process-pool adapter for one optimizer case."""
    return _fit_case(*payload)


def _summary(rows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    """Apply the prespecified one-start and fallback acceptance rules."""
    thresholds = config["optimizer_diagnostic"]
    gaps = np.asarray([row["normalized_objective_gap"] for row in rows], dtype=float)
    one_convergence = float(np.mean([row["one_start"]["converged"] for row in rows]))
    four_convergence = float(np.mean([row["four_start"]["converged"] for row in rows]))
    gap_95 = float(np.quantile(gaps, 0.95))
    gap_max = float(np.max(gaps))
    checks = {
        "one_start_convergence": (
            one_convergence >= float(thresholds["one_start_convergence"])
        ),
        "objective_gap_95th_percentile": (
            gap_95 <= float(thresholds["objective_gap_95th_percentile"])
        ),
        "objective_gap_maximum": (
            gap_max <= float(thresholds["objective_gap_maximum"])
        ),
    }
    one_start_accepted = bool(all(checks.values()))
    four_start_accepted = bool(four_convergence == 1.0)
    return {
        "cases": len(rows),
        "one_start_convergence": one_convergence,
        "four_start_convergence": four_convergence,
        "objective_gap_95th_percentile": gap_95,
        "objective_gap_maximum": gap_max,
        "checks": checks,
        "one_start_accepted": one_start_accepted,
        "four_start_accepted": four_start_accepted,
        "recommended_nstarts": 1 if one_start_accepted else 4,
        "passed": four_start_accepted,
    }


def main(argv: list[str] | None = None) -> int:
    """Run and save the v3 correlated optimizer diagnostic."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "v3" / "optimizer-diagnostics-v3.json",
    )
    args = parser.parse_args(argv)
    if args.ncores < 1:
        parser.error("--ncores must be positive")

    config = json.loads(CONFIG_PATH.read_text())
    cases = _cases(config, args.quick)
    started = time.monotonic()
    rows = []
    if args.ncores == 1:
        for completed, case in enumerate(cases, start=1):
            rows.append(_fit_case(case, config))
            print(
                json.dumps(
                    {
                        "event": "case_complete",
                        "completed": completed,
                        "total": len(cases),
                    }
                ),
                flush=True,
            )
    else:
        with ProcessPoolExecutor(max_workers=min(args.ncores, len(cases))) as pool:
            futures = [pool.submit(_worker, (case, config)) for case in cases]
            for completed, future in enumerate(as_completed(futures), start=1):
                rows.append(future.result())
                print(
                    json.dumps(
                        {
                            "event": "case_complete",
                            "completed": completed,
                            "total": len(cases),
                        }
                    ),
                    flush=True,
                )
    rows.sort(key=lambda row: row["case"])
    summary = _summary(rows, config)
    result = {
        "study_version": 3,
        "kind": "correlated_optimizer_diagnostic",
        "quick": bool(args.quick),
        "elapsed_seconds": float(time.monotonic() - started),
        "config_hash": _json_hash(config),
        "source_hash": _source_hash(),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "toytree": toytree.__version__,
        },
        "summary": summary,
        "cases": rows,
    }
    _atomic_json(args.output, result)
    print(json.dumps(summary), flush=True)
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
