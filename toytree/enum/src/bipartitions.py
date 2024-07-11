#!/usr/bin/env python

"""Split trees into bipartitions and return in a variety of formats.

Methods
-------
iter_bipartitions

"""

from typing import TypeVar, Iterator, Tuple, Optional, Set, Callable, Sequence
from loguru import logger
from toytree import Node, ToyTree
from toytree.core.apis import TreeEnumAPI, add_subpackage_method, add_toytree_method

logger = logger.bind(name="toytree")
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
    normalize: bool = False,
) -> Iterator[Tuple[Set[Node], Set[Node]]]:
    """Generator to yield bipartitions as tuples of two sets of Nodes.

    Bipartitions are yielded in idxorder as Tuple[set, set] objects
    where each represents nodes on either side of an edge. Each is
    ordered as (child, parent) pairs such that the first set contains
    Nodes below the edge and the second Nodes above the edge.

    The order in which bipartitions are yielded, as well as the order
    of the two partitions within each bipartition, depends on the tree
    topology and rooting. To get collections of bipartitions that are
    the same for a given topology regardless of its rooting see the
    options in `.iter_bipartitions`.

    Parameters
    ----------
    feature: str or None
        Option to represent Nodes in bipartitions by a feature, such
        as 'name' or 'idx'. If None then Node objects are returned.
    include_singleton_partitions: bool
        If True then singleton splits (e.g., (A | B,C,D)) are included
        in the result. By default these are excluded since it is
        implicit that one exists for every tip Node in a tree.
    include_internal_nodes: bool
        Default is to only show tip Nodes on either side of a
        bipartition, but internal Nodes can be included as well. In
        this case the results are easier to interpret if internal Nodes
        have names assigned, else you can set the 'feature' arg to
        None, or 'idx', to return Node objects, or a unique feature.

    Examples
    --------
    >>> newick = "(((a,b)X,((c,d)Y,e)Z)R;"
    >>> tree = toytree.tree(newick)

    >>> list(tree.enum._iter_bipartition_sets("name""))
    >>> # [({'c', 'd'}, {'b', 'e', 'f', 'z'}),
    >>> #  ({'e', 'f'}, {'b', 'c', 'd', 'z'}),
    >>> #  ({'c', 'd', 'e', 'f'}, {'b', 'z'})]

    >>> list(tree.enum._iter_bipartition_sets("idx", include_internal_nodes=True))
    >>> # [({2, 3, 6}, {0, 1, 4, 5, 7, 8, 9}),
    >>> #  ({4, 5, 7}, {0, 1, 2, 3, 6, 8, 9}),
    >>> #  ({2, 3, 4, 5, 6, 7, 8}, {0, 1, 9})]
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
    """Generator of bipartitions (Nodes on either side of edges).

    Bipartitions represent the splits in a tree. Many algorithms compare
    tips (or internal Nodes) on either side of each split to compute
    metrics on trees. This function aims to provide a flexible and fast
    framework for yielding bipartitions in various formats.

    Notes
    -----
    - Bipartitions are generated in Node idx traversal order.
    - Bipartitions are formatted as a tuple of two items, each of
    which is referred to as a partition.
    - The order of partitions, e.g. (part1, part2) can be toggled using
    the argument `sort`.
    - The type used to represent a partition can be toggled using the
    argument `type`. Common formats are `set` or `tuple`.

    Parameters
    ----------
    feature: str
        Feature to return to represent Nodes on either side of a
        bipartition. Default is "name". None will return Node objects.
        Any other Node feature, such as "idx" can also be used. Note
        the feature arg does not affect the order in which partitions
        or bipartitions are returned/sorted (see `sort` argument below).
    include_singleton_partitions: bool
        If True then singleton splits (e.g., (A | B,C,D)) are included
        in the result. By default these are excluded since it is
        implicit that one exists for every tip Node in a tree.
    include_internal_nodes: bool
        Default is to only show tip Nodes on either side of a
        bipartition, but internal Nodes can be included as well. In
        this case the results are easier to interpret if the returned
        values have unique features (e.g., feature=None or 'idx').
    type: Callable
        The type of collection used to represent a partition. Default
        is `set` to return a tuple of sets, but another useful option
        is `tuple`, which returns a tuple of tuples. The latter
        collection can be converted into a set of bipartitions.
    sort: bool
        If False, bipartitions are returned as (child, parent) order
        given the topology and rooting in Node idx order traversal. If
        sort=True, bipartitions are instead always sorted first by len,
        e.g., (fewer, longer) and if the same len, then next by the
        lowest alphanumeric tip name, e.g., ({'a', 'b'}, {'c', 'd'}).
        If the requested partition `type` is sortable (i.e., not a set)
        then items within a partition are also consistently sorted.

    Examples
    --------
    >>> tree = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")

    >>> # default: biparts w/ tip names as (child, parent) in idx order
    >>> list(tree.iter_bipartitions())
    >>> # [({'c', 'd'}, {'a', 'b', 'e', 'f'}),
    >>> #  ({'e', 'f'}, {'a', 'b', 'c', 'd'}),
    >>> #  ({'c', 'd', 'e', 'f'}, {'a', 'b'})]

    >>> # same order, but as int idx labels including all Nodes
    >>> list(tree.iter_bipartitions(
    >>>     feature='idx',
    >>>     include_internal_nodes=True,
    >>>     include_singleton_partitions=True,
    >>> ))
    >>> # [({0}, {1, 2, 3, 4, 5, 6, 7, 8, 9}),
    >>> #  ({1}, {0, 2, 3, 4, 5, 6, 7, 8, 9}),
    >>> #  ({2}, {0, 1, 3, 4, 5, 6, 7, 8, 9}),
    >>> #  ({3}, {0, 1, 2, 4, 5, 6, 7, 8, 9}),
    >>> #  ({4}, {0, 1, 2, 3, 5, 6, 7, 8, 9}),
    >>> #  ({5}, {0, 1, 2, 3, 4, 6, 7, 8, 9}),
    >>> #  ({2, 3, 6}, {0, 1, 4, 5, 7, 8, 9}),
    >>> #  ({4, 5, 7}, {0, 1, 2, 3, 6, 8, 9}),
    >>> #  ({2, 3, 4, 5, 6, 7, 8}, {0, 1, 9})]

    >>> # args to get consistently sorted biparts regardless of rooting
    >>> sorted(tree.iter_bipartitions(type=tuple, sort=True))
    >>> # [(('a', 'b'), ('c', 'd', 'e', 'f')),
    >>> #  (('c', 'd'), ('a', 'b', 'e', 'f')),
    >>> #  (('e', 'f'), ('a', 'b', 'c', 'd'))]

    >>> # convert consistent bipartitions to sets for easy comparison
    >>> x = set(tree.root('a').iter_bipartitions(type=tuple, sort=True))
    >>> y = set(tree.root('e').iter_bipartitions(type=tuple, sort=True))
    >>> assert x == y
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
    # the Name feature regarldess of what the returned feature will be.
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
    """Returns node name to use while sorting tip and internal nodes."""
    if node.is_leaf():
        return node.name
    return "".join(sorted(node.get_leaf_names())[::-1])


def _format_bipartition(
    below: Set,
    other: Set,
    type: Callable,
    sort: bool,
) -> Tuple[Sequence[Node], Sequence[Node]]:
    """Sort bipartitions ({Node, Node}, {Node, Node}).

    If sort is True this first sorts the two sides of the split by
    length, or by lowest alphanumeric name if they are same length.
    Example: ({Node, Node}, {Node, Node, Node})
    Example: ({'a', 'z'}, {'b', 'x'})
    This also requires assigning names to internal nodes when present,
    based on their descendant tip names.
    Example: ({'a', 'z', 'za'}, {'b', 'x', 'xb'})
    If the type is not set then items within partitions are
    consistently sorted.
    Example: (['a', 'z', 'za'], ['b', 'x', 'xb']) and can
    be converted to final type (e.g., tuple) in later steps.
    """
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
