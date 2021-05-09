#!/usr/bin/env python

"""
Organization of code in toytree
"""

__version__ = "2.1.0-dev"
__author__ = "Deren Eaton"


# bring API shortcuts to the front
from toytree.core.Toytree import tree, ToyTree
from toytree.core.Rawtree import RawTree as rawtree
# from toytree.core.Multitree import MultiTree as mtree


# accessible as toytree.[module].[func] or tree.[module].[func]
from toytree.core.TreeNode import TreeNode
from toytree.utils.logger import set_loglevel

# legacy support
# import toytree.random as rtree
import toytree.rtree
import toytree.distance
import toytree.drawing
import toytree.treemod
# from . import drawing
# from . import random
# from . import treemod
# from .drawing import *
# from .random import *
# from .pcm import *




# start the logger in INFO
set_loglevel("WARNING")
