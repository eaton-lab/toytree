#!/usr/bin/env python

"""A minimalist Python package for visualizing and studying evolution 
on trees.

Toytree's primary use if for visualizing and manipulating tree data
structures. It includes a number of additional subpackages for working
with trees as data, or data on trees. All subpackages make use only of
standard Python data science libs (e.g., numpy, scipy, pandas, numba) 
and does not include wrappers around any external tools.

"""

__version__ = "3.0.10"
__author__ = "Deren Eaton"

# core class objects
from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.core.multitree import MultiTree

# convenience functions
from toytree.io.src.treeio import tree
from toytree.io.src.mtreeio import mtree
from toytree.io.src.save import save

# toytree v3 supported subpackages
import toytree.rtree
import toytree.distance
import toytree.io
import toytree.mod
import toytree.color
import toytree.enum
import toytree.pcm
import toytree.network
import toytree.annotate
import toytree.data


# container trees... container

# start the logger at log_level WARNING
from toytree.utils.src.logger_setup import set_log_level
set_log_level("WARNING")
