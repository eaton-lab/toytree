#!/usr/bin/env python

"""Draw ``MultiTree`` collections as a grid of tree subplots."""

from __future__ import annotations

from math import isfinite
from numbers import Integral, Real
from typing import Optional, Sequence, TypeVar

from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian
from toyplot.mark import Mark

import toytree
from toytree.annotate import add_axes_scale_bar
from toytree.drawing.src.draw_toytree import (
    _get_tree_style_layout_mark,
    _normalize_extra_kwargs,
)
from toytree.drawing.src.setup_canvas import (
    get_circular_width_and_height,
    get_linear_width_and_height,
)
from toytree.drawing.src.setup_grid import (
    AUTO_GRID_MAX_HEIGHT,
    AUTO_GRID_MAX_WIDTH,
    Grid,
    get_fallback_grid_canvas_size,
    get_grid_size_spec,
)
from toytree.style import get_base_tree_style_by_name
from toytree.utils import ToytreeError

MultiTree = TypeVar("MultiTree")


def _validate_shape(shape: Sequence[int]) -> tuple[int, int]:
    """Return validated grid shape as positive integer rows and columns."""
    if isinstance(shape, (str, bytes)):
        raise ToytreeError("shape must be a 2-item sequence of positive integers.")
    try:
        if len(shape) != 2:
            raise ToytreeError("shape must be a 2-item sequence of positive integers.")
    except TypeError as exc:
        raise ToytreeError(
            "shape must be a 2-item sequence of positive integers."
        ) from exc

    nrows, ncols = shape
    for value, name in ((nrows, "shape[0]"), (ncols, "shape[1]")):
        if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
            raise ToytreeError(f"{name} must be a positive integer.")
    return int(nrows), int(ncols)


def _validate_size(value: float | int | None, name: str) -> float | int | None:
    """Return validated positive canvas size or ``None``."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ToytreeError(f"{name} must be a finite number > 0.")
    fval = float(value)
    if (not isfinite(fval)) or (fval <= 0.0):
        raise ToytreeError(f"{name} must be a finite number > 0.")
    return value


def _validate_padding(value: float | int | None) -> float | int:
    """Return validated non-negative subplot padding."""
    if value is None:
        return 10
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ToytreeError("padding must be a finite number >= 0.")
    fval = float(value)
    if (not isfinite(fval)) or (fval < 0.0):
        raise ToytreeError("padding must be a finite number >= 0.")
    return value


def _validate_margin(
    margin: float | Sequence[float] | None,
) -> float | tuple[float, float, float, float] | None:
    """Return validated scalar or 4-item subplot margin."""
    if margin is None:
        return None
    if isinstance(margin, bool):
        raise ToytreeError("margin must be a finite number or a 4-item numeric tuple.")
    if isinstance(margin, Real):
        fval = float(margin)
        if not isfinite(fval):
            raise ToytreeError(
                "margin must be a finite number or a 4-item numeric tuple."
            )
        return fval
    if isinstance(margin, (str, bytes)):
        raise ToytreeError("margin must be a finite number or a 4-item numeric tuple.")
    try:
        raw_values = tuple(margin)
    except TypeError as exc:
        raise ToytreeError(
            "margin must be a finite number or a 4-item numeric tuple."
        ) from exc
    if any(isinstance(value, bool) for value in raw_values):
        raise ToytreeError("margin must be a finite number or a 4-item numeric tuple.")
    try:
        values = tuple(float(i) for i in raw_values)
    except ValueError as exc:
        raise ToytreeError(
            "margin must be a finite number or a 4-item numeric tuple."
        ) from exc
    if len(values) != 4 or not all(isfinite(i) for i in values):
        raise ToytreeError("margin must be a finite number or a 4-item numeric tuple.")
    return values


def _normalize_tree_indices(
    mtree: MultiTree,
    idxs: Optional[Sequence[int]],
    limit: int,
) -> list[int]:
    """Return validated tree indices truncated to the grid capacity."""
    ntrees = len(mtree.treelist)
    if idxs is None:
        return list(range(min(limit, ntrees)))

    if isinstance(idxs, Integral) and not isinstance(idxs, bool):
        raw_indices = [int(idxs)]
    else:
        if isinstance(idxs, (str, bytes)):
            raise ToytreeError("idxs must be an int or an iterable of ints.")
        try:
            raw_indices = list(idxs)
        except TypeError as exc:
            raise ToytreeError("idxs must be an int or an iterable of ints.") from exc

    indices = []
    for raw in raw_indices:
        if isinstance(raw, bool) or not isinstance(raw, Integral):
            raise ToytreeError("idxs must contain only integer values.")
        idx = int(raw)
        if not -ntrees <= idx < ntrees:
            raise ToytreeError(
                f"idxs contains out-of-range tree index {idx}. "
                f"Valid range is {-ntrees}..{ntrees - 1}."
            )
        indices.append(idx)
    return indices[:limit]


def _resolve_layout(kwargs: dict) -> str:
    """Return layout key used for grid sizing."""
    layout = kwargs.get("layout")
    if layout is not None:
        return layout

    style_key = kwargs.get("ts")
    if style_key is None:
        style_key = kwargs.get("tree_style")
    if style_key is not None:
        return get_base_tree_style_by_name(style_key).layout
    return "r"


def _clamp(value: float, lower: float, upper: float) -> float:
    """Return ``value`` clamped to inclusive numeric bounds."""
    return max(lower, min(upper, value))


def _get_mark_preferred_size(mark: Mark) -> tuple[float, float]:
    """Return single-tree preferred canvas size for a rendered mark."""
    if _is_linear_layout(mark.layout):
        width, height = get_linear_width_and_height(mark)
    else:
        width, height = get_circular_width_and_height(mark)
    return float(width), float(height)


def _get_soft_capped_grid_extent(
    cell_size: float,
    nslots: int,
    base_cell: float,
    soft_cap: float,
) -> float:
    """Return a soft-capped total grid extent for one dimension."""
    total = cell_size * nslots
    if total <= soft_cap:
        return total
    return max(base_cell, soft_cap / nslots) * nslots


def _get_auto_grid_canvas_size(
    treelist: Sequence,
    draw_kwargs: dict,
    nrows: int,
    ncols: int,
    layout: str,
) -> tuple[float, float]:
    """Return extent-aware default canvas size for rendered trees."""
    if not treelist:
        return get_fallback_grid_canvas_size(nrows, ncols, layout)

    spec = get_grid_size_spec(layout)
    cell_width = spec.base_cell_width
    cell_height = spec.base_cell_height

    # Add only the excess beyond compact single-tree defaults so
    # ordinary rooted grids stay near the current baseline size.
    for tree in treelist:
        _, _, mark = _get_tree_style_layout_mark(tree, **draw_kwargs)
        pref_width, pref_height = _get_mark_preferred_size(mark)
        cell_width = max(
            cell_width,
            _clamp(
                spec.base_cell_width + max(0.0, pref_width - spec.ref_mark_width),
                spec.base_cell_width,
                spec.max_cell_width,
            ),
        )
        cell_height = max(
            cell_height,
            _clamp(
                spec.base_cell_height + max(0.0, pref_height - spec.ref_mark_height),
                spec.base_cell_height,
                spec.max_cell_height,
            ),
        )

    width = _get_soft_capped_grid_extent(
        cell_width,
        ncols,
        spec.base_cell_width,
        AUTO_GRID_MAX_WIDTH,
    )
    height = _get_soft_capped_grid_extent(
        cell_height,
        nrows,
        spec.base_cell_height,
        AUTO_GRID_MAX_HEIGHT,
    )
    return width, height


def _apply_tip_labels_style_defaults(draw_kwargs: dict) -> None:
    """Apply default tip-label styles without mutating caller-owned data."""
    if draw_kwargs.get("tip_labels") is False and "tip_labels_style" not in draw_kwargs:
        return
    tip_labels_style = draw_kwargs.get("tip_labels_style")
    if tip_labels_style is None:
        tip_labels_style = {}
    else:
        tip_labels_style = dict(tip_labels_style)
    tip_labels_style.setdefault("-toyplot-anchor-shift", "10px")
    tip_labels_style.setdefault("font-size", "10px")
    draw_kwargs["tip_labels_style"] = tip_labels_style


def _normalize_labels(
    label: str | Sequence[str | None] | None,
    ntrees: int,
) -> list[str | None]:
    """Return per-tree axis labels in render order."""
    if label is None:
        return [None] * ntrees
    if isinstance(label, str):
        return [label] * ntrees
    if isinstance(label, (bytes, bytearray)):
        raise ToytreeError("label must be a str or a sequence of labels.")

    try:
        labels = list(label)
    except TypeError as exc:
        raise ToytreeError("label must be a str or a sequence of labels.") from exc

    if len(labels) != ntrees:
        raise ToytreeError(
            "label sequence length must match the number of rendered trees."
        )
    return labels


def _get_fixed_order_cache_key(
    treelist: Sequence,
) -> tuple[tuple[object, tuple[str, ...]], ...]:
    """Return a cache key for inferred fixed-order tip labels."""
    return tuple(
        (
            tree.get_topology_id(include_root=True),
            tuple(tree.get_tip_labels()),
        )
        for tree in treelist
    )


def _resolve_fixed_order(
    mtree: MultiTree,
    treelist: Sequence,
    fixed_order: bool | Sequence[str] | None,
) -> Sequence[str] | None:
    """Return explicit or inferred fixed-order tip labels for rendering."""
    if (fixed_order is None) or (fixed_order is False):
        return None
    if fixed_order is True:
        if not treelist:
            return None
        if len(treelist) == 1:
            return treelist[0].get_tip_labels()

        cache_key = _get_fixed_order_cache_key(treelist)
        cache = mtree._draw_fixed_order_cache
        if cache_key not in cache:
            cache[cache_key] = list(
                toytree.MultiTree(list(treelist)).get_consensus_tree().get_tip_labels()
            )
        return cache[cache_key]

    return fixed_order


def _is_linear_layout(layout: str) -> bool:
    """Return True if layout is one of the four linear projections."""
    return layout in ("r", "l", "u", "d")


def _hide_axes(axis: Cartesian) -> None:
    """Hide host Cartesian axes for tree-grid cells."""
    axis.x.show = False
    axis.y.show = False


def _get_time_axis(layout: str) -> str:
    """Return axis used to encode tree depth in a linear layout."""
    return "y" if layout in ("u", "d") else "x"


def _get_shared_axis_depth(mark) -> float:
    """Return rendered tree depth span on the layout time axis."""
    axis = _get_time_axis(mark.layout)
    domain = mark.domain(axis)
    return float(abs(domain[1] - domain[0]))


def _get_shared_axis_range(mark, depth: float) -> tuple[float, float]:
    """Return tree-unit range for a shared linear scale bar."""
    if mark.layout in ("r", "u"):
        return (-depth, 0.0)
    return (0.0, depth)


def _apply_shared_axis_domain(axis: Cartesian, mark, depth: float) -> None:
    """Fix host time-axis domain to a shared rendered depth span."""
    if mark.layout == "d":
        axis.y.domain.min = mark.ybaseline
        axis.y.domain.max = mark.ybaseline + depth
    elif mark.layout == "u":
        axis.y.domain.min = mark.ybaseline - depth
        axis.y.domain.max = mark.ybaseline
    elif mark.layout == "l":
        axis.x.domain.min = mark.xbaseline
        axis.x.domain.max = mark.xbaseline + depth
    else:
        axis.x.domain.min = mark.xbaseline - depth
        axis.x.domain.max = mark.xbaseline


def _update_shared_scale_bar(tree, axis: Cartesian, mark, depth: float) -> None:
    """Sync visible shared scale bars to the rendered shared depth span."""
    if mark.scale_bar in (False, None):
        return
    add_axes_scale_bar(
        tree,
        axis,
        range=_get_shared_axis_range(mark, depth),
        scale=mark.scale_bar,
    )


def draw_multitree(
    mtree: MultiTree,
    shape: tuple[int, int] = (1, 4),
    shared_axes: bool = False,
    idxs: Optional[Sequence[int]] = None,
    width: float | int | None = None,
    height: float | int | None = None,
    margin: float | tuple[float, float, float, float] | None = None,
    fixed_order: bool | Sequence[str] | None = None,
    label: str | Sequence[str | None] | None = None,
    **kwargs,
) -> tuple[Canvas, list[Cartesian], list[Mark]]:
    """Return a grid drawing of trees from a ``MultiTree``.

    Parameters
    ----------
    mtree : MultiTree
        Collection of trees to draw.
    shape : tuple[int, int], default=(1, 4)
        Requested grid shape as ``(nrows, ncols)``.
    shared_axes : bool, default=False
        If True, linear layouts share the same rendered tree-depth span.
        Visible scale bars are still controlled by ``scale_bar``.
    idxs : int or Sequence[int] or None, default=None
        Optional tree indices to draw. If more indices are supplied than
        grid cells, extra indices are ignored. ``idxs=[]`` returns a blank
        grid with no marks.
    width : float or int or None, default=None
        Canvas width in px. Must be > 0 when provided. If omitted,
        width is inferred from the rendered tree extents for the
        selected layout and then soft-capped for the full grid.
    height : float or int or None, default=None
        Canvas height in px. Must be > 0 when provided. If omitted,
        height is inferred from the rendered tree extents for the
        selected layout and then soft-capped for the full grid. If
        either dimension is provided explicitly, only the missing
        dimension is auto-sized.
    margin : float or tuple[float, float, float, float] or None, default=None
        Per-subplot margin in px, either as a single scalar or
        ``(top, right, bottom, left)``.
    fixed_order : bool or Sequence[str] or None, default=None
        If True, infer a shared tip order from the selected trees and reuse
        cached results on repeated draws of the same tree selection. If a
        sequence is provided, it is forwarded directly to each rendered tree.
    label : str or Sequence[str or None] or None, default=None
        Axis label text for rendered trees. A scalar string is broadcast to
        rendered trees; a sequence must match the number of rendered trees.
    **kwargs : dict
        Additional ``ToyTree.draw()`` arguments applied to every rendered
        tree. ``padding`` must be a finite number >= 0 when provided.

    Returns
    -------
    tuple[Canvas, list[Cartesian], list[Mark]]
        Canvas, full grid axes list, and marks for the trees actually drawn.
        ``len(axes)`` always equals ``shape[0] * shape[1]`` while
        ``len(marks)`` equals the number of rendered trees.

    Raises
    ------
    ToytreeError
        Raised if ``shape``, ``idxs``, ``width``, ``height``, ``margin``, or
        ``padding`` are invalid, if deprecated ``nrows`` / ``ncols`` kwargs
        are used, or if ``shared_axes=True`` is requested on a non-linear
        layout.

    Examples
    --------
    >>> trees = [toytree.rtree.unittree(10) for _ in range(10)]
    >>> mtre = toytree.mtree(trees)
    >>> mtre.draw(shape=(2, 3), width=800, edge_widths=4)
    """
    if ("nrows" in kwargs) or ("ncols" in kwargs):
        raise ToytreeError(
            "nrows and ncols args are deprecated. Use shape=(nrows, ncols)."
        )

    width = _validate_size(width, "width")
    height = _validate_size(height, "height")
    margin = _validate_margin(margin)
    nrows, ncols = _validate_shape(shape)
    ncells = nrows * ncols
    tidx = _normalize_tree_indices(mtree=mtree, idxs=idxs, limit=ncells)
    treelist = [mtree.treelist[i] for i in tidx]

    draw_kwargs = kwargs.copy()
    draw_kwargs = _normalize_extra_kwargs(draw_kwargs)
    labels = _normalize_labels(label, len(treelist))
    resolved_fixed_order = _resolve_fixed_order(mtree, treelist, fixed_order)
    if resolved_fixed_order is not None:
        draw_kwargs["fixed_order"] = resolved_fixed_order
    else:
        draw_kwargs.pop("fixed_order", None)

    _apply_tip_labels_style_defaults(draw_kwargs)
    layout = _resolve_layout(draw_kwargs)
    if shared_axes and not _is_linear_layout(layout):
        raise ToytreeError("shared_axes=True is supported only for linear layouts.")

    padding = _validate_padding(draw_kwargs.get("padding", 10))
    if "padding" in draw_kwargs:
        draw_kwargs["padding"] = padding
    scale_bar = draw_kwargs.get("scale_bar", False)

    if (width is None) or (height is None):
        auto_width, auto_height = _get_auto_grid_canvas_size(
            treelist,
            draw_kwargs,
            nrows,
            ncols,
            layout,
        )
        if width is None:
            width = auto_width
        if height is None:
            height = auto_height

    grid = Grid(nrows, ncols, width, height, layout, margin, padding, scale_bar)
    canvas = grid.canvas

    marks: list[Mark] = []
    rendered = []

    for idx, tree in enumerate(treelist):
        axis = grid.axes[idx]
        _, _, mark = tree.draw(axes=axis, **draw_kwargs)
        if labels[idx] is not None:
            axis.label.text = labels[idx]
        marks.append(mark)
        rendered.append((idx, tree, mark))

    if shared_axes and treelist:
        shared_depth = max(_get_shared_axis_depth(mark) for _, _, mark in rendered)
        for idx, tree, mark in rendered:
            _apply_shared_axis_domain(grid.axes[idx], mark, shared_depth)
            _update_shared_scale_bar(tree, grid.axes[idx], mark, shared_depth)

    # ToyTree.draw() hides axes automatically only when it creates the host
    # axes itself. MultiTree.draw() always supplies existing axes, so host
    # axes must be hidden here to keep the grid cells visually blank.
    if scale_bar in (False, None):
        for idx in range(len(treelist)):
            _hide_axes(grid.axes[idx])
    for idx in range(len(treelist), ncells):
        _hide_axes(grid.axes[idx])

    return canvas, grid.axes, marks


if __name__ == "__main__":
    trees = [toytree.rtree.unittree(5) for _ in range(10)]
    mtree = toytree.mtree(trees)
    c, a, m = draw_multitree(mtree, shape=(2, 8))
    toytree.utils.show([c], tmpdir="~")
