#!/usr/bin/env python

"""Tree enumeration module.


See code in here for better iter_biparts code:
http://localhost:8888/notebooks/ipyrad/pedtest/birth-death.ipynb


Examples
--------
Examining splits on a tree.
>>> tree.iter_bipartitions()
>>> tree.iter_quartets()
>>> tree.iter_splits()
>>> tree.iter_split_quartets()

Examining sizes of trees.
>>> # toytree.enumeration.iter_...
"""

# pylint: disable='too-many-branches'

from typing import TypeVar, Iterator, Tuple, Optional
import itertools
from loguru import logger

logger = logger.bind(name="toytree")
ToyTree = TypeVar("ToyTree")


def iter_bipartitions(
    tree: ToyTree,
    feature: str="name",
    exclude_root: bool=True,
    exclude_singletons: bool=True,
    exclude_internal_nodes: bool=True,
    ) -> Iterator[Tuple[Tuple[str],Tuple[str]]]:
    """Generator to yield bipartitions (info about splits in a tree).

    Bipartitions are yielded in random order, but splits and labels
    within bipartitions are sorted. By default bipartitions do not
    include the root Node, but this can be toggled on to return
    bipartitions that can uniquely distinguish rooted topologies.

    Parameters
    ----------
    feature: str
        Feature to return to represent Nodes on either side of a
        bipartition. Default is "name", other likely options are "idx"
        to get int index labels, or None to return Node objects. Note
        that 'idx' does not return 
    exclude_root: bool
        Default if to exclude root Node. If True the root Node
        is included in splits, and one additional bipartition is
        included which specifies root location.    
    exclude_singletons: bool
        Default is to exclude singleton splits (e.g., {A | B,C,D})
        since it is implicit that one exists for every tip Node,
        but these can also be included if requested.
    exclude_internal_nodes: bool
        Default is to only show tip Nodes on either side of a
        bipartition, but internal Nodes can be included as well. In 
        this case the feature should likely be set to "idx", None, or
        some other feature for which internal Nodes have unique values.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
    >>> sorted(iter_bipartitions(tree, 'name')))
    >>> # [(('r0', 'r1'), ('r2', 'r3', 'r4')),
    >>> #  (('r3', 'r4'), ('r0', 'r1', 'r2'))]
    >>> #
    >>> sorted(iter_bipartitions(tree, 'name', exclude_root=False)))
    >>> # [(('r0', 'r1'), ('r2', 'r3', 'r4')),
    >>> #  (('r3', 'r4'), ('r0', 'r1', 'r2')),
    >>> #  (('r3', 'r4'), ('r0', 'r1', 'r2'))]
    """
    # TODO: MAYBE faster to store as feature type rather than tformat 
    # repeatedly in every yield iteration.

    # store cache of desc below each node to reduce traversals
    cache = {}

    # if exclude_root_split then do not include root in node_set
    node_set = set(tree)
    if exclude_root and (tree.is_rooted()):
        node_set -= {tree.treenode}
    topnode = tree.nnodes - int(tree.is_rooted()) - int(exclude_root)

    # a funtion to return a tuple of Nodes in the requested feature
    if feature is not None:
        tformat = lambda x: tuple(getattr(i, feature) for i in x)
    else:
        tformat = tuple

    # iterate over all nodes
    for nidx in range(0, topnode):
        node = tree[nidx]
        if node.is_leaf():
            below = cache[node] = {node}
            if exclude_singletons:
                continue
        else:
            below = set.union(*([{node}] + [cache[i] for i in node.children]))
            cache[node] = below

        # get all nodes not under this split
        other = node_set - cache[node]

        # if excluding internal Nodes
        if exclude_internal_nodes:
            below = (i for i in below if i._idx < tree.ntips)
            other = (i for i in other if i._idx < tree.ntips)

        # sort biparts by idx label within each side
        # Note: idx labels do not work for this b/c we want the same
        # biparts to be returned regardless of Node rotations.
        below = sorted(below, key=lambda x: x.name)
        other = sorted(other, key=lambda x: x.name)

        # sort biparts to (shorter, longer), or by name if same len.
        lenb = len(below)
        leno = len(other)
        if lenb < leno:
            clade1, clade2 = tformat(below), tformat(other)
        elif leno < lenb:
            clade1, clade2 = tformat(other), tformat(below)
        else:
            clade1, clade2 = sorted((other, below), key=lambda x: x[0].name)
            clade1, clade2 = tformat(clade1), tformat(clade2)

        # yield the sorted biparts
        if clade1:    
            yield clade1, clade2        

def iter_quartets(
    tree: ToyTree, 
    feature: Optional[str]='name', 
    collapse: bool=False,
    ) -> Iterator:
    """Generator to yield quartets induced by resolved edges in a tree.

    Parameters
    ----------
    feature: str
        Feature to return to represent Nodes on either side of a
        bipartition. Default is "name", but custom features can
        also be returned, or use None to return Node objects.
    collapse: bool
        If True quartets are returned as (0, 1, 2, 3), else they are
        returned as ((0, 1), (2, 3)).

    Example
    -------
    >>> for qrt in tree.iter_quartets():
    >>>     print(qrt)
    >>> # (0, 2, 4, 6)
    >>> # (0, 2, 4, 7)
    >>> # ...
    """
    # sort by name if Node objects, else by custom feature.
    if feature is None:
        sort_func = lambda x: sorted(x, key=lambda i: i[0].name)
    else:
        sort_func = lambda x: sorted(x, key=lambda i: i[0])

    # format into ((),()) or (,,,).
    if collapse:
        format_func = lambda x: tuple(sort_func(x[0]) + sort_func(x[1]))
    else:
        format_func = lambda x: tuple(sort_func(x))

    observed = set([])
    for below, above in iter_bipartitions(tree, feature=feature):
        # generator to sample 2 from either side of bipart
        pairgen = itertools.product(
            itertools.combinations(below, 2),
            itertools.combinations(above, 2),
        )
        for qrt in pairgen:
            qrt = format_func(qrt)
            if qrt not in observed:
                observed.add(qrt)
                yield qrt
    del observed

def iter_splits(tree: ToyTree) -> Iterator:
    """

    Example
    -------
    {(0, 1), (2, 3), (4, 5), (6, 7)}
    {(0, 1), (2, 3), (4, 5), (6, 8)}    
    """
    tips = set(tree.get_tip_labels())
    cache = {}
    
    # iterate over node (edges)
    for node in tree.traverse("idxorder"):
        
        # if tip simply store its info
        if node.is_leaf():
            cache[node] = {node.name}
            continue
       
        # get tips from each child, and store union to this node
        vals = [cache[i] for i in node.children]
        cache[node] = set.union(*vals)

    for nidx in range(tree.ntips, tree.nnodes - 1):
        node = tree[nidx]
        below = [cache[i] for i in node.children]

        # 2. upper edge iterates over sister clades & clade of others
        above = []
        for sis in node.get_sisters():
            if sis.children:
                above.append(set.union(*[cache[i] for i in sis.children]))
            else:
                above.append(cache[sis])
                
        # add others
        others = (tips - set.union(*above)) - set.union(*below)
        above.append(others)
        for x1, x2 in itertools.product(
            itertools.combinations(below, 2),
            itertools.combinations(above, 2),
            ):
            if all([x1[0], x1[1], x2[0], x2[1]]):
                yield x1[0], x1[1], x2[0], x2[1]     
            # for x in itertools.product(x1[0], x1[1], x2[0], x2[1]):
                # yield nidx, x     
        
    if tree.is_rooted():
        #if not tree.treenode.children[0].is_leaf():
        for x1, x2 in itertools.product(
            itertools.combinations(tree.treenode.children[0].children, 2),
            itertools.combinations(tree.treenode.children[1].children, 2),
            ):
            if all([x1[0], x1[1], x2[0], x2[1]]):        
                yield cache[x1[0]], cache[x1[1]], cache[x2[0]], cache[x2[1]]        
            #print(cache[x1[0]], cache[x1[1]], cache[x2[0]], cache[x2[1]])
            # for x in itertools.product(cache[x1[0]], cache[x1[1]], cache[x2[0]], cache[x2[1]]):
                # yield tree.treenode.idx, x

def iter_split_quartets(tree: ToyTree) -> Iterator:
    r"""Generator yields Tuples of tips induced by each tree edge.

    Split quartets are samples of 4 tips in a tree that are drawn 
    from the four subclades induced by a resolved edge in the tree. 
    This set of quartets is only a subset of those returned by 
    `iter_quartets`, which includes quartets induced by *any* edge
    in a tree. The split quartets are sampled from the splits in
    `iter_splits`.

    Example
    -------
    >>> for qrt in tree.iter_split_quartets():
    >>>     print(qrt)
    >>> # ((0, 2, 4, 6))
    >>> # ((1, 2, 4, 6))
    >>> # ...

    See Also
    --------
    - `toytree.enumerate.iter_quartets`
    - `ToyTree.iter_quartets`
    """
    for split in iter_splits(tree):
        for tips in itertools.product(*split):
            yield tips[0], tips[1], tips[2], tips[3]



if __name__ == "__main__":

    import toytree

    BTREE = toytree.rtree.unittree(ntips=5, seed=123)
    ITREE = toytree.rtree.unittree(ntips=5, seed=321)
    UTREE = toytree.rtree.unittree(ntips=5, seed=123).unroot()
    for TREE in (BTREE, ITREE, UTREE):
        TREE.treenode.draw_ascii()
        print("\nBIPARTS-----------")
        # for i in iter_bipartitions(TREE, feature='name', exclude_internal_nodes=False):
        #     print(i)
        for i in iter_bipartitions(TREE, feature='name', exclude_internal_nodes=True):
            print(i)

        print("\nROOTED BIPARTS-----------")
        # for i in iter_bipartitions(TREE, feature='name', exclude_internal_nodes=False, exclude_root_split=False):
        #     print(i)
        for i in iter_bipartitions(TREE, feature='name', exclude_internal_nodes=True, exclude_root=False):
            print(i)

        print("\nQUARTETS-----------")
        for i in iter_quartets(TREE):
            print(i)

        print("\nSPLITS-----------")
        for i in iter_splits(TREE):
            print(i)

        print("\nSPLITS-QUARTETS-----------")
        for i in iter_split_quartets(TREE):
            print(i)

        print("===================================================")


    raise SystemExit()
    # does every placement of the root yield a different topology?
    for edge in UTREE:
        if edge.up:
            t = UTREE.root(edge)
            t.treenode.draw_ascii()
            print(list(iter_bipartitions(t, 'name', exclude_root=False)))


    # FIXME: make None work.
    # for i in iter_bipartitions(TREE, feature=None):
        # print(i)

