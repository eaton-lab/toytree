#!/usr/bin/env python

"""Tree edge modification functions.

Tree edge modification functions set new 'dist' values to one or more
Nodes in a ToyTree.

Note
----
All 'edge' functions in `mod` are written so that the returned ToyTrees 
are ready to be plotted. This means they update the cached heights 
(Node._height attributes). These functions do not change the topology, 
so idx values and x positions do not need to be updated.
"""

from typing import Dict
from loguru import logger
import numpy as np

logger = logger.bind(name="toytree")


def edges_scale_to_root_height(
    tree,
    treeheight: float = 1, 
    include_stem: bool = False, 
    inplace: bool = False,
    ) -> "ToyTree":
    """Return a ToyTree with root height set.

    Returns a toytree copy with all nodes multiplied by a constant 
    so that the root node height equals the value entered for 
    treeheight. The argument include_stem=True can be used to scale 
    the tree so that the root + root.dist is equal to treeheight. 
    This effectively sets the stem height.
    """
    tree = tree if inplace else tree.copy()

    # get total tree height
    height = (
        tree.treenode.height + tree.treenode.dist if include_stem
        else tree.treenode.height)

    # get multiplier
    ratio = treeheight / height

    # scale Nodes using cached Nodes.
    for idx in range(tree.nnodes):
        tree[idx]._dist *= ratio
        tree[idx]._height *= ratio
    return tree

def edges_slider(
    tree, 
    prop=0.999, 
    seed=None, 
    inplace: bool = False,
    ) -> "ToyTree":
    """Return a ToyTree with internal Node heights jittered.

    Internal Node heights slide up or down while retaining the same
    topology as well as root and tip heights. The order of traversal
    is randomly chosen, and then Node heights are uniformly sampled
    in the interval between their parent and highest child.
    """
    tree = tree if inplace else tree.copy()    
    rng = np.random.default_rng(seed)

    # smaller value means less jitter
    assert 0 < prop < 1, "prop must be a proportion >0 and < 1."

    # randomly sample the traveral direction
    order = rng.choice(["postorder", "preorder"])

    # traverse tree sampling new heights within constrained ranges
    for node in tree.traverse(order):

        # slide internal Nodes 
        if (not node.is_root()) and (not node.is_leaf()):

            # the closest child to me
            min_child_dist = min([i.dist for i in node.children])

            # prop distance down toward child
            minh = node._height - (min_child_dist * prop)

            # prop towards parent
            maxh = node._height + (node.dist * prop)

            # node.height
            newheight = rng.uniform(minh, maxh)

            # how much lower am i?
            delta = newheight - node._height

            # edges from children to reach me
            for child in node.children:
                child._dist += delta

            # slide self to match
            node._dist -= delta
            node._height = newheight
    return tree

def edges_multiplier(tree, multiplier=0.5, seed=None, inplace: bool = False):
    """Return ToyTree w/ all Nodes multiplied by a random constant.

    This function differs from `edges_scale_to_root_height` in that the
    multiplier is randomly sampled, and in that it applies to the root
    as well as all other nodes. 

    Parameters
    ----------
    multiplier: float
        The multiplier will be sampled uniformly in (multiplier, 1/multiplier).
    """
    tree = tree if inplace else tree.copy()    
    rng = np.random.default_rng(seed)
    low, high = sorted([multiplier, 1. / multiplier])
    mult = rng.uniform(low, high)
    for idx in range(tree.nnodes):
        tree[idx]._dist = tree[idx].dist * mult
        tree[idx]._height = tree[idx]._height * mult
    return tree

def edges_extend_tips_to_align(tree, inplace: bool = False):
    """Return ToyTree with tip Nodes extended to align at height=0."""
    tree = tree if inplace else tree.copy()
    for idx in range(tree.ntips):
        tree[idx]._dist += tree[idx]._height
        tree[idx]._height = 0
    return tree

def edges_set_node_heights(tree, mapping: Dict[int,float], inplace: bool = False):
    """Return a ToyTree with one or more Node heights set explicitly.
    
    Enter a dictionary mapping node idx to heights. Node idxs that 
    are not included as keys will remain at there existing height. 

    Examples
    --------
    >>> tre = toytree.rtree.unitree(10)
    >>> tre = tre.mod.edges_set_node_heights({10: 55, 11: 60, 12: 100})
    """
    # set node heights on a new tree copy
    tree = tree if inplace else tree.copy()

    # set node height to current value for those not in hdict
    for idx in range(tree.nnodes):
        if idx not in mapping:
            mapping[idx] = tree[idx]._height

    # iterate over nodes from tips to root
    for node in tree.traverse("postorder"):        
        # shorten or elongate child stems to reach node's new height
        node._height = mapping[node.idx]
        if node.up:
            node._dist = mapping[node.up.idx] - mapping[node.idx]
            if node._dist < 0:
                logger.warning("negative edge lengths created.")
    return tree


if __name__ == "__main__":

    import toytree
    TREE = toytree.rtree.rtree(ntips=6)
    TREE = toytree.rtree.unittree(ntips=6, treeheight=100, seed=123)

    NEW_HEIGHTS = {
        10: 200,
        9: 10,
        8: 150,
        7: 130,
        6: 80,
    }

    print(edges_scale_to_root_height(TREE, 100, False, False).get_node_data())
    print(edges_slider(TREE, 0.5).get_node_data())
    print(edges_multiplier(TREE, 0.5).get_node_data())
    print(edges_extend_tips_to_align(TREE).get_node_data())        
    print(edges_set_node_heights(TREE, NEW_HEIGHTS).get_node_data())
