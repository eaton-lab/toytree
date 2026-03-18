#!/usr/bin/env python

"""Tests for circular-layout parsing and coordinate projection."""

import numpy as np
import pytest

import toytree
from toytree.layout.src.layout_circular import CircularLayout, _parse_circular_layout
from toytree.utils import ToytreeError


def _radii(coords: np.ndarray, root_xy: np.ndarray) -> np.ndarray:
    """Return Euclidean radii from one root coordinate."""
    root_xy = np.asarray(root_xy, dtype=float)
    return np.sqrt(np.sum((coords - root_xy) ** 2, axis=1))


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
    """Zero-length trees fall back to unit cladogram heights."""
    tree = toytree.tree("((a:0,b:0):0,(c:0,d:0):0);")
    style = tree.style.copy()
    style.layout = "c"
    style.use_edge_lengths = True

    layout = CircularLayout(tree, style)
    root_xy = layout.coords[tree.treenode.idx]
    radii = _radii(layout.coords, root_xy)
    observed = np.unique(np.round(radii, 6))

    assert np.array_equal(observed, np.array([0.0, 1.0, 2.0]))
    assert np.allclose(_radii(layout.tcoords, root_xy), np.repeat(2.0, 4))


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


@pytest.mark.parametrize("layout", ["c", "c0-180"])
def test_circular_draw_tip_labels_align_false_keeps_tip_coordinates(layout):
    """Circular layout should not align labels unless explicitly requested."""
    tree = toytree.tree("((a:2,b:1):1,(c:1,d:2):1);")
    _, _, mark = tree.draw(
        layout=layout,
        tip_labels=True,
        tip_labels_align=False,
        use_edge_lengths=True,
    )
    root_xy = mark.ntable[tree.treenode.idx]
    tip_radii = _radii(mark.ntable, root_xy)[: tree.ntips]
    label_radii = _radii(mark.ttable, root_xy)

    assert not bool(mark.tip_labels_align)
    assert np.ptp(tip_radii) > 0.0
    assert np.allclose(mark.ttable, mark.ntable[: tree.ntips])
    assert np.allclose(label_radii, tip_radii)


@pytest.mark.parametrize("layout", ["c", "c0-180"])
def test_circular_draw_tip_labels_align_true_uses_outer_ring(layout):
    """Aligned circular labels should move only the label coordinates."""
    tree = toytree.tree("((a:2,b:1):1,(c:1,d:2):1);")
    _, _, mark = tree.draw(
        layout=layout,
        tip_labels=True,
        tip_labels_align=True,
        use_edge_lengths=True,
    )
    root_xy = mark.ntable[tree.treenode.idx]
    tip_radii = _radii(mark.ntable, root_xy)[: tree.ntips]
    label_radii = _radii(mark.ttable, root_xy)

    assert bool(mark.tip_labels_align)
    assert np.ptp(tip_radii) > 0.0
    assert np.ptp(label_radii) < 1e-8
    assert np.isclose(label_radii[0], tip_radii.max())


def test_circular_draw_use_edge_lengths_false_aligns_tips_and_units_internals():
    """Circular cladograms should align tips and use unit internal levels."""
    tree = toytree.tree("(((a:5,b:1):2,c:1):1,(d:1,e:2):1);")
    _, _, mark = tree.draw(
        layout="c",
        tip_labels=False,
        tip_labels_align=False,
        use_edge_lengths=False,
    )
    root_xy = mark.ntable[tree.treenode.idx]
    radii = np.unique(np.round(_radii(mark.ntable, root_xy), 6))
    tip_radii = _radii(mark.ntable, root_xy)[: tree.ntips]

    assert np.allclose(tip_radii, np.repeat(tip_radii[0], tree.ntips))
    assert np.array_equal(radii, np.array([0.0, 1.0, 2.0, 3.0]))


def test_circular_draw_zero_length_fallback_aligns_tips_on_fan_layout():
    """Zero-length circular trees should use cladogram fallback on fan layouts."""
    tree = toytree.tree("(((a:0,b:0):0,c:0):0,(d:0,e:0):0);")
    _, _, mark = tree.draw(
        layout="c0-180",
        tip_labels=False,
        tip_labels_align=False,
        use_edge_lengths=True,
    )
    root_xy = mark.ntable[tree.treenode.idx]
    radii = np.unique(np.round(_radii(mark.ntable, root_xy), 6))
    tip_radii = _radii(mark.ntable, root_xy)[: tree.ntips]

    assert np.allclose(tip_radii, np.repeat(tip_radii[0], tree.ntips))
    assert np.array_equal(radii, np.array([0.0, 1.0, 2.0, 3.0]))


def test_circular_draw_default_does_not_force_label_alignment():
    """Circular draws should preserve the default falsey align setting."""
    tree = toytree.tree("((a:2,b:1):1,(c:1,d:2):1);")
    _, _, mark = tree.draw(layout="c", tip_labels=True)

    assert not bool(mark.tip_labels_align)
    assert np.allclose(mark.ttable, mark.ntable[: tree.ntips])
