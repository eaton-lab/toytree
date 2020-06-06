#!/usr/bin/env python

"""
tree style dictionaries.
"""
import numpy as np
import toyplot
from .html2 import split_rgba_style


# GLOBALS
ITERABLE = (list, tuple, np.ndarray)
COLORS1 = [toyplot.color.to_css(i) for i in toyplot.color.brewer.palette("Set2")]
COLORS2 = [toyplot.color.to_css(i) for i in toyplot.color.brewer.palette("Dark2")]
BLACK = toyplot.color.black


DEFAULT_TREE_STYLE = {
    'edge_type': 'p',
    'edge_colors': None,
    'edge_widths': None,
    'height': None,
    'width': None,
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
    'xbaseline': 0,
    'ybaseline': 0,
    'layout': 'r',
    'admixture_edges': None,
}

DEFAULT_EDGE_STYLE = {
    "stroke": "#262626", 
    "stroke-width": 2, 
    "stroke-linecap": "round", 
    "opacity": 1,
}

DEFAULT_NODE_STYLE = {
    "fill": COLORS1[0],
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
    "-toyplot-anchor-shift": "15px",  # None, 
    "text-anchor": "start",     
}


STYLES = {
    'n': {
        # "tree_style": "normal",
        "layout": "r",
        "use_edge_lengths": True, 
        "tip_labels_align": False, 
    },

    's': {
        # "tree_style": "simple",
        "layout": "r", 
        "use_edge_lengths": False, 
        "node_labels": True, 
        "node_colors": "lightgrey", 
        "node_sizes": 15, 
        "node_style": {
            "stroke": "#262626", 
            "stroke-width": 1.5,
        },
        "tip_labels": True,
    },

    'p': {
        # "tree_style": "population-tree", 
        "layout": "d", 
        "edge_type": "c",
        "use_edge_lengths": True, 
        "tip_labels_align": False, 
        "node_labels": True, 
        "node_sizes": 15, 
        "node_hover": False, 
        "tip_labels": True, 
        "scalebar": True, 
        "edge_widths": "Ne",
        "node_style": {
            "stroke": "#262626",
            "stroke-width": 1,            
        },
    },

    'c': {
        # "tree_style": "coalescent",
        "layout": "d",
        "edge_type": "c",
        "use_edge_lengths": True,
        "node_labels": False,
        "node_sizes": 8,
        "node_hover": False,
        "tip_labels": False,
        "scalebar": True,
        "node_style": {
            "stroke": "#262626",
            "stroke-width": 1.5,
        },
    },

    'd': {
        # tree_style: "dark"
        'layout': 'r', 
        'use_edge_lengths': True, 
        'tip_labels_align': True, 
        'tip_labels_colors': COLORS1[3],
        'edge_style': {
            'stroke': COLORS1[0],
        },
    },

    'm': {
        # tree_style: "multi"    
        'edge_type': 'c', 
        'layout': 'r', 
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

    'f': {
        'edge_type': 'c',
        'layout': 'c',
        'use_edge_lengths': False,
    },

    'o': {
        # tree style: "umlaut"
        'edge_type': 'c',
        'layout': 'r',
        'node_sizes': 8,
        'tip_labels': True,
        'tip_labels_align': True,
        'edge_style': {
            "stroke": "#262626",
            "stroke-width": 2,
        },
        "node_style": {
            "stroke-width": 1.5,
            "stroke": "white",
            "fill": COLORS2[0],
        }
    }

}





class TreeStyle(dict):
    """
    TreeStyle Class for storing tree plotting styling options
    """
    def __init__(self, tree_style='n'):
        # object and dict methods
        self.__dict__ = DEFAULT_TREE_STYLE.copy()

        # Add get and set attrs to dicts
        self._edge_style = DEFAULT_EDGE_STYLE.copy()
        self._node_style = DEFAULT_NODE_STYLE.copy()
        self._edge_align_style = DEFAULT_EDGE_ALIGN_STYLE.copy()
        self._node_labels_style = DEFAULT_NODE_LABEL_STYLE.copy()
        self._tip_labels_style = DEFAULT_TIP_LABEL_STYLE.copy()

        # update dict and subdicts from default to a preset style.
        if tree_style:
            self.update(STYLES[tree_style])



    def update(self, sdict):
        """
        Update this style dict with the values of another. Copies the
        values deeply so no object pointers are shared.
        """
        if isinstance(sdict, TreeStyle):
            sdict = sdict.__dict__

        # update each subdict
        for skey in sdict:

            # if it is a subdictionary
            if skey[0] == "_":
                subdict = sdict[skey]
                for key in subdict:
                    self.__dict__[skey][key] = subdict[key]

            else:
                self.__dict__[skey] = sdict[skey]



    def copy(self):
        """
        Returns a new deepcopy of the TreeStyle object
        """
        newstyle = TreeStyle()
        newstyle.update(self)
        return newstyle




    def __repr__(self):
        """
        Return readable to stdout
        """
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
        return self.__dict__
