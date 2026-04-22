#!/usr/bin/env python

"""Trait evolution subpackage."""

from __future__ import annotations

import importlib

_LAZY_ATTRS = {
    "PCMModelResult": (
        "toytree.pcm.src.traits.aic_table",
        "PCMModelResult",
    ),
    "PCMDiscreteCTMCFitResult": (
        "toytree.pcm.src.traits.fit_discrete_ctmc",
        "PCMDiscreteCTMCFitResult",
    ),
    "fit_discrete_ctmc": (
        "toytree.pcm.src.traits.fit_discrete_ctmc",
        "fit_discrete_ctmc",
    ),
    "infer_ancestral_states_discrete_ctmc": (
        "toytree.pcm.src.traits.fit_discrete_ctmc",
        "infer_ancestral_states_discrete_ctmc",
    ),
    "fit_continuous_ml": (
        "toytree.pcm.src.traits.fit_continuous_ml",
        "fit_continuous_ml",
    ),
    "infer_ancestral_states_continuous_ml": (
        "toytree.pcm.src.traits.fit_continuous_ml",
        "infer_ancestral_states_continuous_ml",
    ),
    "PCMContinuousMLModelFit": (
        "toytree.pcm.src.traits.fit_continuous_ml",
        "PCMContinuousMLModelFit",
    ),
    "PCMContinuousMLFitResult": (
        "toytree.pcm.src.traits.fit_continuous_ml",
        "PCMContinuousMLFitResult",
    ),
}

__all__ = list(_LAZY_ATTRS)


def __getattr__(name: str):
    """Lazily import public trait helpers on first access."""
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
