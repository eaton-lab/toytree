#!/usr/bin/env python

"""Tests for rtree CLI generation methods and argument validation."""

import io
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from conftest import PytestCompat

import toytree
from toytree.cli._tree_transport import read_tree_auto
from toytree.cli.cli_rtree import run_rtree
from toytree.cli.subparsers import get_parser_rtree
from toytree.utils import ToytreeError


class TestRTreeCLI(PytestCompat):
    """Validate random-tree generation command behavior."""

    def setUp(self):
        """Set up temp directory and parser for each test."""
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-rtree-"))
        self.parser = get_parser_rtree()

    def _run_capture(self, argv):
        args = self.parser.parse_args(argv)
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            run_rtree(args)
        return out.getvalue().strip(), err.getvalue().strip()

    def test_default_method_generates_parseable_tree(self):
        """Default method should emit a parseable Newick with requested tips."""
        out, _ = self._run_capture(["-n", "12", "--seed", "123"])
        tree = toytree.tree(out)
        self.assertEqual(tree.ntips, 12)

    def test_unittree_respects_treeheight(self):
        """Unittree mode should produce an ultrametric tree at target height."""
        out, _ = self._run_capture(
            ["--method", "unittree", "-n", "10", "--treeheight", "3.5", "--seed", "1"]
        )
        tree = toytree.tree(out)
        self.assertTrue(tree.is_ultrametric())
        self.assertAlmostEqual(tree.treenode.height, 3.5, places=6)

    def test_method_unambiguous_prefix_u_maps_to_unittree(self):
        """Method shorthand should resolve unambiguous prefix values."""
        out, _ = self._run_capture(
            ["-m", "u", "-n", "10", "--treeheight", "2.0", "--seed", "1"]
        )
        tree = toytree.tree(out)
        self.assertTrue(tree.is_ultrametric())
        self.assertAlmostEqual(tree.treenode.height, 2.0, places=6)

    def test_method_unambiguous_prefix_bd_maps_to_bdtree(self):
        """Method shorthand 'bd' should resolve to bdtree."""
        out, _ = self._run_capture(
            ["-m", "bd", "-n", "8", "--stop", "taxa", "--seed", "7"]
        )
        tree = toytree.tree(out)
        self.assertEqual(tree.ntips, 8)

    def test_coaltree_uses_ntips_and_N(self):
        """Coaltree should use -n as k and accept --N."""
        out, _ = self._run_capture(
            ["--method", "coaltree", "-n", "9", "--N", "250", "--seed", "5"]
        )
        tree = toytree.tree(out)
        self.assertEqual(tree.ntips, 9)

    def test_bdtree_stats_print_to_stderr(self):
        """Bdtree stats mode should print key-value stats to stderr."""
        out, err = self._run_capture(
            [
                "--method",
                "bdtree",
                "-n",
                "8",
                "--stop",
                "taxa",
                "--stats",
                "--seed",
                "7",
            ]
        )
        tree = toytree.tree(out)
        self.assertEqual(tree.ntips, 8)
        self.assertIn("time=", err)
        self.assertIn("births=", err)
        self.assertIn("deaths=", err)

    def test_binary_output_writes_transport_payload(self):
        """Binary mode should write a valid transport payload."""
        outpath = self.tmpdir / "rtree.bin"
        args = self.parser.parse_args(
            ["--method", "rtree", "-n", "6", "-b", "-o", str(outpath)]
        )
        run_rtree(args)
        tree = read_tree_auto(str(outpath))
        self.assertEqual(tree.ntips, 6)

    def test_reject_incompatible_N_for_non_coalescent_method(self):
        """Method-incompatible coalescent arg should be rejected."""
        args = self.parser.parse_args(["--method", "rtree", "-n", "6", "--N", "100"])
        with self.assertRaises(ToytreeError):
            run_rtree(args)

    def test_reject_incompatible_treeheight_for_coalescent_method(self):
        """Method-incompatible treeheight arg should be rejected."""
        args = self.parser.parse_args(
            ["--method", "coaltree", "-n", "6", "--treeheight", "3.0"]
        )
        with self.assertRaises(ToytreeError):
            run_rtree(args)

    def test_names_length_mismatch_raises(self):
        """Names length mismatch should propagate validation error."""
        args = self.parser.parse_args(
            ["--method", "rtree", "-n", "4", "--names", "a", "b", "c"]
        )
        with self.assertRaises(ValueError):
            run_rtree(args)

    def test_method_ambiguous_prefix_b_raises_parser_error(self):
        """Ambiguous shorthand should fail parse with SystemExit."""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["-m", "b", "-n", "6"])
