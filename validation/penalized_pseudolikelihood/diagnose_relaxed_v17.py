#!/usr/bin/env python

"""Diagnose ape-compatible relaxed-model optimization basins in V17."""

# ruff: noqa: E402 -- thread limits must precede NumPy/SciPy imports.

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

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
from scipy.special import gammaln

import toytree
from toytree.mod._src.penalized_pseudolikelihood.relaxed import (
    edges_make_ultrametric_relaxed,
)
from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    _independent_branch_pseudologlik,
    _relaxed_penalty,
)
from validation.penalized_pseudolikelihood import (
    run_validation_v17_benchmark as v17,
)

DEFAULT_OUTPUT = HERE / "v17"
DIAGNOSTIC_SCHEMA = 1


def _json_hash(value: Any) -> str:
    """Return a stable SHA256 hash for JSON-compatible values."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    """Read one JSON object."""
    return json.loads(path.read_text())


def _fit_path(output_dir: Path, mode: str, dataset_id: str, engine: str) -> Path:
    """Return the original V17 fit-cache path."""
    return output_dir / "cache-v17" / mode / f"{dataset_id}-{engine}.json"


def _manifest_path(output_dir: Path, mode: str, dataset_id: str) -> Path:
    """Return the shared V17 dataset-manifest path."""
    return output_dir / "cache-v17" / mode / "datasets" / f"{dataset_id}.json"


def _trial_path(
    output_dir: Path,
    mode: str,
    dataset_id: str,
    nstarts: int,
    trial: int,
) -> Path:
    """Return one independently resumable targeted-fit path."""
    return (
        output_dir
        / "cache-v17"
        / mode
        / "relaxed-basin"
        / f"{dataset_id}-nstarts{nstarts}-trial{trial:02d}.json"
    )


def _select_dataset_ids(
    result: dict[str, Any],
    ape_better: int,
    toytree_better: int,
) -> list[str]:
    """Select objective-separated failures plus opposite-direction controls."""
    rows = [
        pair
        for pair in result["pairs"]
        if pair["scenario"] == "relaxed_gamma_shape4"
        and pair.get("comparison_eligible", pair.get("both_converged", False))
        and pair.get("toytree_minus_ape_objective") is not None
    ]
    ordered = sorted(
        rows,
        key=lambda row: float(row["toytree_minus_ape_objective"]),
    )
    selected = ordered[:ape_better]
    selected.extend(reversed(ordered[-toytree_better:]))
    return list(dict.fromkeys(row["dataset_id"] for row in selected))


def _age_array(tree: Any, fit: dict[str, Any]) -> np.ndarray:
    """Map a fitted Newick chronogram onto the observed tree's node order."""
    fitted = toytree.tree(fit["tree_newick"])
    age_by_clade = v17._age_map(fitted)
    ages = np.zeros(tree.nnodes, dtype=float)
    for node in tree.treenode.traverse("preorder"):
        if not node.is_leaf():
            ages[node.idx] = age_by_clade[v17._clade(node)]
    return ages


def _rate_array(tree: Any, fit: dict[str, Any]) -> np.ndarray:
    """Map fitted branch rates onto the observed tree's edge order."""
    by_clade = dict(zip(fit["rate_clades"], fit["rates"]))
    return np.asarray(
        [by_clade[v17._clade(tree[int(child)])] for child, _ in tree.get_edges("idx")],
        dtype=float,
    )


def _evaluate_fit(manifest: dict[str, Any], fit: dict[str, Any]) -> dict[str, Any]:
    """Re-evaluate one cached fit under ToyTree's ape-compatible objective."""
    tree = toytree.tree(manifest["observed_tree_newick"])
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    observed = np.asarray(
        [tree[int(child)].dist for child, _ in edges],
        dtype=float,
    )
    edata = np.column_stack([observed, gammaln(observed + 1.0)])
    ages = _age_array(tree, fit)
    rates = _rate_array(tree, fit)
    lam = float(manifest["lambda"])
    raw = _independent_branch_pseudologlik(
        rates,
        ages,
        edges,
        edata,
        0.0,
        None,
        model="relaxed",
    )
    penalized = _independent_branch_pseudologlik(
        rates,
        ages,
        edges,
        edata,
        lam,
        None,
        model="relaxed",
    )
    reported = fit.get("penalized_pseudologlik")
    return {
        "status": fit.get("status"),
        "converged": bool(fit.get("converged", False)),
        "pseudologlik": float(raw),
        "penalty": _relaxed_penalty(rates),
        "penalized_pseudologlik": float(penalized),
        "reported_penalized_pseudologlik": reported,
        "reported_objective_error": (
            None if reported is None else float(penalized - float(reported))
        ),
    }


def _trial_payloads(
    result: dict[str, Any],
    output_dir: Path,
    mode: str,
    nstarts: int,
    trials: int,
    ape_better: int,
    toytree_better: int,
) -> list[dict[str, Any]]:
    """Create independent targeted multistart tasks."""
    payloads = []
    solver_hash = v17._solver_hash("relaxed")
    for dataset_id in _select_dataset_ids(result, ape_better, toytree_better):
        manifest_path = _manifest_path(output_dir, mode, dataset_id)
        manifest = _read_json(manifest_path)
        for trial in range(trials):
            seed = int(manifest["seed"]) + 1_000_003 * (trial + 1)
            settings = {
                "nstarts": nstarts,
                "seed": seed,
                "max_iter": 5_000,
                "max_fun": 10_000,
                "max_refine": 10,
            }
            fingerprint = _json_hash(
                {
                    "schema": DIAGNOSTIC_SCHEMA,
                    "dataset_fingerprint": manifest["fingerprint"],
                    "solver_hash": solver_hash,
                    "settings": settings,
                }
            )
            payloads.append(
                {
                    "dataset_id": dataset_id,
                    "manifest_path": str(manifest_path),
                    "cache_path": str(
                        _trial_path(output_dir, mode, dataset_id, nstarts, trial)
                    ),
                    "fingerprint": fingerprint,
                    "settings": settings,
                }
            )
    return payloads


def _fit_trial(payload: dict[str, Any]) -> dict[str, Any]:
    """Run one targeted multistart fit."""
    path = Path(payload["cache_path"])
    if path.exists():
        cached = _read_json(path)
        if cached.get("fingerprint") != payload["fingerprint"]:
            raise RuntimeError(f"stale relaxed diagnostic cache: {path}")
        return {"cache_path": str(path), "resumed": True}
    manifest = _read_json(Path(payload["manifest_path"]))
    tree = toytree.tree(manifest["observed_tree_newick"])
    calibrations = v17._resolve_calibrations(tree, manifest["calibrations"])
    settings = payload["settings"]
    started = time.perf_counter()
    fit = edges_make_ultrametric_relaxed(
        tree,
        lam=float(manifest["lambda"]),
        calibrations=calibrations,
        full=True,
        inplace=False,
        max_iter=int(settings["max_iter"]),
        max_fun=int(settings["max_fun"]),
        max_refine=int(settings["max_refine"]),
        nstarts=int(settings["nstarts"]),
        ncores=1,
        seed=int(settings["seed"]),
    )
    elapsed = time.perf_counter() - started
    slim = v17._slim_toytree_fit(fit, elapsed)
    slim["starts"] = fit["starts"]
    record = {
        "diagnostic_schema": DIAGNOSTIC_SCHEMA,
        "dataset_id": payload["dataset_id"],
        "fingerprint": payload["fingerprint"],
        "settings": settings,
        "fit": slim,
    }
    v17._atomic_json(path, record)
    return {"cache_path": str(path), "resumed": False}


def _run_trials(payloads: list[dict[str, Any]], ncores: int) -> None:
    """Run targeted fit tasks in a global process pool."""
    completed = 0
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=ncores) as pool:
        futures = {pool.submit(_fit_trial, payload): payload for payload in payloads}
        for future in as_completed(futures):
            future.result()
            completed += 1
            print(
                json.dumps(
                    {
                        "event": "relaxed_trial_complete",
                        "completed": completed,
                        "total": len(payloads),
                        "elapsed_seconds": time.perf_counter() - started,
                    }
                ),
                flush=True,
            )


def _score(
    result: dict[str, Any],
    payloads: list[dict[str, Any]],
    output_dir: Path,
    mode: str,
) -> dict[str, Any]:
    """Score objective reproduction and multistart basin recovery."""
    by_dataset: dict[str, list[dict[str, Any]]] = {}
    for payload in payloads:
        by_dataset.setdefault(payload["dataset_id"], []).append(payload)
    records = []
    maximum_reported_error = 0.0
    for dataset_id, group in sorted(by_dataset.items()):
        manifest = _read_json(_manifest_path(output_dir, mode, dataset_id))
        current = {}
        for engine in ("toytree", "ape"):
            cached = _read_json(_fit_path(output_dir, mode, dataset_id, engine))
            current[engine] = _evaluate_fit(manifest, cached["fit"])
            error = current[engine]["reported_objective_error"]
            if error is not None:
                maximum_reported_error = max(maximum_reported_error, abs(error))
        trials = []
        for payload in group:
            cached = _read_json(Path(payload["cache_path"]))
            evaluated = _evaluate_fit(manifest, cached["fit"])
            trials.append(
                {
                    "settings": cached["settings"],
                    "elapsed_seconds": cached["fit"]["elapsed_seconds"],
                    "starts": cached["fit"]["starts"],
                    **evaluated,
                }
            )
        converged_trials = [item for item in trials if item["converged"]]
        candidates = converged_trials or trials
        best_trial = max(
            candidates,
            key=lambda item: float(item["penalized_pseudologlik"]),
        )
        ape_objective = float(current["ape"]["penalized_pseudologlik"])
        default_objective = float(current["toytree"]["penalized_pseudologlik"])
        records.append(
            {
                "dataset_id": dataset_id,
                "ntips": manifest["ntips"],
                "calibration": manifest["calibration"],
                "observation_model": manifest["observation_model"],
                "zero_branch_count": manifest["zero_branch_count"],
                "current": current,
                "trials": trials,
                "converged_trials": len(converged_trials),
                "best_trial_penalized_pseudologlik": best_trial[
                    "penalized_pseudologlik"
                ],
                "best_trial_improvement_over_default": float(
                    best_trial["penalized_pseudologlik"] - default_objective
                ),
                "best_trial_minus_ape": float(
                    best_trial["penalized_pseudologlik"] - ape_objective
                ),
                "random_multistart_reached_ape": bool(
                    converged_trials
                    and best_trial["penalized_pseudologlik"] >= ape_objective - 1e-6
                ),
            }
        )
    reached = sum(row["random_multistart_reached_ape"] for row in records)
    report = {
        "study_version": 17,
        "diagnostic_schema": DIAGNOSTIC_SCHEMA,
        "mode": mode,
        "diagnostic_only": True,
        "datasets": len(records),
        "fit_tasks": len(payloads),
        "maximum_cached_reported_objective_error": maximum_reported_error,
        "random_multistart_reached_ape": reached,
        "random_multistart_failed_to_reach_ape": len(records) - reached,
        "interpretation": {
            "reported_objective_parity": (
                "If cached objective error is non-negligible, diagnose objective "
                "translation before optimizer basins."
            ),
            "multistart_reaches_ape": (
                "The objective is reachable and default relaxed initialization "
                "or start count is inadequate."
            ),
            "multistart_does_not_reach_ape": (
                "Next test an ape-solution warm start and gradients before "
                "changing the model."
            ),
        },
        "records": records,
    }
    target = output_dir / f"relaxed-diagnostics-v17-{mode}.json"
    v17._atomic_json(target, report)
    return report


def main() -> None:
    """Run objective evaluation and targeted relaxed multistarts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("pilot", "confirmation"), default="pilot")
    parser.add_argument("--stage", choices=("fit", "score", "all"), default="all")
    parser.add_argument("--ncores", type=int, default=0)
    parser.add_argument("--nstarts", type=int, default=8)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--ape-better", type=int, default=4)
    parser.add_argument("--toytree-better", type=int, default=2)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.nstarts < 1 or args.trials < 1:
        parser.error("--nstarts and --trials must be positive")
    if args.ape_better < 1 or args.toytree_better < 1:
        parser.error("--ape-better and --toytree-better must be positive")
    result = _read_json(args.output_dir / f"results-v17-{args.mode}.json")
    payloads = _trial_payloads(
        result,
        args.output_dir,
        args.mode,
        args.nstarts,
        args.trials,
        args.ape_better,
        args.toytree_better,
    )
    if args.stage in {"fit", "all"}:
        ncores = (os.cpu_count() or 1) if args.ncores == 0 else args.ncores
        _run_trials(payloads, max(1, min(int(ncores), len(payloads))))
    if args.stage in {"score", "all"}:
        report = _score(result, payloads, args.output_dir, args.mode)
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "datasets": report["datasets"],
                    "fit_tasks": report["fit_tasks"],
                    "random_multistart_reached_ape": report[
                        "random_multistart_reached_ape"
                    ],
                    "output": str(
                        args.output_dir / f"relaxed-diagnostics-v17-{args.mode}.json"
                    ),
                }
            )
        )


if __name__ == "__main__":
    main()
