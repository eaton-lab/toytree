#!/usr/bin/env python

"""Tests for pruning-based phylogenetic logistic regression."""

import numpy as np
import pandas as pd
from conftest import PytestCompat
from scipy.special import expit

import toytree
from toytree.pcm.src.phylolinalg.pglm import PCMPGLMResult
from toytree.utils.src.exceptions import ToytreeError


class TestPGLM(PytestCompat):
    """Tests for phase-1 pruning-based binary phylogenetic GLM."""

    def setUp(self):
        """Create a reproducible tree and binary logistic dataset."""
        self.tree = toytree.rtree.unittree(ntips=18, treeheight=1.0, seed=123)
        rng = np.random.default_rng(123)
        x = rng.normal(size=self.tree.ntips)
        group = np.array(["A" if i % 2 else "B" for i in range(self.tree.ntips)])
        # Simulate a phylogenetically structured latent effect for a realistic
        # binary response while keeping the test deterministic.
        vcv = self.tree.pcm.get_vcv_matrix_from_tree()
        e = rng.multivariate_normal(np.zeros(self.tree.ntips), vcv * 0.1)
        p = expit(-0.2 + 1.1 * x + e)
        y = rng.binomial(1, p, size=self.tree.ntips)
        self.df = pd.DataFrame(
            {"x": x, "group": group, "y": y},
            index=self.tree.get_tip_labels(),
        )

    def test_basic_fit_and_api_exposure(self):
        """Fit through package and tree APIs and inspect result structure."""
        fit = toytree.pcm.pglm(self.tree, "y ~ x", data=self.df)
        self.assertIsInstance(fit, PCMPGLMResult)
        self.assertEqual(fit.family, "binomial")
        self.assertEqual(fit.link, "logit")
        self.assertTrue(np.isfinite(fit.lambda_))
        self.assertTrue(
            ((fit.fitted_probabilities > 0) & (fit.fitted_probabilities < 1)).all()
        )
        fit2 = self.tree.pcm.pglm("y ~ x", data=self.df)
        self.assertIsInstance(fit2, PCMPGLMResult)

    def test_bool_and_two_level_string_responses(self):
        """Accept bool and two-level string binary responses."""
        dfb = self.df.copy()
        dfb["y"] = dfb["y"].astype(bool)
        fitb = toytree.pcm.pglm(self.tree, "y ~ x", data=dfb)
        self.assertIsInstance(fitb, PCMPGLMResult)
        self.assertIsNotNone(fitb.response_levels)

        dfs = self.df.copy()
        dfs["y"] = np.where(dfs["y"].astype(bool), "present", "absent")
        fits = toytree.pcm.pglm(self.tree, "y ~ x", data=dfs)
        self.assertEqual(fits.response_levels, ("absent", "present"))

    def test_reject_nonbinary_response(self):
        """Reject responses with more than two levels."""
        df = self.df.copy()
        df["y"] = ["a", "b", "c"] * 6
        with self.assertRaises(ToytreeError):
            toytree.pcm.pglm(self.tree, "y ~ x", data=df)

    def test_categorical_predictor_support(self):
        """Support Patsy-coded categorical predictors."""
        fit = toytree.pcm.pglm(self.tree, "y ~ x + C(group)", data=self.df)
        self.assertTrue(any("C(group)" in i for i in fit.design_columns))

    def test_firth_policy_and_fixed_lambda(self):
        """Apply family-level Firth policy and support fixed lambda override."""
        fit = toytree.pcm.pglm(self.tree, "y ~ x", data=self.df, lambda_=0.5)
        self.assertAlmostEqual(fit.lambda_, 0.5, places=8)
        self.assertFalse(fit.lambda_optimized)
        self.assertTrue(fit.firth)

    def test_alignment_missing_and_invalid_family_link(self):
        """Handle row alignment, missing rows, and unsupported family/link."""
        shuf = self.df.sample(frac=1.0, random_state=2)
        a = toytree.pcm.pglm(self.tree, "y ~ x", data=self.df, lambda_=1.0)
        b = toytree.pcm.pglm(self.tree, "y ~ x", data=shuf, lambda_=1.0)
        self.assertTrue(np.allclose(a.params.values, b.params.values, atol=1e-6))

        dfn = self.df.copy()
        dfn.loc[dfn.index[0], "x"] = np.nan
        fit = toytree.pcm.pglm(self.tree, "y ~ x", data=dfn, lambda_=1.0)
        self.assertEqual(fit.nobs, self.tree.ntips - 1)

        with self.assertRaises(ToytreeError):
            toytree.pcm.pglm(self.tree, "y ~ x", data=self.df, link="probit")

    def test_poisson_fit_and_validation(self):
        """Fit poisson-log models and validate count responses."""
        rng = np.random.default_rng(321)
        x = rng.normal(size=self.tree.ntips)
        vcv = self.tree.pcm.get_vcv_matrix_from_tree()
        phy = rng.multivariate_normal(np.zeros(self.tree.ntips), 0.05 * vcv)
        mu = np.exp(0.3 + 0.4 * x + phy)
        y = rng.poisson(mu)
        df = pd.DataFrame({"x": x, "y": y}, index=self.tree.get_tip_labels())

        fit_firth = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=df,
            family="poisson",
            link="log",
            lambda_=1.0,
        )
        self.assertEqual(fit_firth.family, "poisson")
        self.assertTrue(fit_firth.firth)
        self.assertTrue((fit_firth.fitted_mean > 0).all())
        self.assertTrue(np.isfinite(fit_firth.params.to_numpy()).all())

        fit = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=df,
            family="poisson",
            link="log",
            lambda_=1.0,
        )
        self.assertEqual(fit.family, "poisson")
        self.assertTrue(fit.firth)
        self.assertTrue((fit.fitted_mean > 0).all())
        self.assertTrue(np.isfinite(fit.params.to_numpy()).all())

        bad = df.copy()
        bad.iloc[0, bad.columns.get_loc("y")] = -1
        with self.assertRaises(ToytreeError):
            toytree.pcm.pglm(self.tree, "y ~ x", data=bad, family="poisson", link="log")
        bad2 = df.copy().astype(float)
        bad2.iloc[1, bad2.columns.get_loc("y")] = 1.5
        with self.assertRaises(ToytreeError):
            toytree.pcm.pglm(
                self.tree,
                "y ~ x",
                data=bad2,
                family="poisson",
                link="log",
            )

    def test_scaffold_family_validation_paths(self):
        """Validate implemented/scaffold family paths and parameter checks."""
        counts = pd.DataFrame(
            {"x": self.df["x"].values, "y": np.arange(self.tree.ntips) % 3},
            index=self.tree.get_tip_labels(),
        )
        fit_nb_fixed = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=counts,
            family="negative_binomial",
            link="log",
            family_params={"alpha": 1.2},
            lambda_=1.0,
        )
        self.assertEqual(fit_nb_fixed.family, "negative_binomial")
        self.assertFalse(fit_nb_fixed.firth)
        self.assertEqual(fit_nb_fixed.dispersion_params, {"alpha": 1.2})
        self.assertFalse(fit_nb_fixed.dispersion_estimated)
        self.assertTrue((fit_nb_fixed.fitted_mean > 0).all())

        fit_nb_est = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=counts,
            family="negative_binomial",
            link="log",
            lambda_=1.0,
        )
        self.assertEqual(fit_nb_est.family, "negative_binomial")
        self.assertFalse(fit_nb_est.firth)
        self.assertIsNotNone(fit_nb_est.dispersion_params)
        self.assertIn("alpha", fit_nb_est.dispersion_params)
        self.assertGreater(fit_nb_est.dispersion_params["alpha"], 0.0)
        self.assertTrue(fit_nb_est.dispersion_estimated)

        with self.assertRaises(ToytreeError):
            toytree.pcm.pglm(
                self.tree,
                "y ~ x",
                data=counts,
                family="negative_binomial",
                link="log",
                family_params={"alpha": -1},
            )

        gamma_df = pd.DataFrame(
            {"x": self.df["x"].values, "y": np.abs(self.df["x"].values) + 0.1},
            index=self.tree.get_tip_labels(),
        )
        fit_gamma_fixed = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=gamma_df,
            family="gamma",
            link="log",
            family_params={"dispersion": 0.5},
            lambda_=1.0,
        )
        self.assertEqual(fit_gamma_fixed.family, "gamma")
        self.assertFalse(fit_gamma_fixed.firth)
        self.assertEqual(fit_gamma_fixed.dispersion_params, {"dispersion": 0.5})
        self.assertFalse(fit_gamma_fixed.dispersion_estimated)
        self.assertTrue((fit_gamma_fixed.fitted_mean > 0).all())

        fit_gamma_est = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=gamma_df,
            family="gamma",
            link="log",
            lambda_=1.0,
        )
        self.assertEqual(fit_gamma_est.family, "gamma")
        self.assertFalse(fit_gamma_est.firth)
        self.assertIsNotNone(fit_gamma_est.dispersion_params)
        self.assertIn("dispersion", fit_gamma_est.dispersion_params)
        self.assertGreater(fit_gamma_est.dispersion_params["dispersion"], 0.0)
        self.assertTrue(fit_gamma_est.dispersion_estimated)

        with self.assertRaises(ToytreeError) as ctx:
            toytree.pcm.pglm(
                self.tree,
                "y ~ x",
                data=gamma_df,
                family="gamma",
                link="inverse",
                family_params={"dispersion": 0.5},
            )
        self.assertIn("not implemented", str(ctx.exception))
        with self.assertRaises(ToytreeError):
            toytree.pcm.pglm(
                self.tree,
                "y ~ x",
                data=gamma_df,
                family="gamma",
                link="log",
                family_params={"dispersion": -0.5},
            )
        gamma_bad = gamma_df.copy()
        gamma_bad.iloc[0, gamma_bad.columns.get_loc("y")] = 0.0
        with self.assertRaises(ToytreeError):
            toytree.pcm.pglm(
                self.tree,
                "y ~ x",
                data=gamma_bad,
                family="gamma",
                link="log",
                family_params={"dispersion": 0.5},
            )

        beta_df = pd.DataFrame(
            {
                "x": self.df["x"].values,
                "y": 0.1 + 0.8 * (np.arange(self.tree.ntips) / self.tree.ntips),
            },
            index=self.tree.get_tip_labels(),
        )
        fit_beta_fixed = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=beta_df,
            family="beta",
            link="logit",
            family_params={"phi": 20},
            lambda_=1.0,
        )
        self.assertEqual(fit_beta_fixed.family, "beta")
        self.assertFalse(fit_beta_fixed.firth)
        self.assertEqual(fit_beta_fixed.dispersion_params, {"phi": 20.0})
        self.assertFalse(fit_beta_fixed.dispersion_estimated)
        self.assertTrue(
            ((fit_beta_fixed.fitted_mean > 0) & (fit_beta_fixed.fitted_mean < 1)).all()
        )

        fit_beta_est = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=beta_df,
            family="beta",
            link="logit",
            lambda_=1.0,
        )
        self.assertEqual(fit_beta_est.family, "beta")
        self.assertFalse(fit_beta_est.firth)
        self.assertIsNotNone(fit_beta_est.dispersion_params)
        self.assertIn("phi", fit_beta_est.dispersion_params)
        self.assertGreater(fit_beta_est.dispersion_params["phi"], 0.0)
        self.assertTrue(fit_beta_est.dispersion_estimated)
        beta_bad = beta_df.copy()
        beta_bad.iloc[0, beta_bad.columns.get_loc("y")] = 1.0
        with self.assertRaises(ToytreeError):
            toytree.pcm.pglm(
                self.tree,
                "y ~ x",
                data=beta_bad,
                family="beta",
                link="logit",
                family_params={"phi": 20},
            )
        beta_bounds = beta_df.copy()
        beta_bounds.iloc[0, beta_bounds.columns.get_loc("y")] = 0.0
        beta_bounds.iloc[1, beta_bounds.columns.get_loc("y")] = 1.0
        with self.assertRaises(ToytreeError):
            toytree.pcm.pglm(
                self.tree,
                "y ~ x",
                data=beta_bounds,
                family="beta",
                link="logit",
                boundary="error",
                lambda_=1.0,
            )
        fit_beta_sq = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=beta_bounds,
            family="beta",
            link="logit",
            boundary="squeeze",
            lambda_=1.0,
        )
        self.assertTrue(fit_beta_sq.response_transform_applied)
        self.assertEqual(fit_beta_sq.response_transform, "beta_boundary_squeeze_sv")
        self.assertGreater(fit_beta_sq.response_transform_n, 0)
        self.assertTrue(
            ((fit_beta_sq.fitted_mean > 0) & (fit_beta_sq.fitted_mean < 1)).all()
        )
        with self.assertRaises(ToytreeError):
            toytree.pcm.pglm(
                self.tree,
                "y ~ x",
                data=self.df,
                family="poisson",
                link="log",
                boundary="squeeze",
            )

    def test_repr_and_html_repr(self):
        """Provide useful text and HTML representations."""
        fit = toytree.pcm.pglm(self.tree, "y ~ x", data=self.df, lambda_=1.0)
        txt = repr(fit)
        self.assertIn("PCMPGLMResult", txt)
        self.assertIn("family=binomial", txt)
        self.assertIn("lambda=", txt)
        self.assertIn("pseudo_R2=", txt)
        h = fit._repr_html_()
        self.assertIn("PCMPGLMResult", h)
        self.assertIn("<table", h)
        self.assertIn("Intercept", h)

        counts = pd.DataFrame(
            {"x": self.df["x"].values, "y": np.arange(self.tree.ntips) % 4},
            index=self.tree.get_tip_labels(),
        )
        nbfit = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=counts,
            family="negative_binomial",
            link="log",
            lambda_=1.0,
        )
        txt2 = repr(nbfit)
        self.assertIn("dispersion_params=", txt2)
        self.assertIn("dispersion_estimated=", txt2)
        h2 = nbfit._repr_html_()
        self.assertIn("dispersion_estimated", h2)

        gamma_df = pd.DataFrame(
            {"x": self.df["x"].values, "y": np.abs(self.df["x"].values) + 0.2},
            index=self.tree.get_tip_labels(),
        )
        gfit = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=gamma_df,
            family="gamma",
            link="log",
            lambda_=1.0,
        )
        gtxt = repr(gfit)
        self.assertIn("family=gamma", gtxt)
        self.assertIn("dispersion_params=", gtxt)
        self.assertIn("dispersion_estimated=", gtxt)

        beta_df = pd.DataFrame(
            {
                "x": self.df["x"].values,
                "y": 0.1 + 0.8 * (np.arange(self.tree.ntips) / self.tree.ntips),
            },
            index=self.tree.get_tip_labels(),
        )
        bfit = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=beta_df,
            family="beta",
            link="logit",
            lambda_=1.0,
        )
        btxt = repr(bfit)
        self.assertIn("family=beta", btxt)
        self.assertIn("dispersion_params=", btxt)
        self.assertIn("dispersion_estimated=", btxt)

        beta_bounds = beta_df.copy()
        beta_bounds.iloc[0, beta_bounds.columns.get_loc("y")] = 0.0
        beta_bounds.iloc[1, beta_bounds.columns.get_loc("y")] = 1.0
        bfit2 = toytree.pcm.pglm(
            self.tree,
            "y ~ x",
            data=beta_bounds,
            family="beta",
            link="logit",
            boundary="squeeze",
            lambda_=1.0,
        )
        btxt2 = repr(bfit2)
        self.assertIn("response_transform=", btxt2)
        self.assertIn("response_transform_n=", btxt2)
        h3 = bfit2._repr_html_()
        self.assertIn("response_transform", h3)
