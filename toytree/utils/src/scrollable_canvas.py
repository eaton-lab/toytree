#!/usr/bin/env python

"""A horizontal scrolling toyplot.Canvas.

This is currently used by the ipcoal and shadie packages to
visualize tree sequences simulated in SLiM and/or msprime using
the `ToyTreeSequenceDrawing` class.
"""

import toyplot

class ScrollableCanvas(toyplot.Canvas):
    """Canvas subclass with horizontal scrolling on large widths.

    This is returned as part of a ToyTreeSequenceDrawing in the typical
    three-part tuple of a toyplot drawing as (Canvas, axes, mark).
    """
    def _repr_html_(self):
        return toyplot.html.tostring(
            self, style={"text-align": "center", "width": f"{self.width}px"}
        )
