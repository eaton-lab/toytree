#!/usr/bin/env python

"""Save canvas to file rendered as HTML, SVG, PDF, or PNG."""

from __future__ import annotations

import importlib
import sys
import xml.etree.ElementTree as xml
from collections.abc import Callable, Iterator, MutableMapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Union

SUFFIXES = (".html", ".svg", ".pdf", ".png")
PDF_PNG_SUFFIXES = (".pdf", ".png")
PDF_PNG_BACKENDS = ("auto", "cairosvg", "reportlab")


def save(
    canvas: Any,
    path: Union[str, Path],
    *,
    backend: str = "auto",
    dpi: float = 96,
    scale: float = 1.0,
    background_color: str | None = None,
    output_width: int | None = None,
    output_height: int | None = None,
) -> None:
    """Save a canvas to HTML, SVG, PDF, or PNG.

    Parameters
    ----------
    canvas : toyplot.Canvas
        A canvas object created from a Toyplot or ToyTree drawing.
    path : str | Path
        Filepath where output will be written. If no filename suffix is
        provided then ``.html`` is appended by default.
    backend : str
        Export backend for ``.pdf`` and ``.png`` outputs. Options are
        ``"auto"``, ``"cairosvg"``, and ``"reportlab"``. The default
        uses CairoSVG when available and otherwise falls back to the
        legacy ReportLab path. This option is ignored for HTML and SVG.
    dpi : float
        Rasterization DPI passed to CairoSVG for PDF and PNG export.
    scale : float
        Scaling factor passed to CairoSVG for PDF and PNG export.
    background_color : str or None
        Optional CSS color override applied during export only. If None,
        the canvas background is preserved.
    output_width : int or None
        Optional output width in pixels passed through to CairoSVG.
    output_height : int or None
        Optional output height in pixels passed through to CairoSVG.

    Raises
    ------
    TypeError
        If ``canvas`` does not look like a Toyplot canvas object.
    OSError
        If the filename suffix is not recognized.
    ValueError
        If ``backend`` is invalid or requested for HTML / SVG export.
    ImportError
        If ``backend="cairosvg"`` is requested and CairoSVG is unavailable.

    Notes
    -----
    SVG is treated as the canonical vector representation for PDF and PNG
    export. When CairoSVG is available it is used to convert SVG output
    into PDF and PNG, which gives better support for filled paths,
    gradients, clipping, and transforms than the legacy ReportLab path.

    The ``reportlab`` backend remains available as a fallback for simple
    figures or environments without CairoSVG, but it may not render all
    SVG features correctly. A warning is printed to stderr when known
    unsupported features are detected.

    Example
    -------
    >>> tree = toytree.rtree.coaltree(10)
    >>> canvas, axes, mark = tree.draw(ts='c')
    >>> toytree.save(canvas, "./drawing.pdf")
    >>> toytree.save(canvas, "./drawing.png", output_width=1600)
    """
    _validate_canvas_like(canvas)
    output_path, suffix = _normalize_output_path(path)
    _validate_backend(backend, suffix)

    if suffix in (".html", ".svg"):
        renderer = _get_renderer_for_suffix(suffix)
        with _temporary_canvas_background(canvas, background_color):
            renderer(canvas, str(output_path))
        return

    selected_backend, cairosvg_module, auto_fallback = _select_pdf_png_backend(backend)
    if selected_backend == "cairosvg":
        _render_pdf_png_with_cairosvg(
            canvas=canvas,
            suffix=suffix,
            output_path=str(output_path),
            cairosvg_module=cairosvg_module,
            dpi=dpi,
            scale=scale,
            background_color=background_color,
            output_width=output_width,
            output_height=output_height,
        )
        return

    svg_root = _render_svg_root(canvas)
    unsupported = _get_reportlab_unsupported_svg_features(svg_root)
    if auto_fallback:
        _warn_reportlab_fallback(suffix, unsupported)
    elif unsupported:
        _warn_reportlab_unsupported_features(suffix, unsupported)
    renderer = _get_renderer_for_suffix(suffix)
    with _temporary_canvas_background(canvas, background_color):
        renderer(canvas, str(output_path))


def _validate_canvas_like(canvas: Any) -> None:
    """Raise if input is not compatible with Toyplot canvas rendering."""
    missing = []
    if not hasattr(canvas, "_scenegraph"):
        missing.append("_scenegraph")
    if not hasattr(canvas, "style"):
        missing.append("style")
    if missing:
        raise TypeError(
            "save() expected a toyplot Canvas-like object; missing required "
            f"attributes: {', '.join(missing)}."
        )


def _normalize_output_path(path: Union[str, Path]) -> tuple[Path, str]:
    """Return normalized output path and lowercase suffix."""
    path = Path(path)
    raw_suffix = path.suffix
    suffix = (raw_suffix or ".html").lower()
    if suffix not in SUFFIXES:
        raise OSError(
            f"File path suffix not recognized ({raw_suffix or ''}). "
            f"Path should end with one of {SUFFIXES}."
        )
    return (path if raw_suffix else path.with_suffix(".html")), suffix


def _validate_backend(backend: str, suffix: str) -> None:
    """Validate backend selection for a requested suffix."""
    if backend not in PDF_PNG_BACKENDS:
        raise ValueError(
            f"Unknown backend '{backend}'. Expected one of {PDF_PNG_BACKENDS}."
        )
    if suffix not in PDF_PNG_SUFFIXES and backend != "auto":
        raise ValueError(
            "The 'backend' option only applies to PDF and PNG export. "
            f"Received backend={backend!r} for suffix={suffix!r}."
        )


def _select_pdf_png_backend(
    backend: str,
) -> tuple[str, Any | None, bool]:
    """Return selected backend, optional CairoSVG module, and fallback flag."""
    if backend == "reportlab":
        return "reportlab", None, False

    if backend == "cairosvg":
        cairosvg = _import_cairosvg()
        if cairosvg is None:
            raise ImportError(
                "PDF/PNG export with backend='cairosvg' requires cairosvg. "
                "Install with `pip install cairosvg` or "
                "`pip install 'toytree[export]'`."
            )
        return "cairosvg", cairosvg, False

    cairosvg = _import_cairosvg()
    if cairosvg is not None:
        return "cairosvg", cairosvg, False
    return "reportlab", None, True


def _import_cairosvg() -> Any | None:
    """Import CairoSVG if available."""
    try:
        return importlib.import_module("cairosvg")
    except ImportError:
        return None


def _get_renderer_for_suffix(suffix: str) -> Callable[[Any, str], Any]:
    """Return direct Toyplot render function for a normalized suffix."""
    if suffix == ".html":
        import toyplot.html

        return toyplot.html.render

    if suffix == ".svg":
        import toyplot.svg

        return toyplot.svg.render

    if suffix == ".pdf":
        import toyplot.pdf

        return toyplot.pdf.render

    if suffix == ".png":
        import toyplot.png

        return toyplot.png.render

    raise RuntimeError(f"No renderer configured for suffix: {suffix}")


def _render_pdf_png_with_cairosvg(
    *,
    canvas: Any,
    suffix: str,
    output_path: str,
    cairosvg_module: Any,
    dpi: float,
    scale: float,
    background_color: str | None,
    output_width: int | None,
    output_height: int | None,
) -> None:
    """Render PDF or PNG by converting canonical SVG output with CairoSVG."""
    svg_bytes = _render_svg_bytes(canvas)
    options = {
        "bytestring": svg_bytes,
        "write_to": output_path,
        "dpi": dpi,
        "scale": scale,
        "background_color": background_color,
        "output_width": output_width,
        "output_height": output_height,
    }
    if suffix == ".pdf":
        cairosvg_module.svg2pdf(**options)
    elif suffix == ".png":
        cairosvg_module.svg2png(**options)
    else:
        raise RuntimeError(f"Unexpected CairoSVG suffix: {suffix}")


def _render_svg_root(canvas: Any) -> xml.Element:
    """Return SVG root element for a canvas."""
    import toyplot.svg

    return toyplot.svg.render(canvas)


def _render_svg_bytes(canvas: Any) -> bytes:
    """Return SVG bytes for a canvas."""
    root = _render_svg_root(canvas)
    return xml.tostring(root, encoding="utf-8")


@contextmanager
def _temporary_canvas_background(
    canvas: Any, background_color: str | None
) -> Iterator[None]:
    """Temporarily override canvas background color during export."""
    style = getattr(canvas, "style", None)
    if background_color is None or not isinstance(style, MutableMapping):
        yield
        return

    sentinel = object()
    original = style.get("background-color", sentinel)
    style["background-color"] = background_color
    try:
        yield
    finally:
        if original is sentinel:
            style.pop("background-color", None)
        else:
            style["background-color"] = original


def _parse_inline_style(style: str) -> dict[str, str]:
    """Return CSS declarations parsed from an inline style string."""
    parsed: dict[str, str] = {}
    for declaration in style.split(";"):
        if not declaration or ":" not in declaration:
            continue
        key, value = declaration.split(":", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def _iter_svg_elements_with_style(
    element: xml.Element, inherited: dict[str, str] | None = None
) -> Iterator[tuple[xml.Element, dict[str, str]]]:
    """Yield SVG elements paired with inherited inline styles."""
    style = dict(inherited or {})
    style.update(_parse_inline_style(element.get("style", "")))
    for key in (
        "fill",
        "fill-opacity",
        "stroke",
        "stroke-opacity",
        "opacity",
    ):
        if key in element.attrib:
            style[key] = element.attrib[key]
    yield element, style
    for child in element:
        yield from _iter_svg_elements_with_style(child, style)


def _get_reportlab_unsupported_svg_features(root: xml.Element) -> list[str]:
    """Return known SVG features that the legacy ReportLab path misses."""
    features: list[str] = []
    if any(_element_tag_name(elem) == "linearGradient" for elem in root.iter()):
        features.append("linear gradients")

    for element, style in _iter_svg_elements_with_style(root):
        if _element_tag_name(element) != "path":
            continue
        fill = style.get("fill")
        if fill and fill != "none":
            features.append("filled paths")
            break
    return features


def _element_tag_name(element: xml.Element) -> str:
    """Return an XML element tag name without namespace prefix."""
    return element.tag.rsplit("}", 1)[-1]


def _warn_reportlab_fallback(suffix: str, unsupported: list[str]) -> None:
    """Print a warning when auto export falls back to ReportLab."""
    message = (
        f"warning: cairosvg is not installed; falling back to legacy reportlab "
        f"{suffix[1:].upper()} export. Install cairosvg or "
        "`pip install 'toytree[export]'` for more reliable PDF/PNG output."
    )
    if unsupported:
        message += (
            " This figure contains SVG features reportlab may not fully render: "
            f"{', '.join(unsupported)}. Saving to SVG is the safest fallback."
        )
    print(message, file=sys.stderr)


def _warn_reportlab_unsupported_features(suffix: str, unsupported: list[str]) -> None:
    """Print a warning when explicit ReportLab export sees unsupported SVG."""
    if not unsupported:
        return
    message = (
        f"warning: legacy reportlab {suffix[1:].upper()} export may not fully "
        f"render this figure because it contains {', '.join(unsupported)}. "
        "Use backend='cairosvg' or save SVG for the most reliable output."
    )
    print(message, file=sys.stderr)


def _canvas_has_toytree_linear_gradients(canvas: Any) -> bool:
    """Return True if the canvas scenegraph contains gradient edge marks."""
    from toytree.drawing.src.mark_annotation import AnnotationGradientLine

    scenegraph = canvas._scenegraph
    stack = [canvas]
    visited: set[int] = set()

    # Use DFS over render targets because marks are nested under axes and
    # possibly other containers; stop immediately on the first match.
    while stack:
        obj = stack.pop()
        oid = id(obj)
        if oid in visited:
            continue
        visited.add(oid)

        if isinstance(obj, AnnotationGradientLine):
            return True

        try:
            targets = scenegraph.targets(obj, "render")
        except Exception:
            targets = ()
        stack.extend(targets)
    return False


if __name__ == "__main__":
    pass
