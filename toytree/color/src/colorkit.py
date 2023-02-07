#!/usr/bin/env python

"""ColorKit class for parsing and converting between color formats.

This is used to parse a SINGLE color input. This is an internal 
not intended to be used by users. Instead, users should use the 
ToyColor object, which uses ColorKit as its parser.

Note
----
If the color value being parsed can be either a single color or a 
container object with multiple colors then the `color_expander()` 
function should be used to parse it. That func will return either a 
single ToyColor or List[ToyColor].
"""

from typing import Union, Tuple
import xml.etree.ElementTree as xml
from copy import copy
import numpy as np
from loguru import logger
import toyplot.color
from toytree.color.src.utils import style_to_string
from toytree.utils import ToytreeError

logger = logger.bind(name="toytree")
ColorType = Union[str, np.ndarray, Tuple[float, float, float, float]]

class ColorKit:
    """Flexible color parser class to get css or rgba tuples.

    Color formats
    -------------
    - rgba = (r:float, g:float, b:float, a:float)
    - rgb = (r:float, g:float, b:float, a:float)
    - hex = "#000000"
    - css = "cornflowerblue"
    - array = np.array((1.0, 0.0, 0.0, 0.5), dtype=toyplot.color.dtype)
    """
    def __init__(self, color: ColorType):

        # store color as css, rgba, and ndarray
        self._css: str = None
        self._rgba: Tuple[float, float, float, float] = None
        self._array: np.ndarray = None
        self._parse_color(color)

        self._style = {
            "float": "left",
            "width": "16px",
            "height": "16px",
            "margin-right": "5px",
            "background-color": self.css,
            "border-radius": "50%",
        }

    @property
    def css(self) -> str:
        """Return CSS string as 'rgba(R%,G%,B%,A%)'."""
        return self._css        

    @property
    def array(self) -> np.ndarray:
        """Return numpy array with complex (r,g,b,a) dtype."""
        return self._array

    @property
    def rgba(self) -> Tuple[float, float, float, float]:
        """Return tuple with float for (r,g,b,a) percentages."""
        return self._rgba

    @property
    def rgb(self) -> Tuple[float, float, float]:
        """Return tuple with float for (r,g,b) percentages, no a."""
        return tuple(float(self.array[i]) for i in 'rgb')

    def get_style_str(self, stroke: bool = False, opacity: float = None) -> str:
        """Return SVG style string with fill/stroke and opacity separate."""
        rgb_css = f"rgb({self.css[5:].rsplit(',', 1)[0]})"
        opacity = self.rgba[-1] if opacity is None else opacity
        if stroke:
            return f"stroke:{rgb_css};stroke-opacity:{opacity}"
        return f"fill:{rgb_css};fill-opacity:{opacity}"

    def _parse_color(self, color: ColorType) -> None:
        """Parse input color to three stored formats."""
        # input is a css string (parse input based on type
        if isinstance(color, str):
            self._array = toyplot.color.css(color)
            if self._array is None:
                raise ToytreeError(f"CSS color '{color}' not recognized")
            self._css = toyplot.color.to_css(self._array)
            self._rgba = tuple(float(self._array[i]) for i in 'rgba')

        # input is an ndarray (e.g., toyplot.color ndarray, 1-d 4 floats)
        elif isinstance(color, np.ndarray) and color.dtype == toyplot.color.dtype:
            if color.size > 1:
                raise ToytreeError(
                    "Cannot parse a multi-color array to a ToyColor. "
                    "Use `toytree.color.ToyColor.color_expander()`\n"
                    "to convert it to a List[ToyColor]."
                )
            self._array = color.copy()
            self._css = toyplot.color.to_css(color)
            if not self._css:
                raise ToytreeError(f"color array {color} not recognized")
            self._rgba = tuple(float(self._array[i]) for i in 'rgba')                

        elif isinstance(color, tuple) and len(color) == 4:
            self._rgba = color
            self._array = toyplot.color.rgba(*self._rgba)
            self._css = toyplot.color.to_css(self._array)

        elif isinstance(color, tuple) and len(color) == 3:
            self._rgba = color + (1.0,)
            self._array = toyplot.color.rgba(*self._rgba)
            self._css = toyplot.color.to_css(self._array)

        elif isinstance(color, ColorKit):
            self._array = copy(color._array)
            self._css = copy(color._css)
            self._rgba = copy(color._rgba)

        elif isinstance(color, np.void):
            self._rgba = copy(color.item())
            self._array = toyplot.color.rgba(*self._rgba)
            self._css = toyplot.color.to_css(self._array)

        else:
            raise ToytreeError(f"color arg {color} not supported")

    def _repr_html_(self):
        """Show color as a div in jupyter notebooks"""
        # create a root dom element
        root_xml = xml.Element(
            "div",
            style="overflow:hidden; height:auto; display:table",
            attrib={"class": "toytree-ToyColor"},
        )
        _ = xml.SubElement(root_xml, "div", style=style_to_string(self._style),
        )
        _ = xml.SubElement(root_xml, "text").text = (
            "Color({:.2f}, {:.2f}, {:.2f}, {:.2f})"
            .format(*self.rgba)
        )

        # convert deom to a simple html script
        html = xml.tostring(root_xml, encoding="unicode", method="html")
        return html

if __name__ == "__main__":

    COLORS = [
        "RED",
        "red",
        "#000000",
        "rgba(100.0%,50.0%,25.0%,0.500)",
        "rgb(100%,50%,25%)",
        (1.0, 0.5, 0.25, 0.5),
        (1.0, 0.5, 0.25),        
        np.array((1.0, 0.5, 0.25, 0.5), dtype=toyplot.color.dtype),
        ColorKit("red"),
    ]
    for i in COLORS:
        c = ColorKit(i)
        print(c.css, c.rgba, c.array, c.get_style_str(), "\t | original =", i)
