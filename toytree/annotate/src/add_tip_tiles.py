#!/usr/bin/env python

"""Add tip-aligned tiled annotations to an existing tree drawing."""

from __future__ import annotations

from typing import Sequence, Tuple, TypeVar, Union

import numpy as np
from toyplot.mark import Mark

from toytree.annotate.src.checks import (
    assert_tree_matches_mark,
    get_last_toytree_mark,
    normalize_tip_mask,
)
from toytree.color import ToyColor
from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian
from toytree.drawing.src.mark_annotation import AnnotationTipTileMark
from toytree.style.src.validate_data import (
    validate_colors,
    validate_numeric,
)
from toytree.utils import ToytreeError

Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = ["add_tip_tiles"]


@add_subpackage_method(AnnotationAPI)
def add_tip_tiles(
    tree: ToyTree,
    axes: Cartesian,
    color: Union[Color, Sequence[Color], tuple, None] = None,
    depth: float = 10.0,
    offset: float = 0.0,
    opacity: Union[float, Sequence[float]] = 1.0,
    mask: Union[np.ndarray, Tuple[int, int, int], None] = None,
    stroke: Color | None = None,
    below: bool = False,
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
        or feature mapping tuples such as ``("feature", "cmap")``.
    depth : float, default=10.0
        Tile thickness in pixel units.
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
    stroke : Color or None, default=None
        Optional stroke color for tile outlines. If None, outlines are omitted.
    below : bool, default=False
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
    tmark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, tmark)

    depth = float(depth)
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

    colors, fill_color = validate_colors(
        tree,
        key="colors",
        size=tree.ntips,
        style={"colors": color},
    )
    if colors is None:
        fill_color = (
            ToyColor(fill_color) if fill_color is not None else ToyColor("#262626")
        )

    opacity_all = validate_numeric(
        tree,
        key="opacity",
        size=tree.ntips,
        style={"opacity": opacity},
    ).astype(float)

    show = normalize_tip_mask(tree, mask)

    stroke_color = None if stroke is None else ToyColor(stroke)

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
        stroke_color=stroke_color,
        style={},
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
