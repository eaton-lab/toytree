#!/usr/bin/env python

"""
A class wrapper for treemod funcs to make accessible from toytrees
"""

from toytree.treemod.treemod import *


class TreeModAPI:
    """
    Accessible from toytree objects at .mod.[function]
    """
    def __init__(self, tree):
        self._tree = tree

    def node_scale_root_height(self, treeheight=1, include_stem=False, nocopy=False):
        """
        Returns a toytree copy with all nodes multiplied by a constant so that
        the root node height equals the value entered for treeheight. The 
        argument include_stem=True can be used to scale the tree so that the
        root + root.dist is equal to treeheight. This effectively sets the 
        stem height.
        """
        return node_scale_root_height(
            self._tree, treeheight, include_stem, nocopy)


    def node_slider(self, prop=0.999, seed=None):
        """
        Returns a toytree copy with node heights modified while retaining 
        the same topology but not necessarily node branching order. 
        Node heights are moved up or down uniformly between their parent 
        and highest child node heights in 'levelorder' from root to tips.
        The total tree height is retained at 1.0, only relative edge
        lengths change.
        """
        return node_slider(self._tree, prop, seed)



    def node_multiplier(self, multiplier=0.5, seed=None):
        """
        Returns a toytree copy with all nodes multiplied by a constant 
        sampled uniformly between (multiplier, 1/multiplier).
        """
        return node_multiplier(self._tree, multiplier, seed)



    def make_ultrametric(self, strategy=1, inplace=False):
        """
        Returns a tree with branch lengths transformed so that the tree is 
        ultrametric. Strategies include:

        (1) tip-align: 
            extend tips to the length of the fartest tip from the root; 
        (2) NPRS: 
            non-parametric rate-smoothing: minimize ancestor-descendant local 
            rates on branches to align tips (not yet supported); and 
        (3) penalized-likelihood: 
            not yet supported.
        """
        return make_ultrametric(self._tree, strategy, inplace)
