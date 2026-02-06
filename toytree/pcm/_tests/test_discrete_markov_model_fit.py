import unittest

import numpy as np

import toytree
from toytree.pcm.src.traits.discrete_markov_model_fit import (
    fit_discrete_markov_model,
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


if __name__ == "__main__":
    unittest.main()
