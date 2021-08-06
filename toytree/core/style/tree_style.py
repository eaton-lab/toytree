#!/usr/bin/env python

"""
Tree Styles checked and expanded at .draw() or repr().

Usage
-----
> toytree.tree(...)                   # DefaultTreeStyle() init
> tree.draw(**kwargs)                 # dict or user args
> style = DefaultTreeStyle(**kwargs)  # DefaultTreeStyle(**dict, **tree.style)
"""

from typing import List, Tuple, Optional, Union, Iterable, Dict
import json
from enum import Enum
from dataclasses import dataclass, asdict, field
import toyplot
from loguru import logger
import numpy as np
import pandas as pd
from toytree.core.style.color import ToyColor, Color
from toytree.utils.exceptions import ToytreeError


COLORS1 = list(
    map(toyplot.color.to_css, toyplot.color.brewer.palette("Set2")))
COLORS2 = list(
    map(toyplot.color.to_css, toyplot.color.brewer.palette("Dark2")))
BLACK = toyplot.color.black


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
class EdgeStyle(SubStyle):
    stroke: Color = 'rgba(16.1%,15.3%,14.1%,1.000)'
    stroke_width: float = 2.
    stroke_linecap: str = "round"  # pydantic alias="stroke-linecap"
    stroke_opacity: float = 1.
    # stroke_dasharray: str = "2,4"

@dataclass
class NodeStyle(SubStyle):
    fill: Color = 'rgba(40.0%,76.1%,64.7%,1.000)'
    stroke: Optional[Color] = None
    stroke_width: float = 1.0

@dataclass
class NodeLabelStyle(SubStyle):
    fill: Color = 'rgba(16.1%,15.3%,14.1%,1.000)'
    font_size: Union[int, str] = "11px"
    font_weight: int = 300
    _toyplot_anchor_shift: Union[str, int] = 0
    baseline_shift: Union[str,int] = 0

@dataclass
class EdgeAlignStyle(SubStyle):
    stroke: Color = 'rgba(66.3%,66.3%,66.3%,1.000)'
    stroke_width: int = 2
    stroke_linecap: str = "round"
    stroke_dasharray: str = "2,4"

@dataclass
class TipLabelsStyle(SubStyle):
    fill: Color = 'rgba(16.1%,15.3%,14.1%,1.000)'
    fill_opacity: Union[str, float] = 1.0
    font_size: Union[str, float] = 11
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
    node_labels: Union[bool, str, Iterable[str]] = False
    node_colors: Union[Color, Iterable[Color], None] = None  # override by fill
    node_sizes: Union[int, Iterable[int]] = 0
    node_markers: Union[str, Iterable[str]] = "o"
    node_hover: Union[bool, str, Iterable[str]] = None  # None = auto
    node_style: NodeStyle = field(default_factory=NodeStyle)
    node_labels_style: NodeLabelStyle = field(default_factory=NodeLabelStyle)

    tip_labels: Union[bool, Iterable[str]] = True
    tip_labels_colors: Union[str, Iterable[str], None] = None
    tip_labels_align: bool = False
    tip_labels_style: TipLabelsStyle = field(default_factory=TipLabelsStyle)
    tip_labels_angles: Union[float, Iterable[float], None] = None

    use_edge_lengths: bool = True
    scalebar: bool = False
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
        """
        self.tree = tree  # ignore
        self._validate_node_colors()
        self._validate_node_mask()
        self._validate_node_sizes()
        self._validate_node_markers()
        self._validate_node_labels()
        self._validate_node_hover()
        self._validate_node_style()

        self._validate_tip_labels()
        self._validate_tip_labels_colors()
        self._validate_tip_labels_angles()        

    def _serialize_colors(self):
        """
        Convert all ndarrays to lists for serialization of JSON.
        """
        self._validate_node_colors()
        self._validate_tip_labels_colors()
        # ... substyledicts

    def _serialize_css_styles(self):
        """
        Convert keys with lower_casendarrays to lists for serialization of JSON.
        """
        self._validate_node_colors()
        self._validate_tip_labels_colors()
        # ... substyledicts

    def _serialize_arrays(self):
        """
        Convert any ndarray inputs to lists for more reliable type
        checking without having to array dtypes, etc.
        TODO: could check shape and type here while they are arrays,
        but problem is we don't know for sure they will be arrays...
        so should we cast everything to an array, and then
        optionally back to list again for serial? Check the Mark
        to see if it actually benefits from arrays?
        """
        arrayed = [
            "node_mask",
            "node_sizes",
            "node_labels",
            "tip_labels",
        ]
        for key in arrayed:
            values = getattr(self, key)
            if isinstance(values, np.ndarray):
                setattr(self, key, values.tolist())
            elif isinstance(values, pd.DataFrame):
                setattr(self, key, values.iloc[:, 0].tolist())
            elif isinstance(values, pd.Series):
                setattr(self, key, values.tolist())

    def _validate_node_colors(self):
        """
        Sets node_colors to ndarray[str] or None, and sets
        node_style.fill to None or single color value.
        """
        # parse as a single color
        if self.node_colors is None:
            return
        try:
            css_color = ToyColor(self.node_colors).css
            self.node_colors = None
            self.node_style.fill = css_color
        except ToytreeError:
            # TODO: could expand a color map here?
            self.node_style.fill = None
            self.node_colors = toyplot.broadcast.pyobject(
                [ToyColor(i).css for i in self.node_colors],
                self.tree.nnodes,
            ).astype(str)

    def _validate_node_mask(self):
        """
        Sets node_mask to ndarray[bool].
            None: special to hide tips only
            True: show all
            False: hide all
            Iterable: custom
        """
        if self.node_mask in [True, False]:
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
            self.node_hover = [str(i) for i in range(self.tree.nnodes)]
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
        if self.node_style.stroke is not None:
            self.node_style.stoke = ToyColor(self.node_style.stroke).css
        if self.node_style.fill is not None:
            self.node_style.fill = ToyColor(self.node_style.fill).css

    def _validate_tip_labels_colors(self):
        """
        Sets tip_labels_colors to ndarray[str] or None, and sets
        tip_labels.style.fill to None or single color.
        """
        if self.tip_labels_colors is None:
            return
        try:
            css_color = ToyColor(self.tip_labels_colors).css
            self.tip_labels_colors = None
            self.tip_labels_style.fill = css_color
        except ToytreeError:
            self.tip_labels_style.fill = None
            self.tip_labels_colors = toyplot.broadcast.pyobject(
                [ToyColor(i).css for i in self.tip_labels_colors],
                self.tree.ntips,
            ).astype(str)

    def _validate_tip_labels(self):
        """
        Expand tip labels to a list of strings of len=ntips.
        """
        if self.tip_labels is True:
            self.tip_labels = np.array(self.tree.get_tip_labels())
        elif self.tip_labels is False:
            self.tip_labels = None
        else:
            self.tip_labels = toyplot.broadcast.pyobject(
                self.tip_labels, self.tree.ntips).astype(str)

    def _validate_tip_labels_angles(self):
        """
        sets tip_labels_angles to ndarray[float]. None is auto layout.
        """
        if self.tip_labels_angles is None:
            if self.layout == 'c':
                # tip_radians = np.linspace(0, -np.pi * 2, self.tree.ntips + 1)[:-1]
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
        if serialize_arrays:
            self._serialize_arrays()
        if serialize_colors:
            self._serialize_colors()
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
    node_sizes: int = 15

@dataclass(repr=False)
class SimpleTreeStyle(TreeStyle):
    tree_style: str = 's'
    layout: LayoutType = "r"
    node_labels: bool = True
    node_sizes: int = 15
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
    node_style: NodeStyle = field(
        default_factory=lambda: NodeStyle(
            stroke="#262626",
            stroke_width=1.0,
        )
    )
    tip_labels: bool = True
    tip_labels_align: bool = False
    scalebar: bool = True
    use_edge_lengths: bool = True

@dataclass(repr=False)
class UmlautTreeStyle(TreeStyle):
    tree_style: str = "o"
    edge_type: EdgeType = 'c'
    layout: LayoutType = 'r'
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

def get_tree_style(ts: str="n") -> TreeStyle:
    """
    Convenience function to return an initialized TreeStyle
    of a given builtin style.
    """
    ts = ts.lower()[0]
    style_dict = {
        "n": NormalTreeStyle(),
        "p": PhyloTreeStyle(),
        "o": UmlautTreeStyle(),
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
