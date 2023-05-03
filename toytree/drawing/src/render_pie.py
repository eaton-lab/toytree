#!/usr/bin/env python

"""
Custom toyplot Mark to create SVG pie charts on nodes, and a
user-facing annotation function for plotting pie charts from
... data.

A standard CSS way to do piecharts is with many circle elements
piled up and using stroke-dasharray and stroke-offset. Its an
ugly hack, we're not using it.

An alternative is to draw filled path arcs in SVG. This is not so
different from what we already do to draw the tree edges, so I
preferred to use this.

<g class='pie-0'b style='stroke: black; stroke-width: 1'>
    <path d="M 1 0 A 1 1 0 0 1 0.8 0.5 L 0 0" style='fill:red'><path>
    <path d="M 1 0 A 0 1 0 0 1 0.8 0.5 L 0 0" style='fill:pink'><path>
</g>           |    |                  |
               move to start position on arc.
                    |                  |
                    arc: rx ry x-axis-rotation large-arc-floag sweep-flag x y
                         radius    always 0        %>50 or no    always 1  end
                                       |
                                       move to center of circle.
"""

import functools
import xml.etree.ElementTree as xml
from multipledispatch import dispatch
import toyplot
import numpy as np
from toytree import ToyTree
from toytree.color import ToyColor
from toytree.color.src.concat import concat_style_fix_color
from toytree.annotate.src.pie_chart_mark import PieChartMark


# Register multipledispatch to use the toyplot.html namespace
dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)


#######################################################################
@dispatch(toyplot.coordinates.Cartesian, PieChartMark, toyplot.html.RenderContext)
def _render(axes, mark, context):
    RenderPieChart(axes, mark, context)
#######################################################################


class RenderPieChart:
    """Multidispatch registered render function for PieChartMarks.

    The PieChartMark object is a custom Mark and contains the data,
    coordinates, and styles. The colors are checked here during
    rendering.
    """
    def __init__(self, axes, mark, context):
        self.axes = axes
        self.mark = mark
        self.context = context

        # project coordinates to axes
        self.nodes_x = self.axes.project('x', self.mark.coordinates[:, 0])
        self.nodes_y = self.axes.project('y', self.mark.coordinates[:, 1])

        # create a group for pie node markers
        self.mark_xml = xml.SubElement(
            self.context.parent, "g",
            id=self.context.get_id(self.mark),
            attrib={"class": "toytree-mark-PieCharts"},
        )

        # fill dict w/ dicts {idx: {fill: ..., fill-opacity: ...}, ...}
        colors = {}
        for cidx, color in enumerate(self.mark.colors):
            colors[cidx] = {'fill': ToyColor(color)}

        # get shared inner stroke styles
        shared_style = {
            "stroke-linecap": "round",
            "stroke-width": self.mark.istroke_width,
        }
        shared_style.update({"stroke": ToyColor(self.mark.istroke).css})

        # render the pies as a group of path elements.
        for nidx in range(self.mark.coordinates.shape[0]):
            group = xml.SubElement(
                self.mark_xml, "g",
                attrib={'id': f'pie-{nidx}'},
                style=concat_style_fix_color(shared_style),
            )
            transform = (
                f"translate({self.nodes_x[nidx]:.3f},{self.nodes_y[nidx]:.3f}) "
                f"rotate({self.mark.rotate})"
            )
            group.set("transform", transform)

            # iterate over slices: e.g., [0.3, 0.5, 0.2]
            # sums = [0, 0.3, 0.8, 1.0]
            for cidx in range(self.mark.data[0].size):
                start_sum = self.mark.data[nidx][:cidx].sum()
                end_sum = self.mark.data[nidx][:cidx + 1].sum()

                # only set radius on circle since placement uses transform
                path = _get_pie_path(
                    percent_start=start_sum,
                    percent_end=end_sum,
                    radius=self.mark.sizes[nidx],
                )
                xml.SubElement(
                    group, "path",
                    d=path,
                    style=concat_style_fix_color(colors[cidx])
                )

            # add a circle to outline the node and
            # TODO: provide optional title hover
            ostyle = {
                "fill": (0, 0, 0, 0),
                "stroke-width": self.mark.ostroke_width,
            }
            ostyle.update({"stroke": ToyColor(self.mark.ostroke)})
            xml.SubElement(
                group, "circle",
                r=str(self.mark.sizes[nidx]),
                style=concat_style_fix_color(ostyle),
            )


def validate_pie_data(
    tree: ToyTree,
    data: np.ndarray,
    # min_size: float = 1e-9,
    # mask: np.ndarray = None,
) -> np.ndarray:
    """Return cleaned pie chart data.

    Checks pie chart data for correct shape and type, and that the row
    values sum to 1.

    Formats
    -------
    - 1-D array -> 2-D array
    - 2-D array -> 2-D array sums to 1
    """
    assert data.min() >= 0, "negative values are not allowed in pie chart data."
    assert data.shape[0] in (tree.nnodes, tree.nnodes - 1), (
        f"pie chart data must be shape (nnodes, nvalues), your data is {data.shape}.")

    # allow single value arrays in [0, 1] to represent two categories
    if data.ndim == 1:
        if data.max() > 1:
            raise ValueError(
                "1 dimensional array data for pie charts must be < 1 to "
                "be expanded to 2 categories: (value, 1 - value).")
        return np.column_stack([data, 1 - data])

    # 2D arrays represent (ntips, ntraits) data.
    else:
        assert np.allclose(data.sum(axis=1), 1), "pie chart data row values must sum to 1."
    return data


def _get_pie_path(percent_start: float, percent_end: float, radius: float) -> str:
    """Return a SVG path for a circle arc.

    <path d='M end_x end_y A r r 0 flag 1 end_x end_y L 0 0'></path>
    """
    start = _get_radial_coordinates_for_percents(percent_start)
    end = _get_radial_coordinates_for_percents(percent_end)
    flag = int((percent_end - percent_start) > 0.5)
    return (
        f"M 0 0 L {radius * start[0]} {radius * start[1]} "
        f"A {radius} {radius} 0 {flag} 1 {radius * end[0]} {radius * end[1]} "
        f"L 0 0"
    )


def _get_radial_coordinates_for_percents(percent):
    """Return the coordinates on a circle of a percentage."""
    xpos = round(np.cos(2 * np.pi * percent), 7)
    ypos = round(np.sin(2 * np.pi * percent), 7)
    return xpos, ypos


if __name__ == "__main__":

    import toytree
    import toyplot

    TREE = toytree.rtree.bdtree(30, seed=123)
    c, a, m = TREE.draw(width=400, height=600, node_sizes=5)
    DATA = np.array([[0.5, 0.3, 0.2]] * (TREE.nnodes))
    COLORS = toytree.color.COLORS1
    TREE.annotate.add_node_pie_charts(axes=a, data=DATA, colors="Greys", mask=False)

    import toyplot.browser
    toyplot.browser.show(c)
