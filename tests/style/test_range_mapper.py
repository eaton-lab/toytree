#!/usr/bin/env python

"""Tests for range mapping helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import toytree
from toytree.data import get_range_mapped_feature, get_range_mapped_values
from toytree.utils import ToytreeError


def test_get_range_mapped_feature_from_tree_feature() -> None:
    """Map numeric tree feature values to a requested range."""
    tree = toytree.rtree.unittree(4).set_node_data("x", [0, 1, 2, 3, 4, 5, 6])
    vals = get_range_mapped_feature(tree, "x", min_value=1, max_value=5)
    assert len(vals) == tree.nnodes
    assert float(np.nanmin(vals)) == pytest.approx(1.0)
    assert float(np.nanmax(vals)) == pytest.approx(5.0)


def test_tree_get_range_mapped_feature_from_tree_feature() -> None:
    """ToyTree should expose the feature range-mapper directly."""
    tree = toytree.rtree.unittree(4).set_node_data("x", [0, 1, 2, 3, 4, 5, 6])
    vals = tree.get_range_mapped_feature("x", min_value=1, max_value=5)
    assert len(vals) == tree.nnodes
    assert float(np.nanmin(vals)) == pytest.approx(1.0)
    assert float(np.nanmax(vals)) == pytest.approx(5.0)


def test_get_range_mapped_feature_rejects_non_str_data() -> None:
    """Feature mapping API only accepts a feature-name string."""
    tree = toytree.rtree.unittree(4)
    with pytest.raises(ToytreeError):
        get_range_mapped_feature(tree, [1, 2, 3])  # type: ignore[arg-type]


def test_get_range_mapped_values_sequence() -> None:
    """Sequence values are interpreted in positional order."""
    vals = get_range_mapped_values([0, 10, 20], min_value=2, max_value=4)
    assert len(vals) == 3
    assert float(vals[0]) == pytest.approx(2.0)
    assert float(vals[-1]) == pytest.approx(4.0)


def test_get_range_mapped_values_series_uses_idx_index() -> None:
    """Series index labels define placement in idx space."""
    series = pd.Series([0.0, 10.0], index=[0, 3])
    vals = get_range_mapped_values(series, min_value=1, max_value=3, nan_value=0)
    assert len(vals) == 4
    assert float(vals[1]) == pytest.approx(0.0)
    assert float(vals[2]) == pytest.approx(0.0)


def test_get_range_mapped_values_rejects_str_and_mapping() -> None:
    """String and Mapping inputs are invalid for values API."""
    with pytest.raises(ToytreeError):
        get_range_mapped_values("x", 1, 2)  # type: ignore[arg-type]
    with pytest.raises(ToytreeError):
        get_range_mapped_values({0: 1.0, 1: 2.0}, 1, 2)  # type: ignore[arg-type]


def test_get_range_mapped_values_series_bad_index_raises() -> None:
    """Series index must be unique non-negative integer labels."""
    with pytest.raises(ToytreeError):
        get_range_mapped_values(pd.Series([1.0, 2.0], index=[0, 0]), 1, 2)
    with pytest.raises(ToytreeError):
        get_range_mapped_values(pd.Series([1.0], index=[-1]), 1, 2)
    with pytest.raises(ToytreeError):
        get_range_mapped_values(pd.Series([1.0], index=["a"]), 1, 2)


def test_get_range_mapped_values_nan_guard() -> None:
    """NaN handling follows nan_value=None guard."""
    with pytest.raises(ToytreeError):
        get_range_mapped_values([1.0, np.nan, 2.0], 1, 2, nan_value=None)
