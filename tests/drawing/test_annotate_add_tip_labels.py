#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for annotate.add_tip_labels."""


import numpy as np
import toyplot.html

import toytree



from conftest import PytestCompat

class TestAnnotateAddTipLabels(PytestCompat):
    def setUp(self):
        self.tree = toytree.rtree.unittree(ntips=10, seed=123)

    def test_add_tip_labels_angle_none_uses_mark_tip_angles(self):
        c, a, m = self.tree.draw(layout="c0-180")
        mark = self.tree.annotate.add_tip_labels(a, labels="idx", angle=None)
        got = mark.angles
        exp = m.tip_labels_angles.copy()
        flip = (exp > 90.0) & (exp < 270.0)
        exp[flip] = exp[flip] - 180.0
        self.assertTrue(np.allclose(np.sort(got), np.sort(exp), atol=1e-8))

    def test_add_tip_labels_angle_scalar_and_sequence(self):
        c1, a1, m1 = self.tree.draw(layout="r")
        mark1 = self.tree.annotate.add_tip_labels(a1, labels="idx", angle=15)
        self.assertTrue(np.allclose(mark1.angles, 15.0))

        c2, a2, m2 = self.tree.draw(layout="r")
        vals = np.arange(self.tree.ntips, dtype=float)
        mark2 = self.tree.annotate.add_tip_labels(a2, labels="idx", angle=vals)
        self.assertTrue(np.allclose(mark2.angles, vals, atol=1e-8))

    def test_add_tip_labels_explicit_style_args_override_style_dict(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_labels(
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

    def test_add_tip_labels_style_only_still_works(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_labels(
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

    def test_add_tip_labels_inherits_mark_tip_label_style_defaults(self):
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
        mark = self.tree.annotate.add_tip_labels(a, labels="idx")
        self.assertEqual(mark.styles[0]["font-size"], "18px")
        self.assertEqual(mark.styles[0]["font-family"], "Courier")
        self.assertEqual(mark.styles[0]["font-weight"], 700)
        self.assertEqual(mark.styles[0]["text-anchor"], "end")
        self.assertEqual(mark.styles[0]["-toyplot-anchor-shift"], 11)
        self.assertEqual(mark.styles[0]["baseline-shift"], 2)

    def test_add_tip_labels_accepts_tip_sized_mask(self):
        c, a, m = self.tree.draw(layout="r")
        mask = np.zeros(self.tree.ntips, dtype=bool)
        mask[::2] = True
        mark = self.tree.annotate.add_tip_labels(a, labels="idx", mask=mask)
        self.assertEqual(mark.labels.size, int(mask.sum()))

    def test_add_tip_labels_accepts_bool_mask(self):
        c, a, m = self.tree.draw(layout="r")
        shown = self.tree.annotate.add_tip_labels(a, labels="idx", mask=True)
        hidden = self.tree.annotate.add_tip_labels(a, labels="idx", mask=False)
        self.assertEqual(shown.labels.size, self.tree.ntips)
        self.assertEqual(hidden.labels.size, 0)

    def test_add_tip_labels_accepts_tuple_mask(self):
        c, a, m = self.tree.draw(layout="r")
        mark = self.tree.annotate.add_tip_labels(a, labels="idx", mask=(1, 1, 1))
        self.assertEqual(mark.labels.size, self.tree.ntips)

    def test_add_tip_labels_rejects_nnodes_mask_array(self):
        c, a, m = self.tree.draw(layout="r")
        bad = np.ones(self.tree.nnodes, dtype=bool)
        with self.assertRaises(ValueError):
            self.tree.annotate.add_tip_labels(a, labels="idx", mask=bad)

    def test_add_tip_labels_shifts_are_applied_on_mark_defaults(self):
        c, a, m = self.tree.draw(
            layout="r",
            tip_labels_style={"-toyplot-anchor-shift": 9, "baseline-shift": 3},
        )
        mark = self.tree.annotate.add_tip_labels(a, labels="idx", xshift=4, yshift=2)
        self.assertEqual(mark.styles[0]["-toyplot-anchor-shift"], 13)
        self.assertEqual(mark.styles[0]["baseline-shift"], 1)

    def test_add_tip_labels_renders_when_mark_fill_opacity_none(self):
        c, a, m = self.tree.draw(layout="l", tip_labels=False)
        self.tree.annotate.add_tip_tiles(
            a, color="idx", opacity=0.5, offset=10, depth=30
        )
        mark = self.tree.annotate.add_tip_labels(a, color="red")
        self.assertEqual(mark.styles[0]["fill-opacity"], 1.0)
        toyplot.html.render(c)

    def test_add_tip_labels_style_fill_opacity_none_is_sanitized(self):
        c, a, m = self.tree.draw(layout="r", tip_labels=False)
        mark = self.tree.annotate.add_tip_labels(
            a, labels="idx", color="red", style={"fill-opacity": None}
        )
        self.assertEqual(mark.styles[0]["fill-opacity"], 1.0)
        toyplot.html.render(c)

    def test_add_tip_labels_circular_single_mark_all_tips(self):
        c, a, m = self.tree.draw(layout="c0-180", tip_labels=False)
        mark = self.tree.annotate.add_tip_labels(a, labels="idx", color="red")
        self.assertEqual(mark.labels.size, self.tree.ntips)

    def test_add_tip_labels_long_labels_fit_participating(self):
        labels = {
            i: f"species_{i}_with_a_very_long_label_name_for_extent_test"
            for i in range(self.tree.ntips)
        }
        tree = self.tree.set_node_data("L", labels, default=np.nan, inplace=False)
        c, a, m = tree.draw(layout="l", tip_labels=False)
        mark = tree.annotate.add_tip_labels(a, labels="L", color="red")
        self.assertFalse(mark.annotation)
        toyplot.html.render(c)

    def test_add_tip_labels_invalidates_axes_finalize_cache(self):
        labels = {
            i: f"species_{i}_with_a_very_long_label_name_for_extent_test"
            for i in range(self.tree.ntips)
        }
        tree = self.tree.set_node_data("L", labels, default=np.nan, inplace=False)
        c, a, m = tree.draw(layout="l", tip_labels=False)

        # Trigger an initial finalize / render pass.
        toyplot.html.render(c)
        self.assertIsNotNone(a._finalized)

        # Adding labels must invalidate cached fit state so new text extents
        # are included in the next clip / autosize calculation.
        tree.annotate.add_tip_labels(a, labels="L", color="red")
        self.assertIsNone(a._finalized)
        self.assertIsNone(a._expand_domain_range_x)
        self.assertIsNone(a._expand_domain_range_y)
        toyplot.html.render(c)


