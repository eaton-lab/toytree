#!/usr/bin/env python

"""Annotate trees to add node height confidence intervals.

"""

from typing import Dict, Tuple, TypeVar
import numpy as np
import toyplot

ToyTree = TypeVar("ToyTree")


def add_node_bars(
    tree: ToyTree,
    axes: toyplot.coordinates.Cartesian, 
    mapping: Dict[int, Tuple[float, float]],
    # edge_color: Union[Color, Sequence[Color]],
    edge_width: float = 1.0,
    **kwargs,
    ) -> 'Mark':
    """Returns a toyplot marker to add confidence intervals on Nodes.

    Takes an input dictionary mapping node idxs to a tuple of lower
    and upper bounds for a bar drawn up and down from each node 
    height.

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
    ninternal = tree.nnodes - tree.ntips
    edges = np.column_stack([
        np.arange(ninternal), 
        np.arange(ninternal, (ninternal) * 2),
    ])

    # vertex for each node -/+ the conf interv.
    mapping = {i: j for (i, j) in mapping.items() if i > tree.ntips - 1}
    vertices = [(-mapping[i][0], tree[i]._x) for i in mapping]
    vertices += [(-mapping[i][1], tree[i]._x) for i in mapping]

    # draw the graph and return the mark
    kwargs["vlabel"] = kwargs.get("vlabel", False)
    kwargs["vsize"] = kwargs.get("vsize", 0)
    kwargs["ewidth"] = kwargs.get("edge_width", 7)
    # kwargs["eopacity"] = kwargs.get("edge_opacity", 7)  # fill/stroke/opacity?????
    mark = axes.graph(
        edges,
        vcoordinates=vertices,
        **kwargs,
    )
    return mark


def test():
    """Test of confidence intervals."""
    import toytree
    tree = toytree.rtree.unittree(10)
    c, a, m1 = tree.draw()
    ci = {i.idx: (i.height * 0.9, i.height * 1.1) for i in tree}
    m2 = add_node_bars(tree, a, ci)
    toytree.utils.show(c)

if __name__ == "__main__":

    test()
    # import toytree
    # tree = toytree.rtree.unittree(10, treeheight=1e5)
    # ages_ci = {
    #     nidx: (node.dist - 1000, node.dist + 1000) 
    #     for nidx, node in enumerate(tree)
    # }
    # canvas, axes, mark0 = tree.draw()
    # node_height_confidence_intervals(tree, axes, ages_ci)
    
    # mark = toytree.annotate.node_height_confidence_intervals(
        # tree=tree, axes=axes, mapping=ages_ci)
