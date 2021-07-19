#!/usr/bin/env python

"""
Annotate time-scaled trees to add node height confidence intervals.

"""

from typing import Dict, Tuple
import numpy as np
import toyplot
from toytree.core.tree import ToyTree



def add_node_height_confidence_intervals(
    axes: toyplot.coordinates.Cartesian, 
    tree: ToyTree,
    mapping: Dict[int,Tuple[float,float]],
    **kwargs,
    ) -> 'Mark':
    """
    Returns a toyplot.graph marker to overlay confidence intervals 
    over nodes given an input dictionary mapping node idxs to a 
    tuple of lower and upper confidence intervals for node heights.

    Example:
    --------
    tree = toytree.rtree.unittree(10, treeheight=1e5)
    ages_ci = {
        nidx: (node.dist - 1000, node.dist + 1000) 
        for nidx, node in tree.idx_dict.items()
    }
    canvas, axes, mark0 = tree.draw()
    mark1 = add_node_height_confidence_intervals(axes, tree, ages_ci)
    """
    # edge connecting each node to a copy of itself
    edges = np.column_stack([
        np.arange(tree.nnodes - tree.ntips), 
        np.arange(tree.nnodes - tree.ntips, (tree.nnodes - tree.ntips) * 2),
    ])

    # vertex for each node -/+ the conf interv.
    vertices = [(-mapping[i][0], tree.idx_dict[i].x) for i in mapping]
    vertices += [(-mapping[i][1], tree.idx_dict[i].x) for i in mapping]

    # draw the graph and return the mark
    kwargs["vlabel"] = kwargs.get("vlabel", False)
    kwargs["vsize"] = kwargs.get("vsize", 0)
    kwargs["ewidth"] = kwargs.get("ewidth", 7)
    mark = axes.graph(
        edges,
        vcoordinates=vertices,
        **kwargs,
    )
    return mark



if __name__ == "__main__":
    pass
