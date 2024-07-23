#!/usr/bin/env python

"""...

"""

import functools
import xml.etree.ElementTree as xml

from multipledispatch import dispatch
import toyplot.html
from toyplot.coordinates import Cartesian
from loguru import logger

from toytree.drawing.src.render_marker import render_marker
from toytree.color.src.concat import concat_style_fix_color
from toytree.drawing.src.mark_annotation import (
    AnnotationMarker, AnnotationRect)

logger = logger.bind(name="toytree")

# ---------------------------------------------------------------------
# Register multipledispatch to use the toyplot.html namespace
dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)


# noqa: F811: multidispatch allows reuse the _render() function name
@dispatch(toyplot.coordinates.Cartesian, AnnotationMarker, toyplot.html.RenderContext)
def _render(axes, mark, context):
    render_markers(axes, mark, context)


@dispatch(toyplot.coordinates.Cartesian, AnnotationRect, toyplot.html.RenderContext)
def _render(axes, mark, context):
    render_rect(axes, mark, context)
# ---------------------------------------------------------------------


def render_markers(
    axes: Cartesian,
    mark: AnnotationMarker,
    context: toyplot.html.RenderContext,
) -> None:
    """...

    """
    # create a <g ..> to group markers into.
    axml = xml.SubElement(
        context.parent, "g",
        id=context.get_id(mark),
        attrib={"class": "toytree-Annotation-Markers"},
        style=concat_style_fix_color(mark.style),
    )

    # project coordinates from data units to px units
    nodes_x = axes.project('x', mark.ntable[:, 0])
    nodes_y = axes.project('y', mark.ntable[:, 1])

    # create a marker for each point and add to axml group
    for nidx in range(mark.ntable.shape[0]):

        # create the <marker ...>
        marker = toyplot.marker.create(
            shape=mark.shapes[nidx],
            size=mark.sizes[nidx],
        )

        # create a <g ..> element for marker w/ or w/o unique style
        attrib = {"id": f"Mark-{nidx}"}
        if (mark.colors is None) and (mark.opacity is None):
            marker_xml = xml.SubElement(axml, "g", attrib=attrib)
        elif mark.colors is None:
            style = f"fill-opacity: {mark.opacity[nidx]:.3f}"
            marker_xml = xml.SubElement(axml, "g", attrib=attrib, style=style)
        else:
            style = concat_style_fix_color({
                "fill": None if mark.colors is None else mark.colors[nidx],
                "fill-opacity": None if mark.opacity is None else mark.opacity[nidx],
            })
            marker_xml = xml.SubElement(axml, "g", attrib=attrib, style=style)

        # project marker in coordinate space
        transform = "translate({:.6g},{:.6g})".format(
            nodes_x[nidx] + mark.xshift,
            nodes_y[nidx] + mark.yshift,
        )
        marker_xml.set("transform", transform)

        # get shape from toyplot marker library
        render_marker(marker_xml, marker)


def render_rect(
    axes: Cartesian,
    mark: AnnotationRect,
    context: toyplot.html.RenderContext,
) -> None:
    """Render rectangle Mark and append to HTML.

    custom rect render function to allow transform in px units and
    curved edge styling.
    """
    # create a <g ..> to group markers into.
    axml = xml.SubElement(
        context.parent, "g",
        id=context.get_id(mark),
        attrib={"class": "toytree-Annotation-Rect"},
        style=concat_style_fix_color(mark.style),
    )

    # project coordinates from data units to px units
    left_x = axes.project('x', mark.xtable[:, 0])
    right_x = axes.project('x', mark.xtable[:, 1])
    top_y = axes.project('y', mark.ytable[:, 0])
    bot_y = axes.project('y', mark.ytable[:, 1])

    widths = right_x - left_x
    heights = abs(top_y - bot_y)

    # create a marker for each point and add to axml group
    for nidx in range(mark.ntable.shape[0]):

        # create a <g ..> element for marker w/ or w/o unique style
        attrib = {"id": f"Rect-{nidx}"}
        if (mark.colors is None) and (mark.opacity is None):
            marker_xml = xml.SubElement(axml, "g", attrib=attrib)
        elif mark.colors is None:
            style = f"fill-opacity: {mark.opacity[nidx]:.3f}"
            marker_xml = xml.SubElement(axml, "g", attrib=attrib, style=style)
        else:
            style = concat_style_fix_color({
                "fill": None if mark.colors is None else mark.colors[nidx],
                "fill-opacity": None if mark.opacity is None else mark.opacity[nidx],
            })
            marker_xml = xml.SubElement(axml, "g", attrib=attrib, style=style)

        # position marker in coordinate space
        xpos = left_x[nidx] + mark.xshift
        ypos = bot_y[nidx] - mark.yshift
        transform = f"translate({xpos:.8g},{ypos:.8g})"
        marker_xml.set("transform", transform)

        # add rect to marker: <rect width=x height=y rx=[0-50] ry=[0-50] />
        kwargs = dict(
            width=f"{widths[nidx]:.8g}",
            height=f"{heights[nidx]:.8g}",
            rx="1",
            ry="1",
        )
        _ = xml.SubElement(marker_xml, "rect", **kwargs)


if __name__ == "__main__":

    import toytree

    # base tree drawing
    tree = toytree.rtree.unittree(15)
    c, a, m = tree.draw(layout='d', scale_bar=True, node_sizes=5, node_colors='black')

    m1 = tree.annotate.add_node_bars(
        a,
        bar_min=tree.get_node_data("height").values * 0.8,
        bar_max=tree.get_node_data("height").values * 1.25,
        size=0.3,
        style={"fill-opacity": 0.4, "stroke": None},
        z_index=-1,
        color='red',
    )
    toytree.utils.show(c)
