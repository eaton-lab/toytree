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


class robinson_foulds():
    """Returns the Robinson-Foulds distance between two trees.

    Faster cleaner version of RF...

    Parameters
    ----------
    trees: list of toytree.ToyTrees
        List of toytrees which will be compared to one another.
    sampmethod: pairwise, random, consensus
        Indicates how trees should be compared
        Pairwise refers to comparing trees in sequential order
        Random refers to comparing trees in a random order
        Consensus refers to comparing each tree to the consensus tree
    consensustree: toytree.Toytree
        Provide a consensus tree if user wants to compute distances between
        each tree and the consensus tree. If no consensus tree is provided,
        default is to create a consensus tree from the given inputted list of trees.
    *args: 
        Additional args TBD.

    Examples
    ---------
    >>> tree1 = toytree.rtree.unittree(10, seed=123)
    >>> tree2 = toytree.rtree.unittree(10, seed=321)
    >>> trees = [tree1, tree2]
    >>> toytree.distance.treedist.robinson_foulds(trees, "pairwise")
    """

    def __init__(self, trees, sampmethod, consensustree=None):
        # store inputs
        self.trees = toytree.core.multitree.MultiTree(trees)
        self.treelist = self.trees.treelist
        self.sampmethod = sampmethod

        # store consensus tree
        self.consensustree = consensustree
        if self.consensustree == None:
            self.consensustree = self.trees.get_consensus_tree() 
        # append consensus tree as last in tree list
        self.trees.treelist.append(self.consensustree)

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
        for idx in range(len(self.trees)):
            ttre = self.treelist[idx]
            
            
            # PART 1: count number of internal edges
            names = ttre.get_tip_labels()
            
            # create dictionary mapping numbers to tip labels
            namedict = dict(enumerate(names))
            # store final number of internal edges
            num_of_internal_edges = 0

            # get all edges in terms of their associated nodes
            for edge in ttre.get_edges():
            # check if second value of edge (associated node that is further down the tree) is in dictionary keys
                if edge[1] not in list(namedict.keys()):
                # number of internal edges
                    num_of_internal_edges += 1
                    
                    
            # PART 2: count number of internal partitions
            # create dictionary mapping tip labels to names
            ndict = {j: i for i, j in enumerate(names)}
            
            # save possible internal partitions in set
            final_partitions = set()
            # use binary notation to record possible partitions
            for node in ttre.treenode.traverse('preorder'):
                partition = np.zeros(len(ttre), dtype=float)
                for child in node.iter_leaf_names():
                    partition[ndict[child]] = True
                
                    # account for inverse partition duplicates (later check if inverse partition is already in set)
                    partition_inverse = np.invert(partition.astype(dtype=bool))
                    partition_inverse = partition_inverse.astype(dtype=float)

                    # prefer partition with more leading zeros
                    partition_and_inverse = set()
                    partition_and_inverse.add(tuple(partition))
                    partition_and_inverse.add(tuple(partition_inverse))
                    preferred_partition = sorted(partition_and_inverse)[0]

                # do not add to set if breaking off end tips or partition includes all the tips
                if sum(partition) == 1 or sum(partition) == ttre.ntips:
                    pass
                # do not add to set if preferred partition is already in set
                elif tuple(preferred_partition) in final_partitions:
                    pass
                else: 
                    final_partitions.add(tuple(preferred_partition))
                        
            # save RF data for each tree
            # if last tree, this means this is the RF set for the consensus tree
            if idx == len(self.trees)-1:
                self.getrfout['consensus'] = num_of_internal_edges, final_partitions
                # remove consensus tree from tree list
                del self.trees.treelist[-1]
            # if not, treat RF set as set for a normal tree that will soon be used for comparisons
            else:
                self.getrfout[idx] = num_of_internal_edges, final_partitions

            
    def compare_rf(self):
        """
        Function to compile tree # and associated RFs into a final data frame as output with self.data
        """
        # follow sampling order if user wants to calculate distances in pairwise/random fashion
        if self.sampmethod == "pairwise" or self.sampmethod == "random":
            # generate sampling order depending on pairwise or random user input
            length = len(self.trees)

            samporder = Sample(length, self.sampmethod)
            self.samporder = samporder.sampling()
        
            # iterate over each pair of trees depending on sampling order
            for idx in range(len(self.trees)-1):      
                t0_ninternaledges = self.getrfout[self.samporder[idx]][0]
                t1_ninternaledges = self.getrfout[self.samporder[idx+1]][0]
                t0_partitions = self.getrfout[self.samporder[idx]][1]
                t1_partitions = self.getrfout[self.samporder[idx+1]][1]
                t0_t1_shared_partitions = len(t0_partitions.intersection(t1_partitions))
                
                rf = t0_ninternaledges + t1_ninternaledges - 2*(t0_t1_shared_partitions)
                max_rf = t0_ninternaledges + t1_ninternaledges
            
                self.data = self.data.append({'trees' : str(self.samporder[idx])+ ", " + str(self.samporder[idx+1]), 
                                              'RF' : rf,
                                              'max_RF': max_rf,
                                              'normalized_rf': rf/max_rf},
                                              ignore_index = True)
        # compares each tree with consensus
        else:
            consensus_ninternaledges = self.getrfout['consensus'][0]
            consensus_partitions = self.getrfout['consensus'][1]
            
            for idx in range(len(self.trees)):
                t0_ninternaledges = self.getrfout[idx][0]
                t0_partitions = self.getrfout[idx][1]
                con_t0_shared_partitions = len(consensus_partitions.intersection(t0_partitions))
                
                rf = consensus_ninternaledges + t0_ninternaledges - 2*(con_t0_shared_partitions)
                max_rf = consensus_ninternaledges + t0_ninternaledges
                
                self.data = self.data.append({'trees' : str(idx) + ", consensus", 
                                              'RF' : rf,
                                              'max_RF': max_rf,
                                              'normalized_rf': rf/max_rf},
                                              ignore_index = True)
        # return data frame as output
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
            # consensus tree already removed so use len(self.trees) is accurate
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
