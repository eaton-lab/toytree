#!/usr/bin/env python
# ruff: noqa: D101, D102

"""Tests for annotate.add_edges."""

import re
import xml.etree.ElementTree as xml

import numpy as np
import toyplot.html

import toytree
from toytree.drawing.src.path_edges import get_tree_edge_polylines



from conftest import PytestCompat

class TestAnnotateAddEdges(PytestCompat):
    def setUp(self):
        self.tree = toytree.rtree.unittree(ntips=8, seed=123)

    def test_add_edges_smoke(self):
        c, a, m = self.tree.draw()
        mark = self.tree.annotate.add_edges(a)
        self.assertIsNotNone(mark)

    def test_add_edges_with_mask_and_arrays(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        colors = ["red"] * self.tree.nnodes
        widths = [1 + (i % 3) for i in range(self.tree.nnodes)]
        opac = [0.5] * self.tree.nnodes
        mask = self.tree.get_node_mask(
            show_tips=True, show_internal=False, show_root=False
        )
        mark = self.tree.annotate.add_edges(
            a,
            color=colors,
            width=widths,
            opacity=opac,
            mask=mask,
        )
        self.assertIsNotNone(mark)

    def test_add_edges_rooted_includes_both_root_adjacent_edges(self):
        c, a, m = self.tree.draw(layout="d")
        mark = self.tree.annotate.add_edges(a, mask=(1, 1, 1), color="red", width=3)
        self.assertIsNotNone(mark)

    def test_add_edges_circular_layout_smoke(self):
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_edges(a, mask=(1, 1, 1), color="red", width=2)
        self.assertIsNotNone(mark)

    def test_add_edges_accepts_stroke_linejoin(self):
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color="red",
            width=4,
            stroke_linejoin="miter",
        )
        self.assertIsNotNone(mark)
        root = toyplot.html.render(c)
        text = xml.tostring(root, encoding="unicode")
        self.assertIn("stroke-linejoin:miter", text)

    def test_add_edges_scalar_opacity_on_group(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color="red",
            width=5,
            opacity=0.3,
        )
        text = xml.tostring(toyplot.html.render(c), encoding="unicode")
        g = re.search(r'toytree-Annotation-Lines"[^>]*style="([^"]+)"', text)
        self.assertIsNotNone(g)
        self.assertIn("opacity:0.3", g.group(1))
        p = re.search(r'id="Line-0"[^>]*style="([^"]+)"', text)
        self.assertIsNotNone(p)
        self.assertNotIn("opacity:0.3", p.group(1))

    def test_add_edges_array_opacity_on_paths(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        opac = np.linspace(0.1, 0.9, self.tree.nnodes)
        self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color="red",
            width=5,
            opacity=opac,
        )
        text = xml.tostring(toyplot.html.render(c), encoding="unicode")
        p = re.search(r'id="Line-0"[^>]*style="([^"]+)"', text)
        self.assertIsNotNone(p)
        self.assertIn("opacity:", p.group(1))

    def test_add_edges_rejects_invalid_stroke_linejoin(self):
        c, a, m = self.tree.draw(layout="d")
        with self.assertRaises(ValueError):
            self.tree.annotate.add_edges(
                a,
                mask=(1, 1, 1),
                stroke_linejoin="meter",
            )

    def test_add_edges_accepts_stroke_dasharray_str(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color="red",
            stroke_dasharray="2,2",
        )
        text = xml.tostring(toyplot.html.render(c), encoding="unicode")
        self.assertIn("stroke-dasharray:2,2", text)

    def test_add_edges_accepts_stroke_dasharray_tuple(self):
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color="red",
            stroke_dasharray=(2, 2),
        )
        text = xml.tostring(toyplot.html.render(c), encoding="unicode")
        self.assertIn("stroke-dasharray:2,2", text)

    def test_add_edges_rejects_invalid_stroke_dasharray_tuple_size(self):
        c, a, m = self.tree.draw(layout="d")
        with self.assertRaises(ValueError):
            self.tree.annotate.add_edges(
                a,
                mask=(1, 1, 1),
                stroke_dasharray=(2, 2, 2),
            )

    def test_add_edges_rejects_invalid_stroke_dasharray_values(self):
        c, a, m = self.tree.draw(layout="d")
        with self.assertRaises(ValueError):
            self.tree.annotate.add_edges(
                a,
                mask=(1, 1, 1),
                stroke_dasharray=(-1, 2),
            )

    def test_add_edges_color_gradient_svg_defs_present(self):
        self.tree.pcm.simulate_discrete_trait(
            3, trait_name="X", state_names="ABC", inplace=True, seed=123
        )
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        mark = self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color=("X", "Dark2"),
            width=6,
            opacity=0.4,
            use_color_gradient=True,
        )
        self.assertIsNotNone(mark)
        root = toyplot.html.render(c)
        text = xml.tostring(root, encoding="unicode")
        self.assertIn("<defs>", text)
        self.assertIn("<linearGradient", text)
        self.assertIn('gradientUnits="userSpaceOnUse"', text)
        self.assertIn('stroke="url(#', text)

    def test_add_edges_color_gradient_paths_oriented_root_to_tip(self):
        self.tree.pcm.simulate_discrete_trait(
            3, trait_name="X", state_names="ABC", inplace=True, seed=123
        )
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        gmark = self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color=("X", "Dark2"),
            use_color_gradient=True,
        )
        shown_edges = m.etable[: self.tree.nnodes - 1]
        for idx, (cidx, pidx) in enumerate(shown_edges):
            xdat = gmark.xpaths[idx]
            ydat = gmark.ypaths[idx]
            cx, cy = m.ntable[cidx]
            px, py = m.ntable[pidx]
            dstart_parent = (xdat[0] - px) ** 2 + (ydat[0] - py) ** 2
            dstart_child = (xdat[0] - cx) ** 2 + (ydat[0] - cy) ** 2
            self.assertLessEqual(dstart_parent, dstart_child)

    def test_add_edges_color_gradient_with_none_color_falls_back(self):
        c, a, m = self.tree.draw(layout="d")
        mark = self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color=None,
            use_color_gradient=True,
        )
        self.assertIsNotNone(mark)
        root = toyplot.html.render(c)
        text = xml.tostring(root, encoding="unicode")
        self.assertNotIn("<linearGradient", text)
        self.assertNotIn('stroke="url(#', text)

    def test_add_edges_gradient_scalar_opacity_on_group(self):
        self.tree.pcm.simulate_discrete_trait(
            3, trait_name="X", state_names="ABC", inplace=True, seed=123
        )
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color=("X", "Dark2"),
            width=6,
            opacity=0.2,
            use_color_gradient=True,
        )
        root = toyplot.html.render(c)
        text = xml.tostring(root, encoding="unicode")
        self.assertIn("toytree-Annotation-GradientLines", text)
        g = re.search(r'toytree-Annotation-GradientLines"[^>]*style="([^"]*)"', text)
        self.assertIsNotNone(g)
        self.assertIn("opacity:0.2", g.group(1))
        m = re.search(r'id="GradientLine-0"[^>]*style="([^"]+)"', text)
        self.assertIsNotNone(m)
        self.assertIsNone(re.search(r'id="GradientLine-0"[^>]*\sopacity="', text))

    def test_add_edges_gradient_array_opacity_on_paths(self):
        self.tree.pcm.simulate_discrete_trait(
            3, trait_name="X", state_names="ABC", inplace=True, seed=123
        )
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        opac = np.linspace(0.1, 0.9, self.tree.nnodes)
        self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color=("X", "Dark2"),
            width=4,
            opacity=opac,
            use_color_gradient=True,
        )
        root = toyplot.html.render(c)
        text = xml.tostring(root, encoding="unicode")
        self.assertIn("GradientLine-0", text)
        self.assertIsNotNone(re.search(r'id="GradientLine-0"[^>]*\sopacity="', text))

    def test_add_edges_gradient_scalar_opacity_sets_group_opacity(self):
        self.tree.pcm.simulate_discrete_trait(
            3, trait_name="X", state_names="ABC", inplace=True, seed=123
        )
        c, a, m = self.tree.draw(layout="d", edge_type="p")
        self.tree.annotate.add_edges(
            a,
            mask=(1, 1, 1),
            color=("X", "Dark2"),
            width=4,
            opacity=0.25,
            use_color_gradient=True,
        )
        root = toyplot.html.render(c)
        text = xml.tostring(root, encoding="unicode")
        g = re.search(r'toytree-Annotation-GradientLines"[^>]*style="([^"]+)"', text)
        self.assertIsNotNone(g)
        self.assertIn("opacity:0.25", g.group(1))
        self.assertIsNone(re.search(r'id="GradientLine-0"[^>]*\sopacity="', text))

    def test_circular_phylogram_arc_segments_use_short_path(self):
        c, a, m = self.tree.draw(layout="c", edge_type="p")
        xpaths, ypaths, _ = get_tree_edge_polylines(a, m, space="data")
        rootx, rooty = m.ntable[-1]
        for xs, ys in zip(xpaths, ypaths):
            if xs.size < 4:
                continue
            # Arc section starts at index 1 (after child->ring segment).
            ang = np.arctan2(ys[1:] - rooty, xs[1:] - rootx)
            unwrapped = np.unwrap(ang)
            span = float(np.abs(unwrapped[-1] - unwrapped[0]))
            self.assertLessEqual(span, np.pi + 1e-6)


