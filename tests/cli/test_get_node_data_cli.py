#!/usr/bin/env python

"""Tests for get-node-data CLI formatting and single-feature output."""

from __future__ import annotations

import io
import pickle
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

from conftest import PytestCompat

import toytree
from toytree.cli.cli_get_node_data import run_get_node_data
from toytree.cli.subparsers import get_parser_get_node_data


class TestGetNodeDataCLI(PytestCompat):
    """Validate get-node-data output formatting and indexing behavior."""

    def setUp(self):
        """Create a small tree parser fixture for get-node-data tests."""
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-get-node-data-"))
        self.tree_path = self.tmpdir / "tree.nwk"
        self.tree_path.write_text("((a:1,b:2):3,c:4);\n", encoding="utf-8")
        self.parser = get_parser_get_node_data()

    def _run_capture_stdout(self, argv):
        """Run CLI args and return stdout with only trailing newlines removed."""
        args = self.parser.parse_args(argv)
        stream = io.StringIO()
        with redirect_stdout(stream):
            run_get_node_data(args)
        return stream.getvalue().rstrip("\n")

    def test_single_feature_column_uses_feature_name(self):
        """Single-feature output should keep the feature name as column header."""
        out = self._run_capture_stdout(["-i", str(self.tree_path), "-f", "name"])
        self.assertEqual(out.splitlines()[0], "\tname")

    def test_single_feature_with_nodes_filter_does_not_crash(self):
        """Single-feature output should support node selection without pandas errors."""
        out = self._run_capture_stdout(
            ["-i", str(self.tree_path), "-f", "name", "-n", "a", "b"]
        )
        lines = out.splitlines()
        self.assertEqual(lines[0], "\tname")
        self.assertEqual(len(lines), 3)
        self.assertTrue(any(line.endswith("\ta") for line in lines[1:]))
        self.assertTrue(any(line.endswith("\tb") for line in lines[1:]))

    def test_index_name_uses_per_row_fallback_to_idx(self):
        """Name index mode should fall back to node idx for unnamed nodes."""
        out = self._run_capture_stdout(["-i", str(self.tree_path), "-f", "name", "-N"])
        lines = out.splitlines()
        self.assertEqual(lines[0], "\tname")
        self.assertIn("a\ta", lines)
        self.assertIn("b\tb", lines)
        self.assertIn("c\tc", lines)
        self.assertIn("3\t", lines)
        self.assertIn("4\t", lines)

    def test_index_name_with_tips_only_uses_tip_names(self):
        """Tips-only name index mode should use tip names for all rows."""
        out = self._run_capture_stdout(
            ["-i", str(self.tree_path), "-f", "name", "-t", "-N"]
        )
        lines = out.splitlines()
        self.assertEqual(lines[0], "\tname")
        self.assertEqual(len(lines), 4)
        self.assertIn("a\ta", lines)
        self.assertIn("b\tb", lines)
        self.assertIn("c\tc", lines)

    def test_binary_tree_input_path_is_supported(self):
        """Binary ToyTree input path should be parsed via shared tree transport."""
        tree = toytree.tree(self.tree_path)
        binary_path = self.tmpdir / "tree.bin"
        binary_path.write_bytes(pickle.dumps(tree, protocol=pickle.HIGHEST_PROTOCOL))
        out = self._run_capture_stdout(["-i", str(binary_path), "-f", "name"])
        lines = out.splitlines()
        self.assertEqual(lines[0], "\tname")
        self.assertTrue(any(line.endswith("\ta") for line in lines[1:]))
        self.assertTrue(any(line.endswith("\tb") for line in lines[1:]))
        self.assertTrue(any(line.endswith("\tc") for line in lines[1:]))
