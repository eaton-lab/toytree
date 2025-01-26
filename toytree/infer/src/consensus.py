#!/usr/bin/env python

"""Infer a consensus tree from a set of trees.

This can be performed with a set of trees that all share the same tips.
(See supertree methods for trees with non-overlapping tip sets.)

Examples
--------
# get consensus tree with supports.
>>> trees = ...
>>> ctree = toytree.infer.get_majority_rule_consensus_tree(trees)
>>> print(ctree.get_node_data())

# get consensus tree with supports and conditional edge dist values
>>> trees = ...
>>> ctree = toytree.infer.get_majority_rule_consensus_tree(trees)
>>> cctree = toytree.infer.map_features_to_consensus_tree(ctree, trees, conditional=True)
>>> print(cctree.get_node_data())

# get consensus tree of rooted trees with support and conditional node heights
>>> trees = ...
>>> ctree = toytree.infer.get_majority_rule_consensus_tree(trees)
>>> rtree = ctree.root(trees[0].treenode.children[0].get_leaf_names())
>>> ftree = toytree.infer.map_features_to_consensus_tree(rtree, trees, rooted=True)
>>> print(ftree.get_node_data())


TODO
----
- support mapping arbitrary traits (discrete and quantitative?) from
  a set of trees onto the nodes of a consensus tree.

"""

from typing import TypeVar, Union, List, Dict
import numpy as np
from toytree.core import ToyTree, Node
from loguru import logger

MultiTree = TypeVar("MultiTree")
logger = logger.bind(name="toytree")

__all__ = [
    "get_consensus_tree",     # (trees)
    "get_consensus_features"  # (tree, trees, ...)
]


def check_trees_set_for_ultrametric(trees: List[ToyTree]) -> None:
    """Raise exception if input trees are not suitable for consensus
    tree analysis with option ultrametric=True.
    """
    for tre in trees:
        if not tre.is_rooted():
            msg = "input trees are not rooted. Cannot use option 'ultrametric=True'"
            logger.error(msg)
            raise ValueError(msg)
        if not np.allclose([i._height for i in tre[:tre.ntips]], 0.0, atol=1e-5):
            msg = "input trees are not ultrametric. Cannot use option 'ultrametric=True'"
            logger.error(msg)
            raise ValueError(msg)


def get_clade_frequencies(trees: Union[MultiTree, List[ToyTree]]) -> Dict[frozenset, float]:
    """Return a dict mapping bipartitions to their frequencies and dists.

    This performs one pass through each tree to get its bipartitions
    and records the frequency of each split and the dist of edges
    corresponding to the split. Rooted trees root node position is
    ignored.

    Parameters
    ----------
    trees: MultiTree | list[ToyTree]
        A collection of ToyTrees (list or MultiTree object) sharing the
        same tip labels.
    """
    # require all trees to share the same tips
    # ... TODO: use MultiTree... or do this outside this func.

    # dict to store clade occurrences. Set full tip set to freq=1.0.
    ntrees = len(trees)
    all_tips = frozenset(trees[0].get_tip_labels())
    clades = {all_tips: {"count": ntrees}}

    # iterate over the input tree set
    for tre in trees:

        # iterate over splits in the tree as (fset, fset)
        iter_biparts = tre.iter_bipartitions("name", True, False, type=frozenset, sort=True)
        for node, bipart in zip(tre, iter_biparts):

            # get node dist; extra if root edge and tree is rooted.
            dist = node._dist
            if not node._up.is_root():
                if tre.is_rooted():
                    dist = sum(node._dist for i in node._up.children)

            # store the partition count and dist
            part = bipart[0]
            if part not in clades:
                clades[part] = {"count": 1, "dist": [dist]}
            else:
                clades[part]["count"] += 1
                clades[part]["dist"].append(dist)

    # sort clades by occurrence
    sclades = sorted(clades, key=lambda x: clades[x]["count"], reverse=True)

    # sort and convert counts to (frequency of trees containing the split)
    clades = {i: clades[i] for i in sclades}
    for clade in clades:
        clades[clade]["freq"] = clades[clade]["count"] / ntrees
    return clades


def get_consensus_clades(clades: Dict[frozenset, float], min_freq: float) -> Dict[frozenset, float]:
    """Return dict with only non-conflicting clades above min_freq.

    This is used prior to constructing a majority-rule consensus tree,
    and min_freq sets the minimum clade frequency to keep/collapse.
    """
    keep = {}
    mark = []
    for clade, data in clades.items():
        freq = data["freq"]
        if freq < min_freq:
            continue

        # bipart conflicts with others, discard.
        conflict = False
        for c in keep:
            if conflict:
                break
            if c.isdisjoint(clade):
                continue
            if c.issubset(clade):
                continue
            if c.issuperset(clade):
                continue
            conflict = True

        # keep this bipartition
        if not conflict:
            keep[clade] = data
        # if conflicted w/ equal frequency then mark existing for removal
        elif conflict and (freq == keep[c]["freq"]):
            mark.append(c)

    # remove any clades that conflicted w/ equal frequency
    for clade in mark:
        if clade in keep:
            keep.pop(clade)
    return keep


def build_consensus_tree(clades: Dict[frozenset, float]) -> ToyTree:
    """Return a majority-rule consensus tree constructed from non-
    conflicting clades.
    """
    # sort clades by size, large to small
    sclades = sorted(clades, key=len, reverse=True)

    # dict {clade-set: Node} in order they are added. Root Node first.
    treenode = sclades.pop(0)
    sets_to_nodes = {treenode: Node()}

    # iterate over filtered clades ordered by size
    for clade in sclades:

        # create the Node
        name = str(*clade) if len(clade) == 1 else ""
        node = Node(name=name, support=clades[clade]["freq"], dist=np.mean(clades[clade]["dist"]))

        # connect node to smallest clade parent
        # TODO: probably faster not to have to sort here
        for eclade in sorted(sets_to_nodes, key=len):
            if clade.issubset(eclade):
                enode = sets_to_nodes[eclade]
                enode._add_child(node)
                break
        # store this {clade: node}
        sets_to_nodes[clade] = node

    # convert to ToyTree
    tree = ToyTree(sets_to_nodes[treenode])

    # set tip and root supports to nan
    tree[-1].support = np.nan
    for nidx in range(tree.ntips):
        tree[nidx].support = np.nan
    return tree


# def get_clade_frequencies2(trees: MultiTree, rooted: bool) -> dict[tuple, float]:
#     """Return a dict mapping bipartitions to their frequencies and dists.

#     This performs one pass through each tree to get its bipartitions
#     and records the count of each split and stores the dist or height
#     associated with the clade. If trees are rooted and ultrametric then
#     heights are stored.

#     Parameters
#     ----------
#     trees: MultiTree
#         A MultiTree containing multiple ToyTree objects.
#     rooted: bool
#         If True node heights are stored instead of dists.
#     """
#     clades = {}
#     ntrees = len(trees)

#     def feat(node: Node) -> float:
#         if rooted:
#             return getattr(node, "_height")
#         return getattr(node, "_dist")

#     # iterate over splits in input trees. If the tree is rooted then
#     # store clades of both descendants from root, not just the split.
#     for tre in trees:
#         iter_biparts = tre.iter_bipartitions("name", True, False, type=frozenset, sort=True)
#         for node, bipart in zip(tre, iter_biparts):
#             part = bipart[0]
#             if part not in clades:
#                 clades[part] = {feature: [feat(node)], "count": 1}
#             else:
#                 clades[part]["count"] += 1
#                 clades[part][feature].append(feat(node))

#             # for rooted trees store other root child
#             if rooted and node.up.is_root():
#                 node = node.get_sisters()[0]
#                 part = bipart[1]
#                 if part not in clades:
#                     clades[part] = {feature: [feat(node)], "count": 1}
#                 else:
#                     clades[part]["count"] += 1
#                     clades[part][feature].append(feat(node))

#         # add full clade
#         part = frozenset(tre.get_tip_labels())
#         if part not in clades:
#             clades[part] = {feature: [feat(tre.treenode)], "count": 1}
#         else:
#             clades[part]["count"] += 1
#             clades[part][feature].append(feat(tre.treenode))

#     # sort clades by occurrence
#     sclades = sorted(clades, key=lambda x: clades[x]["count"], reverse=True)

#     # sort and convert counts to (frequency of trees containing the split)
#     clades = {i: clades[i] for i in sclades}
#     for clade in clades:
#         clades[clade]["freq"] = clades[clade]["count"] / ntrees
#     clades[part]["freq"] = np.nan
#     return clades

# def build_consensus_tree2(clades: dict[frozenset, float], rooted: bool) -> ToyTree:
#     """Return a majority-rule consensus tree constructed from non-
#     conflicting clades.
#     """
#     # dict mapping {clade-set: Node} in order they are added.
#     sets_to_nodes = {}

#     # sort clades by size
#     sclades = sorted(clades, key=len, reverse=True)
#     for clade in sclades:
#         if clade in sets_to_nodes:
#             continue

#         # create the Node
#         name = str(*clade) if len(clade) == 1 else ""
#         node = Node(name=name, support=clades[clade]["freq"])
#         # feats[node.idxname] = clades[clade][feature]
#         node.feat = clades[clade][feature]

#         # connect nodes (visit existing smallest to largest)
#         for eclade in sorted(sets_to_nodes, key=len):
#             if clade.issubset(eclade):
#                 enode = sets_to_nodes[eclade]
#                 enode._add_child(node)
#                 break
#         # store this {clade: node}
#         sets_to_nodes[clade] = node

#     # convert to ToyTree
#     tree = ToyTree(sets_to_nodes[sclades[0]])

#     # set node dist and height attrs
#     if rooted:
#         tree.set_node_data("height", {i: np.mean(i.feat) for i in tree}, inplace=True)
#         tree.set_node_data("height_min", {i: np.min(i.feat) for i in tree}, inplace=True)
#         tree.set_node_data("height_max", {i: np.max(i.feat) for i in tree}, inplace=True)
#         tree.set_node_data("height_std", {i: np.std(i.feat) for i in tree}, inplace=True)
#     else:
#         tree.set_node_data("dist", {i: np.mean(i.feat) for i in tree}, inplace=True)
#         tree.set_node_data("dist_min", {i: np.min(i.feat) for i in tree}, inplace=True)
#         tree.set_node_data("dist_max", {i: np.max(i.feat) for i in tree}, inplace=True)
#         tree.set_node_data("dist_std", {i: np.std(i.feat) for i in tree}, inplace=True)
#     tree.remove_features(feature, inplace=True)
#     return tree


def get_consensus_features(
    tree: ToyTree,
    trees: MultiTree,
    features: List[str] = None,
    ultrametric: bool = False,
    conditional: bool = False,
) -> ToyTree:
    """Return tree with feature data mapped to each bipartition from
    a set of trees that may or may not share the same bipartitions.

    The 'support' value on the consensus tree represents the proportion
    of trees that supported the split in the consensus, and the 'dist'
    is the mean dist value of the bipartition edge in the set of trees
    that included that edge. These two features are set on MJ rule
    consensus trees by default. Other features can be optionally
    computed as well.

    Parameters
    ----------
    tree: ToyTree
        The tree can be the MJ consensus tree or a user input tree.
    trees: MultiTree | list[ToyTree]
        A list of trees from which features will be extracted. Support
        is always measured. Edge lengths are extracted as 'dists' or
        'heights' depending on the option 'rooted'.
    features: None | list[str]
        A list of feature names that exist on the input trees that you
        wish to have summarized across the nodes of the consensus tree.
        For quantitative features this will record min, max, mean, std
        conditional on the existence of the node in the tree.
    ultrametric: bool
        If trees are rooted and ultrametric then set this option to
        True to summarize stats of node heights instead of node dists.
        Note: this forces conditional=True.
    conditional: bool
        If True then dist values of tip nodes on unrooted trees are
        only calculated from the subset of trees where these tips occur
        in the same splits as in the main tree, otherwise dists are
        calculated from tip nodes across all input trees. This only
        affects tip node dists.
    """
    if ultrametric:
        # mtree.all_tree_tips_aligned()
        return map_rooted_tree_supports_and_heights_to_rooted_tree(tree, trees, features)
    return map_unrooted_tree_supports_and_dists_to_unrooted_tree(tree, trees, features, conditional)


def map_unrooted_tree_supports_and_dists_to_unrooted_tree(
    tree: ToyTree,
    trees: MultiTree,
    features: List[str] = None,
    conditional: bool = False,
) -> ToyTree:
    """
    """
    # save outgroup to re-root tree later
    outg = tree.treenode.children[1].get_leaf_names()

    # create a copy of the input tree and set support values to zero
    tree = tree.unroot().set_node_data("support", default=np.nan)

    # get the non-singleton bipartitions
    biparts = list(tree.iter_bipartitions("name", False, False, type=frozenset, sort=True))

    # iterate over all input trees
    data = {}
    tips = {}
    for tre in trees:
        
        # get this trees non-singleton biparts
        biparts2 = tre.iter_bipartitions("name", False, False, type=frozenset, sort=True)
        
        # iterate over biparts in test tree
        for node, bipart in zip(tre[tre.ntips:], biparts2):
            
            # record the bipartition counts to get supports and dist | height
            if bipart in biparts:
                if bipart not in data:
                    data[bipart] = {"count": 1, "dist": [node._dist]}
                else:
                    data[bipart]["count"] += 1
                    data[bipart]["dist"].append(node._dist)

            # if this node contains tips as children then store their
            # features as well conditional on the existence of this clade.
            if conditional:
                for child in node._children:
                    if child.is_leaf():
                        if child.name not in tips:
                            tips[child.name] = {"count": 1, "dist": [node._dist]}
                        else:
                            tips[child.name]["count"] += 1
                            tips[child.name]["dist"].append(node._dist)

                # if tree is unrooted and node parent is root then its
                # sisters can be tips, supported by this split.
                if node.up.is_root():
                    for child in node.get_sisters():
                        if child.is_leaf():
                            if child.name not in tips:
                                tips[child.name] = {"count": 1, "dist": [node._dist]}
                            else:
                                tips[child.name]["count"] += 1
                                tips[child.name]["dist"].append(node._dist)

        # if not conditional tip dists then add all children here.
        if not conditional:
            for node in tre[:tre.ntips]:
                if node.name not in tips:
                    tips[node.name] = {"dist": [node._dist]}
                else:
                    tips[node.name]["dist"].append(node._dist)

    # iterate over input tree nodes and splits
    for node, bipart in zip(tree[tree.ntips:], biparts):
        if bipart in data:
            node.support = data[bipart]["count"] / len(trees)
            setattr(node, "dist_mean", np.mean(data[bipart]["dist"]))
            setattr(node, "dist_min", np.min(data[bipart]["dist"]))
            setattr(node, "dist_max", np.max(data[bipart]["dist"]))
            setattr(node, "dist_std", np.std(data[bipart]["dist"]))
            node._dist = node.dist_mean
            # node.name = set(node.get_leaf_names())            

    for name in tips:
        node = tree.get_nodes(name)[0]
        setattr(node, "dist_mean", np.mean(tips[node.name]["dist"]))
        setattr(node, "dist_min", np.min(tips[node.name]["dist"]))
        setattr(node, "dist_max", np.max(tips[node.name]["dist"]))
        setattr(node, "dist_std", np.std(tips[node.name]["dist"]))
        node._dist = node.dist_mean

    # set as edge features in case user re-roots the tree
    tree.edge_features.add("dist_mean")
    tree.edge_features.add("dist_min")
    tree.edge_features.add("dist_max")
    tree.edge_features.add("dist_std")
    # tree = tree.mod.root_on_minimal_ancestor_deviation(*outg)
    return tree


def map_rooted_tree_supports_and_heights_to_rooted_tree(
    tree: ToyTree,
    trees: MultiTree,
    features: List[str] = None,
    conditional: bool = False,
) -> ToyTree:
    """

    """
    # check that rooted is valid
    check_trees_set_for_ultrametric(trees)

    # create a copy of the input tree and set support values to zero
    tree = tree.copy().set_node_data("support", default=np.nan)

    # store clades as {node: frozenset(leaf_names), ...} for internal nodes
    clades = [frozenset(i.get_leaf_names()) for i in tree[tree.ntips:]]

    # iterate over all input trees
    data = {}
    # tips = {}
    for tre in trees:

        # get this trees clades
        tclades = {i: frozenset(i.get_leaf_names()) for i in tre[tre.ntips:]}

        # iterate over nodes in rooted trees
        for node, clade in tclades.items():
            if clade not in data:
                data[clade] = {"count": 1, "height": [node._height]}
            else:
                data[clade]["count"] += 1
                data[clade]["height"].append(node._height)

    # iterate over input tree nodes and splits
    for node, clade in zip(tree[tree.ntips:], clades):
        if clade in data:
            node.support = data[clade]["count"] / len(trees)
            setattr(node, "height_mean", np.mean(data[clade]["height"]))
            setattr(node, "height_min", np.min(data[clade]["height"]))
            setattr(node, "height_max", np.max(data[clade]["height"]))
            setattr(node, "height_std", np.std(data[clade]["height"]))
    tree.set_node_data("height", {i: i.height_mean for i in tree[tree.ntips:]}, inplace=True)
    tree[-1].support = np.nan
    tree[-2].support = np.nan
    return tree


def get_consensus_tree(trees: Union[MultiTree, List[ToyTree]], min_freq: float=0.0) -> ToyTree:
    """Return an exteded majority-rule consensus tree from a list of trees.

    The trees must contain the same set of tips. The returned tree will
    contain the most frequently occurring non-conflicting clades in the
    input trees. If the most frequent clades conflict with equal
    frequency the node is collapsed. A minimum clade frequency can
    be set to only include clades occurring above that threshold. For
    example, min_freq=0.5 will procude a 50% majority-rule consensus
    tree. The returned tree is unrooted with edge dist values as the
    mean dist across all occurrences of that split in the set of trees.

    Parameters
    ----------
    trees: MultiTree | list[ToyTree]
        A MultiTree or list of ToyTrees sharing the same tip labels.
    min_freq: float
        A minimum frequency cutoff for a split to occur across the set
        of trees for it to be included in the consensus tree.

    See Also
    --------
    map_features_to_consensus_tree
        Map dists, heights, or other features from a set of input trees
        to nodes of a consensus tree with additional options.
    """
    # infer the majority-rule consensus unrooted tree w/ support and dist
    clade_freqs = get_clade_frequencies(trees)
    fclade_freqs = get_consensus_clades(clade_freqs, min_freq)
    ctree = build_consensus_tree(fclade_freqs)
    return ctree


if __name__ == "__main__":

    import toytree
    import numpy as np

    # multiple input rooted trees
    rtrees = toytree.mtree([
        "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
        "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
        # "((a:1,b:1):4,(e:2,(c:3,d:2):1));",
        # "((a:1,b:1):4,(d:2,(c:3,e:2):1));",
        "((a:1,b:1):3,(e:3,(c:2,d:2):1):1);",
        "((a:1,b:1):4,(d:3,(c:2,e:2):1):2);",
    ])

    # multiple input unrooted trees
    utrees = toytree.mtree([
        "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
        "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
        # "((a:1,b:1):4,(e:2,(c:3,d:2):1));",
        # "((a:1,b:1):4,(d:2,(c:3,e:2):1));",
        "((a:1,b:1):3,(e:2,(c:3,d:2):1):1);",
        # "((a:1,b:1):3,(e:2,(c:3,d:2):1):1);",        
        "((a:1,b:1):3,(d:2,(c:3,e:2):1):1);",
        # "((d:2,(c:3,e:2):1),(a:1,b:1):3):1;",
        # "((a:1,e:1):3,(d:3,(c:2,b:2):1):1);",
    ])
    utrees = [i.unroot() for i in utrees]

    utrees[0]._draw_browser(node_sizes=16, node_markers="r1.5x1", node_labels="support", tmpdir="~", scale_bar=True)
    # raise SystemExit(0)

    TREES = utrees
    ROOTED = 0

    cdict = get_clade_frequencies(TREES)
    for i in cdict:
        print(i, cdict[i])
    print("-------------")

    cdict = get_consensus_clades(cdict, 0.0)
    for i in cdict:
        print(i, cdict[i])
    print("-------------")

    tree = build_consensus_tree(cdict)
    print(tree.get_node_data())
    tree.treenode.draw_ascii()

    ctree = get_consensus_features(tree, TREES)
    print(tree.get_node_data())


    fish = toytree.mtree("https://eaton-lab.org/data/densitree.nex")
    fish = get_consensus_tree(fish)
    print(fish.get_node_data())
    raise SystemExit(0)    
    # tree = tree.root("a", "b")
    # tree = tree.mod.root_on_minimal_ancestor_deviation()
    # tree[-2].support = np.nan
    # tree._draw_browser(node_sizes=16, node_markers="r1.5x1", node_labels="support", tmpdir="~", scale_bar=True)

    # tree = map_features_to_consensus_tree(tree, trees, None, False, True)
    # print(tree.get_node_data())
    # tree._draw_browser(node_sizes=16, node_markers="r1.5x1", node_labels="support", tmpdir="~", scale_bar=True)

    # map support and dist to correct utree
    tree = map_features_to_consensus_tree(utrees[0], utrees, None, False, False)
    print(tree.get_node_data())
    tree.treenode.draw_ascii()

    # map support and dist to incorrect utree
    tree = map_features_to_consensus_tree(utrees[-1], utrees, None, False, True)
    print(tree.get_node_data())
    tree.treenode.draw_ascii()

    # map support and height to correct rtree
    # tree = map_features_to_consensus_tree(trees[0], trees, None, True, False)
    tree = map_rooted_tree_supports_and_heights_to_rooted_tree(rtrees[0], rtrees, )
    print(tree.get_node_data(["idx", "name", "support", "dist", "height", "height_mean", "height_std"]))
    tree.treenode.draw_ascii()
    # tree._draw_browser(node_sizes=16, node_markers="r1.5x1", node_labels="support", tmpdir="~", scale_bar=True, ts='b')

    # map support and height to incorrect rtree
    tree = map_rooted_tree_supports_and_heights_to_rooted_tree(rtrees[-1], rtrees, )
    print(tree.get_node_data(["idx", "name", "support", "dist", "height", "height_mean", "height_std"]))
    tree.treenode.draw_ascii()
    # tree._draw_browser(node_sizes=16, node_markers="r1.5x1", node_labels="support", tmpdir="~", scale_bar=True, ts='b')

    # map support of unrooted trees onto a rooted tree.
    # should this unroot the tree?
    # should it mess with dist values?
    tree = map_unrooted_tree_supports_and_dists_to_unrooted_tree(rtrees[0], utrees)
    print(tree.get_node_data())
    tree.treenode.draw_ascii()
    tree._draw_browser(node_sizes=16, node_markers="r1.5x1", node_labels="support", tmpdir="~", scale_bar=True, ts='b')
