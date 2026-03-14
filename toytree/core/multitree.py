#!/usr/bin/env python

"""Utilities for working with ordered collections of ToyTree objects."""

from __future__ import annotations

import sys
from collections.abc import Iterator, Sequence
from copy import deepcopy
from numbers import Integral
from typing import TYPE_CHECKING, TypeVar

from toytree.style import TreeStyle
from toytree.utils import ToytreeError

if TYPE_CHECKING:
    from toyplot.canvas import Canvas
    from toyplot.coordinates import Cartesian
    from toyplot.mark import Mark


ToyTree = TypeVar("ToyTree")
Node = TypeVar("Node")
Query = TypeVar("Query", str, int, Node)


def _warn_deprecated_kwargs(name: str, kwargs: dict) -> None:
    """Print a deprecated-kwargs warning for a public method."""
    if kwargs:
        print(
            f"Deprecated args to {name}(): {list(kwargs.values())}. See docs.",
            file=sys.stderr,
        )


def _require_non_empty_treelist(
    treelist: Sequence[ToyTree],
    action: str,
) -> None:
    """Raise a clear error if a method requires at least one tree."""
    if not treelist:
        raise ToytreeError(f"Cannot {action} on an empty MultiTree.")


def _normalize_tree_indices(
    idxs: int | Sequence[int] | None,
    ntrees: int,
    *,
    caller: str,
) -> list[int]:
    """Return validated tree indices for selection-based methods."""
    if idxs is None:
        return list(range(ntrees))

    if isinstance(idxs, Integral) and not isinstance(idxs, bool):
        raw_indices = [int(idxs)]
    else:
        if isinstance(idxs, (str, bytes)):
            raise ToytreeError(f"{caller} idxs must be an int or an iterable of ints.")
        try:
            raw_indices = list(idxs)
        except TypeError as exc:
            raise ToytreeError(
                f"{caller} idxs must be an int or an iterable of ints."
            ) from exc

    if not raw_indices:
        raise ToytreeError(f"{caller} requires at least one selected tree.")

    indices = []
    for raw in raw_indices:
        if isinstance(raw, bool) or not isinstance(raw, Integral):
            raise ToytreeError(f"{caller} idxs must contain only integer values.")
        idx = int(raw)
        if not -ntrees <= idx < ntrees:
            raise ToytreeError(
                f"{caller} idxs contains out-of-range tree index {idx}. "
                f"Valid range is {-ntrees}..{ntrees - 1}."
            )
        indices.append(idx)
    return indices


class MultiTree:
    """Represent an ordered collection of trees.

    MultiTree objects store one or more ToyTree instances and expose
    convenience methods for collection-level drawing, rooting, writing,
    and consensus inference.

    Notes
    -----
    Use :func:`toytree.mtree` to parse supported multitree inputs into a
    MultiTree instance.

    Examples
    --------
    >>> trees = [toytree.rtree.unittree(10) for _ in range(100)]
    >>> mtree = toytree.mtree(trees)
    >>> mtree.draw()
    """

    def __init__(self, treelist: list[ToyTree]):
        self.treelist: list[ToyTree] = treelist
        """Trees stored in the order they were provided."""
        self._draw_fixed_order_cache: dict[tuple, list[str]] = {}
        """Cached inferred tip orders used by repeated ``draw()`` calls."""

    def __len__(self) -> int:
        """Return the number of trees in the collection."""
        return len(self.treelist)

    def __iter__(self) -> Iterator[ToyTree]:
        """Iterate over ToyTree objects in the collection."""
        return iter(self.treelist)

    def __getitem__(self, idx: int | slice) -> ToyTree | list[ToyTree]:
        """Return one tree or a tree slice from the collection."""
        return self.treelist[idx]

    def __repr__(self) -> str:
        """Return a concise representation of the MultiTree."""
        return f"<toytree.MultiTree ntrees={len(self)}>"

    @property
    def ntips(self) -> int:
        """Return the number of tips in the first tree.

        Raises
        ------
        ToytreeError
            If the MultiTree is empty.
        """
        _require_non_empty_treelist(self.treelist, "get ntips")
        return self.treelist[0].ntips

    @property
    def ntrees(self) -> int:
        """Return the number of trees in the collection."""
        return len(self.treelist)

    def all_tree_tip_labels_same(self) -> bool:
        """Return True if every tree shares the same tip-label set.

        Returns
        -------
        bool
            True if all trees contain the same tip labels, regardless of
            order.

        Raises
        ------
        ToytreeError
            If the MultiTree is empty.
        """
        _require_non_empty_treelist(self.treelist, "compare tip labels")
        first = set(self.treelist[0].get_tip_labels())
        return all(set(tree.get_tip_labels()) == first for tree in self.treelist[1:])

    def all_tree_topologies_same(self, include_root: bool = False) -> bool:
        """Return True if every tree has the same topology.

        Parameters
        ----------
        include_root : bool, default=False
            If True, rooted topology identifiers are compared. Otherwise
            trees are compared by unrooted topology.

        Returns
        -------
        bool
            True if every tree has the same topology under the requested
            root handling.

        Raises
        ------
        ToytreeError
            If the MultiTree is empty.
        """
        _require_non_empty_treelist(self.treelist, "compare topologies")
        first = self.treelist[0].get_topology_id(include_root=include_root)
        return all(
            tree.get_topology_id(include_root=include_root) == first
            for tree in self.treelist[1:]
        )

    def all_tree_tips_aligned(self, rtol: float = 1e-5, atol: float = 1e-5) -> bool:
        """Return True if all tree tips are aligned at height zero.

        Parameters
        ----------
        rtol : float, default=1e-5
            Relative tolerance forwarded to :func:`numpy.allclose`.
        atol : float, default=1e-5
            Absolute tolerance forwarded to :func:`numpy.allclose`.

        Returns
        -------
        bool
            True if every tip height across all trees is approximately
            zero within the requested tolerances.

        Raises
        ------
        ToytreeError
            If the MultiTree is empty.
        """
        import numpy as np

        _require_non_empty_treelist(self.treelist, "check tip alignment")
        heights = [node.height for tree in self.treelist for node in tree]
        return bool(np.allclose(heights, 0.0, rtol=rtol, atol=atol))

    def get_unique_topologies(
        self,
        include_root: bool = False,
    ) -> list[tuple[ToyTree, int]]:
        """Return one representative tree and count for each unique topology.

        Parameters
        ----------
        include_root : bool, default=False
            If True, count rooted topologies separately. Otherwise count
            trees by unrooted topology.

        Returns
        -------
        list[tuple[ToyTree, int]]
            Representative tree and occurrence count for each unique
            topology, sorted from most to least frequent. An empty
            MultiTree returns an empty list.

        Examples
        --------
        >>> mtree = toytree.mtree(
        ...     [toytree.rtree.unittree(6, seed=i) for i in range(10)]
        ... )
        >>> mtree.get_unique_topologies()
        """
        trees_dict: dict[object, tuple[ToyTree, int]] = {}
        for tree in self.treelist:
            hashed = tree.get_topology_id(include_root=include_root)
            if hashed in trees_dict:
                first_tree, count = trees_dict[hashed]
                trees_dict[hashed] = (first_tree, count + 1)
            else:
                trees_dict[hashed] = (tree, 1)
        return sorted(trees_dict.values(), key=lambda item: item[1], reverse=True)

    def copy(self) -> MultiTree:
        """Return a deep copy of the MultiTree."""
        return deepcopy(self)

    def write(
        self,
        path: str | None = None,
        dist_formatter: str | None = "%.12g",
        internal_labels: str | None = "support",
        internal_labels_formatter: str | None = "%.12g",
        features: Sequence[str] | None = None,
        features_prefix: str = "&",
        features_delim: str = ",",
        features_assignment: str = "=",
        **kwargs,
    ) -> str | None:
        """Return serialized tree text or write it to a file.

        Parameters
        ----------
        path : str or None, default=None
            Filepath to write the combined tree text. If None, the text is
            returned instead of written.
        dist_formatter : str or None, default="%.12g"
            Format string for edge lengths. Set to None to suppress edge
            lengths in the serialized output.
        internal_labels : str or None, default="support"
            Node feature to write as internal labels. Set to None to
            suppress internal node labels.
        internal_labels_formatter : str or None, default="%.12g"
            Format string applied to internal label values before writing.
        features : Sequence[str] or None, default=None
            Additional node features to write inside comment blocks.
        features_prefix : str, default="&"
            Prefix used at the start of serialized feature comment blocks.
        features_delim : str, default=","
            Delimiter used between serialized feature assignments.
        features_assignment : str, default="="
            Separator used between serialized feature keys and values.
        **kwargs : dict
            Deprecated extra arguments accepted for backward compatibility.
            Any provided values are ignored with a warning to ``stderr``.

        Returns
        -------
        str or None
            Newline-joined serialized tree text if ``path`` is None.
            Otherwise writes to ``path`` and returns None.
        """
        _warn_deprecated_kwargs("write", kwargs)
        newicks = [
            tree.write(
                path=None,
                dist_formatter=dist_formatter,
                internal_labels=internal_labels,
                internal_labels_formatter=internal_labels_formatter,
                features=features,
                features_prefix=features_prefix,
                features_delim=features_delim,
                features_assignment=features_assignment,
            )
            for tree in self.treelist
        ]
        text = "\n".join(newicks)
        if path is None:
            return text
        with open(path, "w", encoding="utf-8") as out:
            out.write(text)
        return None

    def get_consensus_tree(self, min_freq: float = 0.0, **kwargs) -> ToyTree:
        """Return the consensus tree inferred from the collection.

        Parameters
        ----------
        min_freq : float, default=0.0
            Minimum split frequency required for a clade to be retained in
            the consensus tree.
        **kwargs : dict
            Deprecated extra arguments accepted for backward compatibility.
            Any provided values are ignored with a warning to ``stderr``.

        Returns
        -------
        ToyTree
            Consensus tree inferred from the trees in this MultiTree.

        Raises
        ------
        ToytreeError
            If the MultiTree is empty.
        ValueError
            If ``min_freq`` is outside the valid range expected by the
            consensus inference routine.
        """
        from toytree.infer import consensus_tree

        _require_non_empty_treelist(self.treelist, "infer a consensus tree")
        _warn_deprecated_kwargs("get_consensus_tree", kwargs)
        return consensus_tree(self.treelist, min_freq=min_freq)

    def get_consensus_features(
        self,
        tree: ToyTree,
        features: list[str] | None = None,
        edge_features: list[str] | None = None,
        ultrametric: bool = False,
        conditional: bool = True,
    ) -> ToyTree:
        """Map summary feature data from the collection onto one tree.

        The supplied tree is typically a consensus tree, but any tree
        sharing relevant bipartitions can be used.

        Parameters
        ----------
        tree : ToyTree
            Tree that will receive the summarized feature annotations.
        features : list[str] or None, default=None
            Node features to summarize across matching bipartitions.
        edge_features : list[str] or None, default=None
            Edge features to summarize across matching bipartitions.
        ultrametric : bool, default=False
            If True, treat the input trees as rooted ultrametric trees
            when summarizing edge-related values.
        conditional : bool, default=True
            If True, summarize values only over trees containing the
            matching bipartition. If False, include all trees where the
            feature is defined.

        Returns
        -------
        ToyTree
            Copy of ``tree`` with summary statistics mapped onto matching
            nodes and edges.

        Raises
        ------
        ToytreeError
            If the MultiTree is empty.
        ValueError
            If requested feature names are invalid for the supplied trees.
        """
        from toytree.infer import consensus_features

        _require_non_empty_treelist(self.treelist, "map consensus features")
        return consensus_features(
            tree=tree,
            trees=self.treelist,
            features=features,
            edge_features=edge_features,
            ultrametric=ultrametric,
            conditional=conditional,
        )

    def root(
        self,
        *query: Query,
        root_dist: float | None = None,
        edge_features: Sequence[str] | None = None,
        inplace: bool = False,
    ) -> MultiTree:
        """Return a collection with every tree rooted on the same query.

        Parameters
        ----------
        *query : str, int, or Node
            One or more node selectors forwarded to
            :meth:`toytree.ToyTree.root`.
        root_dist : float or None, default=None
            Distance above the selected edge at which to place the new
            root. If None, each tree roots at the midpoint.
        edge_features : Sequence[str] or None, default=None
            Additional node features that should be treated as edge data
            during rerooting.
        inplace : bool, default=False
            If True, modify this MultiTree in place and return it.
            Otherwise return a rooted deep copy.

        Returns
        -------
        MultiTree
            Rooted collection.

        Raises
        ------
        ToytreeError
            Propagated if any tree cannot be rooted on the requested
            selection.
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
        """Return a collection with every tree unrooted.

        Parameters
        ----------
        inplace : bool, default=False
            If True, modify this MultiTree in place and return it.
            Otherwise return an unrooted deep copy.

        Returns
        -------
        MultiTree
            Unrooted collection.
        """
        mtree = self if inplace else self.copy()
        for tree in mtree:
            tree.unroot(inplace=True)
        return mtree

    def draw(
        self,
        shape: tuple[int, int] = (1, 4),
        shared_axes: bool = False,
        idxs: int | Sequence[int] | None = None,
        width: float | int | None = None,
        height: float | int | None = None,
        margin: float | tuple[float, float, float, float] | None = None,
        fixed_order: bool | Sequence[str] | None = None,
        label: str | Sequence[str | None] | None = None,
        **kwargs,
    ) -> tuple[Canvas, list[Cartesian], list[Mark]]:
        """Return a grid drawing of trees contained in the ``MultiTree``.

        Parameters
        ----------
        shape : tuple[int, int]
            Requested grid shape as ``(nrows, ncols)``.
        shared_axes : bool
            If True, linear layouts share the same rendered tree-depth span.
            Visible scale bars remain controlled by ``scale_bar``.
        idxs : int or Sequence[int] or None
            Optional tree indices to draw. If more indices are supplied than
            grid cells, extra indices are ignored. ``idxs=[]`` returns a
            blank grid with no rendered marks.
        width : float or int or None
            Canvas width in px. Must be > 0 when provided. If omitted,
            width is inferred from the rendered tree extents for the
            selected layout and then soft-capped for the full grid.
        height : float or int or None
            Canvas height in px. Must be > 0 when provided. If omitted,
            height is inferred from the rendered tree extents for the
            selected layout and then soft-capped for the full grid. If
            either dimension is provided explicitly, only the missing
            dimension is auto-sized.
        margin : float or tuple[float, float, float, float] or None
            Per-subplot margin in px, either as one scalar or
            ``(top, right, bottom, left)``.
        fixed_order : bool or Sequence[str] or None
            If True, infer a shared tip order from the selected trees and
            reuse cached results on repeated draws of the same selection.
            If a sequence is provided, it is forwarded directly to each
            rendered tree.
        label : str or Sequence[str or None] or None
            Axis label text for rendered trees. A scalar string is
            broadcast to rendered trees; a sequence must match the number
            of rendered trees.
        **kwargs : dict
            Additional ``ToyTree.draw()`` arguments applied to each
            rendered tree. ``padding`` must be a finite number >= 0 when
            provided.

        Returns
        -------
        tuple[Canvas, list[Cartesian], list[Mark]]
            Canvas, full grid axes list, and marks for rendered trees only.
            ``len(axes)`` always equals ``shape[0] * shape[1]`` while
            ``len(marks)`` equals the number of trees actually drawn.

        Raises
        ------
        ToytreeError
            Raised if drawing inputs are invalid or if ``shared_axes=True``
            is requested on a non-linear layout.
        """
        from toytree.drawing.src.draw_multitree import draw_multitree

        return draw_multitree(
            mtree=self,
            shape=shape,
            shared_axes=shared_axes,
            idxs=idxs,
            width=width,
            height=height,
            margin=margin,
            fixed_order=fixed_order,
            label=label,
            **kwargs,
        )

    def draw_cloud_tree(
        self,
        axes: Cartesian | None = None,
        fixed_order: Sequence[str] | bool | None = None,
        jitter: float = 0.0,
        idxs: int | Sequence[int] | None = None,
        interior_algorithm: int = 1,
        **kwargs,
    ) -> tuple[Canvas | None, Cartesian, list[Mark]]:
        """Return an overlay drawing of multiple trees on one set of axes.

        Parameters
        ----------
        axes : Cartesian or None, default=None
            Existing toyplot Cartesian axes on which to draw. If None, a
            new canvas and axes are created.
        fixed_order : Sequence[str], bool, or None, default=None
            Tip order to use for linear layouts. If a sequence is not
            provided, a consensus order is inferred from the selected
            trees.
        jitter : float, default=0.0
            Random baseline jitter forwarded to the cloud-tree renderer.
        idxs : int, Sequence[int], or None, default=None
            Optional tree indices to render. Negative indices are allowed.
            Unlike ``MultiTree.draw()``, an empty selection is invalid.
        interior_algorithm : int, default=1
            Interior-node positioning algorithm forwarded to each tree draw.
        **kwargs : dict
            Additional ``ToyTree.draw()`` styling arguments applied to the
            rendered trees.

        Returns
        -------
        tuple[Canvas | None, Cartesian, list[Mark]]
            Canvas (or None if ``axes`` was supplied), host Cartesian axes,
            and rendered tree marks in draw order.

        Raises
        ------
        ToytreeError
            If the MultiTree is empty or if ``idxs`` is invalid.
        """
        from toytree.drawing.src.draw_cloudtree import draw_cloudtree
        from toytree.drawing.src.setup_canvas import get_canvas_and_axes

        _require_non_empty_treelist(self.treelist, "draw a cloud tree")
        indices = _normalize_tree_indices(
            idxs,
            len(self.treelist),
            caller="draw_cloud_tree()",
        )
        selected = MultiTree([self.treelist[idx] for idx in indices])

        draw_kwargs = dict(kwargs)
        draw_kwargs["jitter"] = jitter
        draw_kwargs["axes"] = axes
        draw_kwargs["idxs"] = None
        draw_kwargs["tree_style"] = None
        draw_kwargs["fixed_order"] = fixed_order
        draw_kwargs["interior_algorithm"] = interior_algorithm
        draw_kwargs["kwargs"] = {}

        marks = draw_cloudtree(selected, **draw_kwargs)
        canvas, axes = get_canvas_and_axes(
            axes,
            marks[0],
            draw_kwargs.get("width"),
            draw_kwargs.get("height"),
        )

        for mark in marks:
            axes.add_mark(mark)

        if draw_kwargs.get("scale_bar", False):
            from toytree.annotate.src.add_scale_bar import (
                _add_axes_scale_bar_impl,
                _normalize_draw_scale_factor,
            )

            tree = max(selected, key=lambda item: item.treenode.height)
            if tree.style.layout in ("r", "u"):
                srange = (-tree.treenode.height, 0)
            else:
                srange = (0, tree.treenode.height)
            _add_axes_scale_bar_impl(
                tree,
                axes,
                scale=_normalize_draw_scale_factor(draw_kwargs["scale_bar"]),
                domain_override=srange,
            )
        elif canvas is not None:
            axes.x.show = False
            axes.y.show = False

        return canvas, axes, marks

    def reset_tree_styles(self) -> None:
        """Reset ``.style`` on every tree to the default TreeStyle."""
        for tree in self.treelist:
            tree.style = TreeStyle()

    def get_tip_labels(self) -> Sequence[str]:
        """Return tip labels in the order of the first tree.

        Returns
        -------
        Sequence[str]
            Tip-label order from the first tree in the MultiTree.

        Raises
        ------
        ToytreeError
            If the MultiTree is empty or the trees do not share the same
            set of tip labels.
        """
        _require_non_empty_treelist(self.treelist, "get tip labels")
        if not self.all_tree_tip_labels_same():
            raise ToytreeError(
                "All trees in treelist do not share the same set of tip labels."
            )
        return self.treelist[0].get_tip_labels()
