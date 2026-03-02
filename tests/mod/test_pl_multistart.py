#!/usr/bin/env python

import unittest

import numpy as np

from toytree.mod._src.penalized_likelihood.pl_clock import edges_make_ultrametric_pl_clock
from toytree.mod._src.penalized_likelihood.pl_discrete import edges_make_ultrametric_pl_discrete
from toytree.mod._src.penalized_likelihood.pl_relaxed import edges_make_ultrametric_pl_relaxed
from toytree.mod._src.penalized_likelihood.pl_correlated import edges_make_ultrametric_pl_correlated
from toytree.mod._src.penalized_likelihood.pl_utils import (
    get_tree_with_categorical_rates,
    get_tree_with_uncorrelated_relaxed_rates,
    get_tree_with_correlated_relaxed_rates,
)


class TestPenalizedLikelihoodMultistart(unittest.TestCase):
    def test_clock_multistart_full_fields(self):
        tree = get_tree_with_categorical_rates(ntips=10, nrates=1, seed=123)
        res = edges_make_ultrametric_pl_clock(
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
        r1 = edges_make_ultrametric_pl_discrete(tree, **kw)
        r2 = edges_make_ultrametric_pl_discrete(tree, **kw)
        self.assertEqual(r1["best_start"], r2["best_start"])
        self.assertTrue(np.isclose(r1["PHIIC"], r2["PHIIC"]))

    def test_discrete_ncat1_matches_clock(self):
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
        cres = edges_make_ultrametric_pl_clock(tree, **kwargs)
        dres = edges_make_ultrametric_pl_discrete(tree, ncategories=1, **kwargs)
        self.assertTrue(np.isclose(cres["PHIIC"], dres["PHIIC"], atol=1e-9))
        self.assertTrue(np.isclose(cres["loglik"], dres["loglik"], atol=1e-9))
        self.assertEqual(dres["freqs"], [1.0])
        self.assertTrue(np.isclose(float(dres["rates"][0]), float(cres["rate"]), atol=1e-9))

    def test_relaxed_multistart_parallel(self):
        tree = get_tree_with_uncorrelated_relaxed_rates(ntips=10, mean=3, sigma=3, seed=123)
        res = edges_make_ultrametric_pl_relaxed(
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
        tree = get_tree_with_correlated_relaxed_rates(ntips=10, mean=1.0, sigma=1.0, seed=123)
        res = edges_make_ultrametric_pl_correlated(
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


if __name__ == "__main__":
    unittest.main()
