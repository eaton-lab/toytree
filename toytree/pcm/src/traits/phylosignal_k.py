#!/usr/bin/env python

"""Metrics to calculate phylogenetic signal in trait values.

Blomberg's K is used to quantify phylogenetic signal relative in trait
evolution relative to a Brownian motion model. Values of K>1 indicate
samples are less similar than expected, whereas K<1 indicates that they
are more similar than expected. Permutations can be used to perform
a significance test.

Example
-------
>>> tree = toytree.rtree.unittree(ntips=24, seed=123)
>>> trait = tree.pcm.simulate_continuous_brownian([1.0], tips_only=True, seed=123)
>>> kstat = phylogenetic_signal_k(tree=tree, data=trait, test=True)
>>> # {'K': 0.9857885, 'P-value': 0.002, 'permutations': 1000}

References
----------
The original description of the K statistic:  
__Blomberg, S. P., T. Garland Jr., and A. R. Ives (2003) Testing for
phylogenetic signal in comparative data: Behavioral traits are more
labile. Evolution, *57*, 717-745.__

Extension to conduct hypothesis tests and incorporate sampling error:  
__Ives, A. R., P. E. Midford, and T. Garland Jr. (2007) Within-species
variation and measurement error in phylogenetic comparative biology.
Systematic Biology, *56*, 252-270.__

Extension to multivariate measure of K:
__Dean C. Adams, A Generalized K Statistic for Estimating Phylogenetic 
Signal from Shape and Other High-Dimensional Multivariate Data, 
Systematic Biology, Volume 63, Issue 5, September 2014, Pages 685–697, 
https://doi.org/10.1093/sysbio/syu030__

__Philipp Mitteroecker, Michael L Collyer, Dean C Adams, Exploring Phylogenetic
Signal in Multivariate Phenotypes by Maximizing Blomberg’s K, Systematic 
Biology, 2024;, syae035, https://doi.org/10.1093/sysbio/syae035__

__Adams, D. C. (2014). A generalized K statistic for estimating 
phylogenetic signal from shape and other high-dimensional multivariate
data. Systematic biology, 63(5), 685-697.__
"""


from typing import Union, Sequence
import numpy as np
import pandas as pd
from toytree.core import ToyTree
from toytree.pcm import get_vcv_matrix_from_tree
from scipy.optimize import minimize_scalar
from loguru import logger


logger = logger.bind(name="toytree")
feature = Union[str, Sequence[float], pd.Series, pd.DataFrame]
__all__ = ["phylogenetic_signal_k"]


def _validate_features(x: feature, max_dim: int, size: int) -> np.ndarray:
    """Validate data has correct dimensions and size."""
    # if DataFrame w/ only 1 column convert to Series
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 1:
            x = x.iloc[:, 0]
    # force to array
    x = np.asarray(x)
    # check dimensions and size
    assert x.ndim <= max_dim, f"feature ndim ({x.ndim}) exceeds max allowed ndim ({max_dim})."
    assert x.shape[0] == size, "feature cannot exceed ntips"
    return x


def phylogenetic_signal_k(
    tree: ToyTree,
    data: Union[str, Sequence[float]],
    error: Union[str, Sequence[float]] = None,
    test: bool = False,
    permutations: int = 1000,
) -> dict[str, float]:
    """Return Blomberg's K measurement of phylogenetic signal.

    The K statistic is standardized by the expectation under the
    Brownian motion model of evolution so that K<1 indicates that
    relatives resemble each other less than expected under the model
    (perhaps due to adaptive evolution); whereas K>1 indicates that
    close relatives are more similar than expected under the model.

    Parameters
    ----------
    tree: ToyTree
        A tree with edge lengths.
    data: str | Sequence[float]
        Continuous trait values. 
    error: str | Sequence[float]
        Optional standard errors measured on trait values. 
    test: bool
        Perform permutation test for significance.
    permutations: int
        Number of permutations to perform if testing significance.

    Returns
    -------
    dict[str, float]
        A dict with keys: ["K", "P-value", "permutations"]. It can also
        include additional items if standard errors are included which
        will estimate the variance parameter "sig2".

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=10, seed=123, treeheight=2.0)
    >>> data = tree.pcm.simulate_continuous_bm(1.0, tips_only=True)
    >>> tree.pcm.phylogenetic_signal_k(tree, data)
    >>> # {"K": ..., "P-value": ..., ...}
    """
    if error is None:
        return _phylogenetic_signal_k(tree, data, None, test, permutations)
    else:
        return _phylogenetic_signal_k_with_se(tree, data, error, test, permutations)


def _phylogenetic_signal_k(
    tree: ToyTree,
    data: Union[str, Sequence[float]],
    error: Union[str, Sequence[float]] = None,
    test: bool = False,
    permutations: int = 1000,
) -> dict[str, float]:
    """Return Blomberg's K measurement of phylogenetic signal.

    See docstring in `phylogenetic_signal_k`.
    """
    # get ntips and the variance-covariance matrix from tree
    ntips = tree.ntips
    V = get_vcv_matrix_from_tree(tree)

    # [optional] get data as features from the tree
    if isinstance(data, str):
        data = tree.get_node_data(data)[:ntips]
    if isinstance(error, str):
        error = tree.get_node_data(error)[:ntips]
    if error is None:
        error = np.repeat(np.nan, ntips)

    # validate proper trait format returned as float array
    x = _validate_features(data, max_dim=1, size=tree.ntips)    

    # calculate K statistic
    kstat = _calculate_k(x, V)

    # [optional] permutation test
    if test:
        pval = _permutation_test_k(permutations, x, V, kstat)

    # return as a dict
    return {
        "K": kstat,
        "P-value": np.nan if not test else pval,
        "permutations": np.nan if not test else permutations,
    }


def _calculate_k(x, V, IV = None) -> float:
    """Return K statistic calculated for data x and variance-covariance
    matrix V."""
    # compute PGLS mean (root state)
    n = x.size
    IV = IV if IV is not None else np.linalg.inv(V)
    a = np.sum(IV @ x) / np.sum(IV)

    # calculate K statistic
    num = ((x - a).T @ (x - a) / ((x - a).T @ IV @ (x - a)))
    dnm = ((np.sum(V.diagonal()) - n / np.sum(IV)) / (n - 1))
    return num / dnm


def _permutation_test_k(size: int, x: np.ndarray, V: np.ndarray, k: float):
    """Return p-value from permutations as a test statistic. 
    """
    kstats = np.zeros(size)
    rng = np.random.default_rng()
    for i in range(size):
        _x = rng.choice(x, size=x.size, replace=False)
        kstats[i] = _calculate_k(_x, V)

    # the proportion of permutations w/ k_ > k
    return np.sum(kstats >= k) / kstats.size


def _calculate_k_with_se(x: np.ndarray, V: np.ndarray, IV: np.ndarray, E: np.ndarray) -> tuple[float, float]:
    """
    """
    # start using no error vcv
    a = np.sum(IV @ x) / np.sum(IV)
    n = x.size

    # constrain optimization by setting a max on sigma2
    term = x - a
    max_sig2 = (term.T @ IV @ term) / n

    # maximum likelihood model fitting
    estimate = minimize_scalar(
        _likelihood,
        args=(V, E, x),
        bounds=(0, max_sig2),
        method="bounded",
        # options=dict(maxiter=1000, xatol=1e-10, disp=0),
    )
    model_fit = {
        "optimum": estimate.x,
        "LogLik": estimate.fun,
        "convergence": estimate.success,
    }
    # logger.debug(estimate)
    # logger.debug(f"\n{pd.Series(model_fit)}")

    # get rate parameter
    sig2 = model_fit["optimum"] * (n / (n - 1))

    # get VCV w/ rate scalar
    Ve = sig2 * V + E

    # calculate K using optimized Ve
    IVe = np.linalg.inv(Ve)
    a = np.sum(IVe @ x) / np.sum(IVe)
    num = ((x - a).T @ (x - a) / ((x - a).T @ IVe @ (x - a)))
    dnm = ((np.sum(Ve.diagonal()) - n / np.sum(IVe)) / (n - 1))
    return num / dnm, sig2, model_fit["LogLik"], model_fit["convergence"]


def _permutation_test_k_with_se(size: int, x: np.ndarray, V: np.ndarray, IV: np.ndarray, error: np.ndarray, k: float):
    """Return p-value from permutations as a test statistic. 
    """
    kstats = np.zeros(size)
    rng = np.random.default_rng()
    for i in range(size):
        order = rng.choice(range(x.size), size=x.size, replace=False)
        _x = x[order]
        _e = error[order]
        _E = np.diag(_e ** 2)
        kstats[i], _, _, _ = _calculate_k_with_se(_x, V, IV, _E)

    # the proportion of permutations w/ k_ > k
    return np.sum(kstats >= k) / kstats.size


def _phylogenetic_signal_k_with_se(
    tree: ToyTree,
    data: Union[str, Sequence[float]],
    error: Union[str, Sequence[float]] = None,
    test: bool = False,
    permutations: int = 1000,
) -> dict[str, float]:
    """Calculate phylogenetic signal (K) with measurement error.

    This involves fitting a ML model to estimate the rate ...
    """
    # get ntips and the variance-covariance matrix from tree
    ntips = tree.ntips
    V = get_vcv_matrix_from_tree(tree)

    # [optional] get data as features from the tree
    if isinstance(data, str):
        data = tree.get_node_data(data)[:ntips]
    if isinstance(error, str):
        error = tree.get_node_data(error)[:ntips]
    if error is None:
        error = np.repeat(0.0, ntips)

    # validate proper trait format returned as float array
    x = _validate_features(data, max_dim=1, size=ntips)
    error = _validate_features(error, max_dim=1, size=ntips)

    # calculate K stat w/ error
    IV = np.linalg.inv(V)    
    E = np.diag(error ** 2)
    kstat, sig2, loglik, conv = _calculate_k_with_se(x, V, IV, E)
    loglik = _likelihood(sig2, V, E, x)

    # [optional] permutation test statistic
    if test:
        pval = _permutation_test_k_with_se(permutations, x, V, IV, error, kstat)

    # return as a dict
    return {
        "K": kstat, 
        "P-value": np.nan if not test else pval,
        "permutations": 0 if not test else permutations,
        "log-likelihood": -loglik,
        "sig2": sig2,
        "convergence": conv,
    }


def _likelihood(theta: float, V: np.ndarray, E: np.ndarray, y: np.ndarray) -> float:
    """Estimate theta by maximizing the likelihood.
    """
    # weight variances by theta and add Error variance
    C = theta * V + E

    # get pgls mean
    IC = np.linalg.inv(C)
    n = y.size
    a = np.sum(IC @ y) / np.sum(IC)

    # get log determinant of variance covariance matrix
    det = np.linalg.det(C)
    if det <= 0:
        logdet2 = np.nan # np.log(1e-12)
    else:
        logdet2 = np.log(det) / 2.

    # compute log likelihood
    term = (y - a)
    logL = (
        -term.T @ IC @ term / 2. - n * np.log(2 * np.pi) / 2. - logdet2
    )
    # print(theta, -logL)
    return -logL        




if __name__ == "__main__":

    import toytree
    toytree.set_log_level("DEBUG")

    # generate test data
    tree = toytree.rtree.unittree(ntips=50, treeheight=10., seed=123)
    tree.pcm.simulate_continuous_bm(
        rates=[5.0, 0.5], tips_only=True, seed=123, inplace=True
    )

    # get K
    # k = _phylogenetic_signal_k(tree=tree, data="t0", test=True)
    # logger.info(k)

    # get K w/ Error
    k = _phylogenetic_signal_k_with_se(tree=tree, data="t0", error="t1", test=0)
    logger.info(k)
    help(phylogenetic_signal_k)