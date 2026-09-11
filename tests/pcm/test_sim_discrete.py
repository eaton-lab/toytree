import numpy as np
import pandas as pd
import pytest

from toytree.pcm.src.sim.sim_discrete import (
    DiscreteMarkovSimulator,
    MarkovModel,
    simulate_discrete_trait,
)
from toytree.pcm.src.traits.fit_discrete_ctmc import fit_discrete_ctmc
from toytree.utils import ToytreeError


@pytest.fixture
def tree6(make_unittree):
    """Return a small reproducible tree used by discrete simulator tests."""
    return make_unittree(ntips=6, seed=123)


class TestDiscreteMarkovModelSim:
    """Tests discrete CTMC simulation utilities."""

    def test_qmatrix_er_construction(self):
        """Ensure ER model places relative rates directly in Q."""
        model = MarkovModel(nstates=3, mtype="ER", rate_scalar=1.0)
        expected = np.array(
            [
                [-2.0, 1.0, 1.0],
                [1.0, -2.0, 1.0],
                [1.0, 1.0, -2.0],
            ]
        )
        np.testing.assert_allclose(model.qmatrix, expected, rtol=1e-8, atol=1e-12)
        np.testing.assert_allclose(
            model.transition_matrix,
            expected,
            rtol=1e-8,
            atol=1e-12,
        )
        np.testing.assert_allclose(model.state_frequencies, np.repeat(1 / 3, 3))

    def test_ard_stationary_frequencies_are_derived_from_q(self):
        """Derive, rather than independently parameterize, ARD frequencies."""
        rates = np.array([[0.0, 2.0], [1.0, 0.0]])
        model = MarkovModel(nstates=2, mtype="ARD", relative_rates=rates)
        np.testing.assert_allclose(model.qmatrix, [[-2.0, 2.0], [1.0, -1.0]])
        np.testing.assert_allclose(model.state_frequencies, [1 / 3, 2 / 3])
        np.testing.assert_allclose(
            model.state_frequencies @ model.qmatrix,
            [0, 0],
            atol=1e-12,
        )

    def test_nonunique_stationary_distribution_requires_root_prior(self):
        """Require an explicit root distribution when Q has no unique one."""
        rates = np.zeros((2, 2), dtype=float)
        with pytest.raises(ToytreeError, match="root_prior is required"):
            MarkovModel(nstates=2, mtype="ARD", relative_rates=rates)
        model = MarkovModel(
            nstates=2,
            mtype="ARD",
            relative_rates=rates,
            root_prior=[0.25, 0.75],
        )
        assert model.state_frequencies is None
        np.testing.assert_allclose(model.root_prior, [0.25, 0.75])

    def test_seed_reproducibility_for_parameters(self):
        """Ensure seeded models produce identical random parameters."""
        model_a = MarkovModel(nstates=4, mtype="SYM", seed=123)
        model_b = MarkovModel(nstates=4, mtype="SYM", seed=123)
        np.testing.assert_allclose(model_a.relative_rates, model_b.relative_rates)
        np.testing.assert_allclose(model_a.state_frequencies, model_b.state_frequencies)

    def test_simulate_returns_series_when_inplace_true(self, tree6):
        """Simulation returns a Series and still writes to the tree."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            name="X",
            state_names=["A", "B", "C"],
            inplace=True,
            seed=123,
        )
        assert isinstance(data, pd.Series)
        assert data.name == "X"
        assert "X" in tree6.features

    def test_default_output_states_are_uppercase_strings(self, tree6):
        """Small state spaces default to uppercase string labels."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            seed=123,
        )
        assert isinstance(data, pd.Series)
        values = set(data.dropna().tolist())
        assert values.issubset({"A", "B", "C"})
        assert all(isinstance(i, str) for i in values)

    def test_large_state_spaces_fall_back_to_numeric_strings(self, tree6):
        """Larger state spaces use numeric string labels by default."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=27,
            model="ER",
            seed=123,
        )
        values = set(data.dropna().tolist())
        assert values
        assert all(isinstance(i, str) for i in values)
        assert all(value.isdigit() for value in values)

    def test_default_inplace_stores_strings(self, tree6):
        """Default labels written to the tree remain string-valued."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            name="X",
            inplace=True,
            seed=123,
        )
        vals = tree6.get_node_data("X").dropna().tolist()
        assert vals
        assert all(isinstance(i, str) for i in vals)
        assert set(vals).issubset({"A", "B", "C"})
        assert set(data.dropna().tolist()).issubset({"A", "B", "C"})

    def test_simulate_tips_only_inplace_true_still_returns_data(self, tree6):
        """tips_only=True and inplace=True still returns the simulated object."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=2,
            model="ER",
            tips_only=True,
            name="X",
            state_names=["A", "B"],
            inplace=True,
            seed=123,
        )
        assert isinstance(data, pd.Series)
        assert data.shape[0] == tree6.ntips
        assert "X" in tree6.features

    def test_state_names_override_default_labels(self, tree6):
        """Custom state_names labels override default alphabetic labels."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            state_names=["alpha", "beta", "gamma"],
            seed=123,
        )
        values = set(data.dropna().tolist())
        assert values.issubset({"alpha", "beta", "gamma"})

    def test_transition_draws_match_analytic_probability(self, tree6):
        """Repeated edge draws recover exp(Qt) transition probabilities."""
        model = MarkovModel(
            nstates=2,
            mtype="ARD",
            relative_rates=np.array([[0.0, 2.0], [1.0, 0.0]]),
            root_prior=[1.0, 0.0],
        )
        simulator = DiscreteMarkovSimulator(tree6, model, seed=12345)
        expected = model.get_transition_probability_matrix(0.7)[0]
        draws = np.array([simulator._edge_sim(0, 0.7) for _ in range(20_000)])
        observed = np.bincount(draws, minlength=2) / draws.size
        np.testing.assert_allclose(observed, expected, atol=0.01, rtol=0.0)

    def test_single_rng_stream_matches_explicit_construction(self, tree6):
        """Parameter generation and trait evolution consume one RNG stream."""
        public = simulate_discrete_trait(
            tree6,
            3,
            model="ARD",
            root_prior=[1.0, 0.0, 0.0],
            seed=2345,
        )

        rng = np.random.default_rng(2345)
        model = MarkovModel(
            3,
            "ARD",
            root_prior=[1.0, 0.0, 0.0],
            seed=rng,
        )
        indices = DiscreteMarkovSimulator(tree6, model, seed=rng).run()
        expected = pd.Series(
            np.asarray(["A", "B", "C"], dtype=object)[indices],
            index=range(tree6.nnodes),
            name="X",
            dtype=object,
        )
        pd.testing.assert_series_equal(public, expected)

    def test_zero_rate_symmetric_model_is_deterministic(self, tree6):
        """A zero-rate ER/SYM model uses a uniform root but never changes."""
        data = simulate_discrete_trait(
            tree6,
            3,
            model="ER",
            relative_rates=0.0,
            seed=7,
        )
        assert data.nunique() == 1

    def test_state_labels_preserve_qmatrix_order(self, tree6):
        """state_names position is the explicit Q row and column order."""
        data = simulate_discrete_trait(
            tree6,
            3,
            model="ARD",
            relative_rates=np.zeros((3, 3)),
            root_prior=[0.0, 1.0, 0.0],
            state_names=["zebra", "ant", "moose"],
            seed=8,
        )
        assert set(data) == {"ant"}

    def test_custom_state_order_is_carried_into_fitting(self, tree6):
        """A direct simulation Series keeps ARD row/column semantics in fitting."""
        rates = np.array(
            [
                [0.0, 0.3, 0.8],
                [1.2, 0.0, 0.5],
                [0.4, 1.5, 0.0],
            ]
        )
        labels = ["zebra", "ant", "moose"]
        data = simulate_discrete_trait(
            tree6,
            3,
            model="ARD",
            relative_rates=rates,
            root_prior=[0.2, 0.3, 0.5],
            state_names=labels,
            tips_only=True,
            seed=81,
        )
        fit = fit_discrete_ctmc(
            tree6,
            data,
            nstates=3,
            model="ARD",
            fixed_rates=rates,
            root_prior=[0.2, 0.3, 0.5],
        )
        assert fit.state_labels == tuple(labels)
        np.testing.assert_allclose(fit.relative_rates, rates)

    def test_model_constraints_raise_toytree_errors(self):
        """Invalid ER/SYM matrices never rely on removable assertions."""
        with pytest.raises(ToytreeError, match="off-diagonal rates"):
            MarkovModel(2, "ER", relative_rates=[[0.0, 1.0], [2.0, 0.0]])
        with pytest.raises(ToytreeError, match="must be symmetric"):
            MarkovModel(2, "SYM", relative_rates=[[0.0, 1.0], [2.0, 0.0]])
        with pytest.raises(ToytreeError, match="must have shape"):
            MarkovModel(3, "ARD", relative_rates=np.ones((2, 2)))

    def test_zero_time_transition_is_exact_identity(self):
        """A zero-duration CTMC transition is exactly the identity matrix."""
        model = MarkovModel(3, "ER")
        np.testing.assert_array_equal(
            model.get_transition_probability_matrix(0.0), np.eye(3)
        )


def test_default_series_name_is_x(tree6):
    """Single discrete simulations default to the Series name X."""
    data = simulate_discrete_trait(tree=tree6, nstates=2, model="ER", seed=123)
    assert isinstance(data, pd.Series)
    assert data.name == "X"


def test_one_hot_root_prior_is_respected_at_root_node(tree6):
    """A one-hot root prior fixes the simulated root state."""
    data = simulate_discrete_trait(
        tree=tree6,
        nstates=3,
        model="ER",
        root_prior=[0.0, 0.0, 1.0],
        state_names=["A", "B", "C"],
        seed=123,
    )
    root_idx = tree6.treenode.idx
    assert data.loc[root_idx] == "C"


def test_removed_root_state_and_state_frequencies_raise(tree6):
    """Removed root-distribution keywords are not compatibility aliases."""
    with pytest.raises(TypeError):
        simulate_discrete_trait(tree6, 2, root_state=1)
    with pytest.raises(TypeError):
        simulate_discrete_trait(tree6, 2, state_frequencies=[0.5, 0.5])


def test_lowercase_model_labels_are_accepted(tree6):
    """Model labels are normalized to uppercase for convenience."""
    data = simulate_discrete_trait(tree=tree6, nstates=2, model="er", seed=123)
    assert isinstance(data, pd.Series)
    assert data.name == "X"


def test_seed_accepts_numpy_generator(tree6):
    """Discrete simulation accepts a Generator as the seed argument."""
    rng = np.random.default_rng(123)
    data = simulate_discrete_trait(tree=tree6, nstates=2, model="ER", seed=rng)
    assert isinstance(data, pd.Series)


def test_removed_nreplicates_kwarg_raises(tree6):
    """Multi-replicate output is no longer part of the public API."""
    with pytest.raises(TypeError):
        simulate_discrete_trait(  # type: ignore[call-arg]
            tree=tree6,
            nstates=2,
            model="ER",
            nreplicates=2,
        )


def test_blank_name_raises_toytree_error(tree6):
    """Blank output names are rejected."""
    with pytest.raises(ToytreeError, match="name must be a non-empty string"):
        simulate_discrete_trait(
            tree=tree6,
            nstates=2,
            model="ER",
            name="  ",
        )


def test_state_names_must_match_nstates(tree6):
    """Custom state labels must match the number of modeled states."""
    with pytest.raises(ToytreeError, match="state_names length must match nstates"):
        simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            state_names=["A", "B"],
        )


@pytest.mark.parametrize(
    "state_names",
    [
        ["A", "A"],
        ["A", 1],
        [True, False],
    ],
)
def test_state_names_are_unique_and_homogeneous(tree6, state_names):
    """State labels are unambiguous for downstream Q-matrix ordering."""
    with pytest.raises(ToytreeError, match="state_names"):
        simulate_discrete_trait(tree6, 2, state_names=state_names)


@pytest.mark.parametrize("nstates", [True, 1, 0, -1, 2.5])
def test_nstates_requires_at_least_two_integer_states(tree6, nstates):
    """Invalid or degenerate state-space sizes are rejected consistently."""
    with pytest.raises(ToytreeError, match="nstates"):
        simulate_discrete_trait(tree6, nstates)


def test_seedsequence_is_supported_and_reproducible(tree6):
    """Equivalent SeedSequences reproduce parameters and states."""
    first = simulate_discrete_trait(
        tree6, 3, model="SYM", seed=np.random.SeedSequence(9)
    )
    second = simulate_discrete_trait(
        tree6, 3, model="SYM", seed=np.random.SeedSequence(9)
    )
    pd.testing.assert_series_equal(first, second)
