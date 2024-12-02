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

from typing import TypeVar, Dict, Optional, Tuple, Iterator
from loguru import logger
import numpy as np
from toytree.core.node import Node
from toytree.core.tree import ToyTree

logger = logger.bind(name="toytree")

MultiTree = TypeVar("MultiTree")


class ConsensusTree:
    """An extended majority rule consensus class.

    Takes a set of input trees and returns a consensus tree. The input
    trees can be rooted or unrooted, and the returned consensus tree
    can be rooted or unrooted, depending on options used.

    Features on the consensus tree. Support values on the consensus
    tree represent the proportion of edges that existed in the set
    of trees.

    Dist values represent the average 'dist' among edges
    that existed in the set of trees, but are only computed if best
    is not supplied as an input tree.

    If ultrametric is set to true then the returned tree is rooted
    on...

    Parameters
    ----------
    ultrametric: bool
        If true then node height statistics are calculated and the
        tree will be rooted using the "root_method" argument option.
        The tree can be rooted without being ultrametric, but it
        cannot be ultrametric without being rooted.
    root_method: int
        0: root on midpoint given branch lengths on consensus tree.
        1: root on edge that contains root across majority of input
        trees, using the mean root position on this edge.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123)

    Get 20 rooted ultrametric trees w/ same topology and variable dists
    >>> rutrees = [
    >>>    tree.mod.edges_multiplier().mod.edges_slider()
    >>>    for i in range(20)]

    Get 20 unrooted ultrametric trees w/ same topology and variable dists
    >>> uutrees = [
    >>>    tree.unroot().mod.edges_multiplier().mod.edges_slider()
    >>>    for i in range(20)]

    Get 20 unrooted non-ultrametric trees w/ same topology and variable dists
    >>> untrees = [
    >>>    tree.unroot().mod.edges_multiplier().mod.edges_slider()
    >>>    for i in range(20)]
    
    ...
    >>> # ...
    """
    def __init__(
        self,
        mtree: MultiTree,
        best_tree: Optional[ToyTree] = None,
        majority_rule_min: float = 0.0,
        ultrametric: Optional[bool] = None,
        root_method: Optional[bool] = None,
    ):
        # creates an unrooted copy of the original tree
        self.mtree = mtree
        self.best_tree = best_tree
        self.majority_rule_min = majority_rule_min

        if ultrametric is None:
            self.ultrametric = self.mtree.all_tree_tips_aligned()
        else:
            self.ultrametric = ultrametric

    def _iter_unique_trees(self) -> Iterator[Tuple[ToyTree, int]]:
        """Yield unique topologies and their counts from mtree."""
        for tree, count in self.mtree.get_unique_topologies():
            yield tree, count

    def run(self) -> ToyTree:
        """Return a ToyTree with consensus support values."""
        # map clade support values onto a user-supplied input tree
        if self.best_tree is not None:
            return self._map_clades_support_onto_best_tree()

        # build the majrule tree with clade support and other meta data
        ctree = self._get_majority_rule_consensus_tree()

        # if the tree is ultrametric then align tips
        if self.ultrametric:
            # find the most likely root
            ctree.mod.root_on_midpoint(inplace=True)

            # set tips to 0 and root to a temporary high value for now.
            ctree.set_node_data(
                "height",
                {-1: ctree[-2].height + 1} | {i: 0 for i in range(ctree.ntips)},
                inplace=True
            )

            # set internal non-root-associated nodes to their mean height
            ctree.set_node_data(
                "height",
                {i: i.height_mean for i in range(ctree.ntips, ctree.nnodes - 2)},
                inplace=True,
            )

            # prior root node that had its edge split to insert the root
            ctree.set_node_data(
                "height",
                {ctree[-2]: ..., ctree[-1]: ...},
                inplace=True,
            )

            # new root node
            ctree.set_node_data("height", {ctree[-1]: ...}, inplace=True)
        return ctree

    def _map_clades_support_onto_best_tree(self) -> ToyTree:
        """Return the best tree with clade supports from trees.

        This relies on the sorted order of `get_bipartitions`. Finds
        'support' feature for all Nodes in 'best'. Any other requested
        features of the input trees will also be
        """
        # copy best tree and set default to 0
        self.best_tree = self.best_tree.set_node_data("support", default=0)

        # returns ubipartitions (root has no effect)
        best_tree_parts = list(self.best_tree.iter_bipartitions("name", True, False))

        # mirror the support on the root Node's children
        cidxs = [i.idx for i in self.best_tree.treenode.children]
        cmax = max(cidxs)
        cmin = min(cidxs)

        # iterate over all unique tree topologies
        for utree, count in self._iter_unique_trees():

            # iterate over ubipartitions in tree: [[['a'], ['b', 'c']], [...]]
            for nidx, bipart in enumerate(utree.iter_bipartitions("name", True, False)):
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

    def _get_majority_rule_consensus_tree(self) -> ToyTree:
        """Return the majrule consensus tree.

        Calculates clade 'support', 'dist', and 'features'.
        This relies on the sorted order of `get_bipartitions`.
        """
        clade_freqs = self._get_all_clade_freqs()
        fclade_freqs = self._get_all_filtered_clades(clade_freqs)
        root = self._build_all_tree(fclade_freqs)
        return ToyTree(root)

    def _build_all_tree(self, fclade_freqs: Dict[Tuple, int]) -> Node:
        """Build majority-rule consensus tree from clades"""

        # root node
        all_tips = frozenset(self.mtree.get_tip_labels())
        # root = Node(name="")
        # cset = fclade_freqs[all_tips]
        # for feat in ['dist_min', 'dist_max', 'dist_median', 'dist_std']:
        #     setattr(root, feat, 0.)
        # for feat in ['height_min', 'height_max', 'height_median', 'height_std']:

        # dict with {tip-set: Node} in order they are added (Py3)
        # sets_to_nodes = {all_tips: root}
        sets_to_nodes = {}

        # visit filtered clades from LARGEST to SMALLEST
        for cset in sorted(fclade_freqs, key=len, reverse=True):

            # skip if already added
            if cset in sets_to_nodes:
                continue

            # create Node to represent this clade
            dists = np.array(fclade_freqs[cset][1])
            heights = np.array(fclade_freqs[cset][2])

            # ...
            node = Node(
                name=str(*cset) if len(cset) == 1 else "",
                support=fclade_freqs[cset][0],
                dist=dists.mean(),
            )

            # ...
            dmin = dists[dists > 0].min() if (dists > 0).sum() else 0
            setattr(node, "dist_min", dmin)
            setattr(node, "dist_max", dists.max())
            setattr(node, "dist_mean", np.mean(dists))
            setattr(node, "dist_median", np.median(dists))
            setattr(node, "dist_std", dists.std())

            hmin = 0 if not (heights > 0).sum() else min(heights[heights > 0])
            setattr(node, "height_min", hmin)
            setattr(node, "height_max", heights.max())
            setattr(node, "height_mean", np.mean(heights))
            setattr(node, "height_median", np.median(heights))
            setattr(node, "height_std", heights.std())

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
        return sets_to_nodes[all_tips]

    def _get_all_filtered_clades(self, clade_freqs: Dict[Tuple, int]) -> Dict:
        """Remove conflicting clades and those < majority_rule_min"""
        # keep track of kept clades in order they are kept.
        keep_dict = {}  # {frozenset : float}

        # visit clades in sorted order and drop conflicts or low support
        for clade, (freq, dist, height) in clade_freqs.items():

            # clade is below threshold, discard.
            if freq < self.majority_rule_min:
                # logger.debug(f"clade {clade}:{freq} below min threshold")
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
                # logger.debug(f"clade {clade} conflicts.")

            # passed filters, keep it.
            if not conflict:
                keep_dict[cset] = (freq, dist, height)
        return keep_dict

    def _get_all_clade_freqs(self) -> Dict:
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
            iter_biparts = utree.iter_bipartitions("name", True, False, set, True)
            for nidx, bipart in enumerate(iter_biparts):
                # skip tip-only Nodes
                node = utree[nidx]
                # store the smaller half
                clade = tuple(bipart[0])

                # if a root child then store the edge length in unrooted form
                # store the root position on the branch in the case that it
                # is again inferred as the root.
                if node.up:
                    if node.up.is_root():
                        children = node.up.children
                        if len(children) == 2:
                            dist = sum(i.dist for i in children)
                            logger.debug([node, node.dist, dist])
                        else:
                            dist = node.dist
                    else:
                        dist = node.dist
                else:
                    dist = node.dist

                # store dist and height
                if clade in clades:
                    clades[clade][0] += increment
                    clades[clade][1].append(dist)
                    clades[clade][2].append(node.height)
                else:
                    clades[clade] = [increment, [node.dist], [node.height]]

        # return in sorted order and w/ counts as proportions
        sort_clades = sorted(
            clades,
            key=lambda x: clades[x][0], reverse=True
        )

        # add the full (all samples) clade to get stats for it.
        all_tips = tuple(self.mtree[0].get_tip_labels())
        sort_clades = [all_tips] + sort_clades
        clades[all_tips] = (
            1.0,
            [i.treenode.dist for i in self.mtree],
            [i.treenode.height for i in self.mtree],
        )
        return {i: clades[i] for i in sort_clades}


if __name__ == "__main__":

    import toytree

    # these trees should all have full support
    # tres = [toytree.rtree.unittree(10, seed=123) for i in range(5)]
    # mtre = toytree.mtree(tres)
    # ctre = ConsensusTree(mtre).run()
    # # ctre = ctre.root("r8", "r9")
    # ctre._draw_browser(node_sizes=20, node_labels="support", tmpdir="~")


    trees = toytree.mtree([
        "((a,b),(c,(d,e)));",
        "((a,b),(c,(d,e)));",
        "((a,b),(e,(c,d)));",
    ])
    ctre = ConsensusTree(trees).run()
    ctre.treenode.support = np.nan
    ctre._draw_browser(node_sizes=20, node_labels="support", tmpdir="~")    
    ctre.treenode.draw_ascii()    
    print(ctre.get_node_data())#"support"))

    # print(ctre.write(features=ctre.features))

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
