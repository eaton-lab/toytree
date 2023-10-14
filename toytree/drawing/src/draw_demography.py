#!/usr/bin/env python

"""Rewrite of the container drawing class.

Note
----
Ne values are fixed within intervals. The steps to drawing are:

1. Get horizontal spacing of species tree tips based on Ne values.

2. Begin drawing tip lineages in post-order traversal. This start by
creating an Interval for each tip in a cherry, and for their ancestor.
The end positions of the tips is designed to lean towards their parent,
whose positionCreate a new Interval for the cherry parent.

Ideas
------
container = mark (square, angled, styled?)
embedding = mark (must fit within container?, allow migration?)
"""

# pylint: disable=invalid-name

from __future__ import annotations
from typing import List, Dict, Optional, Mapping, Sequence, Union, Tuple
from functools import cached_property
from dataclasses import dataclass, field
from loguru import logger
import numpy as np
from pandas import DataFrame

import toyplot
from toytree.style import get_range_mapped_feature, get_color_mapped_values
from toytree.utils.src.embedding import get_genealogy_embedding_table
from toytree.core import ToyTree, Canvas, Cartesian, Mark, Node
from toytree.color import ColorType

logger = logger.bind(name="toytree")
# ToyTree = TypeVar("ToyTree")


@dataclass
class Interval:
    r"""A single interval of the species tree model.

         pxb0\---------------------/pxb1
            xt0________xt1  ...   ...              y1
             /       /       \     \               |
            /       /         \     \              |
        xb0/_______/xb1        ...   ...           y0
               |
              xm0

    Parameters
    ----------
    xpos: float
        The x position of the lower bound of this interval. This is the
        original left position, but may be updated and extended further
        left if blend=True.
    ypos: float
        The y position (height) of the lower bound of this interval.
    up: Interval or None
        An Interval class that is parent to this one.
    children: List
        A list of Intervals directly descended from this one.
    left: bool
        If True this lineage is the left descendant of its parent.
    blend: bool
        If True then interval bottoms are fit to the width of their
        children intervals to make the tree look less blocky.
    """
    width: float
    height: float
    xpos: float = 0
    ypos: float = 0
    neff: float = 0
    left: bool = False
    blend: bool = False
    up: Optional[Interval] = field(default=None, init=False, repr=False)
    children: List[Interval] = field(default_factory=list, init=False, repr=False)
    data: Dict[str, float] = field(default_factory=dict, init=False, repr=False)

    @cached_property
    def xb0(self):
        """Return the left x-position on the lower bound"""
        if self.children and self.blend:
            return min([i.xt0 for i in self.children])
        return self.xpos

    @cached_property
    def xmid(self):
        """Return the midpoint x-position on lower bound"""
        return self.xpos + (self.width / 2.)

    @cached_property
    def xb1(self):
        """Return the right x-position on the lower bound"""
        if self.children and self.blend:
            return max([i.xt1 for i in self.children])
        return self.xb0 + self.width

    @cached_property
    def xt0(self):
        """Return the left x-position on the upper bound"""
        if not self.up:
            return self.xb0
        if not self.left:
            return self.up.xmid - self.width
        return self.up.xmid

    @cached_property
    def xt1(self):
        """Return the right x-position on the upper bound"""
        if not self.up:
            return self.xb1
        if not self.left:
            return self.up.xmid
        return self.up.xmid + self.width

    @cached_property
    def y0(self):
        """Return the y-position of the lower bound"""
        return self.ypos

    @cached_property
    def y1(self):
        """Return the y-position of the upper bound"""
        return self.ypos + self.height

    # @cached_property
    # def xbounds(self):
    #     """Return the bounding coordinates (xb0, xb1, xt0, xt1)"""
    #     return (self.xb0, self.xb1, self.xt0, self.xt1)

    # @cached_property
    # def ybounds(self):
    #     """Return the bounding coordinates (y0, y0, y1, y1)"""
    #     return (self.y0, self.y0, self.y1, self.y1)

    # @cached_property
    def slope(self, position: float = None):
        """Return the slope (delta x / delta y) for use in :func:is_inside()"""
        if not self.up:
            return 0.
        if not position:
            position = (self.xt1 - self.xt0) / 2.
        # dist to right of xb0 / length of xb
        prop_bottom = (position - self.xb0) / (self.xb1 - self.xb0)
        length_on_top = prop_bottom * (self.xt1 - self.xt0)
        pos_at_same_prop_on_top = self.xt0 + length_on_top
        return (pos_at_same_prop_on_top - position) / self.height

    def is_inside(
        self,
        xpos: float,
        ypos: float,
        padding: float = 0.0,
    ):
        """Return True if coordinate position is inside the interval.

        This is used to avoid overlaps among intervals, and to ensure
        embedded gene trees do not extend outside of of the interval.
        The padding parameter can be used to further limit embeddings
        from coming too close to the edge, or similarly, margin will
        pad the outside to limit how close intervals are to each other.
        """
        ypass = self.y0 <= ypos <= self.y1
        xmin_at_ypos = self.xb0 + padding + (ypos - self.y0) * self.slope()
        xmax_at_ypos = self.xb1 - padding + (ypos - self.y0) * self.slope()
        # logger.info(f"xmin_at_ypos: {xmin_at_ypos}")
        # logger.info(f"xmax_at_ypos: {xmax_at_ypos}")
        xpass = xmin_at_ypos <= xpos <= xmax_at_ypos
        return xpass & ypass

    def is_overlapping(
        self,
        xpos: float,
        ypos: float,
        border: float = 0.0,
    ):
        """Return True if coordinate position is inside the interval.

        This is used to avoid overlaps among intervals, and to ensure
        embedded gene trees do not extend outside of of the interval.
        The padding parameter can be used to further limit embeddings
        from coming too close to the edge, or similarly, margin will
        pad the outside to limit how close intervals are to each other.
        """
        margin: float = 0.0


@dataclass
class Container:
    """Container to visualize a genealogy embedded in a species tree.

    A Container drawing is composed of multiple Interval class
    instances that each have coordinates, and reference each other
    in a tree structure (.up, .children), and can be accessed from
    the Container's .intervals dict.

    Parameters
    ----------
    species_tree: toytree.ToyTree
        A ToyTree that optionally has 'Ne' data set to nodes to use for
        relative interval widths. If no Nes then set to equal widths.
    gene_tree: toytree.ToyTree
        A genealogy to embed in the species tree container.
    spacing: float
        A value to increase spacing between intervals to avoid overlap
        among angled intervals of the tree.
    min_width: float
        A value for the minimum width of intervals after Ne values are
        re-scaled and binned make visualizations fit more simply on
        the canvas.
    max_width: float
        See min_width.
    """
    tree: Union[ToyTree, int]
    spacing: float = 1.5
    blend: bool = False

    # Attributes
    intervals: Dict[int, Interval] = field(default_factory=dict, init=False)
    """: Dict of Interval class objects used for coordinates."""
    min_width: int = 2
    """: Minimum width of an interval, used to help fit drawing on canvas."""
    max_width: int = 8
    """: Maximum width of an interval, used to help fit drawing on canvas."""
    canvas: Canvas = None
    axes: Cartesian = None

    def __post_init__(self):
        """Assign coordinates to Intervals in the species tree model.

        The width of intervals and spacing can be tuned by the user.
        """
        # single population coalescent
        if isinstance(self.tree, (int, float)):
            self.intervals[0] = Interval(
                width=8,
                height=np.inf,
                xpos=0,
                ypos=0,
                neff=self.tree,
                blend=self.blend
            )
            tree = ToyTree(Node(name="0"))
            tree[0].Ne = self.tree
            self.tree = tree
            return

        # species tree model
        # get the widths of the tip intervals
        if "Ne" not in self.tree.features:
            self.tree = self.tree.set_node_data("Ne", default=1000)
        widths = get_range_mapped_feature(
            self.tree,
            "Ne",
            min_value=self.min_width,
            max_value=self.max_width,
            nan_value=self.min_width,
        )

        # traverse in idx order (tips then post-order for internal)
        for idx, node in enumerate(self.tree):

            # tips get x-position from widths starting from zero, whereas
            # internal nodes get their midpoint from child nodes and then
            # expand to sides for width.
            if not node.is_leaf():
                xmids = [self.intervals[child.idx].xmid for child in node.children]
                xmid = sum(xmids) / len(xmids)
                xpos = xmid - (widths[idx] / 2.)
            else:
                xpos = 0 if not idx else self.intervals[idx - 1].xb1 + self.spacing

            # store the interval
            self.intervals[idx] = Interval(
                width=widths[idx],
                height=node.dist,
                xpos=xpos,
                ypos=node.height,
                neff=node.Ne,
                blend=self.blend
            )

            # set child-parent relationships
            self.intervals[idx].children = []
            for child in node.children:
                cidx = child.idx
                self.intervals[cidx].up = self.intervals[idx]
                if self.intervals[idx].children:
                    self.intervals[cidx].left = True
                self.intervals[idx].children.append(self.intervals[cidx])

    def setup_drawing(self, **kwargs) -> Tuple[Canvas, Cartesian]:
        self.canvas = toyplot.Canvas(
            width=kwargs.pop('width', 400),
            height=kwargs.pop('height', 400),
        )
        self.axes = self.canvas.cartesian()
        self.axes.x.show = False
        self.axes.y.ticks.show = True
        return self.canvas, self.axes

    def draw_intervals(
        self,
        container_fill: ColorType,
        container_fill_opacity: float,
        container_fill_opacity_alternate: bool = False,
    ):
        """Return a toyplot drawing of the container.

        """
        # do nothing if single population
        if self.tree.ntips == 1:
            return

        # setup canvas and axes
        # add fill intervals
        marks = []
        for node in self.tree.traverse("levelorder"):
            idx = node.idx
            ival = self.intervals[idx]

            # hover-over information for interval
            title = (
                f"idx={idx}\n"
                f"Ne={ival.neff:.2g}\n"
                f"Tc={ival.height / (2 * ival.neff):.3g}\n"
                f"Tg={ival.height:.2g}"
            )

            # optional alternating stripes of color opacity
            ival.fill = container_fill
            ival.fill_opacity = container_fill_opacity
            if container_fill_opacity_alternate:
                if not ival.up:
                    ival.stripe = 1
                    ival.opacity = container_fill_opacity
                elif ival.up.stripe == 1:
                    ival.stripe = 0
                    ival.opacity = container_fill_opacity / 2
                else:
                    ival.opacity = container_fill_opacity
                    ival.stripe = 1

            # do not draw root yet
            if node.is_root():
                continue

            # draw other nodes (angled left or right)
            if ival.left:
                mark = self.axes.fill(
                    [ival.xb0, ival.xt0, ival.xb1, ival.xt1],
                    [ival.y0, ival.y0, ival.y0, ival.y1],
                    [ival.y0, ival.y1, ival.y1, ival.y1],
                    title=title,
                    color=ival.fill,
                    opacity=ival.opacity,
                )
            else:
                mark = self.axes.fill(
                    [ival.xt0, ival.xb0, ival.xt1, ival.xb1],
                    [ival.y1, ival.y0, ival.y0, ival.y0],
                    [ival.y1, ival.y1, ival.y1, ival.y0],
                    title=title,
                    color=ival.fill,
                    opacity=ival.opacity,
                )
            marks.append(mark)

        # style the drawing
        return self.canvas, self.axes, marks

    def draw_root_interval(
        self,
        container_fill: ColorType,
        container_fill_opacity: float,
        height: float = 100,
    ):
        """
        # draw the root (no angle) as 20% of treeheight by default.
        # To draw this height to fit the gene tree requires knowing
        # the gene tree's root height...
        """
        ival = self.intervals[max(self.intervals)]
        title = (
            f"idx={max(self.intervals)}\n"
            f"Ne={ival.neff:.2g}\n"
            f"Tc={ival.height / (2 * ival.neff):.3g}\n"
            f"Tg={ival.height:.2g}"
        )
        mark = self.axes.fill(
            [ival.xb0, ival.xb0, ival.xb1, ival.xb1],
            [ival.y0] * 4,
            [ival.y0, ival.y0 + height, ival.y0 + height, ival.y0],
            title=title,
            color=container_fill,
            opacity=container_fill_opacity,
        )
        return mark
        # tee = len(str(int(self.maxheight)))
        # tze = (1 * 10 ** (tee - 2))
        # tma = self.maxheight
        # trd = round(tma / tze) * tze
        # print(tee, tze, tma, trd)
        # axes.y.ticks.locator = toyplot.locator.Explicit(
        #     np.linspace(0, trd, 6).astype(int)[:-1],
        #     ["{:.0f}".format(i) for i in np.linspace(0, trd, 6).astype(int)][:-1],
        # )
        # self.axes.y.domain.max = self.maxheight + (self.maxheight * 0.01)
        # self.axes.y.domain.min = -self.maxheight * 0.05

    def draw_stroke(
        self,
        container_stroke,
        container_stroke_width,
        container_stroke_opacity,
    ):
        # TODO
        pass


@dataclass
class EmbeddingPlot:
    """Embed a gene tree in a container.

    This ...
    """
    species_tree: Union[ToyTree, int]
    gene_tree: ToyTree
    imap: Mapping[str, Sequence[str]] = field(default_factory=dict)
    blend: bool = False
    spacing: float = 1.5
    min_width: float = 2.
    max_width: float = 8.
    table: DataFrame = field(default=None, repr=False, init=False)
    container: Container = field(default=None, repr=False, init=False)

    # drawing components
    canvas: Canvas = field(default=None, repr=None, init=False)
    axes: Cartesian = field(default=None, repr=None, init=False)
    marks: List[Mark] = field(default_factory=list, repr=False, init=False)
    _xpoints: List[float] = field(default_factory=list, repr=None, init=False)
    _ypoints: List[float] = field(default_factory=list, repr=None, init=False)
    _labels: List[str] = field(default_factory=list, repr=None, init=False)

    def __post_init__(self):
        # create a container of connected intervals and a ToyTree w/ Ne values
        self.container = Container(
            self.species_tree, blend=self.blend, spacing=self.spacing,
            min_width=self.min_width, max_width=self.max_width,
        )
        self.species_tree = self.container.tree

        # ensure imap
        self.imap = self.imap if self.imap else {'0': self.gene_tree.get_tip_labels()}

        # get a genealogy embedding table
        self.table = get_genealogy_embedding_table(
            self.species_tree, self.gene_tree, self.imap)

    def get_node_coordinates(self, container_root_height: int) -> None:
        """Sample position of each Node at interval (start, end/coal)

        """
        for sidx, ival in self.container.intervals.items():
            tab = self.table[self.table.st_node == sidx]

            if sidx < self.species_tree.ntips:
                # store evenly spaced intervals of tip nodes
                nedges = tab.iloc[0].nedges
                xpos = np.linspace(ival.xb0, ival.xb1, nedges + 2)[1:-1]
                for nidx, pos in zip(tab.iloc[0].edges, xpos):
                    ival.data[nidx] = [pos]
                self._xpoints.append(xpos)
                self._ypoints.append(np.repeat(ival.y0, nedges))
                self._labels.append([f"node={nidx}" for nidx in tab.iloc[0].edges])

            else:
                # get positions at interval intersections from left child
                cidx = self.species_tree[sidx].children[0].idx
                tabl = self.table[self.table.st_node == cidx]
                nedges = tabl.iloc[-1].nedges
                edges = tabl.iloc[-1].edges
                # print(sidx, 'l', edges, ival.children[0].data)
                edges = sorted(edges, key=lambda x: ival.children[0].data[x][0])
                xposl = np.linspace(ival.xb0, ival.xmid, nedges + 2)[1:-1]
                for nidx, pos in zip(edges, xposl):
                    ival.data[nidx] = [pos]

                # get positions at interval intersections from right child
                cidx = self.species_tree[sidx].children[1].idx
                tabr = self.table[self.table.st_node == cidx]
                nedges = tabr.iloc[-1].nedges
                edges = tabr.iloc[-1].edges
                edges = sorted(edges, key=lambda x: ival.children[1].data[x][0])
                # print(sidx, 'r', edges, ival.children[1].data)
                xposr = np.linspace(ival.xmid, ival.xb1, nedges + 2)[1:-1]
                for nidx, pos in zip(edges, xposr):
                    ival.data[nidx] = [pos]
                # self._xpoints.append(np.concatenate([xposl, xposr]))
                # self._ypoints.append(np.repeat(ival.y0, xpos.size))

            # store midpoint positions for coalescence nodes
            for idx in tab.index[:-1]:

                # get who coalesced into whom
                cidxs = set(tab.loc[idx].edges) - set(tab.loc[idx + 1].edges)
                nidx = set(tab.loc[idx + 1].edges) - set(tab.loc[idx].edges)

                # get midpoint position on slope
                shifted = []
                for c in cidxs:
                    pos = ival.data[c][0]
                    slope = ival.slope(pos)
                    # length of edge in this interval
                    node = self.gene_tree[c]
                    dist = node.height + node.dist - ival.ypos
                    shifted.append(pos + (dist * slope))
                    # shifted.append(ival.data[c][0] + shift)
                xpos = sum(shifted) / 2.

                # store the start position of the ancestor coal node
                nidx = nidx.pop()
                ival.data[nidx] = [xpos]

                # store the end positions of nodes that coalesced
                for cidx in cidxs:
                    ival.data[cidx].append(xpos)

                # only store point for plotting if inside plotted intervals
                ypos = tab.loc[idx].stop
                if ypos <= container_root_height:
                    self._xpoints.append([xpos])
                    self._ypoints.append([ypos])
                    self._labels.append([f"node={nidx}"])

    def add_connecting_lines(
        self,
        edge_stroke,
        edge_stroke_width,
        edge_stroke_inherit: bool,
        edge_stroke_opacity: float,
        edge_samples: int,
        edge_variance: int,
        container_root_height: int
    ):
        """...
        """
        # scaling the wiggle. Allow 50 wiggles from tip to root, sample
        # number of wiggles per edge according to the proportion of len.
        if (edge_samples < 2) | (edge_variance <= 0):
            edge_samples = 0
            edge_variance = 1

        # colormap
        # edge_stroke,
        cmap = get_color_mapped_values(range(self.species_tree.ntips), cmap="Dark2")

        # draw edges within each interval
        for sidx, ival in self.container.intervals.items():
            # stroke = stroke if stroke is not None else COLORS2[sidx]
            table = self.table[self.table.st_node == sidx]
            edges_in_interval = set.union(*table.edges.apply(set).tolist())
            for e in edges_in_interval:
                if e != self.gene_tree.treenode.idx:
                    prop = self.gene_tree[e].dist / self.gene_tree.treenode.height
                    nsamps = int(prop * edge_samples) + 2

                    # get x coords
                    x0 = ival.data[e][0]
                    x1 = ival.data[e][1] if len(ival.data[e]) == 2 else ival.up.data[e][0]

                    # get y coords
                    y0 = self.gene_tree[e].height
                    if y0 < table.iloc[0, 0]:
                        y0 = table.iloc[0, 0]
                    if y0 >= container_root_height:
                        continue
                    y1 = self.gene_tree[e].up.height
                    if y1 > table.iloc[-1, 1]:
                        y1 = table.iloc[-1, 1]

                    # if sample does not coalesce in final interval
                    if y1 > container_root_height:
                        y1 = container_root_height
                        xdiff = x0 - x1
                        x1 = x0 - (xdiff / 2.)

                    # override color to black if internal not monophyletic
                    kidx = check_monophyly(self.gene_tree[e].get_leaf_names(), self.imap)
                    if kidx == -1:
                        stroke = "black"
                    else:
                        stroke = cmap[kidx]

                    # add wiggle to x coords
                    ypos = np.linspace(y0, y1, nsamps)
                    xpos = np.linspace(x0, x1, nsamps)
                    xpos[1:-1] += np.random.uniform(-edge_variance, edge_variance, size=nsamps - 2)
                    self.axes.plot(
                        xpos, ypos,
                        color=stroke,
                        stroke_width=edge_stroke_width,
                        # stroke_opacity=stroke_opacity
                    )

    def add_tip_labels(self):
        for sidx, ival in self.container.intervals.items():
            if sidx < self.species_tree.ntips:
                xpos = [ival.data[i][0] for i in ival.data if i < self.gene_tree.ntips]
                names = [i for i in ival.data if i < self.gene_tree.ntips]
                names = [self.gene_tree[i].name for i in names]
                self.axes.text(
                    xpos, [0] * len(xpos), names,
                    angle=-90,
                    style={
                        "font-size": 12,
                        "fill": "black",
                        "-toyplot-anchor-shift": 20,
                    },
                )

    def add_nodes(
        self,
        node_size,
        node_fill,
        node_fill_opacity,
        node_stroke,
        node_stroke_width,
    ):
        node_stroke = "none" if node_stroke is None else node_stroke
        self.axes.scatterplot(
            np.concatenate(self._xpoints),
            np.concatenate(self._ypoints),
            title=np.concatenate(self._labels),
            size=node_size,
            mstyle={
                "fill": node_fill,
                "fill-opacity": node_fill_opacity,
                "stroke": node_stroke,
                "stroke-width": node_stroke_width,
            }
        )

    def add_container(
        self,
        container_width,
        container_height,
        container_fill,
        container_fill_opacity,
        container_fill_opacity_alternate,
        container_stroke,
        container_stroke_opacity,
        container_stroke_width,
        container_root_height,
    ):
        self.canvas, self.axes = self.container.setup_drawing(
            width=container_width,
            height=container_height,
        )

        # draw the species tree w/ root interval depending on user option
        if self.species_tree.ntips == 1:
            self.container.draw_root_interval(
                container_fill=container_fill,
                container_fill_opacity=container_fill_opacity,
                height=container_root_height,  # self.gene_tree.treenode.height
            )
        else:
            self.container.draw_intervals(
                container_fill=container_fill,
                container_fill_opacity=container_fill_opacity,
                container_fill_opacity_alternate=container_fill_opacity_alternate,
            )
            self.container.draw_root_interval(
                container_fill=container_fill,
                container_fill_opacity=container_fill_opacity,
                height=container_root_height,
            )
        self.container.draw_stroke(
            container_stroke,
            container_stroke_opacity,
            container_stroke_width,
        )

    def draw(
        self,
        # container_blend_intervals: bool = False, # already applied
        container_width: int = 350,
        container_height: int = 300,
        container_fill: ColorType = "black",
        container_fill_opacity: float = 0.25,
        container_fill_opacity_alternate: bool = True,
        container_stroke: ColorType = "black",
        container_stroke_opacity: float = 1.0,
        container_stroke_width: float = 2,
        container_root_height: Union[int, bool] = True,
        node_fill: ColorType = "black",
        node_fill_opacity: float = 1.0,
        node_stroke: ColorType = None,
        node_stroke_width: int = 1,
        node_size: int = 5,
        edge_stroke: ColorType = "black",
        edge_stroke_width: int = 2,
        edge_stroke_inherit: bool = True,
        edge_stroke_opacity: float = 1.0,
        edge_samples: int = 10,
        edge_variance: float = 0.0,
        tip_labels_size: int = 10,
    ):
        # single population drawings fit the entire interval
        if self.species_tree.ntips == 1:
            if container_root_height is True:
                container_root_height = self.gene_tree.treenode.height
        else:
            if container_root_height is True:
                container_root_height = (
                    self.gene_tree.treenode.height - self.species_tree.treenode.height)

        # draw species tree container
        self.add_container(
            container_width, container_height,
            container_fill, container_fill_opacity, container_fill_opacity_alternate,
            container_stroke, container_stroke_opacity, container_stroke_width,
            container_root_height,
        )

        # sample positions at interval intersections
        self.get_node_coordinates(self.species_tree.treenode.height + container_root_height)

        # draw the figure
        self.add_connecting_lines(
            edge_stroke=edge_stroke,
            edge_stroke_width=edge_stroke_width,
            edge_stroke_inherit=True,
            edge_stroke_opacity=1.0,
            edge_samples=edge_samples,
            edge_variance=edge_variance,
            container_root_height=self.species_tree.treenode.height + container_root_height,
        )
        self.add_tip_labels()
        self.add_nodes(
            node_size,
            node_fill,
            node_fill_opacity,
            node_stroke,
            node_stroke_width,
        )


def check_monophyly(names, imap) -> int:
    for idx, key in enumerate(imap):
        vals = imap[key]
        if all(i in vals for i in names):
            return idx
    return -1


if __name__ == "__main__":

    import ipcoal
    import toytree
    toytree.set_log_level("INFO")

    # tree = toytree.rtree.unittree(ntips=4, treeheight=1e6, seed=123)
    # tree = tree.mod.edges_slider(seed=333)
    # model = ipcoal.Model(tree, Ne=1e5)
    # model.sim_trees(5)
    # gtree = toytree.tree(model.df.genealogy[0])

    S = toytree.rtree.imbtree(3, treeheight=5e3)
    S.set_node_data("Ne", default=3000, inplace=True)
    M = ipcoal.Model(S, nsamples=3, seed_trees=123)
    M.sim_trees(10)
    G = toytree.tree(M.df.genealogy[0])
    IMAP = M.get_imap_dict()

    E = EmbeddingPlot(S, G, IMAP, blend=1)
    E.sample_intersection_positions()
    E.add_coal_points()

    # con = Container(model.tree, blend=True)
    # print(con.intervals)

    # c, a, m = con.draw(width=400, height=250, color='black', stripe=True, opacity=0.33);
    # a.x.show = True
    # toytree.utils.show(c)
