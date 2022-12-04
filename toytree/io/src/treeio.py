#!/usr/bin/env python

"""Generic function for parsing trees.

Parse flexible input types (filepath, str, Url) to ToyTree class.
"""

from typing import Union, TypeVar
from pathlib import Path
# from loguru import logger

from toytree.core.tree import ToyTree
from toytree.core.node import Node
from toytree.utils import ToytreeError
from toytree.io.src.parse import TreeIOParser

# logger = logger.bind(name="toytree")

# PEP 484 recommend capitalizing alias names
Url = TypeVar("Url")


def tree(data: Union[str, Path, Url]) -> ToyTree:
    """Return a ToyTree parsed from variable input types and formats.

    Returns a :class:`ToyTree` object from a variety of optional 
    input types, including a newick or nexus string, or a filepath or 
    Url to a file containing a newick or nexus string. This function
    will try to auto-detect whether internal node labels are names
    or support values. If the newick string contains additional 
    metadata as comments then you should use the options available in
    `toytree.io.parse_tree_from_newick_file`.

    Parameters
    ----------
    data: Union[str, Path, Url]
        Multiple input types are supported and can be parsed and
        returned as a ToyTree. The str type can be a newick string
        or a valid file path; a Path must be a valid file pathlib.Path
        object, if a valid Url string is entered it will be fetched 
        as string data.

    See Also
    --------
    - `toytree.io.parse_tree_from_newick_file`
    - `toytree.io.parse_tree_from_nexus_file`    
    - `toytree.io.parse_newick`
    - `toytree.io.parse_newick_custom`    

    Examples
    --------
    >>> tree = toytree.tree("((a,b),c);")
    >>> tree = toytree.tree("((a:10,b:20)A:100,c:30);")
    >>> tree = toytree.tree("/tmp/test.nex")
    >>> tree = toytree.tree("https://eaton-lab.org/data/Cyathophora.tre")
    """
    # load ToyTree from Node, insures detach if Node is not root.
    if isinstance(data, Node):
        treenode = data.copy(detach=True)
        ttree = ToyTree(treenode)
    # load ToyTree from a newick or nexus from str, URL, or filepath
    elif isinstance(data, (str, Path)):
        ttree = TreeIOParser(data).parse_node_auto()
    # raise an error (to make an empty tree you must enter empty Node)
    else:
        raise ToytreeError(f"Cannot parse input tree data: {data}")
    return ttree



if __name__ == "__main__":

    URI = "https://eaton-lab.org/data/Cyathophora.tre"
    print(tree(URI))
