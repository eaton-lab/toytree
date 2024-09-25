#!/usr/bin/env python

"""Infer a consensus tree from a set of trees.

This can be performed with a set of trees that all share the same tips
(referred to as fixed names here) or from a set of trees that differ
in their sets of tips. The first scenario is more common, and faster,
but the second scenario is desired often enough that we implemented it
here through a separate set of functions.

Feature data: ...

Does the rooting of trees matter in methods 1 vs 2?
"""

import numpy as np
from toytree.core import ToyTree, Node
from toytree.core.multitree import MultiTree


def get_clade_frequencies_fixed_names(trees: MultiTree) -> dict[tuple, float]:
    """Return a dict mapping bipartitions to their frequencies.

    This performs one pass through each tree to get its bipartitions. Note
    that feature data (e.g., dists) are not stored here, and require another
    pass later to add to the consensus tree that can be inferred from these
    bipartition frequencies.

    Parameters
    ----------
    trees: MultiTree
        A MultiTree containing multiple ToyTree objects.
    """
    clades = {}
    ntrees = len(trees)

    # iterate over unique topologies
    for utree in trees:
        iter_biparts = utree.iter_bipartitions("name", True, False, frozenset, 0)
        for node, bipart in zip(utree, iter_biparts):
            bipart = bipart[0]
            if bipart in clades:
                clades[bipart] += 1
            else:
                clades[bipart] = 1
                
        # add full clade 
        bipart = frozenset(utree.get_tip_labels())
        if bipart in clades:
            clades[bipart] += 1
        else:
            clades[bipart] = 1
    
    # sort clades by occurrence
    sclades = sorted(clades, key=lambda x: clades[x], reverse=True)

    # sort and convert counts to freqs
    clades = {i: clades[i] for i in sclades}
    for clade in clades:
        clades[clade] = clades[clade] / ntrees
    return clades    


def get_consensus_clades_fixed_names(clades: dict[tuple, float], min_freq: float) -> dict[tuple, float]:
    """Return dict with only non-conflicting clades above min_freq.
    """
    keep = {}
    mark = []
    for clade, freq in clades.items():
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
            keep[clade] = freq
        # if conflicted w/ equal frequency then mark existing for removal
        elif conflict and (freq == keep[c]):
            mark.append(c)

    # remove any clades that conflicted w/ equal frequency
    for clade in mark:
        keep.pop(clade)
    return keep    


def build_consensus_tree_fixed_names(clades: dict[tuple, float]) -> ToyTree:
    """Return a majority-rule consensus tree constructed from non-
    conflicting clades.
    """
    # dict mapping {clade-set: Node} in order they are added.
    sets_to_nodes = {}

    # sort clades by size
    sclades = sorted(clades, key=len, reverse=True)
    for clade in sclades:
        if clade in sets_to_nodes:
            continue

        # create the Node
        name = str(*clade) if len(clade) == 1 else ""
        node = Node(name=name, support=clades[clade])

        # connect nodes (visit existing smallest to largest)
        for eclade in sorted(sets_to_nodes, key=len):
            if clade.issubset(eclade):
                enode = sets_to_nodes[eclade]
                enode._add_child(node)
                break
        # store this {clade: node}
        sets_to_nodes[clade] = node
    # return the TreeNode
    return ToyTree(sets_to_nodes[sclades[0]])


def map_features_to_tree_fixed_names(tree: ToyTree, trees: MultiTree) -> ToyTree:
    """Return consensus tree with feature data for each clade computed
    from the set of trees.

    The 'support' value on the consensus tree represents the proportion
    of trees that supported the split in the consensus, and the 'dist'
    is the mean dist value of the bipartition edge in the set of trees
    that included that edge. Other features can be optionally computed
    as well, to get mean and std, such as 'height'.
    """


def get_clade_frequencies_variable_names(trees: MultiTree) -> dict[tuple, float]:
    """Return a dict mapping bipartitions to their frequencies.

    This performs one pass through each tree to get its bipartitions. Note
    that feature data (e.g., dists) are not stored here, and require another
    pass later to add to the consensus tree that can be inferred from these
    bipartition frequencies.

    Here, frequencies could be calculated as the proportion of trees
    that contain an observed clade, or as the proportion of trees that
    contain it among the trees that include that same set of tips. In
    the latter case, a taxon that occurs in only 1 tree will always
    have 100% support, whereas in the former case it would have at
    best 1/ntrees support. The 100% case seems like the expected
    behavior to me, and so that is what we implemented here.

    Parameters
    ----------
    trees: MultiTree
        A MultiTree containing multiple ToyTree objects.
    """
    biparts = {}
    tipsets = {}

    # iterate over unique topologies
    for utree in trees:

        # store tipset count
        tipset = frozenset(utree.get_tip_labels())
        if tipset not in tipsets:
            tipsets[tipset] = 1
        else:
            tipsets[tipset] += 1

        # store bipartition counts
        iter_biparts = utree.iter_bipartitions("name", True, False, frozenset, 0)
        for node, bipart in zip(utree, iter_biparts):
            # skip singleton biparts
            if min((len(i) for i in bipart)) == 1:
                continue
            # store bipart count
            if bipart not in biparts:
                biparts[bipart] = 1
            else:
                biparts[bipart] += 1
            
    # sort and convert counts to freqs
    for bipart in biparts:
        tipset = frozenset.union(*bipart)
        biparts[bipart] = biparts[bipart] / tipsets[tipset]

    # sort clades by occurrence
    sbiparts = sorted(biparts, key=lambda x: biparts[x], reverse=True)
    biparts = {i: biparts[i] for i in sbiparts}
    return biparts


def old_get_consensus_clades_variable_names(clades: dict[tuple, float], min_freq: float) -> dict[tuple, float]:
    """Return dict with only non-conflicting clades above min_freq.
    """
    keep = {}
    mark = []
    for bipart, freq in clades.items():
        if freq < min_freq:
            continue

        # bipart conflicts with others, discard.
        conflict = False
        a1, a2 = bipart
        print(a1, a2, "***")
        for c in keep:
            b1, b2 = c
            print(b1, b2, "----")
            # compare a1 to b1
            if conflict:
                break
            if b1.isdisjoint(a1):
                continue
            if b1.issubset(a1):
                continue
            if b1.issuperset(a1):
                continue
            conflict = True

            # compare a1 to b2
            if conflict:
                break
            if b2.isdisjoint(a1):
                continue
            if b2.issubset(a1):
                continue
            if b2.issuperset(a1):
                continue
            conflict = True

            # compare a2 to b1
            if conflict:
                break
            if b1.isdisjoint(a2):
                continue
            if b1.issubset(a2):
                continue
            if b1.issuperset(a2):
                continue
            conflict = True

            # compare a2 to b2
            if conflict:
                break
            if b2.isdisjoint(a2):
                continue
            if b2.issubset(a2):
                continue
            if b2.issuperset(a2):
                continue
            conflict = True

        # keep this bipartition
        if not conflict:
            keep[bipart] = freq
        # if conflicted w/ equal frequency then mark existing for removal
        elif conflict and (freq == keep[c]):
            mark.append(c)
            # print('popped', c)

    # remove any clades that conflicted w/ equal frequency
    for clade in mark:
        keep.pop(clade)
    return keep


def get_consensus_clades_variable_names(clades: dict[tuple, float], min_freq: float) -> dict[tuple, float]:
    """Return dict with only non-conflicting clades above min_freq.
    """
    keep = {}
    mark = []
    for bipart, freq in clades.items():
        if freq < min_freq:
            continue

        # bipart conflicts with others, discard.
        conflict = False
        a1, a2 = bipart
        for kbipart in keep:
            b1, b2 = kbipart

            # exclude the smaller set if a is a double subset or superset
            # they support the same split but with different taxa sampled
            # {a,b} | {c,d}   |  bipart
            # {a,b} | {c,d,e} |  non-conflicting
            # {a,x} | {c,d,y} |  non-conflicting
            # a1.

            # check conflict: a1 x b1
            if not (a1.isdisjoint(b1) | a1.issubset(b1) | a1.issuperset(b1)):
                conflict = True
            elif not (a1.isdisjoint(b2) | a1.issubset(b2) | a1.issuperset(b2)):
                conflict = True
            elif not (a2.isdisjoint(b1) | a2.issubset(b1) | a2.issuperset(b1)):
                conflict = True
            elif not (a2.isdisjoint(b2) | a2.issubset(b2) | a2.issuperset(b2)):
                conflict = True
            if conflict:
                break

        # store this bipartition
        if not conflict:
            print('keep', bipart)
            keep[bipart] = freq
        # if conflicted w/ equal frequency then mark existing for removal
        else:
            print('conflict', bipart, kbipart)
            if conflict and (freq == keep[kbipart]):
                mark.append(kbipart)

    # remove any clades that conflicted w/ equal frequency
    for bipart in mark:
        keep.pop(bipart)
    return keep    


def create_binary_matrix(tree: ToyTree, tipnames: list[str]) -> np.ndarray:
    """
    Convert a subtree to a binary matrix representation.
    
    :param subtree: A list of lists where each inner list represents a bipartition.
    :param taxa: List of taxa names.
    :return: Binary matrix as a numpy array.
    """
    
    # iteate over unique bipartitions
    biparts = {}
    for bipartition in tree.enum.iter_bipartitions("name"):
        # e.g., ((a, b), (c,d,e))
        part1, part2 = bipartition
        for i in part1:
            for j in part1:
                matrix[tipnames.index(i), tipnames.index(j)] = 1
            for k in part2:
                matrix[tipnames.index(i), tipnames.index(k)] = 1
        for i in part2:
            for j in part2:
                matrix[tipnames.index(i), tipnames.index(j)] = 1                
            for k in part1:
                matrix[tipnames.index(i), tipnames.index(k)] = 1                

    matrix = np.zeros((len(tipnames), len(tipnames)), dtype=int)
    return matrix


def build_consensus_tree_variable_names(clades: dict[tuple, float]) -> ToyTree:
    """Return a majority-rule consensus tree constructed from non-
    conflicting clades.

    Note: sorting by size needs to be figured out here...
    """
    # dict mapping {clade-set: Node} in order they are added.
    sets_to_nodes = {}

    # sort clades by mean child size (largest first)
    sbiparts = sorted(clades, key=lambda x: np.mean([len(x[1]), len(x[0])]), reverse=True)
    for bipart in sbiparts:
        if bipart in sets_to_nodes:
            continue

        # create the Node
        name = str(*bipart[0]) if len(bipart[0]) == 1 else ""
        node1 = Node(name=name, support=clades[bipart])
        name = str(*bipart[1]) if len(bipart[1]) == 1 else ""        
        node2 = Node(name=name, support=clades[bipart])

        # connect nodes (visit existing smallest to largest)
        a1, a2 = bipart
        print("A", a1, a2)
        for ebipart in sorted(sets_to_nodes, key=lambda x: (len(x[0]), len(x[1]))):
            b1, b2 = ebipart
            print("B", b1, b2)
            # if both a1 and a2 are a subset of b1 or b2
            if (a1.issubset(b1) | a1.issubset(b2)) & (a2.issubset(b1) | a2.issubset(b2)):
                if a1.issubset(b1):
                    enode = sets_to_nodes[ebipart][0]
                    enode._add_child(node1)
                elif a1.issubset(b2):
                    enode = sets_to_nodes[ebipart][1]
                    enode._add_child(node1)
                if a2.issubset(b1):
                    enode = sets_to_nodes[ebipart][0]
                    enode._add_child(node2)
                elif a2.issubset(b2):
                    enode = sets_to_nodes[ebipart][1]
                    enode._add_child(node2)
                break
        print("\n")
        # store this {clade: node}
        sets_to_nodes[bipart] = (node1, node2)

    # create a tree
    tree = ToyTree(sets_to_nodes[sbiparts[0]][0])

    # create terminal Nodes
    for node in tree:
        print(node, node.name, )

    # return the TreeNode
    return tree



if __name__ == "__main__":

    import toytree
    import numpy as np
    # rng = np.random.default_rng()
    # trees = [toytree.rtree.unittree(6, seed=rng, random_names=0) for i in range(10)]
    # cdict = get_clade_frequencies_variable_names(trees)

    # trees = toytree.mtree([
    #     "((a,b),(c,d));",
    #     "((a,b),(c,(d,e)));",
    #     "((a,b),(e,(c,d)));",
    #     # "((a,b),((e,f),(c,d)));",
    #     "((e,f),(c,d));",
    # ])
    # cdict = get_clade_frequencies_variable_names(trees)    
    # for i in cdict:
    #     print(i, cdict[i])
    # print("-------------")

    # cdict = get_consensus_clades_variable_names(cdict, 0.0)
    # for i in cdict:
    #     print(i, cdict[i])
    # print("-------------")

    # a = create_binary_matrix(trees[0], list("abcde"))
    # b = create_binary_matrix(trees[1], list("abcde"))
    # print(a)
    # print(b)
    # print(np.sum((a - b) ** 2))

    # sbiparts = sorted(cdict, key=lambda x: (len(x[1]), len(x[0])), reverse=True)
    # for i in sbiparts:
    #     print(i)
    # tree = build_consensus_tree_variable_names(cdict)
    # print(tree.get_node_data())
    # tree.treenode.draw_ascii()

    trees = toytree.mtree([
        "((a,b),(c,(d,e)));",
        "((a,b),(c,(d,e)));",
        "((a,b),(e,(c,d)));",
    ])
    cdict = get_clade_frequencies_fixed_names(trees)    
    for i in cdict:
        print(i, cdict[i])
    print("-------------")

    cdict = get_consensus_clades_fixed_names(cdict, 0.0)
    for i in cdict:
        print(i, cdict[i])
    print("-------------")

    tree = build_consensus_tree_fixed_names(cdict)
    print(tree.get_node_data())
    tree.treenode.draw_ascii()    
