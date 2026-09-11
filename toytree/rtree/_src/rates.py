"""Simulate molecular-rate variation on an existing time tree."""

from __future__ import annotations

from typing import Literal

import numpy as np

from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError

from ._utils import RNGSeed, get_rng, validate_real

RateModel = Literal["strict", "uncorrelated_lognormal", "autocorrelated_lognormal"]

__all__ = ["simulate_branch_rates"]


def _logarithmic_mean(left: float, right: float) -> float:
    """Return the logarithmic mean, with its equal-value limit."""
    log_left = np.log(left)
    log_right = np.log(right)
    difference = log_right - log_left
    if abs(difference) < 1e-12:
        return float(np.exp(0.5 * (log_left + log_right)))
    return float((right - left) / difference)


def simulate_branch_rates(
    tree: ToyTree,
    model: RateModel,
    mean_rate: float = 1.0,
    sigma: float | None = None,
    seed: RNGSeed = None,
) -> ToyTree:
    """Convert a time tree to a phylogram by simulating branch rates.

    Parameters
    ----------
    tree : ToyTree
        Input tree whose edge lengths are branch durations. Durations may use
        any consistent time unit and must be finite and nonnegative. A
        nonzero root distance is treated as an explicit stem duration. The
        input object is never modified and need not have contemporaneous tips.
    model : {"strict", "uncorrelated_lognormal", "autocorrelated_lognormal"}
        Branch-rate process. ``"strict"`` assigns one rate to every edge.
        ``"uncorrelated_lognormal"`` draws rates independently from a
        lognormal distribution with arithmetic mean ``mean_rate``.
        ``"autocorrelated_lognormal"`` evolves endpoint log rates by Brownian
        diffusion along elapsed time and uses the logarithmic mean of the two
        endpoint rates as the effective rate on each edge.
    mean_rate : float, default=1.0
        Positive expected rate in output-distance units per input-time unit.
        For the autocorrelated model this is the fixed rate at the root and
        the conditional arithmetic mean is preserved by the diffusion drift.
    sigma : float or None, optional
        Rate-dispersion parameter. It must be omitted for ``"strict"``. For
        ``"uncorrelated_lognormal"`` it is the dimensionless standard
        deviation of log edge rates. For ``"autocorrelated_lognormal"`` it is
        the log-rate diffusion standard deviation per square-root input-time
        unit. Both variable-rate models require a finite nonnegative value.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source. A supplied Generator is consumed in place. The
        strict model validates but does not consume random values.

    Returns
    -------
    ToyTree
        Independent copy of ``tree`` whose ``dist`` values equal
        ``time * rate``. Every node has ``time`` (the original branch
        duration), ``rate`` (the effective branch rate), and
        ``expected_substitutions`` (the new distance). A zero-duration root
        has zero output distance and rate ``mean_rate``. A nonzero root stem
        is simulated and converted like other branches. The autocorrelated
        model additionally stores ``start_rate`` and ``end_rate`` on every
        branch, including an explicit root stem.

    Raises
    ------
    ToytreeError
        If the model or its parameters are invalid, or any input branch
        duration is negative or nonfinite.

    Examples
    --------
    >>> timetree = toytree.rtree.unittree(20, treeheight=5.0, seed=123)
    >>> phylogram = toytree.rtree.simulate_branch_rates(
    ...     timetree,
    ...     model="uncorrelated_lognormal",
    ...     mean_rate=0.01,
    ...     sigma=0.5,
    ...     seed=123,
    ... )

    Notes
    -----
    Input branch lengths, including an optional root stem, are durations rather
    than expected substitutions per site.
    Output units are determined by ``mean_rate``; for example, a tree in Myr
    and a rate in substitutions/site/Myr produces distances in expected
    substitutions/site.

    Under the autocorrelated model, if parent and child endpoint rates are
    ``r0`` and ``r1``, the effective rate is ``(r1-r0)/(log(r1)-log(r0))``.
    This equals the exact average when log rate is interpolated linearly along
    the branch and has the continuous limit ``r0`` when endpoints are equal.
    """
    if not isinstance(tree, ToyTree):
        raise ToytreeError("tree must be a ToyTree instance.")
    if model not in {
        "strict",
        "uncorrelated_lognormal",
        "autocorrelated_lognormal",
    }:
        raise ToytreeError(
            "model must be 'strict', 'uncorrelated_lognormal', or "
            "'autocorrelated_lognormal'."
        )
    mean_rate = validate_real(mean_rate, "mean_rate", minimum=0, strict_minimum=True)
    if model == "strict":
        if sigma is not None:
            raise ToytreeError("sigma must be None under the strict model.")
        sigma_value = 0.0
    else:
        if sigma is None:
            raise ToytreeError(f"sigma is required under model={model!r}.")
        sigma_value = validate_real(sigma, "sigma", minimum=0)
    rng = get_rng(seed)

    result = tree.copy()
    branch_nodes = list(result)
    times = np.asarray([node.dist for node in branch_nodes], dtype=float)
    if np.any(~np.isfinite(times)) or np.any(times < 0):
        raise ToytreeError("all branch durations must be finite and >= 0.")

    if model == "strict":
        rates = np.full(len(branch_nodes), mean_rate, dtype=float)
    elif model == "uncorrelated_lognormal":
        log_mean = np.log(mean_rate) - 0.5 * sigma_value**2
        rates = np.empty(len(branch_nodes), dtype=float)
        nonroot_count = len(branch_nodes) - 1
        rates[:nonroot_count] = rng.lognormal(log_mean, sigma_value, size=nonroot_count)
        rates[result.treenode.idx] = (
            mean_rate
            if result.treenode.dist == 0
            else float(rng.lognormal(log_mean, sigma_value))
        )
    else:
        rates = np.empty(len(branch_nodes), dtype=float)
        root = result.treenode
        root_duration = float(root.dist)
        root_start_rate = mean_rate
        if root_duration == 0:
            root_end_rate = mean_rate
        else:
            root_log_end = (
                np.log(root_start_rate)
                - 0.5 * sigma_value**2 * root_duration
                + sigma_value * np.sqrt(root_duration) * float(rng.normal())
            )
            root_end_rate = float(np.exp(root_log_end))
        root.start_rate = root_start_rate
        root.end_rate = root_end_rate
        rates[root.idx] = _logarithmic_mean(root_start_rate, root_end_rate)
        endpoint_rates = {id(root): root_end_rate}
        for node in root.traverse("preorder"):
            if node.is_root():
                continue
            start_rate = endpoint_rates[id(node.up)]
            duration = float(node.dist)
            log_end = (
                np.log(start_rate)
                - 0.5 * sigma_value**2 * duration
                + sigma_value * np.sqrt(duration) * float(rng.normal())
            )
            end_rate = float(np.exp(log_end))
            node.start_rate = start_rate
            node.end_rate = end_rate
            endpoint_rates[id(node)] = end_rate
            rates[node.idx] = _logarithmic_mean(start_rate, end_rate)

    expected = times * rates
    for node, duration, rate, distance in zip(branch_nodes, times, rates, expected):
        node.time = float(duration)
        node.rate = float(rate)
        node.expected_substitutions = float(distance)
        node._dist = float(distance)
    result._update()
    return result
