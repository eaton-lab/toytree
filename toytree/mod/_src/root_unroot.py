#!/usr/bin/env python

r"""Class for rooting and unrooting of trees.

Rooting and unrooting trees turns out to be quite a bit more
complicated than you might expect. The difficult part is keeping
track of Node features that in practice are coded as attributes to
Nodes, but in reality are sometimes features of *edges*, such as
'support' or 'dist', and thus need to be re-assigned when an parent
child relationships change.

Re-rooting a rooted tree:
               o                            x
              / \                          / \
             1   2         root('n')      n   u
                / \          -->             / \
               .   u                        2   .
                  / \                      / \
                 .   n                    1   .

Rooting an unrooted tree:
                                            x
                                           / \
              _ 2 _        root('n')      n   u
             |  |  |         -->             / \
             1  .  u                        2   .
                  / \                      / \
                 .   n                    1   .

References
----------
- Czech, L., Huerta-Cepas, J. and Stamatakis, A. (2017) A critical
  review on the use of support values in tree viewers and
  bioinformatics toolkits. Molecular Biology and Evolution, 34,
  1535–1542. doi: 10.1093/molbev/msx055

Examples
--------
>>> # Test Case from Czech et al. 2017 (edge features)
>>> NEWICK = "((C,D)1,(A,(B,X)3)2,E)R;"
>>> tree = toytree.tree(NEWICK)
>>>
>>> # set a color feature to Nodes and 'ecolor' and 'ncolor'
>>> colors = {'1': 'red', '2': 'green', '3': 'orange'}
>>> tree.set_node_data("ecolor", colors, inplace=True)
>>> tree.set_node_data("ncolor", colors, inplace=True)
>>>
>>> # draw the trees
>>> kwargs = {
>>>     'layout': 'd',
>>>     'use_edge_lengths': False,
>>>     'node_sizes': 10,
>>>     'node_labels': 'name',
>>>     'node_labels_style': {
>>>         'font-size': 20,
>>>         'baseline-shift': 10,
>>>         '-toyplot-anchor-shift': 10,
>>>     }}
>>> tree.draw(
>>>     node_colors=tree.get_node_data('ncolor', missing='black'),
>>>     edge_colors=tree.get_node_data('ecolor', missing='black'),
>>>     **kwargs,
>>> )
>>>
>>> # re-root, treating 'ecolor' but not 'ncolor' as edge feat.
>>> rtree = tree.root("X", edge_features=["ecolor"])
>>> rtree.draw(
>>>     node_colors=rtree.get_node_data('ncolor', missing='black'),
>>>     edge_colors=rtree.get_node_data('ecolor', missing='black'),
>>>     **kwargs,
>>> );
"""
from typing import Optional, Sequence, TypeVar, Set, Union
from loguru import logger
import numpy as np
from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.core.apis import (
    TreeModAPI, add_subpackage_method, add_toytree_method
)
from toytree.utils import ToytreeError, NON_MONOPHYLETIC_OUTGROUP

logger = logger.bind(name="toytree")
Query = TypeVar("Query", int, str, Node)

__all__ = ["root", "unroot"]


class Rooter:
    """Root ToyTree on Node query selection.

    See `toytree.mod.root` docstring for details. This class is for
    internal use, not user-facing.
    """
    def __init__(
        self,
        tree: ToyTree,
        *query: Query,
        root_dist: Optional[float] = None,
        edge_features: Optional[Sequence[str]] = None,
        inplace: bool = False,
    ):
        self.tree = tree
        self.query = query
        self.root_dist = root_dist
        self.inplace = inplace
        self.node: Node = self._get_edge_to_split()
        """: The Node below the edge that will be split. Found from query."""
        self.edge_features: Set[str] = self._get_edge_features(edge_features)
        """: Features that should be re-polarized on rooting (e.g., support)"""

    def _get_edge_features(self, edge_features: Optional[Union[str, Sequence[str]]]) -> Set[str]:
        """Return the features associated with edges instead of nodes.

        This requires dist and support to be edge features. It also adds
        any features in self.tree.edge_features, and also adds any that
        were entered as args to the Rooter class.
        """
        default = {"_dist", "support"}
        disallowed = {"dist", "idx", "up", "children"}

        # start with tree's designated edge features
        efeatures = self.tree.edge_features
        # add user entered single feature
        if isinstance(edge_features, str):
            efeatures = self.tree.edge_features | {edge_features}
        # add user entered sequence of features
        elif isinstance(edge_features, (tuple, list, set)):
            efeatures = efeatures | set(edge_features)
        # add default features
        efeatures = efeatures | default
        # remove unallowed features
        efeatures = efeatures - disallowed
        logger.debug(f"edge_features: {efeatures}")
        return efeatures
        # return (default | set(edge_features)) - disallowed

    def _get_edge_to_split(self) -> Node:
        """Return the Node below new root edge from input query.

        Get MRCA Node of the input selection. If it is the root, then
        get the MRCA of the inverse selection. If that group is not
        monophyletic then raise exception for bad selection.
        """
        # get the query as Set[Node]; remove root if present; return if None
        nodes = set(self.tree.get_nodes(*self.query))
        nodes -= {self.tree.treenode}
        if not nodes:
            return self.tree.treenode

        # get only tips and get their mrca
        tips = set.union(*(set(i.get_leaves()) for i in nodes))
        mrca = self.tree.get_mrca_node(*nodes)

        # check monophyly of user query; try reciprocal tip set; then raise
        try:
            # the mrca clade may be non-monophyletic
            if not mrca.is_root():
                if any(node not in tips for node in mrca.iter_leaves()):
                    tips = str(sorted(i.name for i in tips))
                    raise ToytreeError(NON_MONOPHYLETIC_OUTGROUP.format(tips))

            # root mrca. Reciprocal tip set may be monophyletic, all tips, or non-monophyletic
            else:
                all_tips = set(self.tree[:self.tree.ntips])
                tips = all_tips - tips
                if not tips:
                    tips = all_tips
                mrca = self.tree.get_mrca_node(*tips)
                if any(node not in tips for node in mrca.iter_leaves()):
                    tips = str(sorted(i.name for i in tips))
                    raise ToytreeError(NON_MONOPHYLETIC_OUTGROUP.format(tips))
        except ToytreeError as exc:
            logger.error(exc)
            raise exc
        return mrca

    def run(self):
        """Return ToyTree rooted on the input selection."""
        # get tree and node copies
        if not self.inplace:
            self.tree = self.tree.copy()
            self.node = self.tree[self.node.idx]

        # tree is currently rooted, return it or unroot it.
        if self.tree.is_rooted():
            # return same if rooting on current rooting.
            if self.tree.treenode in [self.node, self.node.up]:
                logger.debug("tree is already rooted this way.")
                return self.tree
            self.tree.unroot(inplace=True)

        # tree is currently unrooted, raise exception if no outgroup.
        else:
            if self.node.is_root():
                msg = (
                    "Cannot root unrooted tree on the pseudo-root, it has no "
                    "edge. Select a valid outgroup")
                logger.error(msg)
                raise ToytreeError(msg)

        self._insert_root_node()
        self.tree._update()
        return self.tree

    def _insert_root_node(self):
        r"""Insert a new node to break an edge to create root.

        When inserting a new Node it is given nan support value.

        Important Nodes are:
            - oldroot: o
            - oldroot.children: 1,2
            - node: n
            - node.up: u
            - newroot: x

                   o                         x         polar = [u, 2]
                  / \                       / \        flip = [1]
                 1   2       root('n')     n   u
                    / \         -->           / \
                   .   u                     2   .
                      / x                   / \
                     .   n                 1   .

        oldroot is removed, newroot is created. All Nodes that are
        ancestors of u on the original tree are re-polarized.
        """
        # store references to Nodes before their relationships change.
        # support = self._infer_max_support()
        # self.node.support = np.nan
        newroot = Node(name="root", support=np.nan, dist=0)
        edge = (self.node, self.node.up)
        odist = float(edge[0]._dist)
        # odist = sum([i._dist for i in self.node.up.children if i != self.node])
        # sumdist = sum([ndist, odist])
        # logger.warning(f"edge={edge}, ndist={ndist} odist={odist}")

        # nodes on path from node to the original root.
        path = (self.node,) + self.node.get_ancestors()  # [n, u, 2, o]

        # store edge features for re-polarizing edges in path.
        feats = {
            n: {i: getattr(n, i, None) for i in self.edge_features}
            for n in path
        }

        # polarize each node on path
        for idx in range(1, len(path)):           # [u, 2, o]    [3, 2, R]
            # connect this node to its new parent (previously child)
            node = path[idx]                      # u            R
            child = path[idx - 1]                 # n            2
            node._up = child                      # u -> n       R -> 2
            node._remove_child(child)             # n -x u       2 -x R

            # connect this node to its new child (previously parent)
            # if this node is not the former root node.
            if node != path[-1]:
                node._add_child(path[idx + 1])

            # transfer non-root edge features
            for feature in self.edge_features:
                value = feats[child][feature]
                if value is not None:
                    setattr(node, feature, value)
                else:
                    if hasattr(node, feature):
                        delattr(node, feature)

        # set support of mirror root child to nan
        # self.node.support = np.nan

        # set node and its parent as sisters, and children of newroot.
        newroot._children = edge             # n -> x, u -> x
        edge[0]._up = newroot
        edge[1]._up = newroot

        # position of newroot on edge, None=midpoint, ...
        if self.root_dist is None:
            edge[0]._dist = odist / 2.
            edge[1]._dist = odist / 2.
            # edge[0]._dist /= 2.
            # edge[1]._dist /= 2.
        else:
            logger.debug(f"sumdist={odist}, root_dist={self.root_dist}")
            if self.root_dist > odist:
                raise ValueError(
                    "`root_dist` arg (placement of root node on existing edge) "
                    f"cannot be greater than length of the edge: {odist}.")
            edge[0]._dist = self.root_dist
            edge[1]._dist = odist - self.root_dist
            # logger.warning(f"sumdist={sumdist}, root_dist={self.root_dist}")
            # logger.warning(f"0={edge[0]._dist}, 1={edge[1]._dist}")

        # update as ToyTree
        self.tree.treenode = newroot
        self.tree._update()
        return self.tree


@add_toytree_method(ToyTree)
@add_subpackage_method(TreeModAPI)
def root(
    tree: ToyTree,
    *query: Query,
    root_dist: Optional[float] = None,
    edge_features: Optional[Sequence[str]] = None,
    inplace: bool = False,
) -> ToyTree:
    r"""Return a ToyTree rooted on the edge above selected Node query.

    Manually root a tree on an outgrup by splitting an edge to insert
    a new root Node. The root Node is named "root" and has a np.nan
    support value and dist=0 unless otherwise set.

    Example of rooting an unrooted tree:
                                                x
                                               / \
                  _ 2 _        root('n')      n   u
                 |  |  |         -->             / \
                 1  .  u                        2   .
                      / \                      / \
                     .   n                    1   .

    Example of re-rooting a rooted tree:
                   x                            x
                  / \                          / \
                 1   2         root('n')      n   u
                    / \          -->             / \
                   .   u                        2   .
                      / \                      / \
                     .   n                    1   .

    Parameters
    ----------
    tree: ToyTree
        A rooted or unrooted ToyTree to (re-)root.
    *query: str, int, or Node
        One or more Node selectors, which can be Node objects, names,
        or int idx labels. If multiple are entered the MRCA node will
        be used as the base of the edge to split.
    root_dist: None or float
        The length (dist) along the root edge above the Node query
        where the new root edge should be placed. Default is None
        which will place root at the midpoint of the edge. A float
        can be entered, but will raise ToyTreeError if > len of edge.
    edge_features: Sequence[str]
        One or more Node features that should be treated as a feature
        of its edge, not the Node itself. On rooting, edge features
        are re-polarized, to apply to the correct Node. The 'dist'
        and 'support' features are always treated as edge features.
        Add additional edge features here. See docs for example.
    inplace: bool
        If True the original tree is modified and returned, otherwise
        a modified copy is returned.

    See Also
    --------
    - toytree.mod.root_on_midpoint
    - toytree.mod.root_on_minimal_ancestor_deviation

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=10, seed=123)
    >>> t1 = tree.root("r8", "r9")
    >>> t2 = tree.root("r8", "r9", root_dist=0.3)
    >>> toytree.mtree([t1, t2]).draw();
    """
    kwargs = dict(inplace=inplace, root_dist=root_dist, edge_features=edge_features)
    return Rooter(tree, *query, **kwargs).run()


@add_toytree_method(ToyTree)
@add_subpackage_method(TreeModAPI)
def unroot(tree: ToyTree, inplace: bool = False) -> ToyTree:
    """Return an unrooted tree by collapsing the root split.

    This will convert a binary split into a multifurcation with three
    or more children. This decreases the number of Nodes by one.

    Note
    ----
    The unrooting process is not destructive of information, you can
    re-root a tree on the same edge position as before to recover the
    same tree, and all edge lengths (dist values) are retained. Only
    the position of the root Node along the rooted edge is lost, which
    can be re-set when rooting using the root_dist argument.

    Parameters
    ----------
    inplace: bool
        If True modify and return original tree, else return a copy.
    """
    # fast: return current tree if already unrooted
    if not tree.is_rooted():
        return tree

    # get tree or copy to return
    tree = tree if inplace else tree.copy()
    rootnode = tree.treenode

    # just return current tree if the rootnode node is not binary
    if len(rootnode.children) != 2:
        return tree

    # find a child with children, checking first left then right.
    if not rootnode.children[0].is_leaf():
        newroot = rootnode.children[0]
        ochild = rootnode.children[1]
    elif not rootnode.children[1].is_leaf():
        newroot = rootnode.children[1]
        ochild = rootnode.children[0]
    else:
        raise ToytreeError("Cannot unroot a tree with only two leaves")

    # child becomes ochild's new parent
    ochild._up = newroot
    newroot._children += (ochild,)

    # other child's dist extends to include child->oldrootnode dist
    ochild._dist += newroot.dist
    newroot._dist = 0.

    # ochild->child edge inherits features from child->oldrootnode edge
    ochild.support = newroot.support
    newroot.support = np.nan

    # make child the new rootnode and remove old rootnode
    newroot._up = None

    tree.treenode = newroot
    del rootnode

    # update idxs and return
    tree._update()
    return tree


if __name__ == "__main__":

    # Example test: start with a simple balanced tree.
    import toytree
    toytree.set_log_level("WARNING")
    TREE = toytree.rtree.imbtree(ntips=10)
    print(TREE)

    # root on
    TREE.unroot().root('r0', 'r1', 'r2')

    # raise error b/c not monophyletic
    # TREE.unroot().root("r8", "r9", "r0")

    # c, a, m = unroot(TREE).draw()
    # _, a, m = root(TREE, 'r2')._draw_browser()

    # T0 = root(TREE, 'r2', root_dist=0.3)

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