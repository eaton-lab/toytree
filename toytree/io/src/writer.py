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

from typing import Optional, Tuple, Sequence, TypeVar
import numpy as np
from loguru import logger
from toytree.utils import ToytreeError

Node = TypeVar("Node")
ToyTree = TypeVar("ToyTree")
DISALLOWED_FEATURES = set(['idx', 'dist', 'up', 'children'])  # 'support', 'height'])
logger = logger.bind(name="toytree")


def get_feature_string(
    node: Node,
    features: Sequence[str],
    features_prefix: str,
    features_delim: str,
    features_assignment: str,
    internal_labels_formatter: str,
) -> str:
    """Return a string of commented features inside square brackets.

    Intended to handle formatting/serializeation of flexible object
    types that could be assigned to Nodes.
    """
    if not features:
        return ""
    pairs = []
    for feature in features:
        # get value or None if Node does not have the feature
        value = getattr(node, feature, None)

        # if no value then do not write it
        if value is None:
            continue

        # try to float format the value to a string
        try:
            if np.isnan(value):
                value = ""
            else:
                value = internal_labels_formatter % str(value)
        except TypeError:
            value = str(value)
        pairs.append(features_assignment.join((feature, value)))
    feature_str = features_delim.join(pairs)
    if not feature_str:
        return ""
    return f"[{features_prefix}{feature_str}]"


def node_to_newick(
    node: Node,
    children: Tuple[Node],
    dist_formatter: str = "%.12g",
    internal_labels: Optional[str] = "support",
    internal_labels_formatter: Optional[str] = "%.12g",
    node_features: Optional[Sequence[str]] = None,
    edge_features: Optional[Sequence[str]] = None,
    features_prefix: str = "&",
    features_delim: str = ",",
    features_assignment: str = "=",
) -> str:
    """Reduce function used in tree_reduce"""
    # format the comment feature string for extra features
    node_feature_str = get_feature_string(
        node,
        node_features,
        features_prefix,
        features_delim,
        features_assignment,
        internal_labels_formatter,
    )
    edge_feature_str = get_feature_string(
        node,
        edge_features,
        features_prefix,
        features_delim,
        features_assignment,
        internal_labels_formatter,
    )

    # format the dist values (edge lengths) as strings
    dist = "" if dist_formatter is None else ":" + dist_formatter % node.dist

    # format the internal label feature (usually support, name, or "")
    if internal_labels is None:
        internal = ""
    else:
        internal = getattr(node, internal_labels, "")
        if internal is None:
            internal = ""
        else:
            try:
                if np.isnan(internal):
                    internal = ""
                else:
                    internal = internal_labels_formatter % internal
            except TypeError:
                internal = str(internal)

    # tip node
    if node.is_leaf():
        return f"{node.name}{node_feature_str}{dist}{edge_feature_str}"

    # root node
    if node.is_root():
        if node.dist:
            return f"({','.join(children)}){internal}{node_feature_str}{dist}{edge_feature_str}"
        return f"({','.join(children)}){internal}{node_feature_str}"

    # other internal nodes
    return f"({','.join(children)}){internal}{node_feature_str}{dist}{edge_feature_str}"


def tree_reduce(
    node: Node,
    dist_formatter: str = "%.12g",
    internal_labels: Optional[str] = "support",
    internal_labels_formatter: Optional[str] = "%.12g",
    node_features: Optional[Sequence[str]] = None,
    edge_features: Optional[Sequence[str]] = None,
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
        node_features, edge_features,
        features_prefix, features_delim, features_assignment,
    ]
    reduced_children = [tree_reduce(child, *args) for child in node.children]
    newick = node_to_newick(node, reduced_children, *args)
    # logger.warning([node, newick])
    return newick


def write_newick(
    tree: ToyTree,
    path: Optional[str] = None,
    dist_formatter: str = "%.12g",
    internal_labels: Optional[str] = "support",
    internal_labels_formatter: Optional[str] = "%.12g",
    features: Optional[Sequence[str]] = None,
    features_prefix: str = "&",
    features_delim: str = ",",
    features_assignment: str = "=",
) -> Optional[str]:
    """Write tree to newick string and return or write to filepath.

    The newick string can be formatted in several ways. The default
    will include dist values (edge lengths) and support values as
    internal node labels. The edge lengths can be suppressed by
    setting `dist_formatter=None`, and internal node labels can be
    similarly suppressed, or set to store a different feature, such
    as internal node names. Additional features can be stored in the
    node comment blocks in extended-newick-format (NHX-like) by using
    the "features" arguments (see examples).

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
        Features that are in `.edge_features` will be written as NHX
        meta data for edges, while other features will be written as
        NHX meta data for nodes.
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
    >>> # example tree w/ support on all Nodes and X values on few Nodes
    >>> tree0 = toytree.rtree.unittree(4, seed=123)
    >>> tree0.set_node_data("support", default=100, inplace=True)
    >>> tree0.set_node_data("X", {"r0": 3, "r1": 4}, inplace=True)

    >>> # default arguments to write
    >>> tree0.write()
    >>> # '((r0:0.5,r1:0.5)100:0.5,(r2:0.5,r3:0.5)100:0.5)100;'

    >>> # write topology only
    >>> tree0.write(None, None, None)
    >>> # '(((r0,r1),r2),(r3,r4));'

    >>> # write internal labels (in this case 'support') only
    >>> tree0.write(path=None, dist_formatter=None, internal_labels="support")
    >>> # '((r0,r1)100,(r2,r3)100)100;'

    >>> # write branch lengths (dist values) only
    >>> tree0.write(path=None, dist_formatter="%.12g", internal_labels=None)
    >>> # '((r0:0.5,r1:0.5):0.5,(r2:0.5,r3:0.5):0.5);'

    >>> # write NHX format meta data (support and X features)
    >>> tree0.write(None, None, None, features=["support", "X"])
    """
    if features is None:
        features = []
    features = [features] if isinstance(features, str) else features
    features = set(features) - DISALLOWED_FEATURES
    bad_features = features - set(tree.features)
    if bad_features:
        raise ToytreeError(
            f"Cannot write features not present in tree: {bad_features}")
    node_features = {i for i in features if i not in tree.edge_features}
    edge_features = features - node_features

    newick = tree_reduce(
        tree.treenode,
        dist_formatter,
        internal_labels,
        internal_labels_formatter,
        node_features,
        edge_features,
        features_prefix,
        features_delim,
        features_assignment,
    ) + ";"
    if path is not None:
        with open(path, 'w', encoding="utf-8") as out:
            out.write(newick)
            return None
    return newick


def write_nexus(tree: ToyTree, path: Optional[str] = None, **kwargs):
    """Write tree newick string to NEXUS file format.

    This accepts the same arguments as `toytree.io.write_newick`.

    See Also
    ---------
    `toytree.io.write_newick`, `ToyTree.write`
    """
    newick = write_newick(tree, **kwargs)
    nexus = "#NEXUS\n"
    nexus += "begin trees;\n"
    rooted = "R" if tree.is_rooted() else "U"
    nexus += f"  tree 0 = [&{rooted}] {newick}\n"
    nexus += ";"
    if path is not None:
        with open(path, 'w', encoding="utf-8") as out:
            out.write(nexus)
            return None
    return nexus


if __name__ == "__main__":

    import toytree
    NWK = "((a:3[&state=1],b:3[&state=1])D:1[&state=1],c:4[&state=2])E:1[&state=1];"
    TREE = toytree.tree(NWK)
    # TREE = TREE.set_node_data("support", default=100)

    print(write_newick(TREE))
    print(write_newick(TREE, dist_formatter=None))
    print(write_newick(TREE, internal_labels=None))
    print(write_newick(TREE, internal_labels="name"))
    print(write_newick(TREE, features=["state"]))
    print(write_nexus(TREE, features=["state"]))

    TREE.set_node_data('test', {'a': 7.8, 4: 5}, inplace=True)
    TREE.set_node_data('support', default=100, inplace=True)
    print(TREE.edge_features)
    print(write_newick(TREE, internal_labels=None, features=["support", "test"]))
