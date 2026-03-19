#!/usr/bin/env python

"""Annotation methods for adding text to tree-tip positions."""

from numbers import Real
from typing import Any, Callable, Mapping, Sequence, Tuple, TypeVar, Union

import numpy as np
import toyplot.units

from toytree.annotate.src.checks import (
    assert_tree_matches_mark,
    get_last_toytree_mark_for_tree,
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
from toytree.utils import ToytreeError

Color = TypeVar("Color", str, tuple, np.ndarray)
__all__ = ["add_tip_text"]


def _normalize_tip_text_style(
    style: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Return CSS-keyed style overrides for tip-text annotations."""
    if style is None:
        return {}
    if not isinstance(style, Mapping):
        raise ToytreeError("style must be a mapping of text style properties.")
    css_style = substyle_dict_to_css_dict(dict(style))
    if "anchor-shift" in css_style and "-toyplot-anchor-shift" not in css_style:
        css_style["-toyplot-anchor-shift"] = css_style.pop("anchor-shift")
    return css_style


def _coerce_tip_text_style_shift(style: Mapping[str, Any], key: str) -> float:
    """Return a finite pixel shift parsed from one text-style key."""
    try:
        value = toyplot.units.convert(
            style.get(key, 0.0),
            target="px",
            default="px",
        )
    except (AttributeError, TypeError, ValueError) as exc:
        raise ToytreeError(f"{key} must be convertible to px units.") from exc
    value = float(value)
    if not np.isfinite(value):
        raise ToytreeError(f"{key} must be a finite numeric value.")
    return value


def _coerce_tip_text_offset(value: float | None, name: str) -> float | None:
    """Return an optional finite numeric offset."""
    if value is None:
        return None
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ToytreeError(f"{name} must be a finite float.")
    value = float(value)
    if not np.isfinite(value):
        raise ToytreeError(f"{name} must be a finite float.")
    return value


def _resolve_tip_text_span_shift(
    layout: str,
    offset_span: float,
    flipped: bool,
) -> float:
    """Return the raw baseline-shift that matches positive local span."""
    # Toyplot baseline-shift moves text in its local "up" direction. These
    # sign choices remap positive offset_span onto the tree's local span axis.
    if layout in ("r", "l"):
        return -float(offset_span)
    if layout in ("u", "d"):
        return float(offset_span)
    return float(offset_span) if flipped else -float(offset_span)


def _transform_tip_text_label(
    label: str,
    fn: Callable[[str], str] | None,
    italic: bool,
    bold: bool,
) -> str:
    """Return one tip label after relabel-style text transforms."""
    if label == "":
        return label

    new_label = label
    if fn is not None:
        new_label = fn(new_label)
    if new_label is None:
        return label

    new_label = str(new_label)
    if new_label == "":
        return label
    if italic:
        has_italic = ("<i>" in new_label) and ("</i>" in new_label)
        if not has_italic:
            new_label = f"<i>{new_label}</i>"
    if bold:
        has_bold = ("<b>" in new_label) and ("</b>" in new_label)
        if not has_bold:
            new_label = f"<b>{new_label}</b>"
    return new_label


def _transform_tip_text_labels(
    labels: np.ndarray,
    fn: Callable[[str], str] | None,
    italic: bool,
    bold: bool,
) -> np.ndarray:
    """Return labels after optional callable and HTML tag transforms."""
    if fn is not None and not callable(fn):
        raise ToytreeError("fn must be callable or None.")
    if fn is None and not italic and not bold:
        return labels
    return np.asarray(
        [_transform_tip_text_label(str(label), fn, italic, bold) for label in labels],
        dtype=str,
    )


@add_subpackage_method(AnnotationAPI)
def add_tip_text(
    tree: ToyTree,
    axes: Cartesian,
    labels: Union[str, Sequence[str]] = "name",
    fn: Callable[[str], str] | None = None,
    italic: bool = False,
    bold: bool = False,
    color: Union[Color, Sequence[Color]] = None,
    opacity: Union[float, Sequence[float]] = 1.0,
    font_size: Union[int, None] = None,
    font_family: Union[str, None] = None,
    font_weight: Union[int, str, None] = None,
    text_anchor: Union[str, None] = None,
    angle: Union[int, Sequence[int], None] = None,
    mask: Union[np.ndarray, Tuple[int, int, int], None] = None,
    offset_depth: float | None = None,
    offset_span: float | None = None,
    style: Mapping[str, Any] | None = None,
) -> Mark:
    """Add text labels anchored to tree-tip positions on a drawing.

    Style defaults are copied from the currently drawn tree mark so tip text
    inherits the same font, fill, and anchor behavior as the active drawing.
    The two positioning styles ``-toyplot-anchor-shift`` and
    ``baseline-shift`` are reset to ``0.0`` by default for this annotation
    method, then optionally overridden by ``style`` and finally by the
    ``offset_depth`` and ``offset_span`` arguments.

    Parameters
    ----------
    axes : Cartesian
        A Toyplot Cartesian axes object containing a rendered tree drawing.
    labels : str or Sequence[str], default="name"
        Tip text labels in idx (tip traversal) order, or the name of a tip
        feature to extract from the tree.
    fn : Callable[[str], str] or None, default=None
        Optional callable transform applied to each resolved tip label before
        any italic or bold formatting is added.
    italic : bool, default=False
        If True wrap each non-empty label in ``<i>...</i>`` unless italic
        tags are already present.
    bold : bool, default=False
        If True wrap each non-empty label in ``<b>...</b>`` unless bold
        tags are already present.
    color : str, tuple, array-like, or Sequence, default=None
        A single color or sequence of colors for tip text.
    opacity : float or Sequence[float], default=1.0
        A single opacity or sequence of opacities for tip text.
    font_size : int or None, default=None
        Font size in px. Overrides any matching style value.
    font_family : str or None, default=None
        Font family. Overrides any matching style value.
    font_weight : int, str, or None, default=None
        Font weight. Overrides any matching style value.
    text_anchor : str or None, default=None
        Text anchor. Overrides any matching style value before layout-specific
        tip orientation is applied.
    angle : int, Sequence[int], or None, default=None
        A single angle applied to all labels, or a sequence of angles. If
        ``None`` then angles are inherited from the current tree mark.
    mask : bool, tuple[int, int, int], np.ndarray, or None, default=None
        Controls shown tips. Accepted values are:
        - ``None``: show all tips
        - ``bool``: ``True`` shows all tips, ``False`` shows none
        - ``tuple``: ``(show_tips, show_internal, show_root)`` shortcut
        - ``np.ndarray``: boolean array of size ``ntips``
    offset_depth : float or None, default=None
        Optional tip-text offset in px along the local outward depth direction.
        When provided it overrides ``-toyplot-anchor-shift``.
    offset_span : float or None, default=None
        Optional tip-text offset in px along the local span direction.
        When provided it overrides ``baseline-shift`` using layout-aware sign
        conventions so positive values move in the positive span direction.
    style : Mapping[str, Any] or None, default=None
        Optional style overrides. Keys can be CSS-style (for example
        ``"font-size"``, ``"text-anchor"``, ``"-toyplot-anchor-shift"``,
        ``"baseline-shift"``) or pythonic style keys (for example
        ``font_size``, ``text_anchor``). Values in this mapping override tree
        mark defaults but are overridden by explicit function arguments.

    Returns
    -------
    Mark
        An annotation text mark added to the provided axes.

    Raises
    ------
    ToytreeError
        If ``fn`` is not callable, if ``style`` is not a mapping, if a shift
        style is not convertible to px units, or if ``offset_depth`` /
        ``offset_span`` are not finite numeric values.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, mark = tree.draw()
    >>> text = tree.annotate.add_tip_text(
    ...     axes,
    ...     labels="name",
    ...     fn=str.upper,
    ...     italic=True,
    ...     color="blue",
    ...     offset_depth=15,
    ... )
    """
    # get mark for coordinates on plotted tree.
    tmark = get_last_toytree_mark_for_tree(axes, tree)
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
    labels = _transform_tip_text_labels(labels, fn, italic, bold)

    # Start from the rendered tree mark style so defaults match the
    # currently drawn tree labels, then layer user style overrides. Tip-text
    # annotations start with zero local shifts instead of the tree's draw-time
    # default anchor offset so offset args default to no extra displacement.
    base_style = dict(getattr(tmark, "tip_labels_style", {}))
    base_style["-toyplot-anchor-shift"] = 0.0
    base_style["baseline-shift"] = 0.0
    user_style = _normalize_tip_text_style(style)
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

    anchor = _coerce_tip_text_style_shift(style, "-toyplot-anchor-shift")
    baseline = _coerce_tip_text_style_shift(style, "baseline-shift")
    offset_depth = _coerce_tip_text_offset(offset_depth, "offset_depth")
    offset_span = _coerce_tip_text_offset(offset_span, "offset_span")
    if offset_depth is not None:
        anchor = offset_depth
    style["-toyplot-anchor-shift"] = anchor

    # match tip label orientation behavior in render_tree.py
    layout = str(getattr(tmark, "layout", "r"))
    angles = angle.astype(float).copy()
    styles = [dict(style) for _ in range(labels.size)]
    flip = np.zeros(labels.size, dtype=bool)
    if layout in ("l", "u"):
        flip[:] = True
    elif layout not in ("r", "d"):
        flip = (angles > 90.0) & (angles < 270.0)

    for idx in range(labels.size):
        if offset_span is None:
            styles[idx]["baseline-shift"] = baseline
        else:
            styles[idx]["baseline-shift"] = _resolve_tip_text_span_shift(
                layout,
                offset_span,
                bool(flip[idx]),
            )
        if flip[idx]:
            styles[idx]["text-anchor"] = "end"
            styles[idx]["-toyplot-anchor-shift"] = -anchor

    if layout not in ("r", "l", "u", "d"):
        angles[flip] = angles[flip] - 180.0

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
