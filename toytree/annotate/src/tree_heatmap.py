#!/usr/bin/env python

"""Functions for drawing and aligning trees with heatmaps/matrices.

Aligning trees with heatmaps using toyplot alone tends to be a bit 
tricky because (1) toyplot's canvas.matrix uses canvas coordinates
instead of axes coordinates; (2) adding tip labels can expand the
y-domain which affects alignment of plots on different axes; and
(3) trying to avoid canvas.matrix to instead use rect, scatterplot,
or other functions on a single axes is fairly complicated to write
a generalizable function for that will scale to different tree sizes.

"""

from dataclasses import dataclass

@dataclass
class Matrix:
    pass


