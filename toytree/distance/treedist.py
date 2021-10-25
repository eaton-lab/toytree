#!/usr/env/bin python

"""
A collection of tree distance metrics.

Authors: Deren Eaton, Patrick McKenzie, Scarlet Ming-sha Au
"""

import toytree
import pandas as pd
import numpy as np
import itertools
import os

from toytree.distance.robinson_foulds import OldRobinsonFoulds
from toytree.distance.sample import Sample

# testing

# workflow goal
#def robinson_foulds(tree1, tree2, *args):
   
#    tool = RobinsonFoulds(tree1, tree2, *args)
#    tool.run()
#    return tool.data



class robinson_foulds():
    """Returns the Robinson-Foulds distance between two trees.

    Faster cleaner version of RF...

    Parameters
    ----------
    tree1: toytree.ToyTree
        A first toytree instance to compare to another tree.
    tree2: toytree.ToyTree
        A second toytree instance to compare to tree1.
    *args: 
        Additional args TBD.

    Examples
    ---------
    >>> tree1 = toytree.rtree.unittree(10, seed=123)
    >>> tree2 = toytree.rtree.unittree(10, seed=321)
    >>> toytree.distance.treedist.robinson_foulds(tree1, tree2)
    """

    # use *args to replace sampmethod, consenustree

    def __init__(self, trees, sampmethod, consensustree=None):
        # store inputs
        self.trees = toytree.core.multitree.MultiTree(trees)
        self.treelist = self.trees.treelist
        self.sampmethod = sampmethod

        # store consensus tree
        self.consensustree = consensustree
        if self.consensustree == None:
            self.consensustree = self.trees.get_consensus_tree()

        # store output
        self.getrfout = {}
        self.samporder = []
        self.data = pd.DataFrame(columns = ['trees', 'RF'])
        

    def get_rf(self):
        """
        Function to get RFs depending on user input (pairwise/random sampling of trees
        vs. compare all trees with consensus tree)
        Returns result in a dictionary, with key as tree # and value as RF value. 
        """
        if self.sampmethod == "pairwise" or self.sampmethod == "random":
            samporder = Sample(len(self.trees), self.sampmethod)
            self.samporder = samporder.sampling()

            for idx in range(len(self.trees)-1):
                ttre1 = self.treelist[(self.samporder[idx])]
                ttre2 = self.treelist[(self.samporder[idx+1])]

                rf = ttre1.treenode.robinson_foulds(ttre2.treenode)[0]
                max_rf = ttre1.treenode.robinson_foulds(ttre2.treenode)[1]
                final_rf = rf/max_rf

                self.getrfout[str(self.samporder[idx]) + ", " + str(self.samporder[idx+1])] = final_rf
        
        else:   #self.sampmethod == "consensus":
            for idx in range(len(self.trees)):
                ttre1 = self.treelist[idx]
                rf = ttre1.treenode.robinson_foulds(self.consensustree.treenode, unrooted_trees=True)[0]
                max_rf = ttre1.treenode.robinson_foulds(self.consensustree.treenode, unrooted_trees=True)[1]
                final_rf = rf/max_rf
                
                self.getrfout[str(idx) + ", consensus"] = final_rf
        
        return self.getrfout 
    
    
    def compare_rf(self):
        """
        Function to compile tree # and associated RFs into a final data frame as output with self.data
        """
        for idx in self.getrfout:
            self.data = self.data.append({'trees' : idx, 
                                              'RF' : self.getrfout[idx]},
                                              ignore_index = True)
        return self.data
    
    def run(self):
        """
        Define run function
        """
        self.get_rf()
        self.compare_rf()



class quartets():
    """
    Returns the quartet tree distance between two trees.

    Parameters
    ----------
    tree1: toytree.ToyTree
        A first toytree instance to compare to another tree.
    tree2: toytree.ToyTree
        A second toytree instance to compare to tree1.
    *args: 
        Additional args TBD.

    Examples
    ---------
    >>> tree1 = toytree.rtree.unittree(10, seed=123)
    >>> tree2 = toytree.rtree.unittree(10, seed=321)
    >>> toytree.distance.treedist.quartets(tree1, tree2)

    """
    def __init__(self, trees, sampmethod, consensustree=None):
        # store inputs
        self.trees = toytree.core.multitree.MultiTree(trees)
        self.treelist = self.trees.treelist
        self.sampmethod = sampmethod

        # get consensus tree (if given the use user's consenus tree, or else, get consensus tree from trees provided in user input)
        self.consensustree = consensustree
        if self.consensustree == None:
            self.consensustree = self.trees.get_consensus_tree()
        # append consensus tree as last in tree list
        self.trees.treelist.append(self.consensustree)
        
        # store output
        self.getquartetsout = {}
        self.samporder = []
        self.data = pd.DataFrame(columns = ['trees', 'Quartet_intersection'])
        
        
    def get_quartets(self):
        """
        Find all possible quartets for each phylogenetic tree
        from user input and store in self.getquartetsout dictionary
        with key as tree #/consensus and value as quartet set.
        """       
        # iterate over each tree in input
        for idx in range(len(self.trees)):
            ttre = self.treelist[idx]
            
            # store all quartets in this SET
            qset = set([])
    
            # get a SET with all tips in the tree
            fullset = set(ttre.get_tip_labels())
    
            # get a SET of the descendants from each internal node
            for node in ttre.idx_dict.values():   

                # skip leaf nodes
                if not node.is_leaf():
            
                    children = set(node.get_leaf_names())
                    prod = itertools.product(
                        itertools.combinations(children, 2),
                        itertools.combinations(fullset - children, 2),
                    )
                    quartets = set([tuple(itertools.chain(*i)) for i in prod])
                    qset = qset.union(quartets)

            # order tups in sets
            sorted_set = set()
            for qs in qset:
                if np.argmin(qs) > 1:
                    tup = tuple(sorted(qs[2:]) + sorted(qs[:2]))
                    sorted_set.add(tup)
                else:
                    tup = tuple(sorted(qs[:2]) + sorted(qs[2:]))
                    sorted_set.add(tup)            
            
            # if last tree, this means this is the quartet set for the consensus tree
            if idx == len(self.trees)-1:
                self.getquartetsout['consensus'] = sorted_set
                # remove consensus tree from tree list
                del self.trees.treelist[-1]
            # if not, treat quartet set as set for a normal tree that will soon be used for comparisons
            else:
                self.getquartetsout[idx] = sorted_set
        return self.getquartetsout    

        
    def compare_quartets(self):
        """
        Compare two sets of quartets generated from each pair of
        phylogenetic trees based on pairwise or random sampling order.
        Return data frame with tree # and quartet metric. 
        """
        # follow sampling order if user wants to calculate distances in pairwise/random fashion
        if self.sampmethod == "pairwise" or self.sampmethod == "random":
            # generate sampling order depending on pairwise or random user input
            # define max length as self.trees - 1 because last tree in list is consensus tree
            length = len(self.trees)

            samporder = Sample(length, self.sampmethod)
            self.samporder = samporder.sampling()
        
            # iterate over each pair of trees depending on sampling order
            for idx in range(len(self.trees)-1):      
                q0 = self.getquartetsout[self.samporder[idx]]
                q1 = self.getquartetsout[self.samporder[idx+1]]
        
                # diffs = q0.symmetric_difference(q1)
                # len(diffs)
            
                self.data = self.data.append({'trees' : str(self.samporder[idx])+ ", " + str(self.samporder[idx+1]), 
                                                  'Quartet_intersection' : len(q0.intersection(q1)) / len(q0)},
                                                 ignore_index = True)
        # compares each tree with consensus
        else:
            consensus = self.getquartetsout['consensus']
            for idx in range(len(self.trees)):
                q0 = self.getquartetsout[idx]
                self.data = self.data.append({'trees' : str(idx) + ", consensus", 
                                                  'Quartet_intersection' : len(q0.intersection(consensus)) / len(consensus)},
                                                 ignore_index = True)
        #pd.set_option("display.max_rows", None, "display.max_columns", None)
        # return data frame as output
        return self.data        
        
        
    def run(self):
        """
        Define run function
        """
        self.get_quartets()
        self.compare_quartets()
