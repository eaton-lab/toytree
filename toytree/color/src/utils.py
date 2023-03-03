#!/usr/bin/env python

"""Utilities for working with colors.

"""

from typing import Optional, TypeVar
import itertools
import toyplot.color

Palette = TypeVar("Palette")

# default toytree color palettes
COLORS1 = toyplot.color.brewer.palette("Set2")
COLORS2 = toyplot.color.brewer.palette("Dark2")


def color_cycler(palette: Optional[Palette] = None):
    """Return an infinite cycling iterator over colors in a palette.

    This returns a generator that will cycle the palette infinitely. 
    If palette is None it uses `toytree.color.COLORS1` palette.

    Note
    ----
    Do NOT call `list(color_cycler())` since it is infinite. Instead
    you should iterate from the generator with `next`.

    Example
    --------
    >>> tree = toytree.rtree.unittree(25)
    >>> icolors = toytree.color.color_cycler(toytree.color.COLORS2)
    >>> tipcolors = [next(icolors) for i in tree.get_tip_labels()]
    >>> tree.draw(tip_labels_colors=tipcolors)
    """
    if palette is None:
        palette = COLORS1
    return itertools.cycle(palette)


# def split_rgba_to_rgb(style):
#     """TODO: update/simplify using ToyColor..."""
#     for key in style:
#         if key in ["fill", "stroke"]:
#             value = style.pop(key)
#             # value = ColorKit(value)


# def split_rgba_style(style: Dict[str, str]) -> Dict[str, str]:
#     """Split rgba to rgb and opacity.

#     Because many applications (Inkscape, Adobe Illustrator, Qt) don't handle
#     CSS rgba() colors correctly this function does a work-around.
#     Takes a CSS color in rgba, e.g., 'rgba(40.0%,76.1%,64.7%,1.000)'
#     labeled in a dictionary as {'fill': x, 'fill-opacity': y} and
#     returns with fill as rgb and fill-opacity from rgba. Similarly
#     applied to stroke, stroke-opacity.

#     Note
#     -----
#     If the user sets fill-opacity or stroke-opacity in a style dict
#     it overrules/clobbers any value in the 'a' of the rgba. 
#     """
#     if "fill" in style:
#         color = style["fill"]

#         # try to convert color to css with toyplot. Fails on ...
#         try:
#             color = toyplot.color.css(color)
#         except (TypeError, AttributeError):
#             # print(type(color), color)
#             pass

#         # set 'fill' and 'fill-opacity'
#         if str(color) == "none":
#             style["fill"] = "none"
#             style["fill-opacity"] = 1.0
#         else:
#             rgb = "rgb({:.3g}%,{:.3g}%,{:.3g}%)".format(
#                 color["r"] * 100,
#                 color["g"] * 100,
#                 color["b"] * 100,
#             )
#             style["fill"] = rgb
#             style["fill-opacity"] = str(color["a"])

#     if "stroke" in style:
#         color = style["stroke"]
#         try:
#             color = toyplot.color.css(color)
#         except (TypeError, AttributeError):
#             # print(type(color), color)
#             pass

#         if str(color) == "none":
#             style["stroke"] = "none"
#             style["stroke-opacity"] = 1.0
#         else:
#             rgb = "rgb({:.3g}%,{:.3g}%,{:.3g}%)".format(
#                 color["r"] * 100,
#                 color["g"] * 100,
#                 color["b"] * 100,
#             )
#             style["stroke"] = rgb
#             style["stroke-opacity"] = str(color["a"])
#     return style


# def concat_style_to_str(style: Dict[str, str]) -> str:
#     """Return a style dict concatenated into a style string.

#     Example
#     -------
#     >>> x = {'fill': 'rgb(100%,0%,0%)', 'fill-opacity': 1.0}
#     >>> print(style_to_string(x))
#     >>> # 'fill:rgb(100%,0%,0%);fill-opacity:1.0'
#     """
#     if not style:
#         return ""
#     strs = [
#         f"{key}:{value}" for key, value in sorted(style.items())
#         if value is not None
#     ]
#     return ";".join(strs)


if __name__ == "__main__":

    col = toyplot.color.rgba(1.0, 0.5, 0.5, 0.5)
    sty = {"fill": col, "width": "20px", "height": "20px"}
    print(sty)
    # ssty = split_rgba_style(sty)
    # print(ssty)
    # print(style_to_string(ssty))
