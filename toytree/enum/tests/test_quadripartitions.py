#!/usr/bin/env python

"""Test enumeration methods to find partitions in a tree.

"""

import unittest
import toytree
from toytree.utils import ToytreeError
from toytree.enum.src.partitions import (
    iter_quadripartitions,
    iter_edge_quadripartition_sets,
)


class TestBipartitions(unittest.TestCase):
    def setUp(self):
        """Six tip tree three clades of two."""
        self.tree1 = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")
        self.tree2 = self.tree1.root("a")
        self.tree3 = self.tree1.root("a", "b")
        self.trees = [self.tree1, self.tree2, self.tree3]

    def test_iter_quadripartitions_sets1(self):
        """Quadripartitions """
        PARTS = [
            (({'c'}, {'d'}), ({'e', 'f'}, {'a', 'b'})),
            (({'e'}, {'f'}), ({'c', 'd'}, {'a', 'b'})),
            (({'c', 'd'}, {'e', 'f'}), ({'a'}, {'b'})),
        ]
        parts = sorted(iter_edge_quadripartition_sets(self.tree1))
        self.assertEqual(parts, PARTS)

        PARTS = [
            (({'c'}, {'d'}), ({'EF', 'f', 'e'}, {'AB', 'b', 'a'})),
            (({'e'}, {'f'}), ({'c', 'd', 'CD'}, {'AB', 'b', 'a'})),
            (({'c', 'd', 'CD'}, {'EF', 'f', 'e'}), ({'a'}, {'b'})),
        ]
        parts = sorted(iter_edge_quadripartition_sets(self.tree1, include_internal_nodes=True))
        self.assertEqual(parts, PARTS)

        PARTS = [
            (({'c'}, {'d'}), ({'EF'}, {'AB'})),
            (({'e'}, {'f'}), ({'CD'}, {'AB'})),
            (({'CD'}, {'EF'}), ({'a'}, {'b'})),
        ]
        parts = sorted(iter_edge_quadripartition_sets(self.tree1, contract_partitions=True))
        self.assertEqual(parts, PARTS)

    def test_iter_quadripartitions_sets2(self):
        """Quadripartitions """
        PARTS = [
            (({'c'}, {'d'}), ({'f', 'e'}, {'a', 'b'})),
            (({'e'}, {'f'}), ({'c', 'd'}, {'a', 'b'})),
            (({'c', 'd'}, {'f', 'e'}), ({'b'}, {'a'})),
        ]
        parts = sorted(iter_edge_quadripartition_sets(self.tree2))
        self.assertEqual(parts, PARTS)

        PARTS = [
            (({'c'}, {'d'}), ({'f', 'e', 'EF'}, {'AB', 'b', 'a'})),
            (({'e'}, {'f'}), ({'c', 'd', 'CD'}, {'AB', 'b', 'a'})),
            (({'c', 'd', 'CD'}, {'f', 'e', 'EF'}), ({'b'}, {'a'})),
        ]
        parts = sorted(iter_edge_quadripartition_sets(self.tree2, include_internal_nodes=True))
        self.assertEqual(parts, PARTS)

        PARTS = [
            (({'c'}, {'d'}), ({'EF'}, {'AB'})),
            (({'e'}, {'f'}), ({'CD'}, {'AB'})),
            (({'CD'}, {'EF'}), ({'b'}, {'a'})),
        ]
        parts = sorted(iter_edge_quadripartition_sets(self.tree2, contract_partitions=True))
        self.assertEqual(parts, PARTS)

    def test_iter_quadripartitions_sets3(self):
        """Quadripartitions """
        PARTS = [
            (({'c'}, {'d'}), ({'f', 'e'}, {'a', 'b'})),
            (({'e'}, {'f'}), ({'d', 'c'}, {'a', 'b'})),
            (({'a'}, {'b'}), ({'d', 'c'}, {'f', 'e'})),
        ]
        parts = sorted(iter_edge_quadripartition_sets(self.tree3))
        self.assertEqual(parts, PARTS)

        PARTS = [
            (({'c'}, {'d'}), ({'f', 'e', 'EF'}, {'AB', 'a', 'b'})),
            (({'e'}, {'f'}), ({'CD', 'd', 'c'}, {'AB', 'a', 'b'})),
            (({'a'}, {'b'}), ({'CD', 'd', 'c'}, {'f', 'e', 'EF'})),
        ]
        parts = sorted(iter_edge_quadripartition_sets(self.tree3, include_internal_nodes=True))
        self.assertEqual(parts, PARTS)

        PARTS = [
            (({'c'}, {'d'}), ({'EF'}, {'AB'})),
            (({'e'}, {'f'}), ({'CD'}, {'AB'})),
            (({'a'}, {'b'}), ({'CD'}, {'EF'})),
        ]
        parts = sorted(iter_edge_quadripartition_sets(self.tree3, contract_partitions=True))
        self.assertEqual(parts, PARTS)

    def test_iter_quadripartitions_unrooted(self):
        """Quadripartitions """
        for tree in self.trees:
            parts = sorted(iter_quadripartitions(tree))
            PARTS = [
                (('a', 'b'), ('c', 'e')),
                (('a', 'b'), ('c', 'f')),
                (('a', 'b'), ('d', 'e')),
                (('a', 'b'), ('d', 'f')),
                (('a', 'c'), ('e', 'f')),
                (('a', 'd'), ('e', 'f')),
                (('a', 'e'), ('c', 'd')),
                (('a', 'f'), ('c', 'd')),
                (('b', 'c'), ('e', 'f')),
                (('b', 'd'), ('e', 'f')),
                (('b', 'e'), ('c', 'd')),
                (('b', 'f'), ('c', 'd')),
            ]
            self.assertEqual(parts, PARTS)


if __name__ == "__main__":

    unittest.main()
