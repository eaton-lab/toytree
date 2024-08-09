#!/usr/bin/env python

"""Get quad splits on a tree as (child1, child2, sister, up) tuples.

Methods
-------
Get sets of Nodes from the four subclades of each edge in a tree.
>>> tree._iter_quadripartition_sets()
# (({0}, {1}), ({2}, {3, 4})), ...

Get tuples of Nodes for each quartet induced by quadripartitions in a tree.
>>> tree.iter_quadripartitions()
# (((0,), (1,)), ((2,), (3, 4))), ...

Get tuples of Nodes for each quartet induced by quadripartitions in a tree.
>>> tree.iter_quadripartitions('idx', sort=True, collapse=True)
# ({'c'}, {'d'}, {'a', 'b'}, {'e', 'f'})
"""

from typing import TypeVar, Iterator, Tuple, Optional, Set, Callable, Sequence
import itertools
from loguru import logger
from toytree import Node, ToyTree
from toytree.core.apis import TreeEnumAPI, add_subpackage_method, add_toytree_method
# from toytree.utils import ToytreeError

logger = logger.bind(name="toytree")
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
    """Yield a tuple of sets of tips for each quadripartition.

    Quadripartitions are yielded in Node idxorder traversal as a tuple
    of two tuples of two sets, e.g., `(({e0},{e1}), ({e2},{e3}))`,
    representing sets of (tip) Nodes descending from each of the four
    edges subtending a focal edge. In this example, the focal edge
    splits e0,e1 from e2,e3. Note the use of sets to indicate that the
    items are not sorted.

    Notes
    -----
    - The order of yielded quadripartition sets is in Node idx order.
    - The order of partitions within a quad is (child-left, child-right,
    sister, up) unless at root in an unrooted tree, then it is
    (child-left, child-right, sister-left, sister-right)

    Parameters
    ----------
    tree: ToyTree
        A tree to extract edge sets from.
    feature: str or None
        Feature to represent Nodes in returned sets. Default is 'name'
        to use Node name strings. None will return Node objects.
    contract_partitions: bool
        If True then each partition is contracted to show only the
        first Node closest to the edge.
    include_internal_nodes: bool
        If True then all nodes in each partition are shown, whether it
        is internal or a tip Node. If False then only tips are shown.
        Note: This option is overriden if contract_partitions=True in
        which case the closest Node is shown whether or not it is a tip.

    Examples
    --------
    >>> newick = "((a,b)X,((c,d)Y,e)Z)R;"
    >>> tree = toytree.tree(newick)
    >>> tree.draw(ts='r');

    >>> sorted(_iter_quadripartition_sets(tree))
    >>> # (({'a'}, {'b'}), ({'d', 'c'}, {'e'}))
    >>> # (({'c'}, {'d'}), ({'e'}, {'a', 'b'}))

    >>> kwargs = dict(include_internal_nodes=True)
    >>> sorted(_iter_quadripartition_sets(tree, **kwargs))
    >>> # ({'a'}, {'b'}), ({'c', 'Y', 'd'}, {'e'}))
    >>> # (({'c'}, {'d'}), ({'e'}, {'a', 'X', 'b'}))

    >>> kwargs = dict(contract_partitions=True)
    >>> sorted(iter_edge_quadripartition_sets(tree, **kwargs))
    >>> # (({'a'}, {'b'}), ({'Y'}, {'e'}))
    >>> # (({'c'}, {'d'}), ({'e'}, {'Z'}))
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
        nodes = set(tree.get_nodes()[:tree.ntips])

    # iterate over internal nodes/edges in the tree
    topnode = tree.nnodes - 2 if tree.is_rooted() else tree.nnodes - 1
    for node in tree[tree.ntips: topnode]:

        # get >= 2 sets of nodes for children below
        below = [cache[i] for i in node.children]

        # if up is root then choose (child, child, sister, sister)
        if node._up.is_root():
            above = []
            sisters = node.get_sisters()
            if len(sisters) > 1:
                for sis in sisters:
                    above.append(cache[sis])
            else:
                for sis_child in sisters[0]._children:
                    above.append(cache[sis_child])

            # contract...

            # create generator
            _below = itertools.combinations(below, 2)
            _above = itertools.combinations(above, 2)
            qiter = itertools.product(_below, _above)

        # else choose (child, child, sister, up)
        else:
            # get >= 1 sets of nodes above edge, sister to children.
            up_down = [cache[sis] for sis in node.get_sisters()]

            # get set nodes above edge
            up_up = [nodes - {node, node._up} - set.union(*up_down + below)]

            # unless contracting, then just the parent
            if contract_partitions:
                up_up = [{node._up}]

            # create generator
            _below = itertools.combinations(below, 2)
            _up_down = itertools.combinations(up_down, 1)
            _up_up = itertools.combinations(up_up, 1)
            qiter = itertools.product(_below, _up_down, _up_up)

        # expand qiter(2, 2) or qiter(2, 1, 1)
        for below, above, *other in qiter:
            if len(above) == 1:
                x1, x2 = below
                x3 = above[0]
                x4 = other[0][0]
            else:
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
    """Generator of quadripartitions (Nodes on four clades of a split)

    Quadripartitions represent the splits in a tree. Many algorithms
    compare tips (or internal Nodes) split into the four parts of a
    quadripartition to compute metrics on trees. This function aims to
    provide a flexible and fast framework for yielding quadripartitions
    in various formats.

    Notes
    -----
    - qparts are generated in Node idx traversal order.
    - By default qparts are formatted as a tuple of two tuples of sets,
    e.g., ((set1, set2), (set3, set4)), but can be optionally collapsed
    into the format (set1, set2, set3, set4) where the split in the
    middle is implicit.
    - The partitions can be returned as other types than sets using
    the `type` arg, in which case the items within a part will be
    sorted by names.
    - The order of the two tuples is (below, above) given the traversal
    order of edges, but can instead be sorted consistently to allow for
    comparisons by sorting by len and then names using the `sort` arg.

    Parameters
    ----------
    feature: str
        Feature to return to represent Nodes in partitions. Default is
        "name". None will return Node objects. Any other Node feature,
        such as "idx", is also supported. Note the feature arg does not
        affect the order in which partitions are sorted (see `sort`).
    include_internal_nodes: bool
        If True then internal Node names/features are included in
        addition to tip Nodes.
    contract_partitions: bool
        If True then clades are represented only by the Node (internal
        or tip) closest to the quadripartition edge.
    collapse: bool
        If True then the format is simplified from `((a,b),(x,y))`
        to `(a,b,x,y)` where the split ab|xy is still implicit.
    type: Callable
        The type of collection used to represent a partition. Default
        is `set` to return a tuple of sets, but another useful option
        is `tuple`, which returns a tuple of tuples. The latter
        collection can be converted into a set of quadripartitions.
    sort: bool
        If False, tuple clades are returned as (child, parent) order
        given the topology and rooting in Node idx order traversal. If
        sort=True, qpartitions are instead always sorted first by len,
        e.g., (fewer, longer) and if the same len, then next by the
        lowest alphanumeric tip name, e.g., ({'a', 'b'}, {'c', 'd'}).
        If the requested partition `type` is sortable (i.e., not a set)
        then items within a partition are also consistently sorted.

    Examples
    --------
    >>> tree = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")

    >>> # default: parts w/ tip names as (child, parent) in idx order
    >>> list(tree.enum.iter_quadripartitions())
    >>> # [(({'c'}, {'d'}), ({'e', 'f'}, {'b', 'a'}))
    >>> #  (({'e'}, {'f'}), ({'d', 'c'}, {'b', 'a'}))
    >>> #  (({'d', 'c'}, {'e', 'f'}), ({'a'}, {'b'}))]

    >>> # same order, but as int idx labels including internal Nodes
    >>> list(tree.enum.iter_quadripartitions(
    >>>     feature='idx',
    >>>     include_internal_nodes=True,
    >>> ))
    >>> # [(({2}, {3}), ({4, 5, 7}, {0, 1})),
    >>> #  (({4}, {5}), ({2, 3, 6}, {0, 1})),
    >>> #  (({2, 3, 6}, {4, 5, 7}), ({0}, {1}))]

    >>> # args to get consistently sorted qparts regardless of rooting
    >>> sorted(tree.enum.iter_quadripartitions(type=tuple, sort=True))
    >>> # ((('a',), ('b',)), (('c', 'd'), ('e', 'f')))
    >>> # ((('c',), ('d',)), (('a', 'b'), ('e', 'f')))
    >>> # ((('e',), ('f',)), (('a', 'b'), ('c', 'd')))

    >>> # example: easy comparison of consistently sorted sets
    >>> x = set(tree.root('a').enum.iter_quadripartitions(type=tuple, sort=True))
    >>> y = set(tree.root('e').enum.iter_quadripartitions(type=tuple, sort=True))
    >>> assert x == y
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
        kwargs['feature'] = None
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
    """Returns node name to use while sorting tip and internal nodes."""
    if node.is_leaf():
        return node.name
    return "".join(sorted(node.get_leaf_names())[::-1])


def format_quadripartition(
    below: Set,
    other: Set,
    type: Callable,
    sort: bool,
) -> Tuple[Sequence[Node], Sequence[Node]]:
    """Sort bipartitions ({Node, Node}, {Node, Node}).

    - First sorted by len: ({Node, Node}, {Node, Node, Node})
    - Then by min Node name: ({'a', 'z'}, {'b', 'x'})
    - which also requires assigning names to internal Nodes when present
    based on their descendant tips: ({'a', 'z', 'za'}, {'b', 'x', 'xb'})
    - if the type is not set then items within partitions are
    consistently sorted: (['a', 'z', 'za'], ['b', 'x', 'xb']) and can
    be converted to final type (e.g., tuple) in later steps.
    """
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

    results = iter_quadripartitions(tree, type=list, sort=True, include_internal_nodes=True)
    
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
