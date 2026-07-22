#!/usr/bin/env python

import io
import pickle
import tempfile
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import Mock, patch

from conftest import PytestCompat

import toytree
from toytree.cli._tree_transport import (
    read_tree_auto,
    resolve_input_arg,
    serialize_tree_binary,
)
from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError


class TestTreeTransport(PytestCompat):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-transport-"))
        self.tree = toytree.tree("((a:1,b:1):1,c:1);")

    def test_read_tree_auto_inline_newick_skips_path_exists_probe(self):
        with patch(
            "toytree.cli._tree_transport.Path.exists",
            side_effect=AssertionError("Path.exists should not be called"),
        ):
            tre = read_tree_auto("((a:1,b:1):1,c:1);")
        self.assertIsInstance(tre, ToyTree)
        self.assertEqual(tre.ntips, self.tree.ntips)

    def test_read_tree_auto_respects_custom_input_feature_parse_args(self):
        tre = read_tree_auto(
            "((a[&&NHX:state=1]:1,b:1):1,c:1);",
            feature_prefix="&&NHX:",
            feature_delim=":",
            feature_assignment="=",
        )
        self.assertIn("state", tre.features)
        self.assertEqual(float(tre.get_node_data("state").iloc[0]), 1.0)

    def test_read_tree_auto_respects_feature_unpack(self):
        tre = read_tree_auto(
            "((a[&state=0.1;0.9]:1,b:1):1,c:1);",
            feature_unpack=";",
        )
        self.assertIn("state", tre.features)
        self.assertEqual(tre.get_node_data("state").iloc[0], [0.1, 0.9])

    def test_read_tree_auto_text_path_skips_unpickle_probe(self):
        path = self.tmpdir / "tree.nwk"
        path.write_text(self.tree.write(None) + "\n", encoding="utf-8")
        with patch(
            "toytree.cli._tree_transport.deserialize_tree_binary",
            side_effect=AssertionError("deserialize_tree_binary should not be called"),
        ):
            tre = read_tree_auto(str(path))
        self.assertIsInstance(tre, ToyTree)
        self.assertEqual(tre.ntips, self.tree.ntips)

    def test_read_tree_auto_text_path(self):
        path = self.tmpdir / "tree.nwk"
        path.write_text(self.tree.write(None) + "\n", encoding="utf-8")
        tre = read_tree_auto(str(path))
        self.assertIsInstance(tre, ToyTree)
        self.assertEqual(tre.ntips, self.tree.ntips)

    def test_read_tree_auto_multitree_text_path_warns_and_uses_first_by_default(self):
        path = self.tmpdir / "trees.nwk"
        path.write_text("((a,b),c);\n((a,c),b);\n", encoding="utf-8")
        err = io.StringIO()
        with redirect_stderr(err):
            tre = read_tree_auto(str(path))
        self.assertEqual(tre.write(dist_formatter=None), "((a,b),c);")
        self.assertIn("Loading only the first tree", err.getvalue())

    def test_read_tree_auto_multitree_text_path_selects_by_index(self):
        path = self.tmpdir / "trees_idx.nwk"
        path.write_text("((a,b),c);\n((a,c),b);\n", encoding="utf-8")
        err = io.StringIO()
        with redirect_stderr(err):
            tre = read_tree_auto(str(path), tree_index=1)
        self.assertEqual(tre.write(dist_formatter=None), "((a,c),b);")
        self.assertEqual(err.getvalue(), "")

    def test_read_tree_auto_multitree_text_path_rejects_bad_index(self):
        path = self.tmpdir / "trees_oob.nwk"
        path.write_text("((a,b),c);\n((a,c),b);\n", encoding="utf-8")
        with self.assertRaisesRegex(ToytreeError, "--index 2 is out of range"):
            read_tree_auto(str(path), tree_index=2)

    def test_read_tree_auto_binary_path(self):
        path = self.tmpdir / "tree.bin"
        path.write_bytes(serialize_tree_binary(self.tree))
        tre = read_tree_auto(str(path))
        self.assertIsInstance(tre, ToyTree)
        self.assertEqual(tre.ntips, self.tree.ntips)
        self.assertEqual(tre.get_tip_labels(), self.tree.get_tip_labels())

    def test_read_tree_auto_binary_path_accepts_index_zero(self):
        path = self.tmpdir / "tree_idx0.bin"
        path.write_bytes(serialize_tree_binary(self.tree))
        tre = read_tree_auto(str(path), tree_index=0)
        self.assertEqual(tre.get_tip_labels(), self.tree.get_tip_labels())

    def test_read_tree_auto_binary_path_rejects_nonzero_index(self):
        path = self.tmpdir / "tree_idx1.bin"
        path.write_bytes(serialize_tree_binary(self.tree))
        with self.assertRaisesRegex(
            ToytreeError,
            "--index 1 is invalid for input containing a single tree",
        ):
            read_tree_auto(str(path), tree_index=1)

    def test_read_tree_auto_legacy_pickled_toytree_raises(self):
        path = self.tmpdir / "legacy-tree.bin"
        path.write_bytes(pickle.dumps(self.tree, protocol=pickle.HIGHEST_PROTOCOL))
        with self.assertRaises(ToytreeError):
            read_tree_auto(str(path))

    def test_read_tree_auto_wrong_binary_type_raises(self):
        path = self.tmpdir / "not_tree.bin"
        path.write_bytes(pickle.dumps({"x": 1}, protocol=pickle.HIGHEST_PROTOCOL))
        with self.assertRaises(ToytreeError):
            read_tree_auto(str(path))

    def test_resolve_input_arg_prefers_explicit_value(self):
        self.assertEqual(resolve_input_arg("((a,b),c);"), "((a,b),c);")

    def test_resolve_input_arg_uses_stdin_marker_for_piped_input(self):
        with patch("toytree.cli._tree_transport.sys.stdin.isatty", return_value=False):
            self.assertEqual(resolve_input_arg(None), "-")

    def test_resolve_input_arg_raises_without_input_or_pipe(self):
        with patch("toytree.cli._tree_transport.sys.stdin.isatty", return_value=True):
            with self.assertRaisesRegex(ToytreeError, "no input tree provided"):
                resolve_input_arg(None)

    def test_read_tree_auto_empty_stdin_raises(self):
        stdin_mock = Mock()
        stdin_mock.buffer.read.return_value = b""
        with patch("toytree.cli._tree_transport.sys.stdin", stdin_mock):
            with self.assertRaisesRegex(ToytreeError, "no data received on stdin"):
                read_tree_auto("-")
