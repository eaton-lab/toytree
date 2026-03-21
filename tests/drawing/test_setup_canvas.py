#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for setup_canvas sizing heuristics."""

from __future__ import annotations

import numpy as np
from conftest import PytestCompat

import toytree
from toytree.drawing.src.setup_canvas import (
    get_circular_width_and_height,
    get_linear_width_and_height,
)


class TestSetupCanvasLinearSizing(PytestCompat):
    def test_font_family_changes_width_estimate(self):
        tree = toytree.rtree.unittree(12, seed=123)
        labels = {
            i: f"species_{i}_with_a_very_long_label_name" for i in range(tree.ntips)
        }
        tree = tree.set_node_data("L", labels, default=np.nan, inplace=False)

        _, _, m1 = tree.draw(
            layout="r",
            tip_labels="L",
            tip_labels_style={"font-family": "helvetica", "font-size": 14},
        )
        _, _, m2 = tree.draw(
            layout="r",
            tip_labels="L",
            tip_labels_style={"font-family": "courier", "font-size": 14},
        )
        w1, h1 = get_linear_width_and_height(m1)
        w2, h2 = get_linear_width_and_height(m2)
        self.assertGreaterEqual(w2, w1)
        self.assertGreaterEqual(h2, h1 - 5)

    def test_ntips_increases_tree_depth_until_cap(self):
        tsmall = toytree.rtree.unittree(10, seed=123)
        tlarge = toytree.rtree.unittree(80, seed=123)
        _, _, ms = tsmall.draw(layout="r")
        _, _, ml = tlarge.draw(layout="r")
        ws, hs = get_linear_width_and_height(ms)
        wl, hl = get_linear_width_and_height(ml)
        self.assertGreaterEqual(wl, ws)
        self.assertGreaterEqual(hl, hs)
        self.assertLessEqual(wl, 800)

    def test_layout_swap_behavior_for_ud(self):
        tree = toytree.rtree.unittree(20, seed=123)
        _, _, mr = tree.draw(layout="r")
        _, _, md = tree.draw(layout="d")
        wr, hr = get_linear_width_and_height(mr)
        wd, hd = get_linear_width_and_height(md)
        self.assertAlmostEqual(wd, hr, places=6)
        self.assertAlmostEqual(hd, wr, places=6)

    def test_output_bounds_are_enforced(self):
        tree = toytree.rtree.unittree(60, seed=123)
        labels = {i: f"tip_{i}_" + "X" * 200 for i in range(tree.ntips)}
        tree = tree.set_node_data("L", labels, default=np.nan, inplace=False)
        _, _, m = tree.draw(
            layout="r",
            tip_labels="L",
            tip_labels_style={"font-size": 18},
        )
        w, h = get_linear_width_and_height(m)
        self.assertGreaterEqual(w, 300)
        self.assertLessEqual(w, 800)
        self.assertGreaterEqual(h, 275)
        self.assertLessEqual(h, 1000)

    def test_circular_full_default_is_square(self):
        tree = toytree.rtree.unittree(20, seed=123)
        _, _, mark = tree.draw(layout="c", tip_labels=False)
        width, height = get_circular_width_and_height(mark)
        self.assertEqual(width, height)

    def test_circular_fan_default_is_rectangular(self):
        tree = toytree.rtree.unittree(20, seed=123)
        _, _, mark = tree.draw(layout="c0-180", tip_labels=False)
        width, height = get_circular_width_and_height(mark)
        self.assertNotEqual(width, height)
        self.assertGreater(width, height)
