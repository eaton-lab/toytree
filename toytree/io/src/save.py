#!/usr/bin/env python

"""Save canvas to file rendered as HTML, SVG, PDF, or PNG.

This is similar to the toyplot.render module but is intended to be a
bit simpler by requiring import of the file format prior to use. By
creating a separate module for this in toytree it also reduces the
need to import toyplot alongside toytree solely for the purpose of
saving canvases.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Union

SUFFIXES = (".html", ".svg", ".pdf", ".png")


def save(canvas: Any, path: Union[str, Path]):
    """Save a Canvas to a file path.

    A Canvas can be saved in a variety of formats. If no recognized
    filename suffix exists in the path argument then the default format
    of HTML will be used. Other options are SVG, PDF, and PNG.

    Parameters
    ----------
    canvas: toyplot.Canvas
        A Canvas object created from a toyplot or toytree drawing.
    path: str | Path
        A filepath at which to save the canvas. The suffix of the path
        is used to designate the file type. Default is HTML, but SVG,
        PDF, and PNG are also supported.

        Note
        ----
        Canvases containing toytree linear-gradient edge annotations are
        currently supported only for HTML and SVG outputs. Attempting to
        save these canvases directly to PDF or PNG raises a ``ValueError``.
        Write to SVG first, then export to PDF/PNG using Inkscape or
        Illustrator.

    Example
    -------
    tree = toytree.rtree.coaltree(10)
    canvas, axes, mark = tree.draw(ts='c')
    toytree.save(canvas, "./drawing.svg")
    """
    # get suffix for path
    path = Path(path)
    suffix = path.suffix

    # if not suffix (only filename) then use html.
    if not suffix:
        suffix = ".html"

    # if suffix not recognized then raise error.
    if suffix.lower() not in SUFFIXES:
        raise OSError(
            f"File path suffix not recognized ({suffix}). "
            f"Path should end with one of {SUFFIXES}."
        )

    # Fast preflight check: inspect toytree marks in the canvas scenegraph
    # instead of triggering an additional HTML/SVG render pass.
    if suffix in (".pdf", ".png") and _canvas_has_toytree_linear_gradients(canvas):
        raise ValueError(
            "Canvas contains linearGradients, which are only currently "
            "supported for HTML and SVG outputs. For PDF or PNG write to SVG "
            "and then export to PDF/PNG in Inkscape or Illustrator."
        )

    # ...
    if suffix == ".html":
        import toyplot.html

        toyplot.html.render(canvas, str(path.with_suffix(suffix)))

    elif suffix == ".svg":
        import toyplot.svg

        toyplot.svg.render(canvas, str(path.with_suffix(suffix)))

    elif suffix == ".pdf":
        import toyplot.pdf

        toyplot.pdf.render(canvas, str(path.with_suffix(suffix)))

    elif suffix == ".png":
        import toyplot.png

        # TODO: accommodate pip installs w/o ghostscript here
        toyplot.png.render(canvas, str(path.with_suffix(suffix)))


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
