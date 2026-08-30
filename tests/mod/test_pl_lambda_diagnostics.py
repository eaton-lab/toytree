"""Tests for cache-only correlated lambda-selection diagnostics."""

# ruff: noqa: E402 -- repository validation package is not installed.

import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import (
    diagnose_lambda_selection_v3 as diagnostic,
)
from validation.penalized_pseudolikelihood import run_validation_v3 as study


def _candidate(lam: float, observed: list[float], predicted: list[float]) -> dict:
    """Return one compact cached candidate for unit tests."""
    return {
        "lam": lam,
        "valid": True,
        "mean_score": 0.0,
        "standard_error": 0.0,
        "folds": [
            {
                "fold": idx,
                "edge_index": idx,
                "observed": obs,
                "predicted": pred,
                "predicted_rate": pred,
                "ancestral_rate": None,
                "score": 0.0,
                "converged": True,
                "optimizer_message": "",
            }
            for idx, (obs, pred) in enumerate(zip(observed, predicted))
        ],
    }


def _fit(expected: list[float], rates: list[float]) -> dict:
    """Return one compact cached full fit for unit tests."""
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
    """Return a complete synthetic cache record with two lambda candidates."""
    return {
        "status": "ok",
        "scenario": "unit",
        "track": "gamma",
        "ntips": 2,
        "calibration": "fixed_internal_ages",
        "release_gate": False,
        "baseline_rate": 1.0,
        "gamma_shape": 100.0,
        "sigma": 0.2,
        "replicate": 0,
        "seed": 10,
        "true_ages": [0.0, 0.0, 1.0],
        "true_rates": [1.0, 2.0],
        "true_means": [1.0, 2.0],
        "observed": [1.1, 1.8],
        "selected_lam": 0.1,
        "selected_at_boundary": True,
        "candidates": [
            _candidate(0.1, [1.1, 1.8], [1.0, 2.0]),
            _candidate(1.0, [1.1, 1.8], [0.7, 2.5]),
        ],
        "full_fits": {
            "0.1": _fit([1.0, 2.0], [1.0, 2.0]),
            "1.0": _fit([0.8, 2.4], [0.8, 2.4]),
        },
    }


def test_prediction_score_formulas():
    """Pearson and relative-squared fold scores use predicted denominators."""
    observed = np.array([2.0, 4.0])
    predicted = np.array([1.0, 2.0])
    assert np.allclose(
        diagnostic._prediction_scores(observed, predicted, "pearson"), [1.0, 2.0]
    )
    assert np.allclose(
        diagnostic._prediction_scores(observed, predicted, "relative_squared"),
        [1.0, 1.0],
    )


def test_population_risk_matches_generating_variance():
    """Population risk uses Gamma or Poisson generating variance."""
    true = np.array([1.0, 2.0])
    predicted = np.array([1.1, 2.2])
    gamma = diagnostic._population_risk(predicted, true, "gamma", 100.0)
    count = diagnostic._population_risk(predicted, true, "count", 100.0)
    assert np.isclose(gamma, 1.0)
    assert np.isclose(count, 0.015)


def test_minimum_ties_favor_stronger_smoothing():
    """Exact diagnostic ties reproduce the public selector's stronger lambda."""
    values = np.array([1.0, 1.0, 2.0])
    lambdas = np.array([0.1, 1.0, 10.0])
    assert diagnostic._minimum_index(values, lambdas) == 1


def test_paired_one_se_uses_paired_differences():
    """The paired one-SE comparator chooses the strongest eligible lambda."""
    scores = np.array([[1.0, 3.0], [2.0, 2.0], [10.0, 10.0]])
    valid = np.ones(3, dtype=bool)
    lambdas = np.array([0.1, 1.0, 10.0])
    rule = diagnostic.RULES["pearson_paired_one_se"]
    selected, _ = diagnostic._select_index(scores, valid, lambdas, rule)
    assert selected == 1


def test_trimmed_mean_removes_one_fold_from_each_tail():
    """Ten-percent trimming is deterministic for ten folds."""
    values = np.array([[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 100.0]])
    result = diagnostic._aggregate_scores(values, "trimmed_mean_10_percent")
    assert np.isclose(result[0], 4.5)


def test_bootstrap_selection_is_reproducible():
    """Paired fold bootstrap summaries repeat under the same seed."""
    scores = np.array([[1.0, 2.0, 1.0], [1.1, 1.9, 1.1]])
    valid = np.ones(2, dtype=bool)
    lambdas = np.array([0.1, 1.0])
    rule = diagnostic.RULES["pearson_mean_minimum"]
    first = diagnostic._bootstrap_selection(
        scores, valid, lambdas, rule, 0.1, replicates=100, seed=123
    )
    second = diagnostic._bootstrap_selection(
        scores, valid, lambdas, rule, 0.1, replicates=100, seed=123
    )
    assert first == second


def test_diagnose_records_is_cache_only(monkeypatch):
    """Record diagnosis never invokes the v3 fitting worker or public fitter."""

    def fail(*args, **kwargs):
        raise AssertionError("a fitting function was called")

    monkeypatch.setattr(study, "_fit_worker", fail)
    monkeypatch.setattr(study, "edges_make_ultrametric_correlated", fail)
    result = diagnostic._diagnose_records([_record()], 20, 123)
    assert result["diagnostic_only"]
    assert not result["changes_public_selector"]
    current = result["datasets"][0]["rules"]["pearson_mean_minimum"]
    assert current["selected_lam"] == 0.1
    assert current["absolute_excess_risk"] == 0.0


def test_cache_reader_rejects_missing_and_stale_files(tmp_path: Path):
    """Cache diagnostics fail rather than silently using missing or stale fits."""
    payload = {"cache_path": str(tmp_path / "missing.json"), "fingerprint": "right"}
    with pytest.raises(RuntimeError, match="missing cache"):
        study._read_records([payload])
    path = Path(payload["cache_path"])
    path.write_text('{"fingerprint": "wrong"}\n')
    with pytest.raises(RuntimeError, match="stale cache"):
        study._read_records([payload])
