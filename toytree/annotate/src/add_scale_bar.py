#!/usr/bin/env python

"""Modify ticks and labels on tree axes into a configurable scale bar."""

from __future__ import annotations

from typing import Any, Callable, Literal, Sequence

import numpy as np
from toyplot import locator

from toytree.annotate.src.checks import assert_tree_matches_mark, get_last_toytree_mark
from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian
from toytree.drawing.src.scale_axes import (
    get_toytree_scale_cartesian,
    sync_scale_cartesian_ranges,
)

__all__ = ["add_axes_scale_bar"]


def _get_outward_label_sign(mark: Any, axis: Literal["x", "y"]) -> float:
    """Return signed direction where positive label_offset is outward."""
    # Explicit layout-based mapping for deterministic visual behavior.
    if axis == "x" and mark.layout in ("r", "l"):
        return -1.0
    if axis == "y" and mark.layout in ("u", "d"):
        return 1.0

    # Fallback for other layouts.
    if axis == "x":
        ys = mark.domain("y")
        ycenter = 0.5 * (ys[0] + ys[1])
        return -1.0 if ycenter > mark.ybaseline else 1.0
    xs = mark.domain("x")
    xcenter = 0.5 * (xs[0] + xs[1])
    return -1.0 if xcenter > mark.xbaseline else 1.0


def _apply_axes_expand_margin(
    axes: Cartesian,
    expand_margin: None | int | tuple[int, int, int, int],
) -> None:
    """Expand whitespace margins by symmetric or side-specific deltas."""
    if expand_margin is None:
        return
    if isinstance(expand_margin, int):
        left = right = top = bottom = float(expand_margin)
    else:
        if len(expand_margin) != 4:
            raise ValueError("expand_margin tuple must be (left, right, top, bottom).")
        left, right, top, bottom = [float(i) for i in expand_margin]

    xmin = float(axes._xmin_range)
    xmax = float(axes._xmax_range)
    ymin = float(axes._ymin_range)
    ymax = float(axes._ymax_range)
    new_xmin = xmin + left
    new_xmax = xmax - right
    new_ymin = ymin + top
    new_ymax = ymax - bottom
    if (new_xmin >= new_xmax) or (new_ymin >= new_ymax):
        raise ValueError("expand_margin too large: axes range collapsed or inverted.")
    axes._set_xmin_range(new_xmin)
    axes._set_xmax_range(new_xmax)
    axes._set_ymin_range(new_ymin)
    axes._set_ymax_range(new_ymax)


@add_subpackage_method(AnnotationAPI)
def add_axes_scale_bar(
    tree: ToyTree,
    axes: Cartesian,
    axis: Literal["auto", "x", "y"] = "auto",
    range: tuple[float, float] | None = None,
    scale: bool | int | float | None = None,
    nticks: int | None = None,
    tick_locations: Sequence[float] | None = None,
    only_inside: bool = True,
    formatter: str | Callable[[float], str] | None = None,
    precision: int = 6,
    trim: Literal["k", ".", "0", "-"] = "-",
    label: str | None = None,
    label_center: Literal["axis", "spine"] = "spine",
    label_style: dict[str, Any] | None = None,
    label_offset: int | None = None,
    show_axis: bool = True,
    show_ticks: bool = True,
    show_tick_labels: bool = True,
    ticks_near: int | None = None,
    ticks_far: int | None = None,
    tick_label_offset: int | None = None,
    spine_style: dict[str, Any] | None = None,
    ticks_style: dict[str, Any] | None = None,
    tick_labels_style: dict[str, Any] | None = None,
    padding: float | None = None,
    expand_margin: None | int | tuple[int, int, int, int] = None,
) -> Cartesian:
    """Add or update a tree depth scale bar on companion axes.

    Parameters
    ----------
    axes: Cartesian
        Host axes containing a rendered ``ToyTreeMark``. The scale bar is
        drawn on a hidden companion Cartesian linked to this host axes.
    axis: "auto", "x", or "y"
        Axis to place the scale bar. "auto" infers from tree layout.
    range: tuple[float, float] or None
        The scale-bar domain in tree units. If None, infer from the
        tree domain for the selected axis.
    scale: bool | int | float | None
        If None, use the mark's existing `scale_bar` setting.
        If False, do not modify axes.
        If True, keep raw units.
        If numeric, divide tick labels by this value.
    nticks: int or None
        Target number of ticks for Extended locator mode.
    tick_locations: Sequence[float] or None
        Explicit tick locations in data coordinates. When provided,
        an Explicit locator is used; otherwise Extended is used.
    only_inside: bool
        Forwarded to toyplot's Extended locator.
    formatter: str, callable, or None
        Tick label formatter. Format-string or callable(value)->str.
    precision, trim:
        Defaults for numeric formatting when formatter is None.
    label: str or None
        Optional scale-bar axis label text.
    label_center: "axis" or "spine"
        Label placement mode. "axis" uses the native axis label.
        "spine" centers a custom label on the active scale-bar spine
        domain and offsets it away from the tree.
    label_style: dict[str, Any] or None
        CSS style overrides for the axis label.
    label_offset: int or None
        Offset for axis label placement where positive values move
        farther from the tree and negative values move toward the tree.
    show_axis, show_ticks, show_tick_labels: bool
        Visibility controls for axis line, ticks, and tick labels.
    ticks_near, ticks_far: int or None
        Tick lengths near / far from the spine.
    tick_label_offset: int or None
        Offset for tick labels relative to the ticks.
    spine_style: dict[str, Any] or None
        Optional style updates for the active axis spine.
    ticks_style: dict[str, Any] or None
        Optional style updates for active axis ticks.
    tick_labels_style: dict[str, Any] or None
        Optional style updates for active axis tick labels.
    padding: float or None
        If provided, sets `axes.padding` to this value.
    expand_margin: None | int | tuple[int, int, int, int]
        Optional additive expansion of whitespace margins. If int,
        apply the same delta to all four sides. If tuple, order is
        `(left, right, top, bottom)`. Positive values increase margins
        and shrink the drawable data area; negative values do the
        opposite.

    Notes
    -----
    The input `axes` remains the main plotting axes for tree and annotation
    marks. The scale bar is rendered on a hidden companion Cartesian linked
    to `axes`. This keeps tree-depth ticks tied to tree edges while allowing
    labels / annotations on `axes` to expand display extents independently.
    You can inspect the companion axes with
    `toytree.annotate.get_toytree_scale_cartesian(axes)`.

    Examples
    --------
    Add a default scale bar after drawing:
    >>> tree = toytree.rtree.unittree(10, seed=1)
    >>> canvas, axes, mark = tree.draw(scale_bar=False)
    >>> tree.annotate.add_axes_scale_bar(axes)

    Scale labels into millions:
    >>> tree = toytree.rtree.unittree(10, seed=1)
    >>> canvas, axes, mark = tree.draw(scale_bar=False)
    >>> tree.annotate.add_axes_scale_bar(axes, scale=1e6, label="Time (Myr)")

    Custom range and explicit ticks:
    >>> tree = toytree.rtree.unittree(10, seed=1)
    >>> canvas, axes, mark = tree.draw(scale_bar=False)
    >>> tree.annotate.add_axes_scale_bar(
    >>>     axes,
    >>>     axis="x",
    >>>     range=(0, 5),
    >>>     tick_locations=[0, 1, 2, 5],
    >>>     scale=True,
    >>> )

    Center label on the scale-bar spine domain:
    >>> tree = toytree.rtree.unittree(10, seed=1)
    >>> canvas, axes, mark = tree.draw(scale_bar=False)
    >>> tree.annotate.add_axes_scale_bar(
    >>>     axes,
    >>>     label="Time",
    >>>     label_center="spine",
    >>>     padding=25,
    >>>     spine_style={"stroke-width": 1.5},
    >>>     ticks_style={"stroke": "black"},
    >>> )

    Access the companion scale axes for additional styling:
    >>> tree = toytree.rtree.unittree(10, seed=2)
    >>> canvas, axes, mark = tree.draw(scale_bar=True)
    >>> saxes = toytree.annotate.get_toytree_scale_cartesian(axes)
    >>> saxes.x.spine.style["stroke"] = "crimson"
    """
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)
    scale_axes = get_toytree_scale_cartesian(axes, create=True)

    # resolve effective scale from override or mark default.
    effective_scale = mark.scale_bar if scale is None else scale
    # explicit override to disable any changes
    if scale is False:
        scale_axes.show = False
        scale_axes.x.show = False
        scale_axes.y.show = False
        return axes
    # preserve historical behavior: manual annotation still draws a
    # scale bar even if mark.scale_bar is False.
    if effective_scale is False:
        effective_scale = True

    # resolve axis
    if axis == "auto":
        if mark.layout in ("r", "l"):
            axis = "x"
        elif mark.layout in ("u", "d"):
            axis = "y"
        else:
            xdom = mark.domain("x")
            ydom = mark.domain("y")
            xspan = abs(xdom[1] - xdom[0])
            yspan = abs(ydom[1] - ydom[0])
            axis = "x" if xspan >= yspan else "y"

    # resolve range
    if range is not None:
        if len(range) != 2:
            raise ValueError("range must be a tuple of (min, max).")
        tmin, tmax = float(range[0]), float(range[1])
        if tmax <= tmin:
            raise ValueError("range max must be greater than range min.")
    else:
        if axis == "x":
            left, right = mark.domain("x")
            tree_height = max(abs(right - left), 1e-6)
            if mark.layout == "r":
                tmin, tmax = -tree_height, 0.0
            else:
                tmin, tmax = 0.0, tree_height
        else:
            bottom, top = mark.domain("y")
            tree_height = max(abs(top - bottom), 1e-6)
            if mark.layout == "u":
                tmin, tmax = -tree_height, 0.0
            else:
                tmin, tmax = 0.0, tree_height

    # resolve tick locations
    if tick_locations is not None:
        locs = np.array(tick_locations, dtype=float)
    else:
        if nticks is None:
            if axis == "x":
                csize = axes._xmax_range - axes._xmin_range
            else:
                csize = axes._ymax_range - axes._ymin_range
            nticks = int(max(5, np.floor(csize / 75).astype(int)))
        lct = locator.Extended(count=nticks, only_inside=only_inside)
        locs = lct.ticks(tmin, tmax)[0]
        if only_inside:
            locs = locs[(locs >= tmin) & (locs <= tmax)]

    # apply unit scaling
    if isinstance(effective_scale, (int, float)):
        labels_data = abs(locs / effective_scale)
    else:
        labels_data = abs(locs.copy())

    if formatter is None:
        labels = [
            np.format_float_positional(val, precision=precision, trim=trim)
            for val in labels_data
        ]
    elif isinstance(formatter, str):
        labels = [formatter.format(val) for val in labels_data]
    else:
        labels = [formatter(val) for val in labels_data]

    # keep host axes available for marks and extents; render the scale
    # bar only on the companion scale-axes.
    axes.x.show = False
    axes.y.show = False

    # apply spacing edits on the host axes first, then synchronize
    # scale-axes geometry so projections share the same canvas ranges.
    if padding is not None:
        axes.padding = padding
    _apply_axes_expand_margin(axes, expand_margin)
    sync_scale_cartesian_ranges(axes, scale_axes)
    # domain is mirrored from host axes by HostDomainMark, so keep
    # explicit domain overrides disabled.
    scale_axes.x.domain.min = None
    scale_axes.x.domain.max = None
    scale_axes.y.domain.min = None
    scale_axes.y.domain.max = None

    # set scale-axes visibility/style
    scale_axes.show = show_axis
    if padding is not None:
        scale_axes.padding = padding
    if axis == "x":
        scale_axes.x.show = show_axis
        scale_axes.y.show = False
        scale_axes.x.ticks.show = show_ticks
        scale_axes.x.ticks.labels.show = show_tick_labels
        if ticks_near is not None:
            scale_axes.x.ticks.near = ticks_near
        if ticks_far is not None:
            scale_axes.x.ticks.far = ticks_far
        if tick_label_offset is not None:
            scale_axes.x.ticks.labels.offset = tick_label_offset
        if label_offset is not None:
            sign = _get_outward_label_sign(mark, "x")
            scale_axes.x.label.offset = int(sign * label_offset)
        if spine_style is not None:
            scale_axes.x.spine.style = {**scale_axes.x.spine.style, **spine_style}
        if ticks_style is not None:
            scale_axes.x.ticks.style = {**scale_axes.x.ticks.style, **ticks_style}
        if tick_labels_style is not None:
            scale_axes.x.ticks.labels.style = {
                **scale_axes.x.ticks.labels.style,
                **tick_labels_style,
            }
    else:
        scale_axes.y.show = show_axis
        scale_axes.x.show = False
        scale_axes.y.ticks.show = show_ticks
        scale_axes.y.ticks.labels.show = show_tick_labels
        if ticks_near is not None:
            scale_axes.y.ticks.near = ticks_near
        if ticks_far is not None:
            scale_axes.y.ticks.far = ticks_far
        if tick_label_offset is not None:
            scale_axes.y.ticks.labels.offset = tick_label_offset
        if label_offset is not None:
            sign = _get_outward_label_sign(mark, "y")
            scale_axes.y.label.offset = int(sign * label_offset)
        if spine_style is not None:
            scale_axes.y.spine.style = {**scale_axes.y.spine.style, **spine_style}
        if ticks_style is not None:
            scale_axes.y.ticks.style = {**scale_axes.y.ticks.style, **ticks_style}
        if tick_labels_style is not None:
            scale_axes.y.ticks.labels.style = {
                **scale_axes.y.ticks.labels.style,
                **tick_labels_style,
            }

    # clear any stale custom renderer attrs from prior calls.
    scale_axes.x._toytree_label_mode = None
    scale_axes.y._toytree_label_mode = None
    scale_axes.x._toytree_label_data_midpoint = None
    scale_axes.y._toytree_label_data_midpoint = None

    # set axis label text
    if label is not None:
        if axis == "x":
            scale_axes.x.label.text = label
            if mark.layout in ("r", "l"):
                scale_axes.x.label.location = "below"
            if label_center == "spine":
                scale_axes.x._toytree_label_mode = "spine"
                xdom = mark.domain("x")
                scale_axes.x._toytree_label_data_midpoint = 0.5 * (xdom[0] + xdom[1])
        else:
            scale_axes.y.label.text = label
            if label_center == "spine":
                scale_axes.y._toytree_label_mode = "spine"
                ydom = mark.domain("y")
                scale_axes.y._toytree_label_data_midpoint = 0.5 * (ydom[0] + ydom[1])
    else:
        if axis == "x":
            scale_axes.x.label.text = ""
        else:
            scale_axes.y.label.text = ""

    # optional axis label style
    if label_style is not None:
        if axis == "x":
            scale_axes.x.label.style.update(label_style)
        else:
            scale_axes.y.label.style.update(label_style)

    # place ticks on baseline-aware coordinates
    if axis == "x":
        shifted_locs = locs + mark.xbaseline
        scale_axes.x.ticks.locator = locator.Explicit(
            locations=shifted_locs,
            labels=labels,
        )
    else:
        shifted_locs = locs + mark.ybaseline
        scale_axes.y.ticks.locator = locator.Explicit(
            locations=shifted_locs,
            labels=labels,
        )

    # mark companion axes dirty so toyplot recomputes domains/ticks.
    scale_axes._finalized = None
    return axes


if __name__ == "__main__":
    import toytree

    orig = toytree.rtree.rtree(5, seed=123)
    orig.set_node_data("orig", {i: i.idx for i in orig}, inplace=True)
    # orig.draw('p', node_labels="orig");
    a, b = orig.mod.bisect(1)
    c, ax, m = a.draw()
    add_axes_scale_bar(
        a,
        ax,
    )  # scale_bar=True);
