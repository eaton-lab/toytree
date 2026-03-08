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


def _internal_nodes_excluding_root(tree: toytree.ToyTree) -> list:
    """Return internal nodes excluding the root."""
    return [node for node in tree if (not node.is_leaf()) and (not node.is_root())]


def _find_unittree_seed_with_root_internal_count(
    ntips: int, ninternal: int, max_seed: int = 2000
) -> int:
    """Return first seed where root has exactly ``ninternal`` internal children."""
    for seed in range(max_seed):
        tree = toytree.rtree.unittree(ntips, treeheight=1.0, seed=seed)
        count = sum(int(not child.is_leaf()) for child in tree.treenode.children)
        if count == ninternal:
            return seed
    raise AssertionError(
        f"No seed in range(0, {max_seed}) produced root internal count {ninternal}."
    )


def test_unittree_root_two_internal_children_get_half_internal_length() -> None:
    """When root has two internal children, each root edge should be half X."""
    seed = _find_unittree_seed_with_root_internal_count(8, ninternal=2)
    tree = toytree.rtree.unittree(8, treeheight=1.0, seed=seed)
    root = tree.treenode
    root_internal = [child for child in root.children if not child.is_leaf()]
    assert len(root_internal) == 2

    non_root_internal = _internal_nodes_excluding_root(tree)
    baseline = max(node._dist for node in non_root_internal)
    assert baseline > 0

    for child in root_internal:
        assert child._dist == pytest.approx(0.5 * baseline)


def test_unittree_root_one_tip_child_internal_length_equals_x() -> None:
    """If one root child is tip, the internal root-child edge should be X."""
    seed = _find_unittree_seed_with_root_internal_count(8, ninternal=1)
    tree = toytree.rtree.unittree(8, treeheight=1.0, seed=seed)
    root = tree.treenode
    root_internal = [child for child in root.children if not child.is_leaf()]
    root_tips = [child for child in root.children if child.is_leaf()]
    assert len(root_internal) == 1
    assert len(root_tips) == 1

    non_root_internal = _internal_nodes_excluding_root(tree)
    baseline = max(node._dist for node in non_root_internal)
    assert baseline > 0
    assert root_internal[0]._dist == pytest.approx(baseline)


def test_unittree_ntips_two_still_ultrametric_and_scaled() -> None:
    """ntips=2 should remain ultrametric with requested root height."""
    tree = toytree.rtree.unittree(2, treeheight=3.5, seed=123)
    assert tree.is_ultrametric()
    assert tree.treenode.height == pytest.approx(3.5)


def test_unittree_cached_heights_match_dist_relationships() -> None:
    """Cached heights should remain consistent with branch lengths."""
    for ninternal in (1, 2):
        seed = _find_unittree_seed_with_root_internal_count(10, ninternal=ninternal)
        tree = toytree.rtree.unittree(10, treeheight=1.0, seed=seed)
        for node in tree:
            if node.is_root():
                continue
            expected_dist = node.up.height - node.height
            assert expected_dist == pytest.approx(node.dist)


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
