#!/usr/bin/env python

"""A minimalist Python package for representing tree objects, performing
operations on trees, and performing tree visualization.

Toytree's primary use if for visualizing and manipulating tree data
structures. It includes a number of additional subpackages for working
with trees as data, or data on trees. All subpackages make use only of
standard Python data science libs (e.g., numpy, scipy, pandas).
"""

__version__ = "3.0.12"
__author__ = "Deren Eaton"

# toytree v3 supported subpackages (lazy-loaded for faster imports)
import importlib as _importlib


# submodules mapped to module-API available at toytree.[submodule]
_LAZY_SUBMODULES = {
    "annotate": "toytree.annotate",
    "color": "toytree.color",
    "data": "toytree.data",
    "distance": "toytree.distance",
    "enum": "toytree.enum",
    "infer": "toytree.infer",
    "rtree": "toytree.rtree",
    "io": "toytree.io",
    "mod": "toytree.mod",
    "network": "toytree.network",
    "pcm": "toytree.pcm",
}

# attrs mapped to module-API available at toytree.[attr]
_LAZY_ATTRS = {
    "Node": ("toytree.core.node", "Node"),
    "ToyTree": ("toytree.core.tree", "ToyTree"),
    "MultiTree": ("toytree.core.multitree", "MultiTree"),
    "AdmixtureEvent": ("toytree.network", "AdmixtureEvent"),
    "tree": ("toytree.io.src.treeio", "tree"),
    "mtree": ("toytree.io.src.mtreeio", "mtree"),
    "save": ("toytree.io.src.save", "save"),
    "ToytreeError": ("toytree.utils.src.exceptions", "ToytreeError"),
    "set_log_level": ("toytree.utils.src.logger_setup", "set_log_level"),
}


def __getattr__(name):
    """lazy-load module level submodule or attr on first call if not yet loaded."""
    if name in _LAZY_SUBMODULES:
        module = _importlib.import_module(_LAZY_SUBMODULES[name])
        globals()[name] = module
        return module
    if name in _LAZY_ATTRS:
        module_name, attr_name = _LAZY_ATTRS[name]
        module = _importlib.import_module(module_name)
        attr = getattr(module, attr_name)
        globals()[name] = attr
        return attr
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """set attr and submodule dir names to toytree module to be lazy-loaded on first use"""
    return sorted(
        list(globals().keys())
        + list(_LAZY_SUBMODULES.keys())
        + list(_LAZY_ATTRS.keys())
    )

# _logger.disable("toytree")


if __name__ == "__main__":

    import toytree
