#!/usr/bin/env python

"""Tests for birth-death random tree generation."""

from __future__ import annotations

import pytest

import toytree
from toytree.utils import ToytreeError


def _root_to_tip_distance(node) -> float:
    """Return path length from tip node to root."""
    # In toytree, the root-edge dist can be non-zero, so include the
    # selected node and all of its ancestors in the path sum.
    return sum(float(anc.dist) for anc in [node, *node.iter_ancestors()])


def test_bdtree_taxa_no_zero_length_tip_edges() -> None:
    """`stop='taxa'` should not return deterministic zero-length tips."""
    for seed in range(50):
        tree = toytree.rtree.bdtree(
            ntips=30,
            stop="taxa",
            b=1.0,
            d=0.3,
            seed=seed,
        )
        tip_dists = [float(node.dist) for node in tree[: tree.ntips]]
        assert all(dist > 0.0 for dist in tip_dists)


def test_bdtree_time_stops_at_requested_time() -> None:
    """`stop='time'` should end exactly at the requested horizon."""
    time_stop = 3.25
    tree = toytree.rtree.bdtree(
        stop="time",
        time=time_stop,
        b=1.0,
        d=0.2,
        seed=123,
    )
    tip_depths = [_root_to_tip_distance(node) for node in tree[: tree.ntips]]
    assert max(tip_depths) == pytest.approx(time_stop)


def test_bdtree_time_no_zero_length_tip_edges() -> None:
    """`stop='time'` should not end on a boundary birth event artifact."""
    for seed in range(50):
        tree = toytree.rtree.bdtree(
            stop="time",
            time=2.0,
            b=1.0,
            d=0.3,
            seed=seed,
        )
        tip_dists = [float(node.dist) for node in tree[: tree.ntips]]
        assert all(dist > 0.0 for dist in tip_dists)


def test_bdtree_return_stats_dict_contains_tree_and_counts() -> None:
    """`return_stats=True` should return a dict with tree and event stats."""
    result = toytree.rtree.bdtree(
        ntips=20,
        stop="taxa",
        b=1.0,
        d=0.3,
        seed=123,
        return_stats=True,
    )
    assert isinstance(result, dict)
    assert "tree" in result
    tree = result["tree"]
    assert isinstance(tree, toytree.ToyTree)
    assert result["events"] == result["births"] + result["deaths"]
    if result["deaths"] == 0:
        assert result["birth_death_ratio"] == pytest.approx(float("inf"))
    else:
        assert result["birth_death_ratio"] == pytest.approx(
            result["births"] / result["deaths"]
        )


def test_bdtree_rejects_nonfinite_rates() -> None:
    """Non-finite birth/death rates should raise ToytreeError."""
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(ntips=10, b=float("nan"), d=0.1)
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(ntips=10, b=0.1, d=float("inf"))


def test_bdtree_max_resets_validation() -> None:
    """`max_resets` must be None or integer >= 0."""
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(ntips=10, b=0.1, d=0.1, max_resets=-1)
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(ntips=10, b=0.1, d=0.1, max_resets=True)


def test_bdtree_max_resets_exceeded_raises() -> None:
    """A low restart cap should fail in a high-extinction regime."""
    with pytest.raises(ToytreeError, match="exceeded max_resets"):
        toytree.rtree.bdtree(
            ntips=8,
            stop="taxa",
            b=0.01,
            d=10.0,
            seed=123,
            max_resets=0,
        )
