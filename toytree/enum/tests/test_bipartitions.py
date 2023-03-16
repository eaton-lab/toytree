#!/usr/bin/env python

"""Test enumeration methods to find partitions in a tree.

- iter_bipartitions
- iter_quartets
"""

import unittest
import toytree
from toytree.utils import ToytreeError
from toytree.enum.src.partitions import (
    iter_bipartitions,
    iter_quartets,
)


class TestBipartitions(unittest.TestCase):
    def setUp(self):
        """Six tip tree three clades of two."""
        self.tree1 = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")
        self.tree2 = self.tree1.root("a")
        self.tree3 = self.tree1.root("a", "b")
        self.trees = [self.tree1, self.tree2, self.tree3]

    def test_iter_bipartitions_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.tree1.iter_bipartitions.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.enum.iter_bipartitions.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_iter_quartets_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.tree1.iter_quartets.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.enum.iter_quartets.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_iter_bipartitions_unrooted(self):
        """Bipartitions (left, right) for each edge in tree."""
        biparts = sorted(iter_bipartitions(self.tree1))
        BIPARTS = [
            (('a', 'b'), ('c', 'd', 'e', 'f')),
            (('c', 'd'), ('a', 'b', 'e', 'f')),
            (('e', 'f'), ('a', 'b', 'c', 'd')),
        ]
        self.assertEqual(biparts, BIPARTS)

        # on unrooted tree indicate_root should have no effect.
        biparts = sorted(iter_bipartitions(self.tree1, indicate_root=True))
        self.assertEqual(biparts, BIPARTS)

    def test_iter_bipartitions_rooted_single(self):
        """Bipartitions (left, right) for each edge in tree."""
        biparts = sorted(iter_bipartitions(self.tree2))
        BIPARTS = [
            (('a', 'b'), ('c', 'd', 'e', 'f')),
            (('c', 'd'), ('a', 'b', 'e', 'f')),
            (('e', 'f'), ('a', 'b', 'c', 'd')),
        ]
        self.assertEqual(biparts, BIPARTS)

        # on rooted tree indicate_root adds one additional split.
        biparts = sorted(iter_bipartitions(self.tree2, indicate_root=True))
        extra = [(('a',), ('b', 'c', 'd', 'e', 'f'))]
        self.assertEqual(biparts, extra + BIPARTS)

    def test_iter_bipartitions_rooted_clade(self):
        """Bipartitions (left, right) for each edge in tree."""
        biparts = sorted(iter_bipartitions(self.tree3))
        BIPARTS = [
            (('a', 'b'), ('c', 'd', 'e', 'f')),
            (('c', 'd'), ('a', 'b', 'e', 'f')),
            (('e', 'f'), ('a', 'b', 'c', 'd')),
        ]
        self.assertEqual(biparts, BIPARTS)

        # on rooted tree indicate_root adds one additional split.
        biparts = sorted(iter_bipartitions(self.tree3, indicate_root=True))
        extra = [(('a', 'b'), ('c', 'd', 'e', 'f'))]
        self.assertEqual(biparts, extra + BIPARTS)

    def test_iter_bipartitions_unrooted_w_internal_nodes(self):
        """Bipartitions (left, right) for each edge in tree."""
        biparts = sorted(iter_bipartitions(self.tree1, include_internal_nodes=True))
        BIPARTS = [
            (('a', 'b', 'AB'), ('c', 'd', 'CD', 'e', 'f', 'EF', 'X')),
            (('c', 'd', 'CD'), ('a', 'b', 'e', 'f', 'EF', 'X', 'AB')),
            (('e', 'f', 'EF'), ('a', 'b', 'c', 'd', 'CD', 'X', 'AB')),
        ]
        self.assertEqual(biparts, BIPARTS)

        # on unrooted tree indicate_root should have no effect.
        biparts = sorted(iter_bipartitions(self.tree1, include_internal_nodes=True, indicate_root=True))
        self.assertEqual(biparts, BIPARTS)

    def test_iter_bipartitions_rooted_single_w_internal_nodes(self):
        """Bipartitions (left, right) for each edge in tree."""
        biparts = sorted(iter_bipartitions(self.tree2, include_internal_nodes=True))
        BIPARTS = [
            (('a', 'b', 'AB'), ('c', 'd', 'CD', 'e', 'f', 'EF', 'X')),
            (('c', 'd', 'CD'), ('a', 'b', 'e', 'f', 'EF', 'X', 'AB')),
            (('e', 'f', 'EF'), ('a', 'b', 'c', 'd', 'CD', 'X', 'AB')),
        ]
        self.assertEqual(biparts, BIPARTS)

        # on unrooted tree indicate_root should have no effect.
        biparts = sorted(iter_bipartitions(self.tree2, include_internal_nodes=True, indicate_root=True))
        extra = [(('a',), ('b', 'c', 'd', 'CD', 'e', 'f', 'EF', 'X', 'AB'))]
        self.assertEqual(biparts, extra + BIPARTS)

    def test_iter_bipartitions_rooted_clade_w_internal_nodes(self):
        """Bipartitions (left, right) for each edge in tree.

        Note that the sorting of internal Node names is different here
        than it was in tree2. This is why auto-generated internal node
        names used for sorting does not create consistent ordering.
        This is also why we do not include internal nodes when creating
        bipartitions for tree comparisons. Note that if two trees did
        have names for all internal Nodes then we could create a consistent
        ordering, but that is very rarely the case.
        """
        biparts = sorted(iter_bipartitions(self.tree3, include_internal_nodes=True))
        BIPARTS = [
            (('a', 'b', 'AB'), ('c', 'd', 'CD', 'e', 'f', 'EF', 'X')),
            (('c', 'd', 'CD'), ('a', 'b', 'AB', 'e', 'f', 'EF', 'X')),
            (('e', 'f', 'EF'), ('a', 'b', 'AB', 'c', 'd', 'CD', 'X')),
        ]
        self.assertEqual(biparts, BIPARTS)

        # on unrooted tree indicate_root should have no effect.
        biparts = sorted(iter_bipartitions(self.tree3, include_internal_nodes=True, indicate_root=True))
        extra = [(('a', 'b', 'AB'), ('c', 'd', 'CD', 'e', 'f', 'EF', 'X'))]
        self.assertEqual(biparts, extra + BIPARTS)

    def test_iter_quartets(self):
        """Bipartitions (left, right) for each edge in tree."""
        QRTS = [
            (('a', 'b'), ('c', 'd')),
            (('a', 'b'), ('c', 'e')),
            (('a', 'b'), ('c', 'f')),
            (('a', 'b'), ('d', 'e')),
            (('a', 'b'), ('d', 'f')),
            (('a', 'b'), ('e', 'f')),
            (('a', 'c'), ('e', 'f')),
            (('a', 'd'), ('e', 'f')),
            (('a', 'e'), ('c', 'd')),
            (('a', 'f'), ('c', 'd')),
            (('b', 'c'), ('e', 'f')),
            (('b', 'd'), ('e', 'f')),
            (('b', 'e'), ('c', 'd')),
            (('b', 'f'), ('c', 'd')),
            (('c', 'd'), ('e', 'f')),
        ]
        for tree in self.trees:
            quartets = sorted(iter_quartets(tree))
            self.assertEqual(quartets, QRTS)


if __name__ == "__main__":

    unittest.main()
