#!/usr/bin/env python

"""
PCM: phylogenetic comparative methods tools
"""

import os
import time
import itertools
import numpy as np
import pandas as pd
import toytree


def continuous_ancestral_state_reconstruction(tre, feature):
    """
    Infer ancestral states on ancestral nodes for continuous traits
    under a brownian motion model of evolution. Returns a toytree with
    feature updated to each node.

    Modified from IVY interactive (https://github.com/rhr/ivy/)   
    """
    ntre = tre.copy()
    resdict = phylogenetic_independent_contrasts(ntre, feature)
    ntre = ntre.set_node_values(
        feature, 
        values={i.name: j[0] for (i, j) in resdict.items()}
    )
    return ntre

def tree_to_vcv(tree):
    """
    Return a variance-covariance matrix representing the tree topology
    where the length of shared ancestral edges are covariance and 
    terminal edges are variance.
    """
    theight = tree.treenode.height
    vcv = np.zeros((tree.ntips,tree.ntips))
    for tip1, tip2 in itertools.combinations(range(tree.ntips), 2):
        node = toytree.distance.get_mrca(tree, tip1, tip2)
        vcv[tip1, tip2] = theight - node.height
        vcv[tip2, tip1] = theight - node.height
    vcv[np.diag_indices_from(vcv)] = [
        tree.idx_dict[i].dist for i in range(tree.ntips)]
    tlabels = tree.get_tip_labels()
    return pd.DataFrame(vcv, columns=tlabels, index=tlabels)

def phylogenetic_independent_contrasts(tree, feature):
    """
    Infer ancestral states and calculate phylogenetic independent
    contrasts at nodes for a selected feature (trait). 

    Modified from IVY interactive (https://github.com/rhr/ivy/)

    Parameters
    ----------
    feature: (str)
        The name of a feature of the tree that has been mapped to all 
        tip nodes of the tree. 

    Returns
    -------
    toytree (Toytree.ToyTree)
        A modified copy of the input tree is returned with the mean 
        ancestral value for the selected feature inferred for all nodes 
        of the tree. 
    """
    # get current node features at the tips
    fdict = tree.get_feature_dict(key_attr="name", values_attr=feature)
    data = {i: fdict[i] for i in fdict if i in tree.get_tip_labels()}

    # apply dynamic function from ivy to return dict results
    results = _dynamic_pic(tree.treenode, data, results={})

    # return dictionary mapping nodes to (mean, var, contrast, cvar)
    return results

def _dynamic_pic(node, data, results):
    """
    Phylogenetic independent contrasts. Recursively calculate 
    independent contrasts of a bifurcating node given a dictionary
    of trait values.

    Modified from IVY interactive (https://github.com/rhr/ivy/)

    Args:
        node (Node): A node object
        data (dict): Mapping of leaf names to character values
    Returns:
        dict: Mapping of internal nodes to tuples containing ancestral
              state, its variance (error), the contrast, and the
              contrasts's variance.
    TODO: modify to accommodate polytomies.
    """    
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

    # store in dictionary and 
    results[node] = (means_k, vars_k, means_i - means_j, vars_i + vars_j)
    return results


def calculate_equal_splits(tree):
    """
    Return DataFrame with equal splits (ES) measure sensu Redding and 
    Mooers 2006.

    Reference:
    ----------
    TODO:
    """
    # dataframe for storing results
    data = pd.DataFrame(columns=["ES"], index=tree.get_tip_labels())

    # traverse up to root from each tip
    for idx in range(tree.ntips):
        node = tree.idx_dict[idx]
        divrate = 0
        j = 1
        while node.up:
            divrate += node.up.dist / (2 ** j)
            node = node.up
            j += 1
        data.iloc[idx, 0] = divrate
    return data



def _calculate_tip_level_diversification(tree):
    """
    Returns a dataframe with tip-level diversification rates
    sensu Jetz 2012.

    Reference:
    ----------
    TODO:
    """
    # ensure tree is a tree
    tree = toytree.tree(tree)
    data = 1 / calculate_equal_splits(tree)
    data.columns = ["DR"]
    return data



def calculate_tip_level_diversification(trees, njobs=1):
    """
    Returns a dataframe with tip-level diversification rates calculated
    across a set of trees. Enter a multitree object or, for very large
    trees, you can enter a generator of newick strings (see example).

    Parameters:
    -----------
    trees (Toytree, Multitree, or newick file):
        One or more ultrametric trees in newick format. For ultra large
        datasets use a file as input.

    njobs (int):
        Distribute N jobs in parallel using ProcessPoolExecutor

    Returns:
    --------
    df (pandas.DataFrame):
        The raw DF based on branch lengths of the tree.

    Examples:
    ---------
    # using one or more trees
    df = calculate_tip_level_diversification(trees)

    # loading super large trees
    with open(hugetreefile, 'r') as treegenerator:
        df = calculate_tip_level_diversification(treegenerator, njobs=20)
    """
    # load data and metadata from newick, toytree, or multitree
    if isinstance(trees, str) and os.path.exists(trees):
        with open(trees) as tree_generator:
            tre = toytree.tree(next(tree_generator))
            ntips = tre.ntips
            ntrees = sum(1 for i in tree_generator) + 1
            tiporder = tre.get_tip_labels()
        itertree = open(trees, 'r')
    elif isinstance(trees, toytree.core.Toytree.ToyTree):
        itertree = iter([trees])
        ntrees = len(trees)
        ntips = trees.ntips
        tiporder = trees.get_tip_labels()
    elif isinstance(trees, toytree.core.Multitree.MultiTree):
        itertree = iter(i for i in trees)
        ntrees = len(trees)
        ntips = trees.treelist[0].ntips
        tiporder = trees.treelist[0].get_tip_labels()
    else:
        raise IOError("problem with input: {}".format(trees))

    # array to store results 
    tarr = np.zeros((ntips, ntrees))

    # run non-parallel calculations
    if njobs == 1:
        for tidx, tree in enumerate(itertree):
            df = _calculate_DR(tree)
            tarr[:, tidx] = df.loc[tiporder, "DR"]

    # or, distribute jobs in parallel (py3 only)
    else:
        pool = ProcessPoolExecutor(njobs)
        treegen = iter(trees)
        rasyncs = {}

        # submit as many jobs as there are cores
        for job in range(njobs):
            tree = next(itertree)
            rasyncs[job] = pool.submit(
                calculate_DR,
                (tree),
            )

        # as each job finished submit a new one until none are left.
        # this allows avoiding loading all trees simultaneously.
        tidx = 0
        while 1:
            # get finished jobs
            finished = [i for i in rasyncs if rasyncs[i].done()]
    
            # store results and append new job to the engine
            for job in finished:

                # store result
                result = rasyncs[job].result()
                tarr[:, tidx] = result.loc[tiporder, "DR"]
                tidx += 1
                del rasyncs[job]

                # append new job unless no jobs left
                try:
                    tree = next(itertree)
                    rasyncs[job] = pool.submit(
                        calculate_DR,
                        (tree),
                    )
                except StopIteration:
                    pass

            # wait for next check
            time.sleep(0.5)           

            # wait until all jobs finish
            if not rasyncs:
                break
        pool.shutdown()

    # close the file handle, if exists
    if hasattr(itertree, "close"):
        itertree.close()

    # calculate summary of DR across the distribution of trees.
    arr = pd.DataFrame(tarr, index=tiporder)
    df = pd.DataFrame({
        'mean': arr.mean(1),
        # 'harmMean': hmean(arr, axis=1),
        'median': arr.median(1),
        'std': arr.std(1),
        '2.5%': np.percentile(arr, 0.025, axis=1),
        '97.5%': np.percentile(arr, 0.975, axis=1),
        'min': arr.min(1),
        'max': arr.max(1),
    })
    return df


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

    CMAP = toyplot.color.brewer.map("BlueRed", reverse=True)

    TREE = toytree.rtree.imbtree(5, 1e6)
    TREE = TREE.set_node_values(
        "g", 
        mapping={i: 5 for i in (2, 3, 4)},
        default=1,
    )

    TREE.draw(
        ts='p', 
        node_labels=TREE.get_node_labels("g", 1, 1),
        node_colors=[
            CMAP.colors(i, 0, 5) for i in TREE.get_node_values('g')]
        )

    # apply reconstruction
    ntree = phylogenetic_independent_contrasts(TREE, "g")

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
