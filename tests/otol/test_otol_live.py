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


def test_live_resolve_names_smoke():
    """Resolve one known name against live OTOL."""
    table = otol.match_names(["Homo sapiens"], on_unresolved="raise")
    assert int(table.iloc[0]["ott_id"]) > 0


def test_live_induced_subtree_smoke():
    """Fetch a tiny induced subtree from live OTOL."""
    nwk = otol.induced_subtree([770315, 542509], label_format="name")
    assert isinstance(nwk, str)
    assert nwk.strip().endswith(";")
