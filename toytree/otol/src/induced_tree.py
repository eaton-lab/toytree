"""Internal topology helpers for OpenTree taxonomy and synthesis results."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from toytree.utils import ToytreeError


def _parse_ott_id_from_label(label: str) -> int | None:
    """Extract the final ``ott<digits>`` identifier from a node label."""
    matches = re.findall(r"ott(\d+)", str(label), flags=re.IGNORECASE)
    return int(matches[-1]) if matches else None


def _parse_ott_id_token(token: str | int) -> int:
    """Parse an integer OTT identifier from an API token."""
    if isinstance(token, int):
        return token
    matches = re.findall(r"ott(\d+)", str(token), flags=re.IGNORECASE)
    if not matches:
        raise ToytreeError(f"could not parse ott_id from token: {token!r}")
    return int(matches[-1])


def _normalize_label_token(text: str) -> str:
    """Normalize whitespace for a portable Newick node label."""
    return re.sub(r"\s+", "_", str(text).strip())


def _resolve_anchor_node(tree: Any, anchor_label: str) -> Any:
    """Return the exact synthesis anchor, falling back to the root."""
    anchor = str(anchor_label).strip("'\"")
    for node in tree:
        if str(node.name).strip("'\"") == anchor:
            return node
    return tree.treenode


def _records_by_ott(
    records: list[dict[str, Any]],
    required: list[int],
) -> dict[int, dict[str, Any]]:
    """Index taxonomy records and verify that every query was returned."""
    indexed: dict[int, dict[str, Any]] = {}
    for record in records:
        if record.get("ott_id") is None:
            raise ToytreeError("lineage record missing required key 'ott_id'.")
        indexed[int(record["ott_id"])] = record
    missing = [ott for ott in required if ott not in indexed]
    if missing:
        raise ToytreeError(f"missing lineage records for ott_ids: {missing!r}")
    return indexed


def build_taxonomy_tree(
    records: list[dict[str, Any]],
    queried_ott_ids: list[int],
    *,
    force_as_tips: bool = True,
) -> Any:
    """Merge OpenTree lineage identities into a taxonomy topology.

    OpenTree returns each lineage from the immediate parent toward the root.
    Reversing and merging those paths creates a deterministic trie. Taxonomic
    ranks are retained as features but never interpreted as metric distances.
    """
    import toytree

    records_by_ott = _records_by_ott(records, queried_ott_ids)
    nodes: dict[int, Any] = {}
    candidate_roots: list[Any] = []

    def get_node(ott: int, name: str, rank: str = "") -> Any:
        if ott not in nodes:
            node = toytree.Node(
                name=f"{_normalize_label_token(name)}_ott{ott}",
                dist=1.0,
            )
            node.ott_id = ott
            node.ncbi_id = pd.NA
            node.taxonomic_rank = rank
            nodes[ott] = node
        return nodes[ott]

    for query_ott in queried_ott_ids:
        record = records_by_ott[query_ott]
        path = list(reversed(list(record.get("lineage", [])))) + [record]
        parent = None
        for taxon in path:
            if taxon.get("ott_id") is None:
                raise ToytreeError("taxonomy lineage entry is missing 'ott_id'.")
            ott = int(taxon["ott_id"])
            node = get_node(
                ott,
                str(taxon.get("name", f"ott{ott}")),
                str(taxon.get("rank", "")),
            )
            if parent is None:
                if node not in candidate_roots:
                    candidate_roots.append(node)
            elif node._up is None:
                parent._add_child(node)
            elif node._up is not parent:
                raise ToytreeError(
                    f"inconsistent taxonomy parentage returned for ott{ott}."
                )
            parent = node

    roots = [node for node in candidate_roots if node._up is None]
    if not roots:
        raise ToytreeError("taxonomy records did not contain a usable lineage.")
    if len(roots) == 1:
        root = roots[0]
        root._dist = 0.0
    else:
        root = toytree.Node(name="taxonomy_root", dist=0.0)
        root.ott_id = pd.NA
        root.ncbi_id = pd.NA
        root.taxonomic_rank = ""
        for component in roots:
            root._add_child(component)

    tree = toytree.ToyTree(root)
    if force_as_tips:
        for ott in queried_ott_ids:
            node = nodes[ott]
            if node.is_leaf():
                continue
            tip = toytree.Node(name=f"ott{ott}", dist=1.0)
            tip.ott_id = ott
            tip.ncbi_id = pd.NA
            tip.taxonomic_rank = node.taxonomic_rank
            node._add_child(tip)
        tree._update()

    for node in tree:
        if not node.is_root() and node._dist <= 0:
            node._dist = 1.0
    tree._update()
    return tree


def _normalize_induced_tips_to_ott(induced: Any) -> tuple[Any, list[int]]:
    """Relabel synthesis tips as canonical OTT tokens."""
    mapping: dict[int, str] = {}
    ids: list[int] = []
    for tip in induced[: induced.ntips]:
        ott = _parse_ott_id_from_label(str(tip.name))
        if ott is None:
            raise ToytreeError("induced subtree tip labels must include ott_id tokens.")
        if ott in ids:
            raise ToytreeError(f"induced subtree contains duplicate ott_id ott{ott}.")
        ids.append(ott)
        mapping[tip.idx] = f"ott{ott}"
    induced.set_node_data("name", mapping, inplace=True)
    return induced, ids


def _refine_scaffold_with_induced(scaffold: Any, induced: Any) -> Any:
    """Resolve compatible taxonomy polytomies using synthesis relationships."""
    import toytree

    for node in list(scaffold[scaffold.ntips :]):
        if len(node.children) <= 2:
            continue
        groups: list[tuple[Any, set[str]]] = []
        for child in node.children:
            tips = {
                str(tip.name)
                for tip in child.iter_leaves()
                if _parse_ott_id_from_label(str(tip.name)) is not None
            }
            if tips:
                groups.append((child, tips))
        if len(groups) <= 2:
            continue
        induced_tip_names = set(induced.get_tip_labels())
        if any(not tips.issubset(induced_tip_names) for _, tips in groups):
            continue

        # Existing multi-tip taxonomy children must remain monophyletic in the
        # synthesis tree; otherwise the proposed refinement is incompatible.
        compatible = True
        for _, tips in groups:
            if len(tips) > 1:
                mrca = induced.get_mrca_node(*sorted(tips))
                if set(mrca.get_leaf_names()) != tips:
                    compatible = False
                    break
        if not compatible:
            continue

        representatives = [sorted(tips)[0] for _, tips in groups]
        reduced = induced.mod.prune(*representatives, require_root=False)
        copies = {
            representative: child.copy(detach=True)
            for (child, _), representative in zip(groups, representatives)
        }

        def expand(reduced_node: Any) -> Any:
            if reduced_node.is_leaf():
                return copies[str(reduced_node.name)]
            replacement = toytree.Node(name="", dist=1.0)
            for child in reduced_node.children:
                replacement._add_child(expand(child))
            return replacement

        replacement = expand(reduced.treenode)
        for child in list(node.children):
            node._remove_child(child)
        if replacement.is_leaf():
            node._add_child(replacement)
        else:
            for child in list(replacement.children):
                replacement._remove_child(child)
                node._add_child(child)
        scaffold._update()
    return scaffold
