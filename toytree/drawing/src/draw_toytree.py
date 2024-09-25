#!/usr/bin/env python

"""Parse user args to `draw` and return drawing.

The `draw_toytree` func does the following:
    - calls `get_tree_style_updated_by_draw_args` to get apply user
      args to `draw` to a starting Treestyle. This includes validation
      of user args by `validate_style`.
    - calls `get_layout` to get a BaseLayout child class with Node
      coordinates given the tree style.
    - creates a ToyTreeMark to generate and return the tree drawing.
    - calls `get_canvas_and_axes`to get Canvas and Axes sized.
"""

from typing import Tuple, TypeVar
from loguru import logger
import numpy as np
from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian

# from toytree.annotate.src.add_scale_bar import add_axis_scale_bar_to_mark
from toytree.drawing import ToyTreeMark
from toytree.drawing.src.setup_canvas import get_canvas_and_axes
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

def get_tree_style_updated_by_draw_args(tree: ToyTree, **kwargs) -> TreeStyle:
    """Return an expanded TreeStyle given user args and base treestyle.

    Parses the `Toytree.draw()` function arguments to update TreeStyle.
    - expands special 'ts' arg as `tree_style`.
    - logs warning for any unrecognized args.
    - gets a TreeStyle base.
    - validates style args and updates TreeStyle using them.
    - return the updated TreeStyle object.
    """
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

    # get a TreeStyle COPY from tree.style or new ts TreeStyle()
    style = get_tree_style_base(tree, tree_style=kwargs.pop('tree_style'))

    # special handling of tree_style='p' in case Ne is not a feature.
    if style.tree_style == "p" and "Ne" not in tree.features:
        style.edge_widths = None

    # check and expand user-kwargs if provided else base style value
    style = validate_style(tree, style, **kwargs)
    return style


def draw_toytree(tree: ToyTree, **kwargs) -> Tuple[Canvas, Cartesian, ToyTreeMark]:
    """Parse arguments to draw function and return drawing objects.

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
    # extract Cartesian axes or None
    axes = kwargs.pop("axes")
    label = kwargs.pop("label")

    # get tree style expanded for user args and base tree style (ts)
    style = get_tree_style_updated_by_draw_args(tree, **kwargs)

    # get a Layout with coordinates projected based on style
    layout = get_layout(
        tree=tree,
        style=style,
        fixed_order=kwargs.pop("fixed_order"),
        fixed_position=kwargs.pop("fixed_position"),
    )

    # set tip angles on 'c' or unrooted layouts
    if style.tip_labels_angles is None:
        style.tip_labels_angles = layout.angles

    # generate toyplot Mark. Style is already validated. tables of int idx labels
    mark = ToyTreeMark(
        ntable=layout.coords,
        ttable=layout.tcoords,
        etable=tree.get_edges('idx'),
        **tree_style_to_css_dict(style),
    )

    # create Canvas and Cartesian if they don't yet exist.
    canvas, axes = get_canvas_and_axes(
        axes,
        mark,
        kwargs.get('width'),
        kwargs.get('height')
    )

    # make range symmetric for circular trees
    if style.layout == "c":
        axes.aspect = "fit-range"

    # add ToyTreeMark to Cartesian axes.
    axes.add_mark(mark)

    # Show axes with a scale bar if requested.
    if mark.scale_bar is False:
        # hide axes if Cartesian is new and scale bar not added.
        if canvas is not None:
            axes.x.show = False
            axes.y.show = False
    else:
        tree.annotate.add_axes_scale_bar(axes)

    # add label text to axes (user can add more styling outside)
    if label:
        axes.label.text = label

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
            kwargs.get("fixed_position"),
            kwargs.get("interior_algorithm", 0),
        )

    # warn user that positional constraints are only for linear layouts
    if kwargs.get("fixed_order") is not None:
        logger.warning(f"`fixed_order` has no effect on `{style.layout}` layout.")
    if kwargs.get("fixed_position") is not None:
        logger.warning(f"`fixed_position` has no effect on `{style.layout}` layout.")

    # return circular or unrooted layout
    if style.layout[0] == "c":
        # require tip_labels_align=True for 'c' unless no variation
        if not np.allclose(tree.get_tip_data("height"), 0):
            style.tip_labels_align = True
        return CircularLayout(tree, style)

    # anything else is unrooted (None, etc.)
    return UnrootedLayout(tree, style)
    # if style.layout in ["unrooted", "unroot", "u1", "u2"]:
    # raise ToytreeError(f"layout style not recognized: {style.layout}")


if __name__ == "__main__":

    import toytree
    toytree.set_log_level("DEBUG")
    tre = toytree.rtree.imbtree(10, )
    tre._draw_browser('s', admixture_edges=[((2, 3), 4)], tmpdir="~", label="HI")

    # tre[0].name = "HELLO"
    # tre[4].name = "HELLO"
    # tre[6].name = "HELLO WORLD"
    # tre[-1]._dist = 10
    # tre._draw_browser(
    #     ts='p',
    #     layout='c',
    #     edge_type='c',
    #     height=400,
    #     width=400,
    #     node_mask=tre.get_node_mask(1, 5, 9),
    #     # tip_labels="name",
    # )
