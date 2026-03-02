#!/usr/bin/env python

"""Tests for optional ipcoal simulation wrapper."""

import unittest
from unittest.mock import patch

import pandas as pd

import toytree
from toytree import MultiTree, ToyTree
from toytree.external.src.ipcoal_sim import ipcoal_sim_trees
from toytree.utils import ToytreeError


class _FakeIPCoal:
    """Fake ipcoal module for deterministic wrapper tests."""

    class Model:
        """Fake ipcoal Model with configurable df output."""

        nrows = 1

        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.df = pd.DataFrame()

        def sim_trees(self, **kwargs):
            nrows = int(kwargs.get("ntrees", self.nrows))
            self.df = pd.DataFrame(
                {"genealogy": ["((a:1,b:1):1,c:1);" for _ in range(nrows)]}
            )


class TestIPCoalSimTrees(unittest.TestCase):
    """Validate runtime import and return-shape behavior."""

    def setUp(self):
        """Create a small species tree fixture."""
        self.sptree = toytree.tree("((a:1,b:1):1,c:1);")

    @patch("toytree.external.src.ipcoal_sim._import_ipcoal")
    def test_runtime_import_error_message(self, mock_import):
        """Raise a clear install error if ipcoal is missing."""
        mock_import.side_effect = ToytreeError("ipcoal missing")
        with self.assertRaises(ToytreeError):
            ipcoal_sim_trees(self.sptree, Ne=1000, ntrees=1)

    @patch("toytree.external.src.ipcoal_sim._import_ipcoal")
    def test_return_toytree_when_one_tree(self, mock_import):
        """Return ToyTree when one simulated genealogy is present."""
        mock_import.return_value = _FakeIPCoal
        out = ipcoal_sim_trees(self.sptree, Ne=1000, ntrees=1, return_df=False)
        self.assertIsInstance(out, ToyTree)

    @patch("toytree.external.src.ipcoal_sim._import_ipcoal")
    def test_return_multitree_when_multiple_trees(self, mock_import):
        """Return MultiTree when multiple genealogies are simulated."""
        mock_import.return_value = _FakeIPCoal
        out = ipcoal_sim_trees(self.sptree, Ne=1000, ntrees=3, return_df=False)
        self.assertIsInstance(out, MultiTree)
        self.assertEqual(out.ntrees, 3)

    @patch("toytree.external.src.ipcoal_sim._import_ipcoal")
    def test_return_df_when_requested(self, mock_import):
        """Return model.df when return_df is True."""
        mock_import.return_value = _FakeIPCoal
        out = ipcoal_sim_trees(self.sptree, Ne=1000, ntrees=2, return_df=True)
        self.assertIsInstance(out, pd.DataFrame)
        self.assertEqual(out.shape[0], 2)

    def test_validate_species_tree_type(self):
        """Reject non-ToyTree species_tree."""
        with self.assertRaises(ToytreeError):
            ipcoal_sim_trees("((a,b),c);", Ne=1000, ntrees=1)

    def test_validate_ntrees(self):
        """Reject invalid ntrees values."""
        with self.assertRaises(ToytreeError):
            ipcoal_sim_trees(self.sptree, Ne=1000, ntrees=0)


if __name__ == "__main__":
    unittest.main()
