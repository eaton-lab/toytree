#!/usr/bin/env python

"""...

Priority in color/opacity
-------------------------
1. color settings can take a single or multiple colors. If multiple
colors are entered then individual colors are assigned to each item,
but if only one then the color is set to None and a value will be set
to fill/stroke instead.
>>> color = [a, b, c, ...]

2. 
>>> fill/stroke = x


3. Color rgba value is the default opacity value used. But if user sets
teh 

"""

from __future__ import annotations
from typing import Union, Sequence, TypeVar, Tuple, Optional, Iterator, Any, List
from dataclasses import dataclass, field
from copy import deepcopy
from loguru import logger
from toytree.utils import ToytreeError

logger = logger.bind(name="toytree")
Color = TypeVar("Color")
ToyTree = TypeVar("ToyTree")


@dataclass(repr=False, init=True, eq=False)
class SubStyle:
    """A subclass of Style for CSS on markers."""

    def __delattr__(self, key) -> None:
        raise ToytreeError("TreeStyle dict keys cannot be deleted.")

    def __repr__(self):
        """Return a serialized JSON formatted style dict."""
        block = ["{"]
        for key, val in self.__dict__.items():
            block.append(f"    {key}: {val!r},")
        block.append("}")
        return "\n".join(block)

    def __getitem__(self, key):
        """Get item using Python name, fetch from dict as CSS name."""
        if "-" in key:
            if key == "-toyplot-anchor-shift":
                key = "anchor_shift"
            else:
                key = key.replace("-", "_")
        return self.__dict__[key]

    def __setitem__(self, key, value):
        """Set item using Python name, set to dict as CSS name."""
        if "-" in key:
            if key == "-toyplot-anchor-shift":
                key = "anchor_shift"
            else:
                key = key.replace("-", "_")
        self.__dict__[key] = value

    def copy(self) -> SubStyle:
        """Return a deepcopy."""
        return deepcopy(self)


@dataclass(repr=False, init=True, eq=False)
class NodeStyle(SubStyle):
    fill: Color = (0.4, 0.7607843137254902, 0.6470588235294118, 1.0)
    fill_opacity: float = None
    stroke: Color = "#262626"
    stroke_width: float = 1.5
    stroke_opacity: float = None


@dataclass(repr=False, init=True, eq=False)
class NodeLabelStyle(SubStyle):
    fill: Color = (0.145, 0.145, 0.145, 1.0)
    fill_opacity: float = 1.0
    font_size: Union[int, str] = 9
    font_weight: int = 300
    font_family: str = "Helvetica"
    anchor_shift: Union[str, int] = 0
    baseline_shift: Union[str, int] = 0
    text_anchor: str = "middle"


@dataclass(repr=False, init=True, eq=False)
class EdgeStyle(SubStyle):
    stroke: Color = (0.145, 0.145, 0.145, 1.0)
    stroke_width: float = 2.0
    stroke_opacity: Optional[float] = None
    stroke_linecap: str = "round"
    stroke_dasharray: Optional[str] = None


@dataclass(repr=False, init=True, eq=False)
class EdgeAlignStyle(SubStyle):
    stroke: Color = (0.66, 0.66, 0.66, 1)
    stroke_width: int = 2
    stroke_opacity: Optional[float] = 0.75
    stroke_linecap: str = "round"
    stroke_dasharray: str = "2,4"


@dataclass(repr=False, init=True, eq=False)
class TipLabelStyle(SubStyle):
    fill: Color = (0.145, 0.145, 0.145, 1.0)
    fill_opacity: Optional[float] = None
    font_size: Union[str, float] = 12
    font_weight: int = 300
    font_family: str = "Helvetica"
    anchor_shift: Union[str, float] = 15
    baseline_shift: Union[str, int] = 0
    text_anchor: str = "start"


@dataclass(repr=False, init=True, eq=False)
class TreeStyle:
    """The base tree style on top of which other tree_styles are defined."""
    tree_style: str = None
    """: A tree_style name to set a base style."""
    height: int = None
    """: Canvas height in px units."""
    width: int = None
    """: Canvas width in px units."""
    layout: str = "r"
    """: Tree layout method name for projecting tree in coordinate space."""
    edge_type: str = "p"
    """: Edge type defines straight, diagonal, or curved edges."""
    edge_colors: Union[Color, Sequence[Color], Tuple[str]] = None
    """: Edges can be all the same or different colors."""
    edge_widths: Union[float, Sequence[float], Tuple[str]] = None
    """: Edges can be all the same or different widths in px units."""

    node_mask: Union[bool, Sequence[bool], Tuple[int, int, int]] = None
    """: Node labels are str plotted on top of Node markers."""
    node_colors: Union[Color, Sequence[Color], Tuple[str]] = None
    """: Node colors can set different 'fill' to Node markers."""
    node_sizes: Union[float, Sequence[float], Tuple[str]] = 0.0
    """: Node sizes can set different size to Node markers."""
    node_markers: Union[str, Sequence[str]] = "o"
    """: Node markers define the shape of Node markers."""
    node_hover: Union[bool, str, Sequence[str]] = None
    """: Node hover creates a tooltip for interactive data inspection."""
    node_labels: Union[bool, str, Sequence[str], Tuple[str]] = False
    """: Node labels are str plotted on top of Node markers."""
    node_as_edge_data: bool = False
    """: Node markers and labels are shown as edge markers and labels."""

    tip_labels: Union[bool, Sequence[str], Tuple[str]] = True
    """: Tip labels are str plotted below leaf Node markers."""
    tip_labels_colors: Union[Color, Sequence[Color], Tuple[str]] = None
    """: Tip labels colors can be same or different for each tip."""
    tip_labels_angles: Union[float, Sequence[float]] = None
    """: Tip labels angles can be set but are usually auto-generated."""
    tip_labels_align: bool = None
    """: Align tip labels at farthest Node from root."""

    edge_style: EdgeStyle = field(default_factory=EdgeStyle)
    """: SubStyle dict for setting edge width, stroke, etc."""
    node_style: NodeStyle = field(default_factory=NodeStyle)
    """: SubStyle dict for setting Node fill, stroke, opacity, etc."""
    node_labels_style: NodeLabelStyle = field(default_factory=NodeLabelStyle)
    """: SubStyle dict for setting Node label font, size, fill, etc."""
    tip_labels_style: TipLabelStyle = field(default_factory=TipLabelStyle)
    """: SubStyle dict for setting Tip label font, size, fill, etc."""
    edge_align_style: EdgeAlignStyle = field(default_factory=EdgeAlignStyle)
    """: SubStyle dict for setting Aligned tip labels edges stroke, etc."""

    # self.show_root_edge: bool = None
    use_edge_lengths: bool = True
    """: Plot topology with transformed edge lengths for easier viewing."""
    scale_bar: Union[bool, float] = False
    """: Modify Cartesian axes to show scale in 'dist' feature units."""
    padding: float = 15.0
    """: Modify Cartesian axes to set padding between Mark and axes in px units."""
    xbaseline: float = 0.0
    """: Shift tree on Cartesian axes so Node 0 is at (xbaseline, ybaseline)."""
    ybaseline: float = 0.0
    """: Shift tree on Cartesian axes so Node 0 is at (xbaseline, ybaseline)."""
    shrink: float = 0.0
    """: Add additional space to fit tip names relative to tree."""
    admixture_edges: List[Tuple] = None

    def __repr__(self):
        """Return a serialized JSON formatted style dict."""
        block = ["{"]
        for key, val in self.__dict__.items():
            if isinstance(val, SubStyle):
                block.append(f"{key}: {val!r},")
            else:
                block.append(f"{key}: {val!r},")
        block.append("}")
        return "\n".join(block)

    def __iter__(self) -> Iterator[str]:
        """ToyTree is iterable, returning Nodes in idx order."""
        return (i for i in self.__dict__)

    def _items(self) -> Iterator[Tuple[str, Any]]:
        return ((i, j) for i, j in self.__dict__.items())

    def copy(self) -> TreeStyle:
        """Return a deepcopy."""
        return deepcopy(self)


if __name__ == "__main__":

    ts = TreeStyle()

    ts.tip_labels_style.font_size = 15
    ts.tip_labels_style["font_size"] = 16
    ts.tip_labels_style["font-size"] = 17

    print(ts.tip_labels_style)
    print(ts.tip_labels_style.font_size)
