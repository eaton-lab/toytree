#!/usr/bin/env python

"""Tests for the draw CLI."""

import io
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from conftest import PytestCompat

import toytree
from toytree.cli._subparser_helpers import parse_node_mask
from toytree.cli._tree_transport import serialize_tree_binary
from toytree.cli.cli_draw import run_draw
from toytree.cli.subparsers import get_parser_draw


class TestDrawCLI(PytestCompat):
    """Tests for draw parser and runtime behavior."""

    def setUp(self):
        """Create a parser and temporary directory for CLI tests."""
        self.parser = get_parser_draw()
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-draw-"))

    def test_parse_node_mask_bool(self):
        """Parse bare boolean node-mask values."""
        self.assertTrue(parse_node_mask("true"))
        self.assertFalse(parse_node_mask("false"))

    def test_parse_node_mask_tuple(self):
        """Parse tuple-like node-mask values."""
        self.assertEqual(parse_node_mask("1,0,1"), (True, False, True))
        self.assertEqual(parse_node_mask("(1, 0, 1)"), (True, False, True))
        self.assertEqual(parse_node_mask("[1 0 1]"), (True, False, True))

    def test_parse_node_mask_invalid(self):
        """Reject malformed node-mask values."""
        with self.assertRaises(ValueError):
            parse_node_mask("1,0")
        with self.assertRaises(ValueError):
            parse_node_mask("1,2,1")

    def test_parser_accepts_node_mask(self):
        """Accept node-mask values through the draw parser."""
        args = self.parser.parse_args(["-i", "((a,b),c);", "-nm", "1,0,1"])
        self.assertEqual(args.node_mask, (True, False, True))

    def test_parser_accepts_bare_boolean_flags(self):
        """Accept bare boolean rendering flags."""
        args = self.parser.parse_args(["-i", "((a,b),c);", "-ta", "-tl", "-sb", "-ue"])
        self.assertTrue(args.tip_labels_align)
        self.assertTrue(args.tip_labels)
        self.assertTrue(args.scale_bar)
        self.assertTrue(args.use_edge_lengths)

    def test_parser_accepts_explicit_boolean_flags(self):
        """Accept explicit true/false values for boolean flags."""
        args = self.parser.parse_args(
            ["-i", "((a,b),c);", "-ta", "false", "-tl", "true"]
        )
        self.assertFalse(args.tip_labels_align)
        self.assertTrue(args.tip_labels)

    def test_parser_normalizes_format_case(self):
        """Normalize graphic format values to lowercase."""
        args = self.parser.parse_args(["-i", "((a,b),c);", "-f", "PNG"])
        self.assertEqual(args.format, "png")

    def test_parser_accepts_node_labels_style(self):
        """Accept node-label style entries through short and long options."""
        for option in ("-L", "--node-labels-style"):
            with self.subTest(option=option):
                args = self.parser.parse_args(
                    [
                        "-i",
                        "((a,b),c);",
                        option,
                        "font-size=12px",
                        "fill=red",
                    ]
                )
                self.assertEqual(
                    args.node_labels_style,
                    ["font-size=12px", "fill=red"],
                )

    def test_draw_applies_node_labels_style(self):
        """Apply CLI node-label styles to the rendered node-label group."""
        output = self.tmpdir / "styled-node-labels"
        args = self.parser.parse_args(
            [
                "-i",
                "((a,b),c);",
                "-o",
                str(output),
                "-f",
                "svg",
                "-nl",
                "idx",
                "-L",
                "font-size=12px",
                "fill=red",
            ]
        )
        self.assertEqual(run_draw(args), 0)

        svg = output.with_suffix(".svg").read_text(encoding="utf-8")
        start = svg.index('<g class="toytree-NodeLabels"')
        end = svg.index('<g class="toytree-TipLabels"', start)
        node_labels_svg = svg[start:end]
        self.assertIn("font-size:12px", node_labels_svg)
        self.assertIn("fill:rgb(100.0%,0.0%,0.0%)", node_labels_svg)

    def test_draw_rejects_malformed_node_labels_style(self):
        """Report malformed node-label style entries without a traceback."""
        cmd = [
            sys.executable,
            "-m",
            "toytree.cli.main",
            "draw",
            "-i",
            "((a,b),c);",
            "-o",
            str(self.tmpdir / "tree"),
            "-L",
            "font-size",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn(
            "Error: --node-labels-style expects key=value entries",
            proc.stderr,
        )
        self.assertNotIn("Traceback", proc.stderr)

    def test_draw_help_includes_node_labels_style(self):
        """Document the node-label style option and a visible-label example."""
        help_text = self.parser.format_help()
        self.assertIn("-L, --node-labels-style", help_text)
        self.assertIn("-nl idx -L font-size=12px fill=red", help_text)

    def test_draw_accepts_binary_input_path_ascii_mode(self):
        """Render deprecated text mode from a binary input path."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        bpath = self.tmpdir / "tree.bin"
        bpath.write_bytes(serialize_tree_binary(tree))
        args = self.parser.parse_args(["-i", str(bpath), "-a"])
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            run_draw(args)
        self.assertTrue(out.getvalue().strip())
        self.assertIn("toytree view", err.getvalue())

    def test_draw_accepts_binary_stdin_ascii_mode(self):
        """Render deprecated text mode from binary stdin."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        payload = serialize_tree_binary(tree)
        cmd = [sys.executable, "-m", "toytree.cli.main", "draw", "-i", "-", "-a"]
        proc = subprocess.run(cmd, input=payload, capture_output=True)
        self.assertEqual(
            proc.returncode, 0, msg=proc.stderr.decode("utf-8", errors="replace")
        )
        self.assertTrue(proc.stdout.decode("utf-8", errors="replace").strip())
        self.assertIn("toytree view", proc.stderr.decode("utf-8", errors="replace"))

    def test_draw_accepts_implicit_stdin_without_i(self):
        """Allow deprecated text mode to infer stdin input."""
        payload = "((a:1,b:1):1,c:1);\n"
        cmd = [sys.executable, "-m", "toytree.cli.main", "draw", "-a"]
        proc = subprocess.run(
            cmd,
            input=payload,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertTrue(proc.stdout.strip())
        self.assertIn("toytree view", proc.stderr)

    def test_draw_implicit_stdin_empty_input_errors_cleanly(self):
        """Return a clean error when draw text mode gets empty stdin."""
        cmd = [sys.executable, "-m", "toytree.cli.main", "draw", "-a"]
        proc = subprocess.run(cmd, input="", capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Error: no data received on stdin.", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_binary_pipe_into_draw_with_bare_ta(self):
        """Keep binary pipelines working through deprecated text mode."""
        tree_path = self.tmpdir / "tree.nwk"
        tree_path.write_text("((a:1,b:1):1,c:1);\n", encoding="utf-8")
        set_cmd = (
            f"{sys.executable} -m toytree.cli.main "
            f"set-node-data -i {tree_path} -f X -s a=1 -d 0 -b"
        )
        draw_cmd = f"{sys.executable} -m toytree.cli.main draw -i - -a -ta"
        cmd = f"{set_cmd} | " f"{draw_cmd}"
        proc = subprocess.run(["bash", "-lc", cmd], capture_output=True)
        self.assertEqual(
            proc.returncode, 0, msg=proc.stderr.decode("utf-8", errors="replace")
        )
        self.assertIn("toytree view", proc.stderr.decode("utf-8", errors="replace"))
