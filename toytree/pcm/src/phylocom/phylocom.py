#!/usr/bin/env python

"""Phylogenetic community structure module.

This will be reorganized into a subpackage in the future, like this:
>>> tree = toytree.rtree.unittree(10)
>>> mat = phylocom.simulate_community(tree, size=100, ...)
>>> phylocom.get_community_metric(tree, mat, metric="pd", null=None)

References
----------
- https://pedrohbraga.github.io/CommunityPhylogenetics-Workshop/CommunityPhylogenetics-Workshop.html#within-assemblage-phylogenetic-structure
- https://phylodiversity.net/
- Cavender‐Bares, J. , Kozak, K. H., Fine, P. V. and Kembel, S. W.
(2009), The merging of community ecology and phylogenetic biology.
Ecology Letters, 12: 693-715. doi:10.1111/j.1461-0248.2009.01314.x

PSV and PGLMM methods
---------------------
- Ives and Helmus 2011
- Helmus M.R., Bland T.J., Williams C.K. & Ives A.R. (2007)
  Phylogenetic measures of biodiversity. American Naturalist,
  169, E68-E83
- TODO: phylogenetic entropy, Allen et al. 2009

Validation
----------
Following the methods in this paper
- https://link.springer.com/chapter/10.1007/978-3-662-43550-2_19
which cites Cadotte et al. for the approach, we can simulate
communities, compute N different statistics, and perform clustering
on the outputs to show how similar the results of different metrics
are.


For textbook:
- Faith: goal is to maximize conservation of features.
"""

from typing import TypeVar, Optional, Union
from numpy.typing import ArrayLike
import numpy as np
import pandas as pd
import toytree


ToyTree = TypeVar("ToyTree")


# TODO: simulate abundances as lognormally distributed?
def simulate_community_data(
    tree: ToyTree,
    scalar: float=0,
    size: int=1,
    seed: Optional[int]=None,
    ) -> pd.DataFrame:
    """Return a binary (nsites, nspecies) community data matrix.

    Simulate communities under phylogenetic attraction or repulsion.
    A VCV is generated from the tree; a scalar (c) is positive
    for phylogenetic attraction, or negative for repulsion. Phylo
    effects are modeled by a Cholesky decomposition of the VCV if
    scalar is positive, or of the inverse of VCV if negative. Random
    values are drawn from a normal distribution (R), and the
    prob of species occurrence is logistic with probability:

    $$ p = \frac{e^{cLR}}{(1 - e^{cLR})} $$

    A pandas.DataFrame is returned with N (size) sites where every
    site includes at least one observed species from the phylogeny.

    Parameters
    ----------
    tree: ToyTree
        A toytree with edge lengths from which a variance-covariance
        matrix will be calculated.
    scalar: float
        A constant scalar representing the strength of phylogenetic
        effects. Positive value is attraction, negative is repulsion.
    size: int
        Number of replicate communities (sites) to simulate.
    seed: int or None
        A seed for the numpy random number generator.
    """
    rng = np.random.default_rng(seed)
    vcv = toytree.pcm.get_vcv_matrix_from_tree(tree)
    vcv = np.linalg.inv(vcv) if scalar < 0 else vcv
    l_mat = np.linalg.cholesky(vcv)
    communities = []
    for _ in range(size):
        r_mat = rng.normal(size=vcv.shape[0])
        inner = np.exp(scalar * np.dot(l_mat, r_mat))
        probs = inner / (1 + inner)
        comm = rng.binomial(n=1, p=probs)
        communities.append(comm)
    return pd.DataFrame(columns=tree.get_tip_labels(), data=communities)

def get_community_metric(
    tree: ToyTree,
    matrix: ArrayLike,
    metric="pd",
    null=None,
    ) -> Union[float, np.ndarray]:
    """Return a community metric given a tree and matrix.

    Supported metrics are also available in individual functions
    with more detailed documentation in the `toytree.pcm.phylocom`
    subpackage. These include ...

    Parameters
    ----------
    tree: ToyTree
        A phylogenetic tree with the global species pool as tips.
    matrix: pd.DataFrame
        Community matrix (nsites, nspecies) composed of booleans
        or ints where 0/False indicates absence, and N/True indicates
        presence (if integer >1 it is interpreted as abundance for
        metrics that use abundance, otherwise simply as presence).
    metric: str
        A string matching the name of a supported community metric.
        See supported metrics.
    null: None or str
        A string matching the name of a supported null model. See
        supported null models.

    Examples
    --------
    >>> ...
    >>>    metric    null_mean    null_std   effect_size    name
    >>> 0    ...         ...          ...        ...        'MPD'
    """



if __name__ == "__main__":

    # fetch a test dataset ...
    TREE = toytree.rtree.unittree(10, treeheight=10, seed=123)
    MATRIX = simulate_community_data(TREE, scalar=10, size=10, seed=123)
    print(MATRIX)
