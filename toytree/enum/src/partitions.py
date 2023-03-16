#!/usr/bin/env python

"""Methods for extracting partitions from trees.

Examples
--------
Methods for examining splits on a tree:

Get sets of Nodes on either side of each edge in a tree.
>>> tree.iter_edge_bipartition_sets()      # ({0, 1}, {2, 3, 4}), ...

Get sets of Nodes from the four subclades of each edge in a tree.
>>> tree.iter_edge_quadripartition_sets()  # (({0}, {1}), ({2}, {3, 4})), ...

Get name-ordered tuples of Nodes on either side of each edge in a tree.
>>> tree.iter_bipartitions()               # ((0, 1), (2, 3, 4)), ...

Get name-ordered tuples of Nodes for each quartet induced by bipartitions in a tree.
>>> tree.iter_quartets()                   # ((0, 1), (2, 3)), ...

Get name-ordered tuples of Nodes for each quartet induced by quadripartitions in a tree.
>>> tree.iter_quadripartitions()             # ((0, 1), (2, 3)), ...

Get fast unordered sets of all combinations of 4 tip Nodes in a tree
>>> tree._iter_quartet_sets()              # {0, 1, 2, 3}, ...

Get number of quartets induced by the splits in a tree.
>>> tree.get_n_quartets()                  # 5

Get bipartition for a specific node/edge.
>>> tree.get_bipartition_for_edge(tree, 1)  # ((0, 1), (2, 3, 4)), ...

Get quartets for a specific node/edge.
>>> tree.get_quartets_for_edge(tree, 1)      # [((0, 1), (2, 3)), ...]

Get quadripartitions for a specific node/edge.
>>> tree.get_quadripartitions_for_edge(tree, 1)  # [((0, 1), (2, 3)), ...]

TODO
----
after revisiting the use of bipartitions etc in distance methods
come back to this code and decide if tuples or sets should be used,
or both as an option.
"""

# pylint: disable='too-many-branches'

from typing import TypeVar, Iterator, Tuple, Optional, Set, List
import itertools
from loguru import logger
from toytree.utils import ToytreeError

logger = logger.bind(name="toytree")
ToyTree = TypeVar("ToyTree")
Node = TypeVar("Node")
Query = TypeVar("Query")


def _get_node_name_for_sorter(node) -> str:
    """Returns node name to use while sorting tip and internal nodes.

    To return splits that contain nodes that are ordered consistently
    we use node names for tips, and use temporary names for internal
    nodes built from the names of their descendant leaves. This func
    is used in iter_bipartitions.

    Note
    ----
    Note that the sorting of internal Node names is different between
    trees with different rootings. This is why auto-generated internal
    node names cannot create consistent ordering. This is also why we
    do not include internal nodes when creating bipartitions for tree
    comparisons/distance metrics. Note that if two trees did have names
    set for all internal Nodes then we could create a consistent
    ordering, but that is very rarely the case, and so the use of
    internal names at all is commented out (not used) here.
    """
    if node.is_leaf():
        return node.name
    # if node.name:
        # return node.name
    # else:
    return "-".join(node.get_leaf_names()[::-1])


def iter_edge_bipartition_sets(
    tree: ToyTree,
    feature: Optional[str] = "name",
    include_singleton_partitions: bool = False,
    include_internal_nodes: bool = False,
    indicate_root: bool = False,
) -> Iterator[Tuple[Set[Node], Set[Node]]]:
    """Generator to yield bipartitions as tuples of two sets of Nodes.

    The order in which bipartitions are yielded depends on the tree
    topology and rooting. Each bipartition set is a tuple of two sets
    representing (either all or only the tip) Nodes on either side of
    an edge (split) in the tree. The two sets are not ordered within
    the tuple. To generate bipartitions that are consistently sorted
    by the node names see the function `.iter_bipartitions`.

    Parameters
    ----------
    feature: str or None
        Option to represent Nodes in bipartitions by a feature, such
        as 'name' or 'idx'. If None then Node objects are returned.
    include_singleton_partitions: bool
        If True then singleton splits (e.g., (A | B,C,D)) are included
        in the result. By default these are excluded since it is
        implicit that one exists for every tip Node in a tree.
    include_internal_nodes: bool
        Default is to only show tip Nodes on either side of a
        bipartition, but internal Nodes can be included as well. In
        this case the results are easier to interpret if internal Nodes
        have names assigned, else you can set the 'feature' arg to
        None, or 'idx', to return Node objects, or a unique feature.
    indicate_root: bool
        If True an *extra* bipartition is returned to indicate the
        location of the root Node. This bipartition will be a repeat of
        an existing bipart, since the root is not an actual split, but
        this is still useful for comparing entire collections of 
        bipartitions since the each will be unique to a rooted topology.
        Note that if True the root split will be returned even if it is
        a singleton split and include_singletons is set to False.

    Examples
    --------
    >>> newick = "(((a,b)X,((c,d)Y,e)Z)R;"
    >>> tree = toytree.tree(newick)

    >>> sorted(iter_edge_bipartition_sets(tree))
    >>> # (({a,b}),({c,d,e}))
    >>> # (({a,b,e}),({c,d}))

    >>> sorted(iter_edge_bipartition_sets(tree, include_internal_nodes=True))
    >>> # (({a,b,X}),({c,d,e,Y,Z}))
    >>> # (({a,b,X,e,Z}),({c,d,Y}))
    """
    # store cache of desc below each node to reduce traversals
    cache = {}

    # nodes set to iterate over. Do not include the root.
    node_set = set(tree)
    topnode = tree.nnodes - 1

    # do not include root node in node_set if tree is rooted.
    if tree.is_rooted():
        node_set -= {tree.treenode}
        topnode -= 1

    # If indicate_root then include both root children, else only one.
    if indicate_root:
        topnode += 1

    # iterate over all nodes in idx order building cache as it goes.
    for node in tree[:topnode]:
        if node.is_leaf():
            below = cache[node] = {node}
            if not include_singleton_partitions:
                continue
        else:
            below = set.union(*([{node}] + [cache[i] for i in node.children]))
            cache[node] = below

        # get all nodes not under this split
        other = node_set - cache[node]

        # if excluding internal Nodes
        if not include_internal_nodes:
            below = set(i for i in below if i._idx < tree.ntips)
            other = set(i for i in other if i._idx < tree.ntips)

        # yield biparts except at root in unrooted trees: ({}, {all})
        if below and other:
            if feature is None:
                yield below, other
            else:
                yield (
                    {getattr(i, feature) for i in below},
                    {getattr(i, feature) for i in other},
                )


def iter_bipartitions(
    tree: ToyTree,
    feature: Optional[str] = "name",
    include_singleton_partitions: bool = False,
    include_internal_nodes: bool = False,
    indicate_root: bool = False,
) -> Iterator[Tuple[Tuple[str], Tuple[str]]]:
    """Generator of ordered bipartitions (info about splits in a tree).

    The order in which bipartitions are yielded depends on the tree
    topology and rooting, but the order of nodes within each partition
    is consistently sorted by Node names which allows for comparing
    bipartitions between trees. Here, each bipartition is a tuple of
    two tuples representing (either all or only the tip) Nodes on
    either side of an edge (split) in the tree. For example, the tuple
    `(('r0', 'r1'), ('r2', 'r3'))` indicates a split in the tree
    separating tip Nodes 'r0' and 'r1' from 'r2' and 'r3'.

    Bipartitions are used to in many tree distance metrics (see
    `toytree.distance`) and also to generate a unique hash of tree
    topologies in `get_topology_id`.

    Parameters
    ----------
    feature: str
        Feature to return to represent Nodes on either side of a
        bipartition. Default is "name". None will return Node objects.
        Any other Node feature, such as "idx" can also be used, but
        note that idx labels change depending on topology. Regardless
        of this argument the Nodes are always ordered by names.
    include_singleton_partitions: bool
        If True then singleton splits (e.g., (A | B,C,D)) are included
        in the result. By default these are excluded since it is
        implicit that one exists for every tip Node in a tree.
    include_internal_nodes: bool
        Default is to only show tip Nodes on either side of a
        bipartition, but internal Nodes can be included as well. In
        this case the results are easier to interpret if internal Nodes
        have names assigned, else you can set the 'feature' arg to
        None, or 'idx', to return Node objects, or a unique feature.
    indicate_root: bool
        If True an *extra* bipartition is returned to indicate the
        location of the root Node. This bipartition will be a repeat of
        an existing bipart, since the root is not an actual split, but
        this is still useful for comparing entire collections of 
        bipartitions since the each will be unique to a rooted topology.
        Note that if True the root split will be returned even if it is
        a singleton split and include_singletons is set to False.

    Examples
    --------
    >>> tree = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")
    >>> sorted(tree.iter_bipartitions())
    >>> # [(('a', 'b'), ('c', 'd', 'e', 'f')),
    >>> #  (('c', 'd'), ('a', 'b', 'e', 'f')),
    >>> #  (('e', 'f'), ('a', 'b', 'c', 'd'))]
    """
    # a format funtion to return a tuple of Nodes in the requested feature
    if feature is not None:
        def tformat(node_tuple):
            return tuple(getattr(i, feature) for i in node_tuple)
    else:
        tformat = tuple

    # iterate over pairs of Node sets for each edge
    kwargs = dict(
        tree=tree, feature=None,
        include_singleton_partitions=include_singleton_partitions,
        include_internal_nodes=include_internal_nodes,
        indicate_root=indicate_root,
    )
    for below, other in iter_edge_bipartition_sets(**kwargs):
        # sort biparts by NAME within each side. Note: idx labels (or
        # any kind of traversal-based sort) is not used here b/c we
        # want the same ordered biparts from a tree regardless of its
        # rooting or Node rotations! This uses a func that makes tmp
        # node names of internal nodes based on their leaves.
        below = sorted(below, key=_get_node_name_for_sorter)
        other = sorted(other, key=_get_node_name_for_sorter)

        # sort biparts to (shorter, longer), or by name if same len.
        lenb = len(below)
        leno = len(other)
        if lenb < leno:
            clade1, clade2 = tformat(below), tformat(other)
        elif leno < lenb:
            clade1, clade2 = tformat(other), tformat(below)
        else:
            clade1, clade2 = sorted((other, below), key=lambda x: x[0].name)
            clade1, clade2 = tformat(clade1), tformat(clade2)
        yield clade1, clade2


def iter_edge_quadripartition_sets(
    tree: ToyTree,
    feature: Optional[str] = "name",
    contract_partitions: bool = False,
    include_internal_nodes: bool = False,
) -> Iterator[Tuple[Tuple[Set, Set], Tuple[Set, Set]]]:
    """Yield a tuple of sets of tips for each quadripartition.

    Edge sets are returned as (({e0},{e1}), ({e2},{e3})) representing
    sets of (tip) Nodes descending from each of the four edges
    subtending a focal edge, where the focal edge splits e0,e1 from
    e2,e3. Note the use of sets to indicate that the items are not
    sorted. Rooting only affects the order in which quadripartition
    sets are yielded.

    Parameters
    ----------
    tree: ToyTree
        A tree to extract edge sets from.
    feature: str or None
        Feature to represent Nodes in returned sets. Default is 'name'
        to use Node name strings. None will return Node objects.
    contract_partitions: bool
        If True then each partition is contracted to show only the
        first Node closest to the edge.
    include_internal_nodes: bool
        If True then all nodes in each partition are shown, whether it
        is internal or a tip Node. If False then only tips are shown.
        Note: This option is overriden if contract_partitions=True in
        which case the closest Node is shown whether or not it is a tip.

    Examples
    --------
    >>> newick = "((a,b)X,((c,d)Y,e)Z)R;"
    >>> tree = toytree.tree(newick)

    >>> sorted(iter_edge_quadripartition_sets(tree))
    >>> # (({a},{b}),({c,d},{e}))
    >>> # (({a,b},{e}),({c},{d}))

    >>> kwargs = dict(exclude_internal_nodes=False)
    >>> sorted(iter_edge_quadripartition_sets(tree, **kwargs))
    >>> # (({a},{b}),({c,d,Y},{e}))
    >>> # (({a,b,X},{e}),({c},{d}))

    >>> kwargs = dict(expand_partitions=False)
    >>> sorted(iter_edge_quadripartition_sets(tree, **kwargs))
    >>> # (({a},{b}),({Y},{e}))
    >>> # (({X},{e}),({c},{d}))
    """
    # tree = tree.unroot()
    cache = {}

    # build a cache of descendants for each Node.
    topnode = tree.nnodes - 1 if tree.is_rooted() else tree.nnodes
    for node in tree[:topnode]:  # [:-1]:#.traverse("idxorder"):

        # if tip simply store its info
        if node.is_leaf():
            cache[node] = {node}
            continue

        # get tips from each child, and store union to this node
        vals = [cache[i] for i in node.children]

        # cache only the closest Node (exclude_internal_nodes ignored)
        if contract_partitions:
            cache[node] = {node}

        # cache tip Nodes with or without internal Nodes
        else:
            # cache only the tip Nodes
            if not include_internal_nodes:
                cache[node] = set.union(*vals)
            # cache all nodes including internals
            else:
                cache[node] = set.union(*vals) | {node}

    #print('x', cache[tree.get_nodes("X")[0]]) TODO
    # get set of all relevant nodes for set diffs below
    if include_internal_nodes:
        nodes = set(cache)
    else:
        nodes = set(tree.get_nodes()[:tree.ntips])

    # iterate over internal nodes/edges in the tree
    topnode = tree.nnodes - 2 if tree.is_rooted() else tree.nnodes - 1
    for node in tree[tree.ntips: topnode]:  # tree.nnodes - 1]:
        # get >= 2 sets of nodes for children below
        below = [cache[i] for i in node.children]

        # if up is root then above_left contains all remaining clades
        if node._up.is_root():
            above = []
            for sis in node.get_sisters():
                sis_children = sis._children
                if sis_children:
                    for sis_child in sis_children:
                        above.append(cache[sis_child])
                else:
                    above.append(cache[sis])
            # above = [cache[sis_child] for sis in node.get_sisters()]    
            # above = above_left
            # above = [set(itertools.chain(*above_left))]
            # above_right = []
            # TODO: need to expand partitions near root?
        else:
            # print(node, below, above_left)
            # get >= 1 sets of nodes to represent >= 1 clades above.
            above_left = [cache[sis] for sis in node.get_sisters()]    
            above_right = nodes - {node, node._up} - set.union(*above_left + below)

            # represent final clade by all its desc, or by its mrca.
            if contract_partitions:
                above = above_left + [{tree.get_mrca_node(*above_right)}]
            else:
                above = above_left + [above_right]

        print("node", node, below, above, "\n") # above_left, above_right, "\n")
        # add others
        bpair = itertools.combinations(below, 2)
        apair = itertools.combinations(above, 2)
        for x1, x2 in itertools.product(bpair, apair):
            # require all to exclude root in unrooted tree: ()
            if all([x1[0], x1[1], x2[0], x2[1]]):
                if feature is None:
                    yield ((x1[0], x1[1]), (x2[0], x2[1]))
                else:
                    yield (
                        tuple({getattr(j, feature) for j in i} for i in x1),
                        tuple({getattr(j, feature) for j in i} for i in x2),
                    )


def iter_quartets(
    tree: ToyTree,
    feature: Optional[str] = 'name',
    collapse: bool = False,
) -> Iterator:
    """Generator to yield quartets induced by edges in a tree.

    This yields all quartets (4-sample subtrees) that exist within
    a larger tree. The set of possible quartets is not affected
    by tree rooting, but is affected by collapsed edges (polytomies),
    which reduce the number of quartets.

    Quartets are returned as tuples of tuples, where e.g.,
    (('a', 'b'), ('c', 'd')) implies a `ab|cd` quartet. The order
    in which quartets are yielded depends on the topology and rooting,
    and can be re-sorted after, but the order of Nodes within each
    tuple is sorted consistently by Node names. The arg collapse=True
    can be used to simplify the returned format to a single tuple.

    Parameters
    ----------
    feature: str
        Feature used to represent Nodes on either side of bipartitions.
        Default is "name". None will return Node objects. Other Node
        features can be used but be aware if using quartets to compare
        among trees that 'idx' changes depending on topology, and other
        features may not be unique among Nodes.
    collapse: bool
        If True then quartets are returned as a single tuple, e.g.,
        (0, 1, 2, 3), else they are returned as a tuple of tuples,
        e.g., ((0, 1), (2, 3)). In either case, the induced split is
        implied to occur in the middle, e.g., 0,1 vs 2,3.

    Example
    -------
    >>> tree = toytree.rtree.unittree(5, seed=123)
    >>> sorted(tree.iter_quartets())
    >>> # (('r0', 'r1'), ('r2', 'r3'))
    >>> # (('r0', 'r1'), ('r2', 'r4'))
    >>> # (('r0', 'r1'), ('r3', 'r4'))
    >>> # (('r0', 'r2'), ('r3', 'r4'))
    >>> # (('r1', 'r2'), ('r3', 'r4'))
    """
    # find quartets induced by splits in the tree. This is necessary
    # compared to a simple call of `itertools.combinations(names, 4)`
    # because we indicate which pair of nodes is on which side of each
    # split. We also reduce number of quartets if any polytomies exist.
    observed = set([])
    for below, above in iter_bipartitions(tree, None):
        # generator to sample 2 from either side of each bipart
        pairgen = itertools.product(
            itertools.combinations(below, 2),
            itertools.combinations(above, 2),
        )
        for tups in pairgen:
            # sort within each pair, then sort the two pairs. Nodes are
            # only sorted by names (not idx or other) b/c relationships
            # of names to splits is consistent, unlike idx. Sorting by
            # names and returning Nodes is safest in case duplicate
            # names are present.
            tup0 = sorted(tups[0], key=lambda x: x.name)
            tup1 = sorted(tups[1], key=lambda x: x.name)
            tups = sorted([tup0, tup1], key=lambda x: x[0].name)
            qrt = tuple(tups[0] + tups[1])

            # skip sorted quartets that have been observed.
            if qrt not in observed:
                observed.add(qrt)

                # convert from Node objects to names or other features
                if feature:
                    qrt = tuple(getattr(i, feature) for i in qrt)

                # format func: return quartet as ((,),(,)) or (,,,).
                if not collapse:
                    yield tuple((qrt[:2], qrt[2:]))
                else:
                    yield qrt
    del observed


def iter_quadripartitions(
    tree: ToyTree,
    feature: Optional[str] = "name",
    collapse: bool = False,
) -> Iterator:
    r"""Generator yields name-sorted quadripartitions induced by each edge.

    Quadripartitions are samples of 4 tips in a tree that are drawn
    from the four subclades induced by an edge in a tree. This 
    collection of splits is a subset of the number of *quartets* in a
    tree, which can be generated using the `iter_quartets` function. 
    Whereas quartets represent combinations of two samples from either
    side of bipartition, this function returns combinations of samples
    drawn from the four clades of a quadripartition induced by a split
    in the tree. The difference between these two collections is easy
    to see on larger trees where this set is much smaller than the
    number of quartets.

    Example
    -------
    >>> tree = toytree.tree("((a,b)X,((c,d)Y,e)Z)R;")
    >>> sorted(toytree.enumerate.iter_quadripartitions(tree))
    >>> [(('a', 'b'), ('c', 'e')),
    >>>  (('a', 'b'), ('d', 'e')),
    >>>  (('a', 'e'), ('c', 'd')),
    >>>  (('b', 'e'), ('c', 'd'))]

    See Also
    --------
    - `toytree.enumerate.iter_quartets`
    - `ToyTree.iter_quartets`
    """
    for split in iter_edge_quadripartition_sets(tree, feature=None):
        for tips in itertools.product(*split[0] + split[1]):
            tup0 = sorted((tips[0], tips[1]), key=lambda x: x.name)
            tup1 = sorted((tips[2], tips[3]), key=lambda x: x.name)
            tups = sorted((tup0, tup1), key=lambda x: x[0].name)
            qrt = tuple(tups[0] + tups[1])

            if feature:
                qrt = tuple(getattr(i, feature) for i in qrt)

            if collapse:
                yield (qrt[0], qrt[1], qrt[2], qrt[3])
            else:
                yield (qrt[0], qrt[1]), (qrt[2], qrt[3])


def get_bipartition_for_edge(
    tree: ToyTree,
    *edge: Query,
    feature: Optional[str] = "name",
    include_internal_nodes: bool = False,
) -> Tuple[Tuple, Tuple]:
    """Return the bipartition for a selected Node/edge.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree from which the bipartition will be found.
    edge: Node
        Select an edge on the tree by entering one or more Node queries
        (Nodes, int Node idx labels, or str Node names) from which the
        mrca Node will be selected. The edge connects Node and Node.up.
    feature: str or None
        Feature used to represent Nodes in the returned bipartition. If
        None then Node objects are returned. Default is 'name'.
    include_internal_nodes: bool
        If True then all Nodes in the biparition are included in the
        results, else only tip Nodes are included.

    Examples
    --------
    >>> tree = toytree.tree("(a,b,((c,d)Y,(e,f)X)Z)R;")
    >>> get_bipartition_for_edge(tree, "Y")
    >>> # (('c', 'd'), ('a', 'b', 'e', 'f'))
    >>> get_bipartition_for_edge(tree, "Y", exclude_internal_nodes=False)
    >>> # (('c', 'd', 'Y'), ('a', 'b', 'e', 'f', 'X', 'Z', 'R'))
    >>> get_bipartition_for_edge(tree, 'a', 'b', exclude_internal_nodes=False)
    """
    # get Node to represent selected edge on tree, if root was selected
    # then just sample its first child since its the same split.
    edge = tree.get_mrca_node(*edge)
    if edge.is_root():
        raise ToytreeError("Cannot select the root, it is not a resolved edge.")

    # NOTE: SIMPLER CODE POSSIBLE BUT WAY SLOWER B/C ITERATION OVER ALL NODES
    # for idx, bipart in enumerate(iter_bipartitions(**kwargs)):
    #     if idx == edge.idx:
    #         return bipart

    # a format funtion to return a tuple of Nodes in the requested feature
    if feature is not None:
        def tformat(node_tuple):
            return tuple(getattr(i, feature) for i in node_tuple)
    else:
        tformat = tuple

    # build the bipart for selected edge.
    if include_internal_nodes:
        left = set(tree[edge.idx].get_descendants())
        right = set(tree) - left - {tree.treenode}
    else:
        left = set(tree[edge.idx].get_leaves())
        right = set(tree[:tree.ntips]) - left

    # sort Node by names within each
    left = sorted(left, key=_get_node_name_for_sorter)
    right = sorted(right, key=_get_node_name_for_sorter)

    # sort biparts to (shorter, longer), or by name if same len.
    lenl = len(left)
    lenr = len(right)
    if lenl < lenr:
        clade1, clade2 = tformat(left), tformat(right)
    elif lenr < lenl:
        clade1, clade2 = tformat(right), tformat(left)
    else:
        clade1, clade2 = sorted((left, right), key=lambda x: x[0].name)
        clade1, clade2 = tformat(clade1), tformat(clade2)
    return clade1, clade2


def get_quartets_for_edge(
    tree: ToyTree,
    *edge: Query,
    feature: Optional[str] = "name",
    collapse: bool = False,
) -> List[Tuple[Tuple, Tuple]]:
    """..."""
    quartets = set()
    bipart = get_bipartition_for_edge(tree, *edge, feature=None)
    pairgen = itertools.product(
        itertools.combinations(bipart[0], 2),
        itertools.combinations(bipart[1], 2),
    )
    for tups in pairgen:
        tup0 = sorted(tups[0], key=lambda x: x.name)
        tup1 = sorted(tups[1], key=lambda x: x.name)
        tups = sorted([tup0, tup1], key=lambda x: x[0].name)
        qrt = tuple(tups[0] + tups[1])
        # convert feature
        if feature:
            qrt = tuple(getattr(i, feature) for i in qrt)
        # format func: return quartet as ((,),(,)) or (,,,).
        if not collapse:
            qrt = tuple((qrt[:2], qrt[2:]))
        quartets.add(qrt)
    # if not quartets:
    #     logger.warning(f"No quartets exist for edge: {edge}")
    return sorted(quartets)


def get_quadripartitions_for_edge(
    tree: ToyTree,
    *edge: Query,
    feature: Optional[str] = "name",
    contract_partitions: bool = False,
    include_internal_nodes: bool = False,
) -> List[Tuple[Tuple, Tuple]]:
    """Return the bipartition for a selected Node/edge.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree from which the bipartition will be found.
    edge: Node
        Select an edge on the tree by entering one or more Node queries
        (Nodes, int Node idx labels, or str Node names) from which the
        mrca Node will be selected. The edge connects Node and Node.up.
    feature: str or None
        Feature used to represent Nodes in the returned bipartition. If
        None then Node objects are returned. Default is 'name'.

    Examples
    --------
    >>> tree = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")
    >>> sorted(get_quadripartitions_for_edge(tree, "X"))
    >>> # [(...),
    >>> #  (...),
    >>> #  (...)]
    """
    # only internal edges form valid quadripartitions.
    edge = tree.get_mrca_node(*edge)
    if edge not in tree[tree.ntips:tree.nnodes - 1]:
        raise ToytreeError(
            f"Selected edge ({edge}-{edge.up}) does not form any quadripartitions.")

    # tree will be unrooted, so get edge as collection of leaves, or as
    # collection of reciprocal set of leaves, if
    tree = tree.unroot()
    cache = {}

    # build a cache of descendants for each Node.
    for node in tree.traverse("idxorder"):

        # if tip simply store its info
        if node.is_leaf():
            cache[node] = {node}
            continue

        # get tips from each child, and store union to this node
        vals = [cache[i] for i in node.children]

        # cache only the closest Node (exclude_internal_nodes ignored)
        if contract_partitions:
            cache[node] = {node}

        # cache tip Nodes with or without internal Nodes
        else:
            # cache only the tip Nodes
            if not include_internal_nodes:
                cache[node] = set.union(*vals)
            # cache all nodes including internals
            else:
                cache[node] = set.union(*vals) | {node}

    # get set of all relevant nodes for set diffs below
    if include_internal_nodes:
        nodes = set(cache)
    else:
        nodes = set(tree.get_nodes()[:tree.ntips])

    # iterate over internal nodes/edges in the tree
    for node in tree[tree.ntips: tree.nnodes - 1]:

        # get >= 2 sets of nodes for children below
        below = [cache[i] for i in node.children]

        # get >= 1 sets of nodes to represent >= 1 clades above.
        above_left = [cache[sis] for sis in node.get_sisters()]

        # if up is root then above_left contains all remaining clades
        if node._up.is_root():
            above = above_left
            # TODO: need to expand partitions near root?
        else:
            # print(node, below, above_left)
            above_right = nodes - {node, node._up} - set.union(*above_left + below)

            # represent final clade by all its desc, or by its mrca.
            if contract_partitions:
                above = above_left + [{tree.get_mrca_node(*above_right)}]
            else:
                above = above_left + [above_right]

        # add others
        bpair = itertools.combinations(below, 2)
        apair = itertools.combinations(above, 2)
        for x1, x2 in itertools.product(bpair, apair):
            # require all to exclude root in unrooted tree: ()
            if all([x1[0], x1[1], x2[0], x2[1]]):
                if feature is None:
                    yield ((x1[0], x1[1]), (x2[0], x2[1]))
                else:
                    yield (
                        tuple({getattr(j, feature) for j in i} for i in x1),
                        tuple({getattr(j, feature) for j in i} for i in x2),
                    )


def _iter_quartet_sets(tree: ToyTree, feature: str = None) -> Iterator[Set]:
    """Generator to yield all combinations of four tip Nodes.

    This is simpler than toytree.enumerate.iter_quartets because it
    does not try to return the resolution of quartets. It is thus
    also much faster, but of less use.
    """
    # select function to format returned quartet set
    if feature is None:
        sformat = set
    else:
        def sformat(qrt) -> Set[str]:
            return set(getattr(node, i) for node in qrt)
    for qrt in itertools.combinations(sorted(tree)[:tree.ntips], 4):
        yield sformat(qrt)


def get_n_quartets(tree: ToyTree) -> int:
    """Return the number of quartets..."""
    qiter = itertools.combinations(range(tree.nnodes), 4)
    return sum(1 for i in qiter)


if __name__ == "__main__":

    import toytree

    BTREE = toytree.rtree.unittree(ntips=5, seed=123)
    ITREE = toytree.rtree.unittree(ntips=5, seed=321)
    UTREE = toytree.rtree.unittree(ntips=5, seed=123).unroot()
    for TREE in (BTREE, ITREE, UTREE):
        TREE.treenode.draw_ascii()

        # assign internal node names for viewing results
        for node in TREE:
            if not node.is_leaf():
                node.name = "-".join(node.get_leaf_names()[::-1])

        print("\nBIPART SETS-----------")
        for i in iter_edge_bipartition_sets(TREE):
            print(i)

        print("\nBIPARTS-----------")
        for i in iter_bipartitions(TREE, feature='name'):
            print(i)

        print("\nBIPARTS W INTERNAL-----------")
        for i in iter_bipartitions(TREE, feature='name', include_internal_nodes=True):
            print(i)

        print("\nBIPARTS w ROOT indicated-----------")
        for i in iter_bipartitions(TREE, feature='name', indicate_root=True):
            print(i)

        print("\nQUARTETS-----------")
        for i in iter_quartets(TREE, collapse=True):
            print(i)

        print("\nQUADRIPART SETS-----------")
        for i in iter_edge_quadripartition_sets(TREE):
            print(i)

        print("\nQUADRIPART SETS CONTRACTED-----------")
        for i in iter_edge_quadripartition_sets(TREE, contract_partitions=True):
            print(i)

        print("\nQUADRIPARTITIONS-----------")
        for i in iter_quadripartitions(TREE, feature="name", collapse=True):
            print(i)

        print("\nBIPART FOR EDGE 1-----------")
        print(get_bipartition_for_edge(TREE, 1))

        print("\nBIPART FOR EDGE 5-----------")
        print(get_bipartition_for_edge(TREE, 5))

        print("\nBIPART FOR EDGE 5 w INTERNAL-----------")
        print(get_bipartition_for_edge(TREE, 5, include_internal_nodes=True))

        print("\nQUARTETS FOR EDGE 1-----------")
        print(get_quartets_for_edge(TREE, 1))

        print("\nQUARTETS FOR EDGE 5-----------")
        print(get_quartets_for_edge(TREE, 5))

        print("\nQUADPARTS FOR EDGE 5-----------")
        # print(get_quadripartitions_for_edge(TREE, 5, include_internal_nodes=True))

        print("===================================================")

    raise SystemExit()
    # does every placement of the root yield a different topology?
    for edge in UTREE:
        if edge.up:
            t = UTREE.root(edge)
            t.treenode.draw_ascii()
            # print(list(iter_bipartitions(t, 'name', exclude_root=False)))


    # FIXME: make None work.
    # for i in iter_bipartitions(TREE, feature=None):
        # print(i)

