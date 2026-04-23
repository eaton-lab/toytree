#!/usr/bin/env python

"""Test validation of tree drawing style arguments in ``TreeStyle``.

TreeStyle is a DataClass with a serialized repr. It does not validate
values during setting; instead, a validator is run instide of .draw
when the tree is drawn.
"""

import numpy as np
import toyplot
from conftest import PytestCompat

import toytree
from toytree.core import TreeStyle
from toytree.drawing.src.validate_style import validate_style
from toytree.utils import ToytreeError


class Devnull(object):
    """Fake stream to test repr"""

    def write(self, *_):
        pass


class TestValidator(PytestCompat):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(10, seed=123, treeheight=10)
        self.btree = toytree.rtree.baltree(10, seed=123, treeheight=10)
        self.utree = toytree.rtree.unittree(10, seed=123, treeheight=10)
        self.trees = [self.itree, self.btree, self.utree]

    def test_node_colormap_style_repr_before_validation(self):
        """Set node colormap on style dict and show repr (json) w/o error."""
        tree = self.itree
        colors = [
            ("dist", "BlueRed"),
            ("dist", toyplot.color.brewer.map("BlueRed")),
            toytree.color.ToyColor((0, 1, 0, 0.5)),
            (0, 1, 0.5, 0.5),
            "red",
            ["blue"] + ["red"] * (tree.nnodes - 1),
        ]
        for color_arg in colors:
            style = TreeStyle()
            style.node_colors = color_arg
            print(style, file=Devnull)

    def test_node_colormap_support_nan(self):
        """Set nan values to transparent when color mapping."""
        # only set some data, others have nan.
        svals = {11: 0, 12: 50, 13: 75, 14: 100}
        tree = self.itree.set_node_data("support", svals)
        vals = tree.get_node_data("support").values
        colors = toytree.data.get_color_mapped_feature(
            tree=tree,
            feature="support",
            cmap="BlueRed",
            domain_min=0,
            domain_max=10,
        )

        # assert nans were converted to transparent
        pre = np.where(np.isnan(vals))
        post = np.where(colors == toytree.color.ToyColor("transparent"))
        self.assertEqual(list(pre[0]), list(post[0]))

    def test_node_style_opacity_overrule(self):
        """... opacity should overrule orig fill color opacity."""
        tree = self.itree
        style = TreeStyle()
        style.node_colors = ["red"] + ["blue"] * (tree.nnodes - 1)
        style.node_style.fill_opacity = 0.2
        validate_style(tree, style)
        # print(style.node_colors)

        style = TreeStyle()
        style.node_colors = ("dist", "BlueRed")
        style.node_style.fill_opacity = 0.2
        validate_style(tree, style)
        # self.assertEqual()

    def test_draw_accepts_node_color_dict_format(self):
        """Draw should accept dict-format feature color mapping for nodes."""
        tree = self.itree
        colors = {
            "feature": "dist",
            "cmap": "BlueRed",
            "domain_min": 0,
            "domain_max": 10,
        }
        canvas, axes, mark = tree.draw(
            node_sizes=10,
            node_mask=False,
            node_colors=colors,
        )
        expected = toytree.data.get_color_mapped_feature(
            tree,
            "dist",
            cmap="BlueRed",
            domain_min=0,
            domain_max=10,
        )
        self.assertIsNotNone(canvas)
        self.assertIsNotNone(axes)
        self.assertTrue(np.array_equal(mark.node_colors, expected))

    def test_draw_accepts_edge_color_dict_format(self):
        """Draw should accept dict-format feature color mapping for edges."""
        tree = self.itree
        canvas, axes, mark = tree.draw(
            edge_colors={"feature": "idx", "cmap": "BlueRed", "reverse": True}
        )
        self.assertIsNotNone(canvas)
        self.assertIsNotNone(axes)
        self.assertEqual(len(mark.edge_colors), tree.nnodes)

    def test_draw_accepts_tip_label_color_dict_format(self):
        """Draw should accept dict-format feature color mapping for tip labels."""
        tree = self.itree
        canvas, axes, mark = tree.draw(
            tip_labels_colors={
                "feature": "idx",
                "cmap": "BlueRed",
                "domain_min": 0,
                "domain_max": tree.ntips - 1,
            }
        )
        self.assertIsNotNone(canvas)
        self.assertIsNotNone(axes)
        self.assertEqual(len(mark.tip_labels_colors), tree.ntips)

    def test_draw_rejects_dict_color_mapping_missing_feature(self):
        """Dict-format color mapping requires a feature key."""
        with self.assertRaises(ToytreeError):
            self.itree.draw(node_colors={"cmap": "BlueRed"})

    def test_draw_rejects_dict_color_mapping_non_string_feature(self):
        """Dict-format color mapping requires feature to be a string."""
        with self.assertRaises(ToytreeError):
            self.itree.draw(node_colors={"feature": 3, "cmap": "BlueRed"})

    def test_draw_rejects_dict_color_mapping_unknown_keys(self):
        """Dict-format color mapping rejects unknown kwargs."""
        with self.assertRaises(ToytreeError):
            self.itree.draw(
                node_colors={"feature": "dist", "cmap": "BlueRed", "bogus": 1}
            )

    def test_draw_rejects_dict_color_mapping_tips_only(self):
        """Dict-format color mapping infers tips_only from context."""
        with self.assertRaises(ToytreeError):
            self.itree.draw(
                node_colors={
                    "feature": "dist",
                    "cmap": "BlueRed",
                    "tips_only": True,
                }
            )

    # def test_edge_style_opacity_overrule_2(self):
    #     """..."""
    #     tree = self.itree
    #     tree.style.edge_colors = ['red'] + ['blue'] * (tree.nnodes - 1)
    #     tree.style.edge_style.stroke_opacity = 0.2
    #     style = tree.style.copy()
    #     # validate_style(tree, style)
    #     # print(style.node_colors)

    # def test_set_nan_node_labels_empty_string(self):
    #     """np.nan values on node labels should validate to empty strings."""
    #     self.itree.style.node_colors = "red"
    # style = self.itree.style._validate()
    # self.assertEqual(style, dict...)

    # def test_node_size_to_zeros_for_empty_labels(self):
    #     """Do this?"""

    # def test_node_labels_round_floats_on_validate(self):
    #     """..."""
    #     self.btree.treenode.children[0].support = 99.99
    #     self.btree.treenode.children[1].support = 10

    # def test_anchor_shift_legacy_support(self):
    #     """Support -toyplot-anchor-shift as legacy to anchor-shift."""

    # assert warning message is reported on -toyplot-anchor-shift

    # assert tip_labels support for anchor-shift

    # assert node_labels support for anchor-shift
