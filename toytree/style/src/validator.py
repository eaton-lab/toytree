#!/usr/bin/env python

"""Validate and/or expand styles.

"""

from typing import TypeVar, Sequence, Any, Union, Tuple
from loguru import logger
import numpy as np
import toyplot
from toytree.style import TreeStyle, normalize_values
from toytree.color import ToyColor, color_cycler, get_color_mapped_feature
from toytree.utils import (
    ToytreeError,
    StyleSizeMismatchError,
    StyleTypeMismatchError,
)

logger = logger.bind(name="toytree")
ToyTree = TypeVar("ToyTree")


def check_arr(values: Sequence[Any], label: str, size: int, ctype: type) -> np.ndarray:
    """project a value to an array of size with dtype.

    Raises an exception if values is 1 > len(values) > size, or it is
    not of the supported type.
    """
    arr = np.array(values)
    if not arr.size == size:
        raise StyleSizeMismatchError(
            f"'{label}' len mismatch error: len={arr.size} should be "
            f"len={size}.")
    if not isinstance(arr[0], ctype):
        raise StyleTypeMismatchError(
            f"'{label}' type not supported. You entered {type(arr[0])}, "
            f"should be len={ctype}.")
    return arr


def validate_style(tree: ToyTree, style: TreeStyle) -> TreeStyle:
    """Return a TreeStyle with values expanded and validated."""
    Validator(tree, style).run()


class Validator(TreeStyle):
    def __init__(self, tree: ToyTree, style: TreeStyle):
        super().__init__()
        self.__dict__ = style.__dict__
        self.tree = tree

    def run(self) -> None:
        """Expand, convert, and check all style args."""
        self.validate_node_colors()
        self.validate_node_mask()
        self.validate_node_sizes()
        self.validate_node_markers()
        self.validate_node_hover()
        self.validate_node_style()

        self.validate_node_labels()
        self.validate_node_labels_style()

        self.validate_edge_colors()
        self.validate_edge_widths()
        self.validate_edge_style()
        self.validate_edge_align_style()

        self.validate_tip_labels()
        self.validate_tip_labels_colors()
        self.validate_tip_labels_angles()
        self.validate_tip_labels_style()

    def validate_node_colors(self) -> None:
        """Set .node_colors to type=ndarray size=nnodes or None.

        If only one color was entered then store as node_style.fill.
        Only expand .node_colors into an array of size nnodes if there
        is variation among nodes.

        Args
        ----
        None
        ToyColor, str (css)
        """
        # if no node_colors then nodes will be colored by node_style.fill
        if self.node_colors is None:
            return

        # special (feature, cmap) tuple. This must captures special
        # tuple colormappings but not colors entered as a tuple, e.g.,
        # (0, 1, 0, 1).
        if isinstance(self.node_colors, tuple) and len(self.node_colors) == 2:
            feat, cmap = self.node_colors
            values = self.tree.get_node_data(feat).values
            self.node_colors = get_color_mapped_feature(values, cmap)

        # user entered ToyColor or List[ToyColor], pd.Series[ToyColor]
        colors = ToyColor.color_expander(self.node_colors)

        if isinstance(colors, ToyColor):
            self.node_colors = None
            self.node_style.fill = colors
        else:
            # self.node_style.fill = None
            self.node_colors = check_arr(
                values=colors,
                label="node_colors",
                size=self.tree.nnodes,
                ctype=np.void,
            )

    def validate_node_mask(self) -> None:
        """Sets node_mask to ndarray[bool] size=nnodes.

        Mask is a bool array in idx order where True hides node marker.

        Args
        ----
        None: special arg to hide tips only
        True: mask all nodes
        False: show all nodes
        Iterable: custom boolean mask
        Tuple: (bool, bool, bool) for show (tips, internal, root).
        """
        if self.node_mask is None:
            self.node_mask = (0, 1, 1)
        elif self.node_mask is False:
            self.node_mask = np.repeat(True, self.tree.nnodes)
        elif self.node_mask is True:
            self.node_mask = np.repeat(False, self.tree.nnodes)

        if isinstance(self.node_mask, tuple):
            self.node_mask = self.tree.get_node_mask(
                show_tips=self.node_mask[0],
                show_internal=self.node_mask[1],
                show_root=self.node_mask[2],
            )
        self.node_mask = check_arr(
            self.node_mask, "node_mask", self.tree.nnodes, np.bool_)

    def validate_node_sizes(self) -> None:
        """Sets node_sizes to ndarray[float]."""
        if isinstance(self.node_sizes, (int, float)):
            self.node_sizes = np.repeat(self.node_sizes, self.tree.nnodes)
        self.node_sizes = check_arr(
            self.node_sizes, "node_sizes", self.tree.nnodes, (int, float, np.integer))

    def validate_node_markers(self) -> None:
        """Sets node_markers to ndarray[str] or ndarray[Marker]."""
        if isinstance(self.node_markers, (str, toyplot.marker.Marker)):
            self.node_markers = np.repeat(self.node_markers, self.tree.nnodes)
        self.node_markers = check_arr(
            self.node_markers, "node_markers", self.tree.nnodes,
            (str, toyplot.marker.Marker)
        )

    def validate_node_style(self) -> None:
        """Sets node_style.fill and .stroke"""
        if self.node_style.stroke is None or self.node_style.stroke == "none":
            self.node_style.stroke = ToyColor("transparent")
        if self.node_style.stroke is not None:
            self.node_style.stroke = ToyColor(self.node_style.stroke)
        if isinstance(self.node_style.fill, str):
            if self.node_style.fill == "none":
                self.node_style.fill = None
        if self.node_style.fill is not None:
            self.node_style.fill = ToyColor(self.node_style.fill)
        if self.node_style.fill_opacity:
            assert isinstance(self.node_style.fill_opacity, float), (
                "node_style.fill_opacity must be a float value or None.")

    def validate_node_labels(self) -> None:
        """Sets node_labels to np.ndarray[str] or None.

        Also applies floating point string formatting on node_labels.

        Args
        ----
        None: None
        False: None
        True: 'idx' labels
        other: custom collection of the proper size.
        """
        # get node_labels as either None or mixed type
        if self.node_labels is False:
            self.node_labels = None
        elif self.node_labels is None:
            self.node_labels = None
        elif self.node_labels is True:
            self.node_labels = range(self.tree.nnodes)

        # feature expansion w/ auto-float format to :.2g
        elif isinstance(self.node_labels, str):
            self.node_labels = self.tree.get_node_data(self.node_labels)

        # or, user entered a list, tuple, Series, array, etc.
        # which is checked and handled below.

        # double check size and cast to str
        if self.node_labels is not None:
            # try to float format but OK if fails b/c data may not be a
            # float, and could even be a complex type like a list.
            try:
                self.node_labels = [f"{i:.4g}" for i in self.node_labels]
            except (ValueError, TypeError):
                self.node_labels = [str(i) for i in self.node_labels]

            # set any missing (nan) labels to empty strings.
            self.node_labels = [
                "" if i == "nan" else i for i in self.node_labels
            ]
            # validate.
            self.node_labels = check_arr(
                self.node_labels, "node_labels", self.tree.nnodes, str,
            )

    def validate_node_labels_style(self) -> None:
        """Ensure tip labels are in px sizes and check fill color
        """
        size = toyplot.units.convert(
            value=self.node_labels_style.font_size,
            target="px", default="px",
        )
        self.node_labels_style.font_size = f"{size:.1f}px"
        if self.node_labels_style.fill is not None:
            self.node_labels_style.fill = ToyColor(self.node_labels_style.fill)

    def validate_node_hover(self) -> None:
        """Sets node_hover to ndarray[str] or None.

        No comparisons use 'is in' to support flexible input types
        including pd.Series.
        """
        if self.node_hover is None:
            self.node_hover = None
        elif self.node_hover is False:
            self.node_hover = None

        # create node data strings ordered features
        elif self.node_hover is True:
            ordered_features = ["idx", "dist", "support", "height"]
            lfeatures = list(set(self.tree.features) - set(ordered_features))
            ordered_features += lfeatures
            self.node_hover = [" "] * self.tree.nnodes
            for idx in range(self.tree.nnodes):
                feats = []
                node = self.tree[idx]
                for feature in ordered_features:
                    val = getattr(node, feature, np.nan)
                    if isinstance(val, float):
                        val = f"{val:.3g}"
                    else:
                        val = str(val)
                    feats.append(f"{feature}: {val}")
                self.node_hover[idx] = "\n".join(feats)

        # special extract data from tree data
        elif isinstance(self.node_hover, str):
            self.node_hover = [
                f"{self.node_hover}={i:.3g}" for i in
                self.tree.get_node_data(self.node_hover)
            ]

        # other: user entered data as a collection
        else:
            # this will parse pd.Series, list, ndarray, etc.
            try:
                self.node_hover = [f"{i:.3g}" for i in self.node_hover]
            except Exception as exc:
                raise ToytreeError(
                    f"\n'node_hover' type {type(self.node_hover)} is not supported.\n"
                    "Try using node_hover=True. You can set additional data to the \n"
                    "ToyTree using the .set_node_data() function."
                ) from exc
        # validate
        if self.node_hover is not None:
            self.node_hover = check_arr(
                self.node_hover, "node_hover", self.tree.nnodes, str,
            )

    def validate_tip_labels(self) -> None:
        """Sets tip_labels to np.ndarray[str] or None.

        Args
        ----
        None: None
        False: None
        True: extract labels from tree
        other: custom collection of ntips names in idx order
        """
        # get tip_labels as either None or mixed type
        if self.tip_labels is False:
            self.tip_labels = None
        elif self.tip_labels is None:
            self.tip_labels = None
        elif self.tip_labels is True:
            self.tip_labels = self.tree.get_tip_labels()
        # feature expansion
        elif isinstance(self.tip_labels, str):
            self.tip_labels = self.tree.get_tip_data(self.tip_labels)

        # double check size and cast to str
        if self.tip_labels is not None:
            self.tip_labels = [str(i) for i in self.tip_labels]
            self.tip_labels = check_arr(
                self.tip_labels, "tip_labels",
                self.tree.ntips, str,
            )

    def validate_tip_labels_colors(self) -> None:
        """Set .tip_labels_colors to type=ndarray size=nnodes or None.
        """
        # use tip_labels_style
        if self.tip_labels_colors is None:
            return

        # special (feature, colormap) tuple.
        if isinstance(self.tip_labels_colors, tuple) and len(self.tip_labels_colors) == 2:
            feat, cmap = self.tip_labels_colors
            values = self.tree.get_tip_data(feat).values
            self.tip_labels_colors = get_color_mapped_feature(values, cmap)

        # convert to List[ToyColor]
        colors = ToyColor.color_expander(self.tip_labels_colors)

        if isinstance(colors, ToyColor):
            self.tip_labels_colors = None
            self.tip_labels_style.fill = colors.css
        else:
            self.tip_labels_style.fill = None
            self.tip_labels_colors = check_arr(
                values=colors,
                label="tip_labels_colors",
                size=self.tree.ntips,
                ctype=np.void,
            )

    def validate_tip_labels_angles(self) -> None:
        """Sets tip_labels_angles to ndarray[float]. None is auto layout.
        """
        if self.tip_labels_angles is None:
            if self.layout in ['u', 'd']:
                angles = np.repeat(-90, self.tree.ntips)
            else:
                angles = np.zeros(self.tree.ntips)
        # use auto value filled during layout, or user arg.
        else:
            angles = self.tip_labels_angles
        # validate.
        self.tip_labels_angles = check_arr(
            angles, "tip_labels_angles",
            self.tree.ntips, (float, int, np.integer),
        )

    def validate_tip_labels_style(self) -> None:
        """Sets tip_labels_style minimal requirements.
        """
        size = toyplot.units.convert(
            value=self.tip_labels_style.font_size,
            target="px", default="px"
        )
        self.tip_labels_style.font_size = f"{size:.1f}px"
        if self.tip_labels_style.fill is not None:
            self.tip_labels_style.fill = ToyColor(self.tip_labels_style.fill)
        # if self.tip_labels_style.stroke is not None:
            # self.tip_labels_style.stroke = ToyColor(self.tip_labels_style.stroke)

    def validate_edge_colors(self) -> None:
        """Set .edge_colors to type=ndarray size=nnodes or None.
        """
        if self.edge_colors is None:
            return

        # special (feature, cmap) tuple.
        if isinstance(self.edge_colors, tuple) and len(self.edge_colors) == 2:
            feat, cmap = self.edge_colors
            values = self.tree.get_node_data(feat).values
            self.edge_colors = get_color_mapped_feature(values, cmap)

        # user entered ToyColor or List[ToyColor]
        colors = ToyColor.color_expander(self.edge_colors)

        if isinstance(colors, ToyColor):
            self.edge_colors = None
            self.edge_style.stroke = colors
        else:
            # self.edge_style.stroke = None
            self.edge_colors = check_arr(
                values=colors,
                label="edge_colors",
                size=self.tree.nnodes,
                ctype=np.void,
            )

    def validate_edge_style(self) -> None:
        """Sets edge_style minimal requirements.
        """
        if isinstance(self.edge_style.stroke, str):
            if self.edge_style.stroke == "none":
                self.edge_style.stroke = None
        if self.edge_style.stroke is not None:
            self.edge_style.stroke = ToyColor(self.edge_style.stroke)

    def validate_edge_widths(self) -> None:
        """Sets edge_widths to ndarray[float] or None, in which case the
        value is taken from edge_style.stroke-width.
        """
        # if a single value was entered then overwrite stroke-width
        if isinstance(self.edge_widths, (int, float, np.integer)):
            self.edge_style.stroke_width = float(self.edge_widths)
            self.edge_widths = None

        # if None then use edge_style.stroke_width
        if self.edge_widths is None:
            return

        # special mapping of values to normalized range
        # allow missing feature here to support tree_style='p'
        # default setting for Ne values mapped to edge_widths.
        # as ("Ne", 2, 10)
        if isinstance(self.edge_widths, tuple):
            feat, mini, maxi, *nbins = self.edge_widths
            nbins = nbins[0] if nbins else 10
            if feat in self.tree.features:
                vals = self.tree.get_node_data(feat, missing=2)
            else:
                self.edge_widths = None
                return
            self.edge_widths = normalize_values(vals, mini, maxi, nbins)

        # support special fetching values from tree data.
        if isinstance(self.edge_widths, str):
            vals = self.tree.get_node_data(self.edge_widths, missing=2)
            self.edge_widths = vals

        # validate
        self.edge_widths = check_arr(
            self.edge_widths, "edge_widths",
            self.tree.nnodes, (int, float, np.integer)
        )

    def validate_edge_align_style(self) -> None:
        """Sets edge_align_style minimal requirements.
        """
        if isinstance(self.edge_align_style.stroke, str):
            if self.edge_align_style.stroke == "none":
                self.edge_align_style.stroke = None
        if self.edge_align_style.stroke is not None:
            self.edge_align_style.stroke = ToyColor(self.edge_align_style.stroke)
        if self.edge_align_style.stroke_dasharray is not None:
            assert isinstance(self.edge_align_style.stroke_dasharray, str), (
                "stroke-dasharray arg should be a string, e.g., '2,2'.")

    def validate_admixture_edges(self) -> None:
        """Expand admixture args to a list of tuples.

        The source and dest Nodes can be selected using either their
        Node int idx label, or Node name str, or multiple Node name
        strs, the latter of which will select the MRCA Node.

        The proper format should be:

        >>> admixture_edges = [
        >>>     (src_idx, dest_idx, (src_time, dest_time), dict, str)
        >>> ]
        """
        # bail if empty
        if self.admixture_edges is None:
            return

        # if tuple then expand into a list
        if isinstance(self.admixture_edges, tuple):
            self.admixture_edges = [self.admixture_edges]

        # get color generator and skip the first
        icolors = color_cycler()
        admix_tuples = []
        for atup in self.admixture_edges:

            # required: src node idx from Union[int, str, Iterable[str]]
            if isinstance(atup[0], (int, str)):
                src = self.tree.get_mrca_node(atup[0]).idx
            else:
                src = self.tree.get_mrca_node(*atup[0]).idx

            # required: dest node idx from Union[int, str, Iterable[str]]
            if isinstance(atup[1], (int, str)):
                dest = self.tree.get_mrca_node(atup[1]).idx
            else:
                dest = self.tree.get_mrca_node(*atup[1]).idx

            # optional: proportion on edges
            if len(atup) > 2:
                if isinstance(atup[2], (int, float)):
                    prop = float(atup[2])
                else:
                    prop = (float(atup[2][0]), float(atup[2][1]))
            else:
                prop = 0.5

            # optional: style dictionary
            if len(atup) > 3:
                style = dict(atup[3])
            else:
                style = {}

            # optional label on midpoint
            if len(atup) > 4:
                label = str(atup[4])
            else:
                label = None

            # color setting.
            stroke = (
                ToyColor(next(icolors)) if "stroke" not in style
                else ToyColor(style['stroke'])
            )
            style['stroke'] = stroke.css
            style['stroke-opacity'] = style.get('stroke-opacity', 0.7)

            # check styledict colors, etc
            admix_tuples.append((src, dest, prop, style, label))
        self.admixture_edges = admix_tuples


if __name__ == "__main__":

    import toytree
    import toyplot

    tre = toytree.rtree.unittree(6)
    tre.draw(node_colors='red')

    raise SystemExit(0)

    tre = toytree.rtree.unittree(6)
    tre.set_node_data("test", default=['hi', 3], inplace=True)
    sty = tre.style.copy()

    # sty.node_colors = (["red", "blue"] * 5) + ["green"]
    # sty.node_colors = toytree.color.COLORS1
    # sty.node_colors = toyplot.color.Palette(colors=[
    #     'red', 'blue', 'green', (0.5, 0.4, 0.3, 1.0), toyplot.color.Palette()[0],
    #     'cyan', 'magenta', 'red', 'red', 'red', 'red'
    # ])
    sty.node_colors = ("dist", "Spectral")
    sty.edge_colors = ("dist", "BlueRed")
    sty.tip_labels_colors = "red"
    sty.node_mask = tre.get_node_mask()
    sty.node_sizes = [2.5] * 11
    sty.node_markers = 'o'
    sty.node_markers = toyplot.marker.create("o")
    # sty.node_markers = ['s', 'o']
    sty.node_labels = "idx"
    sty.node_labels = "dist"
    sty.node_labels = tre.get_node_data('height')
    sty.node_labels = True
    sty.node_labels = False
    sty.node_labels = ([2.5, 3, "A", "B", 30000] * 2) + [{'red'}]
    sty.tip_labels = "idx"
    sty.tip_labels = True
    sty.tip_labels = False
    sty.tip_labels = range(6)
    # sty.edge_widths = ([2.] * 10) + [3.5]
    sty.edge_style.stroke_width = 5
    # sty.edge_widths = "idx"
    # sty.edge_widths = ("idx", 2, 5)
    # sty.edge_widths = ("idx", 2, 10)
    # sty.edge_widths = ("idx", 2, 10, 4)
    sty.edge_widths = 3
    sty.node_hover = True
    sty.node_hover = False
    sty.node_hover = "idx"
    sty.node_hover = tre.get_node_data("dist")

    val = Validator(tre, sty)
    val.run()
    print(val.dict(serialize=False))
