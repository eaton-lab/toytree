import unittest

from toytree.network.src.major_tree import parse_major_tree_and_admixture_events


class TestMajorTreeParser(unittest.TestCase):
    def test_no_admixture_edges(self):
        newick = "((a,b),c);"
        tree, events = parse_major_tree_and_admixture_events(newick)
        self.assertEqual(set(tree.get_tip_labels()), {"a", "b", "c"})
        self.assertEqual(events, {})

    def test_single_admixture_edge(self):
        newick = "(C,D,((O,(E,#H7:::0.51)),(B,(A)#H7:::0.49)));"
        tree, events = parse_major_tree_and_admixture_events(newick)
        self.assertIn("H7", events)
        event = events["H7"]
        self.assertAlmostEqual(event.gamma, 0.51, places=2)
        self.assertTrue(set(event.major_descendants))
        self.assertTrue(set(event.minor_descendants))
        self.assertTrue(set(tree.get_tip_labels()).issuperset({"A", "B", "C", "D", "E", "O"}))

    def test_two_admixture_edges(self):
        newick = "((A,#H1:::0.2),(B,#H2:::0.3),(C)#H1,(D)#H2);"
        tree, events = parse_major_tree_and_admixture_events(newick)
        self.assertEqual(set(events.keys()), {"H1", "H2"})
        self.assertAlmostEqual(events["H1"].gamma, 0.2, places=2)
        self.assertAlmostEqual(events["H2"].gamma, 0.3, places=2)
        self.assertTrue(set(tree.get_tip_labels()).issubset({"A", "B", "C", "D"}))


if __name__ == "__main__":
    unittest.main()
