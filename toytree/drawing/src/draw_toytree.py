#!/usr/bin/env python

"""Convert ``ToyTree.draw`` arguments into drawing objects.

This module applies draw-time style arguments to a base ``TreeStyle``,
projects node coordinates with the requested layout, and returns a
``ToyTreeMark`` rendered on toyplot axes.
"""

import sys
from collections.abc import Mapping
from typing import Any, Tuple, TypeVar

from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian

# from toytree.annotate.src.add_scale_bar import add_axis_scale_bar_to_mark
from toytree.drawing.src.mark_toytree import ToyTreeMark
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

SUPPORTED_DRAW_KWARGS = frozenset(
    {
        "tree_style",
        "axes",
        "height",
        "width",
        "layout",
        "tip_labels",
        "tip_labels_colors",
        "tip_labels_align",
        "tip_labels_angles",
        "tip_labels_style",
        "node_mask",
        "node_labels",
        "node_labels_style",
        "node_sizes",
        "node_hover",
        "node_style",
        "node_colors",
        "node_markers",
        "node_as_edge_data",
        "edge_type",
        "edge_colors",
        "edge_widths",
        "edge_style",
        "edge_align_style",
        "use_edge_lengths",
        "scale_bar",
        "padding",
        "xbaseline",
        "ybaseline",
        "admixture_edges",
        "fixed_order",
        "fixed_position",
        "interior_algorithm",
        "label",
    }
)


def _normalize_extra_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Return draw kwargs with shorthand / extras normalized once."""
    parsed = dict(kwargs)
    extra_obj = parsed.pop("kwargs", {})
    if extra_obj is None:
        extra_kwargs = {}
    elif isinstance(extra_obj, Mapping):
        extra_kwargs = dict(extra_obj)
    else:
        print(
            "Expected draw() internal `kwargs` to be a mapping; "
            "received unsupported value and ignored it.",
            file=sys.stderr,
        )
        extra_kwargs = {}

    ts_key = parsed.pop("ts", None)
    nested_ts_key = extra_kwargs.pop("ts", None)
    if ts_key is None:
        ts_key = nested_ts_key
    elif nested_ts_key is not None and nested_ts_key != ts_key:
        print(
            "Both top-level `ts` and nested `ts` were provided; "
            "using the top-level value and ignoring the nested one.",
            file=sys.stderr,
        )
    style_key = parsed.get("tree_style")
    if style_key is None and ts_key is not None:
        parsed["tree_style"] = ts_key
    elif style_key is not None and ts_key is not None and ts_key != style_key:
        print(
            "Both `tree_style` and shorthand `ts` were provided; "
            "using `tree_style` and ignoring `ts`.",
            file=sys.stderr,
        )

    unknown = set(extra_kwargs)
    for key in list(parsed):
        if key not in SUPPORTED_DRAW_KWARGS:
            unknown.add(key)
            parsed.pop(key)

    if unknown:
        unknown_text = ", ".join(sorted(unknown))
        print(
            "Unrecognized keyword arguments passed to draw() were ignored: "
            f"{unknown_text}. Check docs for current argument names.",
            file=sys.stderr,
        )
    return parsed


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
    kwargs = _normalize_extra_kwargs(kwargs)

    # get a TreeStyle COPY from tree.style or new ts TreeStyle()
    style = get_tree_style_base(tree, tree_style=kwargs.pop("tree_style", None))

    # special handling of tree_style='p' in case Ne is not a feature.
    if style.tree_style == "p" and "Ne" not in tree.features:
        style.edge_widths = None

    # check and expand user-kwargs if provided else base style value
    style = validate_style(tree, style, **kwargs)
    return style


def _get_tree_style_layout_mark(
    tree: ToyTree,
    *,
    fixed_order=None,
    fixed_position=None,
    interior_algorithm: int = 0,
    **kwargs,
) -> tuple[TreeStyle, BaseLayout, ToyTreeMark]:
    """Return draw-resolved style, layout, and mark without creating axes."""
    style = get_tree_style_updated_by_draw_args(tree, **kwargs)
    layout = get_layout(
        tree=tree,
        style=style,
        fixed_order=fixed_order,
        fixed_position=fixed_position,
        interior_algorithm=interior_algorithm,
    )

    if style.tip_labels_angles is None:
        style.tip_labels_angles = layout.angles

    mark = ToyTreeMark(
        ntable=layout.coords,
        ttable=layout.tcoords,
        etable=tree.get_edges("idx"),
        _toytree_source_tree=tree,
        **tree_style_to_css_dict(style),
    )
    return style, layout, mark


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

    style, layout, mark = _get_tree_style_layout_mark(
        tree=tree,
        fixed_order=fixed_order,
        fixed_position=fixed_position,
        interior_algorithm=interior_algorithm,
        **kwargs,
    )

    # create Canvas and Cartesian if they don't yet exist.
    canvas, axes = get_canvas_and_axes(
        axes, mark, kwargs.get("width"), kwargs.get("height")
    )

    # Preserve geometry for circular/fan layouts by fitting equal data scales.
    if style.layout.startswith("c"):
        axes.aspect = "fit-range"

    # add ToyTreeMark to Cartesian axes.
    axes.add_mark(mark)

    # Show axes with a scale bar if requested.
    if mark.scale_bar in (False, None):
        # hide axes if Cartesian is new and scale bar not added.
        if canvas is not None:
            axes.x.show = False
            axes.y.show = False
    else:
        # keep host axes free for plotting and extents management; scale
        # bar is rendered on the hidden companion axes.
        from toytree.annotate.src.add_scale_bar import _normalize_draw_scale_factor

        axes.x.show = False
        axes.y.show = False
        scale_kwargs = {"scale": _normalize_draw_scale_factor(mark.scale_bar)}
        if kwargs.get("padding") is not None:
            scale_kwargs["padding"] = kwargs["padding"]
        tree.annotate.add_axes_scale_bar_to_tree(axes, **scale_kwargs)

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
        print(
            f"`fixed_order` has no effect on `{style.layout}` layout.",
            file=sys.stderr,
        )
    if kwargs.get("fixed_position") is not None:
        print(
            f"`fixed_position` has no effect on `{style.layout}` layout.",
            file=sys.stderr,
        )

    # return circular or unrooted layout
    if style.layout.startswith("c"):
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
