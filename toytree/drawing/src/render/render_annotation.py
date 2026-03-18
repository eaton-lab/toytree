#!/usr/bin/env python

"""Render methods for custom Annotation Marks."""

import functools
import xml.etree.ElementTree as xml

import numpy as np
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
    AnnotationStochasticMapLine,
    AnnotationTipBarMark,
    AnnotationTipLabelMark,
    AnnotationTipPathMark,
    AnnotationTipTileMark,
)
from toytree.drawing.src.render.render_marker import render_marker
from toytree.drawing.src.render.render_text import render_text
from toytree.drawing.src.render.svg_defs import (
    LinearGradient,
    LinearGradientStop,
    ensure_linear_gradients,
)
from toytree.layout.src.layout_circular import _parse_circular_layout

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


@dispatch(
    toyplot.coordinates.Cartesian, AnnotationGradientLine, toyplot.html.RenderContext
)
def _render(axes, mark, context):
    render_gradient_lines(axes, mark, context)


@dispatch(
    toyplot.coordinates.Cartesian,
    AnnotationStochasticMapLine,
    toyplot.html.RenderContext,
)
def _render(axes, mark, context):
    render_stochastic_map_lines(axes, mark, context)


@dispatch(
    toyplot.coordinates.Cartesian,
    AnnotationTipTileMark,
    toyplot.html.RenderContext,
)
def _render(axes, mark, context):
    render_tip_tiles(axes, mark, context)


@dispatch(
    toyplot.coordinates.Cartesian,
    AnnotationTipBarMark,
    toyplot.html.RenderContext,
)
def _render(axes, mark, context):
    render_tip_bars(axes, mark, context)


@dispatch(
    toyplot.coordinates.Cartesian,
    AnnotationTipPathMark,
    toyplot.html.RenderContext,
)
def _render(axes, mark, context):
    render_tip_paths(axes, mark, context)


@dispatch(
    toyplot.coordinates.Cartesian,
    AnnotationTipLabelMark,
    toyplot.html.RenderContext,
)
def _render(axes, mark, context):
    render_tip_labels(axes, mark, context)


# ---------------------------------------------------------------------


def render_markers(
    axes: Cartesian,
    mark: AnnotationMarker,
    context: toyplot.html.RenderContext,
) -> None:
    """Dispatched method to insert markers into XML."""
    # create a <g ..> to group markers into.
    axml = xml.SubElement(
        context.parent,
        "g",
        id=context.get_id(mark),
        attrib={"class": "toytree-Annotation-Markers"},
        style=concat_style_fix_color(mark.style),
    )

    # project coordinates from data units to px units
    nodes_x = axes.project("x", mark.ntable[:, 0])
    nodes_y = axes.project("y", mark.ntable[:, 1])
    shift_x = np.asarray(mark.xshift, dtype=float).copy()
    shift_y = np.asarray(mark.yshift, dtype=float).copy()

    # Optional local-frame shifts for circular layouts:
    # span is tangential, depth is radial from the tree root.
    if (
        mark.local_span is not None
        and mark.local_depth is not None
        and mark.root_xy is not None
    ):
        root_x = float(axes.project("x", mark.root_xy[0]))
        root_y = float(axes.project("y", mark.root_xy[1]))
        dx = nodes_x - root_x
        dy = nodes_y - root_y
        radii = np.hypot(dx, dy)
        ux = np.divide(dx, radii, out=np.ones_like(dx), where=radii > 0)
        uy = np.divide(dy, radii, out=np.zeros_like(dy), where=radii > 0)
        tx = -uy
        ty = ux
        shift_x += mark.local_span * tx + mark.local_depth * ux
        shift_y += mark.local_span * ty + mark.local_depth * uy

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
            style = concat_style_fix_color(
                {
                    "fill": None if mark.colors is None else mark.colors[nidx],
                    "fill-opacity": None
                    if mark.opacity is None
                    else mark.opacity[nidx],
                }
            )
            marker_xml = xml.SubElement(axml, "g", attrib=attrib, style=style)

        # project marker in coordinate space
        transform = "translate({:.6g},{:.6g})".format(
            nodes_x[nidx] + shift_x[nidx],
            nodes_y[nidx] + shift_y[nidx],
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
        context.parent,
        "g",
        id=context.get_id(mark),
        attrib={"class": "toytree-Annotation-Rect"},
        style=concat_style_fix_color(mark.style),
    )

    # project coordinates from data units to px units
    left_x = axes.project("x", mark.xtable[:, 0])
    right_x = axes.project("x", mark.xtable[:, 1])
    top_y = axes.project("y", mark.ytable[:, 0])
    bot_y = axes.project("y", mark.ytable[:, 1])

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
            style = concat_style_fix_color(
                {
                    "fill": None if mark.colors is None else mark.colors[nidx],
                    "fill-opacity": None
                    if mark.opacity is None
                    else mark.opacity[nidx],
                }
            )
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
                    LinearGradientStop(
                        offset="0%", color=ToyColor(mark.start_colors[idx]).rgb_css
                    ),
                    LinearGradientStop(
                        offset="100%", color=ToyColor(mark.end_colors[idx]).rgb_css
                    ),
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

        # Per-edge opacity is emitted as an SVG attribute for gradient paths.
        path_attrib: dict[str, str] = {}
        if (not mark.use_group_opacity) and np.isfinite(mark.opacity[idx]):
            path_attrib["opacity"] = f"{mark.opacity[idx]:.8g}"

        # create path element using defined gradient color
        xml.SubElement(
            group_xml,
            "path",
            id=f"GradientLine-{idx}",
            d=path,
            stroke=refs[f"g{short_mark_id}-{idx}"],
            style=concat_style_fix_color(path_style),
            **path_attrib,
        )


def render_stochastic_map_lines(
    axes: Cartesian,
    mark: AnnotationStochasticMapLine,
    context: toyplot.html.RenderContext,
) -> None:
    """Render stochastic-map polyline segments with per-segment colors."""
    render_lines(axes, mark, context)


def render_tip_tiles(
    axes: Cartesian,
    mark: AnnotationTipTileMark,
    context: toyplot.html.RenderContext,
) -> None:
    """Render tip tile path annotations from data-space coords + px parameters."""
    tips_x_px = axes.project("x", mark.ntable[:, 0])
    tips_y_px = axes.project("y", mark.ntable[:, 1])

    if mark.layout in ("r", "l", "u", "d"):
        paths_all, slot_min_all, slot_max_all = _build_rectangular_tile_paths_px(
            tips_x_px=tips_x_px,
            tips_y_px=tips_y_px,
            layout=mark.layout,
            offset=float(mark.offset),
            depth=float(mark.depth),
        )
        slot_kind = "span"
    else:
        root_x_px = float(axes.project("x", float(mark.root_xy[0])))
        root_y_px = float(axes.project("y", float(mark.root_xy[1])))
        _, _, _, is_full_circle = _parse_circular_layout(mark.layout)
        paths_all, slot_min_all, slot_max_all = _build_circular_tile_paths_px(
            tips_x_px=tips_x_px,
            tips_y_px=tips_y_px,
            root_x_px=root_x_px,
            root_y_px=root_y_px,
            wrap=is_full_circle,
            offset=float(mark.offset),
            depth=float(mark.depth),
        )
        slot_kind = "angle"

    tip_indices = np.where(mark.show)[0].astype(int)
    paths = [paths_all[i] for i in tip_indices]
    slot_min = slot_min_all[tip_indices]
    slot_max = slot_max_all[tip_indices]

    # Persist computed geometry for tests / introspection.
    mark.tip_indices = tip_indices
    mark.paths = paths
    mark.slot_min = slot_min
    mark.slot_max = slot_max
    mark.slot_kind = slot_kind

    group_xml = xml.SubElement(
        context.parent,
        "g",
        id=context.get_id(mark),
        attrib={"class": "toytree-Annotation-TipTiles"},
        style=concat_style_fix_color(mark.style),
    )

    for idx, path in enumerate(paths):
        path_style = dict(mark.style)
        if mark.colors is None:
            color = mark.fill_color
        else:
            color = ToyColor(mark.colors[tip_indices[idx]])
        path_style["fill"] = color.rgb
        path_style["fill-opacity"] = float(mark.opacity[tip_indices[idx]])
        xml.SubElement(
            group_xml,
            "path",
            id=f"TipTile-{idx}",
            d=path,
            style=concat_style_fix_color(path_style),
        )


def render_tip_bars(
    axes: Cartesian,
    mark: AnnotationTipBarMark,
    context: toyplot.html.RenderContext,
) -> None:
    """Render tip bar path annotations from data-space coords + px parameters."""
    tips_x_px = axes.project("x", mark.ntable[:, 0])
    tips_y_px = axes.project("y", mark.ntable[:, 1])

    if mark.layout in ("r", "l", "u", "d"):
        (
            paths_all,
            slot_min_all,
            slot_max_all,
            occupied_min_all,
            occupied_max_all,
        ) = _build_rectangular_bar_paths_px(
            tips_x_px=tips_x_px,
            tips_y_px=tips_y_px,
            layout=mark.layout,
            offset=float(mark.offset),
            widths=np.asarray(mark.bar_depths, dtype=float),
            fill_width=float(mark.width),
        )
        slot_kind = "span"
    else:
        root_x_px = float(axes.project("x", float(mark.root_xy[0])))
        root_y_px = float(axes.project("y", float(mark.root_xy[1])))
        _, _, _, is_full_circle = _parse_circular_layout(mark.layout)
        (
            paths_all,
            slot_min_all,
            slot_max_all,
            occupied_min_all,
            occupied_max_all,
        ) = _build_circular_bar_paths_px(
            tips_x_px=tips_x_px,
            tips_y_px=tips_y_px,
            root_x_px=root_x_px,
            root_y_px=root_y_px,
            wrap=is_full_circle,
            offset=float(mark.offset),
            depths=np.asarray(mark.bar_depths, dtype=float),
            fill_width=float(mark.width),
        )
        slot_kind = "angle"

    tip_indices = np.where(mark.show)[0].astype(int)
    paths = [paths_all[i] for i in tip_indices]
    slot_min = slot_min_all[tip_indices]
    slot_max = slot_max_all[tip_indices]
    occupied_min = occupied_min_all[tip_indices]
    occupied_max = occupied_max_all[tip_indices]

    mark.tip_indices = tip_indices
    mark.paths = paths
    mark.slot_min = slot_min
    mark.slot_max = slot_max
    mark.occupied_min = occupied_min
    mark.occupied_max = occupied_max
    mark.slot_kind = slot_kind

    group_xml = xml.SubElement(
        context.parent,
        "g",
        id=context.get_id(mark),
        attrib={"class": "toytree-Annotation-TipBars"},
        style=concat_style_fix_color(mark.style),
    )

    for idx, path in enumerate(paths):
        path_style = dict(mark.style)
        if mark.colors is None:
            color = mark.fill_color
        else:
            color = ToyColor(mark.colors[tip_indices[idx]])
        path_style["fill"] = color.rgb
        if mark.opacity is not None:
            path_style["fill-opacity"] = float(mark.opacity[tip_indices[idx]])
        path_xml = xml.SubElement(
            group_xml,
            "path",
            id=f"TipBar-{idx}",
            d=path,
            style=concat_style_fix_color(path_style),
        )
        if mark.hover_labels is not None:
            xml.SubElement(path_xml, "title").text = str(
                mark.hover_labels[tip_indices[idx]]
            )


def _build_rectangular_tip_paths_px(
    start_x_px: np.ndarray,
    start_y_px: np.ndarray,
    end_x_px: np.ndarray,
    end_y_px: np.ndarray,
    layout: str,
    depth_offset: float,
    span_offset: float,
    depths: np.ndarray,
    bezier_fractions: tuple[float, float],
) -> list[str]:
    """Build SVG path strings for rectangular tip-path annotations."""
    paths = []
    depths = np.asarray(depths, dtype=float)
    frac0 = float(bezier_fractions[0])
    frac1 = float(bezier_fractions[1])
    use_line = bool(np.isclose(frac0, 0.0) and np.isclose(frac1, 1.0))

    for idx in range(int(depths.size)):
        if layout == "r":
            start_x = float(start_x_px[idx] + depth_offset)
            start_y = float(start_y_px[idx] + span_offset)
            end_x = float(end_x_px[idx] + depth_offset + depths[idx])
            end_y = float(end_y_px[idx] + span_offset)
            ctrl1_x = float(start_x + (end_x - start_x) * frac0)
            ctrl1_y = start_y
            ctrl2_x = float(start_x + (end_x - start_x) * frac1)
            ctrl2_y = end_y
        elif layout == "l":
            start_x = float(start_x_px[idx] - depth_offset)
            start_y = float(start_y_px[idx] + span_offset)
            end_x = float(end_x_px[idx] - depth_offset - depths[idx])
            end_y = float(end_y_px[idx] + span_offset)
            ctrl1_x = float(start_x + (end_x - start_x) * frac0)
            ctrl1_y = start_y
            ctrl2_x = float(start_x + (end_x - start_x) * frac1)
            ctrl2_y = end_y
        elif layout == "u":
            start_x = float(start_x_px[idx] + span_offset)
            start_y = float(start_y_px[idx] - depth_offset)
            end_x = float(end_x_px[idx] + span_offset)
            end_y = float(end_y_px[idx] - depth_offset - depths[idx])
            ctrl1_x = start_x
            ctrl1_y = float(start_y + (end_y - start_y) * frac0)
            ctrl2_x = end_x
            ctrl2_y = float(start_y + (end_y - start_y) * frac1)
        elif layout == "d":
            start_x = float(start_x_px[idx] + span_offset)
            start_y = float(start_y_px[idx] + depth_offset)
            end_x = float(end_x_px[idx] + span_offset)
            end_y = float(end_y_px[idx] + depth_offset + depths[idx])
            ctrl1_x = start_x
            ctrl1_y = float(start_y + (end_y - start_y) * frac0)
            ctrl2_x = end_x
            ctrl2_y = float(start_y + (end_y - start_y) * frac1)
        else:
            raise ValueError(f"Unsupported tip-path layout: {layout!r}")

        # Control points share the start and end tangents so rectangular tip
        # paths ease out from one span level and ease back into the other.
        if use_line:
            path = f"M {start_x:.8g} {start_y:.8g} " f"L {end_x:.8g} {end_y:.8g}"
        else:
            path = (
                f"M {start_x:.8g} {start_y:.8g} "
                f"C {ctrl1_x:.8g} {ctrl1_y:.8g} "
                f"{ctrl2_x:.8g} {ctrl2_y:.8g} "
                f"{end_x:.8g} {end_y:.8g}"
            )
        paths.append(path)
    return paths


def render_tip_paths(
    axes: Cartesian,
    mark: AnnotationTipPathMark,
    context: toyplot.html.RenderContext,
) -> None:
    """Render rectangular tip-anchored path annotations."""
    tip_indices = np.where(np.asarray(mark.show, dtype=bool))[0].astype(int)
    start_x, start_y, end_x, end_y = mark._get_path_anchor_coords(tip_indices)
    paths = _build_rectangular_tip_paths_px(
        start_x_px=np.asarray(axes.project("x", start_x), dtype=float),
        start_y_px=np.asarray(axes.project("y", start_y), dtype=float),
        end_x_px=np.asarray(axes.project("x", end_x), dtype=float),
        end_y_px=np.asarray(axes.project("y", end_y), dtype=float),
        layout=mark.layout,
        depth_offset=float(mark.depth_offset),
        span_offset=float(mark.span_offset),
        depths=np.asarray(mark.path_depths[tip_indices], dtype=float),
        bezier_fractions=mark.bezier_fractions,
    )

    mark.tip_indices = tip_indices
    mark.paths = paths

    group_xml = xml.SubElement(
        context.parent,
        "g",
        id=context.get_id(mark),
        attrib={"class": "toytree-Annotation-TipPaths"},
    )

    for idx, path in enumerate(paths):
        path_style = dict(mark.style)
        path_style["fill"] = "none"
        path_style.pop("opacity", None)
        if mark.colors is None:
            color = mark.stroke_color
        else:
            color = ToyColor(mark.colors[tip_indices[idx]])
        path_style["stroke"] = color.rgb
        if mark.opacity is not None:
            path_style.pop("stroke-opacity", None)
            path_style["stroke-opacity"] = float(mark.opacity[tip_indices[idx]])
        path_xml = xml.SubElement(
            group_xml,
            "path",
            id=f"TipPath-{idx}",
            d=path,
            style=concat_style_fix_color(path_style),
        )
        if mark.hover_labels is not None:
            xml.SubElement(path_xml, "title").text = str(
                mark.hover_labels[tip_indices[idx]]
            )


def render_tip_labels(
    axes: Cartesian,
    mark: AnnotationTipLabelMark,
    context: toyplot.html.RenderContext,
) -> None:
    """Render tip label annotation text with per-tip style and angle."""
    text_xml = xml.SubElement(
        context.parent,
        "g",
        id=context.get_id(mark),
        attrib={"class": "toytree-Annotation-TipLabels"},
    )

    xpx = axes.project("x", mark.ntable[:, 0])
    ypx = axes.project("y", mark.ntable[:, 1])
    for idx in range(mark.ntable.shape[0]):
        tstyle = dict(mark.styles[idx])
        if mark.colors is not None:
            tstyle["fill"] = ToyColor(mark.colors[idx])
        tstyle["opacity"] = float(mark.opacity[idx])
        render_text(
            root=text_xml,
            text=str(mark.labels[idx]),
            xpos=float(xpx[idx]),
            ypos=float(ypx[idx]),
            angle=float(mark.angles[idx]),
            attributes={"class": "toytree-Annotation-TipLabel"},
            style=tstyle,
        )


def _build_rectangular_tile_paths_px(
    tips_x_px: np.ndarray,
    tips_y_px: np.ndarray,
    layout: str,
    offset: float,
    depth: float,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Build gapless rectangular tile path strings in pixel coordinates."""
    ntips = int(tips_x_px.size)
    if layout in ("r", "l"):
        span = tips_y_px
        sort_idx = np.argsort(span)
        bounds = _midpoint_bounds(span[sort_idx])
        sign = 1.0 if layout == "r" else -1.0

        paths = [""] * ntips
        slot_min = np.zeros(ntips, dtype=float)
        slot_max = np.zeros(ntips, dtype=float)
        for jdx, tidx in enumerate(sort_idx):
            y0 = float(bounds[jdx])
            y1 = float(bounds[jdx + 1])
            slot_min[tidx] = y0
            slot_max[tidx] = y1
            x0 = float(tips_x_px[tidx] + sign * offset)
            x1 = float(x0 + sign * depth)
            paths[tidx] = (
                f"M {x0:.8g} {y0:.8g} "
                f"L {x1:.8g} {y0:.8g} "
                f"L {x1:.8g} {y1:.8g} "
                f"L {x0:.8g} {y1:.8g} Z"
            )
        return paths, slot_min, slot_max

    span = tips_x_px
    sort_idx = np.argsort(span)
    bounds = _midpoint_bounds(span[sort_idx])
    # Pixel-space y increases downward.
    sign = -1.0 if layout == "u" else 1.0

    paths = [""] * ntips
    slot_min = np.zeros(ntips, dtype=float)
    slot_max = np.zeros(ntips, dtype=float)
    for jdx, tidx in enumerate(sort_idx):
        x0 = float(bounds[jdx])
        x1 = float(bounds[jdx + 1])
        slot_min[tidx] = x0
        slot_max[tidx] = x1
        y0 = float(tips_y_px[tidx] + sign * offset)
        y1 = float(y0 + sign * depth)
        paths[tidx] = (
            f"M {x0:.8g} {y0:.8g} "
            f"L {x1:.8g} {y0:.8g} "
            f"L {x1:.8g} {y1:.8g} "
            f"L {x0:.8g} {y1:.8g} Z"
        )
    return paths, slot_min, slot_max


def _build_circular_tile_paths_px(
    tips_x_px: np.ndarray,
    tips_y_px: np.ndarray,
    root_x_px: float,
    root_y_px: float,
    wrap: bool,
    offset: float,
    depth: float,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Build annular-sector tile paths (as polyline approximations) in px."""
    dx = tips_x_px - float(root_x_px)
    dy = tips_y_px - float(root_y_px)
    radii = np.hypot(dx, dy)
    if np.any(radii <= 0.0):
        raise ValueError("tip radii must be positive in circular layout")

    # Use projected coordinates as the geometry source of truth.
    # This avoids mirrored sectors on circular layouts caused by mixing
    # data-space text angles with pixel-space rendering coordinates.
    theta = np.arctan2(dy, dx)

    if wrap:
        # Full-circle layouts are periodic, so use modulo angles.
        theta = np.mod(theta, 2.0 * np.pi)
        order = np.argsort(theta)
        ts = theta[order]
        left, right = _midpoint_bounds_periodic(ts)
    else:
        # Partial fan layouts are open intervals with a missing arc.
        # Determine the seam from geometry: cut at the largest circular gap.
        theta_mod = np.mod(theta, 2.0 * np.pi)
        order0 = np.argsort(theta_mod)
        ts0 = theta_mod[order0]
        gaps = np.diff(np.concatenate([ts0, [ts0[0] + 2.0 * np.pi]]))
        cut = int(np.argmax(gaps))
        start = (cut + 1) % ts0.size
        order = np.roll(order0, -start)
        ts = np.unwrap(theta_mod[order])
        bounds = _midpoint_bounds(ts)
        left = bounds[:-1]
        right = bounds[1:]

    ntips = int(ts.size)

    paths = [""] * ntips
    slot_min = np.zeros(ntips, dtype=float)
    slot_max = np.zeros(ntips, dtype=float)
    for rank, tidx in enumerate(order):
        r_inner = float(radii[tidx] + offset)
        r_outer = float(r_inner + depth)
        if r_inner <= 0.0 or r_outer <= 0.0:
            raise ValueError(
                "offset/depth produce non-positive tile radius in circular layout"
            )

        t0 = float(left[rank])
        t1 = float(right[rank])
        slot_min[tidx] = t0
        slot_max[tidx] = t1
        if wrap and (t1 <= t0):
            t1 += 2.0 * np.pi

        nsteps = max(8, int(np.ceil((t1 - t0) / (np.pi / 18.0))))
        ang = np.linspace(t0, t1, nsteps)
        x_outer = root_x_px + r_outer * np.cos(ang)
        y_outer = root_y_px + r_outer * np.sin(ang)
        x_inner = root_x_px + r_inner * np.cos(ang[::-1])
        y_inner = root_y_px + r_inner * np.sin(ang[::-1])

        parts = [f"M {x_outer[0]:.8g} {y_outer[0]:.8g}"]
        for i in range(1, nsteps):
            parts.append(f"L {x_outer[i]:.8g} {y_outer[i]:.8g}")
        for i in range(nsteps):
            parts.append(f"L {x_inner[i]:.8g} {y_inner[i]:.8g}")
        parts.append("Z")
        paths[tidx] = " ".join(parts)
    return paths, slot_min, slot_max


def _build_rectangular_bar_paths_px(
    tips_x_px: np.ndarray,
    tips_y_px: np.ndarray,
    layout: str,
    offset: float,
    widths: np.ndarray,
    fill_width: float,
) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build tip bar paths in rectangular layouts."""
    ntips = int(tips_x_px.size)
    if layout in ("r", "l"):
        span = tips_y_px
        sort_idx = np.argsort(span)
        bounds = _midpoint_bounds(span[sort_idx])
        sign = 1.0 if layout == "r" else -1.0

        paths = [""] * ntips
        slot_min = np.zeros(ntips, dtype=float)
        slot_max = np.zeros(ntips, dtype=float)
        occupied_min = np.zeros(ntips, dtype=float)
        occupied_max = np.zeros(ntips, dtype=float)
        for jdx, tidx in enumerate(sort_idx):
            y0 = float(bounds[jdx])
            y1 = float(bounds[jdx + 1])
            slot_min[tidx] = y0
            slot_max[tidx] = y1
            oy0, oy1 = _narrow_slot_bounds(y0, y1, fill_width)
            occupied_min[tidx] = oy0
            occupied_max[tidx] = oy1
            x0 = float(tips_x_px[tidx] + sign * offset)
            x1 = float(x0 + sign * widths[tidx])
            paths[tidx] = (
                f"M {x0:.8g} {oy0:.8g} "
                f"L {x1:.8g} {oy0:.8g} "
                f"L {x1:.8g} {oy1:.8g} "
                f"L {x0:.8g} {oy1:.8g} Z"
            )
        return paths, slot_min, slot_max, occupied_min, occupied_max

    span = tips_x_px
    sort_idx = np.argsort(span)
    bounds = _midpoint_bounds(span[sort_idx])
    sign = -1.0 if layout == "u" else 1.0

    paths = [""] * ntips
    slot_min = np.zeros(ntips, dtype=float)
    slot_max = np.zeros(ntips, dtype=float)
    occupied_min = np.zeros(ntips, dtype=float)
    occupied_max = np.zeros(ntips, dtype=float)
    for jdx, tidx in enumerate(sort_idx):
        x0 = float(bounds[jdx])
        x1 = float(bounds[jdx + 1])
        slot_min[tidx] = x0
        slot_max[tidx] = x1
        ox0, ox1 = _narrow_slot_bounds(x0, x1, fill_width)
        occupied_min[tidx] = ox0
        occupied_max[tidx] = ox1
        y0 = float(tips_y_px[tidx] + sign * offset)
        y1 = float(y0 + sign * widths[tidx])
        paths[tidx] = (
            f"M {ox0:.8g} {y0:.8g} "
            f"L {ox1:.8g} {y0:.8g} "
            f"L {ox1:.8g} {y1:.8g} "
            f"L {ox0:.8g} {y1:.8g} Z"
        )
    return paths, slot_min, slot_max, occupied_min, occupied_max


def _build_circular_bar_paths_px(
    tips_x_px: np.ndarray,
    tips_y_px: np.ndarray,
    root_x_px: float,
    root_y_px: float,
    wrap: bool,
    offset: float,
    depths: np.ndarray,
    fill_width: float,
) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build tip bar paths in circular layouts."""
    dx = tips_x_px - float(root_x_px)
    dy = tips_y_px - float(root_y_px)
    radii = np.hypot(dx, dy)
    if np.any(radii <= 0.0):
        raise ValueError("tip radii must be positive in circular layout")

    theta = np.arctan2(dy, dx)

    if wrap:
        theta = np.mod(theta, 2.0 * np.pi)
        order = np.argsort(theta)
        ts = theta[order]
        left, right = _midpoint_bounds_periodic(ts)
    else:
        theta_mod = np.mod(theta, 2.0 * np.pi)
        order0 = np.argsort(theta_mod)
        ts0 = theta_mod[order0]
        gaps = np.diff(np.concatenate([ts0, [ts0[0] + 2.0 * np.pi]]))
        cut = int(np.argmax(gaps))
        start = (cut + 1) % ts0.size
        order = np.roll(order0, -start)
        ts = np.unwrap(theta_mod[order])
        bounds = _midpoint_bounds(ts)
        left = bounds[:-1]
        right = bounds[1:]

    ntips = int(ts.size)
    paths = [""] * ntips
    slot_min = np.zeros(ntips, dtype=float)
    slot_max = np.zeros(ntips, dtype=float)
    occupied_min = np.zeros(ntips, dtype=float)
    occupied_max = np.zeros(ntips, dtype=float)
    for rank, tidx in enumerate(order):
        t0 = float(left[rank])
        t1 = float(right[rank])
        slot_min[tidx] = t0
        slot_max[tidx] = t1
        o0, o1 = _narrow_slot_bounds(t0, t1, fill_width)
        occupied_min[tidx] = o0
        occupied_max[tidx] = o1

        r_inner = float(radii[tidx] + offset)
        r_outer = float(r_inner + depths[tidx])
        if r_inner <= 0.0 or r_outer <= 0.0:
            raise ValueError(
                "offset/depth produce non-positive bar radius in circular layout"
            )

        nsteps = max(8, int(np.ceil((o1 - o0) / (np.pi / 18.0))))
        ang = np.linspace(o0, o1, nsteps)
        x_outer = root_x_px + r_outer * np.cos(ang)
        y_outer = root_y_px + r_outer * np.sin(ang)
        x_inner = root_x_px + r_inner * np.cos(ang[::-1])
        y_inner = root_y_px + r_inner * np.sin(ang[::-1])

        parts = [f"M {x_outer[0]:.8g} {y_outer[0]:.8g}"]
        for idx in range(1, nsteps):
            parts.append(f"L {x_outer[idx]:.8g} {y_outer[idx]:.8g}")
        for idx in range(nsteps):
            parts.append(f"L {x_inner[idx]:.8g} {y_inner[idx]:.8g}")
        parts.append("Z")
        paths[tidx] = " ".join(parts)
    return paths, slot_min, slot_max, occupied_min, occupied_max


def _narrow_slot_bounds(
    slot_min: float, slot_max: float, fill_width: float
) -> tuple[float, float]:
    """Return centered occupied bounds within a full slot."""
    center = 0.5 * (slot_min + slot_max)
    half = 0.5 * fill_width * (slot_max - slot_min)
    return center - half, center + half


def _midpoint_bounds(values: np.ndarray) -> np.ndarray:
    """Return slot boundaries from sorted center positions."""
    nvals = int(values.size)
    if nvals == 1:
        span = 1.0
        return np.array([values[0] - 0.5 * span, values[0] + 0.5 * span], dtype=float)

    bounds = np.zeros(nvals + 1, dtype=float)
    bounds[1:-1] = 0.5 * (values[:-1] + values[1:])
    bounds[0] = values[0] - 0.5 * (values[1] - values[0])
    bounds[-1] = values[-1] + 0.5 * (values[-1] - values[-2])
    return bounds


def _midpoint_bounds_periodic(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return periodic midpoint bounds for sorted circular values."""
    nvals = int(values.size)
    left = np.zeros(nvals, dtype=float)
    right = np.zeros(nvals, dtype=float)
    for idx in range(nvals):
        prev_idx = (idx - 1) % nvals
        next_idx = (idx + 1) % nvals
        dprev = (values[idx] - values[prev_idx]) % (2.0 * np.pi)
        dnext = (values[next_idx] - values[idx]) % (2.0 * np.pi)
        left[idx] = values[idx] - 0.5 * dprev
        right[idx] = values[idx] + 0.5 * dnext
    return left, right


if __name__ == "__main__":
    import toytree

    # base tree drawing
    tree = toytree.rtree.unittree(15)
    c, a, m = tree.draw(layout="d", scale_bar=True, node_sizes=5, node_colors="black")

    m1 = tree.annotate.add_node_bars(
        a,
        bar_min=tree.get_node_data("height").values * 0.8,
        bar_max=tree.get_node_data("height").values * 1.25,
        size=0.3,
        style={"fill-opacity": 0.4, "stroke": None},
        z_index=-1,
        color="red",
    )
    toytree.utils.show(c)
