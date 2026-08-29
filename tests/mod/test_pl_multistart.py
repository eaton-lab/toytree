#!/usr/bin/env python


import numpy as np
from conftest import PytestCompat

from toytree.mod._src.penalized_pseudolikelihood.clock import (
    edges_make_ultrametric_clock,
)
from toytree.mod._src.penalized_pseudolikelihood.correlated import (
    edges_make_ultrametric_correlated,
)
from toytree.mod._src.penalized_pseudolikelihood.discrete import (
    edges_make_ultrametric_discrete,
)
from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    edges_make_ultrametric_uncorrelated_lognormal,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    get_tree_with_categorical_rates,
    get_tree_with_correlated_rates,
    get_tree_with_uncorrelated_rates,
)


class TestPenalizedLikelihoodMultistart(PytestCompat):
    """Multistart regression tests for penalized-likelihood fits."""

    def test_clock_multistart_full_fields(self):
        """Clock fits should expose multistart metadata."""
        tree = get_tree_with_categorical_rates(ntips=10, nrates=1, seed=123)
        res = edges_make_ultrametric_clock(
            tree,
            calibrations={-1: 1.0},
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
            nstarts=2,
            ncores=1,
            seed=7,
        )
        self.assertIn("starts", res)
        self.assertEqual(res["nstarts"], 2)
        self.assertTrue(res["tree"].is_ultrametric())

    def test_discrete_multistart_seed_reproducible(self):
        """Discrete multistart runs should be reproducible under a fixed seed."""
        tree = get_tree_with_categorical_rates(ntips=10, nrates=2, seed=123)
        kw = dict(
            ncategories=2,
            calibrations={-1: 1.0},
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
            nstarts=3,
            ncores=1,
            seed=11,
        )
        r1 = edges_make_ultrametric_discrete(tree, **kw)
        r2 = edges_make_ultrametric_discrete(tree, **kw)
        self.assertEqual(r1["best_start"], r2["best_start"])
        self.assertTrue(np.isclose(r1["pseudologlik"], r2["pseudologlik"]))
        self.assertTrue(np.allclose(r1["rates"], r2["rates"]))
        self.assertTrue(np.allclose(r1["weights"], r2["weights"]))

    def test_discrete_ncat1_matches_clock(self):
        """One discrete rate category should reduce exactly to the clock model."""
        tree = get_tree_with_categorical_rates(ntips=10, nrates=1, seed=123)
        kwargs = dict(
            calibrations={-1: 1.0},
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
            nstarts=2,
            ncores=1,
            seed=5,
        )
        cres = edges_make_ultrametric_clock(tree, **kwargs)
        dres = edges_make_ultrametric_discrete(tree, ncategories=1, **kwargs)
        self.assertTrue(
            np.isclose(cres["pseudologlik"], dres["pseudologlik"], atol=1e-9)
        )
        self.assertEqual(dres["weights"], [1.0])
        self.assertTrue(
            np.isclose(float(dres["rates"][0]), float(cres["rate"]), atol=1e-9)
        )

    def test_uncorrelated_lognormal_multistart_parallel(self):
        """Lognormal fits should support multistart execution in parallel."""
        tree = get_tree_with_uncorrelated_rates(ntips=10, mean=3, sigma=3, seed=123)
        res = edges_make_ultrametric_uncorrelated_lognormal(
            tree,
            lam=0.5,
            calibrations={-1: 1.0},
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
            nstarts=3,
            ncores=2,
            seed=12,
        )
        self.assertEqual(res["nstarts"], 3)
        self.assertTrue(res["tree"].is_ultrametric())

    def test_correlated_multistart_parallel(self):
        """Correlated fits should support multistart execution in parallel."""
        tree = get_tree_with_correlated_rates(ntips=10, mean=1.0, sigma=1.0, seed=123)
        res = edges_make_ultrametric_correlated(
            tree,
            lam=0.5,
            calibrations={-1: 1.0},
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
            nstarts=2,
            ncores=2,
            seed=12,
        )
        self.assertEqual(res["nstarts"], 2)
        self.assertTrue(res["tree"].is_ultrametric())

    def test_discrete_default_uses_four_starts(self):
        """Discrete fits should use the validated four-start default."""
        tree = get_tree_with_categorical_rates(ntips=6, nrates=2, seed=321)
        result = edges_make_ultrametric_discrete(
            tree,
            ncategories=2,
            calibrations={-1: 1.0},
            full=True,
            max_iter=300,
            max_fun=600,
            max_refine=2,
            ncores=1,
            seed=9,
        )
        self.assertEqual(result["nstarts"], 4)
