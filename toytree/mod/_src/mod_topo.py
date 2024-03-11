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

"""

from typing import Optional, TypeVar
import itertools
from loguru import logger
import numpy as np
from toytree.core.apis import TreeModAPI, add_subpackage_method, add_toytree_method
from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError
# pylint: disable="too-many-branches"

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
    "resolve_polytomies",
    "add_internal_node",
    "add_child_node",
    "add_sister_node",
    "add_internal_node_and_child",
    "add_internal_node_and_subtree",
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
    >>> tree.mod.collapse_nodes(tree.get_mrca_node('r1', 'r2'))
    >>> tree.mod.collapse_nodes(tree.get_mrca_node('~r[1-4]')
    >>> tree = tree.set_node_data("dist", {22: 0.005, 23: 0.005})
    >>> tree = tree.set_node_data("support", {25: 50}, default=100)
    >>> tree = tree.collapse_nodes(min_dist=0.01, min_support=45)
    """
    if not query:  # == (): # Node 0 is always a tip anyways.
        selected = []
    else:
        selected = [i.idx for i in tree.get_nodes(*query)]

    # get tree and nodes copy
    if not inplace:
        tree = tree.copy()

    # remove internal nodes meeting criteria
    for nidx in range(tree.nnodes):
        node = tree[nidx]
        if not node.is_leaf():
            if (node.dist < min_dist) | (node.support < min_support) | (nidx in selected):
                if not node.is_root():
                    node._delete()
        # else:
            # logger.warning("Tip Nodes cannot be collapsed.")
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def remove_unary_nodes(tree: ToyTree, inplace: bool = False) -> ToyTree:
    """Return ToyTree with any unary Nodes removed.

    Parameters
    ----------
    inplace: bool
        If True then the original tree is changed in-place, and
        returned, rather than leaving original tree unchanged.
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
def rotate_node(
    tree: ToyTree,
    *query: Query,
    inplace: bool = False,
) -> ToyTree:
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
    Can chain multiple calls together:
    >>> tree.mod.rotate_node(14).mod.rotate_node(13).mod.rotate_node(12)
    """
    node = tree.get_mrca_node(*query)
    tree = tree if inplace else tree.copy()
    node = tree[node._idx]
    node._children = tuple(node.children[::-1])
    tree._update()
    return tree


@add_subpackage_method(TreeModAPI)
def extract_subtree(tree: ToyTree, *query: Query) -> ToyTree:
    """Return a subtree/clade extracted from a larger tree as a ToyTree.

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors (Node object, names, or idx labels)
        from which the MRCA is found. This will serve as the root Node
        of the returned tree.

    See Also
    --------
    `toytree.mod.prune`

    Example
    -------
    >>> tree = toytree.rtree.unittree(5)
    >>> subtree = tree.mod.extract_subtree("r0", "r1", "r2")
    >>> toytree.mtree([tree, subtree]).draw('p')
    """
    node = tree.get_mrca_node(*query)
    return ToyTree(node.copy(detach=True))


@add_subpackage_method(TreeModAPI)
def prune(
    tree,
    *query: Query,
    preserve_branch_length: bool = True,
    require_root: bool = False,
    inplace: bool = False,
) -> ToyTree:
    r"""Return a tree w/ the minimal edges connecting a subset of Nodes.

    All nodes not included in the entered 'nodes' list will be
    removed from the topology, and the mininal spanning edges to
    connect the remaining nodes are retained. The original root node
    is preserved if 'require_root=True', otherwise the lowest
    mrca connecting the selected nodes will be kept as the new root.

                4      prune([0,2])     4
               / \                     / \
              3   \      ------>      /   \
             / \   \                 /     \
            0   1   2               0       2

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels.
    preserve_branch_length: bool
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
    """
    # expand query into a set of Nodes
    nodes = set(tree.get_nodes(*query))
    nnodes = len(nodes)

    # add mrca Node for each pair and add the root Node
    nodes = nodes.union(set(
        tree.get_mrca_node(i, j) for i, j in
        itertools.permutations(nodes, 2))
    )
    nodes.add(tree.treenode)

    # TODO: this func could be simplified using tree.get_ancestors.

    # create a copy or operate in place
    if not inplace:
        tree = tree.copy()
        nodes = [tree[i.idx] for i in nodes]

    # keep track of ndescendants of each node after pruning to make
    # it easy to find the mrca later, and whether it is a mrca.
    ndesc = {}

    # traverse tree by idx number since we cannot do traversal func
    # while modifying the tree structure.
    for nidx in range(tree.nnodes):
        node = tree[nidx]

        # remove connections to this node
        if node not in nodes:
            for cnode in node.children:

                # add this node's dist to its children's dists
                if preserve_branch_length:
                    cnode._dist += node.dist

                # connect children to grandparent, rm self as child.
                cnode._up = node.up
                node.up._add_child(cnode)
            node.up._remove_child(node)

        # count ndescendants of this node after postorder pruning
        else:
            ndesc[node] = max(1, sum(ndesc[i] for i in node.children))

    # if a kept node is mrca then return it as the new root. If the
    # tree IS only a single Node then
    if not require_root:
        if nnodes == 1:
            tree.treenode = nodes[0]
        else:
            for node, ndesc in ndesc.items():
                if ndesc == nnodes:
                    tree.treenode = node
                    break
        tree.treenode._detach()
        tree._update()
        return tree

    # if keeping orig root node, but it is unary, then remove internal
    # node that is the current pseudo-root and extend its edges to root.
    if len(tree.treenode.children) == 1:
        child = tree.treenode.children[0]
        if child.children:
            for gchild in child.children:
                gchild._up = tree.treenode
                gchild._dist += child.dist
            tree.treenode._remove_child(child)
            tree.treenode._children = child.children

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
    prune: Extract a subtree from tree. The inverse of this function.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10)
    >>> tree.mod.drop_tips(1, 2, 3).draw()
    >>> tree.mod.drop_tips('~r[0-3]$').draw()
    >>> tree.mod.drop_tips('r1', 'r2')
    """
    nodes = tree.get_nodes(*query)
    tree = tree if inplace else tree.copy()
    tipnames = [i.name for i in nodes if i.is_leaf()]
    if len(tipnames) == tree.ntips:
        raise ToytreeError("You cannot drop all tips from the tree.")
    if not tipnames:
        logger.warning(f"No tips selected. Matched query: {nodes}")
    keeptips = [i for i in tree.get_tip_labels() if i not in tipnames]
    tree.mod.prune(*keeptips, preserve_branch_length=True, inplace=True)
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
    >>> tree.resolve_polytomy().draw();
    """
    nodes = tree.get_nodes(*query)
    tree = tree if inplace else tree.copy()
    nodes = [tree[i._idx] for i in nodes]
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

    Splits a branch spanning from node idx (A) to its parent (B)
    to create a new internal node (C). This is not an especially
    useful operation except for internal usage by toytree.

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
        no dist value is set then the edge midpoint is used.
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
        raise ValueError(
            f"the new Node dist must be >= 0 and <= {node.dist:.12g} (dist "
            f"of {node})")

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
        Edge length of the subtree stem dist (the subtree root Node
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

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10)
    >>> subtree = tree.mod.extract_subtree("r0", "r1", "r2")
    >>> new_tree = tree.mod.add_internal_node_and_subtree(
    >>>     "r4", subtree=subtree, subtree_rescale=True)
    >>> new_tree.draw(...)
    """
    # expand query
    node = tree.get_mrca_node(*query)
    if not inplace:
        tree = tree.copy()
        node = tree[node.idx]

    # always copy the subtree and get as a detached Node.
    if isinstance(subtree, ToyTree):
        subtree = subtree.treenode.copy()
    elif isinstance(subtree, Node):
        subtree = subtree.copy(detach=True)
    else:
        raise TypeError("subtree arg must be a ToyTree or Node instance.")

    # use a temporary parent name and set the proper name later
    pname = "PARENT@@@@@"
    add_internal_node(tree, node, name=pname, dist=parent_dist, inplace=True)

    # get parent node
    parent = tree.get_nodes(pname)[0]
    parent.name = parent_name if parent_name else ""

    # get STEM dist for the subtree parent Node
    if subtree_stem_dist is None:
        subtree_stem_dist = max(i.dist for i in parent.children) / 2.

    # optional: scale subtree edges to fit in same dist as sister.
    if subtree_rescale:
        remaining_dist = subtree.treenode.height - subtree_stem_dist
        subtree = subtree.mod.edges_scale_to_root_height(remaining_dist)

    # add as a new child to end of parent's children
    parent._add_child(subtree)

    # set the subtree stem dist
    subtree._dist = subtree_stem_dist

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
    t = toytree.rtree.unittree(16, treeheight=10)
    t.mod.prune(0, 1, 2, 3)
    t.draw()
