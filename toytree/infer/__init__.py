#!/usr/bin/env python

"""toytree inference subpackage.


"""

# methods here will be available at submodule-level (toytree.infer.[method])
from .src.upgma import *  # upgma_tree
from .src.neighbor_joining import * # neighbor_joining_tree
from .src.consensus import * # get_consensus_tree, get_consensus_features
from .src.parsimony import * # consistency_and_retention_indices

# requires sympy which is not yet in conda recipe, so for now
# you need to call the following to access the likelihood code:
# >>> from toytree.infer.src import maximum_likelihood
# >>> from toytree.infer.src.maximum_likelihood import JC69, K80, TN93, get_tree_likelihood, get_tree_likelihood_plot_gen

