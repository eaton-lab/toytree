#!/usr/bin/env python

"""Convert ``ToyTree.draw`` arguments into drawing objects.

This module applies draw-time style arguments to a base ``TreeStyle``,
projects node coordinates with the requested layout, and returns a
``ToyTreeMark`` rendered on toyplot axes.
"""

from collections.abc import Mapping
from typing import Any, Tuple, TypeVar

import numpy as np
from loguru import logger
from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian

# from toytree.annotate.src.add_scale_bar import add_axis_scale_bar_to_mark
from toytree.drawing.src.mark_toytree import ToyTreeMark
from toytree.drawing.src.scale_axes import (
    add_tree_domain_mark,
    get_toytree_scale_cartesian,
)
from toytree.drawing.src.setup_canvas import get_canvas_and_axes
from toytree.layout import BaseLayout, CircularLayout, LinearLayout, UnrootedLayout
from toytree.style import (
    TreeStyle,
    get_base_tree_style_by_name,
    tree_style_to_css_dict,
    validate_style,
)

# from toytree.utils import ToytreeError
ToyTree = TypeVar("ToyTree")


def get_tree_style_updated_by_draw_args(tree: ToyTree, **kwargs) -> TreeStyle:
    """Return a draw-validated ``TreeStyle``.

    Parameters
    ----------
    tree : ToyTree
        Tree object being drawn.
    **kwargs : dict[str, Any]
        Parsed draw arguments forwarded by ``ToyTree.draw``.

    Returns
    -------
    TreeStyle
        Style copy with draw overrides validated and expanded into
        render-ready arrays and style dictionaries.

    Notes
    -----
    Draw-style precedence is:

    1. ``tree_style`` if provided.
    2. ``ts`` shorthand from extra kwargs when ``tree_style`` is not set.
    3. ``tree.style.tree_style`` when present.
    4. Copy of ``tree.style``.

    Unknown extra kwargs are ignored with a warning.
    """
    # extract extra kwargs that are not in ToyTree.draw()
    extra_obj = kwargs.pop("kwargs", {})
    if extra_obj is None:
        extra_kwargs = {}
    elif isinstance(extra_obj, Mapping):
        extra_kwargs = dict(extra_obj)
    else:
        logger.warning(
            "Expected draw() internal `kwargs` to be a mapping; "
            "received unsupported value and ignored it."
        )
        extra_kwargs = {}

    # remove 'ts' shortcut name and expand as a user tree_style arg
    ts_key = extra_kwargs.pop("ts", None)
    style_key = kwargs.get("tree_style")
    if style_key is None and ts_key is not None:
        kwargs["tree_style"] = ts_key
    elif style_key is not None and ts_key is not None and ts_key != style_key:
        logger.warning(
            "Both `tree_style` and shorthand `ts` were provided; "
            "using `tree_style` and ignoring `ts`."
        )

    # warn user of any remaining (unsupported) kwargs
    if extra_kwargs:
        unknown = ", ".join(sorted(extra_kwargs))
        logger.warning(
            "Unrecognized keyword arguments passed to draw() were ignored: "
            f"{unknown}. Check docs for current argument names."
        )

    # get a TreeStyle COPY from tree.style or new ts TreeStyle()
    style = get_tree_style_base(tree, tree_style=kwargs.pop("tree_style", None))

    # special handling of tree_style='p' in case Ne is not a feature.
    if style.tree_style == "p" and "Ne" not in tree.features:
        style.edge_widths = None

    # check and expand user-kwargs if provided else base style value
    style = validate_style(tree, style, **kwargs)
    return style


def draw_toytree(tree: ToyTree, **kwargs) -> Tuple[Canvas, Cartesian, ToyTreeMark]:
    """Return drawing objects from parsed draw arguments.

    Parameters
    ----------
    tree : ToyTree
        Tree object to draw.
    **kwargs : dict[str, Any]
        Draw arguments parsed by ``ToyTree.draw``.

    Returns
    -------
    tuple[Canvas | None, Cartesian, ToyTreeMark]
        Canvas, axes, and tree mark. Canvas is ``None`` if drawing is
        done on user-supplied axes.

    Notes
    -----
    Draw arguments override values in ``tree.style``. If ``tree_style``
    is provided then a built-in base style is selected before applying
    draw-specific overrides.
    """
    # extract Cartesian axes or None
    axes = kwargs.pop("axes", None)
    label = kwargs.pop("label", None)
    fixed_order = kwargs.pop("fixed_order", None)
    fixed_position = kwargs.pop("fixed_position", None)
    interior_algorithm = kwargs.pop("interior_algorithm", 0)

    # get tree style expanded for user args and base tree style (ts)
    style = get_tree_style_updated_by_draw_args(tree, **kwargs)

    # get a Layout with coordinates projected based on style
    layout = get_layout(
        tree=tree,
        style=style,
        fixed_order=fixed_order,
        fixed_position=fixed_position,
        interior_algorithm=interior_algorithm,
    )

    # set tip angles on 'c' or unrooted layouts
    if style.tip_labels_angles is None:
        style.tip_labels_angles = layout.angles

    # generate toyplot Mark. Style is already validated. tables of int idx labels
    mark = ToyTreeMark(
        ntable=layout.coords,
        ttable=layout.tcoords,
        etable=tree.get_edges("idx"),
        **tree_style_to_css_dict(style),
    )

    # create Canvas and Cartesian if they don't yet exist.
    canvas, axes = get_canvas_and_axes(
        axes, mark, kwargs.get("width"), kwargs.get("height")
    )

    # make range symmetric for circular trees
    if style.layout.startswith("c"):
        axes.aspect = "fit-range"

    # add ToyTreeMark to Cartesian axes.
    axes.add_mark(mark)
    add_tree_domain_mark(axes, ntable=layout.coords, layout=style.layout)

    # Show axes with a scale bar if requested.
    if mark.scale_bar is False:
        # hide axes if Cartesian is new and scale bar not added.
        if canvas is not None:
            axes.x.show = False
            axes.y.show = False
        scale_axes = get_toytree_scale_cartesian(axes, create=False)
        if scale_axes is not None:
            scale_axes.show = False
            scale_axes.x.show = False
            scale_axes.y.show = False
    else:
        # keep host axes free for plotting and extents management; scale
        # bar is rendered on the hidden companion axes.
        axes.x.show = False
        axes.y.show = False
        tree.annotate.add_axes_scale_bar(axes)

    # add label text to axes (user can add more styling outside)
    if label is not None:
        axes.label.text = label

    return canvas, axes, mark


def get_tree_style_base(tree: ToyTree, **kwargs) -> TreeStyle:
    """Return base style object for a draw call.

    Parameters
    ----------
    tree : ToyTree
        Tree object being drawn.
    **kwargs : dict[str, Any]
        Optional style selectors (``tree_style`` or ``ts``).

    Returns
    -------
    TreeStyle
        Base style before draw-time validation and expansion.
    """
    # allow tree_style or ts as args.
    if kwargs.get("tree_style"):
        tree_style = kwargs["tree_style"]
    else:
        tree_style = kwargs.get("ts")

    # get new TreeStyle from user-entered arg (e.g., 's')
    if tree_style is not None:
        style = get_base_tree_style_by_name(tree_style)

    # get new TreeStyle from tree.style.tree_style (e.g., 'n')
    elif tree.style.tree_style is not None:
        style = get_base_tree_style_by_name(tree.style.tree_style)

    # get deepcopy of current TreeStyle in tree.style
    else:
        style = tree.style.copy()
    return style


def _normalize_layout(layout: Any) -> str:
    """Return canonical layout token used by draw dispatch.

    Parameters
    ----------
    layout : Any
        Layout value from style or draw arguments.

    Returns
    -------
    str
        Canonical layout key. One of linear keys (``r``, ``l``, ``u``,
        ``d``), a circular key beginning with ``c``, or ``unrooted``.
    """
    if not isinstance(layout, str):
        return "unrooted"

    key = layout.strip().lower()
    if key in {"r", "l", "u", "d"}:
        return key
    if key.startswith("c"):
        return key
    if key.startswith("un"):
        return "unrooted"
    return "unrooted"


def get_layout(tree: ToyTree, style: TreeStyle, **kwargs) -> BaseLayout:
    """Return layout object for current style and constraints.

    Parameters
    ----------
    tree : ToyTree
        Tree to project into drawing coordinates.
    style : TreeStyle
        Validated style object used for drawing.
    **kwargs : dict[str, Any]
        Optional layout constraints including ``fixed_order``,
        ``fixed_position``, and ``interior_algorithm``.

    Returns
    -------
    BaseLayout
        One of ``LinearLayout``, ``CircularLayout``, or
        ``UnrootedLayout``.

    Notes
    -----
    ``layout='un...'`` is treated as unrooted. Any layout string that
    does not match linear or circular forms is also routed to unrooted.
    """
    style.layout = _normalize_layout(style.layout)

    # return a linear layout
    if style.layout in {"r", "l", "u", "d"}:
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
    if style.layout.startswith("c"):
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
    tre = toytree.rtree.imbtree(
        10,
    )
    tre._draw_browser("s", admixture_edges=[((2, 3), 4)], tmpdir="~", label="HI")

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
