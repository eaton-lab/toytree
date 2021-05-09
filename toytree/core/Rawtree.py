#!/usr/bin/env python

"""
Fastest minimal tree for simple non-drawing operations.
"""

from copy import copy
from toytree.io.TreeParser import FastTreeParser
from toytree.io.TreeWriter import NewickWriter



class RawTree():
    """
    A faster tree parsing function that returns a RawTree object, which
    has the functionality for traversing TreeNodes, or extracting 
    simple info, but not for plotting. Used internally in many
    statistical tools for faster calculations over large sets of input
    trees.
    """
    def __init__(self, newick, tree_format=0):
        self.treenode = FastTreeParser(newick, tree_format).treenode
        self.ntips = len(self.treenode)
        self.nnodes = (len(self.treenode) * 2) - 1
        self.idx_dict = {}
        self.update_idxs()


    def write(self, tree_format=5, dist_formatter=None):
        """
        Return newick string
        """
        # get newick string
        writer = NewickWriter(
            treenode=self.treenode,
            tree_format=tree_format,
            dist_formatter=dist_formatter,
        )
        newick = writer.write_newick()
        return newick


    def update_idxs(self):
        """
        Set root idx highest, tip idxs lowest ordered as ladderized
        """
        # n internal nodes - 1 
        idx = self.nnodes - 1

        # from root to tips label idx
        for node in self.treenode.traverse("levelorder"):
            if not node.is_leaf():
                node.add_feature("idx", idx)
                self.idx_dict[idx] = node

                if not node.name:
                    node.name = str(idx)
                idx -= 1

        # external nodes: lowest numbers are for tips (0-N)
        for node in self.treenode.iter_leaves():
            node.add_feature("idx", idx)
            self.idx_dict[idx] = node            
            if not node.name:
                node.name = str(idx)
            idx -= 1


    def copy(self):
        """
        return a shallow copy
        """
        return copy(self)
