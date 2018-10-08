#!/usr/bin/env python

from __future__ import print_function, division, absolute_import

from .ete3mini import TreeNode
import toytree
import random  # b/c ete uses random seed.
import re

#######################################################
# Exception Classes
#######################################################
class ToytreeError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


#######################################################
# Branch modification Class
#######################################################
class TreeMod:
    """
    Return a tree with edge lengths modified according to one of 
    the jitter functions. 

    node_slider: 

    node_multiplier:

    """
    def __init__(self, ttree):
        self._ttree = ttree

    def scale_root_height(self, treeheight=1):
        """
        Returns a toytree copy with all nodes scaled so that the root 
        height equals the value entered for treeheight.
        """
        # make tree height = 1 * treeheight
        ctree = self._ttree.copy()
        _height = ctree.tree.height
        for node in ctree.tree.traverse():
            node.dist = (node.dist / _height) * treeheight
        return ctree


    def node_slider(self, seed=None):
        """
        Returns a toytree copy with node heights modified while retaining 
        the same topology but not necessarily node branching order. 
        Node heights are moved up or down uniformly between their parent 
        and highest child node heights in 'levelorder' from root to tips.
        The total tree height is retained at 1.0, only relative edge
        lengths change.
        """
        # I don't think user's should need to access prop
        prop = 0.999
        assert isinstance(prop, float), "prop must be a float"
        assert prop < 1, "prop must be a proportion >0 and < 1."
        random.seed(seed)

        ctree = self._ttree.copy()
        for node in ctree.tree.traverse():

            ## slide internal nodes 
            if node.up and node.children:

                ## get min and max slides
                minjit = max([i.dist for i in node.children]) * prop
                maxjit = (node.up.height * prop) - node.height
                newheight = random.uniform(-minjit, maxjit)

                ## slide children
                for child in node.children:
                    child.dist += newheight

                ## slide self to match
                node.dist -= newheight
        return ctree


    def node_multiplier(self, multiplier=0.5, seed=None):
        """
        Returns a toytree copy with all nodes multiplied by a constant 
        sampled uniformly between (multiplier, 1/multiplier).
        """
        random.seed(seed)
        ctree = self._ttree.copy()
        low, high = sorted([multiplier, 1. / multiplier])
        mult = random.uniform(low, high)
        for node in ctree.tree.traverse():
            node.dist = node.dist * mult
        return ctree



#######################################################
# Random Tree generation Class
#######################################################
class RandomTree:

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
            toytree.tree().tree.add_child(name=str(i)) for i in range(ntips)]
        while len(tips) > 1:
            rtree = toytree.tree()
            tip1 = tips.pop(random.choice(range(len(tips))))
            tip2 = tips.pop(random.choice(range(len(tips))))
            kingman = (4. * ne) / float(ntips * (ntips - 1))
            dist = random.expovariate(1. / kingman)
            rtree.tree.add_child(tip1, dist=tip2.height + dist)
            rtree.tree.add_child(tip2, dist=tip1.height + dist)
            tips.append(rtree.tree)

        # build new tree from the newick string
        self = toytree.tree(tips[0].write())    
        self.tree.ladderize()

        # make tree edges in units of 2N (then N doesn't matter!)
        if coalunits:
            for node in self.tree.traverse():
                node.dist /= (2. * ne)

        ## ensure tips are at zero
        for node in self.tree.traverse():
            if node.is_leaf():
                node.dist += node.height

        # set tipnames, decompose will fill internals
        ntip = 0
        for tip in self.get_tip_labels():
            node = self.tree.search_nodes(name=tip)[0]
            node.name = "r{}".format(ntip)
            ntip += 1

        # decompose fills in internal node names and idx
        self._coords.update()
        return self


    @staticmethod
    def unittree(ntips, treeheight=1.0, seed=None):
        """
        Function to return a random tree w/ N tips using the ete function
        'populate()'. Branch lengths can be added after the tree is
        generated by modifying its features, or you can use one the preset
        modes for generating divergence times by setting nodes to one of
        ['coalescent', 'yule', 'bd'], and adding params in paramsdict.
        Examples below.

        Parameters
        -----------
        ntips (int):
            The number of tips in the randomly generated tree

        treeheight(float):
            Scale tree height (all edges) so that root is at this height.
        """

        # seed generator
        random.seed(seed)

        # generate tree with N tips.
        tmptree = TreeNode()
        tmptree.populate(ntips)
        self = toytree.tree(newick=tmptree.write())

        # set tip names by labeling sequentially from 0
        self.tree.ladderize()
        self.tree.convert_to_ultrametric()

        # make tree height = 1 * treeheight
        _height = self.tree.height
        for node in self.tree.traverse():
            node.dist = (node.dist / _height) * treeheight

        # set tipnames, decompose will fill internals
        nidx = 0 
        for tip in self.get_tip_labels():
            node = self.tree.search_nodes(name=tip)[0]
            node.name = "r{}".format(nidx)
            nidx += 1

        # fill internal node names and idx
        self._coords.update()
        return self



#######################################################
# Other
#######################################################
def bpp2newick(bppnewick):
    "converts bpp newick format to normal newick"
    regex1 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[:]")
    regex2 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[;]")
    regex3 = re.compile(r": ")
    new = regex1.sub(":", bppnewick)
    new = regex2.sub(";", new)
    new = regex3.sub(":", new)
    return new
