#!/usr/bin/env python

"""
Topology manipulation functions for ToyTrees.

This module includes function for manipulating ToyTrees by adding,
removing, or changing the relationships among TreeNodes. It is the
preferred way for users to modify tree topologies, compared to 
editing TreeNodes directly, since it ensures that the TreeNodes
have a valid ToyTree coordinate structure when returned.
"""

from typing import Optional, List, Union
from loguru import logger
from toytree import Node

logger = logger.bind(name="toytree")


def ladderize(tree, direction: bool=True, inplace: bool=False) -> 'ToyTree':
    """Return a ladderized tree (ordered descendants)

    In a ladderized tree nodes are rotated so that the left/ 
    right child always has fewer/more descendants.

    Parameters
    ----------
    direction: bool
        Reverse the laddizered order.
    """
    # get a copy of the tree to modify
    nself = tree if inplace else tree.copy()

    # visit all nodes from tips to root recording size on the way
    sizes = {}
    for nidx in range(tree.nnodes):
        node = nself[nidx]

        # get node size
        if node.is_leaf():
            sizes[node.idx] = 1
        else:
            sizes[node.idx] = sum(sizes[child.idx] for child in node.children)

            # rotate by size if size > 2 else use alphanumeric names
            if sizes[node.idx] > 2:
                key = lambda x: sizes[x.idx]
            else:
                key = lambda x: x.name
                
            node._children = tuple(sorted(node._children, key=key, reverse=direction))

    # update idx labels for new tree ladderization
    nself._update()
    return nself

def collapse_nodes(
    tree,
    min_dist: float=1e-6,
    min_support: float=0,
    inplace: bool = False,
    ) -> 'ToyTree':
    """Return ToyTree with some internal nodes collapsed.

    Nodes with dist or support values below minimum value setting
    are collapsed, resulting in polytomies. For example, set
    min_support=50 to collapse all nodes with support < 50.

    Parameters
    ----------
    min_dist: float
        The minimum dist (edge length) value allowed.
    min_support: float
        The minimum support (e.g., bootstrap) value allowed.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=20)
    >>> tree = tree.set_node_data("dist", {22: 0.005, 23: 0.005})
    >>> tree = tree.set_node_data("support", {25: 50}, default=100)
    >>> tree = tree.collapse_nodes(min_dist=0.01, min_support=45)
    """
    # get a copy of the tree to modify
    nself = tree if inplace else tree.copy()
    for nidx in range(nself.nnodes):
        node = nself[nidx]
        if not node.is_leaf():
            if (node.dist <= min_dist) | (node.support < min_support):
                node._delete()
    nself._update()
    return nself

def rotate_node(tree, idx: int, inplace: bool=False) -> 'ToyTree':
    """Return ToyTree with a selected Node rotated (children reversed).

    Parameters
    ----------
    idx: int
        The idx labels of the Node to rotate. This can be accessed
        from a Node object as Node.idx.
    """
    nself = tree if inplace else tree.copy()
    nself[idx]._children = nself[idx]._children[::-1] 
    nself._update()
    return nself

def prune(
    tree, 
    nodes: List[Union[int, 'Node']],
    preserve_branch_length: bool=True,
    require_root: bool=True,
    inplace: bool=False,
    ) -> "ToyTree":
    r"""Return a ToyTree as a subtree extracted from an existing tree.

    All nodes not included in the entered 'nodes' list will be
    removed from the topology, and the mininal spanning edges to
    connect the remaining nodes are retained. The root node is
    always preserved if 'require_root=True', otherwise the lowest
    mrca connecting the selected nodes will be kept as the new root.

                4      prune([0,2])     4     
               / \                     / \   
              3   \      ------>      /   \  
             / \   \                 /     \ 
            0   1   2               0       2

    Parameters
    ----------
    nodes: List[Nodes or ints]
        A list of int idx labels, or Node instances, representing Nodes
        (leaves and/or internal) to keep in the pruned subtree.
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
    # create a copy or operate in place
    nself = nself if inplace else tree.copy()

    # if nodes was entered as a single Node then make into a list
    nodes = []
    if isinstance(nodes, Node):
        nodes = [nodes]

    # require that root is in the node list to start.
    nnodes = len(nodes)
    if nself.treenode not in nodes:
        nodes.append(nself.treenode)

    # keep track of ndescendants of each node after pruning to make
    # it easy to find the mrca later, and whether it is a mrca.
    ndesc = {}

    # traverse tree in postorder (tips to root) and remove nodes
    for node in nself.traverse("postorder"):

        # remove connections to this node
        if node not in nodes:
            for cnode in node.children:

                # add this node's dist to its children's dists
                if preserve_branch_length:
                    cnode.dist += node.dist

                # connect children to grandparent, rm self as child.
                cnode._up = node.up
                node._up._children = (
                    node.children + \
                    tuple(i for i in node.up.children if i != node)
                )

        # if node is kept then pop it from the input set
        else:
            nodes.remove(node)

        # count ndescendants of this node after postorder pruning
        ndesc[node] = sum(1 for i in node._iter_descendants())

    # if any nodes remain in 'nodes' list then warn the user.
    for node in nodes:
        logger.warning(f"{node} is not in the tree.")

    # if a kept node is mrca then return it else return root
    if not require_root:
        for node, ndesc in ndesc.items():
            if ndesc == nnodes - 1:
                return node
    return nself

def add_internal_node(
    self, 
    idx: int, 
    dist: Optional[float]=None,
    name: Optional[str]=None, 
    ):
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
    :func:`.topo_add_tip_node`:
        Similar to this function but adds a tip node descending from C.
    
    Parameters
    ----------
    idx: int
        The idx label of the Node whose edge will be split. This
        Node will become a descendant of the newly created Node.
    dist: float
        The distance from the selected Node at which to insert
        the new Node. This will be set as the dist of the 
        descendant (A) whereas the new Node's dist (C) will be 
        the descendants prior dist minus this dist value. If 
        no dist value is set then the edge midpoint is used.
    name: Optional[str]
        A name string to apply to the new Node.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
    >>> tree = tree.mod.topo_new_internal_node(idx=0, dist=0.25)
    >>> tree.draw(ts='n', node_sizes=10);
    """
    tree = self._tree.copy()
    node = tree.idx_dict[idx]
    parent = node.up
    dist = dist if dist is not None else node.dist / 2.
    assert node.dist > dist > 0, (
        f"the new Node dist must be > 0 and < dist of Node {idx} ({node.dist}")
    new_node = toytree.TreeNode(
        name=name if name is not None else "", 
        dist=node.dist - dist,
    )
    node.dist = dist
    parent.children.remove(node)
    parent.children.append(new_node)
    new_node.up = parent
    new_node.children = [node]
    node.up = new_node
    tree._coords.update()
    return tree        

def add_tip_node(
    self,
    idx: int,
    name: Optional[str]=None,
    dist: Optional[float]=None,
    parent_dist: Optional[float]=None,
    parent_name: Optional[str]=None,
    ) -> 'toytree.ToyTree':
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
    idx: int
        The focal node for which to insert a sister lineage.
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

    Examples
    --------
    >>> # add a new tip node
    >>> tree = toytree.rtree.imbtree(5, treeheight=1e6)
    >>> tree = tree.mod.topo_add_tip_node(idx=3).draw();

    >>> # add a ghost lineage to the tree and draw as introgressor
    >>> tree = toytree.rtree.imbtree(5, treeheight=1e6)
    >>> tree = tree.mod.topo_add_tip_node(
    >>>     idx=3, name="x", parent_dist=2e5, dist=3e5)
    >>> tree.ladderize().draw(ts='c', admixture_edges=(['r0', 'r1'], 'x'));
    """
    tree = self._tree.copy()
    orig_parent = tree.idx_dict[idx].up
    sister_1 = tree.idx_dict[idx]
    if dist is None:
        dist = sister_1.dist / 2.
    sister_2 = toytree.TreeNode(name=name, dist=dist)
    if parent_dist is None:
        parent_dist = orig_parent.height - dist

    # modify sister_1 and new_parent dist
    sister_1.dist = sister_1.dist - parent_dist
    new_parent = toytree.TreeNode(name=parent_name, dist=parent_dist)

    orig_parent.children.remove(sister_1)
    orig_parent.children.append(new_parent)
    sister_1.up = new_parent
    sister_2.up = new_parent
    new_parent.children = [sister_1, sister_2]
    new_parent.up = orig_parent

    tree._coords.update()
    return tree

def move_clade(
    tree, 
    idx0: int,
    idx1: int,
    height: Optional[float]=None,
    name: str="",
    shrink: bool=False,
    inplace: bool=False,
    ):
    r"""Move a clade from one part of the tree to another.

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
    height: Optional[float]
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
    src = tree.idx_dict[idx0]
    dest = tree.idx_dict[idx1]

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


# def speciate(self, idx, name=None, dist_prop=0.5):
#     """
#     Split an edge to create a new tip in the tree as in a
#     speciation event.
#     """
#     # make a copy of the toytree
#     nself = self.copy()

#     # get Treenodes of selected node and parent 
#     ndict = nself.get_feature_dict('idx')
#     node = ndict[idx]
#     parent = node.up

#     # get new node species name
#     if not name:
#         if node.is_leaf():
#             name = node.name + ".sis"
#         else:
#             names = nself.get_tip_labels(idx=idx)
#             name = "{}.sis".format("_".join(names))

#     # create new speciation node between them at dist_prop dist.
#     newnode = parent.add_child(
#         name=parent.name + ".spp",
#         dist=node.dist * dist_prop
#     )

#     # connect original node to speciation node.
#     node.up = newnode
#     node.dist = node.dist - newnode.dist
#     newnode.add_child(node)

#     # drop original node from original parent child list
#     parent.children.remove(node)

#     # add new tip node (new sister) and set same dist as onode
#     newnode.add_child(
#         name=name,
#         dist=node.up.height,
#     )

#     # update toytree coordinates
#     nself._coords.update()
#     return nself     
