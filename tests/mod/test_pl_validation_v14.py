"""Regression tests for the V14 profiled correlated-optimizer replay."""

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
    run_validation_v14_correlated as study,
)


def _config():
    return json.loads(study.CONFIG_PATH.read_text())


def _row(**updates):
    row = {
        "default_converged": True,
        "stress_converged": True,
        "oracle_start_converged": True,
        "fixed_age_converged": True,
        "stress_solution_stable": True,
        "calibration_valid": True,
        "relative_objective_gap": 0.0,
        "default_reference_maximum_age_difference": 0.0,
        "time_unit_scale": {
            "converged": True,
            "calibration_valid": True,
            "maximum_normalized_age_difference": 0.0,
            "maximum_rate_relative_error": 0.0,
            "penalty_relative_error": 0.0,
        },
        "all_profile_rate_converged": True,
        "maximum_projected_rate_gradient": 0.0,
    }
    row.update(updates)
    return row


def test_v14_replays_frozen_v13_targets_and_matched_controls():
    """The full replay reconstructs exactly 14 failures and six controls."""
    config = _config()
    datasets = study._datasets(config, "replay", resume=True)
    assert config["study_version"] == 14
    assert len(config["targets"]) == 14
    assert len(config["controls"]) == 6
    assert len(datasets) == 20
    assert sum(item["cohort"] == "target" for item in datasets) == 14
    assert sum(item["cohort"] == "control" for item in datasets) == 6
    assert {study.v13._dataset_id(item) for item in datasets} == set(
        config["targets"] + config["controls"]
    )


def test_v14_expands_every_dataset_into_five_global_tasks(tmp_path):
    """All fit roles are independent tasks, including time-unit replays."""
    config = _config()
    datasets = study._datasets(config, "smoke", resume=True)
    tasks = study._task_payloads(datasets, tmp_path)
    assert len(datasets) == 4
    assert len(tasks) == 20
    assert len({item["cache_path"] for item in tasks}) == 20
    roles = {}
    for item in tasks:
        roles.setdefault(study.v13._dataset_id(item), set()).add(item["role"])
        assert "cache-v14" in item["cache_path"]
    assert all(value == set(study.ROLES) for value in roles.values())


def test_v14_scoring_changes_do_not_invalidate_fit_fingerprints():
    """Gate edits preserve expensive compatible role caches."""
    config = _config()
    changed = copy.deepcopy(config)
    changed["decision_gates"]["maximum_relative_objective_gap"] *= 2.0
    assert study._fit_source_hash(config) == study._fit_source_hash(changed)
    assert study._scoring_hash(config) != study._scoring_hash(changed)


def test_v14_numerical_failures_are_explicit_and_profile_aware():
    """The replay distinguishes objective, unit, and profile failures."""
    gates = _config()["decision_gates"]
    assert study._failure_reasons(_row(), gates) == []
    failed = _row(
        default_converged=False,
        relative_objective_gap=1e-3,
        all_profile_rate_converged=False,
        maximum_projected_rate_gradient=1e-2,
    )
    reasons = study._failure_reasons(failed, gates)
    assert set(reasons) == {
        "default_converged",
        "objective_parity",
        "profile_rate_convergence",
        "profile_rate_gradient",
    }


def test_v14_missing_time_unit_fit_is_a_failure():
    """Every replayed dataset must complete its matched time-unit role."""
    gates = _config()["decision_gates"]
    assert "time_unit_invariance" in study._failure_reasons(
        _row(time_unit_scale=None), gates
    )


def test_v14_slim_result_preserves_new_optimizer_diagnostics():
    """Cached fits retain diagnostics that distinguish profile convergence."""
    fit = {
        "converged": True,
        "tree": type(
            "Tree",
            (),
            {
                "get_node_data": lambda self, name: type(
                    "Series",
                    (),
                    {"to_numpy": lambda self, dtype: np.array([0.0, 1.0])},
                )()
            },
        )(),
        "rates": [1.0],
        "pseudologlik": -1.0,
        "penalized_pseudologlik": -2.0,
        "penalty": 1.0,
        "nstarts": 4,
        "optimizer_strategy": "profiled_rates_joint_polish",
        "profile_rate_converged": True,
        "rate_gradient_max_abs": 1e-10,
        "rate_gradient_before_final_polish": 2e-6,
        "final_rate_polish_used": True,
        "final_rate_polish_accepted": True,
        "final_rate_polish_message": "converged",
        "final_rate_polish_stationarity_steps": 1,
        "outer_profile_converged": True,
        "zero_length_branch_count": 3,
        "evaluated_starts": 5,
        "basin_confirmation_run": True,
        "best_basin_replicated": True,
    }
    slim = study._slim(fit)
    assert slim["optimizer_strategy"] == "profiled_rates_joint_polish"
    assert slim["profile_rate_converged"]
    assert slim["rate_gradient_max_abs"] == 1e-10
    assert slim["rate_gradient_before_final_polish"] == 2e-6
    assert slim["final_rate_polish_used"]
    assert slim["final_rate_polish_accepted"]
    assert slim["final_rate_polish_message"] == "converged"
    assert slim["final_rate_polish_stationarity_steps"] == 1
    assert slim["zero_length_branch_count"] == 3
    assert slim["evaluated_starts"] == 5
