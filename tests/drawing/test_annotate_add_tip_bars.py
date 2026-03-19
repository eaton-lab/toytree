#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for annotate.add_tip_bars."""

import inspect

import numpy as np
import toyplot.html
from conftest import PytestCompat

import toytree
from toytree.color import ToyColor
from toytree.drawing.src.mark_toytree import set_marker_extents, set_tip_label_extents
from toytree.utils import ToytreeError


class TestAnnotateAddTipBars(PytestCompat):
    def setUp(self):
        self.tree = toytree.rtree.unittree(ntips=10, seed=123)
        vals = {i: float(i) for i in range(self.tree.ntips)}
        self.tree = self.tree.set_node_data("X", vals, default=np.nan, inplace=False)

    @staticmethod
    def _expected_auto_offset(tree, tmark, show):
        ntips = tree.ntips
        if not np.any(show):
            return 10.0

        if tmark.tip_labels is not None:
            extents = [np.zeros(tmark.nnodes, dtype=float) for _ in range(4)]
            left, right, top, bottom = set_tip_label_extents(tmark, extents)
            use_label_angles = True
        else:
            extents = [np.zeros(tmark.nnodes, dtype=float) for _ in range(4)]
            left, right, top, bottom = set_marker_extents(tmark, extents)
            use_label_angles = False

        left = left[:ntips][show]
        right = right[:ntips][show]
        top = top[:ntips][show]
        bottom = bottom[:ntips][show]
        layout = str(tmark.layout)

        if layout == "r":
            outward = right
        elif layout == "l":
            outward = -left
        elif layout == "u":
            outward = -top
        elif layout == "d":
            outward = bottom
        else:
            if use_label_angles:
                angles = np.deg2rad(
                    np.asarray(tmark.tip_labels_angles[:ntips], dtype=float)[show]
                )
                unit_x = np.cos(angles)
                unit_y = -np.sin(angles)
            else:
                root_xy = np.asarray(tmark.ntable[tree.treenode.idx], dtype=float)
                tips_xy = np.asarray(tmark.ttable[:ntips], dtype=float)[show]
                vectors = tips_xy - root_xy[None, :]
                norms = np.linalg.norm(vectors, axis=1)
                norms[norms == 0.0] = 1.0
                unit_x = vectors[:, 0] / norms
                unit_y = vectors[:, 1] / norms
            outward = np.max(
                np.column_stack(
                    (
                        left * unit_x + top * unit_y,
                        left * unit_x + bottom * unit_y,
                        right * unit_x + top * unit_y,
                        right * unit_x + bottom * unit_y,
                    )
                ),
                axis=1,
            )
        return float(np.max(np.maximum(outward, 0.0)) + 10.0)

    @staticmethod
    def _tip_bar_paths(root):
        return [
            elem
            for elem in root.iter()
            if elem.attrib.get("id", "").startswith("TipBar-")
        ]

    @staticmethod
    def _tip_bar_titles(root):
        titles = []
        for path in TestAnnotateAddTipBars._tip_bar_paths(root):
            for child in path:
                if child.tag.endswith("title"):
                    titles.append(child.text)
        return titles

    @staticmethod
    def _assert_layout_u_tip_bars_fit_axes(mark, axes, stroke_half_width):
        shown = np.where(mark.show)[0]
        tips_y_px = np.asarray(axes.project("y", mark.ntable[:, 1]), dtype=float)
        actual_left = float(np.min(mark.occupied_min)) - stroke_half_width
        actual_right = float(np.max(mark.occupied_max)) + stroke_half_width
        actual_top = (
            float(
                np.min(
                    tips_y_px[shown]
                    - float(mark.offset)
                    - np.asarray(mark.bar_depths, dtype=float)[shown]
                )
            )
            - stroke_half_width
        )
        assert actual_left >= float(axes._xmin_range) - 1e-6
        assert actual_right <= float(axes._xmax_range) + 1e-6
        assert actual_top >= float(axes._ymin_range) - 1e-6

    def test_signature_uses_style_and_hover_not_stroke(self):
        params = inspect.signature(self.tree.annotate.add_tip_bars).parameters
        self.assertIsNone(params["data"].default)
        self.assertIn("style", params)
        self.assertIn("hover", params)
        self.assertNotIn("stroke", params)
        self.assertIsNone(params["offset"].default)
        self.assertIsNone(params["opacity"].default)
        self.assertTrue(params["below"].default)
        self.assertTrue(params["hover"].default)

    def test_add_tip_bars_smoke_rectangular(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(
            a,
            data="X",
            color="steelblue",
            depth=24,
            offset=2,
        )
        toyplot.html.render(c)
        self.assertIsNotNone(mark)
        self.assertEqual(len(mark.paths), self.tree.ntips)

    def test_add_tip_bars_smoke_circular(self):
        c, a, _ = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(
            a,
            data="X",
            color="steelblue",
            depth=24,
            offset=2,
        )
        toyplot.html.render(c)
        self.assertIsNotNone(mark)
        self.assertEqual(len(mark.paths), self.tree.ntips)

    def test_add_tip_bars_smoke_circular_partial_arc(self):
        c, a, _ = self.tree.draw(layout="c0-180", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(
            a,
            data="X",
            color="steelblue",
            depth=24,
            offset=2,
        )
        toyplot.html.render(c)
        self.assertIsNotNone(mark)
        self.assertEqual(len(mark.paths), self.tree.ntips)

    def test_add_tip_bars_values_normalize_to_depth(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        vals = np.arange(self.tree.ntips, dtype=float)
        mark = self.tree.annotate.add_tip_bars(a, data=vals, depth=30)
        toyplot.html.render(c)
        expected = vals / vals.max() * 30.0
        self.assertTrue(np.allclose(mark.bar_depths, expected))

    def test_add_tip_bars_data_none_uses_full_depth_and_unit_metadata(self):
        canvas, axes, _ = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(axes, depth=30)
        root = toyplot.html.render(canvas)
        self.assertTrue(np.allclose(mark.bar_depths, 30.0))
        self.assertTrue(np.allclose(mark.data, np.ones(self.tree.ntips)))
        self.assertEqual(mark.value_min, 0.0)
        self.assertEqual(mark.value_max, 1.0)
        self.assertIn(f"{self.tree[0].name}: 1", self._tip_bar_titles(root))

    def test_add_tip_bars_selects_tree_specific_mark_on_shared_axes(self):
        other = toytree.rtree.unittree(
            ntips=self.tree.ntips,
            seed=333,
            random_names=True,
        )
        _, axes, tmark1 = self.tree.draw(layout="r", width=500)
        _, axes, tmark2 = other.draw(axes=axes, layout="l", xbaseline=2)
        mark = self.tree.annotate.add_tip_bars(axes, data="X", depth=30)
        self.assertIs(mark.host_tree_mark, tmark1)
        self.assertIsNot(mark.host_tree_mark, tmark2)
        self.assertTrue(
            np.allclose(mark.ntable, np.asarray(tmark1.ttable[: self.tree.ntips]))
        )
        self.assertFalse(
            np.allclose(mark.ntable, np.asarray(tmark2.ttable[: self.tree.ntips]))
        )

    def test_add_tip_bars_stores_raw_scale_metadata(self):
        _, a, _ = self.tree.draw(layout="d", edge_type="p")
        vals = np.arange(self.tree.ntips, dtype=float)
        mark = self.tree.annotate.add_tip_bars(a, data=vals, depth=30)
        self.assertTrue(np.allclose(mark.data, vals))
        self.assertEqual(mark.value_min, 0.0)
        self.assertEqual(mark.value_max, float(vals.max()))
        self.assertEqual(mark.max_bar_depth, 30.0)

    def test_add_tip_bars_auto_offset_uses_shown_tip_labels(self):
        _, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        show = np.zeros(self.tree.ntips, dtype=bool)
        show[::2] = True
        mark = self.tree.annotate.add_tip_bars(axes, data="X", mask=show)
        expected = self._expected_auto_offset(self.tree, tmark, show)
        self.assertAlmostEqual(float(mark.offset), expected)

    def test_add_tip_bars_auto_offset_uses_tip_markers_without_labels(self):
        _, axes, tmark = self.tree.draw(
            layout="r",
            edge_type="p",
            tip_labels=False,
            node_sizes=12,
            node_mask=(True, False, False),
        )
        show = np.ones(self.tree.ntips, dtype=bool)
        mark = self.tree.annotate.add_tip_bars(axes, data="X")
        expected = self._expected_auto_offset(self.tree, tmark, show)
        self.assertAlmostEqual(float(mark.offset), expected)

    def test_add_tip_bars_auto_offset_uses_circular_outward_extent(self):
        _, axes, tmark = self.tree.draw(layout="c0-180", edge_type="p")
        show = np.ones(self.tree.ntips, dtype=bool)
        mark = self.tree.annotate.add_tip_bars(axes, data="X")
        expected = self._expected_auto_offset(self.tree, tmark, show)
        self.assertAlmostEqual(float(mark.offset), expected)

    def test_add_tip_bars_width_one_fills_full_slot(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(a, data="X", width=1.0)
        toyplot.html.render(c)
        self.assertTrue(np.allclose(mark.occupied_min, mark.slot_min))
        self.assertTrue(np.allclose(mark.occupied_max, mark.slot_max))

    def test_add_tip_bars_width_below_one_centers_gaps_rectangular(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(a, data="X", width=0.5)
        toyplot.html.render(c)
        slot_span = mark.slot_max - mark.slot_min
        occupied_span = mark.occupied_max - mark.occupied_min
        slot_center = 0.5 * (mark.slot_min + mark.slot_max)
        occupied_center = 0.5 * (mark.occupied_min + mark.occupied_max)
        self.assertTrue(np.allclose(occupied_span, slot_span * 0.5))
        self.assertTrue(np.allclose(occupied_center, slot_center))

    def test_add_tip_bars_width_below_one_centers_gaps_circular(self):
        c, a, _ = self.tree.draw(layout="c0-180", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(a, data="X", width=0.4)
        toyplot.html.render(c)
        slot_span = mark.slot_max - mark.slot_min
        occupied_span = mark.occupied_max - mark.occupied_min
        slot_center = 0.5 * (mark.slot_min + mark.slot_max)
        occupied_center = 0.5 * (mark.occupied_min + mark.occupied_max)
        self.assertTrue(np.allclose(occupied_span, slot_span * 0.4))
        self.assertTrue(np.allclose(occupied_center, slot_center))

    def test_add_tip_bars_domain_uses_occupied_corners_rectangular(self):
        _, axes, _ = self.tree.draw(layout="u", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(axes, data="X", width=0.5)
        domain_x = mark.domain("x")
        self.assertAlmostEqual(domain_x[0], -0.25)
        self.assertAlmostEqual(domain_x[1], self.tree.ntips - 0.75)

    def test_add_tip_bars_masked_domain_ignores_hidden_tips(self):
        _, axes, _ = self.tree.draw(layout="u", edge_type="p")
        mask = np.ones(self.tree.ntips, dtype=bool)
        mask[0] = False
        mark = self.tree.annotate.add_tip_bars(axes, data="X", width=0.5, mask=mask)
        domain_x = mark.domain("x")
        self.assertAlmostEqual(domain_x[0], 0.75)
        self.assertAlmostEqual(domain_x[1], self.tree.ntips - 0.75)

        hidden = self.tree.annotate.add_tip_bars(axes, data="X", mask=False)
        self.assertEqual(hidden.domain("x"), (None, None))
        coords, extents = hidden.extents("xy")
        self.assertEqual(coords[0].size, 0)
        self.assertEqual(coords[1].size, 0)
        self.assertEqual(extents[0].size, 0)

    def test_add_tip_bars_mask_preserves_slot_positions_and_depths(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        full = self.tree.annotate.add_tip_bars(a, data="X", depth=16)
        toyplot.html.render(c)

        c2, a2, _ = self.tree.draw(layout="d", edge_type="p")
        mask = np.zeros(self.tree.ntips, dtype=bool)
        mask[::2] = True
        masked = self.tree.annotate.add_tip_bars(a2, data="X", depth=16, mask=mask)
        toyplot.html.render(c2)

        self.assertTrue(np.array_equal(masked.tip_indices, np.where(mask)[0]))
        for tidx in masked.tip_indices:
            self.assertAlmostEqual(masked.bar_depths[tidx], full.bar_depths[tidx])

    def test_add_tip_bars_accepts_bool_mask(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        shown = self.tree.annotate.add_tip_bars(a, data="X", mask=True)
        hidden = self.tree.annotate.add_tip_bars(a, data="X", mask=False)
        toyplot.html.render(c)
        self.assertEqual(len(shown.paths), self.tree.ntips)
        self.assertEqual(len(hidden.paths), 0)

    def test_add_tip_bars_rejects_nnodes_mask_array(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        bad = np.ones(self.tree.nnodes, dtype=bool)
        with self.assertRaises(ValueError):
            self.tree.annotate.add_tip_bars(a, data="X", mask=bad)

    def test_add_tip_bars_rejects_negative_values(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        vals = np.arange(self.tree.ntips, dtype=float)
        vals[0] = -1.0
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_bars(a, data=vals)

    def test_add_tip_bars_rejects_nonfinite_values(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        vals = np.arange(self.tree.ntips, dtype=float)
        vals[0] = np.nan
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_bars(a, data=vals)

    def test_add_tip_bars_rejects_invalid_width(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_bars(a, data="X", width=0.0)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_bars(a, data="X", width=1.1)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_bars(a, data="X", width=float("inf"))

    def test_add_tip_bars_rejects_invalid_opacity(self):
        _, axes, _ = self.tree.draw(layout="d", edge_type="p")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_bars(
                axes,
                data="X",
                opacity=np.ones(self.tree.ntips - 1),
            )
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_bars(axes, data="X", opacity=float("nan"))

    def test_add_tip_bars_zero_values_produce_zero_depths(self):
        c, a, _ = self.tree.draw(layout="d", edge_type="p")
        vals = np.zeros(self.tree.ntips, dtype=float)
        mark = self.tree.annotate.add_tip_bars(a, data=vals)
        toyplot.html.render(c)
        self.assertTrue(np.allclose(mark.bar_depths, 0.0))

    def test_add_tip_bars_extents_include_offset_and_depth(self):
        c, a, _ = self.tree.draw(layout="r", tip_labels=False)
        mark = self.tree.annotate.add_tip_bars(a, data="X", offset=10, depth=30)
        coords, ext = mark.extents("xy")
        left, right, top, bottom = ext
        self.assertTrue(np.allclose(left, 0.0))
        self.assertGreaterEqual(float(np.max(right)), 40.0)
        self.assertTrue(np.allclose(top, 0.0))
        self.assertTrue(np.allclose(bottom, 0.0))

    def test_add_tip_bars_style_fill_used_when_color_is_none(self):
        _, axes, _ = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(
            axes,
            data="X",
            style={"fill": "orange"},
        )
        self.assertEqual(str(mark.fill_color), str(ToyColor("orange")))

    def test_add_tip_bars_explicit_color_beats_style_fill(self):
        _, axes, _ = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(
            axes,
            data="X",
            color="steelblue",
            style={"fill": "orange"},
        )
        self.assertEqual(str(mark.fill_color), str(ToyColor("steelblue")))

    def test_add_tip_bars_style_fill_opacity_used_when_opacity_is_none(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_bars(
            axes,
            data="X",
            opacity=None,
            style={"fill_opacity": 0.4},
        )
        root = toyplot.html.render(canvas)
        styles = [
            elem.attrib["style"].replace(" ", "") for elem in self._tip_bar_paths(root)
        ]
        self.assertIn("fill-opacity:0.4", styles[0])
        self.assertIn("fill-opacity:0.4", styles[-1])

    def test_add_tip_bars_scalar_opacity_overrides_style(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_bars(
            axes,
            data="X",
            opacity=0.7,
            style={"fill_opacity": 0.4},
        )
        root = toyplot.html.render(canvas)
        styles = [
            elem.attrib["style"].replace(" ", "") for elem in self._tip_bar_paths(root)
        ]
        self.assertIn("fill-opacity:0.7", styles[0])
        self.assertNotIn("fill-opacity:0.4", styles[0])

    def test_add_tip_bars_sequence_opacity_overrides_shared_style(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_bars(
            axes,
            data="X",
            opacity=np.linspace(0.2, 0.8, self.tree.ntips),
            style={"fill_opacity": 0.4},
        )
        root = toyplot.html.render(canvas)
        styles = [
            elem.attrib["style"].replace(" ", "") for elem in self._tip_bar_paths(root)
        ]
        self.assertIn("fill-opacity:0.2", styles[0])
        self.assertIn("fill-opacity:0.8", styles[-1])
        self.assertNotIn("fill-opacity:0.4", styles[0])

    def test_add_tip_bars_defaults_stroke_to_none(self):
        canvas, axes, _ = self.tree.draw(layout="u", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(
            axes,
            data="X",
            style={"stroke_width": 3},
        )
        root = toyplot.html.render(canvas)
        paths = self._tip_bar_paths(root)
        self.assertEqual(len(paths), self.tree.ntips)
        self.assertEqual(mark.style["stroke"], "none")
        style = paths[0].attrib["style"].replace(" ", "")
        self.assertIn("stroke-opacity:0.0", style)
        self.assertIn("stroke-width:3", style)

    def test_add_tip_bars_style_and_hover_render_on_paths(self):
        canvas, axes, _ = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_tip_bars(
            axes,
            data="X",
            style={
                "stroke": "red",
                "stroke_width": 2,
                "stroke_dasharray": "3,2",
            },
        )
        root = toyplot.html.render(canvas)
        paths = self._tip_bar_paths(root)
        self.assertEqual(len(paths), self.tree.ntips)
        style = paths[0].attrib["style"].replace(" ", "")
        self.assertIn("stroke-width:2", style)
        self.assertIn("stroke-dasharray:3,2", style)
        self.assertNotIn("stroke:none", style)
        self.assertIn(f"{self.tree[0].name}: 0", self._tip_bar_titles(root))

    def test_add_tip_bars_visible_stroke_fits_layout_u(self):
        canvas, axes, _ = self.tree.draw(
            layout="u",
            tip_labels_align=True,
            scale_bar=True,
            padding=90,
            width=600,
        )
        mark = self.tree.annotate.add_tip_bars(
            axes,
            data="X",
            style={"stroke": "black", "stroke_width": 3},
        )
        toyplot.html.render(canvas)
        self._assert_layout_u_tip_bars_fit_axes(mark, axes, stroke_half_width=1.5)

    def test_add_tip_bars_visible_stroke_fits_bdtree_width_u(self):
        tree = toytree.rtree.bdtree(10, seed=123)
        canvas, axes, _ = tree.draw(
            layout="u",
            tip_labels_align=True,
            scale_bar=True,
            padding=90,
            width=600,
        )
        mark = tree.annotate.add_tip_bars(
            axes,
            "dist",
            style={"stroke": "red", "stroke_width": 3},
        )
        toyplot.html.render(canvas)
        self._assert_layout_u_tip_bars_fit_axes(mark, axes, stroke_half_width=1.5)

    def test_add_tip_bars_hover_false_omits_titles(self):
        canvas, axes, _ = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_tip_bars(axes, data="X", hover=False)
        root = toyplot.html.render(canvas)
        self.assertEqual(self._tip_bar_titles(root), [])

    def test_add_tip_bars_default_renders_below_tree(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(a, data="X", depth=10)
        render_targets = a._scenegraph._relationships["render"]._targets[a]
        self.assertLess(render_targets.index(mark), render_targets.index(m))
        toyplot.html.render(c)

    def test_add_tip_bars_above_renders_above_tree(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_tip_bars(a, data="X", depth=10, below=False)
        render_targets = a._scenegraph._relationships["render"]._targets[a]
        self.assertLess(render_targets.index(m), render_targets.index(mark))
        toyplot.html.render(c)
