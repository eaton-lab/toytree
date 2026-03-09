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

from __future__ import annotations

import importlib

_MODULE_EXPORTS = {
    "toytree.mod._src.mod_edges": [
        "edges_scale_to_root_height",
        "edges_slider",
        "edges_multiplier",
        "edges_extend_tips_to_align",
        "edges_set_node_heights",
    ],
    "toytree.mod._src.mod_topo": [
        "ladderize",
        "collapse_nodes",
        "remove_unary_nodes",
        "rotate_node",
        "extract_subtree",
        "prune",
        "drop_tips",
        "bisect",
        "resolve_polytomies",
        "resolve_node",
        "add_internal_node",
        "add_child_node",
        "add_sister_node",
        "add_internal_node_and_child",
        "add_internal_node_and_subtree",
        "remove_nodes",
        "merge_nodes",
    ],
    "toytree.mod._src.root_unroot": ["root", "unroot"],
    "toytree.mod._src.root_funcs": [
        "root_on_midpoint",
        "root_on_balanced_midpoint",
        "root_on_minimal_ancestor_deviation",
        "root_on_minimal_dlc",
    ],
    "toytree.mod._src.penalized_likelihood.pl_clock": [
        "edges_make_ultrametric_pl_clock"
    ],
    "toytree.mod._src.penalized_likelihood.pl_discrete": [
        "edges_make_ultrametric_pl_discrete"
    ],
    "toytree.mod._src.penalized_likelihood.pl_relaxed": [
        "edges_make_ultrametric_pl_relaxed"
    ],
    "toytree.mod._src.penalized_likelihood.pl_correlated": [
        "edges_make_ultrametric_pl_correlated"
    ],
    "toytree.mod._src.penalized_likelihood.pl_make_ultrametric": [
        "edges_make_ultrametric"
    ],
    "toytree.mod._src.tree_move": [
        "move_nni_n",
        "iter_nni_n",
        "move_spr_n",
        "iter_spr_n",
        "move_nni",
        "move_spr",
    ],
}

_LAZY_ATTRS = {
    name: (module, name) for module, names in _MODULE_EXPORTS.items() for name in names
}
__all__ = sorted(_LAZY_ATTRS)


def __getattr__(name: str):
    """Lazily import public tree-modification functions on first access."""
    if name not in _LAZY_ATTRS:
        raise AttributeError(name)
    module_name, attr_name = _LAZY_ATTRS[name]
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__():
    """Return module attributes plus lazily available public names."""
    return sorted(set(globals()) | set(__all__))
