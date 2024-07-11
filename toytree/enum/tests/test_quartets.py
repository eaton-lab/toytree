''' Test enumeration methods for quartets.py

    For each combination of arguments, tests sorting, correct datatypes, and expected outputs

    tree: ToyTree,
    feature: Optional[str] = 'name',
    type: Callable = set,
    sort: bool = False,
    collapse: bool = False,
    quadripartitions: bool = False,
    
    possible combinations of arguments:

    test_set (default)
        test_set_sort
                test_set_sort_quad
        test_set_quad

    test_tuple
        test_tuple_sort
            test_tuple_sort_collapse
                test_tuple_sort_collapse_quad
            test_tuple_sort_quad
        test_tuple_collapse
            test_tuple_collapse_quad
        test_tuple_quad

    test_list
        test_list_sort
            test_list_sort_collapse
                test_list_sort_collapse_quad
            test_list_sort_quad
        test_list_collapse
            test_list_collapse_quad
        test_list_quad
    '''

import unittest
import toytree
from toytree.enum import _iter_unresolved_quartet_sets, _iter_quartet_sets, iter_quartets


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
                        self.assertGreater(item[2], item[0])    #quartet-level sorting (x,y),(i,j) -> (i,j),(x,y)
                    
                    self.assertGreater(item[1], item[0])        #tip-level sorting (j,i) -> (i,j)
                    self.assertGreater(item[3], item[2])
                else:
                    if sort: 
                        self.assertGreater(item[1][0], item[0][0])  #quartet-level sorting (x,y),(i,j) -> (i,j),(x,y)
                    for collection in item: 
                        self.assertGreater(collection[1], collection[0])    #tip-level sorting (j,i) -> (i,j)


    def test_default(self):
        """Test iter_quartets with default parameters."""
        results = list(iter_quartets(self.tree1))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results)

    def test_set_sort(self):
        """Test iter_quartets with sort=True."""
        results = list(iter_quartets(self.tree1, sort=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results, sort=True)

    def test_set_sort_quad(self):
        """Test iter_quartets with sort=True, quadripartitions=True."""
        results = list(iter_quartets(self.tree1, sort=True, quadripartitions=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results, sort=True)

    def test_set_quad(self):
        """Test iter_quartets with quadripartitions=True."""
        results = list(iter_quartets(self.tree1, quadripartitions=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], set)
        self._test_sorting(results)

    def test_tuple(self):
        """Test iter_quartets with type=tuple."""
        results = list(iter_quartets(self.tree1, type=tuple))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results)

    def test_tuple_sort(self):
        """Test iter_quartets with type=tuple, sort=True."""
        results = list(iter_quartets(self.tree1, type=tuple, sort=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results, sort=True)
        parts = sorted(iter_quartets(self.tree2, type=tuple, sort=True))
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
        self.assertEqual(parts, PARTS)

    def test_tuple_sort_collapse(self):
        """Test iter_quartets with type=tuple, sort=True, collapse=True."""
        results = list(iter_quartets(self.tree1, type=tuple, sort=True, collapse=True))
        self._test_sorting(results, True, True)

    def test_tuple_sort_collapse_quad(self):
        """Test iter_quartets with type=tuple, sort=True, collapse=True, quadripartitions=True."""
        results = list(iter_quartets(self.tree1, type=tuple, sort=True, collapse=True, quadripartitions= True))
        self.assertIsInstance(results[0], tuple)
        self._test_sorting(results, collapse=True, sort=True)
        parts = sorted(iter_quartets(self.tree2, type=tuple, sort=True, collapse=True, quadripartitions=True))
        PARTS =  [('r0', 'r1', 'r2', 'r4'), 
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
        self.assertEqual(parts, PARTS)

    def test_tuple_sort_quad(self):
        """Test iter_quartets with type=tuple, sort=True, quadripartitions=True."""
        results = list(iter_quartets(self.tree1, type=tuple, sort=True, quadripartitions= True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results, sort=True)

    def test_tuple_collapse(self):
        """Test iter_quartets with type=tuple, collapse=True."""
        results = list(iter_quartets(self.tree1, type=tuple, collapse=True))
        self.assertIsInstance(results[0], tuple)
        self._test_sorting(results, collapse=True)

    def test_tuple_collapse_quad(self):
        """Test iter_quartets with type=tuple, collapse=True, quadripartitions=True."""
        results = list(iter_quartets(self.tree1, type=tuple, collapse=True, quadripartitions=True))
        self.assertIsInstance(results[0], tuple)
        self._test_sorting(results, collapse=True)

    def test_tuple_quad(self):
        """Test iter_quartets with type=tuple, quadripartitions=True."""
        results = list(iter_quartets(self.tree1, type=tuple, quadripartitions=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], tuple)
        self._test_sorting(results)

    def test_list(self):
        """Test iter_quartets with type=list."""
        results = list(iter_quartets(self.tree1, type=list))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results)

    def test_list_sort(self):
        """Test iter_quartets with type=list, sort=True."""
        results = list(iter_quartets(self.tree1, type=list, sort=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results, sort=True)
        parts = (sorted(iter_quartets(self.tree2, type=list, sort=True)))
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
        self.assertEqual(parts, PARTS)

    def test_list_sort_collapse(self):
        """Test iter_quartets with type=list, sort=True, collapse=True."""
        results = list(iter_quartets(self.tree1, type=list, sort=True, collapse=True))
        parts = (sorted(iter_quartets(self.tree2, type=list, sort=True, collapse=True)))
        self.assertIsInstance(results[0], list)
        self._test_sorting(results, collapse=True, sort=True)
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
        self.assertEqual(parts, PARTS)

    def test_list_sort_collapse_quad(self):
        """Test iter_quartets with type=list, sort=True, collapse=True, quadripartitions=True."""
        results = list(iter_quartets(self.tree1, type=list, sort=True, collapse=True, quadripartitions=True))
        self.assertIsInstance(results[0], list)
        self._test_sorting(results, sort=True, collapse=True)

    def test_list_sort_quad(self):
        """Test iter_quartets with type=list, sort=True, quadripartitions=True."""
        results = list(iter_quartets(self.tree1, type=list, sort=True, quadripartitions=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results, sort=True)

    def test_list_collapse(self):
        """Test iter_quartets with type=list, collapse=True."""
        results = list(iter_quartets(self.tree1, type=list, collapse=True))
        self.assertIsInstance(results[0], list)
        self._test_sorting(results, collapse=True)

    def test_list_collapse_quad(self):
        """Test iter_quartets with type=list, collapse=True, quadripartitions=True."""
        results = list(iter_quartets(self.tree1, type=list, collapse=True, quadripartitions=True))
        self.assertIsInstance(results[0], list)
        self._test_sorting(results, collapse=True)

    def test_list_quad(self):   
        """Test iter_quartets with type=list, quadripartitions=True."""
        results = list(iter_quartets(self.tree1, type=list, quadripartitions=True))
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], list)
        self._test_sorting(results)  

    def test_iter_unresolved_quartet_sets(self):
        '''extra test to test iter_unresolved_quartet_sets function'''
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


if __name__ == "__main__":

    unittest.main()
