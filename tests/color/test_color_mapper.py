#!/usr/bin/env python

"""Tests for color mapping helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import toytree
from toytree.color import ToyColor
from toytree.data import get_color_mapped_feature, get_color_mapped_values
from toytree.utils import ToytreeError


def test_get_color_mapped_feature_from_tree_feature() -> None:
    """Map a named tree feature to colors."""
    tree = toytree.rtree.unittree(4).set_node_data("x", [2, 2, 2, 0, 0, 0, 0])
    colors = get_color_mapped_feature(tree, "x", "Set2")
    cols = toytree.color.COLORS1
    assert all(ToyColor(i) == ToyColor(cols[1]) for i in colors[:3])
    assert all(ToyColor(i) == ToyColor(cols[0]) for i in colors[3:])


def test_tree_get_color_mapped_feature_from_tree_feature() -> None:
    """ToyTree should expose the feature color-mapper directly."""
    tree = toytree.rtree.unittree(4).set_node_data("x", [2, 2, 2, 0, 0, 0, 0])
    colors = tree.get_color_mapped_feature("x", "Set2")
    cols = toytree.color.COLORS1
    assert all(ToyColor(i) == ToyColor(cols[1]) for i in colors[:3])
    assert all(ToyColor(i) == ToyColor(cols[0]) for i in colors[3:])


def test_get_color_mapped_feature_rejects_non_str_data() -> None:
    """Feature mapping API only accepts a feature-name string."""
    tree = toytree.rtree.unittree(4)
    with pytest.raises(ToytreeError):
        get_color_mapped_feature(tree, [1, 2, 3])  # type: ignore[arg-type]


def test_get_color_mapped_values_for_sequence_data() -> None:
    """Map sequence values without tree context."""
    colors = get_color_mapped_values([2, 2, 2, 0, 0, 0, 0], "Set2")
    cols = toytree.color.COLORS1
    assert all(ToyColor(i) == ToyColor(cols[1]) for i in colors[:3])
    assert all(ToyColor(i) == ToyColor(cols[0]) for i in colors[3:])


def test_get_color_mapped_values_series_uses_idx_index() -> None:
    """Series index labels define placement in idx space."""
    series = pd.Series(["A", "B"], index=[0, 3])
    colors = get_color_mapped_values(series, "Set2")
    assert len(colors) == 4
    assert ToyColor(colors[1]) == ToyColor("transparent")
    assert ToyColor(colors[2]) == ToyColor("transparent")


def test_get_color_mapped_values_rejects_plain_str_and_mapping() -> None:
    """String and Mapping inputs are invalid for values API."""
    with pytest.raises(ToytreeError):
        get_color_mapped_values("x", "Set2")  # type: ignore[arg-type]
    with pytest.raises(ToytreeError):
        get_color_mapped_values({0: "A", 1: "B"}, "Set2")  # type: ignore[arg-type]


def test_get_color_mapped_values_series_rejects_duplicate_or_bad_idx() -> None:
    """Series index must be unique non-negative integer labels."""
    with pytest.raises(ToytreeError):
        get_color_mapped_values(pd.Series([1, 2], index=[0, 0]), "BlueRed")
    with pytest.raises(ToytreeError):
        get_color_mapped_values(pd.Series([1], index=[-1]), "BlueRed")
    with pytest.raises(ToytreeError):
        get_color_mapped_values(pd.Series([1], index=["a"]), "BlueRed")


def test_get_color_mapped_values_nan_behavior() -> None:
    """NaN values map to transparent by default."""
    data = np.array([1.0, np.nan, 2.0])
    colors = get_color_mapped_values(data, "BlueRed")
    assert ToyColor(colors[1]) == ToyColor("transparent")


def test_get_color_mapped_values_empty_returns_empty_all_maps() -> None:
    """Empty inputs should always return empty arrays regardless of cmap type."""
    for cmap in ("Set2", "BlueRed", "Spectral"):
        out = get_color_mapped_values([], cmap)
        assert isinstance(out, np.ndarray)
        assert out.size == 0


def test_get_color_mapped_values_nan_not_counted_in_category_capacity() -> None:
    """Missing values should not consume categorical-map category slots."""
    vals = list("ABCDEFGH") + [np.nan]
    out = get_color_mapped_values(vals, "Set2")
    assert len(out) == len(vals)
    assert ToyColor(out[-1]) == ToyColor("transparent")


def test_get_color_mapped_values_pdna_treated_as_missing() -> None:
    """Pandas NA values should map to the missing-value color."""
    vals = pd.Series(["A", pd.NA, "B"])
    out = get_color_mapped_values(vals, "Set2")
    assert len(out) == 3
    assert ToyColor(out[1]) == ToyColor("transparent")


def test_get_color_mapped_values_none_treated_as_missing() -> None:
    """Python None values should map to the missing-value color."""
    vals = ["A", None, "B"]
    out = get_color_mapped_values(vals, "Set2")
    assert len(out) == 3
    assert ToyColor(out[1]) == ToyColor("transparent")


def test_get_color_mapped_values_series_fractional_index_raises() -> None:
    """Series index labels must be integer-valued node idx labels."""
    with pytest.raises(ToytreeError):
        get_color_mapped_values(pd.Series(["A", "B"], index=[0.5, 1.5]), "Set2")
