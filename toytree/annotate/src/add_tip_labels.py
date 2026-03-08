#!/usr/bin/env python

"""Annotation methods for adding node markers to tree drawings.

Examples
--------
...
"""

from typing import Any, Mapping, Sequence, Tuple, TypeVar, Union

import numpy as np
import toyplot.units

from toytree.annotate.src.checks import (
    assert_tree_matches_mark,
    get_last_toytree_mark,
    invalidate_cartesian_fit_cache,
    normalize_tip_mask,
)
from toytree.color import ToyColor
from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian, Mark
from toytree.drawing.src.mark_annotation import AnnotationTipLabelMark
from toytree.style.src.validate_data import (
    validate_colors,
    validate_labels,
    validate_numeric,
)
from toytree.style.src.validate_utils import substyle_dict_to_css_dict

Color = TypeVar("Color", str, tuple, np.ndarray)
__all__ = ["add_tip_labels"]


@add_subpackage_method(AnnotationAPI)
def add_tip_labels(
    tree: ToyTree,
    axes: Cartesian,
    labels: Union[str, Sequence[str]] = "name",
    color: Union[Color, Sequence[Color]] = None,
    opacity: Union[float, Sequence[float]] = 1.0,
    font_size: Union[int, None] = None,
    font_family: Union[str, None] = None,
    font_weight: Union[int, str, None] = None,
    text_anchor: Union[str, None] = None,
    angle: Union[int, Sequence[int], None] = None,
    mask: Union[np.ndarray, Tuple[int, int, int], None] = None,
    xshift: int = 0,
    yshift: int = 0,
    style: Mapping[str, Any] = None,
) -> Mark:
    """Return a Toyplot Mark of tip labels added to a tree drawing.

    This adds text labels to leaf Nodes on the selected tree (or
    last tree) drawn on the Cartesian axes.

    Style defaults are copied from the currently drawn ToyTree mark
    (`mark.tip_labels_style`) so labels inherit the same baseline
    styling as the active tree drawing.

    Priority order for style values is:
    1. explicit function args (`font_size`, `font_family`, `font_weight`,
       `text_anchor`, plus `xshift` / `yshift` adjustments)
    2. entries in `style`
    3. defaults from `mark.tip_labels_style`

    The `opacity` argument applies per-tip label opacity. A style-level
    `fill-opacity` value acts as an additional global alpha multiplier.
    Any unresolved `fill-opacity=None` is sanitized to `1.0` before
    rendering so empty opacity values are never emitted.

    Layout-specific orientation is applied per-tip to match tree
    tip-label rendering conventions.

    Parameters
    ----------
    axes: Cartesian
        A toyplot Cartesian axes object containing a tree drawing.
    labels: str or Sequence[str]
        A sequence of labels as strings in Node idx traversal order.
        The length must be equal to nnodes or nnodes - 1. Use '' to
        not add a label to some edges. You can also enter a single str
        as the name of a feature on the tree to extract data as labels,
        e.g., "idx" will show int idx labels for nodes.
    color: str, tuple, array or Sequence
        A single color or Sequence of colors for node labels.
    opacity: float or Sequence[float]
        A single opacity or Sequence of opacities for node labels.
    font_size: int or None
        Font size in px. Overrides style dict value if provided.
    font_family: str or None
        Font family. Overrides style dict value if provided.
    font_weight: int, str, or None
        Font weight. Overrides style dict value if provided.
    text_anchor: str or None
        Text anchor. Overrides style dict value if provided.
    angle: int, Sequence[int], or None
        A single angle applied to all labels, or Sequence of angles.
        If None then angles are inherited from the current tree mark
        tip angles.
    mask: bool, tuple[int, int, int], np.ndarray, or None
        Controls shown tips. Accepted values are:
        - None: show all tips
        - bool: True shows all tips, False shows none
        - tuple: (show_tips, show_internal, show_root) shortcut
        - np.ndarray: boolean array of size ntips
    xshift: int
        Shift label horizontally by px units (+=right, -=left).
    yshift: int
        Shift label vertically by px units (+=down, -=up).
    style: dict
        Optional style overrides. Keys can be CSS-style (e.g.
        ``"font-size"``, ``"text-anchor"``, ``"font-family"``) or
        pythonic style keys (e.g. ``font_size``, ``text_anchor``).
        Values in this mapping override mark defaults but are overridden
        by explicit function arguments.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, m0 = tree.draw()
    >>> m1 = tree.annotate.add_tip_labels(
    >>>     axes,
    >>>     labels="name",
    >>>     color="blue",
    >>>     font_size=15,
    >>> )
    """
    # get mark for coordinates on plotted tree.
    tmark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, tmark)

    # normalize to a tip-level mask
    mask = normalize_tip_mask(tree, mask)
    coords = tmark.ntable[: tree.ntips][mask].copy()
    if bool(getattr(tmark, "tip_labels_align", False)):
        coords = tmark.ttable[: tree.ntips][mask].copy()

    # check length and type of labels
    labels = validate_labels(
        tree, key="labels", size=tree.ntips, style={"labels": labels}
    )[mask]

    # Start from the rendered tree mark style so defaults match the
    # currently drawn tree labels, then layer user style overrides.
    base_style = dict(getattr(tmark, "tip_labels_style", {}))
    user_style = {} if style is None else substyle_dict_to_css_dict(dict(style))
    style = {**base_style, **user_style}

    # explicit kwargs override style dict keys
    if font_size is not None:
        style["font-size"] = font_size
    if font_family is not None:
        style["font-family"] = font_family
    if font_weight is not None:
        style["font-weight"] = font_weight
    if text_anchor is not None:
        style["text-anchor"] = text_anchor

    # update node colors setting; sets to None if only one color.
    node_colors, fill_color = validate_colors(
        tree, key="color", size=tree.ntips, style={"color": color}
    )

    # if fill_color then set to node_style.fill since node_colors = None
    if node_colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides node_style.fill
        else:
            pass  # node_style.fill overrides
    else:
        node_colors = node_colors[mask]
        style.pop("fill", None)

    # Toyplot expects a numeric fill-opacity whenever fill is set.
    # Style defaults can leave this unset/None, so sanitize both cases.
    if style.get("fill-opacity") is None:
        style["fill-opacity"] = 1.0

    # ...
    opacity = validate_numeric(
        tree, key="opacity", size=tree.ntips, style={"opacity": opacity}
    )[mask]
    if angle is None:
        if hasattr(tmark, "tip_labels_angles") and tmark.tip_labels_angles is not None:
            angle = np.asarray(tmark.tip_labels_angles, dtype=float)
            if angle.size != tree.ntips:
                angle = np.zeros(tree.ntips, dtype=float)
        else:
            angle = np.zeros(tree.ntips, dtype=float)
        angle = angle[mask]
    else:
        angle = validate_numeric(
            tree, key="angle", size=tree.ntips, style={"angle": angle}
        )[mask]

    # expand xshift,yshift args in pixel units
    anchor = toyplot.units.convert(
        style.get("-toyplot-anchor-shift", 0), target="px", default="px"
    )
    baseline = toyplot.units.convert(
        style.get("baseline-shift", 0), target="px", default="px"
    )
    style["-toyplot-anchor-shift"] = anchor + xshift
    style["baseline-shift"] = baseline - yshift

    # match tip label orientation behavior in render_tree.py
    offset = toyplot.units.convert(
        style.get("-toyplot-anchor-shift", 0), target="px", default="px"
    )
    layout = str(getattr(tmark, "layout", "r"))
    angles = angle.astype(float).copy()
    styles = [dict(style) for _ in range(labels.size)]

    if layout in "lu":
        for idx in range(labels.size):
            styles[idx]["-toyplot-anchor-shift"] = -offset
            styles[idx]["text-anchor"] = "end"
    elif layout not in "rd":
        flip = (angles > 90.0) & (angles < 270.0)
        for idx in np.where(flip)[0]:
            styles[idx]["text-anchor"] = "end"
            styles[idx]["-toyplot-anchor-shift"] = -offset
            angles[idx] = angles[idx] - 180.0

    amark = AnnotationTipLabelMark(
        ntable=coords,
        labels=labels,
        angles=angles,
        colors=node_colors,
        opacity=opacity.astype(float),
        styles=styles,
    )
    axes.add_mark(amark)
    invalidate_cartesian_fit_cache(axes)
    return amark


if __name__ == "__main__":
    pass
