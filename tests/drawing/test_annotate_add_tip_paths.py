#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for annotate.add_tip_paths."""

import inspect

import numpy as np
import toyplot.html
from conftest import PytestCompat

import toytree
from toytree.color import ToyColor
from toytree.utils import ToytreeError


class TestAnnotateAddTipPaths(PytestCompat):
    def setUp(self):
        self.tree = toytree.rtree.unittree(ntips=8, seed=123)
        vals = {i: float(i) for i in range(self.tree.ntips)}
        self.tree = self.tree.set_node_data("X", vals, default=np.nan, inplace=False)

    @staticmethod
    def _tip_path_paths(root):
        return [
            elem
            for elem in root.iter()
            if elem.attrib.get("id", "").startswith("TipPath-")
        ]

    @staticmethod
    def _tip_path_titles(root):
        titles = []
        for elem in TestAnnotateAddTipPaths._tip_path_paths(root):
            for child in elem:
                if child.tag.endswith("title"):
                    titles.append(child.text)
        return titles

    @staticmethod
    def _path_line_points(path):
        parts = path.replace("M ", "").replace(" L ", " ").split()
        return (
            (float(parts[0]), float(parts[1])),
            (float(parts[-2]), float(parts[-1])),
        )

    @staticmethod
    def _path_cubic_points(path):
        parts = path.replace("M ", "").replace(" C ", " ").split()
        return (
            (float(parts[0]), float(parts[1])),
            (float(parts[2]), float(parts[3])),
            (float(parts[4]), float(parts[5])),
            (float(parts[6]), float(parts[7])),
        )

    @staticmethod
    def _default_spans(ntable, layout):
        axis = 1 if layout in ("r", "l") else 0
        return np.array(ntable[:, axis], dtype=float, copy=True)

    def test_signature_uses_expected_tip_path_parameters(self):
        params = inspect.signature(self.tree.annotate.add_tip_paths).parameters
        self.assertIn("data", params)
        self.assertIn("spans", params)
        self.assertIn("depth_offset", params)
        self.assertIn("span_offset", params)
        self.assertIn("style", params)
        self.assertIn("bezier_fractions", params)
        self.assertIn("color", params)
        self.assertIn("opacity", params)
        self.assertIn("hover", params)
        self.assertNotIn("bezier_param", params)
        self.assertIsNone(params["data"].default)
        self.assertIsNone(params["color"].default)
        self.assertIsNone(params["depth_offset"].default)
        self.assertIsNone(params["opacity"].default)
        self.assertEqual(params["span_offset"].default, 0.0)
        self.assertIsNone(params["bezier_fractions"].default)
        self.assertTrue(params["below"].default)
        self.assertTrue(params["hover"].default)

    def test_add_tip_paths_smoke_rectangular_layouts(self):
        for layout in ("r", "l", "u", "d"):
            canvas, axes, _ = self.tree.draw(layout=layout, edge_type="p")
            mark = self.tree.annotate.add_tip_paths(
                axes,
                data="X",
                depth=24,
                spans=np.linspace(-4.0, 4.0, self.tree.ntips),
            )
            toyplot.html.render(canvas)
            self.assertEqual(len(mark.paths), self.tree.ntips)

    def test_add_tip_paths_rejects_non_rectangular_layouts(self):
        _, axes, _ = self.tree.draw(layout="c", edge_type="p")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, data="X")

    def test_add_tip_paths_data_none_uses_full_depth(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(axes, data=None, depth=30.0)
        root = toyplot.html.render(canvas)
        self.assertTrue(np.allclose(mark.path_depths, 30.0))
        self.assertTrue(np.allclose(mark.data, np.ones(self.tree.ntips)))
        self.assertEqual(mark.value_min, 0.0)
        self.assertEqual(mark.value_max, 1.0)
        self.assertTrue(
            np.allclose(mark.spans, self._default_spans(mark.ntable, mark.layout))
        )
        self.assertIn(f"{self.tree[0].name}: 1", self._tip_path_titles(root))

    def test_add_tip_paths_values_normalize_to_depth(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        vals = np.arange(self.tree.ntips, dtype=float)
        mark = self.tree.annotate.add_tip_paths(axes, data=vals, depth=40.0)
        expected = vals / vals.max() * 40.0
        self.assertTrue(np.allclose(mark.path_depths, expected))

    def test_add_tip_paths_spans_stay_raw_when_depth_is_scaled(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        vals = np.arange(self.tree.ntips, dtype=float)
        spans = np.linspace(-6.0, 6.0, self.tree.ntips)
        mark = self.tree.annotate.add_tip_paths(
            axes,
            data=vals,
            spans=spans,
            depth=20.0,
        )
        self.assertTrue(np.allclose(mark.spans, spans))

    def test_add_tip_paths_spans_set_absolute_end_positions_in_data_units(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        spans = self._default_spans(tmark.ttable, "r")
        spans[[4, 5]] = spans[[5, 4]]
        mark = self.tree.annotate.add_tip_paths(
            axes,
            data=None,
            spans=spans,
            depth=20.0,
            depth_offset=0.0,
            span_offset=0.0,
            bezier_fractions=(0.0, 1.0),
        )
        toyplot.html.render(canvas)
        path_points = [self._path_line_points(path) for path in mark.paths]
        _, end0 = path_points[0]
        self.assertAlmostEqual(
            end0[1],
            float(axes.project("y", spans[0])),
            delta=1e-5,
        )
        for idx in (0, 1, 2, 3, 6, 7):
            start, end = path_points[idx]
            self.assertAlmostEqual(start[1], end[1], delta=1e-5)
        for idx in (4, 5):
            start, end = path_points[idx]
            self.assertNotAlmostEqual(start[1], end[1], delta=1e-5)
        self.assertEqual(
            mark.domain("x"),
            (float(np.min(mark.ntable[:, 0])), float(np.max(mark.ntable[:, 0]))),
        )
        self.assertEqual(
            mark.domain("y"),
            (
                float(np.min(np.concatenate((mark.ntable[:, 1], spans)))),
                float(np.max(np.concatenate((mark.ntable[:, 1], spans)))),
            ),
        )

    def test_add_tip_paths_auto_depth_offset_matches_tip_bars(self):
        show = np.zeros(self.tree.ntips, dtype=bool)
        show[::2] = True

        _, axes0, _ = self.tree.draw(layout="r", edge_type="p")
        pmark = self.tree.annotate.add_tip_paths(axes0, data=None, mask=show)

        _, axes1, _ = self.tree.draw(layout="r", edge_type="p")
        bmark = self.tree.annotate.add_tip_bars(axes1, data="X", mask=show)

        self.assertAlmostEqual(float(pmark.depth_offset), float(bmark.offset))

    def test_add_tip_paths_span_offset_shifts_vertical_extents(self):
        _, axes0, tmark0 = self.tree.draw(layout="r", edge_type="p")
        spans = self._default_spans(tmark0.ttable, "r")
        mark0 = self.tree.annotate.add_tip_paths(
            axes0,
            data=None,
            spans=spans,
            span_offset=0.0,
            bezier_fractions=(0.0, 1.0),
        )
        _, ext0 = mark0.extents("xy")

        _, axes1, _ = self.tree.draw(layout="r", edge_type="p")
        mark1 = self.tree.annotate.add_tip_paths(
            axes1,
            data=None,
            spans=spans,
            span_offset=12.0,
            bezier_fractions=(0.0, 1.0),
        )
        _, ext1 = mark1.extents("xy")

        self.assertTrue(np.allclose(ext1[2] - ext0[2], 12.0))
        self.assertTrue(np.allclose(ext1[3] - ext0[3], 12.0))

    def test_add_tip_paths_bezier_01_renders_lines(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(
            axes,
            data=None,
            spans=self._default_spans(tmark.ttable, "r"),
            bezier_fractions=(0.0, 1.0),
        )
        root = toyplot.html.render(canvas)
        path = self._tip_path_paths(root)[0].attrib["d"]
        self.assertIn(" L ", path)
        self.assertNotIn(" C ", path)

    def test_add_tip_paths_default_bezier_fractions_render_cubic(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(
            axes,
            data=None,
            spans=self._default_spans(tmark.ttable, "r"),
        )
        root = toyplot.html.render(canvas)
        path = self._tip_path_paths(root)[0].attrib["d"]
        self.assertEqual(mark.bezier_fractions, (0.25, 0.75))
        self.assertIn(" C ", path)

    def test_add_tip_paths_custom_bezier_fractions_set_control_points(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        spans = self._default_spans(tmark.ttable, "r")
        spans[[4, 5]] = spans[[5, 4]]
        self.tree.annotate.add_tip_paths(
            axes,
            data=None,
            spans=spans,
            depth=20.0,
            depth_offset=0.0,
            span_offset=0.0,
            bezier_fractions=(0.1, 0.9),
        )
        root = toyplot.html.render(canvas)
        start, ctrl1, ctrl2, end = self._path_cubic_points(
            self._tip_path_paths(root)[4].attrib["d"]
        )
        self.assertAlmostEqual(ctrl1[1], start[1], delta=1e-5)
        self.assertAlmostEqual(ctrl2[1], end[1], delta=1e-5)
        self.assertAlmostEqual(
            ctrl1[0], start[0] + 0.1 * (end[0] - start[0]), delta=1e-5
        )
        self.assertAlmostEqual(
            ctrl2[0], start[0] + 0.9 * (end[0] - start[0]), delta=1e-5
        )

    def test_add_tip_paths_rejects_invalid_spans(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, spans=np.ones(self.tree.nnodes))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(
                axes,
                spans=np.array([0.0, np.nan] + [0.0] * (self.tree.ntips - 2)),
            )

    def test_add_tip_paths_rejects_invalid_numeric_arguments(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, depth=0.0)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, depth_offset=float("nan"))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, color=["red"])
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, opacity=np.ones(self.tree.ntips - 1))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, span_offset=float("inf"))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, bezier_fractions=0.5)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, bezier_fractions=[0.1, 0.9])
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, bezier_fractions=(0.1,))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, bezier_fractions=(0.5, 0.5))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, bezier_fractions=(0.8, 0.2))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, bezier_fractions=(-0.1, 0.9))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, bezier_fractions=(0.1, 1.1))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, bezier_fractions=(0.1, np.nan))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, hover=5)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, hover=["x"])

    def test_add_tip_paths_default_style_is_line_oriented(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(axes, data=None)
        root = toyplot.html.render(canvas)
        path = self._tip_path_paths(root)[0]
        style = path.attrib["style"].replace(" ", "")
        self.assertEqual(mark.style["fill"], "none")
        self.assertEqual(mark.style["stroke"], "black")
        self.assertIn("fill-opacity:0.0", style)
        self.assertIn("stroke-width:2", style)
        self.assertIn("stroke-linecap:round", style)

    def test_add_tip_paths_style_stroke_used_when_color_is_none(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(
            axes,
            data=None,
            style={"stroke": "orange"},
        )
        self.assertEqual(str(mark.stroke_color), str(ToyColor("orange")))

    def test_add_tip_paths_explicit_color_beats_style_stroke(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(
            axes,
            data=None,
            color="steelblue",
            style={"stroke": "orange"},
        )
        self.assertEqual(str(mark.stroke_color), str(ToyColor("steelblue")))

    def test_add_tip_paths_style_stroke_opacity_used_when_opacity_is_none(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(
            axes,
            data=None,
            opacity=None,
            style={"stroke_opacity": 0.4},
        )
        root = toyplot.html.render(canvas)
        styles = [
            elem.attrib["style"].replace(" ", "") for elem in self._tip_path_paths(root)
        ]
        self.assertIn("stroke-opacity:0.4", styles[0])
        self.assertIn("stroke-opacity:0.4", styles[-1])

    def test_add_tip_paths_scalar_opacity_overrides_style(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(
            axes,
            data=None,
            opacity=0.7,
            style={"stroke_opacity": 0.4},
        )
        root = toyplot.html.render(canvas)
        styles = [
            elem.attrib["style"].replace(" ", "") for elem in self._tip_path_paths(root)
        ]
        self.assertIn("stroke-opacity:0.7", styles[0])
        self.assertNotIn("stroke-opacity:0.4", styles[0])

    def test_add_tip_paths_sequence_opacity_overrides_shared_style(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(
            axes,
            data=None,
            opacity=np.linspace(0.2, 0.8, self.tree.ntips),
            style={"stroke_opacity": 0.4},
        )
        root = toyplot.html.render(canvas)
        styles = [
            elem.attrib["style"].replace(" ", "") for elem in self._tip_path_paths(root)
        ]
        self.assertIn("stroke-opacity:0.2", styles[0])
        self.assertIn("stroke-opacity:0.8", styles[-1])
        self.assertNotIn("stroke-opacity:0.4", styles[0])

    def test_add_tip_paths_hover_true_shows_default_titles(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(axes, data="X", hover=True)
        root = toyplot.html.render(canvas)
        self.assertIn(
            f"{self.tree[0].name}: 0",
            self._tip_path_titles(root),
        )

    def test_add_tip_paths_hover_feature_name_uses_feature_values(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(axes, data=None, hover="X")
        root = toyplot.html.render(canvas)
        self.assertEqual(self._tip_path_titles(root)[0], "0.0")

    def test_add_tip_paths_hover_sequence_uses_custom_labels(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        labels = [f"label-{idx}" for idx in range(self.tree.ntips)]
        self.tree.annotate.add_tip_paths(axes, data=None, hover=labels)
        root = toyplot.html.render(canvas)
        self.assertEqual(self._tip_path_titles(root), labels)

    def test_add_tip_paths_hover_false_omits_titles(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(axes, data=None, hover=False)
        root = toyplot.html.render(canvas)
        self.assertEqual(self._tip_path_titles(root), [])

    def test_add_tip_paths_default_renders_below_tree(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(axes, data=None, depth=12.0)
        render_targets = axes._scenegraph._relationships["render"]._targets[axes]
        self.assertLess(render_targets.index(mark), render_targets.index(tmark))
        toyplot.html.render(canvas)
