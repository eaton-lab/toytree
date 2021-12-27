#!/usr/bin/env python

"""Class for rooting and unrooting of trees.

Rooting and unrooting trees turns out to be quite a bit more
complicated than you might expect. The difficult part is keeping
track of Node features that in practice are coded as attributes to
Nodes, but in reality are sometimes features of *edges*, such as
'support' or 'dist', and thus may need to be re-assigned when an
edge is created or destroyed.

"""

from typing import Optional, Sequence, TypeVar
from loguru import logger
# from toytree.core.node import Node
# from toytree.core.tree import ToyTree
# from toytree.core.node_assist import NodeAssist
from toytree.utils import ToytreeError

logger = logger.bind(name="toytree")

# type aliases
ToyTree = TypeVar("ToyTree")
Node = TypeVar("Node")
Query = TypeVar("Query", int, str, Node)


class Rooter:
    """Root a ToyTree given a monophyletic clade.

    This class is for internal use. Users should access the tree
    rooting function from either `ToyTree.root` or `toytree.mod`.

    Parameters
    ----------

    See Also
    --------
    - `ToyTree.root`

    Examples
    --------
    """
    def __init__(
        self,
        tree,
        nastuple,
        resolve_root_dist,
        edge_features,
        ):

        # store args
        self.tree = tree
        self.resolve_root_dist = resolve_root_dist
        self.edge_features = edge_features
        self.features = {"name", "dist", "support"}
        self.nas = None

        # dict for relabeling nodes {node: [parent, child, feat]}
        self.tdict = {}

        # the new node that will be inserted
        self.nnode = None

        # make a copy and ensure supports are either all int or float
        self.maxsup = max(
            [int(i.support) for i in self.tree.treenode.traverse()])
        self.maxsup = (1.0 if self.maxsup <= 1.0 else 100)
        self.get_features()

        # parse node selecting arguments (nastuple) with NodeAssist
        self.get_match(*nastuple)

        # get the mrca node (or tip node) of the monopyletic matched query.
        self.node1 = self.nas.get_mrca()

        # the node on the other side of the edge to be split.
        self.node2 = self.node1.up

        # experimental: skip hybrid nodes from networks up to next node.
        if self.node2.up and len(self.node2.children) == 1:
            self.node2 = self.node2.up
            self.node1 = self.node1.up

        # if rooting where root already exists then return current tree
        test0 = (self.node1.is_root())
        test1 = (self.node2.is_root() and self.tree.is_rooted())
        if not (test0 or test1):

            # create new root node on an existing edge to split it.
            self.insert_new_node()

            # update edge lengths given new node insertion
            self.config_root_dist()

            # redirect support values and possibly others
            self.redirect_edge_features()
            self.restructure_tree()

            # update coodrds on tree
            self.update_tree_from_tdict()
            self.update()


    def update_tree_from_tdict(self):
        """
        update tree structure and node labels
        """
        for node in self.tdict:
            node.up = self.tdict[node][0]
            node.children = self.tdict[node][1]
            for key, val in self.tdict[node][2].items():
                setattr(node, key, val)

    def update(self):
        """
        update coordinates: updates idx and adds it to any new nodes.
        """
        self.tree.treenode = self.nnode
        self.tree.treenode.ladderize()
        self.tree._coords.update()


    def redirect_edge_features(self):
        """
        Set support values to maximum for new node since the user forced
        rooting, i.e, it is not uncertain.
        """
        # mark new split with zero...
        for feature in set(self.edge_features) - set(["support", "dist"]):
            self.tdict[self.node2][2][feature] = 0.0

        # unless support value, then mark with full.
        if "support" in self.edge_features:
            self.tdict[self.node2][2]['support'] = self.maxsup
        else:
            self.tdict[self.node2][2]['support'] = self.node2.support


    def restructure_tree(self):
        """
        At this point tdict
           (node): (parent) (children), features
        {
            nnode: [None, [node1, node2], {}]
            node1: [nnode, node1.children, {'dist'}]
            node2: [nnode, node2.children, {'dist': 0.0}]
        }
        """
        # start with the node leading from new root child2 to the
        # rest of the tree structure and move up until old root.
        tnode = self.node2.up

        # label all remaining nodes by moving up from tnode to old root.
        while 1:

            # early break
            if tnode is None:
                break

            # get parent node (should be already in tdict)
            # and children to be mod'd (the ones not yet in tdict)
            parent = [i for i in tnode.children if i in self.tdict][0]
            children = [i for i in tnode.children if i not in self.tdict]

            # break occurs after tnode is root
            if tnode.is_root():

                # need a root add feature here if unrooted...
                if len(children) > 1:

                    # update dist from new parent
                    self.tdict[tnode] = [
                        parent,
                        children,
                        {"dist": parent.dist},
                    ]

                    # update edge features from new parent
                    for feature in self.edge_features:
                        self.tdict[tnode][2][feature] = getattr(parent, feature)

                    # set tnode as parent's new child
                    self.tdict[parent][1].append(tnode)

                    # set children as descendant from tnode
                    for child in children:
                        self.tdict[child] = [tnode, child.children, {}]

                # get children that are not in tdict yet
                else:
                    for child in children:

                        # record whose children they are now
                        # (node2 already did this)
                        if parent is self.node2:
                            self.tdict[self.node2][1].append(child)
                        else:
                            self.tdict[parent][1].append(child)

                        # record whose parents they have now and find distance
                        dist = {"dist": sum([i.dist for i in tnode.children])}
                        self.tdict[child] = [parent, child.children, dist]

                # finished
                break

            # update tnode.features [dist will be inherited from child]
            features = {'dist': tnode.dist, 'support': tnode.support}

            # keep connecting swap parent-child up to root
            if not tnode.up.is_root():
                children += [tnode.up]

            # pass support values down (up in new tree struct)
            child = [i for i in tnode.children if i in self.tdict][0]
            for feature in {'dist'}.union(self.edge_features):
                features[feature] = getattr(child, feature)

            # store node update vals
            self.tdict[tnode] = [parent, children, features]

            # move towards root
            tnode = tnode.up


    def config_root_dist(self):
        """
        Now that the new root node is inserted .dist features must be
        set for the two descendant nodes. Midpoint rooting is a common
        option, but users can toggle 'resolve_root_dist' to change this.
        """
        # if not already at root polytomy, then connect node2 to parent
        if self.node2.up:
            if not self.node2.up.is_root():
                self.tdict[self.node2][1] += [self.node2.up]

        # if False create zero length root node
        if self.resolve_root_dist is False:
            self.resolve_root_dist = 0.0

        # if True then use midpoint rooting
        elif self.resolve_root_dist is True:
            self.tdict[self.node1][2]["dist"] = self.node1.dist / 2.
            self.tdict[self.node2][2]["dist"] = self.node1.dist / 2.

        # split the edge on 0 or a float
        if isinstance(self.resolve_root_dist, float):
            self.tdict[self.node1][2]["dist"] = self.node1.dist - self.resolve_root_dist
            self.tdict[self.node2][2]["dist"] = self.resolve_root_dist
            if self.resolve_root_dist > self.node1.dist:
                raise ToytreeError("\n"
                "To preserve existing edge lengths the 'resolve_root_dist' arg\n"
                "must be smaller than the edge being split (it is selecting a \n"
                "a point along the edge.) The edge above node idx {} is {}."
                .format(self.node1.idx, self.node1.dist)
                )


    def insert_new_node(self):
        """
        Create and insert a new node to break an edge to create root.
        """
        # the new root node (.up=None) to be placed on the split
        self.nnode = TreeNode(name="root", support=self.maxsup)
        self.nnode.add_feature("idx", self.tree.nnodes)

        # remove node1 lineage leaving just node2 branch to be made into child
        self.node2.children.remove(self.node1)

        # new node has no parent and 1,2 as children and default features
        self.tdict[self.nnode] = [None, [self.node1, self.node2], {}]

        # node1 has new root parent, same children, and dist will be
        # configured by the config_root_dist function
        self.tdict[self.node1] = [
            self.nnode,
            self.node1.children,
            {"dist": self.node1.dist}
        ]

        # node2 has new root parent, same children (but not nnnode),
        # and dist will be configured by the config_root_dist function
        self.tdict[self.node2] = [
            self.nnode,
            self.node2.children,
            {"dist": 0.0},
        ]


    def get_features(self):
        """
        define which features to use/keep on nodes and which are
        "edge" features which must be redirected on rooting.
        """
        testnode = self.tree.treenode.get_leaves()[0]
        extrafeat = {i for i in testnode.features if i not in self.features}
        self.features.update(extrafeat)


    def get_match(self, names, wildcard, regex):
        """
        tries to get monophyletic clade from selection, then tests
        the reciprocal set, then reports error.
        """
        # find the selected node
        self.nas = NodeAssist(self.tree, names, wildcard, regex)
        self.tipnames = self.nas.get_tipnames()

        # check for reciprocal match
        set0 = (not self.nas.is_query_monophyletic())
        set1 = (self.nas.get_mrca().is_root())
        if set0 or set1:
            clade1 = self.nas.tipnames
            self.nas.match_reciprocal()

            # check reciprocal match
            if not self.nas.is_query_monophyletic():
                # clade2 = self.nas.tipnames

                # reports the smaller sized clade
                raise ToytreeError(
                    "Matched query is paraphyletic: {}".format(clade1)
                )
                # .format(sorted([clade1, clade2], key=len)[0]))


class Rooting:
    """

    Examples
    --------
    >>> tree.root("A", "B", "C")
    >>> tree.root("prz", regex=True)
    >>> tree.root(12)
    """
    def __init__(
        self,
        tree: ToyTree,
        *query: Query,
        resolve_root_dist: bool,
        edge_features: Optional[Sequence[str]],
        ):

        self.tree = tree
        self.query = query
        self.resolve_root_dist = resolve_root_dist
        self.edge_features = edge_features

    def get_edge_to_split(self):
        """Find the edge to root on based on flexible input types."""

        # get mrca of selected Nodes
        mrca = self.tree.get_mrca_node(self.query)

        # if this Node is already at the psuedo-root, then select the
        # reciprocal Node set and get its mrca.
        if mrca == self.tree.treenode:
            logger.warning("flipping rooting Node selection.")

        # get edge between this Node and its ancestor. This is where
        # the new Node will be created to split the edge.
        edge = (mrca, mrca.up)

        # experimental: skip hybrid nodes from networks up to next node.
        if self.node2.up and len(self.node2.children) == 1:
            self.node2 = self.node2.up
            self.node1 = self.node1.up


def unroot(tree: ToyTree, inplace: bool = False) -> Optional[ToyTree]:
    """Return an unrooted ToyTree by collapsing the root Node.

    This will convert a binary split into a multifurcation.
    The Node idx values can change on unrooting because the number of
    Nodes has changed.

    Note
    ----
    The unrooting process is not destructive of information, you can
    re-root a tree on the same edge position as before to recover the
    same tree.
    """
    tree = tree if inplace else tree.copy()
    root = tree.treenode

    # do nothing if the current root node is not binary
    if len(root.children) != 2:
        return None

    # find a child with children, checking first left then right.
    if not root.children[0].is_leaf():
        child = root.children[0]
        ochild = root.children[1]
    elif not root.children[1].is_leaf():
        child = root.children[1]
        ochild = root.children[0]
    else:
        raise ToytreeError("Cannot unroot a tree with only two leaves")

    # child becomes ochild's new parent
    ochild._up = child
    child._children += (ochild,)

    # other child's dist extends to include child->oldroot dist
    ochild._dist += child.dist

    # ochild->child edge inherits features from child->oldroot edge
    ochild.support = child.support

    # return new ToyTree with child as root.
    tree.treenode = child
    tree._update()
    return None if inplace else tree




if __name__ == "__main__":

    # Example test: start with a simple balanced tree.
    import toytree
    TREE = toytree.rtree.baltree(ntips=10)

    c, a, m = unroot(TREE)._draw_browser()
    # c2, a, m = unroot(TREE)._draw_browser(axes=a)
    # print(unroot(TREE))

    # unroot the tree
    # TREE = TREE.unroot()

    # root the tree a clade with the first two samples
    # TREE = TREE.root(['r1', 'r2'])

    # re-root on a different clade, for last two samples
    # TREE = TREE.root(['r9', 'r10'])

    # check that dist and support values were properly retained.
    # ...