#!/usr/bin/env python

"""Matrix representation parsimony (MRP).

MRP is a supertree approach that encodes the splits observed in a set
of trees as binary characters in order to encode a character matrix
that can be used for parsimony phylogenetic inference.
"""


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



# NOTE: not implemented in current release.
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



# NOTE: not implemented in current release.
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

# NOTE: this was moved here but may or may not be useful for MRP.
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



# NOTE: this was moved here but may or may not be useful for MRP.
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
