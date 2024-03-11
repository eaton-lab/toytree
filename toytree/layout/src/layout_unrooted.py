#!/usr/bin/env python

"""Unrooted layout.

"""

from typing import TypeVar, Tuple
import numpy as np
from loguru import logger
from toytree.layout import BaseLayout, get_tip_labels_angles

logger = logger.bind(name="toytree")
ToyTree = TypeVar("ToyTree")


class UnrootedLayout(BaseLayout):
    """Layout for unrooted tree projection: "unrooted", "u1", "u2"
    """
    def run(self):
        """Fills the .coords array with x, y values."""

        # xbaseline, ybaseline to set origin.
        self.coords = equal_daylight_algorithm(
            tree=self.tree,
            max_iter=50,
            use_edge_lengths=self.style.use_edge_lengths)
        self.tcoords = self.coords[:self.tree.ntips, :].copy()
        self.angles = get_tip_labels_angles(self.tree, self.coords)
        self.style_overwrite()

    def style_overwrite(self):
        """Overwrite styles that are not allowed in unrooted layout
        of which should have different defaults.
        """
        self.style.tip_labels_align = False
        # self.style.tip_labels_style._toyplot_anchor_shift = 0
        # self.style.tip_labels_style.text_anchor = "middle"
        self.style.edge_type = 'c'


#####################################################
# UNROOTED LAYOUT UTILITIES
#####################################################


def rotate_arr(
    points: np.ndarray,
    origin: Tuple[float, float] = (0, 0),
    degrees: float = 0,
) -> np.ndarray:
    """Return an array of rotated Node coordinates."""
    angle = np.deg2rad(degrees)
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)],
    ])
    origin = np.atleast_2d(origin)
    point = np.atleast_2d(points)
    return np.squeeze((rotation_matrix @ (point.T - origin.T) + origin.T).T)


def equal_daylight_algorithm(
    tree: ToyTree,
    max_iter: int = 1,
    min_delta: float = 1,
    use_edge_lengths: bool = True,
) -> float:
    """Return coordinates for unrooted layout under the eda algorithm.

    This algorithm equalizes the sizes of angular gaps between
    subtrees. As Felsenstein said, the result is "outstanding".
    The description however is not very detailed, so there is room
    for interpretation.

    I use a levelorder traversal but could it seems that postorder
    can yield better results sometimes, but also much worse sometimes.
    If the eda layout is too different from the eaa layout it will
    be rejected.

    Notes
    -----
    We could estimate the length that tip names will extend past the
    end of tips when calculating daylight. This would ensure that tip
    names to do not crossover, not just that edges do not cross over.
    This would only be necessary if tip names were text-align=start,
    however, but they are usually drawn all with angle=0, so the idea
    is moot I suppose.

    References
    ----------
    - Felsenstein 2004, page 582 (and see Figure 34.6).
    """
    # get the equal angle algorithm tree as a starting tree.
    coords = equal_angle_algorithm(tree, use_edge_lengths=use_edge_lengths)

    # return equal-angles for <= 4-taxon trees
    if (tree.ntips < 5) | (max_iter == 0):
        return coords

    # a set with all Nodes except the root
    # nodes = set(tree.get_nodes()[:-1])
    nodes = set(tree.get_nodes())

    # for Y internal nodes we expect an average rotation of X, thus
    # any solution with more delta than 3 * Y * X is almost surely
    # worse than the equal-angles layout and should be discarded.
    n_internal = tree.nnodes - tree.ntips - 1
    min_angles = n_internal * 3
    avg_change = 30
    max_change = (min_angles * avg_change) / 3  # .5

    # Perform multiple passes through the tree stopping when either
    # the improvement falls below a threshold, max_iters is reached,
    # or the iteration results in more changes than a previous one.
    sum_deltas = []  # list of sum change in angles each iter
    full_circle = None  # record whether full circle encountered.
    niter = 0
    while 1:
        # create a copy of coords to modify
        icoords = coords.copy()

        # record the sum of changed angles this iter
        sum_delta = 0

        # visit each internal node in levelorder and rotate other nodes
        # relative to the position of this one. Skip root and leaves,
        # they only rotate relative to internals.
        for fnode in tree.traverse("levelorder"):

            # only visit internal non-root nodes.
            # if fnode.is_root():
                # continue
            if fnode.is_leaf():
                continue

            # get current focal node coordinates
            pos = icoords[fnode.idx]

            # get the 3 or more subtrees connected to this vertex
            full_set = nodes - {fnode}
            subsets = [set(i.get_descendants()) for i in fnode.children]
            other_set = full_set - set.union(*subsets)
            if other_set:
                subsets.append(full_set - set.union(*subsets))
            subsets = dict(enumerate(subsets))

            # get shaded sectors by subtrees.
            shade = {}
            last = 0
            for sidx, subset in subsets.items():
                rads = []
                for node in subset:

                    # get position of this node relative to focal node
                    npos = icoords[node.idx]
                    delta_x = npos[0] - pos[0]
                    delta_y = npos[1] - pos[1]

                    # get start,end radians of sector where 0 is down
                    rad = np.arctan2(delta_y, delta_x) + np.pi / 2
                    # flip 4th quad negative to positive
                    rad = (2 * np.pi) + rad if rad < 0 else rad
                    # save 1st quad as >2pi
                    rad = (2 * np.pi) + rad if rad < last else rad
                    rads.append(rad)

                # store the sector of each shaded region
                shade[sidx] = (min(rads), max(rads))
                last = max(rads)

            # get the order in which shaded regions rotate around node
            skeys = sorted(shade, key=lambda x: abs(shade[x][0]))
            gaps = [(skeys[i], skeys[i + 1]) for i in range(len(skeys) - 1)]
            gaps += [(skeys[-1], skeys[0])]

            # get daylight as sectors between ordered shaded regions
            # e.g., (0, 1), (1, 2), ...
            light = {}
            for gap in gaps:
                last, this = shade[gap[0]][1], shade[gap[1]][0]
                if last > this:
                    this = 2 * np.pi + this
                light[gap] = np.rad2deg(this - last)

                # debugging daylight for each gap
                # logger.debug(
                #     f"{fnode.idx} daylight: {gap}: size={light[gap]:.1f} "
                #     f"-- last={np.rad2deg(last):.1f}, this={np.rad2deg(this):.1f}"
                # )

            # if subtree angles sum to more than a full circle it is
            # impossible to find a positive angle between subtrees and
            # they will overlap. So we stop the iteration and return
            # last set of coordinates. This will not occur when starting
            # from the equal-angles layout, but can on any subsequent iters.
            if (shade[skeys[-1]][1] - (2 * np.pi)) > shade[skeys[0]][0]:
                full_circle = fnode.idx

            # change angles
            optimal = sum(light.values()) / len(light)      # 56
            rotated = [0]
            for gap in gaps[:-1]:
                # how far the gap[1] needs to be rotated
                gap_to_next = light[gap] + rotated[-1]      # 76 +  0 = 76, 63 + 20
                angle_to_rotate = gap_to_next - optimal     # 76 - 56 = 20, 83 - 56
                rotated.append(angle_to_rotate)             # [0, 20,],

                # rotation = angle_to_rotate
                nodes_to_rotate = subsets[gap[1]]           # [13,4,5],
                idxs = [i.idx for i in nodes_to_rotate]
                icoords[idxs, :] = rotate_arr(
                    points=icoords[idxs],
                    origin=pos,
                    degrees=-angle_to_rotate,
                )
                # debugging rotation applied to each Node
                # logger.debug(
                #     f"node {fnode.idx} rotating {len(nodes_to_rotate)} nodes by "
                #     f"{angle_to_rotate:.2f} deg to get optimal daylight {optimal:.1f} deg.")

            # record how much change has happened
            avg_delta = np.mean([abs(i) for i in rotated[1:]])
            sum_delta += avg_delta

        # iteration finished. Should we accept this change to coordinates?
        # logger.debug(
        #     f"sum angles change={sum(sum_deltas):.1f}, "
        #     f"angles_change_this_iter={sum_delta:.1f}")

        # causes to not accept the proposed coordinate change.
        if full_circle is not None:
            # logger.debug(f"stopping at {niter} iters because subtree angles sum to > full circle @ node {full_circle}")
            break
        if sum_delta > max_change:
            # logger.debug(f"stopping at {niter} iters because bad solution ({sum_delta} > {max_change}).")
            break
        if sum_deltas:
            last = sum_deltas[-1]
            if sum_delta > (last + last * .1):
                # logger.debug(f"stopping at {niter} iters because encountered a worse solution.")
                break

        # accept the coordinates change
        niter += 1
        sum_deltas.append(sum_delta)
        coords = icoords

        if niter == max_iter:
            # logger.debug(f"stopping after {niter} iters because max_iter reached.")
            break
        if sum_delta < min_delta:
            # logger.debug(f"stopping after {niter} iters because delta <= min_delta.")
            break

    return coords


def equal_angle_algorithm(
    tree: ToyTree,
    use_edge_lengths: bool = True,
) -> float:
    """Return coordinates for unrooted layout under the 'eaa' algorithm.

    Assign the root node a sector from 0-360 degrees, and divide each
    descendent node into subsectors with size weighted by their n
    descendants.

    Parameters
    ----------
    tree: ToyTree
        A Toytree from which to build coordinates.
    use_edge_lengths: bool
        If False then all dists are set to 1.

    References
    ----------
    - Felsenstein (2004), page 578.
    """
    coords = np.zeros(shape=(tree.nnodes, 2))

    # if tree is rooted then use root Node as the central vertex.
    ntips = tree.ntips
    radians_per_tip = 2 * np.pi / ntips

    # store {Node: value}
    radian_sums = {}
    sectors = {}

    # record the sum of sector area for each Node as its N
    # descendants * the radians per tip.
    for node in tree.traverse("postorder"):
        if node.is_leaf():
            # node.radian_sum = radians_per_tip
            radian_sums[node] = radians_per_tip
        else:
            # node.radian_sum = sum(i.radian_sum for i in node.children)
            radian_sums[node] = sum(radian_sums[i] for i in node.children)

    # assign radian sectors in levelorder.
    for node in tree.traverse("levelorder"):
        if node.is_root():
            coords[node.idx] = (0, 0)
            sectors[node] = [0, 2 * np.pi]
        else:
            cohort = node.up.children
            idx = cohort.index(node)
            if not idx:
                start = sectors[node.up][0]
            else:
                start = sectors[cohort[idx - 1]][1]
            sectors[node] = [start, start + radian_sums[node]]
            mid = sum(sectors[node]) / 2.

            # geometry relative to parent position and angle
            parent_pos = coords[node.up.idx]
            hypo = node.dist if use_edge_lengths else 1.
            newx = parent_pos[0] + (hypo * np.sin(mid))
            newy = parent_pos[1] - (hypo * np.cos(mid))
            coords[node.idx] = (newx, newy)
    return coords


# NOT CURRENTLY USED
# def get_subtrees(tree: ToyTree, node: Node) -> Sequence[Set[Node]]:
#     """Return subtrees connected to a Node.

#     If this Node was removed from an unrooted tree it would induce
#     three or more subtrees. This returns the sets of Nodes in each
#     subtree. This is used internally for unrooted tree layouts.
#     """
#     nodes = set(tree.get_nodes()) - {node}
#     subsets = [set(i.get_descendants()) for i in node.children]
#     subsets.append(nodes - set.union(*subsets))
#     return subsets


if __name__ == "__main__":

    import toytree
    # Felsenstein book example
    NWK = "(((((((A:4,B:4):6,C:5):8,D:6):3,E:21):10,((F:4,G:12):14,H:8):13):13,((I:5,J:2):30,(K:11,L:11):2):17):4,M:56);"
    # NWK = "(((E,F),(G, H)),((C,D),(B,(I,J)),A));"
    TRE = toytree.tree(NWK)
    # TRE = toytree.rtree.bdtree(20, b=0.5, d=0.5, seed=123)
    # TRE = TRE.unroot()

    toytree.set_log_level("INFO")
    coords1 = equal_angle_algorithm(TRE, False)
    coords2 = equal_daylight_algorithm(TRE, max_iter=10)

    import toyplot

    canvas1 = toyplot.Canvas(400, 400)
    axes = canvas1.cartesian()
    axes.graph(
        TRE.get_edges(),#.values,
        vcoordinates=coords1,
        # vsize=16,
        estyle={"stroke-width": 2},
    )
    canvas2 = toyplot.Canvas(500, 400)
    axes = canvas2.cartesian()
    axes.graph(
        TRE.get_edges(),#.values,
        vcoordinates=coords2,
        #vsize=16,
        estyle={"stroke-width": 2},
        ecolor='black',
    )

    c, a, m = TRE.draw(node_labels="idx")
    toytree.utils.show([canvas1, canvas2, c], new=False)
    # toyplot.browser.show([canvas1, canvas2, c])
    # print(equal_daylight_algorithm(tre))

    # lay = Layout(
    #     tre,
    #     layout='c',
    #     fixed_order=tre.get_tip_labels()[::-1],
    #     fixed_position=None,
    #     xbaseline=10,
    # )
    # print(lay.coords)

    # lay = Layout(
    #     tre,
    #     layout='c0-180',
    #     fixed_order=tre.get_tip_labels()[::-1],
    #     fixed_position=None,
    #     xbaseline=10,
    # )
    # print(lay.coords)

    # # unrooted layout
    # lay = Layout(
    #     tre,
    #     layout="*",
    #     fixed_order=tre.get_tip_labels()[::-1],
    #     fixed_position=None,
    #     xbaseline=10,
    # )
    # print(lay.coords)

