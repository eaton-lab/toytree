#!/usr/bin/env python

"""Phylogenetic comparative methods (pcm) subpackage.

All `pcm` source code is located in `toytree.pcm.src`, with user-facing 
functions exposed in the `api` and `tree_api` submodules. In this 
way, all functions that a user is meant to interact with can be 
accessed from top-level locations at either :mod:`toytree.pcm` 
(package-level usage) or the `.pcm` attribute of :class:`ToyTree`
instances (instance-level usage).

Package level API usage
>>> tree = toytree.rtree.unittree(ntips=10, treeheight=100, seed=123)   
>>> toytree.pcm.simulate_discrete_markov_data(tree, 3, "ER")

Instance level API usage
>>> tree = toytree.rtree.unittree(ntips=10, treeheight=100, seed=123)
>>> tree.pcm.simulate_discrete_markov_data(nstates=3, "ER")

Note
----
This package may be split into more subdivided packages in the future,
as it grows, such as `toytree.pcm.markov`, `toytree.pcm.phylocom`.
"""

# import the tree-api: tree.pcm.functions
# from .src.api_tree import PhyloCompAPI

# import the package-api functions: tree.pcm.functions
from toytree.pcm.src.vcv import *
from toytree.pcm.src.diversification.diversification import *
from toytree.pcm.src.diversification.red import *
from toytree.pcm.src.traits.discrete_markov_model_sim import *
from toytree.pcm.src.traits.continuous_bm_sim import *
from toytree.pcm.src.traits.phylosignal_k import *

# from toytree.pcm.src.phylocom import simulate_community_data