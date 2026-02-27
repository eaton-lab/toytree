#!/usr/bin/env python

"""toytree color subpackage.

This is a simple package for accessing convenience functions for
selecting color palettes. See `toyplot.color` for the full color
module.

Examples
--------
>>> tree.draw(node_colors=toytree.colors.COLOR1[0])
>>> tree.draw(node_colors=toytree.colors.COLOR1)

"""

from __future__ import annotations

import importlib

__all__ = [
    "COLORS1",
    "COLORS2",
    "color_cycler",
    "ToyColor",
    "ColorType",
    "concat_style_fix_color",
]

_LAZY_ATTRS = {
    "COLORS1": ("toytree.color.src.utils", "COLORS1"),
    "COLORS2": ("toytree.color.src.utils", "COLORS2"),
    "color_cycler": ("toytree.color.src.utils", "color_cycler"),
    "ToyColor": ("toytree.color.src.toycolor", "ToyColor"),
    "ColorType": ("toytree.color.src.colorkit", "ColorType"),
    "concat_style_fix_color": ("toytree.color.src.concat", "concat_style_fix_color"),
}


def __getattr__(name: str):
    """Lazily import color utilities to avoid eager toyplot imports."""
    if name not in _LAZY_ATTRS:
        raise AttributeError(name)
    module_name, attr_name = _LAZY_ATTRS[name]
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


# from toyplot.color import Palette
# from toyplot.color import brewer
# from toytree.color.src.color_mapper import get_color_mapped_feature
