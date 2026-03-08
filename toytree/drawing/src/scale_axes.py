#!/usr/bin/env python

"""Helpers for managing hidden scale-bar companion Cartesian axes."""

from __future__ import annotations

from toyplot.coordinates import Cartesian

from toytree.drawing.src.mark_tree_domain import HostDomainMark, TreeDomainMark


def _get_canvas_for_axes(axes: Cartesian):
    """Return the canvas that renders an axes object."""
    return axes._scenegraph.sources("render", axes)[0]


def sync_scale_cartesian_ranges(axes: Cartesian, scale_axes: Cartesian) -> None:
    """Keep companion scale-axes canvas ranges synchronized with host axes."""
    scale_axes._set_xmin_range(float(axes._xmin_range))
    scale_axes._set_xmax_range(float(axes._xmax_range))
    scale_axes._set_ymin_range(float(axes._ymin_range))
    scale_axes._set_ymax_range(float(axes._ymax_range))
    scale_axes.padding = float(axes.padding)
    scale_axes._finalized = None


def _ensure_scale_axes_render_order(axes: Cartesian, scale_axes: Cartesian) -> None:
    """Keep scale axes after host axes so scale graphics render on top."""
    canvas = _get_canvas_for_axes(axes)
    targets = axes._scenegraph._relationships["render"]._targets[canvas]
    if (axes in targets) and (scale_axes in targets):
        targets.remove(scale_axes)
        targets.insert(targets.index(axes) + 1, scale_axes)


def get_toytree_scale_cartesian(
    axes: Cartesian, create: bool = True
) -> Cartesian | None:  # noqa: E501
    """Return hidden companion axes used to draw tree scale bars."""
    scale_axes = getattr(axes, "_toytree_scale_axes", None)
    if (scale_axes is not None) or (not create):
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
    axes._toytree_scale_axes = scale_axes
    _ensure_scale_axes_render_order(axes, scale_axes)
    return scale_axes


def add_tree_domain_mark(axes: Cartesian, ntable, layout: str) -> TreeDomainMark:
    """Add a tree-domain mark to the companion scale axes for one draw call."""
    scale_axes = get_toytree_scale_cartesian(axes, create=True)
    dmark = TreeDomainMark(ntable=ntable, layout=layout)
    scale_axes.add_mark(dmark)
    scale_axes._finalized = None
    return dmark
