#!/usr/bin/env python

"""Tests for svg defs / linearGradient helpers."""

import xml.etree.ElementTree as xml
from types import SimpleNamespace

import toyplot.html
from conftest import PytestCompat

import toytree
from toytree.drawing.src.render.svg_defs import (
    LinearGradient,
    LinearGradientStop,
    add_linear_gradient,
    ensure_linear_gradients,
    get_or_create_defs,
    get_svg_element,
)


class TestSvgDefs(PytestCompat):
    def test_get_or_create_defs_inserts_first_child(self):
        svg = xml.Element("svg")
        _ = xml.SubElement(svg, "g")
        defs = get_or_create_defs(svg)
        self.assertEqual(defs.tag, "defs")
        self.assertIs(list(svg)[0], defs)

    def test_add_linear_gradient_creates_expected_xml(self):
        defs = xml.Element("defs")
        grad = LinearGradient(
            id="grad-a",
            attrs={"x1": "0%", "x2": "0%", "y1": "0%", "y2": "100%"},
            stops=[
                LinearGradientStop(offset="0%", color="red"),
                LinearGradientStop(offset="100%", color="blue", opacity=0.5),
            ],
        )
        out = add_linear_gradient(defs, grad)
        self.assertEqual(out.tag, "linearGradient")
        self.assertEqual(out.attrib["id"], "grad-a")
        stops = [i for i in list(out) if i.tag == "stop"]
        self.assertEqual(len(stops), 2)
        self.assertEqual(stops[0].attrib["offset"], "0%")
        self.assertEqual(stops[0].attrib["stop-color"], "red")
        self.assertEqual(stops[1].attrib["offset"], "100%")
        self.assertEqual(stops[1].attrib["stop-color"], "blue")
        self.assertEqual(stops[1].attrib["stop-opacity"], "0.5")

    def test_add_linear_gradient_duplicate_id_raises(self):
        defs = xml.Element("defs")
        grad = LinearGradient(
            id="dup",
            stops=[LinearGradientStop(offset="0%", color="red")],
        )
        add_linear_gradient(defs, grad)
        with self.assertRaises(ValueError):
            add_linear_gradient(defs, grad)

    def test_get_svg_element_finds_svg_under_root(self):
        tree = toytree.rtree.unittree(5, seed=123)
        canvas, axes, mark = tree.draw()
        root = toyplot.html.render(canvas)
        context = SimpleNamespace(root=root)
        svg = get_svg_element(context)
        self.assertEqual(svg.tag, "svg")

    def test_ensure_linear_gradients_returns_url_mapping(self):
        tree = toytree.rtree.unittree(5, seed=123)
        canvas, axes, mark = tree.draw()
        root = toyplot.html.render(canvas)
        context = SimpleNamespace(root=root)
        mapping = ensure_linear_gradients(
            context,
            gradients=[
                LinearGradient(
                    id="grad-one",
                    stops=[
                        LinearGradientStop(offset="0%", color="black"),
                        LinearGradientStop(offset="100%", color="white"),
                    ],
                ),
            ],
        )
        self.assertEqual(mapping["grad-one"], "url(#grad-one)")
        svg = get_svg_element(context)
        defs = svg.find("defs")
        self.assertIsNotNone(defs)
        self.assertIsNotNone(defs.find("./linearGradient[@id='grad-one']"))
