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
>>> # fit linear model to contrasts through the origin (could use scipy...)
>>> import statsmodels.api as sm
>>> traits = 
>>> sm.OLS.from_model("Y ~ X - 1", Y=pic_y, X=pic_x).summary()
>>> # 0.4319
>>> sm.OLS.from_model("X ~ Y - 1", Y=pic_y, X=pic_x).summary()
>>> # 0.998

References
----------
Felsenstein, J. (1985) Phylogenies and the comparative method.
_American Naturalist_, *125*, 1-15.
"""

from typing import Union, Sequence
import pandas as pd
from toytree.core import ToyTree
from toytree.core.apis import add_subpackage_method, PhyloCompAPI


feature = Union[str, Sequence[float]]
__all__ = [
    "get_phylogenetic_independent_contrasts",
    "get_ancestral_states_pic",
]


@add_subpackage_method(PhyloCompAPI)
def get_phylogenetic_independent_contrasts(tree: ToyTree, feature: feature) -> pd.DataFrame:
    """Return a dictionary of {idx: standardized-contrasts}.

    Independent contrasts are calculated for every internal node
    of a tree for a selected continuous feature (trait) 
    under a Brownian motion model of evolution.

    Modified from IVY interactive (https://github.com/rhr/ivy/)

    Parameters
    ----------
    feature: str | Sequence[float]
        A feature stored to the tree object or a Sequence of floats
        of length ntips.

    Returns
    -------
    pandas.DataFrame with columns for [ancestral state, ancestral state
    variance, independent contrast, independent contrast variance] for
    all internal nodes.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=10, treeheight=1)
    >>> tree.pcm.simulate_continuous_bm({"trait": 1.0}, inplace=True)
    >>> pics = toytree.pcm.get_phylogenetic_independent_contrasts(tree, "trait")
    """
    # get current node features at the tips
    tips = [tree[i] for i in range(tree.ntips)]
    fdict = {i.name: getattr(i, feature) for i in tips}
    data = {i: fdict[i] for i in fdict if i in tree.get_tip_labels()}

    # apply dynamic function from ivy to return dict results
    results = _dynamic_pic(tree.treenode, data, results={})

    # return dictionary mapping nodes to (mean, var, contrast, cvar)
    # return results
    return pd.DataFrame(
        index=[i.idx for i in results],
        columns=["anc", "anc_var", "contrast", "contrast_var"],
        data=list(results.values())
    )


def _dynamic_pic(node, data, results):
    """Used internally by get_independent_contrasts.

    Phylogenetic independent contrasts. Recursively calculate 
    independent contrasts of a bifurcating node given a dictionary
    of trait values.

    Modified from IVY interactive (https://github.com/rhr/ivy/)

    Parameters
    ----------
    node: 
        A node object
    data: dict
        Mapping of leaf names to character values

    Returns
    -------
    dict
        Mapping of internal nodes to tuples containing ancestral
        state, its variance (error), the contrast, and the
        contrasts's variance.

    TODO: modify to accommodate polytomies.
    """
    # store in lists to support flexible number of children (e.g. polytomies)
    means = []
    variances = []

    # recursively does children until X and v are full
    for child in node.children:

        # child has children, do those first
        if child.children:

            # update results dict with children values
            _dynamic_pic(child, data, results)
            child_results = results[child]

            # store childrens values
            means.append(child_results[0])
            variances.append(child_results[1])

        # no child of child, so just do child
        else:
            means.append(data[child.name])
            variances.append(child.dist)

    # Xi - Xj is the contrast value
    means_i, means_j = means

    # vi + vj is the contrast variance
    vars_i, vars_j = variances

    # Xk is the reconstructed state at the node
    means_k = (
        ((1.0 / vars_i) * means_i + (1 / vars_j) * means_j) / (1.0 / vars_i + 1.0 / vars_j)
    )

    # vk is the variance
    vars_k = node.dist + (vars_i * vars_j) / (vars_i + vars_j)

    # store in dictionary and return
    results[node] = (means_k, vars_k, means_i - means_j, vars_i + vars_j)
    return results


@add_subpackage_method(PhyloCompAPI)
def get_ancestral_states_pic(tree: ToyTree, feature: feature, inplace: bool = False) -> Union[pd.Series, ToyTree]:
    """Return feature with ancestral states inferred at internal nodes.

    Trait must be continuous without missing value for tip nodes.

    Parameters
    ----------
    tree: ToyTree
        A tree with branch lengths.
    feature: str | Sequence[float]
        A continous trait for each tip node in the tree entered as a
        sequence of floats or ints, or as a str name of a feature stored
        to the tree object.
    inplace: bool
        If True the result is stored as a feature to the tree data and
        the tree is returned, else a pandas Series is returned with the
        inferred trait values.

    See Also
    --------
    `get_ancestral_state_pgls`

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=10, treeheight=1.0)
    >>> tree.pcm.simulate_continuous_bm({"X": 1.0}, tips_only=True, inplace=True)
    >>> tree.pcm.get_ancestral_state_pic("X", inplace=True)
    >>> print(tree.get_node_data("X"))
    """
    pics = get_phylogenetic_independent_contrasts(tree, feature)
    if inplace:
        tip_traits = list(tree.get_node_data(feature)[:tree.ntips])
        int_traits = list(pics["anc"])
        tree.set_node_data(feature, tip_traits + int_traits, inplace=True)
        return tree
    trait = tree.get_node_data(feature)
    trait.iloc[tree.ntips:] = pics["anc"]
    trait.name = feature
    return trait


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
    get_ancestral_state_pic(TRE, "X", inplace=True)
    print(TRE.get_node_data())

    tree = toytree.rtree.unittree(ntips=10, treeheight=1)
    tree.pcm.simulate_continuous_bm({"trait": 1.0}, inplace=True)
    pics = toytree.pcm.get_phylogenetic_independent_contrasts(tree, "trait")
    print(pics)

    tree = toytree.rtree.unittree(ntips=10, treeheight=1.0)
    tree.pcm.simulate_continuous_bm({"X": 1.0}, tips_only=True, inplace=True)
    tree.pcm.get_ancestral_state_pic("X", inplace=True)
    print(tree.get_node_data("X"))