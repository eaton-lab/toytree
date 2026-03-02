#!/usr/bin/env python

"""Tests for consensus tree functions."""

from __future__ import annotations

import math

import numpy as np
import pytest

import toytree
from toytree.infer import consensus_features, consensus_tree


def test_get_majority_rule_topology(
    mtree_consensus_utrees: toytree.MultiTree,
) -> None:
    tree = consensus_tree(mtree_consensus_utrees)
    assert tree.get_topology_id() == mtree_consensus_utrees[0].get_topology_id()
    assert not tree.is_rooted()
    assert tree.nedges == 5 + 2
    assert math.isnan(tree[-1].support)
    assert tree.get_mrca_node("a", "b").support == 1.0
    assert tree.get_mrca_node("e", "d").support == 0.5


def test_get_majority_rule_topology_minfreq(
    mtree_consensus_utrees: toytree.MultiTree,
) -> None:
    tree = consensus_tree(mtree_consensus_utrees, min_freq=0.51)
    assert not tree.is_rooted()
    assert tree.nedges == 5 + 1
    assert math.isnan(tree[-1].support)
    assert tree.get_mrca_node("a", "b").support == 1.0
    assert tree.get_mrca_node("e", "d") == tree.get_mrca_node("c", "e", "d")


def test_get_majority_rule_topology_equal_freq_collapsed(
    mtree_consensus_utrees: toytree.MultiTree,
) -> None:
    treelist = mtree_consensus_utrees.treelist + [mtree_consensus_utrees[-1]]
    tree = consensus_tree(treelist)
    assert not tree.is_rooted()
    assert tree.nedges == 5 + 1
    assert math.isnan(tree[-1].support)
    assert tree.get_mrca_node("a", "b").support == 1.0
    assert tree.get_mrca_node("e", "d") == tree.get_mrca_node("c", "e", "d")


def test_get_consensus_features_requires_requested_features(
    mtree_consensus_utrees: toytree.MultiTree,
) -> None:
    ctree = consensus_tree(mtree_consensus_utrees)
    with pytest.raises(ValueError):
        consensus_features(ctree, mtree_consensus_utrees, conditional=False)


def test_get_consensus_features_edge_dist(
    mtree_consensus_utrees: toytree.MultiTree,
) -> None:
    ctree = consensus_tree(mtree_consensus_utrees)
    ftree = consensus_features(
        ctree, mtree_consensus_utrees, edge_features=["dist"], conditional=False
    )
    node = ftree.get_mrca_node("a", "b")
    assert hasattr(node, "dist_mean")
    assert hasattr(node, "dist_median")
    assert hasattr(node, "dist_std")
    assert hasattr(node, "dist_min")
    assert hasattr(node, "dist_max")
    assert hasattr(node, "dist_range")


def test_get_consensus_features_additional_feature(
    mtree_consensus_utrees: toytree.MultiTree,
) -> None:
    trees = [i.copy() for i in mtree_consensus_utrees]
    vals = [1, 2, 3, 4, 5, 6]
    for tree, val in zip(trees, vals):
        tree.set_node_data(
            "rate",
            {tree.get_mrca_node("a", "b").idx: val},
            inplace=True,
        )
    ctree = consensus_tree(trees)
    ftree = consensus_features(ctree, trees, features=["rate"])
    node = ftree.get_mrca_node("a", "b")
    assert node.rate_mean == pytest.approx(float(np.mean(vals)))
    assert node.rate_median == pytest.approx(float(np.median(vals)))
    assert node.rate_min == pytest.approx(float(np.min(vals)))
    assert node.rate_max == pytest.approx(float(np.max(vals)))


def test_get_consensus_features_ultrametric_includes_height(
    mtree_consensus_rtrees: toytree.MultiTree,
) -> None:
    ctree = consensus_tree(mtree_consensus_rtrees)
    rtree = ctree.root("a", "b")
    ftree = consensus_features(
        rtree,
        mtree_consensus_rtrees,
        features=["height"],
        ultrametric=True,
    )
    node = ftree.get_mrca_node("a", "b")
    assert hasattr(node, "height_mean")
    assert hasattr(node, "height_median")
    assert hasattr(node, "height_std")
    assert hasattr(node, "height_min")
    assert hasattr(node, "height_max")


def test_get_consensus_features_raises_on_missing_feature(
    mtree_consensus_utrees: toytree.MultiTree,
) -> None:
    ctree = consensus_tree(mtree_consensus_utrees)
    with pytest.raises(ValueError):
        consensus_features(ctree, mtree_consensus_utrees, features=["not_a_feature"])


def test_get_consensus_features_warns_and_remaps_wrong_feature_class(
    mtree_consensus_rtrees: toytree.MultiTree,
    capsys,
) -> None:
    ctree = consensus_tree(mtree_consensus_rtrees).root("a", "b")
    ftree = consensus_features(
        ctree,
        mtree_consensus_rtrees,
        features=["dist"],
        edge_features=["height"],
        ultrametric=True,
    )
    msg = capsys.readouterr().err
    assert "'dist' was provided in features" in msg
    assert "'height' was provided in edge_features" in msg
    assert hasattr(ftree.get_mrca_node("a", "b"), "dist_mean")
    assert hasattr(ftree.get_mrca_node("a", "b"), "height_mean")


def test_get_consensus_tree_rejects_min_freq_out_of_bounds(
    mtree_consensus_utrees: toytree.MultiTree,
) -> None:
    with pytest.raises(ValueError):
        consensus_tree(mtree_consensus_utrees, min_freq=1.1)
