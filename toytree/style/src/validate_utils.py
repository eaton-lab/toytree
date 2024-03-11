#!/usr/bin/env python

"""...

"""

from typing import Mapping, Any, Dict, Sequence
import numpy as np
from loguru import logger
from toytree.style import TreeStyle, SubStyle
from toytree.utils import ToytreeError

logger = logger.bind(name="toytree")


def check_arr(values: Sequence[Any], label: str, size: int, ctype: type) -> np.ndarray:
    """Return a Sequence as an ndarray checked for expected dtype and size.

    Raises an exception if values is 1 > len(values) > size, or it is
    not of the supported type.
    """
    arr = np.array(values)
    sizes = [size] if isinstance(size, int) else size
    if arr.size not in sizes:
        raise ToytreeError(
            f"'{label}' len mismatch error: len={arr.size} should be "
            f"in {sizes}.")
    if not isinstance(arr[0], ctype):
        raise ToytreeError(
            f"'{label}' type not supported. You entered {type(arr[0])}, "
            f"should be len={ctype}.")
    return arr


def substyle_dict_to_css_dict(style: Mapping[str, Any]) -> Dict[str, Any]:
    """Return dict with css style keys, e.g., 'font_size' -> 'font-size'."""
    new = {}
    for key, val in style.items():
        if "_" in key:
            if key == "anchor_shift":
                css_key = "-toyplot-anchor-shift"
                new[css_key] = style[key]
            else:
                css_key = key.replace("_", "-")
                new[css_key] = style[key]
        else:
            new[key] = val
    return new


def tree_style_to_css_dict(style: TreeStyle) -> Mapping[str, Any]:
    """Return dict w/ css keys from a TreeStyle.

    """
    style = style.__dict__
    for key, val in style.items():
        if isinstance(val, SubStyle):
            style[key] = substyle_dict_to_css_dict(val.__dict__)
    return style


if __name__ == "__main__":

    import toytree
    from toytree.style import validate_style

    tree = toytree.rtree.rtree(5)
    style = tree.style.copy()
    style = validate_style(tree, style)

    print(substyle_dict_to_css_dict(tree.style.node_style))#{"baseline_shift": 10}))
    # print(tree_style_to_css_dict(style))
    # tree_style_to_css_dict(style)
