#!/usr/bin/env python

"""Add tip-anchored path annotations to an existing tree drawing."""

from __future__ import annotations

from typing import Any, Mapping, Sequence, Tuple, TypeVar, Union

import numpy as np
from toyplot.mark import Mark

from toytree.annotate.src.add_scale_bar import (
    _install_host_fit_invalidation_add_mark_hook,
)
from toytree.annotate.src.add_tip_bars import (
    _coerce_tip_metric_data,
    _insert_mark_below_tree,
    _resolve_tip_overlay_auto_offset,
)
from toytree.annotate.src.checks import (
    assert_tree_matches_mark,
    finalize_cartesian_with_tip_bar_domains,
    get_last_toytree_mark,
    invalidate_cartesian_fit_cache,
    normalize_tip_mask,
)
from toytree.color import ToyColor
from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian
from toytree.drawing.src.mark_annotation import AnnotationTipPathMark
from toytree.style.src.validate_data import validate_colors
from toytree.style.src.validate_utils import substyle_dict_to_css_dict
from toytree.utils import ToytreeError

__all__ = ["add_tip_paths"]

Color = TypeVar("Color", str, tuple, np.ndarray)


def _coerce_tip_path_spans(
    tree: ToyTree,
    spans: Sequence[float] | None,
) -> np.ndarray:
    """Return one finite tip-sized array of absolute end positions."""
    arr = np.asarray(spans)
    if arr.ndim == 0:
        raise ToytreeError("'spans' must be a tip-sized numeric sequence.")
    if arr.ndim != 1:
        raise ToytreeError("'spans' must be a one-dimensional tip-sized sequence.")
    if arr.size != tree.ntips:
        raise ToytreeError(
            f"'spans' must be size ntips ({tree.ntips}), not {arr.size}."
        )
    try:
        arr = arr.astype(float, copy=False)
    except (TypeError, ValueError) as exc:
        raise ToytreeError("'spans' must contain numeric tip data.") from exc
    if np.any(~np.isfinite(arr)):
        raise ToytreeError("'spans' must contain only finite numeric data.")
    return np.asarray(arr, dtype=float)


def _resolve_tip_path_bezier_fractions(
    bezier_fractions: tuple[float, float] | None,
) -> tuple[float, float]:
    """Return validated cubic control fractions for tip-path rendering."""
    if bezier_fractions is None:
        return (0.25, 0.75)
    if not isinstance(bezier_fractions, tuple):
        raise ToytreeError("'bezier_fractions' must be None or a tuple of two floats.")
    if len(bezier_fractions) != 2:
        raise ToytreeError("'bezier_fractions' must contain exactly two floats.")
    try:
        fractions = np.asarray(bezier_fractions, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ToytreeError(
            "'bezier_fractions' must contain only numeric values."
        ) from exc
    if np.any(~np.isfinite(fractions)):
        raise ToytreeError(
            "'bezier_fractions' must contain only finite numeric values."
        )
    start_fraction = float(fractions[0])
    end_fraction = float(fractions[1])
    if not (
        0.0 <= start_fraction <= 1.0
        and 0.0 <= end_fraction <= 1.0
        and start_fraction < end_fraction
    ):
        raise ToytreeError("'bezier_fractions' must satisfy 0 <= first < second <= 1.")
    return (start_fraction, end_fraction)


def _build_tip_path_hover_labels(
    tree: ToyTree,
    values: np.ndarray | None,
    hover: bool | str | Sequence[str] | None,
) -> np.ndarray | None:
    """Return hover labels in tip order for one tip-path mark."""
    if hover is None:
        return None
    if isinstance(hover, (bool, np.bool_)):
        if not bool(hover):
            return None
        if values is None:
            labels = [tree[idx].name for idx in range(tree.ntips)]
        else:
            labels = [
                f"{tree[idx].name}: {value:.12g}" for idx, value in enumerate(values)
            ]
        return np.asarray(labels, dtype=str)

    if isinstance(hover, str):
        try:
            values = np.asarray(tree.get_tip_data(hover), dtype=object)
        except Exception as exc:  # pragma: no cover - precise error type varies
            raise ToytreeError(
                f"'hover' feature {hover!r} could not be resolved for tip paths."
            ) from exc
        if values.size != tree.ntips:
            raise ToytreeError(
                f"'hover' feature {hover!r} must resolve to size ntips ({tree.ntips})."
            )
        return np.asarray(values, dtype=str)

    labels = np.asarray(hover)
    if labels.ndim == 0:
        raise ToytreeError(
            "'hover' must be bool, a feature name, or a tip-sized label sequence."
        )
    if labels.ndim != 1:
        raise ToytreeError("'hover' label sequence must be one-dimensional.")
    if labels.size != tree.ntips:
        raise ToytreeError(
            "'hover' label sequence must be size "
            f"ntips ({tree.ntips}), not {labels.size}."
        )
    return np.asarray(labels, dtype=str)


def _resolve_tip_path_opacity(
    tree: ToyTree,
    style: Mapping[str, Any],
    opacity: float | Sequence[float] | None,
) -> tuple[dict[str, Any], np.ndarray | None]:
    """Resolve shared or per-tip stroke opacity for tip-path rendering."""
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
        style["stroke-opacity"] = value
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
    style.pop("stroke-opacity", None)
    return style, np.asarray(values, dtype=float)


@add_subpackage_method(AnnotationAPI)
def add_tip_paths(
    tree: ToyTree,
    axes: Cartesian,
    data: str | Sequence[float] | None = None,
    color: Union[Color, Sequence[Color], tuple, None] = None,
    spans: Sequence[float] | None = None,
    depth: float = 100.0,
    depth_offset: float | None = None,
    opacity: Union[float, Sequence[float], None] = None,
    span_offset: float = 0.0,
    mask: np.ndarray | Tuple[int, int, int] | None | bool = None,
    style: Mapping[str, Any] | None = None,
    bezier_fractions: tuple[float, float] | None = None,
    below: bool = True,
    hover: bool | str | Sequence[str] | None = True,
) -> Mark:
    """Add one tip-anchored path per visible tip on rectangular tree drawings.

    Paths are anchored to tip coordinates and then displaced in pixel units
    away from the tree by ``depth_offset`` and along the tip span by
    ``span_offset``. Each path can use the full requested ``depth`` or a
    depth normalized from numeric ``data``. Optional ``spans`` set the
    endpoint position along the tree span axis in data units, and
    ``bezier_fractions`` controls the cubic ease-in-ease-out bend toward that
    endpoint without changing the outward depth scale used by companion
    rulers.

    Parameters
    ----------
    tree : ToyTree
        Tree associated with the existing drawing on ``axes``.
    axes : Cartesian
        Cartesian axes containing a previously drawn tree mark.
    data : str, sequence of float, or None, default=None
        Tip feature name or tip-sized numeric sequence used to scale the
        outward path depth. Values must be finite and non-negative. When
        None, paths use unit data so every visible tip reaches the full
        requested ``depth`` and companion mark scale bars use a ``0..1``
        domain.
    color : Color, sequence, tuple, or None, default=None
        Path stroke color specification. Supports a single color, per-tip
        colors, or feature mapping tuples such as ``("feature", "cmap")``.
        If None, paths use ``style["stroke"]`` when provided, otherwise they
        default to black.
    spans : sequence of float or None, default=None
        Tip-sized sequence giving the absolute endpoint positions on the tree
        span axis in data units. When None, path endpoints reuse the tip span
        coordinates so paths remain straight by default. Endpoint positions
        are not scaled by ``data``.
    depth : float, default=100.0
        Maximum outward path depth in pixel units.
    depth_offset : float or None, default=None
        Distance from the tip edge in pixel units to the path start. When
        None, the gap is set to the furthest outward shown tip-label extent
        plus 10 pixels, or to the furthest shown tip-node extent plus 10
        pixels when the tree drawing has no tip labels.
    opacity : float, sequence, or None, default=None
        Path stroke opacity. When None, paths keep
        ``style["stroke-opacity"]`` if provided and otherwise use the default
        visible stroke opacity. A scalar sets one shared stroke opacity for
        all paths. A tip-sized sequence applies per-path stroke opacity and
        overrides any shared style opacity.
    span_offset : float, default=0.0
        Uniform signed shift in pixel units applied to the whole path along
        the tip span axis.
    mask : bool, tuple[int, int, int], np.ndarray, or None, default=None
        Controls shown tips. Accepted values are:
        - None: show all tips
        - bool: True shows all tips, False shows none
        - tuple: (show_tips, show_internal, show_root) shortcut
        - np.ndarray: boolean array of size ntips
    style : Mapping[str, Any] or None, default=None
        Optional CSS-style mapping for the path lines. By default paths use a
        black round-capped stroke of width 2 pixels with no fill. Explicit
        ``color`` overrides style-level stroke color. ``opacity=None``
        preserves style-level ``stroke-opacity``.
    bezier_fractions : tuple[float, float] or None, default=None
        Normalized depth fractions locating the two cubic Bezier control
        points. When None, the path uses ``(0.25, 0.75)`` for a default
        ease-in-ease-out curve. Use ``(0.0, 1.0)`` to render a straight
        segment.
    below : bool, default=True
        If True, place the path mark below the associated tree mark in
        scenegraph render order.
    hover : bool, str, sequence of str, or None, default=True
        Tooltip labels for rendered paths. ``True`` shows ``"{name}: {value}"``
        using the resolved tip data, including the implicit unit values used
        when ``data`` is None. A string is treated as a tip feature name whose
        resolved values are shown directly. A tip-sized sequence is used
        verbatim as custom labels.

    Returns
    -------
    Mark
        Added annotation mark.

    Raises
    ------
    ToytreeError
        If inputs are invalid or the tree layout is unsupported.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, _ = tree.draw(layout="r")
    >>> tree.annotate.add_tip_paths(
    ...     axes,
    ...     data=[0, 1, 2, 3, 4, 5],
    ...     color="steelblue",
    ...     spans=[0, 1, 2, 4, 3, 5],
    ...     depth=40,
    ...     bezier_fractions=(0.2, 0.8),
    ...     opacity=None,
    ...     hover=True,
    ...     style={"stroke-width": 2.5, "stroke-opacity": 0.7},
    ... )
    """
    tmark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, tmark)

    layout = str(tmark.layout)
    if layout not in ("r", "l", "u", "d"):
        raise ToytreeError(
            "add_tip_paths currently supports only rectangular layouts (r/l/u/d)."
        )

    depth = float(depth)
    if (not np.isfinite(depth)) or depth <= 0.0:
        raise ToytreeError("depth must be a finite float > 0.")

    show = normalize_tip_mask(tree, mask)
    depth_offset = (
        _resolve_tip_overlay_auto_offset(tree, tmark, show)
        if depth_offset is None
        else float(depth_offset)
    )
    if not np.isfinite(depth_offset):
        raise ToytreeError("depth_offset must be a finite float.")

    span_offset = float(span_offset)
    if not np.isfinite(span_offset):
        raise ToytreeError("span_offset must be a finite float.")

    resolved_bezier_fractions = _resolve_tip_path_bezier_fractions(bezier_fractions)

    if spans is None:
        span_axis = 1 if layout in ("r", "l") else 0
        raw_spans = np.array(
            tmark.ttable[: tree.ntips, span_axis],
            dtype=float,
            copy=True,
        )
    else:
        raw_spans = _coerce_tip_path_spans(tree, spans)
    raw_data = _coerce_tip_metric_data(tree, data)
    value_min = 0.0
    value_max = float(np.max(raw_data))
    if value_max == 0.0:
        scale_factors = np.zeros(tree.ntips, dtype=float)
    else:
        scale_factors = np.asarray(raw_data / value_max, dtype=float)
    path_depths = scale_factors * depth

    style = {} if style is None else substyle_dict_to_css_dict(dict(style))
    style.setdefault("fill", "none")
    style.setdefault("stroke", "black")
    style.setdefault("stroke-width", 2.0)
    style.setdefault("stroke-linecap", "round")

    colors, stroke_color = validate_colors(
        tree,
        key="colors",
        size=tree.ntips,
        style={"colors": color},
    )
    if colors is None:
        if stroke_color is not None:
            stroke_color = ToyColor(stroke_color)
        elif "stroke" in style:
            stroke_color = ToyColor(style["stroke"])
        else:
            stroke_color = ToyColor("black")

    style, opacity_all = _resolve_tip_path_opacity(tree, style, opacity)
    hover_labels = _build_tip_path_hover_labels(tree, raw_data, hover)

    amark = AnnotationTipPathMark(
        ntable=np.asarray(tmark.ttable[: tree.ntips], dtype=float),
        host_tree_mark=tmark,
        layout=layout,
        depth_offset=float(depth_offset),
        span_offset=float(span_offset),
        show=show,
        data=np.asarray(raw_data, dtype=float),
        value_min=float(value_min),
        value_max=float(value_max),
        max_path_depth=float(depth),
        path_depths=np.asarray(path_depths, dtype=float),
        spans=np.array(raw_spans, dtype=float, copy=True),
        colors=colors,
        stroke_color=stroke_color,
        opacity=opacity_all,
        hover_labels=hover_labels,
        bezier_fractions=resolved_bezier_fractions,
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
