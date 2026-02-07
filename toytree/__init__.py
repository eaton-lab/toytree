#!/usr/bin/env python

"""A minimalist Python package for representing tree objects, performing
operations on trees, and performing tree visualization.

Toytree's primary use if for visualizing and manipulating tree data
structures. It includes a number of additional subpackages for working
with trees as data, or data on trees. All subpackages make use only of
standard Python data science libs (e.g., numpy, scipy, pandas).
"""

__version__ = "3.0.11"
__author__ = "Deren Eaton"

# core class objects (lazy-loaded for faster imports)
# convenience functions (lazy-loaded for faster imports)

# toytree v3 supported subpackages (lazy-loaded for faster imports)
import importlib

_LAZY_SUBMODULES = {
    "rtree": "toytree.rtree",
    "distance": "toytree.distance",
    "io": "toytree.io",
    "mod": "toytree.mod",
    "color": "toytree.color",
    "enum": "toytree.enum",
    "pcm": "toytree.pcm",
    "network": "toytree.network",
    "annotate": "toytree.annotate",
    "data": "toytree.data",
}

_LAZY_ATTRS = {
    "Node": ("toytree.core.node", "Node"),
    "ToyTree": ("toytree.core.tree", "ToyTree"),
    "MultiTree": ("toytree.core.multitree", "MultiTree"),
    "tree": ("toytree.io.src.treeio", "tree"),
    "mtree": ("toytree.io.src.mtreeio", "mtree"),
    "save": ("toytree.io.src.save", "save"),
    "set_log_level": ("toytree.utils.src.logger_setup", "set_log_level"),
}


def __getattr__(name):
    if name in _LAZY_SUBMODULES:
        module = importlib.import_module(_LAZY_SUBMODULES[name])
        globals()[name] = module
        return module
    if name in _LAZY_ATTRS:
        module_name, attr_name = _LAZY_ATTRS[name]
        module = importlib.import_module(module_name)
        attr = getattr(module, attr_name)
        globals()[name] = attr
        return attr
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(
        list(globals().keys())
        + list(_LAZY_SUBMODULES.keys())
        + list(_LAZY_ATTRS.keys())
    )


# container trees... container

# turn off the logger by default; expose set_log_level for manual enable
from loguru import logger
logger.disable("toytree")


# AN IDEA TO STORE WHETHER WE ARE IN AN IDE OR NOT.
# def inside_notebook() -> bool:
#     """Return True if executed from inside jupyter, else False.

#     takes ~140 ns.
#     """
#     try:
#         shell = get_ipython().__class__.__name__
#         if shell == 'ZMQInteractiveShell':
#             return True   # Jupyter notebook or qtconsole
#         elif shell == 'TerminalInteractiveShell':
#             return False  # Terminal running IPython
#         else:
#             return False  # Other type (?)
#     except NameError:
#         return False      # Probably standard Python interpreter
