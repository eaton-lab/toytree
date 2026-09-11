"""Shared tree and branch-rate generators for current validation studies."""

from typing import Any

import numpy as np

import toytree
from toytree.core import ToyTree


def _edge_array(tree: ToyTree) -> np.ndarray:
    return np.asarray(tree.get_edges("idx"), dtype=int)


def _scale_true_tree(ntips: int, seed: int) -> ToyTree:
    tree = toytree.rtree.bdtree(ntips=ntips, b=1.0, d=0.2, seed=seed)
    root = tree.treenode
    while root.up is not None:
        root = root.up
    tree = ToyTree(root).mod.remove_unary_nodes()
    return tree.mod.edges_scale_to_root_height(1.0)


def _simulate_rates(
    tree: ToyTree,
    model: str,
    rng: np.random.Generator,
    simulation: dict[str, Any],
) -> np.ndarray:
    edges = _edge_array(tree)
    nedges = edges.shape[0]
    baseline = float(simulation["baseline_rate"])
    if model == "clock":
        return np.repeat(baseline, nedges)
    if model == "discrete":
        multipliers = np.asarray(simulation["discrete_multipliers"], dtype=float)
        return baseline * rng.choice(multipliers, size=nedges)
    if model == "uncorrelated_lognormal":
        sigma = float(simulation["uncorrelated_log_sigma"])
        values = rng.normal(0.0, sigma, size=nedges)
        return baseline * np.exp(values - values.mean())
    if model != "correlated":
        raise ValueError(f"unsupported simulation model: {model!r}")
    sigma = float(simulation["correlated_log_sigma"])
    child_to_edge = {int(child): eidx for eidx, (child, _) in enumerate(edges)}
    log_rates = np.full(nedges, np.log(baseline), dtype=float)
    for node in tree.treenode.traverse("preorder"):
        if node.is_root():
            continue
        eidx = child_to_edge[node.idx]
        parent_edge = child_to_edge.get(node.up.idx)
        center = np.log(baseline) if parent_edge is None else log_rates[parent_edge]
        log_rates[eidx] = center + rng.normal(0.0, sigma)
    log_rates -= log_rates.mean() - np.log(baseline)
    return np.exp(log_rates)
