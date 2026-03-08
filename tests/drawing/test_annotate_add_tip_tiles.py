#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for annotate.add_tip_tiles."""

import xml.etree.ElementTree as xml

import numpy as np
import toyplot.html

import toytree
from toytree.utils import ToytreeError



from conftest import PytestCompat

class TestAnnotateAddTipTiles(PytestCompat):
    def setUp(self):
        self.tree = toytree.rtree.unittree(ntips=10, seed=123)
        vals = {i: i % 3 for i in range(self.tree.ntips)}
        self.tree = self.tree.set_node_data("X", vals, default=np.nan, inplace=False)

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

        by_tip_full = {int(t): p for t, p in zip(full.tip_indices, full.paths)}
        by_tip_mask = {int(t): p for t, p in zip(masked.tip_indices, masked.paths)}
        for tidx in np.where(mask)[0]:
            self.assertIn(int(tidx), by_tip_mask)
            self.assertEqual(by_tip_mask[int(tidx)], by_tip_full[int(tidx)])

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

    def test_add_tip_tiles_stroke_none_and_set(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=8, stroke=None)
        text = xml.tostring(toyplot.html.render(c), encoding="unicode")
        self.assertIn("toytree-Annotation-TipTiles", text)
        self.assertIn("stroke:none", text)

        c2, a2, m2 = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_tip_tiles(
            a2,
            color="steelblue",
            depth=8,
            stroke="black",
        )
        text2 = xml.tostring(toyplot.html.render(c2), encoding="unicode")
        self.assertIn("stroke:rgb", text2)

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

    def test_add_tip_tiles_default_renders_above_tree(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(a, color="steelblue", depth=8)
        render_targets = a._scenegraph._relationships["render"]._targets[a]
        self.assertLess(render_targets.index(m), render_targets.index(mark))

    def test_add_tip_tiles_below_renders_below_tree(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_tiles(
            a,
            color="steelblue",
            depth=8,
            below=True,
        )
        render_targets = a._scenegraph._relationships["render"]._targets[a]
        self.assertLess(render_targets.index(mark), render_targets.index(m))
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


