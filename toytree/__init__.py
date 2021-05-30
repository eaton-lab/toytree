#!/usr/bin/env python

"""
Toytree: A minimalist Python package for tree drawing and manipulation.
...
"""

__version__ = "2.1.0-dev"
__author__ = "Deren Eaton"


# expose types: ToyTree, MultiTree
# expose constructors: .tree, .rtree, .mtree, .rawtree
from toytree.src.tree import tree, ToyTree
from toytree.src.rawtree import RawTree as rawtree
from toytree.src.treenode import TreeNode
from toytree.src import rtree
from toytree.src.multitree import mtree, MultiTree

# expose submodules
# import toytree.pcm

# start the logger in INFO
# from toytree.utils.logger import set_loglevel
# set_loglevel("WARNING")
