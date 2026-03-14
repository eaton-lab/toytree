#!/usr/bin/env python

"""Helpers for managing hidden companion Cartesian axes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

from toyplot.coordinates import Cartesian
from toyplot.mark import Mark

from toytree.drawing.src.mark_tree_domain import HostDomainMark, TreeDomainMark


@dataclass(slots=True)
class CompanionScaleSpec:
    """Resolved geometry and domain metadata for one companion scale axes."""

    key: Literal["tree", "mark"]
    axis: Literal["x", "y"]
    data_domain: tuple[float, float]
    locator_domain: tuple[float, float]
    bounds_getter: Callable[[], tuple[float, float, float, float]]
    label_midpoint: float
    shift: float = 0.0
    use_tree_domain_mark: bool = False


def _get_canvas_for_axes(axes: Cartesian):
    """Return the canvas that renders an axes object."""
    return axes._scenegraph.sources("render", axes)[0]


def _disable_companion_interactive_coordinates(axes: Cartesian) -> None:
    """Hide duplicate interactive coordinate readouts on companion axes."""
    axes.x.interactive.coordinates.show = False
    axes.y.interactive.coordinates.show = False


def _get_companion_axes_registry(axes: Cartesian) -> dict[str, Any]:
    """Return the host registry that tracks hidden companion Cartesians."""
    registry = getattr(axes, "_toytree_companion_axes_registry", None)
    if registry is None:
        registry = {
            "tree": getattr(axes, "_toytree_scale_axes", None),
            "marks": getattr(axes, "_toytree_mark_scale_axes", None) or {},
        }
        axes._toytree_companion_axes_registry = registry
    return registry


def _ensure_companion_axes_render_order(
    axes: Cartesian,
    companion_axes: Cartesian,
) -> None:
    """Keep companion axes before the host axes in render order."""
    canvas = _get_canvas_for_axes(axes)
    targets = axes._scenegraph._relationships["render"]._targets[canvas]
    if (axes in targets) and (companion_axes in targets):
        targets.remove(companion_axes)
        targets.insert(targets.index(axes), companion_axes)


def _set_cartesian_bounds(
    axes: Cartesian,
    bounds: tuple[float, float, float, float],
    padding: float = 0.0,
) -> None:
    """Apply explicit pixel bounds to one companion axes."""
    xmin, xmax, ymin, ymax = [float(i) for i in bounds]
    axes._set_xmin_range(xmin)
    axes._set_xmax_range(xmax)
    axes._set_ymin_range(ymin)
    axes._set_ymax_range(ymax)
    axes.padding = float(padding)
    axes._finalized = None


def sync_scale_cartesian_ranges(
    axes: Cartesian,
    scale_axes: Cartesian,
    bounds: tuple[float, float, float, float] | None = None,
) -> None:
    """Keep a tree scale-bar companion axes aligned to the host axes."""
    if bounds is not None:
        _set_cartesian_bounds(scale_axes, bounds, padding=0.0)
        return

    bounds_getter = getattr(scale_axes, "_toytree_bounds_getter", None)
    if bounds_getter is None:
        _set_cartesian_bounds(
            scale_axes,
            (
                float(axes._xmin_range),
                float(axes._xmax_range),
                float(axes._ymin_range),
                float(axes._ymax_range),
            ),
            padding=float(axes.padding),
        )
    else:
        _set_cartesian_bounds(scale_axes, bounds_getter(), padding=0.0)


def _get_mark_scale_axes_registry(axes: Cartesian) -> dict[int, Cartesian]:
    """Return the mark-scale registry stored on a host Cartesian."""
    registry = _get_companion_axes_registry(axes)["marks"]
    axes._toytree_mark_scale_axes = registry
    return registry


def sync_mark_scale_cartesian(
    scale_axes: Cartesian,
    bounds: tuple[float, float, float, float] | None = None,
) -> None:
    """Recompute one mark-scale overlay bounds from its stored callback."""
    if bounds is not None:
        _set_cartesian_bounds(scale_axes, bounds)
        return

    bounds_getter = getattr(scale_axes, "_toytree_bounds_getter", None)
    if bounds_getter is None:
        return
    _set_cartesian_bounds(scale_axes, bounds_getter())


def sync_mark_scale_cartesians(
    axes: Cartesian,
    skip_mark: Mark | None = None,
) -> None:
    """Recompute all registered mark-scale overlay bounds for a host axes."""
    registry = getattr(axes, "_toytree_mark_scale_axes", None)
    if not registry:
        return
    skip_id = None if skip_mark is None else id(skip_mark)
    for mark_id, scale_axes in registry.items():
        if mark_id == skip_id:
            continue
        sync_mark_scale_cartesian(scale_axes)


def get_mark_scale_cartesian(
    axes: Cartesian,
    mark: Mark,
    create: bool = True,
    bounds_getter: Callable[[], tuple[float, float, float, float]] | None = None,
    bounds: tuple[float, float, float, float] | None = None,
) -> Cartesian | None:
    """Return a hidden companion axes used to draw one mark scale bar."""
    registry = _get_mark_scale_axes_registry(axes)
    scale_axes = registry.get(id(mark))
    if scale_axes is not None:
        _disable_companion_interactive_coordinates(scale_axes)
        if bounds_getter is not None:
            scale_axes._toytree_bounds_getter = bounds_getter
        if bounds is not None:
            sync_mark_scale_cartesian(scale_axes, bounds=bounds)
        elif bounds_getter is not None:
            sync_mark_scale_cartesian(scale_axes)
        return scale_axes
    if not create:
        return None
    if bounds_getter is None:
        raise ValueError("bounds_getter is required when creating mark scale axes.")

    canvas = _get_canvas_for_axes(axes)
    if bounds is None:
        # Callers that already projected finalized bounds can pass them through
        # and skip a second bounds_getter() call during companion creation.
        bounds = bounds_getter()
    xmin, xmax, ymin, ymax = [float(i) for i in bounds]
    scale_axes = canvas.cartesian(
        bounds=(xmin, xmax, ymin, ymax),
        margin=0,
        padding=0,
        show=False,
        xshow=False,
        yshow=False,
    )
    scale_axes._toytree_host_axes = axes
    scale_axes._toytree_target_mark = mark
    scale_axes._toytree_bounds_getter = bounds_getter
    registry[id(mark)] = scale_axes
    _disable_companion_interactive_coordinates(scale_axes)
    _ensure_companion_axes_render_order(axes, scale_axes)
    return scale_axes


def get_toytree_scale_cartesian(
    axes: Cartesian, create: bool = True
) -> Cartesian | None:  # noqa: E501
    """Return hidden companion axes used to draw tree scale bars."""
    registry = _get_companion_axes_registry(axes)
    scale_axes = registry.get("tree")
    if scale_axes is not None:
        _disable_companion_interactive_coordinates(scale_axes)
        return scale_axes
    if not create:
        return scale_axes

    canvas = _get_canvas_for_axes(axes)
    scale_axes = canvas.cartesian(
        bounds=(
            float(axes._xmin_range),
            float(axes._xmax_range),
            float(axes._ymin_range),
            float(axes._ymax_range),
        ),
        margin=0,
        padding=float(axes.padding),
        show=False,
        xshow=False,
        yshow=False,
    )
    # Mirror the host display-domain onto the companion axes while
    # keeping tree-only data-domain from TreeDomainMark children.
    scale_axes.add_mark(HostDomainMark(host_axes=axes))
    scale_axes._toytree_host_axes = axes
    registry["tree"] = scale_axes
    axes._toytree_scale_axes = scale_axes
    _disable_companion_interactive_coordinates(scale_axes)
    _ensure_companion_axes_render_order(axes, scale_axes)
    return scale_axes


def add_tree_domain_mark(axes: Cartesian, ntable, layout: str) -> TreeDomainMark:
    """Create or update the tree-domain mark on the companion scale axes."""
    scale_axes = get_toytree_scale_cartesian(axes, create=True)
    dmark = getattr(scale_axes, "_toytree_tree_domain_mark", None)
    if dmark is None:
        render_targets = scale_axes._scenegraph.targets(scale_axes, "render")
        existing = [mark for mark in render_targets if isinstance(mark, TreeDomainMark)]
        if existing:
            dmark = existing[-1]
        else:
            dmark = TreeDomainMark(ntable=ntable, layout=layout)
            scale_axes.add_mark(dmark)
        scale_axes._toytree_tree_domain_mark = dmark
    dmark.ntable = ntable
    dmark.layout = layout
    scale_axes._finalized = None
    return dmark
