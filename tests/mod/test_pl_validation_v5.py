"""Unit tests for the correlated-lambda identifiability study."""

# ruff: noqa: E402 -- repository validation package is not installed.

import json
import sys
from pathlib import Path

import numpy as np

import toytree

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import (
    run_validation_v5_identifiability as study,
)


def _folds(observed: list[float], predicted: list[float]) -> list[dict]:
    """Return compact converged fold records."""
    return [
        {
            "fold": idx,
            "edge_index": idx,
            "observed": obs,
            "predicted": pred,
            "score": (obs - pred) ** 2 / pred,
            "converged": True,
            "optimizer_message": "",
        }
        for idx, (obs, pred) in enumerate(zip(observed, predicted))
    ]


def _fit(expected: list[float], rates: list[float]) -> dict:
    """Return one compact converged full-grid fit."""
    return {
        "converged": True,
        "optimizer_message": "",
        "ages": [0.0, 0.0, 1.0],
        "rates": rates,
        "expected_branch_lengths": expected,
        "pseudologlik": -1.0,
        "penalized_pseudologlik": -1.0,
        "penalty": 0.0,
    }


def _record() -> dict:
    """Return a synthetic cache record whose oracle is the lower boundary."""
    return {
        "status": "ok",
        "scenario": "unit",
        "ntips": 2,
        "calibration": "fixed_internal_ages",
        "baseline_rate": 1.0,
        "gamma_shape": 100.0,
        "sigma": 0.2,
        "replicate": 0,
        "seed": 10,
        "true_ages": [0.0, 0.0, 1.0],
        "true_rates": [1.0, 2.0],
        "true_means": [1.0, 2.0],
        "observed": [1.1, 1.8],
        "selected_lam": 1e-8,
        "candidates": [
            {
                "lam": 1e-8,
                "valid": True,
                "mean_score": 0.0,
                "standard_error": 0.0,
                "folds": _folds([1.1, 1.8], [1.0, 2.0]),
            },
            {
                "lam": 1.0,
                "valid": True,
                "mean_score": 0.0,
                "standard_error": 0.0,
                "folds": _folds([1.1, 1.8], [0.7, 2.5]),
            },
        ],
        "full_fits": {
            "1e-08": _fit([1.0, 2.0], [1.0, 2.0]),
            "1.0": _fit([0.8, 2.4], [0.8, 2.4]),
        },
    }


def test_pilot_factorial_is_complete_and_deterministic(tmp_path: Path):
    """The pinned pilot expands to 40 uniquely cached datasets."""
    config = json.loads(study.CONFIG_PATH.read_text())
    first, first_seeds = study._payloads(config, "pilot", tmp_path, True)
    second, second_seeds = study._payloads(config, "pilot", tmp_path, True)
    assert len(first) == 40
    assert first_seeds == second_seeds
    assert [value["fingerprint"] for value in first] == [
        value["fingerprint"] for value in second
    ]
    assert len({value["cache_path"] for value in first}) == 40
    assert {value["gamma_shape"] for value in first} == {100.0, 400.0}
    assert {value["baseline_rate"] for value in first} == {1.0}
    assert min(first[0]["lambdas"]) == 1e-8
    assert max(first[0]["lambdas"]) == 1e4


def test_calibration_density_controls_contain_true_ages():
    """Sparse and dense intervals are feasible around simulated true ages."""
    tree = toytree.rtree.bdtree(ntips=24, b=1.0, d=0.2, seed=123)
    tree = tree.mod.edges_scale_to_root_height(1.0)
    sparse = study._calibrations(tree, "root_and_internal_interval")
    dense = study._calibrations(tree, "root_and_three_internal_intervals")
    assert len(sparse) == 2
    assert len(dense) == 4
    assert sparse[-1] == dense[-1] == 1.0
    for calibrations in (sparse, dense):
        for node_index, bounds in calibrations.items():
            if node_index == -1:
                continue
            assert bounds[0] <= tree[node_index].height <= bounds[1]


def test_gamma_population_risk_uses_relative_precision():
    """Increasing Gamma shape increases the cost of the same relative error."""
    truth = np.array([1.0, 2.0])
    predicted = np.array([1.1, 2.2])
    assert np.isclose(study._population_risk(predicted, truth, 100.0), 1.0)
    assert np.isclose(study._population_risk(predicted, truth, 400.0), 4.0)


def test_lower_boundary_oracle_is_recorded_without_automatic_failure():
    """Agreement at the expanded lower boundary is a legitimate outcome."""
    first = study._score_record(_record(), 100, 123)
    second = study._score_record(_record(), 100, 123)
    assert first["bootstrap"] == second["bootstrap"]
    assert first["selected_boundary"] == "lower"
    assert first["oracle_boundary"] == "lower"
    assert not first["boundary_disagreement"]
    assert first["population_regret"] == 0.0

    gates = {
        "dataset_convergence": 0.98,
        "fold_convergence": 0.98,
        "population_regret_median": 0.15,
        "population_regret_90th_percentile": 0.50,
        "age_rmse_ratio_median": 1.25,
        "rate_spearman_delta_median": -0.10,
    }
    summary = study._summarize_cell([first], gates)
    assert summary["passed"]
    assert "boundary_selection_fraction" not in summary["checks"]
