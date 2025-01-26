#!/usr/bin/env python

"""Topology manipulation functions for ToyTrees.

This module includes function for manipulating ToyTrees by adding,
removing, or changing the relationships among TreeNodes. It is the
preferred way for users to modify tree topologies, compared to
editing TreeNodes directly, since it ensures that the TreeNodes
have a valid ToyTree coordinate structure when returned.

Most of these functions use a Query selector...

Methods
-------
Return ToyTree with some internal nodes collapsed.
>>> collapse_nodes(tree, ...)

Return ToyTree with one Node rotated (._children tuple order reversed).
>>> rotate_node(tree, ...)

Return a ToyTree connecting a subset of Nodes in a tree.
>>> prune(tree, ...)

Return a ToyTree with some tip Nodes removed.
>>> drop_tips(tree, ...)

Return ToyTree with one or more polytomies randomly resolved.
>>> resolve_polytomies(tree, ...)

Add an internal node by splitting an edge to create new node.
>>> add_internal_node(tree, ...)

Add a tip node as a child of an existing Node.
>>> add_child_node()

Add a sister node as a child of the same existing parent Node (synonymous w/ add_child() called on parent)
>>> add_sister_node(tree, ...)

Add a parent-child pair to split an existing branch into two children (new child Node, old child clade)
>>> add_internal_node_and_child()

Add a parent-child clade pair to split an existing branch.
>>> add_internal_node_and_subtree()

"""

from typing import Optional, TypeVar, Tuple, Callable, Union
from loguru import logger
import numpy as np
from toytree.core.apis import TreeModAPI, add_subpackage_method, add_toytree_method
from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError

logger = logger.bind(name="toytree")
Query = TypeVar("Query", str, int, Node)

__all__ = [
    "ladderize",
    "collapse_nodes",
    "remove_unary_nodes",
    "rotate_node",
    "extract_subtree",
    "prune",
    "drop_tips",
    "bisect",
    "resolve_polytomies",
    "add_internal_node",
    "add_child_node",
    "add_sister_node",
    "add_internal_node_and_child",
    "add_internal_node_and_subtree",
    "remove_nodes",
    "merge_nodes",
]


@add_toytree_method(ToyTree)
@add_subpackage_method(TreeModAPI)
def ladderize(tree: ToyTree, direction: bool = False, inplace: bool = False) -> ToyTree:
    """Return a ladderized tree (ordered descendants)

    In a ladderized tree nodes are rotated so that the left/
    right child always has fewer/more descendants.

    Parameters
    ----------
    direction: bool
        If False then child Nodes are sorted (left to right) from
        smallest to largest number of descendants. If True they are
        sorted in the reverse order.
    """
    # get a copy of the tree to modify
    nself = tree if inplace else tree.copy()
    direction = bool(direction)  # needed to ensure invert below against int arg

    # visit all nodes from tips to root recording size on the way
    sizes = {}
    for nidx in range(tree.nnodes):
        node = nself[nidx]

        # get node size
        if node.is_leaf():
            sizes[node.idx] = 1
        else:
            sizes[node.idx] = sum(sizes[child.idx] for child in node.children)
            node._children = tuple(sorted(
                node._children,
                key=lambda x: sizes[x.idx],
                reverse=direction,
            ))

    # update idx labels for new tree ladderization
    nself._update()
    return nself


@add_subpackage_method(TreeModAPI)
def collapse_nodes(
    tree: ToyTree,
    *query: Query,
    min_dist: float = 1e-6,
    min_support: float = 0,
    inplace: bool = False,
) -> ToyTree:
    """Return ToyTree with some internal nodes collapsed.

    Nodes can be entered as Node instances, Node names strings,
    or Node int idx labels, and/or Nodes can be selected by
    minimum dist or support values. Selected Nodes are collapsed
    into multi-furcating polytomies. For example, set
    min_support=50 to collapse all nodes with support < 50, and/or
    select Node idx 10 to collapse Node 10.

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. To select internal Nodes use idx labels
        or Node object from `tree.get_mrca_node('name1', 'name2')`.
    min_dist: float
        The minimum dist (edge length) value allowed.
    min_support: float
        The minimum support (e.g., bootstrap) value allowed.
    inplace: bool
        If True then the original tree is changed in-place, and
        returned, rather than leaving original tree unchanged.

    Note
    ----
    This cannot be used to remove the root Node. To collapse the root
    into a polytomy use `toytree.mod.unroot`, or collapse the Node(s)
    directly below the root Node.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=12)
    >>> tree.mod.collapse_nodes(14)
    >>> tree.mod.collapse_nodes(tree.get_mrca_node('r1', 'r2').idx)
    >>> tree.mod.collapse_nodes(tree.get_mrca_node('~r[1-4]').idx)
    >>> tree = tree.set_node_data("dist", {22: 0.005, 21: 0.005})
    >>> tree = tree.set_node_data("support", {20: 50}, default=100)
    >>> tree = tree.mod.collapse_nodes(min_dist=0.01, min_support=45)
    """
    nodes = () if not query else tree.get_nodes(*query)
    if not inplace:
        tree = tree.copy()
        nodes = [tree[i.idx] for i in nodes]

    # iterate over all internal nodes
    for node in tree[tree.ntips:-1]:
        if (node.dist < min_dist) | (node.support < min_support) | (node in nodes):
            node._delete(preserve_dists=True, prevent_unary=True)
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def merge_nodes(
    tree: ToyTree,
    merge_method: Union[Callable, str] = "name",
    selection_method: Callable = min,
    inplace: bool = False,
) -> ToyTree:
    r"""Return ToyTree with one or more Nodes merged based on a Callable.

    Merging means to discard at least one tip and one internal Node
    while keeping one child node that inherits its parents dists. An
    example use case for this is to compress duplicate tips in a clade
    into a single representative.

                    |                 |
                   2()                |
                   /  \     --->      |
                0(a)  1(a)           0(a)

    Parameters
    ----------
    merge_method: Callable or str
        Two options: (1) A function that returns True if a Node should
        be merged; or (2) A feature name for which a Node will be
        merged if all descendant leaves share the same feature value.
    selection_method: Callable
        A function that returns a single Node from a collection of
        Nodes. The default func `min` will return the Node with
        the lowest idx index.
    inplace: bool
        If True then the original tree is changed in-place, and
        returned, rather than leaving original tree unchanged.

    See Also
    --------
    `toytree.mod.remove_nodes`

    Example
    -------
    >>> tree = toytree.rtree.unittree(5, seed=123)
    >>> tree1 = tree.mod.add_internal_node_and_child("r1", name="r1")
    >>> # merge nodes with identical leaf names.
    >>> tree2 = tree1.mod.merge_nodes("name")
    >>> # more verbose example to do the same
    >>> merge_method = lambda x: len(set(x.iter_leaf_names())) == 1
    >>> tree2 = tree1.mod.merge_nodes(merge_method)
    >>> toytree.mtree([tree1, tree2]).draw();
    """
    # select which nodes will be removed
    merge = set()

    # if feature selected make a def to return True if all leaf values
    # are the same.
    if isinstance(merge_method, str):
        feat = merge_method
        def merge_method(node: Node) -> bool:
            nvals = set(getattr(i, feat) for i in node.iter_leaves())
            return len(nvals) == 1

    # check Callables
    assert isinstance(merge_method(tree[0]), bool), "merge_method should return a boolean"
    assert len(selection_method(tree[:3])) == 1, "selection_method should retain only one Node"

    # iterate over tree from root to tips
    for node in tree[::-1][1:]:
        if node not in merge:
            if merge_method(node):
                desc = set(node.iter_descendants())
                keep = selection_method(desc)
                desc.discard(keep)
                merge.update(desc)

    # remove nodes and return tree
    return tree.mod.remove_nodes(*merge, inplace=inplace)


@add_subpackage_method(TreeModAPI)
def remove_nodes(tree: ToyTree, *query: Query, preserve_dists: bool = True, inplace: bool = False) -> ToyTree:
    """Return ToyTree with one or more Nodes removed.

    If multiple Nodes are entered they are removed in a postorder
    traversal of the tree. Nodes can be selected using Node Queries.

    Parameters
    ----------
    *query: str, int, or Node
        The Node to rotate can be selected by entering the Node object,
        or its idx label, or name str. For internal Nodes, multiple
        queries can be entered and their MRCA will be rotated.
    preserve_dists: bool
        If True then children inherit the dist values of their
        deleted parents so that their dist value reaches their
        grandparents original height. If False, children retain
        their original dist but are connected to their grandparent.
    inplace: bool
        If True then the original tree is changed in-place, and
        returned, rather than leaving original tree unchanged.

    See Also
    --------
    `toytree.mod.remove_unary_nodes`

    Example
    -------
    >>> # remove a tip leaving behind a unary internal Node.
    >>> tree = toytree.rtree.unittree(5, seed=123)
    >>> tree = toytree.mod.remove_node(tree, "r0")
    """
    nodes = () if not query else tree.get_nodes(*query)
    if not inplace:
        tree = tree.copy()
        nodes = [tree[i.idx] for i in nodes]

    # postorder idx traversal
    for node in tree:
        if node in nodes:
            node._delete(preserve_dists, prevent_unary=False)
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def remove_unary_nodes(tree: ToyTree, inplace: bool = False) -> ToyTree:
    r"""Return ToyTree with any unary Nodes removed.

                4     remove_unary_nodes     4
               / \                          / \
              3   2         ------>        /   \
             /     \                      /     \
            0       1                    0       1

    Parameters
    ----------
    inplace: bool
        If True then the original tree is changed in-place, and
        returned, rather than leaving original tree unchanged.

    Example
    -------
    >>> # add two unary Nodes then remove them.
    >>> tree = toytree.rtree.unittree(5, seed=123)
    >>> tree = toytree.mod.add_internal_node(tree, "~r[0-2]", name="i")
    >>> tree = toytree.mod.add_internal_node(tree, "~r[0-1]", name="j")
    >>> tree = toytree.mod.remove_unary_nodes(tree)
    """
    tree = tree if inplace else tree.copy()
    tipset = set(tree[i] for i in range(tree.ntips))
    for node in tree.traverse("postorder"):
        if len(node.children) == 2:
            tipset.add(node)
        if node not in tipset:
            new_parent = node._up
            if new_parent:
                true_node = node._children[0]
                new_parent._add_child(true_node)
                new_parent._remove_child(node)
                true_node._dist += node._dist
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def rotate_node(tree: ToyTree, *query: Query, inplace: bool = False) -> ToyTree:
    """Return ToyTree with one Node rotated (children order reversed).

    Rotates *only one Node per call*. Internal Nodes can be selected
    by idx label, or by entering multiple tip Node names from which the
    MRCA will be selected and rotated.

    Parameters
    ----------
    *query: str, int, or Node
        The Node to rotate can be selected by entering the Node object,
        or its idx label, or name str. For internal Nodes, multiple
        queries can be entered and their MRCA will be rotated.
    inplace: bool
        If True then the original tree is changed in-place, and
        returned, rather than leaving original tree unchanged.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10)
    >>> toytree.mod.rotate_node(tree, 12)
    >>> toytree.mod.rotate_node(tree, 'r0', 'r1')
    >>> toytree.mod.rotate_node(tree, '~r[0-3]$')
    >>> # Can chain multiple calls together:
    >>> tree.mod.rotate_node(14).mod.rotate_node(13).mod.rotate_node(12)
    """
    node = tree.get_mrca_node(*query)
    if not inplace:
        tree = tree.copy()
        node = tree[node.idx]
    node._children = tuple(node.children[::-1])
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def extract_subtree(tree: ToyTree, *query: Query) -> ToyTree:
    r"""Return a subtree/clade extracted from a larger tree as a ToyTree.

                4      extract_subtree (3)
               / \                           |
              3   \         ------>          3
             / \   \                        / \
            0   1   2                      0   1

    Note
    ----
    The returned subtree is a copy of the subtree from the original;
    the original tree is not affected.

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors (Node object, names, or idx labels)
        from which the MRCA is found. This will serve as the root Node
        of the returned tree.

    See Also
    --------
    `toytree.mod.bisect`
    `toytree.mod.prune`
    `toytree.mod.drop_tips`

    Example
    -------
    >>> tree = toytree.tree("((a,b),c);")
    >>> subtree = tree.mod.extract_subtree('a', b')
    >>> toytree.mtree([tree, subtree]).draw('p')
    """
    node = tree.get_mrca_node(*query)
    return ToyTree(node.copy(detach=True))


@add_subpackage_method(TreeModAPI)
def bisect(tree: ToyTree, *query: Query, reroot: bool = False, dist_partition: float = 1.0) -> Tuple[ToyTree, ToyTree]:
    r"""Return a tree bisected into two subtrees on a selected edge.

    This returns two bisected subsets of the original tree. It does not
    affect the original tree object. If query selects the treenode on
    a rooted tree it returns a subtree for each child as a treenode with
    its original dist. If query selects the treenode on an urooted tree
    it raises an error. If query selects any other node it will split
    the edge above to create two subtrees. The query node will become
    a treenode of one new subtree. The arg 'reroot=False` will retain
    the original treenode in the other subtree, otherwise the node above
    the query becomes the new treenode (i.e., the subtree is re-rooted).
    The subtree below the query will inherit all of the dist of the
    split edge unless the dist_partition arg is used to designate the
    proportion of dist (0.0-1.0) to assign to this treenode.

           __6(T)__      bisect (6)
          |       |       ------->          |          |
         _4_     _5_                       4(T)       5(T)
        |   |   |   |                     |   |      |   |
        0   1   2   3                     0   1      2   3
    # bisect on treenode (T) of rooted tree returns the two child trees.

           __6(T)__      bisect (4)         |
          |       |       ------->          |
         _4_     _5_                       4(T)       5(T)
        |   |   |   |                     |   |      |   |
        0   1   2   3                     0   1      2   3
    # bisect on internal node (4) returns tree rooted on query (4) with
    # full dist of split edge. The treenode (T) is ignored if on split
    # edge and subtree from the side of split edge (5) is returned.

           __6(T)__       bisect (4)
          |       |   dist_partition=0.5    |          |
         _4_     _5_      ------->         4(T)       5(T)
        |   |   |   |                     |   |      |   |
        0   1   2   3                     0   1      2   3
    # The dist of the split edge can be partitioned among the two
    # subtrees using `dist_partition`.

           __6(T)__       bisect (1)                4(T)
          |       |      reroot=True               |   |
         _4_     _5_      ------->                 0   |
        |   |   |   |                       |         _5_
        0   1   2   3                      1(T)      |   |
                                                     2   3
    # If `reroot=True` the subtree on the other side of the split edge
    # is rerooted to make that node the treenode.

           __6(T)__       bisect (1)                 _6(T)
          |       |      reroot=False               |    |
         _4_     _5_      ------->                  |   _5_
        |   |   |   |                       |       |  |   |
        0   1   2   3                      1(T)     0  2   3
    # If `reroot=False` the original treenode remains the treenode on
    # the second subtree and any unary nodes (4) are removed.

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors (Node object, names, or idx labels)
        from which the MRCA will select the Node below the edge to cut.
        is found. This will serve as the root Node of the returned tree.
    reroot: bool
        If True the subtree above the query will be rerooted on the
        node query parent rather than retain the original treenode.
    dist_partition: float
        The proportion of dist of the split edge to assign to the
        subtree selected by query. Default is to assign all dist to
        the treenode of this subtree. A value between 0.0-1.0 can be
        entered to split the dist and assign this proportion to the
        query treenode. This arg cannot be combined with reroot=False.

    TODO
    ----
    instead of disallowing dist_partition when not re-rooting, it could
    create a new Node on the split branch to inherit the dist if the
    dist_partition value is <1.

    Examples
    --------
    >>> tree = toytree.tree.unittree(ntips=6, seed=123)
    >>> subtree1, subtree2 = tree.bisect("r2", "r3")
    >>> subtree1, subtree2 = tree.bisect("r2", "r3", reroot=True)
    >>> subtree1, subtree2 = tree.bisect("r2", "r3", reroot=True, dist_partition=0.5)
    """
    # allow node query from outside tree
    node = tree.get_mrca_node(*query)
    tree = tree.copy()
    node = tree[node.idx]

    # if treenode selected on an unrooted tree raise error
    if node.is_root() and not tree.is_rooted():
        msg = "cannot bisect on treenode of an unrooted tree. Select one of its children."
        logger.error(msg)
        raise ToytreeError(msg)

    # if treenode selected on a rooted tree return child subtrees
    elif node.is_root() and tree.is_rooted():
        children = tree.treenode.children
        left = tree.mod.extract_subtree(children[0])
        right = tree.mod.extract_subtree(children[1])
        # optionally re-partition dist root edge dist among children
        if dist_partition:
            total_dist = left.treenode.dist + right.treenode.dist
            left.treenode._dist = total_dist * dist_partition
            right.treenode._dist = total_dist * (1. - dist_partition)
        return left, right

    # ...
    if reroot:
        raise NotImplementedError("TODO")
    # root on node; detach two child clades; assign dists
    # rtree = tree.root(node)
    # pdist = sum(i.dist for i in rtree.treenode.children)
    # left, right = rtree.treenode.children

    # cleanup original tree
    ndist = node._dist
    if node.up:
        node.up._delete()
    subtree = ToyTree(node._detach())
    subtree.treenode._dist = ndist
    tree._update()
    return (subtree, tree)
    # unroot the trees
    # if not reroot:
    #     if left.ntips > 2:
    #         left.unroot(inplace=True)
    #     if right.ntips > 2:
    #         right.unroot(inplace=True)
    # return partitioned dist on rooted trees
    # else:
    #     # force to be in [0, 1]
    #     dist_partition = max(0, min(1, dist_partition))
    #     alt_partition = 1 - dist_partition
    #     left.treenode._dist = pdist - (pdist * dist_partition)
    #     right.treenode._dist = pdist - (pdist * alt_partition)
    # return (left, right)


@add_subpackage_method(TreeModAPI)
def prune(
    tree: ToyTree,
    *query: Query,
    preserve_dists: bool = True,
    require_root: bool = False,
    inplace: bool = False,
) -> ToyTree:
    r"""Return a tree w/ the minimal edges connecting a subset of Nodes.

    All nodes not included in the entered 'nodes' list will be
    removed from the topology, and the mininal spanning edges to
    connect the remaining nodes are retained. The original root node
    is preserved if 'require_root=True', otherwise the lowest
    mrca connecting the selected nodes will be kept as the new root.

                4      prune([0,1])
               / \
              3   \      ------>        3
             / \   \                   / \
            0   1   2                 0   1
    # min spanning tree of 0,1 involves only nodes 0,1,3

                4      prune([0,1])     4
               / \    require_root=1    |
              3   \      ------>        3
             / \   \                   / \
            0   1   2                 0   1
    # min spanning tree of 0,2 does not require node 4 but it is kept.

                4      prune([0,2])      4
               / \   preserve_dists=0   / \
              3   \      ------>       0   \
             / \   \                        \
            0   1   2                        2
    # min spanning tree of 0,2 involves only 0,2,4 (node 3 is excluded).
    # if preserve_dists=False its dist is also discarded.

                4    prune([0,2,3])      4
               / \                      / \
              3   \      ------>       3   \
             / \   \                  /     \
            0   1   2                0       2
    # min spanning tree of 0,2,3 only excludes Node 1. Internal nodes
    # are kept if selected in query, even if they are unary.

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. You can select tip Nodes and/or internal
        Nodes to be kept in the tree.
    preserve_dists: bool
        If True then the edge lengths of internal nodes that are
        removed are merged into the 'dist' attribute of their
        descendant node that is preserved.
    require_root: bool
        If True then the root node is always preserved. If False
        then the root is only preserved if is it the mrca of the
        selected nodes, otherwise the mrca Node is returned.
    inplace: bool
        If True then the original tree is changed in-place, and also
        returned, else a copy is returned and original is unchanged.

    Examples
    --------
    >>> tree = toytree.tree("((a,b)ab,c)r;")
    >>> tree.mod.prune("a", "b", require_root=False)
    >>> # (a,b)ab;
    >>> tree.mod.prune("a", "b", require_root=True)
    >>> # ((a,b)ab)r;
    >>> tree.mod.prune("a", "b", "ab", require_root=False)
    >>> # (a,b)ab;
    >>> tree.mod.prune("a", "b", "ab", require_root=True)
    >>> # ((a,b)ab)r;
    """
    nodes = tree.get_nodes(*query)
    if not inplace:
        tree = tree.copy()
        nodes = [tree[i.idx] for i in nodes]

    # get mrca node if not requiring root
    if not require_root:
        mrca = tree.get_mrca_node(*nodes)
        nodes.append(mrca)

    # traverse postorder removing nodes, but keeping treenode for now
    counter = {i: 0 for i in tree}
    for node in tree[:-1]:
        # increment parent count and skip node if it is in query
        if node in nodes:
            counter[node._up] += 1
            continue

        # increment parent count if in counter, skip if >1 in counter.
        if counter[node]:
            counter[node._up] += 1
            if counter[node] > 1:
                continue

        # remove the node
        node._delete(preserve_dists=preserve_dists, prevent_unary=False)

    # set mrca node as new treenode or update and return current tree
    if not require_root:
        return ToyTree(mrca._detach())
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def drop_tips(
    tree: ToyTree,
    *query: Query,
    inplace: bool = False,
) -> ToyTree:
    """Return a ToyTree with some tip Nodes removed.

    The ToyTree with the selected tip Nodes (and any remaining internal
    nodes without children) are removed while retaining the original
    edge lengths between remaining nodes. This is effectively the
    inverse of `prune`. Tip names can be selected using a Query method
    of Node instances, Node names, or Node idx int labels. Only
    selected tip Nodes affect the result.

    Parameters
    ----------
    tree: ToyTree
        An input ToyTree to perform function on.
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels.
    inplace: bool
        If True then the original tree is changed in-place, and
        returned, rather than leaving original tree unchanged.

    See Also
    --------
    `mod.extract_subtree`
        Extract a complete clade from a tree as a new ToyTree.
    `mod.prune`
        Extract the minimal spanning tree from a tree that connects
        a subset of tip or internal Nodes.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10)
    >>> tree.mod.drop_tips(1, 2, 3).draw()
    >>> tree.mod.drop_tips('~r[0-3]$').draw()
    >>> tree.mod.drop_tips('r1', 'r2')
    """
    # raise exception if no nodes were selected
    if not query:
        msg = "No nodes selected. Enter a node query."
        logger.error(msg)
        raise ValueError(msg)

    # get query and tree
    nodes = tree.get_nodes(*query)
    if not inplace:
        tree = tree.copy()
        nodes = [tree[i.idx] for i in nodes]

    # raise exception if all tips were selected
    if len(nodes) == tree.nnodes:
        msg = "Cannot drop all tips from the tree."
        logger.error(msg)
        raise ValueError(msg)
    internal = []
    for node in sorted(nodes):
        if node.is_leaf():
            node._delete(prevent_unary=True)
        else:
            internal.append(node)
    # warn user that internal nodes were ignored.
    if internal:
        logger.warning("Only tip Nodes are removed. See `mod.remove_nodes`.")
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def resolve_polytomies(
    tree: ToyTree,
    *query: Query,
    dist: float = 1e-6,
    support: float = np.nan,
    recursive: bool = True,
    seed: Optional[int] = None,
    inplace: bool = False,
) -> ToyTree:
    """Return ToyTree with one or more polytomies randomly resolved.

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. If no Nodes are selected then ALL nodes
        that are multifurcating will be resolved.
    dist: float
        The dist value to set on newly created nodes.
    support: float or np.nan
        The support value to set on newly created nodes.
    recursive: bool
        Recursively resolve nested polytomies (default=True); if False
        then a n-tomy will only be resolved into a (n-1)-tomy.
    seed: int or None
        A seed for numpy random generator for reproducible resolving.
    inplace: bool
        If True then the original tree is changed in-place, and
        returned, rather than leaving original tree unchanged.

    Examples
    --------
    >>> tree = toytree.tree("((a,b,c),d);")
    >>> tree.mod.resolve_polytomies().draw();
    """
    nodes = tree.get_nodes(*query)
    if not inplace:
        tree = tree.copy()
        nodes = [tree[i.idx] for i in nodes]
    rng = np.random.default_rng(seed)

    for node in nodes:
        _resolve_nodes(
            node=node, dist=dist, support=support,
            rng=rng, recursive=recursive)
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def add_internal_node(
    tree: ToyTree,
    *query: Query,
    dist: Optional[float] = None,
    name: Optional[str] = None,
    inplace: bool = False,
) -> ToyTree:
    r"""Add an internal node by splitting an edge to create new node.

    Splits a branch spanning from node (A) to its parent (B)
    to create a new internal unary node (C).

                B                      B          Example
               / \                    / \         -------
              /   \      ---->       C   \        query="A"
             /     \                /     \       name="C"
            A       X              A       X      dist=None

    See Also
    --------
    :func:`.add_child_node`:
        Add a new child Node. Useful to call after `add_internal_node`.
    :func:`.add_internal_node_and_child`:
        This combines `add_internal_node` with `add_child_node`.

    Note
    ----
    If the query selects the root Node then a new Node will be inserted
    above it which will become the new root Node.

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. If multiple are entered the MRCA node will
        be used as the base of the edge to split.
    dist: float
        The distance from the selected Node at which to insert
        the new Node. This will be set as the dist of the
        descendant (A) whereas the new Node's dist (C) will be
        the descendants prior dist minus this dist value. If
        no dist value is set then the edge midpoint is used, except
        for the special case of adding a Node above the root, which
        defaults to dist=1.0.
    name: Optional[str]
        A name string to apply to the new Node. Default="".
    inplace: bool
        Modify tree in place.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
    >>> tree = tree.mod.add_internal_node('r0', name="x")
    >>> tree.draw(ts='n', node_sizes=15, node_labels="name")
    """
    # expand query
    node = tree.get_mrca_node(*query)
    if not inplace:
        tree = tree.copy()
        node = tree[node.idx]

    # get insertion edge and dist of the new Node
    parent = node.up

    # ROOT: if no parent (b/c node is root) then simply add new parent
    if not parent:
        new_node = Node(name=name if name is not None else "", dist=1.0)
        new_node._add_child(node)
        node._dist = dist if dist is not None else 1.0
        tree.treenode = new_node
        tree._update()
        return tree

    # NORMAL: parent is not root.
    dist = dist if dist is not None else node.dist / 2.
    if not node.dist >= dist >= 0:
        msg = f"the new Node dist must be >=0 and <={node.dist:.12g} (dist of {node})"
        logger.error(msg)
        raise ValueError(msg)

    # create the new Node and mend connections nearby
    new_node = Node(
        name=name if name is not None else "",
        dist=node.dist - dist,
    )

    # connect new_node to child (node) and grandparent (parent)
    node._dist = dist
    parent._remove_child(node)
    parent._add_child(new_node)
    new_node._up = parent
    new_node._children = (node, )
    node._up = new_node
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def add_child_node(
    tree: ToyTree,
    *query: Query,
    name: Optional[str] = None,
    dist: Optional[float] = None,
    inplace: bool = False,
) -> ToyTree:
    r"""Add a child Node to existing Node on a tree.

    This function selects an existing Node to act as the parent, and
    inserts a new Node as a child of that parent. The new child's name
    and dist can be set. If no dist value is entered then the child's
    dist is set to match that of its new sister Nodes, or 1.0.

                B                      B          Example
               / \                    /|\         --------
              /   \      ---->       / | \        query="B"
             /     \                /  |  \       name="D"
            A       X              A   D   X      dist=None

    Parameters
    ----------
    *query: Query
        One or more Node queries (Node object, int idx label or str
        name) from which the MRCA is found. The new Node will be added
        as a child of the MRCA Node.
    name: str or None
        Name of the new child Node.
    dist: float or None
        Edge length (dist) of the new child Node. If None it will be
        set to the same length as its longest sister, unless no sisters
        exist, then it is set to 1.
    inplace: bool
        If True the tree is modified inplace and returned, else a copy
        is returned.

    See Also
    --------
    :func:`.add_internal_node`:
        Add a new internal Node. Useful as parent to a new child Node.
    :func:`.add_internal_node_and_child`:
        This combines `add_internal_node` with `add_child_node`.

    Example
    -------
    >>> tree = toytree.rtree.imbtree(5)
    >>> tree = tree.mod.add_child_node('r0', 'r1', 'r2', name="C")
    >>> tree.draw("p", layout="r", node_labels="name");
    """
    # expand query
    node = tree.get_mrca_node(*query)
    if not inplace:
        tree = tree.copy()
        node = tree[node.idx]

    # set dist to user value else to max sister's dist, else to 1.
    if dist is None:
        if node.children:
            dist = max(child.dist for child in node.children)
        else:
            dist = 1.0
    dist = max(0, dist)

    # create the new Node that will be a child.
    new_node = Node(name=name if name is not None else "", dist=dist)

    # add as a new child to end of parent's children
    node._add_child(new_node)
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def add_sister_node(
    tree: ToyTree,
    *query: Query,
    name: Optional[str] = None,
    dist: Optional[float] = None,
    inplace: bool = False,
) -> ToyTree:
    r"""Add a sister Node to existing Node on a tree.

    This function selects an existing Node to act as the sister, and
    inserts a new Node as a child of the same parent. The new sister
    Node's name and dist can be set. If no dist value is entered then
    the its dist is set to match the max dist of its sister Nodes or 1.
    This function is equivalent to :func:`.add_child_node` but the
    query is used to select a sister rather than a parent.

                B                      B          Example
               / \                    /|\         --------
              /   \      ---->       / | \        query="A"
             /     \                /  |  \       name="D"
            A       X              A   D   X      dist=None

    See Also
    --------
    :func:`.add_internal_node`:
        Add a new internal Node. Useful as parent to a new sister Node.
    :func:`.add_internal_node_and_child`:
        This combines `add_internal_node` with `add_child_node`.

    Example
    -------
    >>> tree = toytree.rtree.imbtree(5)
    >>> tree = tree.mod.add_sister_node('r0', 'r1', 'r2', name="C")
    >>> tree.draw("p", layout="r", node_labels="name");
    """
    # expand query
    node = tree.get_mrca_node(*query)
    if not inplace:
        tree = tree.copy()
        node = tree[node.idx]

    assert not node.is_root(), (
        "Cannot add sister to root, it has no parent. See `add_child_node()`.")
    # simply call add_child to the parent of the selected Node.
    parent = node._up
    return add_child_node(tree, parent, name=name, dist=dist, inplace=inplace)


@add_subpackage_method(TreeModAPI)
def add_internal_node_and_child(
    tree: ToyTree,
    *query: Query,
    name: Optional[str] = None,
    dist: Optional[float] = None,
    parent_dist: Optional[float] = None,
    parent_name: Optional[str] = None,
    inplace: bool = False,
) -> ToyTree:
    r"""Add a (parent, child) edge to split an existing branch.

    Splits a branch spanning from query node (A) to its parent (B)
    to create a new internal Node (C) and child Node (D). The new
    parent and child Nodes can be given names and dist values. If
    no value is entered for `parent_dist` then the parent Node is
    inserted at the midpoint of the edge. If a parent_dist value is
    entered then it must fit within the length of the query Node's
    dist or an error is raised. The new child Node dist is not
    constrained. If no value is entered then it will be automatically
    set to match the dist of its sister Node.

                B                      B          Example
               / \                    / \         --------
              /   \      ---->       C   \        query="A"
             /     \                / \   \       name="D"
            A       X              A   D   X      parent_name="C"

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. If multiple are entered the MRCA node will
        be used as the base of the edge to split.
    name: str
        Optional name for the new child node. Default="".
    dist: float
        The dist (edge length) of the new child Node. If None this will
        be set to match its max sister's dist, if present, else 1.
    parent_dist: float
        The dist (edge length) of the new internal parent Node. If
        None it is set to the edge midpoint. If a value is entered it
        must be >0 and < query Node dist.
    parent_name: str
        Optional name for the new internal parent node. Default="".
    inplace: bool
        If False (default) a copy of the original tree is returned.

    Example
    -------
    >>> tree = toytree.rtree.imbtree(5)
    >>> tree = tree.mod.add_internal_node_and_child(
    >>>     'r3', name="C", parent_name="P")
    >>> tree.draw(node_sizes=15, node_labels="name");
    """
    # expand query
    node = tree.get_mrca_node(*query)
    if not inplace:
        tree = tree.copy()
        node = tree[node.idx]

    # set parent name to something unique
    pname = "PARENT@@@@@"
    add_internal_node(tree, node, name=pname, dist=parent_dist, inplace=True)
    add_child_node(tree, pname, name=name, dist=dist, inplace=True)

    # set parent name to user option or ''
    tree.get_nodes(pname)[0].name = parent_name if parent_name else ""
    return tree


@add_subpackage_method(TreeModAPI)
def add_internal_node_and_subtree(
    tree: ToyTree,
    *query: Query,
    subtree: ToyTree,
    subtree_stem_dist: Optional[float] = None,
    subtree_rescale: bool = False,
    parent_dist: Optional[float] = None,
    parent_name: Optional[str] = None,
    inplace: bool = False,
) -> ToyTree:
    r"""Add a subtree by splitting an edge to create a new parent
    Node and inserting the subtree as a child (i.e., tree-grafting).

    Splits a branch spanning from node (A) to its parent (C) to
    create a new ancestral node (Z) from which a subtree (Y) will
    be inserted. The name of node (Z) and the stem dist of node (Y)
    can be set. By default, if left as None, the stem dist will be
    set to half the distance to the farthest leaf, and the subtree
    will be scaled to fill the other half distance so that it aligns
    as the farthest tip node distance.

            C                       C        Example
           / \                     Z \       -------
          /   \                   /\  \      query="A"
         /     \      ---->      /  Y  \     subtree=tree('(W,X)Y;')
        /       \               /  / \  \    parent_name="Z"
       A         B             A  W   X  B

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. If multiple are entered the MRCA node will
        be used as the base of the edge to split.
    subtree: ToyTree or Node
        A subtree to insert into the target tree.
    subtree_stem_dist: float or None
        Edge length of the subtree stem dist (the subtree treenode
        dist value is ignored). If None it is set to half the dist of
        its sister clade.
    subtree_rescale: bool
        If True the subtree edges are rescaled to fit in the dist
        between the sister node height and stem.
    parent_dist: float or None
        Distance above the query Node at which the parent Node will be
        inserted. This length is constrained by the dist of the query
        Node. If None the midpoint of the edge is used.
    parent_name: str
        Optional name for the new internal parent node.
    inplace: bool
        If False (default) a copy of the original tree is returned.

    See Also
    --------
    ...

    Note
    ----
    On speed...

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10, seed=123)
    >>> subtree = tree.mod.extract_subtree("r0", "r1", "r2")
    >>> new_tree = tree.mod.add_internal_node_and_subtree(
    >>>     "r4", subtree=subtree, subtree_rescale=True)
    >>> new_tree.draw();
    """
    # expand query while allowing for Node selector as input
    node = tree.get_mrca_node(*query)
    if not inplace:
        tree = tree.copy()
        node = tree[node.idx]

    # always copy the subtree and get as a detached Node.
    if isinstance(subtree, ToyTree):
        subtree = subtree.copy()
    elif isinstance(subtree, Node):
        subtree = ToyTree(subtree.copy(detach=True))
    elif isinstance(subtree, str):
        subtree = ToyTree(subtree)
    else:
        raise TypeError("subtree arg must be a ToyTree or Node instance.")

    # use a temporary parent name and set the proper name later. This
    # performs an _update call to relabel Node idxs and heights.
    pname = "PARENT@@@@@"
    add_internal_node(tree, node, name=pname, dist=parent_dist, inplace=True)

    # get new parent Node and set its name.
    parent = tree.get_nodes(pname)[0]
    parent.name = parent_name if parent_name else ""

    # get STEM dist for the subtree parent Node
    if subtree_stem_dist is None:
        subtree_stem_dist = max(i.dist for i in parent.children) / 2.

    # optional: scale subtree edges to fit in same dist as sister.
    if subtree_rescale:
        if subtree.nnodes > 1:
            remaining_dist = parent.height - subtree_stem_dist
            subtree = subtree.mod.edges_scale_to_root_height(remaining_dist)
        else:
            subtree_stem_dist = parent.children[0]._dist

    # add as a new child to end of parent's children
    parent._add_child(subtree.treenode)

    # set the subtree stem dist
    subtree.treenode._dist = subtree_stem_dist
    tree._update()
    return tree


# NEEDS WORK, not yet exposed to API.
# JUST USE ONE OF THE TREE MOVE METHODS, right?
# def move_clade(
#     tree: ToyTree,
#     idx0: int,
#     idx1: int,
#     height: Optional[float]=None,
#     name: str="",
#     shrink: bool=False,
#     inplace: bool=False,
# ):
#     r"""Move a clade from one part of the tree to another (SPR).

#     Splits a branch spanning from node idx1 (Y) to its parent (Z)
#     to create a new ancestral node (X). The idx0 clade is detached
#     from the tree (D) and its parent is removed if it leaves only
#     one child (E). The detached clade is reattached to the new
#     ancestral node (D -> X) while maintaining the edge lengths of
#     the subtree. The length of the edge connecting idx0 to the new
#     node (D, X) is automatically set to maintain ultrametricity,
#     unless the subclade height is greater than the dist arg. This
#     will raise an error unless shrink=True, in which case the
#     subtree is scaled to half the dist height to fit.

#                           Z
#           Z              / \              Z
#          / \            E   \            / \
#         E   \          /     \          /   X --- auto-set dist
#        / \   \        C       Y        /   / \
#       D   \   \  -->            -->   /   /   D --- auto-set dist
#      / \   \   \          D          /   /   / \
#     A   B   C   Y        / \        A   Y   A   B --- maintained dist
#                         A   B

#     Note
#     ----
#     This operation is synonymous with a rooted subprune regrafting
#     (SPR) move. Internal nodes that leave no descendants (e.g., E)
#     from above are removed from the tree.

#     See Also
#     --------
#     `toytree.mod.move_spr`: Faster SPR move function, but without
#     arguments to modify edge lengths like in this function.

#     Parameters
#     ----------
#     tree: ToyTree
#         A tree object.
#     idx0: int
#         The idx label of the Node at the top of the clade that
#         will be pruned from the tree and re-attached elsewhere.
#     idx1: int
#         The idx label of the Node whose branch will be split to
#         create a new parent node of the re-attached clade.
#     height: float or None
#         The height at which to insert node idx0 above node idx1.
#         This value must be in the interval between the height of
#         idx1 and its parent (node.height, node.height + node.dist).
#         If None then the node will be inserted at the midpoint
#         along node idx1's edge.
#     name: str
#         A name string to apply to the newly created internal node.
#     shrink: bool
#         If shrink is True then the subtree edge lengths (dists)
#         will be scaled to allow the clade to be inserted anywhere
#         in the tree. If False a ToyTreeError is raised if the
#         subclade cannot be inserted below the dist value.

#     Returns
#     -------
#     ToyTree
#         A modified copy of the original tree is returned.
#     """
#     # TODO: check tree_move SPR code and use that?
#     # create a copy
#     tree = tree if inplace else tree.copy()

#     # get selected nodes (FIXME: use nas to allow names selections)
#     src = tree[idx0]
#     dest = tree[idx1]

#     # cannot move a clade to its own children in rooted move
#     assert idx0 != idx1, "idx0 must be different from idx1"
#     assert idx0 != tree.treenode, "src node cannot be root."
#     assert idx1 != tree.treenode, "dest node cannot be root."
#     assert dest not in src.get_descendants(), (
#         "dest node cannot be a descendant of src in a rooted SPR move."
#     )

#     # check the height arg
#     if height is not None:
#         assert dest.up.height >= height >= dest.height, (
#             f"height {height} does occur on the node {idx1}'s edge: "
#             f"({dest.height}-{dest.up.height})")

#     # get dist arg from height
#     if height is None:
#         dist = dest.dist / 2.
#     else:
#         dist = height - dest.height

#     # if the dest is the src's parent, then we only need to modify the
#     # dist of dest and return the tree.
#     if dest == src.up:
#         diff = dest.dist - dist
#         dest.dist = dist
#         for child in dest.children:
#             child.dist += diff
#         return tree

#     # create new internal node.
#     newnode = Node(name=str(name), dist=dest.dist - dist)

#     # detach the source clade.
#     ancestor = src.up
#     src = src.detach()

#     # remove the null node (preserving bls) and in case the null node
#     # is the root, reset the tree variable to a new TreeNode root.
#     if ancestor.is_root():
#         if dest.up == tree.treenode:
#             root = newnode
#         else:
#             root = [i for i in tree.treenode.children if i != ancestor][0]
#         tree.treenode.delete(True, True)
#     else:
#         root = tree.treenode
#     ancestor.delete(True, True)

#     # set src dist (optional allowing shrink to fit)
#     if src.height > dest.height + dist:
#         if not shrink:
#             raise ValueError(
#                 f"Clade {idx0} does not fit below clade {idx1}. "
#                 "Use shrink=True.\n"
#                 f"Details: node {idx0} height={src.height}; "
#                 f"node {idx1} height={dest.height + dist}; "
#                 f"dist={dist}; "
#                 f"Error b/c {src.height} > {dest.height} + {dist}")
#         orig = src.height + src.dist
#         scale = orig / (dest.height + dist)
#         for node in src.traverse():
#             node.dist /= scale
#     else:
#         src.dist = dest.height + dist - src.height

#     # set dest dist
#     dest.dist = dist

#     # connect newnode to its parent
#     dest_parent = dest.up
#     dest_parent.children.append(newnode)
#     dest_parent.children.remove(dest)

#     # connect newnode to its children
#     newnode.up = dest_parent
#     newnode.children = [src, dest]
#     src.up = newnode
#     dest.up = newnode

#     # re-toytree it from the root
#     tree = toytree.tree(root)

#     # TODO: add highlight boolean arg and color moved clade.
#     # tree.style.edge_colors = ['black'] * tree.nnodes
#     # for idx in tree.get_node_descendant_idxs(src)
#     return tree


def _resolve_nodes(
    node: Node,
    dist: float,
    support: float,
    rng: np.random.Generator,
    recursive: bool,
) -> Node:
    """Resolve multifurcating Nodes. Used in `resolve_polytomies`.

    Randomly choose left/right split among children.
    """
    if len(node.children) <= 2:
        return node.children

    # split the children into [left, (remaining)]
    child_idxs = range(len(node.children))
    idx = rng.choice(child_idxs)
    left = node.children[idx]
    remaining = [node.children[i] for i in child_idxs if i != idx]

    # create new right parent
    right = Node(dist=dist, support=support)

    # resolve this Node
    node._children = (left, right)
    left._up = node
    right._up = node

    # connect remaining as (bi-multi) of right
    for child in remaining:
        child._up = right
        right._add_child(child)

    # update children by recursively operating on right nodes
    if recursive:
        right._children = _resolve_nodes(
            right, dist, support, rng, recursive)
    return left, right


if __name__ == "__main__":

    import toytree
    toytree.set_log_level("DEBUG")
    t = toytree.rtree.unittree(16, treeheight=10)
    t.mod.prune(0, 1, 2, 3)
    t.draw()
