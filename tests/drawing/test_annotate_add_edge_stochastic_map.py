#!/usr/bin/env python

"""Tests for annotate.add_edge_stochastic_map."""

import xml.etree.ElementTree as xml

import numpy as np
import pandas as pd
import toyplot.html

import toytree
from toytree.style.src.map_colors import get_color_mapped_values
from toytree.utils import ToytreeError



from conftest import PytestCompat

class TestAnnotateAddEdgeStochasticMap(PytestCompat):
    """Validate stochastic-map edge annotation behavior."""

    def setUp(self):
        """Create a tree and simulated stochastic maps for reuse across tests."""
        self.tree = toytree.rtree.unittree(ntips=10, seed=123)
        self.tree = self.tree.set_node_data("X", default=np.nan, inplace=False)
        self.tree.pcm.simulate_discrete_trait(
            nstates=3,
            model="ER",
            trait_name="X",
            tips_only=True,
            inplace=True,
            seed=1,
        )
        fit = self.tree.pcm.fit_discrete_ctmc(data="X", nstates=3, model="ER")
        self.maps = self.tree.pcm.simulate_stochastic_map(
            data="X", model_fit=fit, nreplicates=2, seed=2
        )

    def test_add_edge_stochastic_map_smoke(self):
        """Add a stochastic-map overlay and verify a mark is returned."""
        c, a, m = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_edge_stochastic_map(
            a,
            self.maps,
            map_id=0,
            color="Dark2",
            width=3,
        )
        self.assertIsNotNone(mark)
        self.assertGreater(len(mark.xpaths), 0)

    def test_add_edge_stochastic_map_selects_by_map_id_value(self):
        """Select map rows by map_id value rather than positional index."""
        maps = self.maps.copy()
        maps["map_id"] = maps["map_id"] + 10
        c, a, m = self.tree.draw(layout="r", edge_type="p")
        mark = self.tree.annotate.add_edge_stochastic_map(a, maps, map_id=11)
        nrows = int((maps["map_id"] == 11).sum())
        nedges = int(maps.loc[maps["map_id"] == 11, "edge_id"].nunique())
        self.assertEqual(len(mark.xpaths), nrows + nedges)
        self.assertEqual(mark.map_id, 11)

    def test_add_edge_stochastic_map_missing_map_id_raises(self):
        """Raise when requested map_id does not exist in the mapping table."""
        c, a, m = self.tree.draw(layout="r", edge_type="p")
        with self.assertRaises(ToytreeError) as ctx:
            self.tree.annotate.add_edge_stochastic_map(a, self.maps, map_id=999)
        self.assertIn("Valid range is 0..", str(ctx.exception))

    def test_add_edge_stochastic_map_rejects_bezier_edges(self):
        """Reject bezier edge geometry, which is unsupported for this method."""
        c, a, m = self.tree.draw(layout="r", edge_type="b")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_edge_stochastic_map(a, self.maps)

    def test_add_edge_stochastic_map_state_idx_fallback(self):
        """Color-map by state_idx when a state label column is unavailable."""
        c, a, m = self.tree.draw(layout="r", edge_type="p")
        maps = self.maps.drop(columns=["state"])
        mark = self.tree.annotate.add_edge_stochastic_map(a, maps, map_id=0)
        self.assertIsNotNone(mark)
        self.assertEqual(len(mark.colors), len(mark.xpaths))

    def test_add_edge_stochastic_map_requires_columns(self):
        """Require core stochastic-map columns before rendering."""
        c, a, m = self.tree.draw(layout="r", edge_type="p")
        with self.assertRaises(ToytreeError):
            self.tree.annotate.add_edge_stochastic_map(
                a,
                self.maps.drop(columns=["t_start"]),
            )

    def test_add_edge_stochastic_map_adds_span_segment_for_rectangular_p(self):
        """Add one orthogonal span segment per represented edge."""
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        mark = self.tree.annotate.add_edge_stochastic_map(a, self.maps, map_id=0)
        nrows = int((self.maps["map_id"] == 0).sum())
        nedges = int(self.maps.loc[self.maps["map_id"] == 0, "edge_id"].nunique())
        self.assertEqual(len(mark.xpaths), nrows + nedges)

    def test_add_edge_stochastic_map_span_color_matches_depth_end_state(self):
        """Use depth-end state color for the rectangular span segment."""
        tree = toytree.rtree.unittree(ntips=2, seed=123)
        c, a, m = tree.draw(layout="d", edge_type="p")
        edges = tree.get_edges("idx")
        edge_id = 0
        child = int(edges[edge_id, 0])
        blen = float(tree.get_node_data("dist").iloc[child])

        data = pd.DataFrame(
            {
                "map_id": [0, 0],
                "edge_id": [edge_id, edge_id],
                "state_idx": [0, 1],
                "state": ["A", "B"],
                "t_start": [0.0, 0.4 * blen],
                "t_end": [0.4 * blen, blen],
            }
        )
        mark = tree.annotate.add_edge_stochastic_map(
            a, data, map_id=0, color="Set2", width=4
        )

        self.assertEqual(len(mark.xpaths), 3)
        self.assertAlmostEqual(
            float(mark.ypaths[2][0]), float(mark.ypaths[2][1]), places=8
        )
        self.assertNotAlmostEqual(
            float(mark.xpaths[2][0]), float(mark.xpaths[2][1]), places=8
        )

        expected = np.asarray(get_color_mapped_values(["A", "B"], cmap="Set2"))
        self.assertEqual(mark.colors[2].tobytes(), expected[1].tobytes())
        self.assertEqual(mark.colors[2].tobytes(), mark.colors[1].tobytes())

    def test_add_edge_stochastic_map_accepts_stroke_linejoin(self):
        """Accept stroke-linejoin and include it in rendered style."""
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_edge_stochastic_map(
            a, self.maps, map_id=0, stroke_linejoin="miter"
        )
        text = xml.tostring(toyplot.html.render(c), encoding="unicode")
        self.assertIn("stroke-linejoin:miter", text)

    def test_add_edge_stochastic_map_rejects_invalid_stroke_linejoin(self):
        """Reject invalid stroke-linejoin values."""
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        with self.assertRaises(ValueError):
            self.tree.annotate.add_edge_stochastic_map(
                a, self.maps, map_id=0, stroke_linejoin="meter"
            )

    def test_add_edge_stochastic_map_accepts_stroke_dasharray(self):
        """Accept dasharray as string and tuple formats."""
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_edge_stochastic_map(
            a, self.maps, map_id=0, stroke_dasharray="2,2"
        )
        text = xml.tostring(toyplot.html.render(c), encoding="unicode")
        self.assertIn("stroke-dasharray:2,2", text)

        c2, a2, m2 = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_edge_stochastic_map(
            a2, self.maps, map_id=0, stroke_dasharray=(2, 2)
        )
        text2 = xml.tostring(toyplot.html.render(c2), encoding="unicode")
        self.assertIn("stroke-dasharray:2,2", text2)

    def test_add_edge_stochastic_map_rejects_invalid_stroke_dasharray(self):
        """Reject invalid dasharray tuple length and negative values."""
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        with self.assertRaises(ValueError):
            self.tree.annotate.add_edge_stochastic_map(
                a, self.maps, map_id=0, stroke_dasharray=(2, 2, 2)
            )
        with self.assertRaises(ValueError):
            self.tree.annotate.add_edge_stochastic_map(
                a, self.maps, map_id=0, stroke_dasharray=(-1, 2)
            )

    def test_add_edge_stochastic_map_scalar_opacity_on_paths(self):
        """Apply scalar opacity to individual stochastic-map paths."""
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_edge_stochastic_map(a, self.maps, map_id=0, opacity=0.3)
        text = xml.tostring(toyplot.html.render(c), encoding="unicode")
        self.assertIn("stroke-opacity:0.3", text)

    def test_add_edge_stochastic_map_array_opacity_on_paths(self):
        """Apply per-edge opacity values to stochastic-map path styles."""
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        opac = np.linspace(0.1, 0.9, self.tree.nnodes)
        mark = self.tree.annotate.add_edge_stochastic_map(
            a, self.maps, map_id=0, opacity=opac
        )
        self.assertIsNotNone(mark)
        self.assertGreater(float(np.max(mark.opacity)), float(np.min(mark.opacity)))

    def test_add_edge_stochastic_map_mask_hides_edges(self):
        """Mask hidden edges by reducing generated path count."""
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        all_mark = self.tree.annotate.add_edge_stochastic_map(a, self.maps, map_id=0)
        c2, a2, m2 = self.tree.draw(layout="d", edge_type="p")
        mask = self.tree.get_node_mask(
            show_tips=True, show_internal=False, show_root=False
        )
        tip_mark = self.tree.annotate.add_edge_stochastic_map(
            a2, self.maps, map_id=0, mask=mask
        )
        self.assertIsNotNone(all_mark)
        self.assertIsNotNone(tip_mark)
        self.assertLess(len(tip_mark.xpaths), len(all_mark.xpaths))

    def test_add_edge_stochastic_map_applies_shifts(self):
        """Apply xshift/yshift offsets to generated path coordinates."""
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        base = self.tree.annotate.add_edge_stochastic_map(a, self.maps, map_id=0)
        c2, a2, m2 = self.tree.draw(layout="d", edge_type="p")
        shifted = self.tree.annotate.add_edge_stochastic_map(
            a2, self.maps, map_id=0, xshift=1.5, yshift=-2.0
        )
        self.assertIsNotNone(base)
        self.assertIsNotNone(shifted)
        self.assertAlmostEqual(
            float(shifted.xpaths[0][0] - base.xpaths[0][0]), 1.5, places=8
        )
        self.assertAlmostEqual(
            float(shifted.ypaths[0][0] - base.ypaths[0][0]), -2.0, places=8
        )


