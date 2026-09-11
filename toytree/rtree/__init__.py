#!/usr/bin/env python

"""Simulate tree topologies, time trees, genealogies, and branch rates.

The public functions distinguish topology distributions from time-tree
processes and molecular-rate models. See each function's docstring for its
conditioning assumptions and edge-length units.
"""

from toytree.rtree._src.birth_death_conditioned import (
    birth_death_conditioned_tree,
)
from toytree.rtree._src.birth_death_process import (
    BirthDeathProcessResult,
    birth_death_process,
)
from toytree.rtree._src.coalescent import coalescent_tree
from toytree.rtree._src.rates import simulate_branch_rates
from toytree.rtree._src.shapes import baltree, imbtree, unittree
from toytree.rtree._src.topology import random_topology

__all__ = [
    "BirthDeathProcessResult",
    "baltree",
    "birth_death_conditioned_tree",
    "birth_death_process",
    "coalescent_tree",
    "imbtree",
    "random_topology",
    "simulate_branch_rates",
    "unittree",
]
