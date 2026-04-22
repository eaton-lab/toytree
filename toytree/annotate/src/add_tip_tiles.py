#!/usr/bin/env python

"""Add tip-aligned tiled annotations to an existing tree drawing."""

from __future__ import annotations

from typing import Any, Mapping, Sequence, Tuple, TypeVar, Union

import numpy as np
from toyplot.mark import Mark

from toytree.annotate.src.checks import (
    assert_tree_matches_mark,
    get_last_toytree_mark_for_tree,
    normalize_tip_mask,
)
from toytree.color import ToyColor
from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian
from toytree.drawing.src.mark_annotation import AnnotationTipTileMark
from toytree.drawing.src.mark_toytree import set_tip_label_extents
from toytree.drawing.src.validate_data import (
    validate_colors,
    validate_numeric,
)
from toytree.drawing.src.validate_utils import substyle_dict_to_css_dict
from toytree.utils import ToytreeError

Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = ["add_tip_tiles"]


def _resolve_auto_depth(
    tmark: Mark,
    show: np.ndarray,
) -> float:
    """Return a default tile depth sized to the current tip-label geometry."""
    if tmark.tip_labels is None or not np.any(show):
        return 10.0

    ntips = len(tmark.tip_labels)
    extents = [np.zeros(tmark.nnodes, dtype=float) for _ in range(4)]
    left, right, top, bottom = set_tip_label_extents(tmark, extents)
    left = left[:ntips][show]
    right = right[:ntips][show]
    top = top[:ntips][show]
    bottom = bottom[:ntips][show]

    layout = str(tmark.layout)
    if layout == "r":
        outward = right
    elif layout == "l":
        outward = -left
    elif layout == "u":
        outward = -top
    elif layout == "d":
        outward = bottom
    elif layout.startswith("c"):
        angles = np.deg2rad(
            np.asarray(tmark.tip_labels_angles[:ntips], dtype=float)[show]
        )
        unit_x = np.cos(angles)
        unit_y = -np.sin(angles)

        # Project each label-bbox corner onto the outward radial vector to get
        # the furthest pixel reach away from the tip anchor.
        projections = np.column_stack(
            (
                left * unit_x + top * unit_y,
                left * unit_x + bottom * unit_y,
                right * unit_x + top * unit_y,
                right * unit_x + bottom * unit_y,
            )
        )
        outward = np.max(projections, axis=1)
    else:
        return 10.0

    return float(np.max(outward) + 15.0)


@add_subpackage_method(AnnotationAPI)
def add_tip_tiles(
    tree: ToyTree,
    axes: Cartesian,
    color: Union[Color, Sequence[Color], tuple, None] = None,
    depth: float | None = None,
    offset: float = 0.0,
    opacity: Union[float, Sequence[float]] = 1.0,
    mask: Union[np.ndarray, Tuple[int, int, int], None, bool] = None,
    style: Mapping[str, Any] | None = None,
    below: bool = True,
) -> Mark:
    """Add tip-aligned rectangular / annular tiles to an existing tree drawing.

    Tip tiles form a continuous strip across the tip span axis with no gaps
    between neighboring tip slots. For rectangular layouts (``r/l/u/d``),
    each tip tile is a rectangle whose slot boundaries are defined by adjacent
    tip midpoints. For circular layouts (``c*``), each tip tile is an annular
    sector bounded by midpoint angles between adjacent tips.

    Parameters
    ----------
    tree : ToyTree
        Tree associated with the existing drawing on ``axes``.
    axes : Cartesian
        Cartesian axes containing a previously drawn tree mark.
    color : Color, sequence, tuple, or None, default=None
        Tile fill color specification. Supports a single color, per-tip colors,
        or feature mapping tuples such as ``("feature", "cmap")``. If None,
        tiles use ``style["fill"]`` when provided, otherwise they default to
        light grey.
    depth : float or None, default=None
        Tile thickness in pixel units. If None, depth is sized to the maximum
        outward tip-label extent on the current tree mark plus 15 pixels. If
        the tree mark has no tip labels, a default depth of 10.0 is used.
    offset : float, default=0.0
        Distance from the tip edge in pixel units along the depth direction.
    opacity : float or sequence, default=1.0
        Fill opacity as a scalar or per-tip sequence.
    mask : bool, tuple[int, int, int], np.ndarray, or None, default=None
        Controls shown tips. Accepted values are:
        - None: show all tips
        - bool: True shows all tips, False shows none
        - tuple: (show_tips, show_internal, show_root) shortcut
        - np.ndarray: boolean array of size ntips
    style : Mapping[str, Any] or None, default=None
        Optional CSS-style mapping for the tile paths. Use this to set
        properties such as ``stroke``, ``stroke-width``,
        ``stroke-dasharray``, or ``fill``. Explicit ``color`` and ``opacity``
        arguments override fill-related entries.
    below : bool, default=True
        If True, place the tile mark below the associated tree mark in
        scenegraph render order.

    Returns
    -------
    Mark
        Added annotation mark.

    Raises
    ------
    ToytreeError
        If inputs are invalid or layout is unsupported.
    """
    tmark = get_last_toytree_mark_for_tree(axes, tree)
    assert_tree_matches_mark(tree, tmark)

    show = normalize_tip_mask(tree, mask)
    depth = _resolve_auto_depth(tmark, show) if depth is None else float(depth)
    offset = float(offset)
    if (not np.isfinite(depth)) or depth <= 0.0:
        raise ToytreeError("depth must be a finite float > 0")
    if not np.isfinite(offset):
        raise ToytreeError("offset must be a finite float")

    layout = str(tmark.layout)
    if not (layout in ("r", "l", "u", "d") or layout.startswith("c")):
        raise ToytreeError(
            "add_tip_tiles supports rectangular layouts (r/l/u/d) and circular "
            "layouts (c*)."
        )

    style = {} if style is None else substyle_dict_to_css_dict(dict(style))
    style.setdefault("stroke", "none")
    colors, fill_color = validate_colors(
        tree,
        key="colors",
        size=tree.ntips,
        style={"colors": color},
    )
    if colors is None:
        if fill_color is not None:
            fill_color = ToyColor(fill_color)
        elif "fill" in style:
            fill_color = ToyColor(style["fill"])
        else:
            fill_color = ToyColor("lightgrey")

    opacity_all = validate_numeric(
        tree,
        key="opacity",
        size=tree.ntips,
        style={"opacity": opacity},
    ).astype(float)

    amark = AnnotationTipTileMark(
        ntable=np.asarray(tmark.ttable[: tree.ntips], dtype=float),
        root_xy=np.asarray(tmark.ntable[tree.treenode.idx], dtype=float),
        layout=layout,
        depth=depth,
        offset=offset,
        show=show,
        colors=colors,
        fill_color=fill_color,
        opacity=opacity_all,
        style=style,
    )
    axes.add_mark(amark)
    if below:
        # Keep render/map relationships synchronized when reordering the mark
        # beneath the tree mark.
        render_targets = axes._scenegraph._relationships["render"]._targets[axes]
        map_x_targets = axes._scenegraph._relationships["map"]._targets[axes.x]
        map_y_targets = axes._scenegraph._relationships["map"]._targets[axes.y]
        if amark in render_targets and tmark in render_targets:
            tree_index = render_targets.index(tmark)
            render_targets.remove(amark)
            render_targets.insert(tree_index, amark)
        if amark in map_x_targets and tmark in map_x_targets:
            tree_index = map_x_targets.index(tmark)
            map_x_targets.remove(amark)
            map_x_targets.insert(tree_index, amark)
        if amark in map_y_targets and tmark in map_y_targets:
            tree_index = map_y_targets.index(tmark)
            map_y_targets.remove(amark)
            map_y_targets.insert(tree_index, amark)
    return amark
