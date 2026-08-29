# ruff: noqa: D103

import runpy
import subprocess
import sys
from pathlib import Path


def test_pinned_validation_pipeline_smoke(tmp_path: Path):
    script = (
        Path(__file__).parents[2]
        / "validation"
        / "penalized_pseudolikelihood"
        / "run_validation.py"
    )
    fit = subprocess.run(
        [
            sys.executable,
            str(script),
            "--mode",
            "smoke",
            "--ncores",
            "1",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
    )
    assert fit.returncode == 0, fit.stderr
    results = (tmp_path / "results-smoke.json").read_text()
    assert '"release_eligible": false' in results
    assert (tmp_path / "seeds-smoke.json").exists()
    assert (tmp_path / "environment-smoke.json").exists()


def test_v2_validation_cache_and_rescore_smoke(tmp_path: Path):
    script = (
        Path(__file__).parents[2]
        / "validation"
        / "penalized_pseudolikelihood"
        / "run_validation_v2.py"
    )
    command = [
        sys.executable,
        str(script),
        "--mode",
        "smoke",
        "--ncores",
        "1",
        "--output-dir",
        str(tmp_path),
    ]
    fit = subprocess.run(
        command,
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
    )
    assert fit.returncode == 0, fit.stderr
    caches = list((tmp_path / "cache-v2" / "smoke").rglob("*.json"))
    assert caches
    result_path = tmp_path / "results-v2-smoke.json"
    assert result_path.exists()

    score = subprocess.run(
        [*command, "--stage", "score"],
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
    )
    assert score.returncode == 0, score.stderr
    results = result_path.read_text()
    assert '"study_version": 2' in results
    assert '"all_release_gates_passed": false' in results


def test_v3_correlated_lambda_validation_cache_and_rescore_smoke(tmp_path: Path):
    """The correlated-only study checkpoints fits and supports score-only reuse."""
    script = (
        Path(__file__).parents[2]
        / "validation"
        / "penalized_pseudolikelihood"
        / "run_validation_v3.py"
    )
    command = [
        sys.executable,
        str(script),
        "--mode",
        "smoke",
        "--ncores",
        "1",
        "--output-dir",
        str(tmp_path),
    ]
    fit = subprocess.run(
        command,
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
    )
    assert fit.returncode == 0, fit.stderr
    caches = list((tmp_path / "cache-v3" / "smoke").glob("*.json"))
    assert len(caches) == 1
    result_path = tmp_path / "results-v3-smoke.json"
    results = result_path.read_text()
    assert '"study_version": 3' in results
    assert '"scope": "correlated_lambda_selection_only"' in results
    assert '"release_eligible": false' in results

    score = subprocess.run(
        [*command, "--stage", "score"],
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
    )
    assert score.returncode == 0, score.stderr
    assert result_path.exists()


def test_v4_independent_rate_validation_cache_and_rescore_smoke(tmp_path: Path):
    """The independent-rate study checkpoints paired fits and rescoring."""
    script = (
        Path(__file__).parents[2]
        / "validation"
        / "penalized_pseudolikelihood"
        / "run_validation_v4.py"
    )
    command = [
        sys.executable,
        str(script),
        "--mode",
        "smoke",
        "--ncores",
        "1",
        "--output-dir",
        str(tmp_path),
    ]
    fit = subprocess.run(
        command,
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
    )
    assert fit.returncode == 0, fit.stderr
    caches = list((tmp_path / "cache-v4" / "smoke").glob("*.json"))
    assert len(caches) == 2
    result_path = tmp_path / "results-v4-smoke.json"
    results = result_path.read_text()
    assert '"study_version": 4' in results
    assert '"uncorrelated_lognormal"' in results
    assert '"relaxed"' in results

    score = subprocess.run(
        [*command, "--stage", "score"],
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
    )
    assert score.returncode == 0, score.stderr
    assert result_path.exists()


def test_v2_primary_gates_are_method_specific():
    script = (
        Path(__file__).parents[2]
        / "validation"
        / "penalized_pseudolikelihood"
        / "run_validation_v2.py"
    )
    aggregate = runpy.run_path(str(script))["_aggregate_primary"]
    common = {
        "track": "count",
        "ntips": 4,
        "calibration": "root",
        "fixed_ages": False,
        "replicate": 0,
        "seed": 1,
        "log_rate_spearman": None,
        "message": "",
    }
    rows = [
        {
            **common,
            "family": "clock",
            "converged": True,
            "age_mae": 0.01,
            "age_bias": 0.0,
        },
        {
            **common,
            "family": "discrete",
            "converged": False,
            "age_mae": None,
            "age_bias": None,
        },
    ]
    gates = {
        "convergence_wilson_lower": 0.1,
        "normalized_internal_age_mae_median": 0.08,
        "normalized_internal_age_absolute_bias": 0.03,
        "log_rate_spearman_median": 0.75,
    }
    summary, passed = aggregate(rows, gates)
    assert summary["methods"]["clock"]["passed"]
    assert not summary["methods"]["discrete"]["passed"]
    assert not passed
