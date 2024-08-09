#!/usr/bin/env python

"""In development...

A CloudTreeMark is a Mark containing many overlapping trees. To reduce
the html+css size we use a custom render function?
"""

from typing import Sequence, TypeVar
from loguru import logger
# from toytree import MultiTree
from toytree.drawing import ToyTreeMark
# from toytree.core import Canvas, Cartesian
from toytree.style import tree_style_to_css_dict
from toytree.drawing.src.draw_toytree import (
    get_layout,
    get_tree_style_updated_by_draw_args,
)
# from toytree.drawing.src.mark_cloudtree import CloudTreeMark

Mark = TypeVar("Mark")
MultiTree = TypeVar("MultiTree")
logger = logger.bind(name="toytree")


def draw_cloudtree(mtree: MultiTree, **kwargs) -> Sequence[Mark]:
    """Parse arguments to draw_cloudtree and return drawing objects.

    CloudTree is a Mark similar to a ToyTree but with many overlapping
    sets of edges, where each set can be individually styled. Only one
    set of tip labels is plotted.
    """
    # which trees to plot
    idxs = kwargs.get("idxs")
    if idxs:
        mtree = mtree.copy()
        mtree.treelist = mtree.treelist[idxs]

    # TODO: allow jitter options along tip spread axis
    jitter = kwargs.get("jitter", 0.)

    # get fixed order of tips from consensus tree if not provided.
    fixed_order = kwargs.get("fixed_order", None)
    if fixed_order in [True, False, None]:
        fixed_order = (
            mtree
            .get_consensus_tree()
            .get_tip_labels()
        )

    # TODO
    else:
        # require that the user fixed_order argument includes all of
        # the tips present across all the trees.
        # assert len(fixed_order) == max_num_tips, "..."
        pass

    # get a dict mapping tips to indices for the full set of tips
    # tip_pos = dict(zip(fixed_order, range(len(fixed_order))))

    # iterate over trees and for each, allow the trees individual style
    # to override any styles not fixed or from kwargs.
    marks = []
    for tidx, tree in enumerate(mtree):

        # only show tips for the first tree
        if tidx:
            kwargs["tip_labels"] = False

        # hard-coded to disallow some styles
        kwargs["scale_bar"] = False

        # get the tree's style
        style = get_tree_style_updated_by_draw_args(tree, **kwargs)

        # using fixed order while allowing diff numbers of tips
        # style.fixed_order = [tip_pos[i] for i in tree.get_tip_labels()]

        # override styles not set by user
        style.edge_type = kwargs.get("edge_type", 'c')
        if style.edge_style.stroke_opacity is None:
            style.edge_style.stroke_opacity = 1 / len(mtree) * 3

        # get coordinate layout of this tree
        layout = get_layout(
            tree=tree,
            style=style,
            fixed_order=fixed_order,
            fixed_position=kwargs.get("fixed_position", None),
            interior_algorithm=kwargs.get("interior_algorithm", 1),
        )

        if style.tip_labels_angles is None:
            style.tip_labels_angles = layout.angles

        mark = ToyTreeMark(
            ntable=layout.coords,
            ttable=layout.tcoords,
            etable=tree.get_edges('idx'),
            **tree_style_to_css_dict(style),
        )
        marks.append(mark)

    # get a Layout with coordinates projected based on the first tree
    return marks


if __name__ == "__main__":

    import toytree
    import toyplot
    trees = [toytree.rtree.coaltree(k=6, seed=i) for i in range(100)]
    mtree = toytree.mtree(trees)
    c, a, m = mtree.draw_cloud_tree()
    toytree.utils.show([c], tmpdir="~")
    # canvas = toyplot.Canvas()
    # axes = canvas.cartesian()
    # kwargs = dict(
    #     tree_style=None, axes=axes, kwargs={}, edge_widths=3,
    #     fixed_position=None,
    #     # fixed_order=["r1", "r0", "r3", "r4", "r5", "r2"],
    # )

    # mtree[10].style.edge_style.stroke = "red"
    # mtree[10].style.edge_style.stroke_opacity = 1
    # marks = draw_cloudtree(mtree, **kwargs)
    # if marks:
    #     toytree.utils.show([canvas], tmpdir="~")
