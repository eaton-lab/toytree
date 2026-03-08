#!/usr/bin/env python

"""Tests for annotate.add_axes_scale_bar."""

import io
import re

import toyplot.svg

import toytree



from conftest import PytestCompat

class TestAddScaleBar(PytestCompat):
    def setUp(self):
        self.tree = toytree.tree("((a:1,b:1):1,c:2);")

    @staticmethod
    def _scale_axes(axes):
        return getattr(axes, "_toytree_scale_axes")

    def test_custom_range_explicit_ticks_scaled_labels(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar(
            axes,
            axis="x",
            range=(0, 10),
            tick_locations=[0, 5, 10],
            scale=2,
        )
        saxes = self._scale_axes(axes)
        labels = list(saxes.x.ticks.locator._labels)
        self.assertEqual(labels, ["0", "2.5", "5"])

    def test_axis_override_to_y(self):
        _, axes, _ = self.tree.draw(layout="d", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar(
            axes,
            axis="y",
            range=(0, 4),
            tick_locations=[0, 2, 4],
            scale=True,
        )
        saxes = self._scale_axes(axes)
        self.assertTrue(saxes.y.show)
        self.assertFalse(saxes.x.show)

    def test_range_must_be_valid_tuple(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        with self.assertRaises(ValueError):
            self.tree.annotate.add_axes_scale_bar(
                axes,
                range=(0, 0),
            )

    def test_scale_false_returns_without_modification(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=True)
        saxes = self._scale_axes(axes)
        before = saxes.x.ticks.locator
        self.tree.annotate.add_axes_scale_bar(axes, scale=False)
        after = saxes.x.ticks.locator
        self.assertIs(before, after)
        self.assertFalse(saxes.show)

    def test_padding_and_axis_styles_are_applied(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar(
            axes,
            axis="x",
            range=(0, 4),
            tick_locations=[0, 2, 4],
            padding=30,
            spine_style={"stroke-width": 2},
            ticks_style={"stroke": "red"},
            tick_labels_style={"font-size": "9px", "fill": "blue"},
        )
        saxes = self._scale_axes(axes)
        self.assertEqual(saxes.padding, 30)
        self.assertEqual(saxes.x.spine.style.get("stroke-width"), 2)
        self.assertEqual(saxes.x.ticks.style.get("stroke"), "red")
        self.assertEqual(saxes.x.ticks.labels.style.get("font-size"), "9px")
        self.assertEqual(saxes.x.ticks.labels.style.get("fill"), "blue")

    def test_expand_margin_scalar_and_tuple_expand_whitespace(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        x0, x1 = float(axes._xmin_range), float(axes._xmax_range)
        y0, y1 = float(axes._ymin_range), float(axes._ymax_range)
        xspan0, yspan0 = x1 - x0, y1 - y0
        self.tree.annotate.add_axes_scale_bar(
            axes,
            expand_margin=40,
        )
        self.assertEqual(axes._xmin_range, x0 + 40)
        self.assertEqual(axes._xmax_range, x1 - 40)
        self.assertEqual(axes._ymin_range, y0 + 40)
        self.assertEqual(axes._ymax_range, y1 - 40)
        self.assertLess(float(axes._xmax_range - axes._xmin_range), xspan0)
        self.assertLess(float(axes._ymax_range - axes._ymin_range), yspan0)

        x0, x1 = float(axes._xmin_range), float(axes._xmax_range)
        y0, y1 = float(axes._ymin_range), float(axes._ymax_range)
        self.tree.annotate.add_axes_scale_bar(
            axes,
            expand_margin=(10, 20, 30, 40),
        )
        self.assertEqual(axes._xmin_range, x0 + 10)
        self.assertEqual(axes._xmax_range, x1 - 20)
        self.assertEqual(axes._ymin_range, y0 + 30)
        self.assertEqual(axes._ymax_range, y1 - 40)

        x0, x1 = float(axes._xmin_range), float(axes._xmax_range)
        y0, y1 = float(axes._ymin_range), float(axes._ymax_range)
        self.tree.annotate.add_axes_scale_bar(
            axes,
            expand_margin=-5,
        )
        self.assertEqual(axes._xmin_range, x0 - 5)
        self.assertEqual(axes._xmax_range, x1 + 5)
        self.assertEqual(axes._ymin_range, y0 - 5)
        self.assertEqual(axes._ymax_range, y1 + 5)

    def test_expand_margin_raises_if_ranges_collapse(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        with self.assertRaises(ValueError):
            self.tree.annotate.add_axes_scale_bar(
                axes,
                expand_margin=(10_000, 10_000, 0, 0),
            )

    def test_label_and_label_style_are_applied(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar(
            axes,
            axis="x",
            range=(0, 4),
            tick_locations=[0, 2, 4],
            scale=True,
            label="Time (Myr)",
            label_center="axis",
            label_style={"font-size": "14px", "fill": "red"},
            label_offset=20,
        )
        saxes = self._scale_axes(axes)
        self.assertEqual(saxes.x.label.text, "Time (Myr)")
        self.assertEqual(saxes.x.label.style.get("font-size"), "14px")
        self.assertEqual(saxes.x.label.style.get("fill"), "red")
        self.assertEqual(saxes.x.label.offset, -20.0)

    def test_label_center_spine_preserves_axis_domain_limits(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar(axes)
        saxes = self._scale_axes(axes)
        dmin_before = saxes.x.domain.min
        dmax_before = saxes.x.domain.max
        self.tree.annotate.add_axes_scale_bar(
            axes,
            axis="x",
            range=(0, 4),
            tick_locations=[0, 2, 4],
            scale=True,
            label="Time",
            label_center="spine",
        )
        self.assertEqual(saxes.x.domain.min, dmin_before)
        self.assertEqual(saxes.x.domain.max, dmax_before)
        self.assertEqual(saxes.x.label.text, "Time")

    def test_label_offset_direction_is_layout_aware(self):
        def _get_axis_offset(layout: str, offset: int) -> float:
            t = toytree.rtree.unittree(8, seed=3)
            _, axes, _ = t.draw(layout=layout, scale_bar=False)
            t.annotate.add_axes_scale_bar(
                axes,
                label="LBL",
                label_center="spine",
                label_offset=offset,
            )
            saxes = self._scale_axes(axes)
            if layout in ("r", "l"):
                return float(saxes.x.label.offset)
            return float(saxes.y.label.offset)

        x0 = _get_axis_offset("r", 0)
        x1 = _get_axis_offset("r", 20)
        x2 = _get_axis_offset("r", -20)
        self.assertEqual(x0, 0.0)
        self.assertLess(x1, x0)
        self.assertGreater(x2, x0)

        x0 = _get_axis_offset("l", 0)
        x1 = _get_axis_offset("l", 20)
        x2 = _get_axis_offset("l", -20)
        self.assertEqual(x0, 0.0)
        self.assertLess(x1, x0)
        self.assertGreater(x2, x0)

        x0 = _get_axis_offset("u", 0)
        x1 = _get_axis_offset("u", 20)
        x2 = _get_axis_offset("u", -20)
        self.assertEqual(x0, 0.0)
        self.assertGreater(x1, x0)
        self.assertLess(x2, x0)

    def test_default_spine_label_is_outward(self):
        t = toytree.rtree.unittree(8, seed=4)
        _, axes, _ = t.draw(layout="r", scale_bar=False)
        t.annotate.add_axes_scale_bar(
            axes,
            label="LBL",
            label_center="spine",
        )
        saxes = self._scale_axes(axes)
        self.assertEqual(saxes.x.label.location, "below")
        text_marks = [
            i
            for i in axes._scenegraph.targets(axes, "render")
            if i.__class__.__name__ == "Text"
        ]
        self.assertEqual(len(text_marks), 0)

    def test_spine_label_centers_on_spine_domain_not_full_axis(self):
        def _get_label_translate_x(label_center: str) -> float:
            t = toytree.rtree.unittree(20, seed=1)
            c, axes, _ = t.draw(layout="r")
            t.annotate.add_axes_scale_bar(
                axes,
                label="Time (Mya)",
                label_center=label_center,
            )
            b = io.BytesIO()
            toyplot.svg.render(c, b)
            svg = b.getvalue().decode()
            match = re.search(
                r'transform="translate\(([^,]+),([^\)]+)\)"><text[^>]*>Time \(Mya\)</text>',
                svg,
            )
            self.assertIsNotNone(match)
            return float(match.group(1))

        x_axis = _get_label_translate_x("axis")
        x_spine = _get_label_translate_x("spine")
        self.assertNotEqual(x_axis, x_spine)

    def test_companion_scale_axes_created(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=True)
        saxes = self._scale_axes(axes)
        self.assertIsNotNone(saxes)
        self.assertFalse(axes.x.show)
        self.assertFalse(axes.y.show)
        self.assertTrue(saxes.show)

    def test_spine_domain_unaffected_by_annotation_marks(self):
        t = toytree.rtree.unittree(20, seed=7)
        _, axes, _ = t.draw(layout="r", tip_labels=True, scale_bar=True)
        saxes = self._scale_axes(axes)
        saxes._finalize()
        before_data = (float(saxes.x._data_min), float(saxes.x._data_max))

        # Add a non-tree annotation mark to host axes and rebuild scale bar.
        t.annotate.add_tip_labels(axes, labels=t.get_tip_labels())
        t.annotate.add_axes_scale_bar(axes)
        saxes = self._scale_axes(axes)
        saxes._finalize()
        after_data = (float(saxes.x._data_min), float(saxes.x._data_max))
        self.assertEqual(before_data, after_data)


