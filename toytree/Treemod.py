#!/usr/bin/env python

"""
Tree modification functions
"""

import random


class TreeMod:
    """
    Return a tree with edge lengths modified according to one of 
    the mod functions. 
    """
    def __init__(self, toytree):
        self._toytree = toytree


    def node_scale_root_height(self, treeheight=1, include_stem=False, nocopy=False):
        """
        Returns a toytree copy with all nodes multiplied by a constant so that
        the root node height equals the value entered for treeheight. The 
        argument include_stem=True can be used to scale the tree so that the
        root + root.dist is equal to treeheight. This effectively sets the 
        stem height.
        """
        # make tree height = 1 * treeheight
        if nocopy:
            ctree = self._toytree
        else:
            ctree = self._toytree.copy()

        # get total tree height
        if include_stem:
            _height = ctree.treenode.height + ctree.treenode.dist
        else:
            _height = ctree.treenode.height

        # scale internal nodes 
        for node in ctree.treenode.traverse():
            node.dist = (node.dist / _height) * treeheight
        ctree._coords.update()
        return ctree


    def node_slider(self, prop=0.999, seed=None):
        """
        Returns a toytree copy with node heights modified while retaining 
        the same topology but not necessarily node branching order. 
        Node heights are moved up or down uniformly between their parent 
        and highest child node heights in 'levelorder' from root to tips.
        The total tree height is retained at 1.0, only relative edge
        lengths change.
        """
        # I don't think users should need to access prop
        prop = prop
        assert isinstance(prop, float), "prop must be a float"
        assert prop < 1, "prop must be a proportion >0 and < 1."
        random.seed(seed)

        # make copy and iter nodes from root to tips
        ctree = self._toytree.copy()
        for node in ctree.treenode.traverse():

            # slide internal nodes 
            if node.up and node.children:

                # get min and max slides
                # minjit = max([i.dist for i in node.children]) * prop
                # maxjit = (node.up.height * prop) - node.height

                # the closest child to me
                minchild = min([i.dist for i in node.children])

                # prop distance down toward child
                minjit = minchild * prop

                # prop towards parent
                maxjit = node.dist * prop

                # node.height
                newheight = random.uniform(
                    node.height - minjit, node.height + maxjit)

                # how much lower am i?
                delta = newheight - node.height

                # edges from children to reach me
                for child in node.children:
                    child.dist += delta

                # slide self to match
                node.dist -= delta

        # update new coords
        ctree._coords.update()
        return ctree


    def node_multiplier(self, multiplier=0.5, seed=None):
        """
        Returns a toytree copy with all nodes multiplied by a constant 
        sampled uniformly between (multiplier, 1/multiplier).
        """
        random.seed(seed)
        ctree = self._toytree.copy()
        low, high = sorted([multiplier, 1. / multiplier])
        mult = random.uniform(low, high)
        for node in ctree.treenode.traverse():
            node.dist = node.dist * mult
        ctree._coords.update()
        return ctree


    def make_ultrametric(self, strategy=1, nocopy=False):
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
        if nocopy:
            ctree = self._toytree
        else:
            ctree = self._toytree.copy()

        if strategy == 1:
            for node in ctree.treenode.traverse():
                if node.is_leaf():
                    node.dist += node.height
                    # node.dist = node.height + 1

        else:
            raise NotImplementedError(
                "Strategy {} not yet implemented. Seeking developers."
                .format(strategy))

        return ctree
