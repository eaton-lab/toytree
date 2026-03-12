#!/usr/bin/env python

"""Tests for ToyTree text-view helpers."""

import inspect
import io
import warnings
from contextlib import redirect_stdout

from conftest import PytestCompat

import toytree
from toytree.utils.src.ascii_unicode import get_ascii_or_unicode
from toytree.utils.src.exceptions import TreeNodeError


class TestToyTreeView(PytestCompat):
    """Tests for ToyTree.view() and the tree-based text renderer."""

    def test_view_prints_unicode_output_and_returns_none(self):
        """Print Unicode output by default from ToyTree.view."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = tree.view(width=12)
        self.assertIsNone(result)
        self.assertEqual(
            stream.getvalue(),
            get_ascii_or_unicode(tree, width=12, charset="unicode") + "\n",
        )

    def test_view_supports_file_and_renderer_options(self):
        """Forward renderer options and print to a provided text stream."""
        tree = toytree.tree("((a:1,b:1)95:1,(c:1,d:1)60:1,e:1);")
        stream = io.StringIO()
        result = tree.view(
            width=20,
            charset="unicode",
            use_edge_lengths=False,
            heavy="support>90",
            heavier=True,
            ladderize=True,
            file=stream,
        )
        self.assertIsNone(result)
        self.assertEqual(
            stream.getvalue(),
            get_ascii_or_unicode(
                tree,
                width=20,
                charset="unicode",
                use_edge_lengths=False,
                heavy="support>90",
                heavier=True,
                ladderize=True,
            )
            + "\n",
        )

    def test_get_ascii_warns_and_keeps_legacy_string(self):
        """Warn on legacy ToyTree.get_ascii while preserving its return value."""
        tree = toytree.tree("((a,b),c);")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = tree.get_ascii(compact=True)
        self.assertEqual(len(caught), 1)
        self.assertIs(caught[0].category, DeprecationWarning)
        self.assertIn("ToyTree.get_ascii() is deprecated", str(caught[0].message))
        self.assertEqual(result, "   /- /-a\n--|   \\-b\n   \\-c")

    def test_get_ascii_or_unicode_balanced_tree(self):
        """Render a balanced tree with branch-length scaling."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        expected = "\n".join(
            [
                "     /--a",
                "/----+",
                "|    \\----b",
                "|",
                "\\-------c",
            ]
        )
        self.assertEqual(get_ascii_or_unicode(tree, width=12), expected)

    def test_get_ascii_or_unicode_polytomy(self):
        """Render a tree with more than two children."""
        tree = toytree.tree("((a:1,b:1,c:1):1,d:1);")
        expected = "\n".join(
            [
                "    /-----a",
                "    |",
                "/---+-----b",
                "|   |",
                "|   \\-----c",
                "|",
                "\\----d",
            ]
        )
        self.assertEqual(get_ascii_or_unicode(tree, width=12), expected)

    def test_get_ascii_or_unicode_single_tip(self):
        """Render a single-tip tree without connector artifacts."""
        tree = toytree.tree("(a:1);")
        self.assertEqual(get_ascii_or_unicode(tree, width=12), "a")

    def test_get_ascii_or_unicode_rejects_node_input(self):
        """Require a ToyTree rather than a bare Node input."""
        tree = toytree.tree("((a,b),c);")
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree.treenode, width=12)

    def test_get_ascii_or_unicode_supports_tip_label_specs(self):
        """Support the staged tip label specs for ASCII output."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        self.assertEqual(
            get_ascii_or_unicode(tree, width=12, tip_labels=False),
            "\n".join(
                [
                    "       /--",
                    "/------+",
                    "|      \\----",
                    "|",
                    "\\---------",
                ]
            ),
        )
        self.assertEqual(
            get_ascii_or_unicode(tree, width=12, tip_labels="idx"),
            "\n".join(
                [
                    "     /--0",
                    "/----+",
                    "|    \\----1",
                    "|",
                    "\\-------2",
                ]
            ),
        )
        self.assertEqual(
            get_ascii_or_unicode(
                tree,
                width=12,
                tip_labels=("dist", "{:.1f}"),
            ),
            "\n".join(
                [
                    "    /--1.0",
                    "/---+",
                    "|   \\---2.0",
                    "|",
                    "\\------4.0",
                ]
            ),
        )
        self.assertEqual(
            get_ascii_or_unicode(
                tree,
                width=12,
                tip_labels=("name", lambda value: value.upper()),
            ),
            "\n".join(
                [
                    "     /--A",
                    "/----+",
                    "|    \\----B",
                    "|",
                    "\\-------C",
                ]
            ),
        )

    def test_get_ascii_or_unicode_rejects_invalid_tip_label_specs(self):
        """Reject malformed or missing tip label specifications."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, width=12, tip_labels=3.14)
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, width=12, tip_labels=("name", object()))
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, width=12, tip_labels="missing_feature")

    def test_get_ascii_or_unicode_falls_back_to_topology_spacing(self):
        """Fall back to unit spacing when branch lengths are invalid."""
        tree = toytree.tree("((a:-1,b:2):3,c:4);")
        expected = "\n".join(
            [
                "    /-----a",
                "/---+",
                "|   \\-----b",
                "|",
                "\\----c",
            ]
        )
        self.assertEqual(get_ascii_or_unicode(tree, width=12), expected)

    def test_get_ascii_or_unicode_supports_topology_spacing(self):
        """Ignore edge lengths when equal-spacing topology is requested."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        expected = "\n".join(
            [
                "    /-----a",
                "/---+",
                "|   \\-----b",
                "|",
                "\\---------c",
            ]
        )
        self.assertEqual(
            get_ascii_or_unicode(tree, width=12, use_edge_lengths=False),
            expected,
        )

    def test_get_ascii_or_unicode_supports_display_ladderize(self):
        """Ladderize clades for display without changing tree order."""
        tree = toytree.tree("((a:1,b:1,c:1):1,d:1);")
        original_order = tree.get_tip_labels()
        rendered = get_ascii_or_unicode(tree, width=12, ladderize=True)
        self.assertEqual(tree.get_tip_labels(), original_order)
        self.assertEqual(
            rendered,
            "\n".join(
                [
                    "/----d",
                    "|",
                    "|   /-----a",
                    "|   |",
                    "\\---+-----b",
                    "    |",
                    "    \\-----c",
                ]
            ),
        )

    def test_get_ascii_or_unicode_supports_unicode_charset(self):
        """Support the Unicode charset option for cohesive drawings."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        self.assertEqual(
            get_ascii_or_unicode(tree, width=12, charset="unicode"),
            "\n".join(
                [
                    "     ┌──a",
                    "┌────┤",
                    "│    └────b",
                    "│",
                    "└───────c",
                ]
            ),
        )

    def test_get_ascii_or_unicode_rejects_invalid_charset(self):
        """Reject unsupported rendering themes."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, width=12, charset="ansi-art")

    def test_get_ascii_or_unicode_auto_width_matches_heuristic(self):
        """Choose a stable default width when width is None."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        self.assertEqual(
            get_ascii_or_unicode(tree, width=None),
            get_ascii_or_unicode(tree, width=24),
        )

    def test_get_ascii_or_unicode_auto_width_accounts_for_formatted_labels(self):
        """Use formatted label width when estimating the default width."""
        tree = toytree.rtree.unittree(ntips=10, seed=123)
        formatter = ("name", lambda value: f"label-{value}-x")
        leaves = list(tree.treenode.iter_leaves())
        expected_width = max(
            24,
            min(
                160,
                int(2.5 * len(leaves))
                + max(
                    max(len(node.name) for node in leaves),
                    max(len(f"label-{node.name}-x") for node in leaves),
                )
                + 8,
            ),
        )
        self.assertEqual(
            get_ascii_or_unicode(tree, width=None, tip_labels=formatter),
            get_ascii_or_unicode(
                tree,
                width=expected_width,
                tip_labels=formatter,
            ),
        )

    def test_get_ascii_or_unicode_rejects_invalid_width(self):
        """Reject invalid explicit width values."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, width=1)
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, width="12")
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, width=True)

    def test_get_ascii_or_unicode_support_selector_heavy_ascii(self):
        """Render heavy ASCII branches matched by a numeric selector."""
        tree = toytree.tree("((a:1,b:1)95:1,(c:1,d:1)60:1,e:1);")
        self.assertEqual(
            get_ascii_or_unicode(
                tree,
                width=20,
                charset="ascii",
                use_edge_lengths=False,
                heavy="support>90",
            ),
            "\n".join(
                [
                    "        /---------a",
                    "/=======+",
                    "|       \\---------b",
                    "|",
                    "|       /---------c",
                    "+-------+",
                    "|       \\---------d",
                    "|",
                    "\\-----------------e",
                ]
            ),
        )

    def test_get_ascii_or_unicode_support_selector_heavy_unicode(self):
        """Render heavy Unicode branches matched by a numeric selector."""
        tree = toytree.tree("((a:1,b:1)95:1,(c:1,d:1)60:1,e:1);")
        self.assertEqual(
            get_ascii_or_unicode(
                tree,
                width=20,
                charset="unicode",
                use_edge_lengths=False,
                heavy="support>90",
            ),
            "\n".join(
                [
                    "        ┌─────────a",
                    "┌━━━━━━━┤",
                    "│       └─────────b",
                    "│",
                    "│       ┌─────────c",
                    "├───────┤",
                    "│       └─────────d",
                    "│",
                    "└─────────────────e",
                ]
            ),
        )

    def test_get_ascii_or_unicode_supports_heavier_ascii_glyph(self):
        """Use the stronger ASCII heavy glyph when requested."""
        tree = toytree.tree("((a:1,b:1)95:1,(c:1,d:1)60:1,e:1);")
        self.assertEqual(
            get_ascii_or_unicode(
                tree,
                width=20,
                charset="ascii",
                use_edge_lengths=False,
                heavy="support>90",
                heavier=True,
            ),
            "\n".join(
                [
                    "        /---------a",
                    "/#######+",
                    "|       \\---------b",
                    "|",
                    "|       /---------c",
                    "+-------+",
                    "|       \\---------d",
                    "|",
                    "\\-----------------e",
                ]
            ),
        )

    def test_get_ascii_or_unicode_supports_heavier_unicode_glyph(self):
        """Use the stronger Unicode heavy glyph when requested."""
        tree = toytree.tree("((a:1,b:1)95:1,(c:1,d:1)60:1,e:1);")
        self.assertEqual(
            get_ascii_or_unicode(
                tree,
                width=20,
                charset="unicode",
                use_edge_lengths=False,
                heavy="support>90",
                heavier=True,
            ),
            "\n".join(
                [
                    "        ┌─────────a",
                    "┌▒▒▒▒▒▒▒┤",
                    "│       └─────────b",
                    "│",
                    "│       ┌─────────c",
                    "├───────┤",
                    "│       └─────────d",
                    "│",
                    "└─────────────────e",
                ]
            ),
        )

    def test_get_ascii_or_unicode_heavy_selector_applies_to_tip_and_internal_edges(
        self,
    ):
        """Apply heavy styling to any matching non-root child edge."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        tree.get_nodes("a")[0].support = 100
        tree.treenode.children[0].support = 95
        rendered = get_ascii_or_unicode(
            tree,
            width=16,
            charset="ascii",
            use_edge_lengths=False,
            heavy="support>90",
        )
        self.assertIn("/=======a", rendered)
        self.assertIn("/=====+", rendered)
        self.assertNotIn("\\=======", rendered)

    def test_get_ascii_or_unicode_supports_categorical_heavy_selectors(self):
        """Match categorical node features for heavy-branch styling."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        tree.get_nodes("a")[0].sex = "M"
        tree.get_nodes("b")[0].sex = "F"
        tree.get_nodes("c")[0].sex = "M"
        tree.treenode.children[0].sex = "M"
        rendered = get_ascii_or_unicode(
            tree,
            width=16,
            charset="unicode",
            use_edge_lengths=False,
            heavy="sex=M",
        )
        self.assertIn("┌━━━━━━━a", rendered)
        self.assertIn("┌━━━━━┤", rendered)
        self.assertIn("└━━━━━━━━━━━━━c", rendered)
        self.assertIn("└───────b", rendered)

    def test_get_ascii_or_unicode_supports_missing_heavy_selectors(self):
        """Treat absent and NaN-like feature values as missing."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        tree.get_nodes("b")[0].group = "B"
        tree.get_nodes("c")[0].group = "C"
        tree.treenode.children[0].group = None
        rendered = get_ascii_or_unicode(
            tree,
            width=16,
            charset="ascii",
            use_edge_lengths=False,
            heavy="group=nan",
        )
        self.assertIn("/=======a", rendered)
        self.assertIn("/=====+", rendered)
        self.assertIn("\\-------b", rendered)
        self.assertIn("\\-------------c", rendered)

    def test_get_ascii_or_unicode_rejects_invalid_heavy_selectors(self):
        """Reject malformed heavy-selector expressions."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, heavy=True)
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, heavy="")
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, heavy="support")
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, heavy="sex>F")

    def test_get_ascii_or_unicode_rejects_invalid_heavier(self):
        """Reject malformed heavier option values."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, heavier="yes")

    def test_get_ascii_or_unicode_rejects_invalid_ladderize(self):
        """Reject malformed ladderize values."""
        tree = toytree.tree("((a,b),c);")
        with self.assertRaises(TreeNodeError):
            get_ascii_or_unicode(tree, ladderize="yes")

    def test_get_ascii_or_unicode_signature_shows_tree_and_literal_options(self):
        """Expose the tree-based signature in function introspection."""
        sig = str(inspect.signature(get_ascii_or_unicode))
        self.assertIn("ToyTree", sig)
        self.assertIn("Literal", sig)
        self.assertIn("'ascii'", sig)
        self.assertIn("'unicode'", sig)
        self.assertIn("heavy", sig)
        self.assertIn("heavier", sig)
        self.assertIn("ladderize", sig)
        self.assertNotIn("Node", sig)
        self.assertNotIn("heavy_on_min_support", sig)
