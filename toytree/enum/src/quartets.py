#!/usr/bin/env python

"""Generators to sample quartets of tips from a tree.

The primary function `iter_quartets` can be used as a generator to
yield quartet subtrees from a larger tree. This function is quite
fast and includes options for sorting the output, and transforming
its format to return Node objects, names, or any arbitrary feature
of Nodes. See examples.

Methods
-------
Get fast unordered sets of all combinations of 4 tip Nodes in a tree
>>> tree.enum._iter_unresolved_quartet_sets()   # {0, 1, 2, 3}, ...

Get name-ordered tuples of Nodes for each quartet induced by bipartitions in a tree.
>>> tree.enum.iter_quartets()                   # ((0, 1), (2, 3)), ...

See Also
--------
Get number of quartets induced by the splits in a tree.
>>> tree.enum.get_n_quartets()                  # 5

Format
------
Quartets represent a sample from a bipartition or quadripartition
where there is a split, e.g. `AB|CD`, separating to sets of items.
The order of the items within each partition of the quartet is not
often of interest, but it is nice to have a consistent sort option in
case it is useful.

Supported:
- ({'a', 'b'}, {'c', 'd'})  # type=set, collapse=False; sort affects order of p1,p2
- (('a', 'b'), ('c', 'd'))  # type=tuple, collapse=False; sort affects order of p1,p2 and within each p
- ('a', 'b', 'c', 'd')      # type=tuple, collapse=True; same as above, imagine middle split is still there.

Not supported:
- ({'a', 'b', 'c', 'd'})    # type=set, collapse=True; split info lost.
"""

from typing import TypeVar, Iterator, Tuple, Optional, Set, Callable
import itertools
from loguru import logger
from toytree import Node, ToyTree
from toytree.core.apis import TreeEnumAPI, add_subpackage_method, add_toytree_method

logger = logger.bind(name="toytree")
Query = TypeVar("Query")


__all__ = [
    "_iter_unresolved_quartet_sets",
    "_iter_quartet_sets",
    "iter_quartets",
]


def _iter_unresolved_quartet_sets(tree: ToyTree, feature: str = None) -> Iterator[Set]:
    """Generator to yield all combinations of four tip Nodes.

    This is simpler and faster than toytree.enum.iter_quartets because
    it does not find the resolution of quartets, but rather only finds
    all possible combinations. Note the intentional use of a set to
    indicate they are unordered.
    """
    # select function to format returned quartet set
    if feature is None:
        sformat = set
    else:
        def sformat(qrt) -> Set[str]:
            return set(getattr(node, feature) for node in qrt)
    for qrt in itertools.combinations(tree[:tree.ntips], 4):
        yield sformat(qrt)


@add_subpackage_method(TreeEnumAPI)
def _iter_quartet_sets(
    tree: ToyTree,
    feature: Optional[str] = None,
    quadripartitions: bool = False,
) -> Iterator[Tuple[Node, Node, Node, Node]]:
    """Generator to yield quartets induced by edges in a tree.

    This yields all quartets (4-sample subtrees) that exist within
    a larger tree. The set of possible quartets is not affected by
    tree rooting, but is affected by collapsed edges (polytomies),
    which reduce the number of quartets.

    Quartets are returned as Tuple[Node, Node, Node, Node], or Tuple
    of the requested features of Nodes, where e.g. ('a', 'b', 'c', 'd')
    implies the quartet `ab|cd`. The order in which quartets are
    yielded depends on the topology and rooting. The order of yielded
    quartets is in Node idx traversal order, where the first two Nodes
    are below the edge, and the second two above.

    Parameters
    ----------
    feature: str
        Feature used to represent Nodes on either side of bipartitions.
        Default is "name". None will return Node objects. Other Node
        features can be used but be aware if using quartets to compare
        among trees that 'idx' changes depending on topology, and other
        features may not be unique among Nodes.
    quadripartitions: bool
        If True then quartets are only returned that are induced by
        quadripartitite splits in a the tree. This is a subset of the
        quartets induced by bipartitions, since the tip Nodes must come
        from four different clades from each edge/split.

    Example
    -------
    >>> tree = toytree.rtree.unittree(5, seed=123)

    >>> sorted(tree.iter_quartets())
    >>> # (('r0', 'r1'), ('r2', 'r3'))
    >>> # (('r0', 'r1'), ('r2', 'r4'))
    >>> # (('r0', 'r1'), ('r3', 'r4'))
    >>> # (('r0', 'r2'), ('r3', 'r4'))
    >>> # (('r1', 'r2'), ('r3', 'r4'))

    """
    # find quartets induced by splits in the tree. This is necessary
    # compared to a simple call of `itertools.combinations(names, 4)`
    # because we indicate which pair of nodes is on which side of each
    # split. We also reduce number of quartets if any polytomies exist.

    # default args for iter_[bipart,qparts] to get Tuple[Node, ...]
    kwargs = dict(feature=feature, type=set, sort=False)

    # generate subset of quartets from quadripartitions
    if quadripartitions:
        for (i, j), (x, y) in tree.enum.iter_quadripartitions(**kwargs):
            pairgen = itertools.product(i, j, x, y)
            for i, j, x, y in pairgen:
                yield i, j, x, y

    # generate full collection of quartets from bipartitions
    else:
        observed = set()
        for below, above in tree.iter_bipartitions(**kwargs):
            # generator to sample 2 from either side of each bipart
            pairgen = itertools.product(
                itertools.combinations(below, 2),
                itertools.combinations(above, 2),
            )
            for (i, j), (x, y) in pairgen:
                qrt = frozenset((i, j, x, y))
                if qrt not in observed:
                    yield i, j, x, y
                    observed.add(qrt)


@add_toytree_method(ToyTree)
@add_subpackage_method(TreeEnumAPI)
def iter_quartets(
    tree: ToyTree,
    feature: Optional[str] = 'name',
    type: Callable = set,
    sort: bool = False,
    collapse: bool = False,
    quadripartitions: bool = False,
) -> Iterator:
    """Generator to yield quartets induced by edges in a tree.

    This yields all quartets (4-sample subtrees) that exist within
    a larger tree. The set of possible quartets is not affected by
    tree rooting, but is affected by collapsed edges (polytomies),
    which reduce the number of quartets.

    Quartets are returned as Tuple[Node, Node, Node, Node], or Tuple
    of the requested features of Nodes, where e.g. ('a', 'b', 'c', 'd')
    implies the quartet `ab|cd`. The order in which quartets are
    yielded depends on the topology and rooting, and is in Node idx
    traversal order, where the first two Nodes are below the edge, and
    the second two above. This can be changed to a consistent name
    sorted order for each split partition using `sort=True`.

    Parameters
    ----------
    feature: str
        Feature used to represent Nodes on either side of bipartitions.
        Default is "name". None will return Node objects. Other Node
        features can be used but be aware if using quartets to compare
        among trees that 'idx' changes depending on topology, and other
        features may not be unique among Nodes.
    type: Callable
        The type of collection used to represent a partition. Default
        is `set` to return a tuple of sets, but another useful option
        is `tuple`, which returns a tuple of tuples.
    sort: bool
        If False, quartets are returned with Nodes spanning edges as
        (below, below, above, above) in idx traversal order given the
        topology and rooting. If sort=True, partitions are instead
        always sorted alphanumerically within and between partitions.
    collapse: bool
        If True then quartets are returned as a single tuple, e.g.,
        (0, 1, 2, 3), else they are returned as a tuple of tuples,
        e.g., ((0, 1), (2, 3)). In either case, the induced split is
        implied to occur in the middle, e.g., 0,1 vs 2,3. Collapse arg
        cannot be combined with type=set.
    quadripartition: bool
        If True then quartets are only returned that are induced by
        quadripartitite splits in a the tree. This is a subset of the
        quartets induced by bipartitions, since the tip Nodes must come
        from four different clades from each edge/split.

    Example
    -------
    >>> tree = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")

    >>> # get quartets for each (child, parent) edge in idx order
    >>> list(tree.iter_quartets())
    >>> # [({'c', 'd'}, {'e', 'f'}),
    >>> #  ({'c', 'd'}, {'a', 'f'}),
    >>> #  ({'c', 'd'}, {'b', 'f'}),
    >>> #  ({'c', 'd'}, {'a', 'e'}),
    >>> #  ({'c', 'd'}, {'b', 'e'}),
    >>> #  ({'c', 'd'}, {'a', 'b'}),
    >>> #  ({'e', 'f'}, {'a', 'd'}),
    >>> #  ({'e', 'f'}, {'c', 'd'}),
    >>> #  ({'e', 'f'}, {'b', 'd'}),
    >>> #  ({'e', 'f'}, {'a', 'c'}),
    >>> #  ({'e', 'f'}, {'a', 'b'}),
    >>> #  ({'e', 'f'}, {'b', 'c'}),
    >>> #  ({'d', 'e'}, {'a', 'b'}),
    >>> #  ({'d', 'f'}, {'a', 'b'}),
    >>> #  ({'c', 'd'}, {'a', 'b'}),
    >>> #  ({'e', 'f'}, {'a', 'b'}),
    >>> #  ({'c', 'e'}, {'a', 'b'}),
    >>> #  ({'c', 'f'}, {'a', 'b'})]

    >>> # get same quartets consistently ordered and in simpler format
    >>> sorted(tree.iter_quartets(type=tuple, sort=True, collapse=True))
    >>> # [('a', 'b', 'c', 'd'),
    >>> #  ('a', 'b', 'c', 'd'),
    >>> #  ('a', 'b', 'c', 'e'),
    >>> #  ('a', 'b', 'c', 'f'),
    >>> #  ('a', 'b', 'd', 'e'),
    >>> #  ('a', 'b', 'd', 'f'),
    >>> #  ('a', 'b', 'e', 'f'),
    >>> #  ('a', 'b', 'e', 'f'),
    >>> #  ('a', 'c', 'e', 'f'),
    >>> #  ('a', 'd', 'e', 'f'),
    >>> #  ('a', 'e', 'c', 'd'),
    >>> #  ('a', 'f', 'c', 'd'),
    >>> #  ('b', 'c', 'e', 'f'),
    >>> #  ('b', 'd', 'e', 'f'),
    >>> #  ('b', 'e', 'c', 'd'),
    >>> #  ('b', 'f', 'c', 'd'),
    >>> #  ('c', 'd', 'e', 'f'),
    >>> #  ('c', 'd', 'e', 'f')]
    """
    # disallowed combinations
    if (type == set) and (collapse is True):  # noqa: E721
        collapse = False
        logger.warning(
            "collapse argument cannot be used with type=set, using collapse=False")

    # quartet args
    kwargs = dict(tree=tree, feature=None, quadripartitions=quadripartitions)
    for i, j, x, y in _iter_quartet_sets(**kwargs):

        # sort within by min name
        if type != set:  # noqa: E721
            if i.name > j.name:
                j, i = i, j
            if x.name > y.name:
                x, y = y, x

        # sort between by min name
        if sort:
            if i.name > x.name:
                # print(f"SORTING - {i.name},{x.name} to {x.name},{i.name}")
                i, j, x, y = x, y, i, j

        # convert to feature
        if feature:
            i, j, x, y = (getattr(z, feature) for z in (i, j, x, y))

        # return as collapsed or not.
        if collapse:
            yield type((i, j, x, y))
        else:
            yield type((i, j)), type((x, y))


if __name__ == "__main__":

    import toytree

    tree = toytree.rtree.unittree(6, seed=123, random_names=True)

    print("type=set, collapse=False, sort=False")
    for qrt in iter_quartets(tree, type=set, collapse=False, sort=False):
        print(qrt)
    print("")

    print("type=set, collapse=True, sort=False")
    for qrt in iter_quartets(tree, type=set, collapse=True, sort=False):
        print(qrt)
    print("")

    print("type=tuple, collapse=True, sort=False")
    for qrt in iter_quartets(tree, type=tuple, collapse=True, sort=False):
        print(qrt)
    print("")

    print("\n=======================\n")

    print("type=set, collapse=False, sort=False")
    for qrt in iter_quartets(tree, type=set, collapse=False, quadripartitions=True):
        print(qrt)
    print("")

    print("type=tuple, collapse=False, sort=False")
    for qrt in iter_quartets(tree, type=tuple, collapse=False, quadripartitions=True):
        print(qrt)
    print("")

    print("type=tuple, collapse=True, sort=False")
    for qrt in iter_quartets(tree, type=tuple, collapse=True, quadripartitions=True):
        print(qrt)
    print("")

    print("type=tuple, collapse=False, sort=True")
    for qrt in iter_quartets(tree, type=tuple, collapse=False, sort=True, quadripartitions=True):
        print(qrt)
    print("")

    print("type=tuple, collapse=True, sort=True")
    for qrt in iter_quartets(tree, type=tuple, collapse=True, sort=True, quadripartitions=True):
        print(qrt)
    print("")

    print("default")
    for qrt in iter_quartets(tree):
        print(qrt)
    print("")