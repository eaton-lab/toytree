#!/usr/bin/env python

import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

from conftest import PytestCompat

import toytree
from toytree.cli._tree_transport import read_tree_auto
from toytree.cli.cli_relabel import run_relabel
from toytree.cli.subparsers import get_parser_relabel


class TestRelabelCLI(PytestCompat):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-relabel-"))
        self.tree_path = self.tmpdir / "tree.nwk"
        self.tree_path.write_text("((aa|x:1,ab|y:1):1,c|z:1);\n", encoding="utf-8")
        self.parser = get_parser_relabel()

    def _run_capture_stdout(self, argv):
        args = self.parser.parse_args(argv)
        stream = io.StringIO()
        with redirect_stdout(stream):
            run_relabel(args)
        return stream.getvalue().strip()

    def test_strip(self):
        out_nwk = self._run_capture_stdout(["-i", str(self.tree_path), "--strip", "az"])
        tree = toytree.tree(out_nwk)
        self.assertEqual(tree[0].name, "|x")
        self.assertEqual(tree[1].name, "b|y")
        self.assertEqual(tree[2].name, "c|")

    def test_delim_and_idxs(self):
        out_nwk = self._run_capture_stdout(
            ["-i", str(self.tree_path), "--delim", "|", "--delim-idxs", "0"]
        )
        tree = toytree.tree(out_nwk)
        self.assertEqual(tree[0].name, "aa")
        self.assertEqual(tree[1].name, "ab")
        self.assertEqual(tree[2].name, "c")

    def test_nodes_subset(self):
        out_nwk = self._run_capture_stdout(
            ["-i", str(self.tree_path), "-n", "~^aa", "--append", "_X"]
        )
        tree = toytree.tree(out_nwk)
        self.assertEqual(tree[0].name, "aa|x_X")
        self.assertEqual(tree[1].name, "ab|y")
        self.assertEqual(tree[2].name, "c|z")

    def test_italic_and_bold(self):
        out_nwk = self._run_capture_stdout(
            ["-i", str(self.tree_path), "--prepend", "X_", "--italic", "--bold"]
        )
        tree = toytree.tree(out_nwk)
        self.assertEqual(tree[0].name, "<b><i>X_aa|x</i></b>")

    def test_binary_output(self):
        out = self.tmpdir / "out.bin"
        args = self.parser.parse_args(
            ["-i", str(self.tree_path), "--prepend", "X_", "-b", "-o", str(out)]
        )
        run_relabel(args)
        obj = read_tree_auto(str(out))
        self.assertIsInstance(obj, toytree.ToyTree)
        self.assertEqual(obj[0].name, "X_aa|x")

    def test_tips_only_false(self):
        out_nwk = self._run_capture_stdout(
            ["-i", str(self.tree_path), "--prepend", "X_", "--tips-only", "false"]
        )
        tree = toytree.tree(out_nwk)
        self.assertEqual(tree[3].name, "")  # unchanged internal empty name

    def test_stripleft(self):
        out_nwk = self._run_capture_stdout(
            ["-i", str(self.tree_path), "--stripleft", "ac"]
        )
        tree = toytree.tree(out_nwk)
        self.assertEqual(tree[0].name, "|x")
        self.assertEqual(tree[1].name, "b|y")
        self.assertEqual(tree[2].name, "|z")
