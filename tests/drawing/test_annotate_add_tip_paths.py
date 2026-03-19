#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for annotate.add_tip_paths."""

import inspect
import os
import re
import tempfile
import zlib
from base64 import a85decode
from unittest.mock import patch

import numpy as np
import toyplot.html
import toyplot.pdf
from conftest import PytestCompat

import toytree
from toytree.color import ToyColor
from toytree.drawing.src._pdf_patch import install_pdf_render_patch
from toytree.utils import ToytreeError


class TestAnnotateAddTipPaths(PytestCompat):
    def setUp(self):
        self.tree = toytree.rtree.unittree(ntips=8, seed=123)
        ends = {i: float(i) for i in range(self.tree.ntips)}
        spans = {
            i: float(self.tree.ntips - idx)
            for idx, i in enumerate(range(self.tree.ntips))
        }
        self.tree = self.tree.set_node_data(
            "X",
            ends,
            default=np.nan,
            inplace=False,
        )
        self.tree = self.tree.set_node_data(
            "Y",
            spans,
            default=np.nan,
            inplace=False,
        )

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
    def _tip_span_coords(tmark, layout):
        axis = 1 if layout in ("r", "l") else 0
        return np.array(tmark.ttable[:, axis], dtype=float, copy=True)

    @staticmethod
    def _render_pdf_text(canvas):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            pdf_path = tmp.name
        try:
            toyplot.pdf.render(canvas, pdf_path)
            with open(pdf_path, "rb") as infile:
                pdf_bytes = infile.read()
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

        pdf_text = pdf_bytes.decode("latin1", errors="ignore")
        match = re.search(rb"stream\r?\n(.*?)endstream", pdf_bytes, re.S)
        if match is None:
            raise AssertionError("Expected one PDF content stream.")
        raw_stream = match.group(1).strip()
        stream_text = zlib.decompress(a85decode(raw_stream, adobe=True)).decode(
            "latin1",
            errors="ignore",
        )
        return pdf_text, stream_text

    @staticmethod
    def _count_pdf_curve_ops(stream_text):
        return len(
            re.findall(
                r"(?:^|\s)(?:-?\d+(?:\.\d+)?\s+){6}c(?:\s|$)",
                stream_text,
            )
        )

    def test_signature_uses_expected_tip_path_parameters(self):
        params = inspect.signature(self.tree.annotate.add_tip_paths).parameters
        self.assertIn("spans", params)
        self.assertIn("ends", params)
        self.assertIn("depth", params)
        self.assertIn("offset_start", params)
        self.assertIn("offset_end", params)
        self.assertIn("offset_span", params)
        self.assertIn("style", params)
        self.assertIn("bezier_fractions", params)
        self.assertIn("color", params)
        self.assertIn("opacity", params)
        self.assertIn("hover", params)
        self.assertNotIn("data", params)
        self.assertNotIn("lengths", params)
        self.assertNotIn("depth_offset", params)
        self.assertNotIn("span_offset", params)
        self.assertIsNone(params["spans"].default)
        self.assertIsNone(params["ends"].default)
        self.assertEqual(params["depth"].default, 100.0)
        self.assertEqual(params["offset_start"].default, 0.0)
        self.assertEqual(params["offset_end"].default, 0.0)
        self.assertEqual(params["offset_span"].default, 0.0)
        self.assertIsNone(params["color"].default)
        self.assertIsNone(params["opacity"].default)
        self.assertIsNone(params["bezier_fractions"].default)
        self.assertTrue(params["below"].default)
        self.assertTrue(params["hover"].default)
        self.assertEqual(list(params)[:4], ["axes", "spans", "ends", "depth"])

    def test_add_tip_paths_smoke_rectangular_layouts(self):
        ends = np.linspace(0.0, 4.0, self.tree.ntips)
        spans = np.arange(self.tree.ntips, dtype=float)
        for layout in ("r", "l", "u", "d"):
            canvas, axes, _ = self.tree.draw(layout=layout, edge_type="p")
            mark = self.tree.annotate.add_tip_paths(
                axes,
                spans=spans,
                ends=ends,
            )
            toyplot.html.render(canvas)
            self.assertEqual(len(mark.paths), self.tree.ntips)

    def test_add_tip_paths_rejects_non_rectangular_layouts(self):
        _, axes, _ = self.tree.draw(layout="c", edge_type="p")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, ends=np.ones(self.tree.ntips))

    def test_add_tip_paths_no_longer_accepts_lengths_keyword(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        with self.assertRaises(TypeError):
            self.tree.annotate.add_tip_paths(axes, lengths=np.ones(self.tree.ntips))

    def test_add_tip_paths_ends_none_uses_depth_and_unit_metadata(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(axes, ends=None, depth=30.0)
        root = toyplot.html.render(canvas)
        start, end = self._path_line_points(mark.paths[0])
        self.assertIsNone(mark.ends)
        self.assertTrue(np.allclose(mark.data, np.ones(self.tree.ntips)))
        self.assertEqual(mark.value_min, 0.0)
        self.assertEqual(mark.value_max, 1.0)
        self.assertTrue(np.allclose(mark.spans, np.arange(self.tree.ntips)))
        self.assertAlmostEqual(end[0] - start[0], 30.0, delta=1e-5)
        self.assertAlmostEqual(start[1], end[1], delta=1e-5)
        self.assertIn(f"{self.tree[0].name}: 1", self._tip_path_titles(root))

    def test_add_tip_paths_selects_tree_specific_mark_on_shared_axes(self):
        other = toytree.rtree.unittree(
            ntips=self.tree.ntips,
            seed=333,
            random_names=True,
        )
        _, axes, tmark1 = self.tree.draw(layout="r", width=500)
        _, axes, tmark2 = other.draw(axes=axes, layout="l", xbaseline=2)
        mark = self.tree.annotate.add_tip_paths(axes, ends=None, depth=30.0)
        self.assertIs(mark.host_tree_mark, tmark1)
        self.assertIsNot(mark.host_tree_mark, tmark2)
        self.assertTrue(
            np.allclose(mark.ntable, np.asarray(tmark1.ttable[: self.tree.ntips]))
        )
        self.assertFalse(
            np.allclose(mark.ntable, np.asarray(tmark2.ttable[: self.tree.ntips]))
        )

    def test_add_tip_paths_ends_set_absolute_end_positions_in_data_units(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        ends = np.arange(self.tree.ntips, dtype=float)
        spans = self._tip_span_coords(tmark, "r")
        spans[[4, 5]] = spans[[5, 4]]
        mark = self.tree.annotate.add_tip_paths(
            axes,
            spans=spans,
            ends=ends,
            offset_start=0.0,
            offset_end=0.0,
            offset_span=0.0,
            bezier_fractions=(0.0, 1.0),
        )
        toyplot.html.render(canvas)
        path_points = [self._path_line_points(path) for path in mark.paths]
        start0, end0 = path_points[0]
        self.assertAlmostEqual(
            end0[0],
            float(axes.project("x", ends[0])),
            delta=1e-5,
        )
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
        x_domain = np.concatenate((mark.ntable[:, 0], ends))
        self.assertEqual(
            mark.domain("x"),
            (
                float(np.min(x_domain)),
                float(np.max(x_domain)),
            ),
        )
        self.assertEqual(
            mark.domain("y"),
            (
                float(np.min(np.concatenate((mark.ntable[:, 1], spans)))),
                float(np.max(np.concatenate((mark.ntable[:, 1], spans)))),
            ),
        )

    def test_add_tip_paths_ends_feature_name_resolves_tip_data(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        spans = self._tip_span_coords(tmark, "r")
        mark = self.tree.annotate.add_tip_paths(
            axes,
            spans=spans,
            ends="X",
            bezier_fractions=(0.0, 1.0),
        )
        root = toyplot.html.render(canvas)
        self.assertTrue(np.allclose(mark.ends, np.arange(self.tree.ntips)))
        self.assertEqual(mark.value_max, float(self.tree.ntips - 1))
        start, end = self._path_line_points(mark.paths[3])
        self.assertAlmostEqual(
            end[0],
            float(axes.project("x", 3.0)),
            delta=1e-5,
        )
        self.assertAlmostEqual(start[1], end[1], delta=1e-5)
        self.assertIn(f"{self.tree[3].name}: 3", self._tip_path_titles(root))

    def test_add_tip_paths_ends_use_absolute_coordinates_in_up_layout(self):
        canvas, axes, tmark = self.tree.draw(layout="u", edge_type="p")
        ends = np.arange(self.tree.ntips, dtype=float)
        spans = self._tip_span_coords(tmark, "u")
        mark = self.tree.annotate.add_tip_paths(
            axes,
            spans=spans,
            ends=ends,
            bezier_fractions=(0.0, 1.0),
        )
        toyplot.html.render(canvas)
        start, end = self._path_line_points(mark.paths[2])
        self.assertAlmostEqual(
            end[0],
            float(axes.project("x", spans[2])),
            delta=1e-5,
        )
        self.assertAlmostEqual(
            end[1],
            float(axes.project("y", ends[2])),
            delta=1e-5,
        )

    def test_add_tip_paths_spans_feature_name_resolves_tip_data(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(
            axes,
            spans="Y",
            ends=np.arange(self.tree.ntips, dtype=float),
            bezier_fractions=(0.0, 1.0),
        )
        toyplot.html.render(canvas)
        expected = np.arange(self.tree.ntips, 0.0, -1.0)
        self.assertTrue(np.allclose(mark.spans, expected))
        start, end = self._path_line_points(mark.paths[0])
        self.assertAlmostEqual(
            end[1], float(axes.project("y", expected[0])), delta=1e-5
        )
        self.assertEqual(
            mark.domain("y"),
            (
                float(np.min(np.concatenate((mark.ntable[:, 1], expected)))),
                float(np.max(np.concatenate((mark.ntable[:, 1], expected)))),
            ),
        )

    def test_add_tip_paths_ends_and_spans_feature_names_can_be_combined(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(
            axes,
            spans="Y",
            ends="X",
            bezier_fractions=(0.0, 1.0),
        )
        toyplot.html.render(canvas)
        self.assertTrue(np.allclose(mark.ends, np.arange(self.tree.ntips)))
        self.assertTrue(np.allclose(mark.spans, np.arange(self.tree.ntips, 0.0, -1.0)))

    def test_add_tip_paths_spans_default_to_tip_order_range(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(
            axes,
            ends=np.arange(self.tree.ntips),
        )
        self.assertTrue(np.allclose(mark.spans, np.arange(self.tree.ntips)))

    def test_add_tip_paths_offset_span_shifts_vertical_extents(self):
        _, axes0, tmark0 = self.tree.draw(layout="r", edge_type="p")
        spans = self._tip_span_coords(tmark0, "r")
        mark0 = self.tree.annotate.add_tip_paths(
            axes0,
            spans=spans,
            ends=np.arange(self.tree.ntips, dtype=float),
            offset_span=0.0,
            bezier_fractions=(0.0, 1.0),
        )
        _, ext0 = mark0.extents("xy")

        _, axes1, _ = self.tree.draw(layout="r", edge_type="p")
        mark1 = self.tree.annotate.add_tip_paths(
            axes1,
            spans=spans,
            ends=np.arange(self.tree.ntips, dtype=float),
            offset_span=12.0,
            bezier_fractions=(0.0, 1.0),
        )
        _, ext1 = mark1.extents("xy")

        self.assertTrue(np.allclose(ext1[2] - ext0[2], 12.0))
        self.assertTrue(np.allclose(ext1[3] - ext0[3], 12.0))

    def test_add_tip_paths_offset_start_and_end_shift_depth_endpoints(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        spans = self._tip_span_coords(tmark, "r")
        mark = self.tree.annotate.add_tip_paths(
            axes,
            spans=spans,
            ends=None,
            depth=20.0,
            offset_start=5.0,
            offset_end=7.0,
            bezier_fractions=(0.0, 1.0),
        )
        toyplot.html.render(canvas)

        _, start_x, start_y, end_x, end_y = mark._get_rendered_endpoints_px(axes)
        start, end = self._path_line_points(mark.paths[0])
        self.assertAlmostEqual(start[0], start_x[0], delta=1e-5)
        self.assertAlmostEqual(start[1], start_y[0], delta=1e-5)
        self.assertAlmostEqual(end[0], end_x[0], delta=1e-5)
        self.assertAlmostEqual(end[1], end_y[0], delta=1e-5)

    def test_add_tip_paths_bezier_01_renders_lines(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(
            axes,
            spans=self._tip_span_coords(tmark, "r"),
            ends=None,
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
            spans=self._tip_span_coords(tmark, "r"),
            ends=None,
        )
        root = toyplot.html.render(canvas)
        path = self._tip_path_paths(root)[0].attrib["d"]
        self.assertEqual(mark.bezier_fractions, (0.45, 0.55))
        self.assertIn(" C ", path)

    def test_add_tip_paths_custom_bezier_fractions_set_control_points(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        ends = np.arange(self.tree.ntips, dtype=float)
        spans = self._tip_span_coords(tmark, "r")
        spans[[4, 5]] = spans[[5, 4]]
        self.tree.annotate.add_tip_paths(
            axes,
            spans=spans,
            ends=ends,
            offset_start=0.0,
            offset_end=0.0,
            offset_span=0.0,
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

    def test_add_tip_paths_rejects_invalid_ends_and_spans(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, ends=np.ones(self.tree.nnodes))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(
                axes,
                ends=np.array([0.0, np.nan] + [0.0] * (self.tree.ntips - 2)),
            )
        mark = self.tree.annotate.add_tip_paths(
            axes,
            ends=np.array([-1.0] + [0.0] * (self.tree.ntips - 1)),
        )
        self.assertAlmostEqual(float(mark.ends[0]), -1.0)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, spans=np.ones(self.tree.nnodes))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(
                axes,
                spans=np.array([0.0, np.nan] + [0.0] * (self.tree.ntips - 2)),
            )
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, ends="missing")
        with patch.object(
            self.tree,
            "get_tip_data",
            return_value=np.array(["x"] * self.tree.ntips, dtype=object),
        ):
            with self.assertRaises(ToytreeError):
                self.tree.annotate.add_tip_paths(axes, ends="bad")
        with patch.object(
            self.tree,
            "get_tip_data",
            return_value=np.array(
                [0.0, np.nan] + [0.0] * (self.tree.ntips - 2), dtype=float
            ),
        ):
            with self.assertRaises(ToytreeError):
                self.tree.annotate.add_tip_paths(axes, spans="bad")
        with patch.object(
            self.tree,
            "get_tip_data",
            return_value=np.ones(self.tree.ntips - 1, dtype=float),
        ):
            with self.assertRaises(ToytreeError):
                self.tree.annotate.add_tip_paths(axes, spans="bad")

    def test_add_tip_paths_rejects_invalid_numeric_arguments(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, ends=None, depth=0.0)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, ends=None, depth=None)
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, offset_start=float("nan"))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, offset_end=float("inf"))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, color=["red"])
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, opacity=np.ones(self.tree.ntips - 1))
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_paths(axes, offset_span=float("inf"))
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
        mark = self.tree.annotate.add_tip_paths(axes, ends=None)
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
            ends=None,
            style={"stroke": "orange"},
        )
        self.assertEqual(str(mark.stroke_color), str(ToyColor("orange")))

    def test_add_tip_paths_explicit_color_beats_style_stroke(self):
        _, axes, _ = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(
            axes,
            color="steelblue",
            ends=None,
            style={"stroke": "orange"},
        )
        self.assertEqual(str(mark.stroke_color), str(ToyColor("steelblue")))

    def test_add_tip_paths_style_stroke_opacity_used_when_opacity_is_none(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(
            axes,
            ends=None,
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
            ends=None,
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
            ends=None,
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
        ends = np.arange(self.tree.ntips, dtype=float)
        self.tree.annotate.add_tip_paths(axes, ends=ends, hover=True)
        root = toyplot.html.render(canvas)
        self.assertIn(
            f"{self.tree[0].name}: 0",
            self._tip_path_titles(root),
        )

    def test_add_tip_paths_hover_feature_name_uses_feature_values(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(axes, ends=None, hover="X")
        root = toyplot.html.render(canvas)
        self.assertEqual(self._tip_path_titles(root)[0], "0.0")

    def test_add_tip_paths_hover_sequence_uses_custom_labels(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        labels = [f"label-{idx}" for idx in range(self.tree.ntips)]
        self.tree.annotate.add_tip_paths(axes, ends=None, hover=labels)
        root = toyplot.html.render(canvas)
        self.assertEqual(self._tip_path_titles(root), labels)

    def test_add_tip_paths_hover_false_omits_titles(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(axes, ends=None, hover=False)
        root = toyplot.html.render(canvas)
        self.assertEqual(self._tip_path_titles(root), [])

    def test_add_tip_paths_default_renders_below_tree(self):
        canvas, axes, tmark = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_tip_paths(axes, ends=None, depth=12.0)
        render_targets = axes._scenegraph._relationships["render"]._targets[axes]
        self.assertLess(render_targets.index(mark), render_targets.index(tmark))
        toyplot.html.render(canvas)

    def test_add_tip_paths_color_alpha_renders_rgb_and_stroke_opacity(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(
            axes,
            ends=None,
            color=(1.0, 0.0, 0.0, 0.5),
        )
        root = toyplot.html.render(canvas)
        style = self._tip_path_paths(root)[0].attrib["style"].replace(" ", "")
        self.assertIn("stroke:rgb(", style)
        self.assertIn("stroke-opacity:0.5", style)
        self.assertNotIn("rgba(", style)

    def test_add_tip_paths_pdf_uses_rgb_stroke_and_color_alpha(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(
            axes,
            ends=None,
            color=(1.0, 0.0, 0.0, 0.5),
        )
        pdf_text, stream_text = self._render_pdf_text(canvas)
        self.assertIn("1 0 0 RG", stream_text)
        self.assertTrue(re.search(r"/CA\s+(?:0\.5|\.5)\b", pdf_text))

    def test_add_tip_paths_pdf_explicit_opacity_overrides_color_alpha(self):
        canvas, axes, _ = self.tree.draw(layout="r", edge_type="p")
        self.tree.annotate.add_tip_paths(
            axes,
            ends=None,
            color=(1.0, 0.0, 0.0, 0.21),
            opacity=0.73,
        )
        pdf_text, stream_text = self._render_pdf_text(canvas)
        self.assertIn("1 0 0 RG", stream_text)
        self.assertTrue(re.search(r"/CA\s+(?:0\.73|\.73)\b", pdf_text))
        self.assertTrue(re.search(r"/CA\s+(?:0\.21|\.21)\b", pdf_text) is None)

    def test_add_tip_paths_pdf_preserves_cubic_path_segments(self):
        base_canvas, _, _ = self.tree.draw(width=400)
        _, base_stream_text = self._render_pdf_text(base_canvas)
        self.assertEqual(self._count_pdf_curve_ops(base_stream_text), 0)

        canvas, axes, _ = self.tree.draw(width=400)
        self.tree.annotate.add_tip_paths(
            axes,
            spans=[0, 1, 2, 6, 4, 3, 5, 7],
            style={
                "stroke": "salmon",
                "stroke-width": 4,
                "stroke-opacity": 0.5,
            },
            offset_start=40,
            depth=140,
            bezier_fractions=(0.45, 0.55),
        )
        root = toyplot.html.render(canvas)
        self.assertIn(" C ", self._tip_path_paths(root)[0].attrib["d"])

        _, stream_text = self._render_pdf_text(canvas)
        self.assertEqual(self._count_pdf_curve_ops(stream_text), self.tree.ntips)

    def test_add_tip_paths_pdf_patch_install_is_idempotent(self):
        install_pdf_render_patch()
        install_pdf_render_patch()

        canvas, axes, _ = self.tree.draw(width=400)
        self.tree.annotate.add_tip_paths(
            axes,
            spans=[0, 1, 2, 6, 4, 3, 5, 7],
            offset_start=40,
            depth=140,
            bezier_fractions=(0.45, 0.55),
        )
        _, stream_text = self._render_pdf_text(canvas)
        self.assertEqual(self._count_pdf_curve_ops(stream_text), self.tree.ntips)
