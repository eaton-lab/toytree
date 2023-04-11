#!/usr/bin/env python

"""...


Examples
--------
>>> tree = toytree.rtree.unittree(10, seed=123)
>>> c, a, m = tree.draw();
>>> tree.annotate.add_node_pie_charts(
>>>     axes=a,
>>>     data=[(0.5, 0.5) for i in range(tree.nnodes)],
>>> )

"""

from typing import Sequence
from dataclasses import dataclass
import numpy as np
from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian
from toyplot.mark import Mark
from toytree.drawing import ToyTreeMark
from toytree.utils import ToytreeError


@dataclass
class TreeAnnotation:
    """A toyplot.Mark to be added to a toyplot.Cartesian axes using
    coordinates from the last ToyTreeMark rendered on the axes.
    """
    axes: Cartesian
    """: A toyplot.Cartesian axes object on which a ToyTree has been drawn."""
    mark: Mark = None
    """: A ToyTreeMark extracted from the Cartesian axes with Node coordinates."""

    def __post_init__(self):
        self.mark = self._get_last_toytree_mark()

    def _get_last_toytree_mark(self) -> ToyTreeMark:
        """Return the last ToyTreeMark rendered on the Cartesian axes."""
        # get last plotted toytree Mark from the axes
        targets = self.axes._scenegraph.targets(self.axes, "render")
        tree_marks = [i for i in targets if isinstance(i, ToyTreeMark)]
        if not tree_marks:
            raise ToytreeError(
                "No tree drawings (ToyTreeMark) have been rendered on the "
                "Cartesian axes. First draw a ToyTree.")


class NodeAnnotation(TreeAnnotation):
    """A TreeAnnotation that expects data for every Node in a tree.
    """
    data: Sequence[Sequence[float]]
    """: A sequence of floats, or None, of length tree.nnodes."""
    node_mask: np.ndarray = None
    """: A sequence of booleans of length tree.nnodes."""


if __name__ == "__main__":

    pass
