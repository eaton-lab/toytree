#!/usr/bin/env python

"""Function to return a mapping {Node: feature}.

This function is pretty fast while also allowing for regex matching
in Node queries. It is used in many places.
"""

from typing import TypeVar, Mapping, Any
import numpy as np
from toytree import Node, ToyTree
from toytree.utils.src.exceptions import NODE_NOT_IN_TREE_ERROR


Query = TypeVar("Query", Node, int, str)


def expand_node_mapping(tree: ToyTree, mapping: Mapping[Query, Any]) -> Mapping[Node, Any]:
    """Return a mapping of {Nodes: feature} by expanding Node queries.

    This function is similar to `get_nodes`, but in addition to
    expanding a query into Nodes it also keep their mapping to
    features. This function is used inside other toytree functions
    such as `set_node_data`.

    Parameters
    ----------
    mapping: Mapping[Query, Any]
        A mapping (e.g., dict, pd.Series) of Node queries to feature
        values. Queries can be Node objects, idx labels, str names, or
        regular expressions matching mulitple string names, indicated
        by using a '~' str prefix.

    Notes
    -----
    You can `practice your regex here: <https://pythex.org/>`_
    The order in which Nodes are returned may be different than the
    order of queries.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(8, seed=123)
    >>> mapping = {0: 1, 'r1': 2, '~r[2-3]+': 4)
    >>> tree.set_node_data('x', mapping, inplace=True)
    >>> tree.get_node_data('x')
    >>> 0     0.0
    >>> 1     0.0
    >>> 2     0.0
    >>> 3     0.0
    >>> 4     1.0
    >>> 5     2.0
    >>> 6     NaN
    >>> 7     NaN
    >>> 8     NaN
    >>> 9     NaN
    >>> 10    NaN
    >>> 11    NaN
    >>> 12    NaN
    >>> 13    NaN
    >>> 14    NaN
    """
    nodes = {}
    names = {}
    for key, value in dict(mapping).items():
        if isinstance(key, int):
            nodes[tree[key]] = value
        elif isinstance(key, Node):
            if key not in tree:
                raise ValueError(NODE_NOT_IN_TREE_ERROR)
            nodes[key] = value
        elif isinstance(key, str):
            names[key] = value  # names are expanded to Nodes below.
        elif isinstance(key, np.integer):
            nodes[tree[key]] = value
        else:
            raise TypeError(f"query type {type(key)} not supported.")

    # match Node names as a group so we only need to perform one
    # tree traversal. Each query can return multiple regex hits.
    for name, feature in names.items():
        matched = set(tree._iter_nodes_by_name_match(name))
        for node in matched:
            nodes[node] = feature
    # return expanded mapping
    return nodes


if __name__ == "__main__":

    import toytree
    tree = toytree.rtree.unittree(8)
    mapping = {"~r[0-3]+": 0, "r4": 1, tree[5]: 2}
    emap = expand_node_mapping(tree, mapping)
    print(emap)
    # tree.set_node_data('x', emap, inplace=True)
    # print(tree.get_node_data('x'))
