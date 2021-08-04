#!/usr/bin/env python

"""
A class wrapper for treemod funcs to make accessible from toytrees.
"""

from typing import Dict, Optional
from toytree.mod.tree_modifications import (
    node_scale_root_height,
    node_slider,
    node_multiplier,
    set_node_heights,
    make_ultrametric,
)
# from toytree.mod.penalized_likelihood import Chronos
import toytree


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


    def make_ultrametric(self, strategy=1, nocopy=False):
        """
        Returns a tree with branch lengths transformed so that the
        tree is ultrametric. Strategies include:

        (1) tip-align:
            extend tips to the length of the fartest tip from the root;
        (2) NPRS:
            non-parametric rate-smoothing: minimize ancestor-descendant local
            rates on branches to align tips (not yet supported); and
        (3) penalized-likelihood:
            not yet supported.
        """
        return make_ultrametric(self._tree, strategy, nocopy)


    def set_node_heights(self, mapping:Dict[int,float]):
        """
        Enter a dictionary mapping node idx to heights. Node idxs that
        are not included as keys will remain at there existing height.

        Parameters
        ----------
        mapping: Dict
            A dict mapping node idx labels to their new heights.

        Examples:
        ---------
        tre = toytree.rtree.unitree(10)
        tre = tre.mod.set_node_heights({10: 55, 11: 60, 12: 100})
        """
        return set_node_heights(self._tree, mapping)


    def add_sister_node(
        self,
        idx: int,
        name: Optional[str]=None,
        dist: Optional[float]=None,
        parent_dist: Optional[float]=None,
        parent_name: Optional[str]=None,
        ) -> 'toytree.ToyTree':
        r"""
        Splits the branch spanning from node idx (A) to its parent (B)
        to create a new ancestral node (C) and descendant (D). The
        new nodes can be given names and dist values. By default, if
        only a dist is entered for the new sister (D) then the new
        ancestor node (C) dist value will be automated to make node
        D align at the same height as node A.

                    B                      B
                   / \                    / \
                  /   \      ---->       C   \
                 /     \                / \   \
                A       X              A   D   X

        Parameters
        ----------
        idx: int
            The focal node for wihch to insert a sister lineage.
        name: str
            Optional name for the new sister node.
        dist: float
            The dist (edge length) of the new sister node. If None
            this will be set to 1/2 of the sister's original dist.
            If parent_dist is None then the parent_dist will be set
            automatically to make the new sister node height align
            with its sister.
        parent_dist: float
            The dist (edge length) of the new ancestral node. If left
            at None then this value is automatically set to make node
            D align with A. Changing this value does not affect the
            height of node A, but does affect both nodes C and D.
            By setting parent_dist and dist both you can explicitly
            define any heights for the new nodes.
        parent_name: str
            Optional name for the new internal parent node.

        Example
        -------
        tree = toytree.rtree.imbtree(5, treeheight=1e6)

        # add a ghost lineage to the tree.
        newtree = tree.mod.add_sister_node(
            idx=3, name="ghost", parent_dist=2e5, dist=4e5,
        ).ladderize()

        # draw the new tree w/ ghost lineage introgression
        c, a, m = newtree.draw(ts='p', admixture_edges=(['r0', 'r1'], 'ghost'));
        """
        tree = self._tree.copy()
        orig_parent = tree.idx_dict[idx].up
        sister_1 = tree.idx_dict[idx]
        if dist is None:
            dist = sister_1.dist / 2.
        sister_2 = toytree.TreeNode(name=name, dist=dist)
        if parent_dist is None:
            parent_dist = orig_parent.height - dist

        # modify sister_1 and new_parent dist
        sister_1.dist = sister_1.dist - parent_dist
        new_parent = toytree.TreeNode(name=parent_name, dist=parent_dist)

        orig_parent.children.remove(sister_1)
        orig_parent.children.append(new_parent)
        sister_1.up = new_parent
        sister_2.up = new_parent
        new_parent.children = [sister_1, sister_2]
        new_parent.up = orig_parent

        tree._coords.update()
        return tree
