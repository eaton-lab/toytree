#!/usr/bin/env python

"""Dist metrics for collections of trees.

Can return values for random samples of trees or all pairwise.
"""

import toytree
import numpy as np
import pandas as pd


class Sample:
    def __init__(self, ntrees, method):
        # store input
        self.ntrees = ntrees
        self.method = method

        # store output
        self.pairwisesamplingout = np.zeros((self.ntrees, 1), dtype=int)
        self.randomsamplingout = np.zeros((self.ntrees, 1), dtype=int)
    
    def sampling(self):
        """
        Generate pairwise order/pairings to calculate phylogenetic tree distances 
        (ex. 10 trees provided, compare tree 1 & 2, compare 2 & 3 etc.)
    
        OR Generate random order/pairings to calculate phylogenetic tree distances 
        (ex. 10 trees provided, compare tree 1 & 5, compare 5 & 6 etc.)

        Consensus option is for users to calculate distance metrics between each tree
        relative to the consensus tree
        """
        if self.method == "pairwise":
            self.pairwisesamplingout = np.arange(start=0, stop=self.ntrees, step=1)
            return self.pairwisesamplingout

        if self.method == "random":
            self.randomsamplingout = np.random.choice(self.ntrees, size=self.ntrees, replace=False)
            return self.randomsamplingout

        if self.method == "consensus":
            return self.method


if __name__ == "__main__":
    pass