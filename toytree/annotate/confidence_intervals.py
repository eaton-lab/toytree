#!/usr/bin/env python

"""
Annotate time-scaled trees to add node height confidence intervals.

"""

from typing import Dict, Tuple, TypeVar
import numpy as np
import toyplot

ToyTree = TypeVar("ToyTree")


def node_height_confidence_intervals(
    tree: ToyTree,
    axes: toyplot.coordinates.Cartesian, 
    mapping: Dict[int,Tuple[float,float]],
    **kwargs,
    ) -> 'Mark':
    """Returns a toyplot marker to add confidence intervals on Nodes.

    Takes an input dictionary mapping node idxs to a tuple of lower
    and upper confidence intervals for node heights.

    Parameters
    ----------
    ...

    Example
    -------
    >>> tree = toytree.rtree.unittree(10, treeheight=1e5)
    >>> ages_ci = {
    >>>     nidx: (node.dist - 1000, node.dist + 1000) 
    >>>     for nidx, node in enumerate(tree)
    >>> }
    >>> canvas, axes, mark0 = tree.draw()
    >>> tree.annotate.node_height_confidence_intervals(axes, ages_ci)
    >>> 
    >>> mark = toytree.annotate.node_height_confidence_intervals(
    >>>     tree=tree, axes=axes, mapping=ages_ci)
    """
    # edge connecting each node to a copy of itself
    edges = np.column_stack([
        np.arange(tree.nnodes - tree.ntips), 
        np.arange(tree.nnodes - tree.ntips, (tree.nnodes - tree.ntips) * 2),
    ])

    # vertex for each node -/+ the conf interv.
    vertices = [(-mapping[i][0], tree[i].x) for i in mapping]
    vertices += [(-mapping[i][1], tree[i].x) for i in mapping]

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
