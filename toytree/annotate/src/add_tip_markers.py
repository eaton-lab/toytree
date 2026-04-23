#!/usr/bin/env python

"""Annotation methods for adding tip markers to tree drawings.

Examples
--------
...
"""

from typing import Any, Mapping, Sequence, Tuple, TypeVar, Union

import numpy as np
from toyplot.mark import Mark

from toytree.annotate.src.checks import (
    assert_tree_matches_mark,
    get_last_toytree_mark_for_tree,
)
from toytree.color import ToyColor
from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian

# WORK IN PROGRESS...
from toytree.drawing.src.mark_annotation import AnnotationMarker
from toytree.drawing.src.validate_data import (
    validate_colors,
    validate_markers,
    validate_numeric,
)
from toytree.drawing.src.validate_nodes import (
    validate_node_style,
)
from toytree.drawing.src.validate_utils import substyle_dict_to_css_dict

Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    "add_tip_markers",
    # "add_node_bars",
    # "add_node_histograms",
    # "add_node_densigrams",
]


@add_subpackage_method(AnnotationAPI)
def add_tip_markers(
    tree: ToyTree,
    axes: Cartesian,
    align: bool = None,  # default=None and use T/F to override ts?
    marker: Union[str, Sequence[str]] = "o",
    size: Union[int, Sequence[int]] = 8,
    color: Union[Color, Sequence[Color]] = None,
    opacity: Union[float, Sequence[float]] = 1.0,
    mask: Union[np.ndarray, Tuple[int, int, int], bool, None] = None,
    style: Mapping[str, Any] = None,
    xshift: int = 0,
    yshift: int = 0,
    # label: Optional[str] = None,
    # label_angle: int = 45,
) -> Mark:
    """Return toyplot Mark of markers aligned with tips of tree plot.

    This adds node markers to the rendered tree associated with ``tree``
    on the Cartesian axes using the coordinates of plotted Nodes. The
    shape, size, color, and style of markers can be modified.

    Parameters
    ----------
    axes: Cartesian
        A toyplot Cartesian axes object containing a tree drawing.
    align: bool
        If True markers align at the farthest tip position; if False
        markers align at each tip's position; if None markers align
        according to the tip_labels_align arg used during tree drawing.
    marker: str or toyplot.marker.Marker or Sequence
        Marker shape, e.g., "o", "s", "^", "r2x1". See toyplot Markers.
    size: int or Sequence[int]
        Size of markers as single int or Sequence of ints, in px units.
    color: str, tuple, or array, or Sequence
        Color of markers as single color or Sequence of colors.
    opacity: float or Sequence[float]
        Opacity of markers (fill & stroke) as a float or Sequence
        of floats. Note: fill and stroke opacities can be set
        separately using the style dict, but only as single values.
    mask: bool, tuple[int, int, int], np.ndarray, or None
        Controls shown tips. Accepted values are:
        - None: show all tips
        - bool: True shows all tips, False shows none
        - tuple: (show_tips, show_internal, show_root) shortcut
        - np.ndarray: boolean array of size ntips
    style: dict
        Marker style dict. See `toytree.core.NodeStyle` for options.
    xshift: int
        Marker shift in px. On linear layouts this shifts along canvas x.
        On circular layouts this shifts along arc span (tangential direction).
    yshift: int
        Marker shift in px. On linear layouts this shifts along canvas y.
        On circular layouts this shifts along arc depth (radial direction).

    Example
    -------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, m0 = tree.draw()
    >>> # add markers to all Nodes
    >>> m1 = tree.annotate.add_tip_markers(
    >>>     axes,
    >>>     marker='s',
    >>>     size=9,
    >>>     color='red',
    >>>     style={'stroke': 'white', 'stroke-width': 2.5}
    >>> )
    >>>
    >>> # add markers to only a few Nodes
    >>> m2 = tree.annotate.add_tip_markers(
    >>>     axes, marker=">", size=20, mask=tree.get_node_mask(9)
    >>> )
    """
    # get mark for coordinates on plotted tree.
    mark = get_last_toytree_mark_for_tree(axes, tree)
    assert_tree_matches_mark(tree, mark)

    # get coordinates of the tip Nodes
    coords = mark.ttable.copy()
    layout = str(mark.layout)

    # align tips: if mark.tip_labels_align == True this is already done
    align = align if align is not None else mark.tip_labels_align
    if align:
        if layout == "r":
            coords[:, 0] = coords[:, 0].max()
        elif layout == "l":
            coords[:, 0] = coords[:, 0].min()
        elif layout == "u":
            coords[:, 1] = coords[:, 1].max()
        elif layout == "d":
            coords[:, 1] = coords[:, 1].min()
        elif layout.startswith("c"):
            # In circular layouts, align means equalize radial distance from
            # the root so markers form a constant-radius ring.
            root_xy = np.asarray(mark.ntable[tree.treenode.idx], dtype=float)
            dxy = coords - root_xy
            radii = np.sqrt(np.sum(dxy * dxy, axis=1))
            max_radius = float(np.max(radii))
            unit = np.divide(
                dxy,
                radii[:, None],
                out=np.zeros_like(dxy),
                where=radii[:, None] > 0,
            )
            coords = root_xy + unit * max_radius
        else:
            raise NotImplementedError(f"Unsupported layout for tip markers: {layout}")

    # Normalize mask to a tip-level boolean array.
    if mask is None:
        mask_arr = tree.get_tip_mask(show_tips=True)
    elif isinstance(mask, (bool, np.bool_)):
        mask_arr = tree.get_tip_mask(show_tips=bool(mask))
    elif isinstance(mask, tuple):
        if len(mask) != 3:
            raise ValueError(
                "mask tuple must be length 3: " "(show_tips, show_internal, show_root)."
            )
        mask_arr = tree.get_node_mask(
            show_tips=bool(mask[0]),
            show_internal=bool(mask[1]),
            show_root=bool(mask[2]),
        )[: tree.ntips]
    else:
        arr = np.asarray(mask)
        if arr.size != tree.ntips:
            raise ValueError(
                "mask array must be size ntips " f"({tree.ntips}), not {arr.size}."
            )
        mask_arr = arr.astype(bool)

    # update node_style setting
    style = {} if style is None else style
    style = validate_node_style(tree, style=None, **style)
    style = substyle_dict_to_css_dict(style.__dict__)

    # update node colors setting; sets to None if only one color.
    colors, fill_color = validate_colors(
        tree,
        key="colors",
        size=tree.ntips,
        style={"colors": color},
    )

    # if fill_color then set to node_style.fill since node_colors = None
    if colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides node_style.fill
        else:
            pass  # node_style.fill overrides
    else:
        colors = colors[mask_arr]
        style.pop("fill")

    # validate others and trim to mask
    markers = validate_markers(
        tree,
        key="node_markers",
        size=tree.ntips,
        style={"node_markers": marker},
    )[mask_arr]
    sizes = validate_numeric(tree, key="size", size=tree.ntips, style={"size": size})[
        mask_arr
    ]
    opacity = validate_numeric(
        tree, key="opacity", size=tree.ntips, style={"opacity": opacity}
    )[mask_arr]

    # On circular layouts, interpret xshift/yshift in local arc axes:
    # xshift follows tangential span and yshift follows radial depth.
    if layout.startswith("c"):
        xshift_mark = 0.0
        yshift_mark = 0.0
        local_span = np.repeat(float(xshift), mask_arr.sum())
        local_depth = np.repeat(float(yshift), mask_arr.sum())
        root_xy = np.asarray(mark.ntable[tree.treenode.idx], dtype=float)
    else:
        xshift_mark = float(xshift)
        yshift_mark = float(yshift)
        local_span = None
        local_depth = None
        root_xy = None

    # create custom Mark that allows for [xy]shift
    mark = AnnotationMarker(
        ntable=coords[mask_arr],
        xshift=xshift_mark,
        yshift=yshift_mark,
        local_span=local_span,
        local_depth=local_depth,
        root_xy=root_xy,
        sizes=sizes,
        colors=colors,
        opacity=opacity,
        shapes=markers,
        style=style,
    )
    axes.add_mark(mark)
    return mark

    # add label for the data column
    # if label:
    #     label = axes.text(
    #         coords[0, 0] + xoffset,
    #         tree.ntips,
    #         label,
    #         angle=label_angle,
    #         style={'text-anchor': 'start', 'fill': "#252525"},
    #     )



if __name__ == "__main__":
    import toytree

    # base tree drawing
    tree = toytree.rtree.unittree(6)
    c, a, m = tree.draw(layout="d")

    # annotate with edge labels
    # add_edge_labels(tree, axes=a, labels=tree.get_node_data("idx"))
    # add_node_markers(
    #     tree, axes=a, size=10, marker='s', color=("idx", "BlueRed"))
    # add_node_labels(tree, axes=a, labels='idx')
    data = np.array([[0.5, 0.3, 0.2]] * tree.nnodes)
    m = tree.annotate.add_tip_markers(
        a,
        mask=tree.get_node_mask(1, 2, 3),
        color=("name", "Spectral"),
        opacity=1.0,
        size=10,
        # xshift=0, yshift=10,
    )
    # print(m.extents(['x', 'y']))
    toytree.utils.show(c, tmpdir="~")
