#!/usr/bin/env python

"""Builtin tree styles.

"""

from typing import Tuple, TypeVar
from dataclasses import dataclass
from toytree.style import TreeStyle

Color = TypeVar("Color")


@dataclass(repr=False, eq=False)
class TreeStyleN(TreeStyle):
    tree_style: str = "n"


@dataclass(repr=False, eq=False)
class TreeStyleS(TreeStyle):
    tree_style: str = "s"
    node_labels: bool = True
    node_mask: bool = False
    node_sizes: int = 16
    tip_labels: bool = True
    use_edge_lengths: bool = False

    def __post_init__(self):
        self.node_style.fill = (0.8274509803921568, 0.8274509803921568, 0.8274509803921568, 1.0)
        self.node_style.stroke = (0.145, 0.145, 0.145, 1.0)
        self.node_style.stroke_width = 1.5


@dataclass(repr=False, eq=False)
class TreeStyleP(TreeStyle):
    """Phylogeny tree_style ..."""
    tree_style: str = "p"
    layout: str = "d"
    edge_type: str = "c"
    edge_widths: Tuple[str] = ("Ne", 2, 6, 1.5)  # special
    node_labels: bool = True
    node_sizes: int = 15
    node_hover: int = False
    node_mask: int = False
    # tip_labels: bool = True
    tip_labels_align: bool = False
    scale_bar: bool = True

    def __post_init__(self):
        self.node_style.stroke = (0.145, 0.145, 0.145, 1.0)
        self.node_style.stroke_width = 1.0
        self.node_labels_style.font_size = 9


@dataclass(repr=False, eq=False)
class TreeStyleO(TreeStyle):
    """Umlaut style."""
    tree_style: str = "o"
    edge_type: str = "c"
    node_sizes: int = 8
    tip_labels_align: bool = True
    # tip_labels: bool = True

    def __post_init__(self):
        self.edge_style.stroke = (0.145, 0.145, 0.145, 1.0)
        self.edge_style.stroke_width = 2
        self.node_style.stroke = (1.0, 1.0, 1.0, 1.0)
        self.node_style.stroke_width = 1.5
        self.node_style.fill = (0.10588235294117647, 0.6196078431372549, 0.4666666666666667, 1.0)


@dataclass(repr=False, eq=False)
class TreeStyleC(TreeStyle):
    """Coalescent style."""
    tree_style: str = "c"
    edge_type: str = "c"
    layout: str = "d"
    scale_bar: bool = True
    node_sizes: int = 7
    node_mask: bool = False

    def __post_init__(self):
        self.tip_labels_style.anchor_shift = 12
        self.edge_style.stroke = (0.145, 0.145, 0.145, 1.0)
        self.edge_style.stroke_width = 2
        self.node_style.stroke = (0.145, 0.145, 0.145, 1.0)
        self.node_style.stroke_width = 1.5
        self.node_style.fill = (0.4, 0.7607843137254902, 0.6470588235294118, 1.0)


@dataclass(repr=False, eq=False)
class TreeStyleR(TreeStyle):
    """R style."""
    tree_style: str = "r"
    node_mask: Tuple[int, int, int] = (0, 1, 1)
    node_colors: Color = "lightgrey"
    node_markers: str = "r2x1"
    node_sizes: int = 16
    node_labels: str = "name"

    def __post_init__(self):
        self.tip_labels_style.font_size: int = 14


@dataclass(repr=False, eq=False)
class TreeStyleB(TreeStyle):
    """Bootstrap support style."""
    tree_style: str = "b"
    edge_widths: Tuple[str] = ("support", 1.5, 4, 1.5)
    # def __post_init__(self):
    #     pass


@dataclass(repr=False, eq=False)
class TreeStyleD(TreeStyle):
    """Dark style."""
    tree_style: str = "d"

    def __post_init__(self):
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
    """Unrooted style."""
    tree_style = "u"
    layout = "unrooted"
    use_edge_lengths = False
    node_colors = "white"
    node_sizes = 6
    node_labels = "idx"

    def __post_init__(self):
        self.node_style.stroke = None
        self.node_style.stroke_width = 1.5
        self.node_style.fill = "white"  # do not set defaults that override


def get_base_tree_style_by_name(tree_style: str = "n") -> TreeStyle:
    """Return a base TreeStyle indexed by unique str name prefix"""
    tree_style = tree_style.lower()[0]
    style = STYLE_DICTS[tree_style]
    return (style)()


STYLE_DICTS = {
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


    n = get_base_tree_style_by_name('n')
    c = get_base_tree_style_by_name('d')
    print(n.tip_labels_style.fill)
    print(c.tip_labels_style.fill)