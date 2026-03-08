#!/usr/bin/env python

"""Tests for anc-state-discrete CLI model fitting and reconstruction."""

from __future__ import annotations

import io
import pickle
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from conftest import PytestCompat

import toytree
from toytree.cli.cli_anc_state_discrete import run_anc_state_discrete
from toytree.cli.subparsers import get_parser_anc_state_discrete
from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError


class TestAncStateDiscreteCLI(PytestCompat):
    """Validate discrete CTMC fitting and ancestral-state CLI behavior."""

    def setUp(self):
        """Create a small tree with one discrete tip feature for testing."""
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-anc-state-discrete-"))
        self.tree_path = self.tmpdir / "tree.nwk"
        self.tree_path.write_text(
            "((a[&X=A]:1,b[&X=B]:1):1,c[&X=A]:1);\n",
            encoding="utf-8",
        )
        self.parser = get_parser_anc_state_discrete()

    def _run_capture(self, argv):
        """Run command args and return captured stdout and stderr strings."""
        args = self.parser.parse_args(argv)
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            run_anc_state_discrete(args)
        return out.getvalue().strip(), err.getvalue().strip()

    def test_default_outputs_newick_with_packed_posteriors(self):
        """Default mode should emit Newick with MAP and packed posterior metadata."""
        out, err = self._run_capture(
            ["-i", str(self.tree_path), "-f", "X", "-n", "2", "-m", "ER"]
        )
        tree = toytree.tree(out)
        self.assertIn("X_anc", tree.features)
        self.assertIn("X_anc_posterior", tree.features)
        posterior = tree.get_node_data("X_anc_posterior").dropna().iloc[0]
        self.assertIn("|", str(posterior))
        self.assertEqual("", err)

    def test_split_posterior_mode_and_meta_base(self):
        """Split mode should store per-state posterior features under meta base."""
        out, _ = self._run_capture(
            [
                "-i",
                str(self.tree_path),
                "-f",
                "X",
                "-n",
                "2",
                "--posterior-mode",
                "split",
                "--meta-base",
                "Y",
            ]
        )
        tree = toytree.tree(out)
        self.assertIn("Y_anc", tree.features)
        self.assertIn("Y_anc_p0", tree.features)
        self.assertIn("Y_anc_p1", tree.features)
        self.assertNotIn("Y_anc_posterior", tree.features)

    def test_none_posterior_mode_omits_posterior_features(self):
        """Posterior mode none should emit only reconstructed MAP states."""
        out, _ = self._run_capture(
            [
                "-i",
                str(self.tree_path),
                "-f",
                "X",
                "-n",
                "2",
                "--posterior-mode",
                "none",
            ]
        )
        tree = toytree.tree(out)
        self.assertIn("X_anc", tree.features)
        self.assertNotIn("X_anc_posterior", tree.features)
        self.assertFalse(any(i.startswith("X_anc_p") for i in tree.features))

    def test_binary_output_writes_pickled_toytree(self):
        """Binary mode should emit a pickle payload containing a ToyTree object."""
        out_path = self.tmpdir / "anc.bin"
        args = self.parser.parse_args(
            [
                "-i",
                str(self.tree_path),
                "-f",
                "X",
                "-n",
                "2",
                "-b",
                "-o",
                str(out_path),
            ]
        )
        run_anc_state_discrete(args)
        payload = out_path.read_bytes()
        obj = pickle.loads(payload)
        self.assertIsInstance(obj, ToyTree)
        self.assertIn("X_anc", obj.features)

    def test_missing_trait_feature_raises(self):
        """Trait lookup should fail when requested feature is not on the tree."""
        args = self.parser.parse_args(["-i", str(self.tree_path), "-f", "Z", "-n", "2"])
        with self.assertRaises(ToytreeError):
            run_anc_state_discrete(args)

    def test_posterior_separator_conflict_raises(self):
        """Packed separator conflicts with metadata delimiters should raise error."""
        args = self.parser.parse_args(
            [
                "-i",
                str(self.tree_path),
                "-f",
                "X",
                "-n",
                "2",
                "--posterior-sep",
                ",",
            ]
        )
        with self.assertRaises(ToytreeError):
            run_anc_state_discrete(args)

    def test_output_format_option_is_not_supported(self):
        """Legacy output-format arg should be rejected by parser."""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(
                [
                    "-i",
                    str(self.tree_path),
                    "-f",
                    "X",
                    "-n",
                    "2",
                    "--output-format",
                    "tsv",
                ]
            )

    def test_trait_option_is_not_supported(self):
        """Legacy trait arg should be rejected by parser."""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(
                [
                    "-i",
                    str(self.tree_path),
                    "-t",
                    "X",
                    "-n",
                    "2",
                ]
            )

    def test_full_prints_fit_summary_to_stderr(self):
        """Full mode should emit fitted model summary and parameters to stderr."""
        _, err = self._run_capture(
            [
                "-i",
                str(self.tree_path),
                "-f",
                "X",
                "-n",
                "2",
                "--full",
            ]
        )
        self.assertIn("feature=X", err)
        self.assertIn("model=ER", err)
        self.assertIn("AIC=", err)
        self.assertIn("state_frequencies=", err)
        self.assertIn("relative_rates=", err)
        self.assertIn("qmatrix=", err)
