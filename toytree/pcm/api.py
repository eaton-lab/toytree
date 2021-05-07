#!/usr/bin/env python

"""
PCM: phylogenetic comparative methods tools
"""

from toytree.pcm.phylocomp import (
    # ancestral_state_reconstruction,
    tree_to_vcv, 
    # tip_level_diversification_rates, 
    # tip_level_equal_splits,
)


class PhyloCompAPI:
    """
    Phylogenetic comparative methods implemented on toytrees.
    """
    def __init__(self, tree):
        self._tree = tree


    def independent_contrasts(self, feature):
        """

        """      
        return independent_contrasts(self._tree, feature)


    def ancestral_state_reconstruction(self, feature):
        """
        Infer ancestral states on ancestral nodes for continuous traits
        under a brownian motion model of evolution.

        Modified from IVY interactive (https://github.com/rhr/ivy/)

        Returns a toytree with feature applied to each node.
        """
        return ancestral_state_reconstruction(self._tree, feature)


    def tree_to_VCV(self):
        """

        """
        return VCV(self._tree)


    def tip_level_diversification_rates(self):
        """

        """
        pass


    def tip_level_equal_splits(self):
        """

        """
        pass
