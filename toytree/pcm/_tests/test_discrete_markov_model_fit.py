import unittest

import numpy as np
import pandas as pd

import toytree
from toytree.pcm.src.traits.discrete_markov_model_fit import (
    fit_discrete_markov_model,
    infer_ancestral_states_discrete_mk,
)
from toytree.pcm.src.traits.discrete_markov_model_sim import MarkovModel


class TestDiscreteMarkovModelFit(unittest.TestCase):
    def test_fit_with_fixed_rates_and_frequencies(self):
        """Fit with fixed parameters should recover the expected Q matrix."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=123)
        model = MarkovModel(nstates=2, mtype="ER", rate_scalar=1.0)
        data = toytree.pcm.simulate_discrete_data(
            tree=tree,
            nstates=2,
            model="ER",
            relative_rates=model.relative_rates,
            state_frequencies=model.state_frequencies,
            rate_scalar=model.rate_scalar,
            nreplicates=3,
            tips_only=True,
            seed=123,
        )
        data.index = tree.get_tip_labels()
        result = fit_discrete_markov_model(
            tree=tree,
            data=data,
            nstates=2,
            model="ER",
            fixed_rates=model.relative_rates,
            fixed_state_frequencies=model.state_frequencies,
        )
        np.testing.assert_allclose(result.qmatrix, model.qmatrix)
        self.assertTrue(np.isfinite(result.log_likelihood))
        self.assertEqual(result.nparams, 0)

    def test_infer_ancestral_states(self):
        """Inference should return posterior probabilities and states."""
        tree = toytree.rtree.unittree(ntips=4, treeheight=1.0, seed=2)
        data = toytree.pcm.simulate_discrete_data(
            tree=tree,
            nstates=2,
            model="ER",
            tips_only=True,
            seed=2,
        )
        data.index = tree.get_tip_labels()
        result, prob_df, state_df = infer_ancestral_states_discrete_mk(
            tree=tree,
            data=data,
            nstates=2,
            model="ER",
        )
        self.assertTrue(np.isfinite(result.log_likelihood))
        self.assertEqual(prob_df.shape[0], tree.nnodes)
        prob_sums = prob_df.sum(axis=1).to_numpy()
        np.testing.assert_allclose(prob_sums, np.ones(tree.nnodes))
        self.assertEqual(state_df.shape[0], tree.nnodes)

    def test_default_fixed_rates_allow_sym_model(self):
        """Default fixed rates should not error for SYM models."""
        tree = toytree.rtree.unittree(ntips=3, treeheight=1.0, seed=7)
        data = toytree.pcm.simulate_discrete_data(
            tree=tree,
            nstates=3,
            model="SYM",
            tips_only=True,
            seed=7,
        )
        data.index = tree.get_tip_labels()
        result = fit_discrete_markov_model(
            tree=tree,
            data=data,
            nstates=3,
            model="SYM",
        )
        self.assertTrue(np.isfinite(result.log_likelihood))


if __name__ == "__main__":
    unittest.main()
