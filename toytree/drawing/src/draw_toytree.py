#!/usr/bin/env python

"""Parse user args to `draw` and return drawing.

The `draw_toytree` func does the following:
    - get_tree_style: return a TreeStyle given tree and draw kwargs
    - BaseLayout: get Node coordinates given tree and TreeStyle
    - CanvasSetup: get Canvas and Axes from user kwargs or auto-sized.
    - ToyTreeMark to generate and return the tree drawing.
"""

from typing import Tuple, TypeVar
from copy import deepcopy
from loguru import logger
from toytree.layout import BaseLayout, LinearLayout, CircularLayout, UnrootedLayout
from toytree.drawing import ToytreeMark, CanvasSetup
from toytree.style import (
    TreeStyle, SubStyle, get_base_tree_style_by_name, validate_style
)

# from toytree.utils import ToytreeError

ToyTree = TypeVar("ToyTree")
logger = logger.bind(name="toytree")


def draw_toytree(**kwargs) -> Tuple["Canvas", "Cartesian", "Mark"]:
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

    # extract extra kwargs that are not in .draw func
    extra_kwargs = kwargs.pop("kwargs")

    # remove 'ts' shortcut name and expand as a user tree_style arg
    if extra_kwargs.get("ts"):
        kwargs["tree_style"] = extra_kwargs.pop("ts")

    # warn user of any remaining (unsupported) kwargs
    if extra_kwargs:
        logger.warning(
            f"Unrecognized arguments skipped: {list(extra_kwargs)}."
            "\nCheck the docs, argument names may have changed."
        )

    # get a TreeStyle (as new basestyle or tree.style) and update with draw kwargs
    style = get_tree_style(tree, **kwargs)

    # get a Layout with coordinates projected based on style
    layout = get_layout(
        tree=tree,
        style=style,
        fixed_order=kwargs.pop("fixed_order"),
        fixed_position=kwargs.pop("fixed_position"),
    )

    # if no user value to tip-labels-angles then use layout generated val.
    if style.tip_labels_angles is None:
        style.tip_labels_angles = layout.angles

    # check all styles and expand in-place to array values for all nodes
    validate_style(tree, style)

    # get canvas and axes
    csetup = CanvasSetup(tree, axes, style)
    canvas = csetup.canvas
    axes = csetup.axes

    # generate toyplot Mark. Style is already validated. tables of int idx labels
    mark = ToytreeMark(
        ntable=layout.coords, etable=tree.get_edges('idx'), **style.dict(serialize=False)
    )

    # add mark to axes
    axes.add_mark(mark)
    return canvas, axes, mark


def get_tree_style(tree: ToyTree, **kwargs) -> TreeStyle:
    """Return a style class object updated by user-args.

    If a `tree_style` arg was entered this overrides the default
    base style. Any additional style options in kwargs are applied
    on top of the base style.
    """
    # update kwargs for optional shortname for 'treestyle'
    if kwargs.get("ts"):
        kwargs["tree_style"] = kwargs.pop("ts")

    # get new TreeStyle from entered key (e.g., 's')
    if kwargs.get("tree_style"):
        style = get_base_tree_style_by_name(kwargs["tree_style"][0])
    # get new TreeStyle from the key in .style (e.g., 'n')
    elif tree.style.tree_style is not None:
        style = get_base_tree_style_by_name(tree.style.tree_style)
    # use existing TreeStyle in .style (no overwrite of base style)
    else:
        style = deepcopy(tree.style)

    # update base style with user entered style kwargs
    for key, value in kwargs.items():

        # skip key if left at default value (None)
        if value is None:
            continue

        # check if it is a substyledict
        substyle = getattr(style, key, "skip")

        # skip non TreeStyle kwargs (e.g., fixed_order, fixed_position)
        if substyle == "skip":
            continue

        # update value of a standard style argument
        if not isinstance(substyle, SubStyle):
            setattr(style, key, value)

        # update a substyle dict
        else:
            for sub_key in value:
                sub_value = value[sub_key]
                sub_key = sub_key.replace("-", "_")  # for -toyplot-anchor-shift, etc.
                if hasattr(substyle, sub_key):
                    setattr(substyle, sub_key, sub_value)
                else:
                    logger.warning(
                        f"Unrecognized substyle drawing arg skipped: {sub_key} ({substyle})."
                    )
    return style


def get_layout(tree: ToyTree, style: TreeStyle, **kwargs) -> BaseLayout:
    """Return a Layout class object given a tree, style, and optional
    positional constraints.
    """
    # return a linear layout
    if style.layout in "rlud":
        return LinearLayout(
            tree, style,
            kwargs.get("fixed_order"), kwargs.get("fixed_position")
        )

    # warn user that positional constraints are only for linear layouts
    if kwargs.get("fixed_order") is not None:
        logger.warning(f"`fixed_order` has no effect on `{style.layout}` layout.")
    if kwargs.get("fixed_position") is not None:
        logger.warning(f"`fixed_position` has no effect on `{style.layout}` layout.")

    # return circular or unrooted layout
    if style.layout[0] == "c":
        return CircularLayout(tree, style)

    # anything else is unrooted (None, etc.)
    return UnrootedLayout(tree, style)
    # if style.layout in ["unrooted", "unroot", "u1", "u2"]:
    # raise ToytreeError(f"layout style not recognized: {style.layout}")


if __name__ == "__main__":

    import toytree
    toytree.set_log_level("DEBUG")
    tre = toytree.rtree.unittree(10)
    tre._draw_browser(edge_style={"stroke-width": 5, "stroke-opacity": 0.7})
