#!/usr/bin/env python

"""Write trees to Newick and NEXUS text formats."""

from __future__ import annotations

import math
import re
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Any

from toytree.core import Node, ToyTree
from toytree.core.apis import add_toytree_method
from toytree.utils.src.exceptions import ToytreeError

DISALLOWED_FEATURES = {"idx", "dist", "up", "children"}
SAFE_NEXUS_LABEL = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class _WriterConfig:
    """Store precomputed formatter and serialization settings."""

    dist_formatter: Callable[[float], str]
    label_formatter: Callable[[float], str]
    feature_formatter: Callable[[float], str]
    internal_labels: str | None
    node_features: tuple[str, ...]
    edge_features: tuple[str, ...]
    features_prefix: str
    features_delim: str
    features_assignment: str
    feature_pack: str
    names_as_ints: bool
    label_suffixes: dict[int, str] | None
    reserved_text_tokens: tuple[str, ...]


def _is_nan(value: float) -> bool:
    """Return True only for NaN numeric values."""
    try:
        return math.isnan(value)
    except (TypeError, ValueError):
        return False


def _raise_bad_formatter(param_name: str, formatting_str: str) -> None:
    """Raise a consistent formatting validation error."""
    raise ToytreeError(
        f"{param_name} is not a proper Python formatting string: {formatting_str!r}"
    )


def get_float_formatter(
    formatting_str: str | None,
    param_name: str,
) -> Callable[[float], str]:
    """Return a validated callable for float serialization."""
    if formatting_str is None:

        def formatter(_: float) -> str:
            return ""

        return formatter

    try:
        if "%" in formatting_str:
            formatting_str % 1.0

            def formatter(value: float) -> str:
                return formatting_str % value

            return formatter
        if formatting_str.startswith("{"):
            formatting_str.format(1.0)

            def formatter(value: float) -> str:
                return formatting_str.format(value)

            return formatter
    except (IndexError, KeyError, TypeError, ValueError) as exc:
        raise ToytreeError(
            f"{param_name} is not a proper Python formatting string: "
            f"{formatting_str!r}"
        ) from exc

    _raise_bad_formatter(param_name, formatting_str)


def _raise_unsafe_feature_value(feature: str, value: str, token: str) -> None:
    """Raise when a string metadata value would serialize ambiguously."""
    raise ToytreeError(
        f"Cannot write feature {feature!r} value {value!r}; "
        f"it contains reserved metadata token {token!r}."
    )


def _normalize_text_feature_value(
    feature: str,
    value: str,
    config: _WriterConfig,
) -> str:
    """Validate one string metadata value for safe NHX serialization."""
    if not value:
        return ""
    for token in config.reserved_text_tokens:
        if token and token in value:
            _raise_unsafe_feature_value(feature, value, token)
    return value


def _serialize_feature_value(
    feature: str,
    value: Any,
    config: _WriterConfig,
) -> str:
    """Return one node feature value formatted for metadata output."""
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        packed_values: list[str] = []
        for item in value:
            try:
                fitem = float(item)
            except (TypeError, ValueError):
                sval = _normalize_text_feature_value(feature, str(item), config)
                if sval:
                    packed_values.append(sval)
            else:
                if not _is_nan(fitem):
                    packed_values.append(config.feature_formatter(fitem))
        return config.feature_pack.join(packed_values)

    try:
        fval = float(value)
    except (TypeError, ValueError):
        return _normalize_text_feature_value(feature, str(value), config)

    if _is_nan(fval):
        return ""
    return config.feature_formatter(fval)


def get_feature_string(
    node: Node,
    features: Sequence[str],
    config: _WriterConfig,
) -> str:
    """Return a bracketed metadata block for selected node features."""
    if not features:
        return ""

    pairs: list[str] = []
    for feature in features:
        value = getattr(node, feature, None)
        if value is None:
            continue
        serialized = _serialize_feature_value(feature, value, config)
        if serialized:
            pairs.append(f"{feature}{config.features_assignment}{serialized}")

    if not pairs:
        return ""
    return f"[{config.features_prefix}" f"{config.features_delim.join(pairs)}]"


def get_single_feature_label_suffixes(
    tree: ToyTree,
    feature: str,
    feature_formatter: Callable[[float], str],
) -> dict[int, str]:
    """Return a map of node idx to `{value}` label suffixes."""
    if feature not in tree.features:
        raise ToytreeError(f"Cannot write feature not present in tree: {feature!r}")

    suffixes: dict[int, str] = {}
    for node in tree:
        value = getattr(node, feature, None)
        if value is None:
            raise ToytreeError(
                f"write_single_feature={feature!r} requires values on all nodes."
            )
        try:
            fval = float(value)
        except (TypeError, ValueError):
            sval = str(value)
            if sval == "":
                raise ToytreeError(
                    f"write_single_feature={feature!r} cannot include empty values."
                )
        else:
            if _is_nan(fval):
                raise ToytreeError(
                    f"write_single_feature={feature!r} cannot include NaN values."
                )
            sval = feature_formatter(fval)
        suffixes[node.idx] = f"{{{sval}}}"
    return suffixes


def _format_dist(node: Node, config: _WriterConfig) -> str:
    """Return serialized edge-length text including its leading colon."""
    dist = config.dist_formatter(node.dist)
    return f":{dist}" if dist else ""


def _format_internal_label(node: Node, config: _WriterConfig) -> str:
    """Return serialized internal label text for one node."""
    if config.internal_labels is None:
        return ""

    value = getattr(node, config.internal_labels, None)
    if value is None:
        return ""
    try:
        fval = float(value)
    except (TypeError, ValueError):
        return str(value)
    if _is_nan(fval):
        return ""
    return config.label_formatter(fval)


def node_to_newick(
    node: Node,
    children: tuple[str, ...],
    config: _WriterConfig,
) -> str:
    """Return one subtree serialized to Newick text."""
    node_feature_str = get_feature_string(node, config.node_features, config)
    edge_feature_str = get_feature_string(node, config.edge_features, config)
    dist = _format_dist(node, config)
    internal = _format_internal_label(node, config)

    suffix = ""
    if config.label_suffixes is not None:
        suffix = config.label_suffixes.get(node.idx, "")
    if suffix:
        internal = f"{internal}{suffix}" if internal else suffix

    if node.is_leaf():
        label = str(node.idx) if config.names_as_ints else str(node.name)
        if suffix:
            label = f"{label}{suffix}"
        if dist:
            return f"{label}{node_feature_str}{dist}{edge_feature_str}"
        return f"{label}{node_feature_str}"

    subtree = f"({','.join(children)})"
    if node.is_root():
        if node.dist:
            return f"{subtree}{internal}{node_feature_str}{dist}{edge_feature_str}"
        return f"{subtree}{internal}{node_feature_str}"

    if dist:
        return f"{subtree}{internal}{node_feature_str}{dist}{edge_feature_str}"
    return f"{subtree}{internal}{node_feature_str}"


def tree_reduce(node: Node, config: _WriterConfig) -> str:
    """Return the serialized Newick subtree descending from one node."""
    reduced_children = tuple(tree_reduce(child, config) for child in node.children)
    return node_to_newick(node, reduced_children, config)


def _quote_nexus_name(name: str) -> str:
    """Return a NEXUS-safe translation label."""
    if SAFE_NEXUS_LABEL.fullmatch(name):
        return name
    return "'" + name.replace("'", "''") + "'"


def wrap_nexus(tree: ToyTree, newick: str) -> str:
    """Wrap one serialized Newick tree in a NEXUS trees block."""
    lines = ["#NEXUS", "begin trees;", "    translate"]
    for node in tree[: tree.ntips]:
        lines.append(f"        {node.idx} {_quote_nexus_name(str(node.name))},")
    lines.append("    ;")
    rooted = "R" if tree.is_rooted() else "U"
    lines.append(f"    tree 0 = [&{rooted}] {newick}")
    lines.append("end;")
    return "\n".join(lines)


def _normalize_features(features: str | Sequence[str] | None) -> tuple[str, ...]:
    """Return requested metadata features with order preserved."""
    if features is None:
        return ()
    requested = [features] if isinstance(features, str) else list(features)
    seen: set[str] = set()
    ordered: list[str] = []
    for feature in requested:
        if feature in DISALLOWED_FEATURES or feature in seen:
            continue
        seen.add(feature)
        ordered.append(feature)
    return tuple(ordered)


def _validate_internal_label_feature(
    tree: ToyTree,
    internal_labels: str | None,
) -> None:
    """Raise if a requested internal-label feature is absent everywhere."""
    if internal_labels is None:
        return
    internal_nodes = tuple(tree[tree.ntips :])
    if not internal_nodes:
        return
    if all(getattr(node, internal_labels, None) is None for node in internal_nodes):
        raise ToytreeError(
            f"internal_labels={internal_labels!r} is not present on any internal nodes."
        )


def _build_writer_config(
    tree: ToyTree,
    dist_formatter: str | None,
    internal_labels: str | None,
    internal_labels_formatter: str | None,
    features: str | Sequence[str] | None,
    features_prefix: str,
    features_delim: str,
    features_assignment: str,
    feature_pack: str,
    features_formatter: str | None,
    nexus: bool,
    write_single_feature: str | None,
) -> _WriterConfig:
    """Return normalized settings and formatter callables for one write."""
    if feature_pack in {features_delim, features_assignment}:
        raise ToytreeError(
            "feature_pack cannot match features_delim or "
            f"features_assignment: {feature_pack!r}"
        )

    ordered_features = _normalize_features(features)
    bad_features = set(ordered_features) - set(tree.features)
    if bad_features:
        raise ToytreeError(f"Cannot write features not present in tree: {bad_features}")

    _validate_internal_label_feature(tree, internal_labels)

    edge_feature_set = set(tree.edge_features)
    node_features = tuple(
        feature for feature in ordered_features if feature not in edge_feature_set
    )
    edge_features = tuple(
        feature for feature in ordered_features if feature in edge_feature_set
    )

    feature_formatter = get_float_formatter(features_formatter, "features_formatter")
    label_suffixes = None
    if write_single_feature is not None:
        label_suffixes = get_single_feature_label_suffixes(
            tree=tree,
            feature=write_single_feature,
            feature_formatter=feature_formatter,
        )

    reserved_text_tokens = tuple(
        token
        for token in (features_delim, features_assignment, feature_pack, "[", "]")
        if token
    )
    return _WriterConfig(
        dist_formatter=get_float_formatter(dist_formatter, "dist_formatter"),
        label_formatter=get_float_formatter(
            internal_labels_formatter,
            "internal_labels_formatter",
        ),
        feature_formatter=feature_formatter,
        internal_labels=internal_labels,
        node_features=node_features,
        edge_features=edge_features,
        features_prefix=features_prefix,
        features_delim=features_delim,
        features_assignment=features_assignment,
        feature_pack=feature_pack,
        names_as_ints=nexus,
        label_suffixes=label_suffixes,
        reserved_text_tokens=reserved_text_tokens,
    )


@add_toytree_method(ToyTree)
def write(
    tree: ToyTree,
    path: str | PathLike[str] | None = None,
    dist_formatter: str | None = "%.12g",
    internal_labels: str | None = "support",
    internal_labels_formatter: str | None = "%.12g",
    features: str | Sequence[str] | None = None,
    features_prefix: str = "&",
    features_delim: str = ",",
    features_assignment: str = "=",
    feature_pack: str = "|",
    features_formatter: str | None = "%.12g",
    nexus: bool = False,
    write_single_feature: str | None = None,
    **kwargs,
) -> str | None:
    """Write a tree to serialized Newick or NEXUS text.

    Parameters
    ----------
    tree : ToyTree
        Tree to serialize.
    path : str or os.PathLike[str] or None, default=None
        Destination file path. If omitted, the serialized text is
        returned instead of being written to disk.
    dist_formatter : str or None, default="%.12g"
        Python formatting string used for branch lengths. Set to
        ``None`` to omit edge lengths.
    internal_labels : str or None, default="support"
        Feature written as internal-node labels. Set to ``None`` to
        suppress internal labels entirely.
    internal_labels_formatter : str or None, default="%.12g"
        Python formatting string used for numeric internal labels. If
        the selected label values are non-numeric, they are written as
        strings.
    features : str or sequence of str or None, default=None
        Additional node or edge features to write into bracketed NHX-like
        metadata blocks.
    features_prefix : str, default="&"
        Prefix placed at the start of each metadata block.
    features_delim : str, default=","
        Separator between metadata entries inside one block.
    features_assignment : str, default="="
        Separator between metadata keys and values.
    feature_pack : str, default="|"
        Separator used to pack list-like feature values into one metadata
        value.
    features_formatter : str or None, default="%.12g"
        Python formatting string used for numeric metadata values.
    nexus : bool, default=False
        If True, wrap the serialized tree in a NEXUS ``begin trees;``
        block and write tip names through a translation table.
    write_single_feature : str or None, default=None
        Append one feature value to every emitted node label as a
        ``{value}`` suffix. The selected feature must be present on all
        nodes and cannot contain missing or NaN values.
    **kwargs
        Deprecated keyword arguments. Any provided keys are ignored after
        a warning is printed to stderr.

    Returns
    -------
    str or None
        Serialized tree text when ``path`` is None, otherwise None after
        the file is written successfully.

    Raises
    ------
    ToytreeError
        Raised if requested features are missing, metadata output would
        be ambiguous, formatting strings are invalid, ``write_single_feature``
        is incompatible with the other options, or the output file cannot
        be written.

    Examples
    --------
    >>> import toytree
    >>> tree = toytree.rtree.baltree(ntips=4)
    >>> tree = tree.set_node_data("name", {4: "A", 5: "B"})
    >>> tree = tree.set_node_data("support", {4: 100, 5: 90})
    >>> tree.write()
    '((r0:0.5,r1:0.5)100:0.5,(r2:0.5,r3:0.5)90:0.5);'
    >>> tree.write(dist_formatter=None, internal_labels=None)
    '((r0,r1),(r2,r3));'
    >>> tree = tree.set_node_data("state", default=7)
    >>> tree.write(write_single_feature="state")
    '((r0{7}:0.5,r1{7}:0.5)100{7}:0.5,(r2{7}:0.5,r3{7}:0.5)90{7}:0.5){7};'

    See Also
    --------
    toytree.tree
    toytree.mtree
    toytree.io.parse_newick_string
    """
    if kwargs:
        print(f"Deprecated args to write(): {list(kwargs)}. See docs.", file=sys.stderr)

    if write_single_feature is not None and nexus:
        raise ToytreeError("write_single_feature is not supported with nexus=True.")

    config = _build_writer_config(
        tree=tree,
        dist_formatter=dist_formatter,
        internal_labels=internal_labels,
        internal_labels_formatter=internal_labels_formatter,
        features=features,
        features_prefix=features_prefix,
        features_delim=features_delim,
        features_assignment=features_assignment,
        feature_pack=feature_pack,
        features_formatter=features_formatter,
        nexus=nexus,
        write_single_feature=write_single_feature,
    )
    newick = tree_reduce(tree.treenode, config) + ";"
    treestr = wrap_nexus(tree, newick) if nexus else newick

    if path is None:
        return treestr

    destination = Path(path).expanduser()
    try:
        destination.write_text(treestr, encoding="utf-8")
    except OSError as exc:
        raise ToytreeError(
            f"Could not write tree data to {destination!s}: {exc}"
        ) from exc
    return None
