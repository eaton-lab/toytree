"""Tests for explicit rtree CLI generation methods."""

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
    """Validate tree-simulation command behavior."""

    def setUp(self):
        """Set up a temporary directory and standalone parser."""
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-rtree-"))
        self.parser = get_parser_rtree()

    def _run_capture(self, argv):
        args = self.parser.parse_args(argv)
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            run_rtree(args)
        return out.getvalue().strip(), err.getvalue().strip()

    def test_default_random_topology(self):
        """The default method emits a parseable Yule topology."""
        out, _ = self._run_capture(["-n", "12", "--seed", "123"])
        self.assertEqual(toytree.tree(out).ntips, 12)

    def test_pda_topology(self):
        """The topology model selector exposes PDA sampling."""
        out, _ = self._run_capture(
            ["--topology-model", "pda", "-n", "12", "--seed", "123"]
        )
        self.assertEqual(toytree.tree(out).ntips, 12)

    def test_unittree_height_and_prefix(self):
        """Unambiguous method prefixes retain convenient CLI parsing."""
        out, _ = self._run_capture(
            ["--method", "u", "-n", "10", "--treeheight", "3.5", "--seed", "1"]
        )
        tree = toytree.tree(out)
        self.assertTrue(tree.is_ultrametric())
        self.assertAlmostEqual(tree.treenode.height, 3.5, places=6)

    def test_balanced_tree_accepts_odd_tip_count(self):
        """The CLI exposes the corrected odd-sized balanced generator."""
        out, _ = self._run_capture(["--method", "baltree", "-n", "9"])
        self.assertEqual(toytree.tree(out).ntips, 9)

    def test_birth_death_process_stats(self):
        """Forward-process statistics are printed separately from Newick."""
        out, err = self._run_capture(
            [
                "--method",
                "birth-death-process",
                "-n",
                "8",
                "--birth-rate",
                "1.0",
                "--death-rate",
                "0.2",
                "--stats",
                "--seed",
                "7",
            ]
        )
        self.assertEqual(toytree.tree(out).ntips, 8)
        self.assertIn("elapsed_time=", err)
        self.assertIn("births=", err)

    def test_birth_death_process_time_stop(self):
        """An explicit time stop does not also receive the default tip stop."""
        out, _ = self._run_capture(
            [
                "--method",
                "birth-death-process",
                "--stop-time",
                "2.5",
                "--birth-rate",
                "1.0",
                "--death-rate",
                "0.0",
                "--seed",
                "7",
            ]
        )
        self.assertGreaterEqual(toytree.tree(out).ntips, 1)

    def test_birth_death_conditioned(self):
        """The conditioned method requires and honors an explicit age."""
        out, _ = self._run_capture(
            [
                "--method",
                "birth-death-conditioned",
                "-n",
                "8",
                "--crown-age",
                "4",
                "--seed",
                "7",
            ]
        )
        tree = toytree.tree(out)
        self.assertEqual(tree.ntips, 8)
        self.assertAlmostEqual(tree.treenode.height, 4.0, places=6)

    def test_coalescent_tree(self):
        """Coalescent options use explicit Ne and ploidy names."""
        out, _ = self._run_capture(
            [
                "--method",
                "coalescent-tree",
                "-n",
                "9",
                "--Ne",
                "250",
                "--ploidy",
                "2",
                "--seed",
                "5",
            ]
        )
        self.assertEqual(toytree.tree(out).ntips, 9)

    def test_binary_output(self):
        """Binary mode writes a transport payload for new method names."""
        outpath = self.tmpdir / "rtree.bin"
        args = self.parser.parse_args(
            ["--method", "random-topology", "-n", "6", "-b", "-o", str(outpath)]
        )
        run_rtree(args)
        self.assertEqual(read_tree_auto(str(outpath)).ntips, 6)

    def test_reject_incompatible_options(self):
        """Method-specific options cannot silently affect other generators."""
        args = self.parser.parse_args(
            ["--method", "random-topology", "-n", "6", "--Ne", "100"]
        )
        with self.assertRaises(ToytreeError):
            run_rtree(args)
        args = self.parser.parse_args(
            ["--method", "coalescent-tree", "-n", "6", "--treeheight", "3"]
        )
        with self.assertRaises(ToytreeError):
            run_rtree(args)

    def test_legacy_method_names_are_parser_errors(self):
        """Removed method names do not silently select new distributions."""
        for name in ("rtree", "bdtree", "coaltree"):
            with self.assertRaises(SystemExit):
                self.parser.parse_args(["--method", name])
