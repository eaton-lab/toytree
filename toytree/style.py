#!/usr/bin/env python

"""
tree style dictionaries
"""

import toyplot


# GLOBALS
COLORS = [toyplot.color.to_css(i) for i in toyplot.color.Palette()]
BLACK = toyplot.color.to_css(toyplot.color.black)


class EdgeStyle(dict):
    pass 

class NodeStyle(dict):
    pass

class EdgeAlignStyle(dict):
    pass

class AdmixEdgeStyle(dict):
    pass

class NodeLabelsStyle(dict):
    pass

class TipLabelsStyle(dict):
    pass

class AxesStyle(dict):
    pass


class TreeStyle(object):

    def __init__(self, style='p'):
    
        self.style = style
        self.admixture = None
        self.orient = None
        self.node_size = None
        self.node_color = None
        self.node_hover = None
        self.vmarker = "o"
        self.use_edge_lengths = True        
        self.tip_labels = True
        self.tip_labels_color = BLACK
        self.tip_labels_align = False

        ## substyles
        self.edge_style = EdgeStyle()
        self.node_style = NodeStyle()
        self.edge_align_style = EdgeAlignStyle()
        self.node_labels_style = NodeLabelsStyle()
        self.tip_labels_style = TipLabelsStyle()
        self.admix_edge_style = AdmixEdgeStyle()

        ## axes styles
        self.axes = AxesStyle()

        ## fit styles
        self.set_default_styles()
        self.set_defined_style()


    def set_default_styles(self):
        self.tip_labels_style['fill'] = BLACK
        self.tip_labels_style['font-size'] = "12px"
        self.tip_labels_style['text-anchor'] = "start"
        self.tip_labels_style['-toyplot-anchor-shift'] = None

        self.axes["show"] = True
        self.axes["x.show"] = True
        self.axes["y.show"] = True
        self.axes["padding"] = 20
        self.axes["x.ticks.show"] = True
        self.axes["y.ticks.show"] = True
        self.axes["y.ticks.labels.angle"] = -90
        # self.xticks = toyplot.locator.TickLocator()

        self.node_labels_style["fill"] = BLACK  # "#262626"
        self.node_labels_style["font_size"] = "9px"

        self.admix_edge_style["stroke"] = COLORS[0]
        self.admix_edge_style["stroke_linecap"] = "round"
        self.admix_edge_style["stroke_dasharray"] = "2, 4"

        self.edge_style["stroke"] = BLACK
        self.edge_style["stroke-width"] = 2
        self.edge_style["stroke-linecap"] = "round"

        self.node_style["fill"] = COLORS[0]
        self.node_style["stroke"] = "none"

        self.edge_align_style["stroke"] = "darkgrey"
        self.edge_align_style["stroke-linecap"] = "round"
        self.edge_align_style["stroke-dasharray"] = "2, 4"
        self.edge_align_style["width"] = self.edge_style["width"]


    @property
    def stroke_width(self):
        return 8



    def set_defined_style(self):
        if self.style in "phylogram":
            self.orient = "right"
            self.use_edge_lengths = True
            self.tip_labels_align = False


        elif self.style in "coalescent":
            self.orient = "down"
            self.use_edge_lengths = True
            self.tip_labels_align = False
            self.node_labels = "idx"
            self.tip_labels = False

            self.axes["show"] = True
            self.axes["x.show"] = False
            self.axes["y.show"] = True
            self.axes["padding"] = 20
            self.axes["x.ticks.show"] = False
            self.axes["y.ticks.show"] = True
            self.axes["y.ticks.labels.angle"] = -90
