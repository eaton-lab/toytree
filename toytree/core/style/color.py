#!/usr/bin/env python

"""
The ToyColor class is used _internally_ by toytree to store 
colors while plotting. This object is a superclass of a ndarray,
consistent with the color representation in toyplot. It differs
in that it can be serialized to JSON by pydantic by interchangeably
converting to/from a Color object, which is made convenient by 
the ColorMixer superclass.
"""

# pylint: disable=no-member

from typing import Union, Tuple, List
import xml.etree.ElementTree as xml
import numpy as np
import toyplot
import toyplot.color
import pandas as pd
from toytree.core.drawing.render import style_to_string
from toytree.utils.exceptions import ToytreeError


# COLORS1 = [toyplot.color.to_css(i) for i in toyplot.color.brewer.palette("Set2")]
# COLORS2 = [toyplot.color.to_css(i) for i in toyplot.color.brewer.palette("Dark2")]
# BLACK = toyplot.color.black
# ICOLORS1 = _itertools.cycle(COLORS1)

# ITERABLE = (list, tuple, np.ndarray)
# COLORS1 = [toyplot.color.to_css(i) for i in toyplot.color.brewer.palette("Set2")]
# COLORS2 = [toyplot.color.to_css(i) for i in toyplot.color.brewer.palette("Dark2")]
# BLACK = toyplot.color.black


DTYPE = {
    "names": ["r", "g", "b", "a"], 
    "formats": ["float64", "float64", "float64", "float64"],
}


class ToyColor(np.ndarray):
    """
    ToyColor is a superclass of numpy.ndarray, and 
    """
    def __new__(cls, color):
        color = Color(color)
        obj = np.array(color.rgba, dtype=DTYPE).view(cls)
        return obj   
    
    @property
    def css(self):
        """Returns a name or hex value of a color"""
        return Color(self).css

    @property
    def rgba(self):
        """Returns a tuple of (r,g,b,a) as floats."""
        return Color(self).rgba

    # @property
    # def rgb(self):
    #     """Returns a tuple of (r,g,b,a) as floats."""
    #     return Color(self).rgb
    
    @property
    def color(self):
        """Returns a ..."""
        return Color(self)


class Color:
    """
    Flexible color parser class to get css or rgba tuple 
    representation, and easier to work with than toyplot.color 
    arrays. 

    - rgba = (r:float, g:float, b:float, a:float)
    - rgb = (r:float, g:float, b:float, a:float)
    - hex = "#000000"
    - css = "cornflower"

    Attributes
    ----------
    css: str
    rgba: Tuple[float, float, float, float]
    """
    def __init__(self, color: Union[str, np.ndarray]):

        # attrs to fill
        self.css: str = None
        self.rgba: Tuple[float, float, float, float] = None
        self.array: np.ndarray = None

        # input is a css string (parse input based on type
        if isinstance(color, str):
            self.css = color
            if not self.css:
                raise ToytreeError(f"color str {color} not recognized")
            self.array = toyplot.color.css(color)
            self.rgba = tuple(float(self.array[i]) for i in 'rgba')

        # input is an ndarray (e.g., toyplot.color ndarray, 1-d 4 floats)
        elif isinstance(color, np.ndarray) and color.dtype == DTYPE:
            self.array = color.copy()
            self.css = toyplot.color.to_css(color)
            if not self.css:
                raise ToytreeError(f"color array {color} not recognized")
            self.rgba = tuple(float(self.array[i]) for i in 'rgba')                

        elif isinstance(color, tuple) and len(color) == 4:
            self.rgba = color
            self.array = toyplot.color.rgba(*self.rgba)
            self.css = toyplot.color.to_css(self.array)

        elif isinstance(color, ToyColor):
            self.css = color.css
            self.rgba = color.rgba
            self.array = color.copy()

        else:
            raise ToytreeError(f"color arg {color} not supported")

        # store style dict
        self.style = {
            "float": "left",
            "width": "20px",
            "height": "20px",
            "margin-right": "5px",
            "background-color": self.css,
            "border-radius": "50%",
        }

    def _repr_html_(self):
        """
        Show color as a div in jupyter notebooks
        """
        # create a root dom element
        root_xml = xml.Element(
            "div",
            style="overflow:hidden; height:auto; display:table",
            attrib={"class": "toytree-ToyColor"},
        )
        _ = xml.SubElement(
            root_xml, "div",
            style=style_to_string(self.style),
        )
        _ = xml.SubElement(root_xml, "text").text = (
            "Color({:.2f}, {:.2f}, {:.2f}, {:.2f})"
            .format(*self.rgba)
        )

        # convert deom to a simple html script
        html = xml.tostring(root_xml, encoding="unicode", method="html")
        return html


def color_parser(color) -> Union[ToyColor, List[ToyColor]]:
    """
    Parse the input of a color based style argument to .draw(). This
    supports a wide variety of types, with ndarray being the most
    troublesome.
    """
    # return as a ToyColor if str or toyplot color ndarray
    if isinstance(color, str):
        return ToyColor(color)

    if isinstance(color, np.void):
        return ToyColor(tuple(color))

    if isinstance(color, np.ndarray) and color.dtype == DTYPE:
        if color.size == 1:
            return ToyColor(color)
        return [ToyColor(tuple(i)) for i in color]

    # else, it must be a collection of some type.
    if isinstance(color, (pd.Series, np.ndarray, list, tuple, toyplot.color.Palette)):
        return [color_parser(i) for i in color]

    if isinstance(color, toyplot.color.Map):
        raise ToytreeError(
            "toyplot.color.Map not supported. Try using the map to broadcast "
            "your values to a list of colors with colormap.colors(values).")
    raise ToytreeError(
        f"{color} ({type(color)}) is not a supported color argument.")



if __name__ == "__main__":

    import toytree

    PALETTE = toyplot.color.Palette()
    COLOR = PALETTE[0]

    col0 = Color(COLOR)
    col1 = Color('red')
    col2 = Color("#262626")

    col0 = ToyColor(COLOR)
    col1 = ToyColor("red")
    col2 = ToyColor("#262626")
    col3 = ToyColor(toytree.colors[0])

    for col in (col0, col1, col2, col3):
        print(f"{col.css}\t{col.rgba}\t{col}")
