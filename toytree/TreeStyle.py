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
    'edge_colors': None,
    'edge_widths': None,
    'height': None,
    'width': None,
    'orient': 'right',
    'node_labels': False,
    'node_sizes': None,
    'node_colors': None,
    'node_markers': None,
    'node_hover': False,
    'use_edge_lengths': True,
    'tip_labels': True,
    'tip_labels_colors': None,
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
        "node_colors": "lightgrey", 
        "node_sizes": 18, 
        "node_style": {
            "stroke": "#262626", 
            "stroke-width": 1,
        }
    },

    'c': {
        #"tree_style": "coal", 
        "orient": "down", 
        "edge_type": "c",
        "use_edge_lengths": True, 
        "tip_labels_align": False, 
        "node_labels": True, 
        "node_sizes": 15, 
        "node_hover": False, 
        "tip_labels": False, 
        "scalebar": True, 
    },

    'd': {
        'orient': 'right', 
        'use_edge_lengths': True, 
        'tip_labels_align': True, 
        'tip_labels_colors': COLORS[3],
        'edge_style': {
            'stroke': COLORS[0],
        },
    },
    
    'm': {
        'edge_type': 'c', 
        'orient': 'right', 
        'use_edge_lengths': True, 
        'tip_labels_align': False, 
        'node_labels': False, 
        'node_sizes': 0, 
        'edge_style': {
            'opacity': 0.05, 
        },
        'tip_labels_style': {
            '-toyplot-anchor-shift': "15px",
        },
    },
}



class TreeStyle(object):
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

        # set default style
        self.update(DEFAULT_TREE_STYLE)
        if tree_style:
            self.update(STYLES[tree_style])


    def update(self, sdict):
        # sdict can be a dict or a TreeStyle, if latter, turn into dict
        if isinstance(sdict, TreeStyle):
            sdict = sdict.__dict__

        # update self attributes
        nodicts = {i: j for (i, j) in sdict.items() if not isinstance(j, dict)}
        isdicts = {i: j for (i, j) in sdict.items() if isinstance(j, dict)}        
        self.__dict__.update(**nodicts)

        # update subdict style attributes
        for key, val in isdicts.items():
            setattr(self, key, val)


    def to_dict(self):
        "returns self as a dictionary with _underscore subdicts corrected."
        ndict = {}
        for key, val in self.__dict__.items():
            if key[0] == "_":
                ndict[key[1:]] = val
            else:
                ndict[key] = val
        return ndict


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
