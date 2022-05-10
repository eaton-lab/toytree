#!/usr/bin/env python

"""Newick parsing functions.

The core functions here are `parse_newick_string` and 
`parse_newick_string_custom`. The latter can can take custom parsing
functions as input, making it very powerful and flexible, but a bit 
complex for the average user; the `parse_newick_string` function 
offers a simpler interface that should be sufficient for parsing 
most newicks. These funcs are used internally in the generic 
parsing function `toytree.tree`.

Supported formats
-----------------
- ((a,b),c);                           # topology only
- ((a:3,b:3):4,c:1);                   # w/ edge lengths
- ((a:3,b:3)100:4,c:1)100;             # w/ edge lengths and supports
- ((a:3,b:3)D:4,c:1)E;                 # w/ internal names
- ((a:3,b:3)D:4[&prob=100],c:1);       # w/ comment metadata on edges
- ((a:3,b:3)D[&prob=1]:4[&len=4],c:1); # w/ comments on edges and nodes!

References
----------
- https://gist.github.com/Ad115/34dfc6560b64779a40c1a929f560511b
"""

from typing import Optional, List, Any, Sequence, Tuple, Callable, Dict
from functools import partial
from loguru import logger
import numpy as np
from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.utils import NewickError


logger = logger.bind(name="toytree")
PAIRS = {'(': '()', '[': '[]'}


def _find_closing(
    string: str,
    start: int = 1,
    pair: Sequence[str] = '()',
    ) -> int:
    """Find index of next unmatched closing parenth from start position.

    Examples
    --------
    >>> newick = '((),())()'
    >>> _find_closing(newick, start=1, pair='()')  # 6
    >>> _find_closing(newick, start=2, pair='()')  # 2

    Parameters
    ----------
    string: str
        The newick string.
    start: int
        Index starting position in the newick string.
    pair: str
        Allows to specify different opening/closing str types as a pair.
    """
    # get the delimiters
    opening, closing = pair

    # get index of next ')'
    close_idx = string.index(closing, start)

    # if there is no more '(' then return the next ')' index
    if string.find(opening, start) == -1:
        return close_idx

    # get index of next '('
    next_open_idx = string.index(opening, start)

    # if the next '(' is past the next ')' return ')' index
    if close_idx < next_open_idx:
        return close_idx

    # else, find next closure from next opening index, repeat recursively
    skip = _find_closing(string, next_open_idx + 1, pair)
    return _find_closing(string, skip + 1, pair)


def _find_parts_of_subtree(newick: str, delim: str=",") -> Tuple[str,str,str,str]:
    """Extract information for a subtree Node from newick.

    The newick must already be formatted so that any extra metadata
    is stored only in square-brackets, not in curly brackets or other
    unexpected character formats.

    Parameters
    ----------
    newick: str
        The input newick substring representing part of the tree.
    delim: str
        If comment blocks are embedded at both edges and nodes, this
        will combine them into one block, and delimit them using the
        selected character.

    Example
    -------
    >>> nwk = "((a:1,b:2)0.99:3[a=3,b=(a-b)],(c:1,d:1)0.90:3)0.66:1;"
    >>> children, *x = _find_parts_of_subtree(nwk)
    >>> print(children, '->', x)
    >>> # (a:1,b:2)0.99:3[a=3,b=(a-b)],(c:1,d:1)0.90:3 -> ['0.66', '1;', '']
    """
    children = ""

    # if Node has children split children off to get just this node
    if newick.startswith("("):
        children_end = _find_closing(newick)
        children = newick[1: children_end]
        remaining = newick[children_end + 1:]
    else:
        remaining = newick

    # extract all comment data inside of square brackets
    comment = ""
    if "[" in remaining:

        # if only one comment bracket is present
        bracket_count = remaining.count("[")
        if bracket_count == 1:
            remaining, comment = remaining.split("[", maxsplit=1)
            comment = comment[:-1]

            # extract label and length (dist) from before/after ':'
            if ":" in remaining:
                label, length = remaining.split(":", maxsplit=1)
            else:
                label, length = remaining, '1.0'

        # if two comment brackets are present then ":" must be present.
        # "Label[&comment1=3]:100[&comment2=3]"
        # FIXME: but mb format is "Label[&comment1=3][&comment2=3]"
        elif bracket_count == 2:
            label_and, length_and = remaining.split(":", maxsplit=1)
            label, comment1 = label_and.split("[", maxsplit=1)
            comment1 = comment1[:-1]
            length, comment2 = length_and.split("[", maxsplit=1)
            comment2 = comment2[:-1]
            comment = comment1 + delim + comment2
        else:
            raise NewickError("Comment bracket format not recognized.")

    # no comments, just get label and length
    else:
        if ":" in remaining:
            label, length = remaining.split(":", maxsplit=1)
        else:
            label, length = remaining, '1.0'

    # return as a tuple
    return children, label.strip(), length, comment


def _find_next_node_end(nodes_str: str) -> int:
    """Return index of the final position of the first node in newick.

    Examples
    --------
    >>> node1 = '(A:1,(C[x],D))name:1.[c], (X,Y),,[xxx]'
    >>> node2 = '(X,Y),,[xxx]'
    >>> node3 = '[xxx'
    >>> _find_next_node_end(node1)  # 23
    >>> _find_next_node_end(node2)  # 5
    >>> _find_next_node_end(node3)  # 4
    """
    # e.g., '(A:1,(C[x],D))name:1.[c], (X,Y),,[xxx]'
    nodes_str = nodes_str.strip()

    # get closing index, skipping children
    current_end = 0
    if nodes_str.startswith('('):
        current_end = _find_closing(nodes_str)

    # skip label, dist, and comments (!commas can be in comments!)
    # find the next comma that is not surrounded by brackets or
    # parentheses or the end of the string
    while current_end < len(nodes_str):

        # get character at current index
        char = nodes_str[current_end]

        # advance current_end to after next ")" or "]"
        if char in PAIRS:
            current_end = _find_closing(nodes_str, current_end + 1, PAIRS[char])
            continue

        # found a comma, return its position
        if char == ',':
            return current_end - 1

        # found nothing, advance
        current_end += 1

    # reached the end
    return len(nodes_str) - 1


def _split_subtree(nodes_str: str) -> List[str]:
    """Separate a subtree from a newick string.

    Examples
    --------
    >>> nodes = '(a,b), , :12, c[xxx]'
    >>> split_nodes(nodes)  # ['(a,b)', '', ':12', 'c[xxx]']
    """
    nodes_str = nodes_str.strip()

    # if simple, return empties, or (subtree, rest), or recurse.
    if nodes_str == '':
        return []
    if nodes_str == ',':
        return ['', '']
    if nodes_str.startswith(','):
        rest = nodes_str[1:]
        return [''] + _split_subtree(rest)
    if nodes_str.endswith(','):
        rest = nodes_str[:-1]
        return _split_subtree(rest) + ['']

    # or, find node ending and split to return (subtree, rest)
    next_node_end = _find_next_node_end(nodes_str)
    node = nodes_str[:next_node_end+1]
    rest = nodes_str[next_node_end+1:].lstrip()
    if rest.startswith(','):
        rest = rest[1:]
    return [node] + _split_subtree(rest)


def distance_parser(dist: str) -> Optional[float]:
    """Default float distance parser and formatter.
    """
    return float(dist) if dist else 1.0


def feature_parser(
    feats: str, prefix="", delim=",", assignment="=") -> Dict[str, str]:
    """Return a dict with auto-formatted features.

    When using this 'auto' function the dtype of features will be 
    inferred later by toytree inside of the 'parse_newick' function,
    based on the str values for each feature across all Nodes. For 
    example, if all can converted to floats or ints they will be.

    This will return {} if no features present.

    Note
    ----
    problems arise when comma is delim and is also present inside the
    values of some features, such as a set {1.0,1.3}. Requires the
    data to be pre-cleaned to some extent...

    Parameters
    ----------
    feats: str
        A feature string extracted from the newick data. 
    prefix: str
        A string prefix in feats, often starting with '&'.
    delim: str
        A string delimiter between features in the feature string.
    assignment: str
        A string assignment character located between keys and values
        in the feature string.
    """
    # remove the prefix (e.g., &&NHX:)
    feats = feats[len(prefix):]
    if not feats:
        return {}

    # split on feature separator
    items = feats.split(delim)

    # store map of feature names to values
    features = {}

    # iterate over items splitting to key,val pairs on assignment splitter
    for item in items:
        try:
            key, value = item.split(assignment)
        except ValueError as inst:
            msg = (
                "Failed to parse newick format.\n"
                "Try using `toytree.io.parse_newick` with different "
                "options."
            ) 
            logger.error(msg)
            raise NewickError(msg) from inst
        features[key] = str(value)
    return features


def node_aggregator(
    label: str,
    children: List[Node],
    distance: float,
    features: Dict[str,Any],
    ) -> Node:
    """Aggregator function to connect Nodes and add features.

    Example of expected newick format: ((a:10,b:10)100:20, c:30);
    This tree contains 5 nodes, a, b, c, and two unlabeled nodes,
    the (a,b) ancestor, and the root. Their dists are 10, 10, 110,
    30, and default (0). The (a,b) ancestor has a label of '100',
    which could be interpreted as either a node str 'name', or as a
    node int 'support' value. This is a problem.
    """
    node = Node(name=label)
    node._dist = distance
    for child in children:
        node._add_child(child)
    for key, value in features.items():
        setattr(node, key, value)
    return node


def _dict_aggregator(label, children, distance, features):
    """Not Used, only for testing."""
    return dict(
        label=label,
        children=children,
        features=(distance, features)
    )


def _parse_newick_subtree(
    newick: str,
    aggregator = None, #: Callable[[str, List[Node], float, Any], Node] = None,  # This one works.
    dist_formatter = None, #: Callable[str, float] = None,
    feat_formatter = None, #: Callable[str, Any] = None  # FIXME: error on py3.8 'args must be a list.'
    ) -> Node:
    """Recursive func (private) for building Nodes from newick subtrees.

    See parse_newick
    """
    # split first node from the newick string
    children, label, dist, feats = _find_parts_of_subtree(newick.strip())

    # call this func recursive on children to return children as Nodes
    child_nodes = []
    for subtree in _split_subtree(children):
        child = _parse_newick_subtree(subtree, aggregator, dist_formatter, feat_formatter)
        child_nodes.append(child)

    # formatting of distances and features
    distance = dist_formatter(dist)
    features = feat_formatter(feats)

    # convert this node data into a Node and return
    return aggregator(label, child_nodes, distance, features)


def _check_internal_label_for_name_or_support(
    tree: ToyTree, internal_labels: Optional[str]) -> ToyTree:
    """Return a ToyTree with Node 'name' and 'support' updated.

    Check type of 'name' labels on internal Nodes. If all are numeric
    then save them as 'support' values instead of 'name' values.
    Changes are made to the Nodes in-place.
    """
    if internal_labels == "support":
        for idx in range(tree.ntips, tree.nnodes):
            node = tree[idx]
            try:
                node.support = float(node.name)
            except ValueError:
                node.support = np.nan
            node.name = ""

    # NOTE: first written to not check the root b/c root might not 
    # have support values, but strange example makes me question this...

    # infer types, any errors cause internal labels to be str names.
    elif internal_labels is None:
        try:
            # record whether we convert to int or float
            dtype = str

            # is root value present?
            rootval = tree.treenode.name != ""

            # check all node values except root if root is absent ("")
            inodes = range(tree.ntips, tree.nnodes - (1 if not rootval else 0))

            # get all internal node 'name' values 
            supports = (tree[i].name for i in inodes)
                
            # try to convert all to floats (raises an error if str)
            supports = [float(i) for i in supports]

            # try to convert floats to ints if no floating points
            if all(i.is_integer() for i in supports):
                supports = [int(i) for i in supports]
                dtype = int
            else:
                dtype = float

            # convert 'name' features to 'support' for internal nodes.
            for idx, nidx in enumerate(inodes):
                tree[nidx].support = supports[idx]
                tree[nidx].name = ""

            # if rootval is absent then set to a default value, using
            # either 100 or 1.0 as default support based on others.
            if not rootval:
                default = 100 if max(supports) > 1 else 1.0
                tree.treenode.support = dtype(default)
                tree.treenode.name = ""
        except ValueError:
            pass
    return tree


def parse_newick_string_custom(
    newick: str,
    dist_formatter = None, #: Callable[str, float] = None, # FIXME
    feat_formatter = None, #: Callable[str, Dict[str,Any]] = None,
    aggregator = None, #: Callable[[str, List[Node], float, Any], Node] = None,
    internal_labels: Optional[str] = None,
    ) -> ToyTree:
    """Return a ToyTree from a newick string.

    Recursive function to build connected Nodes from nested data in 
    newick format, and return as a ToyTree. Features parsed from the
    newick can be formatted with a custom formatter function, or using
    the default auto-formatting, which aims to infer the proper dtype
    based on the data.

    For high-level usage of this function users must write their own
    custom parsing functions. However, to provide a simpler option, 
    most popular formats can be parsed using a builtin option from
    the toytree function `toytree.tree`.

    See Also
    --------
    `toytree.tree`, `totyree.io`

    Parameters
    ----------
    dist_formatter: Callable
        A custom function for converting edge length data into a float
        or int value to be stored as the .dist attribute of Nodes.
        e.g., `dist_formatter=lambda x: round(x / 100, 2)` to store 
        as a rounded float with two floating points.
    feat_formatter: Callable
        A custom function for parsing newick string metadata to Node 
        feature data. An example is NHX (extended newick) format, or 
        similar formats like used by mrbayes. If no function here then
        the entire metadata is stored as a string as feature "feature".
        The function should return a Dict[str,Any]. 
        >>> def feat_parser(feats, prefix='&NHX:, delim=',', assign='='):
        >>>     feats = feats[len(prefix)]
        >>>     items = feats.split(delim)
        >>>     return dict(zip(items.split(assign)))
        See docs for more examples. The default feat_formatter is 
        similar to above but tries to infer value types.
    aggregator: Callable
        A custom function that takes (name, children, dist, features)
        and returns a Node object. This is used to recursively build 
        the Node objects from tuples of extracted newick data.
    internal_labels: str or None
        Feature type of internal labels. If None it is inferred to be
        either 'name' or 'support' based on numeric or string types
        being present.
    """
    newick = newick.strip()
    assert newick.endswith(";"), "newick string must end with ';'"
    newick = newick[:-1]

    # select formatting functions
    if feat_formatter is None:
        feat_formatter = feature_parser
    if dist_formatter is None:
        dist_formatter = distance_parser
    if aggregator is None:
        aggregator = node_aggregator

    # build the connected Nodes from newick w/ features saved.
    treenode = _parse_newick_subtree(newick, aggregator, dist_formatter, feat_formatter)

    # convert to a tree
    tree = ToyTree(treenode)

    # check whether labels on internal nodes are names or supports
    tree = _check_internal_label_for_name_or_support(tree, internal_labels)

    # return the final tree
    return tree


def parse_newick_string(
    newick: str,
    feature_prefix: str = "&",
    feature_delim: str = ",", 
    feature_assignment: str = "=",
    internal_labels: Optional[str] = None,
    ) -> ToyTree:
    """Return a ToyTree from a newick string.

    Recursive function to build connected Nodes from nested data in 
    newick format, and return as a ToyTree. Features parsed from the
    newick can be formatted with a custom formatter function, or with
    the default auto-formatting, which aims to infer the proper dtype
    based on the data.

    For high-level usage of this function users must write their own
    custom parsing functions. However, to provide a simpler option, 
    most popular formats can be parsed using a builtin option from
    the toytree function `toytree.tree`.

    See Also
    --------
    `toytree.tree`, `totyree.io`, `toytree.io.parse_newick_custom`

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
    >>> tree1 = parse_newick_string(nwk1)
    >>> print(tree1.get_node_data())    
    >>> 
    >>> nwk2 = "((a:1,b:2)0.99:3,(c:1,d:1)0.90:3)0.66:1;"
    >>> tree2 = parse_newick_string(nwk2)
    >>> print(tree2.get_node_data())
    """
    feat_formatter = partial(
        feature_parser, 
        prefix=feature_prefix,
        delim=feature_delim,
        assignment=feature_assignment,
    )
    tree = parse_newick_string_custom(
        newick=newick,
        feat_formatter=feat_formatter,
        dist_formatter=distance_parser,
        aggregator=node_aggregator,
        internal_labels=internal_labels,
    )
    return tree


if __name__ == "__main__":

    # JSON example
    # import json
    # NWK = "((a,b)Name[x=3]:30[length=3],c);"
    # TREE = _parse_newick_subtree(
    #     NWK, 
    #     aggregator=_dict_aggregator,
    #     dist_formatter=distance_parser,
    #     feat_formatter=feature_parser,
    # )
    # print(json.dumps(TREE, indent=2))    

    # COMPLEX newick with two comment brackets
    NWK = "((a,b)Name[x=3]:30[length=3],c);"

    # TOYTREE custom example
    TREE = parse_newick_string_custom(NWK)
    print(TREE.get_node_data())

    # TOYTREE simple example
    TREE = parse_newick_string(NWK, feature_prefix="")
    print(TREE.get_node_data())
