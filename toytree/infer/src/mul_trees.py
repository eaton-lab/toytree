#!/usr/bin/env python

"""Inference methods concerning multi-labeled trees (mul trees).

Count the number of duplications and losses required to embed a
mult-labeled gene tree (mul-tree) into a species tree.

TODO
----
[ ] losses counter is not working correctly.
[ ] better simulation methods for testing. Perhaps, define mul-tree to
serve as the demography for an ipcoal simulation (or implement tt-only).
[ ] read for improvements on the LCA- approach.
[ ] test for compatibility with Thomas paper before releasing.


Methods
-------
...
    Given a set of mul-trees this identifies the parental lineage that
    hybridized to form allopolyploidy.
...
    ...

References
----------
- Thomas, G. W., Ather, S. H., & Hahn, M. W. (2017). Gene-tree
reconciliation with MUL-trees to resolve polyploidy events. Systematic
biology, 66(6), 1007-1018.
- Gascon, M., Dondi, R., & El-Mabrouk, N. (2022). MUL-tree pruning for
consistency and optimal reconciliation-complexity and algorithms.
Theoretical Computer Science, 937, 22-38.

"""

from typing import Dict, Optional, Sequence, Union
from itertools import combinations
import pandas as pd
import toytree
from toytree import ToyTree


def _set_ng_labels(gtree: ToyTree) -> None:
    """Sets a cached feature 'ng' with leaf names under each node.

    In the example below there are two gene tree tips named 'r1'.

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
    >>> tree1 = tree.mod.add_internal_node_and_child("r1", name="r1")
    >>> _set_ng_labels(tree1)
    >>> tree1.get_node_data("ng")
    >>> # 0                     {r0}
    >>> # 1                     {r1}
    >>> # 2                     {r1}
    >>> # 3                     {r2}
    >>> # 4                     {r3}
    >>> # 5                     {r4}
    >>> # 6                     {r1}
    >>> # 7                 {r1, r0}
    >>> # 8             {r1, r0, r2}
    >>> # 9                 {r3, r4}
    >>> # 10    {r4, r3, r2, r1, r0}
    """
    for node in gtree:
        if node._children:
            node.ng = set.union(*(i.ng for i in node._children))
        else:
            node.ng = {node.name}


def _set_ns_labels(gtree: ToyTree, sptree: ToyTree) -> None:
    """Sets feature 'ns' as MRCA sptree node idx containing 'ng' set.

    This assumes that `_set_ng` has already set 'ng' features on the
    gene tree. The stored 'ns' features are species tree idxs.

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
    >>> tree1 = tree.mod.add_internal_node_and_child("r1", name="r1")
    >>> _set_ng_labels(tree1)
    >>> _set_ns_labels(tree1, tree)
    >>> tree1.get_node_data("ns")
    >>> # 0     0
    >>> # 1     1
    >>> # 2     1
    >>> # 3     2
    >>> # 4     3
    >>> # 5     4
    >>> # 6     1
    >>> # 7     5
    >>> # 8     6
    >>> # 9     7
    >>> # 10    8
    """
    for node in gtree:
        node.ns = sptree.get_mrca_node(*node.ng).idx


def _count_duplications(gtree: ToyTree, sptree: ToyTree) -> int:
    """Return numer of duplication events on a gene tree.

    Nodes in the gene tree are said to be duplication nodes when they
    map to the same species tree node as at least one of their
    descendants. This assumes that the gene trees already have a
    value "ns" stored to every Node by `_set_ns_labels`.

    Adds a feature 'duplication' to Nodes with True or False.

    Note
    ----
    - Can you have multiple duplications per node?
    - How to treat polytomies?

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
    >>> tree1 = tree.mod.add_internal_node_and_child("r1", name="r1")
    >>> _set_ng_labels(tree1)
    >>> _set_ns_labels(tree1, tree)
    >>> _count_duplications(tree1)
    >>> # 1
    >>> tree1.get_node_data("duplication")
    >>> # 0     False
    >>> # 1     False
    >>> # 2     False
    >>> # 3     False
    >>> # 4     False
    >>> # 5     False
    >>> # 6      True
    >>> # 7     False
    >>> # 8     False
    >>> # 9     False
    >>> # 10    False
    """
    ndups = 0
    for node in gtree[gtree.ntips:]:
        # if any descendants (not including self) trace back to the
        # same species tree interval then a duplication occurred
        node.duplication = False

        # original method implemented based on paper and species tree nodes
        for desc in node.iter_descendants():
            if node == desc:
                continue
            if node.ns == desc.ns:
                ndups += 1
                node.duplication = True
                break
    return ndups


def _count_duplications_new(gtree, sptree):
    ndups = 0
    for node in gtree[gtree.ntips:]:
        # if any descendants (not including self) trace back to the
        # same species tree interval then a duplication occurred
        node.duplication = False

        # alternative method implemented using simpler double occurrence of desc
        # get a set of tips in each child lineage
        child_sets = [set(i.get_leaf_names()) for i in node.children]
        if any(i & j for (i, j) in combinations(child_sets, 2)):
            ndups += 1
            node.duplication = True
    return ndups


def _count_losses(gtree: ToyTree, sptree: ToyTree) -> int:
    """Return number of loss events on a gene tree.

    Nodes in the gene tree count a loss for every occurrence
    descendants do not include are descended
    from a duplication event but do not include all descendants
    leaves.

    Adds feature 'losses' as an int to each Node.
    """
    losses = 0

    # measure number of nodes between the sptree root and the min
    # sptree interval in which a gtree node must have occurred.
    for node in gtree:
        node.depth = sptree.distance.get_node_distance(
            -1, node.ns, topology_only=True) + 1

    # measure losses as ...
    for node in gtree[:-1]:
        node.losses = ((node.depth - node.up.depth) - 1) + int(node.up.duplication)
        if node.losses:
            losses += 1
    return losses


def _count_losses_new(gtree: ToyTree, sptree: ToyTree) -> int:
    """...


    """
    # expect = {}...
    losses = 0
    for node in gtree:
        desc_g = set(node.get_leaf_names())
        desc_s = set(sptree[node.ns].get_leaf_names())
        node.losses = desc_s - desc_g
        losses += node.losses
    return losses


def get_duplication_loss_coalescence(
    gtree: ToyTree, sptree: ToyTree, imap: Optional[Dict[str, Sequence[str]]] = None,
) -> Dict[str, int]:
    """Returns a dict with duplication, loss, and coalescence info.

    ...

    Parameters
    ----------
    gtree: ToyTree
        ...
    sptree: ToyTree
        ...
    imap: Dict[str, Sequence[str]]
        A dict mapping species tree tip labels to a list of one or
        more gene tree tip labels. If not provided (None) it is
        expected that the names will match identically.

    Example
    -------
    >>> ...
    >>> ...
    """
    if imap:
        raise NotImplementedError("TODO")
    gtree = gtree.copy()  # speed cost but prevents added features.
    _set_ng_labels(gtree)
    _set_ns_labels(gtree, sptree)
    duplications = _count_duplications(gtree, sptree)
    losses = _count_losses(gtree, sptree)
    data = {
        "tree": gtree,
        "duplications": duplications,
        "losses": losses,
        # "coalescences": gtree.nnodes - dups - loss,
        "score": duplications + losses,
    }
    return data


def get_multree_reconciliation_scores(
    gtrees: Union[ToyTree, Sequence[ToyTree]],
    sptrees: Union[ToyTree, Sequence[ToyTree]],
) -> pd.DataFrame:
    """Return table with DLC reconciliation.

    Parameters
    ----------
    gtrees: ToyTree | Sequence[ToyTree]
        One or more mul-trees (gene trees with multi-labeled tips).
    sptrees: ToyTree | Sequence[ToyTree]
        One or more species trees containing only a single tip per
        species

    Returns
    -------
    A pandas dataframe is returned w/ ...[sptree, gtree, dtg, ltg, score]

    Example
    --------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
    >>> dtree = tree.mod.add_internal_node_and_child('r3', name='r3')
    >>> get_multree_reconciliation_score(tree, dtree)

    References
    ----------
    ...
    """
    # check that gtrees and sptrees are iterable (lists)
    if isinstance(gtrees, ToyTree):
        gtrees = [gtrees]
    if isinstance(sptrees, ToyTree):
        sptrees = [sptrees]

    # set 'ng' sets on the Nodes of all gene trees.
    for gtree in gtrees:
        _set_ng_labels(gtree)

    # build collection of species trees to be tested...
    # ...

    # iterate over species trees to compute scores. Linear in time,
    # can be fully parallelized, but is not yet.
    full_data = []
    sub_data = []
    for sidx, sptree in enumerate(sptrees):
        newick_s = sptree.write(None, None, None)

        # cache the MRCA nodes
        for gtree in gtrees:
            _set_ns_labels(gtree, sptree)

        # iterate over ...
        chunks = []
        for gidx, gtree in enumerate(gtrees):
            newick_g = gtree.write(None, None, None)
            dtg = _count_duplications(gtree, sptree)
            ltg = _count_losses(gtree, sptree)
            score = dtg + ltg
            chunks.append([sidx, gidx, newick_s, newick_g, dtg, ltg, score])

        # fill result of all gene trees
        sub_data.append(
            pd.DataFrame(
                chunks,
                columns=['sidx', 'gidx', 'sptree', 'gtree', 'dups', 'losses', 'score'],
            ))
        full_data.append([sidx, newick_s, sub_data[-1].score.sum()])

    # concatenate dataframes into final df and relabel
    sub_data = pd.concat(sub_data).reset_index(drop=True)
    full_data = pd.DataFrame(full_data, columns=["sidx", "sptree", "score"])
    full_data = full_data.sort_values("sidx")
    return full_data, sub_data


def example_fig2_thomas():
    """..."""
    tree = toytree.tree("((A,B),(C,D));")
    subtree = toytree.tree("(Z,(X,Y));")

    # insert the "duplicated" subclade XYZ into both lineages that
    # hybridized (e.g., B and C) to represent a mul-tree.
    tree = tree.mod.add_internal_node_and_subtree("B", subtree=subtree)
    tree = tree.mod.add_internal_node_and_subtree("C", subtree=subtree)
    return tree



if __name__ == "__main__":

    # set up a tree with one duplicated tip label
    tree = toytree.rtree.unittree(5, seed=123)
    tree1 = tree.mod.add_internal_node_and_child("r1", name="r1")

    # add 'ng' feature as {*children idx} for each Node
    _set_ng_labels(tree1)
    print(tree1.get_node_data("ng"))

    # add 'ns' feature as mrca(ng) for each node (minimal sp tree mrca)
    _set_ns_labels(tree1, tree)
    print(tree1.get_node_data("ns"))

    #
    tree1._draw_browser(tmpdir="~", node_sizes=20, node_labels="ns", node_mask=False)

    # get mul-tree
    mul_tree = example_fig2_thomas()
    mul_tree._draw_browser(tmpdir="~", ts='s', tip_labels_colors=("name", "Dark2"))
    # full, sub = get_multree_reconciliation_scores(gtrees, [sptree_mul, sptree_mul2])


    # validation with ipcoal
    # import ipcoal
    # import string

    # # get a single-labeled species tree with names (A-...)
    # NTIPS = 6
    # sptree_single = toytree.rtree.unittree(ntips=NTIPS, treeheight=1e6, seed=123)
    # name_map = dict(zip(range(10), string.ascii_uppercase))
    # sptree_single.set_node_data("name", name_map, inplace=True)

    # # insert an allo-polyploid genome dup event to make a mul-tree
    # subtree = toytree.tree("((X:1,Y:1):1,Z:2):1;")
    # sptree_mul = toytree.mod.add_internal_node_and_subtree(sptree_single, 'A', subtree=subtree)
    # sptree_mul = toytree.mod.add_internal_node_and_subtree(sptree_mul, 'E', subtree=subtree)

    # # generate a different mul-tree to compare against
    # sptree_mul2 = toytree.mod.add_internal_node_and_subtree(sptree_single, 'B', subtree=subtree)
    # sptree_mul2 = toytree.mod.add_internal_node_and_subtree(sptree_mul2, 'F', subtree=subtree)

    # # draw species trees
    # c, _, _ = toytree.mtree([sptree_mul, sptree_mul2]).draw(ts='s', height=400)
    # toytree.utils.show(c, tmpdir="~")

    # # sptree_mul2

    # simulate genealogies on this mul-species-tree
    # model = ipcoal.Model(
    #     sptree_mul, Ne=2e5, nsamples=1, seed_trees=123, seed_mutations=123)
    # model.sim_trees(100)

    # # draw some genealogies
    # # canvas, _, _ = model.draw_genealogies(scale_bar=True, shared_axes=True)
    # # toytree.utils.show(canvas)
    # gtrees = toytree.mtree(model.df.genealogy.to_list())
    # full, sub = get_multree_reconciliation_score(gtrees, [sptree_mul, sptree_mul2])

    # print("Comparing species tree models:")
    # print("------------------------------")
    # print(full)

    # print("\n\nScores of individual gene trees for each model:")
    # print("--------------------------------------------------")
    # print(sub)
