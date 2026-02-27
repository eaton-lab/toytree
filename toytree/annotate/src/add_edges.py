#!/usr/bin/env python

"""Add edge overlay lines to an existing tree drawing."""

from __future__ import annotations

from typing import Any, Mapping, Sequence, Tuple, TypeVar, Union

import numpy as np

from toytree.annotate.src.checks import assert_tree_matches_mark, get_last_toytree_mark
from toytree.color import ToyColor
from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian, Mark
from toytree.drawing.src.mark_annotation import AnnotationGradientLine, AnnotationLine
from toytree.drawing.src.path_edges import get_tree_edge_polylines
from toytree.style.src.validate_data import (
    validate_colors,
    validate_mask,
    validate_numeric,
)

Color = TypeVar("Color", str, tuple, np.ndarray)
ALLOWED_STROKE_LINEJOIN = {"miter", "round", "bevel", "arcs", "miter-clip"}

__all__ = ["add_edges"]


@add_subpackage_method(AnnotationAPI)
def add_edges(
    tree: ToyTree,
    axes: Cartesian,
    color: Union[Color, Sequence[Color], None] = None,
    width: Union[float, Sequence[float]] = 2.0,
    opacity: Union[float, Sequence[float]] = 1.0,
    mask: Union[np.ndarray, Tuple[int, int, int], None] = False,
    xshift: float = 0.0,
    yshift: float = 0.0,
    use_color_gradient: bool = False,
    style: Mapping[str, Any] | None = None,
) -> Mark:
    """Add line overlays on top of currently drawn tree edges.

    This method draws a second set of edges over an existing tree mark on
    ``axes``. It is useful for highlighting subsets of edges (e.g., by feature
    value, support class, or inferred state) while preserving the original
    drawing beneath.

    The overlay uses the same edge geometry as the tree mark (including
    circular phylogram arcs), and supports scalar or per-edge arrays for color,
    width, and opacity.

    Parameters
    ----------
    tree: ToyTree
        Tree associated with the existing drawing on ``axes``.
    axes: Cartesian
        Toyplot Cartesian axes containing a previously drawn tree mark.
    color: str, tuple, np.ndarray, Sequence, or None
        Edge color specification. Can be a single color, a feature mapping
        tuple (e.g., ``("X", "Dark2")``), or a per-node/edge sequence.
        If None, a default dark stroke is used.
    width: float or Sequence[float]
        Line width in px, as a scalar or per-edge sequence.
    opacity: float or Sequence[float]
        Line opacity as a scalar or per-edge sequence. Opacity is applied to
        individual edge paths.
    mask: np.ndarray, tuple[int, int, int], or None
        Boolean show-mask for nodes / edges. A 3-item tuple is interpreted as
        ``(show_tips, show_internal, show_root)``. True values are shown.
    xshift: float
        Horizontal offset applied in data units.
    yshift: float
        Vertical offset applied in data units.
    use_color_gradient: bool
        If True, and if ``color`` resolves to per-node colors, each edge is
        stroked with a linear gradient from parent-node color (rootward end)
        to child-node color (tipward end). If ``color`` is None (or resolves to
        a single shared color), the function falls back to solid strokes.
    style: Mapping[str, Any] or None
        Shared SVG/CSS line style keys (e.g., ``stroke-linecap``,
        ``stroke-linejoin``, ``stroke-dasharray``). If
        ``stroke-linejoin`` is provided it must be one of:
        ``miter``, ``round``, ``bevel``, ``arcs``, or ``miter-clip``.

    Returns
    -------
    Mark
        The added annotation line mark.

    Raises
    ------
    ValueError
        If ``style["stroke-linejoin"]`` is provided but not a supported value.

    Examples
    --------
    >>> tree = toytree.rtree.bdtree(20, seed=123)
    >>> tree.pcm.simulate_discrete_trait(3, trait_name="X", state_names="ABC", inplace=True)
    >>> c, a, m = tree.draw(layout="c", edge_type="p")
    >>> tree.annotate.add_edges(
    ...     a,
    ...     mask=(1, 1, 1),
    ...     color=("X", "Dark2"),
    ...     width=6,
    ...     opacity=0.35,
    ...     use_color_gradient=True,
    ...     style={"stroke-linejoin": "miter", "stroke-linecap": "butt"},
    ... )
    """
    # Validate that the tree and target axes correspond to the same drawn mark.
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)

    # Number of drawable edges represented in mark.etable excludes only the
    # pseudo-root self-edge; rooted trees still draw both root-adjacent edges.
    nedges = tree.nnodes - 1
    etable = mark.etable[:nedges]
    # Resolve edge visibility from show-mask (True=show, False=hide)
    show = validate_mask(tree, style={"node_mask": mask})[:nedges]

    # Resolve color channels (scalar vs per-edge sequence) via style validators.
    colors, single_color = validate_colors(
        tree,
        key="color",
        size=tree.nnodes,
        style={"color": color},
    )
    node_colors = colors
    if colors is not None:
        stroke = colors[:nedges][show]
        per_edge_color = True
    else:
        stroke = (
            ToyColor(single_color) if single_color is not None else ToyColor("#262626")
        )
        per_edge_color = False

    # Resolve width and opacity as per-edge arrays and trim to shown edges.
    widths = validate_numeric(
        tree, key="size", size=tree.nnodes, style={"size": width}
    )[:nedges][show]
    opacs = validate_numeric(
        tree, key="opacity", size=tree.nnodes, style={"opacity": opacity}
    )[:nedges][show]

    # Build data-space edge polylines from the shared drawing utility.
    xpaths, ypaths, _ = get_tree_edge_polylines(axes, mark, space="data")

    # Set default stroke style for nicer overlays, then apply user updates.
    line_style = {
        "stroke-linecap": "round",
    }
    if style is not None:
        line_style.update(style)
    _validate_linejoin(line_style)

    # Build a line annotation mark and add to axes using the custom renderer,
    # which supports SVG line styles (including stroke-linejoin).
    show_idxs = np.where(show)[0]
    if show_idxs.size == 0:
        return None
    xshow = [xpaths[idx] + float(xshift) for idx in show_idxs]
    yshow = [ypaths[idx] + float(yshift) for idx in show_idxs]

    # create lineargradient defs referenced by stop-color:$url(...) on edges
    if use_color_gradient and (node_colors is not None):
        shown_edges = etable[show_idxs]
        # Ensure each path is oriented rootward -> tipward so gradient
        # direction is consistent across layouts / edge types.
        gxshow = []
        gyshow = []
        start_colors = np.zeros(shown_edges.shape[0], dtype=node_colors.dtype)
        end_colors = np.zeros(shown_edges.shape[0], dtype=node_colors.dtype)
        for idx, (cidx, pidx) in enumerate(shown_edges):
            xdat = xshow[idx]
            ydat = yshow[idx]
            cx, cy = mark.ntable[cidx]
            px, py = mark.ntable[pidx]
            dstart_parent = (xdat[0] - px) ** 2 + (ydat[0] - py) ** 2
            dstart_child = (xdat[0] - cx) ** 2 + (ydat[0] - cy) ** 2
            if dstart_parent > dstart_child:
                xdat = xdat[::-1]
                ydat = ydat[::-1]
            gxshow.append(xdat)
            gyshow.append(ydat)
            start_colors[idx] = node_colors[pidx]
            end_colors[idx] = node_colors[cidx]
        grad_style = dict(line_style)

        # group-level opacity mode. Keep scalar opacity on
        # individual edges to preserve per-edge blending behavior.
        use_group_opacity = False
        group_opacity = None
        if isinstance(opacity, (int, float, np.integer, np.floating)):
            use_group_opacity = True
            grad_style.pop("opacity", None)
            grad_style.pop("stroke-opacity", None)
            grad_style["opacity"] = float(opacity)
        else:
            grad_style["opacity"] = None

        outmark = AnnotationGradientLine(
            xpaths=gxshow,
            ypaths=gyshow,
            start_colors=start_colors,
            end_colors=end_colors,
            widths=widths.astype(float),
            opacity=opacs.astype(float),
            use_group_opacity=use_group_opacity,
            group_opacity=group_opacity,
            style=grad_style,
        )

    # apply one solid color to each edge
    else:
        solid_style = dict(line_style)

        # group-level opacity mode. Keep scalar opacity on
        # individual edges to preserve per-edge blending behavior.
        use_group_opacity = False
        group_opacity = None
        if isinstance(opacity, (int, float, np.integer, np.floating)):
            use_group_opacity = True
            solid_style.pop("opacity", None)
            solid_style.pop("stroke-opacity", None)
            solid_style["opacity"] = float(opacity)
        else:
            solid_style["opacity"] = None

        # set colors
        ecolors = stroke if per_edge_color else None
        if not per_edge_color:
            solid_style["stroke"] = stroke

        # create Mark for custom rendering
        outmark = AnnotationLine(
            xpaths=xshow,
            ypaths=yshow,
            colors=ecolors,
            widths=widths.astype(float),
            opacity=opacs.astype(float),
            use_group_opacity=use_group_opacity,
            group_opacity=group_opacity,
            style=solid_style,
        )
    axes.add_mark(outmark)
    return outmark


def _validate_linejoin(style: Mapping[str, Any]) -> None:
    """Validate stroke-linejoin if provided."""
    linejoin = style.get("stroke-linejoin")
    if linejoin is None:
        return
    if linejoin not in ALLOWED_STROKE_LINEJOIN:
        allowed = ", ".join(sorted(ALLOWED_STROKE_LINEJOIN))
        raise ValueError(
            f"Invalid 'stroke-linejoin' value '{linejoin}'. "
            f"Expected one of: {allowed}"
        )
