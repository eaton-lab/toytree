#!/usr/bin/env python

"""Shared simulated-tree builders for penalized-pseudolikelihood tests."""

import numpy as np

import toytree
from toytree.core import ToyTree


def get_tree_with_categorical_rates(ntips: int, nrates: int, seed: int) -> ToyTree:
    """Return a ToyTree with edges scaled by categorical rate variation.

    Rate categories are evenly assigned (linspace) between 1 and 10
    and each edge is randomly assigned to a category. The rate scaler
    for that edge is then sampled from a gamma distribution with
    G(3, RATE) where the alpha=3 sets mean == stderr. Example,
    nrates=2 will generate the rate distributions:
        - G(3, 1)    [mean=3, std=1.73]
        - G(3, 10)   [mean=30, std=17.25]
    """
    rng = np.random.default_rng(seed=seed)
    tree = toytree.rtree.unittree(ntips, seed=123)
    rates = np.linspace(1, 10, nrates)
    for node in tree:
        gidx = rng.choice(nrates)
        node._dist = node._dist * rng.gamma(shape=3, scale=rates[gidx])
    tree._update()
    return tree


def get_tree_with_uncorrelated_rates(
    ntips: int, mean: float = 1.0, sigma: float = 1.0, seed: int = None
) -> ToyTree:
    """Return a ToyTree with edges scaled by uncorrelated relaxed-clock rates.

    A gamma distribution is parameterized with a shape and scale to
    match the desired mean and sigma values, and each branch dist
    value is multiplied by a randomly sampled rate parameter from this
    distribution.

    Rate categories are evenly assigned (linspace) between 1 and 10
    and each edge is randomly assigned to a category. The rate scaler
    for that edge is then sampled from a gamma distribution with
    G(3, RATE).
    """
    rng = np.random.default_rng(seed=seed)
    tree = toytree.rtree.unittree(ntips, seed=123)
    shape = (mean / sigma) ** 2
    scale = sigma**2 / mean
    rates = rng.gamma(shape=shape, scale=scale, size=tree.nnodes)
    for node in tree:
        node._dist = node._dist * rates[node.idx]
    tree._update()
    return tree


def get_tree_with_correlated_rates(
    ntips: int, mean: float = 0.0, sigma: float = 1.0, seed: int = None
) -> ToyTree:
    """Return a ToyTree with edges scaled by correlated relaxed-clock rates.

    A gamma distribution is parameterized with a shape and scale to
    match the desired mean and sigma values, and each branch dist
    value is multiplied by a randomly sampled rate parameter from this
    distribution.

    Rate categories are evenly assigned (linspace) between 1 and 10
    and each edge is randomly assigned to a category. The rate scaler
    for that edge is then sampled from a gamma distribution with
    G(3, RATE).
    """
    rng = np.random.default_rng(seed=seed)
    tree = toytree.rtree.unittree(ntips, seed=123)
    shape = (mean / sigma) ** 2
    scale = sigma**2 / mean
    rates = rng.gamma(shape=shape, scale=scale, size=tree.nnodes)
    for node in tree:
        node._dist = node._dist * rates[node.idx]
    return tree
