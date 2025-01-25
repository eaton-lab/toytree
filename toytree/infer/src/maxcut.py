#!/usr/bin/env python

"""Maxcut algorithm.

TODO
----
- see MQLib for new heuristics to solve max-cut given the graph,
which we construct here.

This is an implementation of the QMC (quartet maxcut) algorithm of
Snir and Rao for fast inference of a supertree from weighted quartets.

The smallest informative piece of phylogenetic information is a quartet
tree (quartet), which is a tree with four tips separated by a single
internal edge. A quartet can be written in newick as "((a,b),(c,d));"
or abbreviated as "ab|cd". Note that this does not mean that 'a' is
more closely related to 'b' than to 'c', only that there is an edge
separating them.

The goal of a supertree construction from quartet trees, or quartet
amalgamation, is to find the tree that is concordant with the greatest
number of input quartet trees. Finding this tree is a NP-hard problem
(Steel 1992).

Development notes
-----------------
- See docs/consensus2.ipynb notebook for current embedding implementation
- For small ntaxa the non-embedding maxcut search is working.
- Have not yet implemented building the tree from the finished set of cuts.

References
----------
The first quartet inference paper
- Snir & Rao 2012 "Quartet MaxCut: A fast algorithm for amalgamating quartet trees".
  https://doi.org/10.1016/j.ympev.2011.06.021

A paper that describes the embedding approach in more detail.
- Snir & Rao 2006 "Using Max Cut to Enhance Rooted Trees Consistency"
  IEEE/ACM Transactions on Computational Biology and Bioinformatics,
  doi: 10.1109/TCBB.2006.58.

A paper that describes the maxcut algorithm in more detail.
- Snir & Rao 2010 "Quartets MaxCut: A Divide and Conquer Quartets Algorithm".
  IEEE/ACM Transactions on Computational Biology and Bioinformatics,
"""

from typing import Union
import itertools
from collections import defaultdict
import numpy as np
import toyplot
from toytree.core import ToyTree, Node
from toytree.core.multitree import MultiTree
from loguru import logger
logger = logger.bind(name="toytree")

# __all__ = [
#     # "get_supertree_from_quartets_by_qmc"
#     # "get_supertree_from_quartets_by_qmc"
#     # "get_quartet_graph",
#     # "get_maxcut_tree_from_quartet_sets",
#     # "get_maxcut_tree_from_multitree",
# ]


##################################################################

def get_weighted_quartets_from_trees(
    trees: Union[MultiTree, list[ToyTree]],
    normalize: bool = False,
) -> dict[tuple[frozenset,frozenset],float]:
    """Return {quartet: weight, ...} from a sequence of trees.

    The weight of each quartet is calculated as the number or
    proportion of trees that contain that quartet.

    Parameters
    ----------
    trees: MultiTree | Sequence[ToyTree]
        An input set of one or more ToyTree objects.
    normalize_by_ntrees: bool
        If True weights are returned as a frequency instead of a count.
    """
    # build weighted graph from quartets
    qrt_counts = {}
    for tree in trees:
        for qrt in tree.enum.iter_quartets(type=frozenset, sort=True):
            if qrt not in qrt_counts:
                qrt_counts[qrt] = 1
            else:
                qrt_counts[qrt] += 1

    # get weights as a proportion.
    if normalize:
        for qrt in qrt_counts:
            qrt_counts[qrt] = qrt_counts[qrt] / len(trees)
    return qrt_counts


##################################################################

def get_graph_from_quartets_qmc(
    quartets: dict[tuple[frozenset,frozenset],float],
    use_weights: bool = False,
) -> dict[frozenset, list[int, int]]:
    """Return {frozenset: weight} for each edge in a graph built from
    quartets where weight is the mean of the quartets that included
    each edge as a partition.

    - good edges are assigned a uniform positive weight (1)
    - bad edges are assigned a -alpha parameter weight.

    Parameters
    ----------
    use_weights: ...
    """
    if use_weights:
        raise NotImplementedError("TODO")
    graph = {}
    # iterate over quartets
    for qrt in quartets:
        # set edge weights between tips on different sides of the quartet (good edges)
        for p1, p2 in itertools.product(*qrt):
            edge = frozenset((p1, p2))
            if edge not in graph:
                graph[edge] = [1, 0]
            else:
                graph[edge][0] += 1

    # set edge weights between tips on same side of the quartet (bad edges)
    for qrt in quartets:
        for part in qrt:
            if part not in graph:
                graph[part] = [0, 1]
            else:
                graph[part][1] += 1
    return graph


##################################################################
# Finding the best cut (partition) for a set of nodes
#
# 1. Compute (plus, minus) score for each edge from quartet sets
# 2a. For small ntaxa test all possible bipartitions.
# 2b. For large ntaxa perform heuristic search to get initial cut (below)
# 3. Distribute nodes randomly on a sphere.
# 4. Move nodes towards center of mass by score/dist weights, iteratively
# 5. Partition on random hyperplane through origin
# 6. Perform greedy search to propose +/- node swap from current
##################################################################

def assign_random_points_on_sphere(ntips: int) -> np.ndarray:
    """Return an array of ntips randomly assigned on a sphere.
    """
    points = []
    for _ in range(ntips):
        # generate random angles
        theta = np.random.uniform(0, 2 * np.pi)  # azimuthal angle
        phi = np.random.uniform(0, np.pi)        # polar angle

        # convert spherical coordinates to Cartesian coordinates
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        points.append((x, y, z))
    return np.array(points)


def get_euclidean_dist_arr(points: np.ndarray) -> np.ndarray:
    """Return array of pairwise Euclidean distances between points in 3D space.

    Parameters
    ----------
    points: numpy.ndarray
        A 2D array where each row represents a point (x, y, z).
    """
    # Calculate differences in each dimension
    diffs = points[:, np.newaxis, :] - points[np.newaxis, :, :]

    # Calculate the squared distances
    squared_diffs = diffs ** 2

    # Sum squared differences along the last axis and take the square root
    distances = np.sqrt(np.sum(squared_diffs, axis=-1))
    return distances


def compute_center_of_mass(focal_point, other_points, weights):
    """Return center of mass for each point.

    The center of mass (COM) point of a vertex is the closest point to
    all its neighbors, proportional to the edge weight to each neighbor.
    For example,if a vertex has two neighbors with equal edge weights, 
    its COM is in the middle of the line connecting these two neighbors,
    and if one edge weight is twice the weight of the other, the COM is 
    on the (1/3, 2/3) point on that line.

    Here, a node should move towards those with negative distances
    (bad edge * alpha) and away from those with positive distances
    (good edges). Our goal is to maximize the sum distance score.
    """
    # Calculate the weighted sum of the neighboring points
    weighted_sum = np.sum(weights[:, np.newaxis] * other_points, axis=0)
    
    # Normalize the weighted sum by the total weight (absolute sum of weights to handle negative weights)
    total_weight = np.sum(np.abs(weights))    
    if total_weight == 0:
        return focal_point  # If total weight is zero, return the focal point as the COM
    com_vector = weighted_sum / total_weight
    
    # The center of mass may not be on the unit sphere, so normalize it
    # (Note: I'm not positive this is required)
    # return com_vector
    com_unit_vector = com_vector / np.linalg.norm(com_vector)
    return com_unit_vector


def get_centers_of_mass(points, edges, adists) -> tuple[np.ndarray, np.ndarray]:
    """...

    """
    # iterate over points
    coms = []
    comdists = []
    for idx in range(points.shape[0]):
        # get which neighbors are connected to this one, e.g., [0, 1, 2, 5]
        point = points[idx]
        idxs = np.nonzero((edges[:, 0] == idx) | (edges[:, 1] == idx))[0]
        neis = sorted(set(edges[idxs].flatten()) - {idx})

        # get their coordinates
        coords = points[neis]

        # get their weights
        weights = adists[idxs].copy()

        # how to handle negative weights? Set negatives to zero.
        #weights[weights < 0] = 0.
        if not weights.sum():
            weights[:] = 1.
        else:
            weights = weights / weights.max()
            weights = weights * -1

        # get center of mass
        com = compute_center_of_mass(point, coords, weights)

        # get distance of point from its center of mass
        comdist = np.linalg.norm(com - point)
        coms.append(com)
        comdists.append(comdist)

    # Sample index weighted by its relative comdist
    coms = np.array(coms)
    comdists = np.array(comdists)
    return coms, comdists


def sample_point_far_from_com(points, coms, comdists) -> tuple[int, tuple[float,float,float]]:
    """Return the index of the sampled point far from the COM.
    # Samples probabilitistically weighted by relative distance to COM.

    Move a point towards its center of mass only if it increases the
    sum dist score (greedy algorithm).

    Parameters
    -----------
    ...
    """
    idx = np.random.choice(range(points.shape[0]), p=comdists / sum(comdists))
    return idx, coms[idx]


def move_point_by_distance_on_sphere(point, distance):
    """Move a point by a given distance in a random direction a unit sphere.
    """
    # Generate a random direction on the sphere by creating a random unit vector
    random_direction = np.random.randn(3)
    random_direction /= np.linalg.norm(random_direction)
    
    # Use spherical linear interpolation (slerp) to move the point
    new_point = np.cos(distance) * point + np.sin(distance) * random_direction
    
    # Ensure the result is still on the unit sphere by normalizing it
    new_point /= np.linalg.norm(new_point)
    return new_point


def get_coordinate_shifted_towards_com(
    point: tuple[float,float,float],
    com: tuple[float,float,float],
    step: float,
) -> tuple[float, float, float]:
    """Return coordinate of point2 shifted closer to point1 on the unit sphere by a specified step.

    Parameters
    ----------
    point1: ndarray
        A 3D coordinate on the unit sphere.
    point2: ndarray
        A 3D coordinate on the unit sphere to be shifted.
    step: float
        A value between 0 and 1 indicating how far to shift point2 towards point1.
    """
    # Ensure the points are numpy arrays
    point1 = np.array(com)
    point2 = np.array(point)

    # Calculate the vector from point2 to point1
    direction = point1 - point2
    
    # Calculate the shift amount
    shift_amount = step * np.linalg.norm(direction)

    # Move point2 towards point1
    new_position = point2 + direction / np.linalg.norm(direction) * shift_amount

    # Normalize the new position to ensure it's on the unit sphere
    new_position = new_position / np.linalg.norm(new_position)
    return new_position


def get_cut_from_heuristic_sdp_embedding(graph, alpha, seed, iters):
    """...

    The goal is to embed points on the unit sphere to maximize the
    function (sumdists(good_edges) - (alpha * sumdists(bad_edges))),
    using Euclidean distances between nodes on the sphere. This is
    similar to an SDP algorithm and is referred to as a heuristic
    SDP-like approach by Snir and Rao.

    Given their initial random positions and weights (default 1) move
    nodes iteratively towards their center of mass until a convergence
    is observed.
    """
    # get alphanumeric sorted nodes
    nodes = sorted(frozenset.union(*graph))
    # assign nodes to random points on a 3D sphere to start
    points = assign_random_points_on_sphere(len(nodes))

    # get sumdist of alpha weighted edges
    proposed = points
    edges, alpha_dists = get_edges_and_alpha_distances(nodes, graph, points, alpha)    
    sumdist = last_sum = sum(alpha_dists)

    # optimize: move points locally to optimize sumdist for current
    # alpha until there is no more improvement.
    # for i in range(iters):
    while 1:

        # sample a proposed shift
        com = get_center_of_mass(points, edges, alpha_dists)
        idx = sample_point_far_from_com(com, points)
        pos = get_coordinate_shifted_towards_com(com, points[idx], 0.05)

        # make an array copy with proposed shift points
        proposed = points.copy()
        proposed[idx] = pos

        # calculate score of proposal
        edges, alpha_dists = get_edges_and_alpha_distances(nodes, graph, proposed, alpha)
        sumdist = sum(alpha_dists)

        # accept or reject proposal based on its score
        if sumdist > last_sum:
            points = proposed
            logger.info(f"accepted shift, score = {sumdist:.5f}")
            last_sum = sumdist
    return points


def get_edges_and_alpha_distances(nodes, graph, points, alpha):
    """..."""
    # calculate euclidean distances    
    dists = get_euclidean_dist_arr(points)
    # get edges and weights as arrays using current alpha and Euclidean
    # dists to sum edges as (good_dists - bad_dists * alpha)
    dgraph = graph.copy()
    for edge, (good, bad) in graph.items():
        e = tuple(edge)
        idxs = nodes.index(e[0]), nodes.index(e[1])
        edist = dists[*idxs]
        dgraph[edge] = (edist * good) - (alpha * (edist * bad))
    edges = np.array([tuple(nodes.index(i) for i in j) for j in graph])
    weights = np.array([dgraph[frozenset(i)] for i in dgraph])
    return edges, weights    


def optimize_sphere_embedding(points, edges, weights): # nodes, graph, points, dists, alpha):
    """...

    """
    # calculate center of mass (COM)
    com = get_center_of_mass(points, edges, weights)

    # find who is farthest from COM
    idx = get_index_of_furthest_point_from_com(com, points)

    # get position 50% between that point and COM, but on the unit sphere.
    new_coordinates_on_sphere = get_coordinate_shifted_towards_com(com, points[idx], 0.5)
    points[idx] = new_coordinates_on_sphere
    return points
    # repeat...




def temp():
    # create graph copy w/ distances {{'a', 'c'}: (3, 0, 1.72839), ...}
    dgraph = graph.copy()
    for edge in graph:
        e = tuple(edge)
        idxs = nodes.index(e[0]), nodes.index(e[1])
        edist = dists[*idxs]
        dgraph[edge] = tuple(graph[edge]) + (edist,)

    # iterate a constant number of times (should converge generally)
    for i in range(10):
        # while 1:

        # store euclidean distances and weights
        scores = {}
        for edge in graph:
            # get nodes and node indices
            node0, node1 = edge
            n0, n1 = nodes.index(node0), nodes.index(node1)
            # get distance and score
            edist = dists[n0, n1]
            dist = 0.
            for good_edge in range(graph[edge][0]):
                dist += edist
            for bad_edge in range(graph[edge][0]):
                dist += -alpha * edist
            #


        # calculate COM of all Nodes
        centers = {}
        for node in nodes:
            centers[node] = sum(-np.array(duv[node]) * np.array(wuv[node]))
            logger.info((node, centers[node]))

        # move a Node closer to that center of mass
        break


def plot_sphere(sphere, points, graph):
    """...
    """
    # ...
    e1 = []
    e2 = []
    w1 = []
    w2 = []
    nodes = sorted(frozenset.union(*graph))
    for edge, scores in graph.items():
        if scores[0]:
            e1.append(tuple(edge))
            w1.append(scores[0])
        if scores[1]:
            e2.append(tuple(edge))
            w2.append(scores[1])
    e1 = np.array(e1)
    e2 = np.array(e2)
    
    # ...
    c, a, m = toyplot.scatterplot(
        sphere[:, 0], sphere[:, 1],
        opacity=0.1,
        size=(sphere[:, 2] * 4) + 5,
        width=350,
        height=350,
    )
    a.graph(
        e1[:, 0],
        e1[:, 1],
        ewidth=w1,
        vcoordinates=points[:, :2],
        vlshow=False,
        vsize=0,
        #vsize=(points[:, 2] * 4) + 8,
        #vcolor='red',
        #vopacity=0.5,
        #vlstyle={"font-size": "15px"},
    )
    a.graph(
        e2[:, 0],
        e2[:, 1],
        ewidth=w2,
        estyle={"stroke-dasharray": "4,2"},
        vcoordinates=points[:, :2] + 0.02,
        vlshow=False,
        vsize=0,
    )
    a.scatterplot(0, 0, color='black')
    a.text(points[:, 0], points[:, 1], nodes, color="black", style={"font-size": 15})
    return c, a, m


# def get_center_of_mass(distance_graph):
#     """Return the center of mass of a graph where edge distances
#     are measured as the sum of Euclidean distances between all good
#     edges and subtacting the Euclidean distances -alpha of bad edges.

#     The center of mass (or centroid) can be thought of as a central
#     vertex or a weighted average of the positions of all vertices. If
#     the graph has weighted vertices, the center of mass may take those
#     weights into account.

#     1. Calculate function(graph, alpha)
#     2. optimize alpha
#     3. get center of mass
#     4. get outlier node
#     5. shift towards COM
#     6. repeat from 1 for N iterations until converged.
#     """
#     # for edge, (good_edges, bad_edges) in graph.items():



def binary_search_optimize_alpha(dgraph):
    """Return alpha minimizing ratio of +/- scores using binary search.

    """
    # TODO: special care for alpha += 4
    # Singleton cuts have an alpha of 2 so we increase alpha to find
    # non-singleton cuts until we hit an empty cut.../?
    # rho is the ratio of good to bad edges.
    # rho <= 4 * nqrts
    # e.g., for 10 quartets rho must be less than 40?
    # Proof: There are exactly 4jQj good edges in the graph.
    # Since there is no perfect cut, any cut contains at least a
    # single bad edge and we get rho=4|Q|.
    # If alpha > 4|Q| and a nonempty cut is returned, then G has a perfect cut.

    high = 1000
    low = 0.
    alpha = (high - low) / 2.

    # optimize score to zero
    while 1:
        # get the max value
        search = {
            i: dgraph[i][0] * dgraph[i][2]
            + (dgraph[i][1] * dgraph[i][2] * -alpha)
            for i in dgraph
        }
        # score = max(search.values())
        score = sum(search.values())
        # logger.debug(f"{alpha} {score}")#{search}")

        # if score has converged then stop.
        if high == low:
            break
        # if score is negative then decrease alpha
        elif score < 0:
            high = alpha
            alpha = (high - low) / 2.
        # if score is positive but still far from zero increase alpha
        elif score > 0.1:
            low = alpha
            alpha = (high + low) / 2.
        else:
            break
    return score, alpha


def get_random_3D_hyperplane() -> tuple[float, float, float]:
    """Return a random hyperplane in 3D space through the origin.
    """
    # Generate a random normal vector (a, b, c)
    normal_vector = np.random.randn(3)  # Generates a 3D vector with normal distribution

    # Normalize the vector to ensure it represents a direction
    normal_vector /= np.linalg.norm(normal_vector)
    return tuple(normal_vector)


def partition_points_by_3D_hyperplane(points, a, b, c, d) -> tuple[list, list]:
    """Partition points in 3D space based on their position relative to a hyperplane.

    Parameters
    ----------
    points: ndarray
        An array of shape (N, 3) where N is the number of points.
    a, b, c, d: float
        Coefficients of the hyperplane equation ax + by + cz + d = 0.
    """
    above_hyperplane = []
    below_hyperplane = []

    for point in points:
        x, y, z = point
        # Evaluate the hyperplane equation
        position = a * x + b * y + c * z + d

        if position > 0:
            above_hyperplane.append(point)
        elif position < 0:
            below_hyperplane.append(point)
        # Optionally handle points on the hyperplane (position == 0)
    return np.array(above_hyperplane), np.array(below_hyperplane)


def get_maxcut_heuristic(graph):
    """Return the cut that maximizes the parameterized qmc score.

    This function uses a heuristic approach to propose cuts given
    that the search space is too large to exhaustively search all
    possible cuts. A greedy algorithm is implemented that starts with
    an empty cut w/ a score of zero and a better cut is returned only
    if its score is greater. If no cut is found then a lower value of
    alpha is tested.
    """
    # ...
    score = 0
    nodes = frozenset.union(*graph)
    ntaxa = len(nodes)


def get_maxcut_qmc(graph: dict[tuple[frozenset,frozenset]: int]) -> tuple[frozenset, frozenset]:
    """Return the cut that maximizes the parameterized qmc score.

    This tests every possible cut that bipartitions the taxon set
    into two. Each cut can either satisfy, violate, or defer the
    relationship in each quartet. Depending on the result, each
    quartet contributes positive or negative values to the score,
    which are stored as [positive, negative] counts. A parameter
    alpha is optimized that is multiplied by the negative counts
    to find the cut that has a minimum non-negative ratio. This
    effectively penalizes singleton cuts to ensure cuts that divide
    the taxon set at least into min groups of 2.
    """
    nodes = frozenset.union(*graph)
    ntaxa = len(nodes)

    # visit every non-singleton cut (e.g., (0, 1), (0, 1, 2), ...)
    # shown as one side with all remaining taxa assumed on other side.
    scores = {}
    for size in range(2, ntaxa - 2):
        cuts = itertools.combinations(nodes, size)

        # iterate over cuts
        for cut in cuts:
            cut = frozenset(cut)
            ocut = nodes - cut
            score = 0
            alpha = 0

            for name in cut:
                for oname in ocut:
                    cut_edge = frozenset((name, oname))
                    # skip if edge is not in the quartet set, which can
                    # occur for subset quartet data sets.
                    if cut_edge in graph:
                        _score, _alpha = graph[cut_edge]
                        score += _score
                        alpha += _alpha
            scores[cut] = (score, alpha)

    # find alpha minimizing ratio of +/- scores using binary search
    high = 0.01
    low = -1000.
    alpha = (high + low) / 2.
    while 1:
        search = {i: scores[i][0] + scores[i][1] * alpha for i in scores}
        score = max(search.values())
        # logger.debug(f"{alpha} {score}")#{search}")
        if high == low:
            break
        elif score < 0:
            low = alpha
            alpha = (high + low) / 2.
        elif score > 0.1:
            high = alpha
            alpha = (high + low) / 2.
        else:
            break

    # get the max non-negative parameterized score
    max_non_negative_score = max(search[i] for i in search)
    # get list of all cuts w/ the max score (there are often ties)
    hits = [i for i in search.items() if i[1] == max_non_negative_score]
    # count N non-artificial taxa in each hit
    hits = [(i, get_part_size(i[0])) for i in hits]
    # choose a cut from among those with largest N
    ss = sorted(hits, key=lambda x: x[1])[-1][0][0]
    # return the selected cut and its inverse
    logger.debug(f"alpha={alpha:4f}; cut={sorted(ss)}")
    return ss, nodes - ss


##################################################################


def get_subset_quartets(quartets, bipartition):
    """Return two sets of quartets that include new deferred quartets
    created from a full set of quartets and a cut.

    The deferred set would replace ((a,b),(c,f)) with ((a,b),(c, x))
    if 'f' is divided from 'abc' by the cut. The name 'x' appends an
    int (e.g., 'x1') and is incremented each time this func is called.
    """
    # select one side of the cut
    cut = bipartition[0]

    # cut1 or cut2 quartets will be passed on while violated or
    # satisfied quartets are discarded.
    cut1_quartets = defaultdict(int)
    cut2_quartets = defaultdict(int)

    # iterate over quartets
    # e.g., qrt is (frozenset({'a', 'b'}), frozenset('c', 'd'))
    art = ArtificialTaxon()
    for qrt in quartets:
        a, b = qrt

        # partial a
        if a.issubset(cut):
            # unaffected: assign to 1
            if b.issubset(cut):
                cut1_quartets[qrt] += 1
                # print(a, b, '1')
            # satisfied: discard
            elif b.isdisjoint(cut):
                pass
                # print(a, b, 'x satisfy 1')
            # deferred: assign modified to 1
            else:
                tup = frozenset(b.intersection(cut).union({art}))
                qrt = (a, tup)
                cut1_quartets[qrt] += 1
                # print(a, b, f'1 defer - {qrt}')

        elif a.isdisjoint(cut):
            # satisfy: discard
            if b.issubset(cut):
                pass
                # print(a, b, 'x satisfy 2')
            # unaffected: assign to 2
            elif b.isdisjoint(cut):
                cut2_quartets[qrt] += 1
                # print(a, b, '2')
            # deferred: assign to 2
            else:
                tup = frozenset(b.difference(cut).union({art}))
                qrt = (a, tup)
                cut2_quartets[qrt] += 1
                # print(a, b, f'2 defep - {qrt}')

        # a conflicts with cut
        else:
            if b.issubset(cut):
                tup = frozenset(a.intersection(cut).union({art}))
                qrt = (b, tup)
                cut1_quartets[qrt] += 1
                # print(a, b, f'1 defeb - {qrt}')
            elif b.isdisjoint(cut):
                tup = frozenset(a.difference(cut).union({art}))
                qrt = (b, tup)
                cut2_quartets[qrt] += 1
                # print(a, b, f'2 defex - {qrt}')
            else:
                pass
                # print(a, b, 'x conflicts')
    parts = (bipartition[0].union({art}), bipartition[1].union({art}))
    qsets = (dict(cut1_quartets), dict(cut2_quartets))
    return parts, qsets


def get_part_size(object) -> int:
    """Return size of a partition not counting artificial taxa"""
    return sum(1 for i in object if not isinstance(i, ArtificialTaxon))


class ArtificialTaxon:
    count = 0
    def __init__(self):
        self.name = f"x{ArtificialTaxon.count}"
        ArtificialTaxon.count += 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


# NOTE:
# Here I implemented a normalization approach that gives high weight
# to splits that occur 100% of the time, but only in a subset of trees,
# due to having one or more taxa that are not present in all trees.
# This approach does not work well and leads to odd placement of the
# rare taxa.
#
# def get_weighted_quartet_graph_from_multitree(
#     trees: MultiTree | list[ToyTree],
#     normalize_by_ntrees: bool = False,
# ) -> dict[tuple[frozenset,frozenset],float]:
#     """Return {quartet: weight} from a MultiTree or sequence of trees.

#     The weight of each quartet is calculated as the proportion of trees
#     that contain that quartet, where this proportion can be scaled by
#     either the total number of trees, or if the trees contain different
#     tips, then by the number of trees that contain all of the tips in
#     the quartet.

#     Parameters
#     ----------
#     trees: MultiTree | Sequence[ToyTree]
#         An input set of one or more ToyTree objects.
#     normalize_by_ntrees: bool
#         If True then the weight of each quartet is calculated by its
#         number of occurrences in the trees divided by the total number
#         of trees, rather than the subset of trees that contain its tips.
#         If all trees have the same tips this has no effect.
#     """
#     # build weighted graph from quartets
#     # ...
#     tip_counts = {}
#     qrt_counts = {}

#     for tree in trees:
#         # store qrt
#         for qrt in tree.enum.iter_quartets(type=frozenset, sort=True):
#             if qrt not in qrt_counts:
#                 qrt_counts[qrt] = 1
#             else:
#                 qrt_counts[qrt] += 1

#         # store tips
#         tips = frozenset(tree.get_tip_labels())
#         if tips not in tip_counts:
#             tip_counts[tips] = 1
#         else:
#             tip_counts[tips] += 1

#     # get weights as the proportion of trees that included this qrt
#     # of the trees that included that set of taxa.
#     qrt_weights = {}
#     if normalize_by_ntrees:
#         for qrt in qrt_counts:
#             qrt_weights[qrt] = qrt_counts[qrt] / len(trees)
#     else:
#         for qrt in qrt_counts:
#             ntrees_with_qrt_tips = 0
#             for tips in tip_counts:
#                 qset = frozenset.union(*qrt)
#                 if qset.issubset(tips):
#                     ntrees_with_qrt_tips += tip_counts[tips]
#             qrt_weights[qrt] = qrt_counts[qrt] / ntrees_with_qrt_tips
#     return qrt_weights


##################################################################


def old_get_maxcut_quartet_supertree(
    trees: Union[MultiTree, list[ToyTree]],
    seed: Union[int, np.random.Generator, None] = None,
    normalize_by_ntrees: bool = False,
) -> ToyTree:
    """Return an unrooted supertree inferred from weighted quartet
    frequencies extracted from a set of input trees with the same or
    different tip sets.

    Parameters
    ----------
    trees: MultiTree | Sequence[ToyTree]
        An input set of one or more ToyTree objects.
    seed: int | np.random.Generator | None
        A seed for randomly choosing among equal scoring cuts.
    normalize_by_ntrees: bool
        If True then the weight of each quartet is calculated by its
        number of occurrences in the trees divided by the total number
        of trees, rather than the subset of trees that contain its tips.
        If all trees have the same tips this has no effect.

    Example
    -------
    >>> trees = toytree.mtree([
    >>>     "((a,b),(c,d));",
    >>>     "((a,b),(c,d));",
    >>>     "((a,b),(c,d,f));",
    >>> ])
    >>> tree = get_maxcut_quartet_supertree(trees)
    """
    raise SystemExit(0)

    # ...
    while partitions:
        # sample next partition
        p = partitions.popleft()
        print('part', p)

        # create a Node
        node = Node(name="".join(sorted(p)))
        print('node', node)

        # connect it to a parent
        if not nodes:
            treenode = node
        else:
            nodes[p]._add_child(node)

        # if partition is terminal
        if len(p) == 1:
            node.name = list(p)[0]
            continue

        # elif partition is a cherry or multi
        if len(p) == 2:
            for child in p:
                node._add_child(Node(name=child))
            print('nodes', nodes)
            continue

        # create a subgraph containing the remaining samples
        subgraph = {e: w for (e, w) in graph.items() if e.issubset(p)}
        print('sub', subgraph)

        # if no more edges to split a partition (e.g., hard polytomy)
        # if not subgraph:
        #     for child in p:
        #         node._add_child(Node(name=child))
        #     print('nodes', nodes)
        #     raise SystemExit()
        #     continue

        # get a maxcut bipartition and add its partitions to the queue
        bipart, score = get_maxcut(subgraph, seed=seed)

        # if no cut is made (hard polytomy)
        if not all(bipart):
            for child in p:
                node._add_child(Node(name=child))
            print('nodes', nodes)
            # raise SystemExit()
            continue

        print('bipart', bipart)
        for part in bipart:
            part = frozenset(part)
            partitions.append(part)
            nodes[part] = node

    # construct a ToyTree
    tree = toytree.ToyTree(treenode)

    # compute edge supports as the proportion of quartets supporting the split.
    for node, bipart in zip(tree[tree.ntips:], tree.enum.iter_bipartitions(type=frozenset)):
        matched = 0
        disjunct = 0
        b0, b1 = bipart
        for qrt in wqrts:
            q0, q1 = qrt
            if b0.issuperset(q0):
                if b1.issuperset(q1):
                    matched += wqrts[qrt]
                    print(q0, q1, b0, b1, wqrts[qrt], True)
            elif b0.issuperset(q1):
                if b1.issuperset(q0):
                    matched += wqrts[qrt]
                    print(q0, q1, b0, b1, wqrts[qrt], True)
            else:
                # this quartet is not relevant to the bipartition
                disjunct += wqrts[qrt]
        node.support = matched / (sum(wqrts.values()) - disjunct)
    return tree



def get_maxcut_quartet_supertree(
    trees: Union[MultiTree, list[ToyTree]],
    seed: Union[int, np.random.Generator, None] = None,
    use_weights: bool = False,
) -> ToyTree:
    """Return an unrooted supertree inferred from weighted quartet
    frequencies extracted from a set of input trees with the same or
    different tip sets.

    Parameters
    ----------
    trees: MultiTree | Sequence[ToyTree]
        An input set of one or more ToyTree objects with the same or
        different number of tips.
    seed: int | np.random.Generator | None
        A seed for randomly choosing among equal scoring cuts.
    use_weights: bool
        If True then quartet edges are weighted by their relative
        occurrence in the input trees.

    Example
    -------
    >>> trees = toytree.mtree([
    >>>     "((a,b),(c,d));",
    >>>     "((a,b),(c,d));",
    >>>     "((a,b),(c,d,f));",
    >>> ])
    >>> tree = get_maxcut_quartet_supertree(trees)
    """
    # get all quartets from the set of trees weighted by relative frequency
    wqrts = get_weighted_quartets_from_trees(trees)
    if not wqrts:
        raise ValueError("Cannot infer a quartet super tree for <4 taxa")
    if len(wqrts) == 1:
        raise ValueError("Cannot infer a quartet super tree for 4 taxa")
        return list(wqrts)

    # start iterative QMC
    queue = [wqrts]
    clades = []
    iteration = 0
    while queue:
        # get next quartet set to process
        wqrts = queue.pop()
        logger.info(("popped", wqrts))
        # build a graph of weighted edges from quartets
        graph = get_graph_from_quartets_qmc(wqrts)
        # find a maxcut
        bipart = get_maxcut_qmc(graph)
        logger.info((iteration, bipart))
        # add deferred quartet labels to cut and get subset quartets
        parts, qsets = get_subset_quartets(wqrts, bipart)
        logger.info((iteration, parts, qsets))
        # save finished partition to add quartet set to queue
        for part, qset in zip(parts, qsets):
            # resolved cherry
            if get_part_size(part) == 2:
                logger.warning(part)
                clades.append(part)
            # finished but unresolved polytomy
            elif not qset:
                logger.warning(part)
                clades.append(part)
            else:
                queue.append(qset)
        iteration += 1

    # build tree from clades
    # ... (clades)

    # assign supports from original quartet set
    # ... (tree, wqrts)
    return clades


def build_tree_from_deferred_clades(clades: list[frozenset]):
    """
    # build a tree from defereed clades, e.g.,
    # {a, b, x}, {c, d, y}, {e, f, x, y},               # (((a,b),(c,d)),(e,f));
    # {a, b, x}, {c, d, y}, {e, z, x, y}, {z, f, g, h}  # ((((a,b),(c,d)),e),(f,g,h));
    """
    nodes = {}
    for clade in clades:
        arts = frozenset({i for i in clade if isinstance(i, ArtificialTaxon)})
        children = clade - arts
        if arts in nodes:
            logger.warning(f"REPEAT {arts}")
        nodes[arts] = children
        # {{x}: (a, b), {y}: (c, d), {x,y}: (e,f)}
        # {{x}: (a, b), {y}: (c, d), {z}: (f,g,h), {x,y,z}: (e,)}
    logger.debug(('nodes', nodes))

    # iterate over artifical taxon set keys from smaller to larger
    snodes = sorted(nodes, key=len)
    tnodes = {}
    for aset in snodes:
        # create a parent Node and connect children
        if len(aset) == 1:
            parent = Node()
            for child in nodes[aset]:
                parent._add_child(Node(name=child))
            tnodes[aset] = parent
        # create a parent Node and connect children and other Nodes
        else:
            parent = Node()
            for child in nodes[aset]:
                parent._add_child(Node(name=child))
            for art in aset:
                anode = tnodes[frozenset({art})]
                parent._add_child(anode)
            tnodes[aset] = parent

        # for art in aset:
        #     parent._add_child(nodes[art])
    logger.debug(tnodes)
    tnodes[aset].draw_ascii()
    raise SystemExit(0)


if __name__ == "__main__":

    import toytree
    toytree.set_log_level("DEBUG")

    trees = [
        # "((a,b),(c,d));",
        # "((a,b),(c,d));",
        # "((a,b),(c,d));",
        # "((a,b),(c,d));",
        # "((a,b),(c,d));",
        # "((a,b),(c,d));",
        # "((a,b),(c,d));",
        # # "((b,a),((d,c),(g,f,e)));",
        # "((b,a),((d,c),(g,(f,e))));",  # problem child.
        # "((b,a),((d,c),((g,h),(f,e))));",  # problem child.
        # "((1,2),((3,4),(5,6)));",
        # "((1,2),(3,4));",
        # "((1,3),(4,5));",
        # "((3,4),(5,6));",
        # "((3,4),(5,7));",
        "((c,d),(a,b));",
        "((b,a),(c,d));",
        "((b,a),(d,c,f));",
        "((b,a),((d,c),f));",
        # "((b,a),((d,c),((f,e),g)));",
        # "((e,d),(h,a));",
        # "((a,c),((b,d),f));",
    ]
    logger.info(trees)
    # trees = [toytree.rtree.unittree(8, seed=123) for i in range(5)]
    trees = toytree.mtree(trees)
    # trees[-1].treenode.draw_ascii()
    # print(trees)
    clades = get_maxcut_quartet_supertree(trees)
    tree = build_tree_from_deferred_clades(clades)
    print(tree)
    raise SystemExit(0)

    # print('weighted quartets---------')
    q = get_weighted_quartets_from_trees(trees)
    # for i in q:
    #     print(i, q[i])

    # print('graph------------')
    g = get_graph_from_quartets_qmc(q)
    for i in g:
        print(i, g[i])

    # get the first cut
    # bipart = get_maxcut_qmc(g)
    # parts, qsets = get_subset_quartets(q, bipart)

    # # process each partition
    # for part, qset in zip(parts, qsets):
    #     nqrts = len(qset)
    #     print(part, qset)
    #     if get_part_size(part) == 2:
    #         logger.info(part)
    #     else:
    #         # for q in qset:
    #         #     print(q, qset[q])
    #         subg = get_graph_from_quartets_qmc(qset)
    #         bipart = get_maxcut_qmc(subg)
    #         parts, qsets = get_subset_quartets(qset, bipart)
    #         for part, qset in zip(parts, qsets):
    #             nqrts = len(qset)
    #             if get_part_size(part) == 2:
    #                 logger.info(part)
    #             else:
    #                 subg = get_graph_from_quartets_qmc(qset)
    #                 bipart = get_maxcut_qmc(subg)
    #                 parts, qsets = get_subset_quartets(qset, bipart)
    #                 if not nqrts:
    #                     logger.info(part)

            # for part, q in zip(bipart, qsets):
            #     nqrts = len(q)
            #     print(f"bipart {part} {nqrts} qrts ---------------")
            #     if nqrts > 2:
            #         subg = get_graph_from_quartets_qmc(q)
            #         bipart = get_maxcut_qmc(subg)
            #         qsets = get_subset_quartets(q, bipart[0])
            #         for part, q in zip(bipart, qsets):
            #             nqrts = len(q)
            #             print(f"bipart {part} {nqrts} qrts ---------------")



    # print("cut bipart---------------", q1)
    # subg = get_graph_from_quartets_qmc(q2)
    # print(subg)
    # bipart = get_maxcut_qmc(subg)
    # q1, q2 = get_subset_quartets(q1, bipart[1])
    # print(bipart)


    # subg = get_graph_from_quartets_qmc(q2)
    # bipart = get_maxcut_qmc(subg)
    # print(bipart)

    # subg = get_graph_from_quartets_qmc(q1)
    # bipart = get_maxcut_qmc(subg)
    # print(bipart)
    # q1, q2 = get_subset_quartets(q, bipart[1])
    # for i in q1:
    #     print(i, q1[i])
    # for i in q2:
    #     print(i, q2[i])




    # print('graph------------')
    # g = get_graph_from_quartets_qmc(q)
    # for i in g:
    #     print(i, g[i])
