#!/usr/bin/env python

"""
A custom Mark and mark generator to create Toytree drawings in toyplot.
"""
import numpy as np
import xml.etree.ElementTree as xml
import toyplot
from toyplot.mark import Mark
from toyplot.html import _draw_bar, _draw_triangle, _draw_circle, _draw_rect
from .TreeStyle import COLORS1
# from toytree.utils import ToytreeError

# Register multipledispatch to share with toyplot.html
import functools
from multipledispatch import dispatch
dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)

"""
- fixed-order extension to tip positions for missing labels..?
- rawtree consensus checking...
- container tree to Mark
"""


PATH_FORMAT = {
    'c': "M {px:.1f} {py:.1f} L {cx:.1f} {cy:.1f}",
    'b1': "M {px:.1f} {py:.1f} C {px:.1f} {cy:.1f}, {px:.1f} {cy:.1f}, {cx:.1f} {cy:.3f}",
    'b2': "M {px:.1f} {py:.1f} C {cx:.1f} {py:.1f}, {cx:.1f} {py:.1f}, {cx:.1f} {cy:.3f}",    
    'p1': "M {px:.1f} {py:.1f} L {px:.1f} {cy:.1f} L {cx:.1f} {cy:.1f}",
    'p2': "M {px:.1f} {py:.1f} L {cx:.1f} {py:.1f} L {cx:.1f} {cy:.1f}",
    'pc': "M {cx:.1f} {cy:.1f} L {dx:.1f} {dy:.1f} A {rr:.1f} {rr:.1f} 0 0 {flag} {px:.1f} {py:.1f}",
}


class ToytreeMark(Mark):
    """
    Custom mark testing.
    """
    def __init__(
        self, 
        ntable, 
        node_colors, 
        node_sizes, 
        node_style,
        node_markers,
        node_hover,
        etable,
        edge_colors,
        edge_widths,
        edge_type,
        edge_style,
        edge_align_style,
        tip_labels,
        tip_labels_angles,
        tip_labels_colors,
        tip_labels_style,
        node_labels,
        node_labels_style,
        tip_labels_align,
        layout,
        xbaseline,
        ybaseline,
        admixture_edges,
        shrink,
        **kwargs):

        # inherit type
        Mark.__init__(self)

        # check arg types
        self._coordinate_axes = ['x', 'y']  
        self.layout = layout
        self.shrink = (shrink if shrink else 0)

        # store anything here that you want available as tool-tip hovers
        self.ntable = ntable
        self.etable = etable

        # positioning
        self.xbaseline = xbaseline
        self.ybaseline = ybaseline
        self.ntable[:, 0] += xbaseline
        self.ntable[:, 1] += ybaseline

        # radial positioning
        self.radii = np.sqrt(
            self.ntable[:, 0] ** 2 + self.ntable[:, 1] ** 2 
        )

        # node plotting args
        self.node_colors = node_colors
        self.node_sizes = node_sizes
        self.node_markers = node_markers
        self.node_style = node_style
        self.node_hover = node_hover

        # edge (tree) plotting args
        self.edge_colors = edge_colors
        self.edge_widths = edge_widths
        self.edge_style = edge_style
        self.edge_type = edge_type
        self.edge_align_style = edge_align_style

        # tip labels
        self.tip_labels = tip_labels
        self.tip_labels_angles = tip_labels_angles
        self.tip_labels_colors = tip_labels_colors
        self.tip_labels_style = tip_labels_style
        self.tip_labels_align = tip_labels_align

        # node labels
        self.node_labels = node_labels
        self.node_labels_style = node_labels_style

        # admix edges
        self.admixture_edges = admixture_edges


    @property
    def nnodes(self):
        return self.ntable.shape[0]


    def domain(self, axis):
        """
        The domain of data that will be tracked.
        """
        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self.ntable[:, index])
        return domain


    def extents(self, axes):
        """
        Extends domain to fit tip names or mars based on their size, but 
        does not extend the data domain. 
        The main component to worry about here is tip labels text, especially
        for weird layouts that make it angled. For circular we project text
        at angle and inverted angle to get projection from anchor start,end.
        But node markers also contribute to this since extents=0 would cut a
        circular 15px node marker in half at the root. So we would need at 
        least 15px left extent.

        Further modification is made by the argument 'scale' which can
        compress the tree to allow more space for names. This is done by 
        making the extents larger.

        extents is [l, r, b, t] for each textbox
        """
        if self.layout != "c":
            # coordinates of all nodes on the tree.
            coords = (
                self.ntable[:, 0],
                self.ntable[:, 1],
            )

            # extents of all node markers
            ntips = len(self.tip_labels)
            nnodes = len(coords[0])

            # get tip label text extents
            if np.any(self.tip_labels):
                text_extents = toyplot.text.extents(
                    self.tip_labels,
                    self.tip_labels_angles,
                    style={
                        "-toyplot-vertical-align": "middle",
                        "font-family": "helvetica",
                        "font-weight": "normal",
                        "stroke": "none",
                        "font-size": toyplot.units.convert(
                            self.tip_labels_style['font-size'], "px") + 10,
                    }
                )

            else:
                text_extents = [[0, 0, 0, 0]] * ntips

            # check node extents
            xnode_sizes = self.node_sizes.copy()
            xnode_sizes[self.node_sizes == None] = 0

            # check edge widths
            # tmp fix for multitrees popping stroke-width currently
            try:
                xedge_widths = self.node_sizes.copy()
                xedge_widths[:-1] = self.edge_widths.copy()
                xedge_widths[xedge_widths == None] = self.edge_style['stroke-width']
            except KeyError:
                xedge_widths = np.repeat(2, self.nnodes)

            # empty extents for filling
            extents = (
                np.zeros(nnodes), np.zeros(nnodes),
                np.zeros(nnodes), np.zeros(nnodes),
            )

            # fill each node 
            for nidx in range(nnodes):

                # check tips extents 
                if nidx < ntips:
                    node_extent = np.array([xnode_sizes[nidx]] * 4)
                    node_extent *= [-1, 1, -1, 1]
                    edge_extent = np.array([xedge_widths[nidx]] * 4)
                    edge_extent *= [-1, 1, -1, 1]

                    if not np.any(self.tip_labels):
                        text_extent = np.array([0, 0, 0, 0])
                    else:
                        text_extent = [
                            text_extents[0][nidx],
                            text_extents[1][nidx],
                            text_extents[2][nidx],
                            text_extents[3][nidx],
                        ]

                        offset = toyplot.units.convert(
                            self.tip_labels_style["-toyplot-anchor-shift"],
                            "px",
                        )

                        # shrink extends the extents in the angle of the tips x layout
                        if self.layout == 'd':
                            width = abs(text_extent[2]) + abs(text_extent[3])
                            text_extent[3] = width + self.shrink + offset
                            text_extent[2] = 0

                        elif self.layout == 'u':
                            width = abs(text_extent[2]) + abs(text_extent[3])
                            text_extent[2] = -(width + offset + self.shrink)
                            text_extent[3] = 0

                        elif self.layout == 'r':
                            width = text_extent[1] - text_extent[0]
                            text_extent[0] = 0
                            text_extent[1] = width + offset * self.shrink

                        elif self.layout == 'l':
                            width = text_extent[1] - text_extent[0]
                            text_extent[0] = -(width + offset + self.shrink)
                            text_extent[1] = 0


                # check tips extents 
                else:
                    node_extent = np.array([xnode_sizes[nidx]] * 4)
                    node_extent *= [-1, 1, -1, 1]
                    edge_extent = np.array([xedge_widths[nidx]] * 4)
                    edge_extent *= [-1, 1, -1, 1]
                    text_extent = np.array([0, 0, 0, 0])

                # store extent nidx
                extents[0][nidx] = min([node_extent[0], edge_extent[0], text_extent[0]])
                extents[1][nidx] = max([node_extent[1], edge_extent[1], text_extent[1]])
                extents[2][nidx] = min([node_extent[2], edge_extent[2], text_extent[2]])
                extents[3][nidx] = max([node_extent[3], edge_extent[3], text_extent[3]])


        # for radial trees we want extents to fit similar in all directions
        # regardless of branch and tip name lengths. So find the radius of 
        # the circle + anchor shift + longest name and pass in all directions.
        else:
            coords = (
                max(self.radii) * np.array([-1, 0, 1, 0]),
                max(self.radii) * np.array([0, 1, 0, -1]),
            )

            # no tip labels for extends
            if all([i is None for i in self.tip_labels]):

                # no extents necessary
                if all([i is None for i in self.node_sizes]):
                    coords = tuple([np.array([])] * 2)
                    extents = tuple([np.array([])] * 4)

                # extend by node size                    
                else:
                    extents = (
                        np.repeat(max(self.node_sizes) * -1, 4),
                        np.repeat(max(self.node_sizes), 4),
                        np.repeat(max(self.node_sizes), 4),
                        np.repeat(max(self.node_sizes) * -1, 4),                                                                        
                    )

            # get the maxwidth of any tips ignoring positioning
            else:
                tips = self.tip_labels
                exts = toyplot.text.extents(
                    tips,
                    0, 
                    style={
                        "-toyplot-vertical-align": "middle",
                        "font-family": "helvetica",
                        "font-weight": "normal",
                        "stroke": "none",
                        "font-size": toyplot.units.convert(
                            self.tip_labels_style['font-size'], "px") + 10,
                    }
                )
                maxw = max([exts[1][i] - exts[0][i] for i in range(len(tips))])
                ashift = toyplot.units.convert(
                    self.tip_labels_style["-toyplot-anchor-shift"], "px")
                extents = (
                    np.repeat(-self.shrink - ashift - maxw * 1.5, 4),  # left ext
                    np.repeat(self.shrink + ashift + maxw * 1.5, 4),  # right ext
                    np.repeat(-self.shrink - ashift - maxw * 1.5, 4),  # bottom
                    np.repeat(self.shrink + ashift + maxw * 1.5, 4),  # top
                )

        # # all other layouts 
        # else:
        #     coords = (
        #         self.ntable[:len(self.tip_labels), 0],
        #         self.ntable[:len(self.tip_labels), 1],
        #     )
        #     style = {
        #         'font-size': toyplot.units.convert(self.tip_labels_style['font-size'], "px") + 5,
        #         '-toyplot-anchor-shift': self.tip_labels_style['-toyplot-anchor-shift']
        #     }
        #     extents = toyplot.text.extents(
        #         self.tip_labels,
        #         self.tip_labels_angles,
        #         style,
        #         #(self.tip_labels_style if self.tip_labels[0] else {}),
        #     )

        return coords, extents



class RenderToytree:
    """
    Organized class to call within _render
    """
    def __init__(self, axes, mark, context):

        # inputs
        self.mark = mark
        self.axes = axes
        self.context = context

        # to be constructed ...
        self.mark_xml = None

        # construction funcs
        self.project_coordinates()
        self.build_dom()


    def build_dom(self):
        """
        Creates DOM of xml.SubElements in self.context.
        """
        self.mark_toytree()
        self.mark_edges()
        self.mark_align_edges()
        self.mark_admixture_edges()
        self.mark_nodes()
        self.mark_node_labels()

        # for multitrees tips are sometimes not drawn.
        self.mark_tip_labels()


    def project_coordinates(self):
        """
        Stores node coordinates (data units) projecting as pixel units.
        """
        # project data coordinates into pixels
        self.nodes_x = self.axes.project('x', self.mark.ntable[:, 0])
        self.nodes_y = self.axes.project('y', self.mark.ntable[:, 1])
        if self.mark.layout == 'c':
            self.radii = self.axes.project('x', self.mark.radii)
            self.maxr = max(self.radii)

        # get align edge tips coords
        if self.mark.tip_labels_align:

            # coords of aligned tips across fixed x axis 0
            ntips = self.mark.tip_labels.size
            if self.mark.layout in ('r', 'l'):
                self.tips_x = np.repeat(
                    self.axes.project('x', self.mark.xbaseline), ntips)
                self.tips_y = self.nodes_y[:ntips]

            # coords of aligned tips across fixed y axis 0
            elif self.mark.layout in ('u', 'd'):
                self.tips_x = self.nodes_x[:ntips]
                self.tips_y = np.repeat(
                    self.axes.project('y', self.mark.ybaseline), ntips)

            # coords of tips around a circumference 
            elif self.mark.layout in ('c'):
                self.tips_x = np.zeros(ntips)
                self.tips_y = np.zeros(ntips)
                for idx, angle in enumerate(self.mark.tip_labels_angles):
                    radian = np.deg2rad(angle)
                    cx = 0 + max(self.mark.radii) * np.cos(radian)
                    cy = 0 - max(self.mark.radii) * np.sin(radian)
                    self.tips_x[idx] = self.axes.project('x', cx)
                    self.tips_y[idx] = self.axes.project('y', cy)             



    def get_paths(self):
        """
        # get edge table shape based on edge and layout types
        # 'c': M x y L x y                  # phylogram
        # 'p': M x y L x y L x y            # cladogram
        # 'b': M x y C x y, x y, x y        # bezier phylogram
        # 'f': M x y A r r, x, a, f, x y    # arcs/circle tree

        The arc/circle method applies to edge_type 'p' when layout='c'       
        """
        # modify order of x or y shift of edges for p,b types.
        if self.mark.edge_type in ('p', 'b'):
            if self.mark.layout == 'c':
                path_format = PATH_FORMAT["pc"]

            elif self.mark.layout in ('u', 'd'):
                path_format = PATH_FORMAT["{}2".format(self.mark.edge_type)]

            else:
                path_format = PATH_FORMAT["{}1".format(self.mark.edge_type)]
        else:
            path_format = PATH_FORMAT[self.mark.edge_type]

        # store paths here
        paths = []
        keys = []

        # countdown from root node idx to tips
        for eidx in range(self.mark.etable.shape[0] - 1, -1, -1):

            # get parent and child
            cidx = self.mark.etable[eidx, 1]
            pidx = self.mark.etable[eidx, 0]
            cx, cy = self.nodes_x[cidx], self.nodes_y[cidx]
            px, py = self.nodes_x[pidx], self.nodes_y[pidx]

            # get parent and child node angles from origin
            if self.mark.layout == 'c':
                ox = self.nodes_x[-1] + 0.000000123  # avoid cx == ox
                oy = self.nodes_y[-1] + 0.000000321
                pr = self.radii[pidx] - ox
                theta = np.arctan((oy - cy) / (cx - ox))               

                # trig to get hypotenuse from theta and parent radius
                if cx >= ox:
                    dx = ox + np.cos(theta) * pr
                    dy = oy - np.sin(theta) * pr
                else:
                    dx = ox - np.cos(theta) * pr
                    dy = oy + np.sin(theta) * pr

                # sweep flag to arc clockwise or not
                if py <= oy:
                    # this is working to arc within hemispheres
                    if dy <= oy:                          
                        if px >= dx:
                            flag = 1
                        else:
                            flag = 0
                    # if arc crosses the origin y
                    else:
                        flag = 1
                else:
                    # dy on same hemisphere?
                    if dy >= oy:
                        if px >= dx:
                            flag = 0
                        else:
                            flag = 1
                    else:
                        flag = 0

                # build paths.
                keys.append("{},{}".format(pidx, cidx))
                paths.append(
                    path_format.format(**{
                        'cx': cx, 'cy': cy, 'px': px, 'py': py,
                        'dx': dx, 'dy': dy, 'rr': pr, 'flag': flag, 
                    })
                )

            # build path string for simple types
            else: 
                keys.append("{},{}".format(pidx, cidx))                
                paths.append(
                    path_format.format(**{
                        'cx': cx, 'cy': cy, 'px': px, 'py': py,
                    })
                )
        return paths, keys



    def mark_toytree(self):
        """
        Creates the top-level Toytree mark.
        """
        self.mark_xml = xml.SubElement(
            self.context.parent, "g", 
            id=self.context.get_id(self.mark),
            attrib={"class": "toytree-mark-Toytree"},
        )



    def mark_edges(self):
        """
        Creates SVG paths for each tree edge under class toytree-Edges
        """
        # get paths based on edge type and layout
        paths, keys = self.get_paths()

        # get shared versus unique styles
        unique_styles = get_unique_edge_styles(self.mark)
        self.mark.edge_style['fill'] = "none"

        # render the edge group
        self.edges_xml = xml.SubElement(
            self.mark_xml, "g", 
            attrib={"class": "toytree-Edges"}, 
            style=style_to_string(self.mark.edge_style)
        )

        # render the edge paths
        for idx, path in enumerate(paths):
            style = unique_styles[idx]
            if style:
                xml.SubElement(
                    self.edges_xml, "path",
                    d=path,
                    id=keys[idx],
                    style=style_to_string(style),
                )
            else:
                xml.SubElement(
                    self.edges_xml, "path",
                    d=path,
                    id=keys[idx],
                )



    def mark_nodes(self):
        """
        Creates marker elements for each node under class toytree-Nodes.
        This could store ids to the nodes if we planned some interesting
        downstream JS interactivity...
        """
        # skip if all nodes are size=0
        if not all([i in (0, None) for i in self.mark.node_sizes]):

            # get fill style if differs among nodes
            unique_styles = [{} for i in range(self.mark.nnodes)]

            # only if variable tho
            if not all([i is None for i in self.mark.node_colors]):                

                # get fill and fill-opacity of each mark (levelorder)
                for idx in range(self.mark.nnodes):

                    # get the rgba node color
                    fill = self.mark.node_colors[idx]

                    # split into rgb and opacity and store result dict
                    unique_styles[idx] = split_rgba_style({'fill': fill})

            # Group all Nodes with shared style applied
            self.nodes_xml = xml.SubElement(
                self.mark_xml, "g", 
                attrib={"class": "toytree-Nodes"}, 
                style=style_to_string(self.mark.node_style),
            )

            # add node markers in reverse idx order (levelorder traversal)
            for nidx in range(self.mark.nnodes):

                # levelorder idx is root to tip idxs
                # idx = self.mark.nnodes - nidx

                # create marker with shape and size, e.g., <marker='o' size=12>
                marker = toyplot.marker.create(
                    shape=self.mark.node_markers[nidx],
                    size=self.mark.node_sizes[nidx],
                )

                # create the marker
                attrib = unique_styles[nidx]
                attrib['id'] = 'node-{}'.format(nidx)
                marker_xml = xml.SubElement(
                    self.nodes_xml, "g", attrib=attrib)

                # optionally add a title UNLESS node_label, then put the hover
                # on the node text instead.
                if self.mark.node_hover[nidx] is not None:
                    if self.mark.node_labels[nidx] is None:
                        xml.SubElement(marker_xml, "title").text = (
                            self.mark.node_hover[nidx])

                # project marker in coordinate space
                transform = "translate({:.3f},{:.3f})".format(
                    self.nodes_x[nidx],
                    self.nodes_y[nidx],
                )
                if marker.angle:
                    transform += " rotate({:.1f})".format(-marker.angle)
                marker_xml.set("transform", transform)

                # get shape type
                if marker.shape == "|":
                    _draw_bar(marker_xml, marker.size)
                elif marker.shape == "/":
                    _draw_bar(marker_xml, marker.size, angle=-45)
                elif marker.shape == "-":
                    _draw_bar(marker_xml, marker.size, angle=90)
                elif marker.shape == "\\":
                    _draw_bar(marker_xml, marker.size, angle=45)
                elif marker.shape == "+":
                    _draw_bar(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size, angle=90)
                elif marker.shape == "x":
                    _draw_bar(marker_xml, marker.size, angle=-45)
                    _draw_bar(marker_xml, marker.size, angle=45)
                elif marker.shape == "*":
                    _draw_bar(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size, angle=-60)
                    _draw_bar(marker_xml, marker.size, angle=60)
                elif marker.shape == "^":
                    _draw_triangle(marker_xml, marker.size)
                elif marker.shape == ">":
                    _draw_triangle(marker_xml, marker.size, angle=-90)
                elif marker.shape == "v":
                    _draw_triangle(marker_xml, marker.size, angle=180)
                elif marker.shape == "<":
                    _draw_triangle(marker_xml, marker.size, angle=90)
                elif marker.shape == "s":
                    _draw_rect(marker_xml, marker.size)
                elif marker.shape == "d":
                    _draw_rect(marker_xml, marker.size, angle=45)
                elif marker.shape and marker.shape[0] == "r":
                    width, height = marker.shape[1:].split("x")
                    _draw_rect(
                        marker_xml, marker.size,
                        width=float(width), height=float(height))
                elif marker.shape == "o":
                    _draw_circle(marker_xml, marker.size)
                elif marker.shape == "oo":
                    _draw_circle(marker_xml, marker.size)
                    _draw_circle(marker_xml, marker.size / 2)
                elif marker.shape == "o|":
                    _draw_circle(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size)
                elif marker.shape == "o/":
                    _draw_circle(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size, -45)
                elif marker.shape == "o-":
                    _draw_circle(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size, 90)
                elif marker.shape == "o\\":
                    _draw_circle(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size, 45)
                elif marker.shape == "o+":
                    _draw_circle(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size, 90)
                elif marker.shape == "ox":
                    _draw_circle(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size, -45)
                    _draw_bar(marker_xml, marker.size, 45)
                elif marker.shape == "o*":
                    _draw_circle(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size)
                    _draw_bar(marker_xml, marker.size, -60)
                    _draw_bar(marker_xml, marker.size, 60)



    def mark_node_labels(self):
        """
        Creates text elements for node label under class toytree-NodeLabels.
        toytree-NodeLabels stores shared text styling but no positional style,
        and positional styling is interpreted and applied using transform
        methods in 'custom_draw_text' func, with unique text styling applied
        there (only 'fill' currently supported).
        """
        if not all([i is None for i in self.mark.node_labels]):

            # make xml with non-positioning styles that apply to all text
            style_group = {}
            exc = ["baseline-shift", "-toyplot-anchor-shift", "text-anchor"]
            style_pos = {"text-anchor": "middle", "stroke": "none"}
            style_pos.update(self.mark.node_labels_style)
            style_group = {
                i: j for (i, j) in style_pos.items() if i not in exc
            }

            # make the group with text style but not position styles
            nlabels_xml = xml.SubElement(
                self.mark_xml, "g", 
                attrib={"class": "toytree-NodeLabels"}, 
                style=toyplot.style.to_css(style_group),
            )

            # if title then put it here instead of on node marker
            for idx in range(self.mark.nnodes):

                label = self.mark.node_labels[idx]
                if label not in ("", " ", None):

                    # get size of text box based on style_pos
                    layout = toyplot.text.layout(
                        str(label),
                        style_pos,
                        toyplot.font.ReportlabLibrary(),
                    )

                    # apply transform to each textbox and add to xml
                    for child in layout.children:
                        for textbox in child.children:

                            # project points into coordinate space 
                            transform = "translate({:.2f},{:.2f})".format(
                                self.nodes_x[idx] + textbox.left,
                                self.nodes_y[idx] + textbox.baseline,
                            )
                            # if angle:
                            # transform += "rotate({:.1f})".format(-angle)

                            # create a group marker for positioning text
                            group = xml.SubElement(
                                nlabels_xml, "g", 
                            )
                            group.set("transform", transform)

                            # optionally add a title 
                            title = self.mark.node_hover[idx]
                            if title is not None:
                                xml.SubElement(group, "title").text = str(title)
                            xml.SubElement(group, "text").text = str(label)



    def mark_tip_labels(self):
        """
        Creates text elements for tip labels under class toytree-TipLabels.
        Styling here needs to support both linear, circular and unrooted trees,
        which is trick by combining style for -toyplot-anchor-shift and angles
        when setting transform.       
        """
        if not all([i is None for i in self.mark.tip_labels]):

            # allowed styling that can be updated by user style
            top_style = {
                'font-family': 'helvetica',
                'font-weight': 'normal',
                'white-space': 'pre',
                'fill': 'rgb(90.6%,54.1%,76.5%)',
                'fill-opacity': '1.0',
                'stroke': 'none',
                'font-size': '9px',
            }
            for sty in top_style:
                if sty in self.mark.tip_labels_style:
                    top_style[sty] = self.mark.tip_labels_style[sty]

            # apply font styling but NOT POSITIONAL styling to group.
            tips_xml = xml.SubElement(
                self.mark_xml, "g", 
                attrib={"class": "toytree-TipLabels"}, 
                style=style_to_string(top_style),
            )

            # add tip markers from 0 to ntips
            for tidx, tip in enumerate(self.mark.tip_labels):

                # allowed positional styling
                pos_style = {
                    "font-family": 'helvetica',
                    "font-size": "11px",
                    "-toyplot-anchor-shift": "15px",
                    "baseline-shift": "0px",
                    "text-anchor": "start",
                }
                for sty in pos_style:
                    if sty in self.mark.tip_labels_style:
                        pos_style[sty] = self.mark.tip_labels_style[sty]

                # get offset as int in case it needs to be flipped
                offset = toyplot.units.convert(
                    pos_style["-toyplot-anchor-shift"], "px",
                )

                # assign tip to class depending on coordinates
                if self.mark.layout == "r":
                    angle = self.mark.tip_labels_angles[tidx]
                    pos_style["text-anchor"] = "start"
                    pos_style["-toyplot-anchor-shift"] = offset

                elif self.mark.layout == "l":
                    angle = self.mark.tip_labels_angles[tidx]  # + 180
                    pos_style["text-anchor"] = "end"
                    pos_style["-toyplot-anchor-shift"] = -offset

                elif self.mark.layout == 'd':
                    angle = self.mark.tip_labels_angles[tidx]
                    pos_style["text-anchor"] = "end"
                    pos_style["-toyplot-anchor-shift"] = -offset

                elif self.mark.layout == "u":
                    angle = self.mark.tip_labels_angles[tidx]  # + 180
                    pos_style["text-anchor"] = "start"
                    pos_style["-toyplot-anchor-shift"] = offset

                elif self.mark.layout == "c":
                    angle = self.mark.tip_labels_angles[tidx]  # * -1
                    pos_style["text-anchor"] = "start"
                    pos_style["-toyplot-anchor-shift"] = offset
                    if (angle < -90) & (angle > -270):
                        angle += 180
                        pos_style["text-anchor"] = "end"
                        pos_style["-toyplot-anchor-shift"] = -offset

                # align tip at end for tip_labels_align=True
                cx = self.nodes_x[tidx]
                cy = self.nodes_y[tidx]
                if self.mark.tip_labels_align:
                    cx = self.tips_x[tidx]
                    cy = self.tips_y[tidx]

                # angle of text
                transform = "translate({:.2f},{:.2f})".format(cx, cy)
                transform += "rotate({:.0f})".format(angle)

                # the position of the tip TextBox
                tip_xml = xml.SubElement(tips_xml, "g")
                tip_xml.set("transform", transform)

                # split unique color if 
                icolor = self.mark.tip_labels_colors[tidx]
                colordict = {}
                if icolor is not None:
                    # try splitting color:
                    try:
                        colordict = split_rgba_style({"fill": icolor})
                    except Exception:
                        colordict = {"fill": icolor}

                # get baseline given font-size, etc.,
                layout = toyplot.text.layout(
                    tip,
                    pos_style,
                    toyplot.font.ReportlabLibrary(),
                )

                for line in layout.children:
                    for box in line.children:
                        xml.SubElement(
                            tip_xml,
                            "text", 
                            x="{:.2f}".format(box.left), 
                            y="{:.2f}".format(box.baseline),
                            style=style_to_string(colordict),
                            ).text = tip


    # def mark_tip_labels(self):
    #     """
    #     Creates text elements for tip labels under class toytree-TipLabels.
    #     Styling here needs to support both linear, circular and unrooted trees,
    #     which is trick by combining style for -toyplot-anchor-shift and angles
    #     when setting transform.       
    #     """
    #     if not all([i is None for i in self.mark.tip_labels]):

    #         # end anchor style updated for user text style
    #         top_style = {
    #             'font-family': 'helvetica',
    #             'font-weight': 'normal',
    #             'white-space': 'pre',
    #             'fill': 'rgb(90.6%,54.1%,76.5%)',
    #             'fill-opacity': '1.0',
    #             'stroke': 'none',
    #             'text-anchor': 'end',
    #             'font-size': '9px',
    #         }
    #         for sty in top_style:
    #             if sty in self.mark.tip_labels_style:
    #                 top_style[sty] = self.mark.tip_labels_style[sty]

    #         # force text-anchor to end of L-tips
    #         top_style['text-anchor'] = 'end'

    #         # apply font styling but NOT POSITIONAL styling to group.
    #         tips_left_xml = xml.SubElement(
    #             self.mark_xml, "g", 
    #             attrib={"class": "toytree-Tiplabels-L"}, 
    #             style=style_to_string(top_style),
    #         )

    #         # apply font styling but not position stylilng to group.
    #         top_style = {
    #             'font-weight': 'normal',
    #             'white-space': 'pre',
    #             'fill': 'rgb(90.6%,54.1%,76.5%)',
    #             'fill-opacity': '1.0',
    #             'stroke': 'none',
    #             'text-anchor': 'end',
    #             'font-size': '9px',
    #         }
    #         for sty in top_style:
    #             if sty in self.mark.tip_labels_style:
    #                 top_style[sty] = self.mark.tip_labels_style[sty]
    #         top_style['text-anchor'] = 'start'
    #         tips_right_xml = xml.SubElement(
    #             self.mark_xml, "g", 
    #             attrib={"class": "toytree-Tiplabels-R"}, 
    #             style=style_to_string(top_style)
    #         )

    #         # add tip markers
    #         for tidx, tip in enumerate(self.mark.tip_labels):

    #             icolor = self.mark.tip_labels_colors[tidx]
    #             tdict = {}
    #             if icolor is not None:
    #                 # try splitting color:
    #                 try:
    #                     tdict = split_rgba_style({"fill": icolor})
    #                 except Exception:
    #                     tdict = {"fill": icolor}

    #             # assign tip to class depending on coordinates
    #             if self.mark.layout == "r":
    #                 parent = tips_right_xml
    #                 angle = self.mark.tip_labels_angles[tidx]
    #             elif self.mark.layout == "l":
    #                 parent = tips_left_xml
    #                 angle = self.mark.tip_labels_angles[tidx]
    #             elif self.mark.layout == "d":
    #                 parent = tips_left_xml
    #                 angle = self.mark.tip_labels_angles[tidx] + 90
    #             elif self.mark.layout == "u":
    #                 parent = tips_right_xml
    #                 angle = self.mark.tip_labels_angles[tidx] - 90
    #             elif self.mark.layout == "c":
    #                 angle = self.mark.tip_labels_angles[tidx]
    #                 if (angle > 90) and (angle < 270):
    #                     parent = tips_left_xml
    #                 else:
    #                     parent = tips_right_xml

    #             # short variables
    #             cx = self.nodes_x[tidx] 
    #             cy = self.nodes_y[tidx]
    #             style_pos = self.mark.tip_labels_style
    #             style_text = tdict
    #             title = None

    #             # align tip at end for tip_labels_align=True
    #             if self.mark.tip_labels_align:
    #                 cx = self.tips_x[tidx]
    #                 cy = self.tips_y[tidx]

    #             # get baseline given font-size, etc.,
    #             layout = toyplot.text.layout(
    #                 tip,
    #                 style_text,
    #                 toyplot.font.ReportlabLibrary(),
    #             )
    #             baseline = layout.children[0].children[0].baseline

    #             # adjust projections based on angle and shift args
    #             ashift = toyplot.units.convert(style_pos["-toyplot-anchor-shift"], "px")

    #             # if right facing then use anchor-shift to +x, else -x
    #             if parent.attrib['class'] == "toytree-Tiplabels-R":

    #                 # anchor shifts left, baseline corrects y
    #                 if self.mark.layout == "r":
    #                     cx += ashift
    #                     cy += baseline

    #                 # anchor shifts up, baseline shifts right, angle is 90
    #                 elif self.mark.layout == "u":
    #                     cx += baseline
    #                     cy -= ashift
    #                     angle += 90

    #                 # 
    #                 elif self.mark.layout == 'c':
    #                     # convert ashift to the angle
    #                     if not angle:
    #                         cx += ashift
    #                         cy += baseline
    #                     else:
    #                         # get lengths from trig.
    #                         trans = toyplot.transform.rotation(angle)[0]                
    #                         ashift_x = ashift * trans[0, 0]
    #                         ashift_y = ashift * trans[0, 1]
    #                         bshift_y = baseline * trans[0, 0]
    #                         bshift_x = baseline * trans[0, 1]
    #                         cx += ashift_x + bshift_x
    #                         cy -= ashift_y - bshift_y

    #             else:

    #                 # anchor shifts down, baseline shifts left, angle is -90
    #                 if self.mark.layout == "d":
    #                     cx += baseline
    #                     cy += ashift
    #                     angle += 90

    #                 elif self.mark.layout == 'l':
    #                     cx -= ashift
    #                     cy += baseline
    #                     angle += 180

    #                 elif self.mark.layout == 'c':
    #                     angle += 180

    #                     # get lengths from trig.
    #                     trans = toyplot.transform.rotation(angle)[0]                
    #                     ashift_x = ashift * trans[0, 0]
    #                     ashift_y = ashift * trans[0, 1]
    #                     bshift_y = baseline * trans[0, 0]
    #                     bshift_x = baseline * trans[0, 1]
    #                     cx = cx - ashift_x + bshift_x
    #                     cy = cy + ashift_y + bshift_y

    #             # project points into coordinate space 
    #             transform = "translate({:.2f},{:.2f})".format(cx, cy)
    #             if angle:
    #                 transform += "rotate({:.1f})".format(-angle)

    #             # create a group marker for positioning text
    #             if style_text:
    #                 group = xml.SubElement(
    #                     parent, "g", style=style_to_string(style_text))
    #             else:
    #                 group = xml.SubElement(parent, "g")
    #             group.set("transform", transform)

    #             # optionally add a title 
    #             if title is not None:
    #                 xml.SubElement(group, "title").text = str(title)

    #             # style text should only include unique styling which currently for 
    #             # nodes is nothing, and for tips is only 'fill' and 'fill-opacity'.
    #             xml.SubElement(group, "text").text = tip




    def mark_align_edges(self):
        """
        Creates SVG paths for from each tip to 0 or radius.
        """
        # get paths based on edge type and layout
        if self.mark.tip_labels_align:
            apaths = []
            for tidx in range(len(self.mark.tip_labels)):

                adict = {
                    'cx': self.nodes_x[tidx],
                    'cy': self.nodes_y[tidx],
                    'px': self.tips_x[tidx], 
                    'py': self.tips_y[tidx],
                }
                path = PATH_FORMAT['c'].format(**adict)
                apaths.append(path)

            # render the edge group
            self.align_xml = xml.SubElement(
                self.mark_xml, "g", 
                attrib={"class": "toytree-AlignEdges"}, 
                style=style_to_string(self.mark.edge_align_style),
            )

            # render the edge paths
            for idx, path in enumerate(apaths):
                xml.SubElement(
                    self.align_xml, "path",
                    d=path,
                    # style=None,
                )



    def mark_admixture_edges(self):
        """
        Creates an SVG path for an admixture edge. The edge takes the same
        style as the edge_type of the tree.
        """
        if self.mark.admixture_edges is None:
            return 

        # iterate over colors for subsequent edges unless provided
        colors = iter(COLORS1)
        next(colors)
        DEFAULT_ADMIXTURE_EDGES_STYLE = {
            "stroke": COLORS1[3], 
            "stroke-width": 5, 
            "stroke-opacity": 0.6,
            "stroke-linecap": "round", 
            "fill": "none",
        }

        # create edge group element
        self.admix_xml = xml.SubElement(
            self.mark_xml, 'g',
            attrib={'class': 'toytree-AdmixEdges'},
            style=style_to_string(DEFAULT_ADMIXTURE_EDGES_STYLE)
        )

        # get position of 15% tipward from source point
        PATH = [
            "M {sdx:.1f} {sdy:.1f}",
            "L {sux:.1f} {suy:.1f}",
            "L {ddx:.1f} {ddy:.1f}",
            "L {dux:.1f} {duy:.1f}",
        ]            

        # ensure admixture_edges is a list of tuples
        if not isinstance(self.mark.admixture_edges, list):
            self.mark.admixture_edges = [self.mark.admixture_edges]

        # drwa each edge
        for aedge in self.mark.admixture_edges:

            # check if nodes have an overlapping interval
            src, dest = aedge[0], aedge[1]

            # get timing as a proportion of the shared edge
            if len(aedge) > 2:
                aprop = aedge[2]
            else:
                aprop = 0.5

            # edge style
            estyle = {
                'stroke': next(colors),
                'stroke-opacity': '0.7',
            }

            # get custom style dict
            if len(aedge) > 3:
                estyle.update(aedge[3])

            # colorfix to edge styles
            colorfix = split_rgba_style(estyle.copy())
            estyle['stroke'] = colorfix['stroke']

            # # try to load timing floats for admixture edges
            # try:
            #     src_yprop = float(aedge[2])
            # except Exception:
            #     src_yprop = 0.5
            # try:
            #     dest_yprop = float(aedge[3])
            # except Exception:
            #     dest_yprop = 0.5
            # # check props
            # check0 = (src_yprop <= 1.0) & (src_yprop >= 0)
            # check1 = (dest_yprop <= 1.0) & (dest_yprop >= 0)
            # if not (check0 & check1):
            #     raise ToytreeError("admix timing must be between 0-1.")

            # get their parents coord positions
            ps = self.mark.etable[self.mark.etable[:, 1] == src, 0][0]
            pd = self.mark.etable[self.mark.etable[:, 1] == dest, 0][0]

            # get selected nodes' coordinate positions 
            if self.mark.layout in ("r", "l"):
                sx, sy = self.nodes_y[src], self.nodes_x[src]
                dx, dy = self.nodes_y[dest], self.nodes_x[dest]
                psx, psy = self.nodes_y[ps], self.nodes_x[ps]
                pdx, pdy = self.nodes_y[pd], self.nodes_x[pd]

            else:
                sx, sy = self.nodes_x[src], self.nodes_y[src]
                dx, dy = self.nodes_x[dest], self.nodes_y[dest]
                psx, psy = self.nodes_x[ps], self.nodes_y[ps]
                pdx, pdy = self.nodes_x[pd], self.nodes_y[pd]

            # get height of the admix line at midshared.
            # admix_src_y = (min([sy, dy]) + max([psy, pdy])) * src_yprop
            # admix_dest_y = (min([sy, dy]) + max([psy, pdy])) * dest_yprop
            admix_ymid = (min([sy, dy]) + max([psy, pdy])) / 2.

            # sample in the 20-80 % of edge range.
            amin = min([sy, dy])
            amax = max([psy, pdy])
            admix_ymid = np.random.uniform(
                amin + (amax - amin) * aprop,
                amax - (amax - amin) * (1 - aprop),
            )

            # how far down does SRC direction line go
            src_down_extend = (sy - admix_ymid) / 2.
            src_tip_y = max([sy, admix_ymid + src_down_extend])

            # how far up does DEST direction line go
            dest_up_extend = (pdy - admix_ymid) / 2.
            dest_tip_y = min([pdy, admix_ymid - dest_up_extend])

            # project angle of up/down lines towards parent nodes.
            if self.mark.edge_type == "c":            

                # angle from src to src parent
                theta = np.arctan((psy - sy) / (psx - sx))

                # x-shift from src to src_up_y
                x_shift_src_tip = (src_tip_y - sy) / np.tan(theta)

                # x-shift from src to admix_ymid
                x_shift_src_mid = (admix_ymid - sy) / np.tan(theta)

                # angle from dest to dest parent
                theta = np.arctan((pdy - dy) / (pdx - dx))

                # x-shift from dest to dest_tip_y
                x_shift_dest_mid = (admix_ymid - dy) / np.tan(theta)

                # x-shift from dest to dest_tip_y
                x_shift_dest_tip = (dest_tip_y - dy) / np.tan(theta)

            else:
                x_shift_dest_mid = x_shift_dest_tip = 0
                x_shift_src_mid = x_shift_src_tip = 0

            # nudge admix line to left or right of tree edges
            if self.mark.edge_widths[src] is None:
                snudge = (2 + (self.mark.edge_style["stroke-width"] / 2.))
            else:
                snudge = self.mark.edge_widths[src]

            # get offset of admix edge based on stroke of DEST tree edge
            if self.mark.edge_widths[dest] is None:
                dnudge = (2 + (self.mark.edge_style["stroke-width"] / 2.))
            else:
                dnudge = self.mark.edge_widths[dest]

            snudge = (-1 * snudge if sx > psx else snudge)
            dnudge = (-1 * dnudge if dx > pdx else dnudge)
            snudge = dnudge = 0

            # build the SVG path
            if self.mark.layout in ("r", "l"):
                edge_dict = {
                    'sdy': sx + x_shift_src_tip + snudge,
                    'sdx': src_tip_y, 
                    'suy': sx + x_shift_src_mid + snudge,
                    'sux': admix_ymid,
                    'ddy': dx + x_shift_dest_mid + dnudge,
                    'ddx': admix_ymid,
                    'duy': dx + x_shift_dest_tip + dnudge,
                    'dux': dest_tip_y,
                }
                tri_dict = {
                    'x0': admix_ymid - 6,
                    'x1': admix_ymid + 6,
                    'x2': admix_ymid,
                    'y0': np.mean([edge_dict['suy'], edge_dict['ddy']]) - 6,
                    'y1': np.mean([edge_dict['suy'], edge_dict['ddy']]) - 6,
                    'y2': np.mean([edge_dict['suy'], edge_dict['ddy']]) + 8,
                }

            else:            
                edge_dict = {
                    'sdx': sx + x_shift_src_tip + snudge,
                    'sdy': src_tip_y, 
                    'sux': sx + x_shift_src_mid + snudge,
                    'suy': admix_ymid,
                    'ddx': dx + x_shift_dest_mid + dnudge,
                    'ddy': admix_ymid,
                    'dux': dx + x_shift_dest_tip + dnudge,
                    'duy': dest_tip_y,
                }

                # TODO: not finished aligning triangle/arrow
                tri_dict = {
                    'y0': admix_ymid - 6,
                    'y1': admix_ymid + 6,
                    'y2': admix_ymid,
                    'x0': np.mean([edge_dict['suy'], edge_dict['ddy']]) - 6,
                    'x1': np.mean([edge_dict['suy'], edge_dict['ddy']]) - 6,
                    'x2': np.mean([edge_dict['suy'], edge_dict['ddy']]) + 8,
                }

            # EDGE path                
            path = " ".join(PATH).format(**edge_dict)

            # RENDER edge paths
            xml.SubElement(
                self.admix_xml, "path",
                d=path,
                style=style_to_string(estyle),
            )

            # RENDER TRIANGLE
            # xml.SubElement(
            #     self.admix_xml, "polygon",
            #     points=(
            #         "{:.0f},{:.0f} {:.0f},{:.0f} {:.0f},{:.0f}"
            #         .format(
            #             tri_dict['x0'], tri_dict['y0'],
            #             tri_dict['x1'], tri_dict['y1'],
            #             tri_dict['x2'], tri_dict['y2'],
            #         )
            #     ),
            #     attrib={
            #         "fill": self.mark.admixture_edges_style["stroke"],
            #         "stroke-dasharray": "0,0",
            #     },
            # )
            # markup.set("transform", "rotate({})".format(-angle))


        # _draw_triangle(marker_xml, marker.size, angle=90)
        # def _draw_triangle(parent_xml, size, angle=0):
        # markup = xml.SubElement(
        #     parent_xml,
        #     "polygon",
        #     points=" ".join(["%r,%r" % (xp, yp) for xp, yp in [
        #        (-size / 2, size / 2),
        #        (0, -size / 2),
        #        (size / 2, size / 2),
        #        ]]),
        #     )
        # if angle:
        #     markup.set("transform", "rotate(%r)" % (-angle,))




@dispatch(toyplot.coordinates.Cartesian, ToytreeMark, toyplot.html.RenderContext)
def _render(axes, mark, context):
    RenderToytree(axes, mark, context)





# HELPER FUNCTIONS ----------------------




def get_unique_edge_styles(mark):
    """
    Reduces node styles to prevent redundancy in HTML.
    """
    # minimum styling of node markers
    unique_styles = [{} for i in range(mark.etable.shape[0])]

    # if edge widths and edge colors are both empty then just return
    check0 = all([i is None for i in mark.edge_colors])
    check1 = all([i is None for i in mark.edge_widths])
    if check0 & check1:
        return unique_styles

    # iterate through styled node marks to get shared styles and expand axes
    for idx in range(mark.etable.shape[0]):

        if mark.edge_widths[idx] is not None:
            unique_styles[idx]['stroke-width'] = mark.edge_widths[idx]

        if mark.edge_colors[idx] is not None:
            subd = split_rgba_style({'stroke': mark.edge_colors[idx]})
            unique_styles[idx]['stroke'] = subd['stroke']
            if subd['stroke-opacity'] != mark.edge_style["stroke-opacity"]:
                unique_styles[idx]['stroke-opacity'] = subd['stroke-opacity']

    return unique_styles




def split_rgba_style(style):
    """
    Because many applications (Inkscape, Adobe Illustrator, Qt) don't handle 
    CSS rgba() colors correctly this function does a work-around.
    Takes a CSS color in rgba, e.g., 'rgba(40.0%,76.1%,64.7%,1.000)' 
    labeled in a dictionary as {'fill': x, 'fill-opacity': y} and 
    returns with fill as rgb and fill-opacity from rgba or clobbered
    by the fill-opacity arg. Similar functionality for stroke, stroke-opacity.
    """
    if "fill" in style:
        color = style['fill']
        try:
            color = toyplot.color.css(color)
        except (TypeError, AttributeError):
            # print(type(color), color)
            pass

        if str(color) == "none":
            style["fill"] = "none"
            style["fill-opacity"] = 1.0
        else:
            rgb = "rgb({:.3g}%,{:.3g}%,{:.3g}%)".format(
                color["r"] * 100, 
                color["g"] * 100, 
                color["b"] * 100,
            )
            style["fill"] = rgb
            style["fill-opacity"] = str(color["a"])


    if "stroke" in style:
        color = style['stroke']
        try:
            color = toyplot.color.css(color)
        except (TypeError, AttributeError):
            # print(type(color), color)            
            pass

        if str(color) == "none":
            style["stroke"] = "none"
            style["stroke-opacity"] = 1.0
        else:
            rgb = "rgb({:.3g}%,{:.3g}%,{:.3g}%)".format(
                color["r"] * 100, 
                color["g"] * 100, 
                color["b"] * 100,
            )
            style["stroke"] = rgb
            style["stroke-opacity"] = str(color["a"])
    return style




def style_to_string(style):
    """
    Takes a style dict and writes to ordered style text:     
    input: {'fill': 'rgb(100%,0%,0%', 'fill-opacity': 1.0}
    returns: 'fill:rgb(100%,0%,0%);fill-opacity:1.0'
    """
    strs = ["{}:{}".format(key, value) for key, value in sorted(style.items())]
    return ";".join(strs)





# def check_admix_tuple_args(args):
#     """
#     Split list into bits.
#     """
#     # check that the argument is a list
#     assert isinstance(args, list), (
#         "admixture edges should be a list of tuples")

#     # iterate over the tuples
#     admixture_edges = []
#     for tup in args:

#         # parse required args
#         source = tup[0]
#         dest = tup[1]

#         # parse optional args
#         try:
#             height = tup[2]
#         except IndexError:
#             height = None

#         try:
#             width = (tup[3] if tup[3] else 3)
#         except IndexError:
#             width = 3

#         try:
#             color = (tup[4] if tup[4] else next(self.colors))
#         except IndexError:
#             color = next(self.colors)

#         try:
#             offset = (tup[5] if tup[5] else 0.05)
#         except IndexError:
#             offset = 0.05

#         # put it back into list as full tuples
#         admixture_edges.append(
#             (source, dest, height, style)



# # TODO
# def _render_text_file(owner, key, label, table, filename, context):
#     """
#     A variant of toyplot.html._render_table that can be used instead
#     to download a text file.
#     """
#     if isinstance(owner, toyplot.mark.Mark) and owner.annotation:
#         return
#     if isinstance(owner, toyplot.coordinates.Table) and owner.annotation:
#         return

#     names = []
#     columns = []

#     if isinstance(table, toyplot.data.Table):
#         for name, column in table.items():
#             if "toyplot:exportable" in table.metadata(name) and table.metadata(name)["toyplot:exportable"]:
#                 if column.dtype == toyplot.color.dtype:
#                     raise ValueError("Color column table export isn't supported.") # pragma: no cover
#                 else:
#                     names.append(name)
#                     columns.append(column.tolist())
#     else: # Assume numpy matrix
#         for column in table.T:
#             names.append(column[0])
#             columns.append(column[1:].tolist())

#     if not (names and columns):
#         return

#     owner_id = context.get_id(owner)
#     if filename is None:
#         filename = "toyplot"

#     context.require(
#         dependencies=["toyplot/menus/context", "toyplot/io"],
#         arguments=[owner_id, key, label, names, columns, filename],
#         code="""function(tables, context_menu, io, owner_id, key, label, names, columns, filename)
#         {
#             tables.set(owner_id, key, names, columns);

#             var owner = document.querySelector("#" + owner_id);
#             function show_item(e)
#             {
#                 return owner.contains(e.target);
#             }

#             function choose_item()
#             {
#                 io.save_file("text/csv", "utf-8", tables.get_csv(owner_id, key), filename + ".csv");
#             }

#             context_menu.add_item("Save " + label + " as CSV", show_item, choose_item);
#         }""",
#     )
