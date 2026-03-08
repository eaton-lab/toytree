#!/usr/bin/env python

"""Tests for quartet enumeration."""

from __future__ import annotations


import toytree
from toytree.enum import _iter_unresolved_quartet_sets, iter_quartets

TREE1_NEWICK = "(a,b,((c,d)CD,(e,f)EF)X)AB;"
TREE2_NEWICK = "((r0,(r3,r2)),(r1,(r4,r5)));"
TREE2_TOPOLOGY_ID = "396253e6e05ca57b9bacf9b82384ff79"

TREE2_TUPLE_SORT = [
    (("r0", "r1"), ("r2", "r3")),
    (("r0", "r1"), ("r4", "r5")),
    (("r0", "r2"), ("r1", "r4")),
    (("r0", "r2"), ("r1", "r5")),
    (("r0", "r2"), ("r4", "r5")),
    (("r0", "r3"), ("r1", "r4")),
    (("r0", "r3"), ("r1", "r5")),
    (("r0", "r3"), ("r4", "r5")),
    (("r0", "r4"), ("r2", "r3")),
    (("r0", "r5"), ("r2", "r3")),
    (("r1", "r2"), ("r4", "r5")),
    (("r1", "r3"), ("r4", "r5")),
    (("r1", "r4"), ("r2", "r3")),
    (("r1", "r5"), ("r2", "r3")),
    (("r2", "r3"), ("r4", "r5")),
]

TREE2_TUPLE_SORT_COLLAPSE_QUAD = [
    ("r0", "r1", "r2", "r3"),
    ("r0", "r1", "r4", "r5"),
    ("r0", "r2", "r1", "r4"),
    ("r0", "r2", "r1", "r5"),
    ("r0", "r3", "r1", "r4"),
    ("r0", "r3", "r1", "r5"),
    ("r0", "r4", "r2", "r3"),
    ("r0", "r5", "r2", "r3"),
    ("r1", "r2", "r4", "r5"),
    ("r1", "r3", "r4", "r5"),
]

TREE2_LIST_SORT = [
    (["r0", "r1"], ["r2", "r3"]),
    (["r0", "r1"], ["r4", "r5"]),
    (["r0", "r2"], ["r1", "r4"]),
    (["r0", "r2"], ["r1", "r5"]),
    (["r0", "r2"], ["r4", "r5"]),
    (["r0", "r3"], ["r1", "r4"]),
    (["r0", "r3"], ["r1", "r5"]),
    (["r0", "r3"], ["r4", "r5"]),
    (["r0", "r4"], ["r2", "r3"]),
    (["r0", "r5"], ["r2", "r3"]),
    (["r1", "r2"], ["r4", "r5"]),
    (["r1", "r3"], ["r4", "r5"]),
    (["r1", "r4"], ["r2", "r3"]),
    (["r1", "r5"], ["r2", "r3"]),
    (["r2", "r3"], ["r4", "r5"]),
]

TREE2_LIST_SORT_COLLAPSE = [
    ["r0", "r1", "r2", "r3"],
    ["r0", "r1", "r4", "r5"],
    ["r0", "r2", "r1", "r4"],
    ["r0", "r2", "r1", "r5"],
    ["r0", "r2", "r4", "r5"],
    ["r0", "r3", "r1", "r4"],
    ["r0", "r3", "r1", "r5"],
    ["r0", "r3", "r4", "r5"],
    ["r0", "r4", "r2", "r3"],
    ["r0", "r5", "r2", "r3"],
    ["r1", "r2", "r4", "r5"],
    ["r1", "r3", "r4", "r5"],
    ["r1", "r4", "r2", "r3"],
    ["r1", "r5", "r2", "r3"],
    ["r2", "r3", "r4", "r5"],
]

TREE1_UNRESOLVED = [
    {"a", "b", "c", "d"},
    {"a", "b", "c", "e"},
    {"a", "b", "c", "f"},
    {"a", "b", "d", "e"},
    {"a", "b", "d", "f"},
    {"a", "b", "e", "f"},
    {"a", "c", "d", "e"},
    {"a", "c", "d", "f"},
    {"a", "c", "e", "f"},
    {"a", "d", "e", "f"},
    {"b", "c", "d", "e"},
    {"b", "c", "d", "f"},
    {"b", "c", "e", "f"},
    {"b", "d", "e", "f"},
    {"c", "d", "e", "f"},
]



from conftest import PytestCompat

class TestQuartets(PytestCompat):
    """Validate quartet enumeration options and output ordering."""

    def setUp(self):
        """Create shared tree fixtures for quartet tests."""
        self.tree1 = toytree.tree(TREE1_NEWICK)
        self.tree2 = toytree.tree(TREE2_NEWICK)
        self.trees = [self.tree1, self.tree2]

    def _test_sorting(self, results, collapse: bool = False, sort: bool = False):
        """Check ordering constraints in quartet outputs."""
        for item in results:
            if isinstance(item[0], set):
                continue

            if collapse:
                if sort:
                    self.assertGreater(item[2], item[0])
                self.assertGreater(item[1], item[0])
                self.assertGreater(item[3], item[2])
                continue

            if sort:
                self.assertGreater(item[1][0], item[0][0])
            for collection in item:
                self.assertGreater(collection[1], collection[0])

    def test_default(self):
        """Return default set-based quartets."""
        results = list(iter_quartets(self.tree1))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results)

    def test_tree2_fixture_topology(self):
        """Guard the fixed topology used in exact-output fixture tests."""
        self.assertEqual(self.tree2.get_topology_id(), TREE2_TOPOLOGY_ID)

    def test_set_sort(self):
        """Return set-based quartets with split-level sorting."""
        results = list(iter_quartets(self.tree1, sort=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results, sort=True)

    def test_set_sort_quad(self):
        """Return set quartets from quadripartitions with sorting."""
        results = list(iter_quartets(self.tree1, sort=True, quadripartitions=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results, sort=True)

    def test_set_quad(self):
        """Return set quartets induced by quadripartitions."""
        results = list(iter_quartets(self.tree1, quadripartitions=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results)

    def test_tuple(self):
        """Return tuple-based quartets."""
        results = list(iter_quartets(self.tree1, type=tuple))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results)

    def test_tuple_sort(self):
        """Match sorted tuple quartets on fixed tree fixture."""
        results = list(iter_quartets(self.tree1, type=tuple, sort=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results, sort=True)
        parts = sorted(iter_quartets(self.tree2, type=tuple, sort=True))
        self.assertEqual(parts, TREE2_TUPLE_SORT)

    def test_tuple_sort_collapse(self):
        """Return collapsed tuple quartets with sorting."""
        results = list(iter_quartets(self.tree1, type=tuple, sort=True, collapse=True))
        self._test_sorting(results, collapse=True, sort=True)

    def test_tuple_sort_collapse_quad(self):
        """Match collapsed tuple quartets from sorted quadripartitions."""
        results = list(
            iter_quartets(
                self.tree1,
                type=tuple,
                sort=True,
                collapse=True,
                quadripartitions=True,
            )
        )
        self.assertIsInstance(results[0], tuple)
        self._test_sorting(results, collapse=True, sort=True)
        parts = sorted(
            iter_quartets(
                self.tree2,
                type=tuple,
                sort=True,
                collapse=True,
                quadripartitions=True,
            )
        )
        self.assertEqual(parts, TREE2_TUPLE_SORT_COLLAPSE_QUAD)

    def test_tuple_sort_quad(self):
        """Return tuple quartets from quadripartitions with sorting."""
        results = list(
            iter_quartets(
                self.tree1,
                type=tuple,
                sort=True,
                quadripartitions=True,
            )
        )
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results, sort=True)

    def test_tuple_collapse(self):
        """Return collapsed tuple quartets."""
        results = list(iter_quartets(self.tree1, type=tuple, collapse=True))
        self.assertIsInstance(results[0], tuple)
        self._test_sorting(results, collapse=True)

    def test_tuple_collapse_quad(self):
        """Return collapsed tuple quartets from quadripartitions."""
        results = list(
            iter_quartets(
                self.tree1,
                type=tuple,
                collapse=True,
                quadripartitions=True,
            )
        )
        self.assertIsInstance(results[0], tuple)
        self._test_sorting(results, collapse=True)

    def test_tuple_quad(self):
        """Return tuple quartets induced by quadripartitions."""
        results = list(iter_quartets(self.tree1, type=tuple, quadripartitions=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results)

    def test_list(self):
        """Return list-based quartets."""
        results = list(iter_quartets(self.tree1, type=list))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results)

    def test_list_sort(self):
        """Match sorted list quartets on fixed tree fixture."""
        results = list(iter_quartets(self.tree1, type=list, sort=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results, sort=True)
        parts = sorted(iter_quartets(self.tree2, type=list, sort=True))
        self.assertEqual(parts, TREE2_LIST_SORT)

    def test_list_sort_collapse(self):
        """Match sorted collapsed list quartets on fixed tree fixture."""
        results = list(iter_quartets(self.tree1, type=list, sort=True, collapse=True))
        parts = sorted(iter_quartets(self.tree2, type=list, sort=True, collapse=True))
        self.assertIsInstance(results[0], list)
        self._test_sorting(results, collapse=True, sort=True)
        self.assertEqual(parts, TREE2_LIST_SORT_COLLAPSE)

    def test_list_sort_collapse_quad(self):
        """Return sorted collapsed list quartets from quadripartitions."""
        results = list(
            iter_quartets(
                self.tree1,
                type=list,
                sort=True,
                collapse=True,
                quadripartitions=True,
            )
        )
        self.assertIsInstance(results[0], list)
        self._test_sorting(results, sort=True, collapse=True)

    def test_list_sort_quad(self):
        """Return sorted list quartets from quadripartitions."""
        results = list(
            iter_quartets(
                self.tree1,
                type=list,
                sort=True,
                quadripartitions=True,
            )
        )
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results, sort=True)

    def test_list_collapse(self):
        """Return collapsed list quartets."""
        results = list(iter_quartets(self.tree1, type=list, collapse=True))
        self.assertIsInstance(results[0], list)
        self._test_sorting(results, collapse=True)

    def test_list_collapse_quad(self):
        """Return collapsed list quartets from quadripartitions."""
        results = list(
            iter_quartets(
                self.tree1,
                type=list,
                collapse=True,
                quadripartitions=True,
            )
        )
        self.assertIsInstance(results[0], list)
        self._test_sorting(results, collapse=True)

    def test_list_quad(self):
        """Return list quartets induced by quadripartitions."""
        results = list(iter_quartets(self.tree1, type=list, quadripartitions=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results)

    def test_quadripartitions_multifurcation_completeness(self):
        """Include multifurcation parent-side quartets via quadripartitions mode."""
        tree = toytree.tree("(((a,b,c)x,d,e)u,f,g)r;")
        results = set(iter_quartets(tree, type=tuple, sort=True, quadripartitions=True))
        self.assertEqual(len(results), 22)
        self.assertIn((("a", "b"), ("d", "e")), results)
        self.assertIn((("a", "c"), ("d", "e")), results)
        self.assertIn((("b", "c"), ("d", "e")), results)

    def test_iter_unresolved_quartet_sets(self):
        """Return all unresolved 4-tip combinations by feature."""
        parts = list(_iter_unresolved_quartet_sets(self.tree1, feature="name"))
        self.assertEqual(parts, TREE1_UNRESOLVED)


