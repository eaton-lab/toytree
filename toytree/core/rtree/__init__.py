#!/usr/bin/env python

"""
Functions for sampling random trees by a variety of methods:
	- rtree
	- unittree
	- imbtree
	- baltree
	- unittree
	- bdtree


Development notes:
------------------
rtree module clobbers rtree subpackage name so that only functions
in the __all__ list are exposed to the API.
"""

from toytree.core.rtree.rtree import *
