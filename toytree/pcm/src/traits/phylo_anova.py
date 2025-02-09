#!/usr/bin/env python

"""Phylogenetic ANOVA

TODO
----
This module is intended for the development of phylogenetic generalized
least squares (PGLS) methods, including a phylogenetic ANOVA. Some
pseudo-code is written but this is IN DEVELOPMENT, and not yet 
intended for use.

References
-----------
__Adams, D. C., & Collyer, M. L. (2018). Phylogenetic ANOVA: group-clade 
aggregation, biological challenges, and a refined permutation procedure.
Evolution, 72(6), 1204-1215.__

"""

from typing import Sequence
import numpy as np
from toytree.core import ToyTree


def anova(values: Sequence[float], groups: Sequence[str]) -> dict[str, float]:
    """Perform a one-way analysis of variance (ANOVA).

    ANOVA is typically used to test for differences in means across
    different groups or treatments. It compares the variance within
    groups to the variance between groups to determine if group means
    are significantly different. This method calls the scipy.stats 
    function `f_oneway` to run a one-way ANOVA.

    Parameters
    ----------
    values: Sequence[float]
        A Sequence (e.g., list, np.ndarray, pd.Series) of quantitative
        values to be analyzed.
    groups: Sequence[str]
        A Sequence (e.g., list, np.ndarray, pd.Series) of categorical
        group assignments for each value.

    Example
    -------
    >>> rng = np.random.default_rng(124)
    >>> values = rng.normal([1, 2, 3], [2, 2, 2], size=(100, 3)).flatten("F")
    >>> groups = np.repeat([1, 2, 3], 100)
    >>> anova(values, groups)
    >>> # {'F-statistic': 33.348302, 'p-value': 8.601108e-14}
    """
    from scipy.stats import f_oneway
    values = np.array(values)
    groups = np.array(groups)
    keys = set(groups)
    grouped_data = [values[groups == i] for i in keys]
    f_stat, p_value = f_oneway(*grouped_data)
    return {"F-statistic": f_stat, "p-value": p_value}


def phylogenetic_anova(trait: Sequence[float], group: Sequence[str], tree: ToyTree) -> dict[str, float]:
    """Generalized Least Squares...

    ANOVA is typically used to test for differences in means across
    different groups or treatments. It compares the variance within
    groups to the variance between groups to determine if group means
    are significantly different. When the groups are related by a
    phylogeny, it is necessary to control for the fact that some are
    expected to be more similar to each other than others. This is
    the goal of a phylogenetic ANOVA. 

    This method calls the scipy.stats 
    function `f_oneway` to run a one-way ANOVA.

    "How is the variation in a trait between different species 
    explained by their evolutionary history?"

    Look at that statistical significance of differences between groups.
    The null hypothesis is that there are no differences; the alternative
    hypothesis is that one or more groups differs from the others even
    after accounting for phylogeny. The key outputs are an F-statistic
    and p-value. The F-statistic measures variation _between-groups_ 
    relative to variation _within-groups_. Larger values indicates
    larger relative differences between groups. The p-value tests the
    null hypothesis that there is no difference.


    """
    # check that all 'group' categories are represented in the tree
    assert set(tree.get_tip_labels()) == set(group), "Mismatch between tree and 'groups' (species)"

    # get phylogenetic variance-covariance matrix
    # raise warning if tree is not ultrametic?


def phylogenetic_generalized_least_squares(values: Sequence[float], groups: Sequence[float], tree: ToyTree) -> dict[str, float]:
    """Returns a ... result of a phylogenetic generalized least squares
    analysis.

    Generalized least squares is used to model data where the errors
    are not independent and identically distributed (i.i.d.). GLS 
    allows for the modeling of heteroscedasticity (unequal variance) 
    and autocorrelation (dependence between error terms). When the
    values being modeled evolved on a phylogeny the variance-covariance
    matrix can be used to model the error structure.

    A GLS model accounts for phylogenetic non-independence by 
    incorporating the variance-covariance structure from the tree.

    DevNotes
    --------
    This is an implementation in progress where we are trying to 
    implement PGLS using only scipy and not statsmodels.

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=10)
    >>> values = tree.pcm.simulate_continuous_brownian(1.0, tips_only=True)
    >>> groups = tree.get_tip_labels()
    >>> phylogenetic_generalized_least_squares(values, groups, tree)
    >>> # 
    """
    from scipy.linalg import inv
    from pandas import get_dummies    

    # The response variable (e.g., trait value)
    y = np.array(values)

    # Group data
    groups = np.array(groups)
    keys = set(groups)

    # check that tree tips match groups
    assert set(tree.get_tip_labels()) == keys, "Mismatch between tree and 'groups' (species)"

    # The design matrix (e.g., intercept + group dummy variables)
    X = get_dummies(groups, drop_first=True).values

    # Covariance matrix (phylogenetic covariance)
    Sigma = tree.pcm.get_corr_matrix_from_tree()

    # Compute the inverse of the covariance matrix
    Sigma_inv = inv(Sigma)

    # Calculate (X^T Σ^(-1) X)
    XT_Sigma_inv_X = X.T @ Sigma_inv @ X

    # Calculate (X^T Σ^(-1) y)
    XT_Sigma_inv_y = X.T @ Sigma_inv @ y

    # GLS solution for beta (coefficients)
    # These represent the estimated effect of each predictor (species), accounting for phylogeny.
    beta = np.linalg.inv(XT_Sigma_inv_X) @ XT_Sigma_inv_y
    print("GLS Coefficients (Beta):\n", beta)

    # Predicted values
    y_pred = X @ beta

    # Residuals
    residuals = y - y_pred

    # Weighted residual sum of squares
    # Residual Sum of Squares is how well the model fits the data after incorporating the covariance structure.
    rss = residuals.T @ Sigma_inv @ residuals
    print("Weighted Residual Sum of Squares:\n", rss)

    # Variance-covariance matrix of coefficients
    # Used to compute confidence intervals and p-values for the coefficients.
    beta_var = np.linalg.inv(XT_Sigma_inv_X)
    print("Variance-Covariance Matrix of Beta:\n", beta_var)

    # Standard errors of coefficients
    # Quantify uncertainty around the estimated coefficients
    beta_se = np.sqrt(np.diag(beta_var))
    print("Standard Errors of Coefficients:\n", beta_se)

    # To calculate p-values for the coefficients using a t-test:
    from scipy.stats import t

    # Degrees of freedom
    n, p = X.shape
    df = n - p

    # t-values
    t_values = beta / beta_se

    # Two-tailed p-values
    p_values = 2 * t.sf(np.abs(t_values), df)
    print("t-values:\n", t_values)
    print("p-values:\n", p_values)



def test_R_gls():
    """Compare results to a pgls in R ...
    """





if __name__ == "__main__":

    import toytree

    # standard ANOVA
    rng = np.random.default_rng(124)
    values = rng.normal([1, 2, 3], [2, 2, 2], size=(100, 3)).flatten("F")
    groups = np.repeat([1, 2, 3], 100)
    result = anova(values, groups)
    # print(result)

    # phylogenetic ANOVA    


    # phylogenetic GLS
    tree = toytree.rtree.unittree(6, treeheight=2, seed=123)
    tree.treenode.draw_ascii()
    traits = tree.pcm.simulate_continuous_brownian(1.0, tips_only=True)
    print(traits)
    groups = tree.get_tip_labels()
    # vcv = tree.pcm.get_vcv_matrix_from_tree(df=True)
    phylogenetic_generalized_least_squares(traits, groups, tree)
