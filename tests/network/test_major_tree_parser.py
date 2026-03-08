from dataclasses import dataclass

from toytree.network.src.parse_network import parse_network


@dataclass
class _LegacyEvent:
    """Compatibility container used by historical parser tests."""

    gamma: float
    major_descendants: tuple[str, ...]
    minor_descendants: tuple[str, ...]


def parse_major_tree_and_admixture_events(newick):
    """Adapt ``parse_network`` output to the legacy test shape."""
    tree, events = parse_network(newick)
    mapped = {}
    for idx, event in enumerate(events):
        label = str(event.meta.get("label", f"H{idx}"))
        mapped[label] = _LegacyEvent(
            gamma=float(event.meta.get("gamma", 0.5)),
            major_descendants=tuple(event.src),
            minor_descendants=tuple(event.dst),
        )
    return tree, mapped


from conftest import PytestCompat

class TestMajorTreeParser(PytestCompat):
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
        self.assertTrue(set(tree.get_tip_labels()).issuperset({"A", "B", "C", "D", "E", "O", "H7"}))
        self.assertTrue(
            set(tree.get_mrca_node("C", "D").get_leaf_names()).issuperset({"C", "D"})
        )

    def test_two_admixture_edges(self):
        newick = "((A,#H1:::0.2),(B,#H2:::0.3),(C)#H1,(D)#H2);"
        tree, events = parse_major_tree_and_admixture_events(newick)
        self.assertEqual(set(events.keys()), {"H1", "H2"})
        self.assertAlmostEqual(events["H1"].gamma, 0.2, places=2)
        self.assertAlmostEqual(events["H2"].gamma, 0.3, places=2)
        self.assertTrue(set(tree.get_tip_labels()).issuperset({"A", "B", "C", "D", "H1", "H2"}))
        self.assertTrue(
            set(tree.get_mrca_node("C", "D").get_leaf_names()).issuperset({"C", "D"})
        )
