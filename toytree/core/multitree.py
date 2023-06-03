#!/usr/bin/env python

"""MultiTree classes for representing a collection of trees.

A MultiTree class is used to store a collection of trees, and includes
functions for visualizing and manipulating multiple trees.

Methods
-------
- get_consensus_tree
    Return a consensus tree from a set of input trees.
- draw
    Return a toyplot drawing of multiple trees spaced on a grid.
- draw_cloud_tree
    Return a toyplot drawing of multiple trees overlaid.

See Also
--------
- toytree.utils.ToyTreeSequence
    A wrapper around the tskit TreeSequence class. This class has
    convenience functions for extracting and plotting trees from a
    TreeSequence object. To use it requires that you install the
    additional library tskit. By contrast the MultiTree class is a
    much simpler collection of trees, and does not require any third
    party packages, and is thus the default object in toytree for
    working with multiple trees.

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

from __future__ import annotations
from typing import Union, List, Sequence, Optional, Tuple, TypeVar, Iterator
from copy import deepcopy
import numpy as np
# import pandas as pd
from loguru import logger
from toytree.core.tree import ToyTree
from toytree.core.tree import Node
from toytree.style import TreeStyle, get_base_tree_style_by_name
from toytree.drawing.src.setup_canvas import get_canvas_and_axes
from toytree.drawing.src.setup_grid import Grid
# from toytree.drawing import CanvasSetup, GridSetup, set_axes_ticks_style
# from toytree.core.drawing.render import ToytreeMark
from toytree.infer.src.consensus import ConsensusTree
# from toytree.utils import ToytreeError

# aliases of Toyplot types returned by draw functions
Canvas = TypeVar("Canvas")
Cartesian = TypeVar("Cartesian")
Mark = TypeVar("Mark")
Query = TypeVar("Query", str, int, Node)
logger = logger.bind(name="toytree")


class MultiTree:
    """MultiTree class to visualize and analyze collections of trees.

    MultiTree objects can be indexed to extract ToyTrees, and are also
    iterable. They include functions for visualizing sets of trees, and
    for comparing and calculating statistics on sets of trees.

    Notes
    -----
    Use factory function `toytree.mtree` to init a MultiTree instance
    from a list of ToyTrees, or from a newick or nexus trees file.

    Examples
    --------
    >>> trees = [toytree.rtree.unittree(10) for i in range(100)]
    >>> mtree = toytree.mtree(trees)
    >>> mtree.draw();
    """
    def __init__(self, treelist: List[ToyTree]):
        self.treelist: List[ToyTree] = treelist
        """List of ToyTree objects in the MultiTree."""

        # self.data: pd.DataFrame = self._init_data(treelist, data)
        # """DataFrame with tree metadata (e.g., ipcoal.Model.df)."""

    # def _init_data(self, treelist, data: Optional[pd.DataFrame]):
    #     if data is None:
    #         data = pd.DataFrame(
    #             index=range(len(self)),
    #             data={"count": 1},
    #         )
    #     return data

    def __len__(self):
        """Return number of trees in the treelist"""
        return len(self.treelist)

    def __iter__(self) -> Iterator[ToyTree]:
        """Generator to yield ToyTrees from MultiTree.treelist."""
        for tree in self.treelist:
            yield tree

    def __getitem__(self, idx: int) -> ToyTree:
        """Return ToyTree by indexing from MultiTree.treelist."""
        return self.treelist[idx]

    def __repr__(self):
        """string representation shows ntrees and type"""
        return f"<toytree.MultiTree ntrees={len(self)}>"

    @property
    def ntips(self):
        """Return number of tips in the FIRST tree in treelist."""
        return self.treelist[0].ntips

    @property
    def ntrees(self):
        """Return number of trees in the MultiTree.treelist"""
        return len(self.treelist)

    def all_tree_tip_labels_same(self) -> bool:
        """Return True if names are the same in all the trees."""
        first = set(self.treelist[0].get_tip_labels())
        return all(set(i.get_tip_labels()) == first for i in self)

    def all_tree_topologies_same(self, include_root: bool = False) -> bool:
        """Return True if all topologies in treelist are identical."""
        return len(set(i.get_topology_id(include_root=include_root) for i in self)) == 1

    # def iter_unique_topologies(self, include_root: bool = False) -> Iterator[ToyTree]:
    #     """Generator to yield unique tree topologies in treelist."""
    #     counter = Counter()
    #     for tree in self:
    #         hashed = tree.get_topology_id(include_root=include_root)
    #         counter[hashed] += 1
    #     return counter

    # better name?
    def get_unique_topologies(self, include_root: bool = False) -> List[Tuple[ToyTree, int]]:
        """Return a list of (ToyTree, count) for each unique tree.

        This can be useful for calculating statistics only on the
        unique set of trees and multiplying by their frequency (for
        example this is done when generating consensus trees).

        Parameters
        ----------
        include_root:
            If False then all unique rooted trees are counted and
            returned rather than all unique unrooted trees.

        Examples
        --------
        >>> mtree = toytree.mtree(
        >>>     [toytree.rtree.rtree(6) for i in range(100)])
        >>> print(mtree.get_unique_topology_counts())
        >>> # [(ToyTree, 10), (ToyTree, 9), (ToyTree, 9), ...]
        """
        trees_dict = {}
        for tree in self:
            hashed = tree.get_topology_id(include_root=include_root)
            if hashed in trees_dict:
                trees_dict[hashed][1] += 1
            else:
                trees_dict[hashed] = [tree, 1]
        # sort trees and return as a List of Tuples
        return sorted(trees_dict.values(), key=lambda x: x[1], reverse=True)

    def copy(self):
        """Return a deepcopy of the MultiTree."""
        return deepcopy(self)

    # todo: use wrap
    def write(
        self,
        path: Optional[str] = None,
        dist_formatter: str = "%.12g",
        internal_labels: Optional[str] = "support",
        internal_labels_formatter: Optional[str] = "%.12g",
        features: Optional[Sequence[str]] = None,
        features_prefix: str = "&",
        features_delim: str = ",",
        features_assignment: str = "=",
        **kwargs,
    ) -> Optional[str]:
        """Write tree to newick string and return or write to filepath.

        The newick string can be formatted in several ways. The default
        will include dist values (edge lengths) and support values as
        internal node labels. The edge lengths can be suppressed by
        setting `dist_formatter=None`, and internal node labels can be
        similarly suppressed, or set to store a different feature, such
        as internal node names. Additional features can be stored in the
        node comment blocks in extended-newick-format (NHX-like) by using
        the "features" arguments (see examples).

        Parameters
        ----------
        tree: ToyTree
            A ToyTree instance to write as a newick string.
        path: str or None
            A filepath to write to file, or None to return newick string.
        dist_formatter: str or None
            A formatting string to format float dist values (edge lengths),
            or None to not write dist values. Default is "%.6g".
        internal_labels: str or None
            A feature to write as internal node labels. None suppresses
            internal labels. The 'support' feature is default, and
            often used here, but 'name' or any other feature can be
            used as well.
        internal_labels_formatter: str or None
            A formatting string to format internal labels. If an internal
            label cannot be formatted due to TypeError (e.g., you select
            'name' for `internal_labels` but leave this optional at its
            default as a float formatter '%.6g', instead of str formatter)
            it will simply be converted to a string.
        features: List[str]
            A list of additional features to write in the newick comment
            block. For example, features=["height"] will save heights.
        features_prefix: str
            A prefix character written to the start of newick comment
            blocks. Typical values are "&" (default) or "&&NHX:".
        features_delim: str
            A character used to delimit features in the newick comment
            block. Default is ",".
        features_assignment: str
            A character used to separate feature keys and values. Default
            is "=".

        See Also
        --------
        `write_nexus`
            Write tree newick string in a NEXUS format.
        `ToyTree.write`
            This function is available from ToyTree objects as `.write`.
        """
        if kwargs:
            logger.warning(
                f"Deprecated args to write(): {list(kwargs.values())}. See docs.")
        newicks = []
        for tree in self:
            newicks.append(tree.write(
                path=None, dist_formatter=dist_formatter,
                internal_labels=internal_labels,
                internal_labels_formatter=internal_labels_formatter,
                features=features,
                features_prefix=features_prefix,
                features_delim=features_delim,
                features_assignment=features_assignment,
            ))
        newicks = "\n".join(newicks)
        if path is None:
            return newicks
        with open(path, 'w', encoding="utf-8") as out:
            out.write(newicks)
        return None

    def get_consensus_tree(
        self,
        best_tree: ToyTree = None,
        majority_rule_min: float = 0.0,
    ) -> ToyTree:
        """Return an extended majority rule consensus Toytree.

        Consensus tree Node 'support' features record the frequency of
        occurrence of clades across the input MultiTree treelist.
        Clades with support below 'majority_rule_min' are collapsed
        into polytomies. If you enter an optional 'best_tree' then
        support values from the input trees will be calculated for
        clades in this tree, and the 'best_tree' is returned with
        support values added to Nodes, else a majority-rule consensus
        tree is generated and returned. The mean, min, and max of
        additional features in the trees can also be calculated.

        Parameters
        ----------
        best_tree: Toytree, str, or None
            A tree that support values should be calculated for and
            added to. For example, you want to calculate how often
            clades in your best ML tree are supported in 100 bootstrap
            trees.
        majority_rule_min: float
            Cut-off below which clades are collapsed in the majority
            rule consensus tree. This is a proportion (e.g., 0.5 means
            50%).

        Examples
        --------
        >>> best = toytree.rtree.unittree(ntips=10, seed=123)
        >>> trees = [toytree.rtree.unittree(ntips=10) for i in range(10)]
        >>> mtree = toytree.mtree(trees)
        >>> ctree1 = mtree.get_consensus_tree(trees, best_tree=best)
        >>> ctree2 = mtree.get_consensus_tree(trees)
        >>> ctree3 = mtree.get_consensus_tree(trees, majority_rule_min=0.5)
        >>> toytree.mtree([ctree1, ctree2, ctree3]).draw();
        """
        cons = ConsensusTree(
            mtree=self,
            best_tree=best_tree,
            majority_rule_min=majority_rule_min,
        )
        return cons.run()

    ################################################################
    # Tree Modification functions
    # These visit and possibly modify every tree in treelist
    ################################################################

    def root(
        self,
        *query: Query,
        root_dist: Optional[float] = None,
        edge_features: Optional[Sequence[str]] = None,
        inplace: bool = False,
    ) -> MultiTree:
        """Return a MultiTree with all ToyTrees in treelist rooted.

        If a tree cannot be rooted on the selected position this
        will raise a ToytreeError.

        Parameters
        ----------
        *query: str, int, or Node
            One or more Node selectors, which can be Node objects, names,
            or int idx labels. If multiple are entered the MRCA node will
            be used as the base of the edge to split.
        regex: bool
            If True then Node name strings are treated as regular
            expressions that can match to multiple Nodes.
        root_dist: None or float
            The length (dist) along the root edge above the Node query
            where the new root edge should be placed. Default is None
            which will place root at the midpoint of the edge. A float
            can be entered, but will raise ToyTreeError if > len of edge.
        edge_features: Sequence[str]
            One or more Node features that should be treated as a feature
            of its edge, not the Node itself. On rooting, edge features
            are re-polarized, to apply to the correct Node. The 'dist'
            and 'support' features are always treated as edge features.
            Add additional edge features here. See docs for example.
        inplace: bool
            If True the original tree is modified and returned, otherwise
            a modified copy is returned.
        """
        mtree = self if inplace else self.copy()
        for tree in mtree:
            tree.root(
                *query,
                root_dist=root_dist,
                edge_features=edge_features,
                inplace=True,
            )
        return mtree

    def unroot(self, inplace: bool = False) -> MultiTree:
        """Return a MultiTree with all ToyTrees in treelist unrooted"""
        mtree = self if inplace else self.copy()
        for tree in mtree:
            tree.unroot(inplace=True)
        return mtree

    ################################################################
    # Tree Comparison/Distance functions
    # >>> toytree.distance.get_treedist_rf(mtre[0], mtre[1])
    # >>> toytree.distance.get_treedist_matrix(*mtre.treelist)
    ################################################################

    # def get_tree_distance(self, idx0: int, idx1: int, metric: str = "rf") -> float:
    #     """Return a distance metric comparing two trees.

    #     Trees are indexed from the treelist by indices idx0 and idx1.

    #     Parameters
    #     ----------
    #     idx0: int
    #         Index of a tree from the treelist.
    #     idx1: int
    #         Index of a tree from the treelist.
    #     metric: str
    #         Name of a supported tree distance metric. For available
    #         options see `toytree.distance.treedist`.
    #     **kwargs: Dict
    #         Additional options accepted by tree distance method.

    #     Examples
    #     --------
    #     >>> ...
    #     """
    #     return get_tree_distance(
    #         self[idx0], self[idx1], metric=metric, **kwargs)

    # def get_tree_distance_matrix(self, ) -> float:
    #     """TODO..."""

    # def get_tree_distance_distribution(
    #     self, ) -> np.ndarray:
    #     """Return a distribution of tree distances.

    #     Tree distances are measure between pairs of trees, but several
    #     options are available for how pairs will be sampled, including
    #     'random', 'consensus', or 'distance'.

    #     Parameters
    #     ----------

    #     Returns
    #     -------
    #     pd.DataFrame?

    #     Examples
    #     --------
    #     >>> ...
    #     """

    ################################################################
    # Drawing functions
    #
    ################################################################

    def draw(
        self,
        shape: Tuple[int, int] = (1, 4),
        shared_axes: bool = False,
        idxs: Optional[Sequence[int]] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        margin: Union[float, Tuple[int, int, int, int]] = None,
        **kwargs,
    ) -> Tuple[Canvas, Cartesian, List[Mark]]:
        """Return a toyplot drawing of a grid of ToyTrees.

        The grid spacing can be controlled with shape and margin
        options, and trees can each be on their own axis or on a
        set of shared axes (same max height dimension), which can be
        better for highlighting differences in heights.

        Parameters
        ----------
        shape: Tuple[int,int]
            A tuple of (nrows, ncolumns) for a tree grid drawing. The
            dimension of this matrix determines the number of trees
            that will be plotted.
        shared_axes (bool):
            If True then the 'height' dimension will be shared among
            all trees, otherwise each tree is scaled to fill the
            space in its grid cell.
        idxs (int):
            The indices of trees in treelist that you want to draw. By
            default the first ncols*nrows trees are drawn, but you can
            select the 10-14th tree by entering idxs=[10,11,12,13].
            The selected trees will be displayed in the grid.
        width (int):
            Width of the canvas
        height (int):
            Height of the canvas
        margin: Tuple[int,int,int,int]
            Spacing between subplots in the grid in pixel units. A
            single value or a tuple for top, right, bottom, left.
        **kwargs (dict):
            Any style arguments supported by .draw() in toytrees.

        Examples
        --------
        >>> mtre = toytree.mtree([toytree.rtree.unittree(10) for i in range(10)])
        >>> mtre.draw(shape=(2, 3), width=800, edge_widths=4)
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
            tidx = [idxs] if isinstance(idxs, int) else list(idxs)

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
            layout = get_base_tree_style_by_name(kwargs.get("ts")).layout
        elif "tree_style" in kwargs:
            layout = get_base_tree_style_by_name(kwargs.get("ts")).layout
        else:
            layout = kwargs.get("layout", 'r')

        # get the canvas and axes that can fit the requested trees.
        padding = kwargs.get("padding", 10)
        scale_bar = kwargs.get("scale_bar", False)
        grid = Grid(nrows, ncols, width, height, layout, margin, padding, scale_bar)
        # GridSetup(nrows, ncols, width, height, layout, margin, padding, scale_bar)
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
                set_axes_ticks_style(ymax, grid.axes[idx], mark, only_inside=True)

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
        axes: Cartesian = None,
        fixed_order: Sequence[str] = None,
        jitter: float = 0.0,
        **kwargs,
    ):
        """
        Draw multiple trees overlapping in coordinate space. The
        order of tip_labels is fixed in cloud trees so that trees
        with discordant relationships can be seen in conflict.

        Parameters
        ----------
        axes: (None or toyplot.coordinates.Cartesian)
            If None then a new Canvas and Cartesian axes object is
            returned, otherwise if a Cartesian axes object is provided
            the cloudtree will be drawn on the axes.
        fixed_order: Sequence[str]
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

        Notes
        -----
        For style arguments that apply to tips (e.g., tip_labels) the
        styles will be re-ordered by fixed_order to apply to all trees
        correctly.
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
        setup = get_canvas_and_axes(self, axes, fstyle)
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

            # plot tip labels by reordering those of tree tidx=0
            if not tidx:
                if not kwargs.get("tip_labels"):
                    kwargs['tip_labels'] = fixed_order
                else:
                    first_tree_tips = tree.get_tip_labels()
                    odx = [fixed_order.index(i) for i in first_tree_tips]
                    kwargs['tip_labels'] = [first_tree_tips[i] for i in odx]
            else:
                kwargs['tip_labels'] = False

            # add mark to axes
            _, _, mark = tree.draw(axes=axes, fixed_order=fixed_order, **kwargs)
            marks.append(mark)

        # get shared tree styles.
        return canvas, axes, marks

    # def draw_tree_sequence(self, ):
    #     """
    #     Return a tree sequence drawing
    #     """
    #     return TreeSequenceDrawing(kwargs)

    def reset_tree_styles(self):
        """Set the .style to default for all ToyTrees in treelist."""
        for tre in self.treelist:
            tre.style = TreeStyle()

    def get_tip_labels(self) -> Sequence[str]:
        """Return ordered tip labels from the first tree in treelist.

        Because a MultiTree contains many trees there are many possible
        orderings of the tip Node labels. For the purposes of plotting,
        it is sometimes desirable to fetch the tip names before plotting
        so that they can be modified, and then supplied as an argument
        to a plotting function, such as `draw_cloud_tree`.

        tree plot order for the *list of tree*, ...
        starting from the zero axis. If all trees in the treelist do not
        share the same set of tips then this will return an error message.

        If fixed_order is a user entered list then names are returned in that
        order. If fixed_order was True then the consensus tree order is
        returned. If fixed_order was None or False then the order of the first
        ToyTree in .treelist is returned.
        """
        if not self.all_tree_tip_labels_same():
            raise Exception(
                "All trees in treelist do not share the same set of tips")
        return self.treelist[0].get_tip_labels()


if __name__ == "__main__":

    import toytree
    mtree = toytree.mtree([toytree.rtree.unittree(10) for i in range(10)])
    print(mtree)
    # c, a, m = mtree.draw(ts='c', shape=(2, 3))
    # toytree.utils.show(c)
    for tree in mtree:
        print(repr(tree))
    print(mtree.get_unique_topologies())