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
               |    |                  |
               move to start position on arc.
</g>                |                  |
                    arc: rx ry x-axis-rotation large-arc-floag sweep-flag x y
                         radius    always 0        %>50 or no    always 1  end
                                       |
                                       move to center of circle.
"""

from typing import List, Union
import functools
import xml.etree.ElementTree as xml
from multipledispatch import dispatch
import toyplot
import numpy as np
from toytree.core.drawing.render import style_to_string, split_rgba_style
from toytree.annotate.pie_chart_mark import PieChartMark
from toytree.core.style.color import ToyColor

# Register multipledispatch to use the toyplot.html namespace
dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)

@dispatch(toyplot.coordinates.Cartesian, PieChartMark, toyplot.html.RenderContext)
def _render(axes, mark, context):
    RenderPieChart(axes, mark, context)


class RenderPieChart:
    """Multidispatch registered render function for PieChartMarks.

    The PieChartMark object is self.mark and contains the data,
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

        # check color styles
        colors = {}
        for cidx, color in enumerate(self.mark.colors):
            fill = ToyColor(color).css
            colors[cidx] = split_rgba_style({'fill': fill})

        # create a group for pie node markers
        self.mark_xml = xml.SubElement(
            self.context.parent, "g",
            id=self.context.get_id(self.mark),
            attrib={"class": "toytree-mark-PieCharts"},
        )

        # get shared inner stroke styles
        shared_style = {
            "stroke-linecap": "round",
            "stroke-width": self.mark.istroke_width,
        }
        shared_style.update(
            split_rgba_style({"stroke": ToyColor(self.mark.istroke).css})
        )

        # render the pies as a group of path elements.
        for nidx in range(self.mark.coordinates.shape[0]):
            group = xml.SubElement(
                self.mark_xml, "g",
                attrib={'id': f'pie-{nidx}'},
                style=style_to_string(shared_style),
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
                path = get_pie_path(
                    percent_start=start_sum,
                    percent_end=end_sum,
                    radius=self.mark.sizes[nidx],
                )
                xml.SubElement(
                    group, "path",
                    d=path,
                    style=style_to_string(colors[cidx])
                )

            # add a circle to outline the node and 
            # TODO: provide optional title hover
            ostyle = {
                "fill": "none", 
                "stroke-width": self.mark.ostroke_width,           
            }
            ostyle.update(split_rgba_style(
                {"stroke": ToyColor(self.mark.ostroke).css},
            ))
            xml.SubElement(
                group, "circle",
                r=str(self.mark.sizes[nidx]),
                style=style_to_string(ostyle),
            )


def draw_node_pie_charts(
    axes,
    coordinates,
    data,
    sizes: Union[int,List[int]]=10,
    colors: Union[List[str], 'color']=None,
    ostroke: 'color'="#262626",
    ostroke_width: float=1.5,
    istroke: 'color'="#262626",
    istroke_width: float=0.,
    rotate: int=-45,
    ):
    """Return a Mark representing pie chart xml

    Parameters
    ----------
    ntable: numpy.ndarray
        x and y coordinate positions of the pie charts.
    data: numpy.ndarray
        Percentage data of dimensions (ncategories, nmarks)
    ...
    rotate: int
        Angle of rotation of pie chart.

    Returns
    -------
    toyplot.Mark

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10, seed=123)
    >>> canvas, axes, mark = tree.draw()
    >>> data = np.array([[0.5, 0.3, 0.2]] * tree.nnodes)
    >>> mark = toytree.annotate.draw_node_pie_chart(
    >>>     axes=axes, 
    >>>     coordinates=tree.get_node_coordinates('r'),
    >>>     data=data,
    >>>     sizes=12, 
    >>>     colors=toytree.COLORS2, 
    >>> )
    """
    # generate toyplot Mark. todo: Style is already validated?
    mark = PieChartMark(
        coordinates=coordinates,
        data=data,
        sizes=sizes,
        colors=colors,
        ostroke=ostroke,
        ostroke_width=ostroke_width,
        istroke=istroke,
        istroke_width=istroke_width,
        rotate=rotate,
    )

    # add mark to axes
    axes.add_mark(mark)
    return mark


def get_pie_path(percent_start, percent_end, radius):
    """Return a SVG path for a circle arc.
    <path d='M end_x end_y A r r 0 flag 1 end_x end_y L 0 0'></path>
    """
    start = get_radial_coordinates_for_percents(percent_start)
    end = get_radial_coordinates_for_percents(percent_end)
    flag = int((percent_end - percent_start) > 0.5)
    return (
        f"M 0 0 L {radius * start[0]} {radius * start[1]} "
        f"A {radius} {radius} 0 {flag} 1 {radius * end[0]} {radius * end[1]} "
        f"L 0 0"
    )

def get_radial_coordinates_for_percents(percent):
    """Return the coordinates on a circle of a percentage."""
    xpos = round(np.cos(2 * np.pi * percent), 7)
    ypos = round(np.sin(2 * np.pi * percent), 7)
    return xpos, ypos


if __name__ == "__main__":


    import toytree
    import toyplot

    TREE = toytree.rtree.bdtree(100, seed=123)
    c, a, m = TREE.draw(width=400, height=600, node_sizes=5)
    DATA = np.array([[0.5, 0.3, 0.2]] * (TREE.nnodes - TREE.ntips))
    COLORS = toytree.COLORS1 #

    MARK = draw_node_pie_charts(
        axes=a, 
        coordinates=TREE.get_node_coordinates('r')[TREE.ntips:],
        data=DATA,
        sizes=10,
        colors=COLORS, 
        istroke="black", 
        istroke_width=0.5,
        ostroke="black",
        ostroke_width=1.5,
    )

    import toyplot.browser
    toyplot.browser.show(c)
