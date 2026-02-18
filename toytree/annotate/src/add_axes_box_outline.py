#!/usr/bin/env python

"""Add outline annotations around Cartesian axes regions."""

from __future__ import annotations

from typing import Any, Literal

from toytree.core import ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian

# from toytree.annotate.src.annotation_mark import (
#     get_last_toytree_mark_from_cartesian,
#     assert_tree_matches_mark,
# )

__all__ = ["add_axes_box_outline"]


def _stroke_width(style: dict[str, Any]) -> float:
    """Extract numeric stroke-width from a style mapping."""
    value = style.get("stroke-width", 1.0)
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower()
    if text.endswith("px"):
        text = text[:-2]
    try:
        return float(text)
    except ValueError:
        return 1.0


@add_subpackage_method(AnnotationAPI)
def add_axes_box_outline(
    tree: ToyTree,
    axes: Cartesian,
    region: Literal["canvas", "axes"] = "canvas",
    style: dict[str, Any] | None = None,
    expand: None | int | tuple[int, int, int, int] = None,
    behind: bool = False,
) -> Cartesian:
    """Return an overlay Cartesian with a box outline around a plot region.

    Parameters
    ----------
    region: "canvas" or "axes"
        Select the region to outline.
        - "canvas": full canvas bounds.
        - "axes": outer axes bounds including padding.
    style: dict[str, Any] | None
        Optional style updates for the rectangle. Both stroke and fill
        can be styled, e.g., ``{"stroke": "red", "fill": "none"}``.
    expand: None | int | tuple[int, int, int, int]
        Additive expansion on (left, right, top, bottom) bounds. If int,
        applies the same value to all four sides. Positive values expand
        outward; negative values contract inward.
    behind: bool
        If True, place the overlay behind the provided `axes` in canvas
        render order.

    Note
    ----
    This function does not mutate the input axes. It returns a new
    overlay axes object used only to render the box rectangle.
    """
    _ = tree
    if region not in ("canvas", "axes"):
        raise ValueError("region must be one of: 'canvas', 'axes'.")

    # set default style and update with user args
    style_ = {
        "stroke": "#262626",
        "stroke-width": 2.0,
        "fill": "none",
    }
    if style is not None:
        style_.update(style)

    # nudge stroke from edges to ensure fully visible
    inset = _stroke_width(style_) / 2.0

    # fetch the canvas
    canvas = axes._scenegraph.sources("render", axes)[0]

    # get boundaries from selected region
    if region == "canvas":
        # Outer drawable bounds of the canvas, inset by half stroke width
        # so the full stroke remains visible.
        left = float(inset)
        right = float(canvas.width - inset)
        top = float(inset)
        bottom = float(canvas.height - inset)
    else:
        pad = float(axes.padding)
        left = float(axes._xmin_range) - pad
        right = float(axes._xmax_range) + pad
        top = float(axes._ymin_range) - pad
        bottom = float(axes._ymax_range) + pad

    # Apply optional outward / inward expansion.
    if expand is not None:
        if isinstance(expand, (int, float)):
            eml = emr = emt = emb = float(expand)
        else:
            if len(expand) != 4:
                raise ValueError("expand tuple must be (left, right, top, bottom).")
            eml, emr, emt, emb = [float(i) for i in expand]
        left -= eml
        right += emr
        top -= emt
        bottom += emb
    if not (left < right and top < bottom):
        raise ValueError("Outline region collapsed; reduce padding / stroke-width.")

    overlay = canvas.cartesian(
        margin=0,
        padding=0,
        show=False,
        xshow=False,
        yshow=False,
        xmin=0,
        xmax=canvas.width,
        ymin=canvas.height,
        ymax=0,
    )

    overlay.rectangle(left, right, top, bottom, style=style_)

    if behind:
        render_targets = canvas._scenegraph._relationships["render"]._targets[canvas]
        if overlay in render_targets and axes in render_targets:
            render_targets.remove(overlay)
            render_targets.insert(render_targets.index(axes), overlay)
    return overlay


@add_subpackage_method(AnnotationAPI)
def set_axes_ticks_external(
    tree: ToyTree,
    axes: Cartesian,
    show_domain: bool = True,
) -> Cartesian:
    """Add custom generic style to plot axes.

    Sets tick marks to extend 5px outside of spine, tick mark labels
    to 10px outside of spine, and text labels to 30px outside of spine.
    To make sure that labels can still fit, the margin is also increased
    by 10px, so that it is 60px on top, bottom, left and right.
    """
    axes.x.ticks.show = True
    axes.x.domain.show = show_domain
    axes.y.domain.show = show_domain
    axes.y.ticks.show = True
    axes.x.ticks.near = 5
    axes.x.ticks.far = 0
    axes.y.ticks.near = 5
    axes.y.ticks.far = 0
    axes.x.ticks.labels.offset = 10
    axes.y.ticks.labels.offset = 10
    axes.y.label.offset = 30
    axes.x.label.offset = 30
    axes.label.offset = 20

    # this is equivalent to increasing margin from default=50 to 60.
    axes._xmin_range += 10
    axes._xmax_range -= 10
    axes._ymin_range += 10
    axes._ymax_range -= 10
    return axes


if __name__ == "__main__":
    pass
