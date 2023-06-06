#!/usr/bin/env python

"""(Experimental) Network class. NOT YET IMPLEMENTED.

- network parsing functions
    - bpp format
    - snaq format

- constrained re-rooting of Network

- conversions to and from tree + admixture args.

- drawing function.
"""

from typing import Union, Tuple, List, Optional
from pathlib import Path
import re
from loguru import logger
import toytree
from toytree.io.src.parse import WHITE_SPACE
from toytree.core.node import Node

logger = logger.bind(name="toytree")


class Node3(Node):
    """Nodes contained within a Network class object.

    In contrast to treenodes these nodes can have degree > 3, by
    having >1 parent.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._up: Tuple[Node] = tuple()
        """: Parent is a tuple of 0 or more Node3s."""
        self._gamma: Tuple[float] = tuple()
        """: Ancestry this Node3 received from parent Node3s, in order."""

    # overwrite some functions such as delete, etc.


class ToyNet(toytree.ToyTree):
    """Child class of ToyTree that stores and draws network edges.

    A network object can be used to draw networks, to calculate or
    report statistics on a network, and to extract minor or major
    trees from a network (as ToyTree objects).

    Algorithm to traverse nodes of a network in order... could still
    use the same traversals that trace the major or minor tree to visit
    each node, but another traversal may be available that would also
    visit nodes connected by an admix edge sooner...
    """
    def __init__(self, network: Union[str, Path]):
        self.network = network
        # tree, admix = parse_network(net, disconnect=disconnect)
        # super().__init__(tree, *args, **kwargs)
        # self.admix = admix

    # def ... , disconnect: bool = True, **kwargs):

    def add_edge(self) -> toytree.ToyTree:
        """Return modified Network with a new degree-3 edge added."""

    def remove_edge(self) -> toytree.ToyTree:
        """Return modified Network with a degree-3 edge removed."""

    def get_major_tree(self) -> toytree.ToyTree:
        """Return the major tree..."""

    def get_admixture_edges(self) -> Tuple:
        """Return Tuple with list of admixture edges..."""

    def write(self):
        """Write network in extended format..."""

    def root(self):
        """raise rootMisMatchError if direction doesn't work..."""


