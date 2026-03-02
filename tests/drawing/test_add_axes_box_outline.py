#!/usr/bin/env python

"""Tests for annotate.add_axes_box_outline."""

import io
import unittest

import toytree
import toyplot.svg


class TestAddAxesBoxOutline(unittest.TestCase):
    def setUp(self):
        self.tree = toytree.tree("((a:1,b:1):1,c:2);")

    @staticmethod
    def _bbox(overlay):
        mins = [1e18, 1e18]
        maxs = [-1e18, -1e18]
        for mk in overlay._scenegraph.targets(overlay, "render"):
            table = mk._table
            keys = list(table.keys())
            if "left" in keys:
                mins[0] = min(mins[0], float(min(table["left"])))
                mins[1] = min(mins[1], float(min(table["top"])))
                maxs[0] = max(maxs[0], float(max(table["right"])))
                maxs[1] = max(maxs[1], float(max(table["bottom"])))
            else:
                xs = table["x"]
                ys = table["y0"]
                mins[0] = min(mins[0], float(min(xs)))
                mins[1] = min(mins[1], float(min(ys)))
                maxs[0] = max(maxs[0], float(max(xs)))
                maxs[1] = max(maxs[1], float(max(ys)))
        return mins[0], maxs[0], mins[1], maxs[1]

    def test_returns_overlay_and_preserves_input_axes(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=True)
        before = (
            axes._xmin_range,
            axes._xmax_range,
            axes._ymin_range,
            axes._ymax_range,
            bool(axes.x.show),
            bool(axes.y.show),
            bool(axes.x.ticks.show),
            bool(axes.y.ticks.show),
            axes.x.label.text,
            axes.y.label.text,
        )
        overlay = self.tree.annotate.add_axes_box_outline(axes, region="canvas")
        after = (
            axes._xmin_range,
            axes._xmax_range,
            axes._ymin_range,
            axes._ymax_range,
            bool(axes.x.show),
            bool(axes.y.show),
            bool(axes.x.ticks.show),
            bool(axes.y.ticks.show),
            axes.x.label.text,
            axes.y.label.text,
        )
        self.assertIsNot(overlay, axes)
        self.assertEqual(before, after)
        self.assertFalse(overlay.show)

    def test_region_ordering_canvas_axes(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=True, padding=20)
        ov_canvas = self.tree.annotate.add_axes_box_outline(axes, region="canvas")
        ov_axes = self.tree.annotate.add_axes_box_outline(axes, region="axes")

        lc, rc, tc, bc = self._bbox(ov_canvas)
        la, ra, ta, ba = self._bbox(ov_axes)

        # canvas encloses axes region
        self.assertLessEqual(lc, la)
        self.assertGreaterEqual(rc, ra)
        self.assertLessEqual(tc, ta)
        self.assertGreaterEqual(bc, ba)

    def test_stroke_width_half_inset_applied_only_to_canvas(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=True)
        canvas = axes._scenegraph.sources("render", axes)[0]
        ov_canvas = self.tree.annotate.add_axes_box_outline(
            axes,
            region="canvas",
            style={"stroke-width": 4},
        )
        lc, rc, tc, bc = self._bbox(ov_canvas)
        self.assertAlmostEqual(lc, 2.0)
        self.assertAlmostEqual(tc, 2.0)
        self.assertAlmostEqual(rc, float(canvas.width) - 2.0)
        self.assertAlmostEqual(bc, float(canvas.height) - 2.0)

        ov_axes = self.tree.annotate.add_axes_box_outline(
            axes,
            region="axes",
            style={"stroke-width": 4},
        )
        la, _, _, _ = self._bbox(ov_axes)
        pad = float(axes.padding)
        self.assertAlmostEqual(la, float(axes._xmin_range) - pad)

    def test_draws_single_rectangle_mark(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=True)
        overlay = self.tree.annotate.add_axes_box_outline(
            axes,
            region="canvas",
        )
        marks = overlay._scenegraph.targets(overlay, "render")
        self.assertEqual(len(marks), 1)

    def test_invalid_region_raises(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=True)
        with self.assertRaises(ValueError):
            self.tree.annotate.add_axes_box_outline(axes, region="outer")
        with self.assertRaises(ValueError):
            self.tree.annotate.add_axes_box_outline(axes, region="axes-margin")
        with self.assertRaises(ValueError):
            self.tree.annotate.add_axes_box_outline(axes, region="axes-padding")

    def test_region_canvas_outline_is_present_in_rendered_svg(self):
        canvas, axes, _ = self.tree.draw(layout="d", scale_bar=True)
        self.tree.annotate.add_axes_box_outline(
            axes,
            region="canvas",
            style={"stroke": "rgb(255, 0, 0)"},
        )
        out = io.BytesIO()
        toyplot.svg.render(canvas, out)
        svg = out.getvalue().decode("utf-8")
        self.assertIn("stroke:rgb(100%,0%,0%)", svg)

    def test_axes_match_ranges_with_padding(self):
        _, axes, _ = self.tree.draw(layout="d", scale_bar=True, padding=15)
        ov_axes = self.tree.annotate.add_axes_box_outline(axes, region="axes")
        la, ra, ta, ba = self._bbox(ov_axes)
        pad = float(axes.padding)
        self.assertAlmostEqual(la, float(axes._xmin_range) - pad)
        self.assertAlmostEqual(ra, float(axes._xmax_range) + pad)
        self.assertAlmostEqual(ta, float(axes._ymin_range) - pad)
        self.assertAlmostEqual(ba, float(axes._ymax_range) + pad)

    def test_expand_expands_and_contracts(self):
        _, axes, _ = self.tree.draw(layout="d", scale_bar=True, padding=15)
        ov0 = self.tree.annotate.add_axes_box_outline(axes, region="axes")
        l0, r0, t0, b0 = self._bbox(ov0)

        ov1 = self.tree.annotate.add_axes_box_outline(
            axes, region="axes", expand=10
        )
        l1, r1, t1, b1 = self._bbox(ov1)
        self.assertAlmostEqual(l1, l0 - 10)
        self.assertAlmostEqual(r1, r0 + 10)
        self.assertAlmostEqual(t1, t0 - 10)
        self.assertAlmostEqual(b1, b0 + 10)

        ov2 = self.tree.annotate.add_axes_box_outline(
            axes, region="axes", expand=(5, 10, 15, 20)
        )
        l2, r2, t2, b2 = self._bbox(ov2)
        self.assertAlmostEqual(l2, l0 - 5)
        self.assertAlmostEqual(r2, r0 + 10)
        self.assertAlmostEqual(t2, t0 - 15)
        self.assertAlmostEqual(b2, b0 + 20)

        ov3 = self.tree.annotate.add_axes_box_outline(
            axes, region="axes", expand=-5
        )
        l3, r3, t3, b3 = self._bbox(ov3)
        self.assertAlmostEqual(l3, l0 + 5)
        self.assertAlmostEqual(r3, r0 - 5)
        self.assertAlmostEqual(t3, t0 + 5)
        self.assertAlmostEqual(b3, b0 - 5)

    def test_expand_invalid_tuple_or_collapse_raises(self):
        _, axes, _ = self.tree.draw(layout="d", scale_bar=True, padding=15)
        with self.assertRaises(ValueError):
            self.tree.annotate.add_axes_box_outline(
                axes, region="axes", expand=(1, 2, 3)
            )
        with self.assertRaises(ValueError):
            self.tree.annotate.add_axes_box_outline(
                axes, region="axes", expand=-1000
            )

    def test_behind_sets_render_order(self):
        canvas, axes, _ = self.tree.draw(layout="d", scale_bar=True)
        front = self.tree.annotate.add_axes_box_outline(axes, behind=False)
        back = self.tree.annotate.add_axes_box_outline(
            axes, style={"stroke": "blue"}, behind=True
        )
        targets = canvas._scenegraph._relationships["render"]._targets[canvas]
        self.assertGreater(targets.index(front), targets.index(axes))
        self.assertLess(targets.index(back), targets.index(axes))


if __name__ == "__main__":
    unittest.main()
