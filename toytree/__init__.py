#!/usr/bin/env python

"""
A minimalist Python package for visualizing and studying evolution on trees.
"""

__version__ = "2.1.1-dev"
__author__ = "Deren Eaton"


# expose core classes (TreeNode, ToyTree, MultiTree)
# and factory functions (.tree, .rtree, .mtree, .rawtree)
from toytree.core.tree import tree, ToyTree
from toytree.core.rawtree import RawTree as rawtree
from toytree.core.treenode import TreeNode
from toytree.core.multitree import mtree, MultiTree

# submodules are exposed with curated functions in their __init__
# from toytree.pcm import ...
# from toytree.mod import ...
# from toytree.distance import ...
# from toytree.annotate import ...

# should these be made into top-level submodules?
from toytree.core import rtree
# from toytree.style import ...

# from toytree.core.style.color import ToyColor
from toytree.core.style.color import COLORS1, COLORS2, color_cycler
# expose submodules
# import toytree.pcm

# start the logger in INFO
from toytree.utils.src.logger_setup import set_log_level
set_log_level("WARNING")
