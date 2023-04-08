#!/usr/bin/env python

"""

"""

from typing import TypeVar
from functools import wraps

ToyTree = TypeVar("ToyTree")


class TreeModAPI:
    """API to acess methods from `toytree.mod` as `tree.mod.{function}`"""
    def __init__(self, tree: ToyTree):
        self._tree = tree


def add_method(cls):
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


# ########################################################################
# # COPY DOCUMENTATION STRINGS TO API FUNCS FROM THE MODULE-LEVEL FUNCS
# # this code will run always on init.
# ########################################################################
# for name, module_func in inspect.getmembers(toytree.mod):
#     if inspect.isfunction(module_func):

#         @add_method(TreeModAPI)


#         # set documentation strings to match
#         api_func = getattr(TreeModAPI, name)
#         api_func.__doc__ = module_func.__doc__

#         # set default args to match
#         setattr(api_func, func.__name__, wrapper)
