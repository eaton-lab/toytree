#!/usr/bin/env python

"""Internal helpers for OTOL induced-tree Newick construction."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Callable

import pandas as pd

from toytree.utils import ToytreeError


def _parse_ott_id_from_label(label: str) -> int | None:
    """Extract OTT ID from a label containing one-or-more ``ott<digits>`` tokens."""
    matches = re.findall(r"ott(\d+)", str(label), flags=re.IGNORECASE)
    return int(matches[-1]) if matches else None


def _parse_ott_id_token(token: str | int) -> int:
    """Parse OTT ID from integer or OTT-like token string."""
    if isinstance(token, int):
        return int(token)
    text = str(token).strip()
    ott_matches = re.findall(r"ott(\d+)", text, flags=re.IGNORECASE)
    if ott_matches:
        return int(ott_matches[-1])
    digit_matches = re.findall(r"(\d+)", text)
    if not digit_matches:
        raise ToytreeError(f"could not parse ott_id from token: {token!r}")
    return int(digit_matches[-1])


def _normalize_label_token(text: str) -> str:
    """Normalize label text for Newick-safe taxon tokens."""
    return re.sub(r"\s+", "_", str(text).strip())


def _resolve_anchor_node(tree: Any, anchor_label: str) -> Any:
    """Return node matching anchor label, or root if no exact match is found."""
    for node in tree:
        if str(node.name) == str(anchor_label):
            return node
    return tree.treenode


def _get_nonbroken_tip_ott_ids(tree: Any) -> list[int]:
    """Return OTT IDs parsed from tip labels on an induced backbone tree."""
    out: list[int] = []
    for tip in tree[: tree.ntips]:
        ott = _parse_ott_id_from_label(str(tip.name))
        if ott is not None:
            out.append(ott)
    return out


def _get_all_ott_ids(
    nonbroken_tip_ott_ids: list[int], broken: dict[str, Any]
) -> list[int]:
    """Return sorted union of non-broken and broken OTT IDs."""
    broken_ott_ids = [_parse_ott_id_token(key) for key in broken]
    all_ott_ids = sorted(set(nonbroken_tip_ott_ids + broken_ott_ids))
    if not all_ott_ids:
        raise ToytreeError(
            "could not extract ott_ids from induced tree tips or broken mapping."
        )
    return all_ott_ids


def _build_rec_by_ott(
    records: list[dict[str, Any]], all_ott_ids: list[int]
) -> dict[int, dict[str, Any]]:
    """Build OTT-indexed lineage record mapping and validate completeness."""
    rec_by_ott: dict[int, dict[str, Any]] = {}
    for rec in records:
        ott = rec.get("ott_id")
        if ott is None:
            raise ToytreeError("lineage record missing required key 'ott_id'.")
        rec_by_ott[int(ott)] = rec
    missing = [ott for ott in all_ott_ids if ott not in rec_by_ott]
    if missing:
        raise ToytreeError(f"missing lineage records for ott_ids: {missing!r}")
    return rec_by_ott


def _score_lineage_overlap(
    left: dict[str, Any],
    right: dict[str, Any],
    rank_map: dict[str, int],
    extract_ranked_ancestors: Callable[
        [dict[str, Any], dict[str, int]], dict[int, tuple[int, str, int]]
    ],
) -> int:
    """Return most-specific shared-rank code between two lineage records."""
    no_shared = max(rank_map.values()) + 1
    left_anc = extract_ranked_ancestors(left, rank_map)
    right_anc = extract_ranked_ancestors(right, rank_map)
    shared = set(left_anc).intersection(right_anc)
    if not shared:
        return no_shared
    return min(min(left_anc[key][0], right_anc[key][0]) for key in shared)


def _add_broken_tip_under_best_overlap(
    tree: Any,
    broken_ott: int,
    b_rec: dict[str, Any],
    rec_by_ott: dict[int, dict[str, Any]],
    rank_map: dict[str, int],
    candidate_tips: list[Any],
    extract_ranked_ancestors: Callable[
        [dict[str, Any], dict[str, int]], dict[int, tuple[int, str, int]]
    ],
) -> Any:
    """Insert one broken OTT tip at winner node or winner MRCA among ties."""
    scored: list[tuple[int, str]] = []
    for tip in candidate_tips:
        ott = _parse_ott_id_from_label(str(tip.name))
        if ott is None:
            continue
        score = _score_lineage_overlap(
            b_rec,
            rec_by_ott[ott],
            rank_map,
            extract_ranked_ancestors,
        )
        scored.append((score, str(tip.name)))
    if not scored:
        raise ToytreeError(
            "failed to score constrained candidates for broken placement."
        )
    min_score = min(i[0] for i in scored)
    winners = [name for score, name in scored if score == min_score]
    if len(winners) == 1:
        target = tree.get_nodes(winners[0])[0]
    else:
        winner_nodes = [tree.get_nodes(name)[0] for name in winners]
        target = tree.get_mrca_node(*winner_nodes)
    return tree.mod.add_child_node(target, name=f"ott{broken_ott}", dist=1.0)


def _insert_broken_on_unconstrained_induced_tree(
    tree: Any,
    broken: dict[str, Any],
    rec_by_ott: dict[int, dict[str, Any]],
    rank_map: dict[str, int],
    nonbroken_tip_ott_ids: list[int],
    extract_ranked_ancestors: Callable[
        [dict[str, Any], dict[str, int]], dict[int, tuple[int, str, int]]
    ],
) -> Any:
    """Insert broken tips directly on induced tree using anchor-clade constraints."""
    for key, anchor_label in broken.items():
        broken_ott = _parse_ott_id_token(key)
        b_rec = rec_by_ott[broken_ott]
        anchor = _resolve_anchor_node(tree, str(anchor_label))

        candidate_tips = []
        for tip in anchor.iter_leaves():
            ott = _parse_ott_id_from_label(str(tip.name))
            if ott in nonbroken_tip_ott_ids:
                candidate_tips.append(tip)
        if not candidate_tips:
            for tip in tree[: tree.ntips]:
                ott = _parse_ott_id_from_label(str(tip.name))
                if ott in nonbroken_tip_ott_ids:
                    candidate_tips.append(tip)
        if not candidate_tips:
            raise ToytreeError(
                "no candidate non-broken tips available for broken placement."
            )
        tree = _add_broken_tip_under_best_overlap(
            tree=tree,
            broken_ott=broken_ott,
            b_rec=b_rec,
            rec_by_ott=rec_by_ott,
            rank_map=rank_map,
            candidate_tips=candidate_tips,
            extract_ranked_ancestors=extract_ranked_ancestors,
        )
    return tree


def _build_taxonomy_rank_scaffold(
    records: list[dict[str, Any]],
    rank_map: dict[str, int],
    extract_ranked_ancestors: Callable[
        [dict[str, Any], dict[str, int]], dict[int, tuple[int, str, int]]
    ],
) -> Any:
    """Return taxonomy scaffold tree with queried taxa as ``ott{ID}`` leaves."""
    import toytree

    root = toytree.Node(name="taxonomy_root", dist=0.0)
    node_by_ott: dict[int, Any] = {}
    query_leaf_by_ott: dict[int, Any] = {}
    for rec in records:
        ott = rec.get("ott_id")
        if ott is None:
            raise ToytreeError("lineage record missing required key 'ott_id'.")
        ott_i = int(ott)
        anc = extract_ranked_ancestors(rec, rank_map)
        path = sorted(anc.values(), key=lambda x: x[0], reverse=True)

        parent = root
        for _, name, anc_ott in path:
            node = node_by_ott.get(int(anc_ott))
            if node is None:
                safe_name = _normalize_label_token(name)
                node = toytree.Node(name=f"{safe_name}_ott{anc_ott}", dist=1.0)
                node_by_ott[int(anc_ott)] = node
            if node._up is None:
                parent._add_child(node)
            parent = node
        if ott_i not in query_leaf_by_ott:
            qleaf = toytree.Node(name=f"ott{ott_i}", dist=1.0)
            query_leaf_by_ott[ott_i] = qleaf
            parent._add_child(qleaf)

    tree = toytree.ToyTree(root)
    if tree.treenode.name == "taxonomy_root" and len(tree.treenode.children) == 1:
        tree = tree.mod.remove_unary_nodes()
    return tree


def _refine_scaffold_with_induced(scaffold: Any, induced: Any) -> Any:
    """Resolve scaffold polytomies with induced topology.

    Existing taxonomy clades are kept as hard constraints.
    """
    import toytree

    for node in list(scaffold[scaffold.ntips :]):
        if len(node.children) <= 2:
            continue
        groups: list[tuple[Any, set[str]]] = []
        for child in node.children:
            child_tips = {
                str(tip.name)
                for tip in child.iter_leaves()
                if _parse_ott_id_from_label(tip.name)
            }
            if child_tips:
                groups.append((child, child_tips))
        if len(groups) <= 2:
            continue
        if any(not induced.get_nodes(lbl) for _, tips in groups for lbl in tips):
            continue

        group_is_monophyletic = True
        for _, tips in groups:
            if len(tips) < 2:
                continue
            gmrca = induced.get_mrca_node(*sorted(tips))
            gdesc = {str(i.name) for i in gmrca.iter_leaves()}
            if gdesc != tips:
                group_is_monophyletic = False
                break
        if not group_is_monophyletic:
            continue

        reps: list[str] = [sorted(tips)[0] for _, tips in groups]
        itemp = induced.mod.prune(*reps, require_root=False)
        rep_to_child = {
            rep: child.copy(detach=True) for (child, _), rep in zip(groups, reps)
        }

        def _expand(rep_node: Any) -> Any:
            if rep_node.is_leaf():
                return rep_to_child[str(rep_node.name)]
            inode = toytree.Node(name="", dist=1.0)
            for cnode in rep_node.children:
                inode._add_child(_expand(cnode))
            return inode

        expanded = _expand(itemp.treenode)
        node._children = tuple()
        if expanded.is_leaf():
            node._add_child(expanded)
        else:
            for child in expanded.children:
                node._add_child(child)
        scaffold._update()
    return scaffold


def _normalize_induced_tips_to_ott(induced: Any) -> tuple[Any, list[int]]:
    """Relabel induced tips as ``ott{ID}`` and return the collected non-broken IDs."""
    induced_tip_map: dict[int, str] = {}
    nonbroken_ott_ids: list[int] = []
    for tip in induced[: induced.ntips]:
        ott = _parse_ott_id_from_label(str(tip.name))
        if ott is None:
            raise ToytreeError("induced subtree tip labels must include ott_id tokens.")
        nonbroken_ott_ids.append(ott)
        induced_tip_map[tip.idx] = f"ott{ott}"
    induced.set_node_data("name", induced_tip_map, inplace=True)
    return induced, nonbroken_ott_ids


def _build_taxonomy_constrained_tree(
    induced: Any,
    broken: dict[str, Any],
    rec_by_ott: dict[int, dict[str, Any]],
    rank_map: dict[str, int],
    extract_ranked_ancestors: Callable[
        [dict[str, Any], dict[str, int]], dict[int, tuple[int, str, int]]
    ],
) -> Any:
    """Build taxonomy-constrained induced tree and insert broken taxa."""
    induced, nonbroken_ott_ids = _normalize_induced_tips_to_ott(induced)
    nonbroken_records = [rec_by_ott[i] for i in nonbroken_ott_ids if i in rec_by_ott]
    scaffold = _build_taxonomy_rank_scaffold(
        records=nonbroken_records,
        rank_map=rank_map,
        extract_ranked_ancestors=extract_ranked_ancestors,
    )
    tree = _refine_scaffold_with_induced(scaffold, induced)
    nonbroken_labels = {f"ott{i}" for i in nonbroken_ott_ids}

    for key, anchor_label in broken.items():
        broken_ott = _parse_ott_id_token(key)
        b_rec = rec_by_ott.get(broken_ott)
        if b_rec is None:
            raise ToytreeError(
                f"missing lineage record for broken ott_id: {broken_ott}"
            )

        ianchor = _resolve_anchor_node(induced, str(anchor_label))
        anchor_labels = [
            str(i.name)
            for i in ianchor.iter_leaves()
            if str(i.name) in nonbroken_labels
        ]
        if anchor_labels:
            target_anchor = tree.get_mrca_node(*anchor_labels)
        else:
            target_anchor = tree.treenode
        candidate_tips = [
            i for i in target_anchor.iter_leaves() if str(i.name) in nonbroken_labels
        ]
        if not candidate_tips:
            candidate_tips = [
                i for i in tree[: tree.ntips] if str(i.name) in nonbroken_labels
            ]
        if not candidate_tips:
            raise ToytreeError(
                "no candidate non-broken tips available for broken placement."
            )

        tree = _add_broken_tip_under_best_overlap(
            tree=tree,
            broken_ott=broken_ott,
            b_rec=b_rec,
            rec_by_ott=rec_by_ott,
            rank_map=rank_map,
            candidate_tips=candidate_tips,
            extract_ranked_ancestors=extract_ranked_ancestors,
        )
    return tree


def _build_unconstrained_tree(
    induced: Any,
    broken: dict[str, Any],
    rec_by_ott: dict[int, dict[str, Any]],
    rank_map: dict[str, int],
    extract_ranked_ancestors: Callable[
        [dict[str, Any], dict[str, int]], dict[int, tuple[int, str, int]]
    ],
) -> Any:
    """Build induced tree without taxonomy scaffold constraints."""
    nonbroken_tip_ott_ids = _get_nonbroken_tip_ott_ids(induced)
    return _insert_broken_on_unconstrained_induced_tree(
        tree=induced,
        broken=broken,
        rec_by_ott=rec_by_ott,
        rank_map=rank_map,
        nonbroken_tip_ott_ids=nonbroken_tip_ott_ids,
        extract_ranked_ancestors=extract_ranked_ancestors,
    )


def _relabel_tree_tips(tree: Any, label_by_ott: dict[int, str]) -> None:
    """Relabel tips from mapping keyed by OTT ID, preserving unknown node labels."""
    tip_map: dict[int, str] = {}
    for tip in tree[: tree.ntips]:
        ott = _parse_ott_id_from_label(str(tip.name))
        if (ott is None) or (ott not in label_by_ott):
            # Synthetic node-like labels (for example mrcaott... tokens) can
            # legitimately survive insertion workflows; keep them as-is.
            tip_map[tip.idx] = _normalize_label_token(str(tip.name))
            continue
        tip_map[tip.idx] = str(label_by_ott[int(ott)])
    if len(set(tip_map.values())) != len(tip_map):
        raise ToytreeError(
            "label formatting produced duplicate labels; "
            "choose a more specific label_template."
        )
    tree.set_node_data("name", tip_map, inplace=True)


# Define absolute anchor depths (higher = deeper in time/broader taxa)
DEFAULT_ANCHORS = {
    'life': 100,
    'domain': 90,
    'kingdom': 80,
    'phylum': 70,
    'class': 60,
    'order': 50,
    'superfamily': 45,
    'family': 40,
    'subfamily': 35,
    'tribe': 30,
    'subtribe': 25,
    'genus': 10,
    'species': 0
}


def build_cophenetic_distance_matrix_from_taxonomy(
    taxa_dict: dict[str, Any],
    anchors: dict[str, int] = DEFAULT_ANCHORS,
):
    """Return pairwise cophenetic distance matrix.

    Distance = (Path from Tip A to MRCA) + (Path from Tip B to MRCA)
    using linearly interpolated depths for unranked nodes.
    """
    global_depths_temp = defaultdict(list)

    # --- STEP 1: Interpolate depths per lineage ---
    for taxon, lineage in taxa_dict.items():
        pinned = []

        # Find all nodes with a recognized rank
        for i, (name, rank, *_) in enumerate(lineage):
            if rank in anchors:
                pinned.append((i, anchors[rank]))

        # Fallbacks: If the tip (index 0) or root (last index) aren't anchored
        if not pinned or pinned[0][0] != 0:
            # Default unranked tips to 0.
            # E.g., if a lineage starts at "family" (40), it gets pinned to 40
            # instead of 0.
            pinned.insert(0, (0, 0))
        if pinned[-1][0] != len(lineage) - 1:
            pinned.append((len(lineage) - 1, anchors.get('life', 100)))

        lineage_depths = [None] * len(lineage)

        # Linear interpolation between pinned anchors
        for p in range(len(pinned) - 1):
            idx1, val1 = pinned[p]
            idx2, val2 = pinned[p+1]

            lineage_depths[idx1] = val1
            lineage_depths[idx2] = val2

            steps = idx2 - idx1
            if steps > 1:
                step_size = (val2 - val1) / steps
                for j in range(1, steps):
                    lineage_depths[idx1 + j] = val1 + (step_size * j)

        # Store in our global tracker
        for node, depth in zip(lineage, lineage_depths):
            global_depths_temp[node].append(depth)

    # --- STEP 2: Average globally for consistent MRCA depths ---
    final_node_depths = {
        node: sum(depths) / len(depths)
        for node, depths in global_depths_temp.items()
    }

    # --- STEP 3: Build the Cophenetic Pairwise Matrix ---
    taxa_names = list(taxa_dict.keys())
    n = len(taxa_names)
    distance_matrix = pd.DataFrame(0.0, index=taxa_names, columns=taxa_names)

    for i in range(n):
        for j in range(i + 1, n):
            taxon_a = taxa_names[i]
            taxon_b = taxa_names[j]

            lineage_a = taxa_dict[taxon_a]
            lineage_b = taxa_dict[taxon_b]

            # Identify the lowest shared MRCA
            mrca = None
            for node in lineage_a:
                if node in lineage_b:
                    mrca = node
                    break

            # Retrieve depths
            mrca_depth = final_node_depths[mrca] if mrca else anchors.get('life', 100)
            distance_matrix.at[taxon_a, taxon_b] = mrca_depth
            distance_matrix.at[taxon_b, taxon_a] = mrca_depth
    return distance_matrix, final_node_depths
