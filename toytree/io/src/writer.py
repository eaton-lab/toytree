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

from typing import Optional, Tuple, Sequence, Callable
import numpy as np
from loguru import logger
from toytree.core import ToyTree, Node
from toytree.utils import ToytreeError
from toytree.core.apis import add_toytree_method

DISALLOWED_FEATURES = set(['idx', 'dist', 'up', 'children'])  # 'support', 'height'])
logger = logger.bind(name="toytree")


def get_float_formatter(formatting_str: str) -> Callable:
    """Return func to format string using % or {} notation.
    """
    if formatting_str is None:
        def formatter(x):
            return ""
    elif "%" in formatting_str:
        def formatter(x):
            return formatting_str % x
    elif formatting_str.startswith("{"):
        def formatter(x):
            return formatting_str.format(x)
    else:
        raise ValueError(
            "'features_formatter' is not a proper Python formatting str: "
            f"{formatting_str}")
    return formatter


def get_feature_string(
    node: Node,
    features: Sequence[str],
    features_prefix: str,
    features_delim: str,
    features_assignment: str,
    features_formatter: str,
) -> str:
    """Return a string of commented features inside square brackets.

    Intended to handle formatting/serializeation of flexible object
    types that could be assigned to Nodes.
    """
    if not features:
        return ""
    pairs = []

    # get float formatting function
    formatter = get_float_formatter(features_formatter)

    # check each feature
    for feature in features:
        # get value or None if Node does not have the feature
        value = getattr(node, feature, None)

        # if no value then do not write it
        if value is None:
            continue

        # try to convert to float and float format the value
        try:
            value = float(value)
            if np.isnan(value):
                value = ""
            else:
                value = formatter(value)
        except (TypeError, ValueError):
            value = str(value)

        # store if a value exists
        if value:
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
    features_formatter: str = "%.12g",
    names_as_ints: bool = False,
) -> str:
    """Reduce function used in tree_reduce"""
    # format the comment feature string for extra features
    node_feature_str = get_feature_string(
        node,
        node_features,
        features_prefix,
        features_delim,
        features_assignment,
        features_formatter,
    )
    edge_feature_str = get_feature_string(
        node,
        edge_features,
        features_prefix,
        features_delim,
        features_assignment,
        features_formatter,
    )

    # format the dist values (edge lengths) as strings
    dist_formatter = get_float_formatter(dist_formatter)
    dist = dist_formatter(node.dist)
    dist = dist if not dist else f":{dist}"

    # format the internal label feature (usually support, name, or "")
    label_formatter = get_float_formatter(internal_labels_formatter)
    if internal_labels is None:
        internal = ""
    else:
        internal = getattr(node, internal_labels, "")
        if internal is None:
            internal = ""
        else:
            try:
                internal = float(internal)
                if np.isnan(internal):
                    internal = ""
                else:
                    internal = label_formatter(internal)
            except (TypeError, ValueError):
                internal = str(internal)

    # tip node write N[meta]:E[emeta] if dist else N[nmeta]
    if node.is_leaf():
        if names_as_ints:
            if dist:
                return f"{node.idx}{node_feature_str}{dist}{edge_feature_str}"
            return f"{node.idx}{node_feature_str}"
        if dist:
            return f"{node.name}{node_feature_str}{dist}{edge_feature_str}"
        return f"{node.name}{node_feature_str}"

    # root node write N[nmeta] unless the root has dist then N[meta]:E[emeta]
    if node.is_root():
        if node.dist:
            return f"({','.join(children)}){internal}{node_feature_str}{dist}{edge_feature_str}"
        return f"({','.join(children)}){internal}{node_feature_str}"

    # other internal nodes write N[nmeta]:E[emeta] if dist else N[nmeta]
    if dist:
        return f"({','.join(children)}){internal}{node_feature_str}{dist}{edge_feature_str}"
    return f"({','.join(children)}){internal}{node_feature_str}"


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
    features_formatter: str = "%.12g",
    names_as_ints: bool = False,
) -> str:
    """Return newick string of ToyTree.

    Recursive function to get formatted newick string of tree data.
    See `write_newick` for docstring.
    """
    args = [
        dist_formatter, internal_labels, internal_labels_formatter,
        node_features, edge_features,
        features_prefix, features_delim, features_assignment,
        features_formatter,
        names_as_ints,
    ]
    reduced_children = [tree_reduce(child, *args) for child in node.children]
    newick = node_to_newick(node, reduced_children, *args)
    # logger.warning([node, newick])
    return newick


def wrap_nexus(tree: ToyTree, newick: str) -> str:
    """Wrap a newick string into NEXUS format.

    """
    nexus = "#NEXUS\n"
    nexus += "begin trees;\n"

    # add translation using idx
    nexus += "    translate\n"
    for node in tree[:tree.ntips]:
        nexus += f"        {node.idx} {node.name},\n"
    nexus += "    ;\n"

    # get rooting info
    rooted = "R" if tree.is_rooted() else "U"

    # write tree
    nexus += f"    tree 0 = [&{rooted}] {newick}\n"
    nexus += "end;"
    return nexus


@add_toytree_method(ToyTree)
def write(
    tree: ToyTree,
    path: Optional[str] = None,
    dist_formatter: Optional[str] = "%.12g",
    internal_labels: Optional[str] = "support",
    internal_labels_formatter: Optional[str] = "%.12g",
    features: Optional[Sequence[str]] = None,
    features_prefix: str = "&",
    features_delim: str = ",",
    features_assignment: str = "=",
    features_formatter: str = "%.12g",
    nexus: bool = False,
    **kwargs,
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
        A formatting string to format float dist values (edge lengths).
        Default is "%.12g". If None edge lengths are excluded.
    internal_labels: str or None
        A feature to write as internal node labels. None suppresses
        internal labels. Default is 'support', 'name' is also commonly
        used here, but any feature name can be selected.
    internal_labels_formatter: str or None
        A formatting string to format internal labels as floats.
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
    features_formatter: str or None
        A formatting string used for float feature metadata. Default
        is "%.12g".
    nexus: bool
        If True the tree data is nested in a "trees" block, names are
        translated to ints, and a #NEXUS header is included.

    See Also
    --------
    `ToyTree.write`
        This function is available from ToyTree objects as `.write`.

    Examples
    --------
    >>> # generate a tree with additional metadata
    >>> tree = toytree.rtree.baltree(ntips=4)
    >>> tree.set_node_data("name", {4: "A", 5: "B", 5: "C"}, inplace=True)
    >>> tree.set_node_data("support", {4: 100, 5: 90}, inplace=True)
    >>> tree.set_node_data("X", default=10, inplace=True)

    >>> # write tree to file path
    >>> tree.write(path="/tmp/test.nwk")

    >>> # return tree as str with various formatting options.
    >>> tree.write()
    >>> '((r0:0.5,r1:0.5)100:0.5,(r2:0.5,r3:0.5)90:0.5);'
    >>> tree.write(dist_formatter=None)
    >>> '((r0,r1)100,(r2,r3)90);'
    >>> tree.write(internal_labels=None)
    >>> '((r0:0.5,r1:0.5):0.5,(r2:0.5,r3:0.5):0.5);'
    >>> tree.write(internal_labels="name")
    >>> '((r0:0.5,r1:0.5)A:0.5,(r2:0.5,r3:0.5)C:0.5);'
    >>> tree.write(features=["X"])
    >>> '((r0[&X=10]:0.5,r1[&X=10]:0.5)100[&X=10]:0.5,(r2[&X=10]:...
    """
    if kwargs:
        logger.warning(f"Deprecated args to write(): {list(kwargs)}. See docs.")

    # separate node and edge features
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

    # build newick string from recursive
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
        features_formatter,
        names_as_ints=nexus,
    ) + ";"

    # optionally wrap as nexus
    treestr = wrap_nexus(tree, newick) if nexus else newick

    # write to file or return
    if path is not None:
        with open(path, 'w', encoding="utf-8") as out:
            out.write(treestr)
            return None
    return treestr


if __name__ == "__main__":

    import toytree
    NWK = "((a:3[&state=1],b:3[&state=1])D:1[&state=1],c:4[&state=2])E:1[&state=1];"
    TREE = toytree.tree(NWK)
    # TREE = TREE.set_node_data("support", default=100)

    print(write(TREE))
    print(write(TREE, dist_formatter=None))
    print(write(TREE, internal_labels=None))
    print(write(TREE, internal_labels="name"))
    print(write(TREE, features=["state"]))
    # print(write_nexus(TREE, features=["state"]))

    TREE.set_node_data('test', {'a': 7.8, 4: 5}, inplace=True)
    TREE.set_node_data('support', default=100, inplace=True)
    # print(TREE.edge_features)
    # print(write(TREE, internal_labels=None, features=["support", "test"], nexus=True))
    print(write(TREE, dist_formatter=None, features=["name", "support"]))


    TREE.write()
