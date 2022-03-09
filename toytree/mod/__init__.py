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

from toytree.mod._src.mod_edges import (
	edges_scale_to_root_height,
	edges_slider,
	edges_multiplier,
	edges_extend_tips_to_align,
	edges_set_node_heights,
)
from toytree.mod._src.mod_topo import (
	ladderize,
	collapse_nodes,
	rotate_node,
	prune,
	drop_tips,
	resolve_polytomies,
	remove_unary_nodes,
	add_internal_node,
	add_tip_node,
)
from toytree.mod._src.root_unroot import unroot, root
from toytree.mod._src.tree_move import (
	move_spr, 
	move_nni,
	move_nni_iter,
)
