#!/usr/bin/env python

"""ape::chronos-compatible non-correlated relaxed-rate model."""

from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    _relaxed_penalty as _relaxed_penalty,
)
from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    edges_make_ultrametric_relaxed,
)

__all__ = ["edges_make_ultrametric_relaxed"]
