#!/usr/bin/env python

"""Add additional Marks to annotate toytree drawings.

Add annotations to drawings to show data or highlight sections
of a toytree drawing. This module is available as both a package-level
module as well as from ToyTree instances as an API.

Examples
--------
>>> tree = toytree.rtree.bdtree(10, seed=123)
>>> c, a, m = tree.draw(layout='d')
>>> toytree.annotate.add_node_pie_markers(axes=a, **kwargs)

>>> tree = toytree.rtree.bdtree(10, seed=123)
>>> c, a, m = tree.draw(layout='d', xbaseline=10)
>>> tree.annotate.node_pie_charts(axes=a, layout='d', xbaseline=10)

>>> # other idea, pass the tree Mark as an arg
>>> c, a, m = tree.draw(layout='d', xbaseline=10)
>>> toytree.annotate.node_pie_charts(mark=m)

Functions
---------
- add_node_markers()
- add_node_labels()
- add_node_pie_markers()

- add_edge_markers()
- add_edge_labels()
- add_edge_pie_markers()
- add_edge_root()
- add_edge_stochastic_map()

- add_axes_scale_bar_to_tree()
- add_axes_scale_bar_to_mark()
- add_confidence_intervals()
- get_toytree_scale_cartesian()

- add_tip_markers()
- add_tip_bars()
- add_tip_text()
- add_tip_heatmap()

- add_image_markers(xpos, ypos, image[s], size, **style)

- radial_...
"""

from __future__ import annotations

import importlib

_LAZY_SUBMODULES = {
    "src": "toytree.annotate.src",
}

_MODULE_EXPORTS = {
    "toytree.annotate.src.add_axes_box_outline": [
        "add_axes_box_outline",
        "set_axes_ticks_external",
    ],
    "toytree.annotate.src.add_edge_markers": [
        "add_edge_markers",
        "add_edge_labels",
    ],
    "toytree.annotate.src.add_edge_stochastic_map": [
        "add_edge_stochastic_map",
    ],
    "toytree.annotate.src.add_edges": [
        "add_edges",
    ],
    "toytree.annotate.src.add_node_markers": [
        "add_node_markers",
        "add_node_labels",
        "add_node_bars",
    ],
    "toytree.annotate.src.add_pie_markers": [
        "add_node_pie_markers",
        "add_edge_pie_markers",
    ],
    "toytree.annotate.src.add_scale_bar": [
        "add_axes_scale_bar_to_tree",
        "add_axes_scale_bar_to_mark",
    ],
    "toytree.annotate.src.add_tip_bars": [
        "add_tip_bars",
    ],
    "toytree.annotate.src.add_tip_markers": [
        "add_tip_markers",
    ],
    "toytree.annotate.src.add_tip_paths": [
        "add_tip_paths",
    ],
    "toytree.annotate.src.add_tip_text": [
        "add_tip_text",
    ],
    "toytree.annotate.src.add_tip_tiles": [
        "add_tip_tiles",
    ],
    "toytree.annotate.src.checks": [
        "get_toytree_scale_cartesian",
    ],
}

_PACKAGE_ATTRS = {
    name: (module_name, name)
    for module_name, names in _MODULE_EXPORTS.items()
    for name in names
    if name != "set_axes_ticks_external"
}

_TREE_API_ONLY_ATTRS = {
    "set_axes_ticks_external": (
        "toytree.annotate.src.add_axes_box_outline",
        "set_axes_ticks_external",
    ),
}

__all__ = sorted(_PACKAGE_ATTRS)


def __getattr__(name: str):
    """Lazily import annotate functions and helper submodules on demand."""
    if name in _LAZY_SUBMODULES:
        module = importlib.import_module(_LAZY_SUBMODULES[name])
        globals()[name] = module
        return module

    if name in _PACKAGE_ATTRS:
        module_name, attr_name = _PACKAGE_ATTRS[name]
    elif name in _TREE_API_ONLY_ATTRS:
        module_name, attr_name = _TREE_API_ONLY_ATTRS[name]
    else:
        raise AttributeError(name)

    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__():
    """Return module attributes plus lazily available public names."""
    return sorted(set(globals()) | set(__all__) | set(_LAZY_SUBMODULES))
