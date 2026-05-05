#!/usr/bin/env python

import io
import tempfile
from contextlib import redirect_stderr
from pathlib import Path

from conftest import PytestCompat

import toytree


class TestRelabel(PytestCompat):
    def setUp(self):
        self.tree = toytree.tree("((a-1:1,b-2:1):1,c-3:1);")
        # assign internal names for tests that include non-tip nodes
        self.tree = self.tree.set_node_data("name", {3: "I-1", 4: "R-1"}, inplace=False)
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-core-relabel-"))

    def test_default_tips_only(self):
        new = self.tree.relabel(fn=str.upper, inplace=False)
        self.assertEqual(new[0].name, "A-1")
        self.assertEqual(new[1].name, "B-2")
        self.assertEqual(new[2].name, "C-3")
        self.assertEqual(new[3].name, "I-1")
        self.assertEqual(new[4].name, "R-1")

    def test_tips_only_false_changes_internal(self):
        new = self.tree.relabel(fn=str.upper, tips_only=False, inplace=False)
        self.assertEqual(new[3].name, "I-1".upper())
        self.assertEqual(new[4].name, "R-1".upper())

    def test_queries_subset(self):
        new = self.tree.relabel(queries="~^a", fn=lambda x: "AAA", inplace=False)
        self.assertEqual(new[0].name, "AAA")
        self.assertEqual(new[1].name, "b-2")
        self.assertEqual(new[2].name, "c-3")

    def test_delim_and_idxs(self):
        new = self.tree.relabel(delim="-", delim_idxs=0, inplace=False)
        self.assertEqual(new[0].name, "a")
        self.assertEqual(new[1].name, "b")
        self.assertEqual(new[2].name, "c")

    def test_delim_idxs_out_of_range_keeps_original(self):
        new = self.tree.relabel(delim="-", delim_idxs=99, inplace=False)
        self.assertEqual(new[0].name, "a-1")
        self.assertEqual(new[1].name, "b-2")
        self.assertEqual(new[2].name, "c-3")

    def test_delim_then_fn_order(self):
        new = self.tree.relabel(
            delim="-",
            delim_idxs=0,
            fn=str.upper,
            inplace=False,
        )
        self.assertEqual(new[0].name, "A")
        self.assertEqual(new[1].name, "B")

    def test_empty_name_skipped(self):
        tre = self.tree.set_node_data("name", {1: ""}, inplace=False)
        new = tre.relabel(fn=str.upper, inplace=False)
        self.assertEqual(new[1].name, "")

    def test_inplace(self):
        tre = self.tree.copy()
        out = tre.relabel(fn=str.upper, inplace=True)
        self.assertIs(out, tre)
        self.assertEqual(tre[0].name, "A-1")

    def test_fn_must_be_callable(self):
        with self.assertRaises(Exception):
            self.tree.relabel(fn="not_callable", inplace=False)

    def test_italic_and_bold_apply_last(self):
        new = self.tree.relabel(
            delim="-", delim_idxs=0, fn=str.upper, italic=True, bold=True, inplace=False
        )
        self.assertEqual(new[0].name, "<b><i>A</i></b>")
        self.assertEqual(new[1].name, "<b><i>B</i></b>")

    def test_do_not_duplicate_existing_tags(self):
        tre = self.tree.set_node_data("name", {0: "<b><i>a-1</i></b>"}, inplace=False)
        new = tre.relabel(queries=[0], italic=True, bold=True, inplace=False)
        self.assertEqual(new[0].name, "<b><i>a-1</i></b>")

    def test_imap_dict_exact_tip_names(self):
        new = self.tree.relabel(imap={"a-1": "alpha", "c-3": "charlie"}, inplace=False)
        self.assertEqual(new[0].name, "alpha")
        self.assertEqual(new[1].name, "b-2")
        self.assertEqual(new[2].name, "charlie")

    def test_imap_dict_regex_selector(self):
        tre = toytree.tree("((aa:1,ab:1):1,c:1);")
        new = tre.relabel(imap={"~^ab$": "beta"}, inplace=False)
        self.assertEqual(new[0].name, "aa")
        self.assertEqual(new[1].name, "beta")
        self.assertEqual(new[2].name, "c")

    def test_imap_file_ignores_extra_columns(self):
        imap = self.tmpdir / "imap.txt"
        imap.write_text("a-1 alpha extra\nc-3 charlie ignored\n", encoding="utf-8")
        new = self.tree.relabel(imap=imap, inplace=False)
        self.assertEqual(new[0].name, "alpha")
        self.assertEqual(new[2].name, "charlie")

    def test_imap_warns_on_unmatched_and_continues(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            new = self.tree.relabel(
                imap={"missing": "X", "a-1": "alpha"},
                inplace=False,
            )
        self.assertEqual(new[0].name, "alpha")
        self.assertEqual(new[1].name, "b-2")
        self.assertIn(
            "WARNING: imap selector 'missing' did not match any tip names.",
            buf.getvalue(),
        )

    def test_imap_raises_on_ambiguous_selector(self):
        tre = toytree.tree("((aa:1,ab:1):1,c:1);")
        with self.assertRaisesRegex(Exception, "matched multiple tips"):
            tre.relabel(imap={"~^a": "ambig"}, inplace=False)

    def test_imap_raises_when_two_selectors_hit_same_tip(self):
        tre = toytree.tree("((aa:1,ab:1):1,c:1);")
        with self.assertRaisesRegex(Exception, "both matched tip 'aa'"):
            tre.relabel(imap={"aa": "alpha", "~^aa$": "beta"}, inplace=False)

    def test_imap_applies_after_other_transforms(self):
        new = self.tree.relabel(
            delim="-",
            delim_idxs=0,
            fn=str.upper,
            imap={"a-1": "alpha"},
            inplace=False,
        )
        self.assertEqual(new[0].name, "alpha")
        self.assertEqual(new[1].name, "B")
        self.assertEqual(new[2].name, "C")
