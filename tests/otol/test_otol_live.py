#!/usr/bin/env python

"""Optional live smoke tests for OTOL endpoints.

These tests are disabled by default. Enable with:
`TOYTREE_RUN_LIVE_OTOL=1`.
"""

from __future__ import annotations

import os

import pytest

import toytree.otol as otol

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
