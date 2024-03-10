#!/usr/bin/env python

"""Tree edge modification functions.

Tree edge modification functions set new 'dist' values to one or more
Nodes in a ToyTree.

Note
----
All 'edge' functions in `mod` are written so that the returned ToyTrees
are ready to be plotted. This means they update the cached heights
(Node._height attributes). These functions do not change the topology,
so idx values and x positions do not need to be updated.
"""

from typing import Dict, TypeVar, Optional
from loguru import logger
import numpy as np
from toytree import Node
from toytree.core.apis import TreeModAPI, add_subpackage_method

logger = logger.bind(name="toytree")
ToyTree = TypeVar("ToyTree")
Query = TypeVar("Query", str, int, Node)


__all__ = [
    "edges_scale_to_root_height",
    "edges_slider",
    "edges_multiplier",
    "edges_extend_tips_to_align",
    "edges_set_node_heights",
]


@add_subpackage_method(TreeModAPI)
def edges_scale_to_root_height(
    tree: ToyTree,
    treeheight: float = 1.,
    include_stem: bool = False,
    inplace: bool = False,
) -> ToyTree:
    """Return ToyTree rescaled to a specific total tree height.

    Edge lengths (Node dist values) are all multiplied by a constant
    factor to make the root Node height align at treeheight. By
    default tree is scaled to the root crown height, but stem height
    can also be specified.

    Parameters
    ----------
    treeheight: float
        Total tree height to scale tree to.
    include_stem: bool
        If True then the stem height is set instead of crown height.
    inplace: bool
        If True the tree is modified, else a copy is returned.

    Example
    -------
    >>> tree = toytree.rtree.unittree(10, seed=123)
    >>> tree = tree.mod.edges_scale_to_root_height(1000)
    >>> tree.draw(scale_bar=True);
    """
    tree = tree if inplace else tree.copy()

    # get total tree height
    height = (
        tree.treenode.height + tree.treenode.dist if include_stem
        else tree.treenode.height)

    # get multiplier
    ratio = treeheight / height

    # scale Nodes using cached Nodes, no ._update call necessary.
    for idx in range(tree.nnodes):
        tree[idx]._height *= ratio
        tree[idx]._dist *= ratio
    return tree


@add_subpackage_method(TreeModAPI)
def edges_slider(
    tree: ToyTree,
    # query: Query = None,
    prop: float = 0.999,
    seed: Optional[int] = None,
    inplace: bool = False,
    root: bool = False,
) -> ToyTree:
    """Return ToyTree with node heights randomly shifted within bounds.

    Node heights are moved up or down uniformly between their parent
    and highest child node heights in 'levelorder' (from root to tips).
    Root and tip heights are fixed, only internal node heights change.

    Parameters
    ----------
    prop: float
        The proportion or percentile of the edge bounds from which
        to sample new heights from.
    seed: int
        Random number generator seed used to sample new heights.
    inplace: bool
        Transform tree in place and return it, or return a copy.
    """
    tree = tree if inplace else tree.copy()
    rng = np.random.default_rng(seed)

    # smaller value means less jitter
    assert 0 < prop < 1, "prop must be a proportion >0 and < 1."

    # randomly sample the traversal direction
    order = rng.choice(["postorder", "preorder"])

    # traverse tree sampling new heights within constrained ranges
    for node in tree.traverse(order):

        # slide internal Nodes
        if (not node.is_root()) and (not node.is_leaf()):

            # the closest child to me
            min_child_dist = min([i.dist for i in node.children])

            # prop distance down toward child
            minh = node._height - (min_child_dist * prop)

            # prop towards parent
            maxh = node._height + (node.dist * prop)

            # node.height
            newheight = rng.uniform(minh, maxh)

            # how much lower am i?
            delta = newheight - node._height

            # edges from children to reach me
            for child in node.children:
                child._dist += delta

            # slide self to match
            node._dist -= delta
            node._height = newheight
    return tree


@add_subpackage_method(TreeModAPI)
def edges_multiplier(
    tree: ToyTree,
    alpha: float = 3.0,
    inplace: bool = False,
    seed: Optional[int] = None
) -> ToyTree:
    """Return ToyTree w/ all Nodes scaled by a random constant.

    This scales the entire tree height and all nodes in unison, similar
    to `edges_scale_to_root_height` but instead of setting the root
    to a specific value, the value is sampled from a gamma distribution.
    The current mean root height serves as the mean of the distribution
    mean = (a / b); the user enter's a value for a to determine the
    variance of the distribution (a / b**2), smaller values have larger
    variance.

    Parameters
    ----------
    alpha: float
        The node height multiplier will be sampled from a gamma dist
        with parameters (a,b), where b will be automatically set so
        that the mean = a/b = current root height.
    inplace: bool
        Transform tree in place and return it, or return a copy.
    seed: int or None or RNG
        Random number generator seed used to sample new heights.
    """
    tree = tree if inplace else tree.copy()
    beta = tree.treenode.height / alpha
    multiplier = np.random.default_rng(seed).gamma(shape=alpha, scale=beta)
    for node in tree:
        node._dist = node._dist * multiplier
        node._height = node._height * multiplier
    # Note: ToyTree._update call is not needed here.
    return tree


@add_subpackage_method(TreeModAPI)
def edges_extend_tips_to_align(
    tree: ToyTree,
    inplace: bool = False,
) -> ToyTree:
    """Return a ToyTree with tips Node dists extended to align.

    Tip Node dists are extended to align with the Node that is farthest
    from the root (defined as height=0). This is a simple way to make
    a tree appear ultrametric.

    See Also
    --------
    ... TODO: [alternative ultrametric scaling methods]

    Parameters
    ----------
    inplace: bool
        If True tree is modified in place, else a copy is
    """
    tree = tree if inplace else tree.copy()
    for node in tree[:tree.ntips]:
        node._dist += node._height
        node._height = 0
    return tree


@add_subpackage_method(TreeModAPI)
def edges_set_node_heights(
    tree: ToyTree,
    data: Dict[Query, float],
    inplace: bool = False,
) -> ToyTree:
    """Return a ToyTree with one or more Node heights set explicitly.

    Enter a dictionary mapping node idx to heights. Node idxs that
    are not included as keys will remain at there existing height, but
    their dist values may be changed to modify the heights of other
    Nodes, since height is an emergent property of the dist values of
    many connected Nodes.

    Parameters
    ----------
    data: Dict[Query, float]
        A dictionary mapping a Node query (Node, Node idx label, or Node
        name) to a float value for the new height of that Node.
    inplace: bool
        Tree is modified in place or returned as a copy.

    Examples
    --------
    >>> tre = toytree.rtree.unitree(10)
    >>> tre = tre.mod.edges_set_node_heights({10: 55, 11: 60, 12: 100})
    """
    # set node heights on a new tree copy
    tree = tree if inplace else tree.copy()

    # convert {query: float} to {idx: float} using Node int idx labels
    mapping = {
        tree.get_nodes(i)[0].idx: j for (i, j) in data.items()
    }

    # set node height to current value for those not in hdict
    for idx in range(tree.nnodes):
        if idx not in mapping:
            mapping[idx] = tree[idx]._height

    # iterate over nodes from tips to root
    for node in tree:  # .traverse("postorder"):
        # shorten or elongate child stems to reach node's new height
        node._height = mapping[node.idx]
        if node.up:
            node._dist = mapping[node.up.idx] - mapping[node.idx]

    # report warning if any edges end up negative
    for node in tree:
        if node._dist < 0:
            logger.warning(f"negative edge length {node._dist:.6g} @ Node {node._idx}")
    return tree


if __name__ == "__main__":

    import toytree
    TREE = toytree.rtree.rtree(ntips=6)
    TREE = toytree.rtree.unittree(ntips=6, treeheight=100, seed=123)

    NEW_HEIGHTS = {
        10: 200,
        9: 10,
        8: 150,
        7: 130,
        6: 80,
    }

    print(edges_scale_to_root_height(TREE, 100, False, False).get_node_data())
    print(edges_slider(TREE, 0.5).get_node_data())
    print(edges_multiplier(TREE, alpha=0.5).get_node_data())
    print(edges_extend_tips_to_align(TREE).get_node_data())
    print(edges_set_node_heights(TREE, NEW_HEIGHTS).get_node_data())
