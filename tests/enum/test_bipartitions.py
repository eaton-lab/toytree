#!/usr/bin/env python

"""Test enumeration methods to find partitions in a tree.

- iter_bipartitions
- iter_quartets
"""

import unittest
import toytree
from toytree.enum import iter_bipartitions


class TestBipartitions(unittest.TestCase):
    def setUp(self):
        """Six tip tree three clades of two."""
        self.tree1 = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")
        self.tree2 = self.tree1.root("a")
        self.tree3 = self.tree1.root("a", "b")
        self.trees = [self.tree1, self.tree2, self.tree3]

    def test_iter_bipartitions_unrooted_sets(self):
        """Bipartitions (left, right) for each edge in tree."""
        biparts = sorted(iter_bipartitions(self.tree1))
        BIPARTS = [
            ({'c', 'd'}, {'a', 'b', 'e', 'f'}),
            ({'e', 'f'}, {'a', 'b', 'c', 'd'}),
            ({'c', 'd', 'e', 'f'}, {'a', 'b'}),
        ]
        self.assertEqual(biparts, BIPARTS)

        biparts = sorted(iter_bipartitions(self.tree1, sort=True))
        BIPARTS = [
            ({'c', 'd'}, {'a', 'b', 'e', 'f'}),
            ({'e', 'f'}, {'a', 'b', 'c', 'd'}),
            ({'a', 'b'}, {'c', 'd', 'e', 'f'}),
        ]
        self.assertEqual(biparts, BIPARTS)

        biparts = sorted(iter_bipartitions(self.tree1, sort=True))
        BIPARTS = [
            ({'c', 'd'}, {'a', 'b', 'e', 'f'}),
            ({'e', 'f'}, {'a', 'b', 'c', 'd'}),
            ({'a', 'b'}, {'c', 'd', 'e', 'f'}),
        ]
        self.assertEqual(biparts, BIPARTS)

        biparts = sorted(iter_bipartitions(self.tree1, include_internal_nodes=True))
        BIPARTS = [
            ({'CD', 'c', 'd'}, {'AB', 'EF', 'X', 'a', 'b', 'e', 'f'}),
            ({'EF', 'e', 'f'}, {'AB', 'CD', 'X', 'a', 'b', 'c', 'd'}),
            ({'CD', 'EF', 'X', 'c', 'd', 'e', 'f'}, {'AB', 'a', 'b'}),
        ]
        self.assertEqual(biparts, BIPARTS)

        biparts = sorted(iter_bipartitions(self.tree1, include_internal_nodes=True, sort=True))
        BIPARTS = [
            ({'CD', 'c', 'd'}, {'AB', 'EF', 'X', 'a', 'b', 'e', 'f'}),
            ({'EF', 'e', 'f'}, {'AB', 'CD', 'X', 'a', 'b', 'c', 'd'}),
            ({'AB', 'a', 'b'}, {'CD', 'EF', 'X', 'c', 'd', 'e', 'f'}),
        ]
        self.assertEqual(biparts, BIPARTS)

        biparts = sorted(iter_bipartitions(
            self.tree1, include_internal_nodes=True,
            include_singleton_partitions=True, sort=True))
        BIPARTS = [
            ({'a'}, {'AB', 'CD', 'EF', 'X', 'b', 'c', 'd', 'e', 'f'}),
            ({'b'}, {'AB', 'CD', 'EF', 'X', 'a', 'c', 'd', 'e', 'f'}),
            ({'c'}, {'AB', 'CD', 'EF', 'X', 'a', 'b', 'd', 'e', 'f'}),
            ({'d'}, {'AB', 'CD', 'EF', 'X', 'a', 'b', 'c', 'e', 'f'}),
            ({'e'}, {'AB', 'CD', 'EF', 'X', 'a', 'b', 'c', 'd', 'f'}),
            ({'f'}, {'AB', 'CD', 'EF', 'X', 'a', 'b', 'c', 'd', 'e'}),
            ({'CD', 'c', 'd'}, {'AB', 'EF', 'X', 'a', 'b', 'e', 'f'}),
            ({'EF', 'e', 'f'}, {'AB', 'CD', 'X', 'a', 'b', 'c', 'd'}),
            ({'AB', 'a', 'b'}, {'CD', 'EF', 'X', 'c', 'd', 'e', 'f'}),
        ]
        self.assertEqual(biparts, BIPARTS)

    def test_iter_bipartitions_unrooted_tuples(self):
        """Tuple partitions are always sorted within, but only optionally
        between partitions.
        """
        biparts = sorted(iter_bipartitions(self.tree1, type=tuple))
        BIPARTS = [
            (('c', 'd'), ('a', 'b', 'e', 'f')),
            (('c', 'd', 'e', 'f'), ('a', 'b')),
            (('e', 'f'), ('a', 'b', 'c', 'd')),
        ]
        self.assertEqual(biparts, BIPARTS)

        biparts = sorted(iter_bipartitions(self.tree1, sort=True, type=tuple))
        BIPARTS = [
            (('a', 'b'), ('c', 'd', 'e', 'f')),
            (('c', 'd'), ('a', 'b', 'e', 'f')),
            (('e', 'f'), ('a', 'b', 'c', 'd')),
        ]
        self.assertEqual(biparts, BIPARTS)

        biparts = sorted(iter_bipartitions(self.tree1, type=tuple, include_internal_nodes=True))
        BIPARTS = [
            (('c', 'd', 'CD'), ('a', 'b', 'e', 'f', 'EF', 'X', 'AB')),
            (('c', 'd', 'CD', 'e', 'f', 'EF', 'X'), ('a', 'b', 'AB')),
            (('e', 'f', 'EF'), ('a', 'b', 'c', 'd', 'CD', 'X', 'AB'))]
        self.assertEqual(biparts, BIPARTS)

        biparts = sorted(iter_bipartitions(self.tree1, type=tuple, include_internal_nodes=True, sort=True))
        BIPARTS = [
            (('a', 'b', 'AB'), ('c', 'd', 'CD', 'e', 'f', 'EF', 'X')),
            (('c', 'd', 'CD'), ('a', 'b', 'e', 'f', 'EF', 'X', 'AB')),
            (('e', 'f', 'EF'), ('a', 'b', 'c', 'd', 'CD', 'X', 'AB')),
        ]
        self.assertEqual(biparts, BIPARTS)

        biparts = sorted(iter_bipartitions(
            self.tree1, type=tuple, include_internal_nodes=True,
            include_singleton_partitions=True, sort=True))
        BIPARTS = [
            (('a',), ('b', 'c', 'd', 'CD', 'e', 'f', 'EF', 'X', 'AB')),
            (('a', 'b', 'AB'), ('c', 'd', 'CD', 'e', 'f', 'EF', 'X')),
            (('b',), ('a', 'c', 'd', 'CD', 'e', 'f', 'EF', 'X', 'AB')),
            (('c',), ('a', 'b', 'd', 'CD', 'e', 'f', 'EF', 'X', 'AB')),
            (('c', 'd', 'CD'), ('a', 'b', 'e', 'f', 'EF', 'X', 'AB')),
            (('d',), ('a', 'b', 'c', 'CD', 'e', 'f', 'EF', 'X', 'AB')),
            (('e',), ('a', 'b', 'c', 'd', 'CD', 'f', 'EF', 'X', 'AB')),
            (('e', 'f', 'EF'), ('a', 'b', 'c', 'd', 'CD', 'X', 'AB')),
            (('f',), ('a', 'b', 'c', 'd', 'CD', 'e', 'EF', 'X', 'AB'))]
        self.assertEqual(biparts, BIPARTS)

    def test_iter_bipartitions_root_equality(self):
        b1 = set(self.tree1.iter_bipartitions(type=tuple))
        b2 = set(self.tree2.iter_bipartitions(type=tuple))
        b3 = set(self.tree3.iter_bipartitions(type=tuple))
        self.assertEqual(b1, b2)
        self.assertEqual(b2, b3)


if __name__ == "__main__":

    unittest.main()
