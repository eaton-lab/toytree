#!/usr/bin/env python

"""ToyColor is a superclass of numpy array w/ the toyplot.color.dtype.

It adds several functions for easily converting between color types, 
and for automatically parsing flexible input types.

Note
----
If the color value being parsed can be either a single color or a
container object with multiple colors then the `color_expander()`
function should be used to parse it. That func will return either a
single ToyColor or List[ToyColor].
>>> ToyColor.color_expander(['red', 'blue'])
>>> # [ToyColor((1,0,0,1), ToyColor((0,0,1,1))]
"""

from __future__ import annotations
from typing import List, Any
import numpy as np
from loguru import logger
import toyplot.color
from toytree.color.src.colorkit import ColorKit
from toytree.utils import ToyColorError
from toytree.utils.src.logger_setup import capture_logs

logger = logger.bind(name="toytree")
DTYPE = {
    "names": ["r", "g", "b", "a"],
    "formats": ["float64", "float64", "float64", "float64"],
}


class ToyColor(np.ndarray):
    """ToyColor is a superclass of numpy.ndarray.

    This is similar to how toyplot uses a numpy array to represent
    color, but it can init from any valid color input type and
    convert to any other.
    """
    def __new__(cls, color):
        color = ColorKit(color)
        obj = np.array(color.rgba, dtype=DTYPE).view(cls)
        return obj

    @property
    def css(self):
        """Returns a name or hex value of a color"""
        return ColorKit(self).css

    @property
    def rgba(self):
        """Returns a tuple of (r,g,b,a) as floats."""
        return ColorKit(self).rgba

    @property
    def rgb(self):
        """Returns a tuple of (r,g,b) as floats."""
        return ColorKit(self).rgb

    @property
    def colorkit(self):
        """Returns a ..."""
        return ColorKit(self)

    def get_style_str(self, stroke: bool = False, opacity: float = None) -> str:
        """Returns a color style string, e.g., 'fill=...; stroke=...'."""
        return self.colorkit.get_style_str(stroke, opacity)

    def __str__(self):
        return self.css

    def __repr__(self):
        tup = tuple(round(i, 3) for i in self.rgba)
        return f"ToyColor({tup})"

    @classmethod
    def color_expander(cls, color: Any, check_nested: bool = True) -> List[ToyColor]:
        """Return a List of ToyColor of the proper size for data points.

        Parse the input of a color based style argument to .draw(). This
        supports a wide variety of types, with ndarray being the most
        troublesome.
        """
        # first try to parse as a single color
        try:
            return ToyColor(color)
        except ToyColorError:
            pass

        # non-iterable container types from toyplot.
        # ndarray with size > 1
        if isinstance(color, np.ndarray):
            return [ToyColor(color.item(i)) for i in range(color.size)]

        # toyplot.color.Map type
        if isinstance(color, toyplot.color.Map):
            raise ToyColorError(COLORMAP_ALONE_ERROR)

        # else it must be a multi-color type object
        if check_nested:
            with capture_logs("ERROR"):
                try:
                    return [cls.color_expander(i, check_nested=False) for i in color]
                except ToyColorError:
                    pass

        raise ToyColorError(
            f"{color} ({type(color)}) is not a supported color argument.")


COLORMAP_ALONE_ERROR = """
toyplot.color.Map objects cannot be used to enter color
values directly. Instead, use the Map object to broadcast
values into an array of colors, which you can then enter
as a valid color input. Example:
>>> cmap = toyplot.color.brewer.map('BlueRed')
>>> colors = cmap.colors([0.0, 0.1, 0.2, 0.3, 0.8, 0.9])

Or, use the tuple type input syntax as a shortcut for color mapping:
>>> tree.draw(node_colors=('dist', 'BlueRed'))
"""


if __name__ == "__main__":

    import toyplot
    # tc = ToyColor((1, 0, 0.2, 0.7))
    # print(tc.colorkit.get_style_str(stroke=True))
    # print(tc)
    # print(tc.__repr_html__)

    # parsing single colors (using ColorKit under the hood)
    COLORS = [
        "RED",
        "red",
        "rgba(100.0%,50.0%,25.0%,0.500)",
        "rgb(100%,50%,25%)",
        (1.0, 0.5, 0.25, 0.5),
        (1.0, 0.5, 0.25),
        np.array((1.0, 0.5, 0.25, 0.5), dtype=toyplot.color.dtype),
        ColorKit("red"),
        toyplot.color.Palette()[0],
    ]
    for i in COLORS:
        c = ToyColor(i)
        print(f"{repr(c):<40} {str(c):<30} \t | original = {i}")

    # parsing single or multicolors (using color_expander -> ColorKit)
    COLORS = [
        "RED",
        "red",
        "rgba(100.0%,50.0%,25.0%,0.500)",
        "rgb(100%,50%,25%)",
        "#000000",
        (1.0, 0.5, 0.25, 0.5),
        (1.0, 0.5, 0.25),
        np.array((1.0, 0.5, 0.25, 0.5), dtype=toyplot.color.dtype),
        toyplot.color.Palette(),
        toyplot.color.brewer.map("BlueRed").colors([0, 2, 1]),
        list(toyplot.color.Palette()),
        ['red', 'blue', 'green'],
        ['red', toyplot.color.Palette()[0], "rgb(100%,50%,25%)"],
    ]
    for i in COLORS:
        c = ToyColor.color_expander(i)
        if isinstance(c, ToyColor):
            print(f"orig = {str(i):<50} | {repr(c)}")
        else:
            print(f"orig = {str(type(i)):<50} | len={len(c)}, {repr([c[0], '...'])}")

    # NOT_SUPPORTED = [
    #     toyplot.color.brewer.map("Pastel1"),
    # ]