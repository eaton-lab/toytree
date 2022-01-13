#!/usr/bin/env python

"""Class to construct and return a consensus tree from multiple trees.

Speed
-----
Reducing to only unique topologies costs as much time as just 
visiting and computing on them, and would not allow getting dist
values. So this visits all trees.

TODO
----
Support getting mean, etc, of any feature on trees. This is a bit
of work, needs to check all for int,float type. Not done.
"""

from typing import TypeVar, Dict, Optional, Tuple
from loguru import logger
import numpy as np
from toytree.core.node import Node
from toytree.core.tree import ToyTree

logger = logger.bind(name="toytree")

MultiTree = TypeVar("MultiTree")


class ConsensusTree:
    """An extended majority rule consensus class.
    
    Takes a set of input trees and returns a consensus tree. 

    Features on the consensus tree. Support values on the consensus
    tree represent the proportion of edges that existed in the set 
    of trees. 

    Dist values represent the average 'dist' among edges
    that existed in the set of trees, but are only computed if best
    is not supplied as an input tree.
    """
    def __init__(
        self,
        mtree: MultiTree,
        best_tree: Optional[ToyTree] = None,
        majority_rule_min: float = 0.0,
        ):

        # creates an unrooted copy of the original tree
        self.mtree = mtree
        self.best_tree = best_tree
        self.majority_rule_min = majority_rule_min

    def _iter_unique_trees(self):
        """Yield unique topologies and their counts from mtree."""
        for tree, count in self.mtree.get_unique_topologies():
            yield tree, count

    def run(self) -> ToyTree:
        """Return a ToyTree with consensus support values."""
        if self.best_tree is not None:
            return self._map_clades_support_onto_best_tree()
        return self._get_majority_rule_consensus_tree()

    def _map_clades_support_onto_best_tree(self):
        """Return the best tree with clade supports from trees.

        This relies on the sorted order of `get_bipartitions`. Finds
        'support' feature for all Nodes in 'best'. Any other requested
        features of the input trees will also be 
        """
        # copy best tree and set default to 0
        self.best_tree = self.best_tree.set_node_data("support", default=0) 

        # returns ubipartitions (root has no effect)
        best_tree_parts = list(self.best_tree._iter_bipartitions("name", True, False))

        # mirror the support on the root Node's children
        cidxs = [i.idx for i in self.best_tree.treenode.children]
        cmax = max(cidxs)
        cmin = min(cidxs)

        # iterate over all unique tree topologies
        for utree, count in self._iter_unique_trees():

            # iterate over ubipartitions in tree: [[['a'], ['b', 'c']], [...]]
            for nidx, bipart in enumerate(utree._iter_bipartitions("name", True, False)):
                if nidx >= self.best_tree.ntips:
                    try:
                        idx = best_tree_parts.index(bipart)
                        if idx == cmin:
                            self.best_tree[cmax].support += count
                            self.best_tree[cmin].support += count
                        else:
                            self.best_tree[idx].support += count
                    except ValueError:
                        pass
        # divide support by ntrees to get proportion
        ntrees = self.mtree.ntrees
        for node in self.best_tree.traverse():
            node.support /= ntrees

        # root Node doesn't truly have support, except in the sense
        # that an outgroup *was* present and is now trimmed from the
        # tree, while retaining support for this tree versus outside.
        self.best_tree.treenode.support = 1.0
        return self.best_tree

    def _get_majority_rule_consensus_tree(self):
        """Return the majrule consensus tree.

        Calculates clade 'support', 'dist', and 'features'.
        This relies on the sorted order of `get_bipartitions`. 
        """
        clade_freqs = self._get_all_clade_freqs()
        fclade_freqs = self._get_all_filtered_clades(clade_freqs)
        root = self._build_all_tree(fclade_freqs)
        return ToyTree(root)

    def _build_all_tree(self, fclade_freqs: Dict[Tuple, int]):
        """Build majority-rule consensus tree from clades"""

        # root node
        root = Node(name="", dist=0, support=1.0)
        for feat in ['dist_min', 'dist_max', 'dist_median', 'dist_std']:
            setattr(root, feat, 0.)

        # dict with {tip-set: Node} in order they are added (Py3)
        all_tips = frozenset(self.mtree.get_tip_labels())
        sets_to_nodes = {all_tips: root}

        # visit filtered clades from LARGEST to SMALLEST
        for cset in sorted(fclade_freqs, key=len, reverse=True):

            # skip if already added
            if cset in sets_to_nodes:
                continue

            # create Node to represent this clade
            dists = np.array(fclade_freqs[cset][1])
            node = Node(
                name=str(*cset) if len(cset) == 1 else "",
                support=round(fclade_freqs[cset][0], 10),
                dist=dists.mean().round(10),
            )
            dmin = dists[dists > 0].min() if (dists > 0).size else 0
            setattr(node, "dist_min", dmin.round(10))
            setattr(node, "dist_max", dists.max().round(10))
            setattr(node, "dist_median", np.median(dists).round(10))
            setattr(node, "dist_std", dists.std().round(10))            

            # visit existing nodes from SMALLEST to LARGEST
            # children iteratively if node is not an descendant.
            for tset in sorted(sets_to_nodes, key=len):
                # is this node (node) is a superset of existing node (tnode)
                if cset.issubset(tset):
                    # get node that exists
                    tnode = sets_to_nodes[tset]
                    tnode._add_child(node)
                    break
            sets_to_nodes[cset] = node
        return root

    def _get_all_filtered_clades(self, clade_freqs: Dict[Tuple, int]):
        """Remove conflicting clades and those < majority_rule_min"""
        # keep track of kept clades in order they are kept.
        keep_dict = {} # {frozenset : float}

        # visit clades in sorted order and drop conflicts or low support
        for clade, (freq, dist) in clade_freqs.items():

            # clade is below threshold, discard.
            if freq < self.majority_rule_min:
                logger.debug(f"clade {clade}:{freq} below min threshold")
                continue

            # clade conflicts with others, discard. If any tips in this
            # clade also occur in an existing clade, then this must be
            # a subset or superset of that clade. Example:
            # ('a', 'b', 'c') conflicts with ('a', 'b', 'd')
            # ('a', 'b', 'c') does not conflict with ('a', 'b', 'c', 'd')
            # ('a', 'b', 'c') does not conflict with ('a', 'b')
            cset = frozenset(clade)

            # check until conflict, or not more sets to compare
            conflict = False
            for pset in keep_dict:
                if conflict:
                    break
                if cset.isdisjoint(pset):
                    continue
                if cset.issubset(pset):
                    continue
                if cset.issuperset(pset):
                    continue
                conflict = True
                logger.debug(f"clade {clade} conflicts.")

            # passed filters, keep it.
            if not conflict:
                keep_dict[cset] = (freq, dist)
        return keep_dict

    def _get_all_clade_freqs(self):
        """Return a dict of {clades: features} where 'support' feature
        is frequency of occurrence across treelist.

        Additional features are stored in a list in order following
        'support' and 'dist'. Clades are represented by the smaller 
        of side of a bipartition (or lowest name str if same size).
        
        The returned dict is sorted by high->low support values.
        {clade2: [support, dist, ...], clade2: [support, ...], ...}
        """
        # keep track of all observed clades
        clades = {}
        ntrees = self.mtree.ntrees
        increment = 1 / ntrees

        # iterate over all unique tree topologies
        for utree in self.mtree:

            # iterate over ubipartitions in tree: [[['a'], ['b', 'c']], [...]]
            for nidx, bipart in enumerate(utree._iter_bipartitions("name", True, False)):
                # skip tip-only Nodes
                node = utree[nidx]
                # store the smaller half
                clade = tuple(bipart[0])

                if clade in clades:
                    clades[clade][0] += increment
                    clades[clade][1].append(node.dist)
                else:
                    clades[clade] = [increment, [node.dist]]

        # return in sorted order and w/ counts as proportions
        sort_clades = sorted(
            clades, 
            key=lambda x: clades[x][0], reverse=True
        )
        return {i: clades[i] for i in sort_clades}


if __name__ == "__main__":

    import toytree

    # these trees should all have full support
    tres = [toytree.rtree.unittree(10, seed=123) for i in range(5)]
    mtre = toytree.mtree(tres)
    ctre = ConsensusTree(mtre).run()
    ctre = ctre.root("r8", "r9")
    # ctre._draw_browser(node_sizes=20, node_labels="support")
    print(ctre.write(features=ctre.features))

    # ctre = ConsensusTree(mtre, best_tree=mtre[0]).run()
    # ctre = ctre.root('r8', 'r9')
    # ctre._draw_browser(node_sizes=20, node_labels="support")

    # these trees should all have diff support
    # trees = [toytree.rtree.unittree(10, ) for i in range(20)]
    # mtree = toytree.mtree(trees)
    # ctree = ConsensusTree(mtree, best_tree=mtree[0]).run()
    # ctree._draw_browser(node_sizes=20, node_labels="support")
    # ctree.root('r8', 'r9', inplace=True)
    # ctree._draw_browser(node_sizes=20, node_labels="support")
