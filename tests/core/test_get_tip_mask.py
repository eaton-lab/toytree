#!/usr/bin/env python

"""Tests for ToyTree.get_tip_mask."""

from __future__ import annotations

import numpy as np

import toytree


def test_get_tip_mask_default_all_false() -> None:
    """Default tip mask should hide all tips."""
    tree = toytree.rtree.unittree(8, seed=123)
    mask = tree.get_tip_mask()
    assert mask.size == tree.ntips
    assert np.all(mask == np.zeros(tree.ntips, dtype=bool))


def test_get_tip_mask_show_tips_true_all_true() -> None:
    """show_tips=True should show all tips."""
    tree = toytree.rtree.unittree(8, seed=123)
    mask = tree.get_tip_mask(show_tips=True)
    assert mask.size == tree.ntips
    assert np.all(mask)


def test_get_tip_mask_query_tips_sets_true() -> None:
    """Queried tips should be set to True."""
    tree = toytree.rtree.unittree(8, seed=123)
    mask = tree.get_tip_mask("r0", "r3")
    assert bool(mask[0]) is True
    assert bool(mask[3]) is True
    assert int(mask.sum()) == 2


def test_get_tip_mask_internal_query_ignored() -> None:
    """Internal node queries should not alter the tip mask."""
    tree = toytree.rtree.unittree(8, seed=123)
    mask = tree.get_tip_mask(tree.treenode.idx)
    assert int(mask.sum()) == 0


def test_get_tip_mask_mixed_tip_and_internal_query() -> None:
    """Mixed queries should include only selected tips."""
    tree = toytree.rtree.unittree(8, seed=123)
    mask = tree.get_tip_mask("r1", tree.treenode.idx)
    assert bool(mask[1]) is True
    assert int(mask.sum()) == 1
