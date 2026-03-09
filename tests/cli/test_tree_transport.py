#!/usr/bin/env python

import pickle
import tempfile
from pathlib import Path
from unittest.mock import patch

from conftest import PytestCompat

import toytree
from toytree.cli._tree_transport import read_tree_auto
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

    def test_read_tree_auto_text_path_skips_unpickle_probe(self):
        path = self.tmpdir / "tree.nwk"
        path.write_text(self.tree.write(None) + "\n", encoding="utf-8")
        with patch(
            "toytree.cli._tree_transport._try_unpickle_tree",
            side_effect=AssertionError("_try_unpickle_tree should not be called"),
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

    def test_read_tree_auto_binary_path(self):
        path = self.tmpdir / "tree.bin"
        path.write_bytes(pickle.dumps(self.tree, protocol=pickle.HIGHEST_PROTOCOL))
        tre = read_tree_auto(str(path))
        self.assertIsInstance(tre, ToyTree)
        self.assertEqual(tre.ntips, self.tree.ntips)

    def test_read_tree_auto_wrong_binary_type_raises(self):
        path = self.tmpdir / "not_tree.bin"
        path.write_bytes(pickle.dumps({"x": 1}, protocol=pickle.HIGHEST_PROTOCOL))
        with self.assertRaises(ToytreeError):
            read_tree_auto(str(path))
