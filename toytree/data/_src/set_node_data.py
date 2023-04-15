#!/usr/bin/env python

"""Function to set data to all Node objects in a tree.

"""

from typing import Union, Mapping, Sequence, Any, TypeVar
from loguru import logger
from toytree import ToyTree, Node
from toytree.core.apis import add_toytree_method
from toytree.data._src.expand_node_mapping import expand_node_mapping
from toytree.utils import ToytreeError


Query = TypeVar("Query", int, str, Node)
logger = logger.bind(name="toytree")


INVALID_SET_NODE_DATA_TYPE = """
Invalid 'data' arg to set_node_data(). Must be either a Mapping or a Series
of length nnodes. This appears to be a Series of len={} while nnodes={}.\
"""

# one of the following types:
# - Mapping[Query: Any], e.g., `data={0: 3, 1: 4}`
# - Series[Any] in Node idx order w/ len=nnodes, e.g., `data=range(tree.nnodes)`
# """


@add_toytree_method(ToyTree)
def set_node_data(
    tree: ToyTree,
    feature: str,
    data: Union[Mapping[Query, Any], Sequence[Any]] = None,
    default: Any = None,
    inherit: bool = False,
    inplace: bool = False,
) -> ToyTree:
    """Create or modify features (data) set to Nodes in a ToyTree.

    Features can be set on all or only some nodes. In the latter case
    a value for nodes with missing features can be imputed when you
    call the function :meth:`~toytree.core.tree.ToyTree.get_node_data`.
    Some features used internally are protected from modification
    (e.g., idx, up, children), but other base features such as name,
    dist, height, and support can be modified, and any new feature can
    be created or modified.

    Parameters
    -----------
    feature: str
        The name of the node attribute to create or modify.
    data: Mapping or Series
        A mapping of {Node Query: value} for one or more Nodes, or a
        Series[value] for all Nodes in Node idx traversal order.
    default: Any
        Optionally set a default value to all Nodes not included in
        data mapping.
    inherit: bool
        If inherit is True then feature values entered as a mapping to
        internal Nodes will also be applied to their descendant Nodes,
        allowing for easy assignment of values to clades.
    inplace: bool
        If True the tree data is modified inplace and returned, else
        the original tree data is unchanged and a copy is returned.

    Notes
    -----
    Data can be set to Nodes by entering `data` as either a Mapping or
    as a Series of values. These two options differ slightly and are
    described below.

    Mapping: Values can be set by providing a 'mapping' (e.g., dict or
    pd.Series) with Node queries (i.e., Node, idx label, str name, or
    name regular expression) mapped to feature values for any number
    of Nodes. The 'default' option can be used to set a value to all
    Nodes not specified in the mapping. Otherwise, any Nodes not in
    the data arg will not have values set, and will maintain either no
    attribute for this feature, or any existing attribute.

    Series: Alternatively, data can be set to Nodes on a tree as a
    Series (e.g., List, np.ndarray) of values instead of a Mapping.
    In this case the Series must be len=nnodes, and the values should
    be listed in Node idx traversal order. The 'default' arg value will
    still apply to any Nodes given a value of None.

    See Also
    --------
    :meth:`~toytree.core.tree.ToyTree.get_node_data`.
    :meth:`~toytree.core.tree.ToyTree.set_tip_data`.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=10)

    >>> # set data to Nodes as a Mapping
    >>> new = tree.set_node_data(feature="Ne", default=5000)
    >>> new = tree.set_node_data(feature="Ne", data={0:1e5, 1:1e6, 2:1e3})
    >>> new = tree.set_node_data(feature="Ne", data={0:1e5, 1:1e6}, default=5000)
    >>> new = tree.set_node_data(feature="Ne", data={'r0':1e5, 'r1':1e6})
    >>> new = tree.set_node_data(feature="Ne", data={'~r[0-5]+': 1e5})
    >>> new = tree.set_node_data("state", {10: "A", 11: "B"}, inherit=True")

    >>> # or, set data to Nodes as a Series
    >>> new = tree.set_node_data("X", range(tree.nnodes))
    """
    # immutable; do not allow modifying topology attributes
    if feature in ["idx", "up", "children"]:
        raise ToytreeError(
            f"cannot modify '{feature}' feature because it affects the "
            "tree topology. To modify topology see `toytree.mod` "
            "subpackage functions.")

    # try to convert data to a Dict[Node, Any] if it is a dict-like
    if data is None:
        mapping = {}
    else:
        try:
            mapping = dict(data)
            mapping = expand_node_mapping(tree, mapping)
        except (ValueError, TypeError):
            if not len(data) == tree.nnodes:
                msg = INVALID_SET_NODE_DATA_TYPE.format(len(data), tree.nnodes)
                logger.error(msg)
                raise ToytreeError(msg)
            mapping = dict(zip(range(tree.nnodes), data))
            mapping = expand_node_mapping(tree, mapping)

        # report non-TypeError mapping exception
        except Exception as exc:
            raise ToytreeError(INVALID_SET_NODE_DATA_TYPE) from exc

    # make a copy of ToyTree to return
    tree = tree if inplace else tree.copy()

    # copy mapping to {int: value} and optionally map to descendants
    ndict = {}

    # sort {Node: feat} keys into reverse idx order for inherit=True
    nkeys = sorted(mapping, reverse=True, key=lambda x: x._idx)

    # fill new dict w/ inherited values
    for node in nkeys:
        value = mapping[node]
        ndict[node._idx] = value
        for desc in node.iter_descendants():
            ndict[desc._idx] = value

    # map {Node: default} for Nodes not in ndict
    if default is not None:
        for node in tree:
            if node._idx not in ndict:
                ndict[node._idx] = default

    # special mod submodule method for height modifications
    if feature == "height":
        height_map = {i._idx: j for (i, j) in ndict.items() if j is not None}
        return tree.mod.edges_set_node_heights(height_map, inplace=inplace)

    # dist is immutable, but allow it here, and do an update.
    if feature == "dist":
        feature = "_dist"

    # add value to Nodes as a feature. If the value can be copied,
    # e.g., a dict, array, etc., then assign copies, otherwise if
    # this object is changed it affects the value of multiple Nodes
    for nidx, value in ndict.items():
        if hasattr(value, 'copy'):
            setattr(tree[nidx], feature, value.copy())
        else:
            setattr(tree[nidx], feature, value)

    # if dist was mod'd then must call update
    if feature == "_dist":
        tree._update()
    return tree


if __name__ == "__main__":

    import toytree
    import numpy as np
    toytree.set_log_level("INFO")

    tree = toytree.rtree.unittree(ntips=10)
    new_tree = set_node_data(tree, feature="Ne", default=5000)
    new_tree = set_node_data(tree, feature="Ne", data={0: 1e5, 1: 1e6, 2: 1e3})
    new_tree = set_node_data(tree, feature="Ne", data={0: 1e5, 1: 1e6}, default=5000)
    new_tree = set_node_data(tree, feature="Ne", data={'r0': 1e5, 'r1': 1e6})
    new_tree = set_node_data(tree, feature="Ne", data={'r0': 1e5, '~r[2-5]+': 1e6})
    new_tree = set_node_data(tree, feature="Ne", data={11: 1e5}, inherit=True)
    new_tree = set_node_data(tree, feature="Ne", data={11: 1e5})
    new_tree = set_node_data(tree, feature="Ne", data=range(tree.nnodes))
    new_tree = set_node_data(tree, "Ne", {11: "red"}, default="blue", inherit=True)
    new_tree = set_node_data(tree, "Ne", {5: 5, 6: 6})

    # typeerror,valuerrror
    new_tree = set_node_data(tree, "Ne", ['a', 'b'] + [np.nan] * (tree.nnodes - 2))
    # new_tree = tree.set_node_data(
    #     feature="state",
    #     mapping={10: "A", 11: "B"},
    #     inherit=True,
    # )
    print(new_tree.get_node_data("Ne"))
