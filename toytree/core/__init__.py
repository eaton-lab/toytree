#!/usr/bin/env python

"""Core subpackage for tree and node objects.
The core subpackage contains modules for manipulating and drawing
ToyTree and MultiTree objects.

Examples
--------
>>> import toytree

Parse tree data to a ToyTree instance:
>>> tree = toytree.tree("((a,b),c);")
>>> tree = toytree.tree("https://eaton-lab.org/data/Cyathophora.tre")

Generate random ToyTrees
>>> tree = toytree.rtree.unittree(ntips=10)
>>> tree = toytree.rtree.bdtree(ntips=10, b=0.5, d=0.1)

Generate a MultiTree object
>>> trees = [toytree.rtree.unittree(10) for i in range(5)]
>>> mtree = toytree.mtree(trees)
"""

from __future__ import annotations

import importlib

__all__ = ["ToyTree", "Node"]

_LAZY_ATTRS = {
    "ToyTree": ("toytree.core.tree", "ToyTree"),
    "Node": ("toytree.core.node", "Node"),
}


def __getattr__(name: str):
    """Lazily import core objects to avoid eager drawing/color imports."""
    if name not in _LAZY_ATTRS:
        raise AttributeError(name)
    module_name, attr_name = _LAZY_ATTRS[name]
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


# easier acces to the main toyplot types
# from toyplot.canvas import Canvas
# from toyplot.coordinates import Cartesian
# from toyplot.mark import Mark
