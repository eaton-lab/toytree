"""Kingman coalescent tree simulation."""

from __future__ import annotations

from collections.abc import Iterable

from toytree.core.node import Node
from toytree.core.tree import ToyTree

from ._utils import (
    RNGSeed,
    assign_tip_names,
    get_rng,
    normalize_names,
    validate_bool,
    validate_int,
    validate_real,
)

__all__ = ["coalescent_tree"]


def coalescent_tree(
    nsample: int,
    Ne: float = 100.0,
    ploidy: float = 2.0,
    names: Iterable[object] | None = None,
    randomize_labels: bool = True,
    seed: RNGSeed = None,
) -> ToyTree:
    """Return a contemporaneous Kingman n-coalescent genealogy.

    Parameters
    ----------
    nsample : int
        Number of sampled gene copies at the present. It must be an integer
        greater than or equal to two.
    Ne : float, default=100.0
        Constant effective population size. Values must be finite and
        strictly positive. This parameter scales branch durations but does not
        otherwise change the constant-size coalescent topology distribution.
    ploidy : float, default=2.0
        Number of gene copies per individual used to scale coalescent time.
        The default describes a diploid autosomal locus; use 1 for a haploid
        locus. Positive noninteger values are accepted as scaling factors.
    names : Iterable[object] or None, optional
        Unique labels for exactly ``nsample`` sampled copies. If omitted,
        labels are generated as ``r0``, ``r1``, and so on.
    randomize_labels : bool, default=True
        Randomly permute labels over sampled copies. The default makes labels
        exchangeable under the coalescent.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source. A supplied Generator is consumed in place.

    Returns
    -------
    ToyTree
        A rooted, binary, ultrametric genealogy whose branch lengths are in
        generations when ``Ne`` is expressed as individuals and ``ploidy``
        converts individuals to gene copies.

    Raises
    ------
    ToytreeError
        If ``nsample``, ``Ne``, ``ploidy``, or ``seed`` is invalid.
    ValueError
        If labels are duplicated or their count differs from ``nsample``.

    Examples
    --------
    >>> tree = toytree.rtree.coalescent_tree(
    ...     nsample=20, Ne=10_000, ploidy=2, seed=123
    ... )

    Notes
    -----
    With ``k`` active lineages, the coalescence rate is
    ``choose(k, 2) / (ploidy * Ne)`` and the mean interval is
    ``2 * ploidy * Ne / (k * (k - 1))``. Consequently,
    ``E[TMRCA] = 2 * ploidy * Ne * (1 - 1 / nsample)``; it approaches
    ``4 * Ne`` for a large diploid sample rather than equalling it at finite
    sample size.
    """
    nsample = validate_int(nsample, "nsample", 2)
    Ne = validate_real(Ne, "Ne", minimum=0, strict_minimum=True)
    ploidy = validate_real(ploidy, "ploidy", minimum=0, strict_minimum=True)
    randomize_labels = validate_bool(randomize_labels, "randomize_labels")
    labels = normalize_names(names, nsample, size_name="nsample")
    rng = get_rng(seed)
    active = [Node() for _ in range(nsample)]
    lineage_ages = {id(node): 0.0 for node in active}
    elapsed = 0.0

    for nlineages in range(nsample, 1, -1):
        mean_wait = (2.0 * ploidy * Ne) / (nlineages * (nlineages - 1))
        elapsed += float(rng.exponential(mean_wait))

        first_idx = int(rng.integers(len(active)))
        first = active[first_idx]
        active[first_idx] = active[-1]
        active.pop()
        second_idx = int(rng.integers(len(active)))
        second = active[second_idx]
        active[second_idx] = active[-1]
        active.pop()
        first._dist = elapsed - lineage_ages.pop(id(first))
        second._dist = elapsed - lineage_ages.pop(id(second))
        parent = Node()
        parent._add_child(first)
        parent._add_child(second)
        lineage_ages[id(parent)] = elapsed
        active.append(parent)

    tree = ToyTree(active[0])
    assign_tip_names(tree, labels, randomize_labels, rng)
    return tree
