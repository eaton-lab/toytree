#!/usr/bin/env python

"""
MultiTree objects

TODO:
    - re-do support for BPP weird format trees.
    - set-like function that drops tips from each tree not shared by all trees.
    - root function that drops tree that cannot be rooted or not set-like
    - consensus function drop tips that are not in set.
    - treegrid simplify args (3, 3) e.g., will make a 600x600 canvas...
    - Annotate class for surrounding markers...
    - A distinct multitree mark for combining styles on topologies
    - New mark: leave proper space for tips to mtree fits same as tree.
"""

from typing import Union, List, Iterable, Optional, Tuple
from copy import deepcopy
from pathlib import Path
import numpy as np

from toytree.core.tree import ToyTree
from toytree.core.consensus import ConsensusTree
from toytree.core.io.TreeParser import TreeParser
from toytree.core.style.tree_style import TreeStyle, get_tree_style
from toytree.core.drawing.canvas_setup import GridSetup, CanvasSetup
# from toytree.core.drawing.render import ToytreeMark
from toytree.core.drawing.canvas_setup import style_ticks
from toytree.utils.exceptions import ToytreeError
import toytree


def mtree(
    data:Union[str, Path, List[ToyTree], List[str]],
    tree_format:int=0,
    ):
    """
    General class constructor to parse and return a MultiTree class
    object from input arguments as a multi-newick string, filepath,
    Url, or Iterable of Toytree objects.

    data (Union[str, Path, Iterable[ToyTree]]):
        string, filepath, or URL for a newick or nexus formatted list
        of trees, or an iterable of ToyTree objects.

    Examples:
    ----------
    mtre = toytree.mtree("many_trees.nwk")
    mtre = toytree.mtree("((a,b),c);\n((c,a),b);")
    mtre = toytree.mtree([toytree.rtree.rtree(10) for i in range(5)])
    """
    # parse the newick object into a list of Toytrees
    treelist = []
    if isinstance(data, Path):
        data = str(Path)
    if isinstance(data, str):
        tns = TreeParser(data, tree_format, multitree=True).treenodes
        treelist = [ToyTree(i) for i in tns]
    elif isinstance(data[0], ToyTree):
        treelist = data
    elif isinstance(data[0], (str, bytes)):
        treelist = [toytree.tree(i) for i in data]
    else:
        raise ToytreeError("mtree input format unrecognized.")
    return MultiTree(treelist)

    # set tip plot order for treelist to the first tree order
    # order trees in treelist to plot in shared order...
    # self._fixed_order = fixed_order   # (<list>, True, False, or None)
    # self._user_order = None
    # self._cons_order = None
    # self._set_tip_order()
    # self._parse_treelist()



class BaseMultiTree:
    def __init__(self):
        self.style = TreeStyle()
        self._i = 0
        self.treelist = []



# class MixedTree(BaseMultiTree):
#     pass


class MultiTree:
    """
    Toytree MultiTree object for plotting or extracting stats from
    a set of trees sharing the same tips. Use factory function
    toytree.mtree to init a MultiTree instance.
    """
    def __init__(self, treelist):
        self._i = 0
        self.treelist = treelist

    def __len__(self):
        return len(self.treelist)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.treelist[self._i]
        except IndexError as err:
            self._i = 0
            raise StopIteration from err
        self._i += 1
        return result

    def __repr__(self):
        """string representation shows ntrees and type"""
        return f"<toytree.MultiTree ntrees={len(self)}>"

    @property
    def ntips(self):
        """returns the number of tips (all the same) in each tree."""
        return self.treelist[0].ntips

    @property
    def ntrees(self):
        """returns the number of trees in the MultiTree treelist."""
        return len(self.treelist)

    @property
    def all_tips_shared(self):
        """Check if names are the same in all the trees in .treelist."""
        alltips_shared = all([
            set(self.treelist[0].get_tip_labels()) == set(i.get_tip_labels())
            for i in self.treelist
        ])
        if alltips_shared:
            return True
        return False

    def copy(self):
        """
        Returns a deepcopy of the MultiTree object.
        """
        return deepcopy(self)

    def write(
        self,
        path: Optional[Path],
        tree_format:int=0,
        features: Optional[Iterable[str]]=None,
        dist_formatter:str="%0.6g",
        ) -> Optional[str]:
        """
        Writes a multi-line string of newick trees to stdout or filepath
        """
        treestr = "\n".join([
            i.write(
                path=None,
                tree_format=tree_format,
                features=features,
                dist_formatter=dist_formatter,
            )
            for i in self.treelist]
        )
        if not path:
            return treestr
        with open(path, 'w') as outtre:
            outtre.write(treestr)
        return None


    def reset_tree_styles(self):
        """
        Sets the .style toytree drawing styles to default for all
        ToyTrees in a MultiTree .treelist.
        """
        for tre in self.treelist:
            tre.style = TreeStyle()


    # -------------------------------------------------------------------
    # Tree List Statistics or Calculations
    # -------------------------------------------------------------------
    # def get_tip_labels(self):
    #     """
    #     Returns the tip names in tree plot order for the *list of tree*,
    #     starting from the zero axis. If all trees in the treelist do not
    #     share the same set of tips then this will return an error message.

    #     If fixed_order is a user entered list then names are returned in that
    #     order. If fixed_order was True then the consensus tree order is
    #     returned. If fixed_order was None or False then the order of the first
    #     ToyTree in .treelist is returned.
    #     """
    #     if not self.all_tips_shared:
    #         raise Exception(
    #             "All trees in treelist do not share the same set of tips")
    #     return self.treelist[0].get_tip_labels()


    def get_consensus_tree(self, cutoff=0.0, best_tree=None):
        """
        Returns an extended majority rule consensus tree as a Toytree
        object. Node labels include 'support' values showing the
        occurrence of clades in the consensus tree across trees in the
        input treelist. Clades with support below 'cutoff' are
        collapsed into polytomies. If you enter an optional
        'best_tree' then support values from the treelist calculated
        for clades in this tree, and the best_tree is returned with
        support values added to nodes.

        Parameters
        ----------
        cutoff (float; default=0.0):
            Cutoff below which clades are collapsed in the majority
            rule consensus tree. This is a proportion (e.g., 0.5 means
            50%).
        best_tree (Toytree or newick string; optional):
            A tree that support values should be calculated for and
            added to. For example, you want to calculate how often
            clades in your best ML tree are supported in 100 bootstrap
            trees.
        """
        if best_tree is not None:
            if not isinstance(best_tree, ToyTree):
                best_tree = ToyTree(best_tree)
        cons = ConsensusTree(self.treelist, best_tree=best_tree, cutoff=cutoff)
        cons.update()
        return cons.ttree


    def draw(
        self,
        shape: Tuple[int,int]=(1, 4),
        shared_axes: bool=False,
        idxs: Optional[Iterable[int]]=None,
        width: Optional[int]=None,
        height: Optional[int]=None,
        margin: Union[float, Tuple[int,int,int,int]]=None,
        **kwargs,
        ) -> Tuple['toyplot.Canvas', List['axes'], List['marks']]:
        """
        Draw a set of trees on a grid with nice spacing and optionally
        with a shared axes. Different styles can be set on each tree
        individually or set here during drawing to be shared across
        trees.

        Parameters:
        -----------
        shape: Tuple[int,int]
            A tuple of (nrows, ncolumns) for tree grid drawing.
        shared_axes (bool):
            If True then the 'height' dimension will be shared among
            all trees, otherwise each tree is scaled to fill the
            space in its grid cell.
        idxs (int):
            The indices of trees in treelist that you want to draw. By
            default the first ncols*nrows trees are drawn, but you can
            select the 10-14th tree by entering idxs=[10,11,12,13]
        width (int):
            Width of the canvas
        height (int):
            Height of the canvas
        margin: Tuple[int,int,int,int]
            Spacing between subplots in the grid in pixel units. A
            single value or a tuple for top, right, bottom, left.
        kwargs (dict):
            Any style arguments supported by .draw() in toytrees.
        """
        # legacy support
        if kwargs.get("nrows") or kwargs.get("ncols"):
            raise DeprecationWarning(
                "nrows and ncols args deprecated. Use shape=(nrows, ncols)")

        # get index of trees that will be drawn
        nrows = max(1, shape[0])
        ncols = max(1, shape[1])
        if idxs is None:
            tidx = range(0, min(nrows * ncols, len(self.treelist)))
        else:
            tidx = idxs

        # get the subset list of ToyTrees
        treelist = [self.treelist[i] for i in tidx]

        # special multitree meaning fixed_order=True is consensus order
        if kwargs.get("fixed_order") is True:
            fixed_order = (
                MultiTree(treelist)
                .get_consensus_tree()
                .get_tip_labels()
            )
            kwargs["fixed_order"] = fixed_order

        # if less than 4 trees reshape ncols,rows to use ntrees
        if len(treelist) < 4:
            if nrows > ncols:
                nrows = len(treelist)
                ncols = 1
            else:
                nrows = 1
                ncols = len(treelist)

        # get layout first from direct arg then from treestyle
        if "ts" in kwargs:
            layout = get_tree_style(kwargs.get("ts")).layout
        elif "tree_style" in kwargs:
            layout = get_tree_style(kwargs.get("ts")).layout
        else:
            layout = kwargs.get("layout", 'r')

        # get the canvas and axes that can fit the requested trees.
        padding = kwargs.get("padding", 10)
        grid = GridSetup(nrows, ncols, width, height, layout, margin, padding)
        canvas = grid.canvas
        axes = grid.axes

        # default style
        if "tip_labels_style" in kwargs:
            if "-toyplot-anchor-shift" not in kwargs["tip_labels_style"]:
                kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "10px"
            if "font-size" not in kwargs["tip_labels_style"]:
                kwargs["font-size"] = "10px"
        else:
            kwargs["tip_labels_style"] = {
                "-toyplot-anchor-shift": "10px",
                "font-size": "10px",
            }

        # add toytree-Grid mark to the axes
        marks = []
        tmpargs = kwargs.copy()

        # get max tree height for shared_axes top
        ymax = max(abs(i.treenode.height) for i in treelist)

        # add ToyTree marks
        for idx in range(grid.nrows * grid.ncols):

            # get the axis
            axes = grid.axes[idx]

            # add the mark
            _, _, mark = treelist[idx].draw(axes=axes, **tmpargs)

            # store the mark
            marks.append(mark)

        # mod style axes
        for idx in range(grid.nrows * grid.ncols):

            if shared_axes:
                # grid.axes[idx].y.domain.max = ymax
                mark.width = canvas.width / ncols
                mark.height = canvas.height / nrows
                mark.scale_bar = kwargs.get("scale_bar", False)
                style_ticks(ymax, grid.axes[idx], mark, only_inside=True)

                # add an invisible spacer point. This does a much
                # better job than setting ticks alone.
                if mark.layout == 'd':
                    grid.axes[idx].scatterplot(
                        mark.xbaseline + treelist[idx].ntips / 2,
                        mark.ybaseline + ymax,
                        color="transparent",
                    )
                elif mark.layout == 'u':
                    grid.axes[idx].scatterplot(
                        mark.xbaseline + treelist[idx].ntips / 2,
                        mark.ybaseline - ymax,
                        color="transparent",
                    )
                elif mark.layout == 'l':
                    grid.axes[idx].scatterplot(
                        mark.xbaseline + ymax,
                        mark.ybaseline + treelist[idx].ntips / 2,
                        color="transparent",
                    )
                elif mark.layout == 'r':
                    grid.axes[idx].scatterplot(
                        mark.xbaseline - ymax,
                        mark.ybaseline + treelist[idx].ntips / 2,
                        color="transparent",
                    )

            # axes off if not scale_bar
            if kwargs.get("scale_bar", False) is False:
                if mark.layout in 'du':
                    grid.axes[idx].y.show = False
                    grid.axes[idx].x.show = False
                else:
                    grid.axes[idx].y.show = False
                    grid.axes[idx].x.show = False

        # add mark to axes
        return canvas, grid.axes, marks


    def draw_cloud_tree(
        self,
        axes: 'toyplot.coordinates.Cartesian'=None,
        fixed_order: Iterable[str]=None,
        jitter: float=0.0,
        **kwargs,
        ):
        """
        Draw multiple trees overlapping in coordinate space. The
        order of tip_labels is fixed in cloud trees so that trees
        with discordant relationships can be seen in conflict.

        Parameters:
        -----------
        axes: (None or toyplot.coordinates.Cartesian)
            If None then a new Canvas and Cartesian axes object is
            returned, otherwise if a Cartesian axes object is provided
            the cloudtree will be drawn on the axes.

        fixed_order: Iterable[str]
            A list of tip names matching those in every tree in the
            multitree, the order of which will determine the fixed
            order of tips in plotted trees. If None (default) then a
            consensus tree is inferred and its ladderized tip order
            is used.

        jitter: float
            A value by which to randomly shift the baseline of tree
            subplots so that they do not overlap perfectly. This adds
            a value drawn from np.random.uniform(-jitter, jitter).

        **kwargs:
            All drawing style arguments supported in the .draw()
            function of toytree objects are also supported by
            .draw_cloudtree(), most notably here, edge_style.

        Note:
        -----
        For style arguments that apply to tips (e.g., tip_labels) the
        styles will be re-ordered by fixed_order to apply to all trees
        correctly.

        a series of nodes
        (e.g., node_colors or tip_labels) the values will be applied
        to

        """
        # TreeStyle used for canvas, axes setup only, based on
        # kwargs, not .style from any subtrees.
        fstyle = TreeStyle()
        fstyle.width = kwargs.get("width", None)
        fstyle.height = kwargs.get("height", None)
        fstyle.tip_labels = self.treelist[0].get_tip_labels()
        fstyle.layout = kwargs.get("layout", 'r')
        fstyle.padding = kwargs.get("padding", 20)
        fstyle.scale_bar = kwargs.get("scale_bar", False)
        fstyle.use_edge_lengths = kwargs.get("use_edge_lengths", True)
        fstyle.xbaseline = kwargs.get("xbaseline", 0)
        fstyle.ybaseline = kwargs.get("ybaseline", 0)

        # get canvas and axes
        setup = CanvasSetup(self, axes, fstyle)
        canvas = setup.canvas
        axes = setup.axes

        # fix order treelist
        if fixed_order is None:
            fixed_order = (
                MultiTree(self.treelist)
                .get_consensus_tree()
                .get_tip_labels()
            )
        assert len(fixed_order) == len(self.treelist[0]), (
            f"fixed_order arg must be the same length as ntips. You entered {fixed_order}")

        # add trees
        marks = []
        for tidx, tree in enumerate(self.treelist):

            # add jitter to tip coordinates
            if jitter:
                if fstyle.layout in ['r', 'l']:
                    kwargs['ybaseline'] = tree.style.ybaseline + np.random.uniform(-jitter, jitter)
                else:
                    kwargs['xbaseline'] = tree.style.xbaseline + np.random.uniform(-jitter, jitter)

            # set the edge stroke-opacity
            if not kwargs.get('edge_style'):
                kwargs['edge_style'] = {"stroke-opacity": 1 / len(self.treelist)}
            else:
                if not kwargs['edge_style'].get('stroke-opacity'):
                    kwargs['edge_style']['stroke-opacity'] = 1 / len(self.treelist)

            # set the edge type to 'c' because the other two look bad
            if 'edge_type' not in kwargs:
                kwargs['edge_type'] = 'c'

            # pass kwargs with tree and its style to draw_toytree
            if not tidx:
                # reorder tip labels entered into fixed order
                if not kwargs.get("tip_labels"):
                    kwargs['tip_labels'] = fixed_order
            else:
                kwargs['tip_labels'] = False

            # add mark to axes
            _, _, mark = tree.draw(axes=axes, fixed_order=fixed_order, **kwargs)
            marks.append(mark)

        # get shared tree styles.
        return canvas, axes, marks




TIP_LABELS_ADVICE = """
Warning: ignoring 'tip_labels' argument.

The 'tip_labels' arg to draw_cloud_tree() should be a dictionary
mapping tip names from the contained ToyTrees to a new string value.
Example: {"a": "tip-A", "b": "tip-B", "c": tip-C"}

# get a MultiTree containing 10 trees with numbered tip names
trees = toytree.mtree([toytree.rtree.imbtree(5) for i in range(10)])

# draw a cloud tree using a set tip order and styled tip names
trees.draw_cloud_tree(
    fixed_order=['0', '1', '2', '3', '4'],
    tip_labels={i: "tip-{}".format(i) for i in trees.treelist[0].get_tip_labels()},
    )
"""
