"""Regression tests for the V10 discrete validation design."""

# ruff: noqa: E402 -- repository validation package is not installed.

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import (
    run_validation_v10_discrete as study,
)


def _config():
    return json.loads(study.CONFIG_PATH.read_text())


def test_v10_uses_independent_versioned_paths_and_defaults():
    """V10 preserves V8 and pins the stress-tested start counts."""
    config = _config()
    assert config["study_version"] == 10
    assert config["fit"]["nstarts_by_model"] == {
        "fractional_poisson": 8,
        "multiplicative_gamma": 16,
    }
    assert config["fit"]["stress_nstarts_by_model"] == {
        "fractional_poisson": 16,
        "multiplicative_gamma": 32,
    }
    assert study.OUTPUT.name == "v10"
    assert study.CACHE_SCHEMA == 2


def test_v10_smoke_expands_dataset_work_into_fit_tasks():
    """Smoke work is parallelized across all independent fitted variants."""
    config = _config()
    datasets = study._payloads("smoke", config, "fingerprint", True)
    tasks = study._fit_payloads(datasets)
    assert len(datasets) == 2
    assert len(tasks) == 8
    roles = {}
    for task in tasks:
        roles.setdefault(study._dataset_id(task), set()).add(task["role"])
        assert "cache-v10" in task["cache_path"]
    poisson = next(
        value for key, value in roles.items() if key.startswith("fractional_poisson")
    )
    gamma = next(
        value for key, value in roles.items() if key.startswith("multiplicative_gamma")
    )
    assert poisson == {"main", "fixed_age", "stress_reference"}
    assert gamma == {
        "main",
        "fixed_age",
        "stress_reference",
        "input_scaled",
        "time_scaled",
    }


def test_v10_failure_replay_preserves_every_v8_problem_seed():
    """The targeted replay contains all convergence and stability failures."""
    config = _config()
    datasets = study._payloads("failure-replay", config, "fingerprint", False)
    assert len(datasets) == 9
    assert {dataset["seed"] for dataset in datasets} == {
        341987789,
        1724942161,
        168581008,
        650024187,
        537658992,
        573146019,
        318523759,
        1403829609,
        1152057083,
    }
    assert all("stress_reference" in study._fit_roles(dataset) for dataset in datasets)


def test_v10_gamma_primary_fit_uses_matching_branch_cv(monkeypatch):
    """Primary Gamma recovery fits the CV used to simulate each dataset."""
    captured = {}

    def fake_gamma(**kwargs):
        captured.update(kwargs)
        return {"sentinel": True}

    monkeypatch.setattr(study, "edges_make_ultrametric_discrete_gamma", fake_gamma)
    monkeypatch.setattr(study, "_slim", lambda fit: fit)
    payload = {
        "model": "multiplicative_gamma",
        "true_cv": 0.2,
        "fit_seed": 3,
        "ncategories": 2,
        "config": {
            "fit": {
                "max_iter": 10,
                "max_fun": 20,
                "max_refine": 1,
            }
        },
    }
    result = study._fit(
        tree=object(),
        calibrations={-1: 1.0},
        payload=payload,
        nstarts=8,
    )
    assert result == {"sentinel": True}
    assert np.isclose(captured["branch_cv"], 0.2)
    assert captured["nstarts"] == 8
    assert captured["ncores"] == 1


def test_v10_default_cv_sensitivity_is_a_separate_fit_role():
    """CV misspecification never replaces the model-matched primary fit."""
    payload = {
        "model": "multiplicative_gamma",
        "true_cv": 0.2,
        "replicate": 1,
        "mode": "pilot",
    }
    roles = study._fit_roles(payload)
    assert "main" in roles
    assert "misspecified_default_cv" in roles


def test_v10_smoke_scoring_uses_execution_checks():
    """Smoke scoring does not require absent confirmation-only CV cells."""
    config = _config()

    def fit(model, rate_scale=1.0, time_scale=1.0):
        return {
            "converged": True,
            "ages": [0.0, 0.0, 0.5 * time_scale, 1.0 * time_scale],
            "rates": [0.5 * rate_scale, 1.5 * rate_scale],
            "weights": [0.5, 0.5],
            "objective": 1.0,
            "boundary_solution": False,
            "boundary_reasons": [],
            "effective_ncategories": 2,
            "mixture_identified": True,
            "optimum_replicated": True,
            "model": model,
        }

    records = []
    for model in ("fractional_poisson", "multiplicative_gamma"):
        main = fit(model)
        record = {
            "model": model,
            "ntips": 2,
            "true_cv": 0.1 if model == "multiplicative_gamma" else None,
            "true_ages": [0.0, 0.0, 0.5, 1.0],
            "true_rates": [0.5, 1.5],
            "true_weights": [0.5, 0.5],
            "calibrations": {"-1": 1.0},
            "main": main,
            "fixed_age": fit(model),
            "stress_reference": fit(model),
            "input_scaled": None,
            "time_scaled": None,
            "misspecified_default_cv": None,
        }
        if model == "multiplicative_gamma":
            record["input_scaled"] = fit(model, rate_scale=1e6)
            record["time_scaled"] = fit(model, rate_scale=1e-6, time_scale=1e6)
        records.append(record)

    summary = study._score(records, config, mode="smoke")
    assert summary["gates_passed"]
    assert all(summary["checks"].values())

    # Collapsed mixtures are singular-model diagnostics, not valid tests of
    # the optimizer stability of the requested identified K-category model.
    records[1]["main"]["mixture_identified"] = False
    collapsed = study._score(records, config, mode="smoke")
    stress = collapsed["details"]["optimizer_stress"]
    assert stress["identified_pairs"] == 1
    assert stress["excluded_unidentified_pairs"] == 1
    assert collapsed["checks"]["stress_objective"]
