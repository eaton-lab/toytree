# ruff: noqa: D103
"""Regression tests for the penalized-pseudolikelihood release ledger."""

import inspect
import json
import subprocess
from pathlib import Path

import pytest

import toytree

REPO = Path(__file__).parents[2]
STATUS_PATH = REPO / "validation" / "penalized_pseudolikelihood" / "release-status.json"
MAX_TRACKED_ARTIFACT_BYTES = 20 * 1024 * 1024
PUBLIC_METHODS = {
    "edges_make_ultrametric",
    "edges_make_ultrametric_clock",
    "edges_make_ultrametric_discrete",
    "edges_make_ultrametric_relaxed",
    "edges_make_ultrametric_uncorrelated_lognormal",
    "edges_make_ultrametric_correlated",
}


def _status():
    return json.loads(STATUS_PATH.read_text())


def test_release_status_ledger_has_final_public_surface():
    status = _status()
    expected = {
        "clock": "validated",
        "discrete": "validated_compatibility",
        "relaxed": "compatibility_only",
        "uncorrelated_lognormal": "validated_fixed_lambda_positive_branches",
        "correlated": "validated_fixed_lambda",
    }
    assert status["module_status"] == "release_ready_with_scoped_validation"
    assert status["schema_version"] == 3
    assert status["fit_failure_policy"] == {
        "full_result": "return_candidate_and_diagnostics",
        "inplace": "mutate_only_when_fit_usable",
        "tree_only": "raise_on_nonconvergence_or_explicit_instability",
        "unassessed_stability": "nonfatal",
    }
    assert set(status["public_api"]) == PUBLIC_METHODS
    for name, expected_status in expected.items():
        entry = status["workflows"][name]
        assert entry["status"] == expected_status
        assert hasattr(toytree.mod, entry["public_api"])


def test_public_model_signatures_have_no_private_controls():
    for name in PUBLIC_METHODS:
        parameters = inspect.signature(getattr(toytree.mod, name)).parameters
        assert not [parameter for parameter in parameters if parameter.startswith("_")]


def test_rejected_workflows_are_absent_from_public_api():
    workflows = _status()["workflows"]
    expected = {
        "automatic_lambda_selection": "unsupported_by_design",
        "cross_family_model_selection": "unsupported_by_design",
        "discrete_category_selection": "explicit_only",
        "discrete_gamma": "retired_removed",
        "phiic": "removed_unvalidated",
    }
    for name, state in expected.items():
        assert workflows[name]["status"] == state
        assert workflows[name]["public_api"] is None
    for name in (
        "edges_make_ultrametric_correlated_lambda_cv",
        "edges_make_ultrametric_uncorrelated_lognormal_lambda_cv",
        "edges_make_ultrametric_cv_model_select",
        "edges_make_ultrametric_discrete_ncategories_cv",
        "edges_make_ultrametric_discrete_gamma",
        "edges_make_ultrametric_phiic",
    ):
        assert not hasattr(toytree.mod, name)


def test_release_status_evidence_paths_are_committed():
    for workflow in _status()["workflows"].values():
        for relative in workflow["evidence"]:
            assert (REPO / relative).is_file(), relative


def test_public_docs_have_scoped_statuses_without_selector_claims():
    notebook = (REPO / "docs" / "src" / "make-ultrametric.ipynb").read_text()
    page = (REPO / "docs" / "pages" / "make-ultrametric.md").read_text()
    for text in (notebook, page):
        assert "Experimental statistical module" not in text
        assert "release status" in text.lower()
        assert "Compatibility only" in text
        assert "edges_make_ultrametric_correlated_lambda_cv" not in text
        assert "automatic lambda" in text.lower()


def test_no_tracked_validation_artifact_exceeds_20_mib():
    try:
        output = subprocess.run(
            ["git", "ls-files", "-z", "validation/penalized_pseudolikelihood"],
            cwd=REPO,
            check=True,
            capture_output=True,
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("Git index unavailable")
    oversized = []
    for raw in output.split(b"\0"):
        if not raw:
            continue
        path = REPO / raw.decode()
        if path.is_file() and path.stat().st_size > MAX_TRACKED_ARTIFACT_BYTES:
            oversized.append((str(path.relative_to(REPO)), path.stat().st_size))
    assert not oversized
