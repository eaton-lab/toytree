#!/usr/bin/env python

"""Core ToyTree class object of the toytree package.

Examples
--------
>>> tree = toytree.rtree.unitree(10)
>>> tree = toytree.ToyTree(toytree.Node('a'))
>>> tree = toytree.tree("((a,b),c);")

References
----------
- ete3
- toytree
"""

from __future__ import annotations
from typing import (
    Sequence, Dict, List, Optional, Iterator, Any, Set,
    Union, Tuple, TypeVar, Callable)
import re
from copy import deepcopy
from hashlib import md5

from loguru import logger
import numpy as np
import pandas as pd
from toyplot import Canvas
from toyplot.coordinates import Cartesian

# subpackage object APIs
from toytree.style import TreeStyle
from toytree.mod._src.api import TreeModAPI
from toytree.distance._src.api import DistanceAPI

from toytree import enumeration
from toytree.core.node import Node
from toytree.drawing import ToytreeMark, draw_toytree, get_layout, get_tree_style
from toytree.utils import ToytreeError
import toytree
# from toytree.io.src.writer import write_newick
# from toytree.pcm.api import PhyloCompAPI

# pylint: disable=too-many-branches, too-many-lines, too-many-public-methods

# toytree logger
logger = logger.bind(name="toytree")

# Type alias for Node selection
Query = TypeVar("Query", str, int, Node, None)


class ToyTree:
    """ToyTree class for manipulating and drawing trees.

    ToyTrees should generally be created using a constructor function
    such as `toytree.tree` or `toytree.rtree`, to init a tree from
    input data (e.g. newick) or random generators, respectively. This
    class can be used for type checking.

    Parameters
    ----------
    Node: Node
        A toytree.Node class instance representing the tree root.
    """
    def __init__(self, treenode: Node) -> ToyTree:
        """Initialize a ToyTree from a Node instance."""

        self.treenode = treenode
        """: The root Node; connected Nodes form the tree structure."""
        self.nnodes: int = 0
        """: number of Nodes in the tree. Automatically updated."""
        self.ntips: int = 0
        """: number of leaf Nodes (tips) in the tree. Automatically updated."""
        self.style = TreeStyle()
        """: dict-like class for setting base drawing styles."""
        self._idx_dict: Dict[int, Node] = {}
        """: dict mapping Node idx labels to Node instance. (private)."""

        # toytree subpackage library API (mod, pcm, distance, layout)"""
        self.mod = TreeModAPI(self)
        """: API to apply :mod:`toytree.mod` tree modification funcs to this tree."""
        self.pcm = None
        """: API to apply :mod:`toytree.pcm` phylogenetic comparative methods funcs to this tree."""
        self.distance = DistanceAPI(self)
        """: API to apply :mod:`toytree.distance` comparison funcs to this tree."""

        # update Node idxs, _idx_dict, nnodes, ntips, and Node heights
        self._update()

    #####################################################
    ## DUNDERS
    #####################################################
    # def __len__(self) -> int:
        # """Ambiguous, does one expect ntips or nnodes? So it is
        # not supported. See .ntips and .nnodes attrs."""
        # return self.ntips

    def __iter__(self) -> Iterator[Node]:
        """ToyTree is iterable, returning Nodes in idx order."""
        return (self[i] for i in range(self.nnodes))

    def __getitem__(self, idx: int) -> Node:
        """ToyTree is indexable by idx label to access Nodes."""
        # decided not to support slice here b/c it slows down indexing 2X.
        # if isinstance(idx, slice):
            # return [self._idx_dict[idx] for idx in range(*idx.indices(self.nnodes))]
        return self._idx_dict[idx]

    def __repr__(self) -> str:
        """Short object representation for toytree.core.tree.ToyTree"""
        return f"<toytree.ToyTree at {hex(id(self))}>"

    #####################################################
    ## FEATURES
    #####################################################

    @property
    def features(self) -> Tuple[str]:
        """Return a set of all Node data feature names.

        The basic 'features' present on all Nodes include 'dist',
        'name', 'support', 'height', and 'idx'. These features will
        all be shown if you call `ToyTree.get_node_data()`. To add
        additional features to all Nodes use `ToyTree.set_node_data`.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10)
        >>> # set 'color' feature on a single Node.
        >>> tree[5].color = 'red'
        >>> # get 'color' values for all Nodes.
        >>> tree.get_node_data("color", missing="blue")
        """
        feats = set()
        for node in self.traverse():
            feats.update(node.__dict__)
        feats = (i for i in feats if not i.startswith("_"))
        defaults = ("idx", "name", "height", "dist", "support")
        return defaults + tuple(feats)

    def remove_feature(self, *feature: str) -> None:
        """Remove one or more non-deafult data features from all Nodes.

        Cannot remove "idx", "name", "height", "dist", or "support".
        """
        for feat in feature:
            if feat in ("idx", "name", "height", "dist", "support"):
                raise ToytreeError(f"cannot remove feature: {feature}")
            for node in self.traverse():
                delattr(node, feat)

    #####################################################
    ## IDENTITY
    #####################################################

    def is_rooted(self) -> bool:
        """Return False if the tree is unrooted."""
        if len(self.treenode.children) > 2:
            return False
        return True

    def is_bifurcating(self, include_root: bool=True) -> bool:
        """Return False if no polytomies exist in tree.

        Parameters
        ----------
        include_root: bool
            If False then the state of the root node is ignored when
            checking for polytomies.
        """
        tris = [len(j.children) <= 2 for i, j in enumerate(self)]
        if include_root:
            return all(tris)
        return all(tris[:-1])

    def copy(self) -> ToyTree:
        """Return a deepcopy of the ToyTree."""
        return deepcopy(self)
        # return ToyTree(self.treenode.copy())

    #####################################################
    ## TRAVERSAL
    ## Visit all connected Nodes, and/or create ._idx_dict cache.
    #####################################################

    def traverse(self, strategy: str = "levelorder") -> Iterator[Node]:
        """Return an iterator over Nodes in a specific traversal order.

        Notes
        -----
        preorder:
            Parents are visited before children. Traverses all the way
            down each left subtree before proceeding to right child.
        postorder:
            Children are visited before parents. The left subtree is
            visited, then right, then the parent.
        levelorder:
            Nodes the same distance from root are visited left to
            right, before descending to next level.
        idxorder:
            Leaf nodes are visited left to right, followed by internal
            nodes in postorder traversal order. But, Nodes can be
            accessed in idxorder faster by indexing from the ToyTree
            directly as `[self[i] for i in range(self.nnodes)]`.
        inorder:
            Nodes are visited in non-descreasing order if they are
            a binary search tree: left child, parent, right child.

        Parameters
        ----------
        strategy: str
            A traversal strategy for the order in which nodes will
            be visited: 'preorder', 'postorder', 'levelorder',
            'inorder', or 'idxorder'.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10, seed=123)
        >>> ords = ['postorder', 'preorder', 'levelorder', 'idxorder']
        >>> for ord in ords:
        >>>     for idx, node in enumerate(tree.treenode.traverse(ord)):
        >>>         node.traverse_order = str(idx)
        >>>     tree.draw(
        >>>         node_labels="traverse_order",
        >>>         node_sizes=16, node_mask=False);
        """
        for node in self.treenode.traverse(strategy=strategy):
            yield node

    def _update(self) -> None:
        """Traverse to set and cache Node idxorder and coordinates.

        idxorder traversal is used to fill the ToyTree._idx_dict to
        make Nodes easily indexable. While doing this it also calculates
        Node heights and spacing (_x) and counts nnodes and ntips.

        If a topology has been modified then idx labels must be
        updated. This function is called by all internal `toytree.mod`
        functions which modify the topology (e.g., add_child, root,
        rotate, etc) but not if users modify Nodes adhoc. This is why
        Node objects are immutable.
        """
        # clear depth counters used to get heights during traversal
        depths = {self.treenode: 0}

        # queue starts with root children, and stack starts with root.
        queue = list(self.treenode._children)

        # start w/ root on stack, as either an inner or a tip.
        if queue:
            inner_stack = [self.treenode]
            outer_stack = []
        else:
            inner_stack = []
            outer_stack = [self.treenode]

        # traverse left then right subtrees to fill and pull from queue
        while queue:
            # get node from start of queue to proceed levelorder
            node = queue.pop()

            # set depth of this node from the root
            depths[node] = depths[node.up] + node._dist

            # if leaf add to output stack and update farthest depth
            if node.is_leaf():
                outer_stack.append(node)
            else:
                inner_stack.append(node)

            # add node's children to the queue (left child on end)
            queue.extend(node._children)

        # get max_depth from root, height is measured relative to this.
        max_depth = max(depths.values())

        # clear idx cache and counter to be filled next
        idx = 0
        self._idx_dict.clear()

        # return nodes in reverse order they were added to stack
        while outer_stack:
            node = outer_stack.pop()
            node._height = max_depth - depths[node]
            node._x = idx
            node._idx = idx
            self._idx_dict[idx] = node
            idx += 1
        self.ntips = idx

        # return internal nodes, or just root if only a single Node.
        while inner_stack:
            node = inner_stack.pop()
            node._height = max_depth - depths[node]
            node._x = sum(i._x for i in node._children) / len(node._children)
            node._idx = idx
            self._idx_dict[idx] = node
            idx += 1
        self.nnodes = idx

    #####################################################
    ## TREE MODIFICATION FUNCTIONS (See ToyTree.mod)
    ## - root, unroot, rotate_node, ladderize,
    ## - set_node_heights, collapse_nodes, prune,
    ## - drop_tips, resolve_polytomy,
    #####################################################

    def root(
        self,
        *query: Query,
        regex: bool=False,
        root_dist: Optional[float] = None,
        edge_features: Optional[Sequence[str]] = None,
        inplace: bool=False,
        ) -> ToyTree:
        r"""Return a ToyTree rooted on the edge above selected Node query.

        Rooting a tree involves splitting and edge to insert a new Node.
        (It helps to think of it as pinching an edge and pulling it back
        to create a new root). This adds a Node to an unrooted tree,
        or keeps the number of Nodes the same for an already rooted
        tree, where the former root Node is discarded.

        Example of rooting an unrooted tree:
                                                    x
                                                   / \
                        2          root('n')      n   u
                      / | \          -->             / \
                     1  .  u                        2   .
                          / \                      / \
                         .   n                    1   .

        Example of re-rooting a rooted tree:
                       o                            x
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
        regex: bool
            If True then Node name strings are treated as regular
            expressions that can match to multiple Nodes.
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

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=10, seed=123)
        >>> t1 = tree.root("r8", "r9")
        >>> t2 = tree.root("r8", "r9", root_dist=0.3)
        >>> toytree.mtree([t1, t2]).draw();
        """
        return self.mod.root(
            *query, regex=regex, root_dist=root_dist,
            edge_features=edge_features, inplace=inplace
        )

    def unroot(self, inplace: bool=False) -> ToyTree:
        """Return an unrooted ToyTree by collapsing the root Node.

        This will convert a binary split into a multifurcation.
        The Node idx values can change on unrooting because the number of
        Nodes has changed.

        Note
        ----
        The unrooting process is not destructive of information, you can
        re-root a tree on the same edge position as before to recover the
        same tree.

        Parameters
        ----------
        inplace: bool
            If True modify and return original tree, else return a copy.
        """
        return self.mod.unroot(inplace=inplace)

    #################################################
    ## NODES SEARCH/MATCH BY FLEXIBLE INPUTS
    ## Matching Nodes by name can be used to color nodes/edges...
    #################################################

    def _iter_nodes_by_name_match(
        self, *query: str, regex: bool = False) -> Iterator[Node]:
        """Return Iterator over Nodes in idxorder matched by leaf names."""
        # get matching function
        if regex:
            try:
                comp = [re.compile(q) for q in query]
            except re.error as inst:
                msg = f"invalid regex query {query} raised a re.error: {inst}"
                logger.error(msg)
                raise ToytreeError(msg) from inst
            match = lambda x: any(q.search(x) for q in comp)
        else:
            match = lambda x: x in query

        # yield matching nodes
        for node in self.traverse("idxorder"):
            if match(node.name):
                yield node

    def get_nodes(self, *query: Query, regex: bool = False) -> List[Node]:
        """Return a list of Nodes matching a flexible query.

        Node instances can be selected by entering Node name strings,
        Node int idx labels, and/or Node objects. Input types are
        detected automatically, and even mixed input types can be
        entered. Node name strings can also be entered as regular
        expressions (e.g., 'r[0-3]') to match multiple names, which
        will be expanded if `regex=True`. If no query is entered then
        all Nodes are returned (this is fast, uses cached data.)

        This function is used inside many other toytree functions that
        similarly take `*Query` as an argument; any place users may
        want to use a flexible query method to select  a set of Nodes,
        or their common ancestor. The order of returned Nodes is
        similar random.

        Parameters
        ----------
        query: str, int, Node, or None
            Flexible query selector can search for Nodes by name, idx
            label, or by entering a Node directly. Multiple values can
            be entered to return a list of matching Nodes.
        regex: bool
            If True then string queries are treated as regular
            expressions. If a regular expression fails to match
            anything it will raise an exception.

        Notes
        -----
        You can `practice your regex here: <https://pythex.org/>`_

        Examples
        --------
        >>> tree = toytree.rtree.unittree(16, seed=123)
        >>> tree.get_nodes()                      # all Nodes returned
        >>> tree.get_nodes("r1")                  # [Node(1)]
        >>> tree.get_nodes("r1", "r2")            # [Node(1), Node(2)]
        >>> tree.get_nodes("r[1-2]$", regex=True) # [Node(1), Node(2)]
        >>> tree.get_nodes(5, 6)                  # [Node(5), Node(6)]
        >>> tree.get_nodes(tree[5], "r1")         # [Node(5), Node(1)]
        >>> tree.get_nodes(*[2,3])                # [Node(2), Node(3)]
        """
        # fastest return, all cached Nodes
        if query == ():  # ignore b/c query can be 0
            return list(self)

        nodes = set()
        for que in query:
            if isinstance(que, int):
                nodes.add(self[que])
            # odd case: query a ToyTree with Nodes from a diff tree.
            elif isinstance(que, toytree.Node):
                if que in self:
                    nodes.add(que)
                else:
                    raise ValueError(
                        f"query {que} is not in *this* tree. Perhaps you are "
                        "tring to query with a Node\nfrom a different ToyTree. "
                        "To avoid this warning, which is trying to save you "
                        "from potential \nerrors, please do the following:\n"
                        "1. Make sure you actually want to query with this Node.\n"
                        "2. Because this tree may not be the same as the tree "
                        "from which the input Node is connected,\nyou should "
                        "instead find the Node in this tree that is equivalent, "
                        "e.g.,\n"
                        ">>> node = tree.get_mrca_node(*other_node.get_tip_labels())\n"
                        ">>> tree.get_nodes(node) \n"
                    )

                    # nodes.add(self[que.idx])
            elif isinstance(que, str):
                matched = set(self._iter_nodes_by_name_match(que, regex=regex))
                nodes.update(matched)
                if not matched:
                    raise ValueError(
                        f"No Node names match '{que}' using regex={regex}.")
            elif isinstance(que, np.integer):
                nodes.add(self[que])
            else:
                raise TypeError(f"query type {type(que)} not supported.")
        return list(nodes)

    def get_ancestors(
        self,
        *query: Query,
        include_query: bool=True,
        include_top: bool=True,
        stop_at_mrca: bool=False,
        ) -> Set[Node]:
        """Return a set of Nodes that are ancestors of the query samples.

        The returned set can include or exclude the sample query; it
        can trace back all ancestors to the root of the tree, or only
        to the MRCA of the sample query; and it include or exclude
        the top node (root or MRCA depending on arguments).

        Parameters
        ----------
        *query: str, int, Node
            One or more Node objects, Node str names, or Node int idx
            labels, any of which can be used to select Nodes.
        include_query: bool
            If False the query Nodes are not included in returned set.
        include_top: bool
            If False the 'top' Node of the set is not included. This
            can be either the tree root, or the MRCA Node, depending
            on the `stop_at_mrca` argument.
        stop_at_mrca: bool
            If False then all ancestors are included back to the root
            of the tree. If True, ancestors only trace back to MRCA
            of the sample query.

        Examples
        --------
        ...
        """
        query = set(self.get_nodes(*query))
        ancestors = set.union(*[
            set(self[i.idx].get_ancestors()) for i in query])
        if stop_at_mrca:
            mrca = self.get_mrca_node(*query)
            for anc in mrca.get_ancestors():
                ancestors.discard(anc)
            if include_top is False:
                ancestors.discard(mrca)
        else:
            if include_top is False:
                ancestors.discard(self.treenode)
        if include_query:
            return query.union(ancestors)
        return ancestors

    def get_mrca_node(
        self, *query: Query, regex: bool = False) -> Node:
        """Return the MRCA Node from Nodes matching a flexible query.

        Find and return the most-recent-common-ancestor Node instance
        based on input selectors that can be either Node names, Node
        int idx labels, or Node objects. Input types are detected
        automatically and handled, so that even mixed input types can
        be entered (e.g., `get_mrca_node('a', 2, 3)`). If the selected
        Nodes do not share a common ancestor this will raise a
        ToytreeError. This function is useful for selecting and
        annotating clades on a tree drawing. Node names can also be
        entered as regular expressions to match multiple names, which
        will be detected and expanded if `regex=True`.

        Parameters
        ----------
        *query: str, int, Node
            One or more Node objects, Node str names, or Node int idx
            labels, any of which can be used to select Nodes.
        regex: bool
            If True then input node name strings are treated as
            regular expressions that can match one or more Nodes.

        Notes
        -----
        If the tree is unrooted then the mrca will be found relative
        to the 'psuedo-root' (the Node that exists as parent to the
        basal trichotomy, but has no features associated with it).

        Examples
        --------
        >>> tree = toytree.rtree.unittree(12)
        >>> mrca = tree.get_mrca_node('r1', 'r2', 'r3')
        >>> mrca = tree.get_mrca_node('r[1-3]$', regex=True)
        >>> mrca = tree.get_mrca_node(12)
        >>> mrca = tree.get_mrca_node(12, 13, 14, 15)
        >>> mrca = tree.get_mrca_node(*(tree[i] for i in (12, 13, 14)))
        >>> print(mrca.idx, mrca.get_descendants())
        """
        # get flexible input as Node instances
        nodes = self.get_nodes(*query, regex=regex)

        # store observed Node idxs to check for disconnected Node inputs
        idx_sets = []

        # find every idx on way up to the root, and add the nidx itself
        for node in nodes:
            nset = set(i.idx for i in node._iter_ancestors())
            nset.add(node.idx)
            idx_sets.append(nset)

        # bad set of node idxs
        if not idx_sets:
            raise ToytreeError(f"No common ancestor of {nodes}")

        # get the lowest idx shared
        mrca_idx = min(set.intersection(*idx_sets))
        return self[mrca_idx]

    def get_node_mask(
        self,
        *unmask: Query,
        mask_tips: bool=True,
        mask_internal: bool=False,
        mask_root: bool=False,
        ) -> Sequence[bool]:
        """Return a boolean array to mask certain Nodes when drawing.

        Creates a boolean mask to hide a set of selected Nodes.
        The array is in Node idxorder (from 0-nnodes) where boolean
        True will *mask* Nodes, and False will *show* Nodes. Additional
        Nodes can be selected to be unmasked by entering Node int idx
        labels or name strings. By default, the tip Nodes are masked
        and all internal Nodes are unmasked.

        Parameters
        ----------
        *unmask: int or str
            Any Nodes selected by int or str labels will be unmasked
            (shown). If selected, this overrides their inclusion in
            mask_tips, mask_internal, or mask_root.
        mask_tips: bool
            If True all tip Nodes will be masked.
        mask_internal: bool
            If True all internal Nodes will be masked.
        mask_root: bool
            If True the root Node will be masked.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10, seed=123)
        >>> mask = tree.get_node_mask(15, 16, internal=True, root=True)
        >>> tree.draw(ts='s', node_mask=mask);
        """
        arr = np.zeros(self.nnodes, dtype=bool)
        if mask_tips:
            arr[:self.ntips] = 1
        if mask_internal:
            arr[self.ntips:-1] = 1
        if mask_root:
            arr[-1] = 1
        if unmask:# != ():
            for node in self.get_nodes(*unmask):
                arr[node.idx] = 0
        return arr

    def is_monophyletic(
        self,
        *query: Query,
        regex: bool = False,
        # unrooted: bool=False,
        ) -> bool:
        """Return True if leaf Nodes form a monophyletic clade.

        If any other leaf Nodes are members of this clade, but not
        included in the input set of 'nodes', then these Nodes are
        not monophyletic. Nodes can be entered either as Node objects
        or by their int idx labels.

        Parameters
        ----------
        *query: Node, str, or int
            One or more Node objects, Node name str, or Node idx int
            labels to check for monophyly.
        regex: bool
            If True then string queries are treated as regular
            expressions that can match multiple Node names.
        unrooted: bool
            If True then the selected Nodes are tested for monophyly
            without reference to the placement of the root Node.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=10, seed=123)
        >>> tree.draw()
        >>> print(tree.is_monophyletic(0, 1, 2))
        >>> print(tree.is_monophyletic(0, 4, 8))
        """
        # if unrooted:
            # raise NotImplementedError("TODO")
        nodes = self.get_nodes(*query, regex=regex)
        mrca = self.get_mrca_node(*nodes)
        for node in mrca._iter_leaves():
            if node not in nodes:
                return False
        return True

    ##################################################
    ## TREE DISTANCE (ToyTree.distance)
    ## get distances between nodes, trees, or data points
    ##################################################

    ###################################################
    ## I/O FORMATTING (toytree.io)
    ## read and write trees to newick, nexus, nhx
    ###################################################

    def write(
        self,
        path: Optional[str] = None,
        dist_formatter: Optional[str] = "%.12g",
        internal_labels: Optional[str] = "support",
        internal_labels_formatter: Optional[str] = "%.12g",
        features: Optional[Sequence[str]] = None,
        features_prefix: str = "&",
        features_delim: str = ",",
        features_assignment: str = "=",
        **kwargs,
        ) -> Optional[str]:
        """Write tree to newick string and return or write to filepath.

        The newick string can be formatted in several ways. The default
        will include dist values (edge lengths) and support values as
        internal node labels. The edge lengths can be suppressed by
        setting `dist_formatter=None`, and internal node labels can be
        similarly suppressed, or set to store a different feature, such
        as internal node names. Additional features can be stored in the
        node comment blocks in extended-newick-format (NHX-like) by using
        the "features" arguments (see examples).

        Parameters
        ----------
        tree: ToyTree
            A ToyTree instance to write as a newick string.
        path: str or None
            A filepath to write to file, or None to return newick string.
        dist_formatter: str or None
            A formatting string to format float dist values (edge lengths),
            or None to not write dist values. Default is "%.6g".
        internal_labels: str or None
            A feature to write as internal node labels. None suppresses
            internal labels. The 'support' feature is default, and
            often used here, but 'name' or any other feature can be
            used as well.
        internal_labels_formatter: str or None
            A formatting string to format internal labels. If an internal
            label cannot be formatted due to TypeError (e.g., you select
            'name' for `internal_labels` but leave this optional at its
            default as a float formatter '%.6g', instead of str formatter)
            it will simply be converted to a string.
        features: List[str]
            A list of additional features to write in the newick comment
            block. For example, features=["height"] will save heights.
        features_prefix: str
            A prefix character written to the start of newick comment
            blocks. Typical values are "&" (default) or "&&NHX:".
        features_delim: str
            A character used to delimit features in the newick comment
            block. Default is ",".
        features_assignment: str
            A character used to separate feature keys and values. Default
            is "=".

        See Also
        --------
        `write_nexus`
            Write tree newick string in a NEXUS format.
        `ToyTree.write`
            This function is available from ToyTree objects as `.write`.

        Examples
        --------
        >>> nwk = "((a:3[&state=1],b:3[&state=1])D:1[&state=1],c:4[&state=2])E:1[&state=1];"
        >>> tree = toytree.io.parse_newick(nwk, features_prefix="&")
        >>> tree.write()
        >>> # ((a:3,b:3)100:1,c:4)100:1
        >>> tree.write(dist_formatter=None)
        >>> # ((a,b)100,c)100
        >>> tree.write(internal_label=None)
        >>> # ((a:3,b:3):1,c:4):1
        >>> tree.write(internal_labels="name")
        >>> # ((a:3,b:3)D:1,c:4)E:1
        >>> tree.write(features=["size"])
        >>> # ((a:3[&state=1],b:3[&state=1])100:1[&state=1],c:4[&state=2])100:1[&state=1]
        """
        if kwargs:
            logger.warning(
                f"Deprecated args to write(): {list(kwargs.values())}. See docs.")
        return toytree.io.write_newick(
            self, path,
            dist_formatter, internal_labels, internal_labels_formatter,
            features, features_prefix, features_delim, features_assignment
        )

    ###################################################
    ## TOPOLOGY OR LEAF ANALYSIS FUNCTIONS
    ## access nodes or features ...
    ###################################################

    def get_tip_labels(self) -> List[str]:
        """Return a list of tip labels in Node idx order."""
        return [self[i].name for i in range(self.ntips)] # .treenode.get_leaf_names()

    def _get_edges(self) -> np.ndarray:
        """Return numpy array of child,parent relationships."""
        data = np.array([(i.idx, i.up.idx) for i in self if i.up])
        return data

    def get_edges(self) -> pd.DataFrame:
        """Return a DataFrame with child -> parent idx labels.

        To return as a numpy array instead of DataFrame you can use
        tree._get_edges().
        """
        return pd.DataFrame(self._get_edges(), columns=["child", "parent"])

    def iter_bipartitions(
        self,
        feature: str="name",
        exclude_root: bool=True,
        exclude_singletons: bool=True,
        exclude_internal_nodes: bool=True,
        ) -> Iterator[Tuple[Tuple[str],Tuple[str]]]:
        """Generator to yield bipartitions (info about splits in a tree).

        Bipartitions are yielded in random order, but splits and labels
        within bipartitions are sorted. By default bipartitions do not
        include the root Node, but this can be toggled on to return
        bipartitions that can uniquely distinguish rooted topologies.

        Parameters
        ----------
        feature: str
            Feature to return to represent Nodes on either side of a
            bipartition. Default is "name", but custom features can
            also be returned, or use None to return Node objects.
        exclude_root: bool
            Default if to exclude root Node. If True the root Node
            is included in splits, and one additional bipartition is
            included which specifies root location.
        exclude_singletons: bool
            Default is to exclude singleton splits (e.g., {A | B,C,D})
            since it is implicit that one exists for every tip Node,
            but these can also be included if requested.
        exclude_internal_nodes: bool
            Default is to only show tip Nodes on either side of a
            bipartition, but internal Nodes can be included as well. In
            this case the feature should likely be set to "idx", None, or
            some other feature for which internal Nodes have unique values.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
        >>> sorted(iter_bipartitions(tree, 'name'))
        >>> # [(('r0', 'r1'), ('r2', 'r3', 'r4')),
        >>> #  (('r3', 'r4'), ('r0', 'r1', 'r2'))]
        >>> #
        >>> sorted(iter_bipartitions(tree, 'name', exclude_root=False))
        >>> # [(('r0', 'r1'), ('r2', 'r3', 'r4')),
        >>> #  (('r3', 'r4'), ('r0', 'r1', 'r2')),
        >>> #  (('r3', 'r4'), ('r0', 'r1', 'r2'))]

        Note
        ----
        feature='idx' is not a good option if you plan to compare
        bipartitions among trees, since tip idx labels can be
        different simply due to Node rotations. Using feature='name'
        will reliably return the same bipartitions regardless of
        Node rotations. See also `ToyTree.get_topology_id` which
        uses bipartitions yield unique hash identifiers for trees.
        """
        return enumeration.iter_bipartitions(
            tree=self,
            feature=feature,
            exclude_root=exclude_root,
            exclude_singletons=exclude_singletons,
            exclude_internal_nodes=exclude_internal_nodes,
            )

    def iter_quartets(
        self,
        feature: str="name",
        collapse: bool=False,
        ) -> Iterator[Tuple]:
        """Generator to yield quartets induced by edges on a tree.

        This yields all quartets (4-sample subtrees) that exist within
        a larger tree. The set of possible quartets is not affected
        by tree rooting, but is affected by collapsed edges
        (polytomies), which reduce the number of quartets.

        Quartets are returned as tuples of tuples, where e.g.,
        (('a', 'b'), ('c', 'd')) implies a `ab|cd` quartet. The
        order in which quartets are yielded depends on the topology,
        and can be sorted after, but the order of Nodes within each
        tuple is sorted by the requested feature (e.g., name). The
        collapse=True argument can be used to simplify the returned
        format to a single tuple with the same order.

        Parameters
        ----------
        feature: str
            Feature to return to represent Nodes on either side of a
            bipartition. Default is "name", but custom features can
            also be returned, or use None to return Node objects.
        collapse: bool
            By default collapse=False returns quartets as a tuple of
            tuples, e.g., ((0, 1), (2, 3)), but if collapse=True they
            are returned as a single tuple (0, 1, 2, 3), in the same
            order, with the split implied between index 1 and 2.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
        >>> print(sorted(tree.iter_quartets()))
        >>> # [(('r0', 'r1'), ('r2', 'r3')),
        >>> #  (('r0', 'r1'), ('r2', 'r4')),
        >>> #  (('r0', 'r1'), ('r3', 'r4')),
        >>> #  (('r0', 'r2'), ('r3', 'r4')),
        >>> #  (('r1', 'r2'), ('r3', 'r4'))]
        >>>
        >>> print(sorted(tree.iter_quartets(collapse=True)))
        >>> # [('r0', 'r1', 'r2', 'r3'),
        >>> #  ('r0', 'r1', 'r2', 'r4'),
        >>> #  ('r0', 'r1', 'r3', 'r4'),
        >>> #  ('r0', 'r2', 'r3', 'r4'),
        >>> #  ('r1', 'r2', 'r3', 'r4')]
        """
        return enumeration.iter_quartets(
            tree=self, feature=feature, collapse=collapse)

    def get_bipartitions(
        self,
        feature: str = "name",
        exclude_internal_labels: bool=True,
        exclude_singleton_splits: bool=True,
        ) -> pd.DataFrame:
        """Return a DataFrame with partitions from tree in idx order.

        Partitions represent splits that separate sets of Nodes in a
        tree, and can be represented by the tips descended from each
        side of the split, e.g., [['a', 'b'], ['c', 'd']]. Options are
        available to return all Nodes on either side of a partition,
        instead of just the tips, but tips are generally of interest.
        The index of the returned DataFrame corresponds to the Node
        idx label below the edge of each partition.

        Note
        ----
        The root Node is ignored, and so rooting has no effect on
        the partitions. This is because the root separates None from
        all, e.g., [[], ['a', 'b', 'c', 'd']], and the nodes on
        either side of the root have the same partition, [['a', 'b'],
        ['c', 'd']], only one of which is returned.

        Parameters
        ----------
        feature: str
            The Node feature to return for every Node on each side of
            a split. Default is "name".
        exclude_internal_labels: bool
            Default is to only show tip Nodes on either side of a
            bipartition, but internal Nodes can be included as well.
        exclude_singleton_splits: bool
            Default is to exclude singleton splits (e.g., {A | B,C,D})
            since it is implicit that one exists for every tip Node,
            but these can be included if requested.

        See Also
        --------
        `ToyTree.iter_bipartitions`, `ToyTree._get_bipartitions_table`

        Examples
        --------
        >>> tree = toytree.rtree.unittree(4)
        >>> print(tree.get_bipartitions())
        """
        biparts = list(self.iter_bipartitions(
            feature, exclude_internal_labels, exclude_singleton_splits))
        if exclude_singleton_splits:
            index = range(self.ntips, self.ntips + len(biparts))
        else:
            index = None
        return pd.DataFrame(biparts, index=index)

    def _get_bipartitions_table(
        self,
        exclude_internal_labels: bool=True,
        exclude_singleton_splits: bool=False,
        dtype: type=int,
        ) -> pd.DataFrame:
        """Return a DataFrame with partitions in binary format."""
        bits = list(self.iter_bipartitions(
            "idx", exclude_internal_labels, exclude_singleton_splits))
        cols = self.ntips if exclude_internal_labels else self.nnodes - 1
        arr = np.zeros(shape=(len(bits), cols), dtype=dtype)
        for idx, bit in enumerate(bits):
            arr[idx, bit[0]] = 1
        if exclude_singleton_splits:
            index = range(self.ntips, self.ntips + len(bits))
        else:
            index = None
        return pd.DataFrame(arr, columns=self.get_tip_labels(), index=index)

    def get_topology_id(self, feature="name", exclude_root: bool=True) -> str:
        """Return a unique ID representing this topology.

        Two trees with the same topology and tip names will produce
        the same id, i.e., the rotation of Nodes does not affect the
        geneated ID. Rooting/Unrooting does affect it. The ID string
        is useful for identifying unique topologies among a set of
        trees without requiring distance comparisons. This method
        uses an md5 hash of a string of ordered Node names with
        the digest value represented as a string of hexadecimal digits.

        Parameters
        ----------
        features: str
            The feature used to represent tip Nodes (default='name').
            This should be a feature that is unique among tip Nodes,
            and is relevant to identifying similarity among the trees
            you plan to compare using topology id strings. Careful
            changing this option from 'name' unless you are familiar
            with the consequences.
        exclude_root: bool
            By default the root Node is excluded (if tree is rooted)
            such that all unrooted trees with the same toplogy return
            the same topology_id. To distinguish among differently
            rooted versions of the same tree set `exclude_root=False`.

        Examples
        --------
        >>> tree.get_topology_id() # '70f5cfb041f176d86020971ac5f633e1'

        See Also
        --------
        - iter_bipartitions
        """
        biparts = sorted(self.iter_bipartitions(
            feature=feature, exclude_root=exclude_root))
        return md5(str(biparts).encode('utf-8')).hexdigest()

    ###################################################
    ## COORDINATE LAYOUT FUNCTIONS
    ## push to .layout subpackage
    ###################################################

    def _get_node_coordinates(self) -> np.ndarray:
        """Return numpy array of 'unstyled' cached node coordinates."""
        return np.array([(i._x, i._height) for i in self])

    def get_node_coordinates(self, **kwargs) -> pd.DataFrame:
        """Return a DataFrame with xy coordinates for plotting nodes.

        This returns coordinates that could be used when adding
        additional annotations to plots, such as scatterplot points,
        or error bars on top of nodes. By default Node idx=0 will be
        located at coordinate position (0, 0), which can be modified
        using the `xbaseline` and `ybaseline` args.

        Take care when calling this function that the coordinates
        will be different depending on the *style* arguments applied.
        The style args come from the `.style` dict-like object of the
        ToyTree, and can be overriden by additional args to this func,
        the same as in the `.draw()` function. For example, layout
        facing down ('d') will yield different coordinates than layout
        facing up ('u').

        Examples
        --------
        >>> style = {'layout': 'd', 'xbaseline': 10}
        >>> canvas, axes, mark = tree.draw(**style)
        >>> node_coords = tree.get_node_coordinates(**style)
        >>> axes.scatterplot(coords.x, coords.y, size=10);
        """
        style = get_tree_style(self, **kwargs)
        coords = get_layout(self, style).coords
        data = pd.DataFrame(
            columns=('x', 'y'),
            index=range(self.nnodes),
            data=coords,
        )
        return data

    def get_tip_coordinates(self, **kwargs) -> pd.DataFrame:
        """Return a DataFrame with xy coordinates for tip nodes.

        See `ToyTree.get_node_coordinates` for details.
        """
        return self.get_node_coordinates(**kwargs).iloc[:self.ntips]

    ###################################################
    ## FULL TREE DATA GET/SET
    ## functions to modify features of all connected Nodes
    ###################################################

    def get_feature_dict(self, keys: str=None, values: str=None) -> Dict:
        """Return a dict mapping selected Node features as keys, values.

        This can be used to return a dict mapping any two arbitrary
        features, or to Node objects. Examples include mapping Node
        objects to dist values, or idx labels to Node names, or
        Node names to Node objects. There are many possibilities. The
        value of None for `keys` or `values` returns Node objects.
        Retured dict is in idxorder.

        Parameters
        ----------
        keys: str or None
            Select the keys of the returned dictionary.
        values: str or None
            Select the values of the returned dictionary.

        Examples
        --------
        >>> nodes_to_dists = tree.get_feature_dict(None, 'dist')
        >>> idx_to_names = tree.get_feature_dict('idx', 'name')
        >>> names_to_nodes = tree.get_feature_dict('name', None)

        See Also
        --------
        get_node_data
            Return feature data as a DataFrame w/ options for
            how to impute values for missing features on some nodes.
        """
        ndict = {}
        try:
            for _, node in self._idx_dict.items():
                if keys is not None:
                    key = getattr(node, keys)
                else:
                    key = node
                if values is not None:
                    value = getattr(node, values)
                else:
                    value = node
                ndict[key] = value
        except AttributeError as exc:
            raise ToytreeError(
                f"feature_dict cannot build {keys} -> {values} mapping "
                "because one or\nmore of the selected features is not assigned "
                "to every Node.\nSee `get_node_data()` for working with "
                "missing values."
            ) from exc

        # check that keys were not duplicated
        if len(ndict) != self.nnodes:
            raise ToytreeError(
                f"feature_dict cannot be built because {keys} "
                "does not have unique values, and thus Nodes with the "
                "same value cannot be represented as keys in the dict.")
        return ndict

    def _set_node_data_dtype(
        self, feature: str, dtype: Optional[Callable]=None) -> None:
        """Set the type/dtype (or infer) of a Node feature in-place.

        This is used internally when data is parsed from strings
        and may be a str, float, int, or complex type, and we want
        to be able to *try* to infer the proper type. Also, if the
        user knows the type then it can be set. This will raise a
        TypeError if the data cannot be cast to the entered dtype.

        Parameters
        ----------
        ...
        """
        raise NotImplementedError("TODO")

    def set_node_data_from_dataframe(
        self,
        table: pd.DataFrame,
        inplace: bool=False,
        ) -> ToyTree:
        """Set new features on Nodes of a ToyTree from a DataFrame.

        The DataFrame should have column names corresponding to features
        that you wish to apply to Nodes of the ToyTree. The index can
        be composed of either strings that match to .name attributes
        of Nodes in the ToyTree, or can be integers, which match to the
        .idx labels of Nodes. Note: to set data to internal Nodes that
        usually do not have unique name labels you will likely need to
        use the numeric idx labels. Be aware that idx labels are
        unique to each topology, and will change if the tree topology
        is modified.

        This function parses the DataFrame and applies the function
        `set_node_data()` for each column.

        Parameters
        ----------
        table: pd.DataFrame
            A DataFrame with data to be applied to Nodes of a ToyTree.
        inplace: bool

        Returns
        -------
        A copy of the original ToyTree with node features modified.

        See Also
        --------
        :meth:`~toytree.core.tree.ToyTree.get_node_data`,
        :meth:`~toytree.core.tree.ToyTree.set_node_data`.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=10)
        >>> data = pd.DataFrame({
        >>>    'trait1': np.arange(tree.nnodes),
        >>>    'trait2': np.random.randint(0, 100, tree.nnodes),
        >>> })
        >>> tree = tree.set_node_data_from_dataframe(data)
        >>> tree.get_node_data()
        """
        # make a copy of ToyTree to return
        tree = self if inplace else self.copy()
        for key in table.columns:
            mapping = table[key].to_dict()
            tree.set_node_data(feature=key, mapping=mapping, inplace=True)
        return tree


    def set_node_data(
        self,
        feature: str,
        mapping: Dict = None,
        default: Any = None,
        inherit: bool = False,
        inplace: bool = False,
        ) -> ToyTree:
        """Create or modify features (data) set to nodes in a ToyTree.

        Features can be set on all or only some nodes. In the latter
        case a value for nodes with missing features can be imputed
        when you call the function :meth:`~toytree.core.tree.ToyTree.get_node_data`.
        Some features used internally are protected from modification
        (e.g., idx, up, children), but other base features such as
        name, dist, height, and support can be modified, and any new
        feature name can be created.

        Values are set by providing a 'mapping' dictionary mapping node
        idx labels (int type) or names (str type) as keys and the
        associated values as dict values. The 'default' option can be
        used to set a value for the feature to all nodes not specified
        in the mapping.

        Parameters
        -----------
        feature: str
            The name of the node attribute to modify (cannot be 'idx').
        mapping: Dict
            A dictionary of {int: value} or {str: value}, where int
            keys will be interpreted as node idx labels, and str keys
            will be interpreted as node name labels.
            Note: use tree.draw(node_labels='idx') to see idx labels.
        default: Any
            You can use a default value to be filled for all other
            nodes not listed in the 'mapping' dictionary.
        inherit: bool
            If inherit is True then feature values are mapped to the
            selected nodes as well as to all of their descendant
            nodes. Note that the order of entries in mapping can
            affect the values applied if multiple selected nodes
            overlap in their descendants.

        Returns
        -------
        A copy of the original ToyTree with node features modified.

        See Also
        --------
        :meth:`~toytree.core.tree.ToyTree.get_node_data`.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=10)
        >>> new_tree = tree.set_node_data(feature="Ne", default=5000)
        >>> new_tree = tree.set_node_data(feature="Ne", mapping={0:1e5, 1:1e6, 2:1e3})
        >>> new_tree = tree.set_node_data(feature="Ne", mapping={0:1e5, 1:1e6}, default=5000)
        >>> new_tree = tree.set_node_data(feature="Ne", mapping={'r0':1e5, 'r1':1e6})
        >>> new_tree = tree.set_node_data(
        >>>     feature="state",
        >>>     mapping={10: "A", 11: "B"},
        >>>     inherit=True,
        >>> )
        """
        # immutable; do not allow modifying topology attributes
        if feature in ["idx", "up", "children"]:
            raise ToytreeError(
                f"cannot modify '{feature}' feature because it affects the "
                "tree topology. To modify topology see `toytree.mod` "
                "subpackage functions.")

        # ensure mapping is proper type. TODO: support pd.Series?
        if not isinstance(mapping, dict):
            if not mapping:
                mapping = {}
            else:
                raise TypeError(
                    "'mapping' arg should be a Dict, Dict-like, or None")

        # get {idx: values} for all mapping entries. The func get_nodes
        # raises an exception if any query is not in the tree.
        mapping = {
            self.get_nodes(i, regex=False)[0].idx: j
            for (i, j) in mapping.items()
        }

        # make a copy of ToyTree to return
        tree = self if inplace else self.copy()

        # sorted key nodes to map oldest (root) to youngest (tips)
        key_nodes = sorted(mapping, reverse=True)

        # make a dict {Node: newvalue} by expanding the entered mapping.
        ndict = {}

        # iterate over nodes sorted by oldest first.
        for nidx in key_nodes:
            node = tree[nidx]
            value = mapping[nidx]

            # map selected Node to value.
            ndict[node] = value

            # optionally map Node's descendants to value as well.
            if inherit:
                for desc in node._iter_descendants():
                    ndict[desc] = value

        # map {Node: default} for Nodes not in ndict
        if default is not None:
            for node in tree:
                if node not in ndict:
                    ndict[node] = default

        # special mod submodule method for height modifications
        if feature == "height":
            height_map = {i.idx: j for (i, j) in ndict.items() if j is not None}
            return tree.mod.edges_set_node_heights(height_map, inplace=inplace)

        # dist is immutable, but allow it here, and do an update.
        if feature == "dist":
            feature = "_dist"

        # add value to Nodes as a feature. If the value can be copied,
        # e.g., a dict, array, etc., then assign copies, otherwise if
        # this object is changed it affects the value of multiple Nodes
        for node, value in ndict.items():
            if hasattr(value, 'copy'):
                setattr(node, feature, value.copy())
            else:
                setattr(node, feature, value)

        # if dist was mod'd then must call update
        if feature == "_dist":
            tree._update()
        return tree

    def get_node_data(
        self,
        feature: Union[str, Sequence[str], None] = None,
        missing: Union[Any, Sequence[Any], None] = None,
        ) -> Union[pd.DataFrame, pd.Series]:
        """Return a pandas Series or DataFrame with values for one or
        more selected features in the tree.

        Parameters
        ----------
        feature: str, Iterable[str], or None
            One or more features of Nodes to get data for. Features
            include the default Node features (idx, name, height, dist,
            support) as well as any attribute that has been set to
            a Node (except attrs with names that start with an '_'.)
        missing: Any, Iterable[Any], or None
            A value to use for missing data (nodes that do not have
            the feature). Default arg is None which will automatically
            set missing data to `np.nan`. Example: you can set the
            missing values to a default value like 0 for an int feature
            or by entering 0, or you can enter a list of values to
            set default missing for all features.

        Returns
        -------
        pd.DataFrame or pd.Series
            If a single feature is selected then a pd.Series will be
            returned with tip node 'idx' attributes as the index.
            If multiple features are selected (or None, which selects
            all features) then a pd.DataFrame is returned with tip
            node 'idx' attributes as the index and feature names as
            the column labels.

        Examples
        --------
        Add a new feature to some nodes and fetch data for all nodes.
        >>> tree = toytree.rtree.unittree(10)
        >>> tree = tree.set_node_data("trait1", {0: "A", 1: "B"})
        >>> tree = tree.set_node_data("trait2", {2: 3.5, 3: 5.0})
        >>> data1 = tree.get_tip_data(feature="trait1", missing="C")
        >>> data2 = tree.get_tip_data(feature="trait2")

        See Also
        --------
        get_feature_dict
            Get a dict mapping any node feature to another.
        set_node_data
            Set a feature value to one or more Nodes in a ToyTree.
        get_tip_data
            Return DataFrame with feature data for only the tip Nodes.

        Note
        ----
        This function is convenient for accessing data in tabular
        format, but is slower than accessing data directly from Nodes,
        for example during a traversal, because it spends time checking
        for Nodes with missing data, and type-checks missing values.

        Setting complex objects to Node data, such as lists or sets,
        rather than float, int, or str, should generally work fine,
        but take care that toytree will not attempt to automatically
        check or fill missing values for these data.
        """
        # Storing missing as pd.NA allows not having to convert the
        # dtype of other values from e.g., int to float. However, if
        # <NA> gets converted to a string for plottig it will cause
        # havoc on the HTML. And it looks weird to have a mix of NaN
        # and <NA> in the data table. So should we use just one, or
        # both? Also pd.NA is very slow compared to np.nan.

        # TODO: AVOID FORMATTING FOR COMPLEX FEATURE TYPES (E.G., DICT, SET, ETC).
        # select one or more features to fetch values for
        if feature is None:
            features = self.features
        elif isinstance(feature, (list, tuple)):
            features = feature
        else:
            features = [feature]

        # create a list of missing values for subs
        if missing is None:
            missing = [np.nan] * len(features)
            # missing = [None] * len(features)
        elif isinstance(missing, (list, tuple)):
            assert len(missing) == len(features), (
                "when entering multiple missing values it must be the same "
                "length as the number of features")
        else:
            missing = [missing] * len(features)

        # check for bad user features
        for feat in features:
            if feat not in self.features:
                raise ValueError(f"feature '{feature}' not in tree.features.")

        # init a dataframe for all selected features
        # data = pd.DataFrame(
        #     index=range(self.nnodes),
        #     columns=features,
        # )

        # # get remaining features
        # for feat in features:
        #     for nidx in range(self.nnodes):
        #         data.loc[nidx, feat] = getattr(self[nidx], feat, pd.NA)

        #     # fill in appropriate missing data value for each Series
        #     if missing is not None:
        #         data[feat] = data[feat].where(data[feat].notnull(), missing)
        #     else:
        #         if data[feat].dtype == "O":
        #             data[feat] = data[feat].where(data[feat].notnull(), "")
        #         else:
        #             data[feat] = data[feat].where(data[feat].notnull(), pd.NA)

        # store as ordered lists, and let pd.Series convert to dtype
        data = {}
        for fidx, feat in enumerate(features):

            # fill ordered list with Node value or missing value
            ofeat = []
            miss = missing[fidx]

            # if miss is None then find auto-filling type. This is
            # quite slow (milliseconds) making this not the recommended
            # method for quick data fetching, as explained in docs.
            # if miss is None:
            #     values = [getattr(self[nidx], feat, None) for nidx in range(self.nnodes)]
            #     types = [type(i) for i in values if i is not None]

            # get value or set to missing
            for nidx in range(self.nnodes):
                value = getattr(self[nidx], feat, miss)
                # if the actual value is nan then replace with miss
                try:
                    if np.isnan(value):
                        value = miss
                except (TypeError, ValueError):
                    pass
                ofeat.append(value)

            # allow pandas to infer dtype
            series = pd.Series(ofeat)

            # modify dtype ...
            data[feat] = series

        # if a single feature was selected return as a Series else DataFrame
        if len(features) == 1:
            return series
        return pd.DataFrame(data)

    def get_tip_data(
        self,
        feature: Union[str, Sequence[str], None] = None,
        missing: Optional[Any] = None,
        ) -> pd.DataFrame:
        """Return a DataFrame with values for one or more selected
        features from every leaf node in the tree.

        Parameters
        ----------
        feature: str, Iterable[str], or None
            One or more features of Nodes to get data for.
        missing: Any
            A value to use for missing data (nodes that do not have
            the feature). Default arg is None which will automatically
            select a missing value based on the data type. Example:
            "" for str type, np.nan for numeric or complex types.
            Any value can be entered here to replace missing data.

        Returns
        -------
        data: pd.DataFrame or pd.Series
            If a single feature is selected then a pd.Series will be
            returned with tip node 'idx' attributes as the index.
            If multiple features are selected (or None, which selects
            all features) then a pd.DataFrame is returned with tip
            node 'idx' attributes as the index and feature names as
            the column labels.

        Examples
        --------
        Add a new feature to some nodes and fetch data for all nodes.
        >>> tree = toytree.rtree.unittree(10)
        >>> tree = tree.set_node_data("trait1", {0: "A", 1: "B"})
        >>> tree = tree.set_node_data("trait2", {2: 3.5, 3: 5.0})
        >>> data1 = tree.get_tip_data(feature="trait1", missing="C")
        >>> data2 = tree.get_tip_data(feature="trait2")

        See Also
        --------
        get_feature_dict
            Get a dict mapping any node feature to another.
        set_node_data
            Set a feature value to one or more Nodes in a ToyTree.

        Note
        ----
        This function is convenient for accessing data in tabular
        format, but is slightly slower than accessing data directly
        from Nodes because it spends time type-checking missing data.
        """
        return self.get_node_data(feature, missing).iloc[:self.ntips]

    ###################################################
    ## DRAWING
    ###################################################

    # --------------------------------------------------------------------
    # Draw functions imported, but docstring here...
    # TODO:
    #    - expand node_hover=True to a table of all features
    #    - fix admixture_edges
    # --------------------------------------------------------------------
    def _draw_browser(self, *args, new: bool = False, **kwargs):
        """Open and display tree drawing in default web browser.

        TODO: overload toyplot function, option to reuse same tab,
        add div styling, etc.
        Or, maybe make this at toytree level as `toytree.draw(canvas)`
        also make a `toytree.save()` shortcut to saving in formats.
        """
        import toyplot.browser
        canvas, axes, mark = self.draw(**kwargs)
        toytree.utils.show([canvas])
        return canvas, axes, mark

    def draw(
        self,
        tree_style: Optional[str]=None,
        height: int=None,
        width: int=None,
        axes: Cartesian=None,
        layout: str=None,
        tip_labels: Union[bool,Sequence]=None,
        tip_labels_colors: Union[str,Sequence]=None,
        tip_labels_angles: Union[float,Sequence[float]]=None,
        tip_labels_style: Dict[str,Any]=None,
        tip_labels_align: bool=None,
        node_mask: Union[bool,Sequence[bool]]=None,
        node_labels: Union[bool,Sequence[str]]=None,
        node_labels_style: Dict[str,Any]=None,
        node_sizes: Union[int,Sequence[int]]=None,
        node_colors: Union[str,Sequence[str]]=None,
        node_style: Dict[str,Any]=None,
        node_hover: bool=None,
        node_markers: Sequence[str]=None,
        edge_colors: Union[str,Sequence[str]]=None,
        edge_widths: float=None,
        edge_type: str=None,
        edge_style: Dict[str,Any]=None,
        edge_align_style: Dict[str,Any]=None,
        use_edge_lengths: bool=None,
        scale_bar: bool=None,
        padding: float=None,
        xbaseline: float=None,
        ybaseline: float=None,
        admixture_edges: List[Tuple[int,int]]=None,
        shrink: float=None,
        fixed_order: Sequence[str]=None,
        fixed_position: Sequence[float]=None,
        **kwargs,
        ) -> Tuple[Canvas, Cartesian, ToytreeMark]:
        """Return a drawing on the tree as a Toyplot figure.

        The drawing function return a tuple of Toyplot objects as
        (Canvas, Cartesian, Mark), and will automatically render
        in a jupyter notebook. The Canvas can be saved to file in a
        number of formats using toyplot. The Cartesian axes can be
        used to add additional toyplot marks to the shared cartsian
        coordinates, and be used to style axes ticks. The Mark can
        be further modified to edit or access style args.

        Parameters
        ----------
        tree_style: str
            One of several builtin styles for tree plotting. The
            default is 'n' (normal), others include "c", "d", "o",
            "m", and you can crate your own TreeStyles (see docs).
            TreeStyle sets a base style on top of which other style
            args override.
        ts: str
            A shorter alias name for tree_style.
        height: int
            If None the plot height is autosized. If 'axes' arg is
            used tree is drawn on an existing Axes and this arg is
            ignored. Else it is height of the Canvas in px units.
        width: int
            If None the plot height is autosized. If 'axes' arg is
            used tree is drawn on an existing Axes and this arg is
            ignored. Else it is width of the Canvas in px units.
        axes: Toyplot.coordinates.Cartesian
            A toyplot cartesian axes object. If provided tree is drawn
            on it. If not provided then a new Canvas and Cartesian
            axes are created and returned with the tree plot added to
            it. See documentation for examples of how this option is
            used to create composite drawings combining tree plots
            with other data plots.
        tip_labels: bool or Sequence[str]
            If True tip labels ('name' features on tip nodes) are
            added to the plot; if False no tip labels are added. If a
            list of tip labels is provided it must be the same len as
            ntips and is applied in order to nodes by idx 0-ntips.
        tip_labels_colors: Color or Sequence[Color]
            Any valid toyplot Color or Sequence of Colors to apply to
            tip labels in node idx order.
        tip_labels_style: Dict[str, str]
            A dictionary of CSS style arguments to apply to text
            tip labels. See tree.style for options.
        tip_labels_align: bool
            If True tip names will be aligned and dashed edges will
            drawn to extend from tree edges to the tip names.
        node_mask: bool or Sequence[bool]
            Masks nodes (size, color, shape, label) if True, shows
            nodes if False. An iterable can be entered to selectively
            hide some nodes. The convenience function .get_node_mask()
            can be used to generate mask arrays. Default options
            vary among tree styles, but usually hide tip nodes.
        node_labels: bool, str, or Sequence[str]
            Labels associated with nodes. True shows node idx labels,
            False hides node labels (sets to ""). A string or
            iterable of strings assigns labels to nodes 0-nnodes.
            An iterable of string values can be generated from node
            features using .get_node_data() or .get_node_labels(),
            the latter includes string formatting options.
        node_sizes: int or Sequence[int]
            Size of node markers can be set as an integer or Iterable
            of integers in node order 0-nnodes. Node size 0 is hidden.
            The node_mask argument sets nodes to size 0 when masked,
            and overrides this argument.
        node_colors: str or Sequence[str]
            Color of node markers can be a single color or Iterable
            of colors in node order 0-nnodes. Any valid toyplot color
            (str, rgb array, rgba array, hex, etc) is accepted. See
            the toyplot.color module. The default color palette is
            accessible from toytree.colors. If all nodes will be set
            to the same color it is more efficient to use the
            node_style dictionary (node_style={"fill": 'red'}). If
            used, node_colors overrides 'fill' in node_style.
        node_style: Dict[str, str]
            A dict of valid CSS styles to apply to node markers, such
            as 'fill', 'stroke'. See tree.style for options.
        node_hover: True, False, or Sequence[str]
            Default is True in which case node hover will show the
            node values. If False then no hover is shown. If a list or
            dict is provided (which should be in node order) then the
            values will be shown in order. If a dict then labels can
            be provided as well.
        node_markers: str or Sequence[str]
            The shape of node markers: 'o'=circle, 's'=square. See
            toyplot documentation for all available options:
            https://toyplot.readthedocs.io/en/stable/markers.html
        edge_colors: str or Sequence[str]
            A color or collection of colors nnodes in length to apply
            to edges in node idx order.
        edge_widths: float or Sequence[float]
            A width arg in px units, or collection of widths to apply
            to edges in node idx order.
        edge_type: str
            Edges can be phylogram ('p') or cladogram ('c') type.
        edge_style: Dict[str, Any]
            A dictionary of valid CSS style args to apply to edge
            lines. See tree.style for available options.
        edge_align_style: Dict[str, Any]
            A dictionary of valid CSS style args to apply to aligned
            edge lines. See tree.style for available options.
        use_edge_lengths: bool
            If True edge lengths ('dist' features of TreeNodes) are
            represented in drawings. If False all terminal edges are
            extended to align tips at 0.
        scale_bar: bool
            If True then the axis corresponding to the height of the
            tree will be set to visible and tick marks will be auto-
            generated to span from time=0 to root height. The style
            of the axes can be further modified from the axes object
            after the draw function is called.
        padding: float
            Padding space between the drawing and the visible axes.
            Default is 20px.
        margin:
            ...
        xbaseline: float
            Shift the position of the tree along x-axis.
        ybaseline: float
            Shift the position of the tree along y-axis.
        admixture_edges: Tuple, List[Tuple]
            Admixture edges add colored edges to the plot in the
            style of the 'edge_align_style'. These will be drawn
            from (source, dest, height, width, color). Example:
            [(4, 3, 50000, 3, 'red')].
        fixed_order: Sequence[str]
            An Iterable of tip labels in the order they should be
            plotted. The default is the node names in idx order
            0-ntips. These nodes will be plotted on the coordinates
            0-ntips on either the x or y-axis depending on the
            layout of the tree drawing. This is a convenient argument
            for visualizing discordance of trees.
        fixed_position: Sequence[float]
            The positions on the tip axis where ordered tips should
            be plotted. If None then default positions range(0, ntips)
            are used. By setting explicit positions tips can be
            spaced to better show discordance, or extinct taxa, or
            morphology. The order of positions applies to tips in
            order of the 'fixed_order' arg.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=10)
        >>> tree.draw();
        >>> canvas, axes, mark = tree.draw(ts="o", scale_bar=True);
        >>>
        >>> # save drawing to file.
        >>> import toyplot.svg
        >>> toyplot.svg.render(canvas, "saved-plot.svg")
        """
        return draw_toytree(
            toytree=self,
            tree_style=tree_style,
            axes=axes,
            height=height,
            width=width,
            layout=layout,
            tip_labels=tip_labels,
            tip_labels_colors=tip_labels_colors,
            tip_labels_align=tip_labels_align,
            tip_labels_angles=tip_labels_angles,
            tip_labels_style=tip_labels_style,
            node_mask=node_mask,
            node_labels=node_labels,
            node_labels_style=node_labels_style,
            node_sizes=node_sizes,
            node_hover=node_hover,
            node_style=node_style,
            node_colors=node_colors,
            node_markers=node_markers,
            edge_type=edge_type,
            edge_colors=edge_colors,
            edge_widths=edge_widths,
            edge_style=edge_style,
            edge_align_style=edge_align_style,
            use_edge_lengths=use_edge_lengths,
            scale_bar=scale_bar,
            padding=padding,
            xbaseline=xbaseline,
            ybaseline=ybaseline,
            admixture_edges=admixture_edges,
            shrink=shrink,
            fixed_order=fixed_order,
            fixed_position=fixed_position,
            kwargs=kwargs,
        )



if __name__ == "__main__":

    import toytree
    tree_ = toytree.rtree.unittree(12, treeheight=1232344, seed=123)
    # tree = tree_.mod.edges_slider(0.5)
    # c, a, m = tree_._draw_browser(tree_style='s', layout='d', new=False)
    print(tree_.write(dist_formatter="%.12g"))
    print(tree_.get_node_data())

    # print(tree.get_tip_labels())

    # tree = tree.set_node_data("color", {i: "red" for i in (2,3,4)})
    # print(tree[3].color)
    # print(tree.features)
    # print(tree.get_node_data())
    # print(tree.get_tip_data("height"))
    # print(tree.get_node_mask())
    # print(tree.get_bipartitions(exclude_singleton_splits=False))
    # print(tree._get_bipartitions_table(exclude_singleton_splits=True))
