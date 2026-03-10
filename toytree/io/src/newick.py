#!/usr/bin/env python

"""Parse Newick and extended Newick strings into `ToyTree` objects.

The public entry points are :func:`parse_newick_string` and
:func:`parse_newick_string_custom`. Both support plain Newick topology,
branch lengths, internal labels, and square-bracket metadata on nodes
or edges. Metadata can use simple ``&key=value`` comments or more
specialized NHX-like prefixes such as ``&&NHX:``.

The parser is iterative rather than recursive so deeply nested trees
can be parsed without hitting Python's recursion limit.
"""

from __future__ import annotations

import math
import re
import sys
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple

from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.utils.src.exceptions import ToytreeError

OPEN_TO_CLOSE = {"(": ")", "[": "]", "{": "}"}
CLOSE_TO_OPEN = {value: key for key, value in OPEN_TO_CLOSE.items()}
BLOCK_ERRORS = {
    "(": "Newick string parentheses are imbalanced",
    "[": "Newick string metadata blocks are imbalanced",
    "{": "Newick string curly trait blocks are imbalanced",
    ")": "Newick string parentheses are imbalanced",
    "]": "Newick string metadata blocks are imbalanced",
    "}": "Newick string curly trait blocks are imbalanced",
}
CURLY_TRAIT_PATTERN = re.compile(r"^(.*)\{([^{}]*)\}$")
RESERVED_FEATURE_NAMES = ["idx", "height", "dist"]
NHX_ERROR = (
    "Error parsing NHX (extended New Hampshire format) newick meta data.\n"
    "  NHX format = "
    '"...[{{prefix}}{{key}}{{assign}}{{value}}{{delim}}{{key}}{{assign}}{{value}}...]"\n'
    '  Your data snippet = "[{}]"\n'
    "  parse args               your values           common entries\n"
    "  -----------------------------------------------------------------\n"
    '  feature_prefix           {:<8}              "", "&", "&&NXH:"\n'
    '  feature_assignment       {:<8}              "=", ":"\n'
    '  feature_delim            {:<8}              ",", ":"\n'
    "Try modifying the parse args to match with your NHX meta data format.\n"
)


@dataclass
class _SubtreeBuilder:
    """Temporary storage for one subtree while scanning a Newick string."""

    children: Optional[List[Tuple[Any, Set[str]]]] = None
    payload_parts: List[str] = field(default_factory=list)


def _find_balanced_end(text: str, start: int, error_message: str) -> int:
    """Return the matching closing index for one nested block."""
    opener = text[start]
    expected = [OPEN_TO_CLOSE[opener]]
    idx = start + 1
    while idx < len(text):
        char = text[idx]
        if char in OPEN_TO_CLOSE:
            expected.append(OPEN_TO_CLOSE[char])
        elif char in CLOSE_TO_OPEN:
            if char != expected[-1]:
                raise ToytreeError(error_message)
            expected.pop()
            if not expected:
                return idx
        idx += 1
    raise ToytreeError(error_message)


def _iter_split_non_nested(text: str, delim: str = ",") -> Iterator[str]:
    """Yield chunks split on `delim` while ignoring nested blocks."""
    if not delim:
        yield text
        return

    start = 0
    idx = 0
    while idx < len(text):
        char = text[idx]
        if char in OPEN_TO_CLOSE:
            idx = _find_balanced_end(text, idx, BLOCK_ERRORS[char]) + 1
            continue
        if char in CLOSE_TO_OPEN:
            raise ToytreeError(BLOCK_ERRORS[char])
        if text.startswith(delim, idx):
            yield text[start:idx]
            idx += len(delim)
            start = idx
            continue
        idx += 1
    yield text[start:]


def _split_label_and_meta(text: str) -> Tuple[str, Optional[str]]:
    """Split one payload segment into label text and metadata text."""
    if not text:
        return "", None

    idx = 0
    while idx < len(text):
        char = text[idx]
        if char == "[":
            end = _find_balanced_end(text, idx, BLOCK_ERRORS[char])
            if end != len(text) - 1:
                raise ToytreeError(
                    "Newick metadata blocks must terminate node or edge data"
                )
            return text[:idx], text[idx + 1 : end]
        if char in "({":
            idx = _find_balanced_end(text, idx, BLOCK_ERRORS[char]) + 1
            continue
        if char in ")]}":
            raise ToytreeError(BLOCK_ERRORS[char])
        idx += 1
    return text, None


def _strip_root_edge_comment_without_colon(text: str) -> str:
    """Preserve historical handling of `[node][root-edge]` payloads."""
    idx = 0
    while idx < len(text):
        char = text[idx]
        if char == "[":
            first_end = _find_balanced_end(text, idx, BLOCK_ERRORS[char])
            next_idx = first_end + 1
            if next_idx < len(text) and text[next_idx] == "[":
                final = _find_balanced_end(text, next_idx, BLOCK_ERRORS["["])
                if final != len(text) - 1:
                    raise ToytreeError(
                        "Newick metadata blocks must terminate node or edge data"
                    )
                return text[: first_end + 1]
            return text
        if char in "({":
            idx = _find_balanced_end(text, idx, BLOCK_ERRORS[char]) + 1
            continue
        if char in ")]}":
            raise ToytreeError(BLOCK_ERRORS[char])
        idx += 1
    return text


def _node_str_to_data(
    payload: str,
) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
    """Return `(label, dist, node_meta, edge_meta)` for one subtree."""
    parts = list(_iter_split_non_nested(payload, delim=":"))
    if len(parts) > 2:
        raise ToytreeError("Newick node data contains multiple ':' separators")

    if len(parts) == 2:
        node_text, edge_text = parts
    else:
        node_text = _strip_root_edge_comment_without_colon(payload)
        edge_text = None

    label, node_meta = _split_label_and_meta(node_text)
    if edge_text is None:
        return label, None, node_meta, None

    dist, edge_meta = _split_label_and_meta(edge_text)
    return label, dist, node_meta, edge_meta


def distance_parser(dist: str) -> Optional[float]:
    """Parse one Newick branch-length token.

    Parameters
    ----------
    dist : str
        Branch-length text extracted from a Newick edge payload.

    Returns
    -------
    float
        Parsed floating-point edge length.

    Raises
    ------
    ValueError
        Raised if ``dist`` cannot be converted to ``float``.

    Examples
    --------
    >>> distance_parser("1.25")
    1.25

    See Also
    --------
    parse_newick_string
    parse_newick_string_custom
    """
    return float(dist)


def _coerce_meta_value(value: str) -> Any:
    """Return one metadata value coerced to float when possible."""
    sval = value.strip()
    try:
        return float(sval)
    except ValueError:
        return sval


def _meta_has_nested_blocks(text: str) -> bool:
    """Return True when metadata text includes nested block delimiters."""
    return ("{" in text) or ("[" in text) or ("(" in text)


def _meta_uses_braces_only(text: str) -> bool:
    """Return True when metadata nesting is limited to curly braces."""
    return ("{" in text) and ("[" not in text) and ("(" not in text)


def _split_ignoring_braces_single(text: str, delim: str) -> List[str]:
    """Split on a one-character delimiter while ignoring `{...}` blocks."""
    parts = []
    start = 0
    depth = 0
    for idx, char in enumerate(text):
        if char == "{":
            depth += 1
        elif char == "}":
            if depth == 0:
                raise ToytreeError(BLOCK_ERRORS[char])
            depth -= 1
        elif depth == 0 and char == delim:
            parts.append(text[start:idx])
            start = idx + 1
    if depth:
        raise ToytreeError(BLOCK_ERRORS["{"])
    parts.append(text[start:])
    return parts


def _split_non_nested_single(text: str, delim: str) -> List[str]:
    """Split on a one-character delimiter while skipping nested blocks."""
    parts = []
    start = 0
    idx = 0
    while idx < len(text):
        char = text[idx]
        if char in OPEN_TO_CLOSE:
            idx = _find_balanced_end(text, idx, BLOCK_ERRORS[char]) + 1
            continue
        if char in CLOSE_TO_OPEN:
            raise ToytreeError(BLOCK_ERRORS[char])
        if char == delim:
            parts.append(text[start:idx])
            start = idx + 1
        idx += 1
    parts.append(text[start:])
    return parts


def _split_meta_assignment_single(item: str, assignment: str) -> Tuple[str, str]:
    """Split one metadata item on a one-character assignment token."""
    split_idx = -1
    idx = 0
    while idx < len(item):
        char = item[idx]
        if char in OPEN_TO_CLOSE:
            idx = _find_balanced_end(item, idx, BLOCK_ERRORS[char]) + 1
            continue
        if char in CLOSE_TO_OPEN:
            raise ToytreeError(BLOCK_ERRORS[char])
        if char == assignment:
            if split_idx != -1:
                raise ValueError(item)
            split_idx = idx
        idx += 1

    if split_idx == -1:
        return "label", item
    return item[:split_idx], item[split_idx + 1 :]


def _split_meta_assignment_braces_single(item: str, assignment: str) -> Tuple[str, str]:
    """Split one metadata item on a one-character token outside braces."""
    split_idx = -1
    depth = 0
    for idx, char in enumerate(item):
        if char == "{":
            depth += 1
        elif char == "}":
            if depth == 0:
                raise ToytreeError(BLOCK_ERRORS[char])
            depth -= 1
        elif depth == 0 and char == assignment:
            if split_idx != -1:
                raise ValueError(item)
            split_idx = idx

    if depth:
        raise ToytreeError(BLOCK_ERRORS["{"])
    if split_idx == -1:
        return "label", item
    return item[:split_idx], item[split_idx + 1 :]


def _split_meta_assignment(item: str, assignment: str) -> Tuple[str, str]:
    """Split one metadata item into key and value text."""
    if not assignment:
        return "label", item

    if _meta_has_nested_blocks(item):
        parts = list(_iter_split_non_nested(item, assignment))
    else:
        parts = item.split(assignment)

    if len(parts) == 1:
        return "label", parts[0]
    if len(parts) == 2:
        return parts[0], parts[1]
    raise ValueError(item)


def meta_parser(
    features: str,
    prefix: str = "",
    delim: str = ",",
    assignment: str = "=",
    feature_unpack: str = "|",
) -> Dict[str, Any]:
    """Parse one square-bracket metadata block into a dictionary.

    Parameters
    ----------
    features : str
        Raw contents of a Newick comment block, excluding the outer
        square brackets.
    prefix : str, default=""
        Optional prefix expected at the start of ``features``, such as
        ``"&"`` or ``"&&NHX:"``.
    delim : str, default=","
        Separator between metadata items.
    assignment : str, default="="
        Separator between metadata keys and values.
    feature_unpack : str, default="|"
        Optional token used to unpack compact list-like values such as
        ``"0.1|0.9"``.

    Returns
    -------
    dict[str, Any]
        Mapping of parsed metadata keys to scalar or list values.

    Raises
    ------
    ToytreeError
        Raised if the metadata does not match the configured prefix,
        delimiter, or assignment format.

    Examples
    --------
    >>> meta_parser("&x=1,y=2", prefix="&")
    {'x': 1.0, 'y': 2.0}
    >>> meta_parser("&&NHX:S=human:E=1.1.1.1", prefix="&&NHX:", delim=":")
    {'S': 'human', 'E': '1.1.1.1'}

    See Also
    --------
    parse_newick_string
    parse_newick_string_custom
    """
    if not prefix:
        feats = features
    elif features.startswith(prefix):
        feats = features[len(prefix) :]
    elif prefix == "&":
        feats = features
    else:
        msg = NHX_ERROR.format(
            features, *(f'"{i}"' for i in (prefix, assignment, delim))
        )
        raise ToytreeError(msg)

    if not feats:
        return {}

    meta: Dict[str, Any] = {}
    try:
        # Most metadata blocks are flat `key=value,key=value` strings.
        # Use native splitting there and fall back to nested-aware
        # parsing only when delimiters may occur inside braces.
        if not _meta_has_nested_blocks(feats):
            items = feats.split(delim) if delim else [feats]
            for item in items:
                key, value = _split_meta_assignment(item, assignment)
                if feature_unpack and feature_unpack in value:
                    meta[key] = [
                        _coerce_meta_value(part) for part in value.split(feature_unpack)
                    ]
                else:
                    meta[key] = _coerce_meta_value(value)
            return meta

        brace_only = _meta_uses_braces_only(feats)
        if delim and len(delim) == 1 and brace_only:
            items = _split_ignoring_braces_single(feats, delim)
        elif delim and len(delim) == 1:
            items = _split_non_nested_single(feats, delim)
        else:
            items = list(_iter_split_non_nested(feats, delim))

        for item in items:
            if assignment and len(assignment) == 1 and brace_only:
                key, value = _split_meta_assignment_braces_single(item, assignment)
            elif assignment and len(assignment) == 1:
                key, value = _split_meta_assignment_single(item, assignment)
            else:
                key, value = _split_meta_assignment(item, assignment)

            if feature_unpack and feature_unpack in value:
                meta[key] = [
                    _coerce_meta_value(part) for part in value.split(feature_unpack)
                ]
            else:
                meta[key] = _coerce_meta_value(value)
    except ValueError as exc:
        msg = NHX_ERROR.format(
            features, *(f'"{i}"' for i in (prefix, assignment, delim))
        )
        raise ToytreeError(msg) from exc
    return meta


def _finalize_subtree_builder(
    builder: _SubtreeBuilder,
    aggregator: Callable[[str, Any, float, Any], Any],
    dist_formatter: Callable[[str], float],
    feat_formatter: Callable[[str], Dict[str, Any]],
) -> Tuple[Any, Set[str]]:
    """Convert one completed builder into the aggregator result."""
    label, dist, node_meta_text, edge_meta_text = _node_str_to_data(
        "".join(builder.payload_parts)
    )

    child_data = []
    edge_features: Set[str] = set()
    if builder.children:
        for child_obj, child_features in builder.children:
            child_data.append(child_obj)
            edge_features.update(child_features)

    distance = 1.0 if dist is None else dist_formatter(dist)
    node_meta = {} if node_meta_text is None else feat_formatter(node_meta_text)
    edge_meta = {} if edge_meta_text is None else feat_formatter(edge_meta_text)
    edge_features.update(edge_meta)

    features = {**node_meta, **edge_meta}
    return aggregator(label, child_data, distance, features), edge_features


def _walk_newick_subtrees(
    newick: str,
    aggregator: Callable[[str, Any, float, Any], Any],
    dist_formatter: Callable[[str], float],
    feat_formatter: Callable[[str], Dict[str, Any]],
) -> Tuple[Any, Set[str]]:
    """Return the parsed root object and edge feature names."""
    current = _SubtreeBuilder()
    stack: List[Tuple[_SubtreeBuilder, List[Tuple[Any, Set[str]]]]] = []
    idx = 0

    while idx < len(newick):
        char = newick[idx]
        if char in "[{":
            end = _find_balanced_end(newick, idx, BLOCK_ERRORS[char])
            current.payload_parts.append(newick[idx : end + 1])
            idx = end + 1
            continue

        if char == "(":
            if current.children is not None or current.payload_parts:
                raise ToytreeError("Unexpected '(' inside Newick node data")
            stack.append((current, []))
            current = _SubtreeBuilder()
        elif char == ",":
            if not stack:
                raise ToytreeError("Newick string commas must occur inside parentheses")
            stack[-1][1].append(
                _finalize_subtree_builder(
                    current,
                    aggregator=aggregator,
                    dist_formatter=dist_formatter,
                    feat_formatter=feat_formatter,
                )
            )
            current = _SubtreeBuilder()
        elif char == ")":
            if not stack:
                raise ToytreeError(BLOCK_ERRORS[char])
            parent, children = stack.pop()
            children.append(
                _finalize_subtree_builder(
                    current,
                    aggregator=aggregator,
                    dist_formatter=dist_formatter,
                    feat_formatter=feat_formatter,
                )
            )
            parent.children = children
            current = parent
        elif char in "]}":
            raise ToytreeError(BLOCK_ERRORS[char])
        else:
            current.payload_parts.append(char)
        idx += 1

    if stack:
        raise ToytreeError(BLOCK_ERRORS["("])

    return _finalize_subtree_builder(
        current,
        aggregator=aggregator,
        dist_formatter=dist_formatter,
        feat_formatter=feat_formatter,
    )


def parse_newick_string_custom(
    newick: str,
    dist_formatter: Callable[[str], float] = None,
    feat_formatter: Callable[[str], Dict[str, Any]] = None,
    aggregator: Callable[[str, List[Node], float, Any], Node] = None,
    internal_labels: Optional[str] = None,
) -> ToyTree:
    """Parse a Newick string using custom value-formatting hooks.

    Parameters
    ----------
    newick : str
        Serialized Newick string ending with ``;``.
    dist_formatter : callable, optional
        Callable used to convert edge-length strings into stored
        distance values.
    feat_formatter : callable, optional
        Callable used to convert comment-block metadata strings into a
        dictionary.
    aggregator : callable, optional
        Callable that receives ``(label, children, distance, features)``
        and returns one node object. The default aggregator builds
        :class:`toytree.Node` instances.
    internal_labels : str or None, default=None
        Controls how internal labels are interpreted after parsing.
        Use ``"support"`` or ``"name"`` to force a feature, or leave
        as ``None`` to infer automatically.

    Returns
    -------
    ToyTree
        Parsed tree object.

    Raises
    ------
    ToytreeError
        Raised if ``newick`` is malformed or missing its terminal
        semicolon.

    Examples
    --------
    >>> tree = parse_newick_string_custom("((a:1,b:2)X:3,c:4)R;")
    >>> tree.ntips
    3

    See Also
    --------
    parse_newick_string
    meta_parser
    toytree.tree
    """
    newick = newick.strip()
    if not newick.endswith(";"):
        raise ToytreeError("Newick string must end with ';'")
    newick = newick[:-1]

    if feat_formatter is None:
        feat_formatter = meta_parser
    if dist_formatter is None:
        dist_formatter = distance_parser
    if aggregator is None:
        aggregator = node_aggregator

    treenode, edge_features = _walk_newick_subtrees(
        newick,
        aggregator=aggregator,
        dist_formatter=dist_formatter,
        feat_formatter=feat_formatter,
    )

    treenode._dist = 0.0
    tree = ToyTree(treenode)
    tree.edge_features.update(edge_features)
    _extract_curly_trait_labels(tree)
    return _infer_internal_label_type(tree, internal_labels)


def node_aggregator(
    label: str,
    children: List[Node],
    distance: float,
    features: Dict[str, Any],
) -> Node:
    """Build one `Node` from parsed subtree data.

    Parameters
    ----------
    label : str
        Parsed node label string.
    children : list[Node]
        Parsed child nodes in Newick order.
    distance : float
        Parsed edge length leading to this node.
    features : dict[str, Any]
        Parsed node and edge metadata associated with this subtree.

    Returns
    -------
    Node
        Connected node object.

    Examples
    --------
    >>> node = node_aggregator("A", [], 1.0, {"state": 1})
    >>> (node.name, node.dist, node.state)
    ('A', 1.0, 1)

    See Also
    --------
    parse_newick_string_custom
    parse_newick_string
    """
    node = Node(name=label)
    node._dist = distance
    for child in children:
        node._add_child(child)

    for key, value in features.items():
        if key in RESERVED_FEATURE_NAMES:
            print(
                f"NHX feature name {key} is reserved and has been changed to __{key}",
                file=sys.stderr,
            )
            key = f"__{key}"
        setattr(node, key, value)
    return node


def _dict_aggregator(label, children, distance, features):
    """Return parsed subtree data as a plain dict for ad hoc tests."""
    return dict(label=label, children=children, features=(distance, features))


def _infer_internal_label_type(
    tree: ToyTree, internal_labels: Optional[str]
) -> ToyTree:
    """Return a `ToyTree` with internal labels assigned to a feature."""
    if internal_labels == "support":
        for idx in range(tree.ntips, tree.nnodes):
            node = tree[idx]
            try:
                node.support = float(node.name)
            except ValueError:
                node.support = math.nan
            node.name = ""

    elif isinstance(internal_labels, str):
        for idx in range(tree.ntips, tree.nnodes):
            node = tree[idx]
            setattr(node, internal_labels, node.name)
            if internal_labels != "name":
                node.name = ""

    else:
        inodes = list(tree[tree.ntips : -1])
        labels = [node.name for node in inodes]
        n_internal = len(labels)
        n_numeric = 0
        n_non_numeric = 0
        numeric_values: list[Optional[float]] = [None] * n_internal

        for idx, value in enumerate(labels):
            sval = "" if value is None else str(value).strip()
            if not sval:
                continue
            try:
                numeric_values[idx] = float(sval)
                n_numeric += 1
            except ValueError:
                n_non_numeric += 1

        numeric_threshold = max(1, n_internal - 2)
        infer_support = (
            n_non_numeric == 0 and n_numeric > 0 and n_numeric >= numeric_threshold
        )

        if infer_support:
            for idx, inode in enumerate(inodes):
                value = numeric_values[idx]
                if value is None:
                    inode.support = math.nan
                else:
                    inode.support = int(value) if value.is_integer() else value
                inode.name = ""
        elif n_non_numeric and n_numeric:
            print(
                "Warning: Because internal node labels are mixed numeric "
                "and non-numeric values,\n"
                "the data's feature cannot be auto-detected as 'name' "
                "(str) or 'support' (numeric).\n"
                "Setting to 'name' by default. Use arg "
                "'internal_labels={feature_name}' in toytree.tree()\n"
                "to suppress this message and manually set data to: "
                "'name', 'support', or {feature_name}",
                file=sys.stderr,
            )

        tree.treenode.support = math.nan
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
    return tree


def _coerce_curly_trait_value(value: str) -> Any:
    """Return parsed curly-brace feature value as int, float, or str."""
    sval = value.strip()
    try:
        fval = float(sval)
        if fval.is_integer():
            return int(fval)
        return fval
    except ValueError:
        return sval


def _extract_curly_trait_labels(tree: ToyTree) -> bool:
    """Extract `name{value}` labels into `name` plus a `trait` feature."""
    parsed = []
    for node in tree:
        label = "" if node.name is None else str(node.name)
        match = CURLY_TRAIT_PATTERN.match(label)
        if match is None:
            if node is tree.treenode:
                continue
            return False
        base_name, raw_value = match.groups()
        parsed.append((node, base_name, _coerce_curly_trait_value(raw_value)))

    if not parsed:
        return False

    for node, base_name, value in parsed:
        node.name = base_name
        setattr(node, "trait", value)
    return True


def parse_newick_string(
    newick: str,
    feature_prefix: str = "&",
    feature_delim: str = ",",
    feature_assignment: str = "=",
    feature_unpack: str = "|",
    internal_labels: Optional[str] = None,
) -> ToyTree:
    """Parse a Newick string using the built-in metadata parser.

    Parameters
    ----------
    newick : str
        Serialized Newick string ending with ``;``.
    feature_prefix : str, default="&"
        Prefix expected at the start of metadata comments, such as
        ``"&"`` or ``"&&NHX:"``.
    feature_delim : str, default=","
        Separator between metadata items inside one comment block.
    feature_assignment : str, default="="
        Separator between metadata keys and values.
    feature_unpack : str, default="|"
        Optional token used to unpack compact list-like metadata
        values.
    internal_labels : str or None, default=None
        Controls how internal labels are interpreted after parsing.

    Returns
    -------
    ToyTree
        Parsed tree object.

    Raises
    ------
    ToytreeError
        Raised if the Newick string or metadata is malformed.

    Examples
    --------
    >>> tree = parse_newick_string("((a:1,b:1)90:1,c:1)100;")
    >>> tree.get_node_data(["name", "support"]).shape[0]
    5
    >>> tree = parse_newick_string(
    ...     "((a[&&NHX:S=human]:1,b:1):1,c:1);",
    ...     feature_prefix="&&NHX:",
    ...     feature_delim=":",
    ... )
    >>> tree.get_node_data("S").iloc[0]
    'human'

    See Also
    --------
    parse_newick_string_custom
    meta_parser
    toytree.tree
    """
    feat_formatter = partial(
        meta_parser,
        prefix=feature_prefix,
        delim=feature_delim,
        assignment=feature_assignment,
        feature_unpack=feature_unpack,
    )

    return parse_newick_string_custom(
        newick=newick,
        feat_formatter=feat_formatter,
        dist_formatter=distance_parser,
        aggregator=node_aggregator,
        internal_labels=internal_labels,
    )
