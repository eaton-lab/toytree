#!/usr/bin/env python

"""Utility functions for annotations."""

from __future__ import annotations

from typing import Any

# from toyplot.canvas import Canvas
import numpy as np
from toyplot.coordinates import (
    _cartesian_max_extent_overflow_px,
    _cartesian_projected_domain_tuple,
    _cartesian_reset_expand_cache,
    _create_projection,
)

from toytree.core import ToyTree
from toytree.drawing import Cartesian, Mark, ToyTreeMark
from toytree.drawing.src.mark_annotation import AnnotationTipBarMark
from toytree.drawing.src.scale_axes import (
    get_toytree_scale_cartesian as _get_scale_axes,
)
from toytree.utils import ToytreeError

CARTESIAN_TYPE_ERROR = """\
'axes' argument to annotation func must be a Cartesian object
containing a ToyTree Mark (drawing). For example:

>>> # get Cartesian axes from a toytree drawing
>>> canvas, axes, mark = tree.draw()
>>> tree.annotate.add_tip_markers(axes, size=9, color='red', xshift=20)
"""
TOYTREE_CARTESIAN_FIT_PX_TOL = 0.5
TOYTREE_CARTESIAN_FIT_EXTRA_ITER = 10


def get_last_toytree_mark(axes: Cartesian) -> ToyTreeMark:
    """Return the last ToyTreeMark rendered on the Cartesian axes."""
    return get_toytree_marks(axes)[-1]


def get_toytree_marks(axes: Cartesian) -> list[ToyTreeMark]:
    """Return all rendered ``ToyTreeMark`` objects on one Cartesian axes."""
    if not isinstance(axes, Cartesian):
        raise TypeError(CARTESIAN_TYPE_ERROR)
    targets = axes._scenegraph.targets(axes, "render")
    tree_marks = [i for i in targets if isinstance(i, ToyTreeMark)]
    if not tree_marks:
        raise ToytreeError(
            "No tree drawings (ToyTreeMark) have been rendered on the "
            "Cartesian axes. First draw a ToyTree."
        )
    return tree_marks


def get_last_toytree_mark_for_tree(axes: Cartesian, tree: ToyTree) -> ToyTreeMark:
    """Return the newest rendered mark associated with one ``ToyTree``."""
    tree_marks = get_toytree_marks(axes)
    matches = [
        mark
        for mark in tree_marks
        if getattr(mark, "_toytree_source_tree", None) is tree
    ]
    if matches:
        return matches[-1]

    # Backward-compatible fallback for older marks that do not record their
    # source tree identity. Preserve single-tree behavior but refuse to guess
    # on shared axes where "last rendered" can silently annotate the wrong tree.
    if len(tree_marks) > 1:
        raise ToytreeError(
            "Multiple ToyTreeMarks are rendered on these Cartesian axes, "
            "but none record source-tree identity for the provided tree. "
            "Tree selection is ambiguous."
        )
    mark = tree_marks[0]
    assert_tree_matches_mark(tree, mark)
    return mark


def assert_tree_matches_mark(tree: ToyTree, mark: Mark) -> None:
    """Raise exception if mark does not match up with tree data."""
    nnodes_in_mark = mark.ntable.shape[0]
    assert tree.nnodes == nnodes_in_mark, (
        f"Cannot annotate a tree drawing containing {tree.nnodes} nodes "
        f"with a different tree that has {nnodes_in_mark} nodes."
    )


def get_toytree_scale_cartesian(
    axes: Cartesian,
    mark: ToyTreeMark | None = None,
    create: bool = False,
) -> Cartesian | None:  # noqa: E501
    """Return the hidden companion Cartesian used for tree scale bars."""
    return _get_scale_axes(axes, mark=mark, create=create)


def invalidate_cartesian_fit_cache(axes: Cartesian) -> None:
    """Invalidate Toyplot Cartesian fit / extent caches after adding marks.

    Toyplot's ``Cartesian.add_mark()`` links the mark into the scenegraph
    but does not clear previously cached finalize state. If a canvas has
    already been rendered, autosize / clipping can remain stale unless
    these caches are reset before the next render.
    """
    axes._finalized = None
    axes._expand_domain_range_x = None
    axes._expand_domain_range_y = None
    axes._expand_domain_range_left = None
    axes._expand_domain_range_right = None
    axes._expand_domain_range_top = None
    axes._expand_domain_range_bottom = None
    increment_cartesian_geometry_token(axes)

    # Keep every registered companion axes dirty so projections stay
    # synchronized after host extents change.
    tree_registry = getattr(axes, "_toytree_tree_scale_axes", None) or {}
    mark_registry = getattr(axes, "_toytree_mark_scale_axes", None) or {}
    companions = list(tree_registry.values()) + list(mark_registry.values())
    if not companions:
        scale_axes = get_toytree_scale_cartesian(axes, create=False)
        companions = [] if scale_axes is None else [scale_axes]

    for scale_axes in companions:
        scale_axes._finalized = None
        scale_axes._expand_domain_range_x = None
        scale_axes._expand_domain_range_y = None
        scale_axes._expand_domain_range_left = None
        scale_axes._expand_domain_range_right = None
        scale_axes._expand_domain_range_top = None
        scale_axes._expand_domain_range_bottom = None


def increment_cartesian_geometry_token(axes: Cartesian) -> int:
    """Advance the host-geometry token and clear geometry-derived caches."""
    token = int(getattr(axes, "_toytree_host_geometry_token", 0)) + 1
    axes._toytree_host_geometry_token = token
    axes._toytree_projected_tip_slot_cache = None
    return token


def _coerce_mark_domain(domain: Any) -> tuple[float, float] | None:
    """Return one finite increasing mark-domain pair or None."""
    if domain is None:
        return None
    try:
        dmin = float(domain[0])
        dmax = float(domain[1])
    except (TypeError, IndexError, ValueError):
        return None
    if (not np.isfinite(dmin)) or (not np.isfinite(dmax)) or dmax < dmin:
        return None
    return dmin, dmax


def _append_extent_cache(
    current: np.ndarray | None,
    update: np.ndarray,
) -> np.ndarray:
    """Append one mark contribution onto cached Cartesian extent arrays."""
    update = np.asarray(update, dtype=float)
    if current is None:
        return update.copy()
    return np.concatenate((np.asarray(current, dtype=float), update))


def _domain_minmax(*values: float | np.ndarray) -> tuple[float, float]:
    """Return finite min / max bounds across scalar and array inputs."""
    merged = np.concatenate(
        [np.atleast_1d(np.asarray(value, dtype=float)) for value in values]
    )
    return float(np.min(merged)), float(np.max(merged))


def _finalize_cartesian_from_cached_state(
    axes: Cartesian,
    projected_domain: tuple[float, float, float, float],
) -> float:
    """Finalize a Cartesian using cached domain / extent arrays only.

    This mirrors the post-child-scan portion of Toyplot's Cartesian
    finalize logic so toytree can update a current Cartesian after adding
    one more mark without rescanning every existing child.
    """
    xdomain_min = float(projected_domain[0])
    xdomain_max = float(projected_domain[1])
    ydomain_min = float(projected_domain[2])
    ydomain_max = float(projected_domain[3])

    if xdomain_min == xdomain_max:
        xdomain_min -= 0.5
        xdomain_max += 0.5
    if ydomain_min == ydomain_max:
        ydomain_min -= 0.5
        ydomain_max += 0.5

    if axes._expand_domain_range_x is not None:
        x_projection = _create_projection(
            axes.x.scale,
            domain_min=xdomain_min,
            domain_max=xdomain_max,
            range_min=axes._xmin_range,
            range_max=axes._xmax_range,
        )
        range_x = x_projection(axes._expand_domain_range_x)
        range_left = range_x + axes._expand_domain_range_left
        range_right = range_x + axes._expand_domain_range_right
        domain_left = x_projection.inverse(range_left)
        domain_right = x_projection.inverse(range_right)
        xdomain_min, xdomain_max = _domain_minmax(
            xdomain_min,
            xdomain_max,
            domain_left,
            domain_right,
        )

    if axes._expand_domain_range_y is not None:
        y_projection = _create_projection(
            axes.y.scale,
            domain_min=ydomain_min,
            domain_max=ydomain_max,
            range_min=axes._ymax_range,
            range_max=axes._ymin_range,
        )
        range_y = y_projection(axes._expand_domain_range_y)
        range_top = range_y + axes._expand_domain_range_top
        range_bottom = range_y + axes._expand_domain_range_bottom
        domain_top = y_projection.inverse(range_top)
        domain_bottom = y_projection.inverse(range_bottom)
        ydomain_min, ydomain_max = _domain_minmax(
            ydomain_min,
            ydomain_max,
            domain_top,
            domain_bottom,
        )

    if axes._aspect == "fit-range":
        dwidth = xdomain_max - xdomain_min
        dheight = ydomain_max - ydomain_min
        daspect = dwidth / dheight
        raspect = (axes._xmax_range - axes._xmin_range) / (
            axes._ymax_range - axes._ymin_range
        )
        if daspect < raspect:
            offset = ((dwidth * (raspect / daspect)) - dwidth) * 0.5
            xdomain_min -= offset
            xdomain_max += offset
        elif daspect > raspect:
            offset = ((dheight * (daspect / raspect)) - dheight) * 0.5
            ydomain_min -= offset
            ydomain_max += offset

    if axes.x.domain.min is not None:
        xdomain_min = axes.x.domain.min
    if axes.x.domain.max is not None:
        xdomain_max = axes.x.domain.max
    if axes.y.domain.min is not None:
        ydomain_min = axes.y.domain.min
    if axes.y.domain.max is not None:
        ydomain_max = axes.y.domain.max

    if xdomain_min == xdomain_max:
        xdomain_min -= 0.5
        xdomain_max += 0.5
    if ydomain_min == ydomain_max:
        ydomain_min -= 0.5
        ydomain_max += 0.5

    xtick_locations = []
    xtick_labels = []
    xtick_titles = []
    if axes.show and axes.x.show:
        xtick_locations, xtick_labels, xtick_titles = axes.x._locator().ticks(
            xdomain_min,
            xdomain_max,
        )
    ytick_locations = []
    ytick_labels = []
    ytick_titles = []
    if axes.show and axes.y.show:
        ytick_locations, ytick_labels, ytick_titles = axes.y._locator().ticks(
            ydomain_min,
            ydomain_max,
        )

    if len(xtick_locations):
        xdomain_min = np.amin((xdomain_min, xtick_locations[0]))
        xdomain_max = np.amax((xdomain_max, xtick_locations[-1]))
    if len(ytick_locations):
        ydomain_min = np.amin((ydomain_min, ytick_locations[0]))
        ydomain_max = np.amax((ydomain_max, ytick_locations[-1]))

    axes._x_projection = _create_projection(
        scale=axes.x.scale,
        domain_min=xdomain_min,
        domain_max=xdomain_max,
        range_min=axes._xmin_range,
        range_max=axes._xmax_range,
    )
    axes._y_projection = _create_projection(
        scale=axes.y.scale,
        domain_min=ydomain_min,
        domain_max=ydomain_max,
        range_min=axes._ymax_range,
        range_max=axes._ymin_range,
    )

    if axes.x.spine.position == "low":
        x_offset = axes.padding
        x_spine_y = axes._ymax_range
        x_ticks_near = 0
        x_ticks_far = 5
        x_tick_location = "below"
        x_label_location = "below"
    elif axes.x.spine.position == "high":
        x_offset = -axes.padding
        x_spine_y = axes._ymin_range
        x_ticks_near = 5
        x_ticks_far = 0
        x_tick_location = "above"
        x_label_location = "above"
    else:
        x_offset = 0
        x_spine_y = axes._y_projection(axes.x.spine.position)
        x_ticks_near = 3
        x_ticks_far = 3
        x_tick_location = "below"
        x_label_location = "below"

    if axes.y.spine._position == "low":
        y_offset = -axes.padding
        y_spine_x = axes._xmin_range
        y_ticks_near = 0
        y_ticks_far = 5
        y_tick_location = "above"
        y_label_location = "above"
    elif axes.y.spine._position == "high":
        y_offset = axes.padding
        y_spine_x = axes._xmax_range
        y_ticks_near = 0
        y_ticks_far = 5
        y_tick_location = "below"
        y_label_location = "below"
    else:
        y_offset = 0
        y_spine_x = axes._x_projection(axes.y.spine._position)
        y_ticks_near = 3
        y_ticks_far = 3
        y_tick_location = "below"
        y_label_location = "below"

    axes.x._finalized = None
    axes.y._finalized = None
    axes.x._finalize(
        x1=axes._xmin_range,
        x2=axes._xmax_range,
        y1=x_spine_y,
        y2=x_spine_y,
        offset=x_offset,
        domain_min=xdomain_min,
        domain_max=xdomain_max,
        tick_locations=xtick_locations,
        tick_labels=xtick_labels,
        tick_titles=xtick_titles,
        default_tick_location=x_tick_location,
        default_ticks_far=x_ticks_far,
        default_ticks_near=x_ticks_near,
        default_label_location=x_label_location,
    )
    axes.y._finalize(
        x1=y_spine_x,
        x2=y_spine_x,
        y1=axes._ymax_range,
        y2=axes._ymin_range,
        offset=y_offset,
        domain_min=ydomain_min,
        domain_max=ydomain_max,
        tick_locations=ytick_locations,
        tick_labels=ytick_labels,
        tick_titles=ytick_titles,
        default_tick_location=y_tick_location,
        default_ticks_far=y_ticks_far,
        default_ticks_near=y_ticks_near,
        default_label_location=y_label_location,
    )
    axes._finalized = axes
    return _cartesian_max_extent_overflow_px(axes)


def try_incremental_tip_bar_host_finalize(axes: Cartesian, mark: Mark) -> bool:
    """Incrementally update one finalized Cartesian for a new tip-bar mark."""
    if not isinstance(mark, AnnotationTipBarMark):
        return False
    if mark.layout not in ("r", "l", "u", "d"):
        return False
    if getattr(axes, "_finalized", None) is None:
        return False
    if any(
        getattr(axes, attr, None) is None
        for attr in (
            "_x_projection",
            "_y_projection",
            "_expand_domain_range_x",
            "_expand_domain_range_y",
            "_expand_domain_range_left",
            "_expand_domain_range_right",
            "_expand_domain_range_top",
            "_expand_domain_range_bottom",
        )
    ):
        return False

    xdomain = _coerce_mark_domain(mark.domain("x"))
    ydomain = _coerce_mark_domain(mark.domain("y"))
    if xdomain is None or ydomain is None:
        return False

    coords, extents = mark.extents(["x", "y"])
    xcoords = np.asarray(coords[0], dtype=float)
    ycoords = np.asarray(coords[1], dtype=float)
    left, right, top, bottom = [np.asarray(arr, dtype=float) for arr in extents]
    if (
        xcoords.size == 0
        or ycoords.size == 0
        or any(arr.size != xcoords.size for arr in (left, right, top, bottom))
    ):
        return False

    projected_domain = _cartesian_projected_domain_tuple(axes)
    if any(not np.isfinite(val) for val in projected_domain):
        return False

    increment_cartesian_geometry_token(axes)
    axes.x._update_domain(xdomain, display=False, data=not mark.annotation)
    axes.y._update_domain(ydomain, display=False, data=not mark.annotation)

    # Reuse the finalized host caches and append only the new mark instead of
    # rebuilding them from every mapped child on the Cartesian.
    axes._expand_domain_range_x = _append_extent_cache(
        axes._expand_domain_range_x,
        xcoords,
    )
    axes._expand_domain_range_y = _append_extent_cache(
        axes._expand_domain_range_y,
        ycoords,
    )
    axes._expand_domain_range_left = _append_extent_cache(
        axes._expand_domain_range_left,
        left,
    )
    axes._expand_domain_range_right = _append_extent_cache(
        axes._expand_domain_range_right,
        right,
    )
    axes._expand_domain_range_top = _append_extent_cache(
        axes._expand_domain_range_top,
        top,
    )
    axes._expand_domain_range_bottom = _append_extent_cache(
        axes._expand_domain_range_bottom,
        bottom,
    )

    axes._finalized = None
    domain = (
        min(float(projected_domain[0]), xdomain[0]),
        max(float(projected_domain[1]), xdomain[1]),
        min(float(projected_domain[2]), ydomain[0]),
        max(float(projected_domain[3]), ydomain[1]),
    )
    overflow = _finalize_cartesian_from_cached_state(axes, domain)
    previous_domain = _cartesian_projected_domain_tuple(axes)
    # Cached projected-domain restarts can converge a little more slowly than
    # Toyplot's full child rescan on large-offset annotations, so give this
    # private fast path a small extra buffer before falling back.
    extra_iterations = TOYTREE_CARTESIAN_FIT_EXTRA_ITER + 2
    for idx in range(extra_iterations):
        if overflow <= TOYTREE_CARTESIAN_FIT_PX_TOL:
            break
        if idx < (extra_iterations - 1):
            axes._finalized = None

        # Reuse the last projected viewport as the next starting point so we
        # can settle fit-overflow without rescanning all existing children.
        overflow = _finalize_cartesian_from_cached_state(axes, previous_domain)
        previous_domain = _cartesian_projected_domain_tuple(axes)
    return overflow <= TOYTREE_CARTESIAN_FIT_PX_TOL


def stabilize_cartesian_fit(
    axes: Cartesian,
    extra_iterations: int = TOYTREE_CARTESIAN_FIT_EXTRA_ITER,
) -> None:
    """Finalize one Cartesian and lightly extend autosize if needed.

    Toyplot's finalize pass is usually sufficient on its own, but large
    pixel-offset annotations can still leave a small amount of residual
    overflow. This helper allows a few extra projected-domain passes to
    settle those cases without chasing subpixel-perfect convergence.
    """
    axes._finalize()
    overflow = _cartesian_max_extent_overflow_px(axes)
    if overflow <= TOYTREE_CARTESIAN_FIT_PX_TOL:
        return

    extra_iterations = int(extra_iterations)
    xaxis = axes.x
    yaxis = axes.y
    previous_domain = _cartesian_projected_domain_tuple(axes)

    # Reuse Toyplot's own iterative expansion logic, but allow a few
    # extra rounds and a tighter tolerance for large annotation offsets.
    for idx in range(extra_iterations):
        _cartesian_reset_expand_cache(axes)
        # Restart each pass from the last projected display-domain so Toyplot
        # expands from the current stable viewport instead of the raw domain.
        xaxis._display_min, xaxis._display_max = (
            previous_domain[0],
            previous_domain[1],
        )
        yaxis._display_min, yaxis._display_max = (
            previous_domain[2],
            previous_domain[3],
        )
        axes._finalized = None
        axes._finalize_once()
        current_domain = _cartesian_projected_domain_tuple(axes)
        overflow = _cartesian_max_extent_overflow_px(axes)
        previous_domain = current_domain
        if overflow <= TOYTREE_CARTESIAN_FIT_PX_TOL:
            break
        if idx < (extra_iterations - 1):
            axes._finalized = None

    # Write the settled projected domain back once more so later host
    # projections and companion syncing use the same finalized viewport.
    xaxis._display_min, xaxis._display_max = previous_domain[0], previous_domain[1]
    yaxis._display_min, yaxis._display_max = previous_domain[2], previous_domain[3]
    axes._finalized = None
    axes._finalize_once()


def finalize_cartesian_with_tip_bar_domains(axes: Cartesian) -> None:
    """Finalize host axes and extend Toyplot fitting only if needed."""
    axes._finalize()
    if _cartesian_max_extent_overflow_px(axes) > TOYTREE_CARTESIAN_FIT_PX_TOL:
        stabilize_cartesian_fit(axes)


def normalize_tip_mask(tree: ToyTree, mask: Any) -> np.ndarray:
    """Return a boolean tip mask from accepted tip-annotation mask formats.

    Accepted mask values are:
    - ``None``: show all tips.
    - ``bool``: show all tips when True, or none when False.
    - ``tuple`` of len 3: ``(show_tips, show_internal, show_root)``.
    - array-like of size ``ntips``.
    """
    if mask is None:
        return tree.get_tip_mask(show_tips=True)

    if isinstance(mask, (bool, np.bool_)):
        return tree.get_tip_mask(show_tips=bool(mask))

    if isinstance(mask, tuple):
        if len(mask) != 3:
            raise ValueError(
                "mask tuple must be length 3: " "(show_tips, show_internal, show_root)."
            )
        return tree.get_node_mask(
            show_tips=bool(mask[0]),
            show_internal=bool(mask[1]),
            show_root=bool(mask[2]),
        )[: tree.ntips]

    arr = np.asarray(mask)
    if arr.size != tree.ntips:
        raise ValueError(
            f"mask array must be size ntips ({tree.ntips}), not {arr.size}."
        )
    return arr.astype(bool)


if __name__ == "__main__":
    pass
