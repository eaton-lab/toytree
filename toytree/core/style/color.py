#!/usr/bin/env python


"""
Attempt to simplify toyplot.color representation and make it 
serializable with pydantic models.

dtype = {
    "names": ["r", "g", "b", "a"], 
    "formats": ["float64", "float64", "float64", "float64"],
    }
"""

# pylint: disable=no-member

import xml
import numpy as np
import toyplot
from pydantic import BaseModel
from pydantic.color import Color


class ToyColor(np.ndarray):
    """

    """
    def __init__(self, r:float, g:float, b:float, a:float=1.0):
        super().__init__([r, g, b, a], dtype=np.float64)

    def _repr_html_(self):
        """
        Show color as a div in jupyter notebooks
        """
        root_xml = xml.Element(
            "div",
            style="overflow:hidden; height:auto",
            attrib={"class": css_class})
        for color in colors:
            xml.SubElement(
                root_xml,
                "div",
                style="float:left;width:20px;height:20px;margin-right:%spx;background-color:%s" % (margin, to_css(color)))
        return xml.tostring(root_xml, encoding="unicode", method="html")




if __name__ == "__main__":

    PALETTE = toyplot.color.Palette()
