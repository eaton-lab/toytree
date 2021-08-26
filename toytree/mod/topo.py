#!/usr/bin/env python

"""
Topology manipulation functions for ToyTrees.

This module includes function for manipulating ToyTrees by adding,
removing, or changing the relationships among TreeNodes. It is the
preferred way for users to modify tree topologies, compared to 
editing TreeNodes directly, since it ensures that the TreeNodes
have a valid ToyTree coordinate structure when returned.
"""

from typing import Optional
import toytree


def topo_add_internal_node(
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


def topo_add_tip_node(
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


def topo_move_clade(
    self, 
    idx0: int,
    idx1: int,
    height: Optional[float]=None,
    name: Optional[str]=None,
    shrink: bool=False,
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
    name: Optional[s]    
        A name string to apply to the newly created internal node.
    shrink: bool
        If shrink is True then the subtree edge lengths (dists) 
        will be scaled to allow the clade to be inserted anywhere
        in the tree. If False a ToyTreeError is raised if the 
        subclade cannot be inserted below the dist value.
    """
    # create a copy
    tree = self._tree.copy()

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
    newnode = toytree.TreeNode(
        name=name if name is not None else "", 
        dist=dest.dist - dist,
    )

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
    return tree
