#!/usr/bin/env python

import io
import pickle
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import toytree
from toytree.cli.cli_consensus import get_parser_consensus, run_consensus


class TestConsensusCLI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-consensus-"))
        self.mtree_path = self.tmpdir / "trees.nwk"
        self.mtree_path.write_text(
            "\n".join(
                [
                    "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
                    "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
                    "((a:1,b:1):3,(e:2,(c:3,d:2):1):1);",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        self.parser = get_parser_consensus()

    def _run_capture_stdout(self, argv):
        args = self.parser.parse_args(argv)
        stream = io.StringIO()
        with redirect_stdout(stream):
            run_consensus(args)
        return stream.getvalue().strip()

    def test_infer_consensus_newick(self):
        out = self._run_capture_stdout(["-i", str(self.mtree_path), "-m", "0.5"])
        tree = toytree.tree(out)
        self.assertEqual(tree.ntips, 5)
        self.assertFalse(tree.is_rooted())

    def test_consensus_with_edge_feature_mapping(self):
        out = self._run_capture_stdout(
            ["-i", str(self.mtree_path), "-m", "0.5", "--edge-features", "dist"]
        )
        tree = toytree.tree(out)
        node = tree.get_mrca_node("a", "b")
        self.assertTrue(hasattr(node, "dist_mean"))

    def test_binary_output(self):
        outpath = self.tmpdir / "consensus.bin"
        args = self.parser.parse_args(["-i", str(self.mtree_path), "-b", "-o", str(outpath)])
        run_consensus(args)
        obj = pickle.loads(outpath.read_bytes())
        self.assertEqual(obj.__class__.__name__, "ToyTree")


if __name__ == "__main__":
    unittest.main()
