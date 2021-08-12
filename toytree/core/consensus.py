#!/usr/bin/env python

"""
Get the consensus tree from a list of trees.

TODO:
    - maybe faster using Python array.
    - calculate mean branch lengths on consensus tree.
    - calculate mean heights keeping 0 min if ultrametric.
    - unroot and then re-root at end?
"""

from typing import List
from hashlib import md5
from collections import defaultdict
import numpy as np
import toytree


class ConsensusTree:
    """
    An extended majority rule consensus function.
    Modelled on the similar function from scikit-bio tree module. If
    cutoff=0.5 then it is a normal majority rule consensus, while if
    cutoff=0.0 then subsequent non-conflicting clades are added to
    the tree.
    """
    def __init__(
        self,
        treelist: List['toytree.ToyTree'],
        best_tree: 'toytree.ToyTree'=None,
        cutoff: float=0.0,
        ):

        self.treelist = treelist
        self.best_tree = best_tree
        if self.best_tree is not None:
            self.best_tree = best_tree.copy().unroot()
            self.names = self.best_tree.get_tip_labels()
        else:
            self.names = self.treelist[0].get_tip_labels()
        self.cutoff = float(cutoff)

        # attrs to fill
        self.namedict = None
        self.treedict = {}
        self.idx_to_tree = {}
        self.idx_to_count = {}
        self.hash_to_idx = {}
        self.clade_counts = None
        self.fclade_counts = None

        # results
        self.ttree = None
        self.nodelist = None

        assert cutoff < 1, "cutoff should be a float proportion (e.g., 0.5)"


    def update(self):
        """
        ...
        """
        # hash a dict to remove duplicate trees
        self.new_hash_trees()

        # map onto best_tree of infer majrule consensus
        if self.best_tree is not None:
            self.map_onto_best_tree()

        else:
            # Find which clades occured with freq > cutoff.
            # Fills namedict, clade_counts
            self.find_clades()

            # Filter out the < cutoff clades
            # Fills fclade_counts
            self.filter_clades()

            # Build consensus tree.
            # Fills .tree
            self.build_trees()  # fclade_counts, namedict)
            ## todo. make sure no singleton nodes were left behind ...

    def new_hash_trees(self):
        """
        Get the counts of all unique unrooted trees.
        """
        for idx, tree in enumerate(self.treelist):
            utree = tree.unroot()
            hashed = utree.treenode.get_topology_id()
            if hashed not in self.hash_to_idx:
                self.hash_to_idx[hashed] = idx
                self.idx_to_tree[idx] = utree
                self.idx_to_count[idx] = 1
            else:
                odx = self.hash_to_idx[hashed]
                self.idx_to_count[odx] += 1

    def hash_trees(self):
        """
        hash ladderized tree topologies
        """
        observed = {}
        for idx, tree in enumerate(self.treelist):
            nwk = tree.write(tree_format=9)
            hashed = md5(nwk.encode("utf-8")).hexdigest()
            if hashed not in observed:
                observed[hashed] = idx
                self.treedict[idx] = 1
            else:
                idx = observed[hashed]
                self.treedict[idx] += 1


    def map_onto_best_tree(self):
        """
        Map clades from tree onto best_tree
        """
        # index names from the first tree
        ndict = {j: i for i, j in enumerate(self.names)}

        # dictionary of bits describing all clades in the best tree
        idict = {}
        bitdict = {}
        for node in self.best_tree.treenode.traverse("preorder"):

            # get byte string representing split
            bits = np.zeros(self.best_tree.ntips, dtype=np.bool_)
            for child in node.iter_leaf_names():
                bits[ndict[child]] = True
            bitstring = bits.tobytes()

            # record split (mirror image not relevant)
            bitdict[bitstring] = 0
            idict[bitstring] = node
        # print(bitdict)

        # count occurrence of clades in best_tree among other trees
        for tidx, ncopies in self.treedict.items():
            tre = self.treelist[tidx].unroot()
            # print(tidx)
            for node in tre.treenode.traverse("preorder"):
                bits = np.zeros(tre.ntips, dtype=np.bool_)
                for child in node.iter_leaf_names():
                    bits[ndict[child]] = True
                bitstring = bits.tobytes()
                # print(bits.astype(int))
                if bitstring in bitdict:
                    bitdict[bitstring] += ncopies
                else:
                    revstring = np.invert(bits).tobytes()
                    if revstring in bitdict:
                        bitdict[revstring] += ncopies
            # print("")

        # convert to frequencies
        for key, val in bitdict.items():
            # print(key, val, idict[key].name)
            idict[key].support = int(100 * val / float(len(self.treelist)))
        self.ttree = self.best_tree
        self.ttree._coords.update()


    def find_clades(self):
        """
        Count clade occurrences.
        """
        # index names from the first tree
        ndict = {j: i for i, j in enumerate(self.names)}
        namedict = dict(enumerate(self.names))

        # store counts
        clade_counts = {}
        for tidx, ncopies in self.idx_to_count.items():  #treedict.items():

            # testing on unrooted trees is easiest but for some reason slow
            ttree = self.idx_to_tree[tidx]

            # traverse over tree
            for node in ttree.treenode.traverse('preorder'):
                bits = np.zeros(len(ttree), dtype=bool)
                for child in node.iter_leaf_names():
                    bits[ndict[child]] = True

                # get bit string and its reverse
                bitstring = bits.tobytes()
                revstring = np.invert(bits).tobytes()

                # add to clades first time, then check for inverse next hits
                if bitstring in clade_counts:
                    clade_counts[bitstring] += ncopies
                else:
                    if revstring not in clade_counts:
                        clade_counts[bitstring] = ncopies
                    else:
                        clade_counts[revstring] += ncopies

        # convert to freq
        for key, val in clade_counts.items():
            clade_counts[key] = val / float(len(self.treelist))

        ## return in sorted order
        self.namedict = namedict
        self.clade_counts = sorted(
            clade_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )


    def filter_clades(self):
        """
        Remove conflicting clades and those < cutoff to get
        majority rule.
        """
        passed = []
        carrs = np.array([list(i[0]) for i in self.clade_counts], dtype=int)
        freqs = np.array([i[1] for i in self.clade_counts])

        for idx in range(carrs.shape[0]):
            conflict = False
            if freqs[idx] < self.cutoff:
                continue

            for pidx in passed:
                intersect = np.max(carrs[idx] + carrs[pidx]) > 1

                # is either one a subset of the other?
                subset_test0 = np.all(carrs[idx] - carrs[pidx] >= 0)
                subset_test1 = np.all(carrs[pidx] - carrs[idx] >= 0)
                if intersect:
                    if (not subset_test0) and (not subset_test1):
                        conflict = True

            if not conflict:
                passed.append(idx)

        rclades = []
        for idx in passed:
            rclades.append((carrs[idx], freqs[idx]))
        self.fclade_counts = rclades


    def build_trees(self):
        """
        Build an unrooted consensus tree from filtered clade counts.
        """
        # storage
        nodes = {}
        idxarr = np.arange(len(self.fclade_counts[0][0]))
        queue = []

        # create dict of clade counts and set keys
        countdict = defaultdict(int)
        for clade, count in self.fclade_counts:
            mask = np.int_(list(clade)).astype(np.bool)
            ccx = idxarr[mask]
            queue.append((len(ccx), frozenset(ccx)))
            countdict[frozenset(ccx)] = count

        while queue:
            queue.sort()
            (clade_size, clade) = queue.pop(0)
            new_queue = []

            # search for ancestors of clade
            for (_, ancestor) in queue:
                if clade.issubset(ancestor):
                    # update ancestor such that, in the following example:
                    # ancestor == {1, 2, 3, 4}
                    # clade == {2, 3}
                    # new_ancestor == {1, {2, 3}, 4}
                    new_ancestor = (ancestor - clade) | frozenset([clade])
                    countdict[new_ancestor] = countdict.pop(ancestor)
                    ancestor = new_ancestor

                new_queue.append((len(ancestor), ancestor))

            # if the clade is a tip, then we have a name
            if clade_size == 1:
                name = list(clade)[0]
                name = self.namedict[name]
            else:
                name = None

            # the clade will not be in nodes if it is a tip
            children = [nodes.pop(c) for c in clade if c in nodes]
            node = toytree.TreeNode(name=name)
            for child in children:
                node.add_child(child)
            if not node.is_leaf():
                node.dist = int(round(100 * countdict[clade]))
                node.support = int(round(100 * countdict[clade]))
            else:
                node.dist = int(100)
                node.support = int(100)

            nodes[clade] = node
            queue = new_queue
        nodelist = list(nodes.values())
        tre = nodelist[0]

        ## return the tree and other trees if present
        self.ttree = toytree.tree(tre.write(format=0))
        self.ttree._coords.update()
        self.nodelist = nodelist


if __name__ == "__main__":

    import toytree

    tre1 = toytree.rtree.unittree(10, seed=123)
    tre2 = toytree.rtree.unittree(10, seed=321)

    mtre = toytree.mtree(([tre1] * 5) + ([tre2] * 5))
    ctre = mtre.get_consensus_tree()
    print(ctre.get_node_data())
