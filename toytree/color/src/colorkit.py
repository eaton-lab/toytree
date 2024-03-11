#!/usr/bin/env python

"""ColorKit class for parsing and converting between color formats.

This is used to parse a SINGLE color input. This is an internal func
not intended for users. Instead, users should use the ToyColor object,
which uses ColorKit as its parser.
"""

from typing import Union, Tuple
from copy import copy
import numpy as np
from loguru import logger
import toyplot.color
from toytree.utils import ToyColorError

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

    def set_opacity(self, value: float) -> None:
        """Set opacity to a new value."""
        rgba = list(self._rgba)
        rgba[3] = value
        self._parse_color(tuple(rgba))
        return self

    def get_style_str(self, stroke: bool = False, opacity: float = None) -> str:
        """Return SVG style string with fill/stroke and opacity separate.

        If opacity is set to False then no opacity is printed. This is
        used when the parent class has an opacity that should be
        inherited.
        """
        # choose stroke or fille
        coltype = "stroke" if stroke else "fill"
        # get rbg from rgba
        rgb_css = f"rgb({self.css[5:].rsplit(',', 1)[0]})"
        # store rgb color as string
        color = f"{coltype}:{rgb_css}"
        # if opacity is None then get value from rgba
        if opacity is None:
            opacity = f";{coltype}-opacity:{self.rgba[-1]}"
        # if opacity if False then do not set.
        elif opacity is False:
            opacity = ""
        # if opacity if a value then use it.
        else:
            opacity = f";{coltype}-opacity:{opacity}"
        # return style string
        return color + opacity

    def _parse_color(self, color: ColorType) -> None:
        """Parse input color to three stored formats."""
        # input is a css string (parse input based on type

        # logger.error(color)
        if isinstance(color, str):
            if color == "none":
                self._rgba = (0, 0, 0, 0)
                self._array = toyplot.color.rgba(*self._rgba)
                self._css = toyplot.color.to_css(self._array)
            else:
                self._array = toyplot.color.css(color)
                if self._array is None:
                    raise ToyColorError(f"CSS color '{color}' not recognized")
                self._css = toyplot.color.to_css(self._array)
                self._rgba = tuple(float(self._array[i]) for i in 'rgba')

        # input is an ndarray (e.g., toyplot.color ndarray, 1-d 4 floats)
        elif isinstance(color, np.ndarray) and color.dtype == toyplot.color.dtype:
            if color.size > 1:
                raise ToyColorError(
                    "Cannot parse a multi-color array to a ToyColor. "
                    "Use `toytree.color.ToyColor.color_expander()`\n"
                    "to convert it to a List[ToyColor]."
                )
            self._array = color.copy()
            self._css = toyplot.color.to_css(color)
            if not self._css:
                raise ToyColorError(f"color array {color} not recognized")
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

        elif isinstance(color, float):
            if np.isnan(color):
                self._rgba = (0, 0, 0, 0)
                self._array = toyplot.color.rgba(*self._rgba)
                self._css = toyplot.color.to_css(self._array)
            else:
                raise ToyColorError(
                    f"Color arg '{color}' not recognized as a valid color input.")

        elif color is None:
            self._rgba = (0, 0, 0, 0)
            self._array = toyplot.color.rgba(*self._rgba)
            self._css = toyplot.color.to_css(self._array)

        else:
            raise ToyColorError(
                f"Color arg '{color}' not recognized as a valid color input.")

    # Colorkit doesn't need a repr, but this one was pretty nice, so 
    # I'll leave it here for now. But I commented it b/c I was encountering
    # a circular import error and didn't feel like fixing it.
    # def _repr_html_(self):
    #     """Show color as a div in jupyter notebooks"""
    #     # create a root dom element
    #     root_xml = xml.Element(
    #         "div",
    #         style="overflow:hidden; height:auto; display:table",
    #         attrib={"class": "toytree-ToyColor"},
    #     )
    #     _ = xml.SubElement(root_xml, "div", style=concat_style_to_str(self._style))
    #     _ = xml.SubElement(root_xml, "text").text = (
    #         "Color({:.2f}, {:.2f}, {:.2f}, {:.2f})"
    #         .format(*self.rgba)
    #     )

    #     # convert deom to a simple html script
    #     html = xml.tostring(root_xml, encoding="unicode", method="html")
    #     return html


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

    # set opacity
    print(c.rgba)
    c.set_opacity(0.5)
    print(c.rgba)