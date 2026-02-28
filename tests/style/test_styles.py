#!/usr/bin/env python

"""Tests using validate_style to test draw/style args.

"""

import unittest
import numpy as np
# import toyplot
import toytree
# from toytree.color import ToyColor
from toytree.style import TreeStyle, validate_style
from toytree.utils import ToytreeError
from toytree.style.src.validate_data import (
    validate_mask,
    validate_numeric,
    validate_markers,
    validate_colors,
    validate_hover,
    validate_labels,
    validate_admixture_edges,
)



class TestValidateStyle(unittest.TestCase):

    def setUp(self):
        self.tree = toytree.rtree.unittree(10, seed=123)
        self.style = TreeStyle()
        self.cycler = toytree.color.color_cycler()

    def test_style_copy(self):
        """Copying a style should deepcopy (copies of substyles and dicts)."""
        _ = self.tree.style.copy()


    def test_style_raise_exception_on_validate_bad_color(self):
        """show style in notebook without fail on complex settings."""
        self.style.node_colors = "..."
        with self.assertRaises(ToytreeError):
            validate_style(self.tree, self.style)


class TestValidateMask(unittest.TestCase):

    def setUp(self):
        self.tree = toytree.rtree.unittree(5, seed=123)

    def test_style_validate_mask(self):
        tests = [
            True,
            False,
            np.zeros(self.tree.nnodes, dtype=np.bool_),        
            np.ones(self.tree.nnodes, dtype=np.bool_),
            self.tree.get_node_mask(),
            self.tree.get_node_mask(2, 3, 4),
            self.tree.get_node_mask(2, 3, 4, show_tips=True),
            self.tree.get_node_mask(2, 3, 4, show_internal=True),
            self.tree.get_node_mask(2, 3, 4, show_root=True),
            (1, 1, 0),
            (0, 0, 0),
        ]
        for arg in tests:
            validate_mask(
                tree=self.tree, tree_style=self.tree.style,
                style={"node_mask": arg})

    def test_style_raise_on_bad_mask(self):
        """..."""


class TestValidateNumeric(unittest.TestCase):

    def setUp(self):
        self.tree = toytree.rtree.unittree(5, seed=123)

    def test_style_validate_numeric_int(self):
        tree = self.tree.copy()
        tree.style.node_sizes = 10
        vals = validate_numeric(
            tree=tree,
            key="node_sizes",
            size=tree.nnodes,
            tree_style=tree.style,
            style={},
        )
        self.assertTrue(isinstance(vals, np.ndarray))
        self.assertEqual(vals[0], 10)
        self.assertTrue(isinstance(vals[0], np.integer))
        self.assertTrue(all(i == 10 for i in vals))

    def test_style_validate_numeric_int_array(self):
        tree = self.tree.copy()
        tree.style.node_sizes = np.arange(tree.nnodes)
        vals = validate_numeric(
            tree=tree,
            key="node_sizes",
            size=tree.nnodes,
            tree_style=tree.style,
            style={},
        )
        self.assertTrue(isinstance(vals, np.ndarray))
        self.assertEqual(vals[1], 1)
        self.assertTrue(isinstance(vals[1], np.integer))

    def test_style_validate_numeric_float_with_nan(self):
        tree = self.tree.copy()
        tree.style.node_sizes = np.ones(tree.nnodes)
        tree.style.node_sizes[3] = np.nan
        vals = validate_numeric(
            tree=tree,
            key="node_sizes",
            size=tree.nnodes,
            tree_style=tree.style,
            style={},
        )
        self.assertTrue(isinstance(vals, np.ndarray))
        self.assertEqual(vals[1], 1.0)
        self.assertTrue(isinstance(vals[1], np.float64))
        self.assertTrue(np.isnan(vals[3]))

    def test_style_validate_numeric_none(self):
        """None should return array of 0 of correct length"""
        tree = self.tree.copy()
        tree.style.node_sizes = None
        vals = validate_numeric(
            tree=tree,
            key="node_sizes",
            size=tree.nnodes,
            tree_style=tree.style,
            style={},
        )
        self.assertTrue(isinstance(vals, np.ndarray))
        self.assertEqual(vals[0], 0.0)
        self.assertTrue(isinstance(vals[1], np.integer))

    # def test_style_validate_numeric_tuple_format(self):
    #     tree = self.tree.copy()
    #     for test in [
    #         "dist",                 # (dist, 5, 20)
    #         ("dist",),              # (dist, 5, 20)
    #         # ("dist", 2),          # (dist, 2, 20)
    #         # ("dist", 2, 5),       # (dist, 2, 5)
    #         # ("dist", 2, 5, 0),    # (dist, 2, 5, 0)
    #         ]:
    #         tree.style.node_sizes = test
    #         vals = validate_numeric(
    #             tree=tree,
    #             key="node_sizes",
    #             size=tree.nnodes,
    #             tree_style=tree.style,
    #             style={},
    #         )
    #         self.assertTrue(isinstance(vals, np.ndarray))
    #         self.assertEqual(vals[0], 1 / 3.)
    #         self.assertTrue(isinstance(vals[1], np.float64))



    def test_style_validate_numeric_nnodes(self):
        self.tree.style.node_sizes = 5.
        tests = [
            None,  # gets it from .style instead of from arg
            np.full(self.tree.nnodes, 5.),
            np.arange(self.tree.nnodes, dtype=np.float64),
            5.,
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            [0, 1, 2, 3, 4, 5., 6., 7., 8.],
            [0, 1, 2, 3, 4, 5., 6., np.nan, np.nan],
            ('dist',),
            ('dist', 0, 5),
            ('support', 0, 5, 5.),
        ]
        for arg in tests:
            vals = validate_numeric(
                tree=self.tree,
                key="node_sizes",
                tree_style=self.tree.style,
                size=self.tree.nnodes,
                style={"node_sizes": arg, "other": '...'})
            print(vals)
            self.assertTrue(len(vals) == self.tree.nnodes)
            self.assertTrue(len(vals) == self.tree.nnodes)            





    # def test_style_validate_multi_colors(self):
    #     """show style in notebook without fail on complex settings."""
    #     self.style.node_colors = ["red"] + ["blue"] * (self.tree.nnodes - 1)
    #     self.style.tip_labels_colors = [next(self.cycler) for i in range(self.tree.ntips)]
    #     # self.style.node_labels_style.stroke = ToyColor((1, 0, 0.5, 0.5))
    #     # self.style.edge_colors = (1, 0, 0.5, 0.5)
    #     validate_style(self.tree, self.style)



if __name__ == "__main__":
    unittest.main()
