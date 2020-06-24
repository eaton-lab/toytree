#!/usr/bin/env python

import toyplot
import numpy as np
from .Render import split_rgba_style
from .utils import ToytreeError

ITERABLE = (list, tuple, np.ndarray)

"""
Checks style dictionaries for types and size and builds out arguments
into arrays for variable styles.
"""


class StyleChecker:
    """
    Checks for allowed styles in style dictionaries and expands args
    for individuals styles into arrays while checking types.
    """
    def __init__(self, ttree, style):

        # input objects
        self.ttree = ttree
        self.style = style

        # dimensions
        self.ntips = self.ttree.ntips
        self.nnodes = self.ttree.nnodes
        self.nedges = self.ttree._coords.edges.shape[0]

        # check dictionary inputs 
        self.check_dicts()

        # expand to arrays and sometimes set 'fill' or 'stroke' in dicts.
        self.expand_vars()



    def check_dicts(self):
        """
        Checks style dicts for allowable styles. 
        TODO: check for None and convert to "none"?
        TODO: convert all fill/stroke to rgb and stroke-opacity.
        """

        # check for allowable types
        self.style.node_style = toyplot.style.require(
            self.style.node_style, toyplot.style.allowed.marker)
        self.style.edge_style = toyplot.style.require(
            self.style.edge_style, toyplot.style.allowed.line)
        self.style.edge_align_style = toyplot.style.require(
            self.style.edge_align_style, toyplot.style.allowed.line)
        self.style.tip_labels_style = toyplot.style.require(
            self.style.tip_labels_style, toyplot.style.allowed.text)
        self.style.node_labels_style = toyplot.style.require(
            self.style.node_labels_style, toyplot.style.allowed.text)

        sdicts = [
            self.style.node_style,
            self.style.edge_style,
            self.style.edge_align_style,
            self.style.tip_labels_style,
            self.style.node_labels_style,
        ]

        # check for None and split colors
        for sdict in sdicts:

            # next set the fill or stroke by splitting rgba to rgb and opacity
            # and set the -opacity unless the unser explicitly set it already.
            for coltype in ['fill', 'stroke']:
                if sdict.get(coltype):

                    # convert to css color if not already
                    color = sdict[coltype]

                    try:
                        color = toyplot.color.css(color)
                    except Exception:
                        pass

                    # split the color
                    coldict = split_rgba_style({coltype: color})
                    sdict[coltype] = coldict[coltype]

                    # set the opacity of this type unless already set
                    okey = "{}-opacity".format(coltype)
                    if not sdict.get(okey):
                        sdict[okey] = coldict[okey]




    def expand_vars(self):
        """
        Expand args for individual styles into arrays of correct length. If
        an indiv style was set with only one value then we instead set the 
        style dict fill or stroke (and opacity) with all properly using rgb
        and opacity settings.
        """
        self._assign_node_labels()
        self._assign_node_colors()
        self._assign_node_sizes()
        self._assign_node_shapes()
        self._assign_node_hover()

        self._assign_tip_colors()
        self._assign_tip_labels()
        self._assign_tip_labels_angles()

        self._assign_edge_colors()
        self._assign_edge_widths()



    def _assign_tip_colors(self):
        """
        Sets .tip_colors as an array of length ntips. Only fills vals if there
        is variation among tips, otherwise leaves empty to use style fill.

        tip_colors=None       |  [None, None, ...]
        tip_colors=ITERABLE   |  [col0, col1, col2, ...] 
        tip_colors=STR        |  [None, None, ...] & tip_labels_style['fill']
        """
        arg = self.style.tip_labels_colors

        # set it all empty
        if arg is None:
            self.style.tip_labels_colors = toyplot.broadcast.pyobject(None, self.ntips)

        else:
            self.style.tip_labels_colors = toyplot.color.broadcast(arg, self.ntips, None)

            # if all the same then reset to None
            if len(set([str(i) for i in self.style.tip_labels_colors])) == 1:

                # save the fixed color and set to None
                color = self.style.tip_labels_colors[0]
                self.style.tip_labels_colors = toyplot.broadcast.pyobject(None, self.ntips)

                # set edge_style stroke and stroke-opacity 
                sub = split_rgba_style({'fill': color})
                self.style.tip_labels_style['fill'] = sub["fill"]
                self.style.tip_labels_style['fill-opacity'] = sub["fill-opacity"]

            else:
                # reorder array for fixed if needed
                if self.style.fixed_order:
                    self.style.tip_labels_colors = self.style.tip_labels_colors[self.ttree._fixed_idx]


    def _assign_tip_labels(self):
        """
        Sets .tip_labels as an array of length ntips.

        tip_labels=None             | ['a', 'b', 'c'] or fixed_order
        tip_labels=True             | ['a', 'b', 'c'] or fixed_order
        tip_labels=False            | [None, None, None]
        tip_labels=['a', 'c', 'b']  | ['a', 'c', 'b']
        """
        arg = self.style.tip_labels

        # set it
        if arg is False:
            self.style.tip_labels = None
        elif isinstance(arg, ITERABLE):
            pass
        else:  # arg in [None, True]:
            self.style.tip_labels = self.ttree.get_tip_labels()

        # check length
        self.style.tip_labels = toyplot.broadcast.pyobject(
            self.style.tip_labels, self.ntips)


    def _assign_tip_labels_angles(self):
        """
        Sets .tip_labels_angles as an array of length ntips. No user 
        args for this one, it inherits from the layout type.
        """
        # set circular layout
        if self.style.layout == 'c':

            # define range of tip radians
            tip_radians = np.linspace(0, -np.pi * 2, self.ntips + 1)[:-1]
            angles = np.array([np.rad2deg(abs(i)) for i in tip_radians]) * -1

        elif self.style.layout == "u":
            angles = -90

        elif self.style.layout == "d":
            angles = -90

        elif self.style.layout == "l":
            angles = 0

        else:
            angles = 0

        self.style.__dict__['tip_labels_angles'] = toyplot.broadcast.scalar(angles, self.ntips)


    def _assign_node_labels(self):
        """
        Sets .node_labels array of length nnodes. In addition to being the
        text labels on nodes these features can also affect whether node
        marks will be shown. Suppressed markers are recorded with nan as 
        the value label. To show the node mark but with empty labels a None
        value is used. 

        node_labels=None                        |  [None, None, None,]
        node_labels=False                       |  [None, None, None,]
        node_labels=True                        |  [0, 1, 2, 3]
        node_labels=ITERABLE                    |  [100, 90, 95, ...]
        node_labels=STR in .feat, e.g., "idx"   |  [nan, nan, 2, ..., nan]
        node_labels=TUPLE, e.g., ("idx", 1, 0)  |  [0, 1, 2, ..., nan]
        """
        arg = self.style.node_labels

        # set it.
        if arg is True:
            self.style.node_labels = self.ttree.get_node_values("idx", 1, 1)[::-1]
        elif arg is False:
            self.style.node_labels = None
        elif arg is None:
            self.style.node_labels = None
        elif isinstance(arg, (str, bytes)):
            if arg in self.ttree.features:
                self.style.node_labels = self.ttree.get_node_values(arg, 0, 0)[::-1]
        elif isinstance(arg, tuple) and (len(arg) == 3):
            if arg[0] in self.ttree.features:
                self.style.node_labels = self.ttree.get_node_values(*arg)[::-1]
        elif isinstance(arg, ITERABLE):
            self.style.node_labels = arg[::-1]
        else:
            raise ToytreeError(
                "node_labels argument not recognized: {}".format(arg))

        # check length
        self.style.node_labels = toyplot.broadcast.pyobject(
            self.style.node_labels, self.nnodes)


    def _assign_node_shapes(self):
        """
        Sets .node_shapes as an array of length nnodes in levelorder

        node_markers=None         | ['o', 'o', 'o', ...]
        node_markers=STR          | ['o', 'o', 'o', ...]
        node_markders=ITERABLE     | ['o', 's', 'o', ...]
        """
        arg = self.style.node_markers
        if isinstance(arg, ITERABLE):
            self.style.node_markers = arg[::-1]
        elif isinstance(arg, (bytes, str)):
            self.style.node_markers = arg
        else:
            self.style.node_markers = 'o'

        # project to size
        self.style.node_markers = toyplot.broadcast.pyobject(
            self.style.node_markers, self.nnodes)


    def _assign_node_sizes(self):
        """
        Sets .node_sizes as an array of length nnodes in levelorder

        node_sizes=None         | [None, None, None, ...]
        node_sizes=INT          | [12, 12, 12, 12, ...]
        node_sizes=ITERABLE     | [5, 12, 20, 5, ...]
        """
        # 
        arg = self.style.node_sizes
        if isinstance(arg, ITERABLE):
            self.style.node_sizes = arg[::-1]
        elif isinstance(arg, (int, float)):
            self.style.node_sizes = arg
        else:
            self.style.node_sizes = None

        # project to size
        self.style.node_sizes = toyplot.broadcast.pyobject(
            self.style.node_sizes, self.nnodes)

        # special: hide nodes with labels that are (TODO: nan) for now ("")
        # but only if arg was None or INT, not if explicity list type.
        if isinstance(arg, (int, float)):
            self.style.node_sizes[self.style.node_labels == ""] = 0


    def _assign_node_hover(self):
        """
        Sets .node_hover as an array of length nnodes in levelorder.

        node_hover=None         | [None, None, None, ...]
        node_hover=True         | [node_idx=31\nname=blah\nfeat=x, ...]
        node_hover="idx"        | [31, 30, 29, 28, ...]
        node_hover=ITERABLE     | ['a', 'b', 'c', 'd', ...]
        """
        # 
        arg = self.style.node_hover
        if isinstance(arg, ITERABLE):
            self.style.node_hover = arg[::-1]
        elif arg is None:
            self.style.node_hover = None
        elif arg is False:
            self.style.node_hover = None
        elif arg is True:
            ordered_features = ["idx", "dist", "support", "height"]
            lfeatures = list(set(self.ttree.features) - set(ordered_features))       
            ordered_features += lfeatures

            # build list of hoverstrings in order of idxs
            self.style.node_hover = [" "] * self.ttree.nnodes
            for idx in self.ttree.idx_dict:
                feats = []
                node = self.ttree.idx_dict[idx]
                for feature in ordered_features:
                    val = getattr(node, feature)
                    if isinstance(val, float):
                        feats.append("{}: {:.4f}".format(feature, val))
                    else:
                        feats.append("{}: {}".format(feature, val))
                self.style.node_hover[idx] = "\n".join(feats)
            # already in levelorder from idx_dict iter
            self.style.node_hover = self.style.node_hover

        # project to size
        self.style.node_hover = toyplot.broadcast.pyobject(
            self.style.node_hover, self.nnodes)

        # special: hide nodes with labels that are (TODO: nan) for now ("")
        # node_labels is already in levelorder.
        self.style.node_hover[self.style.node_labels == ""] = None


    def _assign_node_colors(self):
        """
        Sets .node_colors as an array of length nedges. Default is to 
        leave the list as None so that the default style fill all.

        node_colors=None         | [None, None, None, ...]
        node_colors='red'        | [None, None, ...] & sets node_style['fill']
        node_colors=ITERABLE     | ['red', 'blue', 'green']
        """
        arg = self.style.node_colors

        # set to empty 
        if arg is None:
            self.style.node_colors = toyplot.broadcast.pyobject(arg, self.nnodes)

        # fill array with whatever was provided
        else:
            self.style.node_colors = toyplot.color.broadcast(arg, self.nnodes)[::-1]

            # if all the same then reset to None
            if len(set([str(i) for i in self.style.node_colors])) == 1:

                # save the fixed color and set to None
                color = self.style.node_colors[0]
                self.style.node_colors = toyplot.broadcast.pyobject(None, self.nnodes)

                # set edge_style stroke and stroke-opacity 
                sub = split_rgba_style({'fill': color})
                self.style.node_style['fill'] = sub["fill"]
                self.style.node_style['fill-opacity'] = sub["fill-opacity"]


    def _assign_edge_colors(self):
        """
        Sets .edge_colors as an array of length nedges. Default is to 
        leave the list as None so that the default style stroke fills all.

        edge_colors=None         | [None, None, None, ...]
        edge_colors='red'        | [None, None, ...] & sets edge_style['fill']
        edge_colors=ITERABLE     | ['red', 'blue', 'green']
        """
        arg = self.style.edge_colors

        # set to empty 
        if arg is None:
            self.style.edge_colors = toyplot.broadcast.pyobject(arg, self.nedges)

        # fill array with whatever was provided
        else:
            self.style.edge_colors = toyplot.color.broadcast(arg, self.nedges)[::-1]

            # if all the same then reset to None
            if len(set([str(i) for i in self.style.edge_colors])) == 1:

                # save the fixed color and set to None
                color = self.style.edge_colors[0]
                self.style.edge_colors = toyplot.broadcast.pyobject(None, self.nedges)

                # set edge_style stroke and stroke-opacity 
                sub = split_rgba_style({'stroke': color})
                self.style.edge_style['stroke'] = sub["stroke"]

                # only set sub opacity if it is not already at 1, otherwise
                # keep the edgestyledict opacity b/c user probably set it.
                if self.style.edge_style["stroke-opacity"] == 1:
                    self.style.edge_style['stroke-opacity'] = sub["stroke-opacity"]


    def _assign_edge_widths(self):
        """
        Sets .edge_widths as an array of length nedges. Default is to 
        leave the list as None so that the default style stroke-width sets
        all values. There is special option for entry "Ne" which will auto
        scale edge withs by the range of values on TreeNodes.Ne

        edge_widths=None         | [None, None, None, ...]
        edge_widths=2            | [None, None, ...] & edge_style[stroke-width]
        edge_widths=ITERABLE     | [2, 3, 3, 2, ...]
        edge_widths='Ne'         | [2, 2.5, 5, 2, ...]
        """
        arg = self.style.edge_widths

        # set to empty 
        if arg is None:
            self.style.edge_widths = toyplot.broadcast.pyobject(arg, self.nedges)

        # fill array with whatever was provided
        else:
            if str(arg) == "Ne":
                try:
                    arg = self.ttree.get_edge_values("Ne", normalize=True)
                except Exception:
                    arg = np.repeat(2, self.nedges)
            self.style.edge_widths = toyplot.broadcast.pyobject(arg, self.nedges)[::-1]

            # if all the same then reset to None
            if len(set([str(i) for i in self.style.edge_widths])) == 1:

                # save the fixed color and set to None
                width = self.style.edge_widths[0]
                self.style.edge_widths = toyplot.broadcast.pyobject(None, self.nedges)

                # set edge_style stroke and stroke-opacity 
                self.style.edge_style['stroke-width'] = width
