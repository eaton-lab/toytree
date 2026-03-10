#!/usr/bin/env python

"""Tests for `write_single_feature` Newick serialization mode."""

from __future__ import annotations

import numpy as np
import pytest

import toytree
from toytree.utils import ToytreeError


def test_write_single_feature_roundtrip_to_trait() -> None:
    """Writing `name{value}` labels should roundtrip parse to `trait`."""
    tree = toytree.rtree.unittree(4, seed=123)
    name_map = {node.idx: f"n{node.idx}" for node in tree}
    tree = tree.set_node_data("name", name_map)
    tree = tree.set_node_data("state", default=1)

    nwk = tree.write(
        internal_labels="name",
        dist_formatter=None,
        write_single_feature="state",
    )
    assert "n0{1}" in nwk

    parsed = toytree.tree(nwk, internal_labels="name")
    assert "trait" in parsed.features
    traits = parsed.get_node_data("trait")
    assert set(traits.dropna().tolist()) == {1}


def test_write_single_feature_respects_internal_labels_support() -> None:
    """Curly suffix writing should append to support labels when requested."""
    tree = toytree.tree("((a:1,b:1)90:1,c:1)100:0;")
    tree = tree.set_node_data("state", default=7)
    nwk = tree.write(write_single_feature="state")
    assert "90{7}" in nwk
    assert "100{7}" in nwk


def test_write_single_feature_missing_feature_raises() -> None:
    """Selected write feature must exist in the tree."""
    tree = toytree.rtree.unittree(4, seed=123)
    with pytest.raises(ToytreeError, match="not present"):
        tree.write(write_single_feature="state")


def test_write_single_feature_nan_values_raise() -> None:
    """Selected feature cannot contain NaN values."""
    tree = toytree.rtree.unittree(4, seed=123)
    tree = tree.set_node_data("state", {0: np.nan}, default=1)
    with pytest.raises(ToytreeError, match="cannot include NaN values"):
        tree.write(write_single_feature="state")


def test_write_single_feature_is_not_supported_for_nexus() -> None:
    """Curly-suffix single-feature mode is disabled for Nexus output."""
    tree = toytree.rtree.unittree(4, seed=123)
    tree = tree.set_node_data("state", default=1)
    with pytest.raises(ToytreeError, match="not supported with nexus=True"):
        tree.write(write_single_feature="state", nexus=True)


def test_write_feature_pack_serializes_list_like_values() -> None:
    """List-like metadata values should be packed using `feature_pack`."""
    tree = toytree.rtree.unittree(3, seed=123)
    tree = tree.set_node_data("posterior", default=[0.1, 0.9])
    nwk = tree.write(features=["posterior"])
    assert "[&posterior=0.1|0.9]" in nwk

    parsed = toytree.tree(nwk)
    assert parsed.get_node_data("posterior").iloc[0] == [0.1, 0.9]


def test_write_feature_pack_custom_separator_roundtrips() -> None:
    """Custom pack separators should roundtrip with matching unpack token."""
    tree = toytree.rtree.unittree(3, seed=123)
    tree = tree.set_node_data("posterior", default=[0.2, 0.8])
    nwk = tree.write(features=["posterior"], feature_pack=";")
    assert "[&posterior=0.2;0.8]" in nwk

    parsed = toytree.tree(nwk, feature_unpack=";")
    assert parsed.get_node_data("posterior").iloc[0] == [0.2, 0.8]


def test_write_feature_pack_conflict_raises() -> None:
    """Packed-value token cannot overlap metadata key/value delimiters."""
    tree = toytree.rtree.unittree(3, seed=123)
    tree = tree.set_node_data("posterior", default=[0.2, 0.8])
    with pytest.raises(ToytreeError, match="feature_pack cannot match"):
        tree.write(
            features=["posterior"],
            feature_pack=",",
            features_delim=",",
        )
