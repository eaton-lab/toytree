#!/usr/bin/env python

"""Write trees to newick or nexus formats.

Performs a `tree_reduce` operation to recursively condense the
tree structure into a nested string in parenthetical format, i.e.,
NEWICK format. This can optionally be wrapped with additional
information as a NEXUS formatted file.

References
----------
- https://gist.github.com/Ad115/fbee7a7a85935888d383f05b7f99e956

"""

from typing import Optional, Tuple, Collection
from loguru import logger
from toytree.core.tree2 import ToyTree
from toytree.core.node import Node

logger = logger.bind(name="toytree")


def get_feature_string(
    node: Node,
    features: Collection[str],
    features_prefix: str,
    features_delim: str,
    features_assignment: str,
    ) -> str:
    """Return a string of commented features inside square brackets."""
    if not features:
        return ""
    pairs = []
    for feature in features:
        value = str(getattr(node, feature))
        pairs.append(features_assignment.join((feature, value)))
    feature_str = features_delim.join(pairs)    
    return f"[{features_prefix}{feature_str}]"

def node_to_newick(
    node: Node,
    children: Tuple[Node],
    dist_formatter: str = "%.6g",
    internal_labels: Optional[str] = "support",
    internal_labels_formatter: Optional[str] = "%.6g",
    features: Optional[Collection] = None,
    features_prefix: str = "&",
    features_delim: str = ",",
    features_assignment: str = "=",
    ):
    """Reduce function used in tree_reduce"""
    # format the comment feature string for extra features
    feature_str = get_feature_string(
        node, features, features_prefix, features_delim, features_assignment)

    # format the dist values (edge lengths) as strings
    if dist_formatter is None:
        dist = ""
    else:
        dist = ":" + dist_formatter % node.dist

    # format the internal label feature (usually support, name, or "")
    if internal_labels is None:
        internal = ""
    else:
        internal = getattr(node, internal_labels, "")
        try:
            internal = internal_labels_formatter % internal
        except TypeError:
            internal = str(internal)

    # return the node formatted as newick
    if node.is_leaf():
        return f"{node.name}{dist}{feature_str}"
    return f"({','.join(children)}){internal}{dist}{feature_str}"

def tree_reduce(
    node: Node,
    dist_formatter: str = "%.6g",
    internal_labels: Optional[str] = "support",
    internal_labels_formatter: Optional[str] = "%.6g",
    features: Optional[Collection] = None,
    features_prefix: str = "&",
    features_delim: str = ",",
    features_assignment: str = "=",
    ) -> str:
    """Return newick string of ToyTree.

    Recursive function to get formatted newick string of tree data.
    See `write_newick` for docstring.
    """
    args = [
        dist_formatter, internal_labels, internal_labels_formatter,
        features, features_prefix, features_delim, features_assignment,
    ]
    reduced_children = [tree_reduce(child, *args) for child in node.children]
    newick = node_to_newick(node, reduced_children, *args)
    return newick

def write_newick(
    tree: ToyTree,
    path: Optional[str] = None,
    dist_formatter: str = "%.6g",
    internal_labels: Optional[str] = "support",
    internal_labels_formatter: Optional[str] = "%.6g",    
    features: Optional[Collection] = None,
    features_prefix: str = "&",
    features_delim: str = ",",
    features_assignment: str = "=",
    **kwargs,
    ) -> Optional[str]:
    """Write newick.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree instance to write as a newick string.
    path: str or None
        A filepath to write to file, or None to return newick string.
    dist_formatter: str or None
        A formatting string to format float dist values (edge lengths),
        or None to not write dist values. Default is "%.6g".
    internal_labels: str or None
        A feature to write as internal node labels. The 'support' 
        feature is the default, and often used here, but 'name' is 
        sometimes used as well. Any feature can be selected, or None
        to not write internal labels.
    internal_labels_formatter: str or None
        A formatting string to format internal labels. If an internal
        label cannot be formatted due to TypeError (e.g., you select
        'name' for `internal_labels` but leave this optional at its
        default as a float formatter '%.6g', instead of str formatter)
        it will simply be converted to a string. 
    features: List[str]
        A list of additional features to write in the newick comment
        block. For example, features=["height"] will save heights.
    features_prefix: str
        A prefix character written to the start of newick comment 
        blocks. Typical values are "&" (default) or "&&NHX:".
    features_delim: str
        A character used to delimit features in the newick comment
        block. Default is ",".
    features_assignment: str
        A character used to separate feature keys and values. Default
        is "=". 

    See Also
    --------
    `write_nexus`
        Write tree newick string in a NEXUS format.
    `ToyTree.write`
        This function is available from ToyTree objects as `.write`.

    Examples
    --------
    >>> nwk = "((a:3[&state=1],b:3[&state=1])D:1[&state=1],c:4[&state=2])E:1[&state=1];"
    >>> tree = toytree.io.parse_newick(nwk, features_prefix="&")
    >>> tree.write()
    >>> # ((a:3,b:3)100:1,c:4)100:1
    >>> tree.write(dist_formatter=None)
    >>> # ((a,b)100,c)100
    >>> tree.write(internal_label=None)
    >>> # ((a:3,b:3):1,c:4):1
    >>> tree.write(internal_labels="name")
    >>> # ((a:3,b:3)D:1,c:4)E:1
    >>> tree.write(features=["size"])
    >>> # ((a:3[&state=1],b:3[&state=1])100:1[&state=1],c:4[&state=2])100:1[&state=1]
    """
    if kwargs:
        logger.error(
            "toytree write option {} is deprecated, see updated docs.")

    newick = tree_reduce(
        tree.treenode,
        dist_formatter,
        internal_labels,
        internal_labels_formatter,        
        features,
        features_prefix,
        features_delim,
        features_assignment,
    ) + ";"
    if path is not None:
        with open(path, 'w', encoding="utf-8") as out:
            out.write(newick)
            return None
    return newick


def write_nexus(tree, **kwargs):
    """

    See Also
    ---------
    `write_newick`
    """


if __name__ == "__main__":

    import toytree
    nwk = "((a:3[&state=1],b:3[&state=1])D:1[&state=1],c:4[&state=2])E:1[&state=1];"
    tree = toytree.io.parse_newick(nwk)
    tree = tree.set_node_data("support", default=100)

    print(write_newick(tree))
    print(write_newick(tree, dist_formatter=None))    
    print(write_newick(tree, internal_labels=None))
    print(write_newick(tree, internal_labels="name"))
    print(write_newick(tree, features=["state"]))
