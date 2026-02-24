#!/usr/bin/env python

"""Tree moves used in heuristic tree search algorithms.

Tree 'moves' (perturbations) are used to search tree space and
usually applied with an optimality criterion to find a best scoring
tree under either parsimony or maximum likelihood hill-climbing
algorithms.

TODO
----
- needs to be simplified...
- faster methods that do not require building full tree sets
- ...

UNDER DEVELOPMENT
-----------------
- rooted tree moves need to iterate over placements of the root?
"""

from typing import Iterator, Literal, Optional, TypeAlias

import numpy as np
from loguru import logger

import toytree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError

Query: TypeAlias = int | str | Node

__all__ = [
    "move_nni_n",
    "iter_nni_n",
    "move_spr_n",
    "iter_spr_n",
    "move_nni",
    "move_spr",
]


# FIXME: needs further work.
def move_spr_iter(tree: ToyTree, highlight: bool = False) -> Iterator[ToyTree]:
    """Yield all trees within 1 SPR move of input tree.

    Returns a generator function to iterate through each of the
    unrooted trees that are within 1 subprune and regraft (SPR)
    moves from the input tree. This tree move operation is used to
    heuristically search tree space, and can find relatively large
    changes from the current tree compared to NNI.

    TODO
    ----
    Return only unique topologies, e.g., subtree X inserted to edge
    Y may not be unique from subtree Y inserted to edge X.
    """
    tree = tree.unroot()

    # iterate over internal edges, skip tips, root, and one root child
    # to select each subtree that could be extacted.
    for nidx in range(tree.ntips, tree.nnodes - 1):

        # get list of Nodes (edges) where subtree can be inserted. This
        # cannot be root, or a desc on the subtree Node, or the subtree itself.
        subtree = tree[nidx]
        edges = (
            set(range(tree.nnodes))
            - set((i._idx for i in subtree.iter_descendants()))
            - set((i._idx for i in subtree.iter_sisters()))
            - set((subtree._up._idx, ))
            - set((subtree._idx, ))
        )

        # iterate over each possible insertion point of this edge
        for iedge in edges:

            # create copy of unrooted starting tree
            ntree = tree.copy()
            new_sister = ntree[iedge]
            subtree = ntree[nidx]

            # connect subtree to new sister by inserting a new Node
            new_node = toytree.Node("new")
            new_node_parent = new_sister._up
            old_node = subtree._up
            old_node_parent = old_node._up
            new_node._up = new_node_parent
            new_node._children = (subtree, new_sister)

            # disconnect 7 from 5
            old_node._remove_child(subtree)

            # connect 2 nodes on either side of 7
            if old_node_parent:
                old_node_parent._remove_child(old_node)
                for child in old_node._children:
                    old_node_parent._add_child(child)
                    child._dist += old_node._dist
            else:
                children = sorted(old_node._children, key=lambda x: x.idx)[::-1]
                for child in children[1:]:
                    old_node._remove_child(child)
                    children[0]._add_child(child)
            del old_node

            # connect subtree to tree
            subtree._up = new_node
            new_sister._up = new_node
            if new_node_parent:
                new_node_parent._remove_child(new_sister)
                new_node_parent._add_child(new_node)

            # if old root is now a singleton b/c new_sister is one of its children
            if len(ntree.treenode.children) == 1:
                ntree.treenode = ntree.treenode.children[0]
                oldroot = ntree.treenode._up
                ntree.treenode._up = None
                del oldroot

            # if new_sister is now the root.
            elif new_sister == ntree.treenode:
                ntree.treenode = new_node
            ntree._update()

            # optionally add style highlights
            if highlight:
                ntree = style_tree(ntree)
                ntree.style.node_colors = 'white'
                ntree.style.edge_colors = ['black'] * ntree.nnodes
                ntree.style.edge_widths = [2] * ntree.nnodes

                # color edge green
                # ntree.style.edge_colors[new_node.idx] = toytree.color.COLORS2[0]
                # ntree.style.edge_widths[new_node.idx] = 5

                # # color edge orange
                # ntree.style.edge_colors[subtree.idx] = toytree.color.COLORS2[1]
                # ntree.style.edge_widths[subtree.idx] = 5

                # # color clade 1 orange
                # for edge in nchildren:
                #     ntree.style.edge_colors[edge.idx] = toytree.color.COLORS2[1]
                #     ntree.style.edge_widths[edge.idx] = 5

                # # color clade 1 purple
                # for edge in nsisters + (nparent,):
                #     ntree.style.edge_colors[edge.idx] = toytree.color.COLORS2[2]
                #     ntree.style.edge_widths[edge.idx] = 5
            yield ntree


def move_nni_iter(tree: ToyTree, node: Query):
    """Yield trees one NNI move involving selected edge from input tree.

    Parameters
    ----------
    tree:
        ...
    node:
        ...
    """
    # swap each child with one sister of selected Node
    node = tree.get_mrca_node(node)
    children = node.children
    sister = node.get_sisters()[0]
    for pick in children:

        # make COPY of the tree
        ntree = tree.copy()

        # select Nodes from the COPIED tree.
        nnode = ntree[node._idx]
        nparent = ntree[node._up._idx]
        npick = ntree[pick._idx]
        nsister = ntree[sister._idx]
        nchildren = nnode.children

        # collapse node (connect children to parent, remove self from parent)
        for child in nchildren:
            nparent._add_child(child)
        nparent._remove_child(nnode)

        # re-insert node
        new_node = toytree.Node()
        # new_node.label = "new"
        nparent._add_child(new_node)
        nparent._remove_child(npick)
        new_node._add_child(npick)
        nparent._remove_child(nsister)
        new_node._add_child(nsister)

        # update Node idxs and coordinates
        ntree._update()
    yield ntree


def move_nni_iter_old(tree: ToyTree, highlight: bool = False) -> Iterator[ToyTree]:
    """Yield all trees within one NNI of input tree.

    Returns a generator function to iterate through each of the
    `2 * (ntips - 3)` unrooted trees that are within one nearest-
    neighbor interchange (NNI) move of the input tree. This tree
    move operation is used to heuristically search tree space, and
    is best for finding small changes from the current tree.

    Parameters
    ----------
    tree: ToyTree
        Tree from which one NNI move will be performed.
    highlight: bool
        If True the returned tree's .style dict is modified to
        highlight the swapped edges when drawn w/o a treestyle.

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
    >>> nni_gen = toytree.mod.move_nni_iter(tree, highlight=True)
    >>> for ntre in nni_gen:
    >>>     ntre.draw(layout='unrooted', use_edge_lengths=False)
    """
    tree = tree.unroot()

    # iterate over internal edges, skip tips, root, and one root child.
    for nidx in range(tree.ntips, tree.nnodes - 1):
        node = tree[nidx]

        # swap each child with one sister of selected Node
        children = node.children
        sister = node.get_sisters()[0]
        for pick in children:

            # make COPY of the tree
            ntree = tree.copy()

            # select Nodes from the COPIED tree.
            nnode = ntree[node._idx]
            nparent = ntree[node._up._idx]
            npick = ntree[pick._idx]
            nsister = ntree[sister._idx]
            nchildren = nnode.children
            nsisters = nnode.get_sisters()

            # collapse node (connect children to parent, remove self from parent)
            for child in nchildren:
                nparent._add_child(child)
            nparent._remove_child(nnode)

            # re-insert node
            new_node = toytree.Node()
            new_node.label = "new"
            nparent._add_child(new_node)
            nparent._remove_child(npick)
            new_node._add_child(npick)
            nparent._remove_child(nsister)
            new_node._add_child(nsister)

            # update Node idxs and coordinates
            # logger.info(f"NNI: {nnode} | {npick} <--> {nsister}")
            ntree._update()

            # optionally add style highlights
            if highlight:
                ntree = style_tree(ntree)
                ntree.style.node_colors = 'white'
                ntree.style.edge_colors = ['black'] * ntree.nnodes
                ntree.style.edge_widths = [2] * ntree.nnodes

                # color edge green
                ntree.style.edge_colors[new_node.idx] = toytree.color.COLORS2[0]
                ntree.style.edge_widths[new_node.idx] = 5

                # color clade 1 orange
                for edge in nchildren:
                    ntree.style.edge_colors[edge.idx] = toytree.color.COLORS2[1]
                    ntree.style.edge_widths[edge.idx] = 5

                # color clade 1 purple
                for edge in nsisters + (nparent,):
                    ntree.style.edge_colors[edge.idx] = toytree.color.COLORS2[2]
                    ntree.style.edge_widths[edge.idx] = 5
            yield ntree


def move_nni(
    tree: ToyTree,
    edge: Optional[int] = None,
    seed: Optional[int] = None,
    inplace: bool = False,
    highlight: bool = False,
) -> ToyTree:
    """Return a tree one nearest-neighbor-interchange from current tree.

    An edge is selected and a subtree from either side is randomly
    selected and swapped.

    Parameters
    ----------
    tree: ToyTree
        A tree on which to perform a single NNI move.
    edge: int or None
        The int idx label of an edge in the tree to perform NNI on,
        selected by the Node idx below the edge. If None then an
        internal edge will be randomly selected.
    seed: int or None
        Seed for the numpy random number generator.
    inplace: bool
        If True the tree is modified inplace rather than copied.
    highlight: bool
        If True the .style dict is modified to highlight changes.
    """
    # work with unrooted tree, optionally as a copy (much slower).
    # TODO: can this be done without requiring unrooting?
    tree = tree.unroot(inplace=True) if inplace else tree.unroot()

    # create the random generator
    rng = np.random.default_rng(seed)

    # select an internal edge, or tip, which selects parent internal
    internal_edges = range(tree.ntips, tree.nnodes - 1)
    if edge is None:
        edge = rng.choice(internal_edges)
    else:
        if edge not in internal_edges:
            raise ToytreeError(f"idx must be an internal edge: {internal_edges}")
    node = tree[edge]

    # get references to neighbor nodes
    parent = node.up
    children = node.children

    # select a child to swap with
    pick = rng.choice(children)
    sisters = node.get_sisters()
    sister = sisters[0]
    logger.info(f"NNI: edge={node}, swap={pick} <--> {sister}")

    # add labels when debugging
    # sister.label = "sister"
    # node.label = "node"
    # parent.label = "parent"
    # for idx, child in enumerate(children):
    #     child.label = f"child-{idx}"

    # collapse node (connect children to parent, remove self from parent)
    for child in children:
        parent._add_child(child)
    parent._remove_child(node)

    # re-insert node
    # TODO: can this be done re-using node? is it better for data?
    new_node = toytree.Node()
    new_node.label = "new"
    parent._add_child(new_node)
    parent._remove_child(pick)
    new_node._add_child(pick)
    parent._remove_child(sister)
    new_node._add_child(sister)

    # update Node idxs and coordinates
    tree._update()

    # optionally add style highlights
    if highlight:
        tree = style_tree(tree)
        tree.style.node_colors = 'white'
        tree.style.edge_colors = ['black'] * tree.nnodes
        tree.style.edge_widths = [2] * tree.nnodes

        # color edge green
        tree.style.edge_colors[new_node.idx] = toytree.color.COLORS2[0]
        tree.style.edge_widths[new_node.idx] = 5

        # color clade 1 orange
        for edg in children:
            tree.style.edge_colors[edg.idx] = toytree.color.COLORS2[1]
            tree.style.edge_widths[edg.idx] = 5

        # color clade 1 purple
        for edg in sisters + (parent,):
            tree.style.edge_colors[edg.idx] = toytree.color.COLORS2[2]
            tree.style.edge_widths[edg.idx] = 5
    return tree


# TODO: try to simplify more like in NNI
def move_spr(
    tree: ToyTree,
    seed: Optional[int] = None,
    inplace: bool = False,
    highlight: bool = False,
) -> ToyTree:
    """Return a rooted ToyTree one SPR move from the current tree.

    The returned tree will have a different topology from the starting
    tree, at an SPR distance of 1. It randomly samples a subtree to
    extract from the tree, and then reinserts the subtree at an edge
    that is not (1) one of its descendants; (2) its sister; (3) its
    parent; or (4) itself.

    Parameters
    ----------
    tree: ToyTree
        The tree to be modified by a tree move.
    seed: int or None
        Seed for numpy random number generator.
    inplace: bool
        If True the tree is modified in place, else a copy is returned.
    highlight: bool
        If True the .style dict of the returned ToyTree will be
        modified to show the edges that were involved in the tree
        move if drawn without a tree_style argument.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=8, seed=123)
    >>> new_tree = toytree.mod.move_nni(tree, highlight=True)
    >>> tree.draw();
    >>> new_tree.draw();
    """
    tree = tree if inplace else tree.copy()
    rng = np.random.default_rng(seed)

    # randomly select a subtree (any non-root Node)
    sidx = rng.choice(tree.nnodes - 1)
    subtree = tree[sidx]

    # get list of Nodes (edges) where subtree can be inserted. This
    # cannot be root, or a desc on the subtree Node, or the subtree itself.
    edges = (
        set(range(tree.nnodes)) -
        set((i._idx for i in subtree._iter_descendants())) -
        set((i._idx for i in subtree._iter_sisters())) -
        set((subtree._up._idx, )) -
        set((subtree._idx, ))
    )

    # sample an edge by its descendant Node
    new_sister = tree[rng.choice(list(edges))]
    # logger.info(f"SPR: {sidx} -> {new_sister.idx}; options={edges}")

    # connect subtree to new sister by inserting a new Node
    new_node = toytree.Node("new")
    new_node_parent = new_sister._up
    old_node = subtree._up
    old_node_parent = old_node._up
    new_node._up = new_node_parent
    new_node._children = (subtree, new_sister)

    # remove 12 and connect 11 to 14
    old_node._remove_child(subtree)
    if old_node_parent:
        old_node_parent._remove_child(old_node)
        for child in old_node._children:
            old_node_parent._add_child(child)
            child._dist += old_node._dist
    del old_node

    # connect subtree to tree
    subtree._up = new_node
    new_sister._up = new_node
    if new_node_parent:
        new_node_parent._remove_child(new_sister)
        new_node_parent._add_child(new_node)

    # if old root is now a singleton b/c new_sister is one of its children
    if len(tree.treenode.children) == 1:
        tree.treenode = tree.treenode.children[0]
        oldroot = tree.treenode._up
        tree.treenode._up = None
        del oldroot

    # if new_sister is now the root.
    elif new_sister == tree.treenode:
        tree.treenode = new_node
    tree._update()

    # optional: color edges of the subtree that was moved.
    if highlight:
        tree.style.edge_colors = ['black'] * tree.nnodes
        tree.style.node_colors = ['white'] * tree.nnodes
        tree.style.node_style.stroke_width = 1.5
        tree.style.node_sizes = 8
        tree.style.node_labels = "idx"
        tree.style.node_labels_style.font_size = 12
        tree.style.node_labels_style._toyplot_anchor_shift = -9
        tree.style.node_labels_style.baseline_shift = 7.5
        tree.style.use_edge_lengths = False

        # tree.get_mrca_node(*tips)
        for node in subtree._iter_descendants():
            tree.style.edge_colors[node.idx] = toytree.color.COLORS2[3]
            tree.style.node_colors[node.idx] = toytree.color.COLORS2[3]
        tree.style.node_colors[new_node.idx] = toytree.color.COLORS2[3]
    return tree


def highlight_edges(tree: ToyTree, *edges: toytree.Node) -> ToyTree:
    """Set colors to highlight edges in tree style dict."""
    tree.style.edge_colors = ['black'] * tree.nnodes
    tree.style.edge_widths = [2] * tree.nnodes
    tree.style.node_colors = 'white'
    for idx, edge in enumerate(edges):
        tree.style.edge_colors[edge.idx] = toytree.color.COLORS2[idx]
        tree.style.edge_widths[edge.idx] *= 2
    return tree


def style_tree(tree: ToyTree) -> ToyTree:
    """Add style to show parts of tree that moved."""
    tree.style.layout = "unroot"
    tree.style.use_edge_lengths = False
    tree.style.node_style.stroke_width = 1.5
    tree.style.node_sizes = 6
    tree.style.node_labels = "idx"
    tree.style.node_labels_style.font_size = 12
    tree.style.node_labels_style._toyplot_anchor_shift = 8
    tree.style.node_labels_style.baseline_shift = 8
    tree.style.tip_labels_style._toyplot_anchor_shift = -8
    tree.style.tip_labels_style.baseline_shift = 8
    tree.style.tip_labels_style.font_size = 14
    return tree


def _validate_n_moves(n: int) -> None:
    """Validate N-step move depth."""
    if not isinstance(n, int):
        raise ToytreeError("'n' must be an int.")
    if n < 0:
        raise ToytreeError("'n' must be >= 0.")


def _iter_move_neighborhood_exact_n(
    tree: ToyTree,
    n: int,
    move: Literal["nni", "spr"],
    order: Literal["random", "sorted"] = "random",
    seed: int | None = None,
    highlight: bool = False,
) -> Iterator[ToyTree]:
    """Yield unique trees exactly n moves from input in unrooted space."""
    _validate_n_moves(n)
    if order not in {"random", "sorted"}:
        raise ToytreeError("order must be one of {'random', 'sorted'}.")

    # Work in unrooted tree space for canonical NNI/SPR neighborhoods.
    base = tree.unroot()
    if n == 0:
        yield base
        return

    # store the frontier tree and set of visited topology_ids
    rng = np.random.default_rng(seed)
    frontier: dict[str, ToyTree] = {base.get_topology_id(): base}
    seen = set(frontier)

    # Breadth-first expansion ensures the frontier holds exact-depth neighbors.
    for depth in range(1, n + 1):
        next_frontier: dict[str, ToyTree] = {}
        parents = list(frontier.values())
        if order == "random":
            rng.shuffle(parents)
        else:
            parents.sort(key=lambda i: i.get_topology_id())

        for parent in parents:
            # Only the last expansion depth adds optional edge highlighting.
            do_highlight = bool(highlight and depth == n)
            if move == "nni":
                neighbors = move_nni_iter_old(parent, highlight=do_highlight)
            else:
                neighbors = move_spr_iter(parent, highlight=do_highlight)
            for ntree in neighbors:
                tid = ntree.get_topology_id()
                if tid in seen:
                    continue
                seen.add(tid)
                next_frontier[tid] = ntree
        frontier = next_frontier
        if not frontier:
            break

    # Return exact-depth neighbors in requested output order.
    final = list(frontier.values())
    if order == "random":
        rng.shuffle(final)
    else:
        final.sort(key=lambda i: i.get_topology_id())
    for ntree in final:
        yield ntree


@add_subpackage_method(TreeModAPI)
def iter_nni_n(
    tree: ToyTree,
    n: int = 1,
    *,
    order: Literal["random", "sorted"] = "random",
    seed: int | None = None,
    highlight: bool = False,
) -> Iterator[ToyTree]:
    """Yield unique trees that are exactly ``n`` NNI moves from input."""
    yield from _iter_move_neighborhood_exact_n(
        tree=tree,
        n=n,
        move="nni",
        order=order,
        seed=seed,
        highlight=highlight,
    )


@add_subpackage_method(TreeModAPI)
def iter_spr_n(
    tree: ToyTree,
    n: int = 1,
    *,
    order: Literal["random", "sorted"] = "random",
    seed: int | None = None,
    highlight: bool = False,
) -> Iterator[ToyTree]:
    """Yield unique trees that are exactly ``n`` SPR moves from input."""
    yield from _iter_move_neighborhood_exact_n(
        tree=tree,
        n=n,
        move="spr",
        order=order,
        seed=seed,
        highlight=highlight,
    )


def _sample_tree_from_iter(trees: list[ToyTree], seed: int | None = None) -> ToyTree:
    """Sample one tree uniformly from a non-empty list."""
    if not trees:
        raise ToytreeError("No valid moved trees were generated for requested n.")
    rng = np.random.default_rng(seed)
    return trees[int(rng.integers(len(trees)))]


@add_subpackage_method(TreeModAPI)
def move_nni_n(
    tree: ToyTree,
    n: int = 1,
    *,
    seed: int | None = None,
    mode: Literal["walk", "sample"] = "walk",
    highlight: bool = False,
    inplace: bool = False,
) -> ToyTree:
    """Return one tree exactly ``n`` NNI moves from input."""
    _validate_n_moves(n)
    if mode not in {"walk", "sample"}:
        raise ToytreeError("mode must be one of {'walk', 'sample'}.")
    if n == 0:
        return tree if inplace else tree.unroot()

    # Random-walk mode scales better by avoiding full neighborhood enumeration.
    if mode == "walk":
        rng = np.random.default_rng(seed)
        current = tree.unroot(inplace=True) if inplace else tree.unroot()
        for step in range(n):
            neighbors = list(move_nni_iter_old(current, highlight=highlight and step == n - 1))
            if not neighbors:
                raise ToytreeError("No valid NNI neighbors were generated.")
            current = neighbors[int(rng.integers(len(neighbors)))]
        if inplace:
            tree.treenode = current.treenode
            tree._update()
            return tree
        return current

    # Sampling mode enumerates exact-depth neighborhood then samples one.
    neighborhood = list(iter_nni_n(tree, n=n, order="random", seed=seed, highlight=highlight))
    sample = _sample_tree_from_iter(neighborhood, seed=seed)
    if inplace:
        tree.treenode = sample.treenode
        tree._update()
        return tree
    return sample


@add_subpackage_method(TreeModAPI)
def move_spr_n(
    tree: ToyTree,
    n: int = 1,
    *,
    seed: int | None = None,
    mode: Literal["walk", "sample"] = "walk",
    highlight: bool = False,
    inplace: bool = False,
) -> ToyTree:
    """Return one tree exactly ``n`` SPR moves from input."""
    _validate_n_moves(n)
    if mode not in {"walk", "sample"}:
        raise ToytreeError("mode must be one of {'walk', 'sample'}.")
    if n == 0:
        return tree if inplace else tree.unroot()

    # Random-walk mode scales better by avoiding full neighborhood enumeration.
    if mode == "walk":
        rng = np.random.default_rng(seed)
        current = tree.unroot(inplace=True) if inplace else tree.unroot()
        for step in range(n):
            neighbors = list(move_spr_iter(current, highlight=highlight and step == n - 1))
            if not neighbors:
                raise ToytreeError("No valid SPR neighbors were generated.")
            current = neighbors[int(rng.integers(len(neighbors)))]
        if inplace:
            tree.treenode = current.treenode
            tree._update()
            return tree
        return current

    # Sampling mode enumerates exact-depth neighborhood then samples one.
    neighborhood = list(iter_spr_n(tree, n=n, order="random", seed=seed, highlight=highlight))
    sample = _sample_tree_from_iter(neighborhood, seed=seed)
    if inplace:
        tree.treenode = sample.treenode
        tree._update()
        return tree
    return sample


# def move_nni_search(
#     tree: ToyTree,
#     criterion: Callable,
#     tolerance: float,
#     ) -> Iterator[ToyTree]:
#     """Return an infinite generator of sequential NNI.

#     This function can be used to perform a greedy hill-climbing
#     algorithm. It finds all trees within one NNI move from the
#     current tree, and applies the criterion function to each. The
#     tree with the lowest score will be yielded, and becomes the
#     source from NNI moves in the next iteration. If no trees have
#     a greater score then the generator ends.

#     Note
#     ----
#     To find a best-scoring tree a search should be started from many
#     different random starting trees.

#     Examples
#     --------
#     >>> tree = toytree.rtree.unittree(10, seed=123)
#     >>> search = nni_search(tree)
#     >>> path = [i for i in search]
#     >>> path[-1].draw()
#     """
#     pass
#     # TODO
#     # score = 0
#     # while 1:
#     #     for idx, proposal in enumerate(move_iter_nni):
#     #         score = criterion(proposal)
#     #         scores.append(score)
#     #     yield proposal


# def move_nni(
#     tree: ToyTree,
#     idx1: Optional[int]=None,
#     idx2: Optional[int]=None,
#     seed: Optional[int]=None,
#     inplace: bool=False,
#     highlight: bool=False,
#     ) -> ToyTree:
#     """Return a rooted ToyTree one SPR move from the current tree.

#     The returned tree will have a different topology from the starting
#     tree, at an SPR distance of 1. It randomly samples a subtree to
#     extract from the tree, and then reinserts the subtree at an edge
#     that is not (1) one of its descendants; (2) its sister; (3) its
#     parent; or (4) itself.

#     Parameters
#     ----------
#     tree: ToyTree
#         The tree to be modified by a tree move.
#     idx1: int or None
#         Node index of the first clade to be swapped with another. If
#         None then it is randomly sampled.
#     idx2: int or None
#         Node index of the second clade to be swapped with another. If
#         None then it is randomly sampled given limitations of idx1.
#     seed: int or None
#         Seed for numpy random number generator.
#     inplace: bool
#         If True the tree is modified in place, else a copy is returned.
#     highlight: bool
#         If True the .style dict of the returned ToyTree will be
#         modified to show the edges that were involved in the tree
#         move if drawn without a tree_style argument.

#     Examples
#     --------
#     >>> tree = toytree.rtree.unittree(ntips=8, seed=123)
#     >>> new_tree = toytree.mod.move_nni(tree, highlight=True)
#     >>> tree.draw();
#     >>> new_tree.draw();
#     """
#     # work with unrooted tree, optionally as a copy (much slower).
#     if inplace:
#         tree.unroot(inplace=True)
#     else:
#         tree = tree.unroot()

#     # create the random generator
#     rng = np.random.default_rng(seed)

#     # randomly select a subtree (any non-root Node)
#     node1 = tree[rng.choice(tree.nnodes - 1)] if idx1 is None else tree[idx1]

#     # get list of Nodes (edges) that can be swapped with node1.
#     # 1. starts with all possible Nodes except root.
#     # 2. removes descendants of node1
#     # 3. removes sisters of node1 (uninformative interchange)
#     # 4. remove parent of node1
#     # 5. remove node1
#     edges = (
#         set(range(tree.nnodes - 1)) -
#         set((i._idx for i in node1._iter_descendants())) -
#         set((i._idx for i in node1._iter_sisters())) -
#         set((node1._up._idx, )) -
#         set((node1._idx, ))
#     )

#     # sample an edge by its descendant Node
#     node2 = tree[rng.choice(list(edges))] if idx2 is None else tree[idx2]

#     # raise error if user-entered pair is invalid
#     if node2.idx not in edges:
#         raise ToytreeError(
#             f"invalid NNI move: {node2} not within valid pairs from {node1}: {edges}")

#     # debugging
#     logger.info(f"NNI: {node1} -> {node2}; options={edges}")

#     # re-attach Nodes using references saved before re-attaching
#     parent_1 = node1._up._idx
#     parent_2 = node2._up._idx
#     tree[parent_1]._remove_child(node1)
#     tree[parent_2]._remove_child(node2)
#     tree[parent_1]._add_child(node2)
#     tree[parent_2]._add_child(node1)

#     # store idx of both parents.
#     parent_1 = node1._up._idx
#     parent_2 = node2._up._idx

#     # remove swapping subtrees from the tree
#     tree[parent_1]._remove_child(node1)
#     tree[parent_2]._remove_child(node2)

#     # add the subtrees (node1 to parent2 and node2 to parent1)
#     tree[parent_1]._add_child(node2)
#     tree[parent_2]._add_child(node1)

#     # call toytree update routine
#     tree._update()

#     # add style to show subtrees swapped
#     if highlight:
#         tree.style.edge_colors = ['black'] * tree.nnodes
#         tree.style.node_colors = ['white'] * tree.nnodes
#         tree.style.node_style.stroke_width = 1.5
#         tree.style.node_sizes = 15
#         tree.style.node_labels = "idx"
#         tree.style.node_labels_style.font_size = 8
#         tree.style.tip_labels_style._toyplot_anchor_shift = -12
#         tree.style.tip_labels_style.baseline_shift = 9

#         tree.style.node_colors[node1.idx] = toytree.color.COLORS2[0]
#         for node in node1._iter_descendants():
#             tree.style.edge_colors[node.idx] = toytree.color.COLORS2[0]
#             tree.style.node_colors[node.idx] = toytree.color.COLORS2[0]
#         tree.style.node_colors[node2.idx] = toytree.color.COLORS2[3]
#         for node in node2._iter_descendants():
#             tree.style.edge_colors[node.idx] = toytree.color.COLORS2[3]
#             tree.style.node_colors[node.idx] = toytree.color.COLORS2[3]
#     return tree



# def get_all_neighbors_nni(
#     tree: ToyTree,
#     node=None,
#     highlight=False,
#     seed=None,
#     quiet=True,
#     ):
#     """Return a list of all trees within 1 NNI move from input tree.

#     Given a tree performs multiple NNI to get all the neighbors
#     given a node. If not is not provided, it is selected randomly.

#     Parameters
#     ----------
#     ...
#     """
#     tree = tree.copy()
#     tree = tree.unroot()

#     if not quiet: print(f"There are {2 * (tree.ntips - 3)} expected nearest neighbors for the given tree")

#     rng = np.random.default_rng(seed)


#     # randomly select first subtree (any non-root Node)
#     if node == None:
#         f_idx = rng.choice(tree.nnodes - 1)
#     else:
#         f_idx = node #use node specified by user

#     subtree_a = tree[f_idx]


#     # Check available nodes to select second subtree
#     # It should follow the following statements
#     available_nodes = (
#         set(range(tree.nnodes - 1)) # set with all possible nodes but the root
#         - set((i._idx for i in subtree_a._iter_descendants())) # remove descendants of subtree
#         - set((i._idx for i in subtree_a._iter_sisters())) # remove sisters of subtree (to avoid uninformative interchange)
#         - set((subtree_a._up._idx, )) # remove  parental of subtree (to avoid pick a subtree with subtree_a in there)
#         - set((subtree_a._idx, )) # remove subtree node itself
#     )
#     neighbor_trees = []
#     for available_node in available_nodes:
#         neighbor_trees.append(one_nni(tree, force=(f_idx, available_node), highlight=highlight, quiet=True, seed=seed))

#     return neighbor_trees


if __name__ == "__main__":

    toytree.set_log_level("INFO")
    NTIPS = 5
    TREE = toytree.rtree.unittree(NTIPS, seed=333).unroot()

    # draw the original tree
    c0, _, _ = TREE.draw(
        layout='unroot',
        use_edge_lengths=False,
        # tip_labels_style={"baseline-shift": 15},
        node_labels="idx",
        node_sizes=13,
    )

    # get mtree with all trees in NNI generator
    GEN = move_nni_iter(TREE, highlight=True)
    # GEN = move_spr_iter(TREE, highlight=True)
    MTRE = toytree.mtree(list(GEN))

    # get shape of tree drawing grid
    SIZE = 2 * (NTIPS - 3)
    SHAPE = (int(SIZE / 2), 2)

    # draw all trees within one NNI move
    c1, _, _ = MTRE.draw(
        shape=SHAPE,
        layout='unroot',
        use_edge_lengths=False,
        tip_labels_style={"font-size": 14},
    )

    # show result in default browser
    toytree.utils.show([c0, c1], new=False, tmpdir="~")
