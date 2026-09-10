"""Regression tests for the penalized-pseudolikelihood release-status ledger."""

import json
from pathlib import Path

import toytree

REPO = Path(__file__).parents[2]
STATUS_PATH = REPO / "validation" / "penalized_pseudolikelihood" / "release-status.json"


def _status():
    return json.loads(STATUS_PATH.read_text())


def test_release_status_ledger_has_complete_scoped_public_surface():
    """Every public statistical workflow has one explicit release status."""
    status = _status()
    workflows = status["workflows"]
    expected = {
        "clock": "validated",
        "discrete": "validated_compatibility",
        "relaxed": "compatibility_only",
        "uncorrelated_lognormal": "validated_fixed_lambda_positive_branches",
        "correlated": "validated_fixed_lambda",
        "correlated_lambda_cv": "experimental",
    }

    assert status["module_status"] == "release_ready_with_scoped_validation"
    for name, expected_status in expected.items():
        entry = workflows[name]
        assert entry["status"] == expected_status
        assert hasattr(toytree.mod, entry["public_api"])


def test_release_status_ledger_keeps_rejected_workflows_private():
    """Rejected or absent selectors are not accidentally exported."""
    workflows = _status()["workflows"]
    private = {
        "cross_family_model_selection": "not_public",
        "discrete_category_selection": "not_implemented",
        "discrete_gamma": "retired_private",
        "phiic": "not_implemented",
        "uncorrelated_lognormal_lambda_selection": "not_implemented",
    }
    for name, expected_status in private.items():
        assert workflows[name]["status"] == expected_status
        assert workflows[name]["public_api"] is None

    assert not hasattr(toytree.mod, "edges_make_ultrametric_cv_model_select")
    assert not hasattr(toytree.mod, "edges_make_ultrametric_discrete_ncategories_cv")
    assert not hasattr(toytree.mod, "edges_make_ultrametric_discrete_gamma")
    assert not hasattr(toytree.mod, "edges_make_ultrametric_phiic")
    assert not hasattr(
        toytree.mod,
        "edges_make_ultrametric_uncorrelated_lognormal_lambda_cv",
    )


def test_release_status_evidence_paths_are_committed():
    """Every status decision points to a repository evidence record."""
    for workflow in _status()["workflows"].values():
        for relative in workflow["evidence"]:
            assert (REPO / relative).is_file(), relative


def test_public_docs_have_scoped_statuses_without_blanket_warning():
    """The public page distinguishes workflow status without a module warning."""
    notebook = (REPO / "docs" / "src" / "make-ultrametric.ipynb").read_text()
    page = (REPO / "docs" / "pages" / "make-ultrametric.md").read_text()
    for text in (notebook, page):
        assert "Experimental statistical module" not in text
        assert "release status" in text.lower()
        assert "Compatibility only" in text
        assert "Experimental selector" in text
