"""Subprocess smoke test for correlated-lambda identifiability validation."""

import subprocess
import sys
from pathlib import Path


def test_v5_lambda_identifiability_cache_and_rescore_smoke(tmp_path: Path):
    """The v5 diagnostic checkpoints fits without changing release status."""
    script = (
        Path(__file__).parents[2]
        / "validation"
        / "penalized_pseudolikelihood"
        / "run_validation_v5_identifiability.py"
    )
    command = [
        sys.executable,
        str(script),
        "--mode",
        "smoke",
        "--ncores",
        "1",
        "--bootstrap-replicates",
        "20",
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
    caches = list((tmp_path / "cache-v5" / "smoke").glob("*.json"))
    assert len(caches) == 1
    result_path = tmp_path / "results-v5-smoke.json"
    results = result_path.read_text()
    assert '"study_version": 5' in results
    assert '"diagnostic_only": true' in results
    assert '"changes_public_selector": false' in results
    assert '"rscv_in_scope": false' in results
    assert '"all_release_gates_passed": false' in results

    score = subprocess.run(
        [*command, "--stage", "score"],
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
    )
    assert score.returncode == 0, score.stderr
    assert result_path.exists()
