#!/usr/bin/env python

"""Generic multitree parsing function.

"""

from typing import Union, Sequence
from pathlib import Path
from toytree.core.tree import ToyTree
from toytree.core.multitree import MultiTree
from toytree.io.src.parser import TreeIOParser
from toytree.utils import ToytreeError
import toytree


def mtree(
    data:Union[str, Path, Sequence[ToyTree], Sequence[str]],
    **kwargs) -> MultiTree:
    """General class constructor to parse and return a MultiTree.

    Input arguments as a multi-newick string, filepath, Url, or 
    Collection of Toytree objects.
    
    Parameters
    ----------
    data: str, Path, or Collection
        string, filepath, or URL for a newick or nexus formatted list
        of trees, or a collection of ToyTree objects.

    Examples
    --------
    >>> mtre = toytree.mtree("many_trees.nwk")
    >>> mtre = toytree.mtree("((a,b),c);\n((c,a),b);")
    >>> mtre = toytree.mtree([toytree.rtree.rtree(10) for i in range(5)])
    """
    # parse the newick object into a list of Toytrees
    treelist = []
    if isinstance(data, Path):
        data = str(Path)
    if isinstance(data, str):
        treelist = TreeIOParser(data, multitree=True, **kwargs).trees
    elif isinstance(data[0], ToyTree):
        treelist = [i.copy() for i in data]
    elif isinstance(data[0], (str, bytes)):
        treelist = [toytree.tree(i) for i in data]
    else:
        raise ToytreeError("mtree input format unrecognized.")
    return MultiTree(treelist)
