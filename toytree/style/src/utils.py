#!/usr/bin/env python

"""..."""

from typing import Dict
from loguru import logger
from toytree.color.src.toycolor import ToyColor

logger = logger.bind(name="toytree")


def concat_style_to_str2(style: Dict[str, str], extra: str = None) -> str:
    """Return a ...

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

    # print("result", concat_style_to_str2({"fill": (0, 0, 0, 0)}))
    # print("result", concat_style_to_str2({"fill": (0., 0., 0., 0.)}))
    print("result", concat_style_to_str2({
        "fill": ToyColor((0., 0., 0., 0.5)),
        "fill-opacity": False,
        # "stroke": ToyColor((0., 0., 0., 0.5)),
        # "stroke-opacity": 0.1,
    })
    )

    print(
        "result", concat_style_to_str2({
            "fill": ToyColor((0,0,0,0)),
            "fill-opacity": False,
            # "stroke": ToyColor((0., 0., 0., 0.5)),
            # "stroke-opacity": 0.1,
        })
    )
