#!/usr/bin/env python

"""Outline of ideas for more phylocom metrics...

"""

from typing import TypeVar, Callable, Optional
from dataclasses import dataclass
from numpy.typing import ArrayLike
import numpy as np
import pandas as pd
import toytree


ToyTree = TypeVar("ToyTree")


@dataclass
class NullModel:
    tree: ToyTree
    """: Phylogenetic tree containing the complete species pool."""
    matrix: ArrayLike
    """: Community matrix shape=(nsites, nspecies), dtype=bool or int."""
    method: Callable
    """: A function to compute on the tree x matrix data."""
    size: int
    """: N replicate null community samples for calculating effect sizes."""
    _statistic: ArrayLike
    """: Statistic to be computed for each community."""
    _mean: float
    """: Mean statistic computed across null communities."""
    _std: float
    """: Standard deviation of statistic computed across null communities."""

    def __post_init__(self):
        """Sample null communities and return computed Z scores."""
        self._check_data()
        self._sample_from_null()
        self.get_standard_effect_size()

    def _check_data(self):
        """Verify that names match between tree and matrix.

        Names present in the matrix (DataFrame) should be present in
        the phylogeny, and vice-versa.
        """
        # TODO.

    def _sample_from_null(self):
        """Child class function will set self._mean and self._std."""
        raise NotImplementedError("No function, use a child class.")

    def get_standard_effect_size(self):
        r"""Return effect size (Z-value).
        
        $$ z = \frac{x - \mu}{\sigma} $$
        """
        return (self._statistic - self._mean) / self._std


class ShuffleTips(NullModel):
    """Shuffle tip labels on tree and recompute statistic."""
    def _sample_from_null(self):
        for rep in range(self.size):
            pass 

class Richness(NullModel):
    """Randomize community abundances while maintaining species richness"""

class Frequency(NullModel):
    """Randomize community abundances while maintaining species frequencies"""

class SamplePool(NullModel):
    """Randomize community by sampling species from pool of species 
    occurring in at least one community (sample pool) with equal 
    probability."""

class PhyloPool(NullModel):
    """Randomize community by sampling species from pool of species 
    occurring in at least one community (sample pool) with equal 
    probability.
    
    Note: this description is same as above, probably a typo.
    """

class IndependentSwap(NullModel):
    """Randomizes community data matrix with the independent swap 
    algorithm (Gotelli 2000) maintaining species occurrence frequency
    and sample species richness."""

class TrialSwap(NullModel):
    """Randomizes community data matrix with the trial-swap algorithm
    (Miklos & Podani 2004) maintaining species occurrence frequency
    and sample species richness."""



def get_faith_pd() -> float:
    """..."""


def get_mean_pairwise_distance() -> float:
    """..."""


def get_mean_nearest_neighbor_distance() -> float:
    """..."""


def get_net_relatedness_index() -> float:
    """..."""


def get_nearest_taxon_index() -> float:
    """..."""


def get_species_richness() -> float:
    """..."""


def get_phylogenetic_sorensen_index() -> float:
    """Return the Phylogenetic Sørensen Index of PhyloBetaDiversity.

    This is a phylogenetic analog of the Sørensen index based on 
    the total length of edges shared and unshared between paired
    communities.

    References
    ----------
    - Bryant et al., 2008; Swenson, 2011; Feng et.al., 2012)

    Examples
    --------
    >>> import toyplot, toytree
    >>> tree = ...
    >>> matrix = ...
    >>> sor_index = get_phylo...
    >>>
    >>> # plot a matrix of SorIndex values between pairs of comms.
    >>> ...
    """

def get_unifrac() -> float:
    """Return the Unifrac value of PhyloBetaDiversity.
    
    This measures the unique fraction of the phylogeny that is 
    unshared between a pair of communities. This metric is mostly
    sensitive to dissimilarity at the tips of a phylogeny, but not
    among splits farther back in a tree.
    """
