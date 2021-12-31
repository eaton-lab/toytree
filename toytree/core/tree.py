#!/usr/bin/env python

"""Core ToyTree class object of the toytree package.


References
----------
- ete3
- toytree
"""

from __future__ import annotations
from typing import (
    Sequence, Dict, List, Optional, Iterator, Any,
    Union, Tuple, TypeVar, Callable)
import re
from hashlib import md5

from loguru import logger
import numpy as np
import pandas as pd
from toyplot import Canvas
from toyplot.coordinates import Cartesian

# subpackage object APIs
from toytree.core.style.tree_style import TreeStyle
from toytree.mod._src.api import TreeModAPI
from toytree.distance._src.api import DistanceAPI

from toytree.core.node import Node
from toytree.utils import ToytreeError
from toytree.core.layout import Layout
from toytree.core.drawing.render import ToytreeMark
from toytree.core.drawing.draw_toytree2 import draw_toytree
import toytree
# from toytree.io import write_newick
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
        """: number of Nodes in the tree."""
        self.ntips: int = 0
        """: number of leaf Nodes (tips) in the tree."""
        self.style = TreeStyle()
        """: dict-like class for setting base drawing styles."""
        self._idx_dict: Dict[int, Node] = {}
        """: dict mapping Node idx labels to Node instance."""

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
    def __len__(self) -> int:
        """Return len of Toytree as number of leaf Nodes."""
        return self.ntips

    def __iter__(self) -> Iterator[Node]:
        """ToyTree is iterable, returning leaf Nodes in idx order."""
        return self.treenode._iter_leaves()

    def __getitem__(self, idx: int) -> Node:
        """ToyTree is indexable by idx label to access Nodes."""
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
        tris = [len(j.children) <= 2 for i, j in self._idx_dict.items()]
        if include_root:
            return all(tris)
        return all(tris[:-1])

    def copy(self) -> ToyTree:
        """Return a deepcopy of the ToyTree."""
        return ToyTree(self.treenode.copy())

    #####################################################
    ## TRAVERSAL
    ## Visit all connected Nodes, and/or create idx_dict.
    #####################################################

    def traverse(self, strategy: str = "levelorder") -> Iterator[Node]:
        """Return a Generator over Nodes in a specific traversal order.

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
            nodes in postorder traversal order.
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

    def _update_idxs(self) -> None:
        """Updates the idx labels of all Nodes and `_idx_dict`.

        If a topology has been modified then idx labels must be
        updated. This function is automatically called by all internal
        functions for tree modifications (add_child, root, rotate, etc)
        but not if users modify Nodes adhoc, thus we enforce calling
        it again at the start of drawing/layout functions.
        """
        self.nnodes = 0
        self.ntips = 0
        self._idx_dict = {}
        # iterate idxorder (post-order but tips first)
        for idx, node in enumerate(self.traverse('idxorder')):
            node._idx = idx
            self._idx_dict[node.idx] = node
            self.nnodes += 1

            # get x,y layout for down-facing tree
            if node.is_leaf():
                self.ntips += 1

    def _update_idxs_traversal(self) -> Iterator[Node]:
        """Return a Generator to update idx and yield Nodes in idxorder.

        This does the same as `_update_idxs` but can be used in other
        functions to perform additional operations on each node after
        idx assignment during the same traversal.

        Note
        -----
        Take care that the idx_dict and ntips and nnodes attributes are
        all incomplete during this operation, thus it is hidden for
        internal use only.
        """
        self.nnodes = 0
        self.ntips = 0
        self._idx_dict = {}
        # iterate idxorder (post-order but tips first)
        for idx, node in enumerate(self.traverse('idxorder')):
            node._idx = idx
            self._idx_dict[node.idx] = node
            self.nnodes += 1
            if node.is_leaf():
                self.ntips += 1
            yield node

    def _update(self) -> None:
        """Set idx, x, and y values on Nodes.

        Fetching heights requires two traversals. This is performed
        on init of a ToyTree and any mod or draw functions that occur
        after init simply use and/or modify the existing heights.
        This has a speed tradeoff for init'ing trees (see RawTree),
        but for most concerns is worth it for the convenience.
        """
        # first traversal: parents then children to get dists to root
        max_dist = 0.
        for node in self.traverse("preorder"):
            if node.up:
                node._height = node.dist + node.up._height
            else:
                node._height = 0
            if node.is_leaf():
                max_dist = max(max_dist, node._height)

        # second traversal to update idxs while setting new y values
        for node in self._update_idxs_traversal():
            node._height = max_dist - node._height
            if node.is_leaf():
                node._x = node.idx
            else:
                node._x = np.mean([i._x for i in node.children])

    #####################################################
    ## TREE MODIFICATION FUNCTIONS (ToyTree.mod)
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
        to create a new root).

        Example of rooting an unrooted tree:
                                                    x
                                                   / \
                      _ 2 _        root('n')      n   u
                     |  |  |         -->             / \
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
        self, *query: str, regex: bool = False) -> Iterator[str]:
        """Return Generator of Nodes matched by leaf names."""
        # get matching function
        if regex:
            comp = [re.compile(q) for q in query]
            match = lambda x: any(q.search(x) for q in comp)
        else:
            match = lambda x: x in query

        # yield matching nodes
        for node in self.traverse("idxorder"):
            if match(node.name):
                yield node

    def get_nodes(
        self,
        *query: Query,
        regex: bool = False,
        ) -> Sequence[Node]:
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
        or their common ancestor.

        Parameters
        ----------
        query: str, int, Node, or None
            Flexible query selector can search for Nodes by name, idx
            label, or by entering a Node directly. Multiple values can
            be entered to return a list with all matching Nodes.
        regex: bool
            If True then string queries are treated as regular
            expressions.

        Notes
        -----
        You can `practice your regex here: <https://pythex.org/>`_

        Examples
        --------
        >>> tree = toytree.rtree.unittree(6, seed=123)
        >>> tree.get_nodes()                 # all Nodes are returned.
        >>> tree.get_nodes("r1")                 # [Node(1)]
        >>> tree.get_nodes("r1", "r2")           # [Node(1), Node(2)]
        >>> tree.get_nodes("r[1-2]", regex=True) # [Node(1), Node(2)]
        >>> tree.get_nodes(5, 6)                 # [Node(5), Node(6)]
        >>> tree.get_nodes(tree[5], "r1")        # [Node(5), Node(1)]
        """
        # fastest return, all cached Nodes
        if query == ():
            return list(self._idx_dict.values())

        # next most common, user entered all ints
        nodes = [self[i] for i in query if isinstance(i, int)]
        if len(nodes) != len(query):

            # get more complex query types
            nodes += [self[i.idx] for i in query if isinstance(i, Node)]
            strs = [i for i in query if isinstance(i, str)]
            if strs:
                nodes += list(self._iter_nodes_by_name_match(*strs, regex=regex))

        # NOTE: no longer returning in idx order, user order sometimes wanted.
        return set(nodes)  # sorted(set(nodes), key=lambda x: x.idx)

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
        tips: bool=True,
        internal: bool=False,
        root: bool=False,
        ) -> Sequence[bool]:
        """Return a boolean array to mask certain Nodes when drawing.

        The array is in Node idxorder (from 0-nnodes) where boolean
        True will *mask* Nodes and False will *show* Nodes. Additional
        Nodes can be selected to be unmasked by entering Node int idx
        labels or name strings.

        Parameters
        ----------
        *unmask: int or str
            Additional Nodes selected by int or str labels will be
            unmasked after applying the tips, internal, and root mask.
        tips: bool
            If True all tip Nodes will be masked.
        internal: bool
            If True all internal Nodes will be masked.
        root: bool
            If True the root Node will be masked.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10, seed=123)
        >>> mask = tree.get_node_mask(15, 16, internal=True, root=True)
        >>> tree.draw(ts='s', node_mask=mask);
        """
        arr = np.zeros(self.nnodes, dtype=bool)
        if tips:
            arr[:self.ntips] = 1
        if internal:
            arr[self.ntips:-1] = 1
        if root:
            arr[-1] = 1
        if unmask != ():
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
        nodes = self.get_nodes(*query, regex)
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
        dist_formatter: str = "%.6g",
        internal_labels: Optional[str] = "support",
        internal_labels_formatter: Optional[str] = "%.6g",
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
            A feature to write as internal node labels. The 'support'
            feature is the default, and often used here, but 'name' is
            sometimes used as well. Any feature can be selected, or None
            to not write internal labels.
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
        return self.treenode.get_leaf_names()

    def _get_edges(self) -> np.ndarray:
        """Return numpy array of child,parent relationships."""
        data = np.array(
            [(i.idx, i.up.idx) for _, i in self._idx_dict.items() if i.up])
        return data

    def get_edges(self) -> pd.DataFrame:
        """Return a DataFrame with child -> parent idx labels.

        To return as a numpy array instead of DataFrame you can use
        tree._get_edges().
        """
        return pd.DataFrame(self._get_edges(), columns=["child", "parent"])

    def _iter_bipartitions(
        self,
        feature: str="name",
        tips_only: bool=True,
        ) -> List[List[str],List[str]]:
        """Yield bipartitions in a tree.

        See get_bipartitions for docs. Rooting does not affect result.
        """
        cache = {}
        ridx = self.treenode.idx
        root_nodes = 1 if self.is_rooted() else 0
        all_nodes = range(self.nnodes - root_nodes)
        node_set = set(all_nodes)
        for nidx in all_nodes[:-1]:
            if self[nidx].up:

                # get nodes above and below this edge
                below = {nidx}
                for child in self[nidx].children:
                    below |= cache[child.idx]
                cache[nidx] = below
                other = node_set - below

                # remove ridx, and rm nidx if on same side
                if ridx in below:
                    below.discard(ridx)
                    below.discard(nidx)
                else:
                    other.discard(ridx)

                # limit to the tip Nodes
                if tips_only:
                    below = (i for i in below if i < self.ntips)
                    other = (i for i in other if i < self.ntips)

                # convert to requested type
                below = (getattr(self[i], feature) for i in below)
                other = (getattr(self[i], feature) for i in other)

                # return in a consistent order
                osort = sorted(other)
                bsort = sorted(below)
                if len(osort) == len(bsort):
                    yield sorted((osort, bsort))
                else:
                    yield sorted((osort, bsort), key=len)

    def get_bipartitions(
        self,
        feature: str = "name",
        tips_only: bool = True,
        ) -> pd.DataFrame:
        """Return a DataFrame with partitions in the tree.

        Partitions represent edges that separate sets of Nodes in a
        tree, and can be represented by the tips descended from each
        side of the split, e.g., [['a', 'b'], ['c', 'd']]. Options are
        available to return all Nodes on either side of a partition,
        instead of just the tips, and

        Partitions are usually used to find tip names present on either
        side of a split. For *some* use cases, it may be useful to find
        other features, such as idx labels, on either side of each
        split, and even to get internal Node labels, which can be
        toggled with options to this function.

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
        tips_only: bool
            If True (default) only tip Node features are returned.

        See Also
        --------
        `ToyTree._iter_bipartitions`, `ToyTree._get_bipartitions_table`

        Examples
        --------
        >>> tree = toytree.rtree.unittree(4)
        >>> print(tree.get_bipartitions())
        >>> print(tree.get_bipartitions(feature="idx", tips_only=False))
        """
        return pd.DataFrame(self._iter_bipartitions(feature, tips_only))

    def _get_bipartitions_table(
        self, tips_only: bool=True, dtype: type=int) -> np.ndarray:
        """Return a DataFrame with partitions in binary format."""
        bits = list(self._iter_bipartitions("idx", tips_only=tips_only))
        arr = np.zeros(
            shape=(len(bits), self.ntips if tips_only else self.nnodes - 1),
            dtype=dtype,
        )
        for idx, bit in enumerate(bits):
            arr[idx, bit[0]] = 1
        return arr

    def get_topology_id(self, feature="name") -> str:
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
            you plan to compare using topology id strings.

        Examples
        --------
        >>> tree.get_topology_id() # '70f5cfb041f176d86020971ac5f633e1'
        """
        bi_list = list(self._iter_bipartitions(feature=feature))
        return md5(str(sorted(bi_list)).encode('utf-8')).hexdigest()

    ###################################################
    ## COORDINATE LAYOUT FUNCTIONS
    ## push to .layout subpackage
    ###################################################

    def _get_node_coordinates(self) -> np.ndarray:
        """Return numpy array of 'unstyled' cached node coordinates."""
        return np.array(
            [(i._x, i._height) for _, i in self._idx_dict.items()])

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
        data = pd.DataFrame(
            columns=('x', 'y'),
            index=range(self.nnodes),
            data=Layout(self, **kwargs).coords,
        )
        return data

    def get_tip_coordinates(self, **kwargs) -> pd.DataFrame:
        """Return a DataFrame with xy coordinates for tip nodes.

        See `ToyTree.get_node_coordinates` for details.
        """
        return self.get_node_coordinates(**kwargs).iloc[self.ntips]

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

        # make a copy of ToyTree to return
        tree = self if inplace else self.copy()

        # ensure mapping is proper type
        if not isinstance(mapping, dict):
            if not mapping:
                mapping = {}
            else:
                raise TypeError("'mapping' arg should be a dict or None")

        # convert fuzzy selectors to Node objects
        # for key, value in mapping:
        # nodes = tree.get_nodes(*mapping.keys(), regex=False)
        # mapping = dict(zip(nodes, mapping.values()))

        # make a dict {Node: newvalue} by expanding the entered mapping
        ndict = {}
        for key, value in mapping.items():

            # get node matching the key query int or str
            for node in tree.get_nodes(key, regex=False):

                # map selected Node to value.
                ndict[node] = value

                # optionally map Node's descendants to value as well.
                if inherit:
                    for desc in tree[node.idx]._iter_descendants():
                        ndict[desc] = value

        # map {Node: default} for Nodes not in ndict
        if default is not None:
            for idx in range(tree.nnodes):
                node = tree[idx]
                if node not in ndict:
                    ndict[node] = default

        # special mod submodule method for height modifications
        if feature == "height":
            height_map = {i.idx: j for (i, j) in ndict.items() if j is not None}
            return tree.mod.edges_set_node_heights(height_map)

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
        """Return a DataFrame with values for one or more selected
        features from every node in the tree.

        Parameters
        ----------
        feature: str, Iterable[str], or None
            One or more features of Nodes to get data for.
        missing: Any, Iterable[Any], or None
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
        format, but is slower than accessing data directly from Nodes,
        for example during a traversal, because it spends time checking
        for Nodes with missing data, and type-checks missing values.
        """
        # select one or more features to fetch values for
        if feature is None:
            features = self.features
        elif isinstance(feature, (list, tuple)):
            features = feature
        else:
            features = [feature]

        # check for bad user features
        for feat in features:
            if feat not in self.features:
                raise ValueError(f"feature '{feature}' not in tree.features.")

        # init a dataframe for all selected features
        data = pd.DataFrame(
            index=range(self.nnodes),
            columns=features,
        )

        # get remaining features
        for feat in features:
            for nidx in range(self.nnodes):
                data.loc[nidx, feat] = getattr(self[nidx], feat, pd.NA)

            # fill in appropriate missing data value for each Series
            if missing is not None:
                data[feat] = data[feat].where(data[feat].notnull(), missing)
            else:
                if data[feat].dtype == "O":
                    data[feat] = data[feat].where(data[feat].notnull(), "")
                else:
                    data[feat] = data[feat].where(data[feat].notnull(), pd.NA)

        # if a single feature was selected return as a Series else DataFrame
        if len(features) == 1:
            return data[feature]
        return data

    def get_tip_data(
        self,
        feature: Union[str, Sequence[str], None] = None,
        missing: Optional[Any] = pd.NA,
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
    def _draw_browser(self, **kwargs):
        """Open and display tree drawing in default web browser.

        TODO: overload toyplot function, option to reuse same tab,
        add div styling, etc.
        Or, maybe make this at toytree level as `toytree.draw(canvas)`
        also make a `toytree.save()` shortcut to saving in formats.
        """
        import toyplot.browser
        canvas, axes, mark = self.draw(**kwargs)
        toyplot.browser.show([canvas])
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
    tree = toytree.rtree.unittree(10, seed=123)
    print(tree.get_tip_labels())

    tree = tree.set_node_data("color", {i: "red" for i in (2,3,4)})
    print(tree[3].color)
    print(tree.features)
    print(tree.get_node_data())
    print(tree.get_tip_data("height"))
    print(tree.get_node_mask())
