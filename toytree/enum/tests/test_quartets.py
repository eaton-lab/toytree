
"""Test enumeration methods to find partitions in a tree.

- iter_bipartitions
- iter_quartets
"""


import unittest
import toytree
from toytree.enum import _iter_unresolved_quartet_sets, _iter_quartet_sets, iter_quartets


class TestQuartets(unittest.TestCase):
    def setUp(self):
        """Six tip tree three clades of two."""
        self.tree1 = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")
        self.tree2 = toytree.rtree.unittree(6, seed=123, random_names=True)
        self.trees = [self.tree1, self.tree2]
    def test_iter_quartet_sets(self):
        #feature = 'name', quadripartitions = True
        QUADRIPARTITION_PARTS = [('c', 'd', 'e', 'a'),
                            ('c', 'd', 'e', 'b'),
                            ('c', 'd', 'f', 'a'),
                            ('c', 'd', 'f', 'b'),
                            ('c', 'e', 'a', 'b'),
                            ('c', 'f', 'a', 'b'),
                            ('d', 'e', 'a', 'b'),
                            ('d', 'f', 'a', 'b'),
                            ('e', 'f', 'c', 'a'),
                            ('e', 'f', 'c', 'b'),
                            ('e', 'f', 'd', 'a'),
                            ('e', 'f', 'd', 'b')]
        quadripartition_parts = sorted(_iter_quartet_sets(self.tree1, feature = 'name', quadripartitions = True))
        self.assertEqual(quadripartition_parts, QUADRIPARTITION_PARTS)
    def test_iter_unresolved_quartet_sets(self):
        #feature = 'name'
        PARTS = [{'a', 'b', 'c', 'd'},
                {'a', 'b', 'c', 'e'},
                {'a', 'b', 'c', 'f'},
                {'a', 'b', 'd', 'e'},
                {'a', 'b', 'd', 'f'},
                {'a', 'b', 'e', 'f'},
                {'a', 'c', 'd', 'e'},
                {'a', 'c', 'd', 'f'},
                {'a', 'c', 'e', 'f'},
                {'a', 'd', 'e', 'f'},
                {'b', 'c', 'd', 'e'},
                {'b', 'c', 'd', 'f'},
                {'b', 'c', 'e', 'f'},
                {'b', 'd', 'e', 'f'},
                {'c', 'd', 'e', 'f'}]
        parts = list(_iter_unresolved_quartet_sets(self.tree1, feature = 'name'))
        self.assertEqual(parts, PARTS)
    def test_iter_quartets(self):
        """Quartets"""
        #type=tuple, collapse=False, sort=True
        PARTS = [(('r0', 'r1'), ('r2', 'r3')), 
                  (('r0', 'r1'), ('r2', 'r4')), 
                  (('r0', 'r1'), ('r2', 'r5')), 
                  (('r0', 'r1'), ('r3', 'r4')), 
                  (('r0', 'r1'), ('r3', 'r5')), 
                  (('r0', 'r1'), ('r4', 'r5')), 
                  (('r0', 'r2'), ('r4', 'r5')), 
                  (('r0', 'r3'), ('r4', 'r5')), 
                  (('r0', 'r4'), ('r2', 'r3')), 
                  (('r0', 'r5'), ('r2', 'r3')), 
                  (('r1', 'r2'), ('r4', 'r5')), 
                  (('r1', 'r3'), ('r4', 'r5')), 
                  (('r1', 'r4'), ('r2', 'r3')), 
                  (('r1', 'r5'), ('r2', 'r3')), 
                  (('r2', 'r3'), ('r4', 'r5'))]
        
        parts = sorted(iter_quartets(self.tree2, type=tuple, collapse=False, sort=True))
        self.assertEqual(parts, PARTS)
        #type=tuple, collapse=True, sort=True, quadripartitions=True
        PARTS = [('r0', 'r1', 'r2', 'r4'), 
                  ('r0', 'r1', 'r2', 'r5'), 
                  ('r0', 'r1', 'r3', 'r4'), 
                  ('r0', 'r1', 'r3', 'r5'), 
                  ('r0', 'r2', 'r4', 'r5'), 
                  ('r0', 'r3', 'r4', 'r5'), 
                  ('r0', 'r4', 'r2', 'r3'), 
                  ('r0', 'r5', 'r2', 'r3'), 
                  ('r1', 'r2', 'r4', 'r5'), 
                  ('r1', 'r3', 'r4', 'r5'), 
                  ('r1', 'r4', 'r2', 'r3'), 
                  ('r1', 'r5', 'r2', 'r3')]
        parts = sorted(iter_quartets(self.tree2, type=tuple, collapse=True, sort=True, quadripartitions=True))
        self.assertEqual(parts, PARTS)
        #type=list, collapse=False, sort=True
        PARTS = [(['r0', 'r1'], ['r2', 'r3']), 
                 (['r0', 'r1'], ['r2', 'r4']), 
                 (['r0', 'r1'], ['r2', 'r5']), 
                 (['r0', 'r1'], ['r3', 'r4']), 
                 (['r0', 'r1'], ['r3', 'r5']), 
                 (['r0', 'r1'], ['r4', 'r5']), 
                 (['r0', 'r2'], ['r4', 'r5']), 
                 (['r0', 'r3'], ['r4', 'r5']), 
                 (['r0', 'r4'], ['r2', 'r3']), 
                 (['r0', 'r5'], ['r2', 'r3']), 
                 (['r1', 'r2'], ['r4', 'r5']), 
                 (['r1', 'r3'], ['r4', 'r5']), 
                 (['r1', 'r4'], ['r2', 'r3']), 
                 (['r1', 'r5'], ['r2', 'r3']), 
                 (['r2', 'r3'], ['r4', 'r5'])]
        parts = (sorted(iter_quartets(self.tree2, type=list, collapse=False, sort=True)))
        self.assertEqual(parts, PARTS)
        #type=list, collapse=True, sort=True
        PARTS = [['r0', 'r1', 'r2', 'r3'], 
                 ['r0', 'r1', 'r2', 'r4'], 
                 ['r0', 'r1', 'r2', 'r5'], 
                 ['r0', 'r1', 'r3', 'r4'], 
                 ['r0', 'r1', 'r3', 'r5'], 
                 ['r0', 'r1', 'r4', 'r5'], 
                 ['r0', 'r2', 'r4', 'r5'], 
                 ['r0', 'r3', 'r4', 'r5'], 
                 ['r0', 'r4', 'r2', 'r3'], 
                 ['r0', 'r5', 'r2', 'r3'], 
                 ['r1', 'r2', 'r4', 'r5'], 
                 ['r1', 'r3', 'r4', 'r5'], 
                 ['r1', 'r4', 'r2', 'r3'], 
                 ['r1', 'r5', 'r2', 'r3'], 
                 ['r2', 'r3', 'r4', 'r5']]
        parts = (sorted(iter_quartets(self.tree2, type=list, collapse=True, sort=True)))
        self.assertEqual(parts, PARTS)

        #testing sorting methods (both built in tuple-level sort and (sort=) arg collection-level sort)

        #type=list, collapse=False, sort=True
        for item in list(iter_quartets(self.tree2, type=list, collapse=False, sort=True)):
            self.assertGreater(item[1][0], item[0][0]) #collection-level
            for collection in item:
                self.assertGreater(collection[1], collection[0]) #tuple-level
        #type=tuple, collapse=False, sort=True
        for item in list(iter_quartets(self.tree2, type=tuple, collapse=False, sort=True)):
            self.assertGreater(item[1][0], item[0][0])
            for collection in item:
                self.assertGreater(collection[1], collection[0])
        #type=list, collapse=True, sort=True
        for item in list(iter_quartets(self.tree2, type=list, collapse=True, sort=True)):
            self.assertGreater(item[2], item[0]) #collection-level
            self.assertGreater(item[1], item[0]) #tuple-level
            self.assertGreater(item[3], item[2])
        #type=tuple, collapse=True, sort=True
        for item in list(iter_quartets(self.tree2, type=tuple, collapse=True, sort=True)):
            self.assertGreater(item[2], item[0]) #collection-level
            self.assertGreater(item[1], item[0]) #tuple- level
            self.assertGreater(item[3], item[2])




if __name__ == "__main__":

    unittest.main()
