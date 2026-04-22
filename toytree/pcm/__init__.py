#!/usr/bin/env python

"""Phylogenetic comparative methods exposed as a lazy-loaded package API.

All PCM source code lives under ``toytree.pcm.src``. Public functions are
exposed here so they can be accessed either from :mod:`toytree.pcm` or from
the ``tree.pcm`` API on :class:`toytree.ToyTree` instances.

Examples
--------
>>> tree = toytree.rtree.unittree(ntips=10, treeheight=100, seed=123)
>>> toytree.pcm.simulate_discrete_trait(tree, nstates=3, model="ER")

>>> tree = toytree.rtree.unittree(ntips=10, treeheight=100, seed=123)
>>> tree.pcm.simulate_discrete_trait(nstates=3, model="ER")
"""

from __future__ import annotations

import importlib

# Keep this mapping explicit so the package-level API remains stable while the
# implementation stays lazy. This mirrors the existing eager import order.
_MODULE_EXPORTS = {
    "toytree.pcm.src.diversification.diversification": [
        "get_tip_level_diversification",
        "get_equal_splits",
    ],
    "toytree.pcm.src.diversification.red": [
        "get_relative_evolutionary_divergence",
    ],
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
        "PCMStochasticMapResult",
        "simulate_stochastic_map",
    ],
    "toytree.pcm.src.traits.aic_table": [
        "PCMModelResult",
        "aic_table",
    ],
    "toytree.pcm.src.traits.fit_discrete_ctmc": [
        "PCMDiscreteCTMCFitResult",
        "fit_discrete_ctmc",
        "infer_ancestral_states_discrete_ctmc",
    ],
    "toytree.pcm.src.traits.fit_continuous_ml": [
        "fit_continuous_ml",
        "infer_ancestral_states_continuous_ml",
        "PCMContinuousMLModelFit",
        "PCMContinuousMLFitResult",
    ],
    "toytree.pcm.src.traits.pgls_matrix": [
        "pgls_matrix",
    ],
    "toytree.pcm.src.traits.phylosignal_k": [
        "phylogenetic_signal_k",
    ],
    "toytree.pcm.src.traits.phylosignal_lambda": [
        "phylogenetic_signal_lambda",
    ],
    "toytree.pcm.src.traits.pic": [
        "get_phylogenetic_independent_contrasts",
        "get_ancestral_states_pic",
    ],
    "toytree.pcm.src.vcv": [
        "get_vcv_matrix_from_tree",
        "get_corr_matrix_from_tree",
        "get_distance_matrix_from_vcv_matrix",
        "get_tree_from_vcv_matrix",
    ],
}

_LAZY_ATTRS = {
    name: (module_name, name)
    for module_name, names in _MODULE_EXPORTS.items()
    for name in names
}

__all__ = list(_LAZY_ATTRS)


def __getattr__(name: str):
    """Lazily import public PCM functions and result classes on first access."""
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
