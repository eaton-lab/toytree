#!/usr/bin/env python

"""
Function to parse user args to toytree.draw() and return drawing.
See full args/docstring at toytree.core.Toytree.ToyTree.draw()
"""

from typing import Tuple
from loguru import logger
from toytree.core.style.tree_style import get_tree_style, SubStyle, TreeStyle
from toytree.core.drawing.render import ToytreeMark
from toytree.core.drawing.canvas_setup import CanvasSetup


STYLE_ARGS = list(TreeStyle().__dict__.keys())


def draw_toytree(**user_args) -> Tuple['Canvas', "Cartesian", ToytreeMark]:
    """
    Draw toytree with user entered kwargs overlaid on a TreeStyle.
    """
    # get the parent toytree object
    self = user_args.pop('toytree')

    # get unexpected args, expand 'ts' short arg, and warn of bad args
    kwargs = user_args.pop('kwargs')
    if kwargs.get("ts"):
        user_args['tree_style'] = kwargs.pop("ts")
    if kwargs:
        logger.warning(
            f"Unrecognized arguments skipped: {list(kwargs)}."
            "\nCheck the docs, argument names may have changed.")

    # get TreeStyle (base or from ToyTree instance)
    if user_args['tree_style']:
        base_style = get_tree_style(user_args['tree_style'][0])
    else:
        base_style = self.style.copy()

    # update base_style with user_args
    for key in user_args:
        # get value of key but if it is None then skip it
        value = user_args[key]
        if value is None:
            continue

        # check if it is a substyledict
        substyle = getattr(base_style, key)
        if not isinstance(substyle, SubStyle):
            # update value of a standard style argument
            setattr(base_style, key, value)
        else:
            # update a substyle dict
            for sub_key in value:
                sub_value = value[sub_key]
                # support for -toyplot-anchor-shift, etc.
                sub_key = sub_key.replace("-", "_")
                try:
                    _ = getattr(substyle, sub_key)
                    setattr(substyle, sub_key, sub_value)
                except AttributeError:
                    logger.warning(
                        f"Unrecognized substyle drawing arg skipped: {sub_key}")

    # get edges and verts based on layout
    edges = self._coords.get_edges()
    if user_args['layout'] != 'c':
        verts = self._coords.get_linear_coords(
            base_style.layout,
            base_style.use_edge_lengths,
            user_args['fixed_order'],
            user_args['fixed_position'],
        )
    else:
        verts = self._coords.get_radial_coords(base_style.use_edge_lengths)

    # check all styles and expand to array values for all nodes
    base_style.validate(tree=self)

    # get canvas and axes
    csetup = CanvasSetup(self, user_args['axes'], base_style)
    canvas = csetup.canvas
    axes = csetup.axes

    # generate toyplot Mark. Style is already validated.
    mark = ToytreeMark(
        ntable=verts, etable=edges, **base_style.dict(False, False, True)
    )

    # add mark to axes
    axes.add_mark(mark)
    return canvas, axes, mark
