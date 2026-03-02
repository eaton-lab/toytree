import numpy as np
import pandas as pd
import pytest

from toytree.pcm.src.sim.sim_discrete import MarkovModel, simulate_discrete_trait


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

    def test_simulate_returns_series_when_inplace_true_single_replicate(self, tree6):
        """Single replicate returns Series and still writes to the tree."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            nreplicates=1,
            trait_name="X",
            state_names=["A", "B", "C"],
            inplace=True,
            seed=123,
        )
        assert isinstance(data, pd.Series)
        assert data.name == "X"
        assert "X" in tree6.features

    def test_default_output_states_are_strings_single_replicate(self, tree6):
        """Default unlabeled states are numeric strings, not ints."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            nreplicates=1,
            seed=123,
        )
        assert isinstance(data, pd.Series)
        values = set(data.dropna().tolist())
        assert values.issubset({"0", "1", "2"})
        assert all(isinstance(i, str) for i in values)

    def test_default_output_states_are_strings_multi_replicate(self, tree6):
        """Default unlabeled states are numeric strings for DataFrame output."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            nreplicates=3,
            seed=123,
        )
        assert isinstance(data, pd.DataFrame)
        values = set(pd.unique(data.to_numpy().ravel()))
        assert values.issubset({"0", "1", "2"})
        assert all(isinstance(i, str) for i in values)

    def test_default_inplace_stores_strings(self, tree6):
        """Default unlabeled states written to tree are strings."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            nreplicates=1,
            trait_name="X",
            inplace=True,
            seed=123,
        )
        vals = tree6.get_node_data("X").dropna().tolist()
        assert vals
        assert all(isinstance(i, str) for i in vals)
        assert set(vals).issubset({"0", "1", "2"})
        assert set(data.dropna().tolist()).issubset({"0", "1", "2"})

    def test_simulate_returns_dataframe_when_inplace_true_multi_replicate(self, tree6):
        """Multiple replicates return DataFrame and still write to the tree."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            nreplicates=3,
            trait_name="X",
            state_names=["A", "B", "C"],
            inplace=True,
            seed=123,
        )
        assert isinstance(data, pd.DataFrame)
        assert list(data.columns) == ["X_0", "X_1", "X_2"]
        for col in data.columns:
            assert col in tree6.features

    def test_simulate_tips_only_inplace_true_still_returns_data(self, tree6):
        """tips_only=True and inplace=True still returns the simulated object."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=2,
            model="ER",
            nreplicates=1,
            tips_only=True,
            trait_name="X",
            state_names=["A", "B"],
            inplace=True,
            seed=123,
        )
        assert isinstance(data, pd.Series)
        assert data.shape[0] == tree6.ntips
        assert "X" in tree6.features

    def test_state_names_override_default_string_labels(self, tree6):
        """Custom state_names labels override default numeric-string labels."""
        data = simulate_discrete_trait(
            tree=tree6,
            nstates=3,
            model="ER",
            nreplicates=1,
            state_names=["A", "B", "C"],
            seed=123,
        )
        values = set(data.dropna().tolist())
        assert values.issubset({"A", "B", "C"})


# Additional source-driven tests.


def test_nreplicates_less_than_one_is_coerced_to_single_series(tree6):
    """Nreplicates < 1 is coerced to one replicate and returns Series."""
    data = simulate_discrete_trait(
        tree=tree6,
        nstates=2,
        model="ER",
        nreplicates=0,
        seed=123,
    )
    assert isinstance(data, pd.Series)
    assert data.name == "t0"


def test_default_single_replicate_name_is_t0(tree6):
    """Single replicate default output name is t0."""
    data = simulate_discrete_trait(tree=tree6, nstates=2, model="ER", seed=123)
    assert isinstance(data, pd.Series)
    assert data.name == "t0"


def test_default_multi_replicate_column_names_are_t_series(tree6):
    """Multiple replicate default output names follow t0, t1, ... pattern."""
    data = simulate_discrete_trait(tree=tree6, nstates=2, model="ER", nreplicates=3)
    assert isinstance(data, pd.DataFrame)
    assert list(data.columns) == ["t0", "t1", "t2"]


def test_root_state_is_respected_at_root_node(tree6):
    """Provided root_state is enforced at the root in output."""
    data = simulate_discrete_trait(
        tree=tree6,
        nstates=3,
        model="ER",
        root_state=2,
        nreplicates=1,
        state_names=["A", "B", "C"],
        seed=123,
    )
    root_idx = tree6.treenode.idx
    assert data.loc[root_idx] == "C"
