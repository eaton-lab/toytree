"""Tests for cache-only validation-v5 lambda diagnostics."""

# ruff: noqa: E402 -- repository validation package is not installed.

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import (
    diagnose_lambda_selection_v5 as diagnostic,
)
from validation.penalized_pseudolikelihood import (
    run_validation_v5_identifiability as study,
)


def _folds(predicted: list[float]) -> list[dict]:
    """Return folds sharing observations but using candidate predictions."""
    observed = [1.0, 10.0]
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


def _fit(expected: list[float], converged: bool = True) -> dict:
    """Return a compact full-grid fit."""
    return {
        "converged": converged,
        "optimizer_message": "" if converged else "joint polish failed",
        "ages": [0.0, 0.0, 1.0],
        "rates": expected,
        "expected_branch_lengths": expected,
        "pseudologlik": -1.0,
        "penalized_pseudologlik": -1.0,
        "penalty": 0.0,
    }


def _record() -> dict:
    """Return a cache where Pearson and Gamma-relative scores disagree."""
    return {
        "status": "ok",
        "scenario": "unit",
        "ntips": 2,
        "calibration": "fixed_internal_ages",
        "baseline_rate": 1.0,
        "gamma_shape": 100.0,
        "sigma": 0.6,
        "replicate": 0,
        "seed": 10,
        "true_ages": [0.0, 0.0, 1.0],
        "true_rates": [1.0, 8.0],
        "true_means": [1.0, 8.0],
        "observed": [1.0, 10.0],
        "selected_lam": 1.0,
        "candidates": [
            {
                "lam": 0.1,
                "valid": True,
                "mean_score": 0.25,
                "standard_error": 0.25,
                "folds": _folds([1.0, 8.0]),
            },
            {
                "lam": 1.0,
                "valid": True,
                "mean_score": 0.25,
                "standard_error": 0.25,
                "folds": _folds([0.5, 10.0]),
            },
        ],
        "full_fits": {
            "0.1": _fit([1.0, 8.0]),
            "1.0": _fit([0.5, 10.0]),
        },
    }


def test_prediction_score_formulas():
    """All three fold scores have their intended denominators."""
    observed = np.array([2.0, 4.0])
    predicted = np.array([1.0, 2.0])
    assert np.allclose(
        diagnostic._prediction_scores(observed, predicted, "pearson"), [1.0, 2.0]
    )
    assert np.allclose(
        diagnostic._prediction_scores(observed, predicted, "relative_squared"),
        [1.0, 1.0],
    )
    expected = 2.0 * (2.0 - np.log(2.0) - 1.0)
    assert np.allclose(
        diagnostic._prediction_scores(observed, predicted, "gamma_deviance"),
        [expected, expected],
    )
    assert np.allclose(
        diagnostic._prediction_scores(predicted, predicted, "gamma_deviance"),
        0.0,
    )


def test_cache_only_rules_can_select_different_lambdas(monkeypatch):
    """Rescoring calls no fitter and reproduces the cached Pearson selection."""

    def fail(*args, **kwargs):
        raise AssertionError("a fitting function was called")

    monkeypatch.setattr(study, "_fit_worker", fail)
    monkeypatch.setattr(study, "edges_make_ultrametric_correlated", fail)
    monkeypatch.setattr(study, "edges_make_ultrametric_correlated_lambda_cv", fail)
    result = diagnostic._score_record(_record(), 100, 123)
    rules = result["rules"]
    assert rules["pearson_mean_minimum"]["selected_lam"] == 1.0
    assert rules["relative_squared_mean_minimum"]["selected_lam"] == 0.1
    assert rules["gamma_deviance_mean_minimum"]["selected_lam"] == 0.1
    equivalent = result["risk_equivalent_ranges"]["relative_regret_0.15"]
    assert equivalent["count"] == 1
    assert equivalent["log10_width"] == 0.0


def test_failure_diagnostics_count_folds_and_full_fits():
    """Optimizer failures are grouped by condition and lambda."""
    record = deepcopy(_record())
    record["candidates"][1]["valid"] = False
    record["candidates"][1]["folds"][0]["converged"] = False
    record["candidates"][1]["folds"][0]["optimizer_message"] = "fold failed"
    record["full_fits"]["1.0"] = _fit([0.5, 10.0], converged=False)
    failures = diagnostic._failure_diagnostics([record])
    assert len(failures) == 1
    summary = failures[0]
    assert summary["invalid_candidates"] == 1
    assert summary["failed_folds"] == 1
    assert summary["failed_full_fits"] == 1
    assert {value["message"] for value in summary["optimizer_messages"]} == {
        "fold failed",
        "joint polish failed",
    }


def test_v5_diagnostic_subprocess_uses_smoke_caches(tmp_path: Path):
    """The command rescoring a smoke cache writes a diagnostic artifact."""
    runner = (
        REPO
        / "validation"
        / "penalized_pseudolikelihood"
        / "run_validation_v5_identifiability.py"
    )
    fit = subprocess.run(
        [
            sys.executable,
            str(runner),
            "--mode",
            "smoke",
            "--ncores",
            "1",
            "--bootstrap-replicates",
            "20",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert fit.returncode == 0, fit.stderr
    command = subprocess.run(
        [
            sys.executable,
            str(Path(diagnostic.__file__)),
            "--mode",
            "smoke",
            "--bootstrap-replicates",
            "20",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert command.returncode == 0, command.stderr
    artifact = json.loads((tmp_path / "diagnostics-v5-smoke.json").read_text())
    assert artifact["diagnostic_only"]
    assert artifact["reuses_cached_fits"]
    assert not artifact["changes_public_selector"]
    assert set(artifact["rules"]) == set(diagnostic.RULES)
