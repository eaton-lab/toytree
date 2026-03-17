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
)

from toytree.core import ToyTree
from toytree.drawing import Cartesian, Mark, ToyTreeMark
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
    # source tree identity. This preserves single-tree behavior.
    mark = tree_marks[-1]
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
