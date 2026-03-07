#!/usr/bin/env python

"""Quartet enumeration utilities.

This module provides generators for unresolved and resolved quartets.
Resolved quartets represent unrooted 4-tip splits, for example ``ab|cd``.

Examples
--------
>>> tree = toytree.tree("(a,b,((c,d),(e,f)));")
>>> next(tree.enum.iter_quartets())
({'c', 'd'}, {'e', 'f'})
"""

import itertools
from typing import Callable, Iterator, Optional, Set, Tuple, TypeVar

from loguru import logger

from toytree import Node, ToyTree
from toytree.core.apis import TreeEnumAPI, add_subpackage_method, add_toytree_method

Query = TypeVar("Query")


__all__ = [
    "_iter_unresolved_quartet_sets",
    "_iter_quartet_sets",
    "iter_quartets",
]


def _iter_unresolved_quartet_sets(tree: ToyTree, feature: str = None) -> Iterator[Set]:
    """Yield unresolved combinations of four tips.

    This returns all ``n choose 4`` tip combinations and does not encode a
    split relation among the four tips.

    Parameters
    ----------
    tree : ToyTree
        Tree from which tip combinations are sampled.
    feature : str or None, default=None
        Node attribute to return for each tip. If None, Node objects are
        returned.

    Yields
    ------
    set
        Set of four tip values.

    Examples
    --------
    >>> tree = toytree.tree("((a,b),c,d);")
    >>> list(tree.enum._iter_unresolved_quartet_sets("name"))
    [{'a', 'b', 'c', 'd'}]
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
    """Yield resolved quartets as 4-tuples in ``ij|xy`` orientation.

    Parameters
    ----------
    tree : ToyTree
        Input tree.
    feature : str or None, default=None
        Node feature to return. If None, Node objects are returned.
    quadripartitions : bool, default=False
        If True, return only quartets induced by quadripartition splits.
        If False, return quartets induced by bipartitions.

    Yields
    ------
    tuple
        Tuple ``(i, j, x, y)`` implying split ``ij|xy``.

    Examples
    --------
    >>> tree = toytree.tree("(a,b,((c,d),(e,f)));")
    >>> next(tree.enum._iter_quartet_sets(feature="name"))
    ('c', 'd', 'e', 'f')
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
    """Yield quartets induced by tree splits.

    Quartets encode unrooted 4-tip relationships in split form, e.g.,
    ``ab|cd``. This function formats those quartets as sets, tuples, or
    lists, and can optionally collapse partition structure.

    Parameters
    ----------
    tree : ToyTree
        Input tree.
    feature : str or None, default="name"
        Node attribute returned for each sampled tip. If None, Node
        objects are returned.
    type : Callable, default=set
        Collection type used for partitions (e.g., ``set``, ``tuple``,
        ``list``).
    sort : bool, default=False
        If True, sort values within partitions and between partitions
        by name.
    collapse : bool, default=False
        If True, return each quartet as one collection of four values.
        If False, return two partition collections.
    quadripartitions : bool, default=False
        If True, restrict quartets to those induced by quadripartitions.

    Yields
    ------
    object
        Quartet representation formatted according to ``type``,
        ``feature``, ``sort``, and ``collapse``.

    Notes
    -----
    ``collapse=True`` cannot be used with ``type=set`` because split
    orientation would be lost. In this case a warning is logged and
    ``collapse`` is treated as False.

    Examples
    --------
    >>> tree = toytree.tree("(a,b,((c,d),(e,f)));")
    >>> next(tree.iter_quartets())
    ({'c', 'd'}, {'e', 'f'})
    >>> next(tree.iter_quartets(type=tuple, sort=True, collapse=True))
    ('c', 'd', 'e', 'f')
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
    for qrt in iter_quartets(
        tree,
        type=tuple,
        collapse=False,
        sort=True,
        quadripartitions=True,
    ):
        print(qrt)
    print("")

    print("type=tuple, collapse=True, sort=True")
    for qrt in iter_quartets(
        tree,
        type=tuple,
        collapse=True,
        sort=True,
        quadripartitions=True,
    ):
        print(qrt)
    print("")

    print("default")
    for qrt in iter_quartets(tree):
        print(qrt)
    print("")
