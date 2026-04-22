#!/usr/bin/env python

"""Classes defining default and built-in tree drawing styles."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Literal,
    Sequence,
    TypeAlias,
    TypeVar,
)

from toytree.utils import ToytreeError

if TYPE_CHECKING:
    from toytree.network.src.parse_network import AdmixtureEvent
else:
    AdmixtureEvent = Any

Color = TypeVar("Color")
ToyTree = TypeVar("ToyTree")
Numeric: TypeAlias = int | float
NodeMask: TypeAlias = bool | Sequence[bool] | tuple[bool, bool, bool]
LabelArg: TypeAlias = bool | str | Sequence[Any] | tuple[str, Any]
RangeMapArg: TypeAlias = (
    str
    | tuple[str]
    | tuple[str, Numeric]
    | tuple[str, Numeric, Numeric]
    | tuple[str, Numeric, Numeric, Numeric]
)
ColorMapArg: TypeAlias = (
    str
    | tuple[str]
    | tuple[str, Any]
    | tuple[str, Any, Numeric]
    | tuple[str, Any, Numeric, Numeric]
    | tuple[str, Any, Numeric, Numeric, Numeric]
)
AdmixtureTupleArg: TypeAlias = tuple[Any, ...]
AdmixtureArg: TypeAlias = (
    AdmixtureEvent
    | AdmixtureTupleArg
    | Sequence[AdmixtureEvent | AdmixtureTupleArg]
    | None
)
DashArrayArg: TypeAlias = str | tuple[int | float, int | float] | None


@dataclass(repr=False, init=True, eq=False)
class SubStyle:
    """A subclass of Style for CSS on markers."""

    _ALIASES: ClassVar[dict[str, str]] = {
        "-toyplot-anchor-shift": "anchor_shift",
        "anchor-shift": "anchor_shift",
    }

    @classmethod
    def _normalize_key(cls, key: str) -> str:
        """Return a canonical style key name."""
        key = cls._ALIASES.get(key, key)
        return key.replace("-", "_")

    @classmethod
    def _allowed_keys(cls) -> set[str]:
        """Return supported style keys for this dataclass style object."""
        return set(getattr(cls, "__dataclass_fields__", {}))

    @classmethod
    def _raise_invalid_key(cls, key: str) -> None:
        """Raise a consistent error for unsupported style keys."""
        allowed = ", ".join(sorted(i.replace("_", "-") for i in cls._allowed_keys()))
        raise ToytreeError(
            f"Unsupported style key '{key}' for {cls.__name__}. "
            f"Allowed keys: {allowed}."
        )

    def __delattr__(self, key) -> None:
        """Do not allow deleting TreeStyle defaults."""
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
        key = self._normalize_key(key)
        if key not in self._allowed_keys():
            self._raise_invalid_key(key)
        return self.__dict__[key]

    def __setitem__(self, key, value):
        """Set item using Python name, set to dict as CSS name."""
        setattr(self, key, value)

    def __setattr__(self, key, value) -> None:
        """Allow only declared style keys and private internals."""
        if key.startswith("_"):
            object.__setattr__(self, key, value)
            return
        nkey = self._normalize_key(key)
        if nkey not in self._allowed_keys():
            self._raise_invalid_key(key)
        object.__setattr__(self, nkey, value)

    def copy(self) -> SubStyle:
        """Return a deepcopy."""
        return deepcopy(self)


@dataclass(repr=False, init=True, eq=False)
class NodeStyle(SubStyle):
    """Style fields for node marker rendering."""

    fill: Color = (0.4, 0.7607843137254902, 0.6470588235294118, 1.0)
    fill_opacity: float | None = None
    stroke: Color = "#262626"
    stroke_width: float = 1.5
    stroke_opacity: float | None = None
    stroke_linecap: Literal["round", "butt", "square"] | None = None
    stroke_linejoin: Literal["miter", "round", "bevel"] | None = None
    stroke_dasharray: DashArrayArg = None
    opacity: float | None = None


@dataclass(repr=False, init=True, eq=False)
class NodeLabelStyle(SubStyle):
    """Style fields for node label text rendering."""

    fill: Color = (0.145, 0.145, 0.145, 1.0)
    fill_opacity: float | None = 1.0
    stroke: Color | None = None
    stroke_opacity: float | None = None
    stroke_width: float | None = None
    font_size: int | str = 9
    font_weight: int = 300
    font_family: str = "Helvetica"
    anchor_shift: str | int | float = 0
    baseline_shift: str | int | float = 0
    text_anchor: str = "middle"
    opacity: float | None = None


@dataclass(repr=False, init=True, eq=False)
class EdgeStyle(SubStyle):
    """Style fields for tree edge path rendering."""

    stroke: Color = (0.145, 0.145, 0.145, 1.0)
    stroke_width: float = 2.0
    stroke_opacity: float | None = None
    stroke_linecap: Literal["round", "butt", "square"] = "round"
    stroke_linejoin: Literal["miter", "round", "bevel"] = "round"
    stroke_dasharray: DashArrayArg = None
    opacity: float | None = None


@dataclass(repr=False, init=True, eq=False)
class EdgeAlignStyle(SubStyle):
    """Style fields for optional tip-align guide edges."""

    stroke: Color = (0.66, 0.66, 0.66, 1)
    stroke_width: int = 2
    stroke_opacity: float | None = 0.75
    stroke_linecap: Literal["round", "butt", "square"] = "round"
    stroke_linejoin: Literal["miter", "round", "bevel"] = "round"
    stroke_dasharray: DashArrayArg = "2,4"
    opacity: float | None = None


@dataclass(repr=False, init=True, eq=False)
class TipLabelStyle(SubStyle):
    """Style fields for tip label text rendering."""

    fill: Color = (0.145, 0.145, 0.145, 1.0)
    fill_opacity: float | None = None
    stroke: Color | None = None
    stroke_opacity: float | None = None
    stroke_width: float | None = None
    font_size: str | float = 12
    font_weight: int = 300
    font_family: str = "Helvetica"
    anchor_shift: str | float = 15
    baseline_shift: str | int | float = 0
    text_anchor: str = "start"
    opacity: float | None = None


@dataclass(repr=False, init=True, eq=False)
class TreeStyle:
    """The base tree style on top of which other tree_styles are defined."""

    tree_style: str | None = None
    """: A tree_style name to set a base style."""
    height: int | None = None
    """: Canvas height in px units."""
    width: int | None = None
    """: Canvas width in px units."""
    layout: str = "r"
    """: Tree layout method name for projecting tree in coordinate space."""
    edge_type: Literal["p", "c", "b"] = "p"
    """: Edge type defines straight, diagonal, or curved edges."""
    edge_colors: Color | Sequence[Color] | ColorMapArg | None = None
    """: Edges can be all the same or different colors."""
    edge_widths: Numeric | Sequence[Numeric] | RangeMapArg | None = None
    """: Edges can be all the same or different widths in px units."""

    node_mask: NodeMask | None = None
    """: Node labels are str plotted on top of Node markers."""
    node_colors: Color | Sequence[Color] | ColorMapArg | None = None
    """: Node colors can set different 'fill' to Node markers."""
    node_sizes: Numeric | Sequence[Numeric] | RangeMapArg | None = 0.0
    """: Node sizes can set different size to Node markers."""
    node_markers: str | Sequence[Any] = "o"
    """: Node markers define the shape of Node markers."""
    node_hover: bool | str | Sequence[str] | None = None
    """: Node hover creates a tooltip for interactive data inspection."""
    node_labels: LabelArg | None = False
    """: Node labels are str plotted on top of Node markers."""
    node_as_edge_data: bool = False
    """: Node markers and labels are shown as edge markers and labels."""

    tip_labels: LabelArg | None = True
    """: Tip labels are str plotted below leaf Node markers."""
    tip_labels_colors: Color | Sequence[Color] | ColorMapArg | None = None
    """: Tip labels colors can be same or different for each tip."""
    tip_labels_angles: Numeric | Sequence[Numeric] | None = None
    """: Tip labels angles can be set but are usually auto-generated."""
    tip_labels_align: bool | None = None
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

    use_edge_lengths: bool = True
    """: Plot topology with transformed edge lengths for easier viewing."""
    scale_bar: bool | int | float = False
    """: Modify Cartesian axes to show scale in 'dist' feature units."""
    padding: int | float = 15
    """: Increase Canvas space around the drawing edges in px units."""
    xbaseline: int | float = 0
    """: Shift the tree horizontally by this many px units."""
    ybaseline: int | float = 0
    """: Shift the tree vertically by this many px units."""
    admixture_edges: AdmixtureArg = None
    """: Optional admixture edge specs rendered with the tree."""

    def copy(self) -> TreeStyle:
        """Return a deepcopy."""
        return deepcopy(self)


if __name__ == "__main__":
    ts = TreeStyle()
    print(ts)
