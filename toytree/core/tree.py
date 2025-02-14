#!/usr/bin/env python

"""Core ToyTree class object of the toytree package.

Examples
--------
>>> tree = toytree.rtree.unitree(10)
>>> tree = toytree.ToyTree(toytree.Node('a'))
>>> tree = toytree.tree("((a,b),c);")

"""

from __future__ import annotations
from typing import (
    Sequence, Dict, List, Optional, Iterator, Any, Union, Tuple,
    TypeVar, Set,  # Callable,
)
import re
from pathlib import Path
from copy import deepcopy
from hashlib import md5
# from collections.abc import Sequence as SequenceType

from loguru import logger
import numpy as np
from toyplot import Canvas
from toyplot.coordinates import Cartesian

# subpackage object APIs
from toytree.core.apis import (
    TreeModAPI, TreeDistanceAPI, TreeEnumAPI, PhyloCompAPI, AnnotationAPI)
from toytree.core.node import Node
from toytree.style import TreeStyle
from toytree.drawing import draw_toytree, ToyTreeMark
from toytree.utils.src.exceptions import (
    ToytreeError, NODE_NOT_IN_TREE_ERROR, NODE_INDEXING_ERROR)
import toytree
# from toytree.io.src.writer import write_newick

# toytree logger
logger = logger.bind(name="toytree")

# Type alias for Node selection
Query = TypeVar("Query", str, int, Node)
Color = TypeVar("Color", str, np.ndarray, tuple)  # toyplot.ColorMap, ...
UNPACKING_MSG = """\
Use unpacking on collections:
>>> query_list = [0, 1, 2]
>>> tree.method(*query_list, ...)"""


class ToyTree:
    """ToyTree class for manipulating and drawing trees.

    ToyTrees should generally be created using a constructor function
    such as `toytree.tree` or `toytree.rtree`, to init a tree from
    input data (e.g. newick) or random generators, respectively. This
    class can be used for type checking.

    Parameters
    ----------
    treenode: Node
        A toytree.Node class instance representing the tree root.

    Attributes
    ----------
    nnodes: int
        Number of Nodes in the tree.
    ntips: int
        Number of leaf Nodes (tips) in the tree. Updated on modification.
    features:
        The features names assigned to Nodes. A dynamic property.
    edge_features
        Set of feature names applying to edges, not nodes.
    style: TreeStyle
        Mutable dataclass with base drawing style.
    mod: TreeModAPI
        API to apply methods from `toytree.mod` to this tree.
    enum: TreeEnumAPI
        API to apply methods from `toytree.enum` to this tree.
    distance: TreeDistanceAPI
        API to apply methods from `toytree.distance` to this tree.
    pcm: PhyloCompAPI
        API to apply methods from `toytree.pcm` to this tree.
    annotate: AnnotationAPI
        API to apply methods from `toytree.annotate` to this tree.

    Examples
    --------
    >>> tree = toytree.tree("((a,b),c);")
    >>> isinstance(tree, toytree.ToyTree)
    >>> # True
    """
    def __init__(self, treenode: Node) -> ToyTree:
        """Initialize a ToyTree from a Node instance."""

        self.treenode = treenode
        self.nnodes: int = 0
        self.ntips: int = 0
        self.style = TreeStyle()
        self.edge_features: Set = set(("dist", "support"))
        self._idx_dict: Dict[int, Node] = {}
        """Private dict mapping Node idx labels to Node instances."""

        # toytree subpackage library API (mod, pcm, distance, layout)"""
        self.mod = TreeModAPI(self)
        self.distance = TreeDistanceAPI(self)
        self.pcm = PhyloCompAPI(self)
        self.enum = TreeEnumAPI(self)
        self.annotate = AnnotationAPI(self)

        # update Node idxs, _idx_dict, nnodes, ntips, and Node heights
        self._update()

    #####################################################
    # DUNDERS
    #####################################################
    # def __len__(self) -> int:
        # """Ambiguous, does one expect ntips or nnodes? So it is
        # not supported. See .ntips and .nnodes attrs."""
        # return self.ntips

    def __iter__(self) -> Iterator[Node]:
        """ToyTree is iterable, returning Nodes in idx order."""
        return (self[i] for i in range(self.nnodes))

    # def __getitem__(self, idx: int) -> Node:
    #     """Nodes can be accessed by indexing or slicing by idx label"""
    #     # allow indexing by int, e.g., [3]
    #     try:
    #         return self._idx_dict[idx]
    #     except Exception:
    #         pass
    #     # allow slicing by ints, e.g., [3:10:2]
    #     try:
    #         return [self._idx_dict[idx] for idx in range(*idx.indices(self.nnodes))]
    #     except Exception:
    #         pass
    #     # allow indexing by a Sequence, e.g., [3, 10, 2, 4]
    #     try:
    #         return [self._idx_dict[i] for i in idx]
    #     except Exception:
    #         pass
    #     # if a negative number then get positive and reindex
    #     try:
    #         if isinstance(idx, int) and idx < 0:
    #             return self._idx_dict[self.nnodes + idx]  # idx is negative
    #     # raise a helpful error message.
    #     except Exception as exc:
    #         raise ToytreeError(NODE_INDEXING_ERROR) from exc

    def __getitem__(self, idx: int) -> Node:
        """Nodes can be accessed by indexing or slicing by idx label"""
        # allow indexing by int, e.g., [3]
        try:
            # try casting to int, to support int, np.int64, np.int32, etc
            # if isinstance(idx, int):
            try:
                idx = int(idx)
                if idx >= 0:
                    return self._idx_dict[idx]
                else:
                    return self._idx_dict[self.nnodes + idx]  # idx is negative
            except (ValueError, TypeError):
                pass

            # allow indexing by a Sequence, e.g., [3, 10, 2, 4]
            if isinstance(idx, (list, np.ndarray)):
                return [self._idx_dict[i] for i in idx]

            # allow slicing by ints, e.g., [3:10:2]
            else:
                if hasattr(idx, "indices"):
                    return [self._idx_dict[idx] for idx in range(*idx.indices(self.nnodes))]
                raise ToytreeError("invalid indexing type.")

        # raise a helpful error message.
        except Exception as exc:
            raise ToytreeError(NODE_INDEXING_ERROR) from exc

    def __repr__(self) -> str:
        """Short object representation for toytree.core.tree.ToyTree"""
        return f"<toytree.ToyTree at {hex(id(self))}>"

    # def __str__(self) -> str:
    #     """Return ascii representation of tree."""
    #     return "\n".join(self.treenode._get_ascii()[0])

    @property
    def nedges(self) -> int:
        """Return the number of edges in the tree, *not including the
        root edge if the tree is rooted*.

                        |  <- (not counted)
                       _T_
                     _|_  |                  ___T_
                    |   | |                 |  |  |
                    A   B C                 A  B  C
              (rooted w/ 4 edges)      (unrooted with 3 edges)

        Note
        ----
        This value is not cached and requires an iteration of the tree
        in order to accommodate counting edges of unresolved nodes.
        For super speed-sensitive operations use nnodes-1 if tree is
        bifurcating, else measure the value once and cache it if the
        tree doesn't change.

        See Also
        --------
        `ToyTree.iter_edges`
            Generator of edges as child-parent Node pairs. Has the
            option `include_root` to toggle counting of root split.

        Example
        -------
        >>> tree = toytree.rtree.unittree(5, seed=123)
        >>> tree.nedges == sum(1 for i in tree.iter_edges())
        >>> # True
        """
        internal = sum(1 for i in self.enum.iter_edges())
        return internal
        # to add counting of the root edge of rooted trees do this.
        # return internal + (1 if self.is_rooted() else 0)

    #####################################################
    # FEATURES
    #####################################################

    @property
    def features(self) -> Tuple[str]:
        """Return a tuple of all Node data feature names.

        The basic features present on all Nodes include 'dist',
        'name', 'support', 'height', and 'idx'. These features will
        all be shown if you call `ToyTree.get_node_data()`. To add
        additional features to use `ToyTree.set_node_data`, or add as
        attributes to Node objects. If features apply to edges instead
        of Nodes (e.g., dist, support) they are also listed in
        ToyTree.edge_features.

        Notes:
        This function finds node features dynamically by visiting every
        Node in the tree. It is thus not performant for speed sensitive
        code.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10)
        >>> # set 'color' feature on a single Node.
        >>> tree[5].color = 'red'
        >>> # get 'color' values for all Nodes.
        >>> tree.get_node_data("color", missing="blue")
        """
        feats = set()
        for node in self:
            feats.update(node.__dict__)
        feats = (i for i in feats if not i.startswith("_"))
        defaults = ("idx", "name", "height", "dist", "support")
        return defaults + tuple(sorted(feats))

    def remove_features(self, *feature: str, inplace: bool = False) -> ToyTree:
        """Remove one or more non-default data features from all Nodes.

        This function is very rarely needed. Note that you cannot
        remove default features "idx", "name", "height", "dist", or
        "support".

        Examples
        --------
        >>> tree = tree.set_node_data("new_feature", {0: 10})
        >>> tree = tree.remove_features("new_feature")
        """
        tree = self if inplace else self.copy()
        for feat in feature:
            if feat in ("idx", "name", "height", "dist", "support"):
                raise toytree.utils.NodeDataError(
                    f"Cannot remove required Node feature: {feature}")
            for node in tree.traverse():
                delattr(node, feat)
        return tree

    #####################################################
    # IDENTITY
    #####################################################

    def is_rooted(self) -> bool:
        """Return False if the tree is unrooted."""
        if len(self.treenode.children) > 2:
            return False
        return True

    def is_bifurcating(self, include_root: bool = True) -> bool:
        """Return False if no polytomies exist in tree.

        Parameters
        ----------
        include_root: bool
            If False then the state of the root node is ignored when
            checking for polytomies.
        """
        tris = [len(node.children) <= 2 for node in self]
        if include_root:
            return all(tris)
        return all(tris[:-1])

    def copy(self) -> ToyTree:
        """Return a deepcopy of the ToyTree."""
        return deepcopy(self)
        # return ToyTree(self.treenode.copy())

    #####################################################
    # TRAVERSAL
    # Visit all connected Nodes, and/or create ._idx_dict cache.
    #####################################################

    def traverse(self, strategy: str = "levelorder") -> Iterator[Node]:
        """Return an iterator over Nodes in a specific traversal order.

        Traversal strategies: admonition
        idxorder:
            Leaf nodes are visited first from left to right, followed
            by internal nodes in postorder traversal. Note: this
            traversal order is already cached on any ToyTree and can
            thus be accessed much faster by indexing.
        preorder:
            Parents are visited before children. Traverses all the way
            down each left subtree before proceeding to right child.
        postorder:
            Children are visited before parents. The left subtree is
            visited, then right, then the parent.
        levelorder:
            Nodes the same distance (number of edges) from root are
            visited left to right, before descending to next level.
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
        Generate tree drawings enumerating each traversal strategy
        >>> tree = toytree.rtree.unittree(10, seed=123)
        >>> ords = ['postorder', 'preorder', 'levelorder', 'idxorder']
        >>> for trav in ords:
        >>>     for idx, node in enumerate(tree.traverse(trav)):
        >>>         node.traverse_order = str(idx)
        >>>     _, a, _ = tree.draw(
        >>>         node_labels="traverse_order",
        >>>         node_sizes=16, node_mask=False);
        >>>     a.label.text = trav
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
        depths = {self.treenode: 0.}

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
            depths[node] = depths[node._up] + node._dist

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
    # TREE MODIFICATION FUNCTIONS (See ToyTree.mod)
    # - root, unroot, rotate_node, ladderize,
    # - set_node_heights, collapse_nodes, prune,
    # - drop_tips, resolve_polytomy,
    # - root, unroot
    #####################################################

    #################################################
    # NODES SEARCH/MATCH BY FLEXIBLE INPUTS
    # Matching Nodes by name can be used to color nodes/edges...
    #################################################

    def _iter_nodes_by_name_match(self, *query: str) -> Iterator[Node]:
        """Return Iterator over Nodes in idxorder matched by leaf names
        while allowing for regular expression matched of names.
        """
        # compile regex strings
        comps = []
        for que in query:
            if not que.startswith("~"):
                comps.append((que, None))
            else:
                try:
                    comps.append((que, re.compile(que[1:])))
                except re.error as exc:
                    msg = f"invalid regex query {query} raised re.error:\n{exc}"
                    logger.error(msg)
                    raise ToytreeError(msg) from exc

        # traverse tree in idxorder checking each Node for a name match
        matched = set()
        for node in self:
            for que, regex in comps:
                if regex:
                    # match() is faster but search() is more flexible...
                    # if regex.match(node.name):
                    if regex.search(node.name):
                        matched.add(que)
                        yield node
                else:
                    if que == node.name:
                        yield node
                        matched.add(que)

        # raise exception for non-matched queries
        not_matched = set(query) - set(matched)
        if not_matched:
            msg = f"No Node names match query: {not_matched}"
            logger.error(msg)
            raise ValueError(msg)

    def get_nodes(self, *query: Query) -> List[Node]:
        """Return a list of Nodes matching a flexible Query.

        One or more Node instances are returned that match one ore more
        Node Queries. A Node Query can be an int, str, or Node type,
        and is matched depending on the type. Nodes are simply returned,
        int matches to Node idx labels, and str matches to Node name
        features. A str prefixed by `~` can match multiple Node names
        as a regular expression search. (e.g., `~r[0-3]`) matches will
        match ["r0", "r1", "r2", "r3"]. If no query is entered then
        all Nodes are returned.

        You can [practice your regex here](https://pythex.org/).
        The order in which Nodes are returned may be different than the
        order of queries.

        This function is used inside many other `toytree` functions that
        accept `Query` as an argument.

        Parameters
        ----------
        query: str, int, Node, or None
            Flexible query selector can search for Nodes by name, idx
            label, or by entering a Node directly. Multiple values can
            be entered to return a list of matching Nodes.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(16, seed=123)
        >>> tree.get_nodes()                    # all Nodes returned
        >>> tree.get_nodes("r1")                # [Node(1)]
        >>> tree.get_nodes("r1", "r2")          # [Node(1), Node(2)]
        >>> tree.get_nodes("~r[1-2]$")          # [Node(1), Node(2)]
        >>> tree.get_nodes(5, 6)                # [Node(5), Node(6)]
        >>> tree.get_nodes(tree[5], "r1")       # [Node(5), Node(1)]
        >>> tree.get_nodes(*[2,3])              # [Node(2), Node(3)]
        """
        nodes = set()
        names = set()
        for que in query:
            if isinstance(que, int):
                nodes.add(self[que])
            elif isinstance(que, Node):
                if que not in self:
                    raise ValueError(NODE_NOT_IN_TREE_ERROR)
                nodes.add(que)
            elif isinstance(que, str):
                names.add(que)  # names are expanded to Nodes below.
            elif isinstance(que, np.integer):
                nodes.add(self[que])
            else:
                msg = f"query type {type(que)} not supported. "
                if isinstance(que, (list, tuple)):
                    msg += UNPACKING_MSG
                logger.error(msg)
                raise TypeError(msg)

        # match Node names as a group so we only need to perform one
        # tree traversal. Each query can return multiple regex hits.
        matched = set(self._iter_nodes_by_name_match(*names))
        nodes.update(matched)

        # if not query then return all Nodes
        if not nodes:
            return list(self)
        return list(nodes)

    def get_mrca_node(self, *query: Query) -> Node:
        """Return the MRCA Node from Nodes matching a flexible query.

        Find and return the most-recent-common-ancestor Node instance
        based on input selectors that can be either Node names, Node
        int idx labels, or Node objects. Input types are detected
        automatically and handled, so that even mixed input types can
        be entered (e.g., `get_mrca_node('a', 2, 3)`). If the selected
        Nodes do not share a common ancestor this will raise a
        ToytreeError. This function is useful for selecting and
        annotating clades on a tree drawing. Node names can also be
        entered as regular expressions to match multiple names by
        prefixing the name with "~" (e.g., .get_mrca_node("~r[0-3]$"))

        Parameters
        ----------
        *query: str, int, Node
            One or more Node objects, Node str names, or Node int idx
            labels, any of which can be used to select Nodes.

        Notes
        -----
        If the tree is unrooted then the mrca will be found relative
        to the 'pseudo-root' (the Node that exists as parent to the
        basal trichotomy, but has no parent associated with it).

        Examples
        --------
        >>> tree = toytree.rtree.unittree(12)
        >>> mrca = tree.get_mrca_node('r1', 'r2', 'r3')
        >>> mrca = tree.get_mrca_node('r[1-3]$')
        >>> mrca = tree.get_mrca_node(12)
        >>> mrca = tree.get_mrca_node(12, 13, 14, 15)
        >>> mrca = tree.get_mrca_node(*(tree[i] for i in (12, 13)))
        >>> print(mrca.idx, mrca.get_descendants())
        """
        # get flexible input as Node instances
        nodes = self.get_nodes(*query)
        if len(nodes) == 1:
            return nodes[0]
        # include_self necessary to find ancestor between tip ^ parent
        nset = set.intersection(*(
            set(i.iter_ancestors(include_self=True)) for i in nodes)
        )
        return min(nset)

    def get_ancestors(
        self,
        *query: Query,
        include_query: bool = True,
        include_top: bool = True,
        stop_at_mrca: bool = False,
    ) -> List[Node]:
        """Return a set of Nodes that are ancestors of the query samples.

        The returned set can include or exclude the sample query; it
        can trace back all ancestors to the root of the tree, or only
        to the MRCA of the sample query; and it can include or exclude
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

        Note
        ----
        See also `Node.get_ancestors` which will fetch the ancestors of
        an individual Node. By contrast, this function returns the set
        of Nodes ancestral to a group of one or more queried Nodes,
        and has additional start,stop criteria arguments. To get a
        single Node's ancestors this method is slightly slower, but is
        faster for finding shared ancestors.

        Examples
        --------
        >>> Draw a tree and color ancestors of Nodes 1, 2, 3
        >>> tree = toytree.rtree.unittree(ntips=8, seed=123)
        >>> ancs = tree.get_ancestors(1,2,3)
        >>> tree.set_node_data("path", {i: 1 for i in ancs}, inplace=True)
        >>> tree.draw(ts='p', node_colors=("path", "Set2"));
        """
        # expand query into a set of Nodes
        query = set(self.get_nodes(*query))

        # get union of the ancestors of each query Node, not including the Node
        ancestors = set.union(*[set(i.get_ancestors()) for i in query])

        # optionally include query nodes in ancestor set.
        if include_query:
            ancestors.update(query)

        # stopping criterion (global root or sample mrca)
        if stop_at_mrca:
            mrca = self.get_mrca_node(*query)
            ancestors = {i for i in ancestors if i._idx <= mrca._idx}
            if not include_top:
                ancestors.discard(mrca)
        else:
            if not include_top:
                ancestors.discard(self.treenode)
        return ancestors

    def get_node_mask(
        self,
        *unmask: Query,
        show_tips: bool = False,
        show_internal: bool = False,
        show_root: bool = False,
    ) -> np.ndarray:
        """Return a boolean array masking all Nodes except selected.

        Creates a boolean mask to hide a set of selected Nodes.
        The array is in Node idxorder (from 0-nnodes) where boolean
        True will *mask* Nodes, and False will *show* Nodes. Additional
        Nodes can be selected to be *unmasked* by entering Node int idx
        labels or name strings. The default mask is an array that
        masks tip Nodes but unmasks all internal Nodes.

        Parameters
        ----------
        *unmask: int, str or Node
            Select Nodes using a Query (int or str labels, including
            regular expressions) that will be unmasked (shown).
        show_tips: bool
            If True all tip Nodes will be masked.
        show_internal: bool
            If True all internal Nodes will be masked.
        show_root: bool
            If True the root Node will be masked.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10, seed=123)
        >>> # create a mask that only shows tips & Nodes 15 and 16
        >>> mask = tree.get_node_mask(15, 16, show_tips=True)
        >>> tree.draw(ts='s', node_mask=mask);
        """
        # default is all False (mask all)
        arr = np.zeros(self.nnodes, dtype=np.bool_)
        if show_tips:
            arr[:self.ntips] = True
        if show_internal:
            arr[self.ntips:-1] = True
        if show_root:
            arr[-1] = True
        # check unmask this way because 0 matches a Node.
        if unmask != ():
            # supports regex expansion
            for node in self.get_nodes(*unmask):
                arr[node.idx] = True
        return arr

    def is_monophyletic(self, *query: Query) -> bool:
        """Return True if leaf Nodes form a monophyletic clade.

        If any other leaf Nodes are members of this clade, but not
        included in the input set of 'nodes', then these Nodes are
        not monophyletic. Nodes can be entered either as Node objects
        or by their int idx labels.

        Parameters
        ----------
        *query: Node, str, or int
            One or more Node objects, Node name str, or Node idx int
            labels to check for monophyly. If None then all Nodes are
            used as the query (returns True).

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=10, seed=123)
        >>> tree.draw()
        >>> print(tree.is_monophyletic(0, 1, 2))
        >>> print(tree.is_monophyletic(0, 4, 8))
        """
        if not self.is_rooted():
            raise ToytreeError("The tree must be rooted to test monophyly")
        nodes = self.get_nodes(*query)
        mrca = self.get_mrca_node(*nodes)
        for node in mrca.iter_leaves():
            if node not in nodes:
                return False
        return True

    ##################################################
    # TREE DISTANCE (ToyTree.distance)
    # get distances between nodes, trees, or data points
    ##################################################

    ###################################################
    # I/O FORMATTING (toytree.io)
    # read and write trees to newick, nexus, nhx
    ###################################################

    ###################################################
    # TOPOLOGY OR LEAF ANALYSIS FUNCTIONS
    # access nodes or features ...
    ###################################################
    def iter_tip_labels(self) -> Iterator[str]:
        """Generator of tip labels in idx order."""
        for node in self[:self.ntips]:
            yield node._name

    def get_tip_labels(self) -> List[str]:
        """Return a list of tip labels in Node idx order."""
        return list(self.iter_tip_labels())

    ###################################################
    # TOPOLOGY ENUMERATION
    # access info about splits, bipartitions, quartets, etc.
    # from toytree.enum subpackage:
    # - iter_edges
    # - iter_bipartitions
    # - iter_quartets
    ###################################################

    def get_topology_id(self, feature="name", include_root: bool = False) -> str:
        """Return a unique ID representing this topology.

        Two trees with the same topology and tip names will produce
        the same id, i.e., the rotation of Nodes does not affect the
        generated ID. Rooting/Unrooting does affect it. The ID string
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
        include_root: bool
            By default the root Node is excluded (if tree is rooted)
            such that all unrooted trees with the same toplogy return
            the same topology_id. To distinguish among differently
            rooted versions of the same tree set `include_root=True`.

        Examples
        --------
        >>> tree.get_topology_id() # '70f5cfb041f176d86020971ac5f633e1'

        See Also
        --------
        - iter_bipartitions
        """
        # bipartitions are ordered by edge idx order, and names within
        # bipartitions are consistently ordered by alphanumeric names.
        # so we sort so that trees with the same topology but rotated
        # nodes will have the same bipartitions.
        biparts = sorted(self.iter_bipartitions(
            feature=feature, sort=True, type=tuple))

        # optional: duplicate last bipart to indicate rooting
        if include_root and self.is_rooted():
            biparts += [
                tuple(sorted(
                    sorted(i.get_leaf_names()) for i in self.treenode.children
                ))
            ]
        return md5(str(biparts).encode('utf-8')).hexdigest()

    ###################################################
    # COORDINATE LAYOUT FUNCTIONS
    # push to .layout subpackage
    ###################################################

    def _iter_node_coordinates(self) -> Iterator[Tuple[float, float]]:
        """Generator of 'unstyled' cached node coordinates."""
        for node in self:
            yield node._x, node._height

    # def get_node_coordinates(self, **kwargs) -> pd.DataFrame:
    #     """Return a DataFrame with xy coordinates for plotting nodes.

    #     This returns coordinates that could be used when adding
    #     additional annotations to plots, such as scatterplot points,
    #     or error bars on top of nodes. By default Node idx=0 will be
    #     located at coordinate position (0, 0), which can be modified
    #     using the `xbaseline` and `ybaseline` args.

    #     Take care when calling this function that the coordinates
    #     will be different depending on the *style* arguments applied.
    #     The style args come from the `.style` dict-like object of the
    #     ToyTree, and can be overriden by additional args to this func,
    #     the same as in the `.draw()` function. For example, layout
    #     facing down ('d') will yield different coordinates than layout
    #     facing up ('u').

    #     Examples
    #     --------
    #     >>> style = {'layout': 'd', 'xbaseline': 10}
    #     >>> canvas, axes, mark = tree.draw(**style)
    #     >>> node_coords = tree.get_node_coordinates(**style)
    #     >>> axes.scatterplot(coords.x, coords.y, size=10);
    #     """
    #     style = get_tree_style_base(self, **kwargs)
    #     style = validate_style(self, style, **kwargs)
    #     coords = get_layout(self, style).coords
    #     data = pd.DataFrame(
    #         columns=('x', 'y'),
    #         index=range(self.nnodes),
    #         data=coords,
    #     )
    #     return data

    # def get_tip_coordinates(self, **kwargs) -> pd.DataFrame:
    #     """Return a DataFrame with xy coordinates for tip nodes.

    #     See `ToyTree.get_node_coordinates` for details.
    #     """
    #     return self.get_node_coordinates(**kwargs).iloc[:self.ntips]

    ###################################################
    # FULL TREE DATA GET/SET
    # functions to modify features of all connected Nodes
    # see source in toytree/data/
    # - set_node_data
    # - set_node_data_from_dataframe
    # - get_node_data
    # - get_tip_data
    ###################################################

    def get_feature_dict(self, keys: str = None, values: str = None) -> Dict[str, Any]:
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

    ###################################################
    # DRAWING
    ###################################################

    # ------------------------------------------------------------------
    # Draw functions imported, but docstring here...
    # ------------------------------------------------------------------
    def _draw_browser(self, *args, new: bool = False, tmpdir: Path = None, **kwargs):
        """Open and display tree drawing in default web browser.

        TODO: overload toyplot function, option to reuse same tab,
        add div styling, etc.
        Or, maybe make this at toytree level as `toytree.draw(canvas)`
        also make a `toytree.save()` shortcut to saving in formats.
        """
        # import toyplot.browser
        canvas, axes, mark = self.draw(**kwargs)
        toytree.utils.show([canvas], new=new, tmpdir=tmpdir)
        return canvas, axes, mark

    def draw(
        self,
        tree_style: Optional[str] = None,
        height: int = None,
        width: int = None,
        axes: Cartesian = None,
        layout: str = None,
        tip_labels: Union[bool, Sequence] = None,
        tip_labels_colors: Union[Color, Sequence[Color]] = None,
        tip_labels_angles: Union[float, Sequence[float]] = None,
        tip_labels_style: Dict[str, Any] = None,
        tip_labels_align: bool = None,
        node_mask: Union[bool, Sequence[bool]] = None,
        node_labels: Union[bool, Sequence[str]] = None,
        node_labels_style: Dict[str, Any] = None,
        node_sizes: Union[int, Sequence[int]] = None,
        node_colors: Union[str, Sequence[str]] = None,
        node_style: Dict[str, Any] = None,
        node_hover: bool = None,
        node_markers: Sequence[str] = None,
        node_as_edge_data: bool = False,
        edge_colors: Union[str, Sequence[str]] = None,
        edge_widths: float = None,
        edge_type: str = None,
        edge_style: Dict[str, Any] = None,
        edge_align_style: Dict[str, Any] = None,
        edge_markers: Sequence[str] = None,
        edge_labels: Union[bool, Sequence[str]] = None,
        use_edge_lengths: bool = None,
        scale_bar: bool = None,
        padding: float = None,
        xbaseline: float = None,
        ybaseline: float = None,
        admixture_edges: List[Tuple[int, int]] = None,
        shrink: float = None,
        fixed_order: Sequence[str] = None,
        fixed_position: Sequence[float] = None,
        label: Optional[str] = None,
        **kwargs,
    ) -> Tuple[Canvas, Cartesian, ToyTreeMark]:
        """Return a drawing of the tree as a Toyplot figure.

        Drawings are returned as Tuple[Canvas, Cartesian, ToytreeMark]
        following the style of the toyplot plotting library and will
        render as html figures automatically in jupyter notebook.
        The Canvas can be saved to file in a number of formats using
        toyplot. The Cartesian axes object can be used to position
        multiple Marks onto the same cartesian coordinates, and to
        style axes ticks and labels (see docs). The Mark object can
        be further modified to edit or access style args.

        Parameters
        ----------
        tree_style: str or None
            Select a builtin base TreeStyle on top of which to add other
            style modifications. Options include "n", "c", "p", "o",
            "r", "m", "d"; you can alo create your own (see docs).
            Using a tree_style overrides any `ToyTree.style` dict.
        ts: str or None
            A shorter alias that can be used for `tree_style`.
        height: int or None
            If None the plot height is auto-sized. If 'axes' arg is
            used tree is drawn on an existing Axes and this arg is
            ignored. Else, this sets height of the Canvas in px units.
        width: int
            If None the plot width is auto-sized. If 'axes' arg is
            used tree is drawn on an existing Axes and this arg is
            ignored. Else, this sets width of the Canvas in px units.
        axes: toyplot.coordinates.Cartesian
            A toyplot Cartesian axes object. If provided, tree is drawn
            on it. If not provided then a new Canvas and Cartesian
            axes are created and returned with the tree Mark added to
            it. See documentation for details on how this option is
            used to create composite drawings combining tree plots
            with other data plots (e.g., scatterplots, barplots).
        layout: str or None
            Layout defines the direction parent-child relationships are
            drawn. Options are 'r' 'l', 'u', 'd' for 'right', 'left',
            'up', or 'down' respectively. 'c' draws circular trees from
            angle 0-360 degrees, or cX-Y draws circular trees on an arc
            from X degrees to Y degrees. Finally, any other entry, such
            as None, draws an 'unrooted' layout. Default='r'.
        tip_labels: bool or Sequence[str]
            If True, tip labels ('name' features on tip Nodes) are
            added to the plot; if False, no tip labels are added. If a
            list of tip labels is provided it must be the same len as
            ntips and is applied in Node idx order (0-ntips).
        tip_labels_colors: Color or Sequence[Color] or (feature, colormap)
            A valid toyplot Color, Sequence[Color] of len=ntips, or
            tuple of (feature, colormap) to map colors to tip labels.
        tip_labels_style: Dict[str, str]
            A dictionary of CSS style arguments to apply to text
            tip labels. See tree.style for options.
        tip_labels_angles: int, Sequence[int], or None
            None will set angles based on layout method.
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
        node_as_edge_data: bool
            If True then node_markers and node_labels are instead
            plotted as edge_markers and edge_labels. For more fine
            control see `toytree.annotate`.
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
            Padding space between the drawing and the visible axes. This
            is a setting of the Cartesian axes and can be modified more
            after plotting. Default=20 (px).
        xbaseline: float
            Shift the position of the tree along x-axis.
        ybaseline: float
            Shift the position of the tree along y-axis.
        admixture_edges: Tuple, List[Tuple]
            Admixture edges add colored edges to the plot in the
            style of the 'edge_align_style'. These will be drawn
            from (source, dest, height, width, color). Example:
            `>>> [(4, 3, 50000, 3, 'red')]`.
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
        kwargs = dict(
            # toytree=self,
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
            node_as_edge_data=node_as_edge_data,
            edge_type=edge_type,
            edge_colors=edge_colors,
            edge_widths=edge_widths,
            edge_style=edge_style,
            edge_align_style=edge_align_style,
            # edge_labels=edge_labels,                 # test
            # edge_markers=edge_markers,               # test
            # edge_marker_colors=edge_marker_colors,   # test
            # edge_marker_sizes=edge_marker_size,      # test
            # edge_marker_mask=edge_marker_mask,       # test
            use_edge_lengths=use_edge_lengths,
            scale_bar=scale_bar,
            padding=padding,
            xbaseline=xbaseline,
            ybaseline=ybaseline,
            admixture_edges=admixture_edges,
            shrink=shrink,
            fixed_order=fixed_order,
            fixed_position=fixed_position,
            label=label,
            kwargs=kwargs,
        )
        # private debugging mode returns just the kwargs
        if kwargs.get("kwargs").get("debug"):
            return kwargs

        # draw the ToyTree
        try:
            canvas, axes, mark = draw_toytree(tree=self, **kwargs)
            return canvas, axes, mark
        except ToytreeError as exc:
            logger.error(exc)
            raise exc
        except Exception as exc:
            logger.error(exc)
            raise exc


# def inside_notebook() -> bool:
#     """Return True if executed from inside jupyter, else False.

#     takes only ~140 ns.
#     """
#     try:
#         shell = get_ipython().__class__.__name__
#         if shell == 'ZMQInteractiveShell':
#             return True   # Jupyter notebook or qtconsole
#         elif shell == 'TerminalInteractiveShell':
#             return False  # Terminal running IPython
#         else:
#             return False  # Other type (?)
#     except NameError:
#         return False      # Probably standard Python interpreter


if __name__ == "__main__":

    # import toytree
    tree_ = toytree.rtree.unittree(12, treeheight=1232344, seed=123)
    # tree = tree_.mod.edges_slider(0.5)
    # c, a, m = tree_._draw_browser(tree_style='s', layout='d', new=False)
    # print(tree_.write(dist_formatter="%.12g"))
    # print(tree_.get_node_data())
    # print(tree_.treenode)
    # tree_.draw()
    print(tree_)

    # print(tree.get_tip_labels())

    # tree = tree.set_node_data("color", {i: "red" for i in (2,3,4)})
    # print(tree[3].color)
    # print(tree.features)
    # print(tree.get_node_data())
    # print(tree.get_tip_data("height"))
    # print(tree.get_node_mask())
    # print(tree.get_bipartitions(exclude_singleton_splits=False))
    # print(tree._get_bipartitions_table(exclude_singleton_splits=True))
