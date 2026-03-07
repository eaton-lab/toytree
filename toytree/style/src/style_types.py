#!/usr/bin/env python

"""Builtin one-letter tree style presets used by ``ToyTree.draw``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from toytree.style.src.style_base import TreeStyle
from toytree.utils import ToytreeError

TreeStyleKey = Literal["n", "s", "p", "o", "c", "d", "b", "u", "r"]


@dataclass(repr=False, eq=False)
class TreeStyleN(TreeStyle):
    """Normal baseline tree style."""

    tree_style: str = "n"


@dataclass(repr=False, eq=False)
class TreeStyleS(TreeStyle):
    """Simple style with large internal node markers and no edge lengths."""

    tree_style: str = "s"
    node_labels: bool = True
    node_mask: bool = False
    node_sizes: int = 16
    tip_labels: bool = True
    use_edge_lengths: bool = False

    def __post_init__(self):
        """Apply simple-style node marker defaults."""
        self.node_style.fill = (
            0.8274509803921568,
            0.8274509803921568,
            0.8274509803921568,
            1.0,
        )
        self.node_style.stroke = (0.145, 0.145, 0.145, 1.0)
        self.node_style.stroke_width = 1.5


@dataclass(repr=False, eq=False)
class TreeStyleP(TreeStyle):
    """Population-style preset with scale bar and mapped edge widths."""

    tree_style: str = "p"
    layout: str = "d"
    edge_type: Literal["c"] = "c"
    edge_widths: tuple[str, float, float, float] = ("Ne", 2, 6, 1.5)
    node_labels: bool = True
    node_sizes: int = 15
    node_hover: bool = False
    node_mask: bool = False
    tip_labels_align: bool = False
    scale_bar: bool = True

    def __post_init__(self):
        """Apply population-style marker and label tweaks."""
        self.node_style.stroke = (0.145, 0.145, 0.145, 1.0)
        self.node_style.stroke_width = 1.0
        self.node_labels_style.font_size = 9


@dataclass(repr=False, eq=False)
class TreeStyleO(TreeStyle):
    """Umlaut-style preset with aligned tip labels and circular markers."""

    tree_style: str = "o"
    edge_type: Literal["c"] = "c"
    node_sizes: int = 8
    tip_labels_align: bool = True

    def __post_init__(self):
        """Apply umlaut-style node and edge colors."""
        self.edge_style.stroke = (0.145, 0.145, 0.145, 1.0)
        self.edge_style.stroke_width = 2
        self.node_style.stroke = (1.0, 1.0, 1.0, 1.0)
        self.node_style.stroke_width = 1.5
        self.node_style.fill = (
            0.10588235294117647,
            0.6196078431372549,
            0.4666666666666667,
            1.0,
        )


@dataclass(repr=False, eq=False)
class TreeStyleC(TreeStyle):
    """Coalescent-style preset with downward layout and scale bar."""

    tree_style: str = "c"
    edge_type: Literal["c"] = "c"
    layout: str = "d"
    scale_bar: bool = True
    node_sizes: int = 7
    node_mask: bool = False

    def __post_init__(self):
        """Apply coalescent-style marker, tip-label, and edge defaults."""
        self.tip_labels_style.anchor_shift = 12
        self.edge_style.stroke = (0.145, 0.145, 0.145, 1.0)
        self.edge_style.stroke_width = 2
        self.node_style.stroke = (0.145, 0.145, 0.145, 1.0)
        self.node_style.stroke_width = 1.5
        self.node_style.fill = (0.4, 0.7607843137254902, 0.6470588235294118, 1.0)


@dataclass(repr=False, eq=False)
class TreeStyleR(TreeStyle):
    """R-style preset showing internal node names as labels."""

    tree_style: str = "r"
    node_mask: tuple[bool, bool, bool] = (False, True, True)
    node_colors: str = "lightgrey"
    node_markers: str = "r2x1"
    node_sizes: int = 16
    node_labels: str = "name"

    def __post_init__(self):
        """Apply R-style tip label sizing."""
        self.tip_labels_style.font_size = 14


@dataclass(repr=False, eq=False)
class TreeStyleB(TreeStyle):
    """Bootstrap-style preset mapping support to edge widths."""

    tree_style: str = "b"
    edge_widths: tuple[str, float, float, float] = ("support", 1.5, 4, 1.5)


@dataclass(repr=False, eq=False)
class TreeStyleD(TreeStyle):
    """Dark-style preset with high-contrast node and tip colors."""

    tree_style: str = "d"

    def __post_init__(self):
        """Apply dark-style colors and node stroke settings."""
        self.tip_labels_style.anchor_shift = 8
        self.tip_labels_style.fill = "rgba(90.6%,54.1%,76.5%,1.000)"
        self.edge_style.stroke = "rgba(40.0%,76.1%,64.7%,1.000)"
        self.edge_style.stroke_width = 2
        self.node_labels_style.fill = "rgba(98.8%,55.3%,38.4%,1.000)"
        self.node_style.stroke = None
        self.node_style.stroke_width = 1.5
        self.node_style.fill = "rgba(40.0%,76.1%,64.7%,1.000)"


@dataclass(repr=False, eq=False)
class TreeStyleU(TreeStyle):
    """Unrooted-style preset with topology-based layout and node labels."""

    tree_style: str = "u"
    layout: str = "unrooted"
    edge_type: Literal["c"] = "c"
    use_edge_lengths: bool = False
    node_colors: str = "white"
    node_sizes: int = 6
    node_labels: str = "idx"

    def __post_init__(self):
        """Apply unrooted-style node defaults."""
        self.node_style.stroke = None
        self.node_style.stroke_width = 1.5
        self.node_style.fill = "white"  # do not set defaults that override


def get_base_tree_style_by_name(
    tree_style: TreeStyleKey | str = "n",
) -> TreeStyle:
    """Return a builtin ``TreeStyle`` from a one-letter style key."""
    if not isinstance(tree_style, str):
        raise ToytreeError(
            "tree_style must be a string key. " f"Use one of: {', '.join(STYLE_DICTS)}."
        )
    key = tree_style.lower().strip()
    if key not in STYLE_DICTS:
        raise ToytreeError(
            f"tree_style '{tree_style}' not recognized. "
            f"Use one of: {', '.join(STYLE_DICTS)}."
        )
    style = STYLE_DICTS[key]
    return style()


STYLE_DICTS: dict[TreeStyleKey, type[TreeStyle]] = {
    "n": TreeStyleN,
    "s": TreeStyleS,
    "p": TreeStyleP,
    "o": TreeStyleO,
    "c": TreeStyleC,
    "d": TreeStyleD,
    "b": TreeStyleB,
    "u": TreeStyleU,
    "r": TreeStyleR,
}


if __name__ == "__main__":
    n = get_base_tree_style_by_name("n")
    c = get_base_tree_style_by_name("d")
    print(n.tip_labels_style.fill)
    print(c.tip_labels_style.fill)
