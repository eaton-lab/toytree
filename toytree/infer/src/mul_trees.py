#!/usr/bin/env python

"""Inference methods concerning multi-labeled trees (mul trees).


"""

from typing import TypeVar, Collection
import pandas as pd
import toytree

ToyTree = TypeVar("ToyTree")
Node = TypeVar("Node")


def set_ng_labels(gtree: ToyTree) -> None:
    """Sets a feature 'ng' to each internal node in a tree."""
    for node in gtree:
        if node.children:
            node.ng = set.union(*(i.ng for i in node.children))
        else:
            node.ng = {node.name}


def set_ns_labels(gtrees: Collection[ToyTree], sptree: ToyTree) -> None:
    """Sets a feature 'ns' as MRCA sptree node containing 'ng' set."""
    for gtree in gtrees:
        for node in gtree:
            node.ns = sptree.get_mrca_node(*node.ng)


def count_duplications(gtree: ToyTree) -> int:
    """Return duplication and speciation events on a tree.

    Nodes in the gene tree are said to be duplication nodes when they
    map to the same species tree node as at least one of their
    descendants.

    Adds a feature 'dup' to Nodes with True or False.
    """
    ndups = 0
    for node in gtree.traverse():
        desc_ns = [i.ns for i in node.get_descendants()[1:]]
        if node.ns in desc_ns:
            ndups += 1
            node.dup = True
        else:
            node.dup = False
    return ndups


def depth(sptree: ToyTree, node: Node) -> int:
    """return distance from root in sptree"""
    return sptree.distance.get_node_distance(
        sptree.treenode.idx, node.idx, topology_only=True)


def count_losses(gtree: ToyTree, sptree: ToyTree) -> int:
    """Return ...

    Adds feature 'loss' as an int to each Node.
    """
    loss = 0
    for node in gtree.traverse():
        node.depth = depth(sptree, node.ns) + 1

    for node in gtree.traverse():
        if node.is_root():
            continue
        node.loss = ((node.depth - node.up.depth) - 1) + int(node.up.dup)
        if node.loss:
            loss += 1
    return loss


def get_multree_reconciliation_score(
    gtrees: Collection[ToyTree],
    sptrees: Collection[ToyTree],
) -> pd.DataFrame:
    """

    [sptree, gtree, dtg, ltg, score]
    """
    # check that gtrees and sptrees are iterable (lists)

    # set 'ng' sets on the Nodes of all gene trees.
    for gtree in gtrees:
        set_ng_labels(gtree)

    # build collection of species trees to be tested...
    # ...

    # iterate over species trees to compute scores. Linear in time, 
    # can be fully parallelized.
    full_data = []
    sub_data = []
    for sidx, sptree in enumerate(sptrees):
        newick_s = sptree.write(None, None, None)
        set_ns_labels(gtrees, sptree)
        chunks = []
        for gidx, gtree in enumerate(gtrees):
            newick_g = gtree.write(None, None, None)
            dtg = count_duplications(gtree)
            ltg = count_losses(gtree, sptree)
            score = dtg + ltg
            chunks.append([sidx, gidx, newick_s, newick_g, dtg, ltg, score])

        # fill result of all gene trees
        sub_data.append(
            pd.DataFrame(
                chunks,
                columns=['sidx', 'gidx', 'sptree', 'gtree', 'dups', 'losses', 'score'],
            ))
        full_data.append([sidx, newick_s, sub_data[-1].score.sum()])
    sub_data = pd.concat(sub_data).reset_index(drop=True)
    full_data = pd.DataFrame(full_data, columns=["sidx", "sptree", "score"])
    full_data = full_data.sort_values("sidx")
    return full_data, sub_data


if __name__ == "__main__":

    # validation with ipcoal
    import ipcoal
    import string

    # get a single-labeled species tree with names (A-...)
    NTIPS = 6
    sptree_single = toytree.rtree.unittree(ntips=NTIPS, treeheight=1e6, seed=123)
    name_map = dict(zip(range(10), string.ascii_uppercase))
    sptree_single.set_node_data("name", name_map, inplace=True)

    # insert an allo-polyploid genome dup event to make a mul-tree
    subtree = toytree.tree("((X:1,Y:1):1,Z:2):1;")
    sptree_mul = toytree.mod.add_internal_node_and_subtree(sptree_single, 'A', subtree=subtree)
    sptree_mul = toytree.mod.add_internal_node_and_subtree(sptree_mul, 'E', subtree=subtree)

    # generate a different mul-tree to compare against
    sptree_mul2 = toytree.mod.add_internal_node_and_subtree(sptree_single, 'B', subtree=subtree)
    sptree_mul2 = toytree.mod.add_internal_node_and_subtree(sptree_mul2, 'F', subtree=subtree)

    # draw species trees
    c, _, _ = toytree.mtree([sptree_mul, sptree_mul2]).draw()
    toytree.utils.show(c)

    # simulate genealogies on this mul-species-tree
    model = ipcoal.Model(
        sptree_mul, Ne=2e5, nsamples=1, seed_trees=123, seed_mutations=123)
    model.sim_trees(100)

    # draw some genealogies
    # canvas, _, _ = model.draw_genealogies(scale_bar=True, shared_axes=True)
    # toytree.utils.show(canvas)
    gtrees = toytree.mtree(model.df.genealogy.to_list())
    full, sub = get_multree_reconciliation_score(gtrees, [sptree_mul, sptree_mul2])

    print("Comparing species tree models:")
    print("------------------------------")
    print(full)

    print("\n\nScores of individual gene trees for each model:")
    print("--------------------------------------------------")
    print(sub)
