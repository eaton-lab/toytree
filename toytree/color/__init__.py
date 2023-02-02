#!/usr/bin/env python

"""toytree color subpackage.

This is a simple package for accessing convenience functions for 
selecting color palettes. See `toyplot.color` for the full color
module.

Examples
--------
>>> tree.draw(node_colors=toytree.colors.COLOR1[0])
>>> tree.draw(node_colors=toytree.colors.COLOR1)

"""

from toytree.color.src.utils import COLORS1, COLORS2, color_cycler
from toytree.color.src.toycolor import ToyColor
