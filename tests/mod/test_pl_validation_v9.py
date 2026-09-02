"""Tests for V9 correlated-model uncertainty replay and task parallelism."""

# ruff: noqa: E402 -- repository validation package is not installed.

import copy
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import toytree
from toytree.mod._src.penalized_pseudolikelihood.lambda_cv import (
    _assemble_correlated_cv_candidates,
    _prepare_correlated_cv_problem,
    _run_fold_payloads,
)
from validation.penalized_pseudolikelihood import (
    run_validation_v9_uncertainty as study,
)


def test_v9_replays_only_unresolved_v6_uncertainty_cases(tmp_path: Path):
    """The targeted replay excludes the case already rerun by V6 stability."""
    config = json.loads(study.CONFIG_PATH.read_text())
    specs = config["modes"]["uncertainty-replay"]
    seeds = {int(spec["seed"]) for spec in specs}
    assert len(specs) == 8
    assert seeds == {
        95260891,
        95360894,
        95560900,
        95660903,
        96460927,
        96660933,
        96960942,
        97160948,
    }
    assert 96360924 not in seeds
    assert all("sequence_length" not in spec for spec in specs)

    contexts = study._build_contexts(config, "uncertainty-replay", tmp_path)
    tasks = study._fold_tasks(contexts, True)
    assert len(contexts) == 16
    assert len(tasks) == 624
    assert study._effective_workers(80, len(tasks)) == 80


def test_v9_fit_and_scoring_fingerprints_are_separate():
    """Changing a gate changes scoring provenance but not fitted-cache identity."""
    config = json.loads(study.CONFIG_PATH.read_text())
    changed = copy.deepcopy(config)
    changed["decision_gates"]["gamma_maximum_total_age_uncertainty"] = 0.2
    spec = config["modes"]["smoke"][0]
    kwargs = {
        "spec": spec,
        "loss": "multiplicative_gamma",
        "lambdas": spec["lambdas"],
        "fit": config["fit"],
        "noise": config["noise"],
        "source_hash": "fixed-source",
    }
    assert study._dataset_fingerprint(**kwargs) == study._dataset_fingerprint(**kwargs)
    assert study._scoring_fingerprint(config, 20) != study._scoring_fingerprint(
        changed, 20
    )

    changed_fit = copy.deepcopy(config["fit"])
    changed_fit["max_iter"] += 1
    assert study._dataset_fingerprint(**kwargs) != study._dataset_fingerprint(
        **{**kwargs, "fit": changed_fit}
    )


def test_lambda_cv_external_task_paths_equal_internal_parallel_results():
    """Externally scheduled paths preserve deterministic public-CV semantics."""
    tree = toytree.tree("((a:0.2,b:0.25):0.3,(c:0.35,d:0.4):0.2);")
    problem = _prepare_correlated_cv_problem(
        tree,
        lambdas=[0.1, 1.0],
        calibrations={-1: 1.0},
        max_iter=1000,
        max_fun=2000,
        max_refine=2,
        nstarts=2,
        seed=123,
    )
    serial = _run_fold_payloads(problem["payloads"], ncores=1)
    parallel = _run_fold_payloads(problem["payloads"], ncores=2)
    serial_selection = _assemble_correlated_cv_candidates(problem, serial)
    parallel_selection = _assemble_correlated_cv_candidates(problem, parallel)

    assert serial_selection["selected_lam"] == parallel_selection["selected_lam"]
    assert [
        candidate["mean_score"] for candidate in serial_selection["candidates"]
    ] == [candidate["mean_score"] for candidate in parallel_selection["candidates"]]
    assert np.allclose(
        [fold["predicted"] for fold in serial],
        [fold["predicted"] for fold in parallel],
    )


def test_v9_smoke_task_graph_uses_tip_paths(tmp_path: Path):
    """Smoke mode creates one path per tip and loss, not one worker per dataset."""
    config = json.loads(study.CONFIG_PATH.read_text())
    contexts = study._build_contexts(config, "smoke", tmp_path)
    tasks = study._fold_tasks(contexts, True)
    assert len(contexts) == 2
    assert len(tasks) == 12
    assert all(len(task["path"]) == 3 for task in tasks)
    assert len({task["cache_path"] for task in tasks}) == 12


def test_v9_gamma_gates_use_maximum_dataset_uncertainty():
    """The replay fails when any Gamma dataset exceeds the uncertainty limit."""
    gates = {
        "gamma_all_selected_fits_stable": True,
        "gamma_all_supported_lambdas_valid": True,
        "gamma_minimum_valid_candidates": 5,
        "gamma_maximum_total_age_uncertainty": 0.1,
        "gamma_selected_age_oracle_ratio_median": 1.25,
        "gamma_selected_age_oracle_ratio_p90": 2.0,
    }

    def model(uncertainty: float) -> dict:
        return {
            "selected_fit_stable": True,
            "selected_fit_objective_competitive": True,
            "all_supported_lambdas_valid": True,
            "valid_candidates": 10,
            "selected_age_oracle_ratio": 1.0,
            "folds_stable": 10,
            "folds_total": 10,
            "bootstrap": {"maximum_total_normalized_age_uncertainty": uncertainty},
        }

    rows = [
        {
            "status": "ok",
            "models": {
                "fractional_poisson": model(0.01),
                "multiplicative_gamma": model(value),
            },
        }
        for value in (0.02, 0.11)
    ]
    summary = study._summarize_v9(rows, gates)
    assert (
        summary["losses"]["multiplicative_gamma"]["maximum_total_age_uncertainty"]
        == 0.11
    )
    assert not summary["checks"]["gamma_maximum_total_age_uncertainty"]
    assert not summary["gates_passed"]


def test_v9_smoke_resumes_task_caches_and_rescores(tmp_path: Path):
    """A complete smoke run can be rescored without touching fit caches."""
    script = (
        REPO
        / "validation"
        / "penalized_pseudolikelihood"
        / "run_validation_v9_uncertainty.py"
    )
    command = [
        sys.executable,
        str(script),
        "--mode",
        "smoke",
        "--stage",
        "all",
        "--ncores",
        "2",
        "--bootstrap-replicates",
        "20",
        "--output-dir",
        str(tmp_path),
    ]
    fitted = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
    assert fitted.returncode == 0, fitted.stderr
    caches = sorted((tmp_path / "cache-v9" / "smoke").rglob("*.json"))
    assert len(caches) == 16
    mtimes = {path: path.stat().st_mtime_ns for path in caches}

    score_command = command.copy()
    score_command[5] = "score"
    score_command[7] = "1"
    score = subprocess.run(score_command, cwd=REPO, capture_output=True, text=True)
    assert score.returncode == 0, score.stderr
    assert mtimes == {path: path.stat().st_mtime_ns for path in caches}
    result = json.loads((tmp_path / "results-v9-smoke.json").read_text())
    assert result["study_version"] == 9
    assert result["diagnostic_only"]
    assert not result["release_eligible"]
    assert not result["sequence_length_input"]
    assert result["parallelism"]["fold_path_tasks"] == 12
    assert result["datasets"][0]["status"] == "ok"
