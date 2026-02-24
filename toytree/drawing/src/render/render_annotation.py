#!/usr/bin/env python

"""Render methods for custom Annotation Marks."""

import functools
import xml.etree.ElementTree as xml

import toyplot.html
from multipledispatch import dispatch
from toyplot.coordinates import Cartesian

from toytree.color import ToyColor
from toytree.color.src.concat import concat_style_fix_color
from toytree.drawing.src.mark_annotation import (
    AnnotationGradientLine,
    AnnotationLine,
    AnnotationMarker,
    AnnotationRect,
)
from toytree.drawing.src.render.render_marker import render_marker
from toytree.drawing.src.render.svg_defs import (
    LinearGradient,
    LinearGradientStop,
    ensure_linear_gradients,
)

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


@dispatch(toyplot.coordinates.Cartesian, AnnotationLine, toyplot.html.RenderContext)
def _render(axes, mark, context):
    render_lines(axes, mark, context)


@dispatch(toyplot.coordinates.Cartesian, AnnotationGradientLine, toyplot.html.RenderContext)
def _render(axes, mark, context):
    render_gradient_lines(axes, mark, context)
# ---------------------------------------------------------------------


def render_markers(
    axes: Cartesian,
    mark: AnnotationMarker,
    context: toyplot.html.RenderContext,
) -> None:
    """Dispatched method to insert markers into XML."""
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
    """Dispatched method to insert rectangle Mark into XML.

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


def render_lines(
    axes: Cartesian,
    mark: AnnotationLine,
    context: toyplot.html.RenderContext,
) -> None:
    """Dispatched method to insert polyline Mark (e.g., tree edge) into XML."""
    group_style = dict(mark.style)

    # group-level opacity mode for edge annotations.
    if mark.use_group_opacity and (mark.group_opacity is not None):
        group_style.pop("stroke-opacity", None)
        group_style["opacity"] = mark.group_opacity

    # create the <g> group element for a set of Annotation Edges
    group_xml = xml.SubElement(
        context.parent,
        "g",
        id=context.get_id(mark),
        attrib={"class": "toytree-Annotation-Lines"},
        style=concat_style_fix_color(group_style),
    )

    # iterate over (x, y) path coordinates
    for idx, (xdat, ydat) in enumerate(zip(mark.xpaths, mark.ypaths)):
        # get positions in px units
        xpx = axes.project("x", xdat)
        ypx = axes.project("y", ydat)

        # build the path
        parts = [f"M {xpx[0]:.8g} {ypx[0]:.8g}"]
        for jdx in range(1, xpx.size):
            parts.append(f"L {xpx[jdx]:.8g} {ypx[jdx]:.8g}")
        path = " ".join(parts)

        # Start from shared line style, no-fill, then layer per-edge channels.
        path_style = dict(mark.style)
        path_style["fill"] = "none"
        if mark.colors is not None:
            col = ToyColor(mark.colors[idx])
            path_style["stroke"] = col.rgb
            if mark.opacity[idx] in (None, False):
                path_style["stroke-opacity"] = col.rgba[-1]
            else:
                path_style["stroke-opacity"] = mark.opacity[idx]
        else:
            path_style["opacity"] = mark.opacity[idx]

        # set width
        path_style["stroke-width"] = mark.widths[idx]

        # if using group-level opacity then remove edge-level opacity
        if mark.use_group_opacity:
            path_style.pop("opacity", None)
            path_style.pop("stroke-opacity", None)

        # create line element
        xml.SubElement(
            group_xml,
            "path",
            id=f"Line-{idx}",
            d=path,
            style=concat_style_fix_color(path_style),
        )


def render_gradient_lines(
    axes: Cartesian,
    mark: AnnotationGradientLine,
    context: toyplot.html.RenderContext,
) -> None:
    """Render polylines with per-edge linear gradients."""
    group_style = dict(mark.style)

    # group-level opacity mode for edge annotations.
    if mark.use_group_opacity and (mark.group_opacity is not None):
        group_style.pop("stroke-opacity", None)
        group_style["opacity"] = mark.group_opacity

    # create group tag
    group_xml = xml.SubElement(
        context.parent,
        "g",
        id=context.get_id(mark),
        attrib={"class": "toytree-Annotation-GradientLines"},
        style=concat_style_fix_color(group_style),
    )

    # get mark_id apply same name to lines and defs
    mark_id = context.get_id(mark)

    # Use compact, deterministic gradient ids to keep SVG smaller while
    # remaining unique across marks in the same render context.
    short_mark_id = mark_id[-8:]
    gradients = []
    paths = []
    for idx, (xdat, ydat) in enumerate(zip(mark.xpaths, mark.ypaths)):
        xpx = axes.project("x", xdat)
        ypx = axes.project("y", ydat)
        paths.append((xpx, ypx))
        gradients.append(
            LinearGradient(
                id=f"g{short_mark_id}-{idx}",
                attrs={
                    "gradientUnits": "userSpaceOnUse",
                    "x1": f"{xpx[0]:.8g}",
                    "y1": f"{ypx[0]:.8g}",
                    "x2": f"{xpx[-1]:.8g}",
                    "y2": f"{ypx[-1]:.8g}",
                },
                stops=[
                    LinearGradientStop(offset="0%", color=ToyColor(mark.start_colors[idx]).rgb_css),
                    LinearGradientStop(offset="100%", color=ToyColor(mark.end_colors[idx]).rgb_css),
                ],
            )
        )

    refs = ensure_linear_gradients(context, gradients)

    # create the path elements
    for idx, (xpx, ypx) in enumerate(paths):
        parts = [f"M {xpx[0]:.8g} {ypx[0]:.8g}"]
        for jdx in range(1, xpx.size):
            parts.append(f"L {xpx[jdx]:.8g} {ypx[jdx]:.8g}")
        path = " ".join(parts)

        # get copy of path style
        path_style = dict(mark.style)

        # remove all core paint properties
        for key in ("stroke", "fill", "opacity", "stroke-opacity"):
            path_style.pop(key, None)

        # set styles
        path_style["fill"] = "none"
        path_style["stroke-width"] = f"{mark.widths[idx]:.8g}"

        # per-edge opacity
        if not mark.use_group_opacity:
            path_style["opacity"] = f"{mark.opacity[idx]:.8g}"

        # create path element using defined gradient color
        xml.SubElement(
            group_xml,
            "path",
            id=f"GradientLine-{idx}",
            d=path,
            stroke=refs[f"g{short_mark_id}-{idx}"],
            style=concat_style_fix_color(path_style),
        )


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
