#!/usr/bin/env python

"""toytree inference subpackage.


"""

from toytree.infer.src.upgma import infer_upgma_tree
from toytree.infer.src.neighbor_joining import infer_neighbor_joining_tree
from toytree.infer.src.consensus import get_consensus_tree, get_consensus_features

# requires sympy which is not yet in conda recipe, so for now
# you need to call the following to access the likelihood code:
# >>> from toytree.infer.src import maximum_likelihood
# >>> from toytree.infer.src.maximum_likelihood import JC69, K80, TN93, get_tree_likelihood, get_tree_likelihood_plot_gen

