#!/usr/bin/env python
"""Parse extended-newick networks into a major tree and admixture events."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Union
import re

import toytree
from toytree.io.src.parse import replace_whitespace


@dataclass(frozen=True)
class AdmixtureEvent:
    """Container describing one hybridization event."""

    hybrid_id: str
    major_descendants: Tuple[str, ...]
    minor_descendants: Tuple[str, ...]
    gamma: float
    metadata: Dict[str, object] = field(default_factory=dict)


def _load_network_string(net: Union[str, Path]) -> str:
    """Return the extended-newick network string from a file or string."""
    if ";" not in str(net):
        net = Path(net)
        if not net.exists():
            raise IOError("input type is not a file or newick (no ; ending).")
        with open(net, "rt", encoding="utf-8") as infile:
            net = infile.readline().split(";")[0] + ";"
    else:
        net = str(net).split(";")[0] + ";"
    return replace_whitespace(net)


def _inject_gamma_into_labels(net: str) -> str:
    """Encode gamma values into node labels so ToyTree can parse them."""
    tip_gamma = re.compile(r"(#\w+):::([\d.]+)")
    internal_gamma = re.compile(r"(#\w+):([\d.]+)::([\d.]+)")
    net = tip_gamma.sub(r"\1-gamma-\2", net)
    net = internal_gamma.sub(r"\1-gamma-\3:\2", net)
    return net


def _extract_gamma(label: str) -> Tuple[str, float | None]:
    """Return the base label and parsed gamma if present."""
    if "-gamma-" not in label:
        return label, None
    base, gamma = label.rsplit("-gamma-", 1)
    try:
        return base, float(gamma)
    except ValueError:
        return base, None


def _pseudo_unroot(tree: toytree.ToyTree) -> toytree.ToyTree:
    """Return unrooted tree re-ordered for display and stable parsing."""
    opt = tree.get_nodes()
    for node in tree.traverse("postorder"):
        if node.name.startswith("#H"):
            for desc in node.get_descendants():
                if desc in opt:
                    opt.remove(desc)
    if not opt:
        return tree
    return tree.root(opt[0]).mod.ladderize().mod.unroot()


def _group_hybrid_nodes(nodes: Iterable[toytree.Node]) -> Dict[str, List[toytree.Node]]:
    """Return mapping of hybrid id -> nodes with that label."""
    grouped: Dict[str, List[toytree.Node]] = {}
    for node in nodes:
        label, _ = _extract_gamma(node.name)
        grouped.setdefault(label, []).append(node)
    return grouped


def _filter_hybrid_leaves(leaf_names: Iterable[str]) -> Tuple[str, ...]:
    return tuple(name for name in leaf_names if not name.startswith("#H"))


def _get_gamma_value(nodes: Iterable[toytree.Node]) -> float:
    """Extract gamma preferring leaf node gamma when available."""
    gamma = None
    for node in nodes:
        _, maybe = _extract_gamma(node.name)
        if maybe is None:
            continue
        if node.is_leaf():
            return maybe
        gamma = maybe
    return 0.5 if gamma is None else gamma


def _remove_unary_nodes(tree: toytree.ToyTree) -> None:
    """Remove internal nodes with a single child without collapsing polytomies."""
    for node in list(tree.traverse("postorder")):
        if node.is_leaf():
            continue
        if len(node.children) == 1:
            node._delete(prevent_unary=True)
    tree._update()


def parse_major_tree_and_admixture_events(
    net: Union[str, Path],
) -> Tuple[toytree.ToyTree, Dict[str, AdmixtureEvent]]:
    """Return the major tree and admixture events parsed from a network."""
    net_string = _load_network_string(net)
    net_string = _inject_gamma_into_labels(net_string)
    tree = toytree.tree(net_string, internal_labels="name")
    tree = _pseudo_unroot(tree)

    events: Dict[str, AdmixtureEvent] = {}

    while True:
        try:
            hnodes = tree.get_nodes("~#H*")
        except ValueError:
            hnodes = []
        if not hnodes:
            _remove_unary_nodes(tree)
            return tree, events

        grouped = _group_hybrid_nodes(hnodes)
        hybrid_id = sorted(grouped)[0]
        nodes = grouped[hybrid_id]
        event_id = hybrid_id.lstrip("#")
        if len(nodes) != 2:
            raise ValueError(f"Expected two nodes for {hybrid_id}, found {len(nodes)}")

        source = nodes[0] if nodes[0].is_leaf() else nodes[1]
        dest = nodes[1] if source is nodes[0] else nodes[0]
        if not source.is_leaf() or dest.is_leaf():
            raise ValueError(f"Unable to identify source/destination for {hybrid_id}")

        gamma = _get_gamma_value(nodes)

        source_parent = source._up
        minor_desc = ()
        if source_parent is not None:
            minor_desc = _filter_hybrid_leaves(source_parent.get_leaf_names())
        source.name = event_id

        major_desc = _filter_hybrid_leaves(dest.get_leaf_names())
        dest._delete()

        tree._update()
        events[event_id] = AdmixtureEvent(
            hybrid_id=event_id,
            major_descendants=major_desc,
            minor_descendants=minor_desc,
            gamma=gamma,
        )


__all__ = ["AdmixtureEvent", "parse_major_tree_and_admixture_events"]
