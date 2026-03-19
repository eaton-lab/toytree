#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for annotate.add_axes_scale_bar_to_tree."""

import inspect
import io
import re

import numpy as np
import toyplot.svg
import toyplot.text
from conftest import PytestCompat

import toytree
import toytree.annotate.src.add_scale_bar as add_scale_bar_mod
from toytree.annotate.src.add_scale_bar import (
    _get_linear_tip_bar_scale_bounds_finalized,
    add_axes_scale_bar_to_mark,
    add_axes_scale_bar_to_tree,
)
from toytree.annotate.src.checks import get_last_toytree_mark_for_tree
from toytree.drawing.src.scale_axes import (
    get_mark_scale_cartesian,
    get_toytree_scale_cartesian,
)
from toytree.utils import ToytreeError


class TestAddScaleBar(PytestCompat):
    def setUp(self):
        self.tree = toytree.tree("((a:1,b:1):1,c:2);")
        values = {idx: float(idx) for idx in range(self.tree.ntips)}
        self.bar_tree = self.tree.set_node_data(
            "X",
            values,
            default=np.nan,
            inplace=False,
        )
        long_newick = (
            "((41478_cyathophylloides:0.004,41954_cyathophylloides:0.003):0.002,"
            "((30686_cyathophylla:0.002,29154_superba:0.001):0.003,"
            "(38362_rex:0.001,(39618_rex:0.001,35236_rex:0.001):0.001):0.002):"
            "0.004,((35855_rex:0.001,40578_rex:0.002):0.002,(30556_thamno:0.002,"
            "33413_thamno:0.001):0.002):0.003,(33588_przewalskii:0.002,"
            "32082_przewalskii:0.002):0.006);"
        )
        self.long_bar_tree = toytree.tree(long_newick).set_node_data(
            "X",
            {idx: float(idx) for idx in range(13)},
            default=np.nan,
            inplace=False,
        )

    @staticmethod
    def _scale_axes(axes):
        return get_toytree_scale_cartesian(axes, create=False)

    @staticmethod
    def _mark_scale_axes(axes, mark):
        return get_mark_scale_cartesian(axes, mark, create=False)

    @staticmethod
    def _overlay_bounds(scale_axes):
        return (
            float(scale_axes._xmin_range),
            float(scale_axes._xmax_range),
            float(scale_axes._ymin_range),
            float(scale_axes._ymax_range),
        )

    @staticmethod
    def _projected_scale_ticks(scale_axes, axis):
        scale_axes._finalize()
        active = getattr(scale_axes, axis)
        locs = np.asarray(active.ticks.locator._locations, dtype=float)
        pixels = np.asarray(scale_axes.project(axis, locs), dtype=float)
        return locs, list(active.ticks.locator._labels), pixels

    @staticmethod
    def _projected_bounds(axes, mark):
        axes._finalize()
        coords, extents = mark.extents("xy")
        xs = np.asarray(coords[0], dtype=float)
        ys = np.asarray(coords[1], dtype=float)
        xpx = np.asarray(axes.project("x", xs), dtype=float)
        ypx = np.asarray(axes.project("y", ys), dtype=float)
        left, right, top, bottom = [np.asarray(i, dtype=float) for i in extents]
        return (
            float(np.min(xpx + left)),
            float(np.max(xpx + right)),
            float(np.min(ypx + top)),
            float(np.max(ypx + bottom)),
        )

    @staticmethod
    def _visible_tip_bar_bounds(axes, mark):
        axes._finalize()
        shown = np.flatnonzero(np.asarray(mark.show, dtype=bool))
        tips_x_px = np.asarray(axes.project("x", mark.ntable[:, 0]), dtype=float)
        tips_y_px = np.asarray(axes.project("y", mark.ntable[:, 1]), dtype=float)

        if mark.layout in ("r", "l"):
            span = tips_y_px
            baseline = np.max(tips_x_px[shown]) + float(mark.offset)
            max_depth = float(np.max(mark.bar_depths[shown]))
            if mark.layout == "r":
                xmin = float(baseline)
                xmax = float(baseline + max_depth)
            else:
                xmin = float(baseline - max_depth)
                xmax = float(baseline)
        else:
            span = tips_x_px
            baseline = (
                np.min(tips_y_px[shown]) - float(mark.offset)
                if mark.layout == "u"
                else np.max(tips_y_px[shown]) + float(mark.offset)
            )
            max_depth = float(np.max(mark.bar_depths[shown]))
            if mark.layout == "u":
                ymin = float(baseline - max_depth)
                ymax = float(baseline)
            else:
                ymin = float(baseline)
                ymax = float(baseline + max_depth)

        order = np.argsort(span)
        ordered = span[order]
        bounds = np.zeros(ordered.size + 1, dtype=float)
        bounds[1:-1] = 0.5 * (ordered[:-1] + ordered[1:])
        bounds[0] = ordered[0] - 0.5 * (ordered[1] - ordered[0])
        bounds[-1] = ordered[-1] + 0.5 * (ordered[-1] - ordered[-2])
        slot_min = np.zeros(span.size, dtype=float)
        slot_max = np.zeros(span.size, dtype=float)
        for idx, tidx in enumerate(order):
            slot_min[tidx] = bounds[idx]
            slot_max[tidx] = bounds[idx + 1]
        center = 0.5 * (slot_min[shown] + slot_max[shown])
        half = 0.5 * float(mark.width) * (slot_max[shown] - slot_min[shown])
        orth_min = center - half
        orth_max = center + half

        if mark.layout in ("r", "l"):
            return xmin, xmax, float(np.min(orth_min)), float(np.max(orth_max))
        return float(np.min(orth_min)), float(np.max(orth_max)), ymin, ymax

    def test_tree_scale_bar_signature_matches_public_api(self):
        signature = inspect.signature(add_axes_scale_bar_to_tree)
        params = list(signature.parameters)
        self.assertEqual(
            params[:5],
            ["tree", "axes", "show_spine", "show_ticks", "show_tick_labels"],
        )
        self.assertIn("tick_labels_style", params)
        self.assertIn("tick_labels_offset", params)
        self.assertNotIn("tick_label_offset", params)
        self.assertNotIn("axis", params)
        self.assertNotIn("show_axis", params)
        self.assertNotIn("nticks", params)
        self.assertNotIn("only_inside", params)
        self.assertTrue(signature.parameters["show_spine"].default)
        self.assertEqual(signature.parameters["ticks_near"].default, 0)
        self.assertEqual(signature.parameters["ticks_far"].default, 5)
        self.assertEqual(signature.parameters["tick_labels_offset"].default, 6)
        self.assertEqual(
            params.index("tick_labels_style") + 1,
            params.index("tick_labels_offset"),
        )

    def test_mark_scale_bar_signature_places_mark_after_axes(self):
        tree_params = list(inspect.signature(add_axes_scale_bar_to_tree).parameters)
        mark_params = list(inspect.signature(add_axes_scale_bar_to_mark).parameters)
        self.assertEqual(mark_params[:3], ["tree", "axes", "mark"])
        self.assertEqual(mark_params[3:], tree_params[2:])

    def test_explicit_ticks_scaled_labels(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 1, 2],
            scale=2,
        )
        saxes = self._scale_axes(axes)
        labels = list(saxes.x.ticks.locator._labels)
        self.assertEqual(labels, ["0", "0.5", "1"])

    def test_explicit_tree_ticks_are_clipped_to_domain(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[-1, 1, 3],
            scale=1.0,
        )
        saxes = self._scale_axes(axes)
        labels = list(saxes.x.ticks.locator._labels)
        self.assertEqual(labels, ["0", "1", "2"])

    def test_circular_tree_scale_bar_uses_positive_x_half_domain(self):
        ctree = toytree.rtree.unittree(20, seed=123, treeheight=100)
        _, axes, mark = ctree.draw(layout="c", scale_bar=False, width=400)
        ctree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 40, 80],
            scale=1.0,
        )
        saxes = self._scale_axes(axes)
        self.assertTrue(saxes.x.show)
        self.assertFalse(saxes.y.show)
        locs, labels, _ = self._projected_scale_ticks(saxes, "x")
        self.assertTrue(np.allclose(locs, np.array([0.0, 40.0, 80.0])))
        self.assertEqual(labels, ["0", "40", "80"])
        overlay = self._overlay_bounds(saxes)
        projected = np.asarray(
            axes.project("x", np.array([0.0, float(mark.domain("x")[1])])), dtype=float
        )
        self.assertTrue(
            np.allclose(
                np.array(overlay[:2]),
                np.array([np.min(projected), np.max(projected)]),
            )
        )

    def test_circular_fan_tree_scale_bar_uses_positive_y_half_domain(self):
        ctree = toytree.rtree.unittree(20, seed=123, treeheight=100)
        _, axes, mark = ctree.draw(layout="c60-320", scale_bar=False, width=400)
        ctree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 40, 80],
            scale=1.0,
        )
        saxes = self._scale_axes(axes)
        self.assertFalse(saxes.x.show)
        self.assertTrue(saxes.y.show)
        locs, labels, _ = self._projected_scale_ticks(saxes, "y")
        self.assertTrue(np.allclose(locs, np.array([0.0, 40.0, 80.0])))
        self.assertEqual(labels, ["0", "40", "80"])
        overlay = self._overlay_bounds(saxes)
        projected = np.asarray(
            axes.project("y", np.array([0.0, float(mark.domain("y")[1])])), dtype=float
        )
        self.assertTrue(
            np.allclose(
                np.array(overlay[2:]),
                np.array([np.min(projected), np.max(projected)]),
            )
        )

    def test_circular_negative_fan_scale_bar_uses_positive_labels(self):
        ctree = toytree.rtree.unittree(20, seed=123, treeheight=100)
        _, axes, mark = ctree.draw(layout="c60-160", scale_bar=False, width=400)
        ctree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 40, 80],
            scale=1.0,
        )
        saxes = self._scale_axes(axes)
        self.assertTrue(saxes.x.show)
        self.assertFalse(saxes.y.show)
        locs, labels, _ = self._projected_scale_ticks(saxes, "x")
        self.assertTrue(np.allclose(locs, np.array([0.0, -40.0, -80.0])))
        self.assertEqual(labels, ["0", "40", "80"])
        overlay = self._overlay_bounds(saxes)
        projected = np.asarray(
            axes.project("x", np.array([float(mark.domain("x")[0]), 0.0])),
            dtype=float,
        )
        self.assertTrue(
            np.allclose(
                np.array(overlay[:2]),
                np.array([np.min(projected), np.max(projected)]),
            )
        )

    def test_circular_positive_fan_ticks_are_clipped_to_selected_half(self):
        ctree = toytree.rtree.unittree(20, seed=123, treeheight=100)
        _, axes, mark = ctree.draw(layout="c60-320", scale_bar=False, width=400)
        ymax = float(mark.domain("y")[1])
        ctree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 40, 200],
            scale=1.0,
        )
        saxes = self._scale_axes(axes)
        locs, labels, _ = self._projected_scale_ticks(saxes, "y")
        self.assertTrue(np.isclose(locs[0], 0.0))
        self.assertTrue(np.isclose(locs[1], 40.0))
        self.assertTrue(np.isclose(locs[2], ymax))
        self.assertEqual(labels[0], "0")
        self.assertEqual(labels[1], "40")
        self.assertTrue(np.isclose(float(labels[2]), ymax))

    def test_circular_negative_fan_ticks_are_clipped_to_selected_half(self):
        ctree = toytree.rtree.unittree(20, seed=123, treeheight=100)
        _, axes, mark = ctree.draw(layout="c60-160", scale_bar=False, width=400)
        xmin = float(mark.domain("x")[0])
        ctree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 40, 200],
            scale=1.0,
        )
        saxes = self._scale_axes(axes)
        locs, labels, _ = self._projected_scale_ticks(saxes, "x")
        self.assertTrue(np.isclose(locs[0], 0.0))
        self.assertTrue(np.isclose(locs[1], -40.0))
        self.assertTrue(np.isclose(locs[2], xmin))
        self.assertEqual(labels[0], "0")
        self.assertEqual(labels[1], "40")
        self.assertTrue(np.isclose(float(labels[2]), abs(xmin)))

    def test_circular_negative_fan_ticks_respect_scale_with_positive_labels(self):
        ctree = toytree.rtree.unittree(20, seed=123, treeheight=100)
        _, axes, _ = ctree.draw(layout="c60-160", scale_bar=False, width=400)
        ctree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 40, 80],
            scale=2.0,
        )
        saxes = self._scale_axes(axes)
        labels = list(saxes.x.ticks.locator._labels)
        self.assertEqual(labels, ["0", "20", "40"])

    def test_vertical_layout_uses_y_scale_axis(self):
        _, axes, _ = self.tree.draw(layout="d", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 1, 2],
            scale=1.0,
        )
        saxes = self._scale_axes(axes)
        self.assertTrue(saxes.y.show)
        self.assertFalse(saxes.x.show)

    def test_show_spine_false_hides_only_spine(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(
            axes,
            show_spine=False,
            tick_locations=[0, 1, 2],
            label="Time",
        )
        saxes = self._scale_axes(axes)
        self.assertTrue(saxes.x.show)
        self.assertFalse(saxes.x.spine.show)
        self.assertTrue(saxes.x.ticks.show)
        self.assertTrue(saxes.x.ticks.labels.show)
        self.assertEqual(saxes.x.label.text, "Time")

    def test_removed_tree_scale_bar_kwargs_raise_type_error(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        for kwargs in (
            {"axis": "x"},
            {"show_axis": False},
            {"nticks": 4},
            {"only_inside": False},
        ):
            with self.assertRaises(TypeError):
                self.tree.annotate.add_axes_scale_bar_to_tree(axes, **kwargs)

    def test_removed_mark_scale_bar_kwargs_raise_type_error(self):
        _, axes, _ = self.bar_tree.draw(layout="l", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        for kwargs in (
            {"axis": "x"},
            {"show_axis": False},
            {"nticks": 4},
            {"only_inside": False},
        ):
            with self.assertRaises(TypeError):
                self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark, **kwargs)

    def test_range_argument_is_removed(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        _, bar_axes, _ = self.bar_tree.draw(layout="l", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(bar_axes, data="X", depth=18)
        with self.assertRaises(TypeError):
            self.tree.annotate.add_axes_scale_bar_to_tree(
                axes,
                range=(0, 0),
            )
        with self.assertRaises(TypeError):
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(
                bar_axes,
                bmark,
                range=(0, 2),
            )

    def test_bool_scale_is_rejected(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        _, bar_axes, _ = self.bar_tree.draw(layout="l", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(bar_axes, data="X", depth=18)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_axes_scale_bar_to_tree(axes, scale=True)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_axes_scale_bar_to_tree(axes, scale=False)
        with self.assertRaises(ToytreeError):
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(
                bar_axes, bmark, scale=True
            )
        with self.assertRaises(ToytreeError):
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(
                bar_axes, bmark, scale=False
            )

    def test_padding_and_axis_styles_are_applied(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        host_padding = float(axes.padding)
        self.tree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 1, 2],
            padding=30,
            spine_style={"stroke-width": 2},
            ticks_style={"stroke": "red"},
            tick_labels_style={"font-size": "9px", "fill": "blue"},
        )
        saxes = self._scale_axes(axes)
        self.assertEqual(float(axes.padding), host_padding)
        self.assertEqual(float(saxes.padding), 0.0)
        self.assertEqual(saxes.x.spine.style.get("stroke-width"), 2)
        self.assertEqual(saxes.x.ticks.style.get("stroke"), "red")
        self.assertEqual(saxes.x.ticks.labels.style.get("font-size"), "9px")
        self.assertEqual(saxes.x.ticks.labels.style.get("fill"), "blue")

    def test_tree_scale_bar_padding_is_local_gap(self):
        _, axes0, mark0 = self.tree.draw(layout="r", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(axes0, padding=0)
        zero_pad = self._scale_axes(axes0)
        _, _, _, tree_bottom0 = self._projected_bounds(axes0, mark0)

        _, axes1, mark1 = self.tree.draw(layout="r", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(axes1, padding=20)
        padded = self._scale_axes(axes1)
        _, _, _, tree_bottom1 = self._projected_bounds(axes1, mark1)

        self.assertAlmostEqual(
            float(zero_pad._ymax_range) - tree_bottom0, 0.0, places=3
        )
        self.assertAlmostEqual(float(padded._ymax_range) - tree_bottom1, 20.0, places=3)

    def test_tree_scale_bar_default_padding_is_fifteen_pixels(self):
        _, axes0, mark0 = self.tree.draw(layout="r", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(axes0, padding=0)
        zero_pad = self._scale_axes(axes0)
        _, _, _, tree_bottom0 = self._projected_bounds(axes0, mark0)

        _, axes1, mark1 = self.tree.draw(layout="r", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(axes1)
        default_pad = self._scale_axes(axes1)
        _, _, _, tree_bottom1 = self._projected_bounds(axes1, mark1)

        self.assertAlmostEqual(
            float(zero_pad._ymax_range) - tree_bottom0, 0.0, places=3
        )
        self.assertAlmostEqual(
            float(default_pad._ymax_range) - tree_bottom1, 15.0, places=3
        )

    def test_draw_padding_applies_to_tree_companion_gap_only(self):
        _, axes0, mark0 = self.tree.draw(layout="r", scale_bar=True)
        default_pad = self._scale_axes(axes0)
        _, _, _, tree_bottom0 = self._projected_bounds(axes0, mark0)

        _, axes1, mark1 = self.tree.draw(layout="r", scale_bar=True, padding=30)
        custom_pad = self._scale_axes(axes1)
        _, _, _, tree_bottom1 = self._projected_bounds(axes1, mark1)

        self.assertEqual(float(axes0.padding), 15.0)
        self.assertEqual(float(axes1.padding), 15.0)
        self.assertAlmostEqual(
            float(default_pad._ymax_range) - tree_bottom0, 15.0, places=3
        )
        self.assertAlmostEqual(
            float(custom_pad._ymax_range) - tree_bottom1, 30.0, places=3
        )

    def test_draw_padding_is_noop_when_tree_scale_bar_is_hidden(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=False, padding=30)
        self.assertIsNone(self._scale_axes(axes))
        self.assertEqual(float(axes.padding), 15.0)

    def test_add_axes_scale_bar_reuses_cached_tip_label_extents(self):
        _, axes, _ = self.tree.draw(layout="r", tip_labels=True, scale_bar=False)
        original = toyplot.text.extents
        calls = {"count": 0}

        def counting_extents(*args, **kwargs):
            calls["count"] += 1
            return original(*args, **kwargs)

        toyplot.text.extents = counting_extents
        try:
            self.tree.annotate.add_axes_scale_bar_to_tree(axes, padding=10)
        finally:
            toyplot.text.extents = original

        self.assertEqual(calls["count"], 0)

    def test_tick_labels_offset_is_applied(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 1, 2],
            tick_labels_offset=18,
        )
        saxes = self._scale_axes(axes)
        self.assertEqual(saxes.x.ticks.labels.offset, 18)

    def test_old_tick_label_offset_name_raises_type_error(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        with self.assertRaises(TypeError):
            self.tree.annotate.add_axes_scale_bar_to_tree(
                axes,
                tick_label_offset=18,
            )

    def test_expand_margin_scalar_and_tuple_expand_whitespace(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        x0, x1 = float(axes._xmin_range), float(axes._xmax_range)
        y0, y1 = float(axes._ymin_range), float(axes._ymax_range)
        xspan0, yspan0 = x1 - x0, y1 - y0
        self.tree.annotate.add_axes_scale_bar_to_tree(
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
        self.tree.annotate.add_axes_scale_bar_to_tree(
            axes,
            expand_margin=(10, 20, 30, 40),
        )
        self.assertEqual(axes._xmin_range, x0 + 10)
        self.assertEqual(axes._xmax_range, x1 - 20)
        self.assertEqual(axes._ymin_range, y0 + 30)
        self.assertEqual(axes._ymax_range, y1 - 40)

        x0, x1 = float(axes._xmin_range), float(axes._xmax_range)
        y0, y1 = float(axes._ymin_range), float(axes._ymax_range)
        self.tree.annotate.add_axes_scale_bar_to_tree(
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
            self.tree.annotate.add_axes_scale_bar_to_tree(
                axes,
                expand_margin=(10_000, 10_000, 0, 0),
            )

    def test_label_and_label_style_are_applied(self):
        _, axes, _ = self.tree.draw(layout="l", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 1, 2],
            scale=1.0,
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
        self.tree.annotate.add_axes_scale_bar_to_tree(axes)
        saxes = self._scale_axes(axes)
        dmin_before = saxes.x.domain.min
        dmax_before = saxes.x.domain.max
        self.tree.annotate.add_axes_scale_bar_to_tree(
            axes,
            tick_locations=[0, 1, 2],
            scale=1.0,
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
            t.annotate.add_axes_scale_bar_to_tree(
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
        t.annotate.add_axes_scale_bar_to_tree(
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
            t.annotate.add_axes_scale_bar_to_tree(
                axes,
                label="Time (Mya)",
                label_center=label_center,
            )
            b = io.BytesIO()
            toyplot.svg.render(c, b)
            svg = b.getvalue().decode()
            match = re.search(
                (
                    r'transform="translate\(([^,]+),([^\)]+)\)">'
                    r"<text[^>]*>Time \(Mya\)</text>"
                ),
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

    def test_tree_companion_hides_interactive_coordinate_readout(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=True)
        saxes = self._scale_axes(axes)
        self.assertFalse(saxes.x.interactive.coordinates.show)
        self.assertFalse(saxes.y.interactive.coordinates.show)

    def test_spine_domain_unaffected_by_annotation_marks(self):
        t = toytree.rtree.unittree(20, seed=7)
        _, axes, _ = t.draw(layout="r", tip_labels=True, scale_bar=True)
        saxes = self._scale_axes(axes)
        saxes._finalize()
        before_data = (float(saxes.x._data_min), float(saxes.x._data_max))

        # Add a non-tree annotation mark to host axes and rebuild scale bar.
        t.annotate.add_tip_text(axes, labels=t.get_tip_labels())
        t.annotate.add_axes_scale_bar_to_tree(axes)
        saxes = self._scale_axes(axes)
        saxes._finalize()
        after_data = (float(saxes.x._data_min), float(saxes.x._data_max))
        self.assertEqual(before_data, after_data)

    def test_companion_scale_axes_renders_before_host_axes(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=True)
        saxes = self._scale_axes(axes)
        canvas = axes._scenegraph.sources("render", axes)[0]
        targets = axes._scenegraph._relationships["render"]._targets[canvas]
        self.assertIn(axes, targets)
        self.assertIn(saxes, targets)
        self.assertLess(targets.index(saxes), targets.index(axes))

    def test_two_tree_draws_with_scale_bar_create_two_tree_companions(self):
        _, axes, mark0 = self.tree.draw(layout="r", scale_bar=True, width=400)
        _, axes, mark1 = self.tree.draw(
            axes=axes,
            layout="l",
            xbaseline=6,
            scale_bar=True,
        )
        saxes0 = get_toytree_scale_cartesian(axes, mark=mark0, create=False)
        saxes1 = get_toytree_scale_cartesian(axes, mark=mark1, create=False)
        canvas = axes._scenegraph.sources("render", axes)[0]
        targets = axes._scenegraph._relationships["render"]._targets[canvas]

        self.assertIsNotNone(saxes0)
        self.assertIsNotNone(saxes1)
        self.assertIsNot(saxes0, saxes1)
        self.assertIs(get_toytree_scale_cartesian(axes, create=False), saxes1)
        self.assertIn(saxes0, targets)
        self.assertIn(saxes1, targets)
        self.assertLess(targets.index(saxes0), targets.index(axes))
        self.assertLess(targets.index(saxes1), targets.index(axes))

    def test_two_tree_companions_each_keep_their_own_tree_domain_mark(self):
        _, axes, mark0 = self.tree.draw(layout="r", scale_bar=True, width=400)
        _, axes, mark1 = self.tree.draw(
            axes=axes,
            layout="l",
            xbaseline=6,
            scale_bar=True,
        )
        saxes0 = get_toytree_scale_cartesian(axes, mark=mark0, create=False)
        saxes1 = get_toytree_scale_cartesian(axes, mark=mark1, create=False)
        dmarks0 = [
            mark
            for mark in axes._scenegraph.targets(saxes0, "render")
            if mark.__class__.__name__ == "TreeDomainMark"
        ]
        dmarks1 = [
            mark
            for mark in axes._scenegraph.targets(saxes1, "render")
            if mark.__class__.__name__ == "TreeDomainMark"
        ]

        self.assertEqual(len(dmarks0), 1)
        self.assertEqual(len(dmarks1), 1)
        self.assertEqual(dmarks0[0].layout, "r")
        self.assertEqual(dmarks1[0].layout, "l")

    def test_add_axes_scale_bar_to_tree_targets_newest_matching_tree_mark(self):
        _, axes, mark0 = self.tree.draw(layout="r", scale_bar=False, width=400)
        _, axes, mark1 = self.tree.draw(
            axes=axes,
            layout="l",
            xbaseline=6,
            scale_bar=False,
        )

        self.tree.annotate.add_axes_scale_bar_to_tree(axes, label="Newest")

        self.assertIsNone(get_toytree_scale_cartesian(axes, mark=mark0, create=False))
        saxes1 = get_toytree_scale_cartesian(axes, mark=mark1, create=False)
        self.assertIsNotNone(saxes1)
        self.assertEqual(saxes1.x.label.text, "Newest")

    def test_add_axes_scale_bar_to_mark_targets_exact_tree_draw(self):
        _, axes, mark0 = self.tree.draw(layout="r", scale_bar=False, width=400)
        _, axes, mark1 = self.tree.draw(
            axes=axes,
            layout="l",
            xbaseline=6,
            scale_bar=False,
        )

        self.tree.annotate.add_axes_scale_bar_to_mark(
            axes,
            mark0,
            label="Right tree",
        )
        self.tree.annotate.add_axes_scale_bar_to_mark(
            axes,
            mark1,
            label="Left tree",
        )

        saxes0 = get_toytree_scale_cartesian(axes, mark=mark0, create=False)
        saxes1 = get_toytree_scale_cartesian(axes, mark=mark1, create=False)
        self.assertIsNotNone(saxes0)
        self.assertIsNotNone(saxes1)
        self.assertEqual(saxes0.x.label.text, "Right tree")
        self.assertEqual(saxes1.x.label.text, "Left tree")

    def test_later_scale_bar_false_draw_does_not_hide_existing_tree_companion(self):
        _, axes, mark0 = self.tree.draw(layout="r", scale_bar=True, width=400)
        _, axes, _ = self.tree.draw(
            axes=axes,
            layout="l",
            xbaseline=6,
            scale_bar=False,
        )

        saxes0 = get_toytree_scale_cartesian(axes, mark=mark0, create=False)
        self.assertIsNotNone(saxes0)
        self.assertTrue(saxes0.show)
        self.assertTrue(saxes0.x.show)

    def test_plain_draw_without_scale_bar_creates_no_hidden_companion(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=False)
        saxes = self._scale_axes(axes)
        self.assertIsNone(saxes)
        self.assertFalse(
            getattr(axes, "_toytree_companion_add_mark_hook_installed", False)
        )

    def test_lazy_companion_axes_renders_before_host_axes(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(axes)
        saxes = self._scale_axes(axes)
        canvas = axes._scenegraph.sources("render", axes)[0]
        targets = axes._scenegraph._relationships["render"]._targets[canvas]
        self.assertIn(axes, targets)
        self.assertIn(saxes, targets)
        self.assertLess(targets.index(saxes), targets.index(axes))

    def test_repeated_add_axes_scale_bar_reuses_one_tree_domain_mark(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(axes)
        saxes = self._scale_axes(axes)
        first_targets = axes._scenegraph.targets(saxes, "render")
        first_domain_marks = [
            i for i in first_targets if i.__class__.__name__ == "TreeDomainMark"
        ]
        self.tree.annotate.add_axes_scale_bar_to_tree(axes, padding=20)
        second_targets = axes._scenegraph.targets(saxes, "render")
        second_domain_marks = [
            i for i in second_targets if i.__class__.__name__ == "TreeDomainMark"
        ]
        self.assertEqual(len(first_domain_marks), 1)
        self.assertEqual(len(second_domain_marks), 1)
        self.assertIs(first_domain_marks[0], second_domain_marks[0])

    def test_tree_scale_bar_late_host_marks_update_host_domain(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=False)
        self.tree.annotate.add_axes_scale_bar_to_tree(axes)
        axes.scatterplot(range(10), range(10))
        axes._finalize()
        self.assertGreaterEqual(float(axes.x._data_max), 9.0)
        self.assertGreaterEqual(float(axes.y._data_max), 9.0)

    def test_draw_scale_bar_late_host_marks_update_host_domain(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=True)
        axes.scatterplot(range(10), range(10))
        axes._finalize()
        self.assertGreaterEqual(float(axes.x._data_max), 9.0)
        self.assertGreaterEqual(float(axes.y._data_max), 9.0)

    def test_tip_bar_without_companion_late_host_marks_update_host_domain(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        self.assertTrue(
            getattr(axes, "_toytree_host_fit_add_mark_hook_installed", False)
        )
        axes.scatterplot(range(10), range(10))
        self.assertIsNone(axes._finalized)
        axes._finalize()
        self.assertGreaterEqual(float(axes.x._data_max), 9.0)
        self.assertGreaterEqual(float(axes.y._data_max), 9.0)

    def test_tip_path_without_companion_late_host_marks_update_host_domain(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        self.bar_tree.annotate.add_tip_paths(axes, ends=None, depth=18)
        self.assertTrue(
            getattr(axes, "_toytree_host_fit_add_mark_hook_installed", False)
        )
        axes.scatterplot(range(10), range(10))
        self.assertIsNone(axes._finalized)
        axes._finalize()
        self.assertGreaterEqual(float(axes.x._data_max), 9.0)
        self.assertGreaterEqual(float(axes.y._data_max), 9.0)

    def test_mark_scale_bar_late_host_marks_update_host_domain(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)
        axes.scatterplot(range(10), range(10))
        axes._finalize()
        self.assertGreaterEqual(float(axes.x._data_max), 9.0)
        self.assertGreaterEqual(float(axes.y._data_max), 9.0)

    def test_mark_scale_bar_upgrades_plain_data_annotation_hook(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        self.assertTrue(
            getattr(axes, "_toytree_host_fit_add_mark_hook_installed", False)
        )
        self.assertFalse(
            getattr(axes, "_toytree_companion_add_mark_hook_installed", False)
        )
        original = axes._toytree_original_add_mark
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)
        self.assertFalse(
            getattr(axes, "_toytree_host_fit_add_mark_hook_installed", False)
        )
        self.assertTrue(
            getattr(axes, "_toytree_companion_add_mark_hook_installed", False)
        )
        self.assertIs(axes._toytree_original_add_mark, original)
        axes.scatterplot(range(10), range(10))
        self.assertIsNotNone(axes._finalized)
        self.assertGreaterEqual(float(axes.x._data_max), 9.0)
        self.assertGreaterEqual(float(axes.y._data_max), 9.0)

    def test_tree_and_mark_scale_bars_late_host_marks_update_host_domain(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        self.bar_tree.annotate.add_axes_scale_bar_to_tree(axes)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)
        axes.scatterplot(range(10), range(10))
        axes._finalize()
        self.assertGreaterEqual(float(axes.x._data_max), 9.0)
        self.assertGreaterEqual(float(axes.y._data_max), 9.0)

    def test_node_markers_select_tree_specific_mark_on_shared_axes(self):
        tree1 = toytree.rtree.unittree(ntips=10, seed=123)
        tree2 = toytree.rtree.unittree(ntips=10, seed=333, random_names=True)
        _, axes, tmark1 = tree1.draw(layout="r", width=500)
        _, axes, tmark2 = tree2.draw(axes=axes, layout="l", xbaseline=2)
        mark = tree1.annotate.add_node_markers(axes, mask=False)
        self.assertTrue(np.allclose(mark.ntable, np.asarray(tmark1.ntable)))
        self.assertFalse(np.allclose(mark.ntable, np.asarray(tmark2.ntable)))

    def test_get_last_toytree_mark_for_tree_single_untagged_mark_falls_back(self):
        tree = toytree.rtree.unittree(ntips=8, seed=123)
        _, axes, tmark = tree.draw(layout="r")
        if hasattr(tmark, "_toytree_source_tree"):
            delattr(tmark, "_toytree_source_tree")
        resolved = get_last_toytree_mark_for_tree(axes, tree)
        self.assertIs(resolved, tmark)

    def test_get_last_toytree_mark_for_tree_rejects_ambiguous_shared_axes(self):
        tree1 = toytree.rtree.unittree(ntips=10, seed=123)
        tree2 = toytree.rtree.unittree(ntips=10, seed=333, random_names=True)
        _, axes, tmark1 = tree1.draw(layout="r", width=500)
        _, axes, tmark2 = tree2.draw(axes=axes, layout="l", xbaseline=2)
        if hasattr(tmark1, "_toytree_source_tree"):
            delattr(tmark1, "_toytree_source_tree")
        if hasattr(tmark2, "_toytree_source_tree"):
            delattr(tmark2, "_toytree_source_tree")
        with self.assertRaises(ToytreeError):
            get_last_toytree_mark_for_tree(axes, tree1)

    def test_companion_add_mark_hook_is_installed_only_once(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        self.assertFalse(
            getattr(axes, "_toytree_companion_add_mark_hook_installed", False)
        )
        self.bar_tree.annotate.add_axes_scale_bar_to_tree(axes)
        original = axes._toytree_original_add_mark
        hook_func = axes.add_mark.__func__
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)
        self.assertTrue(axes._toytree_companion_add_mark_hook_installed)
        self.assertIs(axes._toytree_original_add_mark, original)
        self.assertIs(axes.add_mark.__func__, hook_func)

    def test_mark_scale_bar_uses_raw_tip_bar_value_domain(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=24)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(
            axes,
            bmark,
            tick_locations=[0, 1, 2],
            scale=1.0,
        )
        saxes = self._mark_scale_axes(axes, bmark)
        self.assertEqual(float(saxes.x.domain.min), 0.0)
        self.assertEqual(float(saxes.x.domain.max), 2.0)
        self.assertEqual(list(saxes.x.ticks.locator._labels), ["0", "1", "2"])

    def test_mark_scale_bar_uses_unit_data_when_bar_data_is_none(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data=None, depth=24)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(
            axes,
            bmark,
            tick_locations=[0.0, 0.5, 1.0],
            scale=1.0,
        )
        saxes = self._mark_scale_axes(axes, bmark)
        self.assertEqual(float(saxes.x.domain.min), 0.0)
        self.assertEqual(float(saxes.x.domain.max), 1.0)
        self.assertEqual(list(saxes.x.ticks.locator._labels), ["0", "0.5", "1"])

    def test_mark_scale_bar_uses_signed_internal_domain_on_left_and_down(self):
        for layout, axis in (("l", "x"), ("d", "y")):
            _, axes, _ = self.bar_tree.draw(layout=layout, scale_bar=False)
            bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=24)
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(
                axes,
                bmark,
                tick_locations=[0, 1, 2],
                scale=1.0,
            )
            saxes = self._mark_scale_axes(axes, bmark)
            active = getattr(saxes, axis)
            self.assertEqual(float(active.domain.min), -2.0)
            self.assertEqual(float(active.domain.max), 0.0)
            self.assertTrue(
                np.allclose(
                    np.asarray(active.ticks.locator._locations, dtype=float),
                    np.array([0.0, -1.0, -2.0]),
                )
            )
            self.assertEqual(list(active.ticks.locator._labels), ["0", "1", "2"])

    def test_tip_path_mark_scale_bar_is_unsupported(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        pmark = self.bar_tree.annotate.add_tip_paths(
            axes,
            spans=np.array([0.0, -4.0, 4.0]),
            ends="X",
        )
        with self.assertRaises(ToytreeError):
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(
                axes,
                pmark,
                tick_locations=[0, 1, 2],
                scale=1.0,
            )

    def test_tip_path_mark_scale_bar_is_unsupported_with_depth_fallback(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        pmark = self.bar_tree.annotate.add_tip_paths(axes, ends=None, depth=24)
        with self.assertRaises(ToytreeError):
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(
                axes,
                pmark,
                tick_locations=[0.0, 0.5, 1.0],
                scale=1.0,
            )

    def test_mark_scale_bar_rejects_zero_data(self):
        _, axes0, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark0 = self.bar_tree.annotate.add_tip_bars(
            axes0,
            data=np.zeros(self.bar_tree.ntips, dtype=float),
            depth=24,
        )
        with self.assertRaises(ToytreeError):
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes0, bmark0)

    def test_mark_scale_bar_zero_tick_stays_at_tip_baseline_for_all_layouts(self):
        expectations = {
            "r": ("x", 0, 1.0),
            "l": ("x", 1, -1.0),
            "u": ("y", 3, -1.0),
            "d": ("y", 2, 1.0),
        }
        for layout, (axis, bound_index, direction) in expectations.items():
            _, axes, _ = self.bar_tree.draw(layout=layout, scale_bar=False)
            bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=24)
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(
                axes,
                bmark,
                tick_locations=[0, 1, 2],
                scale=1.0,
            )
            saxes = self._mark_scale_axes(axes, bmark)
            _, labels, pixels = self._projected_scale_ticks(saxes, axis)
            bounds = self._overlay_bounds(saxes)
            self.assertEqual(labels[0], "0")
            self.assertAlmostEqual(float(pixels[0]), bounds[bound_index], places=6)
            self.assertTrue(np.all(np.diff(pixels) * direction > 0.0))

    def test_explicit_mark_ticks_are_clipped_to_domain(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=24)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(
            axes,
            bmark,
            tick_locations=[-1, 1, 3],
            scale=1.0,
        )
        saxes = self._mark_scale_axes(axes, bmark)
        self.assertEqual(list(saxes.x.ticks.locator._labels), ["0", "1", "2"])

    def test_add_mark_scale_bar_finalizes_host_once_on_initial_update(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=24)
        original = axes._finalize
        calls = {"count": 0}

        def counting_finalize():
            calls["count"] += 1
            return original()

        axes._finalize = counting_finalize
        try:
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)
        finally:
            axes._finalize = original

        self.assertEqual(calls["count"], 1)

    def test_add_axes_scale_bar_finalizes_host_once_on_initial_update(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=False)
        original = axes._finalize
        calls = {"count": 0}

        def counting_finalize():
            calls["count"] += 1
            return original()

        axes._finalize = counting_finalize
        try:
            self.tree.annotate.add_axes_scale_bar_to_tree(axes)
        finally:
            axes._finalize = original

        self.assertEqual(calls["count"], 1)

    def test_add_mark_scale_bar_with_existing_companions_skips_duplicate_finalize(
        self,
    ):
        _, axes, _ = self.long_bar_tree.draw(
            tip_labels_align=True,
            scale_bar=True,
            padding=15,
            width=600,
        )
        first = self.long_bar_tree.annotate.add_tip_bars(
            axes,
            data="X",
            offset=150,
            width=1.0,
            depth=75,
            style={"stroke": "black"},
        )
        self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, first)
        second = self.long_bar_tree.annotate.add_tip_bars(
            axes,
            data="X",
            offset=250,
            width=1.0,
            depth=75,
            style={"stroke": "black"},
        )

        original = add_scale_bar_mod._finalize_host_axes
        calls = {"count": 0}

        def counting_finalize(axes):
            calls["count"] += 1
            return original(axes)

        add_scale_bar_mod._finalize_host_axes = counting_finalize
        try:
            self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, second)
        finally:
            add_scale_bar_mod._finalize_host_axes = original

        self.assertEqual(calls["count"], 0)

    def test_add_tip_bars_with_existing_companions_skips_full_host_finalize(self):
        _, axes, _ = self.long_bar_tree.draw(
            tip_labels_align=True,
            scale_bar=True,
            padding=15,
            width=600,
        )
        first = self.long_bar_tree.annotate.add_tip_bars(
            axes,
            data="X",
            offset=150,
            width=1.0,
            depth=75,
            style={"stroke": "black"},
        )
        self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, first)

        original = add_scale_bar_mod._finalize_host_axes
        calls = {"count": 0}

        def counting_finalize(axes):
            calls["count"] += 1
            return original(axes)

        add_scale_bar_mod._finalize_host_axes = counting_finalize
        try:
            self.long_bar_tree.annotate.add_tip_bars(
                axes,
                data="X",
                offset=250,
                width=1.0,
                depth=75,
                style={"stroke": "black"},
            )
        finally:
            add_scale_bar_mod._finalize_host_axes = original

        self.assertEqual(calls["count"], 0)

    def test_add_tip_bars_falls_back_to_full_host_finalize_when_incremental_skips(
        self,
    ):
        _, axes, _ = self.long_bar_tree.draw(
            tip_labels_align=True,
            scale_bar=True,
            padding=15,
            width=600,
        )
        first = self.long_bar_tree.annotate.add_tip_bars(
            axes,
            data="X",
            offset=150,
            width=1.0,
            depth=75,
            style={"stroke": "black"},
        )
        self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, first)

        original_try = add_scale_bar_mod.try_incremental_tip_bar_host_finalize
        original_finalize = add_scale_bar_mod._finalize_host_axes
        calls = {"count": 0}

        def skip_incremental(axes, mark):
            return False

        def counting_finalize(axes):
            calls["count"] += 1
            return original_finalize(axes)

        add_scale_bar_mod.try_incremental_tip_bar_host_finalize = skip_incremental
        add_scale_bar_mod._finalize_host_axes = counting_finalize
        try:
            self.long_bar_tree.annotate.add_tip_bars(
                axes,
                data="X",
                offset=250,
                width=1.0,
                depth=75,
                style={"stroke": "black"},
            )
        finally:
            add_scale_bar_mod.try_incremental_tip_bar_host_finalize = original_try
            add_scale_bar_mod._finalize_host_axes = original_finalize

        self.assertEqual(calls["count"], 1)

    def test_second_tree_draw_with_existing_companions_finalizes_host_once(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=True, width=400)
        original = add_scale_bar_mod._finalize_host_axes
        calls = {"count": 0}

        def counting_finalize(axes):
            calls["count"] += 1
            return original(axes)

        add_scale_bar_mod._finalize_host_axes = counting_finalize
        try:
            _, axes, _ = self.tree.draw(
                axes=axes,
                layout="l",
                xbaseline=6,
                scale_bar=True,
            )
        finally:
            add_scale_bar_mod._finalize_host_axes = original

        self.assertEqual(calls["count"], 1)

    def test_mark_scale_bar_default_padding_is_fifteen_pixels(self):
        _, axes0, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark0 = self.bar_tree.annotate.add_tip_bars(axes0, data="X", depth=24)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes0, bmark0, padding=0)
        zero_pad = self._mark_scale_axes(axes0, bmark0)

        _, axes1, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark1 = self.bar_tree.annotate.add_tip_bars(axes1, data="X", depth=24)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes1, bmark1)
        default_pad = self._mark_scale_axes(axes1, bmark1)

        self.assertTrue(
            np.allclose(
                self._overlay_bounds(default_pad)[2:],
                np.array(self._overlay_bounds(zero_pad)[2:]) + 15.0,
            )
        )

    def test_mark_scale_bar_coexists_with_tree_scale_bar(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=True)
        tree_saxes = self._scale_axes(axes)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark, label="Trait")
        mark_saxes = self._mark_scale_axes(axes, bmark)
        canvas = axes._scenegraph.sources("render", axes)[0]
        targets = axes._scenegraph._relationships["render"]._targets[canvas]
        self.assertIsNotNone(mark_saxes)
        self.assertIsNot(tree_saxes, mark_saxes)
        self.assertIn(tree_saxes, targets)
        self.assertIn(mark_saxes, targets)
        self.assertLess(targets.index(tree_saxes), targets.index(axes))
        self.assertLess(targets.index(mark_saxes), targets.index(axes))
        self.assertTrue(mark_saxes.x.show)

    def test_mark_scale_bars_align_to_existing_tree_scale_bar_row(self):
        _, axes, _ = self.long_bar_tree.draw(
            tip_labels_align=True,
            scale_bar=True,
            padding=20,
            width=500,
        )
        m1 = self.long_bar_tree.annotate.add_tip_bars(
            axes,
            data="X",
            offset=150,
            width=1.0,
            depth=75,
            style={"stroke": "black"},
        )
        self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, m1)
        m2 = self.long_bar_tree.annotate.add_tip_bars(
            axes,
            data="X",
            offset=250,
            width=1.0,
            depth=75,
            style={"stroke": "black"},
        )
        self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, m2)
        tree_saxes = self._scale_axes(axes)
        mark1_saxes = self._mark_scale_axes(axes, m1)
        mark2_saxes = self._mark_scale_axes(axes, m2)
        self.assertAlmostEqual(
            float(mark1_saxes._ymax_range),
            float(tree_saxes._ymax_range),
            places=6,
        )
        self.assertAlmostEqual(
            float(mark2_saxes._ymax_range),
            float(tree_saxes._ymax_range),
            places=6,
        )

    def test_mark_companion_hides_interactive_coordinate_readout(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)
        saxes = self._mark_scale_axes(axes, bmark)
        self.assertFalse(saxes.x.interactive.coordinates.show)
        self.assertFalse(saxes.y.interactive.coordinates.show)

    def test_mark_scale_bar_padding_does_not_change_host_or_tree_padding(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=True)
        tree_saxes = self._scale_axes(axes)
        host_padding = float(axes.padding)
        tree_padding = float(tree_saxes.padding)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark, padding=30)
        self.assertEqual(float(axes.padding), host_padding)
        self.assertEqual(float(tree_saxes.padding), tree_padding)

    def test_equal_tree_and_mark_padding_give_equal_local_gaps(self):
        _, axes, tmark = self.bar_tree.draw(width=400, height=400, scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(
            axes,
            data="X",
            depth=100,
            offset=40,
            width=1,
            below=True,
            opacity=0.25,
            style={"stroke": "black"},
        )
        self.bar_tree.annotate.add_axes_scale_bar_to_tree(axes, padding=20)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark, padding=20)
        tree_saxes = self._scale_axes(axes)
        mark_saxes = self._mark_scale_axes(axes, bmark)
        _, _, _, tree_bottom = self._projected_bounds(axes, tmark)
        _, _, _, bar_bottom = self._visible_tip_bar_bounds(axes, bmark)
        self.assertAlmostEqual(
            float(tree_saxes._ymax_range) - tree_bottom, 20.0, places=3
        )
        self.assertAlmostEqual(
            float(mark_saxes._ymax_range) - bar_bottom, 20.0, places=3
        )

    def test_mark_scale_bar_repeated_calls_update_same_overlay(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(
            axes,
            bmark,
            label="Trait A",
            padding=0,
        )
        first = self._mark_scale_axes(axes, bmark)
        before = self._overlay_bounds(first)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(
            axes,
            bmark,
            label="Trait B",
            tick_locations=[0, 2],
            scale=1.0,
            padding=30,
        )
        second = self._mark_scale_axes(axes, bmark)
        self.assertIs(first, second)
        self.assertEqual(second.x.label.text, "Trait B")
        self.assertEqual(list(second.x.ticks.locator._labels), ["0", "2"])
        self.assertNotEqual(before, self._overlay_bounds(second))

    def test_large_offset_tip_bar_fits_host_without_companions(self):
        _, axes, _ = self.long_bar_tree.draw(
            tip_labels_align=True,
            scale_bar=False,
            width=700,
        )
        bmark = self.long_bar_tree.annotate.add_tip_bars(
            axes,
            data="X",
            offset=350,
            width=1.0,
            depth=75,
            style={"stroke": "black"},
        )
        axes._finalize()
        xmax = self._projected_bounds(axes, bmark)[1]
        self.assertLessEqual(xmax, float(axes._xmax_range) + 0.5)

    def test_tip_bar_domain_stays_raw_anchor_domain(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False, width=500)
        bmark = self.bar_tree.annotate.add_tip_bars(
            axes,
            data="X",
            offset=120,
            width=1.0,
            depth=60,
            style={"stroke": "black"},
        )
        raw_x_domain = (
            float(np.min(bmark.ntable[:, 0])),
            float(np.max(bmark.ntable[:, 0])),
        )
        actual = bmark.domain("x")
        self.assertTrue(
            np.allclose(np.asarray(actual), np.asarray(raw_x_domain), atol=1e-8)
        )

    def test_multiple_mark_companions_keep_large_offset_tip_bars_in_host_fit(self):
        _, axes, _ = self.long_bar_tree.draw(
            tip_labels_align=True,
            scale_bar=True,
            padding=20,
            width=700,
        )
        marks = []
        for offset in (150, 250, 350):
            bmark = self.long_bar_tree.annotate.add_tip_bars(
                axes,
                data="X",
                offset=offset,
                width=1.0,
                depth=75,
                style={"stroke": "black"},
            )
            self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)
            marks.append(bmark)

        axes._finalize()
        self.assertEqual(len(getattr(axes, "_toytree_mark_scale_axes", {})), 3)
        self.assertEqual(
            len({id(self._mark_scale_axes(axes, mark)) for mark in marks}),
            3,
        )
        xmax = self._projected_bounds(axes, marks[-1])[1]
        self.assertLessEqual(xmax, float(axes._xmax_range) + 0.5)

    def test_multiple_mark_companions_share_projected_tip_slot_cache(self):
        _, axes, _ = self.long_bar_tree.draw(
            tip_labels_align=True,
            scale_bar=True,
            padding=20,
            width=700,
        )
        original = add_scale_bar_mod._compute_projected_tip_slot_bounds_finalized
        calls = {"count": 0}

        def counting_bounds(axes, mark):
            calls["count"] += 1
            return original(axes, mark)

        add_scale_bar_mod._compute_projected_tip_slot_bounds_finalized = counting_bounds
        try:
            for offset in (150, 250, 350):
                bmark = self.long_bar_tree.annotate.add_tip_bars(
                    axes,
                    data="X",
                    offset=offset,
                    width=1.0,
                    depth=75,
                    style={"stroke": "black"},
                )
                self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)
        finally:
            add_scale_bar_mod._compute_projected_tip_slot_bounds_finalized = original

        self.assertEqual(calls["count"], 3)

    def test_host_axis_stays_raw_data_domain_when_shown(self):
        _, axes, _ = self.long_bar_tree.draw(
            tip_labels_align=True,
            scale_bar=True,
            padding=15,
            width=600,
        )
        marks = []
        for offset in (150, 250, 350):
            bmark = self.long_bar_tree.annotate.add_tip_bars(
                axes,
                data="X",
                offset=offset,
                width=1.0,
                depth=75,
                style={"stroke": "black"},
            )
            self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)
            marks.append(bmark)

        axes.x.show = True
        axes._finalize()
        axis_right = float(axes.x.projection(axes.x._data_max))
        bar_right = self._projected_bounds(axes, marks[-1])[1]
        self.assertLess(axis_right + 1.0, bar_right)

    def test_newest_mark_scale_bar_resyncs_to_final_host_projection(self):
        _, axes, _ = self.long_bar_tree.draw(
            tip_labels_align=True,
            scale_bar=True,
            padding=15,
            width=600,
        )
        for offset in (150, 250):
            bmark = self.long_bar_tree.annotate.add_tip_bars(
                axes,
                data="X",
                offset=offset,
                width=1.0,
                depth=75,
                style={"stroke": "black"},
            )
            self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)

        newest = self.long_bar_tree.annotate.add_tip_bars(
            axes,
            data="X",
            offset=350,
            width=1.0,
            depth=75,
            style={"stroke": "black"},
        )
        self.long_bar_tree.annotate.add_axes_scale_bar_to_mark(axes, newest)
        axes._finalize()
        helper_bounds = _get_linear_tip_bar_scale_bounds_finalized(axes, newest, 15.0)
        self.assertTrue(
            np.allclose(
                np.asarray(self._overlay_bounds(self._mark_scale_axes(axes, newest))),
                np.asarray(helper_bounds),
            )
        )

    def test_mark_scale_bar_syncs_when_tree_scale_bar_expands_margin(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)
        mark_saxes = self._mark_scale_axes(axes, bmark)
        before = (
            float(mark_saxes._xmin_range),
            float(mark_saxes._xmax_range),
            float(mark_saxes._ymin_range),
            float(mark_saxes._ymax_range),
        )
        self.bar_tree.annotate.add_axes_scale_bar_to_tree(axes, expand_margin=20)
        after = (
            float(mark_saxes._xmin_range),
            float(mark_saxes._xmax_range),
            float(mark_saxes._ymin_range),
            float(mark_saxes._ymax_range),
        )
        self.assertNotEqual(before, after)

    def test_mark_scale_bar_rejects_unsupported_mark(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=False)
        lmark = self.tree.annotate.add_tip_text(axes, labels=self.tree.get_tip_labels())
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_axes_scale_bar_to_mark(axes, lmark)

    def test_mark_scale_bar_rejects_circular_tip_bars(self):
        _, axes, _ = self.bar_tree.draw(layout="c", edge_type="p", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        with self.assertRaises(ToytreeError):
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark)

    def test_mark_scale_bar_rejects_invalid_padding(self):
        _, axes, _ = self.bar_tree.draw(layout="r", scale_bar=False)
        bmark = self.bar_tree.annotate.add_tip_bars(axes, data="X", depth=18)
        with self.assertRaises(ToytreeError):
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(axes, bmark, padding=-1)
        with self.assertRaises(ToytreeError):
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(
                axes,
                bmark,
                padding=float("inf"),
            )
        with self.assertRaises(ToytreeError):
            self.bar_tree.annotate.add_axes_scale_bar_to_mark(
                axes,
                bmark,
                padding=float("nan"),
            )

    def test_tree_scale_bar_rejects_invalid_padding(self):
        _, axes, _ = self.tree.draw(layout="r", scale_bar=False)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_axes_scale_bar_to_tree(axes, padding=-1)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_axes_scale_bar_to_tree(axes, padding=float("inf"))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_axes_scale_bar_to_tree(axes, padding=float("nan"))
