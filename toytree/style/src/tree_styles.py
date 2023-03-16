#!/usr/bin/env python

"""...

"""

from toytree.style import TreeStyle


class TreeStyleN(TreeStyle):
    """Normal style."""

    def __init__(self):
        super().__init__()
        self.tree_style: str = "n"


class TreeStyleS(TreeStyle):
    """Simple style."""

    def __init__(self):
        super().__init__()
        self.tree_style = "s"
        self.node_labels = True
        self.node_mask = False
        self.node_sizes = 18
        self.node_style.stroke = "#262626"
        self.node_style.stroke_width = 1.5
        self.node_style.fill = "lightgrey"
        self.tip_labels = True
        self.use_edge_lengths = False


class TreeStyleP(TreeStyle):
    """Phylogeny style."""

    def __init__(self):
        super().__init__()
        self.tree_style = "p"
        self.layout = "d"
        self.edge_type = "c"
        self.edge_widths = ("Ne", 2, 10, 5)  # special
        self.node_labels = True
        self.node_sizes = 15
        self.node_hover = False
        self.node_mask = False
        self.node_style.stroke = "#262626"
        self.node_style.stroke_width = 1.0
        self.node_labels_style.font_size = 9
        self.tip_labels = True
        self.tip_labels_align = False
        self.scale_bar = True
        self.use_edge_lengths = True


class TreeStyleO(TreeStyle):
    """Umlaut style."""

    def __init__(self):
        super().__init__()
        self.tree_style = "o"
        self.edge_type = "c"
        self.node_sizes = 8
        self.tip_labels = True
        self.tip_labels_align = True
        self.edge_style.stroke = "#262626"
        self.edge_style.stroke_width = 2
        self.node_style.stroke = "white"
        self.node_style.stroke_width = 1.5
        self.node_style.fill = "rgba(10.6%,62.0%,46.7%,1.000)"


class TreeStyleC(TreeStyle):
    """Coalescent style."""

    def __init__(self):
        super().__init__()
        self.tree_style = "c"
        self.edge_type = "c"
        self.layout = "d"
        self.scale_bar = True
        self.node_sizes = 7
        self.node_mask = False
        # tip_labels: str = "idx"
        self.tip_labels_style._toyplot_anchor_shift = 12
        self.edge_style.stroke = "#262626"
        self.edge_style.stroke_width = 2
        self.node_style.stroke = "#262626"
        self.node_style.stroke_width = 1.5
        self.node_style.fill = "rgba(40.0%,76.1%,64.7%,1.000)"


class TreeStyleD(TreeStyle):
    """Dark style."""

    def __init__(self):
        super().__init__()
        self.tree_style = "d"
        self.tip_labels = True
        self.tip_labels_style._toyplot_anchor_shift = 8
        self.tip_labels_style.fill = "rgba(90.6%,54.1%,76.5%,1.000)"
        self.edge_style.stroke = "rgba(40.0%,76.1%,64.7%,1.000)"
        self.edge_style.stroke_width = 2
        self.node_labels_style.fill = "rgba(98.8%,55.3%,38.4%,1.000)"
        self.node_style.stroke = None
        self.node_style.stroke_width = 1.5
        self.node_style.fill = "rgba(40.0%,76.1%,64.7%,1.000)"


class TreeStyleU(TreeStyle):
    """Unrooted style."""

    def __init__(self):
        super().__init__()
        self.tree_style = "u"
        self.layout = "unrooted"
        self.use_edge_lengths = False
        self.node_style.stroke = None
        self.node_style.stroke_width = 1.5
        self.node_colors = "white"
        # self.node_style.fill = "white" # do not set defaults that override
        self.node_sizes = 6
        self.node_labels = "idx"


# class TreeStyleB(TreeStyle):
#     """Bootstrap style. Edge widths and node colors map to support."""

#     def __init__(self):
#         super().__init__()
#         self.tree_style = "b"


class TreeStyleR(TreeStyle):
    """Node name style. Mask tip Nodes and increase font size."""
    def __init__(self):
        super().__init__()
        self.tree_style = "x"
        self.node_mask = (0, 1, 1)
        self.node_labels = "name"
        self.node_sizes = 16
        self.node_markers = "r2x1"
        self.node_colors = "lightgrey"


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
    "u": TreeStyleU,
}

if __name__ == "__main__":

    ts = get_base_tree_style_by_name("s")
    print(ts)
