#!/usr/bin/env python

from unittest.mock import patch

import numpy as np
from conftest import PytestCompat

import toytree
from toytree.mod._src.penalized_pseudolikelihood import lambda_cv
from toytree.mod._src.penalized_pseudolikelihood.lambda_cv import (
    _fit_correlated_cv_fold,
    _normalize_lambdas,
    edges_make_ultrametric_correlated_lambda_cv,
)
from toytree.utils import ToytreeError


class TestCorrelatedLambdaCV(PytestCompat):
    """Tests for correlated-rate smoothing selection."""

    def test_lambda_grid_is_sorted_deduplicated_and_validated(self):
        """The lambda grid must contain distinct positive finite values."""
        self.assertEqual(_normalize_lambdas([10, 0.1, 10, 1]), (0.1, 1.0, 10.0))
        for values in ([1], [1, 1], [0, 1], [np.nan, 1], [True, 1], 1.0):
            with self.assertRaises(ToytreeError):
                _normalize_lambdas(values)

    def test_fold_excludes_held_observation_from_fit_and_initialization(self):
        """Held observations cannot leak into fitting or initialization."""
        tree = toytree.tree("((a:1,b:2):1,(c:3,d:4):1);")
        edges = np.asarray(tree.get_edges("idx"), dtype=int)
        child_index = tree.get_nodes("a")[0].idx
        edge_index = int(np.flatnonzero(edges[:, 0] == child_index)[0])
        all_dists = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
        calls = []

        def fake_fit(fit_tree, **kwargs):
            calls.append((fit_tree, kwargs))
            rates = np.ones(tree.nedges)
            return {
                "expected_branch_lengths": np.full(tree.nedges, 2.0),
                "rates": rates,
                "converged": True,
                "pseudologlik": -1.0,
                "penalized_pseudologlik": -1.5,
                "penalty": 0.5,
            }

        base = {
            "tree": tree,
            "lam": 1.0,
            "candidate_index": 0,
            "fold": 0,
            "edge_index": edge_index,
            "child_index": child_index,
            "all_dists": all_dists,
            "calibrations": {-1: 1.0},
            "fit_options": {
                "max_iter": 10,
                "max_fun": 10,
                "max_refine": 1,
                "nstarts": 1,
                "ncores": 1,
                "seed": 1,
            },
        }
        with patch.object(lambda_cv, "edges_make_ultrametric_correlated", fake_fit):
            low = _fit_correlated_cv_fold({**base, "observed": 1.0})
            changed = all_dists.copy()
            changed[edge_index] = 100.0
            high = _fit_correlated_cv_fold(
                {**base, "observed": 100.0, "all_dists": changed}
            )

        self.assertEqual(low["predicted"], high["predicted"])
        self.assertNotEqual(low["score"], high["score"])
        self.assertEqual(low["predicted_rate"], low["ancestral_rate"])
        for fit_tree, kwargs in calls:
            self.assertFalse(kwargs["_observation_mask"][edge_index])
            self.assertNotIn(
                fit_tree.get_node_data("dist").values[child_index],
                (1.0, 100.0),
            )

    def test_unobserved_terminal_rate_is_profiled_from_its_ancestor(self):
        """A held terminal rate is inferred entirely from its ancestral penalty."""
        tree = toytree.tree("((a:0.2,b:0.3):0.4,(c:0.5,d:0.6):0.2);")
        edges = np.asarray(tree.get_edges("idx"), dtype=int)
        child_index = tree.get_nodes("a")[0].idx
        edge_index = int(np.flatnonzero(edges[:, 0] == child_index)[0])
        dists = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
        result = _fit_correlated_cv_fold(
            {
                "tree": tree,
                "lam": 1.0,
                "fold": 0,
                "edge_index": edge_index,
                "child_index": child_index,
                "observed": float(dists[edge_index]),
                "all_dists": dists,
                "calibrations": {-1: 1.0},
                "fit_options": {
                    "max_iter": 1000,
                    "max_fun": 2000,
                    "max_refine": 4,
                    "nstarts": 1,
                    "ncores": 1,
                    "seed": 123,
                },
            }
        )
        self.assertTrue(result["converged"], result["optimizer_message"])
        self.assertTrue(
            np.isclose(
                result["predicted_rate"],
                result["ancestral_rate"],
                rtol=1e-4,
                atol=1e-7,
            )
        )

    def test_exact_score_tie_favors_stronger_smoothing(self):
        """Exact score ties deterministically select the larger lambda."""
        tree = toytree.tree("((a:1,b:1):1,(c:1,d:1):1);")

        def fake_folds(payloads, ncores):
            return [
                {
                    "candidate_index": payload["candidate_index"],
                    "fold": payload["fold"],
                    "converged": True,
                    "score": 1.0,
                }
                for payload in payloads
            ]

        with (
            patch.object(lambda_cv, "_run_fold_payloads", fake_folds),
            patch.object(
                lambda_cv,
                "edges_make_ultrametric_correlated",
                return_value={"converged": True},
            ),
        ):
            result = edges_make_ultrametric_correlated_lambda_cv(
                tree, lambdas=[0.1, 10.0], seed=123
            )
        self.assertEqual(result["selected_lam"], 10.0)
        self.assertTrue(result["selected_at_boundary"])
        self.assertEqual(result["selection_target"], "lambda")
        self.assertEqual(result["score"], "pearson")

    def test_failed_folds_do_not_select_a_candidate(self):
        """A candidate with any failed fold is ineligible for selection."""
        tree = toytree.tree("((a:1,b:1):1,(c:1,d:1):1);")

        def fake_folds(payloads, ncores):
            return [
                {
                    "candidate_index": payload["candidate_index"],
                    "fold": payload["fold"],
                    "converged": False,
                    "score": float("inf"),
                }
                for payload in payloads
            ]

        with patch.object(lambda_cv, "_run_fold_payloads", fake_folds):
            with self.assertRaises(RuntimeError):
                edges_make_ultrametric_correlated_lambda_cv(tree, lambdas=[0.1, 1.0])

    def test_public_surface_has_only_correlated_lambda_selector(self):
        """Only within-correlated lambda selection is publicly exposed."""
        self.assertTrue(
            hasattr(toytree.mod, "edges_make_ultrametric_correlated_lambda_cv")
        )
        self.assertFalse(hasattr(toytree.mod, "edges_make_ultrametric_cv_model_select"))
        tree = toytree.tree("(a:1,b:1);")
        self.assertTrue(
            hasattr(tree.mod, "edges_make_ultrametric_correlated_lambda_cv")
        )
