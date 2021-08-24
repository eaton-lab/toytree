#!/usr/bin/env python

"""
PCM: phylogenetic comparative methods tools
"""

from toytree.pcm.src.utils import get_vcv_from_tree
# from toytree.pcm.src.pic import (
#     continuous_ancestral_state_reconstruction,
#     phylogenetic_independent_contrasts,
# )
# from toytree.pcm.src.diversification import (
#     calculate_tip_level_diversification,
#     calculate_equal_splits,
# )


class PhyloCompAPI:
    """
    Phylogenetic comparative methods implemented on toytrees.
    """
    def __init__(self, tree):
        self._tree = tree


    def phylogenetic_independent_contrasts(self, feature):
        """
        Returns a dictionary of independent contrasts mapped to each node
        idx of a tree for a selected continuous feature (trait) under a 
        Brownian motion model of evolution.

        Modified from IVY interactive (https://github.com/rhr/ivy/)

        Parameters
        ----------
        feature: (str)
            The name of a feature of the tree that has been mapped to all 
            tip nodes of the tree. 

        Returns
        -------
        dict
        """
        return phylogenetic_independent_contrasts(self._tree, feature)


    def continuous_ancestral_state_reconstruction(self, feature):
        """
        Infer ancestral states on ancestral nodes for continuous traits
        under a brownian motion model of evolution.

        Modified from IVY interactive (https://github.com/rhr/ivy/)

        Returns a toytree with feature applied to each node.
        """
        return continuous_ancestral_state_reconstruction(self._tree, feature)


    def tree_to_vcv(self):
        """
        Return a variance-covariance matrix representing the tree topology
        where the length of shared ancestral edges are covariance and 
        terminal edges are variance.
        """
        return tree_to_vcv(self._tree)


    def tip_level_diversification_rates(self):
        """
        Returns a dataframe with tip-level diversification rates
        sensu Jetz 2012.
        """

        return calculate_tip_level_diversification(self._tree)


    def equal_splits(self):
        """
        Return DataFrame with equal splits (ES) measure sensu Redding and 
        Mooers 2006.
        """
        return calculate_equal_splits(self._tree)
