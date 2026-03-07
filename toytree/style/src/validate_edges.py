#!/usr/bin/env python

"""Validation helpers for edge style sub-dicts used by tree drawing."""

from typing import TypeVar

from toytree.color import ToyColor
from toytree.style.src.style_base import EdgeAlignStyle, EdgeStyle
from toytree.utils import ToytreeError

ToyTree = TypeVar("ToyTree")
ALLOWED_STROKE_LINECAP = {"round", "butt", "square"}
ALLOWED_STROKE_LINEJOIN = {"miter", "round", "bevel"}

__all__ = [
    "validate_edge_style",
    "validate_edge_align_style",
]


def validate_edge_style(
    tree: ToyTree,
    style: EdgeStyle | None = None,
    **kwargs,
) -> EdgeStyle:
    """Return validated edge style settings.

    Parameters
    ----------
    tree
        Tree argument kept for API compatibility with other validators.
    style
        Existing edge style object. If None, a new default ``EdgeStyle`` is
        created and updated.
    **kwargs
        Style key/value overrides to apply.
    """
    if style is None:
        style = EdgeStyle()

    for key, val in kwargs.items():
        style[key] = val

    style.stroke = ToyColor(style.stroke)
    _validate_stroke_linecap(style.stroke_linecap, label="edge_style")
    _validate_stroke_linejoin(style.stroke_linejoin, label="edge_style")
    style.stroke_dasharray = _coerce_stroke_dasharray(
        style.stroke_dasharray,
        label="edge_style",
    )
    return style


def validate_edge_align_style(
    tree: ToyTree,
    style: EdgeAlignStyle | None = None,
    **kwargs,
) -> EdgeAlignStyle:
    """Return validated aligned-edge style settings.

    Parameters
    ----------
    tree
        Tree argument kept for API compatibility with other validators.
    style
        Existing aligned-edge style object. If None, a new default
        ``EdgeAlignStyle`` is created and updated.
    **kwargs
        Style key/value overrides to apply.
    """
    if style is None:
        style = EdgeAlignStyle()

    for key, val in kwargs.items():
        style[key] = val

    style.stroke = ToyColor(style.stroke)
    _validate_stroke_linecap(style.stroke_linecap, label="edge_align_style")
    _validate_stroke_linejoin(style.stroke_linejoin, label="edge_align_style")
    style.stroke_dasharray = _coerce_stroke_dasharray(
        style.stroke_dasharray,
        label="edge_align_style",
    )
    return style


def _coerce_stroke_dasharray(
    value: str | tuple[int | float, int | float] | None,
    label: str,
) -> str | None:
    """Normalize dasharray to SVG string representation."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, tuple) and len(value) == 2:
        a, b = value
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return f"{a},{b}"
    raise ToytreeError(
        f"{label} 'stroke-dasharray' must be str or a 2-item numeric tuple."
    )


def _validate_stroke_linecap(value: str, label: str) -> None:
    """Validate accepted SVG stroke-linecap values."""
    if value not in ALLOWED_STROKE_LINECAP:
        allowed = ", ".join(sorted(ALLOWED_STROKE_LINECAP))
        raise ToytreeError(f"{label} 'stroke-linecap' must be one of: {allowed}.")


def _validate_stroke_linejoin(value: str, label: str) -> None:
    """Validate accepted SVG stroke-linejoin values."""
    if value not in ALLOWED_STROKE_LINEJOIN:
        allowed = ", ".join(sorted(ALLOWED_STROKE_LINEJOIN))
        raise ToytreeError(f"{label} 'stroke-linejoin' must be one of: {allowed}.")


if __name__ == "__main__":
    pass
