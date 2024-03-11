#!/usr/bin/env python

"""Test rooting functions.


- cases: root, unroot, polytomies, zero-len edges, big trees...
"""

import unittest
import toytree


class TestRootByMinimalAncestorDeviation(unittest.TestCase):
    def setUp(self):
        self.tree = (
            toytree.rtree.rtree(5, seed=123)
            .unroot()
            .set_node_data(
                'name',
                {i: j for i, j in enumerate("abcdeXYR")},
            )
        )
        self.tree1 = self.tree.set_node_data('dist', {'e': 5, 'Y': 3})
        self.tree2 = self.tree.set_node_data('dist', {'e': 5, 'Y': 3, 'X': 10})
        self.utree = toytree.rtree.unittree(25, seed=123)
        self.itree = toytree.rtree.imbtree(26)
        self.btree = toytree.rtree.baltree(25)

    def test_polytomies(self):
        """..."""
        

    def test_dev0_trees(self):
        for tree in [self.utree, self.itree, self.btree]:
            rtree, stats = tree.mod.root_on_minimal_ancestor_deviation(return_stats=True)
            mad_results = {
                'minimal_ancestor_deviation': 0.,
                'root_ambiguity_index': 0.,
                'root_clock_coefficient_of_variation': 0.,
            }
        for key, stat in stats.items():
            self.assertAlmostEqual(stats[key], mad_results[key])

    def test_tree1_unrooted(self):
        rtree, stats = self.tree1.mod.root_on_minimal_ancestor_deviation(return_stats=True)
        mad_results = {
            'minimal_ancestor_deviation': 0.3281920104298636,
            'root_ambiguity_index': 0.8020452043139145,
            'root_clock_coefficient_of_variation': 41.54087983900019,
        }
        for key, stat in stats.items():
            self.assertAlmostEqual(stats[key], mad_results[key])

    def test_tree1_rooted_terminal(self):
        rtree, stats = self.tree1.root('a').mod.root_on_minimal_ancestor_deviation(return_stats=True)
        mad_results = {
            'minimal_ancestor_deviation': 0.3281920104298636,
            'root_ambiguity_index': 0.8020452043139145,
            'root_clock_coefficient_of_variation': 41.54087983900019,
        }
        for key, stat in stats.items():
            self.assertAlmostEqual(stats[key], mad_results[key])

    def test_tree1_rooted_internal(self):
        rtree, stats = self.tree1.root('X').mod.root_on_minimal_ancestor_deviation(return_stats=True)
        mad_results = {
            'minimal_ancestor_deviation': 0.3281920104298636,
            'root_ambiguity_index': 0.8020452043139145,
            'root_clock_coefficient_of_variation': 41.54087983900019,
        }
        for key, stat in stats.items():
            self.assertAlmostEqual(stats[key], mad_results[key])

    def test_tree1_rooted_on_non_optimal(self):
        rtree, stats = self.tree1.mod.root_on_minimal_ancestor_deviation('a', return_stats=True)
        mad_results = {
            'minimal_ancestor_deviation': 0.3281920104298636,
            'root_ambiguity_index': 0.8020452043139145,
            'root_clock_coefficient_of_variation': 43.30127018922193,  # note, this is increased
        }
        for key, stat in stats.items():
            self.assertAlmostEqual(stats[key], mad_results[key])
        self.assertEqual(rtree.get_topology_id(), self.tree1.root("a").get_topology_id())

    def test_tree2_unrooted(self):
        rtree, stats = self.tree2.mod.root_on_minimal_ancestor_deviation(return_stats=True)
        mad_results = {
            'minimal_ancestor_deviation': 0.4011968627201758,
            'root_ambiguity_index': 0.7276535377387878,
            'root_clock_coefficient_of_variation': 32.766687960159736,
        }
        for key, stat in stats.items():
            self.assertAlmostEqual(stats[key], mad_results[key])

    def test_tree2_rooted_terminal(self):
        rtree, stats = self.tree2.root('a').mod.root_on_minimal_ancestor_deviation(return_stats=True)
        mad_results = {
            'minimal_ancestor_deviation': 0.4011968627201758,
            'root_ambiguity_index': 0.7276535377387878,
            'root_clock_coefficient_of_variation': 32.766687960159736,
        }
        for key, stat in stats.items():
            self.assertAlmostEqual(stats[key], mad_results[key])

    def test_tree2_rooted_internal(self):
        rtree, stats = self.tree2.root('X').mod.root_on_minimal_ancestor_deviation(return_stats=True)
        mad_results = {
            'minimal_ancestor_deviation': 0.4011968627201758,
            'root_ambiguity_index': 0.7276535377387878,
            'root_clock_coefficient_of_variation': 32.766687960159736,
        }
        for key, stat in stats.items():
            self.assertAlmostEqual(stats[key], mad_results[key])

    def test_tree2_rooted_on_non_optimal(self):
        rtree, stats = self.tree2.mod.root_on_minimal_ancestor_deviation('a', return_stats=True)
        mad_results = {
            'minimal_ancestor_deviation': 0.4011968627201758,
            'root_ambiguity_index': 0.7276535377387878,
            'root_clock_coefficient_of_variation': 79.27563332311615,
        }
        for key, stat in stats.items():
            self.assertAlmostEqual(stats[key], mad_results[key])
        self.assertEqual(rtree.get_topology_id(), self.tree1.root("a").get_topology_id())


if __name__ == "__main__":
    unittest.main()
