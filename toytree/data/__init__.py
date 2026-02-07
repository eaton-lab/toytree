#!/usr/bin/env python

"""Example datasets for testing and demonstration.


toytree.data.newick
toytree.data.newick_multitree
toytree.data.nexus
toytree.data.nexus_multitree
toytree.data.nhx
toytree.data.nhx_mb
toytree.data.nhx_beast
toytree.data.distance_matrix
toytree.data.sequence_alignment
"""

# methods here will be available at submodule-level (toytree.data.[method])
from ._src.get_node_data import get_node_data
from ._src.set_node_data import set_node_data
from ._src.expand_node_mapping import expand_node_mapping
# from toytree.data._src.transform import normalize_values
