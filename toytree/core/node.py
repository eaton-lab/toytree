#!/usr/bin/env python

"""
New simplified Node instance, in testing...
"""

# pylint: disable=no-name-in-module, disable=invalid-name
from __future__ import annotations
from collections import deque
from typing import List, Optional, Union
from dataclasses import dataclass, field


@dataclass
class Node:
    """Node class representing a single vertex in a ToyTree.

    """
    idx: int = 0
    """: node index label (idx), unique integer assigned to every node."""
    x: float = 0.
    """: node x-coordinate position on a down-facing tree."""
    y: float = 0.
    """: node y-coordinate position on a down-facing tree."""
    name: str=""
    """: name string assigned to Node."""
    children: List[Node] = field(default_factory=list)
    """: list of Node instances directly descended from this Node."""
    up: Optional[Node] = None
    """: the ancestor Node instance (towards root) from this Node."""
    dist: float = 1.
    """: edge length associated to the edge above this Node."""
    support: float = 0.
    """: support value associated to the edge above this Node."""

    @property
    def height(self):
        """distance from this Node to the farthest tip of the ToyTree.

        Note
        ----
        This attribute is a synonym for `.y`, both of which are 
        calculated at the ToyTree level, not the Node level. ToyTree
        functions re-calculate node heights whenever any Node in the 
        tree is modified, whereas modifications to Node's directly 
        do not do this. Thus, users should generally not edit Node
        attributes directly unless you know what you're doing.
        """
        return self.y

    def __repr__(self):
        return f"<Node idx={self.idx} name={self.name}>"

    def __str__(self):
        return f"<Node idx={self.idx} name={self.name}>"

    def __len__(self):
        return sum(1 for i in self.iter_leaves())

    def iter_leaves(self):
        """ Returns an iterator over the leaves under this node."""
        for node in self.traverse(strategy="preorder"):
            if not node.children:
                yield node

    def get_leaves(self):
        """ Returns the list of terminal nodes (leaves) under this node."""
        return list(self.iter_leaves())

    def iter_leaf_names(self):
        """Returns an iterator over the leaf names under this node."""
        for node in self.iter_leaves():
            yield node.name

    def get_leaf_names(self):
        """ Returns the list of terminal node names under the current node."""
        return list(self.iter_leaf_names())

    def traverse(self, strategy: str="levelorder"):
        """Visit all connected nodes using a traversal strategy.


        """
        if strategy == "preorder":
            return self._iter_descendants_preorder()
        if strategy == "levelorder":
            return self._iter_descendants_levelorder()
        if strategy == "postorder":
            return self._iter_descendants_postorder()
        if strategy == "idxorder":
            return self._iter_descendants_idxorder()
        raise TreeNodeError(
            "strategy must be idxorder, preorder, postorder or levelorder")       


    def _iter_descendants_idxorder(self):
        """TODO"""

    def _iter_descendants_postorder(self):
        """Iterate over all descendant nodes in postorder."""
        to_visit = [self]
        while to_visit:
            node = to_visit.pop(-1)
            try:
                node = node[1]
            except TypeError:
                if not node.children:
                    to_visit.extend(reversed(node.children + [[1, node]]))
                else:
                    yield node
            else:
                yield node

    def _iter_descendants_levelorder(self):
        """Iterate over all desdecendant nodes in levelorder."""
        to_visit = deque([self])
        while len(to_visit) > 0:
            node = to_visit.popleft()
            yield node
            to_visit.extend(node.children)

    def _iter_descendants_preorder(self):
        """Iterate over all descendants in pre-order traversal"""
        to_visit = deque()
        node = self
        while node is not None:
            yield node
            to_visit.extendleft(reversed(node.children))
            try:
                node = to_visit.popleft()
            except IndexError:
                node = None


if __name__ == '__main__':

    node0 = Node(idx=0, y=10, name='z')
    node1 = Node(idx=1, name='x')
    node2 = Node(idx=2, name='y')

    node0.children = [node2, node1]
    node1.up = node0
    node2.up = node0

    for n in node0.traverse('preorder'):
        print(n.idx, n.height)
