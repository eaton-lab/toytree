#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for annotate.add_tip_text."""

import inspect

import numpy as np
import toyplot.html
from conftest import PytestCompat

import toytree
from toytree.utils import ToytreeError


class TestAnnotateAddTipText(PytestCompat):
    def setUp(self):
        self.tree = toytree.rtree.unittree(ntips=10, seed=123)

    def test_add_tip_text_signature_and_public_name(self):
        signature = inspect.signature(toytree.annotate.add_tip_text)
        params = list(signature.parameters)
        self.assertIn("fn", params)
        self.assertIn("italic", params)
        self.assertIn("bold", params)
        self.assertIn("offset_depth", params)
        self.assertIn("offset_span", params)
        self.assertNotIn("xshift", params)
        self.assertNotIn("yshift", params)
        self.assertIsNone(signature.parameters["fn"].default)
        self.assertFalse(signature.parameters["italic"].default)
        self.assertFalse(signature.parameters["bold"].default)
        self.assertIsNone(signature.parameters["offset_depth"].default)
        self.assertIsNone(signature.parameters["offset_span"].default)
        self.assertTrue(hasattr(toytree.annotate, "add_tip_text"))
        self.assertFalse(hasattr(toytree.annotate, "add_tip_labels"))
        self.assertTrue(hasattr(self.tree.annotate, "add_tip_text"))
        self.assertFalse(hasattr(self.tree.annotate, "add_tip_labels"))

    def test_add_tip_text_fn_transforms_resolved_labels(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(a, labels="name", fn=str.upper)
        expected = np.array([label.upper() for label in self.tree.get_tip_labels()])
        self.assertTrue(np.array_equal(mark.labels, expected))

    def test_add_tip_text_italic_and_bold_apply_after_fn(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(
            a,
            labels="name",
            fn=str.upper,
            italic=True,
            bold=True,
        )
        self.assertEqual(mark.labels[0], "<b><i>R0</i></b>")
        self.assertEqual(mark.labels[1], "<b><i>R1</i></b>")

    def test_add_tip_text_does_not_duplicate_existing_tags(self):
        c, a, m = self.tree.draw(layout="r")
        labels = [f"label_{i}" for i in range(self.tree.ntips)]
        labels[0] = "<b><i>tagged</i></b>"
        mark = self.tree.annotate.add_tip_text(
            a,
            labels=labels,
            italic=True,
            bold=True,
        )
        self.assertEqual(mark.labels[0], "<b><i>tagged</i></b>")

    def test_add_tip_text_empty_labels_are_left_unchanged(self):
        c, a, m = self.tree.draw(layout="r")
        labels = [f"label_{i}" for i in range(self.tree.ntips)]
        labels[0] = ""
        mark = self.tree.annotate.add_tip_text(
            a,
            labels=labels,
            fn=str.upper,
            italic=True,
            bold=True,
        )
        self.assertEqual(mark.labels[0], "")
        self.assertEqual(mark.labels[1], "<b><i>LABEL_1</i></b>")

    def test_add_tip_text_empty_or_none_fn_results_preserve_original_label(self):
        c, a, m = self.tree.draw(layout="r")
        keep_none = self.tree.annotate.add_tip_text(
            a,
            labels="name",
            fn=lambda _: None,
        )
        keep_empty = self.tree.annotate.add_tip_text(
            a,
            labels="name",
            fn=lambda _: "",
        )
        expected = np.array(self.tree.get_tip_labels())
        self.assertTrue(np.array_equal(keep_none.labels, expected))
        self.assertTrue(np.array_equal(keep_empty.labels, expected))

    def test_add_tip_text_fn_applies_after_tuple_label_formatting(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(
            a,
            labels=("name", lambda value: f"{value}_x"),
            fn=str.upper,
        )
        self.assertEqual(mark.labels[0], "R0_X")

    def test_add_tip_text_angle_none_uses_mark_tip_angles(self):
        c, a, m = self.tree.draw(layout="c0-180")
        mark = self.tree.annotate.add_tip_text(a, labels="idx", angle=None)
        got = mark.angles
        exp = m.tip_labels_angles.copy()
        flip = (exp > 90.0) & (exp < 270.0)
        exp[flip] = exp[flip] - 180.0
        self.assertTrue(np.allclose(np.sort(got), np.sort(exp), atol=1e-8))

    def test_add_tip_text_angle_scalar_and_sequence(self):
        c1, a1, m1 = self.tree.draw(layout="r")
        mark1 = self.tree.annotate.add_tip_text(a1, labels="idx", angle=15)
        self.assertTrue(np.allclose(mark1.angles, 15.0))

        c2, a2, m2 = self.tree.draw(layout="r")
        vals = np.arange(self.tree.ntips, dtype=float)
        mark2 = self.tree.annotate.add_tip_text(a2, labels="idx", angle=vals)
        self.assertTrue(np.allclose(mark2.angles, vals, atol=1e-8))

    def test_add_tip_text_explicit_style_args_override_style_dict(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(
            a,
            labels="idx",
            style={
                "font-family": "Helvetica",
                "font-weight": 100,
                "text-anchor": "start",
            },
            font_family="Courier",
            font_weight=700,
            text_anchor="end",
        )
        self.assertEqual(mark.styles[0]["font-family"], "Courier")
        self.assertEqual(mark.styles[0]["font-weight"], 700)
        self.assertEqual(mark.styles[0]["text-anchor"], "end")

    def test_add_tip_text_style_only_still_works(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(
            a,
            labels="idx",
            style={
                "font-family": "Helvetica",
                "font-weight": 400,
                "text-anchor": "start",
            },
        )
        self.assertEqual(mark.styles[0]["font-family"], "Helvetica")
        self.assertEqual(mark.styles[0]["font-weight"], 400)
        self.assertEqual(mark.styles[0]["text-anchor"], "start")

    def test_add_tip_text_inherits_tip_style_but_resets_shift_defaults(self):
        c, a, m = self.tree.draw(
            layout="r",
            tip_labels_style={
                "font-size": 18,
                "font-family": "Courier",
                "font-weight": 700,
                "text-anchor": "end",
                "-toyplot-anchor-shift": 11,
                "baseline-shift": 2,
            },
        )
        mark = self.tree.annotate.add_tip_text(a, labels="idx")
        self.assertEqual(mark.styles[0]["font-size"], "18px")
        self.assertEqual(mark.styles[0]["font-family"], "Courier")
        self.assertEqual(mark.styles[0]["font-weight"], 700)
        self.assertEqual(mark.styles[0]["text-anchor"], "end")
        self.assertEqual(mark.styles[0]["-toyplot-anchor-shift"], 0.0)
        self.assertEqual(mark.styles[0]["baseline-shift"], 0.0)

    def test_add_tip_text_accepts_tip_sized_mask(self):
        c, a, m = self.tree.draw(layout="r")
        mask = np.zeros(self.tree.ntips, dtype=bool)
        mask[::2] = True
        mark = self.tree.annotate.add_tip_text(a, labels="idx", mask=mask)
        self.assertEqual(mark.labels.size, int(mask.sum()))

    def test_add_tip_text_accepts_bool_mask(self):
        c, a, m = self.tree.draw(layout="r")
        shown = self.tree.annotate.add_tip_text(a, labels="idx", mask=True)
        hidden = self.tree.annotate.add_tip_text(a, labels="idx", mask=False)
        self.assertEqual(shown.labels.size, self.tree.ntips)
        self.assertEqual(hidden.labels.size, 0)

    def test_add_tip_text_accepts_tuple_mask(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(a, labels="idx", mask=(1, 1, 1))
        self.assertEqual(mark.labels.size, self.tree.ntips)

    def test_add_tip_text_rejects_nnodes_mask_array(self):
        c, a, m = self.tree.draw(layout="r")
        bad = np.ones(self.tree.nnodes, dtype=bool)
        with self.assertRaises(ValueError):
            self.tree.annotate.add_tip_text(a, labels="idx", mask=bad)

    def test_add_tip_text_style_shift_defaults_are_zero(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(a, labels="idx")
        self.assertEqual(mark.styles[0]["-toyplot-anchor-shift"], 0.0)
        self.assertEqual(mark.styles[0]["baseline-shift"], 0.0)

    def test_add_tip_text_offset_depth_overrides_style_anchor_shift(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(
            a,
            labels="idx",
            style={"-toyplot-anchor-shift": 9, "baseline-shift": 3},
            offset_depth=4.0,
        )
        self.assertEqual(mark.styles[0]["-toyplot-anchor-shift"], 4.0)
        self.assertEqual(mark.styles[0]["baseline-shift"], 3.0)

    def test_add_tip_text_offset_span_overrides_style_baseline_shift(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(
            a,
            labels="idx",
            style={"-toyplot-anchor-shift": 9, "baseline-shift": 3},
            offset_span=2.0,
        )
        self.assertEqual(mark.styles[0]["-toyplot-anchor-shift"], 9.0)
        self.assertEqual(mark.styles[0]["baseline-shift"], -2.0)

    def test_add_tip_text_offset_span_is_layout_aware_on_vertical_layouts(self):
        c, a, m = self.tree.draw(layout="u")
        mark = self.tree.annotate.add_tip_text(a, labels="idx", offset_span=2.0)
        self.assertEqual(mark.styles[0]["baseline-shift"], 2.0)

    def test_add_tip_text_offset_span_is_layout_aware_on_circular_flips(self):
        c, a, m = self.tree.draw(layout="c0-180")
        mark = self.tree.annotate.add_tip_text(a, labels="idx", offset_span=6.0)
        flip = (m.tip_labels_angles > 90.0) & (m.tip_labels_angles < 270.0)
        got = np.array([style["baseline-shift"] for style in mark.styles], dtype=float)
        self.assertTrue(np.all(got[~flip] == -6.0))
        self.assertTrue(np.all(got[flip] == 6.0))

    def test_add_tip_text_none_offsets_preserve_style_shifts(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(
            a,
            labels="idx",
            style={"-toyplot-anchor-shift": "9px", "baseline-shift": "3px"},
            offset_depth=None,
            offset_span=None,
        )
        self.assertEqual(mark.styles[0]["-toyplot-anchor-shift"], 9.0)
        self.assertEqual(mark.styles[0]["baseline-shift"], 3.0)

    def test_add_tip_text_supports_anchor_shift_alias(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_text(
            a,
            labels="idx",
            style={"anchor-shift": 7, "baseline-shift": 2},
        )
        self.assertEqual(mark.styles[0]["-toyplot-anchor-shift"], 7.0)
        self.assertEqual(mark.styles[0]["baseline-shift"], 2.0)

    def test_add_tip_text_rejects_invalid_style_type(self):
        c, a, m = self.tree.draw(layout="r")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_text(a, labels="idx", style=["bad"])

    def test_add_tip_text_rejects_non_callable_fn(self):
        c, a, m = self.tree.draw(layout="r")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_text(a, labels="idx", fn="bad")

    def test_add_tip_text_rejects_invalid_offset_depth(self):
        c, a, m = self.tree.draw(layout="r")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_text(a, labels="idx", offset_depth=float("inf"))

    def test_add_tip_text_rejects_invalid_offset_span(self):
        c, a, m = self.tree.draw(layout="r")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_text(a, labels="idx", offset_span="bad")

    def test_add_tip_text_rejects_invalid_anchor_shift_style(self):
        c, a, m = self.tree.draw(layout="r")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_text(
                a,
                labels="idx",
                style={"-toyplot-anchor-shift": "bad"},
            )

    def test_add_tip_text_rejects_invalid_baseline_shift_style(self):
        c, a, m = self.tree.draw(layout="r")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_tip_text(
                a,
                labels="idx",
                style={"baseline-shift": "bad"},
            )

    def test_add_tip_text_renders_when_mark_fill_opacity_none(self):
        c, a, m = self.tree.draw(layout="l", tip_labels=False)
        self.tree.annotate.add_tip_tiles(
            a, color="idx", opacity=0.5, offset=10, depth=30
        )
        mark = self.tree.annotate.add_tip_text(a, color="red")
        self.assertEqual(mark.styles[0]["fill-opacity"], 1.0)
        toyplot.html.render(c)

    def test_add_tip_text_style_fill_opacity_none_is_sanitized(self):
        c, a, m = self.tree.draw(layout="r", tip_labels=False)
        mark = self.tree.annotate.add_tip_text(
            a, labels="idx", color="red", style={"fill-opacity": None}
        )
        self.assertEqual(mark.styles[0]["fill-opacity"], 1.0)
        toyplot.html.render(c)

    def test_add_tip_text_circular_single_mark_all_tips(self):
        c, a, m = self.tree.draw(layout="c0-180", tip_labels=False)
        mark = self.tree.annotate.add_tip_text(a, labels="idx", color="red")
        self.assertEqual(mark.labels.size, self.tree.ntips)

    def test_add_tip_text_unrooted_angle_none_uses_layout_angles(self):
        tree = self.tree.unroot()
        c, a, m = tree.draw(layout="unrooted", tip_labels=False)
        mark = tree.annotate.add_tip_text(a, labels="idx", angle=None)
        self.assertTrue(np.all(np.isfinite(mark.angles)))
        self.assertEqual(mark.labels.size, tree.ntips)
        toyplot.html.render(c)

    def test_add_tip_text_long_labels_fit_participating(self):
        labels = {
            i: f"species_{i}_with_a_very_long_label_name_for_extent_test"
            for i in range(self.tree.ntips)
        }
        tree = self.tree.set_node_data("L", labels, default=np.nan, inplace=False)
        c, a, m = tree.draw(layout="l", tip_labels=False)
        mark = tree.annotate.add_tip_text(a, labels="L", color="red")
        self.assertFalse(mark.annotation)
        toyplot.html.render(c)

    def test_add_tip_text_invalidates_axes_finalize_cache(self):
        labels = {
            i: f"species_{i}_with_a_very_long_label_name_for_extent_test"
            for i in range(self.tree.ntips)
        }
        tree = self.tree.set_node_data("L", labels, default=np.nan, inplace=False)
        c, a, m = tree.draw(layout="l", tip_labels=False)

        toyplot.html.render(c)
        self.assertIsNotNone(a._finalized)

        tree.annotate.add_tip_text(a, labels="L", color="red")
        self.assertIsNone(a._finalized)
        self.assertIsNone(a._expand_domain_range_x)
        self.assertIsNone(a._expand_domain_range_y)
        toyplot.html.render(c)
