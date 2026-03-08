#!/usr/bin/env python

"""Utility functions for annotations."""

from __future__ import annotations

from typing import Any

# from toyplot.canvas import Canvas
import numpy as np

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


def get_last_toytree_mark(axes: Cartesian) -> ToyTreeMark:
    """Return the last ToyTreeMark rendered on the Cartesian axes."""
    if not isinstance(axes, Cartesian):
        raise TypeError(CARTESIAN_TYPE_ERROR)
    targets = axes._scenegraph.targets(axes, "render")
    tree_marks = [i for i in targets if isinstance(i, ToyTreeMark)]
    if not tree_marks:
        raise ToytreeError(
            "No tree drawings (ToyTreeMark) have been rendered on the "
            "Cartesian axes. First draw a ToyTree."
        )
    return tree_marks[-1]


def assert_tree_matches_mark(tree: ToyTree, mark: Mark) -> None:
    """Raise exception if mark does not match up with tree data."""
    nnodes_in_mark = mark.ntable.shape[0]
    assert tree.nnodes == nnodes_in_mark, (
        f"Cannot annotate a tree drawing containing {tree.nnodes} nodes "
        f"with a different tree that has {nnodes_in_mark} nodes."
    )


def get_toytree_scale_cartesian(
    axes: Cartesian, create: bool = False
) -> Cartesian | None:  # noqa: E501
    """Return the hidden companion Cartesian used for tree scale bars."""
    return _get_scale_axes(axes, create=create)


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

    # If this axes has a hidden companion scale-axes, invalidate it too
    # so projections stay synchronized after host extents change.
    scale_axes = get_toytree_scale_cartesian(axes, create=False)
    if scale_axes is not None:
        scale_axes._finalized = None
        scale_axes._expand_domain_range_x = None
        scale_axes._expand_domain_range_y = None
        scale_axes._expand_domain_range_left = None
        scale_axes._expand_domain_range_right = None
        scale_axes._expand_domain_range_top = None
        scale_axes._expand_domain_range_bottom = None


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
