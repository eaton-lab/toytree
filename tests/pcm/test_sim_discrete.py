import numpy as np
import pandas as pd
import pytest

from toytree.pcm.src.sim.sim_discrete import MarkovModel, simulate_discrete_trait
from toytree.utils import ToytreeError


@pytest.fixture
def tree6(make_unittree):
    """Return a small reproducible tree used by discrete simulator tests."""
    return make_unittree(ntips=6, seed=123)


class TestDiscreteMarkovModelSim:
    """Tests discrete CTMC simulation utilities."""

    def test_qmatrix_er_construction(self):
        """Ensure ER model builds expected reversible Q matrix."""
        model = MarkovModel(nstates=3, mtype="ER", rate_scalar=1.0)
        expected = np.array(
            [
                [-2.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
                [1.0 / 3.0, -2.0 / 3.0, 1.0 / 3.0],
                [1.0 / 3.0, 1.0 / 3.0, -2.0 / 3.0],
            ]
        )
        np.testing.assert_allclose(model.qmatrix, expected, rtol=1e-8, atol=1e-12)
        np.testing.assert_allclose(
            model.transition_matrix,
            expected,
            rtol=1e-8,
            atol=1e-12,
        )

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


def test_default_series_name_is_x(tree6):
    """Single discrete simulations default to the Series name X."""
    data = simulate_discrete_trait(tree=tree6, nstates=2, model="ER", seed=123)
    assert isinstance(data, pd.Series)
    assert data.name == "X"


def test_root_state_is_respected_at_root_node(tree6):
    """Provided root_state is enforced at the root in output."""
    data = simulate_discrete_trait(
        tree=tree6,
        nstates=3,
        model="ER",
        root_state=2,
        state_names=["A", "B", "C"],
        seed=123,
    )
    root_idx = tree6.treenode.idx
    assert data.loc[root_idx] == "C"


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
