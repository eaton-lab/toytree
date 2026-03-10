#!/usr/bin/env python

"""Simulation subpackage for phylogenetic comparative methods."""

from __future__ import annotations

import importlib

_MODULE_EXPORTS = {
    "toytree.pcm.src.sim.sim_continuous": [
        "simulate_continuous_trait",
    ],
    "toytree.pcm.src.sim.sim_continuous_mvn": [
        "simulate_multivariate_continuous_trait",
    ],
    "toytree.pcm.src.sim.sim_discrete": [
        "get_markov_model",
        "simulate_discrete_trait",
    ],
    "toytree.pcm.src.sim.sim_pglm": [
        "simulate_pglm_trait",
    ],
    "toytree.pcm.src.sim.sim_pgls": [
        "simulate_pgls_trait",
    ],
    "toytree.pcm.src.sim.sim_stochastic_mapping": [
        "simulate_stochastic_map",
    ],
}

_LAZY_ATTRS = {
    name: (module_name, name)
    for module_name, names in _MODULE_EXPORTS.items()
    for name in names
}

__all__ = list(_LAZY_ATTRS)


def __getattr__(name: str):
    """Lazily import public simulation functions on first access."""
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
