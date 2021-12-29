#!/usr/bin/env python

"""A minimalist Python package for visualizing and studying evolution 
on trees.

Toytree's primary use if for visualizing and manipulating tree data
structures. It includes a number of additional subpackages for working
with trees as data, or data on trees. All subpackages make use only of
standard Python data science libs (e.g., numpy, scipy, pandas, numba) 
and does not include wrappers around any external tools.

Examples
--------
>>> tree1 = toytree.rtree.unittree(ntips=10)
>>> tree1.draw();
>>> tree2 = toytree.tree("https://eaton-lab.org/data/Cyathophora.tree")
>>> tree2.root(wildcard="prz").draw(tree_style='o')
"""

__version__ = "3.0-dev"
__author__ = "Deren Eaton"


# expose core classes (TreeNode, ToyTree, MultiTree)
# and factory functions (.tree, .rtree, .mtree, .rawtree)
# from toytree.core.tree import tree, ToyTree
# from toytree.core.rawtree import RawTree as rawtree
# from toytree.core.treenode import TreeNode
# from toytree.core.multitree import mtree, MultiTree

# submodules are exposed with curated functions in their __init__
# from toytree.pcm import ...
# from toytree.mod import ...
# from toytree.distance import ...
# from toytree.annotate import ...

# should these be made into top-level submodules?
# from toytree.core import rtree

# toytree v3 supported modules
from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.core.multitree import MultiTree
from toytree.io.src.treeio import tree
from toytree.io.src.mtreeio import mtree
# from toytree.core.multitree import MultiTree, mtree

import toytree.rtree
import toytree.distance
import toytree.io
# import toytree.color
# import toytree.distance
# import toytree.pcm
# import toytree.mod
# import toytree.annotate

# from toytree.core.style.color import ToyColor
# from toytree.core.style.color import COLORS1, COLORS2, color_cycler

# start the logger in INFO
from toytree.utils.src.logger_setup import set_log_level
set_log_level("WARNING")
