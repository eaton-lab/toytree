"""Fixed-seed distributional checks for tree simulators."""

from __future__ import annotations

import numpy as np

import toytree
from toytree.rtree._src.birth_death_conditioned import _conditional_time_cdf


def _is_balanced_four_tip_tree(tree: toytree.ToyTree) -> bool:
    """Return whether both root clades contain two leaves."""
    return sorted(len(child.get_leaves()) for child in tree.treenode.children) == [
        2,
        2,
    ]


def test_yule_and_pda_four_tip_shape_probabilities() -> None:
    """Observed shape frequencies match exact small-tree probabilities."""
    nreps = 12_000
    yule_rng = np.random.default_rng(20260911)
    pda_rng = np.random.default_rng(20260912)
    yule_balanced = sum(
        _is_balanced_four_tip_tree(
            toytree.rtree.random_topology(4, model="yule", seed=yule_rng)
        )
        for _ in range(nreps)
    )
    pda_balanced = sum(
        _is_balanced_four_tip_tree(
            toytree.rtree.random_topology(4, model="pda", seed=pda_rng)
        )
        for _ in range(nreps)
    )
    # Yule has balanced probability 1/3. Under PDA, 3 of the 15 rooted
    # labelled four-tip cladograms are balanced, giving probability 1/5.
    assert abs(yule_balanced / nreps - 1 / 3) < 0.015
    assert abs(pda_balanced / nreps - 1 / 5) < 0.015


def test_conditioned_origin_node_times_follow_analytic_cdf() -> None:
    """Inverse-CDF draws satisfy a predeclared DKW empirical-CDF bound."""
    nreps = 5_000
    birth_rate = 1.0
    death_rate = 0.3
    origin_age = 4.0
    rng = np.random.default_rng(20260913)
    crown_ages = np.asarray(
        [
            toytree.rtree.birth_death_conditioned_tree(
                2,
                birth_rate=birth_rate,
                death_rate=death_rate,
                origin_age=origin_age,
                seed=rng,
            ).treenode.height
            for _ in range(nreps)
        ]
    )
    ordered = np.sort(crown_ages)
    expected = _conditional_time_cdf(ordered, origin_age, birth_rate, death_rate)
    empirical_upper = np.arange(1, nreps + 1) / nreps
    empirical_lower = np.arange(0, nreps) / nreps
    ks_distance = max(
        float(np.max(empirical_upper - expected)),
        float(np.max(expected - empirical_lower)),
    )
    # DKW bound with alpha=1e-6: P(D_n > epsilon) <= alpha.
    dkw_bound = np.sqrt(np.log(2e6) / (2 * nreps))
    assert ks_distance < dkw_bound


def test_conditioned_pure_birth_origin_age_has_expected_mean() -> None:
    """Two-tip pure-birth crown ages recover an independent analytic mean."""
    nreps = 5_000
    birth_rate = 0.7
    origin_age = 3.0
    rng = np.random.default_rng(20260918)
    crown_ages = np.asarray(
        [
            toytree.rtree.birth_death_conditioned_tree(
                2,
                birth_rate=birth_rate,
                death_rate=0.0,
                origin_age=origin_age,
                seed=rng,
            ).treenode.height
            for _ in range(nreps)
        ]
    )
    expected_mean = 1.0 / birth_rate - origin_age / np.expm1(birth_rate * origin_age)
    assert abs(crown_ages.mean() / expected_mean - 1.0) < 0.03


def test_coalescent_first_interval_and_tmrca_expectations() -> None:
    """Sample means agree with finite-n Kingman expectations."""
    nreps = 4_000
    nsample = 8
    Ne = 100.0
    ploidy = 2.0
    rng = np.random.default_rng(20260914)
    first_intervals = np.empty(nreps)
    tmrcas = np.empty(nreps)
    for idx in range(nreps):
        tree = toytree.rtree.coalescent_tree(nsample, Ne=Ne, ploidy=ploidy, seed=rng)
        internal_heights = np.sort([node.height for node in tree[tree.ntips :]])
        first_intervals[idx] = internal_heights[0]
        tmrcas[idx] = tree.treenode.height
    expected_first = 2 * ploidy * Ne / (nsample * (nsample - 1))
    expected_tmrca = 2 * ploidy * Ne * (1 - 1 / nsample)
    assert abs(first_intervals.mean() / expected_first - 1) < 0.04
    assert abs(tmrcas.mean() / expected_tmrca - 1) < 0.04


def test_forward_process_event_type_frequency() -> None:
    """Aggregated event types recover birth/(birth+death)."""
    rng = np.random.default_rng(20260915)
    births = 0
    deaths = 0
    for _ in range(3_000):
        result = toytree.rtree.birth_death_process(
            birth_rate=3.0,
            death_rate=2.0,
            stop_time=0.5,
            start="crown",
            condition_on_survival=False,
            seed=rng,
        )
        births += result.births
        deaths += result.deaths
    assert births + deaths > 2_000
    assert abs(births / (births + deaths) - 0.6) < 0.025


def test_uncorrelated_lognormal_rate_moments() -> None:
    """A large tree recovers the requested UCLN arithmetic mean and log-SD."""
    tree = toytree.rtree.random_topology(4_000, seed=1)
    result = toytree.rtree.simulate_branch_rates(
        tree,
        "uncorrelated_lognormal",
        mean_rate=2.0,
        sigma=0.5,
        seed=20260916,
    )
    rates = np.asarray([node.rate for node in result[:-1]])
    assert abs(rates.mean() / 2.0 - 1) < 0.025
    assert abs(np.std(np.log(rates), ddof=1) - 0.5) < 0.02
    assert abs(np.corrcoef(rates[:-1], rates[1:])[0, 1]) < 0.04


def test_autocorrelated_diffusion_standardized_increments() -> None:
    """ACLN endpoint increments have the requested time-scaled distribution."""
    tree = toytree.rtree.unittree(4_000, treeheight=10.0, seed=2)
    sigma = 0.35
    result = toytree.rtree.simulate_branch_rates(
        tree,
        "autocorrelated_lognormal",
        mean_rate=1.0,
        sigma=sigma,
        seed=20260917,
    )
    standardized = []
    for node in result[:-1]:
        if node.time == 0:
            continue
        increment = np.log(node.end_rate) - np.log(node.start_rate)
        standardized.append(
            (increment + 0.5 * sigma**2 * node.time) / (sigma * np.sqrt(node.time))
        )
    standardized = np.asarray(standardized)
    assert abs(standardized.mean()) < 0.04
    assert abs(standardized.std(ddof=1) - 1) < 0.04
