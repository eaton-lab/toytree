#!/usr/bin/env python

"""Save canvas to file rendered as HTML, SVG, PDF, or PNG.

This is similar to the toyplot.render module but is intended to be a
bit simpler by requiring import of the file format prior to use. By
creating a separate module for this in toytree it also reduces the
need to import toyplot alongside toytree solely for the purpose of
saving canvases.
"""

from __future__ import annotations

from collections.abc import Callable, MutableMapping
from pathlib import Path
from typing import Any, Union

SUFFIXES = (".html", ".svg", ".pdf", ".png")


def save(canvas: Any, path: Union[str, Path]) -> None:
    """Save a Canvas to a file path.

    A Canvas can be saved in a variety of formats. If no recognized
    filename suffix exists in the path argument then the default format
    of HTML will be used. Other options are SVG, PDF, and PNG.

    Parameters
    ----------
    canvas : toyplot.Canvas
        A canvas object created from a Toyplot or ToyTree drawing.
    path : str | Path
        Filepath where output will be written. If no filename suffix is
        provided then ``.html`` is appended by default.

    Notes
    -----
    Canvases containing toytree linear-gradient edge annotations are
    currently supported only for HTML and SVG outputs. Attempting to
    save these canvases directly to PDF or PNG raises a ``ValueError``.
    Write to SVG first, then export to PDF/PNG using Inkscape or
    Illustrator.

    PDF and PNG exports currently force canvas background-color to
    ``transparent`` during render and then restore it immediately
    afterward. This is a temporary workaround for backend overpaint
    artifacts with opaque canvas backgrounds.

    Raises
    ------
    TypeError
        If ``canvas`` does not look like a Toyplot canvas object.
    OSError
        If the filename suffix is not recognized.
    ValueError
        If gradient edge marks are present and output is PDF or PNG.

    Example
    -------
    >>> tree = toytree.rtree.coaltree(10)
    >>> canvas, axes, mark = tree.draw(ts='c')
    >>> toytree.save(canvas, "./drawing.svg")
    """
    _validate_canvas_like(canvas)

    # normalize path and suffix once.
    path = Path(path)
    raw_suffix = path.suffix
    suffix = (raw_suffix or ".html").lower()

    # if suffix not recognized then raise error.
    if suffix not in SUFFIXES:
        raise OSError(
            f"File path suffix not recognized ({raw_suffix or ''}). "
            f"Path should end with one of {SUFFIXES}."
        )

    output_path = path if raw_suffix else path.with_suffix(".html")

    # Fast preflight check: inspect toytree marks in the canvas scenegraph
    # instead of triggering an additional HTML/SVG render pass.
    if suffix in (".pdf", ".png") and _canvas_has_toytree_linear_gradients(canvas):
        raise ValueError(
            "Canvas contains linearGradients, which are only currently "
            "supported for HTML and SVG outputs. To obtain a PDF or PNG with "
            "a linear color gradient first write to SVG and then convert to "
            "PDF/PNG in external software like Inkscape or Illustrator."
        )

    renderer = _get_renderer_for_suffix(suffix)

    if suffix in (".pdf", ".png"):
        _render_with_transparent_background(canvas, renderer, str(output_path))
    else:
        renderer(canvas, str(output_path))


def _validate_canvas_like(canvas: Any) -> None:
    """Raise if input is not compatible with toyplot canvas rendering."""
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


def _get_renderer_for_suffix(suffix: str) -> Callable[[Any, str], Any]:
    """Return backend render function for a normalized suffix."""
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

    # Keep a defensive guard here even though save() validates suffix.
    raise RuntimeError(f"No renderer configured for suffix: {suffix}")


def _render_with_transparent_background(
    canvas: Any,
    renderer: Callable[[Any, str], Any],
    output_path: str,
) -> None:
    """Render canvas after temporarily forcing transparent background."""
    style = getattr(canvas, "style", None)
    if not isinstance(style, MutableMapping):
        renderer(canvas, output_path)
        return

    sentinel = object()
    original = style.get("background-color", sentinel)
    style["background-color"] = "transparent"
    try:
        renderer(canvas, output_path)
    finally:
        if original is sentinel:
            style.pop("background-color", None)
        else:
            style["background-color"] = original


def _canvas_has_toytree_linear_gradients(canvas: Any) -> bool:
    """Return True if the canvas scenegraph contains gradient edge marks.

    This inspects the toyplot scenegraph render relationships to find toytree
    ``AnnotationGradientLine`` marks without performing an additional canvas
    render, which keeps the check fast for save-time preflight validation.
    """
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
