#!/usr/bin/env python

"""Tests for unrooted-layout coordinate generation and validation."""

import numpy as np
import pytest

import toytree
from toytree.core import TreeStyle
from toytree.layout.src.layout_unrooted import (
    UnrootedLayout,
    equal_angle_algorithm,
    equal_daylight_algorithm,
)
from toytree.utils import ToytreeError


def test_unrooted_layout_applies_baseline_translation():
    """Unrooted layouts should honor the same baselines as other layouts."""
    tree = toytree.rtree.unittree(12, seed=123)

    base_style = TreeStyle()
    base_style.layout = "unrooted"
    base_style.xbaseline = 0.0
    base_style.ybaseline = 0.0
    base = UnrootedLayout(tree, base_style)

    shifted_style = TreeStyle()
    shifted_style.layout = "unrooted"
    shifted_style.xbaseline = 10.5
    shifted_style.ybaseline = -7.25
    shifted = UnrootedLayout(tree, shifted_style)

    delta = np.array([shifted_style.xbaseline, shifted_style.ybaseline])
    assert np.allclose(shifted.coords, base.coords + delta)
    assert np.allclose(shifted.tcoords, base.tcoords + delta)


def test_unrooted_layout_pins_root_to_origin_by_default():
    """Unrooted layouts should center the tree root at the origin."""
    tree = toytree.rtree.unittree(12, seed=123)
    style = TreeStyle()
    style.layout = "unrooted"
    style.xbaseline = 0.0
    style.ybaseline = 0.0

    layout = UnrootedLayout(tree, style)

    assert np.allclose(layout.coords[tree.treenode.idx], np.zeros(2))


def test_unrooted_layout_pins_root_to_baseline():
    """Unrooted layouts should anchor the tree root at the baselines."""
    tree = toytree.rtree.unittree(12, seed=123)
    style = TreeStyle()
    style.layout = "unrooted"
    style.xbaseline = 10.5
    style.ybaseline = -7.25

    layout = UnrootedLayout(tree, style)

    assert np.allclose(
        layout.coords[tree.treenode.idx],
        np.array([style.xbaseline, style.ybaseline]),
    )


def test_equal_daylight_max_iter_zero_matches_equal_angle():
    """`max_iter=0` should return the unmodified equal-angle layout."""
    tree = toytree.rtree.unittree(10, seed=123)

    equal_angle = equal_angle_algorithm(tree, use_edge_lengths=True)
    equal_daylight = equal_daylight_algorithm(
        tree,
        max_iter=0,
        use_edge_lengths=True,
    )

    assert np.allclose(equal_daylight, equal_angle)


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"max_iter": -1}, "max_iter"),
        ({"max_iter": 1.5}, "max_iter"),
        ({"max_iter": True}, "max_iter"),
        ({"min_delta": -1}, "min_delta"),
        ({"min_delta": np.nan}, "min_delta"),
        ({"min_delta": np.inf}, "min_delta"),
    ],
)
def test_equal_daylight_rejects_invalid_stopping_args(kwargs, match):
    """Invalid equal-daylight stopping arguments should raise ToytreeError."""
    tree = toytree.rtree.unittree(8, seed=123)

    with pytest.raises(ToytreeError, match=match):
        equal_daylight_algorithm(tree, **kwargs)


def test_equal_daylight_returns_finite_coords_for_rooted_and_unrooted_input():
    """Equal-daylight projection should return finite coordinates on both trees."""
    tree = toytree.rtree.unittree(12, seed=123)

    for current in (tree, tree.unroot()):
        coords = equal_daylight_algorithm(current, max_iter=2)
        assert coords.shape == (current.nnodes, 2)
        assert np.all(np.isfinite(coords))
