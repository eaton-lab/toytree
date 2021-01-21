#!/usr/bin/env python

"""
Organization of code in toytree
"""

__version__ = "2.1.0-dev"
__author__ = "Deren Eaton"


# bring API shortcuts to the front
from toytree.core.Toytree import ToyTree as tree
# from .Toytree import RawTree as rawtree
# from .Multitree import MultiTree as mtree

# accessible as toytree.[module].[func] or tree.[module].[func]
from . import drawing
from . import random
from . import treemod
from .core.TreeNode import TreeNode
from .utils.logger import set_loglevel
# from .drawing import *
# from .random import *
# from .pcm import *

# legacy support
import toytree.random as rtree

# start the logger in INFO
set_loglevel("WARNING")
