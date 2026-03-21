#!/usr/bin/env python

"""

Adds admixture edge to existing ToyTree Object.

Method
------

Creates and draws an admixture edge between two tree tips
>>> annotate.add_admixture_edge()


"""

from toytree.core import Node, ToyTree
from toytree.core.apis import AnnotationAPI, add_subpackage_method
from toytree.drawing import Cartesian


@add_subpackage_method(AnnotationAPI)
def add_admixture_edge(
    tree: ToyTree, axes: Cartesian, src: Node = None, dest: Node = None
) -> Mark:
    """Returns a Toyplot mark of the admixture edge added.

    Parameters
    ----------
    src: source node at which the admixture edge will start
    dest: destination where the admixture edge will end


    Below is old implementation
    TODO: add functionality for this argument to add_admixture_edge
    Admixture edges add colored edges to the plot in the
                style of the 'edge_align_style'. These will be drawn
                from (source, dest, height, width, color). Example:
                `>>> [(4, 3, 50000, 3, 'red')]`.
            fixed_order: Sequence[str]
    """
