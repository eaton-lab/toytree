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
import importlib

ToyTree = TypeVar("ToyTree")
# Cartesian = TypeVar("Cartesian")


class SubPackageAPI:
    """API to acess methods from `toytree.mod` as `tree.mod.{function}`"""
    def __init__(self, tree: ToyTree):
        self._tree = tree
        self._module_name = getattr(self, "_module_name", None)

    def __getattr__(self, name):
        if self._module_name:
            importlib.import_module(self._module_name)
            attr = getattr(self.__class__, name, None)
            if attr is not None:
                return attr.__get__(self, self.__class__)
        raise AttributeError(f"{self.__class__.__name__!s} has no attribute {name!r}")

    def __dir__(self):
        if self._module_name:
            module = importlib.import_module(self._module_name)
            module_names = getattr(module, "__all__", None)
            if module_names is None:
                module_names = [name for name in dir(module) if not name.startswith("_")]
        else:
            module_names = []
        return sorted(
            set(dir(self.__class__))
            | set(self.__dict__.keys())
            | set(module_names)
        )


class TreeModAPI(SubPackageAPI):
    """API to acess methods from `toytree.mod` as `tree.mod.{function}`"""
    _module_name = "toytree.mod"


class TreeDistanceAPI(SubPackageAPI):
    """API to acess methods from `toytree.distance` as `tree.distance.{function}`"""
    _module_name = "toytree.distance"


class TreeEnumAPI(SubPackageAPI):
    """API to acess methods from `toytree.pcm` as `tree.enum.{function}`"""
    _module_name = "toytree.enum"


class PhyloCompAPI(SubPackageAPI):
    """API to acess methods from `toytree.pcm` as `tree.pcm.{function}`"""
    _module_name = "toytree.pcm"


class AnnotationAPI(SubPackageAPI):
    """API to acess methods from `toytree.annotate` as `tree.annotate.{function}`"""
    _module_name = "toytree.annotate"


def add_subpackage_method(cls):
    """Clever approach to copy docstring and signature from func to API.

    Add this decorator to a function to make it accessible from an API

    Example
    -------
    >>> @add_subpackage_method(TreeModAPI)
    >>> def method(...):
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

    Add this decorator to a function to make it accessible from ToyTree

    Example
    -------
    >>> @add_toytree_method(ToyTree)
    >>> def method(...):
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
