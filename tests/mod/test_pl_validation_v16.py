"""Regression tests for the V16 correlated final-rate-polish study."""

# ruff: noqa: E402 -- repository validation package is not installed.

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import (
    run_validation_v16_correlated as study,
)


def _config():
    return json.loads(study.CONFIG_PATH.read_text())


def test_v16_replays_frozen_high_gradient_targets_and_controls():
    """Replay targets are the 14 V15 cases above 5e-7 plus six controls."""
    config = _config()
    datasets = study._datasets(config, "replay", resume=True)
    v15 = json.loads(study.V15_RESULTS_PATH.read_text())["datasets"]
    expected = {
        row["dataset_id"]
        for row in v15
        if row["maximum_projected_rate_gradient"] > 5e-7
    }

    assert config["study_version"] == 16
    assert len(config["replay_targets"]) == 14
    assert set(config["replay_targets"]) == expected
    assert len(config["replay_controls"]) == 6
    assert not set(config["replay_targets"]) & set(config["replay_controls"])
    assert len(datasets) == 20
    assert sum(item["cohort"] == "target" for item in datasets) == 14
    assert sum(item["cohort"] == "control" for item in datasets) == 6


def test_v16_replay_has_80_globally_parallel_tasks(tmp_path):
    """Each targeted dataset reruns four primary roles independently."""
    datasets = study._datasets(_config(), "replay", resume=True)
    tasks = study._task_payloads(datasets, tmp_path)
    assert len(tasks) == 80
    assert len({item["cache_path"] for item in tasks}) == 80
    assert {item["role"] for item in tasks} == set(study.ROLES)
    assert all("cache-v16" in item["cache_path"] for item in tasks)


def test_v16_confirmation_is_fresh_and_preserves_v15_design(tmp_path):
    """Confirmation uses a new seed with the frozen 540-dataset design."""
    config = _config()
    v15_config = json.loads(study.V15_CONFIG_PATH.read_text())
    datasets = study._datasets(config, "confirmation", resume=True)
    tasks = study._task_payloads(datasets, tmp_path)

    assert config["confirmation_seed"] != v15_config["confirmation_seed"]
    assert config["modes"]["confirmation"] == v15_config["modes"]["confirmation"]
    assert config["decision_gates"] == v15_config["decision_gates"]
    assert len(datasets) == 540
    assert len(tasks) == 2214
    assert datasets[0]["seed"] == config["confirmation_seed"]


def test_v16_gate_edits_do_not_invalidate_fit_fingerprints():
    """Scoring thresholds remain separate from expensive fitted values."""
    config = _config()
    changed = copy.deepcopy(config)
    changed["decision_gates"]["maximum_projected_rate_gradient"] *= 2.0
    changed["replay_gates"]["maximum_projected_rate_gradient"] *= 2.0
    assert study._fit_source_hash(config) == study._fit_source_hash(changed)
    assert study._scoring_hash(config) != study._scoring_hash(changed)


def test_v16_replay_summary_requires_all_target_gradients_to_pass():
    """A single unresolved target remains a diagnostic replay failure."""
    config = _config()
    baseline = {
        row["dataset_id"]: row
        for row in json.loads(study.V15_RESULTS_PATH.read_text())["datasets"]
    }
    rows = []
    for cohort, identifiers in (
        ("target", config["replay_targets"]),
        ("control", config["replay_controls"]),
    ):
        for identifier in identifiers:
            row = copy.deepcopy(baseline[identifier])
            row.update(
                {
                    "cohort": cohort,
                    "default_converged": True,
                    "stress_converged": True,
                    "oracle_start_converged": True,
                    "fixed_age_converged": True,
                    "all_profile_rate_converged": True,
                    "maximum_projected_rate_gradient": 1e-8,
                    "final_rate_polish_roles": [],
                    "final_rate_polish_stationarity_steps": {},
                    "all_used_final_rate_polishes_accepted": True,
                }
            )
            rows.append(row)

    assert study._replay_summary(rows, config)["gates_passed"]
    rows[0]["maximum_projected_rate_gradient"] = 2e-6
    summary = study._replay_summary(rows, config)
    assert not summary["gates_passed"]
    assert not summary["checks"]["all_target_numerical_failures_resolved"]
    assert not summary["checks"]["profile_rate_gradient"]


def test_v16_committed_confirmation_passes_frozen_release_gates():
    """The committed result validates the exact fixed-lambda implementation."""
    path = study.DEFAULT_OUTPUT / "results-v16-confirmation.json"
    audit_path = study.DEFAULT_OUTPUT / "compatibility-v16-current.json"
    result = json.loads(path.read_text())
    audit = json.loads(audit_path.read_text())

    assert result["fit_source_hash"] == audit["historical_confirmation_fit_source_hash"]
    assert study._fit_source_hash(_config()) == audit["current_fit_source_hash"]
    assert audit["equivalent_for_v16_fitted_values"] is True
    assert result["mode"] == "confirmation"
    assert result["lambda_selection"] is False
    assert result["release_eligible"] is True
    assert result["summary"]["gates_passed"] is True
    assert result["all_release_gates_passed"] is True
    assert all(result["summary"]["checks"].values())
