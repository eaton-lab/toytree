#!/usr/bin/env python

"""Topology manipulation functions for ToyTrees.

This module includes function for manipulating ToyTrees by adding,
removing, or changing the relationships among TreeNodes. It is the
preferred way for users to modify tree topologies, compared to
editing TreeNodes directly, since it ensures that the TreeNodes
have a valid ToyTree coordinate structure when returned.

Most of these functions use a Query selector...
"""

from typing import Optional, TypeVar, Union
import itertools
from loguru import logger
import numpy as np
from toytree import Node
from toytree.utils import ToytreeError

# pylint: disable="too-many-branches"

logger = logger.bind(name="toytree")
ToyTree = TypeVar("ToyTree")
Query = TypeVar("Query", str, int, Node)


def ladderize(tree, direction: bool=False, inplace: bool=False) -> ToyTree:
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
    direction = bool(direction) # needed to ensure invert below against int arg

    # visit all nodes from tips to root recording size on the way
    sizes = {}
    for nidx in range(tree.nnodes):
        node = nself[nidx]

        # get node size
        if node.is_leaf():
            sizes[node.idx] = 1
        else:
            sizes[node.idx] = sum(sizes[child.idx] for child in node.children)
            key = lambda x: sizes[x.idx]
            node._children = tuple(sorted(node._children, key=key, reverse=direction))

    # update idx labels for new tree ladderization
    nself._update()
    return nself

def collapse_nodes(
    tree: ToyTree,
    *query: Query,
    min_dist: float=1e-6,
    min_support: float=0,
    inplace: bool=False,
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
    >>> tree.mod.collapse_nodes(tree.get_mrca_node('r[1-4]', regex=True))
    >>> tree = tree.set_node_data("dist", {22: 0.005, 23: 0.005})
    >>> tree = tree.set_node_data("support", {25: 50}, default=100)
    >>> tree = tree.collapse_nodes(min_dist=0.01, min_support=45)
    """
    if not query: # == (): # Node 0 is always a tip anyways.
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

def rotate_node(
    tree: ToyTree,
    *query: Query,
    regex: bool=False,
    inplace: bool=False,
    ) -> ToyTree:
    """Return ToyTree with one Node rotated (children order reversed).

    Rotates only one Node per call. Internal Nodes are easiest selected
    by idx label, or by entering multiple tip Node names from which the
    MRCA will be selected and rotated.

    Parameters
    ----------
    *query: str, int, or Node
        The Node to rotate can be selected by entering the Node object,
        or its idx label, or name str. For internal Nodes, multiple
        queries can be entered and their MRCA will be rotated.
    regex: bool
        If True then Node name strings are treated as regular
        expressions that can match to multiple Nodes.
    inplace: bool
        If True then the original tree is changed in-place, and
        returned, rather than leaving original tree unchanged.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10)
    >>> toytree.mod.rotate_node(tree, 12)
    >>> toytree.mod.rotate_node(tree, 'r0', 'r1')
    >>> toytree.mod.rotate_node(tree, 'r[0-3]$', regex=True)
    """
    idx = tree.get_mrca_node(*query, regex=regex).idx
    if not inplace:
        tree = tree.copy()
    tree[idx]._children = tree[idx]._children[::-1]
    tree._update()
    return tree

# def extract_subtree(tree, root)

def prune(
    tree,
    *query: Query,
    regex: bool=False,
    preserve_branch_length: bool=True,
    require_root: bool=False,
    inplace: bool=False,
    ) -> ToyTree:
    r"""Return a ToyTree as a subtree extracted from an existing tree.

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
    regex: bool
        If True then Node name strings are treated as regular
        expressions that can match to multiple Nodes.
    preserve_branch_length: bool
        If True then the edge lengths of internal nodes that are
        removed are merged into the 'dist' attribute of their
        descendant node that is preserved.
    require_root: bool
        If True then the root node is always preserved. If False
        then the root is only preserved if is it the mrca of the
        selected nodes, otherwise the mrca Node is returned.
    inplace: bool
        If True then the original tree is changed in-place, and
        returned, rather than leaving original tree unchanged.
    """
    # expand query into a set of Nodes
    nodes = set(tree.get_nodes(*query, regex=regex))    
    nnodes = len(nodes)

    # add mrca Node for each pair and add the root Node
    nodes = nodes.union(set(
        tree.get_mrca_node(i, j) for i, j in 
        itertools.permutations(nodes, 2))
    )
    nodes.add(tree.treenode)

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

def remove_unary_nodes(tree: ToyTree, inplace: bool=False):
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
        if not node in tipset:
            new_parent = node._up
            if new_parent:
                true_node = node._children[0]
                new_parent._add_child(true_node)
                new_parent._remove_child(node)
                true_node._dist += node._dist
    tree._update()
    return tree

def drop_tips(
    tree: ToyTree,
    *query: Query,
    regex: bool=False,
    inplace: bool=False,
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
    regex: bool
        If True then Node name strings are treated as regular
        expressions that can match to multiple Nodes.
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
    >>> tree.mod.drop_tips('r[0-3]$', regex=True).draw()
    >>> tree.mod.drop_tips('r1', 'r2')
    """
    tree = tree if inplace else tree.copy()
    nodes = tree.get_nodes(*query, regex=regex)
    tipnames = [i.name for i in nodes if i.is_leaf()]
    if len(tipnames) == tree.ntips:
        raise ToytreeError("You cannot drop all tips from the tree.")
    if not tipnames:
        logger.warning(f"No tips selected. Matched query: {nodes}")
    keeptips = [i for i in tree.get_tip_labels() if i not in tipnames]
    tree.mod.prune(*keeptips, preserve_branch_length=True, inplace=True)
    return tree

def resolve_polytomies(
    tree: ToyTree,
    *query: Query,
    regex: bool=False,
    dist: float=1.0,
    support: float=100,
    recursive: bool=True,
    seed: Optional[int]=None,
    inplace: bool=False,
    ) -> ToyTree:
    """Return ToyTree with one or more polytomies randomly resolved.

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. If no Nodes are selected then ALL nodes
        that are multifurcating will be resolved.
    regex: bool
        If True then Node name strings are treated as regular
        expressions that can match to multiple Nodes.
    dist: float
        The dist value to set on newly created nodes.
    support: float
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
    tree = tree if inplace else tree.copy()
    nodes = tree.get_nodes(*query, regex=regex)
    rng = np.random.default_rng(seed)

    for node in nodes:
        _resolve_nodes(
            node=node, dist=dist, support=support,
            rng=rng, recursive=recursive)
    tree._update()
    return tree

def add_internal_node(
    tree: ToyTree,
    *query: Query,
    regex: bool=False,
    dist: Optional[float]=None,
    name: Optional[str]=None,
    inplace: bool=False,
    ) -> ToyTree:
    r"""Add an internal node by splitting an edge to create new node.

    Splits a branch spanning from node idx (A) to its parent (B)
    to create a new internal node (C). This is not an especially
    useful operation except for internal usage by toytree.

                B                      B
               / \                    / \
              /   \      ---->       C   \
             /     \                /     \
            A       X              A       X

    See Also
    --------
    :func:`.add_tip_node`:
        Similar to this function but adds a tip node descending from C.

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. If multiple are entered the MRCA node will
        be used as the base of the edge to split.
    regex: bool
        If True then Node name strings are treated as regular
        expressions that can match to multiple Nodes.
    dist: float
        The distance from the selected Node at which to insert
        the new Node. This will be set as the dist of the
        descendant (A) whereas the new Node's dist (C) will be
        the descendants prior dist minus this dist value. If
        no dist value is set then the edge midpoint is used.
    name: Optional[str]
        A name string to apply to the new Node.
    inplace: bool
        Modify tree in place.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
    >>> tree = tree.mod.add_internal_node('r0', dist=0.25)
    >>> tree.draw(ts='n', node_sizes=10);
    """
    # expand query
    node = tree.get_mrca_node(*query, regex=regex)
    if not inplace:
        tree = tree.copy()
        node = tree[node.idx]

    # get insertion edge and dist of the new Node
    parent = node.up
    dist = dist if dist is not None else node.dist / 2.
    if not node.dist > dist > 0:
        raise ValueError("the new Node dist must be > 0 and < dist "
            f"of {node} (dist={node.dist})")

    # create the new Node and mend connections nearby
    new_node = Node(
        name=name if name is not None else "",
        dist=node.dist - dist,
    )
    node._dist = dist
    parent._remove_child(node)
    parent._add_child(new_node)
    new_node._up = parent
    new_node._children = (node, )
    node._up = new_node
    tree._update()
    return tree

def add_tip_node(
    tree: ToyTree,
    *query: Query,
    regex: bool=False,
    name: Optional[str]=None,
    dist: Optional[float]=None,
    parent_dist: Optional[float]=None,
    parent_name: Optional[str]=None,
    inplace: bool=False,
    ) -> ToyTree:
    r"""Add a tip node by splitting an edge to create a new parent
    and descendant node pair.

    Splits a branch spanning from node idx (A) to its parent (B)
    to create a new ancestral node (C) and descendant (D). The
    new nodes can be given names and dist values. By default, if
    only a dist is entered for the new sister (D) then the new
    ancestor node (C) dist value will be automated to make node
    D align at the same height as node A.

                B                      B
               / \                    / \
              /   \      ---->       C   \
             /     \                / \   \
            A       X              A   D   X

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. If multiple are entered the MRCA node will
        be used as the base of the edge to split.
    regex: bool
        If True then Node name strings are treated as regular
        expressions that can match to multiple Nodes.
    name: str
        Optional name for the new sister node.
    dist: float
        The dist (edge length) of the new sister node. If None
        this will be set to 1/2 of the sister's original dist.
        If parent_dist is None then the parent_dist will be set
        automatically to make the new sister node height align
        with its sister.
    parent_dist: float
        The dist (edge length) of the new ancestral node. If left
        at None then this value is automatically set to make node
        D align with A. Changing this value does not affect the
        height of node A, but does affect both nodes C and D.
        By setting parent_dist and dist both you can explicitly
        define any heights for the new nodes.
    parent_name: str
        Optional name for the new internal parent node.
    inplace: bool
        If False (default) a copy of the original tree is returned.

    Examples
    --------
    >>> # add a new tip node
    >>> tree = toytree.rtree.imbtree(5, treeheight=1e6)
    >>> tree = tree.mod.add_tip_node(3).draw();
    >>>
    >>> # add a ghost lineage, and draw as introgressing taxon.
    >>> tree = toytree.rtree.imbtree(5, treeheight=1e6)
    >>> tree = tree.mod.add_tip_node(
    >>>     idx=3, name="x", parent_dist=2e5, dist=3e5)
    >>> tree.ladderize().draw(ts='c', admixture_edges=(['r0', 'r1'], 'x'));
    """
    # get tree and mrca copy
    sister_1 = tree.get_mrca_node(*query, regex=regex)
    if not inplace:
        tree = tree.copy()
        sister_1 = tree[sister_1.idx]    

    # selected a Node whose edge will be split.
    sister_1 = tree.get_mrca_node(*query, regex=regex)
    # create a new Node that will become sister to selected Node and
    # set its edge length to initially match the selected Node.
    sister_2 = Node(name=name, dist=sister_1.height)
    # store reference to selected Node's orig parent (later gparent)
    orig_parent = sister_1.up

    # set the dist and height of sisters (insertion height)
    if dist is None:
        dist = sister_1.dist / 2.
    if parent_dist is None:
        parent_dist = orig_parent.height - dist
        if parent_dist < 0:
            logger.warning("`parent_dist` arg to `add_tip_node` causes negative branch lengths")
    sister_2._dist += dist
    sister_1._dist = dist

    # The two sisters will be childen of the new internal Node.
    new_parent = Node(name=parent_name, dist=parent_dist)
    orig_parent._remove_child(sister_1)
    orig_parent._add_child(new_parent)
    sister_1._up = new_parent
    sister_2._up = new_parent
    new_parent._children = (sister_1, sister_2)
    new_parent._up = orig_parent
    tree._update()
    return tree

def add_subtree(
    tree: ToyTree,
    *query: Query,
    subtree: Union[ToyTree, Node],
    regex: bool=False,
    subtree_stem_dist: Optional[float]=None,
    subtree_rescale: bool=True,
    parent_dist: Optional[float]=None,
    parent_name: Optional[str]=None,
    inplace: bool=False,
    ) -> ToyTree:
    r"""Add a subtree by splitting an edge to create a new parent
    Node and inserting the descendant subtree.

    Splits a branch spanning from node (A) to its parent (C) to
    create a new ancestral node (Z) from which a subtree (Y) will
    be inserted. The name of node (Z) and the stem dist of node (Y) 
    can be set. By default, if left as None, the stem dist will be
    set to half the distance to the farthest leaf, and the subtree
    will be scaled to fill the other half distance so that it aligns
    as the farthest tip node distance. 

                 C                         C
                /\                        Z \
               /  \                      /\  \
              /    \      ---->         /  Y  \
             /      \                  /  / \  \
            A        B                A  W   X  B

    Parameters
    ----------
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. If multiple are entered the MRCA node will
        be used as the base of the edge to split.
    regex: bool
        If True then Node name strings are treated as regular
        expressions that can match to multiple Nodes.
    subtree: ToyTree or Node
        A subtree to insert into the target tree.
    parent_dist: float or None
        Edge length of the new inserted Node (Z). This is the length
        from the top at which it will be inserted into an existing 
        edge (e.g., A). If None it will be automated half the dist
        to the farthest leaf.
    subtree_stem_dist: float or None
        Edge length of the stem edge connecting the new inserted Node
        (Z) to the inserted subtree (Y). If None it will be automated
        to half the dist to the farthest leaf.
    parent_name: str
        Optional name for the new internal parent node.
    rescale_subtree: bool
        If True all edges of the subtree will be rescaled to fit
        in the dist below where the subtree is inserted so that the
        subtrees farthest tip will align with the 
    inplace: bool
        If False (default) a copy of the original tree is returned.
    """
    # get the selected Node and create a new sister
    tree = tree if inplace else tree.copy()
    sister = tree.get_mrca_node(*query, regex=regex)
    parent = sister.up
    new_node = Node(name=parent_name if parent_name else "", dist=0.)

    # set dist of new_node (parent_dist param).
    if parent_dist is not None:
        assert 0 <= parent_dist <= sister.dist, (
            "parent_dist (node insertion) must be within length of the "
            f"query edge ({sister.dist})")
        new_node._dist = parent_dist
        sister._dist -= parent_dist
    else:
        new_node._dist = sister.dist / 2
        sister._dist -= new_node._dist

    # scale the subtree to fit before connecting it.
    if subtree_stem_dist is not None:
        assert 0 <= subtree_stem_dist <= (parent.height - new_node._dist), (
            "subtree_stem_dist arg will create a negative branch length.")
        if subtree_rescale:
            height = (parent.height - new_node._dist) - subtree_stem_dist
            subtree = subtree.mod.edges_scale_to_root_height(
                height, include_stem=False)
        subtree.treenode._dist = subtree_stem_dist            
    else:
        height = parent.height - new_node._dist
        subtree = subtree.mod.edges_scale_to_root_height(
            height, include_stem=True)

    # connect parent to (new_node, sister)
    parent._add_child(new_node)
    parent._remove_child(sister)
    new_node._add_child(sister)

    # insert subtree as a child of new_node
    new_node._add_child(subtree.treenode)
    tree._update()
    return tree    


# NEEDS WORK, not yet exposed to API.
def move_clade(
    tree: ToyTree,
    idx0: int,
    idx1: int,
    height: Optional[float]=None,
    name: str="",
    shrink: bool=False,
    inplace: bool=False,
    ):
    r"""Move a clade from one part of the tree to another (SPR).

    Splits a branch spanning from node idx1 (Y) to its parent (Z)
    to create a new ancestral node (X). The idx0 clade is detached
    from the tree (D) and its parent is removed if it leaves only
    one child (E). The detached clade is reattached to the new
    ancestral node (D -> X) while maintaining the edge lengths of
    the subtree. The length of the edge connecting idx0 to the new
    node (D, X) is automatically set to maintain ultrametricity,
    unless the subclade height is greater than the dist arg. This
    will raise an error unless shrink=True, in which case the
    subtree is scaled to half the dist height to fit.

                          Z
          Z              / \              Z
         / \            E   \            / \
        E   \          /     \          /   X --- auto-set dist
       / \   \        C       Y        /   / \
      D   \   \  -->            -->   /   /   D --- auto-set dist
     / \   \   \          D          /   /   / \
    A   B   C   Y        / \        A   Y   A   B --- maintained dist
                        A   B

    Note
    ----
    This operation is synonymous with a rooted subprune regrafting
    (SPR) move. Internal nodes that leave no descendants (e.g., E)
    from above are removed from the tree.

    See Also
    --------
    `toytree.mod.move_spr`: Faster SPR move function, but without
    arguments to modify edge lengths like in this function.

    Parameters
    ----------
    tree: ToyTree
        A tree object.
    idx0: int
        The idx label of the Node at the top of the clade that
        will be pruned from the tree and re-attached elsewhere.
    idx1: int
        The idx label of the Node whose branch will be split to
        create a new parent node of the re-attached clade.
    height: float or None
        The height at which to insert node idx0 above node idx1.
        This value must be in the interval between the height of
        idx1 and its parent (node.height, node.height + node.dist).
        If None then the node will be inserted at the midpoint
        along node idx1's edge.
    name: str
        A name string to apply to the newly created internal node.
    shrink: bool
        If shrink is True then the subtree edge lengths (dists)
        will be scaled to allow the clade to be inserted anywhere
        in the tree. If False a ToyTreeError is raised if the
        subclade cannot be inserted below the dist value.

    Returns
    -------
    ToyTree
        A modified copy of the original tree is returned.
    """
    # create a copy
    tree = tree if inplace else tree.copy()

    # get selected nodes (FIXME: use nas to allow names selections)
    src = tree[idx0]
    dest = tree[idx1]

    # cannot move a clade to its own children in rooted move
    assert idx0 != idx1, "idx0 must be different from idx1"
    assert idx0 != tree.treenode, "src node cannot be root."
    assert idx1 != tree.treenode, "dest node cannot be root."
    assert dest not in src.get_descendants(), (
        "dest node cannot be a descendant of src in a rooted SPR move."
    )

    # check the height arg
    if height is not None:
        assert dest.up.height >= height >= dest.height, (
            f"height {height} does occur on the node {idx1}'s edge: "
            f"({dest.height}-{dest.up.height})")

    # get dist arg from height
    if height is None:
        dist = dest.dist / 2.
    else:
        dist = height - dest.height

    # if the dest is the src's parent, then we only need to modify the
    # dist of dest and return the tree.
    if dest == src.up:
        diff = dest.dist - dist
        dest.dist = dist
        for child in dest.children:
            child.dist += diff
        return tree

    # create new internal node.
    newnode = Node(name=str(name), dist=dest.dist - dist)

    # detach the source clade.
    ancestor = src.up
    src = src.detach()

    # remove the null node (preserving bls) and in case the null node
    # is the root, reset the tree variable to a new TreeNode root.
    if ancestor.is_root():
        if dest.up == tree.treenode:
            root = newnode
        else:
            root = [i for i in tree.treenode.children if i != ancestor][0]
        tree.treenode.delete(True, True)
    else:
        root = tree.treenode
    ancestor.delete(True, True)

    # set src dist (optional allowing shrink to fit)
    if src.height > dest.height + dist:
        if not shrink:
            raise ValueError(
                f"Clade {idx0} does not fit below clade {idx1}. "
                "Use shrink=True.\n"
                f"Details: node {idx0} height={src.height}; "
                f"node {idx1} height={dest.height + dist}; "
                f"dist={dist}; "
                f"Error b/c {src.height} > {dest.height} + {dist}")
        orig = src.height + src.dist
        scale = orig / (dest.height + dist)
        for node in src.traverse():
            node.dist /= scale
    else:
        src.dist = dest.height + dist - src.height

    # set dest dist
    dest.dist = dist

    # connect newnode to its parent
    dest_parent = dest.up
    dest_parent.children.append(newnode)
    dest_parent.children.remove(dest)

    # connect newnode to its children
    newnode.up = dest_parent
    newnode.children = [src, dest]
    src.up = newnode
    dest.up = newnode

    # re-toytree it from the root
    tree = toytree.tree(root)

    # TODO: add highlight boolean arg and color moved clade.
    # tree.style.edge_colors = ['black'] * tree.nnodes
    # for idx in tree.get_node_descendant_idxs(src)
    return tree

def _resolve_nodes(
    node: Node,
    dist: float,
    support: float,
    rng: np.random.Generator,
    recursive: bool,
    ) -> Node:
    """Resolve multifurcating Nodes.

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
