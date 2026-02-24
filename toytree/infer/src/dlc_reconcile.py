#!/usr/bin/env python

"""Deterministic DLC reconciliation for one gene tree on one species tree.

This module implements a rooted, LCA-mapping-based reconciliation that reports
Duplication, Loss, and extra-lineage (deep coalescence-like) counts for a gene
tree given a species tree and a gene->species tip mapping.
"""

from __future__ import annotations

from typing import Mapping

import pandas as pd

from toytree import ToyTree

__all__ = ["reconcile_gene_tree_dlc"]


def _validate_inputs(
    gtree: ToyTree,
    sptree: ToyTree,
    imap: Mapping[str, str],
    check_binary: bool,
) -> None:
    """Validate inputs."""
    # raise an exception if inputs are not rooted ToyTree objects.
    if not isinstance(gtree, ToyTree):
        raise TypeError("'gtree' must be a ToyTree.")
    if not isinstance(sptree, ToyTree):
        raise TypeError("'sptree' must be a ToyTree.")
    if not gtree.is_rooted():
        raise ValueError("'gtree' must be rooted.")
    if not sptree.is_rooted():
        raise ValueError("'sptree' must be rooted.")

    # optionally raise exception if either tree is unresolved
    if check_binary:
        if any((not n.is_leaf()) and (len(n.children) != 2) for n in gtree):
            raise ValueError("'gtree' must be bifurcating when check_binary=True.")
        if any((not n.is_leaf()) and (len(n.children) != 2) for n in sptree):
            raise ValueError("'sptree' must be bifurcating when check_binary=True.")

    # raise an exception if either tree contains duplicated labels
    species_labels = sptree.get_tip_labels()
    if len(set(species_labels)) != len(species_labels):
        raise ValueError("species tree tip labels must be unique.")
    species_set = set(species_labels)

    gene_labels = gtree.get_tip_labels()
    if len(set(gene_labels)) != len(gene_labels):
        raise ValueError("gene tree tip labels must be unique.")

    # check that all genes are mapped to a species correctly
    missing = [i for i in gene_labels if i not in imap]
    if missing:
        ex = ", ".join(missing[:5])
        raise ValueError(f"imap missing gene tips (e.g., {ex}).")
    bad = sorted({imap[i] for i in gene_labels if imap[i] not in species_set})
    if bad:
        ex = ", ".join(bad[:5])
        raise ValueError(f"imap maps to unknown species labels (e.g., {ex}).")


def _compute_desc_species(gtree: ToyTree, imap: Mapping[str, str]) -> dict[int, frozenset[str]]:
    """Compute descendant species sets for each gene-tree node."""
    desc: dict[int, frozenset[str]] = {}
    for node in gtree:
        if node.is_leaf():
            desc[node.idx] = frozenset((imap[node.name],))
        else:
            merged: set[str] = set()
            for child in node.children:
                merged.update(desc[child.idx])
            desc[node.idx] = frozenset(merged)
    return desc


def _compute_lca_mapping(gtree: ToyTree, sptree: ToyTree, desc_species: Mapping[int, frozenset[str]]) -> dict[int, int]:
    """Map each gene-tree node to species-tree node idx by LCA mapping."""
    mapping: dict[int, int] = {}
    for node in gtree:
        mrca = sptree.get_mrca_node(*desc_species[node.idx])
        mapping[node.idx] = int(mrca.idx)
    return mapping


def _compute_duplications(gtree: ToyTree, ns_map: Mapping[int, int]) -> dict[int, bool]:
    """Flag duplication nodes based on child-vs-parent mapped species node."""
    dups: dict[int, bool] = {}
    for node in gtree:
        if node.is_leaf():
            dups[node.idx] = False
            continue
        dups[node.idx] = any(ns_map[ch.idx] == ns_map[node.idx] for ch in node.children)
    return dups


def _compute_losses(
    gtree: ToyTree,
    sptree: ToyTree,
    ns_map: Mapping[int, int],
    dups: Mapping[int, bool],
) -> tuple[dict[int, int], int]:
    """Count losses using skipped-speciation edges between mapped parent->child nodes."""
    per_node = {n.idx: 0 for n in gtree}
    total = 0

    # For each gene edge, count skipped species-tree intervals as losses.
    for child in gtree[:-1]:
        parent = child.up
        if parent is None:
            continue
        sp_parent = ns_map[parent.idx]
        sp_child = ns_map[child.idx]
        if sp_parent == sp_child:
            continue

        dist = int(sptree.distance.get_node_distance(sp_parent, sp_child, topology_only=True))
        if dist <= 0:
            continue

        # If parent is a duplication, no mandatory speciation at parent mapping.
        baseline = 0 if dups[parent.idx] else 1
        loss = max(0, dist - baseline)
        if loss:
            per_node[child.idx] += int(loss)
            total += int(loss)
    return per_node, total


def _compute_extra_lineages(
    gtree: ToyTree,
    sptree: ToyTree,
    ns_map: Mapping[int, int],
) -> tuple[dict[int, int], int, dict[int, int]]:
    """Compute extra lineages across species-tree edges and per gene-node contributions."""
    edge_counts: dict[int, int] = {n.idx: 0 for n in sptree if n.up is not None}

    # Count how many gene lineages traverse each species-tree edge.
    for child in gtree[:-1]:
        parent = child.up
        if parent is None:
            continue
        sp_parent = ns_map[parent.idx]
        cur = sptree[ns_map[child.idx]]

        while cur.idx != sp_parent:
            edge_counts[cur.idx] += 1
            if cur.up is None:
                # Defensive guard against inconsistent mapping.
                raise ValueError("Invalid mapping: child mapping is not within parent mapping path.")
            cur = cur.up

    edge_extra = {eid: max(0, cnt - 1) for eid, cnt in edge_counts.items()}
    total = int(sum(edge_extra.values()))

    # Attribute edge-level extra-lineage burden to each gene edge path.
    per_node = {n.idx: 0 for n in gtree}
    for child in gtree[:-1]:
        parent = child.up
        if parent is None:
            continue
        sp_parent = ns_map[parent.idx]
        cur = sptree[ns_map[child.idx]]
        contrib = 0
        while cur.idx != sp_parent:
            contrib += edge_extra[cur.idx]
            cur = cur.up
        per_node[child.idx] = int(contrib)

    return per_node, total, edge_counts


def _build_data_table(
    gtree: ToyTree,
    desc_species: Mapping[int, frozenset[str]],
    ns_map: Mapping[int, int],
    dups: Mapping[int, bool],
    losses_per_node: Mapping[int, int],
    coal_per_node: Mapping[int, int],
) -> pd.DataFrame:
    """Build per-node reconciliation table in gene-node idx order."""
    rows = []
    for node in gtree:
        rows.append(
            {
                "gtree_node_idx": int(node.idx),
                "is_tip": bool(node.is_leaf()),
                "parent_idx": None if node.up is None else int(node.up.idx),
                "dlc_ns": int(ns_map[node.idx]),
                "dlc_dups": bool(dups[node.idx]),
                "dlc_losses": int(losses_per_node[node.idx]),
                "dlc_extra_lineages": int(coal_per_node[node.idx]),
                "desc_species_tips": tuple(sorted(desc_species[node.idx])),
            }
        )
    return pd.DataFrame(rows)


def reconcile_gene_tree_dlc(
    gtree: ToyTree,
    sptree: ToyTree,
    imap: Mapping[str, str],
    *,
    inplace: bool = False,
    check_binary: bool = False,
    return_data: bool = True,
) -> dict[str, object]:
    """Reconcile one rooted gene tree to one rooted species tree under a DLC model.

    Parameters
    ----------
    gtree : ToyTree
        Rooted gene tree with unique tip labels.
    sptree : ToyTree
        Rooted species tree with unique tip labels.
    imap : Mapping[str, str]
        Mapping from gene tip label to species tip label.
    inplace : bool, default=False
        If True, annotate and return the input ``gtree``; otherwise annotate a copy.
    check_binary : bool, default=False
        If True, require both trees to be strictly bifurcating.
    return_data : bool, default=True
        If True, include per-node reconciliation table in the returned dict.

    Returns
    -------
    dict[str, object]
        Keys:
        - ``summary``: aggregate counts and run metadata.
        - ``data``: per-gene-node table (if ``return_data=True``).
        - ``tree``: annotated gene tree.

    Notes
    -----
    Event counts use deterministic LCA mapping:
    - duplications: parent node maps to same species node as any child.
    - losses: skipped speciations along mapped parent->child species paths.
    - coalescences: extra lineages across species-tree edges.
    """
    _validate_inputs(gtree, sptree, imap=imap, check_binary=check_binary)
    wtree = gtree if inplace else gtree.copy()

    # Compute descendant species sets and node->species LCA mapping.
    desc_species = _compute_desc_species(wtree, imap)
    ns_map = _compute_lca_mapping(wtree, sptree, desc_species)

    # Compute duplication, loss, and coalescence-like components.
    dups = _compute_duplications(wtree, ns_map)
    losses_per_node, losses_total = _compute_losses(wtree, sptree, ns_map, dups)
    coal_per_node, coal_total, _edge_counts = _compute_extra_lineages(wtree, sptree, ns_map)

    dups_total = int(sum(1 for n in wtree[wtree.ntips:] if dups[n.idx]))
    score = int(dups_total + losses_total + coal_total)

    # Annotate standardized reconciliation features onto the returned tree.
    wtree.set_node_data("dlc_ns", ns_map, inplace=True)
    wtree.set_node_data("dlc_dups", dups, inplace=True)
    wtree.set_node_data("dlc_losses", losses_per_node, inplace=True)
    wtree.set_node_data("dlc_extra_lineages", coal_per_node, inplace=True)

    data = _build_data_table(
        wtree,
        desc_species=desc_species,
        ns_map=ns_map,
        dups=dups,
        losses_per_node=losses_per_node,
        coal_per_node=coal_per_node,
    )

    out = {
        "summary": {
            "duplications": int(dups_total),
            "losses": int(losses_total),
            "coalescences": int(coal_total),
            "score": int(score),
            "n_gene_nodes": int(wtree.nnodes),
            "n_species_nodes": int(sptree.nnodes),
            "n_gene_tips": int(wtree.ntips),
            "n_species_tips": int(sptree.ntips),
            "rooted_gtree": True,
            "rooted_sptree": True,
        },
        "tree": wtree,
    }
    if return_data:
        out["data"] = data
    return out
