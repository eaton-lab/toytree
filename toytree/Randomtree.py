#!/usr/bin/env python

"""
Random Tree generation Class
"""

import numpy as np
import random
import toytree
from .utils import ToytreeError


class RandomTree(object):


    @staticmethod
    def unittree(ntips, treeheight=1.0, random_names=False, seed=None):
        """
        Returns a random tree ultrametric topology w/ N tips and a root 
        height set to 1 or a user-entered treeheight value. Descendant 
        nodes are evenly spaced between the root and time 0.

        Parameters
        -----------
        ntips (int):
            The number of tips in the randomly generated tree

        treeheight(float):
            Scale tree height (all edges) so that root is at this height.

        seed (int):
            Random number generator seed.
        """
        # seed generator
        random.seed(seed)

        # generate tree with N tips.
        tmptree = toytree.tree().treenode  # TreeNode()
        tmptree.populate(ntips)
        self = toytree.tree(newick=tmptree.write())

        # set tip names by labeling sequentially from 0
        self = (
            self
            .ladderize()
            .mod.make_ultrametric()
            .mod.node_scale_root_height(treeheight)
        )

        # set tipnames randomly (doesn't have to match idx)
        nidx = list(range(self.ntips))[::-1]
        if random_names:
            random.shuffle(nidx)
        for tidx, node in enumerate(self.treenode.get_leaves()):
            node.name = "r{}".format(nidx[tidx])

        # set all support values to 100 default
        for node in self.treenode.traverse():
            node.support = 100

        # fill internal node names and idxs
        self.treenode.ladderize()
        self._coords.update()
        return self


    @staticmethod
    def imbtree(ntips, treeheight=1.0, random_names=False):
        """
        Return an imbalanced (comb-like) tree topology.
        """
        node = toytree.TreeNode.TreeNode()
        node.add_child(name="r0")
        node.add_child(name="r1")

        for i in range(2, ntips):
            # empty node
            cherry = toytree.TreeNode.TreeNode()
            # add new child
            cherry.add_child(name="r" + str(i))
            # add old tree
            cherry.add_child(node)
            # update rtree
            node = cherry

        # get toytree from newick            
        tre = toytree.tree(node)
        tre = tre.mod.make_ultrametric(nocopy=True)
        tre = tre.mod.node_scale_root_height(treeheight, nocopy=True)
        tre._coords.update()

        # randomize tip names
        nidx = list(range(tre.ntips))
        if random_names:
            random.shuffle(nidx)
        for idx, node in tre.idx_dict.items():
            if node.is_leaf():
                node.name = "r{}".format(nidx[idx])
        return tre


    @staticmethod
    def baltree(ntips, treeheight=1.0, random_names=False):
        """
        Returns a balanced tree topology.
        """
        # require even number of tips
        if ntips % 2:
            raise ToytreeError("balanced trees must have even number of tips.")

        # make first cherry
        rtree = toytree.tree()
        rtree.treenode.add_child(name="r0")
        rtree.treenode.add_child(name="r1")

        # add tips in a balanced way
        for i in range(2, ntips):

            # get node to split
            node = return_small_clade(rtree.treenode)

            # add two children
            node.add_child(name=node.name)
            node.add_child(name="r" + str(i))

            # rename ancestral node
            node.name = None

        # get toytree from newick            
        tre = toytree.tree(rtree)  # .write(tree_format=9))
        tre = tre.mod.make_ultrametric().mod.node_scale_root_height(treeheight)
        tre._coords.update()

        # rename tips so names are in order
        nidx = list(range(tre.ntips))
        if random_names:
            random.shuffle(nidx)
        for idx, node in tre.idx_dict.items():
            if node.is_leaf():
                node.name = "r{}".format(nidx[idx])
        return tre


    @staticmethod
    def rtree(ntips, treeheight=1.0, random_names=False, seed=None):
        """
        Randomly assigns edge lengths between U(0-1) to edges 
        and then scales total treeheight to 1.0 or entered value.
        """
        # get a unit tree
        self = toytree.rtree.unittree(ntips, treeheight, random_names, seed)

        # randomly assign node dists
        self = self.set_node_values(
            "dist", {i: random.random() for i in range(self.nnodes)}
        )

        # rescale total height to .
        self = self.mod.node_scale_root_height(treeheight, nocopy=True)
        return self


    @staticmethod
    def coaltree(ntips, ne=None, random_names=False, seed=None):
        """
        Returns a coalescent tree with ntips samples and waiting times 
        between coalescent events drawn from the kingman coalescent:
        (4N)/(k*(k-1)), where N is population size and k is sample size.
        Edge lengths on the tree are in generations.

        If no Ne argument is entered then edge lengths are returned in units
        of 2*Ne, i.e., coalescent time units. 
        """
        # seed generator
        random.seed(seed)

        # convert units
        coalunits = False
        if not ne:
            coalunits = True
            ne = 10000

        # build tree: generate N tips as separate Nodes then attach together 
        # at internal nodes drawn randomly from coalescent waiting times.
        tips = [
            toytree.tree().treenode.add_child(name=str(i)) 
            for i in range(ntips)
        ]
        while len(tips) > 1:
            rtree = toytree.tree()
            tip1 = tips.pop(random.choice(range(len(tips))))
            tip2 = tips.pop(random.choice(range(len(tips))))
            kingman = (4. * ne) / float(ntips * (ntips - 1))
            dist = random.expovariate(1. / kingman)
            rtree.treenode.add_child(tip1, dist=tip2.height + dist)
            rtree.treenode.add_child(tip2, dist=tip1.height + dist)
            tips.append(rtree.treenode)

        # build new tree from the newick string
        self = toytree.tree(tips[0].write())    
        self.treenode.ladderize()

        # make tree edges in units of 2N (then N doesn't matter!)
        if coalunits:
            for node in self.treenode.traverse():
                node.dist /= (2. * ne)

        # ensure tips are at zero (they sometime vary just slightly)
        for node in self.treenode.traverse():
            if node.is_leaf():
                node.dist += node.height

        # set tipnames to r{idx}
        nidx = list(range(self.ntips))
        if random_names:
            random.shuffle(nidx)
        for idx, node in self.idx_dict.items():
            if node.is_leaf():
                node.name = "r{}".format(nidx[idx])

        # decompose fills in internal node names and idx
        self._coords.update()
        return self


    @staticmethod
    def bdtree(ntips, b=1, d=0, maxtime=None, random_names=False, seed=None, verbose=False):
        """
        Generate a classic birth/death tree.

        Parameters
        -----------
        ntips (int):
            Number of tips to generate for 'taxa' stopping criterion.

        b (float):
            Birth rate per time unit

        d (float):
            Death rate per time unit (d=0 produces Yule trees)

        maxtime (None or int):
            if maxtime is int then stopping criterion is time and the ntips
            argument is ignored. Simulations are conditional on tips existing
            at maxtime, and will reset until a tree reaches maxtime.

        seed (int):
            Random number generator seed.

        verbose (bool):
            Print some useful information
        """
        assert b <= 1, "birth rate should be between 0-1"
        assert d <= 1, "death rate should be between 0-1"

        # set random seed
        if seed:
            np.random.seed(seed)

        # start from random tree (idxs will be re-assigned at end)
        tre = toytree.tree()
        tre.treenode.idx = 0
        gidx = 1

        # counters for extinctions, total events, and time
        resets = 0
        ext = 0
        evnts = 0
        t = 0

        # continue until stop var
        while 1:

            # get current tips
            tips = tre.treenode.get_leaves()

            # sample time until next event, increment t and evnts
            dt = np.random.exponential(1 / (len(tips) * (b + d)))
            t = t + dt
            evnts += 1

            # sample a [0-1] to choose birth or death and sample a tip node
            r = np.random.sample()
            sp = np.random.choice(tips)

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
                    tre = toytree.tree()
                    tre.treenode.idx = 0
                    gidx = 1
                    ext = 0
                    evnts = 0
                    t = 0

                # connect parent to sp' children
                else:
                    # if parent is None then reset
                    if sp.up is None:
                        tre = toytree.tree()
                        tre.treenode.idx = 0
                        gidx = 1
                        ext = 0
                        evnts = 0
                        t = 0

                    # if parent is root then sister is new root
                    elif sp.up is tre.treenode:
                        tre = [i for i in sp.up.children if i != sp][0]
                        tre = toytree.tree(tre)
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
            tips = tre.treenode.get_leaves()
            for x in tips:
                x.dist += dt

            # time stopping criterion... not quite working right.
            if maxtime:
                if t >= maxtime:
                    break

            # ntips stopping criterion.
            else:
                if len(tips) >= ntips:
                    break

        # report status
        if verbose:
            fill = (evnts - ext, ext, evnts / (evnts - ext), resets)
            print("b:\t{}\nd:\t{}\nb/d:\t{:.2f}\nreset:\t{}".format(*fill))

        # update coords and return
        tre.treenode.ladderize()
        tre._coords.update()

        # rename tips so names are in order else random
        nidx = list(range(tre.ntips))
        if random_names:
            random.shuffle(nidx)
        for idx, node in tre.idx_dict.items():
            if node.is_leaf():
                node.name = "r{}".format(nidx[idx])
        return tre


def _prune(tre, verbose=False):
    """
    Helper function for recursively pruning extinct branches in bd trees.
    Dynamic func!
    """
    ttree = tre.copy()
    tips = ttree.treenode.get_leaves()

    if np.any(np.array([x.height for x in tips]) > 0):
        for t in tips:
            if not np.isclose(t.height, 0):
                if verbose: 
                    print("Removing node/height {}/{}".format(t.name, t.height))
                t.delete(prevent_nondicotomic=False)
                ttree = _prune(ttree)
    return ttree


def return_small_clade(treenode):
    "used to produce balanced trees, returns a tip node from the smaller clade"
    node = treenode
    while 1:
        if node.children:
            c1, c2 = node.children
            node = sorted([c1, c2], key=lambda x: len(x.get_leaves()))[0]
        else:
            return node
