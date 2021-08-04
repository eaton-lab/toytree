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

from typing import Union, Tuple
import xml.etree.ElementTree as xml
import numpy as np
import toyplot
import toyplot.color
import pydantic
import pydantic.color
from toytree.core.drawing.render import style_to_string
from toytree.utils.exceptions import ToytreeError


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
    
    @property
    def color(self):
        """Returns a ..."""
        return Color(self)



class Color(pydantic.color.Color):
    """
    Flexible color parser class to get css or rgba tuple 
    representation, and easier to work with than toyplot.color 
    arrays. Serializable with pydantic, so this is the object type
    that is stored in TreeStyle class objects.

    - rgba = (r:float, g:float, b:float, a:float)
    - rgb = (r:float, g:float, b:float, a:float)
    - hex = "#000000"
    - css = "cornflower"
    - color = pydantic.color.Color

    Attributes
    ----------
    css: str
    rgba: Tuple[float, float, float, float]
    """
    def __init__(
        self,
        color: Union[str, np.ndarray, pydantic.color.Color],
        ):

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
            rgb_ints = [int(i * 255) for i in self.rgba[:3]]
            rgba = rgb_ints + [self.rgba[3]]
            super().__init__(rgba)

        # input is an ndarray (e.g., toyplot.color ndarray, 1-d 4 floats)
        elif isinstance(color, np.ndarray):
            assert all(color[i] <= 1 for i in 'rgba'), (
                "color array should contain floats in range [0, 1]")
            self.array = color
            self.css = toyplot.color.to_css(color)
            if not self.css:
                raise ToytreeError(f"color array {color} not recognized")
            self.rgba = tuple(float(self.array[i]) for i in 'rgba')                
            rgb_ints = [int(i * 255) for i in self.rgba[:3]]
            rgba = rgb_ints + [self.rgba[3]]
            super().__init__(rgba)

        # input is a pydantic Color object
        elif isinstance(color, pydantic.color.Color):
            super().__init__(color)
            self.css = color.as_named()
            rgba = self.as_rgb_tuple(alpha=True)
            rgb_floats = [i / 255. for i in rgba[:3]]
            self.rgba = rgb_floats + [float(rgba[3])]
            self.array = toyplot.color.rgba(*self.rgba)
        else:
            raise ToytreeError(f"color arg {color} not supported")

        # store style dict
        self.style = {
            "float": "left",
            "width": "20px",
            "height": "20px",
            "margin-right": "5px",
            "background-color": self.css,
        }


    def _repr_html_(self):
        """
        Show color as a div in jupyter notebooks
        """
        # create a root dom element
        root_xml = xml.Element(
            "div",
            style="overflow:hidden; height:auto",
            attrib={"class": "toytree-ToyColor"},
        )
        _ = xml.SubElement(
            root_xml, "div",
            style=style_to_string(self.style),
        )
        _ = xml.SubElement(
            root_xml, "text",
        ).text = (
            "ColorMixer({:.2f}, {:.2f}, {:.2f}, {:.2f})"
            .format(*self.rgba)
        )

        # convert deom to a simple html script
        html = xml.tostring(root_xml, encoding="unicode", method="html")
        return html



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
