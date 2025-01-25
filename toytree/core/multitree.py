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
    - set-like function that drops tips from each tree not shared by all trees.
    - root function that drops tree that cannot be rooted or not set-like
    - consensus function drop tips that are not in set.
    - A distinct multitree mark for combining styles on topologies
    - New mark: leave proper space for tips to mtree fits same as tree.
"""

from __future__ import annotations
from typing import Union, List, Sequence, Optional, Tuple, TypeVar, Iterator
from copy import deepcopy
import numpy as np
# import pandas as pd
from loguru import logger
from toytree.utils import ToytreeError
from toytree.core import ToyTree, Node
from toytree.style import TreeStyle, get_base_tree_style_by_name, tree_style_to_css_dict
from toytree.drawing.src.setup_canvas import get_canvas_and_axes
from toytree.drawing.src.setup_grid import Grid
from toytree.drawing.src.draw_cloudtree import draw_cloudtree
from toytree.drawing.src.draw_multitree import draw_multitree
from toytree.annotate import add_axes_scale_bar
# from toytree.core.drawing.render import ToytreeMark
import toytree.infer

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

    def all_tree_tips_aligned(self, rtol: float = 1e-5, atol: float = 1e-5) -> bool:
        """Return True if all tree tips are aligned (i.e., ultrametric)

        This checks that all tip Node heights align at 0 within the
        accepted tolerance level.

        Parameters
        ----------
        rtol: float
            See np.allclose() function docstring.
        atol: float
            See np.allclose() function docstring.
        """
        return np.allclose(
            a=np.concatenate([[i.height for i in tree] for tree in self]),
            b=0,
            rtol=rtol,
            atol=atol,
        )

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
            logger.warning(f"Deprecated args to write(): {list(kwargs.values())}. See docs.")
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

    # ---------------------------------------------------------------#
    # see toytree.infer.get_consensus_tree()
    # ---------------------------------------------------------------#
    def get_consensus_tree(self, min_freq: float = 0.0, **kwargs) -> ToyTree:
        """Return an exteded majority-rule consensus tree from a list of trees.

        The trees must contain the same set of tips. The returned tree will
        contain the most frequently occurring non-conflicting clades in the
        input trees. If the most frequent clades conflict with equal
        frequency the node is collapsed. A minimum clade frequency can
        be set to only include clades occurring above that threshold. For
        example, min_freq=0.5 will procude a 50% majority-rule consensus
        tree. The returned tree is unrooted with edge dist values as the
        mean dist across all occurrences of that split in the set of trees.

        Parameters
        ----------
        trees: MultiTree | list[ToyTree]
            A MultiTree or list of ToyTrees sharing the same tip labels.
        min_freq: float
            A minimum frequency cutoff for a split to occur across the set
            of trees for it to be included in the consensus tree.

        See Also
        --------
        map_features_to_consensus_tree
            Map dists, heights, or other features from a set of input trees
            to nodes of a consensus tree with additional options.

        Examples
        --------
        >>> trees = [toytree.rtree.unittree(ntips=10) for i in range(10)]
        >>> mtree = toytree.mtree(trees)
        >>> ctree1 = mtree.get_consensus_tree(trees)
        >>> ctree2 = mtree.get_consensus_tree(trees, majority_rule_min=0.5)
        >>> toytree.mtree([ctree1, ctree2]).draw();
        """
        if kwargs:
            logger.warning(f"Deprecated args to get_consensus_tree(): {list(kwargs.values())}. See docs.")
        return toytree.infer.get_consensus_tree(self.treelist, min_freq=min_freq)


    def get_consensus_features(self, tree: ToyTree, features: list[str] = None, ultrametric: bool = False, conditional: bool = True) -> ToyTree:
        """Return tree with feature data mapped to each bipartition from
        a set of trees that may or may not share the same bipartitions.

        The 'support' value on the consensus tree represents the proportion
        of trees that supported the split in the consensus, and the 'dist'
        is the mean dist value of the bipartition edge in the set of trees
        that included that edge. These two features are set on MJ rule
        consensus trees by default. Other features can be optionally
        computed as well.

        Parameters
        ----------
        tree: ToyTree
            The tree can be the MJ consensus tree or a user input tree.
        trees: MultiTree | list[ToyTree]
            A list of trees from which features will be extracted. Support
            is always measured. Edge lengths are extracted as 'dists' or
            'heights' depending on the option 'rooted'.
        features: None | list[str]
            A list of feature names that exist on the input trees that you
            wish to have summarized across the nodes of the consensus tree.
            For quantitative features this will record min, max, mean, std
            conditional on the existence of the node in the tree.
        rooted: bool
            If trees are rooted and ultrametric then set this option to
            True to summarize stats of node heights instead of node dists.
            Note: this forces conditional=True.
        conditional: bool
            If True then dist values of tip nodes on unrooted trees are
            only calculated from the subset of trees where these tips occur
            in the same splits as in the main tree, otherwise dists are
            calculated from tip nodes across all input trees. This only
            affects tip node dists.

        See Also
        --------
        ...

        Examples
        --------
        ...
        """
        return toytree.infer.get_consensus_features(
            tree=tree, trees=self.treelist,
            features=features, ultrametric=ultrametric, conditional=True)


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

    # TODO: write grid draw code in separate module
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
        return draw_multitree(
            mtree=self, shape=shape, shared_axes=shared_axes, idxs=idxs,
            width=width, height=height, margin=margin, **kwargs,
        )


    # def draw_cloud_tree(
    #     self,
    #     axes: Cartesian = None,
    #     fixed_order: Sequence[str] = None,
    #     jitter: float = 0.0,
    #     idxs: Optional[Sequence[int]] = None,
    #     **kwargs,
    # ):
    #     """Return a cloud of overlapping low-opacity tree drawings.

    #     Draw multiple trees overlapping in coordinate space. The
    #     order of tip_labels is fixed in cloud trees so that trees
    #     with discordant relationships can be seen in conflict. See
    #     examples from the documentation for tips on using additional
    #     styling options to further visualize patterns among subtrees
    #     within the cloud.

    #     Parameters
    #     ----------
    #     axes: None or toyplot.coordinates.Cartesian
    #         If None then a new Canvas and Cartesian axes object is
    #         returned, otherwise if a Cartesian axes object is provided
    #         the cloudtree will be drawn on the axes.
    #     fixed_order: Sequence[str], bool, or None
    #         A list of tip names matching those in every tree in the
    #         multitree, the order of which will determine the fixed
    #         order of tips in plotted trees. If None (default) then a
    #         consensus tree is inferred and its ladderized tip order
    #         is used.
    #     jitter: float
    #         A value by which to randomly shift the baseline of tree
    #         subplots so that they do not overlap perfectly. This adds
    #         a value drawn from np.random.uniform(-jitter, jitter).
    #     idxs: None or Sequence[int]
    #         Optional select indices of which trees to draw.
    #     **kwargs:
    #         All drawing style arguments supported in the .draw()
    #         function of toytree objects are also supported by
    #         .draw_cloudtree(), most notably here, edge_style.

    #     Notes
    #     -----
    #     For style arguments that apply to tips (e.g., tip_labels) the
    #     styles will be re-ordered by fixed_order to apply to all trees
    #     correctly.
    #     """
    #     logger.warning(("kwargs", kwargs))
    #     # which trees to draw
    #     treelist = self.treelist if idxs is None else idxs

    #     # TreeStyle used for canvas, axes setup only, based on
    #     # kwargs, not .style from any subtrees.
    #     fstyle = TreeStyle()
    #     fstyle.width = kwargs.get("width", None)
    #     fstyle.height = kwargs.get("height", None)
    #     fstyle.layout = kwargs.get("layout", 'r')
    #     fstyle.padding = kwargs.get("padding", 20)
    #     fstyle.scale_bar = kwargs.get("scale_bar", False)
    #     fstyle.use_edge_lengths = kwargs.get("use_edge_lengths", True)
    #     fstyle.edge_type = kwargs.get("edge_type", 'c')
    #     fstyle.xbaseline = kwargs.get("xbaseline", 0)
    #     fstyle.ybaseline = kwargs.get("ybaseline", 0)
    #     fstyle.tip_labels = (
    #         self.treelist[0].get_tip_labels() if "tip_labels" not in kwargs
    #         else kwargs["tip_labels"]
    #     )
    #     logger.warning(("fstyle.tip_labels", fstyle.tip_labels))
    #     fstyle.edge_style.stroke_opacity = 1 / len(treelist)
    #     if "edge_style" in kwargs:
    #         for key, val in kwargs["edge_style"]:
    #             setattr(fstyle, key, val)
    #     logger.warning(("fstyle.edge_style", fstyle.edge_style))

    #     # get fixed order of tips from consensus tree if not provided.
    #     if fixed_order is None:
    #         fixed_order = (
    #             MultiTree(self.treelist)
    #             .get_consensus_tree()
    #             .get_tip_labels()
    #         )
    #     logger.warning(("fixed_order", fixed_order))

    #     # require fixed_order to match ntips
    #     ntips = self.treelist[0].ntips
    #     assert len(fixed_order) == ntips, (
    #         f"fixed_order arg (len={len(fixed_order)}) "
    #         f"must be the same length as ntips (len={ntips}). "
    #         f"You entered: {fixed_order}")

    #     # draw trees sequentially to get a list of ToyTreeMark objects
    #     marks = []
    #     for tidx, tree in enumerate(treelist):

    #         # make copy of fstyle
    #         tmpstyle = fstyle.copy()

    #         # add jitter to tip coordinates
    #         if jitter:
    #             if fstyle.layout in "rl":
    #                 tmpstyle.ybaseline = fstyle.ybaseline + np.random.uniform(-jitter, jitter)
    #             else:
    #                 tmpstyle.xbaseline = fstyle.xbaseline + np.random.uniform(-jitter, jitter)

    #         # set the edge stroke-opacity
    #         if tree.style.edge_style.stroke_opacity is not None:
    #             tmpstyle.edge_style.stroke_opacity

    #         # plot tip labels by reordering those of tree tidx=0
    #         if not tidx:
    #             tmpstyle.tip_labels = fstyle.tip_labels
    #         else:
    #             tmpstyle.tip_labels = False

    #         # add mark to axes
    #         kwargs = tree_style_to_css_dict(tmpstyle)
    #         logger.warning(("kwargs", kwargs))
    #         if not tidx:
    #             canvas, axes, mark = tree.draw(axes=axes, fixed_order=fixed_order, **kwargs)
    #         else:
    #             _, _, mark = tree.draw(axes=axes, fixed_order=fixed_order, **kwargs)
    #         marks.append(mark)

    #     # get shared tree styles.
    #     return canvas, axes, marks


    def draw_cloud_tree(
        self,
        axes: Cartesian = None,
        fixed_order: Union[Sequence[str], bool] = None,
        jitter: float = 0.0,
        idxs: Optional[Sequence[int]] = None,
        interior_algorithm: int = 1,
        **kwargs,
    ):
        """...
        """
        kwargs["jitter"] = jitter
        kwargs["axes"] = axes
        kwargs["idxs"] = idxs
        kwargs["tree_style"] = None
        kwargs["fixed_order"] = fixed_order
        kwargs["interior_algorithm"] = interior_algorithm
        kwargs["kwargs"] = {}
        marks = draw_cloudtree(self, **kwargs)

        # get or create axes and canvas
        canvas, axes = get_canvas_and_axes(
            axes, marks[0],
            kwargs.get("width"), kwargs.get("height"),
        )

        # add marks to axes
        for mark in marks:
            axes.add_mark(mark)

        # style axes
        # scale bar was not allowed on individual trees. Add scale
        # bar for the tallest tree in the bunch
        if kwargs.get("scale_bar", False):
            tree = max(self, key=lambda x: x.treenode.height)
            tree.annotate.add_axes_scale_bar(axes, ymax=tree.treenode.height)
        else:
            if canvas is not None:
                axes.x.show = False
                axes.y.show = False

        return canvas, axes, marks


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
            raise ToytreeError(
                "All trees in treelist do not share the same set of tips")
        return self.treelist[0].get_tip_labels()


if __name__ == "__main__":

    import toytree
    mtree = toytree.mtree([toytree.rtree.unittree(10) for i in range(10)])
    # print(mtree)
    # c, a, m = mtree.draw(ts='c', shape=(2, 3))
    # toytree.utils.show(c)
    # for tree in mtree:
    #     print(repr(tree))
    # print(mtree.get_unique_topologies())
    ctree = mtree.get_consensus_tree()
    print(ctree.get_node_data())

    ctree = mtree.get_consensus_features(ctree)
    print(ctree.get_node_data())
    # ctree._draw_browser(node_sizes=16, node_markers="r1.5x1", node_labels="support", tmpdir="~", scale_bar=True, ts='u')

    # c, a, m = mtree.draw_cloud_tree()
    # toytree.utils.show(c)
    # mtree[1][-1].children[0]._dist = 100
    # mtree[1]._update()
    # c, a, m = mtree.draw(scale_bar=True, node_sizes=0, shared_axes=True, layout='d')
    # toytree.utils.show(c, tmpdir="~")
