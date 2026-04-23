#!/usr/bin/env python

"""Add stochastic-map edge segment overlays to an existing tree drawing."""

from __future__ import annotations

from typing import Literal, Sequence, Tuple, TypeVar, Union

import numpy as np
import pandas as pd
import toyplot

from toytree.annotate.src.checks import (
    assert_tree_matches_mark,
    get_last_toytree_mark_for_tree,
)
from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.data import get_color_mapped_values
from toytree.drawing import Cartesian, Mark
from toytree.drawing.src.mark_annotation import AnnotationStochasticMapLine
from toytree.drawing.src.validate_data import validate_mask, validate_numeric
from toytree.utils import ToytreeError

Color = TypeVar("Color", str, tuple, np.ndarray)
_REQUIRED_COLUMNS = {"map_id", "edge_id", "t_start", "t_end"}
ALLOWED_STROKE_LINECAP = {"round", "butt", "square"}
ALLOWED_STROKE_LINEJOIN = {"miter", "round", "bevel"}

__all__ = ["add_edge_stochastic_map"]


def _validate_data_frame(data: pd.DataFrame) -> None:
    """Validate stochastic-map data frame columns and value constraints."""
    if not isinstance(data, pd.DataFrame):
        raise ToytreeError("data must be a pandas.DataFrame")

    missing = _REQUIRED_COLUMNS - set(data.columns)
    if missing:
        names = ", ".join(sorted(missing))
        raise ToytreeError(f"data is missing required columns: {names}")

    if ("state" not in data.columns) and ("state_idx" not in data.columns):
        raise ToytreeError("data must include a 'state' or 'state_idx' column")


def _coerce_stochastic_map_data(data) -> pd.DataFrame:
    """Return a stochastic-map segment table from result object or DataFrame."""
    if isinstance(data, pd.DataFrame):
        return data
    if hasattr(data, "segments"):
        return data.segments
    raise ToytreeError("data must be a pandas.DataFrame or PCMStochasticMapResult")


def _get_branch_axis_endpoint(
    mark,
    child: int,
    parent: int,
) -> tuple[float, float]:
    """Return branch-length-axis endpoint for one edge in data coordinates."""
    cx, cy = mark.ntable[child]
    px, py = mark.ntable[parent]

    if mark.edge_type == "c":
        return float(px), float(py)

    if mark.edge_type != "p":
        raise ToytreeError(
            "add_edge_stochastic_map supports edge_type 'c' and 'p' only. "
            "Redraw with edge_type='c' or edge_type='p'."
        )

    layout = mark.layout
    if layout in ("u", "d"):
        return float(cx), float(py)
    if layout in ("l", "r"):
        return float(px), float(cy)
    if str(layout).startswith("c"):
        rootx, rooty = mark.ntable[-1]
        dx = float(cx - rootx)
        dy = float(cy - rooty)
        norm = np.hypot(dx, dy)
        if norm <= 0.0:
            return float(cx), float(cy)
        ux, uy = dx / norm, dy / norm
        rp = np.hypot(float(px - rootx), float(py - rooty))
        return float(rootx + (rp * ux)), float(rooty + (rp * uy))

    # Unrooted/default fallback to rectangular left-right interpretation.
    return float(px), float(cy)


def _select_state_column(data: pd.DataFrame) -> str:
    """Return preferred state column for color mapping."""
    if "state" in data.columns:
        return "state"
    return "state_idx"


@add_subpackage_method(AnnotationAPI)
def add_edge_stochastic_map(
    tree: ToyTree,
    axes: Cartesian,
    data: pd.DataFrame,
    map_id: int = 0,
    color: None | str | toyplot.color.Map | Sequence[Color] = None,
    width: float = 2.0,
    opacity: Union[float, Sequence[float]] = 1.0,
    mask: Union[np.ndarray, Tuple[int, int, int], None] = False,
    xshift: float = 0.0,
    yshift: float = 0.0,
    stroke_linecap: Literal["round", "butt", "square"] = "butt",
    stroke_linejoin: Literal["miter", "round", "bevel"] | None = None,
    stroke_dasharray: str | tuple[int, int] | None = None,
) -> Mark:
    """Add stochastic-map state segments on drawn tree edges.

    This overlays a single stochastic map replicate on top of a tree already
    drawn on ``axes``. Segment colors are mapped from state labels (``state``),
    or from ``state_idx`` when ``state`` is unavailable.

    Parameters
    ----------
    tree : ToyTree
        Tree associated with the existing drawing on ``axes``.
    axes : Cartesian
        Toyplot Cartesian axes containing a previously drawn tree mark.
    data : pandas.DataFrame or PCMStochasticMapResult
        Stochastic-map result object or segment table. Segment tables must
        include columns ``map_id``, ``edge_id``, ``t_start``, and ``t_end`` and
        either ``state`` or ``state_idx``.
    map_id : int, default=0
        Replicate identifier selected from ``data['map_id']``.
    color : None, str, toyplot.color.Map, or Sequence[Color], default=None
        Colormap specification used to map discrete states to colors.
        If None, uses ``"Set2"``.
    width : float, default=2.0
        Segment line width in px.
    opacity : float or Sequence[float], default=1.0
        Segment line opacity as a scalar or per-edge sequence.
    mask : np.ndarray, tuple[int, int, int], or None, default=False
        Boolean show-mask for edges. A 3-item tuple is interpreted as
        ``(show_tips, show_internal, show_root)``. True values are shown.
    xshift : float, default=0.0
        Horizontal offset applied in data units.
    yshift : float, default=0.0
        Vertical offset applied in data units.
    stroke_linecap : {"round", "butt", "square"}, default="butt"
        SVG line-cap style applied to rendered stochastic-map paths.
    stroke_linejoin : {"miter", "round", "bevel"} or None, default=None
        SVG line-join style applied to rendered stochastic-map paths.
    stroke_dasharray : str or tuple[int, int] or None, default=None
        SVG dash pattern applied to rendered stochastic-map paths.

    Returns
    -------
    Mark
        The added annotation mark.

    Raises
    ------
    ToytreeError
        Raised if inputs are invalid, requested ``map_id`` is unavailable,
        edge indices are invalid, selected edge geometry is unsupported, or
        segment times are inconsistent with branch lengths.
    ValueError
        If stroke style arguments are invalid.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(20, seed=123)
    >>> tree.pcm.simulate_discrete_trait(
    ...     nstates=3,
    ...     name="X",
    ...     tips_only=True,
    ...     inplace=True,
    ...     seed=1,
    ... )
    >>> fit = tree.pcm.fit_discrete_ctmc("X", nstates=3, model="ER")
    >>> maps = tree.pcm.simulate_stochastic_map("X", model_fit=fit, nreplicates=2)
    >>> c, a, m = tree.draw(edge_type="p")
    >>> tree.annotate.add_edge_stochastic_map(a, maps, map_id=1, color="Dark2", width=4)
    """
    data = _coerce_stochastic_map_data(data)
    _validate_data_frame(data)
    map_id = int(map_id)
    width = float(width)
    if not np.isfinite(width) or width <= 0.0:
        raise ToytreeError("width must be a finite value > 0")

    # Validate that the tree and target axes correspond to the same drawn mark.
    mark = get_last_toytree_mark_for_tree(axes, tree)
    assert_tree_matches_mark(tree, mark)

    # Stochastic segments are defined for straight/step edge drawings only.
    if mark.edge_type == "b":
        raise ToytreeError(
            "add_edge_stochastic_map does not support edge_type='b'. "
            "Redraw with edge_type='c' or edge_type='p'."
        )

    subset = data[data["map_id"] == map_id].copy()
    if subset.empty:
        max_map_id = int(np.nanmax(data["map_id"].to_numpy(dtype=float)))
        raise ToytreeError(
            f"map_id={map_id} not found in data. Valid range is 0..{max_map_id}."
        )

    line_style = _make_line_style(
        stroke_linecap=stroke_linecap,
        stroke_linejoin=stroke_linejoin,
        stroke_dasharray=stroke_dasharray,
    )
    state_col = _select_state_column(subset)
    etable = tree.get_edges("idx")
    nedge = int(etable.shape[0])
    dists = tree.get_node_data("dist").to_numpy(dtype=float)
    show = validate_mask(tree, style={"node_mask": mask})[:nedge]
    edge_opacity = validate_numeric(
        tree, key="opacity", size=tree.nnodes, style={"opacity": opacity}
    )[:nedge]

    if not np.all(np.isfinite(subset["t_start"])) or not np.all(
        np.isfinite(subset["t_end"])
    ):
        raise ToytreeError("t_start and t_end must contain finite values")

    eids = subset["edge_id"].to_numpy(dtype=float)
    if np.any(~np.isfinite(eids)):
        raise ToytreeError("edge_id values must be finite integers")

    eids_int = eids.astype(int)
    if np.any(eids_int != eids):
        raise ToytreeError("edge_id values must be integer-like")
    if np.any((eids_int < 0) | (eids_int >= nedge)):
        raise ToytreeError(
            f"edge_id values must be between 0 and {nedge - 1} (inclusive)"
        )
    subset["edge_id"] = eids_int

    starts = subset["t_start"].to_numpy(dtype=float)
    ends = subset["t_end"].to_numpy(dtype=float)
    if np.any(starts < 0.0):
        raise ToytreeError("t_start values must be >= 0")
    if np.any(ends < starts):
        raise ToytreeError("t_end values must be >= t_start for every segment")

    xpaths: list[np.ndarray] = []
    ypaths: list[np.ndarray] = []
    colors_by_path: list[np.void] = []
    opacities_by_path: list[float] = []
    rows = subset.sort_values(["edge_id", "t_start"]).reset_index(drop=True)
    rows["_color_idx"] = np.arange(rows.shape[0], dtype=int)
    cmap = "Set2" if color is None else color
    seg_colors = np.asarray(
        get_color_mapped_values(rows[state_col].tolist(), cmap=cmap)
    )

    for edge_id, edf in rows.groupby("edge_id", sort=True):
        edge_id = int(edge_id)
        if not bool(show[edge_id]):
            continue
        child, parent = etable[edge_id]
        child = int(child)
        parent = int(parent)
        blen = float(dists[child])
        cx, cy = mark.ntable[child]
        px, py = mark.ntable[parent]
        ax, ay = _get_branch_axis_endpoint(mark, child, parent)

        for _, row in edf.iterrows():
            t_start = float(row["t_start"])
            t_end = float(row["t_end"])
            color_idx = int(row["_color_idx"])

            atol = 1e-8
            if blen <= atol:
                # Zero-length edges can occur in valid trees. Stochastic maps on
                # these edges must have zero start/end times and collapse to a point.
                if (t_start > atol) or (t_end > atol):
                    raise ToytreeError(
                        f"segment times exceed branch length on edge_id={edge_id}: "
                        f"t_start={t_start}, t_end={t_end}, dist={blen}"
                    )
                f0 = 0.0
                f1 = 0.0
            else:
                if t_start > blen + atol:
                    raise ToytreeError(
                        f"segment times exceed branch length on edge_id={edge_id}: "
                        f"t_start={t_start}, dist={blen}"
                    )
                if t_end > blen + atol:
                    raise ToytreeError(
                        f"segment times exceed branch length on edge_id={edge_id}: "
                        f"t_end={t_end}, dist={blen}"
                    )
                f0 = max(0.0, min(1.0, t_start / blen))
                f1 = max(0.0, min(1.0, t_end / blen))

            x0 = float(cx + ((ax - cx) * f0))
            y0 = float(cy + ((ay - cy) * f0))
            x1 = float(cx + ((ax - cx) * f1))
            y1 = float(cy + ((ay - cy) * f1))

            xpaths.append(np.array([x0 + xshift, x1 + xshift], dtype=float))
            ypaths.append(np.array([y0 + yshift, y1 + yshift], dtype=float))
            colors_by_path.append(seg_colors[color_idx])
            opacities_by_path.append(float(edge_opacity[edge_id]))

        # For rectangular phylograms, also draw the orthogonal span segment.
        # It uses the color at the depth-end of the branch segment.
        if (mark.edge_type == "p") and (mark.layout in ("u", "d", "l", "r")):
            end_row = edf.sort_values(["t_end", "t_start"]).iloc[-1]
            end_color_idx = int(end_row["_color_idx"])
            xpaths.append(
                np.array([float(ax + xshift), float(px + xshift)], dtype=float)
            )
            ypaths.append(
                np.array([float(ay + yshift), float(py + yshift)], dtype=float)
            )
            colors_by_path.append(seg_colors[end_color_idx])
            opacities_by_path.append(float(edge_opacity[edge_id]))

    if not xpaths:
        return None

    opac = np.asarray(opacities_by_path, dtype=float)
    widths = np.full(len(xpaths), width, dtype=float)

    outmark = AnnotationStochasticMapLine(
        xpaths=xpaths,
        ypaths=ypaths,
        colors=np.asarray(colors_by_path),
        widths=widths,
        opacity=opac,
        map_id=map_id,
        style=line_style,
    )
    axes.add_mark(outmark)
    return outmark


def _make_line_style(
    stroke_linecap: str,
    stroke_linejoin: str | None,
    stroke_dasharray: str | tuple[int, int] | None,
) -> dict[str, str]:
    """Return validated line-style keys for stochastic-map paths."""
    if stroke_linecap not in ALLOWED_STROKE_LINECAP:
        allowed = ", ".join(sorted(ALLOWED_STROKE_LINECAP))
        raise ValueError(
            f"Invalid 'stroke_linecap' value '{stroke_linecap}'. "
            f"Expected one of: {allowed}"
        )
    if (stroke_linejoin is not None) and (
        stroke_linejoin not in ALLOWED_STROKE_LINEJOIN
    ):
        allowed = ", ".join(sorted(ALLOWED_STROKE_LINEJOIN))
        raise ValueError(
            f"Invalid 'stroke_linejoin' value '{stroke_linejoin}'. "
            f"Expected one of: {allowed}"
        )
    dash = _coerce_dasharray(stroke_dasharray)
    style: dict[str, str] = {"stroke-linecap": stroke_linecap}
    if stroke_linejoin is not None:
        style["stroke-linejoin"] = stroke_linejoin
    if dash is not None:
        style["stroke-dasharray"] = dash
    return style


def _coerce_dasharray(value: str | tuple[int, int] | None) -> str | None:
    """Normalize dasharray to SVG string syntax or None."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if not isinstance(value, tuple) or len(value) != 2:
        raise ValueError(
            "stroke_dasharray must be a string like '2,2' or a tuple[int, int]."
        )
    if not all(isinstance(i, int) for i in value):
        raise ValueError("stroke_dasharray tuple values must be integers.")
    if (value[0] < 0) or (value[1] < 0):
        raise ValueError("stroke_dasharray tuple values must be non-negative.")
    return f"{value[0]},{value[1]}"
