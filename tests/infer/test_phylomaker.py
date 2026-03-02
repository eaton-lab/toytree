#!/usr/bin/env python

"""Tests for phylomaker subtree inference helpers."""

from __future__ import annotations

import pandas as pd
import pytest

import toytree
from toytree.infer.src.phylomaker import PhylomakerResult
from toytree.utils import ToytreeError


def test_phylomaker_sources_has_expected_default_source():
    """Return source table with the OpenTree backend metadata."""
    sources = toytree.infer.phylomaker_sources()
    assert isinstance(sources, pd.DataFrame)
    assert "opentree_synth" in set(sources["name"])
    row = sources[sources["name"] == "opentree_synth"].iloc[0]
    assert bool(row["supports_induced"]) is True
    assert bool(row["supports_full_prune"]) is False


def test_phylomaker_subtree_strict_fails_on_ambiguous(monkeypatch, tmp_path):
    """Raise ToytreeError in strict mode when any query is ambiguous."""

    def _mock_resolve(
        query,
        approximate=False,
        context=None,
        include_synonyms=True,
        on_unresolved="ignore",  # noqa: ARG001
        **kwargs,  # noqa: ARG001
    ):
        return pd.DataFrame(
            [
                {
                    "query": "A",
                    "status": "ambiguous",
                    "matched_name": None,
                    "ott_id": None,
                    "is_synonym": None,
                    "reason": "2_matches",
                }
            ]
        )

    monkeypatch.setattr(
        "toytree.infer.src.phylomaker.otol.match_names",
        _mock_resolve,
    )

    with pytest.raises(ToytreeError, match="strict phylomaker matching failed"):
        toytree.infer.phylomaker_subtree(
            taxa=["A"],
            strict="error",
            cache=True,
            cache_dir=tmp_path,
        )


def test_phylomaker_subtree_returns_tree_report_and_uses_cache(monkeypatch, tmp_path):
    """Build subtree and re-run from cache without new provider calls."""
    calls = {"match": 0, "subtree": 0}

    def _mock_resolve(
        query,
        approximate=False,
        context=None,
        include_synonyms=True,
        on_unresolved="ignore",  # noqa: ARG001
        **kwargs,  # noqa: ARG001
    ):
        calls["match"] += 1
        return pd.DataFrame(
            [
                {
                    "query": str(name),
                    "status": "matched",
                    "matched_name": str(name),
                    "ott_id": idx + 1,
                    "is_synonym": False,
                    "reason": "ok",
                }
                for idx, name in enumerate(query)
            ]
        )

    def _mock_subtree(
        query,
        full_json=False,
        label_format="name_and_id",
        insert_broken_nodes=False,  # noqa: ARG001
    ):
        calls["subtree"] += 1
        assert query == [1, 2, 3]
        return "(A_ott1:1,B_ott2:1,C_ott3:1);"

    monkeypatch.setattr(
        "toytree.infer.src.phylomaker.otol.match_names",
        _mock_resolve,
    )
    monkeypatch.setattr(
        "toytree.infer.src.phylomaker.otol.induced_subtree",
        _mock_subtree,
    )

    out1 = toytree.infer.phylomaker_subtree(
        taxa=["A", "B", "C"],
        strict="error",
        cache=True,
        cache_dir=tmp_path,
        return_report=True,
    )
    assert isinstance(out1, PhylomakerResult)
    assert isinstance(out1.tree, toytree.ToyTree)
    assert out1.tree.ntips == 3
    assert isinstance(out1.report, pd.DataFrame)
    assert out1.summary["match_cache_hit"] is False
    assert out1.summary["subtree_cache_hit"] is False
    assert calls["match"] == 1
    assert calls["subtree"] == 1

    out2 = toytree.infer.phylomaker_subtree(
        taxa=["A", "B", "C"],
        strict="error",
        cache=True,
        cache_dir=tmp_path,
        return_report=True,
    )
    assert isinstance(out2.tree, toytree.ToyTree)
    assert out2.summary["match_cache_hit"] is True
    assert out2.summary["subtree_cache_hit"] is True
    assert calls["match"] == 1
    assert calls["subtree"] == 1
