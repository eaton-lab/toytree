#!/usr/bin/env python

"""Runtime compatibility patch for Toyplot's ReportLab PDF renderer.

This module vendors the current upstream ``toyplot.reportlab.render`` logic
and extends only the SVG ``<path>`` branch to support absolute cubic Bezier
commands (``C``). ToyTree's tip-path annotations emit cubic SVG paths, and
Toyplot's current ReportLab translator drops those segments during PDF export.
"""

from __future__ import annotations

import base64
import inspect
import io
import re

import reportlab.lib.colors
import reportlab.lib.utils
import toyplot.color
import toyplot.reportlab
import toyplot.units
from toyplot.require import as_float


def _render_with_cubic_paths(svg, canvas):
    """Render SVG to a ReportLab canvas with cubic ``<path>`` support."""

    def get_fill(root, style):
        if "fill" not in style:
            return None, None  # pragma: no cover

        gradient_id = re.match(r"^url[(]#(.*)[)]$", style["fill"])
        if gradient_id:
            gradient_id = gradient_id.group(1)
            gradient_xml = root.find(f".//*[@id='{gradient_id}']")
            if gradient_xml.tag != "linearGradient":
                raise NotImplementedError(
                    "Only linear gradients are implemented."
                )  # pragma: no cover
            if gradient_xml.get("gradientUnits") != "userSpaceOnUse":
                raise NotImplementedError(
                    "Only userSpaceOnUse gradients are implemented."
                )  # pragma: no cover
            return None, gradient_xml

        color = toyplot.color.css(style["fill"])
        if color is None:
            return None, None

        fill_opacity = as_float(style.get("fill-opacity", 1.0))
        opacity = as_float(style.get("opacity", 1.0))
        fill = toyplot.color.rgba(
            color["r"],
            color["g"],
            color["b"],
            color["a"] * fill_opacity * opacity,
        )
        return fill, None

    def get_stroke(style):
        if "stroke" not in style:
            return None  # pragma: no cover

        color = toyplot.color.css(style["stroke"])
        if color is None:
            return None

        stroke_opacity = as_float(style.get("stroke-opacity", 1.0))
        opacity = as_float(style.get("opacity", 1.0))
        return toyplot.color.rgba(
            color["r"],
            color["g"],
            color["b"],
            color["a"] * stroke_opacity * opacity,
        )

    def get_line_cap(style):
        if "stroke-linecap" not in style:
            return 0
        elif style["stroke-linecap"] == "butt":
            return 0
        elif style["stroke-linecap"] == "round":
            return 1
        elif style["stroke-linecap"] == "square":
            return 2

    def get_font_family(style):
        if "font-family" not in style:
            return None  # pragma: no cover

        bold = style.get("font-weight", "") == "bold"
        italic = style.get("font-style", "") == "italic"
        for font_family in style["font-family"].split(","):
            font_family = font_family.lower()
            if font_family in get_font_family.substitutions:
                font_family = get_font_family.substitutions[font_family]
                return get_font_family.font_table[(font_family, bold, italic)]

        raise ValueError(
            f"Unknown font family: {style['font-family']}"
        )  # pragma: no cover

    get_font_family.font_table = {
        ("courier", False, False): "Courier",
        ("courier", True, False): "Courier-Bold",
        ("courier", False, True): "Courier-Oblique",
        ("courier", True, True): "Courier-BoldOblique",
        ("helvetica", False, False): "Helvetica",
        ("helvetica", True, False): "Helvetica-Bold",
        ("helvetica", False, True): "Helvetica-Oblique",
        ("helvetica", True, True): "Helvetica-BoldOblique",
        ("times", False, False): "Times-Roman",
        ("times", True, False): "Times-Bold",
        ("times", False, True): "Times-Italic",
        ("times", True, True): "Times-BoldItalic",
    }

    get_font_family.substitutions = {
        "courier": "courier",
        "helvetica": "helvetica",
        "monospace": "courier",
        "sans-serif": "helvetica",
        "serif": "times",
        "times": "times",
    }

    def set_fill_color(target_canvas, color):
        target_canvas.setFillColorRGB(color["r"], color["g"], color["b"])
        target_canvas.setFillAlpha(color["a"].item())

    def set_stroke_color(target_canvas, color):
        target_canvas.setStrokeColorRGB(color["r"], color["g"], color["b"])
        target_canvas.setStrokeAlpha(color["a"].item())

    def draw_svg_path(path_object, commands):
        # Tip-path annotations emit absolute M/C path commands with whitespace
        # separators, so matching Toyplot's simple token parser is sufficient.
        while commands:
            command = commands.pop(0)
            if command == "L":
                path_object.lineTo(
                    as_float(commands.pop(0)),
                    as_float(commands.pop(0)),
                )
            elif command == "M":
                path_object.moveTo(
                    as_float(commands.pop(0)),
                    as_float(commands.pop(0)),
                )
            elif command == "C":
                path_object.curveTo(
                    as_float(commands.pop(0)),
                    as_float(commands.pop(0)),
                    as_float(commands.pop(0)),
                    as_float(commands.pop(0)),
                    as_float(commands.pop(0)),
                    as_float(commands.pop(0)),
                )
            elif command in ("Z", "z"):
                path_object.close()

    def render_element(root, element, target_canvas, styles):
        target_canvas.saveState()

        current_style = {}
        if styles:
            current_style.update(styles[-1])
        for declaration in element.get("style", "").split(";"):
            if declaration == "":
                continue
            key, value = declaration.split(":")
            current_style[key] = value
        styles.append(current_style)

        if "stroke-width" in current_style:
            target_canvas.setLineWidth(as_float(current_style["stroke-width"]))

        if "stroke-dasharray" in current_style:
            target_canvas.setDash(
                [
                    as_float(length)
                    for length in current_style["stroke-dasharray"].split(",")
                ]
            )

        if current_style.get("visibility") != "hidden":
            if "transform" in element.attrib:
                for transformation in element.get("transform").split(")")[::1]:
                    if transformation:
                        transform, arguments = transformation.split("(")
                        arguments = arguments.split(",")
                        if transform.strip() == "translate":
                            if len(arguments) == 2:
                                target_canvas.translate(
                                    as_float(arguments[0]),
                                    as_float(arguments[1]),
                                )
                        elif transform.strip() == "rotate":
                            if len(arguments) == 1:
                                target_canvas.rotate(as_float(arguments[0]))
                            if len(arguments) == 3:
                                target_canvas.translate(
                                    as_float(arguments[1]),
                                    as_float(arguments[2]),
                                )
                                target_canvas.rotate(as_float(arguments[0]))
                                target_canvas.translate(
                                    -as_float(arguments[1]),
                                    -as_float(arguments[2]),
                                )

            if element.tag == "svg":
                if "background-color" in current_style:
                    set_fill_color(
                        target_canvas,
                        toyplot.color.css(current_style["background-color"]),
                    )
                    target_canvas.rect(
                        0,
                        0,
                        as_float(element.get("width")[:-2]),
                        as_float(element.get("height")[:-2]),
                        stroke=0,
                        fill=1,
                    )

                if current_style["border-style"] != "none":
                    set_stroke_color(
                        target_canvas,
                        toyplot.color.css(current_style["border-color"]),
                    )
                    target_canvas.setLineWidth(as_float(current_style["border-width"]))
                    target_canvas.rect(
                        0,
                        0,
                        as_float(element.get("width")[:-2]),
                        as_float(element.get("height")[:-2]),
                        stroke=1,
                        fill=0,
                    )

                for child in element:
                    render_element(root, child, target_canvas, styles)

            elif element.tag == "a":
                for child in element:
                    render_element(root, child, target_canvas, styles)

            elif element.tag == "g":
                if element.get("clip-path", None) is not None:
                    clip_id = element.get("clip-path")[5:-1]
                    clip_path = root.find(f".//*[@id='{clip_id}']")
                    for child in clip_path:
                        if child.tag == "rect":
                            x = as_float(child.get("x"))
                            y = as_float(child.get("y"))
                            width = as_float(child.get("width"))
                            height = as_float(child.get("height"))
                            path = target_canvas.beginPath()
                            path.moveTo(x, y)
                            path.lineTo(x + width, y)
                            path.lineTo(x + width, y + height)
                            path.lineTo(x, y + height)
                            path.close()
                            target_canvas.clipPath(path, stroke=0, fill=1)
                        else:
                            raise NotImplementedError(
                                f"Unhandled clip tag: {child.tag}"
                            )  # pragma: no cover

                for child in element:
                    render_element(root, child, target_canvas, styles)

            elif element.tag == "clipPath":
                pass

            elif element.tag == "line":
                stroke = get_stroke(current_style)
                if stroke is not None:
                    set_stroke_color(target_canvas, stroke)
                    target_canvas.setLineCap(get_line_cap(current_style))
                    target_canvas.line(
                        as_float(element.get("x1", 0)),
                        as_float(element.get("y1", 0)),
                        as_float(element.get("x2", 0)),
                        as_float(element.get("y2", 0)),
                    )
            elif element.tag == "path":
                stroke = get_stroke(current_style)
                if stroke is not None:
                    set_stroke_color(target_canvas, stroke)
                    target_canvas.setLineCap(get_line_cap(current_style))
                    path = target_canvas.beginPath()
                    draw_svg_path(path, element.get("d").split())
                    target_canvas.drawPath(path)
            elif element.tag == "polygon":
                fill, fill_gradient = get_fill(root, current_style)
                if fill_gradient is not None:
                    raise NotImplementedError(
                        "Gradient <polygon> not implemented."
                    )  # pragma: no cover
                if fill is not None:
                    set_fill_color(target_canvas, fill)
                stroke = get_stroke(current_style)
                if stroke is not None:
                    set_stroke_color(target_canvas, stroke)

                points = [point.split(",") for point in element.get("points").split()]
                path = target_canvas.beginPath()
                for point in points[:1]:
                    path.moveTo(as_float(point[0]), as_float(point[1]))
                for point in points[1:]:
                    path.lineTo(as_float(point[0]), as_float(point[1]))
                path.close()
                target_canvas.drawPath(
                    path,
                    stroke=stroke is not None,
                    fill=fill is not None,
                )
            elif element.tag == "rect":
                fill, fill_gradient = get_fill(root, current_style)
                if fill is not None:
                    set_fill_color(target_canvas, fill)
                stroke = get_stroke(current_style)
                if stroke is not None:
                    set_stroke_color(target_canvas, stroke)

                x = as_float(element.get("x", 0))
                y = as_float(element.get("y", 0))
                width = as_float(element.get("width"))
                height = as_float(element.get("height"))

                path = target_canvas.beginPath()
                path.moveTo(x, y)
                path.lineTo(x + width, y)
                path.lineTo(x + width, y + height)
                path.lineTo(x, y + height)
                path.close()

                if fill_gradient is not None:
                    pdf_colors = []
                    pdf_offsets = []
                    for stop in fill_gradient:
                        offset = as_float(stop.get("offset"))
                        color = toyplot.color.css(stop.get("stop-color"))
                        opacity = as_float(stop.get("stop-opacity"))
                        pdf_colors.append(
                            reportlab.lib.colors.Color(
                                color["r"],
                                color["g"],
                                color["b"],
                                color["a"] * opacity,
                            )
                        )
                        pdf_offsets.append(offset)
                    target_canvas.saveState()
                    target_canvas.clipPath(path, stroke=0, fill=1)
                    target_canvas.setFillAlpha(1)
                    target_canvas.linearGradient(
                        as_float(fill_gradient.get("x1")),
                        as_float(fill_gradient.get("y1")),
                        as_float(fill_gradient.get("x2")),
                        as_float(fill_gradient.get("y2")),
                        pdf_colors,
                        pdf_offsets,
                    )
                    target_canvas.restoreState()

                target_canvas.drawPath(
                    path,
                    stroke=stroke is not None,
                    fill=fill is not None,
                )
            elif element.tag == "circle":
                fill, fill_gradient = get_fill(root, current_style)
                if fill_gradient is not None:
                    raise NotImplementedError(
                        "Gradient <circle> not implemented."
                    )  # pragma: no cover
                if fill is not None:
                    set_fill_color(target_canvas, fill)
                stroke = get_stroke(current_style)
                if stroke is not None:
                    set_stroke_color(target_canvas, stroke)

                cx = as_float(element.get("cx", 0))
                cy = as_float(element.get("cy", 0))
                radius = as_float(element.get("r"))
                target_canvas.circle(
                    cx,
                    cy,
                    radius,
                    stroke=stroke is not None,
                    fill=fill is not None,
                )
            elif element.tag == "text":
                x = as_float(element.get("x", 0))
                y = as_float(element.get("y", 0))
                fill, fill_gradient = get_fill(element, current_style)
                stroke = get_stroke(current_style)
                font_family = get_font_family(current_style)
                font_size = toyplot.units.convert(
                    current_style["font-size"],
                    target="px",
                )
                text = element.text

                target_canvas.saveState()
                target_canvas.setFont(font_family, font_size)
                if fill is not None:
                    set_fill_color(target_canvas, fill)
                if stroke is not None:
                    set_stroke_color(target_canvas, stroke)
                target_canvas.translate(x, y)
                target_canvas.scale(1, -1)
                target_canvas.drawString(0, 0, text)
                target_canvas.restoreState()

            elif element.tag == "image":
                import PIL.Image

                image = element.get("xlink:href")
                if not image.startswith("data:image/png;base64,"):
                    raise ValueError("Unsupported image type.")  # pragma: no cover
                image = base64.standard_b64decode(image[22:])
                image = io.BytesIO(image)
                image = PIL.Image.open(image)
                image = reportlab.lib.utils.ImageReader(image)

                x = as_float(element.get("x", 0))
                y = as_float(element.get("y", 0))
                width = as_float(element.get("width"))
                height = as_float(element.get("height"))

                target_canvas.saveState()
                set_fill_color(target_canvas, toyplot.color.rgb(1, 1, 1))
                target_canvas.rect(x, y, width, height, stroke=0, fill=1)
                target_canvas.translate(x, y + height)
                target_canvas.scale(1, -1)
                target_canvas.drawImage(
                    image=image,
                    x=0,
                    y=0,
                    width=width,
                    height=height,
                    mask=None,
                )
                target_canvas.restoreState()

            elif element.tag in ["defs", "title"]:
                pass

            else:
                raise Exception(f"unhandled tag: {element.tag}")  # pragma: no cover

        styles.pop()
        target_canvas.restoreState()

    render_element(svg, svg, canvas, [])


def install_pdf_render_patch() -> None:
    """Install the cubic-path ReportLab patch once per Python process."""
    if getattr(toyplot.reportlab.render, "_toytree_cubic_patch", False):
        return

    try:
        source = inspect.getsource(toyplot.reportlab.render)
    except (OSError, TypeError):  # pragma: no cover
        source = ""
    if ("curveTo(" in source) or ('command == "C"' in source):
        return

    original = toyplot.reportlab.render
    _render_with_cubic_paths._toytree_cubic_patch = True
    _render_with_cubic_paths._toytree_original = original
    toyplot.reportlab.render = _render_with_cubic_paths
