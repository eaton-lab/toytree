#!/usr/bin/env python

"""Parse a ToyTree object from an edge table.

Example
-------
>>> import toyplot
>>> import numpy as np
>>> import scipy.spatial
>>> import scipy.cluster

# generate 100 random data points for 12 things
>>> rng = np.random.default_rng(123)
>>> data = rng.random(size=(6, 100))

# calculate a measure of distance between samples
>>> dists = scipy.spatial.distance.pdist(data)

# infer a hierarchical tree by clustering samples by distances
>>> edges = scipy.cluster.hierarchy.average(dists)

# draw the tree
>>> canvas, axes, mark = tree.draw()
"""

import numpy as np
import toytree


def _build_tree_from_scipy_dist_table(table: np.ndarray):
    """Return ToyTree from a scipy distance table.
    
    A greedy algorithm to implement hierarchical clustering of samples
    based on distances in a distance table.
    """
    name_to_node = {}
    
    # iterate over rows of the table
    for ridx in range(table.shape[0]):
        
        # internal name is row number + ntips
        iname = int(ridx + table[-1, -1])
        
        # create new internal node
        internal = toytree.Node(name=str(iname))
        name_to_node[iname] = internal
        
        # iterate over child indices
        for cidx in table[ridx, [0, 1]]:
            cidx = int(cidx)
            
            # create child node if it doesn't exist
            if cidx not in name_to_node:
                child = toytree.Node(name=str(cidx))
                name_to_node[cidx] = child
            else:
                child = name_to_node[cidx]
                
            # set distance
            child.dist = table[ridx, 2]
            
            # connect to parent
            child.up = internal
            internal.children.append(child)
    return toytree.ToyTree(internal)


if __name__ == "__main__":

    import toyplot
    import numpy as np
    import scipy.spatial
    import scipy.cluster

    # generate 100 random data points for 12 things
    rng = np.random.default_rng(123)
    data = rng.random(size=(6, 100))

    # calculate a measure of distance between samples
    dists = scipy.spatial.distance.pdist(data)

    # infer a hierarchical tree by clustering samples by distances
    edges = scipy.cluster.hierarchy.average(dists)
    print(edges)
    # draw the tree
    # canvas, axes, mark = tree.draw()