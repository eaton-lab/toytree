#!/usr/bin/env python

"""Custom exception classes.

We catch most errors that are of the ToytreeError BaseClass and try
to handle them more nicely than other random errors. This includes
adding a logging.error message.
"""

class ToytreeError(Exception):
    """BaseClass for many custom exceptions or common user errors."""


class ToytreeRegexError(Exception):
    """Exceptions for data getting/setting on Nodes."""
    pass


class NodeDataError(Exception):
    """Exceptions for data getting/setting on Nodes."""
    pass


class ToyColorError(ToytreeError):
    """Exceptions for parsing color inputs."""
    pass


class StyleSizeMismatchError(ToytreeError):
    pass


class StyleTypeMismatchError(ToytreeError):
    pass


class StyleColorMappingTupleError(ToytreeError):
    pass


class TreeNodeError(ToytreeError):
    """Exceptions for operating on immutable attributes."""
    pass


class NewickError(ToytreeError):
    pass


class NexusError(ToytreeError):
    pass


NODE_NOT_IN_TREE_ERROR = """\
"query Node belongs to a different tree (e.g., tree1) than the one
being queried (e.g., tree2). Make sure you are selecting the correct
Node, and consider using Node .idx or .name features as queries. Beware
.idx labels often change between trees. To avoid this warning try the
following to translate a query from one tree to another:

# get Node of interest from tree1 using your query
>>> node = tree1.get_mrca_node(*query)

# represent this Node by its set of leaf names
>>> tips = node.get_leaf_names()

# run your function of interest on tree2 using leaf names as query
>>> tree2.get_nodes(*tips)
"""

NODE_INDEXING_ERROR = """\
Error indexing from ToyTree object. You likely entered an invalid
Node query. Note: Nodes can be selected by their int idx label using
indexing, slicing, or as a list:
>>> tree[3]                         # Node(idx=3)
>>> tree[3:4]                       # [Node(idx=3), Node(idx=4)]
>>> tree[[3,10,2]]                  # [Node(idx=3), Node(idx=10), Node(idx=2)]

Also, see the `.get_nodes` function for more options to query Nodes
by int idx label, str name label, Node object, or a mixture:
>>> tree.get_nodes('name3', 0)        # [Node(idx=3), Node(idx=0)]
"""

NON_MONOPHYLETIC_OUTGROUP = """\
Cannot root on non-monophyletic outgroup ({})
If you want to root on the MRCA of these nodes try:
>>> mrca = tree.get_mrca_node(*query)
>>> tree.root(mrca)
"""

if __name__ == "__main__":

    # raise ValueError("HELLO WORLD")
    # raise ToytreeError("HELLO WORLD")
    import toytree
    tree = toytree.rtree.unittree(10)
    # tree.draw(node_colors=['red', 'blue'])
    raise ToytreeError("error ")
