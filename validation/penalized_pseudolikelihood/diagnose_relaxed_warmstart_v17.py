#!/usr/bin/env python

"""Test cached ape relaxed solutions as direct ToyTree optimizer starts."""

# ruff: noqa: E402 -- thread limits must precede NumPy/SciPy imports.

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

for _name in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ[_name] = "1"

import numpy as np
from scipy.optimize import approx_fprime
from scipy.special import gammaln

import toytree
from toytree.mod._src.penalized_pseudolikelihood.relaxed import (
    DIST_FLOOR,
    RATE_FLOOR,
    _fit_relaxed_start,
    _objective_relaxed,
    _relaxed_branch_pseudologlik,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    _decode_age_params,
    _encode_age_params,
    _get_children_map_from_edges,
    _get_init_ages,
    _get_params_bounds,
    _normalize_calibrations,
    _pack_log_rates,
    _unpack_log_rates,
    _validate_branch_lengths,
    _validate_observation_mask,
)
from validation.penalized_pseudolikelihood import (
    diagnose_relaxed_v17 as basin,
)
from validation.penalized_pseudolikelihood import (
    run_validation_v17_benchmark as v17,
)

DEFAULT_OUTPUT = HERE / "v17"
WARMSTART_SCHEMA = 1


def _target_ids(result: dict[str, Any], count: int) -> list[str]:
    """Return the strongest jointly converged ape-better relaxed cases."""
    pairs = [
        row
        for row in result["pairs"]
        if row["scenario"] == "relaxed_gamma_shape4"
        and row.get("comparison_eligible", row.get("both_converged", False))
        and row.get("toytree_minus_ape_objective") is not None
        and float(row["toytree_minus_ape_objective"]) < 0.0
    ]
    pairs.sort(key=lambda row: float(row["toytree_minus_ape_objective"]))
    return [row["dataset_id"] for row in pairs[:count]]


def _problem(manifest: dict[str, Any], ape_fit: dict[str, Any]) -> dict[str, Any]:
    """Build the legacy relaxed objective in ape-solution coordinates."""
    tree = toytree.tree(manifest["observed_tree_newick"])
    calibrations = v17._resolve_calibrations(tree, manifest["calibrations"])
    calibrations = _normalize_calibrations(
        tree,
        calibrations,
        dist_floor=DIST_FLOOR,
    )
    ages_base, _ = _get_init_ages(tree, calibrations)
    rates_bounds, ages_bounds_map = _get_params_bounds(tree, calibrations)
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    children_map = _get_children_map_from_edges(edges)
    ages_idxs = np.asarray(sorted(ages_bounds_map), dtype=int)
    ages_bounds = [ages_bounds_map[idx] for idx in ages_idxs]
    ages = basin._age_array(tree, ape_fit)
    rates = basin._rate_array(tree, ape_fit)
    age_params = _encode_age_params(
        ages,
        ages_idxs,
        ages_bounds,
        children_map,
        dist_floor=DIST_FLOOR,
    )
    log_rate_bounds = [
        (np.log(max(lo, RATE_FLOOR)), np.log(max(hi, RATE_FLOOR)))
        for lo, hi in (rates_bounds[idx] for idx in range(tree.nedges))
    ]
    bounds = log_rate_bounds + [(None, None)] * age_params.size
    observed = _validate_branch_lengths(tree)
    edata = np.column_stack([observed, gammaln(observed + 1.0)])
    observation_mask = _validate_observation_mask(None, tree.nedges)
    lam = float(manifest["lambda"])
    valid_loglik = _relaxed_branch_pseudologlik(
        rates,
        ages,
        edges,
        edata,
        lam,
        None,
    )
    params = np.hstack([_pack_log_rates(rates, rate_floor=RATE_FLOOR), age_params])
    return {
        "tree": tree,
        "params": params,
        "bounds": bounds,
        "rates_init": rates,
        "age_params_init": age_params,
        "ages_init": ages_base,
        "ages_idxs": ages_idxs,
        "ages_bounds": ages_bounds,
        "children_map": children_map,
        "edges": edges,
        "edata": edata,
        "lam": lam,
        "valid_loglik": valid_loglik,
        "observation_mask": observation_mask,
    }


def _objective(problem: dict[str, Any]) -> Callable[[np.ndarray], float]:
    """Return the joint minimized objective for one prepared problem."""
    return lambda params: _objective_relaxed(
        params,
        False,
        False,
        problem["rates_init"],
        problem["age_params_init"],
        problem["ages_init"],
        problem["ages_idxs"],
        problem["ages_bounds"],
        problem["children_map"],
        problem["edges"],
        problem["edata"],
        problem["lam"],
        problem["valid_loglik"],
    )


def _projected_gradient(
    params: np.ndarray,
    function: Callable[[np.ndarray], float],
    bounds: list[tuple[float | None, float | None]],
) -> dict[str, float]:
    """Return finite-difference full and bound-projected gradient maxima."""
    gradient = approx_fprime(params, function, epsilon=1e-7)
    projected = gradient.copy()
    for idx, (lower, upper) in enumerate(bounds):
        value = params[idx]
        if lower is not None and value <= float(lower) + 1e-8 and gradient[idx] > 0:
            projected[idx] = 0.0
        if upper is not None and value >= float(upper) - 1e-8 and gradient[idx] < 0:
            projected[idx] = 0.0
    return {
        "gradient_max_abs": float(np.max(np.abs(gradient))),
        "projected_gradient_max_abs": float(np.max(np.abs(projected))),
    }


def _cache_path(output_dir: Path, mode: str, dataset_id: str) -> Path:
    """Return one ape-warm-start diagnostic cache path."""
    return (
        output_dir / "cache-v17" / mode / "relaxed-ape-warmstart" / f"{dataset_id}.json"
    )


def _payloads(
    result: dict[str, Any],
    output_dir: Path,
    mode: str,
    count: int,
) -> list[dict[str, Any]]:
    """Create fingerprinted warm-start tasks."""
    payloads = []
    solver_hash = v17._solver_hash("relaxed")
    for dataset_id in _target_ids(result, count):
        manifest_path = basin._manifest_path(output_dir, mode, dataset_id)
        ape_cache_path = basin._fit_path(output_dir, mode, dataset_id, "ape")
        missing = [
            path for path in (manifest_path, ape_cache_path) if not path.exists()
        ]
        if missing:
            paths = ", ".join(str(path) for path in missing)
            raise RuntimeError(
                "V17 fit caches are required for this diagnostic; run it in the "
                f"checkout that produced the benchmark fits. Missing: {paths}"
            )
        manifest = basin._read_json(manifest_path)
        fingerprint = basin._json_hash(
            {
                "schema": WARMSTART_SCHEMA,
                "dataset_fingerprint": manifest["fingerprint"],
                "solver_hash": solver_hash,
                "start": "cached-ape-solution",
                "max_iter": 5_000,
                "max_fun": 10_000,
                "max_refine": 10,
                "gradient_epsilon": 1e-7,
            }
        )
        payloads.append(
            {
                "dataset_id": dataset_id,
                "manifest_path": str(manifest_path),
                "ape_cache_path": str(ape_cache_path),
                "cache_path": str(_cache_path(output_dir, mode, dataset_id)),
                "fingerprint": fingerprint,
            }
        )
    return payloads


def _worker(payload: dict[str, Any]) -> dict[str, Any]:
    """Measure ape-solution stationarity and optimize from that point."""
    path = Path(payload["cache_path"])
    if path.exists():
        cached = basin._read_json(path)
        if cached.get("fingerprint") != payload["fingerprint"]:
            raise RuntimeError(f"stale relaxed warm-start cache: {path}")
        return {"cache_path": str(path), "resumed": True}
    manifest = basin._read_json(Path(payload["manifest_path"]))
    ape_fit = basin._read_json(Path(payload["ape_cache_path"]))["fit"]
    problem = _problem(manifest, ape_fit)
    function = _objective(problem)
    initial_penalized = float(-function(problem["params"]))
    gradient = _projected_gradient(
        problem["params"],
        function,
        problem["bounds"],
    )
    fit_payload = {
        "start": 0,
        "params": problem["params"],
        "bounds": problem["bounds"],
        "rates_init": problem["rates_init"],
        "age_params_init": problem["age_params_init"],
        "ages_init": problem["ages_init"],
        "ages_idxs": problem["ages_idxs"],
        "ages_bounds": problem["ages_bounds"],
        "children_map": problem["children_map"],
        "edges": problem["edges"],
        "edata": problem["edata"],
        "lam": problem["lam"],
        "valid_loglik": problem["valid_loglik"],
        "observation_mask": problem["observation_mask"],
        "max_iter": 5_000,
        "max_fun": 10_000,
        "max_refine": 10,
        "model": "relaxed",
    }
    started = time.perf_counter()
    optimized = _fit_relaxed_start(fit_payload)
    elapsed = time.perf_counter() - started
    rsize = problem["rates_init"].size
    rates = _unpack_log_rates(optimized["params"][:rsize])
    ages = _decode_age_params(
        optimized["params"][rsize:],
        problem["ages_init"],
        problem["ages_idxs"],
        problem["ages_bounds"],
        problem["children_map"],
        dist_floor=DIST_FLOOR,
    )
    final_penalized = _relaxed_branch_pseudologlik(
        rates,
        ages,
        problem["edges"],
        problem["edata"],
        problem["lam"],
        problem["valid_loglik"],
    )
    record = {
        "warmstart_schema": WARMSTART_SCHEMA,
        "dataset_id": payload["dataset_id"],
        "fingerprint": payload["fingerprint"],
        "ape_reported_penalized_pseudologlik": ape_fit["penalized_pseudologlik"],
        "initial_penalized_pseudologlik": initial_penalized,
        **gradient,
        "optimized_converged": bool(optimized["converged"]),
        "optimizer_message": optimized["message"],
        "optimized_penalized_pseudologlik": float(final_penalized),
        "optimized_improvement": float(final_penalized - initial_penalized),
        "elapsed_seconds": elapsed,
    }
    v17._atomic_json(path, record)
    return {"cache_path": str(path), "resumed": False}


def _run(payloads: list[dict[str, Any]], ncores: int) -> None:
    """Run independent warm-start tasks."""
    started = time.perf_counter()
    completed = 0
    with ProcessPoolExecutor(max_workers=ncores) as pool:
        futures = {pool.submit(_worker, payload): payload for payload in payloads}
        for future in as_completed(futures):
            future.result()
            completed += 1
            print(
                json.dumps(
                    {
                        "event": "relaxed_warmstart_complete",
                        "completed": completed,
                        "total": len(payloads),
                        "elapsed_seconds": time.perf_counter() - started,
                    }
                ),
                flush=True,
            )


def _score(
    payloads: list[dict[str, Any]], output_dir: Path, mode: str
) -> dict[str, Any]:
    """Summarize ape objective stationarity and warm-start retention."""
    records = [basin._read_json(Path(item["cache_path"])) for item in payloads]
    report = {
        "study_version": 17,
        "warmstart_schema": WARMSTART_SCHEMA,
        "mode": mode,
        "diagnostic_only": True,
        "datasets": len(records),
        "objective_reproduced": all(
            abs(
                row["initial_penalized_pseudologlik"]
                - row["ape_reported_penalized_pseudologlik"]
            )
            <= 1e-8
            for row in records
        ),
        "all_warm_starts_converged": all(row["optimized_converged"] for row in records),
        "warm_start_retained_or_improved_ape": all(
            row["optimized_penalized_pseudologlik"]
            >= row["ape_reported_penalized_pseudologlik"] - 1e-6
            for row in records
        ),
        "maximum_projected_gradient_at_ape": max(
            row["projected_gradient_max_abs"] for row in records
        ),
        "records": records,
    }
    target = output_dir / f"relaxed-warmstart-v17-{mode}.json"
    v17._atomic_json(target, report)
    return report


def main() -> None:
    """Run or score the ape-solution warm-start diagnostic."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("pilot", "confirmation"), default="pilot")
    parser.add_argument("--stage", choices=("fit", "score", "all"), default="all")
    parser.add_argument("--ncores", type=int, default=0)
    parser.add_argument("--datasets", type=int, default=4)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.datasets < 1:
        parser.error("--datasets must be positive")
    result = basin._read_json(args.output_dir / f"results-v17-{args.mode}.json")
    payloads = _payloads(
        result,
        args.output_dir,
        args.mode,
        args.datasets,
    )
    if args.stage in {"fit", "all"}:
        ncores = (os.cpu_count() or 1) if args.ncores == 0 else args.ncores
        _run(payloads, max(1, min(int(ncores), len(payloads))))
    if args.stage in {"score", "all"}:
        report = _score(payloads, args.output_dir, args.mode)
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "datasets": report["datasets"],
                    "objective_reproduced": report["objective_reproduced"],
                    "all_warm_starts_converged": report["all_warm_starts_converged"],
                    "warm_start_retained_or_improved_ape": report[
                        "warm_start_retained_or_improved_ape"
                    ],
                    "output": str(
                        args.output_dir / f"relaxed-warmstart-v17-{args.mode}.json"
                    ),
                }
            )
        )


if __name__ == "__main__":
    main()
