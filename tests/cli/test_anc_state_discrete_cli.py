#!/usr/bin/env python

"""Tests for anc-state-discrete CLI model fitting and reconstruction."""

from __future__ import annotations

import io
import json
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from conftest import PytestCompat

import toytree
from toytree.cli._tree_transport import read_tree_auto
from toytree.cli.cli_anc_state_discrete import run_anc_state_discrete
from toytree.cli.subparsers import get_parser_anc_state_discrete
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
        self.assertIsInstance(posterior, list)
        self.assertEqual(len(posterior), 2)
        self.assertAlmostEqual(sum(float(i) for i in posterior), 1.0, places=6)
        self.assertEqual("", err)

    def test_binary_output_writes_transport_payload(self):
        """Binary mode should emit transport payload containing a ToyTree."""
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
        obj = read_tree_auto(str(out_path))
        self.assertIn("X_anc", obj.features)
        self.assertIn("X_anc_posterior", obj.features)
        posterior = obj.get_node_data("X_anc_posterior").dropna().iloc[0]
        self.assertFalse(isinstance(posterior, str))

    def test_missing_trait_feature_raises(self):
        """Trait lookup should fail when requested feature is not on the tree."""
        args = self.parser.parse_args(["-i", str(self.tree_path), "-f", "Z", "-n", "2"])
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

    def test_meta_base_option_is_not_supported(self):
        """Reconstruction metadata base arg should be rejected by parser."""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(
                [
                    "-i",
                    str(self.tree_path),
                    "-f",
                    "X",
                    "-n",
                    "2",
                    "--meta-base",
                    "Y",
                ]
            )

    def test_posterior_mode_option_is_not_supported(self):
        """Posterior mode arg should be rejected by parser."""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(
                [
                    "-i",
                    str(self.tree_path),
                    "-f",
                    "X",
                    "-n",
                    "2",
                    "--posterior-mode",
                    "split",
                ]
            )

    def test_posterior_separator_option_is_not_supported(self):
        """Posterior separator arg should be rejected by parser."""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(
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

    def test_output_feature_formatting_options_are_not_supported(self):
        """Output formatting should be handled via `toytree io`, not this command."""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(
                [
                    "-i",
                    str(self.tree_path),
                    "-f",
                    "X",
                    "-n",
                    "2",
                    "--features-prefix",
                    "&&NHX:",
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
        self.assertNotIn("meta_base=", err)
        self.assertNotIn("posterior_mode=", err)

    def test_json_prints_structured_fit_summary_to_stderr(self):
        """JSON mode should emit structured model-fit summary to stderr."""
        _, err = self._run_capture(
            [
                "-i",
                str(self.tree_path),
                "-f",
                "X",
                "-n",
                "2",
                "--json",
            ]
        )
        payload = json.loads(err)
        self.assertEqual(payload["feature"], "X")
        self.assertEqual(payload["model"], "ER")
        self.assertEqual(payload["nstates"], 2)
        self.assertIn("AIC", payload)
        self.assertIn("qmatrix", payload)

    def test_warns_when_internal_node_states_are_present(self):
        """CLI should surface the shared API warning for constrained nodes."""
        tree = toytree.tree(self.tree_path)
        tree = tree.set_node_data(
            "X",
            {0: "A", 1: "B", 2: "A", 3: "B"},
            default=None,
            inplace=False,
        )
        internal_path = self.tmpdir / "tree_internal.nwk"
        internal_path.write_text(tree.write(features=["X"]) + "\n", encoding="utf-8")

        out, err = self._run_capture(
            ["-i", str(internal_path), "-f", "X", "-n", "2", "-m", "ER"]
        )
        self.assertIn("warning:", err)
        self.assertIn("1 non-missing internal node state(s)", err)
        self.assertIn("treated as fixed constraints", err)
        self.assertTrue(out.endswith(";"))
