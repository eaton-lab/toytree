#!/usr/bin/env python

"""helper functions for tree parsing odd file formats.

tree parsing specifics
----------------------
- toytree.io.parse_tree_from_newick_file
- toytree.io.parse_tree_from_nexus_file
x- toytree.io.parse_tree_from_mb_file
x- toytree.io.parse_tree_from_beast3_file
x- toytree.io.parse_tree_from_bpp_file
x- toytree.io.parse_tree_from_superbpp_file
"""

from typing import Union, TypeVar, Optional, Union
import re
from pathlib import Path
from toytree.core import ToyTree
from toytree.io.src.parse import parse_tree, parse_tree_object
from toytree.utils import ToytreeError

# temporary
# ToyTree = TypeVar("ToyTree")
MultiTree = TypeVar("MultiTree")


def read_newick(
    path: Union[str, Path],
    feature_prefix: str = "&",
    feature_delim: str = ",",
    feature_assignment: str = "=",
    internal_labels: Optional[str] = None,
) -> Union[ToyTree, MultiTree]:
    """Return a ToyTree or MultiTree from a newick file.

    The file should contain one or more newick tree strings each on
    a separate line. This will parse the newick strings including
    those in extended-newick format with data stored in square-bracket
    comment blocks and return ToyTrees with data stored to Nodes.

    Compared to `toytree.tree` this function has additional options
    for specifying the format of feature comment blocks, and of the
    internal node label types (e.g., support values or names).

    See Also
    --------
    `toytree.tree`, `toytree.io.parse_newick_custom`

    Parameters
    ----------
    feature_prefix: str
        If additional features are stored in the newick as comments,
        they should be inside of square brackets. These blocks often
        start with a prefix character, such as "&" or "&&NHX". Check
        your file if you are unsure.
    feature_delim: str
        The character used to delimit features inside of a comment
        block. This is usually "," or ":".
    feature_assignment: str
        The character separating feature names and values in a comment
        block used for assignment. This is usually "=" or ":".
    internal_labels: str or None
        The feature that is present on internal node labels. If None
        then it will be inferred from the values present. Internal
        labels are usually either 'support' or 'name'. If only numeric
        values are present then it is parsed as 'support' floats,
        but this can overridden here if set `internal_labels='name'`.

    Examples
    --------
    >>> nwk1 = "((A,B),(C,D));"
    >>> tree1 = toytree.io.read_newick(nwk1)
    >>> print(tree1.get_node_data())
    >>>
    >>> nwk2 = "((a:1,b:2)0.99:3,(c:1,d:1)0.90:3)0.66:1;"
    >>> tree2 = toytree.io.read_newick(nwk2)
    >>> print(tree2.get_node_data())
    """
    kwargs = {
        "feature_prefix": feature_prefix,
        "feature_delim": feature_delim,
        "feature_assignment": feature_assignment,
        "internal_labels": internal_labels,
    }
    return parse_tree(path, **kwargs)


def read_nexus(path: Union[str, Path], **kwargs) -> ToyTree:
    """Return a ToyTree or MultiTree from a NEXUS file.

    The NEXUS file must contain a 'trees' block that includes one
    or more trees. This function takes the same arguments as
    `read_newick` for parsing extended-newick format of newick strings.
    It has additional arguments to parse other data from the NEXUS
    file, such as from the ... block (TODO)...
    """
    return parse_tree_object(path, **kwargs)


def read_mb_file(path: Union[str, Path], **kwargs) -> Union[ToyTree, MultiTree]:
    """Return a ToyTree from a mrbayes tree file.

    Mrbayes .trees files are NEXUS format with trees recorded
    using an extended newick format (NHX-like) with comment blocks
    that include both edge and node statistics separately. A trees
    file may contain many trees (a posterior distribution) or a single
    tree (e.g., a consensus tree).

    Internal node values can include ranges with "," inside, which
    requires additional comma-parsing that is automated by this
    function, as opposed to using `read_nexus`. TODO.

    Returns
    -------
    ToyTree or MultiTree
        The returned type depends on whether one or more trees in file.
    """
    return parse_tree_object(path, **kwargs)


def read_bpp_file(path: str, **kwargs):
    """Return a ToyTree or MultiTree from a BPP "00" tree file.

    This format has NHX data separately on nodes and edges, which is
    not typical other than perhaps for FigTree.

    Example
    -------
    >>> (a,(b,c))[]
    (6:0.000898,(5:0.000420,(3:0.000071,(2:0.000061,1:0.000061)[&height_95%_HPD={0.00004600,0.00007400},theta=0.0003823]:0.000010)[&height_95%_HPD={0.00005500,0.00008600},theta=0.0008018]:0.000349)[&height_95%_HPD={0.00033100,0.00050700},theta=0.0102051]:0.000478)[&height_95%_HPD={0.00078400,0.00101700},theta=0.0064148]
    """
    return parse_tree_object(path, **kwargs)


if __name__ == "__main__":

    # get a tree with metadata features
    import toytree
    TREE = toytree.rtree.imbtree(4, treeheight=3)

    # write/read newick
    # NWK = TREE.write()
    # TRE = toytree.io.read_newick(NWK)
    # print(TRE.get_node_data())

    # Example usage
    newick_string = "(c,(a,b)[&x=3,y=2]:0.1)[&x=4,y=5]:0.5;"

    # write/read mrbayes NEXUS
    # BPP1 = "/home/deren/Downloads/bpp-cacti-res/clades5-nloci1K-sample500K_r3.figtree.nex"
    # read_nexus(BPP1)
