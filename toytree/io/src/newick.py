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
- (str)str[Any]:float[Any]             # most complex

References
----------
- https://gist.github.com/Ad115/34dfc6560b64779a40c1a929f560511b
"""

from typing import (
    Optional, List, Any, Sequence, Tuple, Callable, Dict, Iterator, Set)
import re
from functools import partial
from loguru import logger
import numpy as np
from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError


logger = logger.bind(name="toytree")
PAIRS = {'(': '()', '[': '[]', '{': "{}"}
COLON_OUTSIDE_SQUARE_BRACKETS = re.compile(r'(?<!\[):|:(?!\])')
RESERVED_FEATURE_NAMES = ["idx", "height", "dist"]
NHX_ERROR = """\
Error parsing NHX (extended New Hampshire format) newick meta data.
  NHX format = "...[{{prefix}}{{key}}{{assign}}{{value}}{{delim}}{{key}}{{assign}}{{value}}...]"
  Your data snippet = "[{}]"
  parse args               your values           common entries
  -----------------------------------------------------------------
  feature_prefix           {:<8}              "", "&", "&&NXH:"
  feature_assignment       {:<8}              "=", ":"
  feature_delim            {:<8}              ",", ":"
Try modifying the parse args to match with your NHX meta data format.
"""


def _find_closing(string: str, start: int = 1, pair: Sequence[str] = '()') -> int:
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


def _iter_split_non_nested(node_str: str, delim: str = ",") -> Iterator[str]:
    """Generator of substrings between delimiter in a string.

    The delimiter does not split string if it occurs within a nested
    set: (), [], {}. This is used to parse node children, and also to
    parse NHX meta data, while avoiding really poorly formatted meta
    data (e.g., includes the delimiter) from messing things up.
    """
    final = len(node_str)
    start = 0
    end = 0
    while 1:

        # end and yield last chunk if at end of string
        if end == final:
            child = node_str[start:end]
            if child:
                yield child
            break

        # select the next character
        char = node_str[end]

        # if char is in "([{" then skip to next ")]}" respectively
        if char in PAIRS:
            pair = PAIRS[char]
            end = _find_closing(node_str, end + 1, pair)

        # split on delimiter not inside of nest and yield previous chunk
        elif char == delim:
            child = node_str[start:end]
            yield child
            start = end = end + 1
            # end += 1

        # advance if a data char
        else:
            end += 1


def _walk_newick_subtrees(
    newick: str,
    aggregator: Callable[[str, Any, float, Any], Any] = None,
    dist_formatter: Callable[[str], float] = None,
    feat_formatter: Callable[[str], Any] = None
) -> Tuple[Any, Set[str]]:
    """Recursive func (private) for extracting nested newick subtrees.

    The return type depends on the aggregator function.
    """
    # split first node from the newick string (inner)root[x]:dist[y];
    # leaving 'inner' which contains this Node's children.
    inner, label, dist, nmeta, emeta = _node_str_to_data(newick)

    # iterator of substrings split on ',' to separate children.
    # ""                  no children
    # ","                 two children w/ no info
    # ",,"                multiple children w/ no info
    # "a,b"               children with names
    # "a:3,b:4"           children w/ names and dist"
    # "a[...]:100[...]"   child w/ '' and meta
    # "(c,d),e"           subtree and child(ren) w or w/o stuff
    subtrees = _iter_split_non_nested(inner, delim=",")

    # iterate over subtrees calling this function recursively on each
    # and storing their data to their parent Node's child_data list.
    edge_features = set()
    child_data = []
    for child in subtrees:
        args = (aggregator, dist_formatter, feat_formatter)
        child_obj, features = _walk_newick_subtrees(child, *args)
        child_data.append(child_obj)
        edge_features.update(features)
        # edge_features |= features

    # str to float format the dist values
    distance = 1. if dist is None else dist_formatter(dist)

    # str to dict format the meta features
    nmeta = {} if nmeta is None else feat_formatter(nmeta)
    emeta = {} if emeta is None else feat_formatter(emeta)
    edge_features.update(set(emeta))
    # edge_features |= set(emeta)

    # aggegator func converts nested data to dict, Node, or other format.
    all_meta = {**nmeta, **emeta}
    # all_meta = nmeta | emeta  # dict merge operator '|' only py3.9+
    return aggregator(label, child_data, distance, all_meta), edge_features


def _node_str_to_data(newick: str) -> Tuple[str, str, str, str, str]:
    """Return data from a Node string (inner, label, dist, nmeta, emeta)

    """
    # split this node from the rest of tree.
    if newick.startswith("("):
        eidx = _find_closing(newick)
        outer = newick[eidx + 1:]
        inner = newick[1: eidx]
    else:
        outer = newick
        inner = ""

    # extract info from Node and Edge if ":" occurs outside sq brackets
    # label:          -> (label, None)
    # label[anno]:    -> (label, anno)
    # [anno]:         -> ('', anno)
    parts = list(_iter_split_non_nested(outer, delim=":"))
    if len(parts) > 1:
        node, edge = parts
        label, nmeta = _split_label_and_meta(node)
        dist, emeta = _split_label_and_meta(edge)

    # special for awful mrbayes format root edge anno w/o ':' delimiter
    # [anno1][anno2]  -> ('', anno1)
    elif "][" in outer:
        node, edge = outer.split("][")
        label, nmeta = _split_label_and_meta(node + "]")
        dist, emeta = None, None

    # label           -> (label, None)
    # label[anno]     -> (label, anno)
    # ''              -> ('', None)
    # [anno]          -> ('', anno)
    else:
        label, nmeta = _split_label_and_meta(outer)
        dist, emeta = None, None
    return inner, label, dist, nmeta, emeta


def _split_label_and_meta(substring: str) -> Tuple[str, str]:
    """Return tuple with (label, meta) given an outer newick substring."""
    for i, j in enumerate(substring):
        if j in "[:":
            return substring[:i], substring[i + 1: -1]
    return substring, None


def distance_parser(dist: str) -> Optional[float]:
    """Default float distance parser and formatter."""
    return float(dist)


def meta_parser(
    features: str,
    prefix: str = "",
    delim: str = ",",
    assignment: str = "=",
) -> Dict[str, str]:
    """Return a dict with auto-formatted features.

    When using this 'auto' function the dtype of features will be
    inferred later by toytree inside of the 'parse_newick' function,
    based on the str values for each feature across all Nodes. For
    example, if all can converted to floats or ints they will be.

    This will return {} if no features present.

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
    # remove the prefix (e.g., &&NHX:) and check that prefix was not
    # entered wrongly.
    #   [x=3]
    #   [&x=3]       amp can appear within metadata
    #   [&&NHX:x=3]  colons can appear within metadata.
    feats = features.lstrip(prefix)

    # return empty dict if no meta data present
    if not feats:
        return {}

    # split on feature separator
    items = _iter_split_non_nested(feats, delim)

    # store map of feature names to values
    meta = {}

    # iterate over items splitting to key,val pairs on assignment
    # splitter and attempting to convert to float.
    try:
        for item in items:
            # accommodate simplest NHX as in the example of RaxmlBipartitionsBranchLabels
            # format which has only [value], with no prefix, delim, or assignment
            if assignment not in item:
                key = "label"
                value = item
            # else parse it as you would normally expect, e.g., [...key=value...]
            else:
                key, value = item.split(assignment)

            # try to treat the value as numeric, else default to str
            try:
                meta[key] = float(value)
            except ValueError:
                meta[key] = str(value)
    except ValueError as exc:
        msg = NHX_ERROR.format(
            features,
            *(f"\"{i}\"" for i in (prefix, assignment, delim))
        )
        logger.error(msg)
        raise ToytreeError(msg) from exc
    return meta


def parse_newick_string_custom(
    newick: str,
    dist_formatter: Callable[[str], float] = None,
    feat_formatter: Callable[[str], Dict[str, Any]] = None,
    aggregator: Callable[[str, List[Node], float, Any], Node] = None,
    internal_labels: Optional[str] = None,
) -> Tuple[ToyTree, List[str]]:
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
    `toytree.tree`, `toytree.io`

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
    # raise exception if semicolon is missing then strip it.
    newick = newick.strip()
    assert newick.endswith(";"), "newick string must end with ';'"
    newick = newick[:-1]

    # raise exception if parentheses are imbalanced
    if newick.count("(") != newick.count(")"):
        raise ToytreeError("Newick string parentheses are imbalanced")

    # select formatting functions
    if feat_formatter is None:
        feat_formatter = meta_parser
    if dist_formatter is None:
        dist_formatter = distance_parser
    if aggregator is None:
        aggregator = node_aggregator

    # build the connected Nodes from newick w/ features saved.
    args = (newick, aggregator, dist_formatter, feat_formatter)
    treenode, edge_features = _walk_newick_subtrees(*args)

    # set default root dist to 0 (Note: other Node's w/o dist default=1.)
    treenode._dist = 0.

    # convert connected Nodes to a ToyTree
    tree = ToyTree(treenode)

    # set edge features to ensure proper polarization if re-rooted
    tree.edge_features.update(edge_features)

    # infer whether labels on internal nodes are names or supports
    tree = _infer_internal_label_type(tree, internal_labels)

    # return the final tree
    return tree


# default aggregator in `parse_newick_string_custom`
def node_aggregator(
    label: str,
    children: List[Node],
    distance: float,
    features: Dict[str, Any],
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

    # if any metadata annotations (e.g., [&x=3]) store as features
    for key, value in features.items():
        if key in RESERVED_FEATURE_NAMES:
            key = f"__{key}"
            # logger.warning(f"NHX feature name {key} is reserved and has been changed to __{key}")
        setattr(node, key, value)
    return node


def _dict_aggregator(label, children, distance, features):
    """Not Used, only for testing."""
    return dict(
        label=label,
        children=children,
        features=(distance, features)
    )


def _infer_internal_label_type(tree: ToyTree, internal_labels: Optional[str]) -> ToyTree:
    """Return a ToyTree with Node 'name' and 'support' updated.

    Check type of 'name' labels on internal Nodes. If all are numeric
    then save them as 'support' values instead of 'name' values.
    Changes are made to the Nodes in-place.
    """
    # if support set as numeric type
    if internal_labels == "support":
        for idx in range(tree.ntips, tree.nnodes):
            node = tree[idx]
            try:
                node.support = float(node.name)
            except ValueError:
                node.support = np.nan
            node.name = ""

    # if user entered a diff name then use that
    elif isinstance(internal_labels, str):
        for idx in range(tree.ntips, tree.nnodes):
            node = tree[idx]
            setattr(node, internal_labels, node.name)
            if internal_labels != "name":
                node.name = ""

    # infer types, any errors cause internal labels to be str names.
    # To save support values there must be a numeric label for every
    # internal non-root Node.
    else:  # elif internal_labels is None:
        try:
            # try to convert all internal node 'names' to floats (raises ValueError if str)
            names = [i.name for i in tree[tree.ntips:-1]]
            supports = [float(i.name) for i in tree[tree.ntips:-1]]

            # try to convert floats to ints if no floating points
            if all(i.is_integer() for i in supports):
                supports = [int(i) for i in supports]

            # store internal node values as 'support' and set 'name' to empty.
            for idx, inode in enumerate(tree[tree.ntips:-1]):
                inode.support = supports[idx]
                inode.name = ""

            # root Node is likely empty, but may have a name or even support
            # value. If so, we will try to store it numeric first, then string.
            tree.treenode.support = np.nan
            if not tree.treenode.name:
                tree.treenode.name = ""
            else:
                try:
                    tree.treenode.support = float(tree.treenode.name)
                    if tree.treenode.support.is_integer():
                        tree.treenode.support = int(tree.treenode.support)
                    tree.treenode.name = ""
                except ValueError:
                    pass

        # internal Node labels are inferred to be string name labels or other.
        except ValueError:
            if any(names):
                logger.info(
                    "empty or non-numeric node labels detected and set "
                    "as 'name' feature, not 'support'")
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
    # set default args to the feature parser (NHX)
    feat_formatter = partial(
        meta_parser,
        prefix=feature_prefix,
        delim=feature_delim,
        assignment=feature_assignment,
    )

    # parse tree using custom func with custom subfuncs
    tree = parse_newick_string_custom(
        newick=newick,
        feat_formatter=feat_formatter,
        dist_formatter=distance_parser,
        aggregator=node_aggregator,
        internal_labels=internal_labels,
    )
    return tree


def test1():
    NWK = "((a,b)Name[&&&x=3,z=0]:30[&&&length=3,y=4],c);"
    print(NWK)
    TREE = parse_newick_string_custom(NWK)
    print(TREE.get_node_data())


def test2():
    NWK = "((a,b)Name[&&&x=3,z=0]:30[&&&length=3,y=4],c[&&&height=10]);"
    print(NWK)
    TREE = parse_newick_string(NWK, feature_prefix="&&&")
    print(TREE.get_node_data())


def test3():
    import toytree
    NWK = """
(((ADH2:0.1[&&NHX:S=human:E=1.1.1.1],
ADH1:0.11[&&NHX:S=human:E=1.1.1.1]):0.05[&&NHX:S=Primates:E=1.1.1.1:D=Y:B=100],
ADHY:0.1[&&NHX:S=nematode:E=1.1.1.1],
ADHX:0.12[&&NHX:S=insect:E=1.1.1.1]):0.1[&&NHX:S=Metazoa:E=1.1.1.1:D=N],
(ADH4:0.09[&&NHX:S=yeast:E=1.1.1.1],ADH3:0.13[&&NHX:S=yeast:E=1.1.1.1],
ADH2:0.12[&&NHX:S=yeast:E=1.1.1.1],
ADH1:0.11[&&NHX:S=yeast:E=1.1.1.1]):0.1[&&NHX:S=Fungi])[&&NHX:E=1.1.1.1:D=N];
ADH1:0.11[&&NHX:S=yeast:E=1.1.1.1]):0.1[&&NHX:S=Fungi])[&&NHX:E=1.1.1.1:D=N];
"""
    # print(NWK)
    t = toytree.tree(NWK, feature_delim=":", feature_prefix="&&NHX:", feature_assignment="=")
    print(t.get_node_data())


def test4():
    import toytree
    NWK = "((C,D)1,(A,(B,X)3)2,E)R;"
    print(toytree.tree(NWK).get_node_data())
    print(toytree.tree(NWK, internal_labels='name').get_node_data())


if __name__ == "__main__":

    test2()
    # test3()
    # test4()
    # print(meta_parser("&A=100", prefix="&", delim="", assignment="="))
    # print(meta_parser("100", prefix=""))
