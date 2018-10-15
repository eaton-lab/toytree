#!/usr/bin/env python

"""
tree style dictionaries
"""

from toyplot import color


# GLOBALS
COLORS = [color.to_css(i) for i in color.Palette()]
BLACK = color.black



class TreeStyle:
    def __init__(self, tree_style='n'):
        """
        TreeStyle object used to store tree plotting configurations.
        """
        # set default
        self.tree_style = tree_style
        self.edge_type = 'p'
        self.height = None
        self.width = None
        self.orient = 'right'
        self.node_labels = False
        self.node_size = None
        self.node_color = None
        self.vmarker = "o"
        self.node_hover = True
        self.use_edge_lengths = True
        self.tip_labels = True
        self.tip_labels_color = BLACK
        self.tip_labels_align = False
        self.tip_labels_space = None
        self.scalebar = False
        self.padding = 20

        # substyles with default 'normal' styling
        self.edge_style = EdgeStyle()
        self.node_style = NodeStyle()
        self.edge_align_style = EdgeAlignStyle()
        self.node_labels_style = NodeLabelStyle()
        self.tip_labels_style = TipLabelStyle()
        # self.axes_style = AxesStyle()
        #self.admix_edge_style = AdmixEdgeStyle()
        # override defaults with built-in styles


    def __repr__(self):
        "returns an indented dictionary and subdict print"
        view = []
        for (i, j) in self.__dict__.items():
            if not hasattr(j, '_t'):
                view.append("{}: {}".format(i, j))
            else:
                view.append("{}:".format(i))
                for (k, v) in j.__dict__.items():
                    if k != "_t":
                        view.append("    {}: {}".format(k, v))
        return "\n".join(view)


    def __str__(self):
        "returns same as __repr__"
        return self.__repr__()


    # def _update_from_tree_style(self):
    #     "update this styledict with another styledict or a built-in"
    #     # built-in type
    #     if self.tree_style in ("c", "coal"):
    #         self._update_from_dict(coal.__dict__)
    #     elif self.tree_style in ("d", "dark"):
    #         self._update_from_dict(dark.__dict__)
    #     elif self.tree_style in ("m", "multi"):
    #         self._update_from_dict(multi.__dict__)
    #     else:
    #         self._update_from_dict(normal.__dict__)            


    def _update_from_dict(self, kwargs):
        "updates the default attrs as well as those in Style class objects"
        # iterate over each item in kwargs
        for (key, val) in kwargs.items():

            # enter standard items
            if not isinstance(val, dict):
                if key in self.__dict__.keys():
                    if val is not None:
                        self.__setattr__(key, val)

            # extra style are dicts that contain CSS style '-' keys
            else:
                # load the styledict
                styleobj = self.__dict__.get(key)
                alt = {j: i for (i, j) in styleobj._t.items()}
                for (ikey, ival) in val.items():
                    # key may be a mod-key so we'll try to update both since
                    # it doesn't hurt and allows user to use either arg.
                    tkey = styleobj._t.get(ikey)
                    akey = alt.get(ikey)
                    for key in (ikey, tkey, akey):
                        if key in styleobj.__dict__.keys():
                            # update styledict value
                            if ival is not None:
                                styleobj.__setattr__(key, ival)



class EdgeStyle:
    def __init__(self):
        self.stroke = BLACK
        self.stroke_width = 2
        self.stroke_linecap = "round"
        self.opacity = 1
    
        self._t = {
            "stroke": "stroke", 
            "stroke_width": "stroke-width", 
            "stroke_linecap": "stroke-linecap",
            "opacity": "opacity",
        }

    def cssdict(self):
        return {self._t[i]: j for (i, j) in self.__dict__.items() if i != '_t'}

    # a pretty printed styledict
    def __repr__(self):
        view = []
        for (i, j) in self.__dict__.items():
            if i != "_t":
                view.append("{}: {}".format(i, j))
        return "\n".join(view)


class NodeStyle:
    def __init__(self):
        self.fill = COLORS[0]
        self.stroke = "none"
        self.stroke_width = 10
        self._t = {
            "fill": "fill",
            "stroke": "stroke",
            "stroke_width": "stroke-width",
        }

    def cssdict(self):
        return {self._t[i]: j for (i, j) in self.__dict__.items() if i != '_t'}

    # a pretty printed styledict
    def __repr__(self):
        view = []
        for (i, j) in self.__dict__.items():
            if i != "_t":
                view.append("{}: {}".format(i, j))
        return "\n".join(view)


class EdgeAlignStyle:
    def __init__(self):
        self.stroke = "darkgrey"
        self.stroke_width = 2
        self.stroke_linecap = "round"
        self.stroke_dasharray = "2, 4"
        self._t = {
            "stroke": "stroke", 
            "stroke_width": "stroke-width", 
            "stroke_linecap": "stroke-linecap", 
            "stroke_dasharray": "stroke-dasharray"
        }

    def cssdict(self):
        return {self._t[i]: j for (i, j) in self.__dict__.items() if i != '_t'}

    # a pretty printed styledict
    def __repr__(self):
        view = []
        for (i, j) in self.__dict__.items():
            if i != "_t":
                view.append("{}: {}".format(i, j))
        return "\n".join(view)


class NodeLabelStyle:
    def __init__(self):
        self.fill = BLACK
        self.font_size = "10px"
        self._t = {
            "fill": "fill", 
            "font_size": "font-size",
        }

    def cssdict(self):
        return {self._t[i]: j for (i, j) in self.__dict__.items() if i != '_t'}

    # a pretty printed styledict
    def __repr__(self):
        view = []
        for (i, j) in self.__dict__.items():
            if i != "_t":
                view.append("{}: {}".format(i, j))
        return "\n".join(view)


class TipLabelStyle:
    def __init__(self):
        self.fill = BLACK
        self.font_size = "12px"
        self.text_anchor = "start"
        self.text_anchor_shift = None
        self._t = {
            "fill": "fill", 
            "font_size": "font-size", 
            "text_anchor": "text-anchor", 
            "text_anchor_shift": "-toyplot-anchor-shift",
        }

    def cssdict(self):
        return {self._t[i]: j for (i, j) in self.__dict__.items() if i != '_t'}

    # a pretty printed styledict
    def __repr__(self):
        view = []
        for (i, j) in self.__dict__.items():
            if i != "_t":
                view.append("{}: {}".format(i, j))
        return "\n".join(view)

# class AdmixEdgeStyle:
#     def __init__(self):
#         self["admix_edge_style"]["stroke"] = COLORS[0]
#         self["admix_edge_style"]["stroke_linecap"] = "round"
#         self["admix_edge_style"]["stroke_dasharray"] = "2, 4"


# class AxesStyle:
#     def __init__(self):
#         # standard axes names args
#         self.show = False
#         self.padding = 20
#         self.x_show = True
#         self.x_ticks_show = True
#         self.x_ticks_labels_angle = 0
#         self.y_show = True
#         self.y_ticks_show = True
#         self.y_ticks_labels_angle = 0
    
#         # non-standard axes name args
#         self.x_label_color = None
#         self.y_label_color = None        
#         self.y_domain_min = None
#         self.x_domain_min = None
#         self.y_domain_max = None
#         self.x_domain_max = None
#         #self.y.domain.min = ("y.domain.min", None)
#         #self["axes"]["x.domain.min"] = None
#         #self["axes"]["y.domain.max"] = None
#         #self["axes"]["x.domain.max"] = None

#         self._t = {
#             "show": "show",
#             "padding": "padding",
#             "x_show": "x.show",
#             "x_ticks_show": "x.ticks.show",
#             "x_ticks_labels_angle": "x.ticks.labels.angle",
#             "y_show": "y.show",
#             "y_ticks_show": "y.ticks.show",
#             "y_ticks_labels_angle": "y.ticks.labels.angle",
#             "x_label_color": "x_label_color", 
#             "y_label_color": "y_label_color",
#             "x_domain_max": "x.domain.max", 
#             "y_domain_max": "y.domain.max", 
#             "x_domain_min": "x.domain.min", 
#             "y_domain_min": "y.domain.min",            
#         }

#     # a pretty printed styledict
#     def __repr__(self):
#         view = []
#         for (i, j) in self.__dict__.items():
#             if i != '_t':
#                 view.append("{}: {}".format(i, j))
#         return "\n".join(view)


# PREFIX STYLES ---------------------
normal = TreeStyle('normal')
normal.orient = "right"
normal.use_edge_lengths = True
normal.tip_labels_align = False
# normal.axes_style.show = False
# normal.axes_style.padding = 20


coal = TreeStyle('coal')
coal.edge_type = 'c'
coal.orient = 'down'
coal.use_edge_lengths = True
coal.tip_labels_align = False
coal.node_labels = True
coal.node_size = 15
coal.node_hover = False
coal.tip_labels = False
coal.scalebar = True
# coal.axes_style.show = True
# coal.axes_style.padding = 20
# coal.axes_style.x_show = False
# coal.axes_style.x_ticks_show = False
# coal.axes_style.x_ticks_labels_angle = 0
# coal.axes_style.y_show = True
# coal.axes_style.y_ticks_show = True
# coal.axes_style.y_domain_min = 0


dark = TreeStyle('dark')
dark.orient = 'right'
dark.use_edge_lengths = True
dark.tip_labels_align = True
dark.tip_labels_color = COLORS[3]
dark.edge_style.stroke = COLORS[0]
# dark.axes_style.padding = 20
# dark.axes_style.show = False
# dark.axes_style.x_show = True
# dark.axes_style.x_label_color = COLORS[7]
# dark.axes_style.y_label_color = COLORS[7]


multi = TreeStyle('multi')
multi.edge_type = 'c'
multi.orient = 'down'
multi.use_edge_lengths = True
multi.tip_labels_align = False
multi.node_labels = False
multi.node_size = 0
multi.tip_labels = True
multi.edge_style.opacity = 0.1
multi.tip_labels_style.text_anchor_shift = "15px"
# multi.axes_style.show = False



#     def update_axes(self, sdict):
#         "add scale bar given orientation of tree and internal/external axes"

#         # can we set the domain max past zero but still show ticks only at
#         # domains that are within the tree scale?
#         if sdict["scalebar"]:
#             if self["orient"] in ["right", "left"]:
#                 self["axes"]["show"] = True
#                 self["axes"]["x.show"] = True
#                 self["axes"]["y.show"] = False
#                 self["axes"]["padding"] = 10
#                 self["axes"]["x.ticks.show"] = True
#                 self["axes"]["y.ticks.show"] = False
#                 self["axes"]["y.ticks.labels.angle"] = 0
#                 self["axes"]["x.domain.max"] = 0
#             else:
#                 self["axes"]["show"] = True
#                 self["axes"]["x.show"] = False
#                 self["axes"]["y.show"] = True
#                 self["axes"]["padding"] = 10
#                 self["axes"]["x.ticks.show"] = False
#                 self["axes"]["y.ticks.show"] = True
#                 self["axes"]["y.ticks.labels.angle"] = -90
#                 self["axes"]["y.domain.min"] = 0
#                 #locations = np.linspace()
#                 #self._x_tick_locator = toyplot.locator.Explicit(
#                 #    locations=locations, 
#                 #    format="{:.2f}")

#         if sdict["padding"]:
#             self["axes"]["padding"] = sdict["padding"]


#     def update_canvas(self, sdict):
#         sdict = {i: j for i, j in sdict.items() if j is not None}
#         for key, val in sdict.items():
#             if isinstance(val, dict):
#                 self[key].update(sdict[key])
#             else:
#                 self[key] = val        
