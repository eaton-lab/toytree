#!/usr/bin/env python

"""Tree API allows calling submodule functions from a tree object.

For example, the function in the `toytree.mod` submodule can be called
as `toytree.mod.prune(tree)`, or the submodule can be called from a
ToyTree object as `tree.mod.prune()`. For some very common functions,
such as `root`, the function is also made available from the ToyTree
object directly without accessing the submodule, e.g., `tree.root()`.

To simplify the code and avoid errors in making these functions
accessible from three places we use a clever wrapper in functools and
a method described at the link below. This allows us to write the
function just once and to copy its docstring, signature, etc. to
automatically set it as a method in the API.

Thus, most function's source code is in the submodule folders, e.g.,
`toytree.mod.root`, and it is added as a method to the tree-level
subpackage API, e.g., `tree.mod` or to the ToyTree object itself, e.g.,
`tree.root` using the wrapper in this module.

References
----------
https://mgarod.medium.com/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
"""

from typing import TypeVar
from functools import wraps

ToyTree = TypeVar("ToyTree")


class TreeModAPI:
    """API to acess methods from `toytree.mod` as `tree.mod.{function}`"""
    def __init__(self, tree: ToyTree):
        self._tree = tree


class TreeDistanceAPI:
    """API to acess methods from `toytree.distance` as `tree.distance.{function}`"""
    def __init__(self, tree: ToyTree):
        self._tree = tree


class TreeEnumAPI:
    """API to acess methods from `toytree.pcm` as `tree.enum.{function}`"""
    def __init__(self, tree: ToyTree):
        self._tree = tree


class PhyloCompAPI:
    """API to acess methods from `toytree.pcm` as `tree.pcm.{function}`"""
    def __init__(self, tree: ToyTree):
        self._tree = tree


def add_subpackage_method(cls):
    """Clever approach to copy docstring and signature from func to API.

    Reference
    ---------
    https://mgarod.medium.com/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
    """
    def decorator(func):

        # creates a wrapper for a toytree.mod.{function} that copies
        # its docstring and arg signatures but sets self._tree as the
        # first argument of the function.
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self._tree, *args, **kwargs)

        # sets: TreeModAPI.{function} = wrapper
        setattr(cls, func.__name__, wrapper)

        # Note we are not binding func, but wrapper which accepts self
        # but does exactly the same as func.
        # returning func means func can still be used normally
        return func
    return decorator


def add_toytree_method(cls):
    """Clever approach to copy docstring and signature from func to API.

    Reference
    ---------
    https://mgarod.medium.com/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
    """
    def decorator(func):

        # creates a wrapper for a toytree.mod.{function} that copies
        # its docstring and arg signatures but sets self._tree as the
        # first argument of the function.
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        # sets: TreeModAPI.{function} = wrapper
        setattr(cls, func.__name__, wrapper)

        # Note we are not binding func, but wrapper which accepts self
        # but does exactly the same as func.
        # returning func means func can still be used normally
        return func
    return decorator


if __name__ == "__main__":

    @add_toytree_method(ToyTree)
    @add_subpackage_method(TreeModAPI)
    def test(arg1: int, arg2: str) -> float:
        """This is a test."""
        return 32.0

    help(test)

    help(TreeModAPI.test)

    help(ToyTree.test)
