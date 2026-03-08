#!/usr/bin/env python

import pickle
import tempfile
from pathlib import Path

import toytree
from toytree.cli.cli_prune import run_prune
from toytree.cli.cli_root import run_root
from toytree.cli.cli_set_node_data import run_set_node_data
from toytree.cli.subparsers import (
    get_parser_prune,
    get_parser_root,
    get_parser_set_node_data,
)
from toytree.core.tree import ToyTree



from conftest import PytestCompat

class TestBinaryTreeCLIPipeline(PytestCompat):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-binary-pipe-"))
        self.tree_path = self.tmpdir / "tree.nwk"
        self.tree_path.write_text("((a:1,b:1):1,c:1);\n", encoding="utf-8")

    def test_root_binary_out_then_prune_text_out(self):
        root_parser = get_parser_root()
        bin_path = self.tmpdir / "rooted.bin"
        root_args = root_parser.parse_args(
            ["-i", str(self.tree_path), "-n", "a", "-b", "-o", str(bin_path)]
        )
        run_root(root_args)
        self.assertTrue(bin_path.exists())

        prune_parser = get_parser_prune()
        out_path = self.tmpdir / "pruned.nwk"
        prune_args = prune_parser.parse_args(
            ["-i", str(bin_path), "-n", "a", "b", "-o", str(out_path)]
        )
        run_prune(prune_args)
        out_tree = toytree.tree(out_path)
        self.assertEqual(out_tree.ntips, 2)

    def test_set_node_data_binary_out(self):
        parser = get_parser_set_node_data()
        out_path = self.tmpdir / "setdata.bin"
        args = parser.parse_args(
            [
                "-i",
                str(self.tree_path),
                "--feature",
                "score",
                "--set",
                "a=1.0",
                "--default",
                "0.0",
                "--binary-out",
                "--output",
                str(out_path),
            ]
        )
        run_set_node_data(args)
        payload = out_path.read_bytes()
        obj = pickle.loads(payload)
        self.assertIsInstance(obj, ToyTree)
        self.assertIn("score", obj.features)

