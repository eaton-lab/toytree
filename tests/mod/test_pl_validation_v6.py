"""Tests for the v6 correlated-model reliability study."""

# ruff: noqa: E402 -- repository validation package is not installed.

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import (
    run_validation_v6_reliability as study,
)


def test_v6_pilot_factorial_is_paired_and_deterministic(tmp_path: Path):
    """The pilot expands to 40 paired datasets without a site-count input."""
    config = json.loads(study.CONFIG_PATH.read_text())
    first = study._payloads(config, "pilot", tmp_path, True)
    second = study._payloads(config, "pilot", tmp_path, True)
    assert len(first) == 40
    assert [item["fingerprint"] for item in first] == [
        item["fingerprint"] for item in second
    ]
    assert len({item["cache_path"] for item in first}) == 40
    assert all(
        item["observation_losses"] == ["fractional_poisson", "multiplicative_gamma"]
        for item in first
    )
    assert sum(bool(item["run_scale_check"]) for item in first) == 1
    assert all("sequence_length" not in item for item in first)

    stress = study._payloads(config, "optimizer-stress", tmp_path, True)
    assert {item["seed"] for item in stress} == {
        90260861,
        90260863,
        90260865,
        90260867,
    }


def test_v6_prediction_scores_match_their_definitions():
    """Cache-only cross-scoring uses Pearson and Gamma unit deviance."""
    observed = np.array([2.0, 4.0])
    predicted = np.array([1.0, 2.0])
    assert np.allclose(
        study._prediction_scores(observed, predicted, "pearson"),
        [1.0, 2.0],
    )
    expected = 2.0 * (2.0 - np.log(2.0) - 1.0)
    assert np.allclose(
        study._prediction_scores(observed, predicted, "gamma_deviance"),
        expected,
    )


def test_v6_selected_recovery_scores_the_fit_returned_to_users():
    """Selected recovery uses the independent fit returned by lambda CV."""
    warm_fit = {
        "converged": True,
        "ages": [0.0, 0.0, 10.0],
        "rates": [2.0, 1.0],
        "penalized_pseudologlik": -10.0,
        "optimizer_retries": 0,
    }
    cold_fit = {
        "converged": True,
        "ages": [0.0, 0.0, 8.0],
        "rates": [1.0, 2.0],
        "penalized_pseudologlik": -10.0,
        "optimizer_retries": 0,
    }
    folds = [
        {
            "observed": value,
            "predicted": value,
            "converged": True,
            "optimizer_retries": 0,
        }
        for value in (1.0, 2.0)
    ]
    record = {
        "ntips": 2,
        "calibration": "root_and_internal_interval",
        "true_ages": [0.0, 0.0, 8.0],
        "true_rates": [1.0, 2.0],
        "models": {
            "fractional_poisson": {
                "selected_lam": 1.0,
                "cold_selected_fit": cold_fit,
                "full_fits": {"1.0": warm_fit},
                "candidates": [
                    {
                        "lam": 1.0,
                        "valid": True,
                        "folds": folds,
                    }
                ],
                "warm_cold_objective_delta": 0.0,
            }
        },
    }

    result = study._score_model(
        record,
        "fractional_poisson",
        bootstrap_replicates=20,
        bootstrap_seed=123,
    )

    assert result["selected_age_rmse"] == 0.0
    assert result["selected_rate_spearman"] == 1.0
    assert result["warm_cold_normalized_age_rmse"] == 0.25
    assert result["warm_cold_max_normalized_age_difference"] == 0.25


def test_v6_cache_and_rescore_smoke(tmp_path: Path):
    """Smoke mode fits once and score-only mode reuses the paired cache."""
    script = (
        REPO
        / "validation"
        / "penalized_pseudolikelihood"
        / "run_validation_v6_reliability.py"
    )
    command = [
        sys.executable,
        str(script),
        "--mode",
        "smoke",
        "--stage",
        "all",
        "--ncores",
        "1",
        "--bootstrap-replicates",
        "20",
        "--output-dir",
        str(tmp_path),
    ]
    fit = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
    assert fit.returncode == 0, fit.stderr
    caches = list((tmp_path / "cache-v6" / "smoke").glob("*.json"))
    assert len(caches) == 1

    result_path = tmp_path / "results-v6-smoke.json"
    result = json.loads(result_path.read_text())
    assert result["study_version"] == 6
    assert result["diagnostic_only"]
    assert not result["changes_public_api"]
    assert not result["sequence_length_input"]
    assert not result["all_release_gates_passed"]
    for model in result["datasets"][0]["models"].values():
        assert np.isfinite(model["warm_cold_relative_objective_delta"])
        assert np.isfinite(model["warm_cold_normalized_age_rmse"])
        assert np.isfinite(model["warm_cold_max_normalized_age_difference"])
    for loss in study.LOSS_SCORE:
        summary = result["summary"]["losses"][loss]
        assert np.isfinite(summary["maximum_warm_cold_relative_objective_delta"])
        assert np.isfinite(
            summary["maximum_warm_cold_normalized_age_difference"]
        )
        assert np.isfinite(summary["p90_warm_cold_normalized_age_rmse"])

    score = subprocess.run(
        [*command[:5], "score", *command[6:]],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert score.returncode == 0, score.stderr
    assert len(list((tmp_path / "cache-v6" / "smoke").glob("*.json"))) == 1
