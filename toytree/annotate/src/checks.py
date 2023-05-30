#!/usr/bin/env python

"""Utility functions for annotations.
"""

# from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian
from toyplot.mark import Mark
from toytree import ToyTree
from toytree.drawing import ToyTreeMark
from toytree.utils import ToytreeError

CARTESIAN_TYPE_ERROR = """\
'axes' argument to annotation func must be a Cartesian object
containing a ToyTree Mark (drawing). For example:

>>> # get Cartesian axes from a toytree drawing
>>> canvas, axes, mark = tree.draw()
>>> tree.annotate.add_tip_markers(axes, size=9, color='red', xshift=20)
"""


def get_last_toytree_mark(axes: Cartesian) -> ToyTreeMark:
    """Return the last ToyTreeMark rendered on the Cartesian axes.

    """
    if not isinstance(axes, Cartesian):
        raise TypeError(CARTESIAN_TYPE_ERROR)
    targets = axes._scenegraph.targets(axes, "render")
    tree_marks = [i for i in targets if isinstance(i, ToyTreeMark)]
    if not tree_marks:
        raise ToytreeError(
            "No tree drawings (ToyTreeMark) have been rendered on the "
            "Cartesian axes. First draw a ToyTree.")
    return tree_marks[-1]


def assert_tree_matches_mark(tree: ToyTree, mark: Mark) -> None:
    """Raise exception if mark does not match up with tree data.
    """
    nnodes_in_mark = mark.ntable.shape[0]
    assert tree.nnodes == nnodes_in_mark, (
        f"Cannot annotate a tree drawing containing {tree.nnodes} nodes "
        f"with a different tree that has {nnodes_in_mark} nodes.")


if __name__ == "__main__":

    pass
