import numpy as np
from conftest import PytestCompat

import toytree
from toytree.mod._src.penalized_likelihood.pl_utils import (
    _decode_age_params,
    _encode_age_params,
    _finalize_ultrametric_ages,
    _get_children_map_from_edges,
    _normalize_calibrations,
    _pack_log_rates,
    _unpack_log_rates,
)
from toytree.utils import ToytreeError


class TestPenalizedLikelihoodUtils(PytestCompat):
    """Tests for shared penalized-likelihood helpers."""

    def test_pack_unpack_log_rates_roundtrip_with_floor(self):
        """Pack/unpack should preserve positive rates with a floor."""
        rates = np.array([0.0, 1e-20, 0.5, 2.0], dtype=float)
        packed = _pack_log_rates(rates, rate_floor=1e-12)
        unpacked = _unpack_log_rates(packed)
        expected = np.array([1e-12, 1e-12, 0.5, 2.0], dtype=float)
        self.assertTrue(np.allclose(unpacked, expected))

    def test_get_children_map_from_edges(self):
        """Children map should group edge endpoints by parent idx."""
        edges = np.array([[0, 3], [1, 3], [2, 4], [3, 4]], dtype=int)
        cmap = _get_children_map_from_edges(edges)
        self.assertTrue(np.array_equal(np.sort(cmap[3]), np.array([0, 1])))
        self.assertTrue(np.array_equal(np.sort(cmap[4]), np.array([2, 3])))

    def test_encode_decode_age_params_roundtrip(self):
        """Age parameter transforms should round-trip valid ages."""
        edges = np.array([[0, 3], [1, 3], [2, 4], [3, 4]], dtype=int)
        cmap = _get_children_map_from_edges(edges)
        ages_idxs = np.array([3, 4], dtype=int)
        ages_bounds = [(0.01, 1e9), (0.02, 1e9)]
        ages = np.array([0.0, 0.0, 0.0, 0.4, 0.9], dtype=float)
        params = _encode_age_params(ages, ages_idxs, ages_bounds, cmap)
        decoded = _decode_age_params(
            params, np.zeros_like(ages), ages_idxs, ages_bounds, cmap
        )
        self.assertTrue(np.allclose(decoded[ages_idxs], ages[ages_idxs], atol=1e-8))
        self.assertGreater(decoded[4], decoded[3])

    def test_decode_respects_child_order_and_upper_bounds(self):
        """Decoded ages should stay ordered and inside finite bounds."""
        edges = np.array([[0, 3], [1, 3], [2, 4], [3, 4]], dtype=int)
        cmap = _get_children_map_from_edges(edges)
        ages_idxs = np.array([3, 4], dtype=int)
        ages_bounds = [(0.0, 0.25), (0.1, 0.3)]
        # push both nodes toward their effective lower bounds
        params = np.array([-30.0, -30.0], dtype=float)
        decoded = _decode_age_params(
            params,
            np.zeros(5, dtype=float),
            ages_idxs,
            ages_bounds,
            cmap,
            dist_floor=1e-8,
            age_upper_switch=1e6,
        )
        # internal nodes should still be strictly older than their oldest child
        self.assertGreater(decoded[3], 0.0)
        self.assertGreater(decoded[4], decoded[3])
        # bounded transforms should respect calibration upper bounds
        self.assertLessEqual(decoded[3], 0.25)
        self.assertLessEqual(decoded[4], 0.3)

    def test_finalize_ultrametric_ages_repairs_small_negative_branch(self):
        """Tiny negative branches should be projected back to positive length."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        mrca = tree.get_mrca_node("a", "b").idx
        root = tree.treenode.idx
        ages = np.zeros(tree.nnodes, dtype=float)
        ages[mrca] = 0.5
        ages[root] = ages[mrca] - 5e-9

        repaired = _finalize_ultrametric_ages(tree, ages, dist_floor=1e-12)
        edges = tree.get_edges("idx")
        dists = repaired[edges[:, 1]] - repaired[edges[:, 0]]

        self.assertGreater(repaired[root], repaired[mrca])
        self.assertTrue(np.all(dists > 1e-12))

    def test_finalize_ultrametric_ages_raises_on_large_negative_branch(self):
        """Materially invalid branch lengths should raise instead of repair."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        mrca = tree.get_mrca_node("a", "b").idx
        root = tree.treenode.idx
        ages = np.zeros(tree.nnodes, dtype=float)
        ages[mrca] = 0.5
        ages[root] = 0.49

        with self.assertRaises(ToytreeError):
            _finalize_ultrametric_ages(tree, ages, dist_floor=1e-12)

    def test_normalize_calibrations_rejects_incompatible_bounds(self):
        """Ancestor and descendant intervals should be checked for overlap."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        mrca = tree.get_mrca_node("a", "b").idx
        with self.assertRaises(ToytreeError):
            _normalize_calibrations(
                tree,
                {-1: 0.8, mrca: (0.9, 0.95)},
                dist_floor=1e-12,
            )
