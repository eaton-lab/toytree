"""Tests for the V9 cache-only lambda-selector diagnostic."""

# ruff: noqa: E402 -- repository validation package is not installed.

import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import (
    diagnose_lambda_selection_v9 as diagnostic,
)


def test_v9_selector_aggregations_are_defined():
    """Mean, median, and trimmed mean use paired fold rows."""
    matrix = np.array(
        [
            [0.0, 1.0, 2.0, 3.0, 100.0],
            [1.0, 1.0, 1.0, 1.0, 1.0],
        ]
    )
    assert np.allclose(diagnostic._aggregate(matrix, "mean"), [21.2, 1.0])
    assert np.allclose(diagnostic._aggregate(matrix, "median"), [2.0, 1.0])
    assert np.allclose(
        diagnostic._aggregate(matrix, "trimmed_mean_10_percent"), [21.2, 1.0]
    )

    wider = np.tile(matrix, (1, 2))
    trimmed = diagnostic._aggregate(wider, "trimmed_mean_10_percent")
    expected = np.mean(np.sort(wider, axis=1)[:, 1:-1], axis=1)
    assert np.allclose(trimmed, expected)


def test_v9_paired_one_se_favors_stronger_eligible_smoothing():
    """The paired one-SE rule selects the strongest eligible lambda."""
    matrix = np.array(
        [
            [1.0, 1.0, 1.0, 1.0],
            [2.0, 0.5, 2.0, 0.5],
            [4.0, 4.0, 4.0, 4.0],
        ]
    )
    valid = np.ones(3, dtype=bool)
    lambdas = np.array([0.1, 1.0, 10.0])
    minimum, _ = diagnostic._select_index(
        matrix,
        valid,
        lambdas,
        {"aggregation": "mean", "selection": "minimum"},
    )
    one_se, _ = diagnostic._select_index(
        matrix,
        valid,
        lambdas,
        {"aggregation": "mean", "selection": "paired_one_se_stronger"},
    )
    assert lambdas[minimum] == 0.1
    assert lambdas[one_se] == 1.0


def test_v9_summary_does_not_make_release_claims():
    """Targeted checks are rule-specific diagnostics, not release gates."""
    model = {
        "selected_age_rmse": 0.1,
        "selected_age_oracle_ratio": 1.0,
        "selected_at_boundary": False,
        "bootstrap": {
            "maximum_total_normalized_age_uncertainty": 0.05,
            "log10_lam_80_percent_width": 1.0,
        },
    }
    rows = [
        {
            "status": "ok",
            "models": {
                loss: {"rules": {name: dict(model) for name in diagnostic.RULES}}
                for loss in ("fractional_poisson", "multiplicative_gamma")
            },
        }
    ]
    gates = {
        "gamma_maximum_total_age_uncertainty": 0.1,
        "gamma_selected_age_oracle_ratio_median": 1.25,
        "gamma_selected_age_oracle_ratio_p90": 2.0,
    }
    summary = diagnostic._summarize(rows, gates)
    assert all(
        check["targeted_criteria_passed"]
        for check in summary["targeted_gamma_checks"].values()
    )
    assert "release_eligible" not in summary
