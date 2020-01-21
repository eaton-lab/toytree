#!/usr/bin/env python


import re
from .utils import ToytreeError



class NodeAssist:
    """
    Given a search query (list of names, wildcard or regex) a node or list of 
    names can be retrieved under a set of pre-built functions.
    """
    def __init__(self, ttree, names, wildcard, regex):

        # attributes
        self.ttree = ttree
        self.names = names
        self.wildcard = wildcard
        self.regex = regex

        # require arguments
        if not any([names, wildcard, regex]):
            raise ToytreeError(
                "Must enter a name list, wildcard selector, or regex pattern")

        if len([i for i in [names, wildcard, regex] if i]) != 1:
            raise ToytreeError(
                "Only one method allowed at a time for: name list, "
                "wildcard selector, or regex pattern")

        # matched values
        self.nodes = []
        self.tipnames = []
        self.match_query()

        # default options to be updated in function calls
        self.mrca = True
        self.monophyletic = True


    def match_query(self):
        """
        Get list of **nodes** from {list, wildcard, or regex}
        """
        tips = []
        if self.names:

            # allow tips to be entered instead of a list
            if isinstance(self.names, (str, int)):
                self.names = [self.names]

            # report any names entered that seem like typos
            bad = [i for i in self.names if i not in self.ttree.get_tip_labels()]
            if any(bad):
                raise ToytreeError(
                    "Sample {} is not in the tree".format(bad))

            # select *nodes* that match these names
            tips = [
                i for i in self.ttree.treenode.get_leaves() 
                if i.name in self.names
            ]

        # use regex to match tipnames
        elif self.regex:

            # select *nodes* that regex match. Raise error if None.
            tips = [
                i for i in self.ttree.treenode.get_leaves() 
                if re.match(self.regex, i.name)
            ]               
            if not any(tips):
                raise ToytreeError("No Samples matched the regular expression")

        # use wildcard substring matching
        elif self.wildcard:

            # select *nodes* that match the wildcard search
            tips = [
                i for i in self.ttree.treenode.get_leaves()
                if self.wildcard in i.name
            ]
            if not any(tips):
                raise ToytreeError("No Samples matched the wildcard")

        # build list of **tipnames** from matched nodes
        if not tips:
            raise ToytreeError("no matching tipnames")

        # store results
        self.nodes = tips
        self.tipnames = [i.name for i in tips]


    def match_reciprocal(self):
        # get new query names list
        alltips = set(self.ttree.get_tip_labels())
        query_tips = set(self.tipnames)
        other_tips = list(alltips - query_tips)

        # rerun query matching
        self.names = other_tips
        self.wildcard = None
        self.regex = None
        self.match_query()


    def get_nodes(self):
        return self.nodes

    def get_tipnames(self):
        return self.tipnames

    def get_mrca(self):
        if len(self.nodes) > 1:
            return self.ttree.treenode.get_common_ancestor(self.nodes)
        return self.nodes[0]

    def get_mrca_leaves(self):
        return self.get_mrca().get_leaves()

    def get_mrca_descendants(self):
        return [i for i in self.get_mrca().traverse()]

    def is_query_monophyletic(self):
        # if multiple tips descendant from check if they're monophyletic
        if len(self.tipnames) < 2:
            return True

        mbool, mtype, mnames = (
            self.ttree.treenode.check_monophyly(
                self.tipnames, "name", ignore_missing=True)
        )
        return mbool
