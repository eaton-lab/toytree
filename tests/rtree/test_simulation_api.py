"""Tests for the explicit tree-simulation APIs."""

from __future__ import annotations

import numpy as np
import pytest

import toytree
from toytree.utils import ToytreeError


def test_removed_ambiguous_public_names() -> None:
    """Clean-break names are absent from the public namespace."""
    for name in ("rtree", "bdtree", "coaltree"):
        assert not hasattr(toytree.rtree, name)


@pytest.mark.parametrize("model", ["yule", "pda"])
def test_random_topology_invariants_and_reproducibility(model: str) -> None:
    """Topology generators return reproducible binary unit-edge trees."""
    first = toytree.rtree.random_topology(20, model=model, seed=123)
    second = toytree.rtree.random_topology(20, model=model, seed=123)
    assert first.ntips == 20
    assert first.nnodes == 39
    assert first.get_topology_id() == second.get_topology_id()
    assert first.get_tip_labels() == second.get_tip_labels()
    assert first.treenode.dist == 0
    assert all(node.dist == 1 for node in first if not node.is_root())
    assert all(len(node.children) == 2 for node in first[first.ntips :])


def test_random_topology_accepts_numpy_random_sources() -> None:
    """Generator and SeedSequence inputs follow the shared RNG contract."""
    sequence = np.random.SeedSequence(123)
    first = toytree.rtree.random_topology(12, seed=sequence)
    second = toytree.rtree.random_topology(12, seed=np.random.SeedSequence(123))
    assert first.get_topology_id() == second.get_topology_id()
    generator = np.random.default_rng(123)
    one = toytree.rtree.random_topology(12, seed=generator)
    two = toytree.rtree.random_topology(12, seed=generator)
    assert one.get_topology_id() != two.get_topology_id()


def test_shared_label_validation() -> None:
    """All generators reject duplicate labels after string conversion."""
    with pytest.raises(ValueError, match="unique"):
        toytree.rtree.random_topology(3, names=[1, "1", 2])
    with pytest.raises(ValueError, match="unique"):
        toytree.rtree.baltree(3, names=["a", "a", "b"])
    with pytest.raises(ValueError, match="unique"):
        toytree.rtree.coalescent_tree(3, names=["a", "a", "b"])


def test_shared_validation_rejects_ambiguous_types() -> None:
    """Shared validation rejects strings, truthy flags, and negative seeds."""
    with pytest.raises(ValueError, match="not one string"):
        toytree.rtree.random_topology(3, names="abc")
    with pytest.raises(ToytreeError, match="boolean"):
        toytree.rtree.random_topology(3, randomize_labels=1)
    with pytest.raises(ToytreeError, match="boolean"):
        toytree.rtree.imbtree(3, randomize_labels=1)
    with pytest.raises(ToytreeError, match="boolean"):
        toytree.rtree.baltree(3, randomize_labels=1)
    with pytest.raises(ToytreeError, match="nonnegative"):
        toytree.rtree.random_topology(3, seed=-1)
    with pytest.raises(ToytreeError, match="boolean"):
        toytree.rtree.birth_death_process(stop_time=1.0, condition_on_survival="yes")


def test_shape_generators_are_ultrametric_and_allow_odd_balance() -> None:
    """Fixed-shape generators share validation and height semantics."""
    for function in (
        toytree.rtree.unittree,
        toytree.rtree.imbtree,
        toytree.rtree.baltree,
    ):
        tree = function(9, treeheight=3.5, seed=123)
        assert tree.ntips == 9
        assert tree.is_ultrametric()
        assert tree.treenode.height == pytest.approx(3.5)
    balanced = toytree.rtree.baltree(9)
    for node in balanced[balanced.ntips :]:
        if node.is_leaf():
            continue
        sizes = [len(child.get_leaves()) for child in node.children]
        assert abs(sizes[0] - sizes[1]) <= 1


def test_unittree_uses_full_basal_internal_edges() -> None:
    """Basal internal edges use the same pre-scaling unit as other internals."""
    for seed in range(100):
        tree = toytree.rtree.unittree(16, seed=seed)
        basal = [child for child in tree.treenode.children if not child.is_leaf()]
        if len(basal) == 2:
            internal = [
                node for node in tree if not node.is_leaf() and not node.is_root()
            ]
            assert all(node.dist == pytest.approx(internal[0].dist) for node in basal)
            break
    else:
        raise AssertionError("no tested seed produced two internal basal edges")


def test_birth_death_process_time_stop_and_status() -> None:
    """Forward histories stop exactly and identify extant/extinct leaves."""
    result = toytree.rtree.birth_death_process(
        birth_rate=1.0,
        death_rate=0.4,
        stop_time=3.0,
        start="crown",
        seed=123,
    )
    assert result.elapsed_time == 3.0
    assert result.stop_reason == "time"
    assert result.events == result.births + result.deaths
    assert result.extant_tips >= 1
    assert result.reconstructed_tree is not None
    assert result.reconstructed_tree.is_ultrametric()
    assert all(
        getattr(node, "extant", False)
        for node in result.reconstructed_tree[: result.reconstructed_tree.ntips]
    )


def test_birth_death_process_taxa_stop_has_event_boundary() -> None:
    """Richness stopping retains the statistically meaningful event boundary."""
    result = toytree.rtree.birth_death_process(
        birth_rate=1.0, death_rate=0.2, stop_ntips=12, seed=17
    )
    assert result.extant_tips == 12
    assert result.stop_reason == "taxa"
    assert (
        sum(
            node.dist == 0
            for node in result.complete_tree[: result.complete_tree.ntips]
        )
        >= 2
    )


def test_birth_death_process_rejects_impossible_or_unbounded_inputs() -> None:
    """Invalid stopping combinations and impossible richness targets fail fast."""
    with pytest.raises(ToytreeError, match="exactly one"):
        toytree.rtree.birth_death_process(stop_time=1, stop_ntips=3)
    with pytest.raises(ToytreeError, match="positive birth_rate"):
        toytree.rtree.birth_death_process(birth_rate=0, death_rate=1, stop_ntips=3)
    with pytest.raises(ToytreeError, match="max_events"):
        toytree.rtree.birth_death_process(
            birth_rate=1, death_rate=0, stop_ntips=100, max_events=2, seed=1
        )


def test_birth_death_conditioned_crown_and_origin() -> None:
    """Conditioned trees honor explicit crown and origin conventions."""
    crown = toytree.rtree.birth_death_conditioned_tree(
        20, birth_rate=1.0, death_rate=0.2, crown_age=4.0, seed=123
    )
    assert crown.ntips == 20
    assert crown.is_ultrametric()
    assert crown.treenode.height == pytest.approx(4.0)
    assert crown.treenode.dist == 0

    origin = toytree.rtree.birth_death_conditioned_tree(
        20, birth_rate=1.0, death_rate=0.2, origin_age=4.0, seed=123
    )
    assert origin.is_ultrametric()
    assert origin.treenode.height < 4.0
    assert origin.treenode.height + origin.treenode.dist == pytest.approx(4.0)
    assert origin.treenode.origin_age == 4.0


def test_birth_death_conditioned_supports_critical_limit() -> None:
    """Equal birth and death rates use the analytic critical limit."""
    tree = toytree.rtree.birth_death_conditioned_tree(
        16, birth_rate=0.5, death_rate=0.5, crown_age=3.0, seed=4
    )
    assert tree.ntips == 16
    assert tree.is_ultrametric()
    assert tree.treenode.height == pytest.approx(3.0)


def test_coalescent_tree_units_and_validation() -> None:
    """The coalescent returns a contemporaneous genealogy in generations."""
    tree = toytree.rtree.coalescent_tree(12, Ne=100, ploidy=2, seed=123)
    assert tree.ntips == 12
    assert tree.nnodes == 23
    assert tree.is_ultrametric()
    with pytest.raises(ToytreeError):
        toytree.rtree.coalescent_tree(1)
    with pytest.raises(ToytreeError):
        toytree.rtree.coalescent_tree(4, Ne=0)


@pytest.mark.parametrize(
    "model,sigma",
    [
        ("strict", None),
        ("uncorrelated_lognormal", 0.5),
        ("autocorrelated_lognormal", 0.3),
    ],
)
def test_simulate_branch_rates_contract(model: str, sigma: float | None) -> None:
    """Rate simulation copies its input and annotates each output edge."""
    tree = toytree.rtree.unittree(12, treeheight=2.0, seed=1)
    before = tree.write(None, None, None)
    result = toytree.rtree.simulate_branch_rates(
        tree, model=model, mean_rate=0.02, sigma=sigma, seed=123
    )
    assert tree.write(None, None, None) == before
    assert result is not tree
    for node in result[:-1]:
        assert node.time >= 0
        assert node.rate > 0
        assert node.expected_substitutions == pytest.approx(node.time * node.rate)
        assert node.dist == pytest.approx(node.expected_substitutions)


@pytest.mark.parametrize(
    "model,sigma",
    [
        ("strict", None),
        ("uncorrelated_lognormal", 0.4),
        ("autocorrelated_lognormal", 0.4),
    ],
)
def test_simulate_branch_rates_converts_explicit_root_stem(
    model: str, sigma: float | None
) -> None:
    """Origin-conditioned stem duration is converted with all other edges."""
    tree = toytree.rtree.birth_death_conditioned_tree(
        12, birth_rate=1.0, death_rate=0.2, origin_age=4.0, seed=2
    )
    stem_time = tree.treenode.dist
    result = toytree.rtree.simulate_branch_rates(
        tree, model=model, mean_rate=0.02, sigma=sigma, seed=3
    )
    assert stem_time > 0
    assert result.treenode.time == pytest.approx(stem_time)
    assert result.treenode.rate > 0
    assert result.treenode.dist == pytest.approx(
        result.treenode.time * result.treenode.rate
    )
    assert tree.treenode.dist == pytest.approx(stem_time)


def test_simulate_branch_rates_parameter_validation() -> None:
    """Model-specific dispersion and input branch validation are explicit."""
    tree = toytree.rtree.unittree(5)
    with pytest.raises(ToytreeError, match="must be None"):
        toytree.rtree.simulate_branch_rates(tree, "strict", sigma=0.1)
    with pytest.raises(ToytreeError, match="required"):
        toytree.rtree.simulate_branch_rates(tree, "uncorrelated_lognormal")
    broken = tree.copy()
    broken[0]._dist = -1
    with pytest.raises(ToytreeError, match="finite and >= 0"):
        toytree.rtree.simulate_branch_rates(broken, "strict")
