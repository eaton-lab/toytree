#!/usr/bin/env python

"""Function to split or combine color arguments for broader support.

Many tools do not support color as (r,g,b,a) but instead take (r,g,b)
and opacity as a separate style arg. This function is used to split
ToyColor objects to separate the opacity.
"""

from typing import Dict
# from loguru import logger
from toytree.color.src.toycolor import ToyColor

# logger = logger.bind(name="toytree")


# def concat_style_to_str(style: Dict[str, str]) -> str:
#     """Return a style dict concatenated into a style string.

#     Example
#     -------
#     >>> x = {'fill': 'rgb(100%,0%,0%)', 'fill-opacity': 1.0}
#     >>> print(style_to_string(x))
#     >>> # 'fill:rgb(100%,0%,0%);fill-opacity:1.0'
#     """
#     strs = [f"{key}:{value}" for key, value in sorted(style.items())]
#     return ";".join(strs)


# def color_style_split(style: Dict[str, Any]) -> Dict[str, Any]:
#     """

#     This is used in annotation functions to fix up colors in style
#     dicts before passing to toyplot drawing functions.

#     Examples
#     --------
#     >>> d = {'fill': ToyColor("red"), fill-opacity: 0.5}
#     >>> color_style_split(d)
#     >>> # {'fill': (1, 0, 0), 'fill-opacity': 0.5}

#     >>> d = {'fill': ToyColor((1, 0, 0, 0.5))}
#     >>> color_style_split(d)
#     >>> # {'fill': (1, 0, 0), 'fill-opacity': 0.5}
#     """
#     if not style:
#         return {}

#     fill = style.pop("fill", None)
#     fillo = style.pop("fill-opacity", None)
#     stroke = style.pop("stroke", None)
#     strokeo = style.pop("stroke-opacity", None)

#     # get fill or stroke style string with opacity separated and optinally
#     # overwritten if provided as an argument. The 'if not X' arg here
#     # will return False for transparent color (0,0,0,0) which we use up
#     # until this point for missing data (np.nan) colors.
#     styles = []

#     # if None then use parent value
#     if fill is not None:
#         # if (0,0,0,0) then suppress style
#         if not fill:
#             styles.append("fill:none")
#         else:
#             styles.append(ToyColor(fill).get_style_str(opacity=fillo))

#     # if None then use parent value
#     if stroke is not None:
#         # if (0,0,0,0) then suppress style
#         if not stroke:
#             styles.append("stroke:none")
#         else:
#             styles.append(ToyColor(stroke).get_style_str(stroke=True, opacity=strokeo))

#     # keep any other styles in style dict in the style string
#     for key, value in sorted(style.items()):
#         if value is not None:
#             styles.append(f"{key}:{value}")


def concat_style_fix_color(style: Dict[str, str], extra: str = None) -> str:
    """Return a style dict concatenated to string w/ color fixes.

    The style dict here will have fill/stroke color and opacity items
    that need to be evaluated. The colors will always be np.void
    type, representing a single color from an array of colors.

    Note
    ----
    This is destructive to the style dict, popping items from it.
    """
    if not style:
        return ""
    style = style.copy()  # for now, needed for node.style.fill-opacity
    fill = style.pop("fill", None)
    fillo = style.pop("fill-opacity", None)
    stroke = style.pop("stroke", None)
    strokeo = style.pop("stroke-opacity", None)

    # get fill or stroke style string with opacity separated and optinally
    # overwritten if provided as an argument. The 'if not X' arg here
    # will return False for transparent color (0,0,0,0) which we use up
    # until this point for missing data (np.nan) colors.
    styles = []

    # if None then use parent value
    if fill is not None:
        # if (0,0,0,0) then suppress style
        if not fill:
            styles.append("fill:none")
        else:
            styles.append(ToyColor(fill).get_style_str(opacity=fillo))

    # if None then use parent value
    if stroke is not None:
        # if (0,0,0,0) then suppress style
        if not stroke:
            styles.append("stroke:none")
        else:
            styles.append(ToyColor(stroke).get_style_str(stroke=True, opacity=strokeo))

    # keep any other styles in style dict in the style string
    for key, value in sorted(style.items()):
        if value is not None:
            styles.append(f"{key}:{value}")

    # add additional string styles
    if extra:
        styles.append(extra)
    return ";".join(styles)


if __name__ == "__main__":

    # print("result", concat_style_fix_color({"fill": (0, 0, 0, 0)}))
    # print("result", concat_style_fix_color({"fill": (0., 0., 0., 0.)}))
    sty1 = {
        "fill": ToyColor((0., 0., 0., 0.5)),
        "fill-opacity": False,
    }
    print(f"result: '{concat_style_fix_color(sty1)}'")

    sty2 = {
        "fill": ToyColor((0., 0., 0., 0.5)),
        "fill-opacity": None,
    }
    print(f"result: '{concat_style_fix_color(sty2)}'")

    sty3 = {
        "fill": ToyColor((0., 0., 0., 0.5)),
        "fill-opacity": 1.0,
    }
    print(f"result: '{concat_style_fix_color(sty3)}'")

    sty4 = {
        "stroke": ToyColor((0., 0., 0., 0.5)),
        "stroke-opacity": 0.1,
    }
    print(f"result: '{concat_style_fix_color(sty4)}'")

    sty5 = {
        "stroke": ToyColor((0., 0., 0., 0.5)),
        "stroke-opacity": False,
    }
    print(f"result: '{concat_style_fix_color(sty5)}'")

    sty6 = {
        "stroke": ToyColor((0., 0., 0., 0.5)),
        "stroke-opacity": None,
    }
    print(f"result: '{concat_style_fix_color(sty6)}'")

    sty7 = {
        "stroke": ToyColor((0., 0., 0., 0.5)),
        "stroke-opacity": 1.0,
    }
    print(f"result: '{concat_style_fix_color(sty7)}'")

    sty8 = {
        "fill": ToyColor((0., 0., 0., 0.5)),
        "fill-opacity": 1.0,
        "stroke": ToyColor((0., 0., 0., 0.5)),
        "stroke-opacity": 1.0,
    }
    print(f"result: '{concat_style_fix_color(sty8)}'")

    sty9 = {
        "fill": ToyColor((0., 0., 0., 0.5)),
        "fill-opacity": 1.0,
        "stroke": ToyColor((0., 0., 0., 0.5)),
        "stroke-opacity": 1.0,
        "stroke-width": 3.0,
    }
    print(f"result: '{concat_style_fix_color(sty9)}'")
