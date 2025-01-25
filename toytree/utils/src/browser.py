#!/usr/bin/env python

"""Functionality for displaying a Toyplot canvas in a web browser.

"""

from typing import Sequence, Union, TypeVar
import xml.etree.ElementTree as xml
import tempfile
import webbrowser
from pathlib import Path

Canvas = TypeVar("Canvas")


def show(
    canvases: Union[Canvas, Sequence[Canvas]],
    title: str = "toytree",
    new: bool = False,
    tmpdir: Union[Path, str] = None,
) -> None:
    """Display one or more canvases in a web browser.

    Uses Toyplot's preferred HTML+SVG+Javascript backend to display
    one-or-more interactive canvases in a web browser window. The
    canvases will open in the default browser window or tab.

    Parameters
    ----------
    canvases: :class:`toyplot.canvas.Canvas` instance or sequence of :class:`toyplot.canvas.Canvas` instances.
        The canvases to be displayed.
    title: string, optional
        Optional page title to be displayed by the browser.
    new: bool
        If True then a new window will be opened. This appears to work
        on some systems but not others, where it will only always open
        new window.
    """
    import toyplot.canvas
    import toyplot.html

    # require Canvas or Sequence[Canvas] and make into Sequence[Canvas]
    if isinstance(canvases, toyplot.canvas.Canvas):
        canvases = [canvases]
    elif all(isinstance(i, toyplot.canvas.Canvas) for i in canvases):
        pass
    else:
        raise ValueError(
            f"Expected toyplot.Canvas or List[toyplot.Canvas], not {canvases}")

    # wrap the toytree as a html/svg element
    html = xml.Element("html")
    head = xml.SubElement(html, "head")
    xml.SubElement(head, "title").text = title
    body = xml.SubElement(html, "body")
    for canvas in canvases:
        body.append(toyplot.html.render(canvas))

    # write to a tempfile
    if tmpdir:
        path = Path(tmpdir).expanduser().resolve() / f"{title}.html"
    else:
        path = Path(tempfile.gettempdir()) / f"{title}.html"
    with open(path, "wb") as stream:
        stream.write(xml.tostring(html, method="html"))

    # open tmp html file in a window or tab in browser
    # autoraise=False tells it not to raise the window to the top,
    # but in some browsers this is not suppressable.
    webbrowser.open(str(path), new=new, autoraise=False)


if __name__ == "__main__":

    import toytree
    # tre = toytree.rtree.unittree(10)
    # c, a, m = tre.draw()
    # show(c, tmpdir="~")
