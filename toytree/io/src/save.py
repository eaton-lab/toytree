#!/usr/bin/env python

"""Save canvas to file rendered as HTML, SVG, PDF, or PNG.

This is similar to the toyplot.render module but is intended to be a
bit simpler by requiring import of the file format prior to use. By
creating a separate module for this in toytree it also reduces the
need to import toyplot alongside toytree solely for the purpose of
saving canvases.
"""

from typing import Union
from pathlib import Path
from toytree.core import Canvas


SUFFIXES = (".html", ".svg", ".pdf", ".png")


def save(canvas: Canvas, path: Union[str, Path]):
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
            "File path suffix not recognized ({suffix}). "
            "Path should end with one of {SUFFIXES}.")

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


if __name__ == "__main__":
    pass
