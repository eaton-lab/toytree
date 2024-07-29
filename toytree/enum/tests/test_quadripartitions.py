#!/usr/bin/env python

"""Test enumeration methods to find partitions in a tree.

args:
feature, 
contract_partitions, (True, False) "con"
include_internal_nodes, (True, False) "int"
collapse, (True, False) "col"
type, (set, list, tuple)
sort (True, False)

possible combinations of arguments:

2*2*2*2*3 = 48

test_set (default)
    test_set_sort
            test_set_sort_int
                test_set_sort_int_con
                    test_set_sort_int_con_col
                test_set_sort_con
                    test_set_sort_con_col
            test_set_int
                test_set_int_con
                    test_set_int_con_col
        
etc.

These tests pick a subset of 16 possible combinations picked at random
(first three test defaults of each major type)
*reproducable tests will be checked for exact content

test_default (set)
test_tuple 
test_list
test_set_int_col
test_set_int_con_col
test_list_sort_int_con_col*
test_list_sort_con*
test_list_sort_con_col*
test_list_int
test_list_sort_int_col*
test_set_int
test_list_sort*
test_tuple_col
test_tuple_int
test_set_int_col
test_tuple_sort_int_col*


"""

import unittest
import toytree
# from toytree.utils import ToytreeError
from toytree.enum import iter_quadripartitions, _iter_quadripartition_sets


class TestQuartets(unittest.TestCase):
    def setUp(self):
        """Setting up test trees: 
        tree1: Six tip tree three clades of two.
        tree2: random six tip tree from seed for reproduceability
        tree3: list of tree1 and tree2"""
        self.tree1 = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")
        self.tree2 = toytree.rtree.unittree(6, seed=123, random_names=True)
        self.trees = [self.tree1, self.tree2]

    def _test_sorting(self, results, collapse: bool = False, sort: bool = False):
        """Helper function to test sorting of quartets.
        Tests both the automatic sorting method on the tip-level pairs
        and the sort= argument at the quartet-level"""
        for item in results: 
            if not isinstance(item[0], set):
                if collapse:
                    if sort:
                        if item[0][0] > item[1][0]:  #if the first node of each collection is out of order, then make sure it is in length order
                            self.assertGreater(len(item[1]), len(item[0]))  
                
                else:
                    if sort: 
                        self.assertGreater(item[0][1][0], item[0][0][0])  #quartet-level sorting (x,y),(i,j) -> (i,j),(x,y)


    def test_default(self):
        results = list(iter_quadripartitions(self.tree1))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], set)
        self._test_sorting(results)
    def test_tuple(self):
        results = list(iter_quadripartitions(self.tree1, type=tuple))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], tuple)
        self._test_sorting(results)
    def test_list(self):
        results = list(iter_quadripartitions(self.tree1, type=list))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], list)
        self._test_sorting(results)
    def test_set_int_col(self):
        results = list(iter_quadripartitions(self.tree1, include_internal_nodes=True, collapse=True))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], set)
        self._test_sorting(results, collapse=True)
    def test_set_int_con_col(self):
        results = list(iter_quadripartitions(self.tree1, include_internal_nodes=True, contract_partitions=True, collapse=True))
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results, collapse=True)
    def test_list_sort_int_con_col(self):
        results = sorted(iter_quadripartitions(self.tree1, type=list, sort=True, include_internal_nodes=True, contract_partitions=True, collapse=True))
        RESULTS = [(['CD'], ['EF'], ['a'], ['b']), (['CD'], ['X'], ['e'], ['f']), (['EF'], ['X'], ['c'], ['d'])]
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results, collapse=True, sort=True)
        self.assertEqual(results, RESULTS)
        self._test_sorting(results, collapse=True, sort=True)
    def test_list_sort_con(self):
        results = sorted(iter_quadripartitions(self.tree1, type=list, sort=True, contract_partitions=True))
        RESULTS = [((['CD'], ['EF']), (['a'], ['b'])), ((['CD'], ['X']), (['e'], ['f'])), ((['EF'], ['X']), (['c'], ['d']))]
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], list)
        self._test_sorting(results, sort=True)
        self.assertEqual(results,RESULTS)
    def test_list_sort_con_col(self):
        results = sorted(iter_quadripartitions(self.tree1, type=list, sort=True, contract_partitions=True, collapse=True))
        RESULTS = [(['CD'], ['EF'], ['a'], ['b']), (['CD'], ['X'], ['e'], ['f']), (['EF'], ['X'], ['c'], ['d'])]
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results, collapse=True, sort=True)
        self.assertEqual(results,RESULTS)
    def test_list_int(self):
        results = list(iter_quadripartitions(self.tree1, type=list, include_internal_nodes=True))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], list)
        self._test_sorting(results)
    def test_list_sort_int_col(self):
        results = sorted(iter_quadripartitions(self.tree1, type=list, sort=True, include_internal_nodes=True, collapse=True))
        RESULTS = [(['a'], ['b'], ['c', 'd', 'CD'], ['e', 'f', 'EF']), (['c'], ['d'], ['a', 'b'], ['e', 'f', 'EF']), (['e'], ['f'], ['a', 'b'], ['c', 'd', 'CD'])]
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results, collapse=True, sort=True)
        self.assertEqual(results,RESULTS)
    def test_set_int(self):
        results = list(iter_quadripartitions(self.tree1, include_internal_nodes=True))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], set)
        self._test_sorting(results)
    def test_list_sort(self):
        results = sorted(iter_quadripartitions(self.tree1, type=list, sort=True))
        RESULTS = [((['a'], ['b']), (['c', 'd'], ['e', 'f'])), ((['c'], ['d']), (['a', 'b'], ['e', 'f'])), ((['e'], ['f']), (['a', 'b'], ['c', 'd']))]
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], list)
        self._test_sorting(results, sort=True)
        self.assertEqual(results,RESULTS)
    def test_tuple_col(self):
        results = list(iter_quadripartitions(self.tree1, type=tuple, collapse=True))
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results, collapse=True)
    def test_tuple_int(self):
        results = list(iter_quadripartitions(self.tree1, type=tuple, include_internal_nodes=True))
        self.assertIsInstance(results[0][0], tuple)
        self.assertIsInstance(results[0][0][0], tuple)
        self._test_sorting(results)
    def test_set_int_col(self):
        results = list(iter_quadripartitions(self.tree1, include_internal_nodes=True, collapse=True))
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results, collapse=True)
    def test_tuple_sort_int_col(self):
        results = sorted(iter_quadripartitions(self.tree1, type=tuple, sort=True, include_internal_nodes=True, collapse=True))
        RESULTS = [(('a',), ('b',), ('c', 'd', 'CD'), ('e', 'f', 'EF')), (('c',), ('d',), ('a', 'b'), ('e', 'f', 'EF')), (('e',), ('f',), ('a', 'b'), ('c', 'd', 'CD'))]
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results, collapse=True, sort=True)
        self.assertEqual(results, RESULTS)


if __name__ == "__main__":

    unittest.main()
