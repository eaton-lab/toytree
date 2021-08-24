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
    dist: Optional[float]=None,
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
        E   \          /     \          /   X --- aut-set dist
       / \   \        C       Y        /   / \  
      D   \   \  -->            -->   /   /   D --- auto-set dist
     / \   \   \          D          /   /   / \  
    A   B   C   Y        / \        A   Y   A   B --- maintained dist
                        A   B

    Note
    ----
    This operation is synonymous with a subprune regrafting (SPR).
    Internal nodes that leave no descendants (e.g., E) from above
    are removed from the tree.
    
    Parameters
    ----------
    idx0: int
        The idx label of the Node at the top of the clade that 
        will be pruned from the tree and re-attached elsewhere.

    idx1: int
        The idx label of the Node whose branch will be split to 
        create a new parent node of the re-attached clade. 

    dist: Optional[float]
        The distance along the length of the idx1 Node's edge at
        which to insert the new parent Node. This must be > 0 
        and < idx1 Node dist. If None the midpoint is used. The
        dist of the new internal node will be the original idx1 
        Node dist minus this value.
    
    name: Optional[s]    
        A name string to apply to the newly created internal node.

    shrink: bool
        If shrink is True then the subtree edge lengths (dists) 
        will be scaled to allow the clade to be inserted anywhere
        in the tree. If False a ToyTreeError is raised if the 
        subclade cannot be inserted below the dist value.
    """
    tree = self._tree.copy()

    clade = tree.idx_dict[idx0]
    clade_parent = clade.up
    clade.detach()

    # this will set new idxs on everything...
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

