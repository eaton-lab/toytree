#!/usr/bin/env python

"""
New simplified Node instance, in testing...
"""

# pylint: disable=no-name-in-module
from __future__ import annotations
from collections import deque
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class Node(BaseModel):
    idx: int = 0
    _x: float = 0.
    _y: float = 0.

    name: Union[float,str] = Field("")
    children: List[Node] = Field(default_factory=list)
    up: Optional[Node] = None
    dist: float = 1.
    support: float = 0.

    class Config:
        validate_assignment = True
    
    @property
    def height(self):
        """
        Distance from this node to the farthest tip of the tree.
        """
        return self._y

    def __repr__(self):
        return f"<Node idx={self.idx} name={self.name}>"

    def __str__(self):
        return f"<Node idx={self.idx} name={self.name}>"

    def traverse(self, strategy:str="levelorder"):
        """
        Visit all connected nodes in a specific order (strategy).
        """
        if strategy == "preorder":
            return self._iter_descendants_preorder()
        if strategy == "levelorder":
            return self._iter_descendants_levelorder()
        if strategy == "postorder":
            return self._iter_descendants_postorder()
        raise TreeNodeError(
            "strategy must be preorder, postorder or levelorder")


    def _iter_descendants_levelorder(self):
        """ 
        Iterate over all descendant nodes.
        """
        todo = deque([self])
        while todo:
            node = todo.popleft()
            todo.extend(node.children)
            yield node

    def _iter_descendants_preorder(self):
        """ 
        Iterate over all descendant nodes
        """
        todo = deque()
        node = self
        while 1:
            todo.extendleft(reversed(node.children))
            try:
                node = todo.popleft()
                yield node
            except IndexError:
                node = self
            yield node


Node.update_forward_refs()


if __name__ == '__main__':

    node1 = Node(idx=0, y=10, name=1)
    node2 = Node(idx=1, name=2)
    node3 = Node(idx=2, name=3)

    node1.children = [node2, node3]
    node1.name = 'a'
    print(node1.height)
    for node in node1.traverse('preorder'):
        print(node)
