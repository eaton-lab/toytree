#!/usr/bin/env python

"""Tests for strict style-key handling and style serialization."""

from __future__ import annotations

import inspect

import pytest

import toytree
from toytree.core.style_base import NodeStyle, TipLabelStyle, TreeStyle
from toytree.drawing.src.validate_edges import (
    validate_edge_align_style,
    validate_edge_style,
)
from toytree.drawing.src.validate_utils import (
    substyle_dict_to_css_dict,
    tree_style_to_css_dict,
)
from toytree.utils import ToytreeError


def test_substyle_rejects_unknown_keys() -> None:
    """Unknown style keys should fail fast to catch typos."""
    sty = NodeStyle()
    with pytest.raises(ToytreeError, match="Unsupported style key"):
        sty["not-a-real-style"] = 1
    with pytest.raises(ToytreeError, match="Unsupported style key"):
        sty.not_a_real_style = 1


def test_substyle_accepts_css_alias_keys() -> None:
    """CSS-style aliases should normalize to canonical dataclass keys."""
    sty = TipLabelStyle()
    sty["anchor-shift"] = 7
    assert sty.anchor_shift == 7
    sty["-toyplot-anchor-shift"] = 11
    assert sty.anchor_shift == 11
    assert sty["-toyplot-anchor-shift"] == 11


def test_tree_style_to_css_dict_is_non_mutating() -> None:
    """Serializing to CSS should not mutate SubStyle objects in TreeStyle."""
    sty = TreeStyle()
    css = tree_style_to_css_dict(sty)
    assert isinstance(sty.node_style, NodeStyle)
    assert isinstance(css["node_style"], dict)
    assert "stroke-width" in css["node_style"]
    assert "shrink" not in css


def test_tree_style_no_longer_exposes_shrink() -> None:
    """The default TreeStyle should not advertise removed draw-only fields."""
    sty = TreeStyle()
    assert not hasattr(sty, "shrink")


def test_substyle_dict_to_css_dict_drops_none_values() -> None:
    """Style serialization should omit unset keys with ``None`` values."""
    css = substyle_dict_to_css_dict(
        {
            "fill": "red",
            "stroke": None,
            "fill_opacity": None,
            "font_size": 12,
            "anchor_shift": 7,
        }
    )
    assert css["fill"] == "red"
    assert css["font-size"] == 12
    assert css["-toyplot-anchor-shift"] == 7
    assert "stroke" not in css
    assert "fill-opacity" not in css


def test_validate_edge_style_coerces_dasharray_tuple() -> None:
    """Edge validators should normalize dasharray tuples to SVG strings."""
    tree = toytree.rtree.unittree(4, seed=123)
    out = validate_edge_style(
        tree,
        stroke_linecap="round",
        stroke_linejoin="bevel",
        stroke_dasharray=(2, 2),
    )
    assert out.stroke_dasharray == "2,2"


def test_validate_edge_align_style_coerces_dasharray_tuple() -> None:
    """Aligned-edge validator should support tuple dasharray input."""
    tree = toytree.rtree.unittree(4, seed=123)
    out = validate_edge_align_style(
        tree,
        stroke_linecap="round",
        stroke_linejoin="miter",
        stroke_dasharray=(3, 1),
    )
    assert out.stroke_dasharray == "3,1"


def test_validate_edge_style_rejects_invalid_linejoin() -> None:
    """Invalid linejoin values should raise clear style validation errors."""
    tree = toytree.rtree.unittree(4, seed=123)
    with pytest.raises(ToytreeError, match="stroke-linejoin"):
        validate_edge_style(tree, stroke_linejoin="diagonal")


def test_draw_signature_drops_edge_marker_edge_label_args() -> None:
    """Draw API should not expose stale edge marker/label params."""
    params = inspect.signature(toytree.ToyTree.draw).parameters
    assert "edge_markers" not in params
    assert "edge_labels" not in params
