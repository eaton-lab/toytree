#!/usr/bin/env python

import numpy as np
import pandas as pd
import pytest

from toytree.utils import ToytreeError


class TestContinuousBMSim:
    """Tests univariate and multivariate continuous simulators."""

    @pytest.fixture(autouse=True)
    def _setup_tree(self, make_unittree):
        """Create a reproducible tree for each test."""
        self.tree = make_unittree(ntips=8, treeheight=1.0, seed=123)

    def test_bm_returns_series(self):
        """BM simulation returns a node-indexed Series."""
        out = self.tree.pcm.simulate_continuous_trait("bm", params=1.0, seed=1)
        assert isinstance(out, pd.Series)
        assert out.shape[0] == self.tree.nnodes

    def test_bm_inplace_still_returns_series(self):
        """inplace=True still returns the simulated Series."""
        out = self.tree.pcm.simulate_continuous_trait(
            "bm",
            params=1.0,
            name="x",
            inplace=True,
            seed=2,
        )
        assert isinstance(out, pd.Series)
        assert out.name == "x"
        stored = self.tree.get_node_data("x")
        assert stored.shape[0] == self.tree.nnodes

    def test_tips_only_returns_series(self):
        """tips_only=True returns only tip rows."""
        out = self.tree.pcm.simulate_continuous_trait(
            "bm",
            params=1.0,
            tips_only=True,
            seed=3,
        )
        assert isinstance(out, pd.Series)
        assert out.shape[0] == self.tree.ntips

    def test_ou_alpha_zero_matches_bm_seeded(self):
        """OU with alpha=0 matches BM under identical seed."""
        bm = self.tree.pcm.simulate_continuous_trait("bm", params=1.0, seed=4)
        ou = self.tree.pcm.simulate_continuous_trait("ou", params=(1.0, 0.0), seed=4)
        pd.testing.assert_series_equal(bm, ou)

    def test_eb_r_zero_matches_bm_seeded(self):
        """EB with r=0 matches BM under identical seed."""
        bm = self.tree.pcm.simulate_continuous_trait("bm", params=1.0, seed=5)
        eb = self.tree.pcm.simulate_continuous_trait("eb", params=(1.0, 0.0), seed=5)
        pd.testing.assert_series_equal(bm, eb)

    def test_multivariate_sigma_validation(self):
        """Multivariate BM validates covariance matrix shape and SPD."""
        with pytest.raises(ToytreeError):
            self.tree.pcm.simulate_multivariate_continuous_trait(
                model="bm",
                params=np.array([[1.0, 2.0, 3.0], [2.0, 1.0, 2.0]]),
                seed=7,
            )
        with pytest.raises(ToytreeError):
            self.tree.pcm.simulate_multivariate_continuous_trait(
                model="bm",
                params=np.array([[1.0, 2.0], [0.0, 1.0]]),
                seed=7,
            )

    def test_multivariate_output_shape(self):
        """Multivariate BM returns DataFrame with requested trait names."""
        out = self.tree.pcm.simulate_multivariate_continuous_trait(
            model="bm",
            params=np.array([[1.0, 0.3], [0.3, 2.0]]),
            names=["a", "b"],
            seed=8,
        )
        assert isinstance(out, pd.DataFrame)
        assert out.shape[0] == self.tree.nnodes
        assert list(out.columns) == ["a", "b"]

    def test_multivariate_default_names_are_x_series(self):
        """Default multivariate output names follow the X1, X2, ... pattern."""
        out = self.tree.pcm.simulate_multivariate_continuous_trait(
            model="bm",
            params=np.array([[1.0, 0.3], [0.3, 2.0]]),
            seed=18,
        )
        assert list(out.columns) == ["X1", "X2"]

    def test_multivariate_ou_a_zero_matches_bm_seeded(self):
        """Multivariate OU with zero A matches multivariate BM."""
        rmat = np.array([[1.0, 0.2], [0.2, 1.5]])
        bm = self.tree.pcm.simulate_multivariate_continuous_trait(
            model="bm",
            params=rmat,
            seed=101,
        )
        ou = self.tree.pcm.simulate_multivariate_continuous_trait(
            model="ou",
            params=(rmat, np.zeros((2, 2))),
            seed=101,
        )
        pd.testing.assert_frame_equal(bm, ou)

    def test_multivariate_eb_r_zero_matches_bm_seeded(self):
        """Multivariate EB with r-vector zeros matches multivariate BM."""
        rmat = np.array([[1.0, 0.2], [0.2, 1.5]])
        bm = self.tree.pcm.simulate_multivariate_continuous_trait(
            model="bm",
            params=rmat,
            seed=102,
        )
        eb = self.tree.pcm.simulate_multivariate_continuous_trait(
            model="eb",
            params=(rmat, np.zeros(2)),
            seed=102,
        )
        pd.testing.assert_frame_equal(bm, eb)

    def test_multivariate_bm_regime_params_accept_feature_name(self):
        """Multivariate regime mapping can be supplied via tree feature name."""
        regmap = {
            node.idx: ("fast" if node.idx % 2 == 0 else "slow")
            for node in self.tree
            if not node.is_root()
        }
        tree = self.tree.set_node_data("reg", regmap, inplace=False)
        out = tree.pcm.simulate_multivariate_continuous_trait(
            model="bm",
            params={
                "fast": np.array([[2.0, 0.1], [0.1, 1.0]]),
                "slow": np.array([[0.5, 0.0], [0.0, 0.5]]),
            },
            regime="reg",
            seed=103,
        )
        assert isinstance(out, pd.DataFrame)
        assert out.shape[0] == tree.nnodes

    def test_invalid_bm_params_raise(self):
        """Negative BM sigma2 is rejected."""
        with pytest.raises(ToytreeError):
            self.tree.pcm.simulate_continuous_trait("bm", params=-1.0)

    def test_root_state_scalar_only(self):
        """Univariate root_state must be scalar or None."""
        with pytest.raises(ToytreeError):
            self.tree.pcm.simulate_continuous_trait(
                "bm",
                params=1.0,
                root_state=[0.0, 1.0],
            )
        with pytest.raises(ToytreeError):
            self.tree.pcm.simulate_continuous_trait(
                "bm",
                params=1.0,
                root_state={"t0": 0.0},
            )

    def test_name_default_and_custom(self):
        """Default and custom output names are applied correctly."""
        out_default = self.tree.pcm.simulate_continuous_trait("bm", params=1.0, seed=9)
        assert out_default.name == "X"
        out_custom = self.tree.pcm.simulate_continuous_trait(
            "bm",
            params=1.0,
            name="X",
            seed=9,
        )
        assert out_custom.name == "X"

    def test_tips_only_inplace_sets_internal_nan(self):
        """tips_only + inplace stores tip values and leaves internal as NaN."""
        out = self.tree.pcm.simulate_continuous_trait(
            "bm",
            params=1.0,
            name="X",
            tips_only=True,
            inplace=True,
            seed=10,
        )
        assert out.shape[0] == self.tree.ntips
        stored = self.tree.get_node_data("X")
        assert stored.iloc[self.tree.ntips :].isna().all()

    def test_bm_regime_params_accept_feature_name(self):
        """Univariate BM regime parameters can be keyed by feature labels."""
        regmap = {
            node.idx: ("fast" if node.idx % 2 == 0 else "slow")
            for node in self.tree
            if not node.is_root()
        }
        tree = self.tree.set_node_data("reg", regmap, inplace=False)
        out = tree.pcm.simulate_continuous_trait(
            "bm",
            params={"fast": 2.0, "slow": 0.5},
            regime="reg",
            seed=11,
        )
        assert isinstance(out, pd.Series)
        assert out.shape[0] == tree.nnodes

    def test_bm_regime_params_accept_series_indexed_by_idx(self):
        """Regime labels are accepted as node-indexed Series."""
        reg = pd.Series(index=range(self.tree.nnodes), dtype=object)
        reg[:] = "slow"
        reg.iloc[0] = "fast"
        out = self.tree.pcm.simulate_continuous_trait(
            "bm",
            params={"fast": 2.0, "slow": 0.5},
            regime=reg,
            seed=12,
        )
        assert isinstance(out, pd.Series)

    def test_regime_requires_full_coverage_when_params_is_dict(self):
        """Regime dict params require labels on all non-root nodes."""
        tree = self.tree.set_node_data("reg", {0: "fast"}, inplace=False)
        with pytest.raises(ToytreeError):
            tree.pcm.simulate_continuous_trait(
                "bm",
                params={"fast": 2.0},
                regime="reg",
                seed=14,
            )

    def test_ou_and_eb_regime_params_validation(self):
        """OU/EB validate tuple length and accept regime dict parameter maps."""
        with pytest.raises(ToytreeError):
            self.tree.pcm.simulate_continuous_trait("ou", params=(1.0,), seed=15)
        with pytest.raises(ToytreeError):
            self.tree.pcm.simulate_continuous_trait("eb", params=(1.0,), seed=15)

        tree = self.tree.set_node_data(
            "reg",
            {
                node.idx: ("fast" if node.idx % 2 == 0 else "slow")
                for node in self.tree
                if not node.is_root()
            },
            inplace=False,
        )
        ou = tree.pcm.simulate_continuous_trait(
            "ou",
            params={"fast": (2.0, 0.5), "slow": (1.0, 0.5)},
            regime="reg",
            seed=16,
        )
        eb = tree.pcm.simulate_continuous_trait(
            "eb",
            params={"fast": (2.0, -0.2), "slow": (1.0, -0.2)},
            regime="reg",
            seed=16,
        )
        assert isinstance(ou, pd.Series)
        assert isinstance(eb, pd.Series)

    def test_ou_optimum_follows_root_state(self):
        """Changing OU root_state changes simulated values with fixed seed."""
        out0 = self.tree.pcm.simulate_continuous_trait(
            "ou",
            params=(1.0, 1.0),
            root_state=0.0,
            seed=17,
        )
        out1 = self.tree.pcm.simulate_continuous_trait(
            "ou",
            params=(1.0, 1.0),
            root_state=2.0,
            seed=17,
        )
        assert not np.allclose(out0.values, out1.values)

    def test_old_kwargs_removed(self):
        """Removed legacy kwargs should raise TypeError."""
        with pytest.raises(TypeError):
            self.tree.pcm.simulate_continuous_trait("bm", sigma2=1.0)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            self.tree.pcm.simulate_continuous_trait(  # type: ignore[call-arg]
                "bm",
                params=1.0,
                nreplicates=2,
            )


# Additional source-driven tests.


def test_invalid_model_raises_toytree_error(make_unittree):
    """Unknown model labels are rejected."""
    tree = make_unittree(ntips=8, treeheight=1.0, seed=123)
    with pytest.raises(ToytreeError, match="model must be one of"):
        tree.pcm.simulate_continuous_trait("xyz", params=1.0)


def test_blank_name_raises_toytree_error(make_unittree):
    """Blank output trait names are rejected."""
    tree = make_unittree(ntips=8, treeheight=1.0, seed=123)
    with pytest.raises(ToytreeError, match="name must be a non-empty string"):
        tree.pcm.simulate_continuous_trait("bm", params=1.0, name="  ")


def test_regime_dict_params_require_regime_arg(make_unittree):
    """Dict-valued params require regime labels to be provided."""
    tree = make_unittree(ntips=8, treeheight=1.0, seed=123)
    with pytest.raises(ToytreeError, match="regime is required"):
        tree.pcm.simulate_continuous_trait(
            "bm",
            params={"fast": 2.0, "slow": 0.5},
        )


def test_eb_nonfinite_r_rejected(make_unittree):
    """EB validates that r is finite."""
    tree = make_unittree(ntips=8, treeheight=1.0, seed=123)
    with pytest.raises(ToytreeError, match="finite r"):
        tree.pcm.simulate_continuous_trait("eb", params=(1.0, np.inf))
