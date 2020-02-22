#!/usr/bin/env python

"""
PCM: phylogenetic comparative methods tools
"""

import numpy as np


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
