#!/usr/bin/env python

"""Draw cloud-tree overlays by stacking many ``ToyTreeMark`` objects."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, TypeVar

# from toytree import MultiTree
from toytree.drawing import ToyTreeMark
from toytree.drawing.src.draw_toytree import (
    get_layout,
    get_tree_style_updated_by_draw_args,
)
from toytree.drawing.src.fixed_order import resolve_fixed_order

# from toytree.core import Canvas, Cartesian
from toytree.drawing.src.validate_utils import tree_style_to_css_dict
from toytree.utils import ToytreeError

# from toytree.drawing.src.mark_cloudtree import CloudTreeMark

Mark = TypeVar("Mark")
MultiTree = TypeVar("MultiTree")

PER_TREE_FORBIDDEN_KEYS = frozenset(
    {
        "axes",
        "fixed_order",
        "fixed_position",
        "height",
        "idxs",
        "interior_algorithm",
        "jitter",
        "layout",
        "per_tree",
        "scale_bar",
        "tree_style",
        "ts",
        "width",
    }
)


def _normalize_per_tree_kwargs(
    per_tree: Sequence[Mapping[str, Any] | None] | None,
    ntrees: int,
) -> list[dict[str, Any]]:
    """Return validated per-tree draw-override mappings."""
    if per_tree is None:
        return [{} for _ in range(ntrees)]

    if isinstance(per_tree, (str, bytes, bytearray)) or isinstance(per_tree, Mapping):
        raise ToytreeError("per_tree must be a sequence of mappings or None values.")

    try:
        entries = list(per_tree)
    except TypeError as exc:
        raise ToytreeError(
            "per_tree must be a sequence of mappings or None values."
        ) from exc

    if len(entries) != ntrees:
        raise ToytreeError("per_tree length must match the number of rendered trees.")

    normalized: list[dict[str, Any]] = []
    for idx, entry in enumerate(entries):
        if entry is None:
            normalized.append({})
            continue
        if not isinstance(entry, Mapping):
            raise ToytreeError(
                f"per_tree[{idx}] must be a mapping of draw kwargs or None."
            )

        forbidden = sorted(PER_TREE_FORBIDDEN_KEYS.intersection(entry))
        if forbidden:
            raise ToytreeError(
                "per_tree entries cannot override cloud-level args: "
                f"{', '.join(forbidden)}."
            )
        normalized.append(dict(entry))
    return normalized


def draw_cloudtree(mtree: MultiTree, **kwargs) -> Sequence[Mark]:
    """Parse arguments to draw_cloudtree and return drawing objects.

    CloudTree is a Mark similar to a ToyTree but with many overlapping
    sets of edges, where each set can be individually styled. Only one
    set of tip labels is plotted.
    """
    shared_kwargs = dict(kwargs)
    shared_kwargs.pop("jitter", None)
    per_tree = _normalize_per_tree_kwargs(
        shared_kwargs.pop("per_tree", None),
        len(mtree),
    )
    fixed_order = resolve_fixed_order(
        mtree,
        mtree.treelist,
        shared_kwargs.get("fixed_order"),
        infer_when_missing=True,
    )
    fixed_position = shared_kwargs.get("fixed_position", None)
    interior_algorithm = shared_kwargs.get("interior_algorithm", 1)

    # Iterate over trees and resolve each draw from the explicit kwargs
    # plus a fresh default TreeStyle.
    marks = []
    for tidx, tree in enumerate(mtree):
        draw_kwargs = dict(shared_kwargs)
        draw_kwargs.update(per_tree[tidx])

        # only show tips for the first tree
        if tidx:
            draw_kwargs["tip_labels"] = False

        # hard-coded to disallow some styles
        draw_kwargs["scale_bar"] = False

        # get the tree's style
        style = get_tree_style_updated_by_draw_args(tree, **draw_kwargs)

        # override styles not set by user
        if draw_kwargs.get("edge_type") is None:
            style.edge_type = "c"
        if style.edge_style.stroke_opacity is None:
            style.edge_style.stroke_opacity = 1 / len(mtree) * 3

        # get coordinate layout of this tree
        layout = get_layout(
            tree=tree,
            style=style,
            fixed_order=fixed_order,
            fixed_position=fixed_position,
            interior_algorithm=interior_algorithm,
        )

        if style.tip_labels_angles is None:
            style.tip_labels_angles = layout.angles

        mark = ToyTreeMark(
            ntable=layout.coords,
            ttable=layout.tcoords,
            etable=tree.get_edges("idx"),
            _toytree_source_tree=tree,
            **tree_style_to_css_dict(style),
        )
        marks.append(mark)

    # get a Layout with coordinates projected based on the first tree
    return marks


if __name__ == "__main__":
    import toytree

    trees = [toytree.rtree.coaltree(k=6, seed=i) for i in range(100)]
    mtree = toytree.mtree(trees)
    c, a, m = mtree.draw_cloud_tree()
    toytree.utils.show([c], tmpdir="~")
    # canvas = toyplot.Canvas()
    # axes = canvas.cartesian()
    # kwargs = dict(
    #     tree_style=None, axes=axes, kwargs={}, edge_widths=3,
    #     fixed_position=None,
    #     # fixed_order=["r1", "r0", "r3", "r4", "r5", "r2"],
    # )

    # mtree[10].style.edge_style.stroke = "red"
    # mtree[10].style.edge_style.stroke_opacity = 1
    # marks = draw_cloudtree(mtree, **kwargs)
    # if marks:
    #     toytree.utils.show([canvas], tmpdir="~")
