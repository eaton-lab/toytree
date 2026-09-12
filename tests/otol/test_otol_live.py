#!/usr/bin/env python

"""Optional live smoke tests for OTOL endpoints.

These tests are disabled by default. Enable with:
`TOYTREE_RUN_LIVE_OTOL=1`.
"""

from __future__ import annotations

import os

import pytest

import toytree
import toytree.otol as otol
from toytree.otol.src import timetree

pytestmark = pytest.mark.skipif(
    os.environ.get("TOYTREE_RUN_LIVE_OTOL") != "1",
    reason="set TOYTREE_RUN_LIVE_OTOL=1 to run live OTOL tests",
)


def test_live_fetch_json_match_names_smoke():
    """Resolve one known name against live OTOL TNRS."""
    rows = otol.fetch_json_match_names(["Homo sapiens"])
    assert isinstance(rows, list)
    assert rows


def test_live_fetch_json_induced_subtree_smoke():
    """Fetch one tiny induced subtree payload from live OTOL."""
    payload = otol.fetch_json_induced_subtree([770315, 542509], label_format="name")
    assert isinstance(payload, dict)
    assert str(payload.get("newick", "")).strip().endswith(";")


def test_live_toytree_builders_smoke():
    """Build taxonomy and synthesis trees through the ToyTree-first API."""
    resolved = otol.resolve_names(["Homo sapiens", "Pan troglodytes"])
    taxonomy = otol.fetch_tree_from_taxonomy(resolved)
    synthesis = otol.fetch_tree_from_synthesis(resolved)
    assert isinstance(taxonomy, toytree.ToyTree)
    assert isinstance(synthesis, toytree.ToyTree)
    assert taxonomy.ntips == 2
    assert synthesis.ntips == 2


def test_live_timetree_pairwise_smoke():
    """Parse the current TimeTree pairwise response shape."""
    client = timetree._TimeTreeClient(cache=False)
    payload = client.request_json(
        "pairwise",
        {"taxon_a": "Homo sapiens", "taxon_b": "Pan troglodytes"},
    )
    parsed = client._extract_age_data(payload)
    assert parsed is not None
    assert parsed["age"] > 0
