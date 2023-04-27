#!/usr/bin/env python

"""Parse user args to `draw` and return drawing.

The `draw_toytree` func does the following:
    - get_tree_style: return a TreeStyle given tree and draw kwargs
    - BaseLayout: get Node coordinates given tree and TreeStyle
    - CanvasSetup: get Canvas and Axes from user kwargs or auto-sized.
    - ToyTreeMark to generate and return the tree drawing.
"""

from typing import Tuple, TypeVar, Optional
from loguru import logger
from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian

from toytree.drawing import ToyTreeMark, get_canvas_and_axes, CanvasSetup
from toytree.layout import BaseLayout, LinearLayout, CircularLayout, UnrootedLayout
from toytree.style import (
    TreeStyle,
    validate_style,
    get_base_tree_style_by_name,
    tree_style_to_css_dict,
)


# from toytree.utils import ToytreeError
ToyTree = TypeVar("ToyTree")
logger = logger.bind(name="toytree")


def draw_toytree(tree: ToyTree, **kwargs) -> Tuple[Canvas, Cartesian, ToyTreeMark]:
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
    # TODO: can we get rid of this?
    # tree = kwargs.pop("toytree")

    # extract Cartesian axes or None
    axes = kwargs.pop("axes")

    # extract extra kwargs that are not in ToyTree.draw()
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

    # get a TreeStyle copy from tree.style or new ts TreeStyle()
    style = get_tree_style_base(tree, tree_style=kwargs.pop('tree_style'))

    # check and expand user-kwargs if provided else base style value
    style = validate_style(tree, style, **kwargs)

    # get a Layout with coordinates projected based on style
    # also sets tip_labels_angles for circular and unrooted layouts.
    # if no user value to tip-labels-angles then get layout generated val.
    # TODO: move to validation.
    # if style.tip_labels_angles is None:
    #     style.tip_labels_angles = layout.angles
    layout = get_layout(
        tree=tree,
        style=style,
        fixed_order=kwargs.pop("fixed_order"),
        fixed_position=kwargs.pop("fixed_position"),
    )

    # generate toyplot Mark. Style is already validated. tables of int idx labels
    mark = ToyTreeMark(
        ntable=layout.coords,
        etable=tree.get_edges('idx'),
        **tree_style_to_css_dict(style),
    )

    # use existing canvas and axes or create new ones. If created, the
    # size is built from (extents, ntips, height, margin, padding)
    # TODO: update. requires validated tip labels; sets height, width, ...
    logger.warning(style.height)
    # canvas, axes = get_canvas_and_axes(tree, axes, style)
    csetup = CanvasSetup(tree, axes, style)
    canvas = csetup.canvas
    axes = csetup.axes

    # add mark to axes
    axes.add_mark(mark)
    return canvas, axes, mark


def get_tree_style_base(tree: ToyTree, **kwargs) -> TreeStyle:
    """Return a style class object updated by user-args.

    If a `tree_style` arg was entered this overrides the default
    base style. Any additional style options in kwargs are applied
    on top of the base style.
    """
    # allow tree_style or ts as args.
    if kwargs.get('tree_style'):
        tree_style = kwargs['tree_style']
    else:
        tree_style = kwargs.get('ts')

    # get new TreeStyle from user-entered arg (e.g., 's')
    if tree_style is not None:
        style = get_base_tree_style_by_name(tree_style[0])

    # get new TreeStyle from tree.style.tree_style (e.g., 'n')
    elif tree.style.tree_style is not None:
        style = get_base_tree_style_by_name(tree.style.tree_style[0])

    # get deepcopy of current TreeStyle in tree.style
    else:
        style = tree.style.copy()
    return style


def get_layout(tree: ToyTree, style: TreeStyle, **kwargs) -> BaseLayout:
    """Return a Layout class object given a tree, style, and optional
    positional constraints.
    """
    # return a linear layout
    if style.layout in "rlud":
        return LinearLayout(
            tree,
            style,
            kwargs.get("fixed_order"),
            kwargs.get("fixed_position")
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
    tre._draw_browser(
        height=400, width=400,
        edge_style={"stroke-width": 5, "stroke-opacity": 0.7},
    )
