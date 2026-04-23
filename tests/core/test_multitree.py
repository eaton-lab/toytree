#!/usr/bin/env python

"""Tests for ``MultiTree`` collection behavior and hardening."""

from __future__ import annotations

import numpy as np
import pytest

import toytree
from toytree.drawing.src.scale_axes import get_toytree_scale_cartesian


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


def test_multitree_no_longer_exposes_reset_tree_styles() -> None:
    """MultiTree should not expose the removed style-reset helper."""
    mtree = _make_mtree(2)

    with pytest.raises(AttributeError):
        _ = mtree.reset_tree_styles


def test_draw_cloud_tree_uses_explicit_layout_for_all_marks() -> None:
    """Cloud draws should use the explicit draw layout for every tree."""
    mtree = _make_mtree(3)

    _, _, marks = mtree.draw_cloud_tree(layout="u")

    assert [mark.layout for mark in marks] == ["u", "u", "u"]


def test_draw_cloud_tree_accepts_per_tree_overrides() -> None:
    """Cloud draws should allow per-tree draw kwargs in rendered order."""
    mtree = _make_mtree(2)

    _, _, marks = mtree.draw_cloud_tree(
        node_mask=False,
        node_sizes=5,
        per_tree=[
            {"node_colors": {"feature": "idx", "cmap": "BlueRed"}},
            {
                "node_sizes": 9,
                "node_colors": {
                    "feature": "idx",
                    "cmap": "BlueRed",
                    "reverse": True,
                },
            },
        ],
    )

    expected0 = toytree.data.get_color_mapped_feature(
        mtree[0],
        "idx",
        cmap="BlueRed",
    )
    expected1 = toytree.data.get_color_mapped_feature(
        mtree[1],
        "idx",
        cmap="BlueRed",
        reverse=True,
    )

    assert np.array_equal(marks[0].node_colors, expected0)
    assert np.array_equal(marks[1].node_colors, expected1)
    assert np.allclose(marks[0].node_sizes, 5)
    assert np.allclose(marks[1].node_sizes, 9)


def test_draw_cloud_tree_per_tree_aligns_to_selected_render_order() -> None:
    """Per-tree overrides should match the rendered subset order after idxs."""
    trees = [toytree.rtree.unittree(5, seed=idx) for idx in range(3)]
    mtree = toytree.mtree(trees)

    _, _, marks = mtree.draw_cloud_tree(
        idxs=[2, 0],
        fixed_order=trees[0].get_tip_labels(),
        edge_widths=2,
        per_tree=[{"edge_widths": 7}, {"edge_widths": 3}],
    )

    assert np.allclose(marks[0].edge_widths, 7)
    assert np.allclose(marks[1].edge_widths, 3)
    assert marks[0]._toytree_source_tree.get_topology_id() == trees[2].get_topology_id()
    assert marks[1]._toytree_source_tree.get_topology_id() == trees[0].get_topology_id()


def test_draw_cloud_tree_reuses_inferred_fixed_order_cache(monkeypatch) -> None:
    """Repeated cloud draws should reuse cached inferred fixed-order labels."""
    mtree = _make_mtree(3)
    call_count = 0
    real = toytree.MultiTree.get_consensus_tree

    def wrapped(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return real(*args, **kwargs)

    monkeypatch.setattr(toytree.MultiTree, "get_consensus_tree", wrapped)

    mtree.draw_cloud_tree(tip_labels=False)
    mtree.draw_cloud_tree(tip_labels=False)

    assert call_count == 1
    assert len(mtree._draw_fixed_order_cache) == 1


@pytest.mark.parametrize(
    ("layout", "expected_domain"),
    [
        ("u", (-1.0, 0.0)),
        ("d", (0.0, 1.0)),
        ("r", (-1.0, 0.0)),
        ("l", (0.0, 1.0)),
    ],
)
def test_draw_cloud_tree_scale_bar_uses_resolved_layout_direction(
    layout: str,
    expected_domain: tuple[float, float],
) -> None:
    """Cloud-tree scale bars should follow the explicit layout direction."""
    mtree = _make_mtree(3)

    _, axes, marks = mtree.draw_cloud_tree(layout=layout, scale_bar=True)
    scale_axes = get_toytree_scale_cartesian(axes, mark=marks[0], create=False)

    assert scale_axes is not None
    assert scale_axes._toytree_scale_spec.locator_domain == expected_domain


def test_draw_cloud_tree_accepts_index_sequences_in_selected_order() -> None:
    """Cloud draws should honor validated selection order."""
    trees = [toytree.rtree.unittree(5, seed=idx) for idx in range(3)]
    mtree = toytree.mtree(trees)

    canvas, axes, marks = mtree.draw_cloud_tree(
        idxs=[2, 0],
        fixed_order=trees[0].get_tip_labels(),
    )

    assert canvas is not None
    assert axes is not None
    assert [mark._toytree_source_tree.get_topology_id() for mark in marks] == [
        trees[2].get_topology_id(),
        trees[0].get_topology_id(),
    ]


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
    mtree = toytree.mtree(trees)

    _, _, marks = mtree.draw_cloud_tree(
        idxs=idxs,
        fixed_order=trees[0].get_tip_labels(),
        layout=expected_layout,
    )

    assert len(marks) == 1
    assert marks[0].layout == expected_layout
    assert marks[0]._toytree_source_tree.get_topology_id() == (
        trees[idxs].get_topology_id()
    )


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


def test_draw_cloud_tree_rejects_per_tree_length_mismatch() -> None:
    """Per-tree override count should match rendered tree count."""
    mtree = _make_mtree(3)

    with pytest.raises(toytree.ToytreeError, match="rendered trees"):
        mtree.draw_cloud_tree(per_tree=[{}, {}])


def test_draw_cloud_tree_rejects_cloud_level_per_tree_keys() -> None:
    """Per-tree overrides should not accept cloud-level layout kwargs."""
    mtree = _make_mtree(2)

    with pytest.raises(toytree.ToytreeError, match="cloud-level args"):
        mtree.draw_cloud_tree(per_tree=[{"layout": "u"}, None])
