#!/usr/bin/env python

"""Create convergence-aware diagnostics from compact V17 benchmark results."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "v17"


def _finite(values: list[Any]) -> np.ndarray:
    """Return finite values as a one-dimensional array."""
    array = np.asarray(
        [np.nan if value is None else value for value in values], dtype=float
    )
    return array[np.isfinite(array)]


def _stats(values: list[Any]) -> dict[str, Any]:
    """Return robust summaries without allowing sentinels to dominate."""
    array = _finite(values)
    if not array.size:
        return {
            "n": 0,
            "median": None,
            "p90": None,
            "maximum": None,
            "maximum_absolute": None,
        }
    return {
        "n": int(array.size),
        "median": float(np.median(array)),
        "p90": float(np.quantile(array, 0.9)),
        "maximum": float(np.max(array)),
        "maximum_absolute": float(np.max(np.abs(array))),
    }


def _row_eligible(row: dict[str, Any]) -> bool:
    """Return whether an engine fit is valid for recovery summaries."""
    return bool(
        row.get(
            "accuracy_eligible",
            row.get("status") == "ok"
            and row.get("converged")
            and row.get("calibrations_valid"),
        )
    )


def _pair_eligible(row: dict[str, Any]) -> bool:
    """Return whether a paired fit is valid for parity comparisons."""
    return bool(row.get("comparison_eligible", row.get("both_converged", False)))


def _cell_label(row: dict[str, Any], engine: str | None = None) -> str:
    """Return a stable experimental-cell label."""
    parts = [
        row["scenario"],
        f"n{row['ntips']}",
        row["calibration"],
        row["observation_model"],
    ]
    if engine is not None:
        parts.insert(1, engine)
    return ":".join(parts)


def _engine_cells(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize convergence and recovery within each engine cell."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[_cell_label(row, row["engine"])].append(row)
    result = {}
    for label, group in sorted(groups.items()):
        eligible = [row for row in group if _row_eligible(row)]
        result[label] = {
            "datasets": len(group),
            "successful": sum(row.get("status") == "ok" for row in group),
            "converged": sum(bool(row.get("converged")) for row in group),
            "accuracy_eligible": len(eligible),
            "zero_containing": sum(
                row.get("zero_branch_count", 0) > 0 for row in group
            ),
            "normalized_age_mae": _stats(
                [row.get("normalized_age_mae") for row in eligible]
            ),
            "normalized_age_rmse": _stats(
                [row.get("normalized_age_rmse") for row in eligible]
            ),
        }
    return result


def _failure_patterns(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Count nonconvergence by engine, model, and observation regime."""
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if not _row_eligible(row):
            groups[(row["scenario"], row["engine"], row["observation_model"])].append(
                row
            )
    result = {}
    for (scenario, engine, observation), group in sorted(groups.items()):
        label = f"{scenario}:{engine}:{observation}"
        result[label] = {
            "datasets": len(group),
            "zero_containing": sum(
                row.get("zero_branch_count", 0) > 0 for row in group
            ),
            "dataset_ids": sorted(row["dataset_id"] for row in group),
        }
    return result


def _paired_cells(
    rows: list[dict[str, Any]], pairs: list[dict[str, Any]]
) -> dict[str, Any]:
    """Summarize only jointly valid paired engine comparisons."""
    by_fit = {(row["dataset_id"], row["engine"]): row for row in rows}
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        groups[_cell_label(pair)].append(pair)
    result = {}
    for label, group in sorted(groups.items()):
        eligible = [pair for pair in group if _pair_eligible(pair)]
        age_differences = []
        for pair in eligible:
            toy = by_fit[(pair["dataset_id"], "toytree")]
            ape = by_fit[(pair["dataset_id"], "ape")]
            left = toy.get("normalized_age_mae")
            right = ape.get("normalized_age_mae")
            if left is not None and right is not None:
                age_differences.append(float(left) - float(right))
        result[label] = {
            "datasets": len(group),
            "comparison_eligible": len(eligible),
            "toytree_minus_ape_age_mae": _stats(age_differences),
            "maximum_normalized_chronogram_difference": _stats(
                [
                    pair.get("maximum_normalized_chronogram_difference")
                    for pair in eligible
                ]
            ),
            "toytree_minus_ape_objective": _stats(
                [pair.get("toytree_minus_ape_objective") for pair in eligible]
            ),
        }
    return result


def _relaxed_diagnostic(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    """Expose objective dominance and the largest relaxed disagreements."""
    eligible = [
        pair
        for pair in pairs
        if pair["scenario"] == "relaxed_gamma_shape4" and _pair_eligible(pair)
    ]
    objective = _finite([pair.get("toytree_minus_ape_objective") for pair in eligible])
    ranked = sorted(
        eligible,
        key=lambda row: abs(
            float(row.get("maximum_normalized_chronogram_difference") or 0.0)
        ),
        reverse=True,
    )
    tolerance = 1e-8
    return {
        "comparison_eligible": len(eligible),
        "toytree_objective_better": int(np.count_nonzero(objective > tolerance)),
        "ape_objective_better": int(np.count_nonzero(objective < -tolerance)),
        "objective_tied": int(np.count_nonzero(np.abs(objective) <= tolerance)),
        "objective_difference": _stats(objective.tolist()),
        "chronogram_difference": _stats(
            [pair.get("maximum_normalized_chronogram_difference") for pair in eligible]
        ),
        "largest_chronogram_disagreements": [
            {
                "dataset_id": pair["dataset_id"],
                "ntips": pair["ntips"],
                "calibration": pair["calibration"],
                "observation_model": pair["observation_model"],
                "maximum_normalized_chronogram_difference": pair.get(
                    "maximum_normalized_chronogram_difference"
                ),
                "toytree_minus_ape_objective": pair.get("toytree_minus_ape_objective"),
            }
            for pair in ranked[:10]
        ],
    }


def diagnose(result: dict[str, Any]) -> dict[str, Any]:
    """Return a compact diagnostic report from one V17 result payload."""
    rows = result["rows"]
    pairs = result["pairs"]
    return {
        "study_version": 17,
        "mode": result["mode"],
        "source_config_hash": result["config_hash"],
        "fit_source_hashes": result["fit_source_hashes"],
        "diagnostic_only": True,
        "interpretation": {
            "primary_accuracy_population": (
                "successful, converged, calibration-valid engine fits"
            ),
            "primary_parity_population": (
                "paired successful, converged, calibration-valid fits"
            ),
            "runtime_ratio": "ToyTree elapsed time divided by ape elapsed time",
        },
        "engine_cells": _engine_cells(rows),
        "failure_patterns": _failure_patterns(rows),
        "paired_cells": _paired_cells(rows, pairs),
        "relaxed": _relaxed_diagnostic(pairs),
    }


def main() -> None:
    """Parse arguments and write the convergence-aware diagnostic."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("smoke", "pilot", "confirmation"), required=True
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = args.output_dir / f"results-v17-{args.mode}.json"
    target = args.output_dir / f"diagnostics-v17-{args.mode}.json"
    result = json.loads(source.read_text())
    target.write_text(json.dumps(diagnose(result), indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "mode": args.mode,
                "output": str(target),
                "diagnostic_only": True,
            }
        )
    )


if __name__ == "__main__":
    main()
