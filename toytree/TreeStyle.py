#!/usr/bin/env python

"""
tree style dictionaries
"""

from toyplot import color


# GLOBALS
COLORS = [color.to_css(i) for i in color.Palette()]
BLACK = color.black


DEFAULT_TREE_STYLE = {
    'edge_type': 'p',
    'height': None,
    'width': None,
    'orient': 'right',
    'node_labels': False,
    'node_size': None,
    'node_color': None,
    'vmarker': 'o',
    'node_hover': True,
    'use_edge_lengths': True,
    'tip_labels': True,
    'tip_labels_color': "#262626",
    'tip_labels_align': False, 
    'scalebar': False, 
    'padding': 20,
}

DEFAULT_EDGE_STYLE = {
    "stroke": "#262626", 
    "stroke-width": 2, 
    "stroke-linecap": "round", 
    "opacity": 1,
}

DEFAULT_NODE_STYLE = {
    "fill": COLORS[0],
    "stroke": None,
    "stroke-width": 1, 
}

DEFAULT_NODE_LABEL_STYLE = {
    "fill": "#262626", 
    "font-size": "9px", 
}

DEFAULT_EDGE_ALIGN_STYLE = {
    "stroke": "darkgrey", 
    "stroke-width": 2, 
    "stroke-linecap": "round", 
    "stroke-dasharray": "2, 4", 
}

DEFAULT_TIP_LABEL_STYLE = {
    "fill": "#262626", 
    "font-size": "11px", 
    "text-anchor": "start", 
    "-toyplot-anchor-shift": None, 
}


STYLES = {
    'n': {
        #"tree_style": "normal",
        "orient": "right", 
        "use_edge_lengths": True, 
        "tip_labels_align": False, 
    },

    's': {
        #"tree_style": "simple",
        "orient": "right", 
        "use_edge_lengths": False, 
        "node_labels": True, 
        "node_color": "lightgrey", 
        "node_size": 18, 
        "_node_style": {
            "stroke": "#262626", 
            "stroke-width": 1,
        }
    },

    'c': {
        #"tree_style": "coal", 
        "orient": "down", 
        "use_edge_lengths": True, 
        "tip_labels_align": False, 
        "node_labels": True, 
        "node_size": 15, 
        "node_hover": False, 
        "tip_labels": False, 
        "scalebar": True, 
    },

    'd': {
        'orient': 'right', 
        'use_edge_lengths': True, 
        'tip_labels_align': True, 
        'tip_labels_color': COLORS[3],
        '_edge_style': {
            'stroke': COLORS[0],
        },
    },
    
    'm': {
        'edge_type': 'c', 
        'orient': 'down', 
        'use_edge_lengths': True, 
        'tip_labels_align': False, 
        'node_labels': False, 
        'node_size': 0, 
        'tip_labels': True, 
        '_edge_style': {
            'opacity': 0.1, 
        },
        '_tip_labels_style': {
            '-toyplot-anchor-shift': "15px",
        },
    },
}



class TreeStyle:
    "TreeStyle Class for storing tree plotting styling options"
    def __init__(self, tree_style='n'):
        # object and dict methods
        self.__dict__ = {}

        # sub style dictionaries
        self._edge_style = Style(DEFAULT_EDGE_STYLE)
        self._node_style = Style(DEFAULT_NODE_STYLE)
        self._edge_align_style = Style(DEFAULT_EDGE_ALIGN_STYLE)
        self._node_labels_style = Style(DEFAULT_NODE_LABEL_STYLE)
        self._tip_labels_style = Style(DEFAULT_TIP_LABEL_STYLE)

        self.__dict__.update(DEFAULT_TREE_STYLE)
        if tree_style:
            self.__dict__.update(STYLES[tree_style])

    # these only allow updating styledict, not removing items
    @property
    def edge_style(self):
        return self._edge_style
    @edge_style.setter
    def edge_style(self, sdict):
        try:
            self._edge_style.update(sdict)
            self._edge_style = Style(self._edge_style)
        except ValueError:
            raise TypeError("Style entries must be a dictionary")

    @property
    def node_style(self):
        return self._node_style
    @node_style.setter
    def node_style(self, sdict):
        try:
            self._node_style.update(sdict)
            self._node_style = Style(self._node_style)
        except ValueError:
            raise TypeError("Style entries must be a dictionary")

    @property
    def edge_align_style(self):
        return self._edge_align_style
    @edge_align_style.setter
    def edge_align_style(self, sdict):
        try:
            self._edge_align_style.update(sdict)
            self._edge_align_style = Style(self._edge_align_style)
        except ValueError:
            raise TypeError("Style entries must be a dictionary")

    @property
    def node_labels_style(self):
        return self._node_labels_style
    @node_labels_style.setter
    def node_labels_style(self, sdict):
        try:
            self._node_labels_style.update(sdict)
            self._node_labels_style = Style(self._node_labels_style)
        except ValueError:
            raise TypeError("Style entries must be a dictionary")

    @property
    def tip_labels_style(self):
        return self._tip_labels_style
    @tip_labels_style.setter
    def tip_labels_style(self, sdict):
        try:
            self._tip_labels_style.update(sdict)
            self._tip_labels_style = Style(self._tip_labels_style)
        except ValueError:
            raise TypeError("Style entries must be a dictionary")

        
    def __repr__(self):
        lines = []
        nkeys = [i for i in self.__dict__ if not i[0] == "_"]
        dkeys = [i for i in self.__dict__ if i[0] == "_"]
        for i in sorted(nkeys):
            lines.append("{}: {}".format(i, self.__dict__[i]))
        for i in sorted(dkeys):
            lines.append("{}: ".format(i[1:]) + "{")
            for val in self.__dict__[i]:
                lines.append("    {}: {}".format(val, self.__dict__[i][val]))
            lines.append("}")
        return "\n".join(lines)
       

    def __str__(self):
        return self.__repr__()
        


class Style(dict):
    "Base Class: dictionary with object gettattrs setattrs for convenience"

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)
