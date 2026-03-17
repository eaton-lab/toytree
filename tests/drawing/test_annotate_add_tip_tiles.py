#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for annotate.add_tip_tiles."""

import inspect

import numpy as np
import toyplot.html
from conftest import PytestCompat

import toytree
from toytree.annotate.src.add_tip_tiles import add_tip_tiles
from toytree.color import ToyColor
from toytree.drawing.src.mark_toytree import set_tip_label_extents
from toytree.utils import ToytreeError


class TestAnnotateAddTipTiles(PytestCompat):
    def setUp(self):
        self.tree = toytree.rtree.unittree(ntips=10, seed=123)
        vals = {i: i % 3 for i in range(self.tree.ntips)}
        self.tree = self.tree.set_node_data("X", vals, default=np.nan, inplace=False)

    @staticmethod
    def _assert_layout_u_tip_tiles_fit_axes(mark, axes):
        tips_y_px = np.asarray(axes.project("y", mark.ntable[:, 1]), dtype=float)
        actual_left = float(np.min(mark.slot_min))
        actual_right = float(np.max(mark.slot_max))
        actual_top = float(
            np.min(tips_y_px[mark.tip_indices] - float(mark.offset) - float(mark.depth))
        )
        assert actual_left >= float(axes._xmin_range) - 1e-6
        assert actual_right <= float(axes._xmax_range) + 1e-6
        assert actual_top >= float(axes._ymin_range) - 1e-6

    @staticmethod
    def _tip_tile_paths(root):
        return [
            elem
            for elem in root.iter()
            if elem.attrib.get("id", "").startswith("TipTile-")
        ]

    def test_add_tip_tiles_signature_uses_style_and_defaults_below_true(self):
        params = inspect.signature(add_tip_tiles).parameters
        self.assertIn("style", params)
        self.assertNotIn("stroke", params)
        self.assertIsNone(params["depth"].default)
        self.assertTrue(params["below"].default)

    def test_add_tip_tiles_auto_depth_matches_tip_labels_rectangular(self):
        labels = [f"very_long_tip_label_{idx}" for idx in range(self.tree.ntips)]
        c, a, m = self.tree.draw(
            layout="r",
            edge_type="p",
            tip_labels=labels,
            tip_labels_style={"font-size": "18px"},
        )
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue")
        toyplot.html.render(c)
        expected = self._get_expected_auto_depth(
            m, np.ones(self.tree.ntips, dtype=bool)
        )
        self.assertAlmostEqual(mark.depth, expected)

    def test_add_tip_tiles_auto_depth_matches_tip_labels_circular(self):
        labels = [f"very_long_tip_label_{idx}" for idx in range(self.tree.ntips)]
        c, a, m = self.tree.draw(
            layout="c",
            edge_type="p",
            tip_labels=labels,
            tip_labels_style={"font-size": "18px"},
        )
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=None)
        toyplot.html.render(c)
        expected = self._get_expected_auto_depth(
            m, np.ones(self.tree.ntips, dtype=bool)
        )
        self.assertAlmostEqual(mark.depth, expected)

    def test_add_tip_tiles_auto_depth_falls_back_without_tip_labels(self):
        c, a, _ = self.tree.draw(layout="r", edge_type="p", tip_labels=False)
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue")
        toyplot.html.render(c)
        self.assertEqual(mark.depth, 10.0)

    def test_add_tip_tiles_auto_depth_uses_only_shown_tips(self):
        labels = ["x"] * self.tree.ntips
        labels[-1] = "very_long_hidden_tip_label"
        c, a, m = self.tree.draw(
            layout="r",
            edge_type="p",
            tip_labels=labels,
            tip_labels_style={"font-size": "18px"},
        )
        mask = np.ones(self.tree.ntips, dtype=bool)
        mask[-1] = False
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue", mask=mask)
        toyplot.html.render(c)
        expected = self._get_expected_auto_depth(m, mask)
        self.assertAlmostEqual(mark.depth, expected)

    def test_add_tip_tiles_smoke_rectangular(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(
            a,
            color="steelblue",
            depth=8,
            offset=2,
        )
        toyplot.html.render(c)
        self.assertIsNotNone(mark)
        self.assertGreater(len(mark.paths), 0)

    def test_add_tip_tiles_smoke_circular(self):
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(
            a,
            color="steelblue",
            depth=8,
            offset=2,
        )
        toyplot.html.render(c)
        self.assertIsNotNone(mark)
        self.assertEqual(len(mark.paths), self.tree.ntips)

    def test_add_tip_tiles_smoke_circular_partial_arc(self):
        c, a, m = self.tree.draw(layout="c0-180", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(
            a,
            color="steelblue",
            depth=8,
            offset=2,
        )
        toyplot.html.render(c)
        self.assertIsNotNone(mark)
        self.assertEqual(len(mark.paths), self.tree.ntips)

    def test_add_tip_tiles_rectangular_slots_touch_without_gaps(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=8)
        toyplot.html.render(c)
        order = np.argsort(mark.slot_min)
        mins = mark.slot_min[order]
        maxs = mark.slot_max[order]
        self.assertTrue(np.allclose(maxs[:-1], mins[1:], atol=1e-8, rtol=0.0))

    def test_add_tip_tiles_circular_slots_touch_without_gaps(self):
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=8)
        toyplot.html.render(c)
        # Normalize slots to sorted contiguous [a, b) representation.
        lo = np.mod(mark.slot_min, 2.0 * np.pi)
        hi = np.mod(mark.slot_max, 2.0 * np.pi)
        spans = np.where(hi >= lo, hi - lo, hi + 2.0 * np.pi - lo)
        order = np.argsort(lo)
        lo_s = lo[order]
        spans_s = spans[order]
        hi_s = lo_s + spans_s
        # compare internal adjacencies + wrap-around adjacency.
        self.assertTrue(np.allclose(hi_s[:-1], lo_s[1:], atol=1e-7, rtol=0.0))
        self.assertAlmostEqual((hi_s[-1] - lo_s[0]) % (2.0 * np.pi), 0.0, places=6)

    def test_add_tip_tiles_circular_partial_arc_slots_open_no_wrap(self):
        c, a, m = self.tree.draw(layout="c0-180", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=8)
        toyplot.html.render(c)
        order = np.argsort(mark.slot_min)
        mins = mark.slot_min[order]
        maxs = mark.slot_max[order]
        # Internal neighbors are contiguous, but endpoints remain open.
        self.assertTrue(np.allclose(maxs[:-1], mins[1:], atol=1e-7, rtol=0.0))
        self.assertGreater(mins[0], -1e6)  # smoke against NaN/inf regressions
        self.assertGreater(maxs[-1] - mins[0], 0.0)

    def test_add_tip_tiles_circular_partial_arc_no_oversized_boundary_sector(self):
        c, a, m = self.tree.draw(layout="c0-180", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=8)
        toyplot.html.render(c)
        spans = mark.slot_max - mark.slot_min
        med = float(np.median(spans))
        self.assertLess(float(np.max(spans)), med * 2.5)

    def test_add_tip_tiles_circular_partial_arc_matches_tip_side(self):
        c, a, m = self.tree.draw(layout="c0-180", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=8)
        toyplot.html.render(c)
        self._assert_tile_angles_match_tip_angles(mark, a, m)

    def test_add_tip_tiles_circular_partial_arc_matches_tip_side_no_labels(self):
        c, a, m = self.tree.draw(layout="c0-180", edge_type="p", tip_labels=False)
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=8)
        toyplot.html.render(c)
        self._assert_tile_angles_match_tip_angles(mark, a, m)

    def test_add_tip_tiles_mask_preserves_tip_slot_positions(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        full = self.tree.annotate.add_tip_tiles(a, color=("X", "Set2"), depth=10)
        toyplot.html.render(c)

        c2, a2, m2 = self.tree.draw(layout="d", edge_type="p")
        mask = np.zeros(self.tree.ntips, dtype=bool)
        mask[::2] = True
        masked = self.tree.annotate.add_tip_tiles(
            a2, color=("X", "Set2"), depth=10, mask=mask
        )
        toyplot.html.render(c2)

        self.assertEqual(len(full.paths), self.tree.ntips)
        self.assertTrue(np.array_equal(masked.tip_indices, np.where(mask)[0]))
        self.assertEqual(len(masked.paths), int(np.sum(mask)))

    def test_add_tip_tiles_domain_uses_occupied_corners_rectangular(self):
        _, axes, _ = self.tree.draw(layout="u", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(axes, color="steelblue", depth=8)
        domain_x = mark.domain("x")
        self.assertAlmostEqual(domain_x[0], -0.5)
        self.assertAlmostEqual(domain_x[1], self.tree.ntips - 0.5)

    def test_add_tip_tiles_masked_domain_ignores_hidden_tips(self):
        _, axes, _ = self.tree.draw(layout="u", edge_type="p")
        mask = np.ones(self.tree.ntips, dtype=bool)
        mask[0] = False
        mark = self.tree.annotate.add_tip_tiles(
            axes,
            color="steelblue",
            depth=8,
            mask=mask,
        )
        domain_x = mark.domain("x")
        self.assertAlmostEqual(domain_x[0], 0.5)
        self.assertAlmostEqual(domain_x[1], self.tree.ntips - 0.5)

        hidden = self.tree.annotate.add_tip_tiles(
            axes,
            color="steelblue",
            depth=8,
            mask=False,
        )
        self.assertEqual(hidden.domain("x"), (None, None))
        coords, extents = hidden.extents("xy")
        self.assertEqual(coords[0].size, 0)
        self.assertEqual(coords[1].size, 0)
        self.assertEqual(extents[0].size, 0)

    def test_add_tip_tiles_style_fill_used_when_color_is_none(self):
        _, axes, _ = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(
            axes,
            depth=8,
            style={"fill": "orange"},
        )
        self.assertEqual(str(mark.fill_color), str(ToyColor("orange")))

    def test_add_tip_tiles_explicit_color_beats_style_fill(self):
        _, axes, _ = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(
            axes,
            color="steelblue",
            depth=8,
            style={"fill": "orange"},
        )
        self.assertEqual(str(mark.fill_color), str(ToyColor("steelblue")))

    def test_add_tip_tiles_default_fill_is_lightgrey(self):
        _, axes, _ = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(axes, depth=8)
        self.assertEqual(str(mark.fill_color), str(ToyColor("lightgrey")))

    def test_add_tip_tiles_supports_feature_color_mapping(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(a, color=("X", "Set2"), depth=7)
        toyplot.html.render(c)
        self.assertIsNotNone(mark)
        self.assertEqual(len(mark.paths), self.tree.ntips)

    def test_add_tip_tiles_accepts_bool_mask(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        shown = self.tree.annotate.add_tip_tiles(
            a, color="steelblue", depth=8, mask=True
        )
        hidden = self.tree.annotate.add_tip_tiles(
            a, color="steelblue", depth=8, mask=False
        )
        toyplot.html.render(c)
        self.assertEqual(len(shown.paths), self.tree.ntips)
        self.assertEqual(len(hidden.paths), 0)

    def test_add_tip_tiles_accepts_tuple_mask(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(
            a, color="steelblue", depth=8, mask=(1, 1, 1)
        )
        toyplot.html.render(c)
        self.assertEqual(len(mark.paths), self.tree.ntips)

    def test_add_tip_tiles_rejects_nnodes_mask_array(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        bad = np.ones(self.tree.nnodes, dtype=bool)
        with self.assertRaises(ValueError):
            self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=8, mask=bad)

    def test_add_tip_tiles_defaults_stroke_to_none(self):
        canvas, axes, _ = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(
            axes,
            depth=8,
            style={"stroke_width": 3},
        )
        root = toyplot.html.render(canvas)
        paths = self._tip_tile_paths(root)
        self.assertEqual(len(paths), self.tree.ntips)
        self.assertEqual(mark.style["stroke"], "none")
        style = paths[0].attrib["style"].replace(" ", "")
        self.assertIn("stroke-opacity:0.0", style)
        self.assertIn("stroke-width:3", style)

    def test_add_tip_tiles_style_stroke_renders_on_paths(self):
        canvas, axes, _ = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_tip_tiles(
            axes,
            depth=8,
            style={
                "stroke": "black",
                "stroke_width": 2,
                "stroke_dasharray": "3,2",
            },
        )
        root = toyplot.html.render(canvas)
        paths = self._tip_tile_paths(root)
        self.assertEqual(len(paths), self.tree.ntips)
        style = paths[0].attrib["style"].replace(" ", "")
        self.assertIn("stroke-width:2", style)
        self.assertIn("stroke-dasharray:3,2", style)
        self.assertNotIn("stroke:none", style)

    def test_add_tip_tiles_rejects_invalid_depth(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_tiles(a, depth=0)

    def test_add_tip_tiles_rejects_unsupported_layout(self):
        c, a, m = self.tree.draw(layout="unr")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_tiles(a, depth=5)

    def test_add_tip_tiles_extents_include_circular_offset_and_depth(self):
        c, a, m = self.tree.draw(layout="c0-180", tip_labels=False)
        mark = self.tree.annotate.add_tip_tiles(a, color="idx", offset=10, depth=30)
        coords, ext = mark.extents("xy")
        left, right, top, bottom = ext
        self.assertTrue(np.all(left <= -39.9))
        self.assertTrue(np.all(right >= 39.9))
        self.assertTrue(np.all(top <= -39.9))
        self.assertTrue(np.all(bottom >= 39.9))

    def test_add_tip_tiles_extents_directional_rectangular(self):
        c, a, m = self.tree.draw(layout="r", tip_labels=False)
        mark = self.tree.annotate.add_tip_tiles(a, color="idx", offset=10, depth=30)
        coords, ext = mark.extents("xy")
        left, right, top, bottom = ext
        self.assertTrue(np.allclose(left, 0.0))
        self.assertTrue(np.all(right >= 40.0))
        self.assertTrue(np.allclose(top, 0.0))
        self.assertTrue(np.allclose(bottom, 0.0))

    def test_add_tip_tiles_extents_support_negative_offset(self):
        c, a, m = self.tree.draw(layout="r", tip_labels=False)
        mark = self.tree.annotate.add_tip_tiles(a, color="idx", offset=-10, depth=30)
        coords, ext = mark.extents("xy")
        left, right, top, bottom = ext
        self.assertTrue(np.all(left <= -10.0))
        self.assertTrue(np.all(right >= 20.0))

    def test_add_tip_tiles_fit_layout_u_uses_rect_corners(self):
        canvas, axes, _ = self.tree.draw(layout="u", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(axes, color="steelblue", depth=8)
        toyplot.html.render(canvas)
        self._assert_layout_u_tip_tiles_fit_axes(mark, axes)

    def test_add_tip_tiles_default_renders_below_tree(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=8)
        render_targets = a._scenegraph._relationships["render"]._targets[a]
        self.assertLess(render_targets.index(mark), render_targets.index(m))

    def test_add_tip_tiles_above_renders_above_tree(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(
            a,
            color="steelblue",
            depth=8,
            below=False,
        )
        render_targets = a._scenegraph._relationships["render"]._targets[a]
        self.assertLess(render_targets.index(m), render_targets.index(mark))
        toyplot.html.render(c)

    def _assert_tile_angles_match_tip_angles(self, mark, axes, tmark):
        tips_x = axes.project("x", tmark.ttable[: self.tree.ntips, 0])
        tips_y = axes.project("y", tmark.ttable[: self.tree.ntips, 1])
        root_x = float(axes.project("x", tmark.ntable[self.tree.treenode.idx, 0]))
        root_y = float(axes.project("y", tmark.ntable[self.tree.treenode.idx, 1]))
        tip_theta = np.arctan2(tips_y - root_y, tips_x - root_x)
        tile_theta = 0.5 * (mark.slot_min + mark.slot_max)
        delta = np.abs(
            np.arctan2(
                np.sin(tile_theta - tip_theta),
                np.cos(tile_theta - tip_theta),
            )
        )
        self.assertTrue(np.all(delta < 0.35))

    def _get_expected_auto_depth(self, tmark, show):
        if tmark.tip_labels is None or not np.any(show):
            return 10.0

        ntips = len(tmark.tip_labels)
        extents = [np.zeros(tmark.nnodes, dtype=float) for _ in range(4)]
        left, right, top, bottom = set_tip_label_extents(tmark, extents)
        left = left[:ntips][show]
        right = right[:ntips][show]
        top = top[:ntips][show]
        bottom = bottom[:ntips][show]

        if tmark.layout == "r":
            outward = right
        elif tmark.layout == "l":
            outward = -left
        elif tmark.layout == "u":
            outward = -top
        elif tmark.layout == "d":
            outward = bottom
        else:
            angles = np.deg2rad(
                np.asarray(tmark.tip_labels_angles[:ntips], dtype=float)[show]
            )
            unit_x = np.cos(angles)
            unit_y = -np.sin(angles)
            projections = np.column_stack(
                (
                    left * unit_x + top * unit_y,
                    left * unit_x + bottom * unit_y,
                    right * unit_x + top * unit_y,
                    right * unit_x + bottom * unit_y,
                )
            )
            outward = np.max(projections, axis=1)
        return float(np.max(outward) + 15.0)
