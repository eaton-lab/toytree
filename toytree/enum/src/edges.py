#!/usr/bin/env python

"""Edge enumeration utilities.

This module provides helpers to iterate over tree edges as ``(child, parent)``
pairs, or collect them as an array / DataFrame table.

Examples
--------
>>> tree = toytree.tree("(a,b,((c,d),(e,f)));")
>>> next(tree.iter_edges("idx"))
(0, 6)
"""

from typing import Iterator, Optional, Tuple, Union

import numpy as np
import pandas as pd

from toytree import Node, ToyTree
from toytree.core.apis import TreeEnumAPI, add_subpackage_method, add_toytree_method

__all__ = [
    "iter_edges",
]


@add_toytree_method(ToyTree)
@add_subpackage_method(TreeEnumAPI)
def iter_edges(
    self,
    feature: Optional[str] = None,
    include_root: bool = False,
) -> Iterator[Tuple[Node, Node]]:
    """Yield edges in ``(child, parent)`` orientation.

    Edges are produced in node index traversal order for the current rooting.
    To represent edges as clade splits, use ``iter_bipartitions`` instead.

    Parameters
    ----------
    feature : str or None, default=None
        Node feature to return instead of Node objects (e.g., ``"idx"`` or
        ``"name"``).
    include_root : bool, default=False
        If True on rooted trees, append the root edge as ``(root, None)``.
        On unrooted trees this option has no effect.

    Yields
    ------
    tuple
        Edge tuple as ``(child, parent)`` where values are Node objects or
        selected feature values.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(5, seed=123)
    >>> list(tree.iter_edges(feature="idx"))[:3]
    [(0, 5), (1, 5), (2, 6)]
    >>> list(tree.iter_edges(feature="idx", include_root=True))[-1]
    (8, None)
    """
    if feature:
        for node in self[:-1]:
            yield (getattr(node, feature), getattr(node._up, feature))
    else:
        for node in self[:-1]:
            yield (node, node._up)

    # optionally return root edge
    if self.is_rooted() and include_root:
        node = self[-1]
        if feature:
            yield (getattr(node, feature), None)
        else:
            yield (node, None)


@add_toytree_method(ToyTree)
def get_edges(
    self,
    feature: Optional[str] = None,
    df: bool = False,
    include_root: bool = False,
) -> Union[np.ndarray, pd.DataFrame]:
    """Return all edges as an array or DataFrame.

    Edges are collected from ``iter_edges`` and retain the same
    ``(child, parent)`` orientation and traversal order.

    Parameters
    ----------
    feature : str or None, default=None
        Node feature to return for edge values. If None, Node objects are
        returned.
    df : bool, default=False
        If True, return a pandas DataFrame with columns ``child`` and
        ``parent``.
    include_root : bool, default=False
        If True on rooted trees, include the root edge as ``(root, None)``.

    Returns
    -------
    numpy.ndarray or pandas.DataFrame
        Edge table in ``(child, parent)`` format.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(5, seed=123)
    >>> tree.get_edges("idx").shape
    (8, 2)
    >>> tree.get_edges("idx", df=True).columns.tolist()
    ['child', 'parent']

    See Also
    --------
    ToyTree.iter_edges
    """
    edges = list(self.iter_edges(feature=feature, include_root=include_root))
    if df:
        return pd.DataFrame(edges, columns=["child", "parent"])
    return np.array(edges)


if __name__ == "__main__":
    import toytree

    tree = toytree.rtree.unittree(10, seed=123)
    edges = list(tree.iter_edges())
    print(edges)
    print(tree.get_edges("idx", df=1))

    # not ideal, but the include_root option is available.
    # print(tree.get_edges('idx', df=1, include_root=True))
    # print(tree.get_edges('idx', df=0, include_root=True))
    # print(tree.get_edges(include_root=True))
