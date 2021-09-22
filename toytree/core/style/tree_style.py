#!/usr/bin/env python

"""Tree Styles checked and expanded at .draw() or repr().

Examples
--------
>>> toytree.tree(...)                   # DefaultTreeStyle() init
>>> tree.draw(**kwargs)                 # dict or user args
>>> style = DefaultTreeStyle(**kwargs)  # DefaultTreeStyle(**dict, **tree.style)
"""

from typing import List, Tuple, Optional, Union, Iterable, Dict
import json
from enum import Enum
from dataclasses import dataclass, asdict, field
import toyplot
from loguru import logger
import numpy as np
import pandas as pd
from toytree.core.node_assist import NodeAssist
from toytree.core.style.color import ToyColor, Color, color_parser, color_cycler
from toytree.utils.transform import normalize_values
from toytree.utils import ToytreeError


class EdgeType(str, Enum):
    cladogram = 'c'
    phylogram = 'p'
    bezier = 'b'

class LayoutType(str, Enum):
    right = 'right'
    left = 'left'
    down = 'down'
    up = 'up'
    circle = 'circular'
    #unrooted = 'unrooted'

class SubStyle:
    """
    When converted to dict the keys of substyles will be changed
    from e.g., _toyplot_anchor_shift to -toyplot-anchor-shift.
    """

@dataclass
class NodeStyle(SubStyle):
    fill: Color = 'rgba(40.0%,76.1%,64.7%,1.000)'
    fill_opacity: Optional[float] = None
    stroke: Optional[Color] = "#262626"
    stroke_width: float = 1.0

@dataclass
class NodeLabelStyle(SubStyle):
    fill: Color = 'rgba(16.1%,15.3%,14.1%,1.000)'
    font_size: Union[int, str] = 9
    font_weight: int = 300
    font_family: str = "Helvetica"
    _toyplot_anchor_shift: Union[str, int] = 0
    baseline_shift: Union[str,int] = 0
    text_anchor: str = "middle"

@dataclass
class EdgeStyle(SubStyle):
    stroke: Color = 'rgba(16.1%,15.3%,14.1%,1.000)'
    stroke_width: float = 2.
    stroke_opacity: Optional[float] = None
    stroke_linecap: str = "round"
    stroke_dasharray: Optional[str] = None

@dataclass
class EdgeAlignStyle(SubStyle):
    stroke: Color = 'rgba(66.3%,66.3%,66.3%,1.000)'
    stroke_width: int = 2
    stroke_opacity: Optional[float] = 0.75
    stroke_linecap: str = "round"
    stroke_dasharray: str = "2,4"

@dataclass
class TipLabelsStyle(SubStyle):
    fill: Color = 'rgba(16.1%,15.3%,14.1%,1.000)'
    fill_opacity: Optional[float] = None
    font_size: Union[str, float] = 11
    font_weight: int = 300
    font_family: str = "Helvetica"
    _toyplot_anchor_shift: Union[str, float] = 15
    baseline_shift: Union[str,int] = 0
    text_anchor: str = "start"

######################################################################
#
#  Base TreeStyle Class with validation functions
#
######################################################################

@dataclass
class TreeStyle:
    # inherited from tree at validation steps
    tree_style: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
    layout: LayoutType = 'r'

    edge_type: EdgeType = 'p'
    edge_colors: Union[Color, Iterable[Color], None] = None  # override by fill
    edge_widths: Union[int, Iterable[int], None] = None  # override by stroke-width
    edge_style: EdgeStyle = field(default_factory=EdgeStyle)
    edge_align_style: EdgeAlignStyle = field(default_factory=EdgeAlignStyle)

    node_mask: Union[bool, Iterable[bool], None] = None  # None = auto
    node_colors: Union[Color, Iterable[Color], None] = None  # override by fill
    node_sizes: Union[int, Iterable[int]] = 0
    node_markers: Union[str, Iterable[str]] = "o"
    node_hover: Union[bool, str, Iterable[str]] = None  # None = auto
    node_style: NodeStyle = field(default_factory=NodeStyle)

    node_labels: Union[bool, str, Iterable[str]] = False
    node_labels_style: NodeLabelStyle = field(default_factory=NodeLabelStyle)

    tip_labels: Union[bool, Iterable[str]] = True
    tip_labels_colors: Union[str, Iterable[str], None] = None
    tip_labels_align: bool = False
    tip_labels_style: TipLabelsStyle = field(default_factory=TipLabelsStyle)
    tip_labels_angles: Union[float, Iterable[float], None] = None

    use_edge_lengths: bool = True
    scale_bar: Union[bool,float] = False
    padding: int = 15
    xbaseline: int = 0
    ybaseline: int = 0
    admixture_edges: Union[List[Tuple[int, int]], None] = None
    shrink: int = 0


    def validate(self, tree: 'toytree.ToyTree'):
        """
        Expand iterable style entires to None or ndarray, and
        convert color args to CSS strings. This function is called
        before passing style args to ToyTreeMark.

        The validate x_style funcs should come last in each group
        because the fill,stroke styles can change.
        """
        self.tree = tree  # ignore
        self._validate_node_colors()
        self._validate_node_mask()
        self._validate_node_sizes()
        self._validate_node_markers()
        self._validate_node_hover()
        self._validate_node_style()

        self._validate_node_labels()
        self._validate_node_labels_style()

        self._validate_tip_labels()
        self._validate_tip_labels_colors()
        self._validate_tip_labels_angles()
        self._validate_tip_labels_style()

        self._validate_edge_colors()
        self._validate_edge_widths()
        self._validate_edge_style()
        self._validate_edge_align_style()

        self._validate_admixture_edges()

    def _serialize_colors(self):
        """
        Convert all ndarrays to lists for serialization of JSON.
        """
        self._validate_node_colors()
        self._validate_tip_labels_colors()
        self._validate_edge_colors()
        # ... substyledicts

    def _serialize_css_styles(self):
        """
        Convert keys with lower_case ndarrays to lists for
        serialization of JSON...
        """
        self._validate_node_colors()
        self._validate_tip_labels_colors()
        # ... substyledicts

    def _serialize_arrays(self):
        """
        Convert any numpy or pandas inputs to lists for easier
        validation casting. This is called for serialization and
        during validation.
        """
        arrayed = [
            "node_mask",
            "node_sizes",
            "node_labels",
            "node_colors",
            "tip_labels",
        ]
        for key in arrayed:
            values = getattr(self, key)
            if isinstance(values, pd.DataFrame):
                logger.warning("DataFrame entry is ambiguous, select a Series")
                setattr(self, key, values.iloc[:, 0].tolist())
            elif isinstance(values, pd.Series):
                setattr(self, key, values.tolist())
            # TODO, maybe this is unnecessary now with color-parser
            elif isinstance(values, np.ndarray):
                # array can be a collection of things, or a color array
                if hasattr(values, 'r'):
                    setattr(self, key, ToyColor(values).css)
                else:
                    setattr(self, key, values.tolist())


    def _validate_node_colors(self):
        """
        Sets node_colors to ndarray[str] or None, and sets
        node_style.fill to None or single color value.
        """
        if self.node_colors is None:
            return
        # convert to a ToyColor or list of ToyColors
        colors = color_parser(self.node_colors)

        if isinstance(colors, ToyColor):
            css_color = colors.css
            self.node_colors = None
            self.node_style.fill = css_color
        else:
            colors = [i.css for i in colors]
            self.node_colors = toyplot.broadcast.pyobject(
                colors, self.tree.nnodes).astype(str)
            self.node_style.fill = None

    def _validate_node_mask(self):
        """
        Sets node_mask to ndarray[bool].
            None: special to hide tips only
            True: show all
            False: hide all
            Iterable: custom
        """
        if self.node_mask is True:
            self.node_mask = np.repeat(self.node_mask, self.tree.nnodes)
        if self.node_mask is False:
            self.node_mask = np.repeat(self.node_mask, self.tree.nnodes)
        if self.node_mask is None:
            self.node_mask = np.zeros(self.tree.nnodes, dtype=bool)
            self.node_mask[:self.tree.ntips] = True
        self.node_mask = toyplot.broadcast.pyobject(
            self.node_mask, self.tree.nnodes).astype(bool)

    def _validate_node_sizes(self):
        """
        Sets node_sizes to ndarray[float]
        """
        self.node_sizes = toyplot.broadcast.scalar(
            self.node_sizes, self.tree.nnodes)

    def _validate_node_markers(self):
        """
        Sets node_markers to ndarray[str]
        """
        self.node_markers = toyplot.broadcast.pyobject(
            self.node_markers, self.tree.nnodes)

    def _validate_node_labels(self):
        """
        Sets node_labels to ndarray[str] or None and apply simple
        floating point string formatting on node_labels.
        """
        # get node_labels as either None or mixed type
        if self.node_labels is False:
            self.node_labels = None
        elif self.node_labels is None:
            self.node_labels = None
        elif self.node_labels is True:
            self.node_labels = range(self.tree.nnodes)
        elif isinstance(self.node_labels, pd.Series):
            # assume user can float format themselves...
            pass
        elif isinstance(self.node_labels, str):
            # auto-float format
            self.node_labels = self.tree.get_node_data(self.node_labels)

            # check if it can be cast from float to int
            if self.node_labels.dtype == float:

                # wrap in try to allow for customs with NaN
                try:
                    # trim off anything after .6, and string format to match
                    self.node_labels = self.node_labels.round(6)

                    # check if it can be cast to int
                    if all(i % 1 == 0 for i in self.node_labels):
                        self.node_labels = self.node_labels.astype(int)
                except Exception:
                    pass

        # double check size and cast to str
        if self.node_labels is not None:
            self.node_labels = toyplot.broadcast.pyobject(
                self.node_labels, self.tree.nnodes).astype(str)

    def _validate_node_labels_style(self):
        """
        Ensure tip labels are in px sizes and check fill color
        """
        self.node_labels_style.font_size = "{:.1f}px".format(
            toyplot.units.convert(
                value=self.node_labels_style.font_size,
                target="px", default="px")
        )
        if self.node_labels_style.fill is not None:
            self.node_labels_style.fill = ToyColor(self.node_labels_style.fill)

    def _validate_node_hover(self):
        """
        Sets node_hover to ndarray[str] or None. No comparisons use
        'is in' to support flexible input types including pd.Series.
        """
        if self.node_hover is None:
            self.node_hover = None
        elif self.node_hover is False:
            self.node_hover = None
        elif self.node_hover is True:
            ordered_features = ["idx", "dist", "support", "height"]
            lfeatures = list(set(self.tree.features) - set(ordered_features))
            ordered_features += lfeatures
            self.node_hover = [" "] * self.tree.nnodes
            for idx in self.tree.idx_dict:
                feats = []
                node = self.tree.idx_dict[idx]
                for feature in ordered_features:
                    val = getattr(node, feature)
                    if isinstance(val, float):
                        fstring = np.format_float_positional(round(val, 8), trim='0')
                        feats.append(f"{feature}: {fstring}")
                    else:
                        feats.append(f"{feature}: {val}")
                self.node_hover[idx] = "\n".join(feats)
        elif isinstance(self.node_hover, pd.Series):
            self.node_hover = self.node_hover.astype(str)
        elif isinstance(self.node_hover, str):
            self.node_hover = self.tree.get_node_data(self.node_hover).astype(str)
        else:
            self.node_hover = toyplot.broadcast.pyobject(self.node_hover, self.tree.nnodes).astype(str)

    def _validate_node_style(self):
        """
        Sets node_style.fill and .stroke to str
        """
        if self.node_style.stroke is None or self.node_style.stroke == "none":
            self.node_style.stroke = "transparent"
        if self.node_style.stroke is not None:
            self.node_style.stoke = ToyColor(self.node_style.stroke).css
        if self.node_style.fill == "none":
            self.node_style.fill = None
        if self.node_style.fill is not None:
            self.node_style.fill = ToyColor(self.node_style.fill).css

    def _validate_tip_labels_colors(self):
        """
        Sets tip_labels_colors to ndarray[str] or None, and sets
        tip_labels.style.fill to None or single color.
        """
        if self.tip_labels_colors is None:
            return
        # convert to a ToyColor or list of ToyColors
        colors = color_parser(self.tip_labels_colors)
        if isinstance(colors, ToyColor):
            css_color = colors.css
            self.tip_labels_colors = None
            self.tip_labels_style.fill = css_color
        else:
            colors = [i.css for i in colors]
            self.tip_labels_colors = toyplot.broadcast.pyobject(
                colors, self.tree.ntips).astype(str)
            self.tip_labels_style.fill = None

    def _validate_tip_labels(self):
        """
        Expand tip labels to a list of strings of len=ntips.
        """
        if self.tip_labels is True:
            self.tip_labels = np.array(self.tree.get_tip_labels())
        elif self.tip_labels is False:
            self.tip_labels = None
        else:
            if isinstance(self.tip_labels, str):
                if self.tip_labels in self.tree.features:
                    self.tip_labels = self.tree.get_tip_data(self.tip_labels)
            self.tip_labels = toyplot.broadcast.pyobject(
                self.tip_labels, self.tree.ntips).astype(str)

    def _validate_tip_labels_angles(self):
        """
        sets tip_labels_angles to ndarray[float]. None is auto layout.
        """
        if self.tip_labels_angles is None:
            if self.layout == 'c':
                tip_radians = np.linspace(0, np.pi * 2, self.tree.ntips + 1)[:-1]
                angles = np.array([np.rad2deg(abs(i)) for i in tip_radians])
            elif self.layout in ["u", "d"]:
                angles = -90
            else:
                angles = 0
        else:
            angles = self.tip_labels_angles
        self.tip_labels_angles = (
            toyplot.broadcast.scalar(angles, self.tree.ntips))

    def _validate_tip_labels_style(self):
        """

        """
        self.tip_labels_style.font_size = "{:.1f}px".format(
            toyplot.units.convert(
                value=self.tip_labels_style.font_size,
                target="px", default="px")
        )
        # self.tip_labels_style._toyplot_anchor_shift = "{:.2f}px".format(
        #     toyplot.units.convert(
        #         self.tip_labels_style._toyplot_anchor_shift, "px", "px")
        # )


    def _validate_edge_colors(self):
        """
        Sets edge_colors to ndarray[str] or None, and sets
        edge_style.stroke to None or single color value. Allow
        values to be nnodes or nnodes -1, since root edge is not
        shown?
        """
        if self.edge_colors is None:
            return
        # convert to a ToyColor or list of ToyColors
        colors = color_parser(self.edge_colors)
        if isinstance(colors, ToyColor):
            css_color = colors.css
            self.edge_colors = None
            self.edge_style.stroke = css_color
        else:
            colors = [i.css for i in colors]
            self.edge_colors = toyplot.broadcast.pyobject(
                colors, self.tree.nnodes).astype(str)
            self.edge_style.stroke = None

    def _validate_edge_style(self):
        """
        If edge_colors are variable then edge_style.stroke is set to
        None, else edge_style.stroke is one color. Opacity is set to
        None by default, if a value is set then it applies on top of
        existing colors.
        """
        if isinstance(self.edge_style.stroke, str):
            if self.edge_style.stroke == "none":
                self.edge_style.stroke = None
        if self.edge_style.stroke is not None:
            self.edge_style.stoke = ToyColor(self.edge_style.stroke).css
        # self.edge_style.stroke_opacity

    def _validate_edge_widths(self):
        """
        Sets edge_widths to ndarray[float] or None, in which case the
        value is taken from edge_style.stroke-width.
        """
        if self.edge_widths is not None:
            if isinstance(self.edge_widths, str):
                if self.edge_widths in self.tree.features:
                    self.edge_widths = normalize_values(
                        self.tree.get_node_data(self.edge_widths, missing=2)
                    )
                else:
                    self.edge_widths = 2
        self.edge_widths = toyplot.broadcast.scalar(
            self.edge_widths, self.tree.nnodes)

    def _validate_edge_align_style(self):
        """

        """
        # if self.edge_align_style.stroke == "none":
        #     self.edge_style.stroke = None
        # if self.edge_style.stroke is not None:
        #     self.edge_style.stoke = ToyColor(self.edge_style.stroke).css
        # # self.edge_style.stroke_opacity


    def _validate_admixture_edges(self):
        """
        Expand to a list of tuples of form:
        admixture_edges = [
            (src_idx, dest_idx, (src_time, dest_time), styledict, label)
        ]
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
            if isinstance(atup[0], (str, list, tuple)):
                nas = NodeAssist(self.tree, atup[0], None, None)
                node = nas.get_mrca()
                if not node.is_root():
                    src = node.idx
                else:
                    nas.match_reciprocal()
                    src = nas.get_mrca().idx
            else:
                src = int(atup[0])

            # required: dest node idx from Union[int, str, Iterable[str]]
            if isinstance(atup[1], (str, list, tuple)):
                nas = NodeAssist(self.tree, atup[1], None, None)
                node = nas.get_mrca()
                if not node.is_root():
                    dest = node.idx
                else:
                    nas.match_reciprocal()
                    dest = nas.get_mrca().idx
            else:
                dest = int(atup[1])

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
            style['stroke'] = stroke.color.css
            style['stroke-opacity'] = style.get('stroke-opacity', 0.7)

            # check styledict colors, etc
            admix_tuples.append((src, dest, prop, style, label))
        self.admixture_edges = admix_tuples


    def dict(
        self,
        serialize_colors: bool=False,
        serialize_arrays: bool=False,
        validate_css: bool=False,
        ):
        """
        Returns a (serializable) dictionary of the TreeStyle.

        Parameters
        ----------
        serialize_colors: bool
            Converts colors to CSS strings.
        serialize_arrays: bool
            Converts ndarrays to lists.
        validate_css: bool
            Converts substyle keys to valide CSS (e.g., '_' -> '-'')
        """
        # first convert any ndarray colors to CSS str or Collection[str]
        # whether entered as a single value or a Collectin of values.
        if serialize_colors:
            self._serialize_colors()


        # first converts pandas/numpy to List[Any] or str. This is

        # not called by validate()
        if serialize_arrays:
            self._serialize_arrays()
        # next convert
        style_dict = asdict(self)
        if validate_css:
            self._to_css_styles(style_dict)
        return style_dict

    def json(self):
        """Returns a JSON serialized dict of the TreeStyle"""
        mydict = self.dict(True, True, True)
        return json.dumps(mydict, indent=4)

    def __repr__(self):
        """Recursive dict to JSON representation"""
        return self.json()

    def _to_css_styles(self, style_dict: Dict[str,str]):
        """
        Convert dict keys to valid CSS styles
        """
        style_dict_keys = list(style_dict.keys())
        for key in style_dict_keys:
            sub_style = getattr(self, key)
            if isinstance(sub_style, SubStyle):
                sub_style_dict = style_dict[key]
                sub_style_dict_keys = list(sub_style_dict.keys())
                for skey in sub_style_dict_keys:
                    new_skey = skey.replace("_", "-")
                    svalue = sub_style_dict.pop(skey)
                    sub_style_dict[new_skey] = svalue


######################################################################
#
# BUILTIN TREE STYLES
#
######################################################################


@dataclass(repr=False)
class NormalTreeStyle(TreeStyle):
    tree_style: str = 'n'

@dataclass(repr=False)
class SimpleTreeStyle(TreeStyle):
    tree_style: str = 's'
    node_labels: bool = True
    node_mask: bool = False
    node_sizes: int = 18
    node_style: NodeStyle = field(
        default_factory=lambda: NodeStyle(
            stroke="#262626",
            stroke_width=1.5,
            fill="lightgrey",
        )
    )
    tip_labels: bool = True
    use_edge_lengths: bool = False

@dataclass(repr=False)
class PhyloTreeStyle(TreeStyle):
    tree_style: str = 'p'
    layout: LayoutType = 'd'
    edge_type: EdgeType = 'c'
    edge_widths: Union[int, Iterable[int], str] = "Ne"  # special
    node_labels: bool = True
    node_sizes: int = 15
    node_hover: bool = False
    node_mask: bool = False
    node_style: NodeStyle = field(
        default_factory=lambda: NodeStyle(
            stroke="#262626",
            stroke_width=1.0,
        )
    )
    node_labels_style: NodeLabelStyle = field(
        default_factory=lambda: NodeLabelStyle(
            font_size=9,
        )
    )
    tip_labels: bool = True
    tip_labels_align: bool = False
    scale_bar: bool = True
    use_edge_lengths: bool = True

@dataclass(repr=False)
class UmlautTreeStyle(TreeStyle):
    tree_style: str = "o"
    edge_type: EdgeType = 'c'
    node_sizes: int = 8
    tip_labels: bool = True
    tip_labels_align: bool = True
    edge_style: EdgeStyle = field(
        default_factory=lambda: EdgeStyle(
            stroke='#262626',
            stroke_width=2,
        )
    )
    node_style: NodeStyle = field(
        default_factory=lambda: NodeStyle(
            stroke="white",
            stroke_width=1.5,
            fill='rgba(10.6%,62.0%,46.7%,1.000)',
        )
    )

@dataclass(repr=False)
class CoalTreeStyle(TreeStyle):
    tree_style: str = "c"
    edge_type: EdgeType = 'c'
    layout: LayoutType = 'd'
    scale_bar: bool = True
    node_sizes: int = 7
    node_mask: bool = False
    # tip_labels: str = "idx"
    tip_labels_style: TipLabelsStyle = field(
        default_factory=lambda: TipLabelsStyle(
            _toyplot_anchor_shift = 12,
        )
    )
    edge_style: EdgeStyle = field(
        default_factory=lambda: EdgeStyle(
            stroke='#262626',
            stroke_width=2,
        )
    )
    node_style: NodeStyle = field(
        default_factory=lambda: NodeStyle(
            stroke="#262626",
            stroke_width=1.5,
            fill='rgba(40.0%,76.1%,64.7%,1.000)',
        )
    )

@dataclass(repr=False)
class DarkTreeStyle(TreeStyle):
    tree_style: str = "d"
    tip_labels: bool = True
    tip_labels_style: TipLabelsStyle = field(
        default_factory=lambda: TipLabelsStyle(
            _toyplot_anchor_shift=8,
            fill='rgba(90.6%,54.1%,76.5%,1.000)'
        )
    )
    edge_style: EdgeStyle = field(
        default_factory=lambda: EdgeStyle(
            stroke='rgba(40.0%,76.1%,64.7%,1.000)',
            stroke_width=2,
        )
    )
    node_labels_style: NodeLabelStyle = field(
        default_factory=lambda: NodeLabelStyle(
            fill='rgba(98.8%,55.3%,38.4%,1.000)',
        )
    )
    node_style: NodeStyle = field(
        default_factory=lambda: NodeStyle(
            stroke=None,
            stroke_width=1.5,
            fill='rgba(40.0%,76.1%,64.7%,1.000)', #'white',
        )
    )



def get_tree_style(ts: str="n") -> TreeStyle:
    """
    Convenience function to return an initialized TreeStyle
    of a given builtin style.
    """
    ts = ts.lower()[0]
    style_dict = {
        "n": NormalTreeStyle(),
        "s": SimpleTreeStyle(),
        "p": PhyloTreeStyle(),
        "o": UmlautTreeStyle(),
        "c": CoalTreeStyle(),
        "d": DarkTreeStyle(),
    }
    return style_dict[ts]


if __name__ == "__main__":

    import toytree
    import numpy as np

    TREE = toytree.rtree.unittree(10)
    tstyle = NormalTreeStyle(
        node_labels="hi", #np.zeros(10),
        node_hover="yo",
        height=400,
        width=400,
        edge_type="c",
        node_sizes=np.zeros(5),
        node_colors=list(toyplot.color.Palette()),
        edge_colors='red',
    )
    tstyle = UmlautTreeStyle(node_colors='red')
    print(tstyle)
