#!/usr/bin/env python

"""
PCM: phylogenetic comparative methods tools
"""

import itertools
import numpy as np
import pandas as pd
# from toytree.distance import get_mrca


def tree_to_vcv(tree):
    """
    Return a variance-covariance matrix representing the tree topology
    where the length of shared ancestral edges are covariance and 
    terminal edges are variance.
    """
    theight = tree.treenode.height
    vcv = np.zeros((tree.ntips,tree.ntips))
    for tip1, tip2 in itertools.combinations(range(tree.ntips), 2):
        node = tree.distance.get_mrca(tip1, tip2)
        # node = get_mrca(tree, tip1, tip2)
        vcv[tip1, tip2] = theight - node.height
        vcv[tip2, tip1] = theight - node.height
    vcv[np.diag_indices_from(vcv)] = [
        tree.idx_dict[i].dist for i in range(tree.ntips)]
    tlabels = tree.get_tip_labels()
    return pd.DataFrame(vcv, columns=tlabels, index=tlabels)

