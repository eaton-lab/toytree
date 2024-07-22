#!/usr/bin/env python

"""A simple immutable Node class.

A Node represents a vertex in a tree or graph, with connections
represented by pointers to other Node objects in its `.up` and
`.children` attributes. The core purpose of Node objects it to
provide *traversal* functions for accessing connected Nodes in an
order determined by their connections.

Notes
-----
This class is inspired by the ete3.TreeNode class object, and retains
similarities in syntax to make it easy to learn for ete users. However,
it is greatly simplified, and differs in several other important
respects. Most notably, the toytree.Node class is intended to be
_immutable_, meaning users are not able to directly edit .dist, .up,
.children, or other attributes of Node objects that affect the tree
topology. Instead, ToyTree class objects have functions for modifying
Nodes that do so in the context of updating the entire tree (i.e.,
updating other Node's attributes if needed). Thus, toytree.Node is a
more minimal object used mainly for traversal and to store Node data.

References
----------
- https://en.wikipedia.org/wiki/Tree_traversal
- https://github.com/ete3
"""

# pylint: disable=no-name-in-module
# pylint: disable=invalid-name
# pylint: disable=too-many-public-methods
# pylint: disable=no-self-use, unused-argument


from __future__ import annotations
from typing import List, Optional, Union, Iterator, Tuple  # Set, Any
from functools import total_ordering
from copy import deepcopy
from collections import deque

from loguru import logger
import numpy as np
from toytree.utils import TreeNodeError

# register the logger
logger = logger.bind(name="toytree")


class Node:
    """Node class representing a single vertex in a ToyTree.

    Node objects store the parent/child relationships among directly
    connected Nodes, as well as attributes/features of a Node. The
    core purpose of Node objects it to provide *traversal* functions
    for accessing connected Nodes in an order determined by their
    connections. The root of a set of connected Nodes is stored as
    the `treenode` attribute of a ToyTree class object.

    Note
    ----
    Node class objects are intended to be *mostly* immutable, i.e.,
    not directly modified by users. This is to reduce user errors by
    modifying Node features that affect the tree topology or values.
    Nodes are mutable, however, in terms of assigning and modifying
    arbritrary data to Nodes (e.g., `tree[3].body_size = 10`).

    Although Nodes *can* be modified directly, the recommended way
    is to use specific ToyTree class functions to change attributes
    of Nodes (e.g., change topology, edge lengths, rotations, rooting,
    features). See functions in `ToyTree.mod` to modify the tree, and
    see `ToyTree.set_node_data` to assign or modify data on Nodes.

    Parameters
    ----------
    name: str
        Node name is shown as either a tip or node label in tree
        drawings, and can be any string, including HTML.
    dist: float
        Node dist value is the edge length from this Node to its parent.
    support: float
        Node support value for the edge from this Node to its parent.

    Examples
    --------
    >>> # you can create a Node directly, but this is not intended.
    >>> node = toytree.Node(name='root')
    >>>
    >>> # instead, create a ToyTree and access Nodes from it.
    >>> tree = toytree.rtree.unittree(ntips=10, seed=123)
    >>>
    >>> # Nodes can be accessed by traversal from ToyTrees or Nodes
    >>> for node in tree.traverse("postorder"):
    >>>     print(node)
    >>>
    >>> # or, Nodes can be indexed from ToyTrees by their idx label.
    >>> node = tree[3]
    >>>
    >>> # other Nodes can be accessed relative to this one by traversal
    >>> parent = node.up
    >>> ancs = node.get_ancestors()
    >>> descs = node.get_descendants()
    >>>
    >>> # Node data/attributes can be accessed from a Node
    >>> print(node.name, node.idx, node.dist)
    >>>
    >>> # but cannot be modified on Nodes (they are immutable)
    >>> node.dist = 10  # raises a TreeNodeError
    """

    def __init__(self, name: str = "", dist: float = 0.0, support: float = np.nan):
        self._name = str(name)
        """: name string assigned to Node."""
        self._dist = float(dist)
        """: length value associated to the edge above this Node."""
        self._support = float(support)
        """: support value associated to the edge above this Node."""

        # Non-init attributes.
        self._children: Tuple[Node] = tuple()
        """: tuple of Node instances directly descended from this Node."""
        self._up: Optional[Node] = None
        """: the ancestor Node instance (towards root) from this Node."""
        self._idx: int = -1
        """: unique node index label (idx) assigned to Nodes in a ToyTree."""
        self._height: float = 0.0
        """: height of this Node above the connected Node farthest from root."""
        self._x: float = 0.0
        """: private attribute updated during drawing as x-coordinate."""

    @property
    def name(self) -> str:
        """Name string assigned to Node."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the 'name' attribute, forced as a string."""
        self._name = str(value)

    @property
    def dist(self) -> float:
        """Edge length associated to the edge above this Node."""
        return self._dist

    @dist.setter
    def dist(self, value: float) -> None:
        """Set the dist attribute, forced as an int or float."""
        raise TreeNodeError(
            "Cannot set .dist attribute of a Node. If you are an "
            "advanced user then you can do so by setting ._dist. "
            "See the docs section on Modifying Nodes and Tree Topology."
        )

    @property
    def support(self) -> float:
        """Return the support value for the edge above this Node."""
        return self._support

    @support.setter
    def support(self, value: float) -> None:
        """Set a 'support' attribute. This is like any other feature
        that can be set on a Node, but defaults to nan for all Nodes."""
        try:
            self._support = float(value)
        except ValueError as err:
            raise TreeNodeError("Node support must be int or float") from err

    @property
    def height(self) -> float:
        """Return the cached height of this Node.

        Node heights are calculated relative to a connected Node
        that is furthest from the root Node, defined as height 0.

        `height` is an emergent property of a collection of Nodes, and
        thus cannot be set for an individual Node. It can, however, be
        set from a ToyTree (collection of Nodes), using `set_node_data`,
        which will modify the `.dist` attributes of multiple Nodes to
        set the height of one or more Nodes to the entered values. This
        can also be set using `toytree.mod.set_node_heights()`.
        """
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        """height Node attribute cannot be set by user.        """
        raise TreeNodeError(
            "Cannot set .height attribute of a Node since it is an emergent "
            "property of multiple Nodes. The prefered method of setting Node "
            "heights is to use `set_node_data` from a ToyTree, or "
            "`set_node_heights` from the `.mod` submodule. See the docs "
            "section on Modifying Nodes and Tree Topology for more details. "
            "Finally, if you know what you are doing you *can* force the "
            "height of a Node by setting its `._height` attribute."
        )

    @property
    def children(self) -> Tuple[Node]:
        """Return a list of child Nodes of this Node."""
        return self._children

    @children.setter
    def children(self, value: Node) -> None:
        """The children tuple cannot be modified. See ToyTree.mod."""
        raise TreeNodeError(
            "Cannot set .children attribute of a Node. If you are an "
            "advanced user then you can do so by setting ._children. "
            "See the docs section on Modifying Nodes and Tree Topology."
        )

    @property
    def up(self) -> Union[Node, None]:
        """The parent node (next node towards root) from this node."""
        return self._up

    @up.setter
    def up(self, value: Node) -> None:
        """Modifying up requires a call to ToyTree._update()."""
        raise TreeNodeError(
            "Cannot set .up attribute of a Node. If you are an "
            "advanced user then you can do so by setting ._up. "
            "See the docs section on Modifying Nodes and Tree Topology."
        )

    @property
    def idx(self) -> int:
        """Return the unique integer idx label of this Node."""
        return self._idx

    @idx.setter
    def idx(self, value: int):
        """This will raise an TreeNodeError, users cannot set idx."""
        raise TreeNodeError(
            "Cannot set .idx attribute of a Node. If you are an "
            "advanced user then you can do so by setting ._idx. "
            "See the docs section on Modifying Nodes and Tree Topology."
        )

    ################################################
    # IDENTITY
    ################################################

    def is_leaf(self) -> bool:
        """Return True if Node is a leaf (terminal)."""
        return not bool(self.children)

    def is_root(self):
        """Return True if Node has no parent."""
        return self.up is None

    def copy(self, detach: bool = False) -> Node:
        r"""Return a deepcopy of this Node (and its connected Nodes).

        All connected Nodes (ancestral and descendant) are also copied
        and the can be referenced from the returned Node. The Node
        that calls .copy() can optionally be detached from its
        ancestors and returned as the root of its subtree. This is
        slightly faster since only descendant Nodes are copied.

                4   when .copy called from Node 3   n4
               / \    all connected Nodes are       / \
              3   \     also copied ------>       n3   \
             / \   \                              / \   \
            0   1   2                           n0  n1  n2

        Parameters
        ----------
        detach: bool
            If True the Node is returned as the treenode (root) of its
            subtree with all Nodes of the subtree copied. If False any
            ancestral Nodes are also copied and are connected to the
            returned Node.

        See Also
        --------
        `Toytree.copy()`, `toytree.mod.extract_subtree`

        Examples
        --------
        >>> tree = toytree.tree("((a,b),c);")
        >>> node = tree.get_mrca_node("a", "b")
        >>> cnode = node.copy(detach=True)
        >>> subtree = toytree.tree(cnode)
        """
        # return a deepcopy of this Node and its descendants detached
        # from any ancestor Nodes.
        if detach:
            # save connection to ancestors and remove it from this Node
            saved_connection = self.up
            self._up = None
            # create deepcopy of this Node and descendants (not ancestors)
            copied_node = deepcopy(self)
            # restore connection to ancestors for the original Node
            self._up = saved_connection
            return copied_node

        # get connected root Node
        treenode = self.get_treenode()

        # make a deepcopy of root, otherwise only nested are copied.
        # TODO: is it still necessary to do this?
        copied_treenode = deepcopy(treenode)

        # find focal node to be returned
        for node in copied_treenode.traverse():
            if (node.idx == self.idx) and (node.name == self.name):
                return node
        raise TreeNodeError("copy failed, tree structure is broken.")

    #################################################
    # DUNDERS
    #################################################

    def __repr__(self) -> str:
        """Returned string showing Node idx and name only if present."""
        _idx = "" if self.idx == -1 else f"idx={self.idx}"
        _name = "" if not self.name else f"name='{self.name}'"
        inner = ", ".join([i for i in (_idx, _name) if i])
        return f"<Node({inner})>"

    # def __str__(self) -> str:
    #     """Printed string representation of Node"""
    #     return self.__repr__()f"Node(idx={self.idx}, {pic})"

    def __len__(self) -> int:
        """Return length of Node as number of descendant leaf Nodes"""
        return sum(1 for i in self.iter_leaves())

    @total_ordering  # auto-creates all other ordering operations
    def __gt__(self, other: Node) -> bool:
        """Return True if this Node's idx is greater than the others."""
        if self._idx > other._idx:
            return True
        return False

    def __hash__(self) -> int:
        """Return a hash of the Node based on its repr."""
        return hash(repr(self))

    #####################################################
    # NODE CONNECTIONS
    # after modifying connections among Nodes in a ToyTree the
    # ToyTree._update() function must be called. See the
    # ToyTree.mod subpackage for alternative tree modification funcs.
    # These funcs are primarily for internal/developer use.
    #####################################################

    def _add_child(self, node: Node) -> None:
        """Connect a Node by adding it as a child to this one.

        See the ToyTree.mod subpackage for alternative user-facing
        functions for adding Nodes to a tree.

        Note
        ----
        If you use this private function to add connections among Nodes
        be aware that you are modifying the tree, and thus need to
        follow `Node/Tree updating rules in toytree <toytree.rtfd.io>`_.
        """
        node._up = self
        self._children += (node,)

    def _remove_child(self, node: Node) -> None:
        """Remove a connection from this Node to a child Node."""
        # should we add assertion that children do not have self as .up?
        self._children = tuple(i for i in self._children if i != node)

    def _delete(self, preserve_dists: bool = True, prevent_unary: bool = False) -> None:
        r"""Delete a Node from a tree.

        This removes a Node object and its connections to other Nodes.
        The `.up` and `.children` attributes of any connected Nodes are
        modified.

                    4                         4
                   / \       delete 3        /|\
                  3   \      ------->       / | \
                 / \   \                   /  |  \
                0   1   2                 0   1   2

        Parameters
        ----------
        preserve_dists: bool
            If True then children inherit the dist values of their
            deleted parents so that their dist value reaches their
            grandparents original height. If False, children retain
            their original dist but are connected to their grandparent.
        prevent_unary: bool
            If True then any unary Nodes (internal nodes with a single
            child) that are left behind from the deletion process will
            be removed as well. For example, if Node 1 is deleted in
            the example above then Node 3 would also be deleted to
            connect Node 0 to Node 4.

        See Also
        --------
        `toytree.mod.remove_node`, `toytree.mod.remove_unary_nodes`

        Example
        --------
        >>> tree = toytree.tree("((a,b),c);")
        >>> node = tree.get_mrca_node('a', 'b')
        >>> node._delete()
        >>> tree._update()  # required b/c Nodes changed
        >>> tree.draw()
        """
        # get parent node
        grandparent = self.up
        if not grandparent:
            logger.warning("cannot delete root Node.")
            return

        # each child inherits deleted Node's dist
        if preserve_dists:
            for child in self._children:
                child._dist += self._dist

        # connect children to grandparent and rm reference to self
        for child in self._children:
            grandparent._add_child(child)
        grandparent._remove_child(self)

        # do not allow parents with only one child
        if prevent_unary and len(grandparent.children) < 2:
            grandparent._delete(preserve_dists, prevent_unary)

        # Node cannot be deleted here, but all connections are severed.
        self._idx = -1
        self._up = None
        self._children = ()


    def _detach(self) -> Node:
        r"""Return this Node as a subtree detached from its ancestor.

        This Node and its descendants are detached from their ancestor
        Nodes. In other words, this removes the parent from this Node's
        `up` and removes this Node from its parent's `children`. This
        does not create a copy of any Nodes (see Node.copy()), thus
        other Nodes connected to this one are also affected. In the
        example below .detach() is called on Node 3 and Node 3 is
        returned as a subtree of the original tree structure, but note
        that Node 4 was also modified.

                    4                                   4
                   / \       detach 3       |           |
                  /   3      ------->       3           |
                 /   / \                   / \          |
                0   1   2                 1   2         0
                                        [Returned]  [Modified]

        Note
        ----
        The Node will preserve its .dist (edge length) attribute, and
        can be connected to another Node using the `Node._add_child`
        method. The detach method is primarily used internally.

        See Also
        --------
        `Node.copy`, `toytree.mod.extract_subtree`

        Example
        -------
        >>> tree = toytree.tree("((1,2)3,0)4;")
        >>> # get (1,2) detached as subtree
        >>> node = tree.get_mrca_node('1', '2')
        >>> subtree_node = node._detach()
        """
        if self._up:
            self._up._children = self.get_sisters()
            self._up = None
        return self

    #################################################
    # TRAVERSAL                                    ##
    #################################################

    def traverse(self, strategy: str = "levelorder") -> Iterator[Node]:
        """Visit all connected Nodes using a tree traversal strategy.

        Notes
        -----
        preorder:
            Parents are visited before children. Traverses all the way
            down each left subtree before proceeding to right child.
        postorder:
            Children are visited before parents. The left subtree is
            visited, then right, then the parent.
        levelorder:
            Nodes the same distance from root are visited left to
            right, before descending to next level.
        idxorder:
            Leaf nodes are visited left to right, followed by internal
            nodes in postorder traversal order.
        inorder:
            Nodes are visited in non-descreasing order if they are
            a binary search tree: left child, parent, right child.

        Parameters
        ----------
        strategy: str
            A traversal strategy for the order in which nodes will
            be visited: 'preorder', 'postorder', 'levelorder',
            'inorder', or 'idxorder'.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10)
        >>> for order, node in enumerate(tree.treenode.traverse("postorder")):
        >>>     node.name = str(order)
        >>> tree.draw(node_labels="name", node_sizes=18);
        """
        if strategy == "preorder":
            return self._traverse_preorder()
        if strategy == "levelorder":
            return self._traverse_levelorder()
        if strategy == "postorder":
            return self._traverse_postorder()
        if strategy == "inorder":
            return self._traverse_inorder()
        if strategy == "idxorder":
            return self._traverse_idxorder()
        raise TreeNodeError(
            "supported strategies are ['idxorder', 'preorder', "
            "'postorder', 'levelorder', and 'inorder']"
        )

    def _traverse_idxorder(self) -> Iterator[Node]:
        """Iterates over all nodes in 'idx' order.

        This is a non-standard tree traversal algorithm that is used
        for working with phylogenetic trees, where the leaf nodes
        are typically of special interest as the extant samples, and
        thus numbering them sequentially (0-ntips) is convenient. All
        internal nodes are labeled by post-order from (ntips-nnodes).
        The order is topologically sorted.

        See Also
        ---------
        ToyTree._update
            A similar idxorder traversal is performed by ToyTree class
            objects in the private update function, which is called
            everytime a tree is init or topology changed to update the
            Node idx labels and cache the idxorder. This func also
            sets Node height and spacing during traversal.
        """
        queue = [self]
        inner_stack = []
        outer_stack = []
        while queue:

            # get node from end of the queue
            node = queue.pop()

            # if node is leaf insert to output stack ntips from right
            if node.is_leaf():
                outer_stack.append(node)

            # if not leaf then insert to output stack...
            else:
                inner_stack.append(node)

            # add node's children to the queue
            queue.extend(node.children)

        # return nodes in reverse order they were added to stack
        while outer_stack:
            yield outer_stack.pop()
        while inner_stack:
            yield inner_stack.pop()

    def _traverse_postorder(self) -> Iterator[Node]:
        """Iterate over all descendant nodes in tip-to-root order.

        This visits all children before parents by visiting nodes...
        """
        queue = [self]
        stack = []
        while queue:

            # push node from queue onto the output stack
            node = queue.pop()
            stack.append(node)

            # push node's children to the queue
            queue.extend(node.children)

        # return nodes in reverse order they were added to stack
        while stack:
            yield stack.pop()

    def _traverse_preorder(self) -> Iterator[Node]:
        """Iterate over all nodes by 'preorder' traversal.

        This visits parents before children, by visiting all the way
        down the left and then right descendants of each node.
        """
        queue = [self]
        while queue:
            # select node from right end of queue
            node = queue.pop()
            yield node

            # add node's children to queue in [right, left] order.
            queue.extend(node.children[::-1])

    def _traverse_levelorder(self) -> Iterator[Node]:
        """Iterate over all descendant nodes in levelorder.

        This is also called breadth-first search (BFS). It starts at
        the root and visits all nodes that are the same distance from
        the root (number of nodes away) before visiting the next level
        of nodes.
        """
        queue = deque([self])
        while queue:
            node = queue.popleft()
            yield node
            queue.extend(node.children)

    def _traverse_inorder(self) -> Iterator[Node]:
        """Iterate over all nodes by 'inorder' traversal.

        This algorithm traverse up each left subtree before each right
        subtree, and is intended for use on binary-search-trees. It
        may not give intended results when trees are non-binary.
        """
        queue = []
        node = self

        # if both the queue and current node are empty traversal is done
        while queue or node:

            # if current node exists then store it until later
            # and select its left child
            if node:
                queue.append(node)
                try:
                    node = node.children[0]
                except IndexError:
                    node = None

            # if it is empty then grab node from queue and select its
            # right child.
            else:
                node = queue.pop()
                yield node
                try:
                    node = node.children[1]
                except IndexError:
                    node = None

    #################################################
    # LEAF AND LEAF NAME RETRIEVAL                 ##
    # Defaults to returning in 'idxorder'          ##
    #################################################

    def iter_leaves(self) -> Iterator[Node]:
        """Return a Generator of leaves descended from this node in
        idxorder."""
        for node in self.traverse(strategy="idxorder"):
            if not node.children:
                yield node

    def get_leaves(self) -> List[Node]:
        """Return a list of leaf nodes descended from this node in
        idxorder."""
        return list(self.iter_leaves())

    def iter_leaf_names(self) -> Iterator[str]:
        """Return a Generator of names of Nodes descended from this
        node in idxorder."""
        for node in self.iter_leaves():
            yield node.name

    def get_leaf_names(self) -> List[str]:
        """Return a list of names of Nodes descended from this node
        in idxorder."""
        return list(self.iter_leaf_names())

    #################################################
    # NODE RELATIVE RETRIEVAL / TRAVERSAL
    #################################################

    def iter_sisters(self) -> Iterator[Node]:
        """Return a Generator to iterate over sister nodes."""
        if self._up:
            for child in self._up._children:
                if child != self:
                    yield child

    def get_sisters(self) -> Tuple[Node]:
        """Return list of other Nodes that are children of same parent."""
        return tuple(self.iter_sisters())

    def iter_descendants(self, strategy: str = "levelorder") -> Iterator[Node]:
        """A generator of descendant Nodes (including self)."""
        for node in self.traverse(strategy=strategy):
            yield node

    def get_descendants(self, strategy: str = "levelorder") -> Tuple[Node]:
        """Return a list of descendant Nodes (including self)."""
        return tuple(self.iter_descendants(strategy=strategy))

    def iter_ancestors(self, root: Optional[Node] = None, include_self: bool = False) -> Iterator[Node]:
        """Return a Generator of Nodes on path from this node to root.

        Parameters
        ----------
        root: Node or None
            Iteration will stop when <root> is reached, without yielding
            <root>. Default is None, which occurs above the tree root
            Node. You can optionally enter a Node to serve as the root/
            endpoint of iteration.
        include_self: bool
            If True then this Node will be returned as its own first
            ancestor, else its parent (.up) will be the first ancestor.

        Note
        ----
        'include_self' arg overrides 'root' and will return this Node
        if it is both self and root.
        """
        node = self

        # optionally yield self
        if include_self:
            yield self

        # end iteration if self == root
        if self == root:
            return

        # continue up tree yielding nodes until root or None is reached.
        node = node._up
        while 1:
            if node in (root, None):
                break
            yield node
            node = node._up

    def get_ancestors(self, root: Optional[Node] = None, include_self: bool = False) -> Tuple[Node]:
        """Return a tuple of Nodes on path from this node to root.

        Parameters
        ----------
        root: Node or None
            Iteration will stop when <root> is reached, without yielding
            <root>. Default is None, which occurs above the tree root
            Node. You can optionally enter a Node to serve as the root/
            endpoint of iteration.
        include_self: bool
            If True then this Node will be returned as its own first
            ancestor, else its parent (.up) will be the first ancestor.

        Note
        ----
        'include_self' arg overrides 'root' and will return this Node
        if it is both self and root.
        """
        return tuple(self.iter_ancestors(root=root, include_self=include_self))

    def get_treenode(self) -> Node:
        """Return the treenode (top Node) from a connected set of Nodes.

        This calls .up recursively until the top Node is reached and
        returned.

        Note
        ----
        It is much faster to fetch the treenode from a ToyTree object
        using its cached info at ToyTree.treenode.

        Examples
        --------
        >>> tree = toytree.tree("((a,b),c);")
        >>> t0 = tree[-1]
        >>> t1 = tree.treenode
        >>> t2 = tree[0].get_treenode()
        >>> assert t0 == t1 == t2
        """
        node = self
        while 1:
            if node.up:
                node = node.up
            else:
                return node


    #####################################################
    # TO TOYTREE                                        #
    # return a ToyTree with this Node as root treenode. #
    #####################################################
    # def to_toytree(self):
    #     """Return this Node as root treenode of a ToyTree class object."""
    #     return ToyTree(self.copy())

    # def _update_heights(self) -> None:
    #     """Sets the Node .height attribute by checking all other Nodes.

    #     This is intended for internal use only. It must be called to
    #     update Node heights if a tree topology or branch lengths have
    #     been modified. This will update *all* connected Node height
    #     values in-place.

    #     Note
    #     ----
    #     Height attributes are always updated when Nodes are modified
    #     by using built-in functions from ToyTree objects, such as in
    #     `toytree.mod`. This is why Node objects are purposefuly made
    #     to be immutable, to prevent users from changing the tree
    #     structure without properly updating connected Nodes, which
    #     could make height attributes incorrect.
    #     """
    #     # get the root node
    #     root = self
    #     while 1:
    #         if root.up:
    #             root = root.up
    #         else:
    #             break

    #     # get distance from each node to the root
    #     max_dist = 0.
    #     for node in root.traverse("preorder"):
    #         if node.up:
    #             node._height = node.dist + node.up._height
    #         else:
    #             node._height = 0
    #         if node.is_leaf():
    #             max_dist = max(max_dist, node._height)

    #     # set height as distance above Node farthest from the root.
    #     for node in root.traverse("preorder"):
    #         node._height = max_dist - node._height

    def _get_ascii(self, char1="-", compact=False):
        """Return the ASCII representation of a tree.

        Code based on the PyCogent GPL project.
        """
        if self.is_leaf():
            return ([char1 + "-" + self.name], 0)

        # internal nodes require spacing concerns
        space = max(3, len(self.name) if not self.children else 3)
        padding = " " * space
        pad = " " * (space - 1)
        mids = []
        result = []
        for child in self.children:
            if len(self.children) == 1:
                char2 = "/"
            elif child is self.children[0]:
                char2 = "/"
            elif child is self.children[-1]:
                char2 = "\\"
            else:
                char2 = "-"

            # recursion
            (clines, mid) = child._get_ascii(char2, compact=compact)
            mids.append(mid + len(result))
            result.extend(clines)
            if not compact:
                result.append("")
        if not compact:
            result.pop()
        (lo, hi, end) = (mids[0], mids[-1], len(result))

        prefixes = (
            [padding] * (lo + 1) + [pad + "|"] * (hi - lo - 1) + [padding] * (end - hi)
        )
        mid = int((lo + hi) / 2)
        prefixes[mid] = char1 + "-" * (space - 2) + prefixes[mid][-1]
        result = [x + y for (x, y) in zip(prefixes, result)]
        return (result, mid)

    def draw_ascii(self, compact: bool = False):
        """Return the ASCII drawing of a Node and its descendants.

        Code based on the PyCogent GPL project.
        """
        lines, _ = self._get_ascii(compact=compact)
        tree_lines = "\n".join(lines)
        print(f"\n{tree_lines}")


if __name__ == "__main__":

    nodes = {i: Node(name=i) for i in range(20)}
    for idx, n in enumerate(nodes):
        nodes[n]._idx = idx

    nodes[1]._add_child(nodes[2])
    nodes[1]._add_child(nodes[3])
    nodes[2]._add_child(nodes[4])
    nodes[3]._add_child(nodes[5])
    nodes[3]._add_child(nodes[6])
    nodes[5]._add_child(nodes[7])
    nodes[5]._add_child(nodes[8])

    for n in nodes[1]._traverse_levelorder():
        print(n.name)

    print("postorder")
    for n in nodes[1]._traverse_postorder():
        print(n.name)

    print("inorder")
    for n in nodes[1]._traverse_inorder():
        print(n.name)

    print("preorder")
    for n in nodes[1]._traverse_preorder():
        print(n.name)

    print("idxorder")
    for n in nodes[1]._traverse_idxorder():
        print(n.name)

    # print(nodes[3].copy())
    # print(nodes[3].__dict__.keys())

    import toytree

    tree = toytree.rtree.rtree(10)
    tree[3].hello = "3"
    print(tree.features)
    print(tree.get_node_data("support"))
    # print(tree.get_node_data('hello'))

    tree.treenode.draw_ascii(compact=False)

    # x = tree.copy()
    # print(x[0] <= x[1])
