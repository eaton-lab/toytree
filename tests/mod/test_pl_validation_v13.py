"""Regression tests for the V13 fixed-lambda correlated study."""

# ruff: noqa: E402 -- repository validation package is not installed.

import copy
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import (
    run_validation_v13_correlated as study,
)


def _config():
    return json.loads(study.CONFIG_PATH.read_text())


def _fit_result(ages, rates, objective=10.0):
    return {
        "converged": True,
        "ages": list(ages),
        "rates": list(rates),
        "objective": float(objective),
        "penalty": 1.0,
        "optimizer_retries": 0,
        "solution_stable": True,
    }


def test_v13_is_fixed_lambda_with_independent_confirmation_seeds():
    """The study validates a matched penalty and never selects lambda."""
    config = _config()
    assert config["study_version"] == 13
    assert config["development_seed"] != config["confirmation_seed"]
    assert "lambda_grid" not in json.dumps(config)
    assert config["fit"]["default_nstarts"] == 4
    assert config["fit"]["stress_nstarts"] == 8
    assert np.isclose(study._matched_lambda(0.5), 2.0)
    assert study._role_seed_offset("time_scaled") == study._role_seed_offset(
        "default"
    )


def test_v13_smoke_expands_datasets_into_global_fit_tasks(tmp_path):
    """Each fit role can occupy an independent remote worker."""
    config = _config()
    datasets = study._datasets(config, "smoke", resume=True)
    tasks = study._task_payloads(datasets, tmp_path)
    assert len(datasets) == 6
    assert len(tasks) == 30
    assert len({task["cache_path"] for task in tasks}) == len(tasks)
    roles = {}
    for task in tasks:
        roles.setdefault(study._dataset_id(task), set()).add(task["role"])
        assert "cache-v13" in task["cache_path"]
    assert all(
        value
        == {"default", "stress", "oracle_start", "fixed_age", "time_scaled"}
        for value in roles.values()
    )


def test_v13_scoring_changes_do_not_invalidate_fit_fingerprints():
    """Decision-gate edits preserve completed compatible task caches."""
    config = _config()
    changed = copy.deepcopy(config)
    changed["decision_gates"]["age_mae_median"] *= 2.0
    assert study._fit_source_hash(config) == study._fit_source_hash(changed)
    assert study._scoring_hash(config) != study._scoring_hash(changed)


def test_v13_oracle_role_uses_truth_and_matched_lambda(monkeypatch):
    """The oracle diagnostic supplies truth without changing the estimator."""
    captured = {}

    def fake_correlated(*args, **kwargs):
        captured.update(kwargs)
        return {"sentinel": True}

    monkeypatch.setattr(study, "edges_make_ultrametric_correlated", fake_correlated)
    monkeypatch.setattr(study, "_slim", lambda fit: fit)
    payload = {
        "sigma_log": 0.5,
        "fit_seed": 7,
        "config": {
            "fit": {
                "max_iter": 10,
                "max_fun": 20,
                "max_refine": 1,
                "retry_multiplier": 4,
            }
        },
    }
    ages = np.array([0.0, 0.0, 1.0])
    rates = np.array([0.5, 2.0])
    result = study._fit(
        object(),
        {-1: 1.0},
        payload,
        "oracle_start",
        nstarts=2,
        true_ages=ages,
        true_rates=rates,
    )
    assert result == {"sentinel": True}
    assert np.isclose(captured["lam"], 2.0)
    assert captured["nstarts"] == 2
    assert captured["ncores"] == 1
    assert np.array_equal(captured["_initial_ages"], ages)
    assert np.array_equal(captured["_initial_rates"], rates)


def test_v13_rate_increments_include_centered_basal_edges():
    """Increment recovery measures the complete fitted penalty graph."""
    rates = np.exp([0.0, 2.0, 1.0, 3.0])
    parent_edges = np.array([-1, -1, 0, 1])
    observed = study._rate_increments(rates, parent_edges)
    assert np.allclose(observed, [-1.0, 1.0, 1.0, 1.0])


def test_v13_score_uses_public_fit_for_recovery_and_best_reference_for_parity():
    """Truth starts diagnose missed basins without replacing user-fit recovery."""
    true_ages = [0.0, 0.0, 0.5, 1.0]
    user_ages = [0.0, 0.0, 0.6, 1.0]
    rates = [0.5, 2.0, 1.0]
    record = {
        "dataset_id": "example",
        "scenario": "fixed-lambda-correlated-recovery",
        "ntips": 2,
        "calibration": "root",
        "observation_model": "expected_branch",
        "sigma_log": 0.5,
        "lam": 2.0,
        "replicate": 1,
        "seed": 1,
        "true_ages": true_ages,
        "true_rates": rates,
        "parent_edges": [-1, -1, 0],
        "observed_branch_lengths": [1.0, 2.0, 0.5],
        "calibrations": [{"idx": -1, "lower": 1.0, "upper": 1.0}],
        "fits": {
            "default": _fit_result(user_ages, rates, 10.0),
            "stress": _fit_result(true_ages, rates, 9.5),
            "oracle_start": _fit_result(true_ages, rates, 9.0),
            "fixed_age": _fit_result(true_ages, rates, 9.0),
        },
    }
    row = study._score_record(record)
    assert row["reference_role"] == "oracle_start"
    assert np.isclose(row["age_mae"], 0.05)
    assert np.isclose(row["relative_objective_gap"], 1.0 / 9.0)
    assert np.isclose(row["fixed_age_rate_spearman"], 1.0)


def test_v13_summary_accepts_an_ideal_complete_result():
    """All prespecified fixed-lambda gates pass for ideal data."""
    scale = {
        "converged": True,
        "calibration_valid": True,
        "maximum_normalized_age_difference": 0.0,
        "maximum_rate_relative_error": 0.0,
        "penalty_relative_error": 0.0,
    }
    rows = [
        {
            "default_converged": True,
            "stress_converged": True,
            "oracle_start_converged": True,
            "fixed_age_converged": True,
            "stress_solution_stable": True,
            "calibration_valid": True,
            "relative_objective_gap": 0.0,
            "default_reference_maximum_age_difference": 0.0,
            "age_mae": 0.01,
            "age_bias": 0.0,
            "fixed_age_rate_spearman": 0.99,
            "fixed_age_centered_log_rate_rmse": 0.01,
            "fixed_age_increment_spearman": 0.99,
            "fixed_age_increment_rmse": 0.01,
            "optimizer_retries": 0,
            "zero_length_branch_count": 0,
            "zero_length_branch_fraction": 0.0,
            "time_unit_scale": scale,
            "observation_model": "expected_branch",
            "sigma_log": 0.3,
            "calibration": "root",
        }
    ]
    summary = study._summarize(rows, _config()["decision_gates"])
    assert summary["gates_passed"]
    assert all(summary["checks"].values())
