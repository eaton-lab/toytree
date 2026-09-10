"""Regression tests for the V15 fixed-lambda correlated confirmation."""

# ruff: noqa: E402 -- repository validation package is not installed.

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import (
    run_validation_v15_correlated as study,
)


def _config():
    return json.loads(study.CONFIG_PATH.read_text())


def test_v15_uses_untouched_independent_confirmation_stream():
    """Confirmation seeds are distinct from development and fully enumerated."""
    config = _config()
    datasets = study._datasets(config, "confirmation", resume=True)
    assert config["study_version"] == 15
    assert config["development_seed"] != config["confirmation_seed"]
    assert len(datasets) == 540
    assert datasets[0]["seed"] == config["confirmation_seed"]
    assert {item["ntips"] for item in datasets} == {24, 48, 96}
    assert {item["replicate"] for item in datasets} == set(range(10))


def test_v15_confirmation_has_2214_globally_parallel_tasks(tmp_path):
    """Every fit role can occupy a worker without nested parallelism."""
    config = _config()
    datasets = study._datasets(config, "confirmation", resume=True)
    tasks = study._task_payloads(datasets, tmp_path)
    assert len(tasks) == 2214
    assert len({item["cache_path"] for item in tasks}) == len(tasks)
    assert all("cache-v15" in item["cache_path"] for item in tasks)
    role_counts = {
        role: sum(item["role"] == role for item in tasks)
        for role in (*study.ROLES, "time_scaled")
    }
    assert role_counts == {
        "default": 540,
        "stress": 540,
        "oracle_start": 540,
        "fixed_age": 540,
        "time_scaled": 54,
    }


def test_v15_smoke_is_small_but_exercises_every_fit_role(tmp_path):
    """Preflight covers all observation and calibration combinations."""
    config = _config()
    datasets = study._datasets(config, "smoke", resume=True)
    tasks = study._task_payloads(datasets, tmp_path)
    assert len(datasets) == 6
    assert len(tasks) == 30
    expected = set(study.ROLES) | {"time_scaled"}
    assert all(set(study._roles(item)) == expected for item in datasets)


def test_v15_gate_edits_do_not_invalidate_fit_fingerprints():
    """Scoring thresholds can be audited without repeating fitted values."""
    config = _config()
    changed = copy.deepcopy(config)
    changed["decision_gates"]["age_mae_p90"] *= 2.0
    assert study._fit_source_hash(config) == study._fit_source_hash(changed)
    assert study._scoring_hash(config) != study._scoring_hash(changed)


def test_v15_increment_recovery_is_diagnostic_not_release_gating():
    """The frozen summary reports but does not gate shrunken increments."""
    config = _config()
    result = study.HERE / "v13" / "results-v13-pilot.json"
    rows = copy.deepcopy(json.loads(result.read_text())["datasets"])
    for row in rows:
        row.update(
            {
                "all_profile_rate_converged": True,
                "maximum_projected_rate_gradient": 0.0,
                "default_best_basin_replicated": True,
                "stress_best_basin_replicated": True,
                "all_primary_outer_profiles_converged": True,
            }
        )
    summary = study._summarize(rows, config)
    assert "fixed_age_increment_recovery" not in summary["checks"]
    assert "fixed_age_increment_spearman_median" in summary["diagnostics"]
    assert "profile_rate_convergence" in summary["checks"]
    assert "default_basin_replication" in summary["checks"]


def test_v15_quantile_ignores_nonfinite_values():
    """Recovery tails are computed only from defined finite statistics."""
    assert study._quantile([1.0, 2.0, float("nan")], 0.5) == 1.5
