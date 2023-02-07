#!/usr/bin/env python

"""..."""

from typing import Dict
from toytree.color.src.toycolor import ToyColor

def concat_style_to_str2(style: Dict[str, str], extra: str = None) -> str:
    """..."""
    if not style:
        return ""
    fill = style.pop("fill", None)
    fillo = style.pop("fill-opacity", None)
    stroke = style.pop("stroke", None)
    strokeo = style.pop("stroke-opacity", None)    
    
    # get 'fill''
    styles = []
    if fill:
        styles.append(ToyColor(fill).get_style_str(opacity=fillo))
    if stroke:
        styles.append(ToyColor(stroke).get_style_str(stroke=True, opacity=strokeo))
    for key, value in sorted(style.items()):
        if value is not None:
            styles.append(f"{key}:{value}")

    # add additional string styles
    if extra:
        styles.append(extra)
    return ";".join(styles)
