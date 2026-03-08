#!/usr/bin/env python

import io
import tempfile
import warnings
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd
from pandas.errors import ParserWarning

import toytree
from toytree.cli.cli_set_node_data import run_set_node_data
from toytree.cli.subparsers import get_parser_set_node_data
from toytree.utils import ToytreeError



from conftest import PytestCompat

class TestSetNodeDataCLI(PytestCompat):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-set-node-data-"))
        self.tree_path = self.tmpdir / "tree.nwk"
        self.tree_path.write_text("((a:1,b:2)90:3,c:4)100:0;\n")
        self.parser = get_parser_set_node_data()

    def _run_capture_stdout(self, argv):
        args = self.parser.parse_args(argv)
        stream = io.StringIO()
        with redirect_stdout(stream):
            run_set_node_data(args)
        return stream.getvalue().strip()

    def test_mapping_mode_sets_feature_and_default(self):
        out_nwk = self._run_capture_stdout(
            [
                "-i",
                str(self.tree_path),
                "--feature",
                "color",
                "--set",
                "a='red'",
                "b='blue'",
                "--default",
                "'gray'",
            ]
        )
        tree = toytree.tree(out_nwk)
        data = tree.get_node_data("color")
        self.assertEqual(data.iloc[0], "red")
        self.assertEqual(data.iloc[1], "blue")
        self.assertEqual(data.iloc[2], "gray")

    def test_table_mode_tab_comma_space(self):
        # tab-separated table
        tab_path = self.tmpdir / "data.tsv"
        tab_path.write_text("idx\ttrait\n0\t1\n1\t2\n3\t9\n")
        out_nwk = self._run_capture_stdout(
            ["-i", str(self.tree_path), "--table", str(tab_path), "--table-sep", "\t"]
        )
        tree = toytree.tree(out_nwk)
        self.assertEqual(int(tree.get_node_data("trait").iloc[0]), 1)
        self.assertEqual(int(tree.get_node_data("trait").iloc[1]), 2)
        self.assertEqual(int(tree.get_node_data("trait").iloc[3]), 9)

        # comma-separated table
        csv_path = self.tmpdir / "data.csv"
        csv_path.write_text("idx,trait\n0,5\n2,7\n")
        out_nwk = self._run_capture_stdout(
            ["-i", str(self.tree_path), "--table", str(csv_path), "--table-sep", ","]
        )
        tree = toytree.tree(out_nwk)
        self.assertEqual(int(tree.get_node_data("trait").iloc[0]), 5)
        self.assertEqual(int(tree.get_node_data("trait").iloc[2]), 7)

        # space-separated table
        sp_path = self.tmpdir / "data.space.txt"
        sp_path.write_text("idx trait\n0 11\n1 13\n")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ParserWarning)
            out_nwk = self._run_capture_stdout(
                ["-i", str(self.tree_path), "--table", str(sp_path), "--table-sep", " "]
            )
        tree = toytree.tree(out_nwk)
        self.assertEqual(int(tree.get_node_data("trait").iloc[0]), 11)
        self.assertEqual(int(tree.get_node_data("trait").iloc[1]), 13)

    def test_table_mode_headers_and_regex_queries(self):
        path = self.tmpdir / "data_no_header.tsv"
        path.write_text("^[ab]\tgroup1\n^c\tgroup2\n", encoding="utf-8")
        out_nwk = self._run_capture_stdout(
            [
                "-i",
                str(self.tree_path),
                "--table",
                str(path),
                "--table-sep",
                "\\t",
                "--table-headers",
                "group",
                "--table-query-regex",
            ]
        )
        tree = toytree.tree(out_nwk)
        data = tree.get_node_data("group")
        self.assertEqual(data.iloc[0], "group1")
        self.assertEqual(data.iloc[1], "group1")
        self.assertEqual(data.iloc[2], "group2")

    def test_table_mode_allow_unmatched_queries(self):
        path = self.tmpdir / "data_regex.tsv"
        path.write_text("query\ttrait\n^a\tA\n^z\tZ\n", encoding="utf-8")
        out_nwk = self._run_capture_stdout(
            [
                "-i",
                str(self.tree_path),
                "--table",
                str(path),
                "--table-query-regex",
                "--table-allow-unmatched",
            ]
        )
        tree = toytree.tree(out_nwk)
        data = tree.get_node_data("trait")
        self.assertEqual(data.iloc[0], "A")
        self.assertTrue(pd.isna(data.iloc[1]))
        self.assertTrue(pd.isna(data.iloc[2]))

    def test_table_mode_query_column_by_name(self):
        path = self.tmpdir / "data_query_col.tsv"
        path.write_text("group,query\nG1,a\nG2,b\n", encoding="utf-8")
        out_nwk = self._run_capture_stdout(
            [
                "-i",
                str(self.tree_path),
                "--table",
                str(path),
                "--table-sep",
                ",",
                "--table-query-column",
                "query",
            ]
        )
        tree = toytree.tree(out_nwk)
        data = tree.get_node_data("group")
        self.assertEqual(data.iloc[0], "G1")
        self.assertEqual(data.iloc[1], "G2")

    def test_requires_exactly_one_mode(self):
        args = self.parser.parse_args(["-i", str(self.tree_path)])
        with self.assertRaises(ToytreeError):
            run_set_node_data(args)
        args = self.parser.parse_args(
            [
                "-i",
                str(self.tree_path),
                "--feature",
                "x",
                "--set",
                "0=1",
                "--table",
                str(self.tree_path),
            ]
        )
        with self.assertRaises(ToytreeError):
            run_set_node_data(args)

    def test_output_feature_formatting_options(self):
        out_nwk = self._run_capture_stdout(
            [
                "-i",
                str(self.tree_path),
                "--feature",
                "trait",
                "--set",
                "0=1",
                "--default",
                "0",
                "--features-prefix",
                "&&NHX:",
                "--features-delim",
                ":",
                "--features-assignment",
                "=",
                "--features-formatter",
                "%.3f",
            ]
        )
        self.assertIn("[&&NHX:trait=1.000]", out_nwk)

