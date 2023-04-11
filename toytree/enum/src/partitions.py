# #!/usr/bin/env python

# """Methods for extracting partitions from trees.

# Formatting
# -----------
# We considered the following formats for partitions/bipartitions:

# ({0, 1}, {2, 3}) - fastest, (node, node.up) sorted, but not easy to compare between trees.
# ((0, 1), (2, 3)) - sorting of biparts and parts allows for easy comparison between trees.
# {(0, 1), (2, 3)} - sorting of biparts destroys order within parts.
# {{0, 1}, {2, 3}} - XXX not possible.

# The first and second formats both have useful cases and so we provide
# functions to return both types.

# Examples
# --------
# Methods for examining splits on a tree:


# Get sets of Nodes on either side of each edge in a tree.
# >>> tree.iter_edge_bipartition_sets()      # ({0, 1}, {2, 3, 4}), ...

# Get sets of Nodes from the four subclades of each edge in a tree.
# >>> tree.iter_edge_quadripartition_sets()  # (({0}, {1}), ({2}, {3, 4})), ...

# Get name-ordered tuples of Nodes on either side of each edge in a tree.
# >>> tree.iter_bipartitions()               # ((0, 1), (2, 3, 4)), ...

# Get name-ordered tuples of Nodes for each quartet induced by bipartitions in a tree.
# >>> tree.iter_quartets()                   # ((0, 1), (2, 3)), ...

# Get name-ordered tuples of Nodes for each quartet induced by quadripartitions in a tree.
# >>> tree.iter_quadripartitions()             # ((0, 1), (2, 3)), ...

# Get fast unordered sets of all combinations of 4 tip Nodes in a tree
# >>> tree._iter_quartet_sets()              # {0, 1, 2, 3}, ...

# Get number of quartets induced by the splits in a tree.
# >>> tree.get_n_quartets()                  # 5

# Get bipartition for a specific node/edge.
# >>> tree.get_bipartition_for_edge(tree, 1)  # ((0, 1), (2, 3, 4)), ...

# Get quartets for a specific node/edge.
# >>> tree.get_quartets_for_edge(tree, 1)      # [((0, 1), (2, 3)), ...]

# Get quadripartitions for a specific node/edge.
# >>> tree.get_quadripartitions_for_edge(tree, 1)  # [((0, 1), (2, 3)), ...]

# TODO
# ----
# after revisiting the use of bipartitions etc in distance methods
# come back to this code and decide if tuples or sets should be used,
# or both as an option.




# DEPRECATED!!!!



# """

# # pylint: disable='too-many-branches'

# from typing import TypeVar, Iterator, Tuple, Optional, Set, List, Union, Callable, Sequence, Any
# import itertools
# from loguru import logger
# import pandas as pd
# import numpy as np
# from toytree import Node, ToyTree
# from toytree.core.apis import TreeEnumAPI, add_subpackage_method, add_toytree_method
# from toytree.utils import ToytreeError

# logger = logger.bind(name="toytree")
# Query = TypeVar("Query")
# # Node = TypeVar("Node")

# __all__ = [
#     "iter_edges",
#     "iter_bipartitions",
#     # "_iter_unordered_quadripartitions",
#     "iter_quadripartitions",
#     "iter_quartets",
#     # "iter_edge_quadripartition_sets",
#     # "iter_bipartitions_info",
#     "get_edges",
#     "get_bipartitions_table",
#     "get_bipartition_for_edge",
# ]





# @add_toytree_method(ToyTree)
# @add_subpackage_method(TreeEnumAPI)
# def iter_edges(self, feature: Optional[str] = None) -> Iterator[Tuple[Node, Node]]:
#     """Generator of (Node, Node) tuples representing edges in tree.

#     Given the current tree rooting edges are yielded in idx order
#     as (child, parent). The edges set will include edges connected
#     to the root Node even if the tree is unrooted. To instead view
#     edges as bipartitions of Node sets see `iter_bipartitions`.

#     Parameters
#     ----------
#     feature: str
#         An optional feature of a Node returned in place of the Node
#         object to represent it. For example, 'name' or 'idx'.

#     Example
#     -------
#     >>> tree = toytree.rtree.unittree(5, seed=123)
#     >>> list(iter_edges(feature='idx'))
#     >>> # [(0, 5), (1, 5), (2, 6), (3, 7), (4, 7), (5, 6), (6, 8), (7, 8)]
#     """
#     if feature:
#         for node in self[:-1]:
#             yield (getattr(node, feature), getattr(node._up, feature))
#     else:
#         for node in self[:-1]:
#             yield (node, node._up)


# @add_toytree_method(ToyTree)
# @add_subpackage_method(TreeEnumAPI)
# def get_edges(self, feature: Optional[str] = None, df: bool = False) -> Union[np.ndarray, pd.DataFrame]:
#     """Return matrix of (child, parent) edges.

#     Given the current tree rooting edges are yielded in idx order
#     as (child, parent).

#     Parameters
#     ----------
#     feature: str or None
#         Edges can be represented by Node features such as 'idx' or
#         'name' (default='idx'). None returns Node objects.
#     df: bool
#         If True the matrix is returned as a pd.DataFrame rather
#         than as a np.ndarray.

#     See Also
#     --------
#     tree.iter_edges
#     """
#     edges = list(self.iter_edges(feature=feature))
#     if df:
#         return pd.DataFrame(edges, columns=["child", "parent"])
#     return np.array(edges)


# @add_subpackage_method(TreeEnumAPI)
# def iter_edge_quadripartition_sets(
#     tree: ToyTree,
#     feature: Optional[str] = "name",
#     contract_partitions: bool = False,
#     include_internal_nodes: bool = False,
# ) -> Iterator[Tuple[Tuple[Set, Set], Tuple[Set, Set]]]:
#     """Yield a tuple of sets of tips for each quadripartition.

#     Edge sets are returned as (({e0},{e1}), ({e2},{e3})) representing
#     sets of (tip) Nodes descending from each of the four edges
#     subtending a focal edge, where the focal edge splits e0,e1 from
#     e2,e3. Note the use of sets to indicate that the items are not
#     sorted. Rooting only affects the order in which quadripartition
#     sets are yielded.

#     Parameters
#     ----------
#     tree: ToyTree
#         A tree to extract edge sets from.
#     feature: str or None
#         Feature to represent Nodes in returned sets. Default is 'name'
#         to use Node name strings. None will return Node objects.
#     contract_partitions: bool
#         If True then each partition is contracted to show only the
#         first Node closest to the edge.
#     include_internal_nodes: bool
#         If True then all nodes in each partition are shown, whether it
#         is internal or a tip Node. If False then only tips are shown.
#         Note: This option is overriden if contract_partitions=True in
#         which case the closest Node is shown whether or not it is a tip.

#     Examples
#     --------
#     >>> newick = "((a,b)X,((c,d)Y,e)Z)R;"
#     >>> tree = toytree.tree(newick)

#     >>> sorted(iter_edge_quadripartition_sets(tree))
#     >>> # (({a},{b}),({c,d},{e}))
#     >>> # (({a,b},{e}),({c},{d}))

#     >>> kwargs = dict(exclude_internal_nodes=False)
#     >>> sorted(iter_edge_quadripartition_sets(tree, **kwargs))
#     >>> # (({a},{b}),({c,d,Y},{e}))
#     >>> # (({a,b,X},{e}),({c},{d}))

#     >>> kwargs = dict(expand_partitions=False)
#     >>> sorted(iter_edge_quadripartition_sets(tree, **kwargs))
#     >>> # (({a},{b}),({Y},{e}))
#     >>> # (({X},{e}),({c},{d}))
#     """
#     # tree = tree.unroot()
#     cache = {}

#     # build a cache of descendants for each Node.
#     topnode = tree.nnodes - 1 if tree.is_rooted() else tree.nnodes
#     for node in tree[:topnode]:  # [:-1]:#.traverse("idxorder"):

#         # if tip simply store its info
#         if node.is_leaf():
#             cache[node] = {node}
#             continue

#         # get tips from each child, and store union to this node
#         vals = [cache[i] for i in node.children]

#         # cache only the closest Node (exclude_internal_nodes ignored)
#         if contract_partitions:
#             cache[node] = {node}

#         # cache tip Nodes with or without internal Nodes
#         else:
#             # cache only the tip Nodes
#             if not include_internal_nodes:
#                 cache[node] = set.union(*vals)
#             # cache all nodes including internals
#             else:
#                 cache[node] = set.union(*vals) | {node}

#     #print('x', cache[tree.get_nodes("X")[0]]) TODO
#     # get set of all relevant nodes for set diffs below
#     if include_internal_nodes:
#         nodes = set(cache)
#     else:
#         nodes = set(tree.get_nodes()[:tree.ntips])

#     # iterate over internal nodes/edges in the tree
#     topnode = tree.nnodes - 2 if tree.is_rooted() else tree.nnodes - 1
#     for node in tree[tree.ntips: topnode]:  # tree.nnodes - 1]:
#         # get >= 2 sets of nodes for children below
#         below = [cache[i] for i in node.children]

#         # if up is root then above_left contains all remaining clades
#         if node._up.is_root():
#             above = []
#             for sis in node.get_sisters():
#                 sis_children = sis._children
#                 if sis_children:
#                     for sis_child in sis_children:
#                         above.append(cache[sis_child])
#                 else:
#                     above.append(cache[sis])
#             # above = [cache[sis_child] for sis in node.get_sisters()]
#             # above = above_left
#             # above = [set(itertools.chain(*above_left))]
#             # above_right = []
#             # TODO: need to expand partitions near root?
#         else:
#             # print(node, below, above_left)
#             # get >= 1 sets of nodes to represent >= 1 clades above.
#             above_left = [cache[sis] for sis in node.get_sisters()]
#             above_right = nodes - {node, node._up} - set.union(*above_left + below)

#             # represent final clade by all its desc, or by its mrca.
#             if contract_partitions:
#                 above = above_left + [{tree.get_mrca_node(*above_right)}]
#             else:
#                 above = above_left + [above_right]

#         print("node", node, below, above, "\n") # above_left, above_right, "\n")
#         # add others
#         bpair = itertools.combinations(below, 2)
#         apair = itertools.combinations(above, 2)
#         for x1, x2 in itertools.product(bpair, apair):
#             # require all to exclude root in unrooted tree: ()
#             if all([x1[0], x1[1], x2[0], x2[1]]):
#                 if feature is None:
#                     yield ((x1[0], x1[1]), (x2[0], x2[1]))
#                 else:
#                     yield (
#                         tuple({getattr(j, feature) for j in i} for i in x1),
#                         tuple({getattr(j, feature) for j in i} for i in x2),
#                     )




# @add_subpackage_method(TreeEnumAPI)
# def iter_quadripartitions(
#     tree: ToyTree,
#     feature: Optional[str] = "name",
#     collapse: bool = False,
# ) -> Iterator:
#     r"""Generator yields name-sorted quadripartitions induced by each edge.

#     Quadripartitions are samples of 4 tips in a tree that are drawn
#     from the four subclades induced by an edge in a tree. This
#     collection of splits is a subset of the number of *quartets* in a
#     tree, which can be generated using the `iter_quartets` function.
#     Whereas quartets represent combinations of two samples from either
#     side of bipartition, this function returns combinations of samples
#     drawn from the four clades of a quadripartition induced by a split
#     in the tree. The difference between these two collections is easy
#     to see on larger trees where this set is much smaller than the
#     number of quartets.

#     Example
#     -------
#     >>> tree = toytree.tree("((a,b)X,((c,d)Y,e)Z)R;")
#     >>> sorted(toytree.enumerate.iter_quadripartitions(tree))
#     >>> [(('a', 'b'), ('c', 'e')),
#     >>>  (('a', 'b'), ('d', 'e')),
#     >>>  (('a', 'e'), ('c', 'd')),
#     >>>  (('b', 'e'), ('c', 'd'))]

#     See Also
#     --------
#     - `toytree.enumerate.iter_quartets`
#     - `ToyTree.iter_quartets`
#     """
#     for split in iter_edge_quadripartition_sets(tree, feature=None):
#         for tips in itertools.product(*split[0] + split[1]):
#             tup0 = sorted((tips[0], tips[1]), key=lambda x: x.name)
#             tup1 = sorted((tips[2], tips[3]), key=lambda x: x.name)
#             tups = sorted((tup0, tup1), key=lambda x: x[0].name)
#             qrt = tuple(tups[0] + tups[1])

#             if feature:
#                 qrt = tuple(getattr(i, feature) for i in qrt)

#             if collapse:
#                 yield (qrt[0], qrt[1], qrt[2], qrt[3])
#             else:
#                 yield (qrt[0], qrt[1]), (qrt[2], qrt[3])


# def iter_bipartitions_info(
#     tree: ToyTree,
#     feature: str = "name",
#     include_internal_nodes: bool = False,
#     include_singleton_partitions: bool = False,
#     include_root: bool = False,
# ) -> Iterator[Tuple[Node, Tuple, float]]:
#     """..."""
#     is_rooted = tree.is_rooted()
#     iter_biparts = tree.iter_bipartitions(
#         include_internal_nodes=include_internal_nodes,
#         include_singleton_partitions=True,
#         include_root=include_root,
#     )
#     for node, bipart in zip(tree, iter_biparts):
#         if node._is_leaf():
#             if include_singleton_partitions:
#                 yield node, bipart, node._dist
#         elif node._up.is_root() and is_rooted:
#             yield node, bipart, sum(i._dist for i in node._up.children)
#         else:
#             yield node, bipart, node._dist


# @add_subpackage_method(TreeEnumAPI)
# def get_bipartitions_table(
#     tree: ToyTree,
#     feature: str = "name",
#     include_internal_nodes: bool = False,
#     include_singleton_partitions: bool = False,
# ) -> pd.DataFrame:
#     """Return a DataFrame with partitions from tree in idx order.

#     Partitions represent splits that separate sets of Nodes in a
#     tree, and can be represented by the tips descended from each
#     side of the split, e.g., [['a', 'b'], ['c', 'd']]. Options are
#     available to return all Nodes on either side of a partition,
#     instead of just the tips, but tips are generally of interest.
#     The index of the returned DataFrame corresponds to the Node
#     idx label below the edge of each partition.

#     Note
#     ----
#     The root Node is ignored, and so rooting has no effect on
#     the partitions. This is because the root separates None from
#     all, e.g., [[], ['a', 'b', 'c', 'd']], and the nodes on
#     either side of the root have the same partition, [['a', 'b'],
#     ['c', 'd']], only one of which is returned.

#     Parameters
#     ----------
#     feature: str
#         The Node feature to return for every Node on each side of
#         a split. Default is "name".
#     exclude_internal_labels: bool
#         Default is to only show tip Nodes on either side of a
#         bipartition, but internal Nodes can be included as well.
#     exclude_singleton_splits: bool
#         Default is to exclude singleton splits (e.g., {A | B,C,D})
#         since it is implicit that one exists for every tip Node,
#         but these can be included if requested.

#     See Also
#     --------
#     `ToyTree.iter_bipartitions`, `ToyTree._get_bipartitions_table`

#     Examples
#     --------
#     >>> tree = toytree.rtree.unittree(4)
#     >>> tree.get_bipartitions_table()
#     >>> #     0            1      dist
#     >>> #   (,0)   (1, 2, 3)       0.1
#     >>> #   (,1)      (2, 3)       0.5
#     >>> #   ...
#     """
#     biparts = list(
#         tree.iter_bipartitions(
#             feature=feature,
#             include_internal_nodes=include_internal_nodes,
#             include_singleton_partitions=include_singleton_partitions,
#         )
#     )
#     if not include_singleton_partitions:
#         index = range(tree.ntips, tree.ntips + len(biparts))
#     else:
#         index = None
#     frame = pd.DataFrame(biparts, index=index)

#     # add dist info as unrooted tree
#     frame['dist'] = 0.
#     is_rooted = tree.is_rooted()
#     for idx in frame.index:
#         node = tree[idx]
#         if node._up.is_root() and is_rooted:
#             frame.loc[idx, "dist"] = sum(i._dist for i in node._up.children)
#         else:
#             frame.loc[idx, "dist"] = node._dist
#     return frame


# @add_subpackage_method(TreeEnumAPI)
# def get_bipartition_for_edge(
#     tree: ToyTree,
#     *edge: Query,
#     feature: Optional[str] = "name",
#     include_internal_nodes: bool = False,
# ) -> Tuple[Tuple, Tuple]:
#     """Return the bipartition for a selected Node/edge.

#     Parameters
#     ----------
#     tree: ToyTree
#         A ToyTree from which the bipartition will be found.
#     edge: Node
#         Select an edge on the tree by entering one or more Node queries
#         (Nodes, int Node idx labels, or str Node names) from which the
#         mrca Node will be selected. The edge connects Node and Node.up.
#     feature: str or None
#         Feature used to represent Nodes in the returned bipartition. If
#         None then Node objects are returned. Default is 'name'.
#     include_internal_nodes: bool
#         If True then all Nodes in the biparition are included in the
#         results, else only tip Nodes are included.

#     Examples
#     --------
#     >>> tree = toytree.tree("(a,b,((c,d)Y,(e,f)X)Z)R;")
#     >>> get_bipartition_for_edge(tree, "Y")
#     >>> # (('c', 'd'), ('a', 'b', 'e', 'f'))
#     >>> get_bipartition_for_edge(tree, "Y", exclude_internal_nodes=False)
#     >>> # (('c', 'd', 'Y'), ('a', 'b', 'e', 'f', 'X', 'Z', 'R'))
#     >>> get_bipartition_for_edge(tree, 'a', 'b', exclude_internal_nodes=False)
#     """
#     # get Node to represent selected edge on tree, if root was selected
#     # then just sample its first child since its the same split.
#     edge = tree.get_mrca_node(*edge)
#     if edge.is_root():
#         raise ToytreeError("Cannot select the root, it is not a resolved edge.")

#     # NOTE: SIMPLER CODE POSSIBLE BUT WAY SLOWER B/C ITERATION OVER ALL NODES
#     # for idx, bipart in enumerate(iter_bipartitions(**kwargs)):
#     #     if idx == edge.idx:
#     #         return bipart

#     # a format funtion to return a tuple of Nodes in the requested feature
#     if feature is not None:
#         def tformat(node_tuple):
#             return tuple(getattr(i, feature) for i in node_tuple)
#     else:
#         tformat = tuple

#     # build the bipart for selected edge.
#     if include_internal_nodes:
#         left = set(tree[edge.idx].get_descendants())
#         right = set(tree) - left - {tree.treenode}
#     else:
#         left = set(tree[edge.idx].get_leaves())
#         right = set(tree[:tree.ntips]) - left

#     # sort Node by names within each
#     left = sorted(left, key=_get_node_name_for_sorter)
#     right = sorted(right, key=_get_node_name_for_sorter)

#     # sort biparts to (shorter, longer), or by name if same len.
#     lenl = len(left)
#     lenr = len(right)
#     if lenl < lenr:
#         clade1, clade2 = tformat(left), tformat(right)
#     elif lenr < lenl:
#         clade1, clade2 = tformat(right), tformat(left)
#     else:
#         clade1, clade2 = sorted((left, right), key=lambda x: x[0].name)
#         clade1, clade2 = tformat(clade1), tformat(clade2)
#     return clade1, clade2


# @add_subpackage_method(TreeEnumAPI)
# def get_quartets_for_edge(
#     tree: ToyTree,
#     *edge: Query,
#     feature: Optional[str] = "name",
#     collapse: bool = False,
# ) -> List[Tuple[Tuple, Tuple]]:
#     """..."""
#     quartets = set()
#     bipart = get_bipartition_for_edge(tree, *edge, feature=None)
#     pairgen = itertools.product(
#         itertools.combinations(bipart[0], 2),
#         itertools.combinations(bipart[1], 2),
#     )
#     for tups in pairgen:
#         tup0 = sorted(tups[0], key=lambda x: x.name)
#         tup1 = sorted(tups[1], key=lambda x: x.name)
#         tups = sorted([tup0, tup1], key=lambda x: x[0].name)
#         qrt = tuple(tups[0] + tups[1])
#         # convert feature
#         if feature:
#             qrt = tuple(getattr(i, feature) for i in qrt)
#         # format func: return quartet as ((,),(,)) or (,,,).
#         if not collapse:
#             qrt = tuple((qrt[:2], qrt[2:]))
#         quartets.add(qrt)
#     # if not quartets:
#     #     logger.warning(f"No quartets exist for edge: {edge}")
#     return sorted(quartets)


# @add_subpackage_method(TreeEnumAPI)
# def get_quadripartitions_for_edge(
#     tree: ToyTree,
#     *edge: Query,
#     feature: Optional[str] = "name",
#     contract_partitions: bool = False,
#     include_internal_nodes: bool = False,
# ) -> List[Tuple[Tuple, Tuple]]:
#     """Return the bipartition for a selected Node/edge.

#     Parameters
#     ----------
#     tree: ToyTree
#         A ToyTree from which the bipartition will be found.
#     edge: Node
#         Select an edge on the tree by entering one or more Node queries
#         (Nodes, int Node idx labels, or str Node names) from which the
#         mrca Node will be selected. The edge connects Node and Node.up.
#     feature: str or None
#         Feature used to represent Nodes in the returned bipartition. If
#         None then Node objects are returned. Default is 'name'.

#     Examples
#     --------
#     >>> tree = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")
#     >>> sorted(get_quadripartitions_for_edge(tree, "X"))
#     >>> # [(...),
#     >>> #  (...),
#     >>> #  (...)]
#     """
#     # only internal edges form valid quadripartitions.
#     edge = tree.get_mrca_node(*edge)
#     if edge not in tree[tree.ntips:tree.nnodes - 1]:
#         raise ToytreeError(
#             f"Edge ({edge._idx}, {edge._up._idx if edge._up else None}) "
#             "does not form a quadripartition. Select an internal edge.")

#     # tree will be unrooted, so get edge as collection of leaves, or as
#     # collection of reciprocal set of leaves, if
#     tree = tree.unroot()
#     cache = {}

#     # build a cache of descendants for each Node.
#     for node in tree:

#         # if tip simply store its info
#         if node.is_leaf():
#             cache[node] = {node}
#             continue

#         # get tips from each child, and store union to this node
#         vals = [cache[i] for i in node.children]

#         # cache only the closest Node (exclude_internal_nodes ignored)
#         if contract_partitions:
#             cache[node] = {node}

#         # cache tip Nodes with or without internal Nodes
#         else:
#             # cache only the tip Nodes
#             if not include_internal_nodes:
#                 cache[node] = set.union(*vals)
#             # cache all nodes including internals
#             else:
#                 cache[node] = set.union(*vals) | {node}

#     # get set of all relevant nodes for set diffs below
#     if include_internal_nodes:
#         nodes = set(cache)
#     else:
#         nodes = set(tree.get_nodes()[:tree.ntips])

#     # iterate over internal nodes/edges in the tree
#     for node in tree[tree.ntips: tree.nnodes - 1]:

#         # get >= 2 sets of nodes for children below
#         below = [cache[i] for i in node.children]

#         # get >= 1 sets of nodes to represent >= 1 clades above.
#         above_left = [cache[sis] for sis in node.get_sisters()]

#         # if up is root then above_left contains all remaining clades
#         if node._up.is_root():
#             above = above_left
#             # TODO: need to expand partitions near root?
#         else:
#             # print(node, below, above_left)
#             above_right = nodes - {node, node._up} - set.union(*above_left + below)

#             # represent final clade by all its desc, or by its mrca.
#             if contract_partitions:
#                 above = above_left + [{tree.get_mrca_node(*above_right)}]
#             else:
#                 above = above_left + [above_right]

#         # add others
#         bpair = itertools.combinations(below, 2)
#         apair = itertools.combinations(above, 2)
#         for x1, x2 in itertools.product(bpair, apair):
#             # require all to exclude root in unrooted tree: ()
#             if all([x1[0], x1[1], x2[0], x2[1]]):
#                 if feature is None:
#                     yield ((x1[0], x1[1]), (x2[0], x2[1]))
#                 else:
#                     yield (
#                         tuple({getattr(j, feature) for j in i} for i in x1),
#                         tuple({getattr(j, feature) for j in i} for i in x2),
#                     )


# def _iter_quartet_sets(tree: ToyTree, feature: str = None) -> Iterator[Set]:
#     """Generator to yield all combinations of four tip Nodes.

#     This is simpler than toytree.enumerate.iter_quartets because it
#     does not try to return the resolution of quartets. It is thus
#     also much faster, but of less use.
#     """
#     # select function to format returned quartet set
#     if feature is None:
#         sformat = set
#     else:
#         def sformat(qrt) -> Set[str]:
#             return set(getattr(node, i) for node in qrt)
#     for qrt in itertools.combinations(sorted(tree)[:tree.ntips], 4):
#         yield sformat(qrt)


# def get_bipartitions_table(
#     tree: ToyTree,
#     include_internal_nodes: bool = False,
#     include_singleton_partitions: bool = False,
#     dtype: type = int,
# ) -> pd.DataFrame:
#     """Return a DataFrame with partitions in binary format.

#     Parameters
#     ----------

#     Example
#     -------
#     >>> toytree.rtree.unittree(5).enum.get_bipartitions_table()
#     >>>    r0   r1   r2   r3   r4
#     >>> 0   1    1    0    0    0
#     >>> 1   0    0    0    1    1

#     """
#     bits = list(
#         iter_bipartitions(
#             tree,
#             feature="idx",
#             include_internal_nodes=include_internal_nodes,
#             include_singleton_partitions=include_singleton_partitions,
#         )
#     )
#     cols = tree.nnodes - 1 if include_internal_nodes else tree.ntips
#     arr = np.zeros(shape=(len(bits), cols), dtype=dtype)
#     for idx, bit in enumerate(bits):
#         arr[idx, bit[0]] = 1
#     if include_singleton_partitions:
#         index = range(tree.ntips, tree.ntips + len(bits))
#     else:
#         index = None
#     return pd.DataFrame(arr, columns=tree.get_tip_labels(), index=index)


# @add_subpackage_method(TreeEnumAPI)
# def get_n_quartets(tree: ToyTree) -> int:
#     """Return the number of quartets..."""
#     qiter = itertools.combinations(range(tree.nnodes), 4)
#     return sum(1 for i in qiter)



# if __name__ == "__main__":

#     import toytree

#     BTREE = toytree.rtree.unittree(ntips=5, seed=123)
#     ITREE = toytree.rtree.unittree(ntips=5, seed=321)
#     UTREE = toytree.rtree.unittree(ntips=5, seed=123).unroot()
#     for TREE in (BTREE, ITREE, UTREE):
#         TREE.treenode.draw_ascii()

#         # assign internal node names for viewing results
#         for node in TREE:
#             if not node.is_leaf():
#                 node.name = "-".join(node.get_leaf_names()[::-1])

#         print("\nBIPART SETS-----------")
#         for i in iter_bipartitions(TREE, feature="name", sort=False):
#             print(i)

#         print("\nBIPARTS-----------")
#         for i in iter_bipartitions(TREE, feature='name'):
#             print(i)

#         print("\nBIPARTS W INTERNAL-----------")
#         for i in iter_bipartitions(TREE, feature='name', include_internal_nodes=True):
#             print(i)

#         print("\nBIPARTS w ROOT indicated-----------")
#         for i in iter_bipartitions(TREE, feature='name', indicate_root=True):
#             print(i)

#         print("\nQUARTETS-----------")
#         for i in iter_quartets(TREE, collapse=True):
#             print(i)

#         print("\nQUADRIPART SETS-----------")
#         for i in iter_edge_quadripartition_sets(TREE):
#             print(i)

#         print("\nQUADRIPART SETS CONTRACTED-----------")
#         for i in iter_edge_quadripartition_sets(TREE, contract_partitions=True):
#             print(i)

#         print("\nQUADRIPARTITIONS-----------")
#         for i in iter_quadripartitions(TREE, feature="name", collapse=True):
#             print(i)

#         print("\nBIPART FOR EDGE 1-----------")
#         print(get_bipartition_for_edge(TREE, 1))

#         print("\nBIPART FOR EDGE 5-----------")
#         print(get_bipartition_for_edge(TREE, 5))

#         print("\nBIPART FOR EDGE 5 w INTERNAL-----------")
#         print(get_bipartition_for_edge(TREE, 5, include_internal_nodes=True))

#         print("\nQUARTETS FOR EDGE 1-----------")
#         print(get_quartets_for_edge(TREE, 1))

#         print("\nQUARTETS FOR EDGE 5-----------")
#         print(get_quartets_for_edge(TREE, 5))

#         print("\nQUADPARTS FOR EDGE 5-----------")
#         # print(get_quadripartitions_for_edge(TREE, 5, include_internal_nodes=True))

#         print("===================================================")

#     raise SystemExit()
#     # does every placement of the root yield a different topology?
#     for edge in UTREE:
#         if edge.up:
#             t = UTREE.root(edge)
#             t.treenode.draw_ascii()
#             # print(list(iter_bipartitions(t, 'name', exclude_root=False)))


#     # FIXME: make None work.
#     # for i in iter_bipartitions(TREE, feature=None):
#         # print(i)

