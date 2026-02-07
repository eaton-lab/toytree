#!/usr/bin/env python

"""Helpers for placing and resizing images on a Toyplot canvas."""

"""Helpers for placing and resizing images on a Toyplot canvas."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Tuple

import numpy as np
import requests
import toyplot
from PIL import Image
from toyplot.html import RenderContext, dispatch, xml


def generate_example_image(width: int = 96, height: int = 96) -> np.ndarray:
    """Create a small RGB gradient image as a demo placeholder.

    Parameters
    ----------
    width : int
        Image width in pixels.
    height : int
        Image height in pixels.

    Returns
    -------
    numpy.ndarray
        A (height, width, 3) float array in the range [0, 1].
    """
    x = np.linspace(0.0, 1.0, width)
    y = np.linspace(0.0, 1.0, height)
    xv, yv = np.meshgrid(x, y)
    red = xv
    green = yv
    blue = 0.3 * np.ones_like(xv)
    return np.dstack((red, green, blue))


@dataclass(frozen=True)
class FetchedImage:
    """Container for fetched image bytes and metadata."""

    data: bytes
    format: str
    content_type: str | None


@dataclass(frozen=True)
class SvgMark(toyplot.mark.Mark):
    """Render SVG content directly onto a Toyplot canvas."""

    svg_text: str
    xmin: float
    ymin: float
    width: float
    height: float


@dispatch(SvgMark, RenderContext)
def _render(mark: SvgMark, context: RenderContext) -> None:
    mark_xml = xml.SubElement(
        context.parent,
        "g",
        id=context.get_id(mark),
        attrib={"class": "toyplot-mark-SVG"},
    )
    svg_element = xml.fromstring(mark.svg_text)
    svg_element.set("x", str(mark.xmin))
    svg_element.set("y", str(mark.ymin))
    svg_element.set("width", str(mark.width))
    svg_element.set("height", str(mark.height))
    svg_element.set("preserveAspectRatio", "xMidYMid meet")
    mark_xml.append(svg_element)


def _detect_image_format(data: bytes, content_type: str | None) -> str:
    if content_type:
        normalized = content_type.split(";")[0].strip().lower()
        if normalized == "image/png":
            return "png"
        if normalized in {"image/svg+xml", "image/svg"}:
            return "svg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    probe = data[:1024].lstrip()
    if probe.startswith(b"<svg") or b"<svg" in probe or probe.startswith(b"<?xml"):
        if b"<svg" in probe:
            return "svg"
    raise ValueError("Unsupported image format; expected PNG or SVG.")


def fetch_image_from_url(url: str, *, timeout: float = 10) -> FetchedImage:
    """Fetch an image and return a container with detected format."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    content_type = response.headers.get("content-type")
    data = response.content
    image_format = _detect_image_format(data, content_type)
    return FetchedImage(data=data, format=image_format, content_type=content_type)


def _convert_svg_to_png_bytes(data: bytes, *, scale: float = 1.0) -> bytes:
    try:
        import cairosvg
    except ImportError as exc:
        raise ImportError(
            "SVG conversion requires cairosvg. Install with `pip install cairosvg`."
        ) from exc
    return cairosvg.svg2png(bytestring=data, scale=scale)


def image_to_array(image: np.ndarray | FetchedImage, *, svg_scale: float = 1.0) -> np.ndarray:
    """Convert a fetched PNG/SVG or numpy array into an image array."""
    if isinstance(image, FetchedImage):
        data = image.data
        if image.format == "svg":
            data = _convert_svg_to_png_bytes(data, scale=svg_scale)
        pil_image = Image.open(BytesIO(data)).convert("RGBA")
        return np.asarray(pil_image)
    return image


def place_svg_on_canvas(
    canvas: toyplot.Canvas,
    svg: str | bytes | FetchedImage,
    *,
    x: float = 50,
    y: float = 50,
    width: float = 120,
    height: float = 120,
) -> SvgMark:
    """Place an SVG directly into the canvas XML."""
    if isinstance(svg, FetchedImage):
        if svg.format != "svg":
            raise ValueError("Expected an SVG image to render as XML.")
        svg_text = svg.data.decode("utf-8")
    elif isinstance(svg, bytes):
        svg_text = svg.decode("utf-8")
    else:
        svg_text = svg
    mark = SvgMark(svg_text=svg_text, xmin=x, ymin=y, width=width, height=height)
    canvas._scenegraph.add_edge(canvas, "render", mark)
    return mark


def place_image_on_canvas(
    canvas: toyplot.Canvas,
    image: np.ndarray | FetchedImage,
    *,
    x: float = 50,
    y: float = 50,
    width: float = 120,
    height: float = 120,
    svg_scale: float = 1.0,
) -> toyplot.mark.Image:
    """Place an image at a position and size on a Toyplot canvas.

    Parameters
    ----------
    canvas : toyplot.Canvas
        Canvas to receive the image.
    image : numpy.ndarray or FetchedImage
        RGB/RGBA image data, or a fetched PNG/SVG image.
    x, y : float
        Upper-left corner position in canvas coordinates (pixels by default).
    width, height : float
        Image size in canvas units (pixels by default).
    svg_scale : float
        Scale factor applied when rasterizing SVG images.

    Returns
    -------
    toyplot.mark.Image
        The image mark added to the canvas.
    """
    image_data = image_to_array(image, svg_scale=svg_scale)
    return canvas.image(data=image_data, rect=(x, y, width, height))


def minimal_working_example(
    *,
    canvas_size: Tuple[int, int] = (400, 300),
    image_size: Tuple[int, int] = (140, 140),
    image_position: Tuple[int, int] = (40, 60),
) -> Tuple[toyplot.Canvas, toyplot.mark.Image]:
    """Build a minimal canvas with a movable/resizable image.

    Adjust ``image_size`` and ``image_position`` to resize and reposition the
    image on the canvas.
    """
    canvas = toyplot.Canvas(width=canvas_size[0], height=canvas_size[1])
    image = generate_example_image(width=image_size[0], height=image_size[1])
    mark = place_image_on_canvas(
        canvas,
        image,
        x=image_position[0],
        y=image_position[1],
        width=image_size[0],
        height=image_size[1],
    )
    return canvas, mark


def svg_embed_example(
    url: str,
    *,
    canvas_size: Tuple[int, int] = (400, 300),
    image_size: Tuple[int, int] = (140, 140),
    image_position: Tuple[int, int] = (40, 60),
) -> Tuple[toyplot.Canvas, SvgMark]:
    """Fetch an SVG and embed it directly in the canvas XML."""
    canvas = toyplot.Canvas(width=canvas_size[0], height=canvas_size[1])
    svg_image = fetch_image_from_url(url)
    mark = place_svg_on_canvas(
        canvas,
        svg_image,
        x=image_position[0],
        y=image_position[1],
        width=image_size[0],
        height=image_size[1],
    )
    return canvas, mark
