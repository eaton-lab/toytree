#!/usr/bin/env python

"""
PCM: phylogenetic comparative methods tools
"""

import os
import time
import numpy as np
import toytree



class PCM:
    """
    Phylogenetic comparative methods implemented on toytrees.
    """
    def __init__(self, tree):
        self.tree = tree


    def independent_contrasts(self, feature):
        ntree = self.tree.copy()
        resdict = PIC(ntree, feature)
        ntree = ntree.set_node_values(
            feature="{}-contrast",
            values={i.name: j[2] for (i, j) in resdict.items()}
        )
        ntree = ntree.set_node_values(
            feature="{}-contrast-var",
            values={i.name: j[3] for (i, j) in resdict.items()}
        )        
        return ntree


    def ancestral_state_reconstruction(self, feature):
        """
        Infer ancestral states on ancestral nodes for continuous traits
        under a brownian motion model of evolution.

        Modified from IVY interactive (https://github.com/rhr/ivy/)

        Returns a toytree with feature applied to each node.
        """
        ntree = self.tree.copy()
        resdict = PIC(ntree, feature)
        ntree = ntree.set_node_values(
            feature, 
            values={i.name: j[0] for (i, j) in resdict.items()}
        )
        return ntree


    def tree_to_VCV(self):
        return VCV(self.tree)




def VCV(tree):
    """
    Return the variance co-variance metrix representing the tree topology.
    """
    vcv_ = np.zeros((tree.ntips,tree.ntips))
    labs = tree.get_tip_labels()
    for lab1 in range(tree.ntips):
        for lab2 in range(tree.ntips):
            mrca_idx = tree.get_mrca_idx_from_tip_labels([labs[lab1],labs[lab2]])
            mrca_height = tree.treenode.search_nodes(idx=mrca_idx)[0].height
            vcv_[lab1, lab2] = tree.treenode.height - mrca_height
    return(vcv_)



def PIC(tree, feature):
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
        A modified copy of the input tree is returned with the mean ancestral
        value for the selected feature inferred for all nodes of the tree. 
    """
    # get current node features at the tips
    fdict = tree.get_feature_dict(key_attr="name", values_attr=feature)
    data = {i: j for (i, j) in fdict.items() if i in tree.get_tip_labels()}

    # apply dynamic function from ivy to return dict results
    results = dynamicPIC(tree.treenode, data, results={})

    # return dictionary mapping nodes to (mean, var, contrast, cvar)
    return results



def dynamicPIC(node, data, results):
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
    X = []
    v = []

    # recursively does children until X and v are full
    for child in node.children:

        # child has children, do those first
        if child.children:

            # update results dict with children values
            dynamicPIC(child, data, results)
            child_results = results[child]

            # store childrens values
            X.append(child_results[0])
            v.append(child_results[1])

        # no child of child, so just do child
        else:
            X.append(data[child.name])
            v.append(child.dist)

    # Xi - Xj is the contrast value
    Xi, Xj = X  

    # vi + vj is the contrast variance
    vi, vj = v

    # Xk is the reconstructed state at the node
    Xk = ((1.0 / vi) * Xi + (1 / vj) * Xj) / (1.0 / vi + 1.0 / vj)

    # vk is the variance
    vk = node.dist + (vi * vj) / (vi + vj)

    # store in dictionary and 
    results[node] = (Xk, vk, Xi - Xj, vi + vj)
    return results



def calculate_ES(tree):
    "Return DataFrame with equal splits measure sensu Redding and Mooers 2006"
    # dataframe for storing results
    df = pd.DataFrame(columns=["DR"], index=tree.get_tip_labels())

    # traverse up to root from each tip
    for idx in range(tree.ntips):
        node = tree.idx_dict[idx]
        DR = 0
        j = 1
        while node.up:
            DR += node.up.dist / (2 ** j)
            node = node.up
            j += 1
        df.iloc[idx, 0] = DR
    return df



def calculate_DR(tree):
    "Returns a dataframe with tip-level diversification rates sensu Jetz 2012"
    # ensure tree is a tree
    tree = toytree.tree(tree)
    return 1 / calculate_ES(tree)



def calculate_tip_level_diversification(trees, njobs=1):
    """
    Returns a dataframe with tip-level diversification rates calculated
    across a set of trees. Enter a multitree object or, for very large trees,
    you can enter a generator of newick strings (see example).

    Parameters:
    -----------
    trees (Toytree, Multitree, or newick file):
        One or more ultrametric trees in newick format. For ultra large
        datasets use a file as input.

    njobs (int):
        Distribute N jobs in parallel usign ProcessPoolExecutor

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

    # not yet adding pandas as a global dependency
    import pandas as pd

    # load data and metadata from newick, toytree, or multitree
    if isinstance(trees, str) and os.path.exists(trees):
        with open(trees) as tree_generator:
            tre = toytree.tree(next(tree_generator))
            ntips = tre.ntips
            ntrees = sum(1 for i in tree_generator) + 1
            tiporder = tre.get_tip_labels()
        itertree = open(trees, 'r')
    elif isinstance(trees, toytree.Toytree.ToyTree):
        itertree = iter([trees])
        ntrees = len(trees)
        ntips = trees.ntips
        tiporder = trees.get_tip_labels()
        topen = None
    elif isinstance(trees, toytree.Multitree.MultiTree):
        itertree = iter(i for i in trees)
        ntrees = len(trees)
        ntips = trees.treelist[0].ntips
        tiporder = trees.treelist[0].get_tip_labels()
        topen = None
    else:
    	raise IOError("problem with input: {}".format(trees))

    # array to store results 
    tarr = np.zeros((ntips, ntrees))

    # run non-parallel calculations
    if njobs == 1:
        for tidx, tree in enumerate(itertree):
            df = calculate_DR(tree)
            tarr[:, tidx] = df.loc[tiporder, "DR"]

    # or, distribute jobs in parallel (py3 only)
    else:
        from concurrent.futures import ProcessPoolExecutor 
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




# single test
if __name__ == "__main__":

    import toyplot
    import toytree

    colormap = toyplot.color.brewer.map("BlueRed", reverse=True)
    colormap

    tree = toytree.rtree.imbtree(5, 1e6)
    tree = tree.set_node_values(
        "g", 
        values={i: 5 for i in (2, 3, 4)},
        default=1,
    )
    tree.draw(
        ts='p', 
        node_labels=tree.get_node_values("g", 1, 1),
        node_colors=[
            colormap.colors(i, 0, 5) for i in tree.get_node_values('g', 1, 1)]
        )

    # apply reconstruction
    ntree = PIC(tree, "g")

    # new values are stored as -mean, -var, -contrasts, ...
    evals = ntree.get_edge_values("g-mean")

    # draw new tree
    ntree.draw(
        ts='p', 
        node_labels=ntree.get_node_values("g-mean", 1, 1),
        node_colors=[
            colormap.colors(i, 0, 5) for i in 
            ntree.get_node_values('g-mean', 1, 1)]
    )
