#!/usr/bin/env python

"""Phylogenetic independent contrasts for continuous traits.

References
----------
- Felsenstein 1985
- Harmon textbook
- ...

"""

from typing import Tuple


def get_phylogenetic_independent_contrasts(tree, feature):
    """Return a dictionary of {idx: standardized-contrasts}.

    Independent contrasts are calculated for every internal node
    of a tree for a selected continuous feature (trait) 
    under a Brownian motion model of evolution.

    Modified from IVY interactive (https://github.com/rhr/ivy/)

    Parameters
    ----------
    feature: (str)
        The name of a feature of the tree that has been mapped to all 
        tip nodes of the tree. 

    Returns
    -------
    Dict[int, Tuple(float, float, float, float)]

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=10, treeheight=1)
    >>> tree.set_node_data("trait", dict(range(10), range(10)), inplace=True)
    >>> pics = toytree.pcm.get_phylogenetic_independent_contrasts(tree, "trait")
    >>> ...
    """
    # get current node features at the tips
    tips = [tree[i] for i in range(tree.ntips)]
    fdict = {i.name: getattr(i, feature) for i in tips}
    data = {i: fdict[i] for i in fdict if i in tree.get_tip_labels()}

    # apply dynamic function from ivy to return dict results
    results = _dynamic_pic(tree.treenode, data, results={})

    # return dictionary mapping nodes to (mean, var, contrast, cvar)
    return results


### NEEDS MORE...

# def get_continuous_ancestral_states(tre, feature):
#     """Infer ancestral states on ancestral nodes for continuous traits
#     under a brownian motion model of evolution.

#     Modified from IVY interactive (https://github.com/rhr/ivy/)   

#     Returns:
#     --------
#     toytree (toytree.ToyTree)
#         A modified copy of the input tree is returned with the mean 
#         ancestral value for the selected feature applied to all nodes 
#         of the tree. 
#     """
#     ntre = tre.copy()
#     resdict = get_phylogenetic_independent_contrasts(ntre, feature)
#     ntre = ntre.set_node_data(
#         feature, 
#         {i.idx: j[0] for (i, j) in resdict.items()}
#     )
#     return ntre


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
        ((1.0 / vars_i) * means_i + (1 / vars_j) * means_j) / 
        (1.0 / vars_i + 1.0 / vars_j)
    )

    # vk is the variance
    vars_k = node.dist + (vars_i * vars_j) / (vars_i + vars_j)

    # store in dictionary and return
    results[node] = (means_k, vars_k, means_i - means_j, vars_i + vars_j)
    return results


# def independent_contrasts(tre, feature):
#     """
#     Set independent contrasts as features on internal nodes labeled
#     as ...
#     """
#     ntre = tre.copy()
#     resdict = PIC(ntre, feature)
#     ntre = ntre.set_node_values(
#         feature="{}-contrast",
#         values={i.name: j[2] for (i, j) in resdict.items()}
#     )
#     ntre = ntre.set_node_values(
#         feature="{}-contrast-var",
#         values={i.name: j[3] for (i, j) in resdict.items()}
#     )        
#     return ntree

# single test
if __name__ == "__main__":

    import toyplot
    import toytree

    CMAP = toyplot.color.brewer.map("BlueRed", reverse=True)

    TREE = toytree.rtree.imbtree(5, 1e6)
    TREE = TREE.set_node_data(
        "g", 
        mapping={i: 5 for i in (2, 3, 4)},
        default=1,
    )

    TREE.draw(
        ts='p', 
        node_labels=TREE.get_node_data("g"),
        node_colors=[
            CMAP.colors(i, 0, 5) for i in TREE.get_node_data('g')]
        )

    # apply reconstruction
    ntree = get_phylogenetic_independent_contrasts(TREE, "g")

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
