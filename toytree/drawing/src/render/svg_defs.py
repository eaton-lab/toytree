#!/usr/bin/env python

"""Internal helpers to manage SVG ``<defs>`` and ``<linearGradient>``."""

from __future__ import annotations

import xml.etree.ElementTree as xml
from dataclasses import dataclass, field
from typing import Sequence

# from toytree.color.src.concat import concat_style_fix_color


@dataclass(frozen=True)
class LinearGradientStop:
    """One stop entry for an SVG linear gradient."""

    offset: str
    color: str
    opacity: float | str | None = None


@dataclass(frozen=True)
class LinearGradient:
    """One SVG linearGradient definition."""

    id: str
    stops: Sequence[LinearGradientStop]
    attrs: dict[str, str] = field(default_factory=dict)


DEFAULT_LINEAR_GRADIENT_ATTRS = {
    "x1": "0%",
    "y1": "0%",
    "x2": "100%",
    "y2": "0%",
}


def _local_name(tag: str) -> str:
    """Return local XML tag name, dropping optional namespace prefix."""
    return tag.split("}", 1)[-1] if "}" in tag else tag


def get_svg_element(context) -> xml.Element:
    """Return root ``<svg>`` element from a toyplot render context."""
    # get root element or raise exception
    root = getattr(context, "root", None)
    if root is None:
        raise RuntimeError("Render context does not define a root element.")

    # find svg tag as a child of root, or deeper, and raise if not found
    if _local_name(root.tag) == "svg":
        return root
    for elem in root.iter():
        if _local_name(elem.tag) == "svg":
            return elem
    raise RuntimeError("Could not locate SVG element in render context root.")


def get_or_create_defs(svg: xml.Element) -> xml.Element:
    """Get ``<defs>`` under svg root, or create it as first child."""
    for child in list(svg):
        if _local_name(child.tag) == "defs":
            return child
    defs = xml.Element("defs")
    svg.insert(0, defs)
    return defs


def add_linear_gradient(defs: xml.Element, gradient: LinearGradient) -> xml.Element:
    """Append one ``<linearGradient>`` definition to ``defs``.

    Raises
    ------
    ValueError
        If the gradient id is invalid/duplicate, or if stops are malformed.
    """
    if not isinstance(gradient.id, str) or not gradient.id:
        raise ValueError("LinearGradient requires non-empty string 'id'.")
    for child in list(defs):
        if _local_name(child.tag) == "linearGradient" and child.attrib.get("id") == gradient.id:
            raise ValueError(f"Duplicate linearGradient id: '{gradient.id}'.")

    # raise if input gradient is empty
    if len(gradient.stops) == 0:
        raise ValueError("LinearGradient requires one or more stops.")

    # make dict copy of gradient def and create a subelement
    attrs = dict(DEFAULT_LINEAR_GRADIENT_ATTRS)
    attrs.update(gradient.attrs)
    attrs["id"] = gradient.id
    lg = xml.SubElement(
        defs,
        "linearGradient",
        attrs,
    )

    # iterate over stops in the input LinearGradient
    for stop in gradient.stops:
        if not stop.offset or not stop.color:
            raise ValueError("Each LinearGradientStop requires offset and color.")

        # set 'offset', 'stop-color' and 'stop-opacity' on lineargradient
        stop_attrs = {
            "offset": str(stop.offset),
            "stop-color": str(stop.color),
        }
        if stop.opacity is not None:
            stop_attrs["stop-opacity"] = str(stop.opacity)
        xml.SubElement(lg, "stop", stop_attrs)
    return lg


def ensure_linear_gradients(
    context,
    gradients: Sequence[LinearGradient],
) -> dict[str, str]:
    """Ensure gradients exist in svg defs and return ``id -> url(#id)`` mapping."""
    svg = get_svg_element(context)
    defs = get_or_create_defs(svg)
    mapping: dict[str, str] = {}
    for gradient in gradients:
        lg = add_linear_gradient(defs, gradient)
        gid = lg.attrib["id"]
        mapping[gid] = f"url(#{gid})"
    return mapping

