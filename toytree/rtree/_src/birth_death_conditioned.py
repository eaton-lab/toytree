"""Conditioned reconstructed constant-rate birth--death trees."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError

from ._utils import (
    RNGSeed,
    assign_tip_names,
    get_rng,
    normalize_names,
    validate_bool,
    validate_int,
    validate_real,
)

__all__ = ["birth_death_conditioned_tree"]


def _conditional_time_cdf(
    ages: np.ndarray,
    maximum_age: float,
    birth_rate: float,
    death_rate: float,
) -> np.ndarray:
    """Return the conditional reconstructed-node-time CDF."""
    ages = np.asarray(ages, dtype=float)
    delta = birth_rate - death_rate
    if np.isclose(delta, 0.0, rtol=0.0, atol=1e-12 * birth_rate):
        numerator = ages / (1.0 + birth_rate * ages)
        denominator = maximum_age / (1.0 + birth_rate * maximum_age)
        return numerator / denominator
    with np.errstate(over="ignore", invalid="ignore"):
        exp_age = np.exp(-delta * ages)
        exp_maximum = np.exp(-delta * maximum_age)
        numerator = (1.0 - exp_age) / (birth_rate - death_rate * exp_age)
        denominator = (1.0 - exp_maximum) / (birth_rate - death_rate * exp_maximum)
    return numerator / denominator


def _sample_conditional_times(
    count: int,
    maximum_age: float,
    birth_rate: float,
    death_rate: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample reconstructed branching ages by analytic inverse CDF."""
    if count == 0:
        return np.empty(0, dtype=float)
    uniform = rng.random(count)
    delta = birth_rate - death_rate
    if np.isclose(delta, 0.0, rtol=0.0, atol=1e-12 * birth_rate):
        maximum_transform = maximum_age / (1.0 + birth_rate * maximum_age)
        transformed = uniform * maximum_transform
        return transformed / (1.0 - birth_rate * transformed)
    exp_maximum = np.exp(-delta * maximum_age)
    maximum_transform = (1.0 - exp_maximum) / (birth_rate - death_rate * exp_maximum)
    transformed = uniform * maximum_transform
    ratio = (1.0 - birth_rate * transformed) / (1.0 - death_rate * transformed)
    return -np.log(ratio) / delta


def _tree_from_branching_ages(
    ntips: int,
    branching_ages: np.ndarray,
    rng: np.random.Generator,
) -> ToyTree:
    """Construct an exchangeable ranked tree from ordered coalescent ages."""
    active = [Node() for _ in range(ntips)]
    node_ages = {id(node): 0.0 for node in active}
    for age in np.sort(np.asarray(branching_ages, dtype=float)):
        first_idx = int(rng.integers(len(active)))
        first = active[first_idx]
        active[first_idx] = active[-1]
        active.pop()
        second_idx = int(rng.integers(len(active)))
        second = active[second_idx]
        active[second_idx] = active[-1]
        active.pop()
        first._dist = float(age - node_ages[id(first)])
        second._dist = float(age - node_ages[id(second)])
        parent = Node()
        parent._add_child(first)
        parent._add_child(second)
        node_ages[id(parent)] = float(age)
        active.append(parent)
    return ToyTree(active[0])


def birth_death_conditioned_tree(
    ntips: int,
    birth_rate: float = 1.0,
    death_rate: float = 0.0,
    *,
    crown_age: float | None = None,
    origin_age: float | None = None,
    names: Iterable[object] | None = None,
    randomize_labels: bool = True,
    seed: RNGSeed = None,
) -> ToyTree:
    """Sample a conditioned reconstructed birth--death tree directly.

    Parameters
    ----------
    ntips : int
        Fixed number of extant, completely sampled tips. It must be an integer
        greater than or equal to two.
    birth_rate : float, default=1.0
        Constant per-lineage speciation rate per time unit. It must be finite
        and strictly positive.
    death_rate : float, default=0.0
        Constant per-lineage extinction rate per time unit. It must be finite,
        nonnegative, and no greater than ``birth_rate``. Equality selects the
        critical branching-process limit.
    crown_age : float or None, optional
        Fixed age of the most recent common ancestor. Supply exactly one of
        ``crown_age`` and ``origin_age``. The returned root has this height.
    origin_age : float or None, optional
        Fixed age at which the process began with one lineage. The sampled
        crown is younger than this age; its difference from ``origin_age`` is
        stored as the root distance representing the unobserved stem.
    names : Iterable[object] or None, optional
        Unique labels for exactly ``ntips`` extant leaves. If omitted, labels
        are generated as ``r0``, ``r1``, and so on.
    randomize_labels : bool, default=True
        Randomly permute labels over tips. The default preserves the
        exchangeability of labels under the conditioned process.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source. A supplied Generator is consumed in place.

    Returns
    -------
    ToyTree
        A rooted, binary, ultrametric reconstructed tree. Branch lengths use
        the same time units as the supplied age and reciprocal rate units.
        Under origin conditioning, ``tree.treenode.dist`` stores stem duration.

    Raises
    ------
    ToytreeError
        If rates, ages, tip count, conditioning, or random-number source are
        invalid.
    ValueError
        If labels are duplicated or their count differs from ``ntips``.

    Examples
    --------
    >>> crown = toytree.rtree.birth_death_conditioned_tree(
    ...     20, birth_rate=1.0, death_rate=0.2, crown_age=3.0, seed=123
    ... )
    >>> stem = toytree.rtree.birth_death_conditioned_tree(
    ...     20, birth_rate=1.0, death_rate=0.2, origin_age=4.0, seed=123
    ... )

    Notes
    -----
    This function implements the conditioned reconstructed-process result of
    Gernhard (2008): conditional on origin age, all ``ntips - 1`` branching
    times are independent draws from the analytic conditional distribution;
    conditional on crown age, the crown is fixed and the remaining
    ``ntips - 2`` times are independent draws. Ranked oriented histories and
    label placements are exchangeable. Extinct lineages are integrated out.

    Complete extant sampling is assumed. No implicit prior is placed on tree
    age, and this release does not implement a sampling-fraction parameter.
    Use :func:`birth_death_process` when a complete forward event history is
    required.

    References
    ----------
    Gernhard, T. (2008). The conditioned reconstructed process. Journal of
    Theoretical Biology, 253, 769--778. doi:10.1016/j.jtbi.2008.04.005
    """
    ntips = validate_int(ntips, "ntips", 2)
    birth_rate = validate_real(birth_rate, "birth_rate", minimum=0, strict_minimum=True)
    death_rate = validate_real(death_rate, "death_rate", minimum=0)
    if death_rate > birth_rate:
        raise ToytreeError("death_rate must be <= birth_rate.")
    if (crown_age is None) == (origin_age is None):
        raise ToytreeError("supply exactly one of crown_age or origin_age.")
    randomize_labels = validate_bool(randomize_labels, "randomize_labels")
    labels = normalize_names(names, ntips)
    rng = get_rng(seed)

    if crown_age is not None:
        maximum_age = validate_real(
            crown_age, "crown_age", minimum=0, strict_minimum=True
        )
        sampled = _sample_conditional_times(
            ntips - 2, maximum_age, birth_rate, death_rate, rng
        )
        branching_ages = np.concatenate((sampled, [maximum_age]))
        stem_duration = 0.0
    else:
        maximum_age = validate_real(
            origin_age, "origin_age", minimum=0, strict_minimum=True
        )
        branching_ages = _sample_conditional_times(
            ntips - 1, maximum_age, birth_rate, death_rate, rng
        )
        stem_duration = maximum_age - float(np.max(branching_ages))

    tree = _tree_from_branching_ages(ntips, branching_ages, rng)
    tree.treenode._dist = stem_duration
    tree.treenode.origin_age = maximum_age if origin_age is not None else None
    assign_tip_names(tree, labels, randomize_labels, rng)
    return tree
