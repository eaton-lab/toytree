#!/usr/bin/env python

"""
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

from toytree.core.tree import ToyTree
from toytree.core.node import Node
# from toytree.core.multitree import MultiTree

# easier acces to the main toyplot types
from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian
from toyplot.mark import Mark
