#!/usr/bin/env python

"""Modify ticks and labels on hidden companion axes into scale bars."""

from __future__ import annotations

from numbers import Real
from types import MethodType
from typing import Any, Callable, Literal, Sequence

import numpy as np
from toyplot import locator
from toyplot.mark import Mark

from toytree.annotate.src.checks import (
    assert_tree_matches_mark,
    finalize_cartesian_with_tip_bar_domains,
    get_last_toytree_mark_for_tree,
    invalidate_cartesian_fit_cache,
    try_incremental_tip_bar_host_finalize,
)
from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian, ToyTreeMark
from toytree.drawing.src.mark_annotation import (
    AnnotationTipBarMark,
    AnnotationTipPathMark,
)
from toytree.drawing.src.scale_axes import (
    CompanionScaleSpec,
    add_tree_domain_mark,
    get_mark_scale_cartesian,
    get_toytree_scale_cartesian,
    sync_mark_scale_cartesian,
    sync_scale_cartesian_ranges,
)
from toytree.layout.src.layout_circular import _parse_circular_layout
from toytree.utils import ToytreeError

__all__ = ["add_axes_scale_bar_to_tree", "add_axes_scale_bar_to_mark"]


def _get_host_geometry_token(axes: Cartesian) -> int:
    """Return the host-geometry version tracked on one Cartesian."""
    return int(getattr(axes, "_toytree_host_geometry_token", 0))


def _record_companion_sync_token(axes: Cartesian) -> None:
    """Record that all active companions match the current host geometry."""
    axes._toytree_companion_sync_token = _get_host_geometry_token(axes)


def _companion_sync_is_current(
    axes: Cartesian,
    expand_margin: None | int | tuple[int, int, int, int],
) -> bool:
    """Return True when companion geometry already matches the host axes."""
    if expand_margin is not None:
        return False
    if getattr(axes, "_finalized", None) is None:
        return False
    return getattr(axes, "_toytree_companion_sync_token", None) == (
        _get_host_geometry_token(axes)
    )


def _prepare_axes_for_companion_update(
    axes: Cartesian,
    expand_margin: None | int | tuple[int, int, int, int],
) -> bool:
    """Ensure host geometry is current and return True when it was reused."""
    if _companion_sync_is_current(axes, expand_margin):
        return True
    _apply_axes_expand_margin(axes, expand_margin)
    invalidate_cartesian_fit_cache(axes)
    _finalize_host_axes(axes)
    return False


def _store_scale_spec(
    scale_axes: Cartesian,
    mark: Mark,
    spec: CompanionScaleSpec,
) -> None:
    """Attach resolved scale metadata to one companion axes."""
    scale_axes._toytree_scale_spec = spec
    scale_axes._toytree_target_mark = mark
    scale_axes._toytree_scale_axis = spec.axis


def _get_outward_label_sign(mark: Any, axis: Literal["x", "y"]) -> float:
    """Return signed direction where positive label_offset is outward."""
    if axis == "x" and getattr(mark, "layout", None) in ("r", "l"):
        return -1.0
    if axis == "y" and getattr(mark, "layout", None) in ("u", "d"):
        return 1.0

    # Fallback for tree marks where layout is less constrained.
    if axis == "x" and hasattr(mark, "ybaseline"):
        ys = mark.domain("y")
        ycenter = 0.5 * (ys[0] + ys[1])
        return -1.0 if ycenter > mark.ybaseline else 1.0
    if axis == "y" and hasattr(mark, "xbaseline"):
        xs = mark.domain("x")
        xcenter = 0.5 * (xs[0] + xs[1])
        return -1.0 if xcenter > mark.xbaseline else 1.0
    return 1.0


def _apply_axes_expand_margin(
    axes: Cartesian,
    expand_margin: None | int | tuple[int, int, int, int],
) -> None:
    """Expand whitespace margins by symmetric or side-specific deltas."""
    if expand_margin is None:
        return
    if isinstance(expand_margin, int):
        left = right = top = bottom = float(expand_margin)
    else:
        if len(expand_margin) != 4:
            raise ValueError("expand_margin tuple must be (left, right, top, bottom).")
        left, right, top, bottom = [float(i) for i in expand_margin]

    xmin = float(axes._xmin_range)
    xmax = float(axes._xmax_range)
    ymin = float(axes._ymin_range)
    ymax = float(axes._ymax_range)
    new_xmin = xmin + left
    new_xmax = xmax - right
    new_ymin = ymin + top
    new_ymax = ymax - bottom
    if (new_xmin >= new_xmax) or (new_ymin >= new_ymax):
        raise ValueError("expand_margin too large: axes range collapsed or inverted.")
    axes._set_xmin_range(new_xmin)
    axes._set_xmax_range(new_xmax)
    axes._set_ymin_range(new_ymin)
    axes._set_ymax_range(new_ymax)


def _get_tree_scale_axes(axes: Cartesian) -> list[Cartesian]:
    """Return all registered tree companion axes on one host axes."""
    registry = getattr(axes, "_toytree_tree_scale_axes", None)
    if registry:
        return list(registry.values())
    scale_axes = get_toytree_scale_cartesian(axes, create=False)
    return [] if scale_axes is None else [scale_axes]


def _sync_tree_scale_axes_finalized(
    axes: Cartesian,
    skip_mark: ToyTreeMark | None = None,
) -> None:
    """Synchronize the tree companion axes from finalized host geometry."""
    for scale_axes in _get_tree_scale_axes(axes):
        target_mark = getattr(scale_axes, "_toytree_target_mark", None)
        if target_mark is None or target_mark is skip_mark:
            continue
        spec = getattr(scale_axes, "_toytree_scale_spec", None)
        if spec is None:
            continue
        bounds = spec.bounds_getter()
        sync_scale_cartesian_ranges(axes, scale_axes, bounds=bounds)


def _sync_mark_scale_axes_finalized(
    axes: Cartesian,
    skip_mark: Mark | None = None,
) -> None:
    """Synchronize mark companions from finalized host geometry."""
    registry = getattr(axes, "_toytree_mark_scale_axes", None)
    if not registry:
        return

    for scale_axes in registry.values():
        target_mark = getattr(scale_axes, "_toytree_target_mark", None)
        if target_mark is None or target_mark is skip_mark:
            continue
        spec = getattr(scale_axes, "_toytree_scale_spec", None)
        if spec is None:
            continue
        bounds = spec.bounds_getter()
        sync_mark_scale_cartesian(scale_axes, bounds=bounds)


def _sync_all_companion_axes(axes: Cartesian) -> None:
    """Synchronize active companion axes from finalized host geometry."""
    _sync_tree_scale_axes_finalized(axes)
    _sync_mark_scale_axes_finalized(axes)
    _align_companion_scale_axes(axes)
    _record_companion_sync_token(axes)


def _finalize_host_axes(axes: Cartesian) -> None:
    """Finalize one host axes using fit-only annotation overflow handling."""
    finalize_cartesian_with_tip_bar_domains(axes)


def _align_scale_axis_group(
    scale_axes_group: list[Cartesian],
    axis: Literal["x", "y"],
    anchor: float | None,
) -> float | None:
    """Shift one group of companions outward to a shared anchor."""
    if not scale_axes_group:
        return anchor

    if anchor is None:
        anchor = (
            max(float(scale_axes._ymax_range) for scale_axes in scale_axes_group)
            if axis == "x"
            else min(float(scale_axes._xmin_range) for scale_axes in scale_axes_group)
        )

    for scale_axes in scale_axes_group:
        if axis == "x":
            current = float(scale_axes._ymax_range)
            if current >= anchor:
                continue
            delta = anchor - current
            scale_axes._set_ymin_range(float(scale_axes._ymin_range) + delta)
            scale_axes._set_ymax_range(anchor)
        else:
            current = float(scale_axes._xmin_range)
            if current <= anchor:
                continue
            delta = anchor - current
            scale_axes._set_xmin_range(anchor)
            scale_axes._set_xmax_range(float(scale_axes._xmax_range) + delta)
        scale_axes._finalized = None
    return anchor


def _align_companion_scale_axes(axes: Cartesian) -> None:
    """Align tree and mark scale bars on shared outer rows / columns.

    Tree scale bars define the anchor when they exist. Mark scale bars align
    to that anchor only when doing so moves them farther outward, which
    preserves the requested local gap. Without any tree companions, mark scale
    bars align among themselves on the outermost row / column.
    """
    tree_axes = _get_tree_scale_axes(axes)
    mark_registry = getattr(axes, "_toytree_mark_scale_axes", None) or {}
    mark_axes = list(mark_registry.values())
    if not tree_axes and not mark_axes:
        return

    tree_x_axes = [
        scale_axes
        for scale_axes in tree_axes
        if getattr(scale_axes, "_toytree_scale_axis", None) == "x"
    ]
    tree_y_axes = [
        scale_axes
        for scale_axes in tree_axes
        if getattr(scale_axes, "_toytree_scale_axis", None) == "y"
    ]
    mark_x_axes = [
        scale_axes
        for scale_axes in mark_axes
        if getattr(scale_axes, "_toytree_scale_axis", None) == "x"
    ]
    mark_y_axes = [
        scale_axes
        for scale_axes in mark_axes
        if getattr(scale_axes, "_toytree_scale_axis", None) == "y"
    ]

    x_anchor = _align_scale_axis_group(tree_x_axes, "x", anchor=None)
    y_anchor = _align_scale_axis_group(tree_y_axes, "y", anchor=None)
    _align_scale_axis_group(mark_x_axes, "x", anchor=x_anchor)
    _align_scale_axis_group(mark_y_axes, "y", anchor=y_anchor)


def _add_mark_and_sync_companions(axes: Cartesian, mark: Mark) -> Mark:
    """Add a host mark, then refresh host fit and active companion axes."""
    original_add_mark = axes._toytree_original_add_mark
    result = original_add_mark(mark)

    # Repeated rectangular tip-bar additions dominate the multi-companion
    # workload, so reuse the finalized host extents when that path is safe.
    if try_incremental_tip_bar_host_finalize(axes, mark):
        _sync_all_companion_axes(axes)
        return result

    invalidate_cartesian_fit_cache(axes)
    _finalize_host_axes(axes)
    _sync_all_companion_axes(axes)
    return result


def _add_mark_and_invalidate_host_fit(axes: Cartesian, mark: Mark) -> Mark:
    """Add a host mark and clear cached fit state for the next finalize."""
    original_add_mark = axes._toytree_original_add_mark
    result = original_add_mark(mark)
    invalidate_cartesian_fit_cache(axes)
    return result


def _ensure_original_add_mark(axes: Cartesian) -> None:
    """Store Toyplot's original ``add_mark()`` once for later wrappers."""
    if not hasattr(axes, "_toytree_original_add_mark"):
        axes._toytree_original_add_mark = axes.add_mark


def _install_host_fit_invalidation_add_mark_hook(axes: Cartesian) -> None:
    """Wrap ``axes.add_mark()`` so later host marks invalidate cached fit."""
    if getattr(axes, "_toytree_companion_add_mark_hook_installed", False):
        return
    if getattr(axes, "_toytree_host_fit_add_mark_hook_installed", False):
        return
    _ensure_original_add_mark(axes)
    axes.add_mark = MethodType(_add_mark_and_invalidate_host_fit, axes)
    axes._toytree_host_fit_add_mark_hook_installed = True


def _install_companion_add_mark_hook(axes: Cartesian) -> None:
    """Wrap ``axes.add_mark()`` so later host marks refresh companions."""
    if getattr(axes, "_toytree_companion_add_mark_hook_installed", False):
        return
    _ensure_original_add_mark(axes)
    axes.add_mark = MethodType(_add_mark_and_sync_companions, axes)
    axes._toytree_companion_add_mark_hook_installed = True
    axes._toytree_host_fit_add_mark_hook_installed = False


def _resolve_tree_scale_axis(
    mark: Any, axis: Literal["auto", "x", "y"]
) -> Literal["x", "y"]:
    """Resolve the active tree scale-bar axis from layout and override."""
    if axis != "auto":
        return axis
    if mark.layout in ("r", "l"):
        return "x"
    if mark.layout in ("u", "d"):
        return "y"
    xdom = mark.domain("x")
    ydom = mark.domain("y")
    xspan = abs(xdom[1] - xdom[0])
    yspan = abs(ydom[1] - ydom[0])
    return "x" if xspan >= yspan else "y"


def _resolve_tip_bar_scale_axis(
    mark: AnnotationTipBarMark,
    axis: Literal["auto", "x", "y"],
) -> Literal["x", "y"]:
    """Resolve and validate the active value axis for a tip-bar mark."""
    expected = "x" if mark.layout in ("r", "l") else "y"
    if axis == "auto":
        return expected
    if axis != expected:
        raise ToytreeError(
            f"Tip bar layout '{mark.layout}' only supports axis='{expected}'."
        )
    return axis


def _resolve_tree_scale_range(
    mark: Any, axis: Literal["x", "y"]
) -> tuple[float, float]:
    """Return the default visible tree scale-bar range in display-axis units."""
    if mark.layout.startswith("c"):
        lo, hi = mark.domain(axis)
        lo = float(lo)
        hi = float(hi)
        is_full_circle = _parse_circular_layout(mark.layout)[3]
        pos_extent = max(hi, 0.0)
        neg_extent = abs(min(lo, 0.0))
        if is_full_circle or pos_extent >= neg_extent:
            return 0.0, pos_extent
        return min(lo, 0.0), 0.0

    if axis == "x":
        left, right = mark.domain("x")
        tree_height = max(abs(right - left), 1e-6)
        if mark.layout == "r":
            return -tree_height, 0.0
        return 0.0, tree_height

    bottom, top = mark.domain("y")
    tree_height = max(abs(top - bottom), 1e-6)
    if mark.layout == "u":
        return -tree_height, 0.0
    return 0.0, tree_height


def _validate_scale_factor(scale: Real, target: str) -> float:
    """Return a validated positive numeric scale factor."""
    if isinstance(scale, (bool, np.bool_)) or not isinstance(scale, Real):
        raise ToytreeError(
            f"scale must be a positive numeric factor for {target} scale bars."
        )
    scale = float(scale)
    if (not np.isfinite(scale)) or scale <= 0.0:
        raise ToytreeError(
            f"scale must be a finite numeric factor > 0 for {target} scale bars."
        )
    return scale


def _normalize_draw_scale_factor(scale: Any) -> float | None:
    """Return the numeric factor used by draw-time scale-bar callers."""
    if scale in (None, False):
        return None
    if scale is True:
        return 1.0
    return _validate_scale_factor(scale, "draw-time")


def _resolve_internal_tree_scale_domain(
    mark: Any,
    axis: Literal["x", "y"],
    domain_override: tuple[float, float] | None = None,
) -> tuple[float, float]:
    """Return tree scale-bar domain for public or internal callers."""
    if domain_override is None:
        return _resolve_tree_scale_range(mark, axis)

    if len(domain_override) != 2:
        raise ValueError("internal scale-bar domain override must be length 2.")
    tmin = float(domain_override[0])
    tmax = float(domain_override[1])
    if tmax <= tmin:
        raise ValueError("internal scale-bar domain override must increase.")
    return tmin, tmax


def _resolve_circular_tree_locator_domain(
    tmin: float,
    tmax: float,
) -> tuple[tuple[float, float], float]:
    """Return outward tick span and sign for one circular tree ruler."""
    if tmax <= 0.0:
        return (0.0, abs(float(tmin))), -1.0
    return (0.0, float(tmax)), 1.0


def _validate_scale_padding(padding: float, target: str) -> float:
    """Return validated non-negative local gap for a scale bar."""
    padding = float(padding)
    if (not np.isfinite(padding)) or padding < 0.0:
        raise ToytreeError(
            f"padding must be a finite float >= 0 for {target} scale bars."
        )
    return padding


def _resolve_tick_locations(
    csize: float,
    tmin: float,
    tmax: float,
    tick_locations: Sequence[float] | None,
) -> np.ndarray:
    """Return scale-bar tick locations in data coordinates."""
    if tick_locations is not None:
        locs = np.asarray(tick_locations, dtype=float)
        # Clipping can collapse multiple explicit locations onto the same
        # endpoint; keep the first occurrence order while dropping duplicates.
        clipped = np.clip(locs, tmin, tmax)
        _, indices = np.unique(clipped, return_index=True)
        return clipped[np.sort(indices)]

    count = int(max(5, np.floor(csize / 75.0).astype(int)))
    lct = locator.Extended(count=count, only_inside=True)
    locs = np.asarray(lct.ticks(tmin, tmax)[0], dtype=float)
    return locs[(locs >= tmin) & (locs <= tmax)]


def _format_tick_labels(
    locs: np.ndarray,
    effective_scale: bool | int | float,
    formatter: str | Callable[[float], str] | None,
    precision: int,
    trim: Literal["k", ".", "0", "-"],
    use_absolute: bool = True,
) -> list[str]:
    """Return formatted tick labels for one scale axis."""
    if isinstance(effective_scale, (int, float)):
        labels_data = locs / effective_scale
    else:
        labels_data = locs.copy()

    if use_absolute:
        labels_data = abs(labels_data)

    if formatter is None:
        return [
            np.format_float_positional(val, precision=precision, trim=trim)
            for val in labels_data
        ]
    if isinstance(formatter, str):
        return [formatter.format(val) for val in labels_data]
    return [formatter(val) for val in labels_data]


def _reset_custom_label_state(scale_axes: Cartesian) -> None:
    """Clear custom toytree label-centering attributes from both axes."""
    scale_axes.x._toytree_label_mode = None
    scale_axes.y._toytree_label_mode = None
    scale_axes.x._toytree_label_data_midpoint = None
    scale_axes.y._toytree_label_data_midpoint = None


def _style_scale_axes(
    scale_axes: Cartesian,
    mark: Any,
    axis: Literal["x", "y"],
    show_spine: bool,
    show_ticks: bool,
    show_tick_labels: bool,
    ticks_near: int,
    ticks_far: int,
    tick_labels_style: dict[str, Any] | None,
    tick_labels_offset: int,
    label_offset: int | None,
    spine_style: dict[str, Any] | None,
    ticks_style: dict[str, Any] | None,
) -> None:
    """Apply visibility and styling options to the active scale axis."""
    scale_axes.show = True
    active = scale_axes.x if axis == "x" else scale_axes.y
    inactive = scale_axes.y if axis == "x" else scale_axes.x
    active.show = True
    inactive.show = False
    active.spine.show = show_spine
    active.ticks.show = show_ticks
    active.ticks.labels.show = show_tick_labels
    active.ticks.near = ticks_near
    active.ticks.far = ticks_far
    if tick_labels_style is not None:
        active.ticks.labels.style = {
            **active.ticks.labels.style,
            **tick_labels_style,
        }
    active.ticks.labels.offset = tick_labels_offset
    if label_offset is not None:
        sign = _get_outward_label_sign(mark, axis)
        active.label.offset = int(sign * label_offset)
    if spine_style is not None:
        active.spine.style = {**active.spine.style, **spine_style}
    if ticks_style is not None:
        active.ticks.style = {**active.ticks.style, **ticks_style}


def _set_scale_axis_label(
    scale_axes: Cartesian,
    mark: Any,
    axis: Literal["x", "y"],
    label: str | None,
    label_center: Literal["axis", "spine"],
    label_style: dict[str, Any] | None,
    label_midpoint: float,
) -> None:
    """Apply label text and optional spine-centered label placement."""
    _reset_custom_label_state(scale_axes)
    active = scale_axes.x if axis == "x" else scale_axes.y
    if label is None:
        active.label.text = ""
    else:
        active.label.text = label
        if axis == "x" and getattr(mark, "layout", None) in ("r", "l"):
            active.label.location = "below"
        if label_center == "spine":
            active._toytree_label_mode = "spine"
            active._toytree_label_data_midpoint = float(label_midpoint)
    if label_style is not None:
        active.label.style.update(label_style)


def _set_tree_scale_axis_domain(
    scale_axes: Cartesian,
    axis: Literal["x", "y"],
    domain_override: tuple[float, float] | None = None,
) -> None:
    """Restore tree scale axes to host domains or one explicit active range."""
    scale_axes.x.domain.min = None
    scale_axes.x.domain.max = None
    scale_axes.y.domain.min = None
    scale_axes.y.domain.max = None
    if domain_override is None:
        return
    active = scale_axes.x if axis == "x" else scale_axes.y
    active.domain.min = float(domain_override[0])
    active.domain.max = float(domain_override[1])


def _set_mark_scale_axis_domain(
    scale_axes: Cartesian,
    axis: Literal["x", "y"],
    domain_min: float,
    domain_max: float,
) -> None:
    """Apply explicit value-domain limits to a mark scale-bar axes."""
    active = scale_axes.x if axis == "x" else scale_axes.y
    active.domain.min = float(domain_min)
    active.domain.max = float(domain_max)


def _set_scale_axis_locator(
    scale_axes: Cartesian,
    axis: Literal["x", "y"],
    locs: np.ndarray,
    labels: list[str],
    shift: float = 0.0,
) -> None:
    """Attach an explicit locator to the active scale axis."""
    active = scale_axes.x if axis == "x" else scale_axes.y
    active.ticks.locator = locator.Explicit(
        locations=np.asarray(locs, dtype=float) + float(shift),
        labels=labels,
    )


def _midpoint_bounds(values: np.ndarray) -> np.ndarray:
    """Return slot boundaries from sorted center positions."""
    nvals = int(values.size)
    if nvals == 1:
        return np.array([values[0] - 0.5, values[0] + 0.5], dtype=float)
    bounds = np.zeros(nvals + 1, dtype=float)
    bounds[1:-1] = 0.5 * (values[:-1] + values[1:])
    bounds[0] = values[0] - 0.5 * (values[1] - values[0])
    bounds[-1] = values[-1] + 0.5 * (values[-1] - values[-2])
    return bounds


def _get_projected_tip_slot_cache(
    axes: Cartesian,
) -> dict[tuple[int, str], tuple[np.ndarray, np.ndarray]]:
    """Return per-host-token projected slot bounds shared by tip-bar companions."""
    token = _get_host_geometry_token(axes)
    cache = getattr(axes, "_toytree_projected_tip_slot_cache", None)
    if cache is None or cache.get("token") != token:
        cache = {"token": token, "slots": {}}
        axes._toytree_projected_tip_slot_cache = cache
    return cache["slots"]


def _get_projected_tip_slot_cache_key(
    mark: AnnotationTipBarMark,
) -> tuple[int, str]:
    """Return the slot-cache key shared by bars from the same host tree."""
    host_tree_mark = getattr(mark, "host_tree_mark", None)
    tree_key = id(mark if host_tree_mark is None else host_tree_mark)
    axis = "y" if mark.layout in ("r", "l") else "x"
    return tree_key, axis


def _compute_projected_tip_slot_bounds_finalized(
    axes: Cartesian,
    mark: AnnotationTipBarMark,
) -> tuple[np.ndarray, np.ndarray]:
    """Project one full set of linear tip slots into pixel coordinates."""
    if mark.layout in ("r", "l"):
        span = np.asarray(axes.project("y", mark.ntable[:, 1]), dtype=float)
    else:
        span = np.asarray(axes.project("x", mark.ntable[:, 0]), dtype=float)

    sort_idx = np.argsort(span)
    bounds = _midpoint_bounds(span[sort_idx])
    slot_min = np.zeros(span.size, dtype=float)
    slot_max = np.zeros(span.size, dtype=float)
    slot_min[sort_idx] = np.asarray(bounds[:-1], dtype=float)
    slot_max[sort_idx] = np.asarray(bounds[1:], dtype=float)
    return slot_min, slot_max


def _get_projected_tip_slot_bounds_finalized(
    axes: Cartesian,
    mark: AnnotationTipBarMark,
) -> tuple[np.ndarray, np.ndarray]:
    """Return cached projected slot bounds in tip order for one bar family."""
    cache = _get_projected_tip_slot_cache(axes)
    key = _get_projected_tip_slot_cache_key(mark)
    bounds = cache.get(key)
    if bounds is None:
        bounds = _compute_projected_tip_slot_bounds_finalized(axes, mark)
        cache[key] = tuple(arr.copy() for arr in bounds)
    return tuple(arr.copy() for arr in bounds)


def _get_projected_mark_bounds_finalized(
    axes: Cartesian,
    mark: Mark,
) -> tuple[float, float, float, float]:
    """Return rendered pixel bounds for a mark on finalized host axes."""
    coords, extents = mark.extents("xy")
    xvals = np.asarray(coords[0], dtype=float)
    yvals = np.asarray(coords[1], dtype=float)
    xpx = np.asarray(axes.project("x", xvals), dtype=float)
    ypx = np.asarray(axes.project("y", yvals), dtype=float)
    left, right, top, bottom = [np.asarray(i, dtype=float) for i in extents]
    return (
        float(np.min(xpx + left)),
        float(np.max(xpx + right)),
        float(np.min(ypx + top)),
        float(np.max(ypx + bottom)),
    )


def _get_visible_tip_slot_bounds_finalized(
    axes: Cartesian,
    mark: AnnotationTipBarMark,
) -> tuple[np.ndarray, np.ndarray]:
    """Return visible full-slot bounds for a finalized linear tip-bar mark."""
    tip_indices = np.flatnonzero(np.asarray(mark.show, dtype=bool))
    if not tip_indices.size:
        raise ToytreeError(
            "Cannot add a mark scale bar to a tip-bar mark with no visible bars."
        )
    slot_min, slot_max = _get_projected_tip_slot_bounds_finalized(axes, mark)
    return slot_min[tip_indices], slot_max[tip_indices]


def _get_visible_tip_bar_span_bounds_finalized(
    axes: Cartesian,
    mark: AnnotationTipBarMark,
) -> tuple[np.ndarray, np.ndarray]:
    """Return visible occupied orthogonal bounds on finalized host axes."""
    slot_min, slot_max = _get_visible_tip_slot_bounds_finalized(axes, mark)
    center = 0.5 * (slot_min + slot_max)
    half = 0.5 * float(mark.width) * (slot_max - slot_min)
    return center - half, center + half


def _get_tree_scale_bounds_finalized(
    axes: Cartesian,
    mark: Mark,
    axis: Literal["x", "y"],
    padding: float,
    axis_domain: tuple[float, float] | None = None,
) -> tuple[float, float, float, float]:
    """Return tree scale-bar bounds assuming host ranges are finalized."""
    left, right, top, bottom = _get_projected_mark_bounds_finalized(axes, mark)
    xmin = float(axes._xmin_range)
    xmax = float(axes._xmax_range)
    ymin = float(axes._ymin_range)
    ymax = float(axes._ymax_range)

    if axis == "x":
        delta = (bottom + float(padding)) - ymax
        if axis_domain is not None:
            projected = np.asarray(
                axes.project("x", np.asarray(axis_domain, dtype=float)),
                dtype=float,
            )
            xmin = float(np.min(projected))
            xmax = float(np.max(projected))
        return xmin, xmax, ymin + delta, ymax + delta

    delta = (left - float(padding)) - xmin
    if axis_domain is not None:
        projected = np.asarray(
            axes.project("y", np.asarray(axis_domain, dtype=float)),
            dtype=float,
        )
        ymin = float(np.min(projected))
        ymax = float(np.max(projected))
    return xmin + delta, xmax + delta, ymin, ymax


def _get_linear_tip_bar_scale_bounds_finalized(
    axes: Cartesian,
    mark: AnnotationTipBarMark,
    padding: float,
) -> tuple[float, float, float, float]:
    """Return overlay bounds for a finalized linear tip-bar scale bar."""
    shown = np.flatnonzero(np.asarray(mark.show, dtype=bool))
    if not shown.size:
        raise ToytreeError(
            "Cannot add a mark scale bar to a tip-bar mark with no visible bars."
        )

    slot_min, slot_max = _get_visible_tip_bar_span_bounds_finalized(axes, mark)
    tips_x_px = np.asarray(axes.project("x", mark.ntable[:, 0]), dtype=float)
    tips_y_px = np.asarray(axes.project("y", mark.ntable[:, 1]), dtype=float)
    depth = float(mark.max_bar_depth)
    offset = float(mark.offset)
    padding = float(padding)

    if mark.layout == "r":
        baseline = float(np.max(tips_x_px[shown]) + offset)
        return (
            baseline,
            baseline + depth,
            float(np.min(slot_min) + padding),
            float(np.max(slot_max) + padding),
        )
    if mark.layout == "l":
        baseline = float(np.min(tips_x_px[shown]) - offset)
        return (
            baseline - depth,
            baseline,
            float(np.min(slot_min) + padding),
            float(np.max(slot_max) + padding),
        )
    if mark.layout == "u":
        baseline = float(np.min(tips_y_px[shown]) - offset)
        return (
            float(np.min(slot_min) - padding),
            float(np.max(slot_max) - padding),
            baseline - depth,
            baseline,
        )
    if mark.layout == "d":
        baseline = float(np.max(tips_y_px[shown]) + offset)
        return (
            float(np.min(slot_min) - padding),
            float(np.max(slot_max) - padding),
            baseline,
            baseline + depth,
        )
    raise ToytreeError(
        "add_axes_scale_bar_to_mark() currently supports only rectangular "
        "tip-bar layouts (r/l/u/d)."
    )


def _resolve_tip_bar_scale_domain(
    mark: AnnotationTipBarMark,
    tmax: float,
) -> tuple[float, float, float]:
    """Return internal domain limits and locator sign for tip-bar rulers."""
    if mark.layout in ("r", "u"):
        return 0.0, tmax, 1.0
    return -tmax, 0.0, -1.0


def _configure_companion_scale_axes(
    axes: Cartesian,
    scale_axes: Cartesian,
    mark: Mark,
    spec: CompanionScaleSpec,
    *,
    scale: float,
    tick_locations: Sequence[float] | None,
    formatter: str | Callable[[float], str] | None,
    precision: int,
    trim: Literal["k", ".", "0", "-"],
    label: str | None,
    label_center: Literal["axis", "spine"],
    label_style: dict[str, Any] | None,
    label_offset: int | None,
    show_spine: bool,
    show_ticks: bool,
    show_tick_labels: bool,
    ticks_near: int,
    ticks_far: int,
    spine_style: dict[str, Any] | None,
    ticks_style: dict[str, Any] | None,
    tick_labels_style: dict[str, Any] | None,
    tick_labels_offset: int,
    bounds: tuple[float, float, float, float] | None = None,
) -> Cartesian:
    """Apply one resolved scale spec to a hidden companion axes."""
    resolved_bounds = spec.bounds_getter() if bounds is None else bounds
    scale_axes._toytree_bounds_getter = spec.bounds_getter
    _store_scale_spec(scale_axes, mark, spec)

    if spec.use_tree_domain_mark:
        # Tree companions still rely on the hidden HostDomainMark /
        # TreeDomainMark pairing for host synchronization, but circular tree
        # rulers can clamp the visible active axis to one selected half-domain.
        add_tree_domain_mark(axes, ntable=mark.ntable, layout=mark.layout, mark=mark)
        sync_scale_cartesian_ranges(axes, scale_axes, bounds=resolved_bounds)
        _set_tree_scale_axis_domain(
            scale_axes,
            spec.axis,
            domain_override=spec.axis_domain,
        )
        axes.x.show = False
        axes.y.show = False
    else:
        # Mark companions carry their numeric scale directly in the resolved
        # data_domain instead of via hidden proxy marks.
        sync_mark_scale_cartesian(scale_axes, bounds=resolved_bounds)
        _set_mark_scale_axis_domain(
            scale_axes,
            spec.axis,
            spec.data_domain[0],
            spec.data_domain[1],
        )

    csize = (
        float(resolved_bounds[1] - resolved_bounds[0])
        if spec.axis == "x"
        else float(resolved_bounds[3] - resolved_bounds[2])
    )
    resolved_tick_locations = tick_locations
    if (
        spec.use_tree_domain_mark
        and mark.layout.startswith("c")
        and tick_locations is not None
    ):
        resolved_tick_locations = np.abs(np.asarray(tick_locations, dtype=float))
    tick_values = _resolve_tick_locations(
        csize=csize,
        tmin=spec.locator_domain[0],
        tmax=spec.locator_domain[1],
        tick_locations=resolved_tick_locations,
    )
    # Tip-bar companions on left / down layouts store outward depth on a
    # signed internal axis so value 0 stays at the bar baseline near tips.
    locs = tick_values * float(spec.locator_sign)
    labels = _format_tick_labels(locs, scale, formatter, precision, trim)

    _style_scale_axes(
        scale_axes=scale_axes,
        mark=mark,
        axis=spec.axis,
        show_spine=show_spine,
        show_ticks=show_ticks,
        show_tick_labels=show_tick_labels,
        ticks_near=ticks_near,
        ticks_far=ticks_far,
        tick_labels_style=tick_labels_style,
        tick_labels_offset=tick_labels_offset,
        label_offset=label_offset,
        spine_style=spine_style,
        ticks_style=ticks_style,
    )
    _set_scale_axis_label(
        scale_axes=scale_axes,
        mark=mark,
        axis=spec.axis,
        label=label,
        label_center=label_center,
        label_style=label_style,
        label_midpoint=spec.label_midpoint,
    )
    _set_scale_axis_locator(
        scale_axes,
        spec.axis,
        locs,
        labels,
        shift=spec.shift,
    )
    scale_axes._finalized = None
    return axes


def _add_axes_scale_bar_impl(
    tree: ToyTree,
    axes: Cartesian,
    axis: Literal["auto", "x", "y"] = "auto",
    show_spine: bool = True,
    show_ticks: bool = True,
    show_tick_labels: bool = True,
    label: str | None = None,
    label_center: Literal["axis", "spine"] = "spine",
    label_style: dict[str, Any] | None = None,
    label_offset: int | None = None,
    tick_locations: Sequence[float] | None = None,
    ticks_near: int = 0,
    ticks_far: int = 5,
    ticks_style: dict[str, Any] | None = None,
    tick_labels_style: dict[str, Any] | None = None,
    tick_labels_offset: int = 6,
    spine_style: dict[str, Any] | None = None,
    padding: float = 15.0,
    expand_margin: None | int | tuple[int, int, int, int] = None,
    scale: float = 1.0,
    formatter: str | Callable[[float], str] | None = None,
    precision: int = 6,
    trim: Literal["k", ".", "0", "-"] = "-",
    domain_override: tuple[float, float] | None = None,
    mark: ToyTreeMark | None = None,
) -> Cartesian:
    """Add a tree scale bar with an optional internal domain override."""
    if mark is None:
        mark = get_last_toytree_mark_for_tree(axes, tree)
    else:
        render_targets = axes._scenegraph.targets(axes, "render")
        if mark not in render_targets:
            raise ToytreeError("mark must be rendered on the provided axes.")
        assert_tree_matches_mark(tree, mark)
    _install_companion_add_mark_hook(axes)

    reused_sync = _prepare_axes_for_companion_update(axes, expand_margin)
    scale_axes = get_toytree_scale_cartesian(axes, mark=mark, create=True)
    spec = mark.get_companion_scale_spec(
        axes,
        axis=axis,
        padding=padding,
        domain_override=domain_override,
    )
    _configure_companion_scale_axes(
        axes,
        scale_axes,
        mark,
        spec,
        scale=scale,
        tick_locations=tick_locations,
        formatter=formatter,
        precision=precision,
        trim=trim,
        label=label,
        label_center=label_center,
        label_style=label_style,
        label_offset=label_offset,
        show_spine=show_spine,
        show_ticks=show_ticks,
        show_tick_labels=show_tick_labels,
        ticks_near=ticks_near,
        ticks_far=ticks_far,
        spine_style=spine_style,
        ticks_style=ticks_style,
        tick_labels_style=tick_labels_style,
        tick_labels_offset=tick_labels_offset,
    )
    if not reused_sync:
        _sync_tree_scale_axes_finalized(axes, skip_mark=mark)
        _sync_mark_scale_axes_finalized(axes)
    _align_companion_scale_axes(axes)
    _record_companion_sync_token(axes)
    return axes


@add_subpackage_method(AnnotationAPI)
def add_axes_scale_bar_to_tree(
    tree: ToyTree,
    axes: Cartesian,
    show_spine: bool = True,
    show_ticks: bool = True,
    show_tick_labels: bool = True,
    label: str | None = None,
    label_center: Literal["axis", "spine"] = "spine",
    label_style: dict[str, Any] | None = None,
    label_offset: int | None = None,
    tick_locations: Sequence[float] | None = None,
    ticks_near: int = 0,
    ticks_far: int = 5,
    ticks_style: dict[str, Any] | None = None,
    tick_labels_style: dict[str, Any] | None = None,
    tick_labels_offset: int = 6,
    spine_style: dict[str, Any] | None = None,
    padding: float = 15.0,
    expand_margin: None | int | tuple[int, int, int, int] = None,
    scale: float = 1.0,
    formatter: str | Callable[[float], str] | None = None,
    precision: int = 6,
    trim: Literal["k", ".", "0", "-"] = "-",
) -> Cartesian:
    """Add or update a tree-depth scale bar on companion axes.

    Parameters
    ----------
    axes : Cartesian
        Host axes containing a rendered ``ToyTreeMark``.
    show_spine : bool, default=True
        Show the scale-bar spine line.
    show_ticks : bool, default=True
        Show tick marks on the active scale axis.
    show_tick_labels : bool, default=True
        Show tick labels on the active scale axis.
    label : str or None, default=None
        Optional label text for the scale bar.
    label_center : {"axis", "spine"}, default="spine"
        Center the label on the full axis length or only on the visible spine.
    label_style : dict[str, Any] or None, default=None
        Style overrides applied to the axis label text.
    label_offset : int or None, default=None
        Pixel offset for the label. Positive values move it outward.
    tick_locations : Sequence[float] or None, default=None
        Explicit tick locations in tree units. Values outside the tree-depth
        domain are clipped to the nearest endpoint. If omitted, ticks are
        chosen automatically from the visible tree-depth domain. Circular and
        fan layouts use only one visible half-domain, and their tick locations
        are measured outward from zero on that selected side.
    ticks_near : int, default=0
        Tick length in pixels on the near side of the spine.
    ticks_far : int, default=5
        Tick length in pixels on the far side of the spine.
    ticks_style : dict[str, Any] or None, default=None
        Style overrides applied to tick marks.
    tick_labels_style : dict[str, Any] or None, default=None
        Style overrides applied to tick-label text.
    tick_labels_offset : int, default=6
        Pixel offset between tick marks and tick labels.
    spine_style : dict[str, Any] or None, default=None
        Style overrides applied to the visible spine line.
    padding : float, default=15.0
        Pixel gap between the rendered tree and its companion scale bar.
    expand_margin : int or tuple[int, int, int, int] or None, default=None
        Optional additive expansion of host-axes whitespace margins. Use this
        when the local gap would otherwise run into the canvas margin.
    scale : float, default=1.0
        Positive factor that divides displayed tick-label values.
    formatter : str or Callable[[float], str] or None, default=None
        Optional formatter for displayed tick labels.
    precision : int, default=6
        Precision used for default numeric label formatting.
    trim : {"k", ".", "0", "-"}, default="-"
        Trimming mode used for default numeric label formatting.

    Returns
    -------
    Cartesian
        The input host axes. The host remains responsible for fitting the
        union of visible tree content, annotation marks, and later host data
        marks, while the companion axes renders only the tree scale bar. The
        scale-bar domain is fixed by the tree depth shown in the drawing.
        Circular full-circle layouts render only the positive half of the
        chosen companion axis, while circular fan layouts render the longer
        positive or negative half; negative-side fan labels are displayed as
        positive outward distances. Tick locations are generated automatically
        from that visible domain unless ``tick_locations`` is provided
        explicitly, in which case out-of-domain values are clipped to the
        visible domain endpoints.

    Raises
    ------
    ToytreeError
        If ``padding`` or ``scale`` is invalid.
    ValueError
        If ``expand_margin`` is invalid.
    """
    return _add_axes_scale_bar_impl(
        tree=tree,
        axes=axes,
        show_spine=show_spine,
        show_ticks=show_ticks,
        show_tick_labels=show_tick_labels,
        label=label,
        label_center=label_center,
        label_style=label_style,
        label_offset=label_offset,
        tick_locations=tick_locations,
        ticks_near=ticks_near,
        ticks_far=ticks_far,
        ticks_style=ticks_style,
        tick_labels_style=tick_labels_style,
        tick_labels_offset=tick_labels_offset,
        spine_style=spine_style,
        padding=padding,
        expand_margin=expand_margin,
        scale=_validate_scale_factor(scale, "tree"),
        formatter=formatter,
        precision=precision,
        trim=trim,
    )


@add_subpackage_method(AnnotationAPI)
def add_axes_scale_bar_to_mark(
    tree: ToyTree,
    axes: Cartesian,
    mark: Mark,
    show_spine: bool = True,
    show_ticks: bool = True,
    show_tick_labels: bool = True,
    label: str | None = None,
    label_center: Literal["axis", "spine"] = "spine",
    label_style: dict[str, Any] | None = None,
    label_offset: int | None = None,
    tick_locations: Sequence[float] | None = None,
    ticks_near: int = 0,
    ticks_far: int = 5,
    ticks_style: dict[str, Any] | None = None,
    tick_labels_style: dict[str, Any] | None = None,
    tick_labels_offset: int = 6,
    spine_style: dict[str, Any] | None = None,
    padding: float = 15.0,
    expand_margin: None | int | tuple[int, int, int, int] = None,
    scale: float = 1.0,
    formatter: str | Callable[[float], str] | None = None,
    precision: int = 6,
    trim: Literal["k", ".", "0", "-"] = "-",
) -> Cartesian:
    """Add or update a scale bar for a scale-capable annotation mark.

    Parameters
    ----------
    axes : Cartesian
        Host axes containing the target annotation mark.
    mark : Mark
        Rendered mark to scale. This can be a scale-capable annotation mark
        or a rendered ``ToyTreeMark`` for exact per-tree targeting on shared
        host axes.
    show_spine : bool, default=True
        Show the scale-bar spine line.
    show_ticks : bool, default=True
        Show tick marks on the active scale axis.
    show_tick_labels : bool, default=True
        Show tick labels on the active scale axis.
    label : str or None, default=None
        Optional label text for the scale bar.
    label_center : {"axis", "spine"}, default="spine"
        Center the label on the full axis length or only on the visible spine.
    label_style : dict[str, Any] or None, default=None
        Style overrides applied to the axis label text.
    label_offset : int or None, default=None
        Pixel offset for the label. Positive values move it outward.
    tick_locations : Sequence[float] or None, default=None
        Explicit tick locations in mark-value units. Values outside the mark
        data domain are clipped to the nearest endpoint. If omitted, ticks
        are chosen automatically from the mark data domain.
    ticks_near : int, default=0
        Tick length in pixels on the near side of the spine.
    ticks_far : int, default=5
        Tick length in pixels on the far side of the spine.
    ticks_style : dict[str, Any] or None, default=None
        Style overrides applied to tick marks.
    tick_labels_style : dict[str, Any] or None, default=None
        Style overrides applied to tick-label text.
    tick_labels_offset : int, default=6
        Pixel offset between tick marks and tick labels.
    spine_style : dict[str, Any] or None, default=None
        Style overrides applied to the visible spine line.
    padding : float, default=15.0
        Pixel gap between the target mark and its companion scale bar.
        This affects only the mark scale-bar overlay, not the host axes or
        tree scale-bar companion axes. If a tree scale bar already exists on
        the same host axes, compatible mark scale bars align to that existing
        spine row when it still satisfies this minimum gap.
    expand_margin : int or tuple[int, int, int, int] or None, default=None
        Optional additive expansion of host-axes whitespace margins. Use this
        to create more canvas room for the shifted mark scale bar.
    scale : float, default=1.0
        Positive factor that divides displayed tick-label values.
    formatter : str or Callable[[float], str] or None, default=None
        Optional formatter for displayed tick labels.
    precision : int, default=6
        Precision used for default numeric label formatting.
    trim : {"k", ".", "0", "-"}, default="-"
        Trimming mode used for default numeric label formatting.

    Returns
    -------
    Cartesian
        The input host axes. The host remains responsible for fitting the
        union of visible tree content, annotation marks, and later host data
        marks, while the companion axes renders only the mark scale bar. The
        scale-bar domain is fixed by the mark's value data, and tick
        locations are generated automatically unless ``tick_locations`` is
        provided explicitly, in which case out-of-domain values are clipped to
        the domain endpoints.

    Raises
    ------
    ToytreeError
        If ``mark`` is unsupported, is not rendered on ``axes``, or if
        ``scale`` / ``padding`` is invalid.
    ValueError
        If ``expand_margin`` is invalid.
    """
    render_targets = axes._scenegraph.targets(axes, "render")
    if mark not in render_targets:
        raise ToytreeError("mark must be rendered on the provided axes.")
    if isinstance(mark, ToyTreeMark):
        return _add_axes_scale_bar_impl(
            tree=tree,
            axes=axes,
            mark=mark,
            show_spine=show_spine,
            show_ticks=show_ticks,
            show_tick_labels=show_tick_labels,
            label=label,
            label_center=label_center,
            label_style=label_style,
            label_offset=label_offset,
            tick_locations=tick_locations,
            ticks_near=ticks_near,
            ticks_far=ticks_far,
            ticks_style=ticks_style,
            tick_labels_style=tick_labels_style,
            tick_labels_offset=tick_labels_offset,
            spine_style=spine_style,
            padding=padding,
            expand_margin=expand_margin,
            scale=_validate_scale_factor(scale, "tree"),
            formatter=formatter,
            precision=precision,
            trim=trim,
        )

    # Get the rendered tree mark associated with this Tree on these axes.
    tmark = get_last_toytree_mark_for_tree(axes, tree)
    assert_tree_matches_mark(tree, tmark)
    if isinstance(mark, AnnotationTipPathMark):
        raise ToytreeError("Tip-path marks do not support companion scale axes.")
    if not hasattr(mark, "get_companion_scale_spec"):
        raise ToytreeError("mark does not define companion scale metadata.")

    # validate scale arg is numeric
    scale = _validate_scale_factor(scale, "mark")

    reused_sync = _prepare_axes_for_companion_update(axes, expand_margin)

    # get specifications for the companion scale
    spec = mark.get_companion_scale_spec(
        axes,
        padding=padding,
    )

    # lambda func that returns bounds of the data on the Mark
    # that are relevant to the scale bar only.
    mark_bounds = spec.bounds_getter()

    # create a new companion Cartesian for showing the scale bar
    scale_axes = get_mark_scale_cartesian(
        axes,
        mark,
        create=True,
        bounds_getter=spec.bounds_getter,
        bounds=mark_bounds,
    )

    # wrap ``add_mark`` so later marks will refresh the companions
    _install_companion_add_mark_hook(axes)

    # set style specifications on the companion scale bar
    _configure_companion_scale_axes(
        axes,
        scale_axes,
        mark,
        spec,
        scale=scale,
        tick_locations=tick_locations,
        formatter=formatter,
        precision=precision,
        trim=trim,
        label=label,
        label_center=label_center,
        label_style=label_style,
        label_offset=label_offset,
        show_spine=show_spine,
        show_ticks=show_ticks,
        show_tick_labels=show_tick_labels,
        ticks_near=ticks_near,
        ticks_far=ticks_far,
        spine_style=spine_style,
        ticks_style=ticks_style,
        tick_labels_style=tick_labels_style,
        tick_labels_offset=tick_labels_offset,
        bounds=mark_bounds,
    )

    if not reused_sync:
        # if a tree companion exists update it
        _sync_tree_scale_axes_finalized(axes)

        # if >=1 mark companions exist update them
        _sync_mark_scale_axes_finalized(axes, skip_mark=mark)

    # if both exist make them align visually
    _align_companion_scale_axes(axes)
    _record_companion_sync_token(axes)
    return axes
