#!/usr/bin/env python

"""Consensus tree inference and feature mapping."""

from __future__ import annotations

import sys
from collections import defaultdict
from typing import Iterable, Optional

import numpy as np

from toytree.core import Node, ToyTree

__all__ = [
    "consensus_tree",
    "consensus_features",
]


def _as_treelist(trees: Iterable[ToyTree]) -> list[ToyTree]:
    """Return trees as a concrete list."""
    if hasattr(trees, "treelist"):
        treelist = list(trees.treelist)
    else:
        treelist = list(trees)
    if not treelist:
        raise ValueError("at least one tree is required.")
    if any(not isinstance(i, ToyTree) for i in treelist):
        raise TypeError("all items in 'trees' must be ToyTree objects.")
    return treelist


def _validate_shared_tips(trees: list[ToyTree]) -> frozenset[str]:
    """Validate all trees share the same unique tip labels."""
    labels = trees[0].get_tip_labels()
    if len(set(labels)) != len(labels):
        raise ValueError("tip labels must be unique within each tree.")
    tips = frozenset(labels)
    for idx, tree in enumerate(trees[1:], start=1):
        tlabels = tree.get_tip_labels()
        if len(set(tlabels)) != len(tlabels):
            raise ValueError(
                f"tip labels must be unique within each tree (tree index={idx})."
            )
        if frozenset(tlabels) != tips:
            raise ValueError("all trees must contain the same set of tip labels.")
    return tips


def _canonical_split(clade: frozenset[str], all_tips: frozenset[str]) -> frozenset[str]:
    """Return canonical root-invariant representation of a split side."""
    if (not clade) or (clade == all_tips):
        return all_tips
    other = all_tips - clade
    if len(clade) < len(other):
        return clade
    if len(other) < len(clade):
        return other
    return clade if tuple(sorted(clade)) <= tuple(sorted(other)) else other


def _numeric_or_none(value) -> Optional[float]:
    """Return float(value) for finite numeric values else None."""
    if value is None:
        return None
    if isinstance(value, (bool, str)):
        return None
    if isinstance(value, (int, float, np.number)):
        value = float(value)
        return value if np.isfinite(value) else None
    return None


def _normalize_features(features: Optional[list[str] | str]) -> list[str]:
    """Normalize feature argument to a list of feature names."""
    if features is None:
        return []
    if isinstance(features, str):
        return [features]
    return [i for i in features if i]


def _feature_exists_anywhere(trees: list[ToyTree], feature: str) -> bool:
    """Return True if a node feature exists in any input tree."""
    for tree in trees:
        if feature in tree.features:
            return True
    return False


def _edge_feature_exists_anywhere(trees: list[ToyTree], feature: str) -> bool:
    """Return True if an edge feature exists in any input tree."""
    for tree in trees:
        if feature in tree.edge_features:
            return True
    return False


def _get_feature_value(node: Node, feature: str) -> Optional[float]:
    """Return numeric feature from a node."""
    return _numeric_or_none(getattr(node, feature, None))


def _set_summary_attrs(node: Node, feature: str, values: list[float]) -> None:
    """Set summary attributes for one feature on one node."""
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return
    fmin = float(np.min(arr))
    fmax = float(np.max(arr))
    setattr(node, f"{feature}_mean", float(np.mean(arr)))
    setattr(node, f"{feature}_median", float(np.median(arr)))
    setattr(node, f"{feature}_std", float(np.std(arr)))
    setattr(node, f"{feature}_min", fmin)
    setattr(node, f"{feature}_max", fmax)
    setattr(node, f"{feature}_range", fmax - fmin)
    setattr(node, f"{feature}_count", int(arr.size))


def check_trees_set_for_ultrametric(trees: list[ToyTree]) -> None:
    """Raise if trees are not rooted+ultrametric."""
    for tidx, tre in enumerate(trees):
        # Rootedness is required because node heights are only meaningful on rooted trees.
        if not tre.is_rooted():
            raise ValueError(
                "input trees are not rooted. Cannot use option ultrametric=True "
                f"(tree index={tidx})."
            )

        # In an ultrametric tree, all tip heights are ~0 in toytree's representation.
        tip_heights = np.fromiter(
            (node._height for node in tre[: tre.ntips]), dtype=float
        )
        if not np.allclose(tip_heights, 0.0, atol=1e-5):
            raise ValueError(
                "input trees are not ultrametric. Cannot use option ultrametric=True "
                f"(tree index={tidx})."
            )


def get_clade_frequencies(
    trees: Iterable[ToyTree],
) -> dict[frozenset[str], dict[str, object]]:
    """Return split frequencies and dist samples keyed by canonical clades."""
    # Validate input once and reuse normalized state in the full traversal.
    treelist = _as_treelist(trees)
    all_tips = _validate_shared_tips(treelist)
    ntrees = len(treelist)

    # Seed with the full clade so root-level metadata stays available.
    clades: dict[frozenset[str], dict[str, object]] = {
        all_tips: {"count": ntrees, "dist": []},
    }
    for tre in treelist:
        # Track split keys already seen in this source tree so each split counts once per tree.
        seen: set[frozenset[str]] = set()
        rooted = tre.is_rooted()
        for node in tre[:-1]:
            # Canonicalize each node clade into a root-invariant split key.
            clade = (
                frozenset(node.get_leaf_names())
                if not node.is_leaf()
                else frozenset((node.name,))
            )
            key = _canonical_split(clade, all_tips)
            if key in seen:
                continue
            seen.add(key)

            # For rooted trees, the root-adjacent edge becomes a merged edge if unrooted.
            if rooted and node._up is not None and node._up.is_root():
                # In rooted trees this split becomes the merged edge on unrooting.
                dist = sum(i._dist for i in node._up.children)
            else:
                dist = node._dist
            dist = _numeric_or_none(dist)
            # Store split count and optional dist sample for downstream summaries.
            if key not in clades:
                clades[key] = {"count": 1, "dist": [] if dist is None else [dist]}
            else:
                clades[key]["count"] = int(clades[key]["count"]) + 1
                if dist is not None:
                    clades[key]["dist"].append(dist)

    # Deterministic ordering: frequency desc, clade-size desc, lexical key.
    ordered = sorted(
        clades,
        key=lambda c: (
            -int(clades[c]["count"]),
            -len(c),
            tuple(sorted(c)),
        ),
    )
    out = {clade: clades[clade] for clade in ordered}
    for clade, data in out.items():
        data["freq"] = int(data["count"]) / ntrees
    return out


def get_consensus_clades(
    clades: dict[frozenset[str], dict[str, object]],
    min_freq: float,
) -> dict[frozenset[str], dict[str, object]]:
    """Return non-conflicting clades above a frequency cutoff."""

    def _conflicts(a: frozenset[str], b: frozenset[str]) -> bool:
        if a.isdisjoint(b):
            return False
        if a.issubset(b):
            return False
        if a.issuperset(b):
            return False
        return True

    keep: dict[frozenset[str], dict[str, object]] = {}
    banned: set[frozenset[str]] = set()
    tol = 1e-12
    for clade, data in clades.items():
        if any(_conflicts(clade, bclade) for bclade in banned):
            continue
        freq = float(data["freq"])
        if freq < min_freq:
            continue
        conflicts = []
        for kclade in keep:
            if _conflicts(kclade, clade):
                conflicts.append(kclade)

        if not conflicts:
            keep[clade] = data
            continue

        # drop equal-frequency conflicting clades (collapse ambiguous split).
        if all(abs(freq - float(keep[c]["freq"])) <= tol for c in conflicts):
            banned.add(clade)
            for cclade in conflicts:
                keep.pop(cclade, None)
                banned.add(cclade)
    return keep


def build_consensus_tree(clades: dict[frozenset[str], dict[str, object]]) -> ToyTree:
    """Build consensus tree from a dict of compatible clades."""
    if not clades:
        raise ValueError("no clades available to build a consensus tree.")

    sclades = sorted(clades, key=len, reverse=True)
    root_clade = sclades.pop(0)
    root = Node()
    sets_to_nodes: dict[frozenset[str], Node] = {root_clade: root}

    for clade in sclades:
        name = str(*clade) if len(clade) == 1 else ""
        dist_values = [float(i) for i in clades[clade].get("dist", [])]
        dist_mean = float(np.mean(dist_values)) if dist_values else np.nan
        node = Node(name=name, support=float(clades[clade]["freq"]), dist=dist_mean)
        if dist_values:
            _set_summary_attrs(node, "dist", dist_values)

        for eclade in sorted(sets_to_nodes, key=len):
            if clade.issubset(eclade):
                sets_to_nodes[eclade]._add_child(node)
                break
        sets_to_nodes[clade] = node

    tree = ToyTree(root)
    tree[-1].support = np.nan
    for nidx in range(tree.ntips):
        tree[nidx].support = np.nan

    for stat in ("mean", "median", "std", "min", "max", "range", "count"):
        tree.edge_features.add(f"dist_{stat}")
    return tree


def _collect_source_node_maps(
    tree: ToyTree, all_tips: frozenset[str]
) -> dict[frozenset[str], Node]:
    """Map canonical split keys to source tree nodes."""
    cmap: dict[frozenset[str], Node] = {}
    for node in tree[tree.ntips :]:
        clade = frozenset(node.get_leaf_names())
        key = _canonical_split(clade, all_tips)
        if key == all_tips:
            continue
        if key not in cmap:
            cmap[key] = node
            continue
        # Prefer the node whose clade equals the canonical split side.
        if clade == key:
            cmap[key] = node
    return cmap


def map_features_from_unrooted_trees_to_unrooted_tree(
    tree: ToyTree,
    trees: Iterable[ToyTree],
    features: Optional[list[str] | str] = None,
    edge_features: Optional[list[str] | str] = None,
    conditional: bool = False,
) -> ToyTree:
    """Map provided feature summaries from unrooted source trees."""
    treelist = _as_treelist(trees)
    all_tips = _validate_shared_tips(treelist)
    if frozenset(tree.get_tip_labels()) != all_tips:
        raise ValueError("consensus tree and input trees must share the same tip set.")

    # Operate on an unrooted copy so split matching is root-invariant.
    out = tree.unroot()

    # Build lookup tables on target tree: internal split key -> node and tip name -> node.
    target_internal: dict[frozenset[str], Node] = {}
    for node in out[out.ntips :]:
        clade = frozenset(node.get_leaf_names())
        target_internal[_canonical_split(clade, all_tips)] = node
    target_tips = {node.name: node for node in out[: out.ntips]}

    # Normalize requested feature lists and keep a union for shared collection logic.
    feat_list = list(dict.fromkeys(_normalize_features(features)))
    edge_feat_list = list(dict.fromkeys(_normalize_features(edge_features)))
    all_feats = feat_list + [i for i in edge_feat_list if i not in feat_list]

    # Accumulate raw per-node values (internal splits and tips) before summarizing.
    data: dict[tuple[int, str], list[float]] = defaultdict(list)
    tip_data: dict[tuple[int, str], list[float]] = defaultdict(list)

    # Single pass through each source tree:
    # 1) map internal split-matched values to target internal nodes;
    # 2) map tip values directly by tip name;
    # 3) optional conditional tip mapping for edge features using matched splits.
    for tre in treelist:
        source_map = _collect_source_node_maps(tre, all_tips)
        for key, src_node in source_map.items():
            tgt_node = target_internal.get(key)
            if tgt_node is None:
                continue
            for feat in all_feats:
                value = _get_feature_value(src_node, feat)
                if value is not None:
                    data[(tgt_node.idx, feat)].append(value)

            if conditional:
                for efeat in edge_feat_list:
                    eval_ = _get_feature_value(src_node, efeat)
                    if eval_ is None:
                        continue
                    for child in src_node.children:
                        if child.is_leaf() and child.name in target_tips:
                            tip_data[(target_tips[child.name].idx, efeat)].append(eval_)
                    if src_node.up is not None and src_node.up.is_root():
                        for child in src_node.get_sisters():
                            if child.is_leaf() and child.name in target_tips:
                                tip_data[(target_tips[child.name].idx, efeat)].append(
                                    eval_
                                )

        for tip in tre[: tre.ntips]:
            for feat in all_feats:
                if conditional and feat in edge_feat_list:
                    continue
                value = _get_feature_value(tip, feat)
                if value is not None and tip.name in target_tips:
                    tip_data[(target_tips[tip.name].idx, feat)].append(value)

    # Convert accumulated values into summary statistics on the target tree.
    for (node_idx, feat), values in data.items():
        _set_summary_attrs(out[node_idx], feat, values)
    for (node_idx, feat), values in tip_data.items():
        _set_summary_attrs(out[node_idx], feat, values)

    # Register edge-feature summaries so they are preserved as edge-polarized data.
    for feat in edge_feat_list:
        out.edge_features.add(feat)
        for stat in ("mean", "median", "std", "min", "max", "range", "count"):
            out.edge_features.add(f"{feat}_{stat}")
    return out


def map_features_from_rooted_trees_to_rooted_tree(
    tree: ToyTree,
    trees: Iterable[ToyTree],
    features: Optional[list[str] | str] = None,
    edge_features: Optional[list[str] | str] = None,
    conditional: bool = False,
) -> ToyTree:
    """Map provided feature summaries from rooted source trees."""
    _ = conditional  # reserved for API compatibility
    treelist = _as_treelist(trees)
    all_tips = _validate_shared_tips(treelist)
    if not tree.is_rooted():
        raise ValueError("ultrametric=True requires a rooted target tree.")
    if frozenset(tree.get_tip_labels()) != all_tips:
        raise ValueError("consensus tree and input trees must share the same tip set.")

    out = tree.copy()

    target_internal = {
        frozenset(node.get_leaf_names()): node for node in out[out.ntips :]
    }
    target_tips = {node.name: node for node in out[: out.ntips]}

    feat_list = list(dict.fromkeys(_normalize_features(features)))
    edge_feat_list = list(dict.fromkeys(_normalize_features(edge_features)))
    all_feats = feat_list + [i for i in edge_feat_list if i not in feat_list]

    data: dict[tuple[int, str], list[float]] = defaultdict(list)
    tip_data: dict[tuple[int, str], list[float]] = defaultdict(list)

    for tre in treelist:
        for node in tre[tre.ntips :]:
            clade = frozenset(node.get_leaf_names())
            tgt_node = target_internal.get(clade)
            if tgt_node is None:
                continue
            for feat in all_feats:
                value = _get_feature_value(node, feat)
                if value is not None:
                    data[(tgt_node.idx, feat)].append(value)

        for tip in tre[: tre.ntips]:
            if tip.name not in target_tips:
                continue
            for feat in all_feats:
                value = _get_feature_value(tip, feat)
                if value is not None:
                    tip_data[(target_tips[tip.name].idx, feat)].append(value)

    for (node_idx, feat), values in data.items():
        _set_summary_attrs(out[node_idx], feat, values)
    for (node_idx, feat), values in tip_data.items():
        _set_summary_attrs(out[node_idx], feat, values)

    for feat in edge_feat_list:
        out.edge_features.add(feat)
        for stat in ("mean", "median", "std", "min", "max", "range", "count"):
            out.edge_features.add(f"{feat}_{stat}")
    return out


def consensus_features(
    tree: ToyTree,
    trees: Iterable[ToyTree],
    features: Optional[list[str] | str] = None,
    edge_features: Optional[list[str] | str] = None,
    ultrametric: bool = False,
    conditional: bool = False,
) -> ToyTree:
    """Map consensus support and feature summaries onto a target tree.

    This function summarizes feature values across a set of source trees and
    maps the resulting statistics onto matching clades of a target tree.
    Only the features entered in ``features`` and/or ``edge_features`` are
    summarized.

    Parameters
    ----------
    tree: ToyTree
        Target tree onto which summaries are mapped. It must share the same
        tip set as the source trees.
    trees: Iterable[ToyTree]
        A list-like collection of source ``ToyTree`` objects with identical
        tip sets.
    features: list[str] | str | None
        Optional node-feature name(s) to summarize.
        Non-numeric values are ignored.
    edge_features: list[str] | str | None
        Optional edge-feature name(s) to summarize.
        Summary outputs for these are registered as edge features.
    ultrametric: bool
        If ``True``, requires rooted ultrametric source trees and includes
        height summaries (``height_*``) as node-feature outputs.
    conditional: bool
        If ``True``, uses conditional accumulation for some split-dependent
        tip distance mappings in the unrooted workflow.

    Returns
    -------
    ToyTree
        A new tree with mapped support and summary fields. For each mapped
        feature, the following fields are created:
        ``*_mean``, ``*_median``, ``*_std``, ``*_min``, ``*_max``,
        ``*_range``, and ``*_count``.

    Raises
    ------
    ValueError
        If no features are entered, if requested features are not found in
        source trees, if tip sets do not match, or when ``ultrametric=True``
        is requested with non-rooted/non-ultrametric source trees.
    TypeError
        If any item in ``trees`` is not a ``ToyTree``.

    Examples
    --------
    >>> import toytree
    >>> trees = toytree.mtree([
    ...     "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
    ...     "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
    ...     "((a:1,b:1):3,(e:2,(c:3,d:2):1):1);",
    ... ])
    >>> ctree = toytree.infer.consensus_tree(trees, min_freq=0.5)
    >>> ftree = toytree.infer.consensus_features(
    ...     ctree, trees, edge_features=["dist"], conditional=False
    ... )
    >>> ftree.get_node_data(["dist_mean", "dist_std"]).head()
    """
    feat_list = list(dict.fromkeys(_normalize_features(features)))
    edge_feat_list = list(dict.fromkeys(_normalize_features(edge_features)))

    if not (feat_list or edge_feat_list):
        raise ValueError("must enter one or more features or edge_features to map")

    if "dist" in feat_list:
        print(
            "warning: 'dist' was provided in features; treating it as edge_features.",
            file=sys.stderr,
        )
        feat_list.remove("dist")
        edge_feat_list.append("dist")
    if "support" in feat_list:
        print(
            "warning: 'support' was provided in features; treating it as edge_features.",
            file=sys.stderr,
        )
        feat_list.remove("support")
        edge_feat_list.append("support")
    if "height" in edge_feat_list:
        print(
            "warning: 'height' was provided in edge_features; treating it as features.",
            file=sys.stderr,
        )
        edge_feat_list.remove("height")
        feat_list.append("height")

    feat_list = list(dict.fromkeys(feat_list))
    edge_feat_list = list(dict.fromkeys(edge_feat_list))

    treelist = _as_treelist(trees)
    missing_features = [
        i for i in feat_list if not _feature_exists_anywhere(treelist, i)
    ]
    if missing_features:
        raise ValueError(
            f"requested feature(s) not found in input trees: {missing_features}"
        )
    missing_edge_features = [
        i for i in edge_feat_list if not _edge_feature_exists_anywhere(treelist, i)
    ]
    if missing_edge_features:
        raise ValueError(
            f"requested edge feature(s) not found in input trees: {missing_edge_features}"
        )

    if ultrametric:
        check_trees_set_for_ultrametric(treelist)
        return map_features_from_rooted_trees_to_rooted_tree(
            tree=tree,
            trees=treelist,
            features=feat_list,
            edge_features=edge_feat_list,
            conditional=conditional,
        )
    return map_features_from_unrooted_trees_to_unrooted_tree(
        tree=tree,
        trees=treelist,
        features=feat_list,
        edge_features=edge_feat_list,
        conditional=conditional,
    )


def consensus_tree(trees: Iterable[ToyTree], min_freq: float = 0.0) -> ToyTree:
    """Infer a majority-rule consensus tree from a set of input trees.

    The input trees must all contain the same set of unique tip labels.
    Splits are collected across trees, filtered to non-conflicting clades,
    and retained if their observed frequency is >= ``min_freq``.

    Parameters
    ----------
    trees: Iterable[ToyTree]
        A list-like collection of ``ToyTree`` objects with identical tip
        sets.
    min_freq: float
        Minimum clade frequency required for inclusion in the consensus.
        Must be in the closed interval [0, 1]. A value of 0.5 yields a
        standard 50% majority-rule consensus.

    Returns
    -------
    ToyTree
        An unrooted consensus tree with split support stored on internal
        nodes and distance summary features on edges, including:
        ``dist_mean``, ``dist_median``, ``dist_std``, ``dist_min``,
        ``dist_max``, ``dist_range``, and ``dist_count``.

    Raises
    ------
    ValueError
        If ``min_freq`` is outside [0, 1], if the tree set is empty, or if
        trees do not share the same tip set.
    TypeError
        If any item in ``trees`` is not a ``ToyTree``.

    See Also
    --------
    consensus_features
        Map summary statistics for selected node and edge features from a
        set of trees onto a target tree (including a consensus tree).

    Examples
    --------
    >>> import toytree
    >>> trees = toytree.mtree([
    ...     "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
    ...     "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
    ...     "((a:1,b:1):3,(e:2,(c:3,d:2):1):1);",
    ... ])
    >>> ctree = toytree.infer.consensus_tree(trees, min_freq=0.5)
    >>> ctree.get_node_data(["support", "dist_mean"]).head()
    """
    if min_freq < 0.0 or min_freq > 1.0:
        raise ValueError("min_freq must be in [0, 1].")
    clade_freqs = get_clade_frequencies(trees)
    fclade_freqs = get_consensus_clades(clade_freqs, min_freq=min_freq)
    return build_consensus_tree(fclade_freqs)
