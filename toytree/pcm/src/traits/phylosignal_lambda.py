#!/usr/bin/env python

"""Lambda metric to calculate phylogenetic signal in trait values.

Pagel's Lambda is used to quantify phylogenetic signal in trait
evolution...

A λ transformation multiplies all internal branches by a constant (λ)
while adjusting terminal edges to maintain the same constant height
from root to tips.

Example
-------
>>> tree = toytree.rtree.unittree(ntips=25, treeheight=1.0, seed=123)
>>> traits = tree.pcm.simulate_continuous_bm(rates=[0.1, 0.001], seed=123, tips_only=True)
>>> phylogenetic_signal_lambda(tree, traits.t0, traits.t1)
>>> # {'lambda': 1.095589, 'sig2': 0.004051, 'P-value': 0.041663, 'LR_test': 4.148850, ...}
"""

from typing import Union, Sequence
import numpy as np
from scipy.stats import chi2
from scipy.optimize import minimize_scalar, minimize
from toytree.core import ToyTree
from toytree.pcm import get_vcv_matrix_from_tree
from toytree.pcm.src.utils import _validate_features
from toytree.core.apis import add_subpackage_method, PhyloCompAPI

__all__ = [
    "phylogenetic_signal_lambda",
    # "max_λ",
    # "edges_scale_by_lambda"
]

@add_subpackage_method(PhyloCompAPI)
def phylogenetic_signal_lambda(
    tree: ToyTree,
    data: Union[str, Sequence[float]],
    error: Union[str, Sequence[float]] = None,
    intervals: int = 25,
) -> dict[str, float]:
    """Return Pagel's lambda measurement of phylogenetic signal.

    The lambda statistic ranges between 0 and 1 where ...

    Parameters
    ----------
    tree: ToyTree
        A tree with edge lengths.
    data: str | Sequence[float]
        Continuous trait values. 
    error: str | Sequence[float]
        Optional standard errors measured on trait values. 
    intervals: int
        Number of random start trials to optimize parameters by ML.

    Returns
    -------
    dict[str, float]
        A dict with keys: ["lambda", "P-value", "permutations"]. It can
        also include additional items if standard errors are included 
        which will estimate the variance parameter "sig2".

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=25, treeheight=1.0, seed=123)
    >>> traits = tree.pcm.simulate_continuous_bm(rates=[0.1, 0.001], seed=123, tips_only=True)
    >>> phylogenetic_signal_lambda(tree, traits.t0, traits.t1)
    >>> # {'lambda': 1.095589, 'sig2': 0.004051, 'P-value': 0.041663, 'LR_test': 4.148850, ...}
    """
    # [optional] get data as features from the tree
    if isinstance(data, str): 
        data = tree.get_node_data(data)[:tree.ntips]
    if isinstance(error, str):
        error = tree.get_node_data(error)[:tree.ntips]

    # validate proper trait format returned as float array
    x = _validate_features(data, max_dim=1, size=tree.ntips)
    if error is not None:
        e = _validate_features(error, max_dim=1, size=tree.ntips)        

    if error is None:
        return _phylogenetic_signal_λ(tree, x, intervals)
    else:
        return _phylogenetic_signal_λ_w_se(tree, x, e, intervals)


def _phylogenetic_signal_λ(tree: ToyTree, x: np.ndarray, intervals: int = 20) -> dict[str, float]:
    """Return Pagel's λ measurement of phylogenetic signal.

    See docstring in `phylogenetic_signal_lambda`.
    """
    # get ntips and the variance-covariance matrix from tree
    V = get_vcv_matrix_from_tree(tree)

    # estimate optimal λ that maximizes loglik
    maxλ = max_λ(tree)
    res = _estimate_λ(x, V, maxλ, intervals=intervals)
    λ = res.x
    λ_loglik = res.fun

    # calculate logLik at λ=0
    λ_0_loglik = _likelihood_λ(0.0, V, x)

    # likelihood-ratio test 
    lr_stat = -2 * (λ_loglik - λ_0_loglik)
    df_diff = 1
    pval = chi2.sf(lr_stat, df_diff)

    # return as a dict
    return {
        "lambda": λ,
        "P-value": pval,
        "LR_test": lr_stat,
        "log-likelihood_λ": λ_loglik,
        "log-likelihood_λ0": λ_0_loglik,
    }


def _phylogenetic_signal_λ_w_se(tree: ToyTree, x: np.ndarray, e: np.ndarray, intervals: int = 20) -> dict[str, float]:
    """Return Pagel's λ measurement of phylogenetic signal.

    See docstring in `phylogenetic_signal_lambda`.
    """
    # get ntips and the variance-covariance matrix from tree
    ntips = tree.ntips
    V = get_vcv_matrix_from_tree(tree)

    # validate proper trait format returned as float array
    x = _validate_features(x, max_dim=1, size=ntips)
    error = _validate_features(e, max_dim=1, size=ntips)

    # 
    E = np.diag(error ** 2)
    maxλ = max_λ(tree)

    # estimate optimal λ that maximizes loglik with measure error
    res = _estimate_λ_and_e(x, V, E, maxλ, intervals=intervals)
    λ, sigma2 = res.x
    λ_loglik = res.fun

    # calculate logLik at λ=0
    res = _estimate_λ_and_e(x, V, E, 1e-9, intervals=intervals)    
    λ_0_loglik = res.fun

    # likelihood-ratio test 
    lr_stat = -2 * (λ_loglik - λ_0_loglik)
    df_diff = 1
    pval = chi2.sf(lr_stat, df_diff)

    # return as a dict
    return {
        "lambda": λ,
        "P-value": pval,
        "LR_test": lr_stat,
        "log-likelihood_λ": λ_loglik,
        "log-likelihood_λ0": λ_0_loglik,
        "sig2": sigma2,
    }


def _λ_transform(V: np.ndarray, λ: float) -> np.ndarray:
    """Scale VCV by a lambda parameter (in place!)

    The internal edges (off-diagonals) are multipled by lambda, while
    the terminal edges are 
    """
    V = V.copy()
    mask = ~np.eye(V.shape[0], dtype=np.bool_)
    V[mask] *= λ
    return V


def _likelihood_λ(theta: float, V: np.ndarray, y: float) -> float:
    """Return -log likelihood given a test lambda parameter.

    Parameters
    ----------
    theta: np.ndarray
        A test value for the lambda parameter.
    V: np.ndarray
        The original variance-covariance matrix.
    y: np.ndarray
        The trait data in idx order.
    """
    # ...
    C = _λ_transform(V, theta)
    IC = np.linalg.inv(C)
    n = C.shape[0]
    a = np.sum(IC @ y) / np.sum(IC)

    # get rate
    term = (y - a)
    sig2 = (term.T @ IC @ term) / n

    # slogdet is more stable than det for large/small values; when sign>0,
    # log(det(V)) == logdet from slogdet
    sign, logdet = np.linalg.slogdet(C)
    logdet2 = logdet / 2. if sign > 0 else np.nan  # np.log(1e-12)

    # compute log-likelihood
    logL = (
        -term.T @ (1 / sig2 * IC) @ term / 2. - n * np.log(2 * np.pi) / 2. - logdet2
    )
    return -logL


def _likelihood_λ_w_se(params: tuple[float, float], V: np.ndarray, y: float, E: np.ndarray) -> float:
    """Return -log likelihood given a test lambda parameter.

    Parameters
    ----------
    theta: np.ndarray
        A test value for the lambda parameter.
    sigma: np.ndarray
        A test value for the error.
    V: np.ndarray
        The original variance-covariance matrix.
    y: np.ndarray
        The trait data in idx order.
    """
    # get lambda transformed V
    theta, sigma = params
    Cl = sigma * _λ_transform(V, theta)
    # get V with E
    V = Cl + E
    # invert it
    IC = np.linalg.inv(V)
    # 
    n = V.shape[0]
    a = np.sum(IC @ y) / np.sum(IC)
    # get rate
    term = (y - a)

    # get log determinant of variance covariance matrix
    # slogdet is more stable than det for large/small values; when sign>0,
    # log(det(V)) == logdet from slogdet
    sign, logdet = np.linalg.slogdet(V)
    logdet2 = logdet / 2. if sign > 0 else np.nan  # np.log(1e-12)

    det = np.linalg.det(V)
    if det <= 0:
        logdet2 = np.nan # np.log(1e-12)
    else:
        logdet2 = np.log(det) / 2.

    # compute log-likelihood
    logL = (
        -term.T @ IC @ term / 2. - n * np.log(2 * np.pi) / 2. - logdet2
    )
    return -logL


def _estimate_λ(x: np.ndarray, V: np.ndarray, maxλ: float, intervals: int) -> float:
    """Return best fitting λ estimated in intervals by ML.
    """
    # get intervals between 0-max(λ)
    ivals = np.linspace(0, maxλ, intervals)

    # get max λ in each interval
    lim = 1e-12
    fits = []
    for i, _ in enumerate(ivals[:-1]):
        start, stop = ivals[i] + lim, ivals[i + 1] - lim
        fit = minimize_scalar(
            _likelihood_λ,
            args=(V, x),
            bounds=(start, stop),
            method="bounded",
        )
        fits.append(fit)

    # return fit for interval with max loglik
    logliks = [i.fun for i in fits]
    lidx = logliks.index(min(logliks))
    return fits[lidx]


def _estimate_λ_and_e(x: np.ndarray, V: np.ndarray, E: np.ndarray, maxλ: float, intervals: int) -> float:
    """Return best fitting λ estimated in intervals by ML.
    """
    # get intervals between 0-max(λ)
    ivals = np.linspace(0, maxλ, intervals)

    # get max λ in each interval
    lim = 1e-12
    emean = np.mean(E)
    fits = []
    for i, _ in enumerate(ivals[:-1]):
        midλ = ivals[i:i + 1].mean()           
        fit = minimize(
            fun=_likelihood_λ_w_se,
            x0=np.array([midλ, emean]),
            args=(V, x, E),
            bounds=[(lim, maxλ - lim), (lim, np.inf)],
            method='L-BFGS-B',
        )
        fits.append(fit)

    # return fit for interval with max loglik
    logliks = [i.fun for i in fits]
    lidx = logliks.index(min(logliks))
    return fits[lidx]


####################################################################
def max_λ(tree: ToyTree) -> float:
    """Return the max lambda for a given tree.

    The max value is a >1 lambda value at which the new internal 
    node dists contain a dist value that leaves no room for a tip
    (untransformed) edge to still be positive, creating a neg. edge.
    """
    root_to_tip_dists = tree.distance.get_node_distance_matrix()[-1]
    internal_dists = root_to_tip_dists[tree.ntips:]
    return tree.treenode.height / max(internal_dists)    


def edges_transform_lambda(tree: ToyTree, λ: float, inplace: bool = False) -> ToyTree:
    """Return tree with transformed by Pagel's lambda.

    All internal edge lengths are multiplied by lambda and tip edge
    lengths are extended to maintain their original distance from the
    tree root.
    """
    # select tree or copy
    tree = tree if inplace else tree.copy()

    # get node distances on the orig tree
    dists1 = tree.distance.get_node_distance_matrix()[-1]

    # multiply internal edges by lambda
    for node in tree[tree.ntips:]:
        node._dist *= λ

    # get node distances on new transformed tree
    dists2 = tree.distance.get_node_distance_matrix()[-1]

    # extend tips to original distance from root
    for node in tree[:tree.ntips]:
        node._dist += dists1[node._idx] - dists2[node._idx]

    # update new tree heights
    tree._update()
    return tree



if __name__ == "__main__":

    import toytree

    # generate test data
    tree = toytree.rtree.unittree(ntips=50, treeheight=1.0, seed=123)
    traits = tree.pcm.simulate_continuous_bm(1.0, seed=123, tips_only=True)
    traits["se"] = np.random.default_rng(seed=123).uniform(0, 0.01, tree.ntips)

    # write data
    tree.write("/tmp/test.nwk")
    traits.to_csv("/tmp/test.csv")

    res = phylogenetic_signal_lambda(tree, traits.t0)
    print(res)
    res = phylogenetic_signal_lambda(tree, traits.t0, traits.se, intervals=20)
    print(res)
    res = phylogenetic_signal_lambda(tree, traits.se, intervals=20)
    print(res)
    # res = phylogenetic_signal_lambda(tree, traits.se, traits.se, intervals=25)
    # print(res)

    # maxλ = max_λ(tree)
    # V = tree.pcm.get_vcv_matrix_from_tree()
    # x = traits.t0
    # E = traits.t1.values ** 2
    # print(_likelihood_λ(0.9, V, x))
    # print(_likelihood_λ_w_se((0.9, 0.1), V, x, E))
    # print(_likelihood_λ_w_se((0.9, 0.01), V, x, E))
    # print(_likelihood_λ_w_se((0.94, 0.003), V, x, E))
    # print(_likelihood_λ_w_se((1.096, 4.05e-3), V, x, E))


#### t0
# Phylogenetic signal lambda : 1.0174
# logL(lambda) : 81.0235
# LR(lambda=0) : 7.51733
# P-value (based on LR test) : 0.00611082

#### t1
# Phylogenetic signal lambda : 1.06847
# logL(lambda) : 204.894
# LR(lambda=0) : 11.2749
# P-value (based on LR test) : 0.000785623
