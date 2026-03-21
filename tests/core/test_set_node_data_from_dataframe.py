#!/usr/bin/env python


import pandas as pd
from conftest import PytestCompat

import toytree


class TestSetNodeDataFromDataFrame(PytestCompat):
    def setUp(self):
        self.tree = toytree.tree("((aa:1,ab:1):1,c:1);")

    def test_first_column_is_query_default(self):
        df = pd.DataFrame(
            {
                "query": ["aa", "ab"],
                "state": ["A", "B"],
            }
        )
        tre = self.tree.set_node_data_from_dataframe(df, inplace=False)
        data = tre.get_node_data("state")
        self.assertEqual(data.iloc[0], "A")
        self.assertEqual(data.iloc[1], "B")
        self.assertTrue(pd.isna(data.iloc[2]))

    def test_regex_queries_with_tilde_prefix(self):
        df = pd.DataFrame(
            {
                "state": ["X"],
            },
            index=["~^a"],
        )
        tre = self.tree.set_node_data_from_dataframe(df, inplace=False)
        data = tre.get_node_data("state")
        self.assertEqual(data.iloc[0], "X")
        self.assertEqual(data.iloc[1], "X")
        self.assertTrue(pd.isna(data.iloc[2]))

    def test_query_is_regex_prepends_tilde(self):
        df = pd.DataFrame(
            {
                0: ["^a", "^c"],
                1: ["G1", "G2"],
            }
        )
        tre = self.tree.set_node_data_from_dataframe(
            df,
            query_is_regex=True,
            table_headers=["group"],
            inplace=False,
        )
        data = tre.get_node_data("group")
        self.assertEqual(data.iloc[0], "G1")
        self.assertEqual(data.iloc[1], "G1")
        self.assertEqual(data.iloc[2], "G2")

    def test_unmatched_query_raises_clear_error(self):
        df = pd.DataFrame(
            {
                "query": ["does_not_match"],
                "state": ["X"],
            }
        )
        with self.assertRaisesRegex(Exception, "No Node names match query"):
            self.tree.set_node_data_from_dataframe(
                df,
                query_is_regex=True,
                inplace=False,
            )

    def test_allow_unmatched_query_skips_rows(self):
        df = pd.DataFrame(
            {
                "query": ["^a", "does_not_match"],
                "state": ["X", "Y"],
            }
        )
        tre = self.tree.set_node_data_from_dataframe(
            df,
            query_is_regex=True,
            allow_unmatched_queries=True,
            inplace=False,
        )
        data = tre.get_node_data("state")
        self.assertEqual(data.iloc[0], "X")
        self.assertEqual(data.iloc[1], "X")
        self.assertTrue(pd.isna(data.iloc[2]))

    def test_table_headers_length_must_match_features(self):
        df = pd.DataFrame(
            {
                0: ["aa", "ab"],
                1: ["A", "B"],
            }
        )
        with self.assertRaisesRegex(Exception, "table_headers length must match"):
            self.tree.set_node_data_from_dataframe(
                df,
                table_headers=["f1", "f2"],
                inplace=False,
            )

    def test_query_column_by_name(self):
        df = pd.DataFrame(
            {
                "state": ["A", "B"],
                "query": ["aa", "ab"],
            }
        )
        tre = self.tree.set_node_data_from_dataframe(
            df,
            query_column="query",
            inplace=False,
        )
        data = tre.get_node_data("state")
        self.assertEqual(data.iloc[0], "A")
        self.assertEqual(data.iloc[1], "B")
