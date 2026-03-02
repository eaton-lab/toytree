#!/usr/bin/env python

from __future__ import annotations

import pytest

import toytree
from toytree.utils import ToytreeError


def test_rtree_rejects_invalid_ntips() -> None:
    for bad in (0, 1, -1, 2.5, "4", True):
        with pytest.raises(ToytreeError):
            toytree.rtree.rtree(bad)


def test_rtree_two_tips() -> None:
    tree = toytree.rtree.rtree(2, seed=123)
    assert tree.ntips == 2
    assert tree.nnodes == 3


def test_rtree_seeded_reproducibility() -> None:
    tree1 = toytree.rtree.rtree(12, random_names=True, seed=123)
    tree2 = toytree.rtree.rtree(12, random_names=True, seed=123)
    assert tree1.get_topology_id() == tree2.get_topology_id()
    assert tree1.get_tip_labels() == tree2.get_tip_labels()


def test_rtree_root_child_edges_are_half() -> None:
    tree = toytree.rtree.rtree(10, seed=123)
    dists = [child._dist for child in tree.treenode.children]
    assert len(dists) == 2
    assert all(dist == 0.5 for dist in dists)


def test_rtree_names_len_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        toytree.rtree.rtree(4, names=["a", "b", "c"])


def test_rtree_names_assigned_in_idx_order() -> None:
    names = ["a", "b", "c", "d"]
    tree = toytree.rtree.rtree(4, names=names, random_names=False, seed=123)
    assert tree.get_tip_labels() == names


def test_rtree_names_random_assignment() -> None:
    names = ["a", "b", "c", "d", "e", "f"]
    tree1 = toytree.rtree.rtree(6, names=names, random_names=True, seed=123)
    tree2 = toytree.rtree.rtree(6, names=names, random_names=True, seed=123)
    assert tree1.get_tip_labels() == tree2.get_tip_labels()
    assert set(tree1.get_tip_labels()) == set(names)


def test_unittree_names_len_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        toytree.rtree.unittree(4, names=["a", "b", "c"])


def test_unittree_treeheight_validation() -> None:
    for bad in (0, -1, float("nan"), float("inf"), "bad", True):
        with pytest.raises(ToytreeError):
            toytree.rtree.unittree(4, treeheight=bad)


def test_unittree_names_and_height() -> None:
    names = ["a", "b", "c", "d", "e", "f"]
    tree = toytree.rtree.unittree(
        6, treeheight=5.0, names=names, random_names=False, seed=123
    )
    assert tree.get_tip_labels() == names
    assert tree.is_ultrametric()
    assert tree.treenode.height == pytest.approx(5.0)


def test_unittree_names_random_assignment() -> None:
    names = ["a", "b", "c", "d", "e", "f"]
    tree1 = toytree.rtree.unittree(6, names=names, random_names=True, seed=123)
    tree2 = toytree.rtree.unittree(6, names=names, random_names=True, seed=123)
    assert tree1.get_tip_labels() == tree2.get_tip_labels()
    assert set(tree1.get_tip_labels()) == set(names)


def test_bdtree_parameter_validation() -> None:
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(stop="bad")
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(b=-1)
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(d=-1)
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(b=0, d=0)
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(stop="taxa", ntips=1)
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(stop="time", time=0)


def test_bdtree_retain_extinct_keeps_extinct_lineages() -> None:
    tree = toytree.rtree.bdtree(
        ntips=8,
        b=1.0,
        d=0.9,
        stop="taxa",
        retain_extinct=True,
        seed=1,
    )
    extinct_count = sum(int(getattr(node, "extinct", False)) for node in tree)
    assert extinct_count > 0


def test_bdtree_yule_time_stop_ultrametric() -> None:
    tree = toytree.rtree.bdtree(stop="time", time=2.0, b=1.0, d=0.0, seed=123)
    assert tree.is_ultrametric()


def test_bdtree_high_extinction_with_resets() -> None:
    tree = toytree.rtree.bdtree(ntips=6, b=0.2, d=0.8, stop="taxa", seed=123)
    assert tree.ntips == 6


def test_bdtree_time_stop_retain_extinct() -> None:
    tree = toytree.rtree.bdtree(
        stop="time", time=2.0, b=1.0, d=0.8, retain_extinct=True, seed=123
    )
    assert tree.ntips >= 1
    extinct = sum(int(getattr(node, "extinct", False)) for node in tree)
    assert extinct >= 0


def test_bdtree_names_taxa_stop() -> None:
    names = ["a", "b", "c", "d", "e", "f"]
    tree = toytree.rtree.bdtree(
        ntips=6,
        b=1.0,
        d=0.2,
        stop="taxa",
        names=names,
        random_names=False,
        seed=123,
    )
    assert tree.get_tip_labels() == names


def test_bdtree_names_validation() -> None:
    with pytest.raises(ValueError):
        toytree.rtree.bdtree(ntips=4, stop="taxa", names=["a", "b", "c"])
    with pytest.raises(ToytreeError):
        toytree.rtree.bdtree(stop="time", time=2.0, names=["a", "b"])


def test_imbtree_validation_and_names() -> None:
    with pytest.raises(ToytreeError):
        toytree.rtree.imbtree(1)
    with pytest.raises(ToytreeError):
        toytree.rtree.imbtree(4, treeheight=0)
    with pytest.raises(ValueError):
        toytree.rtree.imbtree(4, names=["a", "b", "c"])
    names = ["a", "b", "c", "d"]
    tree = toytree.rtree.imbtree(4, names=names, random_names=False, seed=123)
    assert tree.get_tip_labels() == names
    assert tree.treenode.height == pytest.approx(1.0)


def test_baltree_validation_and_names() -> None:
    with pytest.raises(ToytreeError):
        toytree.rtree.baltree(1)
    with pytest.raises(ToytreeError):
        toytree.rtree.baltree(3)
    with pytest.raises(ToytreeError):
        toytree.rtree.baltree(4, treeheight=float("nan"))
    with pytest.raises(ValueError):
        toytree.rtree.baltree(4, names=["a", "b", "c"])
    names = ["a", "b", "c", "d"]
    tree = toytree.rtree.baltree(4, names=names, random_names=False, seed=123)
    assert tree.get_tip_labels() == names
    assert tree.treenode.height == pytest.approx(1.0)


def test_coaltree_validation() -> None:
    with pytest.raises(ToytreeError):
        toytree.rtree.coaltree(1)
    with pytest.raises(ToytreeError):
        toytree.rtree.coaltree(4, N=0)
    with pytest.raises(ToytreeError):
        toytree.rtree.coaltree(4, N=float("nan"))
    with pytest.raises(ValueError):
        toytree.rtree.coaltree(4, names=["a", "b", "c"])


def test_coaltree_names_and_randomization() -> None:
    names = ["a", "b", "c", "d", "e", "f"]
    tree = toytree.rtree.coaltree(6, names=names, random_names=False, seed=123)
    assert tree.get_tip_labels() == names
    tree1 = toytree.rtree.coaltree(6, names=names, random_names=True, seed=123)
    tree2 = toytree.rtree.coaltree(6, names=names, random_names=True, seed=123)
    assert tree1.get_tip_labels() == tree2.get_tip_labels()
    assert set(tree1.get_tip_labels()) == set(names)


def test_coaltree_basic_shape() -> None:
    tree = toytree.rtree.coaltree(8, N=100, seed=123)
    assert tree.ntips == 8
    assert tree.nnodes == 15
    assert tree.is_ultrametric()
