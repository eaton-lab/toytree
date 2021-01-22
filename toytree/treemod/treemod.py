#!/usr/bin/env python

"""
Tree modification functions.

TODO: 
    - figure out how to make API access from tree
    - convert to all numpy random.
"""

import numpy as np


# limit API view
__all__ = [
    "node_scale_root_height",
    "node_slider",
    "node_multiplier",
    "make_ultrametric",
    "set_node_heights",
]



def node_scale_root_height(tre, treeheight=1, include_stem=False, nocopy=False):
    """
    Returns a toytree copy with all nodes multiplied by a constant 
    so that the root node height equals the value entered for 
    treeheight. The argument include_stem=True can be used to scale 
    the tree so that the root + root.dist is equal to treeheight. 
    This effectively sets the stem height.
    """
    if not nocopy:
        tre = tre.copy()

    # get total tree height
    if include_stem:
        height = tre.treenode.height + tre.treenode.dist
    else:
        height = tre.treenode.height

    # scale internal nodes 
    if len(tre) == 1:
        tre.treenode.dist = treeheight
    else:
        for node in tre.treenode.traverse():
            node.dist = (node.dist / height) * treeheight

    # update idx and coordinates
    tre._coords.update()
    return tre



def node_slider(tre, prop=0.999, seed=None):
    """
    Returns a toytree copy with node heights modified while retaining 
    the same topology but not necessarily node branching order. 
    Node heights are moved up or down uniformly between their parent 
    and highest child node heights in 'levelorder' from root to tips.
    The total tree height is retained at 1.0, only relative edge
    lengths change.
    """
    rng = np.random.default_rng(seed)

    # smaller value means less jitter
    assert isinstance(prop, float), "prop must be a float"
    assert prop < 1, "prop must be a proportion >0 and < 1."

    # make copy and iter nodes from root to tips
    tre = tre.copy()
    for node in tre.treenode.traverse():

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
            newheight = rng.uniform(node.height - minjit, node.height + maxjit)

            # how much lower am i?
            delta = newheight - node.height

            # edges from children to reach me
            for child in node.children:
                child.dist += delta

            # slide self to match
            node.dist -= delta

    # update new coords
    tre._coords.update()
    return tre



def node_multiplier(tre, multiplier=0.5, seed=None):
    """
    Returns a toytree copy with all nodes multiplied by a constant 
    sampled uniformly between (multiplier, 1/multiplier).
    """
    rng = np.random.default_rng(seed)
    tre = tre.copy()
    low, high = sorted([multiplier, 1. / multiplier])
    mult = rng.uniform(low, high)
    for node in tre.treenode.traverse():
        node.dist = node.dist * mult
    tre._coords.update()
    return tre



def make_ultrametric(tre, strategy=1, nocopy=False):
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
    if not nocopy:
        tre = tre.copy()

    if strategy == 1:
        for node in tre.treenode.traverse():
            if node.is_leaf():
                node.dist += node.height
    else:
        raise NotImplementedError(
            "Strategy {} not yet implemented. Seeking developers."
            .format(strategy))
    return tre



def set_node_heights(tre, hdict):
    """
    Enter a dictionary mapping node idx to heights. Nodes that 
    are not included as keys will remain at there existing height.

    tre = toytree.rtree.unitree(10)
    tre = tre.mod.set_node_heights({10: 55, 11: 60, 12: 100})
    """
    # set node heights on a new tree copy
    ntre = tre.copy()

    # set node height to current value for those not in hdict
    for nidx in tre.idx_dict:
        if nidx not in hdict:
            hdict[nidx] = tre.idx_dict[nidx].height

    # iterate over nodes from tips to root
    for node in ntre.treenode.traverse("postorder"):
            
        # shorten or elongate child stems to reach node's new height
        for child in node.children:
            child.dist = hdict[node.idx] - hdict[child.idx] 
    return ntre



# def speciate(self, idx, name=None, dist_prop=0.5):
#     """
#     Split an edge to create a new tip in the tree as in a
#     speciation event.
#     """
#     # make a copy of the toytree
#     nself = self.copy()

#     # get Treenodes of selected node and parent 
#     ndict = nself.get_feature_dict('idx')
#     node = ndict[idx]
#     parent = node.up

#     # get new node species name
#     if not name:
#         if node.is_leaf():
#             name = node.name + ".sis"
#         else:
#             names = nself.get_tip_labels(idx=idx)
#             name = "{}.sis".format("_".join(names))

#     # create new speciation node between them at dist_prop dist.
#     newnode = parent.add_child(
#         name=parent.name + ".spp",
#         dist=node.dist * dist_prop
#     )

#     # connect original node to speciation node.
#     node.up = newnode
#     node.dist = node.dist - newnode.dist
#     newnode.add_child(node)

#     # drop original node from original parent child list
#     parent.children.remove(node)

#     # add new tip node (new sister) and set same dist as onode
#     newnode.add_child(
#         name=name,
#         dist=node.up.height,
#     )

#     # update toytree coordinates
#     nself._coords.update()
#     return nself     




if __name__ == "__main__":


    import toytree
    ttre = toytree.rtree.unittree(ntips=6, treeheight=100, seed=123)

    new_heights = {
        10: 200,
        9: 10,
        8: 150,
        7: 130,
        6: 20,
    }

    new_tre = set_node_heights(ttre, new_heights)
    print(ttre.get_feature_dict("idx", "height"))
    print(new_tre.get_feature_dict("idx", "height"))    
