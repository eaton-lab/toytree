#!/usr/bin/env python

"""Tests for ``MultiTree`` collection behavior and hardening."""

from __future__ import annotations

import pytest

import toytree
from toytree.style import TreeStyle


def _make_mtree(ntrees: int = 3) -> toytree.MultiTree:
    """Return a deterministic multitree for core behavior tests."""
    trees = [toytree.rtree.unittree(5, seed=idx) for idx in range(ntrees)]
    return toytree.mtree(trees)


@pytest.mark.parametrize(
    ("name", "call"),
    [
        ("ntips", lambda mtree: mtree.ntips),
        ("all_tree_tip_labels_same", lambda mtree: mtree.all_tree_tip_labels_same()),
        ("all_tree_topologies_same", lambda mtree: mtree.all_tree_topologies_same()),
        ("all_tree_tips_aligned", lambda mtree: mtree.all_tree_tips_aligned()),
        ("get_tip_labels", lambda mtree: mtree.get_tip_labels()),
        ("draw_cloud_tree", lambda mtree: mtree.draw_cloud_tree()),
    ],
)
def test_empty_multitree_methods_raise_clear_error(name, call) -> None:
    """Methods that require trees should fail clearly on empty collections."""
    mtree = toytree.MultiTree([])

    with pytest.raises(toytree.ToytreeError, match="empty MultiTree"):
        call(mtree)


def test_get_tip_labels_rejects_mismatched_tip_sets() -> None:
    """Tip-label order should only be available for matching tip sets."""
    trees = [toytree.rtree.unittree(5, seed=idx) for idx in range(2)]
    trees[1][0].name = "different_tip"
    mtree = toytree.mtree(trees)

    with pytest.raises(toytree.ToytreeError, match="same set of tip labels"):
        mtree.get_tip_labels()


def test_get_unique_topologies_returns_tuples_and_counts() -> None:
    """Unique-topology counts should be returned as tuples in frequency order."""
    tree1 = toytree.rtree.unittree(5, seed=0)
    tree2 = tree1.copy()
    tree3 = toytree.rtree.unittree(5, seed=1)
    mtree = toytree.mtree([tree1, tree2, tree3])

    result = mtree.get_unique_topologies()

    assert isinstance(result[0], tuple)
    assert result[0][1] == 2
    assert sum(count for _, count in result) == 3


def test_reset_tree_styles_resets_all_member_styles() -> None:
    """Style reset should restore the default TreeStyle on every tree."""
    mtree = _make_mtree(2)
    default = TreeStyle()
    for tree, layout in zip(mtree, ("u", "l")):
        tree.style.layout = layout
        tree.style.node_sizes = 17

    mtree.reset_tree_styles()

    assert all(tree.style.layout == default.layout for tree in mtree)
    assert all(tree.style.node_sizes == default.node_sizes for tree in mtree)


def test_draw_cloud_tree_accepts_index_sequences_in_selected_order() -> None:
    """Cloud draws should honor validated selection order."""
    trees = [toytree.rtree.unittree(5, seed=idx) for idx in range(3)]
    for tree, layout in zip(trees, ("r", "u", "l")):
        tree.style.layout = layout
    mtree = toytree.mtree(trees)

    canvas, axes, marks = mtree.draw_cloud_tree(
        idxs=[2, 0],
        fixed_order=trees[0].get_tip_labels(),
    )

    assert canvas is not None
    assert axes is not None
    assert [mark.layout for mark in marks] == ["l", "r"]


@pytest.mark.parametrize(
    ("idxs", "expected_layout"),
    [
        (1, "u"),
        (-1, "l"),
    ],
)
def test_draw_cloud_tree_accepts_int_and_negative_indices(
    idxs,
    expected_layout: str,
) -> None:
    """Cloud draws should support integer and negative index selection."""
    trees = [toytree.rtree.unittree(5, seed=idx) for idx in range(3)]
    for tree, layout in zip(trees, ("r", "u", "l")):
        tree.style.layout = layout
    mtree = toytree.mtree(trees)

    _, _, marks = mtree.draw_cloud_tree(
        idxs=idxs,
        fixed_order=trees[0].get_tip_labels(),
    )

    assert len(marks) == 1
    assert marks[0].layout == expected_layout


def test_draw_cloud_tree_rejects_empty_selection() -> None:
    """Cloud draws should reject an explicit empty selection."""
    mtree = _make_mtree(3)

    with pytest.raises(toytree.ToytreeError, match="at least one selected tree"):
        mtree.draw_cloud_tree(idxs=[])


def test_draw_cloud_tree_rejects_out_of_range_indices() -> None:
    """Cloud draws should reject invalid tree indices with a clear error."""
    mtree = _make_mtree(3)

    with pytest.raises(toytree.ToytreeError, match="out-of-range"):
        mtree.draw_cloud_tree(idxs=[10])


def test_draw_cloud_tree_rejects_non_integer_indices() -> None:
    """Cloud draws should reject non-integer selections."""
    mtree = _make_mtree(3)

    with pytest.raises(toytree.ToytreeError, match="integer values"):
        mtree.draw_cloud_tree(idxs=["bad"])
