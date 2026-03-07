#!/usr/bin/env python

"""Tests for enumeration counting helpers."""

import pytest

import toytree


def test_get_num_bifurcating_trees_known_values():
    """Match known rooted and unrooted counts for small n."""
    rooted = {2: 1, 3: 3, 4: 15, 5: 105, 6: 945}
    unrooted = {3: 1, 4: 3, 5: 15, 6: 105}

    for ntips, expected in rooted.items():
        assert toytree.enum.get_num_bifurcating_trees(ntips, rooted=True) == expected
    for ntips, expected in unrooted.items():
        assert toytree.enum.get_num_bifurcating_trees(ntips, rooted=False) == expected


def test_get_num_bifurcating_trees_large_n_no_overflow():
    """Return exact large integers without float overflow."""
    result = toytree.enum.get_num_bifurcating_trees(200, rooted=True)
    assert isinstance(result, int)
    assert result > 0


def test_get_num_quartets_and_subtrees_consistency():
    """Quartet counts should equal 4-tip subtree counts."""
    tree = toytree.rtree.unittree(10, seed=123)
    assert toytree.enum.get_num_quartets(10) == 210
    assert toytree.enum.get_num_quartets(tree) == 210
    assert toytree.enum.get_num_subtrees(10, 4) == 210
    assert toytree.enum.get_num_subtrees(tree, 4) == 210


def test_get_num_subtrees_handles_subtree_size_larger_than_ntips():
    """Requesting oversized subsets should return zero."""
    assert toytree.enum.get_num_subtrees(4, 5) == 0


def test_get_num_labeled_histories_known_values():
    """Match known ranked labeled-history counts for small n."""
    rooted = {1: 1, 2: 1, 3: 3, 4: 18, 5: 180, 6: 2700}
    unrooted = {2: 1, 3: 1, 4: 3, 5: 18, 6: 180}

    for ntips, expected in rooted.items():
        assert toytree.enum.get_num_labeled_histories(ntips, rooted=True) == expected
    for ntips, expected in unrooted.items():
        assert toytree.enum.get_num_labeled_histories(ntips, rooted=False) == expected


def test_get_num_unlabeled_histories_known_values():
    """Match recurrence values for ranked unlabeled histories."""
    rooted = {1: 1, 2: 1, 3: 1, 4: 3, 5: 6, 6: 24, 7: 84}
    unrooted = {2: 1, 3: 1, 4: 1, 5: 3, 6: 6}

    for ntips, expected in rooted.items():
        assert toytree.enum.get_num_unlabeled_histories(ntips, rooted=True) == expected
    for ntips, expected in unrooted.items():
        assert toytree.enum.get_num_unlabeled_histories(ntips, rooted=False) == expected


def test_get_num_multifurcating_trees_total_excludes_bifurcating():
    """Default totals should count only trees with at least one polytomy."""
    rooted = {2: 0, 3: 1, 4: 11, 5: 131}
    unrooted = {3: 0, 4: 1, 5: 11, 6: 131}

    for ntips, expected in rooted.items():
        assert toytree.enum.get_num_multifurcating_trees(ntips, rooted=True) == expected
    for ntips, expected in unrooted.items():
        assert (
            toytree.enum.get_num_multifurcating_trees(ntips, rooted=False) == expected
        )


def test_get_num_multifurcating_trees_by_internal_nodes():
    """Internal-node-class counts should match DP table classes."""
    assert toytree.enum.get_num_multifurcating_trees(5, 1, rooted=True) == 1
    assert toytree.enum.get_num_multifurcating_trees(5, 2, rooted=True) == 25
    assert toytree.enum.get_num_multifurcating_trees(5, 3, rooted=True) == 105

    with pytest.raises(ValueError, match="fully bifurcating"):
        toytree.enum.get_num_multifurcating_trees(5, 4, rooted=True)


def test_get_num_labeled_partitions_respects_min_size():
    """Partition counts should change when min_size changes."""
    assert toytree.enum.get_num_labeled_partitions(6, min_size=1) == 31
    assert toytree.enum.get_num_labeled_partitions(6, min_size=2) == 25
    assert toytree.enum.get_num_labeled_partitions(6, min_size=3) == 10
    assert toytree.enum.get_num_labeled_partitions(6, min_size=4) == 0


def test_counting_api_exposure_scope():
    """New counting helpers are available from module-level enum API only."""
    assert hasattr(toytree.enum, "get_num_labeled_histories")
    assert hasattr(toytree.enum, "get_num_unlabeled_histories")
    assert hasattr(toytree.enum, "get_num_multifurcating_trees")

    tree = toytree.rtree.unittree(5, seed=123)
    assert not hasattr(tree.enum, "get_num_labeled_histories")
    assert not hasattr(tree.enum, "get_num_unlabeled_histories")
    assert not hasattr(tree.enum, "get_num_multifurcating_trees")


def test_get_num_quartets_removed_method_arg():
    """Legacy unused method argument should no longer be accepted."""
    with pytest.raises(TypeError):
        toytree.enum.get_num_quartets(10, method=0)
