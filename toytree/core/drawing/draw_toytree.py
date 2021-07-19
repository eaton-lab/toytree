#!/usr/bin/env python

"""
Function to parse user args to toytree.draw() and return drawing.
See full args/docstring at toytree.core.Toytree.ToyTree.draw()
"""

import sys
from toytree.core.drawing.tree_style import TreeStyle
from toytree.core.drawing.style_checker import StyleChecker
from toytree.core.drawing.render import ToytreeMark
from toytree.core.drawing.canvas_setup import CanvasSetup


def draw_toytree(**kwargs):
    """
    Draw toytree with user entered kwargs.
    """
    # get the parent toytree object
    self = kwargs.pop('toytree')

    # get curstyle: use base style (ts or tree_style), or use default ts
    if kwargs['kwargs'].get("ts"):
        kwargs['tree_style'] = kwargs['kwargs'].pop("ts")
    if kwargs['tree_style']:
        base_style = TreeStyle(kwargs['tree_style'][0])
    else:
        base_style = self.style.copy()

    # warn user if they entered kwargs that arent't supported.
    if kwargs.get("kwargs"):
        sys.stderr.write(
            f"Unrecognized arguments skipped: {list(kwargs['kwargs'])}."
            "\nCheck the docs, argument names may have changed.")
        kwargs.pop('kwargs')

    # drop None value'd args from user kwargs and update base_style
    user = dict(
        ("_" + i, j) if isinstance(j, dict) else (i, j)
        for (i, j) in kwargs.items() if j is not None
    )
    base_style.update(user)

    # update coords based on layout
    edges = self._coords.get_edges()
    if kwargs['layout'] == 'c':
        verts = self._coords.get_radial_coords(base_style.use_edge_lengths)
    else:
        verts = self._coords.get_linear_coords(
            base_style.layout, 
            base_style.use_edge_lengths,
            kwargs['fixed_order'],
            kwargs['fixed_position'],
        )

    # check all styles
    fstyle = StyleChecker(self, base_style).style

    # debugging returns the mark and prints the modified kwargs
    if kwargs.get('debug'):
        print(user)
        return fstyle

    # get canvas and axes
    csetup = CanvasSetup(self, kwargs['axes'], fstyle)
    canvas = csetup.canvas
    axes = csetup.axes

    # generate toyplot Mark
    mark = ToytreeMark(ntable=verts, etable=edges, **fstyle.to_dict())

    # add mark to axes
    axes.add_mark(mark)
    return canvas, axes, mark
