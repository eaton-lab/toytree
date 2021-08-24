#!/usr/bin/env python

"""
Random or fixed tree generation submodule.

The :mod:`toytree.core.random.rtree` is accessible from the top-level
of the toytree package as :mod:`toytree.rtree`. This module includes
functions for generating random trees, like `rtree` and `bdtree`, or
fixed trees of topology shapes that are often useful for research,
such as `baltree` or `imbtree`. 
"""

from .rtree import *
