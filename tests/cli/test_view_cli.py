#!/usr/bin/env python

"""Tests for the view CLI."""

import io
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

from conftest import PytestCompat

import toytree
from toytree.cli._tree_transport import serialize_tree_binary
from toytree.cli.cli_view import run_view
from toytree.cli.subparsers import get_parser_view
from toytree.utils.src.ascii_unicode import get_ascii_or_unicode


class TestViewCLI(PytestCompat):
    """Tests for the text-tree view command."""

    def setUp(self):
        """Create a parser and temporary directory for view tests."""
        self.parser = get_parser_view()
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-view-"))

    def test_parser_defaults_to_unicode(self):
        """Default the text viewer to Unicode output."""
        args = self.parser.parse_args(["-i", "((a,b),c);"])
        self.assertEqual(args.charset, "unicode")
        self.assertTrue(args.tip_labels)
        self.assertTrue(args.use_edge_lengths)
        self.assertFalse(args.heavier)
        self.assertFalse(args.ladderize)

    def test_parser_accepts_ascii_alias_and_tip_labels_feature(self):
        """Accept the ASCII alias and feature-based tip labels."""
        args = self.parser.parse_args(
            ["-i", "((a,b),c);", "--ascii", "--tip-labels", "idx"]
        )
        self.assertEqual(args.charset, "ascii")
        self.assertEqual(args.tip_labels, "idx")

    def test_parser_accepts_heavy_selector(self):
        """Accept selector syntax for heavy-branch rendering."""
        args = self.parser.parse_args(["-i", "((a,b),c);", "--heavy", "support>90"])
        self.assertEqual(args.heavy, "support>90")

    def test_parser_accepts_heavier_flag(self):
        """Accept the stronger heavy-glyph flag."""
        args = self.parser.parse_args(["-i", "((a,b),c);", "--heavier"])
        self.assertTrue(args.heavier)

    def test_parser_accepts_ladderize_option(self):
        """Accept the display-only ladderize option."""
        args = self.parser.parse_args(["-i", "((a,b),c);", "--ladderize"])
        self.assertTrue(args.ladderize)

    def test_parser_accepts_explicit_boolean_tip_labels(self):
        """Accept explicit boolean values for tip labels."""
        args = self.parser.parse_args(["-i", "((a,b),c);", "--tip-labels", "false"])
        self.assertFalse(args.tip_labels)

    def test_view_prints_default_unicode_output(self):
        """Print Unicode text output by default."""
        tree = toytree.tree("((a:1,b:2):3,c:4);")
        path = self.tmpdir / "tree.nwk"
        path.write_text(tree.write(), encoding="utf-8")
        args = self.parser.parse_args(["-i", str(path), "-w", "12"])
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = run_view(args)
        self.assertEqual(result, 0)
        self.assertEqual(
            stream.getvalue(),
            get_ascii_or_unicode(tree, width=12, charset="unicode") + "\n",
        )

    def test_view_supports_ascii_and_renderer_options(self):
        """Forward ASCII-mode rendering options to the tree viewer."""
        tree = toytree.tree("((a:1,b:1)95:1,(c:1,d:1)60:1,e:1);")
        args = self.parser.parse_args(
            [
                "-i",
                tree.write(),
                "--ascii",
                "-w",
                "20",
                "--use-edge-lengths",
                "false",
                "--ladderize",
                "--heavy",
                "support>90",
                "--heavier",
            ]
        )
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = run_view(args)
        self.assertEqual(result, 0)
        self.assertEqual(
            stream.getvalue(),
            get_ascii_or_unicode(
                tree,
                width=20,
                charset="ascii",
                use_edge_lengths=False,
                heavy="support>90",
                heavier=True,
                ladderize=True,
            )
            + "\n",
        )

    def test_view_supports_categorical_heavy_selector(self):
        """Forward categorical heavy selectors to the renderer."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        tree.get_nodes("a")[0].sex = "M"
        tree.treenode.children[0].sex = "M"
        args = self.parser.parse_args(
            ["-i", tree.write(features=["sex"]), "--heavy", "sex=M", "--ascii"]
        )
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = run_view(args)
        self.assertEqual(result, 0)
        self.assertEqual(
            stream.getvalue(),
            get_ascii_or_unicode(tree, charset="ascii", heavy="sex=M") + "\n",
        )

    def test_view_supports_binary_input_path(self):
        """Accept binary transport payloads from an input path."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        bpath = self.tmpdir / "tree.bin"
        bpath.write_bytes(serialize_tree_binary(tree))
        args = self.parser.parse_args(["-i", str(bpath)])
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = run_view(args)
        self.assertEqual(result, 0)
        self.assertEqual(
            stream.getvalue(),
            get_ascii_or_unicode(tree, charset="unicode") + "\n",
        )

    def test_view_accepts_binary_stdin(self):
        """Accept binary transport payloads on stdin."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        payload = serialize_tree_binary(tree)
        cmd = [sys.executable, "-m", "toytree.cli.main", "view", "-i", "-"]
        proc = subprocess.run(cmd, input=payload, capture_output=True)
        self.assertEqual(
            proc.returncode, 0, msg=proc.stderr.decode("utf-8", errors="replace")
        )
        self.assertTrue(proc.stdout.decode("utf-8", errors="replace").strip())

    def test_view_accepts_implicit_stdin_without_i(self):
        """Infer stdin input when -i is omitted."""
        payload = "((a:1,b:1):1,c:1);\n"
        cmd = [sys.executable, "-m", "toytree.cli.main", "view"]
        proc = subprocess.run(
            cmd,
            input=payload,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertTrue(proc.stdout.strip())

    def test_view_implicit_stdin_empty_input_errors_cleanly(self):
        """Return a clean error when stdin is empty."""
        cmd = [sys.executable, "-m", "toytree.cli.main", "view"]
        proc = subprocess.run(cmd, input="", capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Error: no data received on stdin.", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
