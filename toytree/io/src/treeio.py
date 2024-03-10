#!/usr/bin/env python

"""Generic function for parsing trees.

Parse flexible input types (filepath, str, Url) to ToyTree class.
"""

from typing import Union, TypeVar, Optional
from pathlib import Path
# from loguru import logger

from toytree.core import ToyTree, Node
# from toytree.core.node import Node
from toytree.utils import ToytreeError
from toytree.io.src.parse import parse_tree

# logger = logger.bind(name="toytree")

# PEP 484 recommend capitalizing alias names
Url = TypeVar("Url")


def tree(
    data: Union[str, Path, Url],
    feature_prefix: str = "&",
    feature_delim: str = ",",
    feature_assignment: str = "=",
    internal_labels: Optional[str] = None,
) -> ToyTree:
    """Return a ToyTree parsed from variable input types and formats.

    Returns a :class:`ToyTree` object from a variety of optional
    input types, including a newick or nexus string, or a filepath or
    Url to a file containing a newick or nexus string. This function
    will try to auto-detect whether internal node labels are names
    or support values. If the newick string contains additional
    metadata as NHX annotations these will be parsed and stored as Node
    features.

    Parameters
    ----------
    data: Union[str, Path, Url]
        One of several allowed input types containing tree data. The
        str type can be a newick string or valid file path; the Path
        type must be a pathlib.Path object; the Url type is any string
        starting with http, from which str data will be fetched.
    feature_prefix: str
        If NHX meta data is present in the newick string enter the
        common prefix contained in each set of square brackets.
        Common options are "", "&", or "&&NHX:". Default="&".
    feature_delim: str
        If NHX meta data is present in the newick string enter the
        delimiter used to separate key-value pairs. Default=",".
    feature_assignment: str
        If NHX meta data is present in the newick string enter the
        assignment operator between key-value pairs. Default="=".
    internal_labels: str or None
        Labels next to internal nodes are often interchangeably used to
        record node names or support values. Enter "name", "support",
        or a different feature name to assign the values to. Default
        is None which mean toytree will infer as 'name' vs 'support'
        based on whether values are str or numeric type.

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
        ttree = parse_tree(
            data,
            feature_prefix=feature_prefix,
            feature_delim=feature_delim,
            feature_assignment=feature_assignment,
            internal_labels=internal_labels,
        )
    # raise an error (to make an empty tree you must enter empty Node)
    else:
        raise ToytreeError(f"Cannot parse input tree data: {data}")
    return ttree


if __name__ == "__main__":

    URI = "https://eaton-lab.org/data/Cyathophora.tre"
    TREE = tree(URI)
    print(TREE)
    print(TREE.get_node_data())

    import toytree
    tree = toytree.tree("((a,b),c),d);")
    tree