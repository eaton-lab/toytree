#!/usr/bin/env python

"""Tests for multitree drawing style selection behavior."""

from __future__ import annotations

import toytree


def test_mtree_draw_accepts_tree_style_u() -> None:
    """Passing ``tree_style='u'`` should resolve layout without error."""
    trees = [
        toytree.rtree.unittree(6, seed=1),
        toytree.rtree.unittree(6, seed=2),
    ]
    mtree = toytree.mtree(trees)
    _, _, marks = mtree.draw(
        shape=(1, 2),
        tree_style="u",
        tip_labels=False,
    )
    assert len(marks) == 2
    assert all(mark.layout == "unrooted" for mark in marks)
