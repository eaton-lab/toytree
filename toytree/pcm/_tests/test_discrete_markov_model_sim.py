import unittest

import numpy as np

from toytree.pcm.src.traits.discrete_markov_model_sim import MarkovModel


class TestDiscreteMarkovModelSim(unittest.TestCase):
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
        np.testing.assert_allclose(model.transition_matrix, expected, rtol=1e-8, atol=1e-12)

    def test_seed_reproducibility_for_parameters(self):
        """Ensure seeded models produce identical random parameters."""
        model_a = MarkovModel(nstates=4, mtype="SYM", seed=123)
        model_b = MarkovModel(nstates=4, mtype="SYM", seed=123)
        np.testing.assert_allclose(model_a.relative_rates, model_b.relative_rates)
        np.testing.assert_allclose(model_a.state_frequencies, model_b.state_frequencies)


if __name__ == "__main__":
    unittest.main()
