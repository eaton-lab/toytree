#!/usr/bin/env python

"""Tests for quadripartition enumeration."""

from __future__ import annotations

import itertools
from collections import Counter

import numpy as np

import toytree
from toytree.enum import _iter_quadripartition_sets, iter_quadripartitions

TREE1_NEWICK = "(a,b,((c,d)CD,(e,f)EF)X)AB;"
TREE2_NEWICK = "((r0,(r3,r2)),(r1,(r4,r5)));"

TREE1_LIST_SORT_INT_CON_COL = [
    (["CD"], ["EF"], ["a"], ["b"]),
    (["CD"], ["X"], ["e"], ["f"]),
    (["EF"], ["X"], ["c"], ["d"]),
]
TREE1_LIST_SORT_CON = [
    ((["CD"], ["EF"]), (["a"], ["b"])),
    ((["CD"], ["X"]), (["e"], ["f"])),
    ((["EF"], ["X"]), (["c"], ["d"])),
]
TREE1_LIST_SORT_CON_COL = [
    (["CD"], ["EF"], ["a"], ["b"]),
    (["CD"], ["X"], ["e"], ["f"]),
    (["EF"], ["X"], ["c"], ["d"]),
]
TREE1_LIST_SORT_INT_COL = [
    (["a"], ["b"], ["c", "d", "CD"], ["e", "f", "EF"]),
    (["c"], ["d"], ["a", "b"], ["e", "f", "EF"]),
    (["e"], ["f"], ["a", "b"], ["c", "d", "CD"]),
]
TREE1_LIST_SORT = [
    ((["a"], ["b"]), (["c", "d"], ["e", "f"])),
    ((["c"], ["d"]), (["a", "b"], ["e", "f"])),
    ((["e"], ["f"]), (["a", "b"], ["c", "d"])),
]
TREE1_TUPLE_SORT_INT_COL = [
    (("a",), ("b",), ("c", "d", "CD"), ("e", "f", "EF")),
    (("c",), ("d",), ("a", "b"), ("e", "f", "EF")),
    (("e",), ("f",), ("a", "b"), ("c", "d", "CD")),
]


def _neighbors(node):
    neighbors = list(node.children)
    if node.up is not None:
        neighbors.append(node.up)
    return neighbors


def _tips_reachable(start, blocked_from):
    stack = [(start, blocked_from)]
    seen = set()
    out = set()
    while stack:
        node, prev = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        if node.is_leaf():
            out.add(node.name)
        for neighbor in _neighbors(node):
            if neighbor is prev:
                continue
            stack.append((neighbor, node))
    return frozenset(out)


def _canonical_qpart(a, b, c, d):
    def fs_key(values):
        return (len(values), tuple(sorted(values)))

    side1 = tuple(sorted((frozenset(a), frozenset(b)), key=fs_key))
    side2 = tuple(sorted((frozenset(c), frozenset(d)), key=fs_key))

    def side_key(side):
        return (len(side[0]) + len(side[1]), fs_key(side[0]), fs_key(side[1]))

    return tuple(sorted((side1, side2), key=side_key))


def _quadripartition_counter_bruteforce(tree):
    """Count canonical quadripartitions by explicit edge-local combinatorics."""
    counter = Counter()
    all_tips = frozenset(tree.get_tip_labels())
    topnode = tree.nnodes - 2 if tree.is_rooted() else tree.nnodes - 1

    for node in tree[tree.ntips : topnode]:
        below = [_tips_reachable(child, node) for child in node.children]
        if len(below) < 2:
            continue

        if node.up.is_root():
            sisters = node.get_sisters()
            if len(sisters) > 1:
                above = [_tips_reachable(sister, node.up) for sister in sisters]
            else:
                above = [
                    _tips_reachable(child, sisters[0])
                    for child in sisters[0].children
                ]
        else:
            sisters = [
                _tips_reachable(sister, node.up)
                for sister in node.get_sisters()
            ]
            covered = set().union(*below, *sisters)
            above = sisters + [frozenset(all_tips - covered)]

        for below_pair in itertools.combinations(below, 2):
            for above_pair in itertools.combinations(above, 2):
                counter[_canonical_qpart(*below_pair, *above_pair)] += 1

    return counter


def _quadripartition_counter_observed(tree):
    counter = Counter()
    for (left, right), (up_left, up_right) in _iter_quadripartition_sets(
        tree,
        feature="name",
    ):
        counter[_canonical_qpart(left, right, up_left, up_right)] += 1
    return counter



from conftest import PytestCompat

class TestQuadripartitions(PytestCompat):
    """Validate quadripartition enumeration and formatting options."""

    def setUp(self):
        """Create shared tree fixtures for quadripartition tests."""
        self.tree1 = toytree.tree(TREE1_NEWICK)
        self.tree2 = toytree.tree(TREE2_NEWICK)
        self.trees = [self.tree1, self.tree2]

    def _test_sorting(self, results, collapse: bool = False, sort: bool = False):
        """Check ordering constraints for sorted quadripartition outputs."""
        for item in results:
            if isinstance(item[0], set):
                continue
            if collapse:
                if sort and item[0][0] > item[1][0]:
                    self.assertGreater(len(item[1]), len(item[0]))
            elif sort:
                self.assertGreater(item[0][1][0], item[0][0][0])

    def test_default(self):
        """Return default set-based quadripartitions."""
        results = list(iter_quadripartitions(self.tree1))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], set)
        self._test_sorting(results)

    def test_tuple(self):
        """Return tuple-based quadripartitions."""
        results = list(iter_quadripartitions(self.tree1, type=tuple))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], tuple)
        self._test_sorting(results)

    def test_list(self):
        """Return list-based quadripartitions."""
        results = list(iter_quadripartitions(self.tree1, type=list))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], list)
        self._test_sorting(results)

    def test_set_int_col(self):
        """Collapse set output while including internal nodes."""
        results = list(
            iter_quadripartitions(
                self.tree1,
                include_internal_nodes=True,
                collapse=True,
            )
        )
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results, collapse=True)

    def test_set_int_con_col(self):
        """Collapse contracted set output including internal nodes."""
        results = list(
            iter_quadripartitions(
                self.tree1,
                include_internal_nodes=True,
                contract_partitions=True,
                collapse=True,
            )
        )
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results, collapse=True)

    def test_list_sort_int_con_col(self):
        """Match sorted list output with internal+contracted collapse."""
        results = sorted(
            iter_quadripartitions(
                self.tree1,
                type=list,
                sort=True,
                include_internal_nodes=True,
                contract_partitions=True,
                collapse=True,
            )
        )
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results, collapse=True, sort=True)
        self.assertEqual(results, TREE1_LIST_SORT_INT_CON_COL)

    def test_list_sort_con(self):
        """Match sorted list output with contracted partitions."""
        results = sorted(
            iter_quadripartitions(
                self.tree1,
                type=list,
                sort=True,
                contract_partitions=True,
            )
        )
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], list)
        self._test_sorting(results, sort=True)
        self.assertEqual(results, TREE1_LIST_SORT_CON)

    def test_list_sort_con_col(self):
        """Match sorted collapsed list output with contracted partitions."""
        results = sorted(
            iter_quadripartitions(
                self.tree1,
                type=list,
                sort=True,
                contract_partitions=True,
                collapse=True,
            )
        )
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results, collapse=True, sort=True)
        self.assertEqual(results, TREE1_LIST_SORT_CON_COL)

    def test_list_int(self):
        """Return list output including internal nodes."""
        results = list(
            iter_quadripartitions(
                self.tree1,
                type=list,
                include_internal_nodes=True,
            )
        )
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], list)
        self._test_sorting(results)

    def test_list_sort_int_col(self):
        """Match sorted collapsed list output including internal nodes."""
        results = sorted(
            iter_quadripartitions(
                self.tree1,
                type=list,
                sort=True,
                include_internal_nodes=True,
                collapse=True,
            )
        )
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results, collapse=True, sort=True)
        self.assertEqual(results, TREE1_LIST_SORT_INT_COL)

    def test_set_int(self):
        """Return set output including internal nodes."""
        results = list(iter_quadripartitions(self.tree1, include_internal_nodes=True))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], set)
        self._test_sorting(results)

    def test_list_sort(self):
        """Match sorted list output on default partitions."""
        results = sorted(iter_quadripartitions(self.tree1, type=list, sort=True))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], list)
        self._test_sorting(results, sort=True)
        self.assertEqual(results, TREE1_LIST_SORT)

    def test_tuple_col(self):
        """Return collapsed tuple output."""
        results = list(iter_quadripartitions(self.tree1, type=tuple, collapse=True))
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results, collapse=True)

    def test_tuple_int(self):
        """Return tuple output including internal nodes."""
        results = list(
            iter_quadripartitions(
                self.tree1,
                type=tuple,
                include_internal_nodes=True,
            )
        )
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], tuple)
        self._test_sorting(results)

    def test_tuple_sort_int_col(self):
        """Match sorted tuple output including internal nodes and collapse."""
        results = sorted(
            iter_quadripartitions(
                self.tree1,
                type=tuple,
                sort=True,
                include_internal_nodes=True,
                collapse=True,
            )
        )
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results, collapse=True, sort=True)
        self.assertEqual(results, TREE1_TUPLE_SORT_INT_COL)

    def test_multifurcation_parent_side_pairings(self):
        """Include all parent-side clade pairings on multifurcations."""
        tree = toytree.tree("(((a,b,c)x,d,e)u,f,g)r;")
        results = sorted(
            iter_quadripartitions(
                tree,
                type=tuple,
                sort=True,
                collapse=True,
            )
        )
        self.assertEqual(len(results), 12)
        self.assertIn((("a",), ("b",), ("d",), ("e",)), results)
        self.assertIn((("a",), ("c",), ("d",), ("e",)), results)
        self.assertIn((("b",), ("c",), ("d",), ("e",)), results)

        uresults = sorted(
            iter_quadripartitions(
                tree.unroot(),
                type=tuple,
                sort=True,
                collapse=True,
            )
        )
        self.assertEqual(len(uresults), 12)
        self.assertIn((("a",), ("b",), ("d",), ("e",)), uresults)

    def test_quadripartitions_match_bruteforce_random_multifurcations(self):
        """Match brute-force edge-local counts on random multifurcating trees."""
        checked = 0
        for seed in range(12):
            rng = np.random.default_rng(seed)
            tree = toytree.rtree.unittree(12, seed=seed)
            internal = [node.idx for node in tree[tree.ntips : -1]]
            if len(internal) < 2:
                continue

            k = min(3, len(internal))
            chosen = rng.choice(internal, size=k, replace=False).tolist()
            mtree = tree.mod.collapse_nodes(*chosen)
            if all(len(node.children) <= 2 for node in mtree[mtree.ntips : -1]):
                continue

            for ttree in (mtree, mtree.unroot()):
                expected = _quadripartition_counter_bruteforce(ttree)
                observed = _quadripartition_counter_observed(ttree)
                self.assertEqual(observed, expected)

            checked += 1

        self.assertGreater(checked, 0)


