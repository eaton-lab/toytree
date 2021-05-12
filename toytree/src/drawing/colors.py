#!/usr/bin/env python

"""
Shortcut to make my favorite color Palettes in toyplot more accessible.
"""

import itertools
import toyplot.color


# # bring API utilities to the front
# # like my favorite color palettes
# from .drawing.TreeStyle import COLORS1 as colors
# from .drawing.TreeStyle import COLORS2 as darkcolors
# from .drawing.TreeStyle import 

# import itertools as _itertools
# icolors1 = _itertools.cycle(colors)
# icolors2 = _itertools.cycle(darkcolors)

COLORS1 = [toyplot.color.to_css(i) for i in toyplot.color.brewer.palette("Set2")]
COLORS2 = [toyplot.color.to_css(i) for i in toyplot.color.brewer.palette("Dark2")]
BLACK = toyplot.color.black


def icolors1():
    """
    Returns a color from an infinitely cycling palette 
    from the COLORS1 palette.
    """
    icolors = itertools.cycle(COLORS1)
    while 1:
        color = next(icolors)
        yield color

