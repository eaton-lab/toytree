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


"""

# pylint: disable=invalid-name

from __future__ import annotations
from typing import List, Dict, Optional
from functools import cached_property
from dataclasses import dataclass, field
from loguru import logger
import numpy as np

from toytree.utils.transform import normalize_values
import toytree
import toyplot
import ipcoal

logger = logger.bind(name="toytree")


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
    xpos: float=0
    ypos: float=0
    neff: float=0
    up: Optional[Interval]=field(default=None, init=False, repr=False)
    children: List[Interval]=field(default_factory=list, init=False, repr=False)
    left: bool=False
    blend: bool=False

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
        if self.left:
            return self.up.xmid - self.width
        return self.up.xmid

    @cached_property
    def xt1(self):
        """Return the right x-position on the upper bound"""
        if self.left:
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

    @cached_property
    def slope(self):
        """Return the slope (delta x / delta y) for use in :func:is_inside()"""
        return (self.xt0 - self.xb0) / self.height

    def is_inside(
        self, 
        xpos: float, 
        ypos: float, 
        padding: float=0.0, 
        ):
        """Return True if coordinate position is inside the interval.

        This is used to avoid overlaps among intervals, and to ensure
        embedded gene trees do not extend outside of of the interval.
        The padding parameter can be used to further limit embeddings 
        from coming too close to the edge, or similarly, margin will 
        pad the outside to limit how close intervals are to each other.
        """
        ypass = self.y0 <= ypos <= self.y1
        xmin_at_ypos = self.xb0 + padding + (ypos - self.y0) * self.slope
        xmax_at_ypos = self.xb1 - padding + (ypos - self.y0) * self.slope
        # logger.info(f"xmin_at_ypos: {xmin_at_ypos}")
        # logger.info(f"xmax_at_ypos: {xmax_at_ypos}")
        xpass = xmin_at_ypos <= xpos <= xmax_at_ypos
        return xpass & ypass

    def is_overlapping(
        self, 
        xpos: float, 
        ypos: float, 
        border: float=0.0, 
        ):
        """Return True if coordinate position is inside the interval.

        This is used to avoid overlaps among intervals, and to ensure
        embedded gene trees do not extend outside of of the interval.
        The padding parameter can be used to further limit embeddings 
        from coming too close to the edge, or similarly, margin will 
        pad the outside to limit how close intervals are to each other.
        """
        margin: float=0.0        


@dataclass
class Container:
    """Container to visualize a genealogy embedded in a species tree.

    A container drawing is composed of multiple Interval class 
    instances that each have coordinates 

    Parameters
    ----------
    model: ipcoal.Model
        An ipcoal Model class instance.
    idx: int or None
        The index of a genealogy to embed in the species tree drawing.
    spacer: float
        A value to increase spacing between intervals to avoid overlap
        among angled intervals of the tree.
    min_width: float
        A value for the minimum width of intervals after Ne values are
        re-scaled and binned make visualizations fit more simply on 
        the canvas.
    max_width: float
        See min_width.
    """
    model: ipcoal.Model
    idx: Optional[int] = None
    spacer: float = 1.5
    blend: bool = False

    # Attributes
    intervals: Dict[int, Interval] = field(default_factory=dict, init=False)
    """Dict of Interval class objects used for coordinates."""
    min_width: int = 2
    """Minimum width of an interval, used to help fit drawing on canvas."""
    max_width: int = 8
    """Maximum width of an interval, used to help fit drawing on canvas."""    

    def __post_init__(self):
        """Assign coordinates to Intervals in the species tree model.

        The width of intervals and spacing can be tuned by the user.
        """
        # get the widths of the tip intervals
        widths = normalize_values(
            values=self.model.tree.get_node_data("Ne"),
            nbins=10,
            min_value=self.min_width,
            max_value=self.max_width,
        )

        # traverse in idx order (tips then post-order for internal)
        for idx, node in enumerate(tree):

            # tips get x-position from widths starting from zero, whereas
            # internal nodes get their midpoint from child nodes and then
            # expand to sides for width.
            if not node.is_leaf():
                xmids = [self.intervals[tnode.idx].xmid for tnode in node.children]
                xmid = sum(xmids) / len(xmids)
                xpos = xmid - (widths[idx] / 2.)
            else:
                if not idx:
                    xpos = 0
                else:
                    last_interval = self.intervals[idx - 1]
                    xpos = last_interval.xb1 + self.spacer

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


    def draw(self, stripe: bool=False, **kwargs: dict):
        """Return a toyplot drawing of the container."""
        # setup canvas and axes
        canvas = toyplot.Canvas(
            width=kwargs.pop('width', 400), 
            height=kwargs.pop('height', 400),
        )
        axes = canvas.cartesian()

        # add fill intervals
        marks = []
        for node in self.model.tree.treenode.traverse():
            idx = node.idx
            ival = self.intervals[idx]

            # hover-over information for interval
            title = (
                f"idx={idx}\n"
                f"Ne={ival.neff:.0f}\n"
                f"Tc={ival.height / (2 * ival.neff):.3f}\n"
                f"Tg={ival.height:.0f}"
            )

            # optional alternating stripes of color opacity
            if stripe:
                if not ival.up:
                    opacity = kwargs.pop('opacity', 0.6)
                    kwargs['opacity'] = opacity
                    ival.tone = 'dark'
                elif ival.up.tone == "light":
                    kwargs['opacity'] = opacity
                    ival.tone = 'dark'
                else:
                    kwargs['opacity'] = opacity / 2
                    ival.tone = 'light'

            # draw the root (no angle)
            if not ival.up:
                temp_height = self.model.tree.treenode.height * 0.2
                mark = axes.fill(
                    [ival.xb0, ival.xb0, ival.xb1, ival.xb1],
                    [ival.y0] * 4,
                    [ival.y0, ival.y0 + temp_height, ival.y0 + temp_height, ival.y0],
                    title=title,
                    **kwargs,
                )

            # draw other nodes (angled left or right)
            else:
                if ival.left:
                    mark = axes.fill(
                        [ival.xb0, ival.xt0, ival.xb1, ival.xt1],
                        [ival.y0, ival.y0, ival.y0, ival.y1],
                        [ival.y0, ival.y1, ival.y1, ival.y1],
                        title=title,                        
                        **kwargs,
                    )
                else:
                    mark = axes.fill(
                        [ival.xt0, ival.xb0, ival.xt1, ival.xb1],
                        [ival.y1, ival.y0, ival.y0, ival.y0],
                        [ival.y1, ival.y1, ival.y1, ival.y0],
                        title=title,                        
                        **kwargs,
                    )
            marks.append(mark)

        # style the drawing
        axes.x.show = False
        axes.y.ticks.show = True
        # tee = len(str(int(self.maxheight)))
        # tze = (1 * 10 ** (tee - 2))
        # tma = self.maxheight
        # trd = round(tma / tze) * tze
        # print(tee, tze, tma, trd)
        # axes.y.ticks.locator = toyplot.locator.Explicit(
            # np.linspace(0, trd, 6).astype(int)[:-1],
            # ["{:.0f}".format(i) for i in np.linspace(0, trd, 6).astype(int)][:-1],
        # )
        # self.axes.y.domain.max = self.maxheight + (self.maxheight * 0.01)
        # self.axes.y.domain.min = -self.maxheight * 0.05        

        return canvas, axes, marks


class Embedding:
    r"""Sample points within bounds to connect lower to upper edge.

                   \     \
           _________\123 4\___
          /        1 23 | 4   \
         /     1 2   3 /\ 4    \
        /__1___2___3__/  \ 4  __\

    Applies an OU method to attract points towards the sloped line, 
    while allowing for wiggling off of the line. 

    Sample points at N intervals across the entire tree, then 
    """
    xs_start: np.ndarray
    xs_end: np.ndarray
    y_pos: np.ndarray


if __name__ == "__main__":

    toytree.set_log_level("INFO")

    tree = toytree.rtree.unittree(ntips=5, treeheight=1e6, seed=123)
    model = ipcoal.Model(tree, Ne=1e5)
    model.sim_trees(5)

    con = Container(model, idx=0)
    print(con.intervals)
