#!/usr/bin/env python

import io
import pickle
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import toytree
from toytree.cli._subparser_helpers import parse_node_mask
from toytree.cli.cli_draw import run_draw
from toytree.cli.subparsers import get_parser_draw



from conftest import PytestCompat

class TestDrawCLI(PytestCompat):
    def setUp(self):
        self.parser = get_parser_draw()
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-draw-"))

    def test_parse_node_mask_bool(self):
        self.assertTrue(parse_node_mask("true"))
        self.assertFalse(parse_node_mask("false"))

    def test_parse_node_mask_tuple(self):
        self.assertEqual(parse_node_mask("1,0,1"), (True, False, True))
        self.assertEqual(parse_node_mask("(1, 0, 1)"), (True, False, True))
        self.assertEqual(parse_node_mask("[1 0 1]"), (True, False, True))

    def test_parse_node_mask_invalid(self):
        with self.assertRaises(ValueError):
            parse_node_mask("1,0")
        with self.assertRaises(ValueError):
            parse_node_mask("1,2,1")

    def test_parser_accepts_node_mask(self):
        args = self.parser.parse_args(["-i", "((a,b),c);", "-nm", "1,0,1"])
        self.assertEqual(args.node_mask, (True, False, True))

    def test_parser_accepts_bare_boolean_flags(self):
        args = self.parser.parse_args(["-i", "((a,b),c);", "-ta", "-tl", "-sb", "-ue"])
        self.assertTrue(args.tip_labels_align)
        self.assertTrue(args.tip_labels)
        self.assertTrue(args.scale_bar)
        self.assertTrue(args.use_edge_lengths)

    def test_parser_accepts_explicit_boolean_flags(self):
        args = self.parser.parse_args(["-i", "((a,b),c);", "-ta", "false", "-tl", "true"])
        self.assertFalse(args.tip_labels_align)
        self.assertTrue(args.tip_labels)

    def test_parser_normalizes_format_case(self):
        args = self.parser.parse_args(["-i", "((a,b),c);", "-f", "PNG"])
        self.assertEqual(args.format, "png")

    def test_draw_accepts_binary_input_path_ascii_mode(self):
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        bpath = self.tmpdir / "tree.bin"
        bpath.write_bytes(pickle.dumps(tree, protocol=pickle.HIGHEST_PROTOCOL))
        args = self.parser.parse_args(["-i", str(bpath), "-a"])
        stream = io.StringIO()
        with redirect_stdout(stream):
            run_draw(args)
        self.assertTrue(stream.getvalue().strip())

    def test_draw_accepts_binary_stdin_ascii_mode(self):
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        payload = pickle.dumps(tree, protocol=pickle.HIGHEST_PROTOCOL)
        cmd = [sys.executable, "-m", "toytree.cli.main", "draw", "-i", "-", "-a"]
        proc = subprocess.run(cmd, input=payload, capture_output=True)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr.decode("utf-8", errors="replace"))
        self.assertTrue(proc.stdout.decode("utf-8", errors="replace").strip())

    def test_binary_pipe_into_draw_with_bare_ta(self):
        tree_path = self.tmpdir / "tree.nwk"
        tree_path.write_text("((a:1,b:1):1,c:1);\n", encoding="utf-8")
        cmd = (
            f"{sys.executable} -m toytree.cli.main set-node-data -i {tree_path} -f X -s a=1 -d 0 -b | "
            f"{sys.executable} -m toytree.cli.main draw -i - -a -ta"
        )
        proc = subprocess.run(["bash", "-lc", cmd], capture_output=True)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr.decode("utf-8", errors="replace"))
