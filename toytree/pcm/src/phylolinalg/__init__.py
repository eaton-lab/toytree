#!/usr/bin/env python

"""Pruning-based phylogenetic linear algebra backends."""

from __future__ import annotations

import importlib

_MODULE_EXPORTS = {
    "toytree.pcm.src.phylolinalg.pglm": [
        "PCMPGLMResult",
        "PCMPGLMPruningModel",
        "pglm",
    ],
    "toytree.pcm.src.phylolinalg.pgls": [
        "PCMPGLSResult",
        "PCMPGLSPruningModel",
        "pgls",
    ],
    "toytree.pcm.src.phylolinalg.pgls_infer": [
        "infer_node_states_pgls",
    ],
}

_LAZY_ATTRS = {
    name: (module_name, name)
    for module_name, names in _MODULE_EXPORTS.items()
    for name in names
}

__all__ = list(_LAZY_ATTRS)


def __getattr__(name: str):
    """Lazily import public phylolinalg symbols on first access."""
    if name not in _LAZY_ATTRS:
        raise AttributeError(name)
    module_name, attr_name = _LAZY_ATTRS[name]
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__():
    """Return module attributes plus lazily available public names."""
    return sorted(set(globals()) | set(__all__))
