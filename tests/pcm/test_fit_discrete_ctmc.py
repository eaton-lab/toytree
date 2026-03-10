import io
from contextlib import redirect_stderr

import numpy as np
import pandas as pd
from conftest import PytestCompat

import toytree
from toytree.pcm.src.sim.sim_discrete import MarkovModel
from toytree.pcm.src.traits.fit_discrete_ctmc import (
    DiscreteMarkovModelFit,
    fit_discrete_ctmc,
    infer_ancestral_states_discrete_ctmc,
)
from toytree.utils import ToytreeError


class TestDiscreteMarkovModelFit(PytestCompat):
    """Tests discrete CTMC model fitting and ancestral-state wrappers."""

    def test_hard_rename_api_surface(self):
        """Only the CTMC inference name should be exported."""
        self.assertTrue(hasattr(toytree.pcm, "infer_ancestral_states_discrete_ctmc"))
        self.assertFalse(hasattr(toytree.pcm, "infer_ancestral_states_discrete_mk"))

    def test_fit_accepts_feature_name_string(self):
        """String feature input should be coerced as one replicate."""
        tree = toytree.rtree.unittree(ntips=6, treeheight=1.0, seed=10)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=3,
            model="ER",
            tips_only=True,
            seed=10,
        )
        tree = tree.set_node_data("X", dict(data), default=np.nan, inplace=False)
        result = fit_discrete_ctmc(
            tree=tree,
            data="X",
            nstates=3,
            model="ER",
        )
        self.assertTrue(np.isfinite(result.log_likelihood))
        self.assertEqual(result.nstates, 3)

    def test_fit_with_fixed_rates_and_frequencies(self):
        """Fit with fixed parameters should recover the expected Q matrix."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=123)
        model = MarkovModel(nstates=2, mtype="ER", rate_scalar=1.0)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=2,
            model="ER",
            relative_rates=model.relative_rates,
            state_frequencies=model.state_frequencies,
            rate_scalar=model.rate_scalar,
            nreplicates=1,
            tips_only=True,
            seed=123,
        )
        data.index = tree.get_tip_labels()
        tree = tree.set_node_data("x", dict(data), default=np.nan, inplace=False)
        result = fit_discrete_ctmc(
            tree=tree,
            data="x",
            nstates=2,
            model="ER",
            fixed_rates=model.relative_rates,
            fixed_state_frequencies=model.state_frequencies,
        )
        np.testing.assert_allclose(result.qmatrix, model.qmatrix)
        self.assertTrue(np.isfinite(result.log_likelihood))
        self.assertEqual(result.nparams, 0)

    def test_fit_rejects_dataframe_input(self):
        """Fit should reject multi-trait DataFrame input."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=3)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=2,
            model="ER",
            nreplicates=2,
            tips_only=True,
            seed=3,
        )
        data.index = tree.get_tip_labels()
        with self.assertRaises(ToytreeError):
            fit_discrete_ctmc(
                tree=tree,
                data=data,
                nstates=2,
                model="ER",
            )

    def test_public_fit_no_longer_accepts_rate_scalar(self):
        """Public wrapper should hide the advanced internal rate scale arg."""
        tree = toytree.rtree.unittree(ntips=6, treeheight=1.0, seed=13)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=3,
            model="ER",
            tips_only=True,
            seed=13,
        )
        data.index = tree.get_tip_labels()
        tree = tree.set_node_data("x", dict(data), default=np.nan, inplace=False)
        with self.assertRaises(TypeError):
            fit_discrete_ctmc(
                tree=tree,
                data="x",
                nstates=3,
                model="ER",
                rate_scalar=2.0,
            )

    def test_internal_fitter_allows_rate_scalar_with_fixed_rates(self):
        """Advanced rate scaling remains available through the internal fitter."""
        tree = toytree.rtree.unittree(ntips=6, treeheight=1.0, seed=14)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=2,
            model="ER",
            tips_only=True,
            seed=14,
        )
        data.index = tree.get_tip_labels()
        tree = tree.set_node_data("x", dict(data), default=np.nan, inplace=False)
        fixed_rates = np.array([[0.0, 1.0], [1.0, 0.0]])
        result = DiscreteMarkovModelFit(
            tree=tree,
            data="x",
            nstates=2,
            model="ER",
            fixed_rates=fixed_rates,
            rate_scalar=2.0,
        ).fit()
        self.assertTrue(np.isfinite(result.log_likelihood))

    def test_sym_rejects_one_sided_fixed_rate_pair(self):
        """SYM fixed_rates must fix mirrored entries together or leave both NaN."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=21)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=3,
            model="SYM",
            tips_only=True,
            seed=21,
        )
        data.index = tree.get_tip_labels()
        tree = tree.set_node_data("x", dict(data), default=np.nan, inplace=False)
        fixed_rates = np.full((3, 3), np.nan)
        np.fill_diagonal(fixed_rates, 0.0)
        fixed_rates[0, 1] = 1.0
        with self.assertRaises(ToytreeError):
            DiscreteMarkovModelFit(
                tree=tree,
                data="x",
                nstates=3,
                model="SYM",
                fixed_rates=fixed_rates,
            )

    def test_er_rejects_one_sided_fixed_rate_pair(self):
        """ER fixed_rates must fix mirrored entries together or leave both NaN."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=22)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=2,
            model="ER",
            tips_only=True,
            seed=22,
        )
        data.index = tree.get_tip_labels()
        tree = tree.set_node_data("x", dict(data), default=np.nan, inplace=False)
        fixed_rates = np.array([[0.0, 1.0], [np.nan, 0.0]])
        with self.assertRaises(ToytreeError):
            DiscreteMarkovModelFit(
                tree=tree,
                data="x",
                nstates=2,
                model="ER",
                fixed_rates=fixed_rates,
            )

    def test_sym_accepts_paired_equal_fixed_entries(self):
        """SYM accepts mirrored fixed values when they are equal."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=23)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=3,
            model="SYM",
            tips_only=True,
            seed=23,
        )
        data.index = tree.get_tip_labels()
        tree = tree.set_node_data("x", dict(data), default=np.nan, inplace=False)
        fixed_rates = np.full((3, 3), np.nan)
        np.fill_diagonal(fixed_rates, 0.0)
        fixed_rates[0, 1] = 1.5
        fixed_rates[1, 0] = 1.5
        fitter = DiscreteMarkovModelFit(
            tree=tree,
            data="x",
            nstates=3,
            model="SYM",
            fixed_rates=fixed_rates,
        )
        self.assertIsInstance(fitter, DiscreteMarkovModelFit)

    def test_sym_rejects_paired_unequal_fixed_entries(self):
        """SYM rejects mirrored fixed values when they differ."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=24)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=3,
            model="SYM",
            tips_only=True,
            seed=24,
        )
        data.index = tree.get_tip_labels()
        tree = tree.set_node_data("x", dict(data), default=np.nan, inplace=False)
        fixed_rates = np.full((3, 3), np.nan)
        np.fill_diagonal(fixed_rates, 0.0)
        fixed_rates[0, 1] = 1.0
        fixed_rates[1, 0] = 2.0
        with self.assertRaises(ToytreeError):
            DiscreteMarkovModelFit(
                tree=tree,
                data="x",
                nstates=3,
                model="SYM",
                fixed_rates=fixed_rates,
            )

    def test_infer_ancestral_states(self):
        """Inference should return posterior probabilities and states."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=2)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=2,
            model="ER",
            tips_only=True,
            seed=2,
        )
        data.index = tree.get_tip_labels()
        out = infer_ancestral_states_discrete_ctmc(
            tree=tree,
            data=data,
            nstates=2,
            model="ER",
        )
        result = out["model_fit"]
        df = out["data"]
        self.assertNotIn("tree", out)
        self.assertTrue(np.isfinite(result.log_likelihood))
        self.assertEqual(df.shape[0], tree.nnodes)
        prob_col = f"{data.name}_anc_posterior"
        prob_sums = pd.DataFrame(df[prob_col].tolist()).sum(axis=1).to_numpy()
        np.testing.assert_allclose(prob_sums, np.ones(tree.nnodes))
        state_col = f"{data.name}_anc"
        self.assertEqual(df[state_col].shape[0], tree.nnodes)
        self.assertNotIn(f"{data.name}_anc", tree.features)
        self.assertNotIn(f"{data.name}_anc_posterior", tree.features)

    def test_infer_ancestral_states_tip_only_data_emits_no_warning(self):
        """Tip-only observations should not emit an internal-state warning."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=20)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=2,
            model="ER",
            tips_only=True,
            seed=20,
        )
        data.index = tree.get_tip_labels()
        err = io.StringIO()
        with redirect_stderr(err):
            infer_ancestral_states_discrete_ctmc(
                tree=tree,
                data=data,
                nstates=2,
                model="ER",
            )
        self.assertEqual(err.getvalue(), "")

    def test_infer_ancestral_states_warns_for_internal_node_states(self):
        """Observed internal states should emit a fixed-constraint warning."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=21)
        tree = tree.set_node_data(
            "X",
            {0: "A", 1: "A", 2: "B", 3: "B", 4: "B"},
            default=np.nan,
            inplace=False,
        )
        err = io.StringIO()
        with redirect_stderr(err):
            out = infer_ancestral_states_discrete_ctmc(
                tree=tree,
                data="X",
                nstates=2,
                model="ER",
            )
        self.assertIn("warning:", err.getvalue())
        self.assertIn("1 non-missing internal node state(s)", err.getvalue())
        self.assertIn("treated as fixed constraints", err.getvalue())
        self.assertEqual(out["data"].shape[0], tree.nnodes)

    def test_infer_ancestral_states_inplace_mutates_input_tree(self):
        """inplace=True should write ancestral states and posteriors to tree."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=12)
        tree.pcm.simulate_discrete_trait(
            nstates=2,
            model="ER",
            tips_only=True,
            trait_name="X",
            state_names="AB",
            inplace=True,
            seed=12,
        )
        out = infer_ancestral_states_discrete_ctmc(
            tree=tree,
            data="X",
            nstates=2,
            model="ER",
            inplace=True,
        )
        self.assertNotIn("tree", out)
        self.assertIn("X_anc", tree.features)
        self.assertIn("X_anc_posterior", tree.features)

    def test_default_fixed_rates_allow_sym_model(self):
        """Default fixed rates should not error for SYM models."""
        tree = toytree.rtree.unittree(ntips=3, treeheight=1.0, seed=7)
        data = toytree.pcm.simulate_discrete_trait(
            tree=tree,
            nstates=3,
            model="SYM",
            tips_only=True,
            seed=7,
        )
        data.index = tree.get_tip_labels()
        tree = tree.set_node_data("x", dict(data), default=np.nan, inplace=False)
        result = fit_discrete_ctmc(
            tree=tree,
            data="x",
            nstates=3,
            model="SYM",
        )
        self.assertTrue(np.isfinite(result.log_likelihood))
