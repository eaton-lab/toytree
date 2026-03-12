#!/usr/bin/env python

"""Tests for circular-layout parsing and coordinate projection."""

import numpy as np
import pytest

import toytree
from toytree.layout.src.layout_circular import CircularLayout, _parse_circular_layout
from toytree.utils import ToytreeError


@pytest.mark.parametrize(
    ("layout", "expected"),
    [
        ("c", (0, 360, 360, True)),
        ("c360", (0, 360, 360, True)),
        ("c0-360", (0, 360, 360, True)),
        ("c180-0", (180, 360, 180, False)),
        ("c350-10", (350, 370, 20, False)),
        ("c10-370", (10, 370, 360, True)),
    ],
)
def test_parse_circular_layout_valid_cases(layout, expected):
    """Circular layout parser normalizes wrapped spans consistently."""
    assert _parse_circular_layout(layout) == expected


@pytest.mark.parametrize(
    "layout",
    ["", "r", "cx", "c0-0", "c10-10", "c720", "c0-721", "c10--20"],
)
def test_parse_circular_layout_rejects_invalid_cases(layout):
    """Malformed or over-wide circular spans raise ToytreeError."""
    with pytest.raises(ToytreeError):
        _parse_circular_layout(layout)


def test_circular_layout_uses_unit_depths_when_edge_lengths_are_zero():
    """Zero-length trees fall back to root-depth radii instead of collapsing."""
    tree = toytree.tree("((a:0,b:0):0,(c:0,d:0):0);")
    style = tree.style.copy()
    style.layout = "c"
    style.use_edge_lengths = True

    layout = CircularLayout(tree, style)
    radii = np.linalg.norm(layout.coords, axis=1)
    observed = np.unique(np.round(radii, 6))

    assert np.array_equal(observed, np.array([0.0, 1.0, 2.0]))
    assert np.allclose(
        np.linalg.norm(layout.tcoords, axis=1),
        np.repeat(2.0, tree.ntips),
    )


def test_circular_layout_single_tip_tree_smoke():
    """A one-tip tree produces valid coordinate tables without special casing."""
    tree = toytree.tree("a;")
    style = tree.style.copy()
    style.layout = "c0-180"

    layout = CircularLayout(tree, style)

    assert layout.coords.shape == (tree.nnodes, 2)
    assert layout.tcoords.shape == (tree.ntips, 2)
    assert np.all(np.isfinite(layout.coords))
    assert np.all(np.isfinite(layout.tcoords))


def test_shifted_full_circle_layout_uses_square_domain():
    """Any 360-degree circular span uses the symmetric full-circle domain."""
    tree = toytree.rtree.unittree(10, seed=123)
    _, _, mark = tree.draw(layout="c10-370", tip_labels=False)
    xmin, xmax = mark.domain("x")
    ymin, ymax = mark.domain("y")

    assert np.isclose(abs(xmin), abs(xmax))
    assert np.isclose(abs(ymin), abs(ymax))
    assert np.isclose(xmax - xmin, ymax - ymin)
