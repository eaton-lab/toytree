#!/usr/bin/env python

"""
tree style dictionaries
"""

from toyplot import color


# GLOBALS
COLORS = [color.to_css(_) for _ in color.Palette()]
BLACK = color.black


class TreeStyle(dict):
    """
    Pre-configured tree_style objects for distinct tree plotting styles.

    "n" (normal) - phylogram on white
    "a" (admixture) - space for adding admixture edges
    "c" (coalescent) - cladogram with node idx labels
    "d" (dark) - like 'n' but light edge and axes colors for dark backgrounds

    To create custom TreeStyle dictionaries do the following:

    ts = toytree.style.TreeStyle()
    ts["tip_labels_color"] = "green"
    ts["node_size"] = 18

    tre = toytree.rtree.coaltree(8)
    tre.draw(tree_style=ts)

    """
    def __init__(self, tree_style='normal'):
    
        # allow user TreeStyles
        if isinstance(tree_style, TreeStyle):
            self["tree_style"] = "custom"
            self.update(tree_style)

        # load default styles
        else:
            self["tree_style"] = tree_style
            self["edge_type"] = None
            self["admixture"] = None
            self["height"] = None
            self["width"] = None

            self["orient"] = None
            self["node_labels"] = False
            self["node_size"] = None
            self["node_color"] = None

            self["vmarker"] = "o"
            self["node_hover"] = True
            self["use_edge_lengths"] = True
            self["tip_labels"] = True
            self["tip_labels_color"] = BLACK
            self["tip_labels_align"] = False

            ## substyles
            self["edge_style"] = dict()
            self["node_style"] = dict()
            self["edge_align_style"] = dict()
            self["node_labels_style"] = dict()
            self["tip_labels_style"] = dict()
            self["admix_edge_style"] = dict()

            ## axes styles
            self["axes"] = dict()

            ## fit styles
            self.set_default_styles()
            self.set_defined_style()


    def set_default_styles(self):

        self["edge_type"] = "p"
        self["orient"] = "right"

        self["tip_labels_style"]["fill"] = BLACK
        self["tip_labels_style"]["font-size"] = "12px"
        self["tip_labels_style"]["text-anchor"] = "start"
        self["tip_labels_style"]["-toyplot-anchor-shift"] = None

        # standard axes names args
        self["axes"]["show"] = True
        self["axes"]["padding"] = 20
        self["axes"]["x.show"] = True
        self["axes"]["x.ticks.show"] = True
        self["axes"]["x.ticks.labels.angle"] = 0
        self["axes"]["y.show"] = True
        self["axes"]["y.ticks.show"] = True
        self["axes"]["y.ticks.labels.angle"] = 0
        self["axes"]["y.domain.min"] = None
        self["axes"]["x.domain.min"] = None
        self["axes"]["y.domain.max"] = None
        self["axes"]["x.domain.max"] = None
        
        # non-standard axes name args
        self["axes"]["x_label_color"] = None
        self["axes"]["y_label_color"] = None
        # self["xticks"] = toyplot.locator.TickLocator()

        self["node_labels_style"]["fill"] = BLACK
        self["node_labels_style"]["font-size"] = "9px"

        self["admix_edge_style"]["stroke"] = COLORS[0]
        self["admix_edge_style"]["stroke_linecap"] = "round"
        self["admix_edge_style"]["stroke_dasharray"] = "2, 4"

        self["edge_style"]["stroke"] = BLACK
        self["edge_style"]["stroke-width"] = 2
        self["edge_style"]["stroke-linecap"] = "round"

        self["node_style"]["fill"] = COLORS[0]
        self["node_style"]["stroke"] = "none"

        self["edge_align_style"]["stroke"] = "darkgrey"
        self["edge_align_style"]["stroke-width"] = self["edge_style"]["stroke-width"]
        self["edge_align_style"]["stroke-linecap"] = "round"
        self["edge_align_style"]["stroke-dasharray"] = "2, 4"


    def set_defined_style(self):

        if self["tree_style"] in ("n", "normal"):
            self["orient"] = "right"
            self["use_edge_lengths"] = True
            self["tip_labels_align"] = False
            self["axes"]["show"] = False
            self["axes"]["padding"] = 20

        elif self["tree_style"] in ("c", "coal", "coalescent"):
            self["edge_type"] = "c"
            self["orient"] = "down"
            self["use_edge_lengths"] = True
            self["tip_labels_align"] = False
            self["node_labels"] = "idx"
            self["node_size"] = 15
            self["tip_labels"] = False
            self["axes"]["show"] = True
            self["axes"]["padding"] = 20
            self["axes"]["x.show"] = False
            self["axes"]["x.ticks.show"] = False
            self["axes"]["x.ticks.labels.angle"] = 0
            self["axes"]["y.show"] = True
            self["axes"]["y.ticks.show"] = True
            self["axes"]["y.ticks.labels.angle"] = -90
            self["axes"]["y.domain.min"] = 0

        if self["tree_style"] in ("d", "dark"):
            self["orient"] = "right"
            self["use_edge_lengths"] = True
            self["tip_labels_align"] = True
            self["tip_labels_color"] = COLORS[3]
            self["edge_style"]["stroke"] = COLORS[0]
            self["axes"]["show"] = False
            self["axes"]["padding"] = 20
            self["axes"]["x.show"] = True
            self["axes"]["x_label_color"] = COLORS[7]
            self["axes"]["y_label_color"] = COLORS[7]            

        if self["tree_style"] in ("m", "multi"):
            self["edge_type"] = "c"
            self["orient"] = "down"
            self["use_edge_lengths"] = True
            self["tip_labels_align"] = False
            self["node_labels"] = False
            self["node_size"] = 0
            self["tip_labels"] = False
            self["axes"]["show"] = False
            self["edge_style"]["opacity"] = 0.1
            self["tip_labels_style"]["-toyplot-anchor-shift"] = "15px"


    def update_mark(self, sdict):
        "update mark styles from dict"
        sdict = {i: j for i, j in sdict.items() if j is not None}
        for key, val in sdict.items():
            if isinstance(val, dict):
                if not isinstance(val, TreeStyle):
                    self[key].update(sdict[key])
            else:
                self[key] = val


    def update_axes(self, sdict):
        "add scale bar given orientation of tree and internal/external axes"

        if sdict["scalebar"]:
            if self["orient"] in ["right", "left"]:
                self["axes"]["show"] = True
                self["axes"]["x.show"] = True
                self["axes"]["y.show"] = False
                self["axes"]["padding"] = 10
                self["axes"]["x.ticks.show"] = True
                self["axes"]["y.ticks.show"] = False
                self["axes"]["y.ticks.labels.angle"] = 0
                self["axes"]["x.domain.max"] = 0
            else:
                self["axes"]["show"] = True
                self["axes"]["x.show"] = False
                self["axes"]["y.show"] = True
                self["axes"]["padding"] = 10
                self["axes"]["x.ticks.show"] = False
                self["axes"]["y.ticks.show"] = True
                self["axes"]["y.ticks.labels.angle"] = -90
                self["axes"]["y.domain.min"] = 0


                #locations = np.linspace()
                #self._x_tick_locator = toyplot.locator.Explicit(
                #    locations=locations, 
                #    format="{:.2f}")

        if sdict["padding"]:
            self["axes"]["padding"] = sdict["padding"]


    def update_canvas(self, sdict):
        sdict = {i: j for i, j in sdict.items() if j is not None}
        for key, val in sdict.items():
            if isinstance(val, dict):
                self[key].update(sdict[key])
            else:
                self[key] = val        