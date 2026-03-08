#!/usr/bin/env python

import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import toytree
from toytree.cli.cli_make_ultrametric import (
    NEGATIVE_CAL_QUERY_PREFIX,
    get_parser_make_ultrametric,
    run_make_ultrametric,
    _parse_calibrations,
    normalize_calibration_argv,
)
from toytree.utils import ToytreeError



from conftest import PytestCompat

class TestMakeUltrametricCLI(PytestCompat):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-make-ultrametric-"))
        self.tree_path = self.tmpdir / "tree.nwk"
        # non-ultrametric input
        self.tree_path.write_text("((a:1,b:2):1,c:1);\n", encoding="utf-8")
        self.parser = get_parser_make_ultrametric()

    def _run_capture_stdout(self, argv):
        args = self.parser.parse_args(argv)
        stream = io.StringIO()
        with redirect_stdout(stream):
            run_make_ultrametric(args)
        return stream.getvalue().strip()

    def test_extend_method_makes_tree_ultrametric(self):
        out_nwk = self._run_capture_stdout(
            ["-i", str(self.tree_path), "--method", "extend"]
        )
        tree = toytree.tree(out_nwk)
        self.assertTrue(tree.is_ultrametric())

    def test_discrete_requires_ncategories(self):
        args = self.parser.parse_args(["-i", str(self.tree_path), "--method", "discrete"])
        with self.assertRaises(ToytreeError):
            run_make_ultrametric(args)

    def test_lam_must_be_non_negative(self):
        args = self.parser.parse_args(
            ["-i", str(self.tree_path), "--method", "relaxed", "--lam", "-0.1"]
        )
        with self.assertRaises(ToytreeError):
            run_make_ultrametric(args)

    def test_parse_calibrations_single_and_range(self):
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        cals = _parse_calibrations(tree, ["-1=1.0", "a=0.1-0.2"])
        self.assertIn(tree[-1].idx, cals)
        self.assertEqual(cals[tree[-1].idx], 1.0)
        self.assertEqual(cals[tree[0].idx], (0.1, 0.2))

    def test_cli_calibrations_accept_negative_node_query_token(self):
        argv = normalize_calibration_argv(
            ["-i", str(self.tree_path), "--method", "clock", "-c", "-1=1.0"]
        )
        args = self.parser.parse_args(argv)
        self.assertEqual(args.calibrations, [f"{NEGATIVE_CAL_QUERY_PREFIX}1=1.0"])

    def test_correlated_method_runs(self):
        out_nwk = self._run_capture_stdout(
            [
                "-i",
                str(self.tree_path),
                "--method",
                "correlated",
                "--lam",
                "0.5",
                "--max-iter",
                "200",
                "--max-fun",
                "200",
                "--max-refine",
                "2",
                "--nstarts",
                "2",
                "--ncores",
                "2",
                "--seed",
                "3",
            ]
        )
        tree = toytree.tree(out_nwk)
        self.assertTrue(tree.is_ultrametric())

    def test_discrete_estimate_runs_without_ncat(self):
        out_nwk = self._run_capture_stdout(
            [
                "-i",
                str(self.tree_path),
                "--method",
                "discrete",
                "--estimate",
                "3",
                "--max-iter",
                "200",
                "--max-fun",
                "200",
                "--max-refine",
                "2",
            ]
        )
        tree = toytree.tree(out_nwk)
        self.assertTrue(tree.is_ultrametric())

    def test_estimate_invalid_for_clock(self):
        args = self.parser.parse_args(
            ["-i", str(self.tree_path), "--method", "clock", "--estimate", "3"]
        )
        with self.assertRaises(ToytreeError):
            run_make_ultrametric(args)


