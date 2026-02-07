import unittest

import numpy as np

from toytree.mod._src.penalized_likelihood.pl_relaxed_test import (
    edges_make_ultrametric_pl_relaxed,
)
from toytree.mod._src.penalized_likelihood.pl_utils import (
    get_tree_with_uncorrelated_relaxed_rates,
)


class TestPenalizedLikelihoodRelaxed(unittest.TestCase):
    def test_relaxed_pl_makes_ultrametric(self):
        tree = get_tree_with_uncorrelated_relaxed_rates(ntips=10, mean=3, sigma=3, seed=123)
        result = edges_make_ultrametric_pl_relaxed(
            tree,
            lam=0.5,
            calibrations={-1: 1.0},
            full=True,
            max_iter=5_000,
            max_fun=5_000,
            max_refine=5,
        )
        new_tree = result["tree"]
        heights = new_tree.get_node_data("height").values
        tip_heights = heights[:new_tree.ntips]
        self.assertTrue(np.allclose(tip_heights, tip_heights[0]))
        self.assertIn("penalty", result)


if __name__ == "__main__":
    unittest.main()
