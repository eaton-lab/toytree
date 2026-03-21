#!/usr/bin/env python

"""Quadripartition enumeration utilities.

Quadripartitions describe four clades around an edge split. This module
provides iterators that return those clades in configurable formats.

Examples
--------
>>> tree = toytree.tree("(a,b,((c,d),(e,f)));")
>>> next(tree.enum.iter_quadripartitions(type=tuple, sort=True))
((('a',), ('b',)), (('c', 'd'), ('e', 'f')))
"""

import itertools
from typing import Callable, Iterator, Optional, Sequence, Set, Tuple, TypeVar

from toytree import Node, ToyTree
from toytree.core.apis import TreeEnumAPI, add_subpackage_method

# from toytree.utils import ToytreeError

Query = TypeVar("Query")
# Node = TypeVar("Node")

__all__ = [
    "_iter_quadripartition_sets",
    "iter_quadripartitions",
    # "iter_edge_quadripartition_sets",
]


@add_subpackage_method(TreeEnumAPI)
def _iter_quadripartition_sets(
    tree: ToyTree,
    feature: Optional[str] = "name",
    contract_partitions: bool = False,
    include_internal_nodes: bool = False,
) -> Iterator[Tuple[Tuple[Set, Set], Tuple[Set, Set]]]:
    """Yield quadripartitions as ``((part1, part2), (part3, part4))``.

    Each yielded value represents the four clades around a focal edge.
    By default, clades contain tip names as sets.

    Notes
    -----
    - Quadripartitions are generated in node index traversal order.
    - The default orientation is ``(child-left, child-right, sister, up)``.
      Near the root of an unrooted tree, ``up`` is represented by two sister
      sides instead.

    Parameters
    ----------
    tree : ToyTree
        Tree from which quadripartitions are extracted.
    feature : str or None, default="name"
        Node feature to return. If None, Node objects are returned.
    contract_partitions : bool, default=False
        If True, each partition is represented only by its closest node.
    include_internal_nodes : bool, default=False
        If True, include internal nodes along with tips in partitions.
        Ignored when ``contract_partitions=True``.

    Examples
    --------
    >>> tree = toytree.tree("((a,b)X,((c,d)Y,e)Z)R;")
    >>> next(tree.enum._iter_quadripartition_sets())
    (({'a'}, {'b'}), ({'c', 'd'}, {'e'}))
    >>> next(tree.enum._iter_quadripartition_sets(feature="idx"))
    (({0}, {1}), ({2, 3}, {4}))
    """
    # tree = tree.unroot()
    cache = {}

    # build a cache of descendants for each Node.
    for node in tree[:-1]:
        # if tip simply store its info
        if node.is_leaf():
            cache[node] = {node}
            continue

        # get tips from each child, and store union to this node
        vals = [cache[i] for i in node.children]

        # cache only the closest Node (exclude_internal_nodes ignored)
        if contract_partitions:
            cache[node] = {node}

        # cache tip Nodes with or without internal Nodes
        else:
            # cache only the tip Nodes
            if not include_internal_nodes:
                cache[node] = set.union(*vals)
            # cache all nodes including internals
            else:
                cache[node] = set.union(*vals) | {node}

    # get set of all relevant nodes for set diffs below
    if include_internal_nodes:
        nodes = set(cache)
    else:
        nodes = set(tree.get_nodes()[: tree.ntips])

    # iterate over internal nodes/edges in the tree
    topnode = tree.nnodes - 2 if tree.is_rooted() else tree.nnodes - 1
    for node in tree[tree.ntips : topnode]:
        # get >= 2 sets of nodes for children below
        below = [cache[i] for i in node.children]

        # if up is root then choose (child, child, sister, sister)
        if node.up.is_root():
            above = []
            sisters = node.get_sisters()
            if len(sisters) > 1:
                for sis in sisters:
                    above.append(cache[sis])
            else:
                for sis_child in sisters[0].children:
                    above.append(cache[sis_child])

            # create generator from all choose-2 clade pairings on both sides.
            qiter = itertools.product(
                itertools.combinations(below, 2),
                itertools.combinations(above, 2),
            )

        # else choose (child, child, sister, up)
        else:
            # collect all clades above the edge: sisters at parent, plus the
            # remainder of the tree above parent. For multifurcations this
            # can include >2 clades, so we must take all choose-2 pairings.
            up_down = [cache[sis] for sis in node.get_sisters()]

            # get set nodes above edge
            up_up = [nodes - {node, node.up} - set.union(*up_down + below)]

            # unless contracting, then just the parent
            if contract_partitions:
                up_up = [{node.up}]

            above = up_down + up_up
            qiter = itertools.product(
                itertools.combinations(below, 2),
                itertools.combinations(above, 2),
            )

        # expand qiter(2, 2)
        for below, above in qiter:
            x1, x2 = below
            x3, x4 = above

            # require all to exclude root in unrooted tree: ()
            if feature is None:
                yield ((x1, x2), (x3, x4))
            else:
                yield (
                    tuple({getattr(j, feature) for j in i} for i in (x1, x2)),
                    tuple({getattr(j, feature) for j in i} for i in (x3, x4)),
                )


@add_subpackage_method(TreeEnumAPI)
def iter_quadripartitions(
    tree: ToyTree,
    feature: Optional[str] = "name",
    contract_partitions: bool = False,
    include_internal_nodes: bool = False,
    collapse: bool = False,
    type: Callable = set,
    sort: bool = False,
) -> Iterator[Tuple]:
    """Yield quadripartitions in configurable formats.

    Quadripartitions represent four clades around an edge split. This method
    can return clades as sets, tuples, or lists and can optionally collapse
    output to a 4-part tuple.

    Notes
    -----
    - Results are generated in node index traversal order.
    - The default format is ``((part1, part2), (part3, part4))``.
    - ``collapse=True`` returns ``(part1, part2, part3, part4)``.
    - ``sort=True`` provides rooting-independent ordering.

    Parameters
    ----------
    tree : ToyTree
        Tree from which quadripartitions are extracted.
    feature : str or None, default="name"
        Node feature to return for values in each partition.
    contract_partitions : bool, default=False
        If True, each partition is represented by the closest node.
    include_internal_nodes : bool, default=False
        If True, include internal nodes in partitions.
    collapse : bool, default=False
        If True, return a flat 4-part tuple.
    type : Callable, default=set
        Collection type to use for each partition.
    sort : bool, default=False
        If True, sort partitions and values for stable comparisons.

    Yields
    ------
    tuple
        Quadripartition formatted according to ``type``, ``collapse``,
        ``feature``, and ``sort``.

    Examples
    --------
    >>> tree = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")
    >>> next(tree.enum.iter_quadripartitions())
    (({'c'}, {'d'}), ({'e', 'f'}, {'a', 'b'}))
    >>> next(tree.enum.iter_quadripartitions(type=tuple, sort=True, collapse=True))
    (('a',), ('b',), ('c', 'd'), ('e', 'f'))
    """
    kwargs = dict(
        tree=tree,
        feature=feature,
        contract_partitions=contract_partitions,
        include_internal_nodes=include_internal_nodes,
    )

    # fastest approach returns bipart consistently as (child, parent)
    # and get feature from _iter_bipartition_sets if requested.
    # yield ({part1}, {part2})
    if (not sort) and (type == set):
        for below, other in _iter_quadripartition_sets(**kwargs):
            if collapse:
                yield below[0], below[1], other[0], other[1]
            else:
                yield below, other

    # slower approach sorts parts alphanumerically by tip Node names.
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
        kwargs["feature"] = None
        for below, other in _iter_quadripartition_sets(**kwargs):
            # optional: sort qparts by len or min name (p3, p2), (p1, p0)
            # always: if not type==set sort within by name
            # returned as sets or sorted lists

            clade1 = format_quadripartition(below[0], below[1], type, sort)
            clade2 = format_quadripartition(other[0], other[1], type, sort)

            p1 = tformat(clade1[0])
            p2 = tformat(clade1[1])
            p3 = tformat(clade2[0])
            p4 = tformat(clade2[1])

            if sort:
                plen1 = len(p1) + len(p2)
                plen2 = len(p3) + len(p4)
                if plen1 > plen2:
                    p1, p2, p3, p4 = p3, p4, p1, p2
                elif plen1 == plen2:
                    if min(min(p1), min(p2)) > min(min(p3), min(p4)):
                        p1, p2, p3, p4 = p3, p4, p1, p2
            if collapse:
                yield (p1, p2, p3, p4)
            else:
                yield ((p1, p2), (p3, p4))


def _build_node_names_for_sorting(node: Node) -> str:
    """Return a stable sort key for tip and internal nodes."""
    if node.is_leaf():
        return node.name
    return "".join(sorted(node.get_leaf_names())[::-1])


def format_quadripartition(
    below: Set,
    other: Set,
    type: Callable,
    sort: bool,
) -> Tuple[Sequence[Node], Sequence[Node]]:
    """Sort a pair of clades for quadripartition output formatting."""
    blen = len(below)
    olen = len(other)

    # if type == set then items within a partition do not need to be
    # sorted, but part1 vs part2 does still need it.
    if sort and (type == set):
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

    # newick = "((a,b)X,((c,d)Y,e)Z)R;"
    # tree = toytree.tree(newick).root("c")

    # tree = toytree.rtree.baltree(12, seed=1234).unroot()
    tree = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")

    results = iter_quadripartitions(
        tree, type=list, sort=True, include_internal_nodes=True
    )

    for item in results:
        print(item[1][0][0])

    # tree._draw_browser(ts='r')
    # for bipart in _iter_quadripartition_sets(tree, include_internal_nodes=True):
    # for part in iter_quadripartitions(tree,):
    # print(part)

    # args to get consistently sorted biparts regardless of rooting
    # tree = tree.root("X")
    # for i in sorted(iter_quadripartitions(tree, type=set, sort=True)):
    #     print(i)
    # [(('a', 'b'), ('c', 'd', 'e', 'f')),
    #  (('c', 'd'), ('a', 'b', 'e', 'f')),
    #  (('e', 'f'), ('a', 'b', 'c', 'd'))]

    # tree = tree.root("X")
    # for i in sorted(iter_quadripartitions(tree, sort=True, collapse=True)):
    #     print(i)

    # convert consistent bipartitions to sets for easy comparison
    # x = set(tree.root('a').enum.iter_quadripartitions(type=tuple, sort=True))
    # y = set(tree.root('e').enum.iter_quadripartitions(type=tuple, sort=True))
    # assert x == y

    # tree = toytree.rtree.unittree(6, seed=123).unroot()
    # c1, *_ = tree.draw('p')

    # for bipart in _iter_quadripartition_sets(tree, 'idx'):#contract_partitions=True):
    #     print(bipart)

    # print("+========================================================")
    # tree = toytree.rtree.unittree(6, seed=123).root("r0")
    # c2, *_ = tree.draw(ts='p')

    # for bipart in _iter_quadripartition_sets(tree, 'idx'):#contract_partitions=True):
    #     print(bipart)

    # toytree.utils.show([c1, c2])
