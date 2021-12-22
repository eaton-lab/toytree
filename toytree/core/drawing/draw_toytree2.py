#!/usr/bin/env python

"""Parse user args to `draw` and return drawing.

This function uses the Layout class to parse Node coordinates from
the tree given the tree drawing style, and CanvasSetup to get either 
a user-defined or auto-sized Canvas and Axes, and ToyTreeMark to 
generate and return the tree drawing.

"""

from typing import Tuple
from loguru import logger
from toytree.core.layout import Layout
# from toytree.core.style.tree_style import SubStyle, TreeStyle
from toytree.core.drawing.render import ToytreeMark
from toytree.core.drawing.canvas_setup import CanvasSetup


def draw_toytree(**kwargs) -> Tuple['Canvas', 'Cartesian', 'Mark']:
    """Parse arguements to draw function and return drawing objects.

    The drawing style arguments can be entered in two ways, either
    by modifying attributes of the `.style` dict-like object linked 
    to a ToyTree, or by providing parameter arguments to the `.draw`
    function. The latter type overrides any values in the `.style`
    settings, and similarly, if a `tree_style` argument is used this
    overrides any/all settings in `.style` setting a new fresh base
    style setting.

    This function parses arguments to `draw`, updates a copy of the
    `.style`, and passes these style args as a dict to the ToyTreeMark
    class init function, along with the edges and verts.
    """
    # extract the ToyTree instance from kwargs
    tree = kwargs.pop("toytree")

    # extract optional non-styling kwargs
    axes = kwargs.pop("axes")

    # extract user kwargs
    extra_kwargs = kwargs.pop("kwargs")

    # remove 'ts' shortcut name and expand as a user tree_style arg
    if extra_kwargs.get("ts"):
        kwargs["tree_style"] = extra_kwargs.pop("ts")

    # warn user of any remaining (unsupported) kwargs
    if extra_kwargs:
        logger.warning(
            f"Unrecognized arguments skipped: {list(extra_kwargs)}."
            "\nCheck the docs, argument names may have changed.")

    # Use Layout class:
    # Get a base style setting on top of which to apply user args.
    # IF a tree_style arg is present in either user args or .style
    # then it clears any .style settings to start from a base style,
    # else, user args are applied on top of the non-default style.
    # The Layout.style dict is thus either new or a copy of .style
    layout = Layout(
        tree=tree, 
        fixed_order=kwargs.pop("fixed_order"),
        fixed_position=kwargs.pop("fixed_position"),
        **kwargs,
    )

    # check all styles and expand in-place to array values for all nodes
    layout.style.validate(tree=tree)

    # get canvas and axes
    csetup = CanvasSetup(tree, axes, layout.style)
    canvas = csetup.canvas
    axes = csetup.axes

    # generate toyplot Mark. Style is already validated.
    mark = ToytreeMark(
        ntable=layout.coords, 
        etable=tree._get_edges(),
        **layout.style.dict(False, False, True)
    )

    # add mark to axes
    axes.add_mark(mark)
    return canvas, axes, mark
