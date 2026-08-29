# ruff: noqa: D103

import numpy as np

import toytree


def _normalized_internal_ages(tree):
    ages = tree.get_node_data("height").to_numpy(dtype=float)
    return ages[tree.ntips :] / ages[-1]


def test_time_unit_rescaling_preserves_penalized_chronograms():
    tree = toytree.tree("((a:0.2,b:0.4):0.3,(c:0.5,d:0.7):0.2);")
    mrca = tree.get_mrca_node("a", "b").idx
    base_calibrations = {-1: 2.0, mrca: (0.4, 1.4)}
    scaled_calibrations = {-1: 2e6, mrca: (0.4e6, 1.4e6)}
    for method in ("uncorrelated_lognormal", "correlated"):
        base = tree.mod.edges_make_ultrametric(
            method=method,
            lam=0.5,
            calibrations=base_calibrations,
            full=True,
            max_iter=2_000,
            max_fun=4_000,
            max_refine=5,
        )
        scaled = tree.mod.edges_make_ultrametric(
            method=method,
            lam=0.5,
            calibrations=scaled_calibrations,
            full=True,
            max_iter=2_000,
            max_fun=4_000,
            max_refine=5,
        )
        assert np.allclose(
            _normalized_internal_ages(base["tree"]),
            _normalized_internal_ages(scaled["tree"]),
            atol=2e-4,
        )
        assert np.isclose(base["penalty"], scaled["penalty"], atol=2e-4)
        assert np.allclose(
            np.asarray(base["rates"]) / 1e6,
            np.asarray(scaled["rates"]),
            rtol=2e-3,
            atol=1e-10,
        )


def test_all_full_results_declare_observation_model_and_units():
    tree = toytree.tree("((a:0.2,b:0.4):0.3,(c:0.5,d:0.7):0.2);")
    configs = [
        {"method": "clock"},
        {"method": "discrete", "ncategories": 2},
        {"method": "relaxed", "lam": 0.5},
        {"method": "uncorrelated_lognormal", "lam": 0.5},
        {"method": "correlated", "lam": 0.5},
    ]
    for config in configs:
        result = tree.mod.edges_make_ultrametric(
            calibrations={-1: 1.0},
            full=True,
            max_iter=1_000,
            max_fun=2_000,
            max_refine=3,
            **config,
        )
        assert result["observation_model"] == "fractional_poisson"
        assert result["branch_length_units"] == "substitutions_per_site"
        assert "pseudologlik" in result
        assert "penalized_pseudologlik" in result
        assert "loglik" not in result
