#!/usr/bin/env python

"""
Robinson-Foulds Distance Calculations modified from ete3 TreeNode subfunction.
"""

from __future__ import print_function
from .utils import TreeError
# from .TreeParser import TreeParser


class RobinsonFoulds(object):
    """
    Simplified RF code for comparing TreeNodes.
    """
    def __init__(self, 
        t1,
        t2, 
        attr_t1="name", 
        attr_t2="name", 
        unrooted_trees=False, 
        expand_polytomies=False,
        polytomy_size_limit=5,
        skip_large_polytomies=False,
        correct_by_polytomy_size=False,
        min_support_t1=0.0,
        min_support_t2=0.0,
        ):

        # store attributes
        self.t1 = t1
        self.t2 = t2
        self.attr_t1 = attr_t1
        self.attr_t2 = attr_t2
        self.unrooted_trees = unrooted_trees
        self.expand_polytomies = expand_polytomies
        self.polytomy_size_limit = polytomy_size_limit
        self.skip_large_polytomies = skip_large_polytomies
        self.correct_by_polytomy_size = correct_by_polytomy_size
        self.min_support_t1 = min_support_t1
        self.min_support_t2 = min_support_t2

        # to be updated
        self.polytomy_correction = 0
        self.common_attrs = set()
        self.t1s = []
        self.t2s = []
        self.min_comparison = None

        # run functions
        self.check_args()
        self.check_attrs()
        self.get_trees()
        self.get_corrections()
        #self.compare_trees()


    def check_args(self):
        # check whether to bail out
        if self.unrooted_trees:
            if self.expand_polytomies:
                raise TreeError(
                    "Cannot use 'expand_polytomies' and 'unrooted_trees'")                    
        else:
            if (len(self.t1.children) > 2) or (len(self.t2.children) > 2):
                raise TreeError(
                    "Unrooted tree found! See 'unrooted_trees' flag.")

        if self.expand_polytomies and self.correct_by_polytomy_size:
            raise TreeError(
                "Cannot use expand_polytomies with correct_by_polytomy_size")


    def check_attrs(self):
        # get common attributes of the two trees, use generators
        attrs_t1 = (
            getattr(i, self.attr_t1) for i in self.t1.iter_leaves() 
            if hasattr(i, self.attr_t1)
        )
        attrs_t2 = (
            getattr(i, self.attr_t2) for i in self.t2.iter_leaves() 
            if hasattr(i, self.attr_t2)
        )
        self.common_attrs = set(attrs_t1) & set(attrs_t2)

        # Check for duplicated items (is this necessary?)
        size1 = sum((
            1 for i in self.t1.iter_leaves() if 
            getattr(i, self.attr_t1, None) in self.common_attrs
        ))
        size2 = sum((
            1 for i in self.t2.iter_leaves() if 
            getattr(i, self.attr_t2, None) in self.common_attrs
        ))
        if size1 > len(self.common_attrs):
            raise TreeError('Duplicated items found in source tree')
        if size2 > len(self.common_attrs):
            raise TreeError('Duplicated items found in reference tree')


    def get_trees(self):
        """
        TODO: rewrite this so it doesn't have to re-parse newicks.
        """
        # expand polytomies to get all resolutions possible, but fail if > max
        if self.expand_polytomies:
            raise NotImplementedError(
                "RF dist of unresolved trees not implemented currently. TODO: contact developers.")

            self.t1s = (
                TreeParser(nw).treenodes[0] for nw in
                self.t1.expand_polytomies(
                    map_attr=self.attr_t1,
                    polytomy_size_limit=self.polytomy_size_limit,
                    skip_large_polytomies=self.skip_large_polytomies
                    )
                )
            self.t2s = (
                # toytree.tree(nw).treenode for nw in                                 
                TreeParser(nw).treenodes[0] for nw in 
                self.t2.expand_polytomies(
                    map_attr=self.attr_t2,
                    polytomy_size_limit=self.polytomy_size_limit,
                    skip_large_polytomies=self.skip_large_polytomies,
                    )
                )
            # why ...?
            self.attr_t1, self.attr_t2 = "name", "name"
        else:
            self.t1s = [self.t1]
            self.t2s = [self.t2]


    def get_corrections(self):
        # correct for the N polytomies
        if self.correct_by_polytomy_size:
            corr1 = (
                len(i.children) - 2 for i in self.t1.traverse() 
                if len(i.children) > 2
            )
            corr2 = (
                len(i.children) - 2 for i in self.t2.traverse() 
                if len(i.children) > 2
            )
            if corr1 and corr2:
                raise TreeError(
                    "Both trees have polytomies! Try expand_polytomies=True")
            else:
                self.polytomy_correction = max((corr1, corr2))


    def get_edges(self, tx_content, tx_leaves, attr):

        if self.unrooted_trees:
            edges = set()
            for content in tx_content.values():  
                    
                # get name from nodes if they have a name and its in common
                names1 = tuple(sorted(
                    getattr(node, attr) for node in content if 
                    (
                        hasattr(node, attr) and \
                        (getattr(node, attr) in self.common_attrs)
                    )
                ))

                # get names of all leaves minus this node's descendants
                names2 = tuple(sorted(
                    getattr(node, attr) for node in tx_leaves - content if 
                    (
                        hasattr(node, attr) and \
                        (getattr(node, attr) in self.common_attrs)
                    )
                ))

                # add the split to the edges set
                edges.add(tuple(sorted(set([names1, names2]))))
            edges.discard(((), ()))

        # get edges of a rooted tree: just tuples of tips descended
        else:
            edges = set()
            for content in tx_content.values():
                names1 = tuple(sorted(
                    getattr(node, attr) for node in content if 
                    (
                        hasattr(node, attr) and \
                        (getattr(node, attr) in self.common_attrs)
                    )
                ))
                edges.add(tuple(sorted(set(names1))))
            edges.discard(())
        return edges


    def get_support_dict(self, tx_content, attr):
        cdict = {}
        for branch, content in tx_content.items():
            key = tuple(sorted(
                getattr(node, attr) for node in content if 
                (
                    hasattr(node, attr) and \
                    (getattr(node, attr) in self.common_attrs)
                )
            ))
            cdict[key] = branch.support
        return cdict


    def get_discards(self, t1_edges, t1_sdict, t2_edges, t2_sdict):

        # initial empty
        discard_t1, discard_t2 = set(), set()

        # get discards from t1
        if self.min_support_t1 and self.unrooted_trees:
            discard_t1 = set()
            for split in t1_edges:
                split_support = t1_sdict.get(
                    split[0], 
                    t1_sdict.get(split[1], 999999999)
                )
                if split_support < self.min_support_t1:
                    discard_t1.add(split)

        elif self.min_support_t1:
            discard_t1 = set([
                split for split in t1_edges 
                if t1_sdict[split] < self.min_support_t1
            ])

        # get discards from t2
        if self.min_support_t2 and self.unrooted_trees:
            discard_t2 = set()
            for split in t2_edges:
                split_support = t2_sdict.get(
                    split[0], 
                    t2_sdict.get(split[1], 999999999)
                )
                if split_support < self.min_support_t2:
                    discard_t2.add(split)

        elif self.min_support_t2:
            discard_t2 = set([
                split for split in t2_edges 
                if t2_sdict[split] < self.min_support_t2
            ])
        return discard_t1, discard_t2


    def compare_trees(self):
        """
        Iterate over trees in t1 and t2 to count splits present in both
        """
        for t1 in self.t1s:
            # a dictionary of {node: node.get_leaves()}
            t1_content = t1.get_cached_content()

            # a list of nodes descended from this one: [node0, node1, node2]
            t1_leaves = t1_content[t1]
            
            # get edges of the tree: set of tuples on either side of splits
            t1_edges = self.get_edges(t1_content, t1_leaves, self.attr_t1)

            # get support on tree ...
            t1_sdict = None
            if self.min_support_t1:
                t1_sdict = self.get_support_dict(t1_content, self.attr_t1)

            # iterate over target trees
            for t2 in self.t2s:
                # a dictionary of {node: node.get_leaves()}
                t2_content = t2.get_cached_content()
                
                # nodes descended from this one: [node0, node1, node2, ...]
                t2_leaves = t2_content[t2]

                # get edges of the tree: set of tuples on either side of splits
                t2_edges = self.get_edges(t2_content, t2_leaves, self.attr_t2)

                # get support dict
                t2_sdict = None
                if self.min_support_t2:
                    t2_sdict = self.get_support_dict(t2_content, self.attr_t2)

                # if support constraint, discard lowly supported splits
                discard_t1, discard_t2 = self.get_discards(
                    t1_edges, t1_sdict, t2_edges, t2_sdict)

                # the two root edges are never counted here, as they are always
                # present in both trees because of the common attr filters
                rf = len(((t1_edges ^ t2_edges) - discard_t2) - discard_t1)
                rf -= self.polytomy_correction

                # count parts
                cedges1 = t1_edges - discard_t1
                cedges2 = t2_edges - discard_t2

                if self.unrooted_trees:
                    max_parts = sum((
                        sum(1 for split in cedges1 if split[0] and split[1]),
                        sum(1 for split in cedges2 if split[0] and split[1]),
                    ))
                else:
                    # Otherwise we need to count the actual number of valid
                    # partitions in each tree -2 is to avoid counting the root
                    # partition of the two trees (only needed in rooted trees)
                    max_parts = sum((
                        sum(1 for split in cedges1 if split),
                        sum(1 for split in cedges2 if split),
                    )) - 2

                # update min_comparison if this compare was worse
                if not self.min_comparison or (self.min_comparison[0] > rf):
                    min_comparison = [
                        rf, 
                        max_parts, 
                        self.common_attrs, 
                        t1_edges, 
                        t2_edges, 
                        discard_t1, 
                        discard_t2,
                    ]

        return min_comparison