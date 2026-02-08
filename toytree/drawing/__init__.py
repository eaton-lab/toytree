#!/usr/bin/env python

"""Drawing functions for constructing Marks in the toyplot context.

"""

# main tree drawing Mark and .draw() function lazy-imported inside tree.py
from .src.mark_toytree import ToyTreeMark
from .src.draw_toytree import draw_toytree

# The render modules must be imported to expose multidispatch calls
from .src.render import *

# canvas/axes setup
# from toytree.drawing.src.setup_canvas import get_canvas_and_axes
# from toytree.drawing.src.setup_grid import Grid  #Setup
