#!/usr/bin/env python

"""...

"""

import numpy as np
from toytree.color.src.colorkit import ColorKit

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

    # TODO: update repr_html, repr, str so that this plays nice in json


if __name__ == "__main__":

    tc = ToyColor((1, 0, 0.2, 0.7))
    print(tc.colorkit.get_style_str(stroke=True))
