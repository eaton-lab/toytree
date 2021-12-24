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

from typing import Union, TypeVar, Optional
import re
from toytree.core.tree import ToyTree
from toytree.io.src.parser import TreeIOParser

# temporary
# ToyTree = TypeVar("ToyTree")
MultiTree = TypeVar("MultiTree")


def read_newick(
    path: str,
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
    treeio = TreeIOParser(path, **kwargs)
    if len(treeio.trees) == 1:
        return ToyTree(treeio.trees[0])
    return MultiTree(treeio.trees)


def read_nexus(**kwargs):
    """Return a ToyTree or MultiTree from a NEXUS file.

    The NEXUS file must contain a 'trees' block that includes one
    or more trees. This function takes the same arguments as 
    `read_newick` for parsing extended-newick format of newick strings.
    It has additional arguments to parse other data from the NEXUS
    file, such as from the ... block (TODO)...
    """
    return read_newick(**kwargs)


def read_mb_file(path: str, **kwargs) -> Union[ToyTree, MultiTree]:
    """Return a ToyTree from a mrbayes tree file.
    
    Mrbayes .trees files are NEXUS format with trees recorded
    using an extended newick format (NHX-like) with comment blocks 
    that include both edge and node statistics separately. A trees
    file may contain many trees (a posterior distribution) or a single
    tree (e.g., a consensus tree).

    Returns
    -------
    ToyTree or MultiTree
        The returned type depends on whether one or more trees in file.
    """
    kwargs['path'] = path
    return toytree.io.read_nexus(**kwargs)


def read_bpp_file(path: str, **kwargs):
    """Return a ToyTree or MultiTree from a BPP "00" tree file.

    """
    # Converts bpp outfile format to normal newick
    regex1 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[:]")
    regex2 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[;]")
    regex3 = re.compile(r": ")
    new = regex1.sub(":", path)
    new = regex2.sub(";", new)
    new = regex3.sub(":", new)
    new = new.strip()
    # TODO
    raise NotImplementedError("TODO...")


if __name__ == "__main__":
    
    # get a tree with metadata features
    import toytree
    TREE = toytree.rtree.imbtree(4, treeheight=3)

    # write/read newick
    NWK = TREE.write()
    TRE = toytree.io.read_newick(NWK)
    print(TRE.get_node_data())

    # write/read mrbayes NEXUS
    pass