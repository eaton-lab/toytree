#!/usr/bin/env python

"""Annotation methods for adding node markers to tree drawings.

Examples
--------
...
"""

from typing import Tuple, Sequence, Mapping, Any, Union, TypeVar
import numpy as np

from toytree.core import ToyTree, Cartesian, Mark
from toytree.color import ToyColor
from toytree.core.apis import add_subpackage_method, AnnotationAPI
from toytree.style.src.validate_utils import substyle_dict_to_css_dict
from toytree.annotate.src.checks import get_last_toytree_mark, assert_tree_matches_mark
from toytree.style.src.validate_data import (
    validate_colors,
    validate_numeric,
    validate_mask,
    validate_labels,
)
from toytree.style.src.validate_node_labels import validate_node_labels_style

Color = TypeVar("Color", str, tuple, np.ndarray)
__all__ = ["add_tip_labels"]

@add_subpackage_method(AnnotationAPI)
def add_tip_labels(
    tree: ToyTree,
    axes: Cartesian,
    labels: Union[str, Sequence[str]] = "name",
    color: Union[Color, Sequence[Color]] = None,
    opacity: Union[float, Sequence[float]] = 1.0,
    font_size: Union[int, None] = 12,
    angle: Union[int, Sequence[int]] = 0,
    mask: Union[np.ndarray, Tuple[int, int, int], None] = None,
    xshift: int = 0,
    yshift: int = 0,
    style: Mapping[str, Any] = None,
) -> Mark:
    """Return a toyplot Mark of tip labels added to a tree drawing.

    This adds text labels to leaf Nodes on the selected tree (or 
    last tree) drawn on the Cartesian axes.

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
    font_size: float
        Font size in px. Overrides 'font-size' setting in style dict.
    angle: int or Sequence[int]
        A single angle applied to all labels, or Sequence of angles.
    mask: np.array or None
        A boolean array of len nnodes or nnodes - 1 where True masks
        an node from being shown and False shows the node. None or False
        shows all nodes. A tuple of 3 booleans can be entered as a
        shortcut to (show_tips, show_internal, show_root).
    xshift: int
        Shift label horizontally by px units (+=right, -=left).
    yshift: int
        Shift label vertically by px units (+=down, -=up).
    style: dict
        Style dict. See `tree.style.node_labels_style` for options.

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
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)

    # mask some edges
    if mask is None:
        mask = tree.get_node_mask(show_tips=True)[:tree.ntips]
    else:
        if mask.size == tree.ntips:
            # add False for all internal nodes to make the mask = nnodes
            mask = np.concatenate(mask, np.full(tree.nnodes - tree.ntips), False)
        if mask.size == tree.nnodes:
            mask = validate_mask(tree, style={"node_mask": mask})[:tree.ntips]
        else:
            raise ValueError("mask should be a boolean array of size ntips or nnodes")
    coords = mark.ntable[:tree.ntips][mask]

    # check length and type of labels
    labels = validate_labels(
        tree, key="labels", size=tree.ntips, style={"labels": labels})[mask]

    # set styles on top of defaults
    style = {} if style is None else style
    style["text-anchor"] = style.get("text-anchor", "start")
    style = validate_node_labels_style(tree, style=style, **style)
    style = substyle_dict_to_css_dict(style.__dict__)

    # override font size
    if font_size:
        style["font-size"] = font_size

    # update node colors setting; sets to None if only one color.
    node_colors, fill_color = validate_colors(
        tree, key="color", size=tree.ntips, style={"color": color})

    # if fill_color then set to node_style.fill since node_colors = None
    if node_colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides node_style.fill
        else:
            pass  # node_style.fill overrides
    else:
        node_colors = node_colors[mask]
        style.pop("fill")

    # ...
    opacity = validate_numeric(
        tree, key="opacity", size=tree.ntips, style={"opacity": opacity})[mask]
    angle = validate_numeric(
        tree, key="angle", size=tree.ntips, style={"angle": angle})[mask]

    # expand xshift,yshift args in pixel units
    style['-toyplot-anchor-shift'] += xshift
    style['baseline-shift'] -= yshift

    # add text at Node positions + half length of dists.
    mark = axes.text(
        coords[:, 0],
        coords[:, 1],
        labels,
        color=node_colors,
        opacity=opacity,
        angle=angle,
        style=style,
        annotation=True,
    )
    return mark


if __name__ == "__main__":
    pass
