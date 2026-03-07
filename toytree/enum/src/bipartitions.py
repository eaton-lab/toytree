#!/usr/bin/env python

"""Bipartition enumeration utilities.

Bipartitions are edge-induced splits of a tree into two node sets.
This module provides iterators that return those splits in configurable
formats for downstream comparison and distance calculations.

Examples
--------
>>> tree = toytree.tree("(a,b,((c,d),(e,f)));")
>>> next(tree.iter_bipartitions())
({'c', 'd'}, {'a', 'b', 'e', 'f'})
"""

from typing import Callable, Iterator, Optional, Sequence, Set, Tuple, TypeVar

from toytree import Node, ToyTree
from toytree.core.apis import TreeEnumAPI, add_subpackage_method, add_toytree_method

Query = TypeVar("Query")

__all__ = [
    "iter_bipartitions",
    "_iter_bipartition_sets",
]


@add_subpackage_method(TreeEnumAPI)
def _iter_bipartition_sets(
    tree: ToyTree,
    feature: Optional[str] = "name",
    include_singleton_partitions: bool = False,
    include_internal_nodes: bool = False,
) -> Iterator[Tuple[Set[Node], Set[Node]]]:
    """Yield bipartitions as ``(below, other)`` pairs of sets.

    Each yielded tuple represents one edge split where ``below`` is the
    descendant side of the edge and ``other`` is the complement.

    Parameters
    ----------
    tree : ToyTree
        Tree from which bipartitions are extracted.
    feature : str or None, default="name"
        Feature used to represent nodes in returned partitions, such as
        ``"name"`` or ``"idx"``. If None, Node objects are returned.
    include_singleton_partitions : bool, default=False
        If True, singleton splits (for example, ``A | B,C,D``) are
        included. By default these are excluded since one singleton split
        exists for every tip and is often implicit.
    include_internal_nodes : bool, default=False
        By default only tips are shown on either side of each split. If
        True, internal nodes are included as well. In that case, results are
        easiest to interpret if returned values are unique (for example,
        ``feature=None`` or ``feature="idx"``).

    Yields
    ------
    tuple[set, set]
        Bipartition as ``(below, other)``.

    Examples
    --------
    >>> newick = "(a,b,((c,d)Y,e)Z)R;"
    >>> tree = toytree.tree(newick)
    >>> list(tree.enum._iter_bipartition_sets("name"))
    [({'c', 'd'}, {'a', 'b', 'e'}), ({'c', 'd', 'e'}, {'a', 'b'})]
    >>> list(tree.enum._iter_bipartition_sets("idx", include_internal_nodes=True))
    [({2, 3, 5}, {0, 1, 4, 6, 7}), ({2, 3, 4, 5, 6}, {0, 1, 7})]
    """
    # store cache of desc below each node to reduce traversals
    cache = {}

    # nodes set to iterate over. Do not include the root.
    node_set = set(tree)
    topnode = tree.nnodes - 1

    # do not include root node in node_set if tree is rooted.
    if tree.is_rooted():
        node_set -= {tree.treenode}
        topnode -= 1

    # iterate over all nodes in idx order building cache as it goes.
    for node in tree[:topnode]:
        if node.is_leaf():
            below = cache[node] = {node}
            if not include_singleton_partitions:
                continue
        else:
            below = set.union(*([{node}] + [cache[i] for i in node.children]))
            cache[node] = below

        # get all nodes not under this split
        other = node_set - cache[node]

        # if excluding internal Nodes
        if not include_internal_nodes:
            below = set(i for i in below if i._idx < tree.ntips)
            other = set(i for i in other if i._idx < tree.ntips)

        # yield biparts except at root in unrooted trees: ({}, {all})
        if feature is None:
            yield below, other
        else:
            yield (
                set(getattr(i, feature) for i in below),
                set(getattr(i, feature) for i in other),
            )


@add_toytree_method(ToyTree)
@add_subpackage_method(TreeEnumAPI)
def iter_bipartitions(
    tree: ToyTree,
    feature: Optional[str] = "name",
    include_singleton_partitions: bool = False,
    include_internal_nodes: bool = False,
    type: Callable = set,
    sort: bool = False,
) -> Iterator[Tuple[Sequence, Sequence]]:
    """Yield edge bipartitions in configurable formats.

    Bipartitions represent nodes on either side of an edge split. This method
    can return split sides as sets, tuples, or lists, and can optionally
    canonicalize ordering for rooting-invariant comparisons.

    Notes
    -----
    - Results are generated in node-index traversal order.
    - With ``sort=False`` partitions are returned as ``(child, parent)``.
    - With ``sort=True`` partitions are canonicalized by size/name.

    Parameters
    ----------
    tree : ToyTree
        Tree from which bipartitions are extracted.
    feature : str or None, default="name"
        Feature used to represent nodes on either side of each split.
        Default is ``"name"``. If None, Node objects are returned. Any
        other node feature such as ``"idx"`` can also be used. The chosen
        feature does not affect ordering of returned partitions (see
        ``sort``).
    include_singleton_partitions : bool, default=False
        If True, singleton splits (for example, ``A | B,C,D``) are
        included. By default these are excluded since they are often
        implicit.
    include_internal_nodes : bool, default=False
        By default only tips are shown on either side of a split. If True,
        internal nodes are also included. In that case, returned values are
        easier to interpret if they are unique (for example,
        ``feature=None`` or ``feature="idx"``).
    type : Callable, default=set
        Collection type used to represent each partition. The default
        ``set`` returns a tuple of sets. Another common choice is
        ``tuple``, which returns a tuple of tuples and can be converted into
        a set of canonicalized bipartitions.
    sort : bool, default=False
        If False, bipartitions are returned as ``(child, parent)`` in node
        index traversal order for the current rooting. If True, partitions
        are sorted first by size and then by minimum alphanumeric name.
        When ``type`` is sortable (for example, ``tuple``), items within each
        partition are also sorted consistently.

    Yields
    ------
    tuple[Sequence, Sequence]
        Bipartition pair formatted according to ``type``, ``feature``,
        and ``sort``.

    Examples
    --------
    >>> tree = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")

    default: tip names as (child, parent) in idx order
    >>> list(tree.iter_bipartitions())
    ... # [({'c', 'd'}, {'a', 'b', 'e', 'f'}),
    ... #  ({'e', 'f'}, {'a', 'b', 'c', 'd'}),
    ... #  ({'c', 'd', 'e', 'f'}, {'a', 'b'})]

    consistently sorted output for rooting-invariant comparison
    >>> sorted(tree.iter_bipartitions(type=tuple, sort=True))
    ... # [(('a', 'b'), ('c', 'd', 'e', 'f')),
    ... #  (('c', 'd'), ('a', 'b', 'e', 'f')),
    ... #  (('e', 'f'), ('a', 'b', 'c', 'd'))]

    >>> x = set(tree.root("a").iter_bipartitions(type=tuple, sort=True))
    >>> y = set(tree.root("e").iter_bipartitions(type=tuple, sort=True))
    >>> x == y
    True
    """
    kwargs = dict(
        tree=tree,
        feature=feature,
        include_singleton_partitions=include_singleton_partitions,
        include_internal_nodes=include_internal_nodes,
    )

    # fastest approach returns bipart consistently as (child, parent)
    # and get feature from _iter_bipartition_sets if requested.
    # yield ({part1}, {part2})
    if (not sort) and (type == set):  # noqa E721
        for below, other in _iter_bipartition_sets(**kwargs):
            yield below, other

    # slower approach sorts bipart alphanumerically by tip Node names.
    # sort requires first getting objects as Nodes so we can access
    # the Name feature regardless of what the returned feature will be.
    else:
        # yield as type(*Nodes) or as type(feature(*Nodes))
        if feature is not None:
            def tformat(node_tuple):
                return type(getattr(i, feature) for i in node_tuple)
        else:
            tformat = type

        # iterate over bipartitions and order items within
        kwargs['feature'] = None
        for below, other in _iter_bipartition_sets(**kwargs):
            # optional: sort biparts by len or min name
            # always: if not type==set sort within by name
            # returned as sets or sorted lists
            clade1, clade2 = _format_bipartition(below, other, type, sort)

            # return as requested feature and type
            yield tformat(clade1), tformat(clade2)


def _build_node_names_for_sorting(node: Node) -> str:
    """Return a stable node-name sort key for tips and internal nodes."""
    if node.is_leaf():
        return node.name
    return "".join(sorted(node.get_leaf_names())[::-1])


def _format_bipartition(
    below: Set,
    other: Set,
    type: Callable,
    sort: bool,
) -> Tuple[Sequence[Node], Sequence[Node]]:
    """Format and optionally sort the two sides of a bipartition."""
    blen = len(below)
    olen = len(other)

    # if type == set then items within a partition do not need to be
    # sorted, but part1 vs part2 does still need it.
    if sort and (type == set):  # noqa E721
        if blen < olen:
            return below, other
        elif olen < blen:
            return other, below
        else:
            # min names
            bmin = min(i.name for i in below)
            omin = min(i.name for i in other)
            if bmin < omin:
                return below, other
            else:
                return other, below

    # if sort == False and type != set then items within partition need
    # to be sorted, but part1 vs part2 does not b/c we want to maintain
    # the (child, parent) order.
    if not sort:
        return (
            sorted(below, key=_build_node_names_for_sorting),
            sorted(other, key=_build_node_names_for_sorting),
        )

    # if sort == True and type != set then call sort on each partition
    # as well as between the two partitions.
    if blen < olen:
        return (
            sorted(below, key=_build_node_names_for_sorting),
            sorted(other, key=_build_node_names_for_sorting),
        )
    elif olen < blen:
        return (
            sorted(other, key=_build_node_names_for_sorting),
            sorted(below, key=_build_node_names_for_sorting),
        )
    else:
        # min names
        bmin = min(_build_node_names_for_sorting(i) for i in below)
        omin = min(_build_node_names_for_sorting(i) for i in other)
        if bmin < omin:
            return (
                sorted(below, key=_build_node_names_for_sorting),
                sorted(other, key=_build_node_names_for_sorting),
            )
        else:
            return (
                sorted(other, key=_build_node_names_for_sorting),
                sorted(below, key=_build_node_names_for_sorting),
            )


if __name__ == "__main__":

    import toytree

    tree = toytree.rtree.unittree(10, seed=123)

    for bipart in tree.iter_bipartitions(
        'idx', sort=True, include_singleton_partitions=True):
        print(bipart)
