"""Regression tests for the V12 fixed-lambda UCLN study."""

# ruff: noqa: E402 -- repository validation package is not installed.

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import run_validation_v12_ucln as study


def _config():
    return json.loads(study.CONFIG_PATH.read_text())


def test_v12_is_fixed_lambda_and_has_independent_seed_streams():
    """The study validates fixed penalties rather than selecting lambda."""
    config = _config()
    assert config["study_version"] == 12
    assert config["development_seed"] != config["confirmation_seed"]
    assert "lambda_grid" not in json.dumps(config)
    assert config["fit"]["default_nstarts"] == 4
    assert config["fit"]["stress_nstarts"] == 8


def test_v12_replay_reconstructs_every_failed_v11_numerical_case(tmp_path):
    """Replay selection is derived from the frozen V11 result and thresholds."""
    config = _config()
    datasets = study._datasets(config, "replay", resume=True)
    selected = study._v11_failed_dataset_ids(config)
    assert len(selected) == 40
    assert {study._dataset_id(item) for item in datasets} == selected
    tasks = study._task_payloads(datasets, tmp_path)
    assert len(tasks) == 125
    assert all(item["scenario"] == "v11-failed-numerical-gate-replay" for item in tasks)


def test_v12_smoke_expands_each_dataset_into_parallel_fit_tasks(tmp_path):
    """One dataset does not monopolize one remote worker."""
    config = _config()
    datasets = study._datasets(config, "smoke", resume=True)
    tasks = study._task_payloads(datasets, tmp_path)
    assert len(datasets) == 6
    assert len(tasks) == 24
    assert len({task["cache_path"] for task in tasks}) == len(tasks)
    roles = {}
    for task in tasks:
        roles.setdefault(study._dataset_id(task), set()).add(task["role"])
        assert "cache-v12" in task["cache_path"]
    assert all(
        value == {"default", "stress", "fixed_age", "time_scaled"}
        for value in roles.values()
    )


def test_v12_fit_uses_sigma_matched_lambda(monkeypatch):
    """The generating sigma deterministically defines the fitted penalty."""
    captured = {}

    def fake_ucln(*args, **kwargs):
        captured.update(kwargs)
        return {"sentinel": True}

    monkeypatch.setattr(
        study, "edges_make_ultrametric_uncorrelated_lognormal", fake_ucln
    )
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
    result = study._fit(object(), {-1: 1.0}, payload, nstarts=4)
    assert result == {"sentinel": True}
    assert np.isclose(captured["lam"], 2.0)
    assert captured["nstarts"] == 4
    assert captured["ncores"] == 1


def test_v12_score_record_uses_four_start_ages_and_fixed_age_rates():
    """Age and rate validation score the intended independent fit roles."""
    true_ages = [0.0, 0.0, 0.5, 1.0]
    fit = {
        "converged": True,
        "ages": true_ages,
        "rates": [0.5, 2.0, 1.0],
        "objective": 10.0,
        "penalty": 1.0,
        "optimizer_retries": 0,
        "solution_stable": True,
        "best_basin_replicated": True,
        "zero_length_branch_count": 0,
        "zero_length_branch_fraction": 0.0,
        "zero_length_terminal_branch_count": 0,
        "zero_length_internal_branch_count": 0,
        "minimum_positive_to_median_ratio": 1.0,
    }
    record = {
        "dataset_id": "example",
        "scenario": "fixed-lambda-ucln-recovery",
        "ntips": 2,
        "calibration": "root",
        "observation_model": "expected_branch",
        "sigma_log": 0.5,
        "lam": 2.0,
        "replicate": 1,
        "seed": 1,
        "true_ages": true_ages,
        "true_rates": [0.5, 2.0, 1.0],
        "calibrations": [{"idx": -1, "lower": 1.0, "upper": 1.0}],
        "fits": {
            "default": dict(fit),
            "stress": dict(fit),
            "fixed_age": dict(fit),
        },
    }
    row = study._score_record(record)
    assert row["age_mae"] == 0.0
    assert row["relative_objective_gap"] == 0.0
    assert np.isclose(row["fixed_age_rate_spearman"], 1.0)


def test_v12_summary_gates_clean_synthetic_results():
    """The prespecified summary accepts an ideal complete result."""
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
            "fixed_age_converged": True,
            "stress_solution_stable": True,
            "calibration_valid": True,
            "relative_objective_gap": 0.0,
            "default_stress_maximum_age_difference": 0.0,
            "age_mae": 0.01,
            "age_bias": 0.0,
            "fixed_age_rate_spearman": 0.99,
            "fixed_age_centered_log_rate_rmse": 0.01,
            "optimizer_retries": 0,
            "default_best_basin_replicated": True,
            "stress_best_basin_replicated": True,
            "zero_length_branch_count": 0,
            "zero_length_branch_fraction": 0.0,
            "zero_length_terminal_branch_count": 0,
            "zero_length_internal_branch_count": 0,
            "minimum_positive_to_median_ratio": 1.0,
            "time_unit_scale": scale,
            "observation_model": "expected_branch",
            "sigma_log": 0.3,
        }
    ]
    summary = study._summarize(rows, _config()["decision_gates"])
    assert summary["gates_passed"]
    assert all(summary["checks"].values())


def test_v12_committed_positive_branch_scope_passes_every_gate():
    """The 360 positive-branch confirmation datasets pass the frozen gates."""
    result_path = study.DEFAULT_OUTPUT / "results-v12-confirmation.json"
    result = json.loads(result_path.read_text())
    positive = [
        row
        for row in result["datasets"]
        if row["observation_model"] in {"expected_branch", "continuous_gamma"}
    ]
    summary = study._summarize(positive, _config()["decision_gates"])

    assert result["mode"] == "confirmation"
    assert result["lambda_selection"] is False
    assert len(positive) == 360
    assert summary["gates_passed"] is True
    assert all(summary["checks"].values())


def test_v12_compatibility_audit_pins_historical_confirmation():
    """The frozen confirmation remains tied to its audited source."""
    result_path = study.DEFAULT_OUTPUT / "results-v12-confirmation.json"
    audit_path = study.DEFAULT_OUTPUT / "compatibility-v12-current.json"
    archive_path = study.HERE / "archive" / "manifest.json"
    result = json.loads(result_path.read_text())
    audit = json.loads(audit_path.read_text())
    archive = json.loads(archive_path.read_text())

    assert result["source_hash"] == audit["historical_confirmation_source_hash"]
    assert audit["equivalent_for_v12_fitted_values"] is True
    assert archive["archive_commit"] == "cb0dfc3c4fae61a75c3d8bdd367ad1c57bd2953d"
