#!/usr/bin/env python

"""Tests for edge midpoint geometry across layouts and edge types."""

from __future__ import annotations

import numpy as np
import pytest

import toytree
from toytree.layout.src.get_edge_midpoints import get_edge_midpoints


def _draw_mark(layout: str, edge_type: str):
    """Return a deterministic tree drawing mark."""
    tree = toytree.rtree.unittree(8, seed=123)
    _, _, mark = tree.draw(layout=layout, edge_type=edge_type, tip_labels=False)
    return mark


@pytest.mark.parametrize(
    ("layout", "edge_type"),
    [
        ("r", "c"),
        ("r", "p"),
        ("r", "b"),
        ("u", "c"),
        ("u", "p"),
        ("u", "b"),
        ("c", "c"),
        ("c", "p"),
        ("c", "b"),
        ("c270-90", "c"),
        ("c270-90", "p"),
        ("c270-90", "b"),
        ("unrooted", "c"),
    ],
)
def test_get_edge_midpoints_returns_finite_coords_for_supported_drawings(
    layout: str,
    edge_type: str,
) -> None:
    """All supported drawn edge geometries should produce finite midpoint data."""
    mark = _draw_mark(layout, edge_type)
    mids = get_edge_midpoints(mark.etable, mark.ntable, mark.layout, mark.edge_type)

    assert mids.shape == mark.ntable.shape
    assert np.all(np.isfinite(mids[: mark.nnodes - 1]))


@pytest.mark.parametrize("layout", ["r", "l", "u", "d"])
def test_linear_phylogram_midpoints_stay_on_branch_segment(layout: str) -> None:
    """Rectangular phylogram midpoints should stay on the branch-length segment."""
    mark = _draw_mark(layout, "p")
    mids = get_edge_midpoints(mark.etable, mark.ntable, mark.layout, mark.edge_type)

    for child_idx, parent_idx in mark.etable:
        child = mark.ntable[child_idx]
        parent = mark.ntable[parent_idx]
        midpoint = mids[child_idx]

        if layout in ("u", "d"):
            assert np.isclose(midpoint[0], child[0])
            assert np.isclose(midpoint[1], 0.5 * (parent[1] + child[1]))
        else:
            assert np.isclose(midpoint[0], 0.5 * (parent[0] + child[0]))
            assert np.isclose(midpoint[1], child[1])


@pytest.mark.parametrize("layout", ["r", "l", "u", "d"])
def test_linear_bezier_midpoints_follow_curve_at_half_branch_depth(
    layout: str,
) -> None:
    """Bezier midpoints should lie on the rendered curve at half branch depth."""
    mark = _draw_mark(layout, "b")
    mids = get_edge_midpoints(mark.etable, mark.ntable, mark.layout, mark.edge_type)
    t = float(np.cbrt(0.5))
    omt = 1.0 - t

    for child_idx, parent_idx in mark.etable:
        child = mark.ntable[child_idx]
        parent = mark.ntable[parent_idx]
        midpoint = mids[child_idx]

        if layout in ("u", "d"):
            control = np.array([child[0], parent[1]], dtype=float)
            assert np.isclose(midpoint[1], 0.5 * (parent[1] + child[1]))
        else:
            control = np.array([parent[0], child[1]], dtype=float)
            assert np.isclose(midpoint[0], 0.5 * (parent[0] + child[0]))

        expected = (
            (omt**3) * parent
            + 3.0 * (omt**2) * t * control
            + 3.0 * omt * (t**2) * control
            + (t**3) * child
        )
        assert np.allclose(midpoint, expected)


@pytest.mark.parametrize("layout", ["c", "c270-90"])
def test_circular_cladogram_midpoints_are_chord_midpoints(layout: str) -> None:
    """Straight circular edges should use simple Cartesian midpoints."""
    mark = _draw_mark(layout, "c")
    mids = get_edge_midpoints(mark.etable, mark.ntable, mark.layout, mark.edge_type)

    for child_idx, parent_idx in mark.etable:
        child = mark.ntable[child_idx]
        parent = mark.ntable[parent_idx]
        assert np.allclose(mids[child_idx], 0.5 * (parent + child))


@pytest.mark.parametrize("layout", ["c", "c270-90"])
@pytest.mark.parametrize("edge_type", ["p", "b"])
def test_circular_phylogram_midpoints_follow_child_spoke(
    layout: str,
    edge_type: str,
) -> None:
    """Circular phylogram and circular bezier midpoints should stay radial."""
    mark = _draw_mark(layout, edge_type)
    mids = get_edge_midpoints(mark.etable, mark.ntable, mark.layout, mark.edge_type)
    root = mark.ntable[-1]

    for child_idx, parent_idx in mark.etable:
        child = mark.ntable[child_idx]
        parent = mark.ntable[parent_idx]
        midpoint = mids[child_idx]

        child_vec = child - root
        child_radius = np.hypot(child_vec[0], child_vec[1])
        parent_radius = np.hypot(*(parent - root))
        expected = root + child_vec * (
            (0.5 * (child_radius + parent_radius)) / child_radius
        )

        assert np.allclose(midpoint, expected)


def test_unrooted_midpoints_are_straight_edge_midpoints() -> None:
    """Unrooted layout edges should use straight-line Cartesian midpoints."""
    mark = _draw_mark("unrooted", "c")
    mids = get_edge_midpoints(mark.etable, mark.ntable, mark.layout, mark.edge_type)

    for child_idx, parent_idx in mark.etable:
        child = mark.ntable[child_idx]
        parent = mark.ntable[parent_idx]
        assert np.allclose(mids[child_idx], 0.5 * (parent + child))
