import numpy as np

from toytree.mod._src.penalized_likelihood.pl_correlated import (
    edges_make_ultrametric_pl_correlated,
)
from toytree.mod._src.penalized_likelihood.pl_utils import (
    get_tree_with_correlated_relaxed_rates,
)



from conftest import PytestCompat

class TestPenalizedLikelihoodCorrelated(PytestCompat):
    def test_correlated_pl_makes_ultrametric(self):
        tree = get_tree_with_correlated_relaxed_rates(ntips=12, mean=3, sigma=2, seed=123)
        result = edges_make_ultrametric_pl_correlated(
            tree,
            lam=0.5,
            calibrations={-1: 1.0},
            full=True,
            max_iter=2_000,
            max_fun=2_000,
            max_refine=4,
        )
        new_tree = result["tree"]
        heights = new_tree.get_node_data("height").values
        tip_heights = heights[:new_tree.ntips]
        self.assertTrue(np.allclose(tip_heights, tip_heights[0]))
        self.assertIn("penalty", result)
        self.assertIn("optimizer_message", result)


