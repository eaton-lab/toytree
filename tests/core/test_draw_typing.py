#!/usr/bin/env python

"""Tests for draw() typing surface."""

import inspect
import unittest

import numpy as np
import toytree
from toytree.utils import ToytreeError


class TestDrawTyping(unittest.TestCase):
    def test_draw_exposes_interior_algorithm(self):
        sig = inspect.signature(toytree.ToyTree.draw)
        self.assertIn("interior_algorithm", sig.parameters)
        self.assertEqual(sig.parameters["interior_algorithm"].default, 0)

    def test_draw_uses_condensed_tuple_aliases(self):
        sig = inspect.signature(toytree.ToyTree.draw)
        self.assertIn("TupleRangeMap", str(sig.parameters["node_sizes"].annotation))
        self.assertIn("TupleColorMap", str(sig.parameters["node_colors"].annotation))

    def test_draw_accepts_interior_algorithm(self):
        tree = toytree.rtree.unittree(8, seed=123)
        canvas, axes, mark = tree.draw(interior_algorithm=1)
        self.assertIsNotNone(canvas)
        self.assertIsNotNone(axes)
        self.assertIsNotNone(mark)

    def test_draw_interior_algorithm_changes_layout(self):
        tree = toytree.tree("((a,b),c);")
        fixed_position = [0.0, 1.0, 10.0]
        _, _, mark0 = tree.draw(layout="r", fixed_position=fixed_position, interior_algorithm=0)
        _, _, mark1 = tree.draw(layout="r", fixed_position=fixed_position, interior_algorithm=1)
        self.assertFalse(np.allclose(mark0.ntable, mark1.ntable))

    def test_draw_weighted_algorithm_differs_when_child_dists_differ(self):
        tree = toytree.tree("((a:0.1,b:2.0):1,(c:1.5,d:0.2):1);")
        _, _, mark0 = tree.draw(layout="r", interior_algorithm=0)
        _, _, mark2 = tree.draw(layout="r", interior_algorithm=2)
        self.assertFalse(np.allclose(mark0.ntable, mark2.ntable))

    def test_draw_weighted_algorithm_handles_zero_length_branches(self):
        tree = toytree.tree("((a:0,b:1):1,c:1);")
        _, _, mark2 = tree.draw(layout="r", fixed_position=[0.0, 2.0, 10.0], interior_algorithm=2)
        self.assertTrue(np.isfinite(mark2.ntable).all())

    def test_draw_median_and_trimmed_mean_are_bounded(self):
        tree = toytree.tree("((a,b),c);")
        pos = [0.0, 1.0, 10.0]
        _, _, mark3 = tree.draw(layout="r", fixed_position=pos, interior_algorithm=3)
        _, _, mark4 = tree.draw(layout="r", fixed_position=pos, interior_algorithm=4)
        # root internal node y-position in right layout is column 1.
        root_y3 = mark3.ntable[-1, 1]
        root_y4 = mark4.ntable[-1, 1]
        self.assertTrue(min(pos) <= root_y3 <= max(pos))
        self.assertTrue(min(pos) <= root_y4 <= max(pos))

    def test_draw_unknown_interior_algorithm_falls_back_to_zero(self):
        tree = toytree.tree("((a,b),c);")
        pos = [0.0, 1.0, 10.0]
        _, _, mark0 = tree.draw(layout="r", fixed_position=pos, interior_algorithm=0)
        _, _, markx = tree.draw(layout="r", fixed_position=pos, interior_algorithm=99)
        self.assertTrue(np.allclose(mark0.ntable, markx.ntable))

    def test_draw_rejects_invalid_tree_style(self):
        tree = toytree.rtree.unittree(8, seed=123)
        with self.assertRaises(ToytreeError):
            tree.draw(tree_style="phylo")

    def test_draw_rejects_invalid_ts_alias(self):
        tree = toytree.rtree.unittree(8, seed=123)
        with self.assertRaises(ToytreeError):
            tree.draw(ts="phylo")


if __name__ == "__main__":
    unittest.main()
