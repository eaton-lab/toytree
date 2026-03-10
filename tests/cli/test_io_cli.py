#!/usr/bin/env python

"""Tests for io CLI tree conversion behavior."""

import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

from conftest import PytestCompat

import toytree
from toytree.cli._tree_transport import read_tree_auto, serialize_tree_binary
from toytree.cli.cli_io import run_io
from toytree.cli.subparsers import get_parser_io
from toytree.utils import ToytreeError


class TestIOCLI(PytestCompat):
    """Validate io command format conversion and metadata handling."""

    def setUp(self):
        """Create parser and temporary Newick input for each test."""
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-io-"))
        self.parser = get_parser_io()
        self.tree_path = self.tmpdir / "tree.nwk"
        self.tree_path.write_text(
            "((a:1[&X=1],b:1[&X=2])90:1,c:1)100:0;\n",
            encoding="utf-8",
        )

    def _run_capture_stdout(self, argv):
        args = self.parser.parse_args(argv)
        stream = io.StringIO()
        with redirect_stdout(stream):
            run_io(args)
        return stream.getvalue().strip()

    def test_default_newick_roundtrip_keeps_support_and_features(self):
        """Default text mode should keep support labels and metadata features."""
        out = self._run_capture_stdout(["-i", str(self.tree_path)])
        tree = toytree.tree(out)
        self.assertIn("X", tree.features)
        support = tree.get_node_data("support")
        self.assertIn(90.0, set(float(i) for i in support.dropna()))

    def test_binary_out_writes_transport_tree_payload(self):
        """Binary mode should serialize a transport payload with features intact."""
        outpath = self.tmpdir / "tree.bin"
        args = self.parser.parse_args(
            ["-i", str(self.tree_path), "-b", "-o", str(outpath)]
        )
        run_io(args)
        tree = read_tree_auto(str(outpath))
        self.assertEqual(tree.ntips, 3)
        self.assertIn("X", tree.features)

    def test_binary_in_binary_out_pass_through_preserves_payload(self):
        """Binary to binary should pass through identical bytes in io mode."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        inpath = self.tmpdir / "in.bin"
        outpath = self.tmpdir / "out.bin"
        payload = serialize_tree_binary(tree)
        inpath.write_bytes(payload)
        args = self.parser.parse_args(["-i", str(inpath), "-b", "-o", str(outpath)])
        run_io(args)
        self.assertEqual(outpath.read_bytes(), payload)

    def test_binary_in_to_newick_roundtrip(self):
        """Binary input should be converted back to parseable Newick text."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        tree = tree.set_node_data("grp", {"a": "A", "b": "B"}, default="C")
        binpath = self.tmpdir / "input.bin"
        binpath.write_bytes(serialize_tree_binary(tree))
        out = self._run_capture_stdout(["-i", str(binpath)])
        roundtrip = toytree.tree(out)
        self.assertIn("grp", roundtrip.features)
        self.assertEqual(roundtrip.get_node_data("grp").iloc[0], "A")

    def test_nexus_output_by_flag(self):
        """--nexus should force Nexus output to stdout."""
        out = self._run_capture_stdout(["-i", str(self.tree_path), "--nexus"])
        self.assertTrue(out.startswith("#NEXUS"))

    def test_nexus_output_by_output_suffix(self):
        """Output .nex suffix should auto-enable Nexus serialization."""
        outpath = self.tmpdir / "tree.nex"
        args = self.parser.parse_args(["-i", str(self.tree_path), "-o", str(outpath)])
        run_io(args)
        text = outpath.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("#NEXUS"))

    def test_exclude_features_suppresses_support_and_metadata(self):
        """-x should suppress support labels and metadata comments in text mode."""
        out = self._run_capture_stdout(["-i", str(self.tree_path), "-x"])
        self.assertNotIn("[&", out)
        tree = toytree.tree(out)
        self.assertNotIn("X", tree.features)
        support = tree.get_node_data("support")
        self.assertTrue(support.dropna().empty)

    def test_custom_input_feature_parse_args(self):
        """Input parse options should ingest non-default NHX formatting."""
        nhx_path = self.tmpdir / "tree.nhx"
        nhx_path.write_text(
            "((a[&&NHX:state=1]:1,b[&&NHX:state=2]:1):1,c:1);\n",
            encoding="utf-8",
        )
        out = self._run_capture_stdout(
            [
                "-i",
                str(nhx_path),
                "--in-feature-prefix",
                "&&NHX:",
                "--in-feature-delim",
                ":",
                "--in-feature-assignment",
                "=",
                "--in-feature-unpack",
                "|",
            ]
        )
        tree = toytree.tree(out)
        self.assertIn("state", tree.features)
        self.assertEqual(float(tree.get_node_data("state").iloc[0]), 1.0)

    def test_custom_input_feature_unpack_parses_list_values(self):
        """Custom input unpack token should split list-like metadata values."""
        nhx_path = self.tmpdir / "tree_list.nhx"
        nhx_path.write_text(
            "((a[&state=0.1;0.9]:1,b[&state=0.2;0.8]:1):1,c:1);\n",
            encoding="utf-8",
        )
        out = self._run_capture_stdout(
            [
                "-i",
                str(nhx_path),
                "--in-feature-unpack",
                ";",
            ]
        )
        tree = toytree.tree(out)
        self.assertEqual(tree.get_node_data("state").iloc[0], [0.1, 0.9])

    def test_write_single_feature_outputs_curly_brace_labels(self):
        """--write-single-feature should emit name{value} labels on all nodes."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        tree = tree.set_node_data("state", default=5)
        binpath = self.tmpdir / "state.bin"
        binpath.write_bytes(serialize_tree_binary(tree))

        out = self._run_capture_stdout(
            ["-i", str(binpath), "--write-single-feature", "state"]
        )
        self.assertIn("{5}", out)
        roundtrip = toytree.tree(out)
        self.assertIn("trait", roundtrip.features)
        values = {float(i) for i in roundtrip.get_node_data("trait")}
        self.assertEqual(values, {5.0})

    def test_write_single_feature_with_exclude_features_still_writes_curly_labels(self):
        """-x should suppress comments, while --write-single-feature remains active."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        tree = tree.set_node_data("state", default=5)
        binpath = self.tmpdir / "state_x.bin"
        binpath.write_bytes(serialize_tree_binary(tree))

        out = self._run_capture_stdout(
            ["-i", str(binpath), "-x", "--write-single-feature", "state"]
        )
        self.assertNotIn("[&", out)
        self.assertIn("{5}", out)

    def test_features_pack_custom_separator_writes_expected_values(self):
        """--features-pack should customize packed list-like metadata output."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        tree = tree.set_node_data("posterior", default=[0.25, 0.75])
        binpath = self.tmpdir / "packed.bin"
        binpath.write_bytes(serialize_tree_binary(tree))

        out = self._run_capture_stdout(["-i", str(binpath), "--features-pack", ";"])
        self.assertIn("[&posterior=0.25;0.75]", out)
        parsed = toytree.tree(out, feature_unpack=";")
        self.assertEqual(parsed.get_node_data("posterior").iloc[0], [0.25, 0.75])

    def test_write_single_feature_rejected_with_binary_out(self):
        """--write-single-feature should error when -b binary output is requested."""
        args = self.parser.parse_args(
            ["-i", str(self.tree_path), "-b", "--write-single-feature", "X"]
        )
        with self.assertRaisesRegex(
            ToytreeError,
            "--write-single-feature is only valid for text output",
        ):
            run_io(args)

    def test_write_single_feature_rejected_with_nexus_flag(self):
        """--write-single-feature should error when --nexus output is requested."""
        args = self.parser.parse_args(
            ["-i", str(self.tree_path), "--nexus", "--write-single-feature", "X"]
        )
        with self.assertRaisesRegex(
            ToytreeError,
            "--write-single-feature is not supported for Nexus output",
        ):
            run_io(args)

    def test_write_single_feature_rejected_with_nexus_output_suffix(self):
        """--write-single-feature should error for .nex/.nexus output suffixes."""
        outpath = self.tmpdir / "out.nex"
        args = self.parser.parse_args(
            [
                "-i",
                str(self.tree_path),
                "-o",
                str(outpath),
                "--write-single-feature",
                "X",
            ]
        )
        with self.assertRaisesRegex(
            ToytreeError,
            "--write-single-feature is not supported for Nexus output",
        ):
            run_io(args)

    def test_features_pack_conflict_raises(self):
        """Packed-value separator cannot match metadata delimiters."""
        args = self.parser.parse_args(
            [
                "-i",
                str(self.tree_path),
                "--features-pack",
                ",",
            ]
        )
        with self.assertRaisesRegex(
            ToytreeError,
            "--features-pack cannot match --features-delim or --features-assignment",
        ):
            run_io(args)
