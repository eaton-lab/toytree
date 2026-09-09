#!/usr/bin/env python

"""Non-correlated relaxed-rate model provided for ape::chronos parity."""

from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    _relaxed_penalty as _relaxed_penalty,
)
from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    edges_make_ultrametric_relaxed,
)

__all__ = ["edges_make_ultrametric_relaxed"]
