#!/usr/bin/env python
# ruff: noqa: F401, F403

"""Drawing functions for constructing Marks in the toyplot context."""

from toyplot import Canvas
from toyplot.coordinates import Cartesian
from toyplot.mark import Mark

from .src._pdf_patch import install_pdf_render_patch
from .src.draw_toytree import draw_toytree

# main tree drawing Mark and .draw() function lazy-imported inside tree.py
from .src.mark_toytree import ToyTreeMark
from .src.mark_tree_domain import TreeDomainMark

# The render modules must be imported to expose multidispatch calls
from .src.render import *

# Patch Toyplot's ReportLab backend only once drawing is in use.
install_pdf_render_patch()

# canvas/axes setup
# from toytree.drawing.src.setup_canvas import get_canvas_and_axes
# from toytree.drawing.src.setup_grid import Grid  #Setup
