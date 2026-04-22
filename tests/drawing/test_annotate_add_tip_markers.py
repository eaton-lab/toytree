#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for annotate.add_tip_markers."""

import numpy as np
import toyplot.html
from conftest import PytestCompat

import toytree


class TestAnnotateAddTipMarkers(PytestCompat):
    def setUp(self):
        self.tree = toytree.rtree.unittree(ntips=12, seed=123)

    def test_add_tip_markers_smoke_rectangular(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_markers(a, marker="o", size=8, color="red")
        toyplot.html.render(c)
        self.assertIsNotNone(mark)
        self.assertEqual(mark.ntable.shape[0], self.tree.ntips)

    def test_add_tip_markers_smoke_circular(self):
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_tip_markers(a, marker="o", size=8, color="red")
        toyplot.html.render(c)
        self.assertIsNotNone(mark)
        self.assertEqual(mark.ntable.shape[0], self.tree.ntips)

    def test_add_tip_markers_accepts_color_dict_format(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_markers(
            a,
            marker="o",
            size=8,
            color={
                "feature": "idx",
                "cmap": "BlueRed",
                "domain_min": 0,
                "domain_max": self.tree.ntips - 1,
            },
        )
        toyplot.html.render(c)
        self.assertIsNotNone(mark)
        self.assertEqual(mark.ntable.shape[0], self.tree.ntips)

    def test_add_tip_markers_mask_tuple_shortcut(self):
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_tip_markers(
            a,
            marker="o",
            size=8,
            color="red",
            mask=(1, 1, 1),
        )
        self.assertEqual(mark.ntable.shape[0], self.tree.ntips)

    def test_add_tip_markers_mask_bool_true_false(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        shown = self.tree.annotate.add_tip_markers(a, mask=True)
        hidden = self.tree.annotate.add_tip_markers(a, mask=False)
        self.assertEqual(shown.ntable.shape[0], self.tree.ntips)
        self.assertEqual(hidden.ntable.shape[0], 0)

    def test_add_tip_markers_mask_rejects_nnodes_array(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        bad = np.ones(self.tree.nnodes, dtype=bool)
        with self.assertRaises(ValueError):
            self.tree.annotate.add_tip_markers(a, mask=bad)

    def test_add_tip_markers_circular_depth_shift_is_radial(self):
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_tip_markers(
            a,
            align=False,
            xshift=0,
            yshift=12,
        )
        toyplot.html.render(c)
        root_x = float(a.project("x", m.ntable[self.tree.treenode.idx, 0]))
        root_y = float(a.project("y", m.ntable[self.tree.treenode.idx, 1]))
        px = a.project("x", mark.ntable[:, 0])
        py = a.project("y", mark.ntable[:, 1])
        dx = px - root_x
        dy = py - root_y
        radii = np.hypot(dx, dy)
        ux = np.divide(dx, radii, out=np.ones_like(dx), where=radii > 0)
        uy = np.divide(dy, radii, out=np.zeros_like(dy), where=radii > 0)

        disp_x = (
            np.asarray(mark.local_span, dtype=float) * (-uy)
            + np.asarray(mark.local_depth, dtype=float) * ux
        )
        disp_y = (
            np.asarray(mark.local_span, dtype=float) * ux
            + np.asarray(mark.local_depth, dtype=float) * uy
        )
        radial_dot = disp_x * ux + disp_y * uy
        tangent_dot = disp_x * (-uy) + disp_y * ux
        self.assertTrue(np.all(radial_dot > 0.0))
        self.assertTrue(np.all(np.abs(tangent_dot) < 1e-6))

    def test_add_tip_markers_circular_span_shift_is_tangential(self):
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_tip_markers(
            a,
            align=False,
            xshift=12,
            yshift=0,
        )
        toyplot.html.render(c)
        root_x = float(a.project("x", m.ntable[self.tree.treenode.idx, 0]))
        root_y = float(a.project("y", m.ntable[self.tree.treenode.idx, 1]))
        px = a.project("x", mark.ntable[:, 0])
        py = a.project("y", mark.ntable[:, 1])
        dx = px - root_x
        dy = py - root_y
        radii = np.hypot(dx, dy)
        ux = np.divide(dx, radii, out=np.ones_like(dx), where=radii > 0)
        uy = np.divide(dy, radii, out=np.zeros_like(dy), where=radii > 0)

        disp_x = (
            np.asarray(mark.local_span, dtype=float) * (-uy)
            + np.asarray(mark.local_depth, dtype=float) * ux
        )
        disp_y = (
            np.asarray(mark.local_span, dtype=float) * ux
            + np.asarray(mark.local_depth, dtype=float) * uy
        )
        radial_dot = disp_x * ux + disp_y * uy
        tangent_dot = disp_x * (-uy) + disp_y * ux
        self.assertTrue(np.all(np.abs(radial_dot) < 1e-6))
        self.assertTrue(np.all(tangent_dot > 0.0))

    def test_add_tip_markers_circular_align_true_equalizes_radii(self):
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_tip_markers(
            a,
            align=True,
            xshift=0,
            yshift=0,
        )
        root_xy = np.asarray(m.ntable[self.tree.treenode.idx], dtype=float)
        radii = np.sqrt(np.sum((mark.ntable - root_xy) ** 2, axis=1))
        self.assertLess(float(np.ptp(radii)), 1e-8)
