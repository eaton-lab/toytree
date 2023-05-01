#!/usr/bin/env python

"""BaseLayout class from which child classes define other layouts.

This class is used to get the (x,y) coordinates at which to place
nodes on a set of Cartesian coordinate axes when plotting. The layout
types currently supported are 'right', 'left', 'up', 'down', 
'circular' and 'unrooted'. 

Note
----
The circular layout is projected into Cartesian coordinates at the
end, not polar coordinates.
"""

from typing import TypeVar, Sequence, Optional
from abc import ABC
import numpy as np
from loguru import logger
from toytree.style import TreeStyle
from toytree.utils import ToytreeError

ToyTree = TypeVar("ToyTree")
Node = TypeVar("Node")
logger = logger.bind(name="toytree")


class BaseLayout(ABC):
    """Abstract base class for Layout objects.

    Layout class object generates a `.style` object as a TreeStyle
    updated with user kwargs to `.draw()`, and uses relevant args
    in this to build a `.coords` array with Node coordinates, which
    is affected by 'layout', 'use_edge_lengths' and 'tip_labels_align'.
    """

    def __init__(
        self,
        tree: ToyTree,
        style: TreeStyle,
        fixed_order: Optional[Sequence[str]] = None,
        fixed_position: Optional[Sequence[float]] = None,
    ):
        self.tree = tree
        """: ToyTree from which tree shape will be extracted."""
        self.style = style
        """: TreeStyle dict-like from which layout style is extracted."""
        self.fixed_order = fixed_order
        """: List of tip names to override default layout tip order."""
        self.fixed_position = fixed_position
        """: List of tip pos to override default layout tip spacing."""

        # ----------- results to be generated ------------------
        self.coords: np.ndarray = None
        """: Node coordinates in the projected layout."""
        self.tcoords: np.ndarray = None
        """: Tip node coordinates in the projected layout. Note: these
        can be different from those in coords when tip_labels_align=True."""
        self.angles: np.ndarray = None
        """: Tip label angles in the projected layout."""

        # subclasses have a run function that fill .coords and .tcoords
        self.run()

    def run(self):
        """BaseLayout has no run function."""
        raise ToytreeError(f"Use a subclass of {self.__class__}")
