#!/usr/bin/env python

"""Phylogenetic independent contrasts for continuous traits.

Examples
--------
>>> # The example in Phylip 3.5c (originally from Lynch 1991)
>>> NWK = "((((Homo:0.21,Pongo:0.21):0.28,Macaca:0.49):0.13,Ateles:0.62):0.38,Galago:1.00);"
>>> TREE = toytree.tree(NWK)
>>> NAMES = ["Homo", "Pongo", "Macaca", "Ateles", "Galago"]
>>> TREE.set_node_data("X", dict(zip(NAMES, [4.09434, 3.61092, 2.37024, 2.02815, -1.46968])), inplace=True)
>>> TREE.set_node_data("Y", dict(zip(NAMES, [4.09434, 3.61092, 2.37024, 2.02815, -1.46968])), inplace=True)
>>>
>>> # get pic's
>>> pic_x = get_phylogenetic_independent_contrasts(TREE, "X")
>>> pic_y = get_phylogenetic_independent_contrasts(TREE, "Y")
>>> 
>>> # fit linear model to contrasts through the origin
>>> import statsmodels.api as sm
>>> traits = ...
>>> sm.OLS.from_model("Y ~ X - 1", Y=pic_y, X=pic_x).summary()
>>> # 0.4319
>>> sm.OLS.from_model("X ~ Y - 1", Y=pic_y, X=pic_x).summary()
>>> # 0.998

References
----------
Felsenstein, J. (1985) Phylogenies and the comparative method.
_American Naturalist_, *125*, 1-15.

ape:::pic
"""

from typing import Dict, List, Tuple, Union
import numpy as np
import pandas as pd
from toytree.core import ToyTree
from toytree.core.apis import add_subpackage_method, PhyloCompAPI


trait_t = Union[str, pd.Series]
__all__ = [
    "get_phylogenetic_independent_contrasts",
    "get_ancestral_states_pic",
]


@add_subpackage_method(PhyloCompAPI)
def get_phylogenetic_independent_contrasts(
    tree: ToyTree,
    trait: trait_t,
    epsilon: float = 1e-12,
) -> pd.DataFrame:
    """Return standardized PICs and ancestral estimates in long format.

    Independent contrasts are calculated for every internal node
    of a tree for a selected continuous feature (trait)
    under a Brownian motion model of evolution.

    Parameters
    ----------
    trait: str | pandas.Series
        Trait values as a feature name stored on the tree, or a Series
        indexed by tip names and / or tip idx labels.
    epsilon: float
        Small positive floor used to stabilize variance terms when
        branch lengths are zero or near-zero.

    Returns
    -------
    pandas.DataFrame
        One row per independent contrast with columns:
        `node`, `contrast_id`, `anc`, `anc_var`, `contrast_raw`,
        `contrast_var`, and `contrast` (standardized).

        `contrast_id` is the within-node contrast index. For bifurcating
        nodes there is one contrast and `contrast_id` is always 0. For
        a polytomy with `k` children there are `k - 1` contrasts with
        `contrast_id` values `0..k-2`.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=10, treeheight=1)
    >>> tree.pcm.simulate_continuous_bm({"trait": 1.0}, inplace=True)
    >>> pics = toytree.pcm.get_phylogenetic_independent_contrasts(tree, trait="trait")
    """
    if epsilon <= 0:
        raise ValueError("epsilon must be > 0")
    trait_name, tip_map = _normalize_trait_to_tip_map(tree, trait)
    rows, _ = _compute_pic(tree, tip_map, epsilon)
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(
            columns=["node", "contrast_id", "anc", "anc_var", "contrast_raw", "contrast_var", "contrast"]
        )
    df = df.sort_values(["node", "contrast_id"]).reset_index(drop=True)
    df.attrs["trait"] = trait_name
    return df


@add_subpackage_method(PhyloCompAPI)
def get_ancestral_states_pic(
    tree: ToyTree,
    trait: trait_t,
    inplace: bool = False,
    epsilon: float = 1e-12,
) -> pd.Series:
    """Return trait with ancestral states inferred at internal nodes.

    Trait must be continuous without missing value for tip nodes.

    Parameters
    ----------
    tree: ToyTree
        A tree with branch lengths.
    trait: str | pandas.Series
        Trait as a feature name or a Series indexed by tip names and / or
        tip idx labels.
    inplace: bool
        If True, inferred states are stored on the input tree under the
        feature name `{trait}_anc`. In all cases this function returns
        a pandas Series with that same name.
    epsilon: float
        Small positive floor used to stabilize variance terms when
        branch lengths are zero or near-zero.

    See Also
    --------
    `get_ancestral_state_pgls`

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=10, treeheight=1.0)
    >>> tree.pcm.simulate_continuous_bm({"X": 1.0}, tips_only=True, inplace=True)
    >>> anc = tree.pcm.get_ancestral_states_pic(trait="X", inplace=True)
    >>> print(tree.get_node_data("X_anc"))
    """
    if epsilon <= 0:
        raise ValueError("epsilon must be > 0")
    trait_name, tip_map = _normalize_trait_to_tip_map(tree, trait)
    _, anc_by_idx = _compute_pic(tree, tip_map, epsilon)

    if isinstance(trait, str):
        values = tree.get_node_data(trait_name, missing=float("nan"))
        values = values.reindex(range(tree.nnodes)).astype(float).copy()
    else:
        values = pd.Series(np.nan, index=range(tree.nnodes), name=trait_name, dtype=float)
        for idx in range(tree.ntips):
            node = tree[idx]
            if idx in trait.index:
                values.loc[idx] = float(trait.loc[idx])
            elif node.name in trait.index:
                values.loc[idx] = float(trait.loc[node.name])
    for nidx, anc in anc_by_idx.items():
        values.loc[nidx] = anc
    anc_feature = f"{trait_name}_anc"
    values.name = anc_feature

    if inplace:
        tree.set_node_data(anc_feature, values, inplace=True)
    return values


def _normalize_trait_to_tip_map(tree: ToyTree, trait: trait_t) -> Tuple[str, Dict[str, float]]:
    """Return (trait_name, {tip_name: float_value}) with input validation."""
    if isinstance(trait, str):
        trait_name = trait
        series = tree.get_node_data(trait_name, missing=float("nan"))
    elif isinstance(trait, pd.Series):
        trait_name = trait.name if trait.name else "trait"
        series = trait.copy()
    else:
        raise TypeError("trait must be a str feature name or pandas.Series")

    tip_map: Dict[str, float] = {}
    tip_names = tree.get_tip_labels()
    for idx in range(tree.ntips):
        node = tree[idx]
        value = np.nan
        if idx in series.index:
            value = series.loc[idx]
        elif node.name in series.index:
            value = series.loc[node.name]
        if pd.isna(value):
            raise ValueError(f"missing trait value for tip '{node.name}' (idx={idx})")
        try:
            value = float(value)
        except Exception as exc:
            raise TypeError(f"trait values must be numeric; failed at tip '{node.name}'") from exc
        if not np.isfinite(value):
            raise ValueError(f"trait value for tip '{node.name}' is not finite")
        tip_map[node.name] = value

    # keep explicit check so error is clear if tip labels are weird / duplicated
    if len(tip_map) != len(tip_names):
        raise ValueError("could not map trait values to all unique tip names")
    return trait_name, tip_map


def _safe_var(value: float, epsilon: float) -> float:
    """Return variance clamped to a positive floor for stability."""
    return value if value > epsilon else epsilon


def _compute_pic(
    tree: ToyTree,
    tip_map: Dict[str, float],
    epsilon: float,
) -> Tuple[List[dict], Dict[int, float]]:
    """Compute PIC rows and ancestral states for all internal nodes."""
    rows: List[dict] = []
    anc_by_idx: Dict[int, float] = {}

    def recurse(node) -> Tuple[float, float]:
        # leaf: return observed trait and variance contribution to parent.
        if not node.children:
            x = tip_map[node.name]
            v = _safe_var(float(node.dist), epsilon)
            return x, v

        child_pairs = [recurse(child) for child in node.children]
        means = np.array([i[0] for i in child_pairs], dtype=float)
        vars_ = np.array([_safe_var(i[1], epsilon) for i in child_pairs], dtype=float)
        precisions = 1.0 / vars_
        anc = float(np.sum(means * precisions) / np.sum(precisions))
        anc_var = float(_safe_var(float(node.dist), epsilon) + (1.0 / np.sum(precisions)))
        anc_by_idx[node.idx] = anc

        # Generate k-1 independent contrasts for k-child nodes.
        if len(means) >= 2:
            running_x = means[0]
            running_w = precisions[0]
            running_v = 1.0 / running_w
            for cidx in range(1, len(means)):
                xj = means[cidx]
                vj = vars_[cidx]
                contrast_raw = running_x - xj
                contrast_var = running_v + vj
                contrast = contrast_raw / np.sqrt(contrast_var)
                rows.append({
                    "node": node.idx,
                    "contrast_id": cidx - 1,
                    "anc": anc,
                    "anc_var": anc_var,
                    "contrast_raw": contrast_raw,
                    "contrast_var": contrast_var,
                    "contrast": contrast,
                })
                wj = 1.0 / vj
                running_x = (running_x * running_w + xj * wj) / (running_w + wj)
                running_w = running_w + wj
                running_v = 1.0 / running_w
        return anc, anc_var

    recurse(tree.treenode)
    return rows, anc_by_idx


# single test
if __name__ == "__main__":

    import toyplot
    import toytree

    CMAP = toyplot.color.brewer.map("BlueRed", reverse=True)

    TREE = toytree.rtree.imbtree(ntips=5, treeheight=1)
    TREE = TREE.set_node_data("g", data={i: 5 for i in (2, 3, 4)}, default=1)
    TREE.draw(
        ts='p', 
        node_labels=TREE.get_node_data("g"),
        node_colors=[
            CMAP.colors(i, 0, 5) for i in TREE.get_node_data('g')]
        )

    # apply reconstruction
    # pics = get_phylogenetic_independent_contrasts(TREE, "g")
    # for node in pics:
    #     print(node, pics[node])
    # print(ntree)#.get_node_data())


    # # new values are stored as -mean, -var, -contrasts, ...
    # evals = ntree.get_edge_values("g-mean")

    # # draw new tree
    # ntree.draw(
    #     ts='p', 
    #     node_labels=ntree.get_node_values("g-mean", 1, 1),
    #     node_colors=[
    #         colormap.colors(i, 0, 5) for i in 
    #         ntree.get_node_values('g-mean', 1, 1)]
    # )

    NWK = "((((Homo:0.21,Pongo:0.21):0.28,Macaca:0.49):0.13,Ateles:0.62):0.38,Galago:1.00);"
    TRE = toytree.tree(NWK)
    names = ["Homo", "Pongo", "Macaca", "Ateles", "Galago"]
    X = pd.Series([4.09434, 3.61092, 2.37024, 2.02815, -1.46968], index=names)
    Y = pd.Series([4.74493, 3.33220, 3.36730, 2.89037, 2.30259], index=names)
    TRE = TRE.set_node_data("X", X)
    TRE = TRE.set_node_data("Y", Y)    
    # print(TRE.get_node_data())
    # PICX = get_phylogenetic_independent_contrasts(TRE, "X")
    get_ancestral_states_pic(TRE, "X", inplace=True)
    print(TRE.get_node_data())

    tree = toytree.rtree.unittree(ntips=10, treeheight=1)
    tree.pcm.simulate_continuous_bm({"trait": 1.0}, inplace=True)
    pics = toytree.pcm.get_phylogenetic_independent_contrasts(tree, "trait")
    print(pics)

    tree = toytree.rtree.unittree(ntips=10, treeheight=1.0)
    tree.pcm.simulate_continuous_bm({"X": 1.0}, tips_only=True, inplace=True)
    tree.pcm.get_ancestral_states_pic("X", inplace=True)
    print(tree.get_node_data("X"))
