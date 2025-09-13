#!/usr/bin/env python

"""...

Described in section "TRANSFORMATION OF BRANCH LENGTHS..." in Blomberg...


Given (tree, tip-traits) fit a model of the variance-covariance of
tips under an evolutionary model. 

- Brownian
- OU (one optimum)
- AC/DC

References
----------
Blomberg

"""

# from typing import Optional
from statsmodels.api import GLS
import pandas as pd
from toytree.core import ToyTree



def pgls(tree: ToyTree, formula: str = None, data: pd.DataFrame | None = None) -> "GLS":
    """Return a phylogenetic generalized least squares model fit to 
    two features on the tips of a tree.

    The GLS model is fit using `statsmodels.api.GLS` where the model
    formula is interpreted by `GLS.from_formula`. The formula should
    typically be `y ~ x` or `y ~ x - 1`. 

    Parameters
    ----------
    X: pd.DataFrame | np.ndarray | Sequence[float]
        Independent variables (2D array or pandas DataFrame).
    y: Sequence[float | str]
        Dependent variable (1D array or pandas Series)
    formula: str | None
        An optional str representation of the formula to fit. The trait
        names 
    
    Example
    -------
    >>> # simulate two traits on a tree under Brownian motion
    >>> tree = toytree.rtree.unittree(ntips=50)
    >>> traits = toytree.pcm.simulate_continuous_bm([1.0, 2.0], tips_only=True)
    >>> model = toytree.pcm.pgls(tree, "t0 ~ t1", traits)
    >>> print(model.summary())
    >>> print(model.params)
    >>> print(model.rsquared)
    """
    # get and validate data from tips
    # if isinstance(x, str):
    #     x = tree.get_node_data(x)[:tree.ntips]
    #     x = _validate_features(x, max_dim=1, size=tree.ntips)
    # if isinstance(y, str):
    #     y = tree.get_node_data(y)[:tree.ntips]
    #     y = _validate_features(y, max_dim=2, size=tree.ntips)

    # get covariance matrix
    vcv = tree.pcm.get_vcv_matrix_from_tree()

    # get data from tree if not provided as a dataframe
    if data is None:
        data = tree.get_node_data()

    # return phylogenetic least squares model fit
    gls_model = GLS.from_formula(formula, data=data, sigma=vcv)
    return gls_model.fit()


def pgls2():
    """
    

    fixed_effects: 
        Coefficients for const (intercept) and x.
    random_effects: 
        Variance components of the random intercept.
    """


def old_code():
    # ...
    ones = np.ones((ntips, 1))    
    ones_T_vcv_inv_ones = ones.T @ vcv_inv @ ones
    term2 = np.linalg.inv(ones_T_vcv_inv_ones) @ (ones.T @ vcv_inv @ x)
    pgls_resids = x - ones @ term2.T
    pgls_mse = np.mean(pgls_resids ** 2)
    
    logger.debug(f"phylogenetic trait mean: {pgls_mean}")
    logger.debug(f"phylogenetic mean sum-of-squares: {pgls_mse}")

    # get SS_cor: sum of squares of the tip data after correcting for
    # phylogeny (i.e., calculating phylogenetic trait mean)
    pgls_model = GLS(x, ones, sigma=vcv).fit()
    pgls_mean = pgls_model.params
    pgls_resids = pgls_model.resid
    pgls_mse = np.mean(pgls_resids ** 2)

    # get SS_obs: 
    # [1] as deviations from the phylogenetically corrected mean
    # if option:
    #     ols_resids = x - pgls_mean
    #     ols_mse = np.mean(ols_resids ** 2)        
    #     # pgls_mean2 = pgls_resids.T @ pgls_resids
    #     # logger.debug(f"OTHER {pgls_mean2} {pgls_model.params}")

    # # [2] as ordinary sum of squares around the (not phylo corrected) mean
    # else:
    #     ols_resids = x - x.mean()
    #     ols_mse = np.mean(ols_resids ** 2)

    ols_resids = x - x.mean()
    ols_mse = np.mean(ols_resids ** 2)

    # debug logging
    logger.debug(f"phylogenetic trait mean: {pgls_mean[0]}")
    logger.debug(f"phylogenetic mean sum-of-squares: {pgls_mse}")
    logger.debug(f"non-corrected trait mean: {x.mean()}")
    logger.debug(f"non-corrected mean sum-of-squares: {ols_mse}")

    # compute the expected ratio of SS_obs / SS_cor under an evolutionary
    # model (Brownian motion) to standardize K.
    vcv_inv = np.linalg.inv(vcv)
    trace_vcv = np.trace(vcv)
    ones_T_vcv_inv_ones = ones.T @ vcv_inv @ ones  # Compute (1ᵀ Ω⁻¹ 1)
    epsilon = (trace_vcv - (ones_T_vcv_inv_ones * (1 / ntips))) * (1 / (ntips - 1))
    epsilon = epsilon[0]

    logger.debug(f"ratio: {ols_mse} {pgls_mse} {ols_mse / pgls_mse}")
    logger.debug(f"epsilon: {epsilon}")
    return (ols_mse / pgls_mse) / epsilon


if __name__ == "__main__":

    import toytree

    # simulate data
    tree = toytree.rtree.unittree(ntips=25, treeheight=1.0, seed=123)
    traits = tree.pcm.simulate_continuous_bm(rates=[0.1, 0.001], seed=123, tips_only=True)

    # write data
    tree.write("/tmp/test.nwk")
    traits.to_csv("/tmp/test.csv")

    # ...
    print(traits)
    model = pgls(tree, "t0 ~ t1", data=traits)
    print(model.summary())


    # Generalized least squares fit by REML
    #   Model: t0 ~ t1
    #   Data: traits
    #         AIC       BIC   logLik
    #   -75.51482 -72.10834 40.75741

    # Correlation Structure: corBrownian
    #  Formula: ~1
    #  Parameter estimate(s):
    # numeric(0)

    # Coefficients:
    #                  Value Std.Error   t-value p-value
    # (Intercept)   0.015005  0.024507  0.612271  0.5464
    # t1          -10.787529 26.161921 -0.412337  0.6839

    #  Correlation:
    #    (Intr)
    # t1 0.31

    # Standardized residuals:
    #         Min          Q1         Med          Q3         Max
    # -1.46669581 -0.53812120  0.05030459  0.40130407  2.50647412

    # Residual standard error: 0.06278833
    # Degrees of freedom: 25 total; 23 residual    