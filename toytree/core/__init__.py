#!/usr/bin/env python

"""
Core Tree objects, as three hierarchical objects:
	TreeNode
	Toytree(TreeNode)
	Multitree([Toytree, Toytree, ...])
"""

from .Toytree import ToyTree
from .Multitree import MultiTree
from .NodeAssist import NodeAssist
