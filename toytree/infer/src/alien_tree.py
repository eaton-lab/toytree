#!/usr/bin/env python

"""Non-parametric topology-based index for alien (HGT-like) gene clades.

This module implements a heuristic score that compares a gene tree to a
species tree and asks whether removing any internal gene clade improves
topological congruence. Large positive improvements indicate clades that
behave like alien inserts (e.g., horizontal transfer or severe model mismatch).

The method is intentionally non-parametric: it uses only topology and a
gene-tip to species-tip mapping (`imap`), and does not assume branch-length
models on either tree.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Literal, Mapping

import numpy as np
import pandas as pd

from toytree.core import ToyTree
from toytree.network import AdmixtureEvent

__all__ = ["alien_tree_index", "alien_tree_hybrid_null"]


@dataclass
class _CandidateScore:
    """Container for one candidate prune result."""

    node_idx: int
    n_gene_tips_removed: int
    n_species_removed: int
    n_species_remaining: int
    rf_before: float
    rf_after: float
    gain_raw: float
    gain_weighted: float
    subtree_rf: float
    subtree_compatibility: float
    gain_adjusted: float
    gain_term: float
    compat_term: float
    disp_topo: float | None
    disp_topo_norm: float | None
    disp_term: float
    alien_score_base: float
    best_descendant_alien_score_base: float
    lineage_redundancy: float
    lineage_nonredundancy: float
    alien_score: float
    alien_score_z: float
    src_node_idx: int
    dst_node_idx: int | None
    candidate_tested: bool
    subtree_nni_variants_tested: int
    tested_local_nni: bool


def _canonical_split_side(clade: frozenset[str], all_species: frozenset[str]) -> frozenset[str]:
    """Return a root-invariant canonical side of a split."""
    other = all_species - clade
    if len(clade) < len(other):
        return clade
    if len(other) < len(clade):
        return other
    return clade if tuple(sorted(clade)) <= tuple(sorted(other)) else other


def _validate_inputs(species_tree: ToyTree, gene_tree: ToyTree, imap: Mapping[str, str]) -> None:
    """Validate trees and mapping."""
    # Validate object types before feature access.
    if not isinstance(species_tree, ToyTree):
        raise TypeError("'species_tree' must be a ToyTree.")
    if not isinstance(gene_tree, ToyTree):
        raise TypeError("'gene_tree' must be a ToyTree.")
    if not isinstance(imap, Mapping):
        raise TypeError("'imap' must be a mapping of gene_tip -> species_tip.")

    # Species labels must be unique for unambiguous clade/MRCA matching.
    species_labels = species_tree.get_tip_labels()
    if len(set(species_labels)) != len(species_labels):
        raise ValueError("species tree tip labels must be unique.")
    species_set = set(species_labels)

    # Gene tip labels must also be unique so each tip maps cleanly via imap.
    gene_labels = gene_tree.get_tip_labels()
    if len(set(gene_labels)) != len(gene_labels):
        raise ValueError("gene tree tip labels must be unique.")
    # Validate map coverage and map-to-species validity.
    missing = [name for name in gene_labels if name not in imap]
    if missing:
        preview = ", ".join(missing[:5])
        raise ValueError(f"'imap' is missing mappings for gene tips (e.g., {preview}).")

    bad_species = sorted({imap[g] for g in gene_labels if imap[g] not in species_set})
    if bad_species:
        preview = ", ".join(bad_species[:5])
        raise ValueError(
            f"'imap' contains species labels not present in species_tree (e.g., {preview})."
        )


def _descendant_species_sets(tree: ToyTree, imap: Mapping[str, str]) -> dict[int, frozenset[str]]:
    """Return descendant species sets for all nodes in idx order."""
    # Bottom-up cache used by overlap filtering and candidate scoring.
    desc: dict[int, frozenset[str]] = {}
    for node in tree:
        if node.is_leaf():
            desc[node.idx] = frozenset((imap[node.name],))
        else:
            merged = set()
            for child in node.children:
                merged.update(desc[child.idx])
            desc[node.idx] = frozenset(merged)
    return desc


def _duplication_overlap_flags(
    tree: ToyTree,
    desc_species: Mapping[int, frozenset[str]],
) -> dict[int, bool]:
    """Flag nodes with overlap across child species sets."""
    # Overlapping child species-sets indicate duplication-like patterns.
    flags: dict[int, bool] = {}
    for node in tree:
        if node.is_leaf():
            flags[node.idx] = False
            continue
        csets = [set(desc_species[c.idx]) for c in node.children]
        flags[node.idx] = any(a & b for a, b in combinations(csets, 2))
    return flags


def _species_tree_split_set(
    species_tree: ToyTree,
    species_subset: frozenset[str],
) -> set[frozenset[str]]:
    """Return canonical internal split set from species tree restricted to subset."""
    # Restrict species tree to shared species before computing splits for RF.
    if len(species_subset) < 4:
        return set()
    stree = species_tree.mod.prune(*species_subset)
    all_species = frozenset(stree.get_tip_labels())
    splits: set[frozenset[str]] = set()
    for node in stree[stree.ntips:-1]:
        clade = frozenset(node.get_leaf_names())
        if 1 < len(clade) < (len(all_species) - 1):
            splits.add(_canonical_split_side(clade, all_species))
    return splits


def _projected_gene_split_set(
    gene_tree: ToyTree,
    imap: Mapping[str, str],
    species_subset: frozenset[str],
) -> set[frozenset[str]]:
    """Return overlap-filtered split set from gene tree on shared species."""
    # Project to species space and drop overlap-marked nodes to reduce dup bias.
    if len(species_subset) < 4:
        return set()
    desc = _descendant_species_sets(gene_tree, imap)
    dups = _duplication_overlap_flags(gene_tree, desc)
    all_species = frozenset(species_subset)
    splits: set[frozenset[str]] = set()
    for node in gene_tree[gene_tree.ntips:-1]:
        if dups[node.idx]:
            continue
        clade = frozenset(i for i in desc[node.idx] if i in all_species)
        if 1 < len(clade) < (len(all_species) - 1):
            splits.add(_canonical_split_side(clade, all_species))
    return splits


def _rf_from_split_sets(
    a: set[frozenset[str]],
    b: set[frozenset[str]],
    normalize: bool,
) -> float:
    """Return RF-style distance from two split sets."""
    sym = len(a ^ b)
    if not normalize:
        return float(sym)
    denom = len(a) + len(b)
    if denom == 0:
        return 0.0
    return float(sym) / float(denom)


def _rf_distance(
    species_tree: ToyTree,
    gene_tree: ToyTree,
    imap: Mapping[str, str],
    normalize: bool,
) -> float:
    """Return RF distance between species tree and projected gene tree."""
    # Compute RF over species shared by the current gene tree instance.
    present_species = frozenset(imap[name] for name in gene_tree.get_tip_labels())
    if len(present_species) < 4:
        return np.nan
    s_splits = _species_tree_split_set(species_tree, present_species)
    g_splits = _projected_gene_split_set(gene_tree, imap, present_species)
    return _rf_from_split_sets(s_splits, g_splits, normalize=normalize)


def _local_nni_variants(tree: ToyTree, node_idx: int) -> list[ToyTree]:
    """Return tree plus deterministic one-step NNI variants around node edge."""
    # Local one-edge alternatives used as lightweight error robustness.
    variants = [tree]
    node = tree[node_idx]
    if node.is_leaf() or node.is_root():
        return variants
    parent = node.up
    if parent is None:
        return variants
    if (len(node.children) != 2) or (len(parent.children) != 2):
        return variants

    for pick in node.children:
        ntree = tree.copy()
        nnode = ntree[node_idx]
        nparent = nnode.up
        if nparent is None or (len(nnode.children) != 2) or (len(nparent.children) != 2):
            continue
        npick = ntree[pick.idx]
        nsister = [c for c in nparent.children if c is not nnode][0]

        nparent._remove_child(nsister)
        nnode._remove_child(npick)
        nparent._add_child(npick)
        nnode._add_child(nsister)
        ntree._update()
        variants.append(ntree)
    return variants


def _iter_local_nni_variants_all_edges(tree: ToyTree):
    """Yield deterministic one-step local-NNI variants across all internal edges."""
    # Deduplicate generated variants by topology id.
    seen = {tree.get_topology_id()}
    yield tree
    for node in tree[tree.ntips:-1]:
        for var in _local_nni_variants(tree, node.idx)[1:]:
            tid = var.get_topology_id()
            if tid in seen:
                continue
            seen.add(tid)
            yield var


def _best_rf_with_nni_cap(
    species_tree: ToyTree,
    gene_tree: ToyTree,
    imap: Mapping[str, str],
    normalize: bool,
    max_variants: int,
) -> tuple[float, int]:
    """Return best (minimum) RF over a capped deterministic local-NNI neighborhood."""
    # Cap the search for predictable runtime on larger trees.
    best = np.inf
    ntested = 0
    for variant in _iter_local_nni_variants_all_edges(gene_tree):
        if ntested >= max_variants:
            break
        rf = _rf_distance(species_tree, variant, imap, normalize)
        if not np.isnan(rf):
            best = min(best, rf)
        ntested += 1
    if best == np.inf:
        return np.nan, ntested
    return float(best), ntested


def _subtree_compatibility(
    species_tree: ToyTree,
    subtree: ToyTree,
    imap: Mapping[str, str],
    normalize_rf: bool,
    max_subtree_nni_variants: int,
) -> tuple[float, float, int]:
    """Return (compatibility, subtree_rf, nvariants_tested)."""
    # Subtrees with <4 species are weakly informative; keep neutral weight.
    species = frozenset(imap[i] for i in subtree.get_tip_labels())
    if len(species) < 4:
        return 1.0, np.nan, 0
    rf, ntested = _best_rf_with_nni_cap(
        species_tree=species_tree,
        gene_tree=subtree,
        imap=imap,
        normalize=normalize_rf,
        max_variants=max_subtree_nni_variants,
    )
    if np.isnan(rf):
        return 1.0, np.nan, ntested
    return max(0.0, 1.0 - float(rf)), float(rf), ntested


def _clade_tuple(species_set: frozenset[str]) -> tuple[str, ...]:
    """Return clade tuple sorted for stable anchoring."""
    return tuple(sorted(species_set))


def _infer_best_event(
    gene_tree: ToyTree,
    species_tree: ToyTree,
    imap: Mapping[str, str],
    best_node_idx: int,
) -> AdmixtureEvent:
    """Infer donor/recipient endpoints for the best candidate as AdmixtureEvent.

    Mapping rule:
    - src: MRCA clade of species descending from best node.
    - dst: MRCA clade of species descending from best-node parent minus src species.
    """
    # Infer species-tree anchored source and destination node ids.
    src_node_idx, dst_node_idx = _infer_event_endpoints(
        gene_tree=gene_tree,
        species_tree=species_tree,
        imap=imap,
        node_idx=best_node_idx,
    )
    src_node = species_tree[src_node_idx]
    dst_node = species_tree[dst_node_idx] if dst_node_idx is not None else None

    # Return an event with endpoint clades only; no extra metadata payload.
    event = AdmixtureEvent(
        src=_clade_tuple(frozenset(src_node.get_leaf_names())),
        dst=None if dst_node is None else _clade_tuple(frozenset(dst_node.get_leaf_names())),
        src_dist=None,
        dst_dist=None,
        style={},
        meta=None,
    )
    return event


def _max_internal_topo_distance(species_tree: ToyTree) -> int:
    """Return maximum topology-only distance among internal species-tree nodes."""
    internals = [n.idx for n in species_tree[species_tree.ntips:]]
    if len(internals) < 2:
        return 1
    maxdist = 1
    for i, n0 in enumerate(internals[:-1]):
        for n1 in internals[i + 1:]:
            dist = int(species_tree.distance.get_node_distance(n0, n1, topology_only=True))
            if dist > maxdist:
                maxdist = dist
    return maxdist


def _infer_event_endpoints(
    gene_tree: ToyTree,
    species_tree: ToyTree,
    imap: Mapping[str, str],
    node_idx: int,
) -> tuple[int, int | None]:
    """Return (src_node_idx, dst_node_idx) endpoints on the species tree."""
    node = gene_tree[node_idx]
    src_species = {imap[i] for i in node.get_leaf_names()}
    src_mrca = species_tree.get_mrca_node(*src_species)
    src = int(src_mrca.idx)

    dst_species: set[str] = set()
    if node.up is not None:
        parent_species = {imap[i] for i in node.up.get_leaf_names()}
        dst_species = parent_species - src_species
    if dst_species:
        dst_mrca = species_tree.get_mrca_node(*dst_species)
        dst = int(dst_mrca.idx)
    else:
        dst = None
    return src, dst


def _topological_displacement_from_endpoints(
    species_tree: ToyTree,
    src: int,
    dst: int | None,
    max_internal_dist: int,
) -> tuple[float | None, float | None]:
    """Return (raw, normalized) topology distance for event endpoints."""
    if dst is None:
        return None, None
    raw = float(species_tree.distance.get_node_distance(src, dst, topology_only=True))
    norm = raw / float(max_internal_dist)
    return raw, norm


def _compute_descendant_max_base_scores(
    gene_tree: ToyTree,
    base_by_idx: Mapping[int, float],
) -> dict[int, float]:
    """Return node->max descendant base score over candidate nodes only."""
    neg_inf = float("-inf")
    subtree_max: dict[int, float] = {}
    desc_max: dict[int, float] = {}

    # Post-order traversal (idx order) allows child->parent dynamic programming.
    for node in gene_tree:
        child_max = max((subtree_max[c.idx] for c in node.children), default=neg_inf)
        self_score = float(base_by_idx.get(node.idx, neg_inf))
        subtree_max[node.idx] = max(self_score, child_max)
        desc_max[node.idx] = child_max
    return desc_max


def _leave_one_out_zscores(values: np.ndarray) -> np.ndarray:
    """Return leave-one-out Z-scores for a 1D numeric array."""
    arr = np.asarray(values, dtype=float)
    nvals = arr.size
    if nvals <= 1:
        return np.zeros(nvals, dtype=float)

    total = float(arr.sum())
    total_sq = float(np.dot(arr, arr))
    out = np.zeros(nvals, dtype=float)
    denom = float(nvals - 1)
    for i, val in enumerate(arr):
        mean_others = (total - float(val)) / denom
        mean_sq_others = (total_sq - float(val) * float(val)) / denom
        var_others = mean_sq_others - mean_others * mean_others
        if var_others <= 0.0:
            out[i] = 0.0
        else:
            out[i] = (float(val) - mean_others) / float(np.sqrt(var_others))
    return out


def _event_topological_displacement(
    species_tree: ToyTree,
    event: AdmixtureEvent | None,
) -> tuple[float | None, float | None]:
    """Return (raw, normalized) topology displacement between event src/dst."""
    if (event is None) or (event.dst is None):
        return None, None
    src_node = species_tree.get_mrca_node(*event.src)
    dst_node = species_tree.get_mrca_node(*event.dst)
    return _topological_displacement_from_endpoints(
        species_tree=species_tree,
        src=int(src_node.idx),
        dst=int(dst_node.idx),
        max_internal_dist=_max_internal_topo_distance(species_tree),
    )


def alien_tree_index(
    species_tree: ToyTree,
    gene_tree: ToyTree,
    imap: Mapping[str, str],
    *,
    min_remaining_species: int = 4,
    min_candidate_species: int = 2,
    min_candidate_tips: int = 2,
    error_mode: Literal["local_nni", "none"] = "local_nni",
    normalize_rf: bool = True,
    max_subtree_nni_variants: int = 256,
    displacement_k: float = 3.0,
    min_score_z: float = 3.0,
) -> dict[str, object]:
    """Return alien-score results from species/gene-tree incongruence gains.

    Parameters
    ----------
    species_tree : ToyTree
        Species tree used as topology reference.
    gene_tree : ToyTree
        Gene tree that may include missing species and duplicated species copies.
    imap : Mapping[str, str]
        Mapping from gene-tree tip name to species-tree tip name.
    min_remaining_species : int, default=4
        Skip a candidate if pruning would leave fewer species than this threshold.
    min_candidate_species : int, default=2
        Minimum number of represented species under a candidate clade to test it.
    min_candidate_tips : int, default=2
        Minimum number of descendant gene tips under a candidate clade.
    error_mode : {"local_nni", "none"}, default="local_nni"
        If "local_nni", evaluate one-step local NNI variants around each candidate
        edge before pruning and keep the best RF score.
    normalize_rf : bool, default=True
        If True, RF is normalized by the total split count in both trees.
    max_subtree_nni_variants : int, default=256
        Maximum number of deterministic local-NNI variants used when scoring
        compatibility of a candidate subtree with the species tree.
    min_score_z : float, default=3.0
        Minimum alien-score Z value used to collect entries in the ``hits`` list.

    Returns
    -------
    dict[str, object]
        Dictionary with keys:
        - ``summary``: run-level aggregate statistics for this evaluation.
        - ``data``: per-node table of candidate and diagnostic scores.
        - ``hits``: list of compact dict records for nodes with
          ``alien_score_z >= min_score_z``.
    """
    _validate_inputs(species_tree, gene_tree, imap)
    if error_mode not in {"local_nni", "none"}:
        raise ValueError("error_mode must be one of: {'local_nni', 'none'}.")
    if (not np.isfinite(min_score_z)):
        raise ValueError("min_score_z must be a finite float.")

    # Precompute mapped species sets per node for fast candidate evaluation.
    desc_species = _descendant_species_sets(gene_tree, imap)
    all_species = frozenset(imap[name] for name in gene_tree.get_tip_labels())
    n_species_total = len(all_species)
    max_internal_dist = _max_internal_topo_distance(species_tree)
    rows: list[_CandidateScore] = []
    n_candidates_tested = 0

    # Score every internal node as a potential removable "alien" clade.
    for node in gene_tree[gene_tree.ntips:-1]:
        tip_names = node.get_leaf_names()
        cand_species = desc_species[node.idx]
        rem_species = all_species - cand_species
        src_node_idx, dst_node_idx = _infer_event_endpoints(
            gene_tree=gene_tree,
            species_tree=species_tree,
            imap=imap,
            node_idx=node.idx,
        )

        # Default row state for internal edges that fail candidate filters.
        rf_before = np.nan
        rf_after = np.nan
        gain_raw = 0.0
        gain_weighted = 0.0
        subtree_comp = 1.0
        subtree_rf = np.nan
        n_subtree_vars = 0
        gain_adjusted = 0.0
        disp_topo = None
        disp_topo_norm = None
        disp_term = 0.0
        gain_term = 0.0
        compat_term = 1.0
        alien_score_base = 0.0
        candidate_tested = False

        passes_filters = (
            (len(tip_names) >= min_candidate_tips)
            and (len(cand_species) >= min_candidate_species)
            and (len(rem_species) >= min_remaining_species)
        )
        if passes_filters:
            # Optionally evaluate local NNI alternatives before pruning.
            if error_mode == "local_nni":
                before_variants = _local_nni_variants(gene_tree, node.idx)
                rf_before = np.nanmin(
                    [_rf_distance(species_tree, t, imap, normalize_rf) for t in before_variants]
                )
            else:
                rf_before = _rf_distance(species_tree, gene_tree, imap, normalize_rf)

            # Remove candidate clade and evaluate how much species/gene fit improves.
            keep = [name for name in gene_tree.get_tip_labels() if name not in set(tip_names)]
            if len(keep) >= 4:
                pruned = gene_tree.mod.prune(*keep, preserve_dists=True, require_root=False)
                rf_after = _rf_distance(species_tree, pruned, imap, normalize_rf)

            if not np.isnan(rf_before) and not np.isnan(rf_after):
                candidate_tested = True
                n_candidates_tested += 1
                gain_raw = float(rf_before - rf_after)
                weight = float(len(rem_species) / max(1, n_species_total))
                gain_weighted = gain_raw * weight

                # Downweight gains when the removed subtree is itself species-compatible.
                subtree = gene_tree.mod.extract_subtree(node.idx)
                subtree_comp, subtree_rf, n_subtree_vars = _subtree_compatibility(
                    species_tree=species_tree,
                    subtree=subtree,
                    imap=imap,
                    normalize_rf=normalize_rf,
                    max_subtree_nni_variants=max_subtree_nni_variants,
                )
                gain_adjusted = gain_weighted * subtree_comp

                # Compute endpoint displacement for this candidate and transform it to [0, 1].
                disp_topo, disp_topo_norm = _topological_displacement_from_endpoints(
                    species_tree=species_tree,
                    src=src_node_idx,
                    dst=dst_node_idx,
                    max_internal_dist=max_internal_dist,
                )
                disp_term = (
                    0.0
                    if disp_topo_norm is None
                    else float(1.0 - np.exp(-displacement_k * disp_topo_norm))
                )

                # Composite score emphasizes prune improvement, compatibility, and displacement.
                gain_term = max(0.0, gain_weighted)
                compat_term = float(subtree_comp)
                alien_score_base = gain_term * compat_term * disp_term

        rows.append(
            _CandidateScore(
                node_idx=node.idx,
                n_gene_tips_removed=len(tip_names),
                n_species_removed=len(cand_species),
                n_species_remaining=len(rem_species),
                rf_before=float(rf_before),
                rf_after=float(rf_after),
                gain_raw=gain_raw,
                gain_weighted=gain_weighted,
                subtree_rf=float(subtree_rf) if not np.isnan(subtree_rf) else np.nan,
                subtree_compatibility=float(subtree_comp),
                gain_adjusted=float(gain_adjusted),
                gain_term=float(gain_term),
                compat_term=float(compat_term),
                disp_topo=disp_topo,
                disp_topo_norm=disp_topo_norm,
                disp_term=float(disp_term),
                alien_score_base=float(alien_score_base),
                best_descendant_alien_score_base=0.0,
                lineage_redundancy=0.0,
                lineage_nonredundancy=1.0,
                alien_score=float(alien_score_base),
                alien_score_z=0.0,
                src_node_idx=int(src_node_idx),
                dst_node_idx=dst_node_idx,
                candidate_tested=candidate_tested,
                subtree_nni_variants_tested=int(n_subtree_vars),
                tested_local_nni=(error_mode == "local_nni"),
            )
        )

    data = pd.DataFrame([r.__dict__ for r in rows])
    # Fallback for degenerate trees without internal edges to score.
    if data.empty:
        summary = {
            "min_score_z": float(min_score_z),
            "n_hits": 0,
            "alien_score_mean": 0.0,
            "alien_score_std": 0.0,
            "alien_score_z_mean": 0.0,
            "alien_score_z_std": 0.0,
            "n_internal_edges_scored": 0,
            "n_candidates_tested": 0,
            "n_species_total": n_species_total,
        }
        return {"summary": summary, "data": data, "hits": []}

    data["src_node_idx"] = data["src_node_idx"].astype(int)
    data["dst_node_idx"] = pd.array(data["dst_node_idx"], dtype="Int64")

    # Penalize ancestor-level candidates that are weaker than strong descendants.
    eps = 1e-12
    base_by_idx = {int(idx): float(score) for idx, score in zip(data["node_idx"], data["alien_score_base"])}
    desc_max_by_idx = _compute_descendant_max_base_scores(gene_tree, base_by_idx)
    data["best_descendant_alien_score_base"] = [
        0.0 if np.isneginf(desc_max_by_idx[int(idx)]) else float(desc_max_by_idx[int(idx)])
        for idx in data["node_idx"]
    ]
    ratio = data["best_descendant_alien_score_base"] / (data["alien_score_base"] + eps)
    data["lineage_redundancy"] = np.clip(ratio, 0.0, 1.0)
    data["lineage_nonredundancy"] = 1.0 - data["lineage_redundancy"]
    data["alien_score"] = data["alien_score_base"] * data["lineage_nonredundancy"]
    data["alien_score_z"] = _leave_one_out_zscores(data["alien_score"].to_numpy(dtype=float))

    # Build compact hit records for strong outliers.
    hits_df = data[data["alien_score_z"] >= float(min_score_z)].copy()
    hits_df = hits_df.sort_values(
        by=["alien_score_z", "alien_score", "node_idx"],
        ascending=[False, False, True],
    )
    hits: list[dict[str, object]] = []
    for row in hits_df.itertuples(index=False):
        event = _infer_best_event(
            gene_tree=gene_tree,
            species_tree=species_tree,
            imap=imap,
            best_node_idx=int(row.node_idx),
        )
        hits.append(
            {
                "gtree_node_idx": int(row.node_idx),
                "alien_score": float(row.alien_score),
                "alien_score_z": float(row.alien_score_z),
                "stree_src_node_idx": int(row.src_node_idx),
                "stree_dst_node_idx": None if pd.isna(row.dst_node_idx) else int(row.dst_node_idx),
                "sptree_src": tuple(sorted(species_tree[int(row.src_node_idx)].get_leaf_names())),
                "sptree_dst": (
                    None
                    if pd.isna(row.dst_node_idx)
                    else tuple(sorted(species_tree[int(row.dst_node_idx)].get_leaf_names()))
                ),
                "event": event,
            }
        )

    # Summary stores generic run information only.
    summary = {
        "min_score_z": float(min_score_z),
        "n_hits": int(len(hits)),
        "alien_score_mean": float(data["alien_score"].mean()),
        "alien_score_std": float(data["alien_score"].std(ddof=0)),
        "alien_score_z_mean": float(data["alien_score_z"].mean()),
        "alien_score_z_std": float(data["alien_score"].std(ddof=0)),
        "n_internal_edges_scored": int(data.shape[0]),
        "n_candidates_tested": int(n_candidates_tested),
        "n_species_total": n_species_total,
    }
    return {"summary": summary, "data": data, "hits": hits}


def _simulate_dup_loss_null_gene_tree(
    species_tree: ToyTree,
    *,
    target_ntips: int,
    target_species: int,
    rng: np.random.Generator,
) -> tuple[ToyTree, dict[str, str]]:
    """Simulate a simple duplication/loss-only null gene tree.

    Loss is represented as species pruning (missing taxa), and duplications
    are added as sister copies of random tips.
    """
    # Sample retained species (loss process) from the species tree.
    species_labels = species_tree.get_tip_labels()
    target_species = max(2, min(target_species, len(species_labels)))

    keep_species = list(rng.choice(species_labels, size=target_species, replace=False))
    gtree = species_tree.mod.prune(*keep_species, preserve_dists=True, require_root=False)

    # Label retained tips as gene-copy IDs and initialize imap.
    # assign gene-copy labels and map.
    imap: dict[str, str] = {}
    counters = {sp: 0 for sp in keep_species}
    for node in gtree[: gtree.ntips]:
        sp = node.name
        gname = f"{sp}__{counters[sp]}"
        counters[sp] += 1
        node.name = gname
        imap[gname] = sp
    gtree._update()

    # Add random sister copies to emulate duplications.
    # add duplications to match target ntips.
    ndups = max(0, target_ntips - gtree.ntips)
    for _ in range(ndups):
        tip = gtree[int(rng.integers(gtree.ntips))]
        sp = imap[tip.name]
        new_name = f"{sp}__{counters[sp]}"
        counters[sp] += 1
        gtree = gtree.mod.add_sister_node(tip.idx, name=new_name, inplace=False)
        imap[new_name] = sp

    return gtree, imap


def alien_tree_hybrid_null(
    species_tree: ToyTree,
    gene_tree: ToyTree,
    imap: Mapping[str, str],
    *,
    nreps_parametric: int = 200,
    nreps_random_prune: int = 200,
    seed: int | None = None,
    min_remaining_species: int = 4,
    min_candidate_species: int = 2,
    min_candidate_tips: int = 2,
    error_mode: Literal["local_nni", "none"] = "local_nni",
    normalize_rf: bool = True,
    max_subtree_nni_variants: int = 256,
    displacement_k: float = 3.0,
    min_score_z: float = 3.0,
) -> dict[str, object]:
    """Return hybrid-null significance for the alien score.

    Hybrid null combines:
    1) parametric duplication/loss-only simulations (no HGT), and
    2) matched random-prune sampling from observed candidate clades.
    """
    # Compute observed score once, then compare against two null expectations.
    rng = np.random.default_rng(seed)
    observed = alien_tree_index(
        species_tree=species_tree,
        gene_tree=gene_tree,
        imap=imap,
        min_remaining_species=min_remaining_species,
        min_candidate_species=min_candidate_species,
        min_candidate_tips=min_candidate_tips,
        error_mode=error_mode,
        normalize_rf=normalize_rf,
        max_subtree_nni_variants=max_subtree_nni_variants,
        displacement_k=displacement_k,
        min_score_z=min_score_z,
    )
    observed_score = (
        float(observed["data"]["alien_score"].max())
        if not observed["data"].empty
        else 0.0
    )
    odata = observed["data"]

    # Parametric null: dup/loss-only simulated families with matched size stats.
    # parametric null distribution.
    obs_species = len({imap[name] for name in gene_tree.get_tip_labels()})
    obs_ntips = gene_tree.ntips
    null_param = np.zeros(nreps_parametric, dtype=float)
    for ridx in range(nreps_parametric):
        ntree, nimap = _simulate_dup_loss_null_gene_tree(
            species_tree=species_tree,
            target_ntips=obs_ntips,
            target_species=obs_species,
            rng=rng,
        )
        nres = alien_tree_index(
            species_tree=species_tree,
            gene_tree=ntree,
            imap=nimap,
            min_remaining_species=min_remaining_species,
            min_candidate_species=min_candidate_species,
            min_candidate_tips=min_candidate_tips,
            error_mode=error_mode,
            normalize_rf=normalize_rf,
            max_subtree_nni_variants=max_subtree_nni_variants,
            displacement_k=displacement_k,
            min_score_z=min_score_z,
        )
        null_param[ridx] = (
            float(nres["data"]["alien_score"].max())
            if not nres["data"].empty
            else 0.0
        )

    # Nonparametric null: matched random-prune values from observed candidates.
    # matched random-prune null distribution from observed candidates.
    null_rand = np.zeros(nreps_random_prune, dtype=float)
    if odata.empty:
        null_rand[:] = 0.0
    else:
        best = odata.iloc[int(odata["alien_score"].argmax())]
        matched = odata[
            (odata["n_gene_tips_removed"] == best["n_gene_tips_removed"])
            & (odata["n_species_removed"] == best["n_species_removed"])
        ]
        if matched.empty:
            matched = odata
        vals = matched["alien_score"].to_numpy(dtype=float)
        picks = rng.integers(0, vals.size, size=nreps_random_prune)
        null_rand = vals[picks]

    # Conservative hybrid p-value uses the less significant of the two tests.
    p_param = float((1 + np.sum(null_param >= observed_score)) / (nreps_parametric + 1))
    p_rand = float((1 + np.sum(null_rand >= observed_score)) / (nreps_random_prune + 1))
    return {
        "observed": observed,
        "observed_alien_score": observed_score,
        "null_parametric": null_param,
        "null_random_prune": null_rand,
        "pvalue_parametric": p_param,
        "pvalue_random_prune": p_rand,
        "pvalue_hybrid": max(p_param, p_rand),
    }
