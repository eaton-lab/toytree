#!/usr/bin/env python

"""
Write Toytree or TreeNode to newick string
"""

import re
from .utils import NW_FORMAT

# globals
ILLEGAL_NEWICK_CHARS = r":;(),\[\]\t\n\r="
ITERABLE_TYPES = set([list, set, tuple, frozenset])

# formatters
FF = "%0.6g"
NF = "%s"
DF = FF  # ":" + FF


class NewickWriter(object):
    """
    Write TreeNode to a newick string.

    Parameters
    ----------
    tree: TreeNode
        Input TreeNode
    tree_format: (int)
        Format of newick string, see ete formats 0-10.
    format_root_node: (bool)
        Write node info (e.g., support, dist) for root node.   
    features: (None or list,set,tuple)
        Features to be written in NHX format in newick string.
    """
    def __init__(
        self, 
        treenode,
        tree_format=0, 
        format_root_node=False, 
        features=None,
        is_leaf_fn=None,
        dist_formatter=None,
        name_formatter=None,
        support_formatter=None,
        ):

        # store attrs
        self.treenode = treenode
        self.tf = tree_format
        self.format_root_node = format_root_node
        self.features = features
        self.fn = (is_leaf_fn if is_leaf_fn else is_leaf)
        self.newick = []

        # formatters
        self.dist_formatter = dist_formatter
        self.support_formatter = support_formatter
        self.name_formatter = name_formatter


    def write_newick(self):

        # returns (1, tipnode) or (0, tipnode); 1 means visited in postorder
        for post, node in self.treenode.iter_prepostorder(is_leaf_fn=self.fn):

            # if node visited in postorder then it has already been formatted
            if post:

                # close the node
                self.newick.append(")")

                # add node info and features
                if node.up or self.format_root_node:
                    self.newick.append(
                        format_node(
                            node, 
                            "internal", 
                            self.tf, 
                            self.dist_formatter,
                            self.support_formatter,
                            self.name_formatter,                            
                        )
                    )
                    self.newick.append(get_features(node, self.features))

            # first pass, node needs to be formatted...
            else:

                # if not root and not child0, put comma and wait for sister
                if (node != self.treenode) and (node != node.up.children[0]):
                    self.newick.append(",")

                # if leaf then write node name
                if node.is_leaf():

                    # sub out bad characters
                    node.name = re.sub(
                        "[" + ILLEGAL_NEWICK_CHARS + "]", 
                        "_", 
                        str(getattr(node, "name")),
                    )

                    # store formatted node
                    self.newick.append(
                        format_node(node, "leaf", self.tf, DF, DF, NF)
                    )
                    self.newick.append(get_features(node, self.features))

                # start new internal node
                else:
                    self.newick.append("(")

        self.newick.append(";")
        return ''.join(self.newick)



def format_node(
    node, 
    node_type, 
    format,
    dist_formatter=None,
    support_formatter=None,
    name_formatter=None):
    """
    Used when writing newick...
    """

    # use default formatters unless specified
    if dist_formatter is None: 
        dist_formatter = FF
    if support_formatter is None: 
        support_formatter = FF
    if name_formatter is None: 
        name_formatter = NF

    # apply formatting to leaves or nodes
    if node_type == "leaf":
        container1 = NW_FORMAT[format][0][0]  # name
        container2 = NW_FORMAT[format][1][0]  # dists
        converterFn1 = NW_FORMAT[format][0][1]
        converterFn2 = NW_FORMAT[format][1][1]
        flexible1 = NW_FORMAT[format][0][2]
    else:
        container1 = NW_FORMAT[format][2][0]  # support/name
        container2 = NW_FORMAT[format][3][0]  # dist
        converterFn1 = NW_FORMAT[format][2][1]
        converterFn2 = NW_FORMAT[format][3][1]
        flexible1 = NW_FORMAT[format][2][2]

    # Format node names
    FIRST_PART = ""
    if converterFn1 is not None:

        # convert node attribute to a string
        if converterFn1 == str:
            try:
                FIRST_PART = re.sub(
                    "[" + ILLEGAL_NEWICK_CHARS + "]",
                    "_", 
                    str(getattr(node, container1))
                )
                if not FIRST_PART and container1 == 'name' and not flexible1:
                    FIRST_PART = "NoName"
            except (AttributeError, TypeError):
                FIRST_PART = "?"

            # format as ...
            FIRST_PART = name_formatter % FIRST_PART

        # apply converter function to node attribute
        else:
            try:
                #FIRST_PART =  "%0.6f" %(converterFn2(getattr(node, container1)))
                FIRST_PART = support_formatter % (
                    converterFn2(getattr(node, container1))
                    )
            except (ValueError, TypeError):
                FIRST_PART = "?"

    # Format node info
    SECOND_PART = ""
    if converterFn2 is not None:

        # convert to string
        if converterFn2 == str:
            try:
                SECOND_PART = ":" + re.sub(
                    "[" + ILLEGAL_NEWICK_CHARS + "]",
                    "_",
                    str(getattr(node, container2))
                )
            except (ValueError, TypeError):
                SECOND_PART = ":?"
        else:
            try:
                SECOND_PART = ":%s" % (
                    dist_formatter % (converterFn2(getattr(node, container2))))
            except (ValueError, TypeError):
                SECOND_PART = ":?"

    return "%s%s" % (FIRST_PART, SECOND_PART)


def get_features(self, features=None):
    """ 
    Generates the extended newick string NHX with extra data about a node.
    """
    string = ""
    if features is None:
        features = []
    elif (features == []) or (features is True):
        features = self.features

    for pr in features:
        if hasattr(self, pr):
            raw = getattr(self, pr)
            
            # convert to a string
            if type(raw) in ITERABLE_TYPES:
                raw = '|'.join([str(i) for i in raw])
            elif type(raw) == dict:
                raw = '|'.join(
                    ["{}-{}".format(i, j) for (i, j) in raw.items()]
                )
                # map(lambda x,y: "%s-%s" %(x, y), six.iteritems(raw)))
            elif type(raw) == str:
                pass
            else:
                raw = str(raw)

            value = re.sub("[" + ILLEGAL_NEWICK_CHARS + "]", "_", raw)
            if string != "":
                string += ":"
            string += r"%s=%s" % (pr, str(value))
    if string != "":
        string = "[&&NHX:" + string + "]"

    return string




def is_leaf(node):
    return not bool(node.children)
