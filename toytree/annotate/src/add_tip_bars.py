#!/usr/bin/env python

"""Add tip-aligned bar annotations to an existing tree drawing."""

from __future__ import annotations

from typing import Any, Mapping, Sequence, Tuple, TypeVar, Union

import numpy as np
from toyplot.mark import Mark

from toytree.annotate.src.add_scale_bar import (
    _install_host_fit_invalidation_add_mark_hook,
)
from toytree.annotate.src.checks import (
    assert_tree_matches_mark,
    finalize_cartesian_with_tip_bar_domains,
    get_last_toytree_mark_for_tree,
    invalidate_cartesian_fit_cache,
    normalize_tip_mask,
)
from toytree.color import ToyColor
from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian
from toytree.drawing.src.mark_annotation import AnnotationTipBarMark
from toytree.drawing.src.mark_toytree import set_marker_extents, set_tip_label_extents
from toytree.style.src.validate_data import validate_colors
from toytree.style.src.validate_utils import substyle_dict_to_css_dict
from toytree.utils import ToytreeError

Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = ["add_tip_bars"]


def _coerce_tip_metric_data(
    tree: ToyTree,
    data: str | Sequence[float] | None,
) -> np.ndarray:
    """Return one finite non-negative tip-sized numeric array in tip order."""
    if data is None:
        arr = np.ones(tree.ntips, dtype=float)
    elif isinstance(data, str):
        arr = np.asarray(tree.get_tip_data(data), dtype=float)
    else:
        arr = np.asarray(data)
        if arr.ndim == 0:
            raise ToytreeError(
                "'data' must be a tip-sized numeric sequence or a tip feature name."
            )
        if arr.ndim != 1:
            raise ToytreeError("'data' must be a one-dimensional tip-sized sequence.")
        if arr.size != tree.ntips:
            raise ToytreeError(
                f"'data' must be size ntips ({tree.ntips}), not {arr.size}."
            )
        try:
            arr = arr.astype(float, copy=False)
        except (TypeError, ValueError) as exc:
            raise ToytreeError("'data' must contain numeric tip data.") from exc

    if arr.size != tree.ntips:
        raise ToytreeError(
            f"'data' must resolve to size ntips ({tree.ntips}), not {arr.size}."
        )
    if np.any(~np.isfinite(arr)):
        raise ToytreeError("'data' must contain only finite numeric data.")
    if np.any(arr < 0.0):
        raise ToytreeError("'data' must be non-negative.")
    return np.asarray(arr, dtype=float)


def _resolve_tip_bar_opacity(
    tree: ToyTree,
    style: Mapping[str, Any],
    opacity: float | Sequence[float] | None,
) -> tuple[dict[str, Any], np.ndarray | None]:
    """Resolve shared or per-tip fill opacity for tip-bar rendering."""
    style = dict(style)
    if opacity is None:
        return style, None

    if np.isscalar(opacity):
        try:
            value = float(opacity)
        except (TypeError, ValueError) as exc:
            raise ToytreeError(
                "'opacity' must be numeric or a tip-sized sequence."
            ) from exc
        if not np.isfinite(value):
            raise ToytreeError("'opacity' must contain only finite numeric values.")
        style["fill-opacity"] = value
        return style, None

    values = np.asarray(opacity)
    if values.ndim == 0:
        raise ToytreeError("'opacity' must be numeric or a tip-sized sequence.")
    if values.ndim != 1:
        raise ToytreeError("'opacity' sequence must be one-dimensional.")
    if values.size != tree.ntips:
        raise ToytreeError(
            f"'opacity' sequence must be size ntips ({tree.ntips}), not {values.size}."
        )
    try:
        values = values.astype(float, copy=False)
    except (TypeError, ValueError) as exc:
        raise ToytreeError("'opacity' must contain numeric values.") from exc
    if np.any(~np.isfinite(values)):
        raise ToytreeError("'opacity' must contain only finite numeric values.")
    style.pop("fill-opacity", None)
    return style, np.asarray(values, dtype=float)


def _insert_mark_below_tree(axes: Cartesian, tree_mark: Mark, mark: Mark) -> None:
    """Move an added annotation mark beneath the tree mark in scenegraph order."""
    render_targets = axes._scenegraph._relationships["render"]._targets[axes]
    map_x_targets = axes._scenegraph._relationships["map"]._targets[axes.x]
    map_y_targets = axes._scenegraph._relationships["map"]._targets[axes.y]
    if mark in render_targets and tree_mark in render_targets:
        tree_index = render_targets.index(tree_mark)
        render_targets.remove(mark)
        render_targets.insert(tree_index, mark)
    if mark in map_x_targets and tree_mark in map_x_targets:
        tree_index = map_x_targets.index(tree_mark)
        map_x_targets.remove(mark)
        map_x_targets.insert(tree_index, mark)
    if mark in map_y_targets and tree_mark in map_y_targets:
        tree_index = map_y_targets.index(tree_mark)
        map_y_targets.remove(mark)
        map_y_targets.insert(tree_index, mark)


def _project_bbox_outward(
    left: np.ndarray,
    right: np.ndarray,
    top: np.ndarray,
    bottom: np.ndarray,
    unit_x: np.ndarray,
    unit_y: np.ndarray,
) -> np.ndarray:
    """Return the furthest bbox reach along one outward unit vector."""
    projections = np.column_stack(
        (
            left * unit_x + top * unit_y,
            left * unit_x + bottom * unit_y,
            right * unit_x + top * unit_y,
            right * unit_x + bottom * unit_y,
        )
    )
    return np.max(projections, axis=1)


def _get_tip_outward_unit_vectors(
    tree: ToyTree,
    tmark: Mark,
    show: np.ndarray,
    use_label_angles: bool,
) -> tuple[np.ndarray, np.ndarray]:
    """Return outward unit vectors for shown tips in circular layouts."""
    ntips = tree.ntips
    if use_label_angles and getattr(tmark, "tip_labels_angles", None) is not None:
        angles = np.deg2rad(np.asarray(tmark.tip_labels_angles[:ntips], dtype=float))
        angles = angles[show]
        return np.cos(angles), -np.sin(angles)

    root_xy = np.asarray(tmark.ntable[tree.treenode.idx], dtype=float)
    tips_xy = np.asarray(tmark.ttable[:ntips], dtype=float)[show]
    vectors = tips_xy - root_xy[None, :]
    norms = np.linalg.norm(vectors, axis=1)
    norms[norms == 0.0] = 1.0
    return vectors[:, 0] / norms, vectors[:, 1] / norms


def _resolve_outward_extent(
    tree: ToyTree,
    tmark: Mark,
    show: np.ndarray,
    left: np.ndarray,
    right: np.ndarray,
    top: np.ndarray,
    bottom: np.ndarray,
    *,
    use_label_angles: bool,
) -> np.ndarray:
    """Return outward extent for shown tips in the current tree layout."""
    layout = str(tmark.layout)
    if layout == "r":
        return right
    if layout == "l":
        return -left
    if layout == "u":
        return -top
    if layout == "d":
        return bottom
    if layout.startswith("c"):
        unit_x, unit_y = _get_tip_outward_unit_vectors(
            tree,
            tmark,
            show,
            use_label_angles,
        )
        return _project_bbox_outward(left, right, top, bottom, unit_x, unit_y)
    return np.zeros(int(np.sum(show)), dtype=float)


def _resolve_tip_overlay_auto_offset(
    tree: ToyTree,
    tmark: Mark,
    show: np.ndarray,
) -> float:
    """Return a default outward gap from the rendered tree tip geometry."""
    if not np.any(show):
        return 10.0

    ntips = tree.ntips
    if tmark.tip_labels is not None:
        extents = [np.zeros(tmark.nnodes, dtype=float) for _ in range(4)]
        left, right, top, bottom = set_tip_label_extents(tmark, extents)
        outward = _resolve_outward_extent(
            tree,
            tmark,
            show,
            left[:ntips][show],
            right[:ntips][show],
            top[:ntips][show],
            bottom[:ntips][show],
            use_label_angles=True,
        )
    else:
        extents = [np.zeros(tmark.nnodes, dtype=float) for _ in range(4)]
        left, right, top, bottom = set_marker_extents(tmark, extents)
        outward = _resolve_outward_extent(
            tree,
            tmark,
            show,
            left[:ntips][show],
            right[:ntips][show],
            top[:ntips][show],
            bottom[:ntips][show],
            use_label_angles=False,
        )

    return float(np.max(np.maximum(outward, 0.0)) + 10.0)


def _build_tip_hover_labels(tree: ToyTree, values: np.ndarray) -> np.ndarray:
    """Return default hover text in tip order for one tip-bar mark."""
    return np.asarray(
        [f"{tree[idx].name}: {value:.12g}" for idx, value in enumerate(values)],
        dtype=str,
    )


@add_subpackage_method(AnnotationAPI)
def add_tip_bars(
    tree: ToyTree,
    axes: Cartesian,
    data: str | Sequence[float] | None = None,
    color: Union[Color, Sequence[Color], tuple, None] = None,
    depth: float = 100.0,
    offset: float | None = None,
    width: float = 0.8,
    opacity: Union[float, Sequence[float], None] = None,
    mask: Union[np.ndarray, Tuple[int, int, int], None, bool] = None,
    style: Mapping[str, Any] | None = None,
    below: bool = True,
    hover: bool = True,
) -> Mark:
    """Add tip-aligned quantitative bars to an existing tree drawing.

    Bars occupy the tip slots defined by neighboring tip midpoints, just
    like :func:`add_tip_tiles`, but each tip receives its own outward bar
    length based on the corresponding numeric value. Values are normalized
    to the largest tip value so that the maximum visible bar reaches
    ``depth`` pixels from the baseline.

    Parameters
    ----------
    tree : ToyTree
        Tree associated with the existing drawing on ``axes``.
    axes : Cartesian
        Cartesian axes containing a previously drawn tree mark.
    data : str, sequence of float, or None, default=None
        Tip feature name or tip-sized numeric sequence to render as bar
        lengths. Values must be finite and non-negative. When None, bars use
        unit data so every visible tip reaches the full requested ``depth``
        and companion mark scale bars use a ``0..1`` domain.
    color : Color, sequence, tuple, or None, default=None
        Bar fill color specification. Supports a single color, per-tip
        colors, or feature mapping tuples such as ``("feature", "cmap")``.
        If None, bars use ``style["fill"]`` when provided, otherwise they
        default to light grey.
    depth : float, default=100.0
        Maximum bar length in pixel units after normalization.
    offset : float or None, default=None
        Distance from the tip edge in pixel units to the bar baseline. When
        None, the gap is set to the furthest outward shown tip-label extent
        plus 10 pixels, or to the furthest shown tip-node extent plus 10
        pixels when the tree drawing has no tip labels.
    width : float, default=0.8
        Proportion of each tip slot occupied by the bar, from ``0`` to ``1``.
        Values below ``1`` leave centered gaps between neighboring bars.
    opacity : float, sequence, or None, default=None
        Bar fill opacity. When None, bars keep ``style["fill-opacity"]`` if
        provided and otherwise use the default visible fill opacity. A scalar
        sets one shared fill opacity for all bars. A tip-sized sequence
        applies per-bar fill opacity and overrides any shared style opacity.
    mask : bool, tuple[int, int, int], np.ndarray, or None, default=None
        Controls shown tips. Accepted values are:
        - None: show all tips
        - bool: True shows all tips, False shows none
        - tuple: (show_tips, show_internal, show_root) shortcut
        - np.ndarray: boolean array of size ntips
    style : Mapping[str, Any] or None, default=None
        Optional CSS-style mapping for the bar paths. Use this to set
        properties such as ``stroke``, ``stroke-width``,
        ``stroke-dasharray``, ``fill``, or ``fill-opacity``. Explicit
        ``color`` and ``opacity`` arguments override fill-related entries.
    below : bool, default=True
        If True, place the bar mark below the associated tree mark in
        scenegraph render order.
    hover : bool, default=True
        If True, show ``"{name}: {value}"`` tooltips for visible bars using
        the anchored tip-node name and the raw data value.

    Returns
    -------
    Mark
        Added annotation mark.

    Raises
    ------
    ToytreeError
        If inputs are invalid or layout is unsupported.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, _ = tree.draw(layout="r")
    >>> tree.annotate.add_tip_bars(
    ...     axes,
    ...     data=[0, 1, 2, 3, 4, 5],
    ...     offset=None,
    ...     style={"stroke": "black", "stroke-width": 1.5},
    ... )
    >>> canvas, axes, _ = tree.draw();
    >>> tree.annotate.add_tip_bars(
    ...     axes,
    ...     data="dist",
    ...     offset=0.0,
    ...     opacity=0.5,
    ...     color="violet",
    ...     below=True,
    ... )
    """
    tmark = get_last_toytree_mark_for_tree(axes, tree)
    assert_tree_matches_mark(tree, tmark)

    depth = float(depth)
    width = float(width)
    if (not np.isfinite(depth)) or depth <= 0.0:
        raise ToytreeError("depth must be a finite float > 0")
    if (not np.isfinite(width)) or width <= 0.0 or width > 1.0:
        raise ToytreeError("width must be a finite float in the interval (0, 1].")

    layout = str(tmark.layout)
    if not (layout in ("r", "l", "u", "d") or layout.startswith("c")):
        raise ToytreeError(
            "add_tip_bars supports rectangular layouts (r/l/u/d) and circular "
            "layouts (c*)."
        )

    show = normalize_tip_mask(tree, mask)
    offset = (
        _resolve_tip_overlay_auto_offset(tree, tmark, show)
        if offset is None
        else float(offset)
    )
    if not np.isfinite(offset):
        raise ToytreeError("offset must be a finite float")

    raw_data = _coerce_tip_metric_data(tree, data)
    max_value = float(np.max(raw_data))
    if max_value == 0.0:
        bar_depths = np.zeros(tree.ntips, dtype=float)
    else:
        bar_depths = (raw_data / max_value) * depth

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

    style, opacity_all = _resolve_tip_bar_opacity(tree, style, opacity)
    hover_labels = _build_tip_hover_labels(tree, raw_data) if hover else None

    amark = AnnotationTipBarMark(
        ntable=np.asarray(tmark.ttable[: tree.ntips], dtype=float),
        root_xy=np.asarray(tmark.ntable[tree.treenode.idx], dtype=float),
        host_tree_mark=tmark,
        layout=layout,
        offset=offset,
        width=width,
        show=show,
        values=np.asarray(raw_data, dtype=float),
        value_min=0.0,
        value_max=max_value,
        max_bar_depth=depth,
        bar_depths=np.asarray(bar_depths, dtype=float),
        colors=colors,
        fill_color=fill_color,
        opacity=opacity_all,
        hover_labels=hover_labels,
        style=style,
    )
    axes.add_mark(amark)
    if below:
        _insert_mark_below_tree(axes, tmark, amark)
    if not getattr(axes, "_toytree_companion_add_mark_hook_installed", False):
        invalidate_cartesian_fit_cache(axes)
        finalize_cartesian_with_tip_bar_domains(axes)
        _install_host_fit_invalidation_add_mark_hook(axes)
    return amark
