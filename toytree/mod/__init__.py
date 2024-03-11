#!/usr/bin/python

"""toytree subpackage for modifying tree topology or features.

>>> tree = toytree.tree.rtree(10)

>>> tree = tree.mod.root()
>>> tree = tree.mod.unroot()
>>> tree = tree.mod.edges_scale_to_root_height()
>>> tree = tree.mod.edges_slide_nodes()
>>> tree = tree.mod.edges_align_tips_by_extending()
>>> tree = tree.mod.edges_align_tips_by_penalized_likelihood()
>>> tree = tree.mod.add_internal_node()
>>> tree = tree.mod.add_leaf_node()
>>> tree = tree.mod.move_clade()
>>> tree = tree.mod._iter_spr_unrooted()
>>> tree = tree.mod.move_spr_unrooted()

# raised to ToyTree level
>>> tree.root()
>>> tree.unroot()
"""

from toytree.mod._src.mod_edges import *
from toytree.mod._src.mod_topo import *
from toytree.mod._src.root_unroot import *
from toytree.mod._src.root_funcs import *
# from toytree.mod._src.tree_move import *
#     move_spr,
#     move_spr_iter,
#     move_nni,
#     move_nni_iter,
# )
