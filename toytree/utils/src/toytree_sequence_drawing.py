#!/usr/bin/env python

"""Utilities for visualizing TreeSequences from tskit or SLiM.

The :class:`ToyTreeSequence` class holds the tskit.trees.TreeSequence 
object in its `.tree_sequence` attribute. It is primarily used to 
generate drawings of one or more trees with the option to display 
mutations, MutationTypes, and a chromosome structure. These latter 
options are mostly for SLiM simulated TreeSequences.

Examples
--------
>>> tts = toytree.utils.tree_sequence.ToyTreeSequence(tree_sequence)
>>> tts.draw_tree(idx=0)
>>> tts.draw()
"""

from typing import List, Tuple, Optional, Iterable
from dataclasses import dataclass
import toyplot
from toytree.utils.src.scrollable_canvas import ScrollableCanvas
import toytree


@dataclass
class Box:
    """Delimited boxes used in TreeSequenceDrawing."""
    left: float
    right: float
    top: float
    bottom: float


@dataclass
class MultiDrawing:
    trees: List['ToyTree']
    breakpoints: List[float]
    width: float
    height: float
    padding: float = 20
    margin: Tuple[float,float,float,float] = (50, 50, 50, 50)

    def __post_init__(self):
        self.height = self.height if self.height is not None else 325
        self.width = max(300, (
            self.width if self.width is not None else 
            15 * self.trees[0].ntips * len(self.trees)
        ))


class ToyTreeSequenceDrawing(MultiDrawing):
    """Return a drawing of multiple trees from a tree sequence.

    A ToyTreeSequence...

    Parameters
    ----------
    """
    def __init__(
        self,
        trees: List['ToyTree'],
        breakpoints: Iterable[int],
        width: Optional[int]=None,
        height: Optional[int]=None,
        padding: float=20,
        margin: Tuple[float,float,float,float]=(50,50,50,50),
        colormap: List['color']=None,
        scrollable: bool=True,
        axes: Optional['toyplot.coordinates.Cartesian']=None,
        **kwargs,
    ):
        super().__init__(trees, breakpoints, width, height, padding, margin)
        self.canvas = self.get_canvas(scrollable, axes)
        self.axes = self.get_axes(axes)
        self.marks = []

        # colormap
        self.icolors = toytree.color.color_cycler(colormap)

        # positioning
        self.xprop_space = 0.2
        self.xspace = max(2., self.xprop_space * self.trees[0].ntips - 1)
        self.xtree = self.xspace + self.trees[0].ntips - 1
        self.xmax = self.xtree * len(self.trees)
        self.ymax = max(tre.treenode.height for tre in self.trees)

        # store
        self.boxes = {}
        self.colors = {}

        # run funcs
        self.get_position_bar_marks()
        self.get_polygon_container_marks()
        self.get_tree_marks(kwargs)
        self.set_axes_style()

    def __repr__(self):
        return "<TreeSequenceDrawing>"

    def get_canvas(self, scrollable, axes):
        """Return a toyplot.Canvas with option for width overflow."""
        # if an existing axes was passed then use its canvas
        if axes is not None:
            return None
        # create a new canvas
        if scrollable:
            canvas = ScrollableCanvas(width=self.width, height=self.height)
        else:
            canvas = toyplot.Canvas(width=self.width, height=self.height)
        return canvas

    def get_axes(self, axes):
        """Get toyplot axes, or use input one. 
        Makes a 'share' axes so that ticks appear on top of plot.
        """
        if axes is not None:
            return axes
        axes = self.canvas.cartesian(margin=self.margin, padding=self.padding)
        axes2 = axes.share('y')
        axes.x.show = False
        return axes2


    def get_position_bar_marks(self):
        """Get breakpoint bars on top spanning horizontal axis.
        """
        for idx, pos in enumerate(self.breakpoints[:-1]):

            # top bar starts with \ and ends with /
            pos0 = self.xmax * (self.breakpoints[idx] / max(self.breakpoints))
            pos1 = self.xmax * (self.breakpoints[idx + 1] / max(self.breakpoints))
            if pos == self.breakpoints[-2]:
                pos1 += self.xspace

            box = Box(
                left=pos0,
                right=pos1,
                top=self.ymax + self.ymax * 0.25,
                bottom=self.ymax + self.ymax * 0.2,
            )
            self.boxes[idx] = box
            self.colors[idx] = next(self.icolors)

            self.axes.fill(
                [box.left, box.right],
                [box.bottom, box.bottom],
                [box.top, box.top],
                style={
                    "fill": self.colors[idx],
                    "fill-opacity": 0.85,
                    'stroke': 'white',
                    'stroke-opacity': 0.5,
                },
            )

    def get_polygon_container_marks(self):
        """
        Get polygon fill marks to surround trees.
        """
        for idx, _ in enumerate(self.trees):
            box = self.boxes[idx]
            tbox = Box(
                left=self.xspace / 2 + (idx * self.xtree),
                right=self.xspace / 2 + ((idx + 1) * self.xtree),
                top=self.ymax,
                bottom=0,
            )

            # hover pop-up
            title = "\n".join([
                f"idx: {idx}",
                f"interval: ({self.breakpoints[idx]:.0f} - {self.breakpoints[idx + 1]:.0f})",
                f"tmrca: {round(self.trees[idx].treenode.height, 2)}",
                #f"mutations: 0", # todo
                #f"alleles: 1", # todo
            ])

            # polygon style
            pstyle = {
                "fill": self.colors[idx],
                'fill-opacity': 0.25,
                'stroke': 'white',
                'stroke-opacity': 0.5,
            }

            # draw polygons
            if box.left < tbox.right:
                self.axes.fill(
                    [box.left,   tbox.left,  tbox.left,   tbox.right,  tbox.right, box.right],
                    [box.bottom, tbox.top,   tbox.bottom, tbox.bottom, tbox.top,   box.bottom],
                    [box.bottom, box.bottom, box.bottom,  box.bottom,  box.bottom, box.bottom],
                    annotation=False,
                    title=title,
                    style=pstyle,
                )
            else:
                self.axes.fill(
                    [tbox.left,   box.left,    box.right,   tbox.right,],
                    [tbox.bottom, tbox.bottom, tbox.bottom, tbox.bottom],
                    [tbox.top,    box.bottom,  box.bottom,  tbox.top,  ],
                    annotation=False,
                    title=title,
                    style=pstyle,
                )

    def get_tree_marks(self, kwargs):
        """Get ToyTree marks.
        """
        for idx, tree in enumerate(self.trees):
            base_style = {
                'xbaseline': self.xspace + (idx * self.xtree),
                'layout': 'd',
                'scale_bar': True,
                'tip_labels_style': {"font-size": "10px"}
            }
            base_style.update(kwargs)
            _, _, mark = tree.draw(axes=self.axes, **base_style)
            # mark.annotation = True
            self.marks.append(mark)

            # build mutation marker info
            xpos = []
            ypos = []
            titles = []
            colors = []
            for mut in tree.mutations:

                # get node id and time using the 'tsidx' (tskit node id)
                node = tree.tsidx_dict[mut.node]
                time = mut.time

                # skip if on root edge (shared by all)
                if node.is_root():
                    continue

                # project mutation points to proper layout type
                xpos.append(node._x + mark.xbaseline)
                ypos.append(time)

                # store color and title for this point
                try:
                    mtype = int(mut.metadata['mutation_list'][0]['mutation_type'])
                except Exception:
                    mtype = 0
                    
                color = toytree.color.COLORS1[mtype]
                colors.append(color)
                title = (
                    f"id: {mut.id}\n"
                    f"pos: {mut.site:.0f}\n"
                    f"time: {mut.time:.0f}\n"
                    f"mtype: {mtype}")
                titles.append(title)

            # update mutation style dict
            mstyle = {"stroke": "black"}

            # draw the mutations
            if xpos:
                mark = self.axes.scatterplot(
                    xpos, ypos,
                    marker='o',
                    size=7,
                    color=colors,
                    mstyle=mstyle,
                    title=titles,
                )
                mark.annotation = True
                self.marks.append(mark)

    def set_axes_style(self):
        """Adds ..."""
        # get tick marks within domain 
        locator = toyplot.locator.Extended(only_inside=True)
        ticks = locator.ticks(0, max([i.top for i in self.boxes.values()]))
        self.axes.y.ticks.locator = toyplot.locator.Explicit(*ticks)

        # import numpy as np
        # locator = toyplot.locator.Extended(count=10, only_inside=True)
        # ticks = locator.ticks(0, self.xmax)
        # labels = locator.ticks(min(self.breakpoints), max(self.breakpoints))
        # self.axes.x.ticks.locator = toyplot.locator.Explicit(
        #     ticks[0], labels[1])


if __name__ == "__main__":
    pass
