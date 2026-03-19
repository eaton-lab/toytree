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
    _insert_mark_below_tree,
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
from toytree.drawing.src.mark_annotation import AnnotationTipPathMark
from toytree.style.src.validate_data import validate_colors
from toytree.style.src.validate_utils import substyle_dict_to_css_dict
from toytree.utils import ToytreeError

__all__ = ["add_tip_paths"]

Color = TypeVar("Color", str, tuple, np.ndarray)


def _coerce_tip_path_ends(
    tree: ToyTree,
    ends: str | Sequence[float] | None,
) -> np.ndarray | None:
    """Return one finite tip-sized end-position array or None."""
    if ends is None:
        return None
    if isinstance(ends, str):
        try:
            arr = np.asarray(tree.get_tip_data(ends))
        except Exception as exc:  # pragma: no cover - precise error type varies
            raise ToytreeError(
                f"'ends' feature {ends!r} could not be resolved for tip paths."
            ) from exc
    else:
        arr = np.asarray(ends)
    if arr.ndim == 0:
        raise ToytreeError(
            "'ends' must be a tip-sized numeric sequence or a tip feature name."
        )
    if arr.ndim != 1:
        raise ToytreeError("'ends' must be a one-dimensional tip-sized sequence.")
    if arr.size != tree.ntips:
        raise ToytreeError(f"'ends' must be size ntips ({tree.ntips}), not {arr.size}.")
    try:
        arr = arr.astype(float, copy=False)
    except (TypeError, ValueError) as exc:
        raise ToytreeError("'ends' must contain numeric tip data.") from exc
    if np.any(~np.isfinite(arr)):
        raise ToytreeError("'ends' must contain only finite numeric data.")
    return np.asarray(arr, dtype=float)


def _coerce_tip_path_spans(
    tree: ToyTree,
    spans: str | Sequence[float] | None,
) -> np.ndarray:
    """Return one finite tip-sized array of absolute end positions."""
    if isinstance(spans, str):
        try:
            arr = np.asarray(tree.get_tip_data(spans))
        except Exception as exc:  # pragma: no cover - precise error type varies
            raise ToytreeError(
                f"'spans' feature {spans!r} could not be resolved for tip paths."
            ) from exc
    else:
        arr = np.asarray(spans)
    if arr.ndim == 0:
        raise ToytreeError(
            "'spans' must be a tip-sized numeric sequence or a tip feature name."
        )
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
        return (0.45, 0.55)
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
    spans: str | Sequence[float] | None = None,
    ends: str | Sequence[float] | None = None,
    depth: float | None = 100.0,
    offset_start: float = 0.0,
    offset_end: float = 0.0,
    offset_span: float = 0.0,
    color: Union[Color, Sequence[Color], tuple, None] = None,
    opacity: Union[float, Sequence[float], None] = None,
    mask: np.ndarray | Tuple[int, int, int] | None | bool = None,
    style: Mapping[str, Any] | None = None,
    bezier_fractions: tuple[float, float] | None = None,
    below: bool = True,
    hover: bool | str | Sequence[str] | None = True,
) -> Mark:
    """Add one tip-anchored path per visible tip on rectangular tree drawings.

    Path endpoints can be specified directly in tree data coordinates using
    ``spans`` and ``ends``. When ``ends`` is None, the path endpoint
    along the depth axis falls back to a pixel-space depth offset given by
    ``depth``. The three offset arguments then apply additional pixel-space
    shifts to the rendered start point, end point, and shared span axis.

    Parameters
    ----------
    tree : ToyTree
        Tree associated with the existing drawing on ``axes``.
    axes : Cartesian
        Cartesian axes containing a previously drawn tree mark.
    spans : str, sequence of float, or None, default=None
        Tip feature name or tip-sized sequence giving the absolute endpoint
        positions on the tree span axis in data units. When None, endpoint
        spans default to ``np.arange(tree.ntips)`` in tip order.
    ends : str, sequence of float, or None, default=None
        Tip feature name or tip-sized sequence giving the absolute endpoint
        positions on the tree depth axis in data units. When provided, the
        path endpoint is placed exactly at this depth-axis coordinate and
        ``depth`` is ignored. When None, paths use the pixel-space ``depth``
        fallback and hover labels use a synthetic unit value of ``1``.
    depth : float or None, default=100.0
        Pixel-space fallback distance from the start point to the end point
        along the depth axis. Used only when ``ends`` is None.
    offset_start : float, default=0.0
        Pixel-space shift applied to the start point along the depth axis.
    offset_end : float, default=0.0
        Pixel-space shift applied to the end point along the depth axis.
    offset_span : float, default=0.0
        Pixel-space shift applied to both endpoints along the span axis.
    color : Color, sequence, tuple, or None, default=None
        Path stroke color specification. Supports a single color, per-tip
        colors, or feature mapping tuples such as ``("feature", "cmap")``.
        If None, paths use ``style["stroke"]`` when provided, otherwise they
        default to black.
    opacity : float, sequence, or None, default=None
        Path stroke opacity. When None, paths keep
        ``style["stroke-opacity"]`` if provided and otherwise use the default
        visible stroke opacity. A scalar sets one shared stroke opacity for
        all paths. A tip-sized sequence applies per-path stroke opacity and
        overrides any shared style opacity.
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
        points. When None, the path uses ``(0.45, 0.55)`` for a default
        ease-in-ease-out curve. Use ``(0.0, 1.0)`` to render a straight
        segment.
    below : bool, default=True
        If True, place the path mark below the associated tree mark in
        scenegraph render order.
    hover : bool, str, sequence of str, or None, default=True
        Tooltip labels for rendered paths. ``True`` shows ``"{name}: {value}"``
        using the resolved tip end values, including the implicit unit values
        used when ``ends`` is None. A string is treated as a tip feature
        name whose resolved values are shown directly. A tip-sized sequence is
        used verbatim as custom labels.

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
    ...     spans=[0, 1, 2, 4, 3, 5],
    ...     ends=[0, 1, 2, 3, 4, 5],
    ...     color="steelblue",
    ...     offset_end=10,
    ...     offset_span=4,
    ...     bezier_fractions=(0.2, 0.8),
    ...     opacity=None,
    ...     hover=True,
    ...     style={"stroke-width": 2.5, "stroke-opacity": 0.7},
    ... )
    """
    tmark = get_last_toytree_mark_for_tree(axes, tree)
    assert_tree_matches_mark(tree, tmark)

    layout = str(tmark.layout)
    if layout not in ("r", "l", "u", "d"):
        raise ToytreeError(
            "add_tip_paths currently supports only rectangular layouts (r/l/u/d)."
        )

    show = normalize_tip_mask(tree, mask)
    raw_ends = _coerce_tip_path_ends(tree, ends)
    if raw_ends is None:
        if depth is None:
            raise ToytreeError("depth must be a finite float > 0 when ends is None.")
        pixel_depth = float(depth)
        if (not np.isfinite(pixel_depth)) or pixel_depth <= 0.0:
            raise ToytreeError("depth must be a finite float > 0 when ends is None.")
        values = np.ones(tree.ntips, dtype=float)
    else:
        pixel_depth = None
        values = np.asarray(raw_ends, dtype=float)

    offset_start = float(offset_start)
    offset_end = float(offset_end)
    offset_span = float(offset_span)
    if not np.isfinite(offset_start):
        raise ToytreeError("offset_start must be a finite float.")
    if not np.isfinite(offset_end):
        raise ToytreeError("offset_end must be a finite float.")
    if not np.isfinite(offset_span):
        raise ToytreeError("offset_span must be a finite float.")

    resolved_bezier_fractions = _resolve_tip_path_bezier_fractions(bezier_fractions)

    if spans is None:
        raw_spans = np.arange(tree.ntips, dtype=float)
    else:
        raw_spans = _coerce_tip_path_spans(tree, spans)

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
    hover_labels = _build_tip_path_hover_labels(tree, values, hover)

    amark = AnnotationTipPathMark(
        ntable=np.asarray(tmark.ttable[: tree.ntips], dtype=float),
        host_tree_mark=tmark,
        layout=layout,
        ends=None if raw_ends is None else np.asarray(raw_ends, dtype=float),
        spans=np.array(raw_spans, dtype=float, copy=True),
        pixel_depth=pixel_depth,
        offset_start=float(offset_start),
        offset_end=float(offset_end),
        offset_span=float(offset_span),
        show=show,
        data=np.asarray(values, dtype=float),
        value_min=0.0,
        value_max=float(np.max(values)),
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
