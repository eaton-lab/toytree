#!/usr/bin/env python

"""
Random Tree generation Classes. Uses numpy RNG.
"""

from typing import Optional
import numpy as np
from loguru import logger
from toytree.core.tree import ToyTree
from toytree.core.treenode import TreeNode
from toytree.utils.exceptions import ToytreeError


# limit the API view
__all__ = [
    "rtree", 
    "unittree",
    "imbtree", 
    "baltree",
    "bdtree",
    # "coaltree",
]


def rtree(ntips:int, seed:Optional[int]=None):
    """
    Returns a random topology (fastest method). Default values are
    set on node support (100) and dist (1.0) attributes. To set 
    more specific dist (edge lengths) either use treemod functions
    on the resulting tree, or see the other random tree functions.
    """
    # seed generator
    rng = np.random.default_rng(seed)

    # generate random topology with N tips.
    root = TreeNode()
    current_tips = [root]

    # add children n-1 times
    for _ in range(ntips - 1):
        tip = rng.choice(current_tips)
        current_tips.remove(tip)
        child0 = tip.add_child()
        child1 = tip.add_child()
        current_tips.extend([child0, child1])

    # will ladderize the tree and assign names and idxs
    tree = ToyTree(root)
    for nidx in range(tree.ntips):
        tree.idx_dict[nidx].name = f"r{tree.idx_dict[nidx].name}"
    return tree


def unittree(ntips, treeheight=1.0, random_names=False, seed=None):
    """
    Returns a random ultrametric topology w/ N tips and all internal
    edge lengths set to 1.0 (terminal edge lengths extend to make the
    tree ultrametric). The total tree root height set to 1 or a 
    user-entered treeheight value. 

    Parameters
    -----------
    ntips (int):
        The number of tips in the randomly generated tree
    treeheight(float):
        Scale tree height (all edges) so that root is at this height.
    random_names (bool):
        If True then numerics in names do not align with the tip order.
    seed (int):
        Random number generator seed.
    """
    # seed generator
    rng = np.random.default_rng(seed)

    # generate random topology with N tips.
    tre = rtree(ntips, seed=rng.integers(0, 1e9))

    # ladderize, extend terminal edges to align, scale total height
    tre = (tre
        .mod.make_ultrametric(nocopy=True)
        .mod.node_scale_root_height(treeheight, nocopy=True)
    )

    # randomize names
    nums = range(tre.ntips)
    if random_names:
        nums = rng.choice(nums, size=len(nums), replace=False)
    for nidx in range(tre.ntips):
        tre.idx_dict[nidx].name = "r{}".format(nums[nidx])
    return tre


def imbtree(ntips, treeheight=1.0, random_names=False, seed=None):
    """
    Return an imbalanced (comb-like) tree topology.
    """
    # generate random topology with N tips.
    root = TreeNode()
    tip = root

    # add children n-1 times
    for _ in range(ntips - 1):
        tip.add_child()
        child1 = tip.add_child()
        tip = child1

    # will ladderize the tree and assign names and idxs
    root.ladderize()
    tre = (ToyTree(root)
        .mod.make_ultrametric(nocopy=True)
        .mod.node_scale_root_height(treeheight, nocopy=True)
    )

    # randomize names
    nums = range(tre.ntips)
    if random_names:
        rng = np.random.default_rng(seed)
        nums = rng.choice(nums, size=len(nums), replace=False)
    for nidx in range(tre.ntips):
        tre.idx_dict[nidx].name = "r{}".format(nums[nidx])
    return tre


def baltree(ntips, treeheight=1.0, random_names=False, seed=None):
    """
    Returns a balanced tree topology.
    """
    # require even number of tips
    if ntips % 2:
        raise ToytreeError("balanced trees must have even number of tips.")

    # generate random topology with N tips.
    root = TreeNode()

    # add children n-1 times
    for _ in range(ntips - 1):
        node = _return_small_clade(root)
        node.add_child()
        node.add_child()        

    # will ladderize the tree and assign names and idxs
    root.ladderize()
    tre = (
        ToyTree(root)
        .mod.make_ultrametric(nocopy=True)
        .mod.node_scale_root_height(treeheight, nocopy=True)
    )

    # randomize names
    nums = range(tre.ntips)
    if random_names:
        rng = np.random.default_rng(seed)
        nums = rng.choice(nums, size=len(nums), replace=False)
    for nidx in range(tre.ntips):
        tre.idx_dict[nidx].name = "r{}".format(nums[nidx])
    return tre


    # # add tips in a balanced way
    # for i in range(2, ntips):

    #     # get node to split
    #     node = _return_small_clade(rtree.treenode)

    #     # add two children
    #     node.add_child(name=node.name)
    #     node.add_child(name="r" + str(i))

    #     # rename ancestral node
    #     node.name = None

    # # get toytree from newick            
    # tre = toytree.tree(rtree)  # .write(tree_format=9))
    # tre = tre.mod.make_ultrametric().mod.node_scale_root_height(treeheight)
    # tre._coords.update()

    # # rename tips so names are in order
    # nidx = list(range(tre.ntips))
    # if random_names:
    #     random.shuffle(nidx)
    # for idx, node in tre.idx_dict.items():
    #     if node.is_leaf():
    #         node.name = "r{}".format(nidx[idx])
    # return tre


def bdtree(
    ntips=10,
    time=4,
    b=1,
    d=0,
    stop="taxa",
    seed=None,
    retain_extinct=False,
    random_names=False,
    verbose=False,
    ):
    """
    Generate a classic birth/death tree.

    Parameters
    -----------
    ntips (int):
        Number of tips to generate for 'taxa' stopping criterion.
    time (float):
        Amount of time to simulate for 'time' stopping criterion.
    b (float):
        Birth rate per time unit
    d (float):
        Death rate per time unit (d=0 produces Yule trees)
    stop (str):
        Stopping critereon. Valid values are only 'taxa' or 'time'.
    seed (int):
        Random number generator seed.
    retain_extinct (bool):
        (Unimplemented) Whether to retain internal nodes leading to extinct tips.
    random_names (bool):
        Whether to randomize tip names or name them in order.
    verbose (bool):
        Print some useful information
    """
    # require an appropriate option for stopping
    if stop not in ["taxa", "time"]:
        raise ToytreeError("stop must be either 'taxa' or 'time'")

    # random generator
    rng = np.random.default_rng(seed)

    taxa_stop = ntips
    time_stop = time

    # start from random tree (idxs will be re-assigned at end)
    tre = TreeNode()
    tre.idx = 0
    gidx = 1

    # counters for extinctions, total events, and time
    resets = 0
    ext = 0
    evnts = 0
    t = 0

    # continue until stop var
    while 1:

        # get current tips
        tips = tre.get_leaves()

        # sample time until next event, increment t and evnts
        dt = rng.exponential(1 / (len(tips) * (b + d)))
        t = t + dt
        evnts += 1

        # sample a [0-1] to choose birth or death and sample a tip node
        r = rng.random()
        sp = rng.choice(tips)

        # event is a birth
        if (r <= b / (b + d)):
            c1 = sp.add_child(name=str(t) + "-1", dist=0)
            c1.add_feature("tdiv", t)
            c1.idx = gidx
            gidx += 1

            c2 = sp.add_child(name=str(t) + "-2", dist=0)
            c2.add_feature("tdiv", t)
            c2.idx = gidx
            gidx += 1

        # else event is extinction
        else:
            # get parent node
            parent = sp.up

            # if no parent then reset to empty tree
            if parent is None:
                resets += 1
                tre = TreeNode()
                tre.idx = 0
                gidx = 1
                ext = 0
                evnts = 0
                t = 0

            # connect parent to sp' children
            else:
                # if parent is None then reset
                if sp.up is None:
                    tre = TreeNode()
                    tre.idx = 0
                    gidx = 1
                    ext = 0
                    evnts = 0
                    t = 0

                # if parent is root then sister is new root
                elif sp.up is tre:
                    tre = [i for i in sp.up.children if i != sp][0]
                    tre = TreeNode()
                    tre.up = None

                # if parent is a non-root node then connect sister to up.up
                else:
                    # get sister
                    sister = [i for i in sp.up.children if i != sp][0]

                    # connect sister to grandparent
                    sister.up = sp.up.up

                    # drop parent from grandparent
                    sp.up.up.children.remove(sp.up)

                    # add sister to grandparent children
                    sp.up.up.children.append(sister)

                    # extend sisters dist to reach grandparent
                    sister.dist += sp.up.dist

                ext += 1

        # update branch lengths so all tips end at time=present
        tips = tre.get_leaves()
        for x in tips:
            x.dist += dt

        # check stopping criterion
        if stop == "taxa":
            if len(tips) >= taxa_stop:
                break
        else:
            if t >= time_stop:
                break

    # report status
    if verbose:
        print("\n"
            f"b:\t{evnts - ext}\n"
            f"d:\t{ext}\n"
            f"b/d:\t{evnts / (evnts - ext)}\n"
            f"resets:\t{resets}")

    # update coords and return
    tre.ladderize()
    tre = ToyTree(tre)

    # rename tips so names are in order else random
    nidx = list(range(tre.ntips))
    if random_names:
        rng.shuffle(nidx)
    for idx, node in tre.idx_dict.items():
        if node.is_leaf():
            node.name = "r{}".format(nidx[idx])
    return tre




# def coaltree(ntips, Ne, random_names=False, seed=None):
#     """
#     Returns a coalescent tree with ntips samples and waiting times 
#     between coalescent events drawn from the kingman coalescent:
#     (4N)/(k*(k-1)), where N is effective population size (ne) and 
#     k is sample size (ntips). Edge lengths on the tree are in 
#     generations.
#     """
#     rng = np.random.default_rng(seed)

#     # convert units
#     coalunits = False
#     if not ne:
#         coalunits = True
#         ne = 10000

#     # build tree: generate N tips as separate Nodes then attach together 
#     # at internal nodes drawn randomly from coalescent waiting times.
#     tips = [
#         toytree.tree().treenode.add_child(name=str(i)) 
#         for i in range(ntips)
#     ]
#     while len(tips) > 1:
#         rtree = toytree.tree()
#         tip1 = tips.pop(random.choice(range(len(tips))))
#         tip2 = tips.pop(random.choice(range(len(tips))))
#         kingman = (4. * ne) / float(ntips * (ntips - 1))
#         dist = random.expovariate(1. / kingman)
#         rtree.treenode.add_child(tip1, dist=tip2.height + dist)
#         rtree.treenode.add_child(tip2, dist=tip1.height + dist)
#         tips.append(rtree.treenode)

#     # build new tree from the newick string
#     self = toytree.tree(tips[0].write())    
#     self.treenode.ladderize()

#     # make tree edges in units of 2N (then N doesn't matter!)
#     if coalunits:
#         for node in self.treenode.traverse():
#             node.dist /= (2. * ne)

#     # ensure tips are at zero (they sometime vary just slightly)
#     for node in self.treenode.traverse():
#         if node.is_leaf():
#             node.dist += node.height

#     # set tipnames to r{idx}
#     nidx = list(range(self.ntips))
#     if random_names:
#         random.shuffle(nidx)
#     for idx, node in self.idx_dict.items():
#         if node.is_leaf():
#             node.name = "r{}".format(nidx[idx])

#     # decompose fills in internal node names and idx
#     self._coords.update()
#     return self



def _prune(tre):
    """
    Helper function for recursively pruning extinct branches in bd trees.
    Dynamic func!
    """
    ttree = tre.copy()
    tips = ttree.treenode.get_leaves()

    if np.any(np.array([x.height for x in tips]) > 0):
        for tip in tips:
            if not np.isclose(tip.height, 0):
                logger.debug(
                    f"Removing node/height {tip.name}/{tip.height}")
                tip.delete(prevent_nondicotomic=False)
                ttree = _prune(ttree)
    return ttree


def _return_small_clade(treenode):
    """
    used to produce balanced trees, returns a tip node from the 
    smaller clade
    """
    node = treenode
    while 1:
        if node.children:
            child1, child2 = node.children
            node = sorted([child1, child2], key=len)[0]
        else:
            return node


if __name__ == "__main__":

    import toytree
    
    sim_trees = [
        toytree.rtree.rtree(10),
        toytree.rtree.baltree(10),
        toytree.rtree.imbtree(10),
        toytree.rtree.bdtree(10),
        toytree.rtree.unittree(10),
    ]
    print(sim_trees)