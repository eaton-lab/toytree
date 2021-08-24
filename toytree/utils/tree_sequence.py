#!/usr/bin/env python

"""
Utilities for working with tree sequences. This is currently used
by the ipcoal library to visualize tree sequences simulated in 
msprime. This is not necessarily intended to be a user-friendly 
tool

Example:
---------
import msprime as ms
import toytree

ts = ms.sim_ancestry(...)
tts = toytree.utils.tree_sequence.ToyTreeSequence(ts)
tree = tts.at_index(0)
"""

from typing import List, Union, Tuple, Optional
from dataclasses import dataclass
import toyplot
import toytree



class ScrollableCanvas(toyplot.Canvas):
    """Canvas subclass with horizontal scrolling on large widths"""
    def _repr_html_(self):
        return toyplot.html.tostring(
            self, style={"text-align": "center", "width": f"{self.width}px"}
        )

@dataclass
class Box:
    left: float
    right: float
    top: float
    bottom: float

@dataclass
class MultiDrawing:
    trees: Union['toytree.MultiTree', 'tskit.trees.TreeSequence']
    breakpoints: List[float]
    width: float
    height: float
    padding: float = 20
    margin: Tuple[float,float,float,float] = (50, 50, 50, 50)
    # todo: set width and height from tree dims if None...


class TreeSequenceDrawing(MultiDrawing):
    """
    Generate a tree-sequence drawing for ntrees.
    """
    def __init__(self, colormap=None, **kwargs):
        super().__init__(**kwargs)

        self.canvas = self.get_canvas()
        self.axes = self.get_axes()

        # colormap
        self.icolors = toytree.color_cycler(colormap)

        # positioning
        self.xprop_space = 0.2
        self.xspace = self.xprop_space * self.trees[0].ntips - 1
        self.xtree = self.xspace + self.trees[0].ntips - 1
        self.xmax = self.xtree * len(self.trees)
        self.ymax = max(tre.treenode.height for tre in self.trees)

        # store
        self.boxes = {}
        self.colors = {}

        # run funcs
        self.get_position_bar_marks()
        self.get_polygon_container_marks()
        self.get_tree_marks()
        self.set_axes_style()

    def get_canvas(self):
        """
        Get a horizontal scrollable canvas
        """
        # TODO: use Canvas Method to get dim from tree stats
        canvas = ScrollableCanvas(width=self.width, height=self.height)
        return canvas

    def get_axes(self):
        """
        Get a 'share' axes on the top of plot
        """
        axes = self.canvas.cartesian(margin=self.margin, padding=self.padding)
        return axes

    def get_position_bar_marks(self):
        """
        Get breakpoint bars.
        """
        for idx, _ in enumerate(self.breakpoints[:-1]):
            pos0 = self.xmax * (self.breakpoints[idx] / max(self.breakpoints))
            pos1 = self.xmax * (self.breakpoints[idx + 1] / max(self.breakpoints))            
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
                f"mutations: 0",
                f"alleles: 1",
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
                    annotation=True,
                    title=title,
                    style=pstyle,
                )
            else:
                self.axes.fill(
                    [tbox.left,   box.left,    box.right,   tbox.right,],
                    [tbox.bottom, tbox.bottom, tbox.bottom, tbox.bottom],
                    [tbox.top,    box.bottom,  box.bottom,  tbox.top,  ],
                    annotation=True,
                    title=title,
                    style=pstyle,
                )

    def get_tree_marks(self):
        """
        Get ToyTree marks.
        """
        for idx, tree in enumerate(self.trees):
            tree.draw(
                axes=self.axes,
                xbaseline=self.xspace + (idx * self.xtree),
                layout='d',
                scale_bar=True,
                tip_labels_style={"font-size": "10px"}
            )

    def set_axes_style(self):
        self.axes.y.locator = toyplot.locator.Extended(only_inside=True)
        # self.axes.x.locator = toyplot.locator.Extended(only_inside=True)
        self.axes.x.show = True
        self.axes.x.locator = toyplot.locator.Explicit(self.breakpoints)
        # top_axes = axes.share("y")
        # axes.x.show = False
        # top_axes.x.show = True
        # top_axes.x.ticks.show = True


@dataclass
class ToyTreeSequence:
    """
    Class for converting tskit TreeSequence objects to ToyTrees, 
    with some associated metadata, for generating toytree drawings.
    """
    tree_sequence: 'tskit.trees.TreeSequence'
    _i: int = 0

    def __len__(self):
        return self.tree_sequence.num_trees

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.at_index(self._i)
        except IndexError as err:
            self._i = 0
            raise StopIteration from err
        self._i += 1
        return result

    def __repr__(self):
        return f"<ToyTreeSequence ntrees={len(self)}>"

    def at_index(self, index: int):
        """
        Returns a ToyTree from the indexed order in the tree_sequence.
        """
        # bpoints = self.tree_sequence.breakpoints(as_array=True)[:-1]
        # position = bpoints[index]
        tree = self.tree_sequence.at_index(index)
        return self._get_toytree(tree)        

    def at_site(self, pos: int):
        """
        Returns a ToyTree for a position in the tree_sequence.
        """
        tree = self.tree_sequence.at(pos)
        return self._get_toytree(tree, site=pos)

    def _get_toytree(self, tree: 'tskit.trees.Tree', site: Optional[int]=None):
        """
        Returns a Toytree for a tree selected by site or index.
        """
        # create the root node
        pdict = tree.get_parent_dict()        
        root_idx = max(pdict.values())
        idx_dict = {root_idx: toytree.TreeNode(name=root_idx, dist=0)}
        idx_dict[root_idx].add_feature("tsidx", root_idx)

        # add all children nodes
        for cidx in pdict:
            pidx = pdict[cidx]
            if pidx in idx_dict:
                pnode = idx_dict[pidx]
            else:
                pnode = toytree.TreeNode(
                    name=str(pidx),
                    dist=tree.branch_length(pidx)
                )
                pnode.add_feature("tsidx", pidx)
                idx_dict[pidx] = pnode
            if cidx in idx_dict:
                cnode = idx_dict[cidx]
            else:
                pop = self.tree_sequence.tables.nodes.population[cidx]
                cnode = toytree.TreeNode(
                    name=f"p{pop}-{cidx}",
                    dist=tree.branch_length(cidx),
                )
                cnode.add_feature("tsidx", cidx)
                idx_dict[cidx] = cnode
            cnode.up = pnode
            pnode.children.append(cnode)

        # wrap TreeNode as a toytree
        ttree = toytree.ToyTree(idx_dict[root_idx])

        # add Tree as metadata
        if site:
            ttree.mutations = [i for i in tree.mutations() if i.position == site]
        else:
            ttree.mutations = list(tree.mutations())

        # add dict to translate ts idx to toytree idx
        ttree.tsidx_dict = ttree.get_feature_dict("tsidx", None)
        return ttree

    def draw(
        self,
        height: int=None,
        width: int=None,
        show_mutations: bool=True,
        idxs: List[int]=None,
        scrollable: bool=True,
        **kwargs,
        ):
        # -> Tuple[toyplot.Canvas, toyplot.coordinates.cartesian, :
        """
        Returns a toyplot Canvas, Axes, and list of marks composing 
        a TreeSequenceDrawing with genealogies corresponding to 
        positions along a chromosome.

        Parameters:
        -----------
        """


    # def as_mtree(self):
    #     """
    #     Returns the tree sequence as a MultiTree object.
    #     """
    #     return toytree.mtree(list(self))



if __name__ == "__main__":

    # EXAMPLE
    import ipcoal
    import toyplot.browser

    TREE = toytree.rtree.unittree(10, treeheight=1e5)
    MOD = ipcoal.Model(tree=TREE, Ne=1e4, nsamples=1)
    MOD.sim_loci(5, 2000)
    
    # optional: access the tree sequences directly
    TS = MOD.ts_dict[0]

    # get a specific ToyTree
    TOYTS = ToyTreeSequence(TS)

    # draw the tree sequence
    TOYTS.draw(width=None, height=300, idxs=None, scrollable=True)

    # draw one tree
    TOY = TOYTS.at_index(0)
    TOY.draw()

    # tss = TreeSequence(ts)
    # print(list(tss))
    # tss.at_index(1)
    # print([i for i in tss])
    # .at_index(1)
    # print(tree)
