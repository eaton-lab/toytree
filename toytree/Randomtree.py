#!/usr/bin/env python

"""
Random Tree generation Class
"""

import random
import toytree
from .utils import ToytreeError


class RandomTree(object):

    @staticmethod
    def coaltree(ntips, ne=None, seed=None):
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

        # set tipnames
        for tip in self.get_tip_labels():
            node = self.treenode.search_nodes(name=tip)[0]
            node.name = "r{}".format(node.idx)

        # decompose fills in internal node names and idx
        self._coords.update()
        return self


    @staticmethod
    def unittree(ntips, treeheight=1.0, seed=None):
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
        nidx = list(range(self.ntips))
        random.shuffle(nidx)
        for tidx, node in enumerate(self.treenode.get_leaves()):
            node.name = "r{}".format(nidx[tidx])

        for node in self.treenode.traverse():
            node.support = 100            
        # fill internal node names and idx
        self.treenode.ladderize()
        self._coords.update()
        return self


    @staticmethod
    def imbtree(ntips, treeheight=1.0):
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
        return tre


    @staticmethod
    def baltree(ntips, treeheight=1.0):
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

        # rename tips so names are in order
        idx = len(rtree) - 1
        for node in rtree.treenode.traverse("postorder"):
            if node.is_leaf():
                node.name = "r" + str(idx)
                idx -= 1

        # get toytree from newick            
        tre = toytree.tree(rtree.write(tree_format=9))
        tre = tre.mod.make_ultrametric()
        self = tre.mod.node_scale_root_height(treeheight)
        self._coords.update()
        return self        


    @staticmethod
    def rtree(ntips, treeheight=1.0, seed=None):
        """
        Randomly assigns edge lengths between U(0-1) to edges 
        and then scales total treeheight to 1.0 or entered value.
        """
        # get a unit tree
        self = toytree.rtree.unittree(ntips, treeheight, seed)      

        # randomly assign node dists
        self = self.set_node_values(
            "dist", {i: random.random() for i in range(self.nnodes)}
        )

        # rescale total height to .
        self = self.mod.node_scale_root_height(treeheight, nocopy=True)
        return self        


def return_small_clade(treenode):
    "used to produce balanced trees, returns a tip node from the smaller clade"
    node = treenode
    while 1:
        if node.children:
            c1, c2 = node.children
            node = sorted([c1, c2], key=lambda x: len(x.get_leaves()))[0]
        else:
            return node
