#!/usr/bin/env python

"""Random or fixed tree generation subpackage

The :mod:`toytree.core.random.rtree` is accessible from the top-level
of the toytree package as :mod:`toytree.rtree`. This module includes
functions for generating random trees, like `rtree` and `bdtree`, or
fixed trees of topology shapes that are often useful for research,
such as `baltree` or `imbtree`. 

Examples
--------
>>> tree1 = toytree.rtree.rtree(10)
>>> tree2 = toytree.rtree.unittree(ntips=10, seed=123)
>>> tree3 = toytree.rtree.baltree(ntips=10, treeheight=1e6)
"""

from toytree.rtree._src.rtree import (
	rtree, unittree, imbtree, baltree, bdtree, coaltree)
