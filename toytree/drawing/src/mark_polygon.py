#!/usr/bin/env python

"""A simple polygon shape Marker in toyplot style.

SVG
---
<polygon points="100,100 150,25 150,75 200,0" fill="none" stroke="black" />

Python
------
In toytree this code is used only to setup container tree (e.g., 
species trees) drawings. But, in the future this could be ported
to toyplot as a more general polygon shape object for complex 
shapes such as maps, etc.

>>> toytree.container(...)
"""

from typing import List, Tuple

import functools
import xml.etree.ElementTree as xml
from multipledispatch import dispatch

import numpy as np
import toyplot.html
from toyplot.mark import Mark
from toytree.color import ToyColor
# from toytree.color.src.utils import style_to_string, split_rgba_style, concat_style_to_str
# from toytree.color.src.utils import concat_style_to_str
from toytree.style.src.utils import concat_style_to_str2


class Polygon(Mark):
    def __init__(self, points: np.ndarray, **kwargs):
        Mark.__init__(self, annotation=kwargs.get("annotation", False))

        self._coordinate_axes: List[str] = ["x", "y"]
        self._table = points
        # self.points: str = self._points_to_str(points)
        self.stroke: str = kwargs.get("stroke", "black")
        self.stroke_width: float = kwargs.get("stroke_width", 1)
        self.fill: str = kwargs.get("fill", ToyColor("black"))

    def domain(self, axis: str) -> np.ndarray:
        """Return position of Marks on a coordinate axis."""
        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self._table[:, index])
        return domain

    def extents(self, axes: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Return extent of Marks extending from their coordinates."""
        extents = [np.zeros(self._table.shape[0]) for i in range(4)]
        return tuple(self._table.T), tuple(extents)


# ---------------------------------------------------------------------
# Register multipledispatch to use the toyplot.html namespace
dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)


# register a _render function for ToyTreeMark objects
@dispatch(toyplot.coordinates.Cartesian, Polygon, toyplot.html.RenderContext)
def _render(axes, mark, context):
    RenderPolygon(axes, mark, context)
# ---------------------------------------------------------------------    


class RenderPolygon:
    def __init__(self, axes, mark, context):
        self.axes = axes
        self.mark = mark
        self.context = context

        self.mark_xml: xml.SubElement = xml.SubElement(
            context.parent, "g",
            id=context.get_id(self.mark),
            attrib={"class": "toytree-Polygon"},
        )

        xproj = self.axes.project("x", self.mark._table[:, 0])
        yproj = self.axes.project("y", self.mark._table[:, 1]) 
        points = " ".join([f"{i[0]},{i[1]}" for i in zip(xproj, yproj)])
        xml.SubElement(
            self.mark_xml, "polygon",
            points=points,
            style=concat_style_to_str2({
                "fill": "red", 
                "fill-opacity": 0.5,
                "stroke": self.mark.stroke,
                "stroke-width": 3,
            }),
        )


if __name__ == "__main__":

    import toytree
    import toyplot

    arr = np.array([
        [0, 0],
        [5, 0],
        [6, 2],
        [3, 3],
        [0, 0],
    ])
    pol = Polygon(points=arr, stroke="blue")
    cvs = toyplot.Canvas(300, 300)
    axe = cvs.cartesian()
    axe.add_mark(pol)

    toytree.utils.show(cvs)
