#!/usr/bin/env python

"""Submodule for quartet distance functions.

Authors: Deren Eaton and Scarlet Ming-sha Au


Description
------------
N = s + d + r1 + r2 + u
s = intersection of resolved quartets
s = intersection of two of these: get_resolved_sorted_quartets()
d = symmetric difference of resolved quartets
d = symmetric difference of two of these: get_resolved_sorted_quartets()
r1 = unresolved in t1 but resolved in t2
r2 = vice-versa
r1 = (qrt1 - qrt2) - d(t1, t2)

References
----------
- ...
- ...
"""

from typing import Iterator, Tuple, TypeVar
import itertools
import toytree


ToyTree = TypeVar("ToyTree")


def get_quartet_sets(tree: ToyTree) -> Iterator[Tuple[str]]:
    """..."""
    for qrt in itertools.combinations(tree.get_tip_labels(), 4):
        yield qrt

def get_n_quartets(tree: ToyTree) -> int:
    """..."""
    return sum(1 for i in get_quartet_sets(tree))

def get_resolved_sorted_quartets(tree: ToyTree) -> Iterator[Tuple[str]]:
    """Yield quartets of tip names spanning each edge of a tree.
    
    FIXME: sort within and between tuples. remove self ref.
    FIXME: yield as a single sorted Tuple of (0,1,2,3) assuming split in middle.

    Examples
    --------
    >>> small_tree = toytree.rtree.unittree(6)
    >>> print(list(small_tree._iter_quartets()))
    >>>
    >>> large_tree = toytree.rtree.unittree(100)
    >>> nquartets = sum(1 for i in large_tree._iter_quartets())
    >>> print(f'nquartets={nquartets}')
    """
    # mapping node idx to a set of node idx
    cache = {i: {i} for i in range(tree.ntips)}
    ridx = tree.treenode.idx
    root_nodes = 1 if tree.is_rooted() else 0
    all_nodes = range(tree.ntips, tree.nnodes - root_nodes)
    node_set = set(range(tree.nnodes - root_nodes))
    observed = set([])

    for nidx in all_nodes[:-1]:
        if tree[nidx].up:

            # get nodes above and below this edge
            below = {nidx}
            for child in tree[nidx].children:
                below |= cache[child.idx]
            cache[nidx] = below
            other = node_set - below

            # remove ridx, and rm nidx if on same side
            if ridx in below:
                below.discard(ridx)
                below.discard(nidx)
            else:
                other.discard(ridx)

            # limit to the tip Nodes
            below = (i for i in below if i < tree.ntips)
            other = (i for i in other if i < tree.ntips)

            # convert to requested type
            below = (getattr(tree[i], "name") for i in below)
            other = (getattr(tree[i], "name") for i in other)

            # subsample 2 from each side of bipart.
            # {0, 1, 2} -> {0, 1}, {0, 2}, and {1, 2}.
            # Perhaps all {0, 1} quartets have already been done,
            # we still need to visit all {0, 2} and {1, 2} so we
            # check and skip redundant quartets below.
            biquarts = itertools.product(
                itertools.combinations(below, 2),
                itertools.combinations(other, 2),
            )

            # iterate over quartets from this bipart and yield
            # if it has not been visited yet.
            for quart in biquarts:
                if quart not in observed:
                    observed.add(quart)
                    yield tuple(itertools.chain(*quart))
                    #pair1 = sorted(quart[0])
                    #pair2 = sorted(quart[1])
                    #yield tuple(itertools.chain(*sorted([pair1, pair2])))
                    # yield quart    


def get_simple_quartets(tree):
    """TODO..."""
    tips = set(tree.get_tip_labels())
    cache = {}
    for node in tree.traverse("idxorder"):
        if node.is_leaf():
            cache[node] = {node.idx}
        else:
            cache[node] = set.union(*(cache[i] for i in node.children))

        sisters = set.union(*(cache[i] for i in node.get_sisters()))



def get_n_resolved_quartets(tree: ToyTree) -> int:
    """..."""
    return sum(1 for i in get_resolved_sorted_quartets(tree))


if __name__ == "__main__":
    TREE1 = toytree.rtree.unittree(5, seed=123)
    TREE2 = toytree.rtree.unittree(5, seed=321)
    TREE2 = TREE2.mod.collapse_nodes(5, 6, 7)
    # print(list(get_quartet_sets(tree)))


    Q1 = get_resolved_sorted_quartets(TREE1)
    Q2 = get_resolved_sorted_quartets(TREE2)    

    # resolved differently: in one or other but not both
    d = set(Q1).symmetric_difference(Q2)
    print(d)

    # unresolved in t1 but resolved in t2
    q1minusq2 = set(Q1) - set(Q2)
    r1 = len(q1minusq2) - len(d)
    print(r1)