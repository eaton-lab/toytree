#!/usr/bin/env python

"""
A custom Mark and mark generator to create Toytree drawings in toyplot.
"""

import numpy as np
import xml.etree.ElementTree as xml
import toyplot
from toyplot.mark import Mark
from toyplot.coordinates import _mark_exportable
from toyplot.html import _draw_bar, _draw_triangle, _draw_circle, _draw_rect
from multipledispatch import dispatch

# Register multipledispatch to share with toyplot.html
import functools
dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)

"""
TODO: 
- tip labels align: just another set of node coords and edges, all M.. L.. 
- extents when tip labels is empty/false
- extents on all layouts with long names


- do not draw node if no size...
- NodeLabels style has #262626
- Do not set custom fill on tips if not variable.
- allow xbaseline ybaseline args.
"""


PATH_FORMAT = {
    'c': "M {xs:.3f} {ys:.3f} L {xe:.3f} {ye:.3f}",
    'p': "M {xs:.3f} {ys:.3f} L {xs:.3f} {ye:.3f} L {xe:.3f} {ye:.3f}",
    'b': "M {xs:.3f} {ys:.3f} C {xs:.3f} {ye:.3f}, {xs:.3f} {ye:.3f}, {xe:.3f} {ye:.3f}",
    'f': "M {xs:.3f} {ys:.3f} A {} {}, 0, 0, {}, {xe:.3f} {ye:.3f}",
}


class Toytree(Mark):
    """
    Custom mark testing.
    """
    def __init__(
        self, 
        coordinate_axes, 
        ntable, 
        node_colors, 
        node_sizes, 
        node_style,
        node_shapes,
        etable,
        edge_colors,
        edge_widths,
        edge_type,
        edge_style,
        tip_labels,
        tip_labels_angles,
        tip_labels_colors,
        tip_labels_style,
        node_labels,
        node_labels_style,
        edge_align_style,
        layout,
        tree_height,
        ):
        # ecolor, ecoords, eopacity, eshape, estyle, etable, etarget):

        # inherit type
        Mark.__init__(self)

        # check arg types
        self._coordinate_axes = ['x', 'y']  
        self.layout = layout
        self.tree_height = tree_height

        # store anything here that you want available as tool-tip hovers
        self.ntable = toyplot.require.instance(ntable, toyplot.data.Table)
        self.etable = toyplot.require.instance(etable, toyplot.data.Table)

        # node plotting args
        self.node_colors = node_colors
        self.node_sizes = node_sizes
        self.node_shapes = node_shapes
        self.node_style = node_style 

        # edge (tree) plotting args
        self.edge_colors = edge_colors
        self.edge_widths = edge_widths
        self.edge_style = edge_style
        self.edge_type = edge_type

        # tip labels
        self.tip_labels = tip_labels
        self.tip_labels_angles = tip_labels_angles
        self.tip_labels_colors = tip_labels_colors
        self.tip_labels_style = tip_labels_style

        # node labels
        self.node_labels = node_labels
        self.node_labels_style = node_labels_style


    @property
    def nnodes(self):
        return self.ntable.shape[0]


    def domain(self, axis):
        """
        The domain of data that will be tracked.
        """
        domain = toyplot.data.minimax([self.ntable[axis]])
        return domain


    def extents(self, axes):
        """
        Extends borders to fit tip names without extending the domain.
        The main component to worry about here is tip labels text, especially
        for weird layouts that make it angled. For circular we project text
        at angle and inverted angle to get projection from anchor start and end

        extents is [l, r, b, t] for each textbox
        """

        # for radial trees we want extents to fit similar in all directions
        # regardless of branch and tip name lengths. So find the radius of 
        # the circle + anchor shift + longest name and pass in all directions.
        if self.layout == "c":
            coords = (
                self.tree_height * np.array([-1, 0, 1, 0]),
                self.tree_height * np.array([0, 1, 0, -1]),
            )

            # get the maxwidth of any tips ignoring positioning
            if np.all(self.tip_labels == None):
                empty = np.array([])                
                extents = tuple([empty] * 2), tuple([empty] * 4)

            else:
                tips = self.tip_labels
                exts = toyplot.text.extents(
                    tips, 0, {"font-size": self.tip_labels_style["font-size"]}
                )
                print(exts)
                maxw = max([exts[1][i] - exts[0][i] for i in range(len(tips))])
                ashift = toyplot.units.convert(
                    self.tip_labels_style["-toyplot-anchor-shift"], "px")
                extents = (
                    np.repeat(0 - ashift - maxw * 1.5, 4),  # left ext
                    np.repeat(0 + ashift + maxw * 1.5, 4),  # right ext
                    np.repeat(0 - ashift - maxw * 1.5, 4),  # bottom
                    np.repeat(0 + ashift + maxw * 1.5, 4),  # top
                )

        # all other layouts 
        else:
            coords = (
                self.ntable['x', :len(self.tip_labels)],
                self.ntable['y', :len(self.tip_labels)],
            )
            # extents = []
            # for tip in 
            extents = toyplot.text.extents(
                self.tip_labels,
                self.tip_labels_angles,
                (self.tip_labels_style if self.tip_labels[0] else {}),
            )

        return coords, extents



def toytree_mark(
    ttree,
    layout=None,
    node_sizes=None,
    node_colors=None,
    node_shapes=None,
    node_style=None,
    edge_colors=None,
    edge_widths=None,
    edge_style=None,
    edge_type=None,
    tip_labels=None,
    tip_labels_colors=None,
    tip_labels_angles=None,
    tip_labels_style=None,
    node_labels=None,
    node_labels_style=None,
    edge_align_style=None,
    ):
    """
    A convenience function for generating Marks with minimum args and 
    checking input types, lens, and allowed styles.
    """
    ttree.style.layout = layout
    ttree._coords.update()
    verts = ttree._coords.verts
    nnodes = ttree.nnodes
    nedges = ttree._coords.edges.shape[0]
    ntips = ttree.ntips
    tree_height = ttree.treenode.height

    # node style setup
    ntable = toyplot.data.Table()
    ntable['idx'] = range(nnodes)
    ntable['x'] = verts[:, 0]
    ntable['y'] = verts[:, 1]
    node_sizes = toyplot.broadcast.scalar(node_sizes, nnodes)
    node_shapes = toyplot.broadcast.pyobject(node_shapes, nnodes)
    node_colors = toyplot.broadcast.pyobject(node_colors, nnodes)
    node_style = toyplot.style.require(node_style, toyplot.style.allowed.marker)
    # node_colors = toyplot.color.broadcast(node_colors, nnodes, "none")

    # edge style setup (exposing edges could allow tooltip funcs.)
    etable = toyplot.data.Table()
    etable['idx'] = range(nedges)
    etable['parent'] = ttree._coords.edges[:, 0]
    etable['child'] = ttree._coords.edges[:, 1]
    edge_widths = toyplot.broadcast.scalar(edge_widths, nedges)
    edge_colors = toyplot.broadcast.scalar(edge_colors, nedges)
    edge_type = (edge_type if edge_type else "p")
    edge_style = toyplot.style.require(edge_style, toyplot.style.allowed.line)

    # tip labels
    # ttable = toyplot.data.Table()
    # ttable['idx'] = range(ntips)
    # ttable['x'] = verts[:ntips, 0]
    # ttable['y'] = verts[:ntips, 1]
    # ttable['text'] = toyplot.broadcast.pyobject(tip_labels, ntips)
    # ttable['angle'] = toyplot.broadcast.scalar(0, ntips)
    tip_labels = toyplot.broadcast.pyobject(tip_labels, ntips)
    tip_labels_colors = toyplot.color.broadcast(tip_labels_colors, ntips, "#262626")

    # a dictionary with required
    def_tl_style = {'-toyplot-anchor-shift': "15px", 'text-anchor': "start"}
    def_tl_style.update(tip_labels_style)
    tip_labels_style = def_tl_style
    tip_labels_style = toyplot.style.require(
        tip_labels_style, toyplot.style.allowed.text)

    node_labels = toyplot.broadcast.pyobject(node_labels, nnodes)
    node_labels_style = (node_labels_style if node_labels_style else {})
    node_labels_style = toyplot.style.require(
        node_labels_style, toyplot.style.allowed.text)

    # expose node coordinates and edges for tooltip functions and projecting.
    _mark_exportable(ntable, 'x')
    _mark_exportable(ntable, 'y')
    _mark_exportable(etable, 'parent')
    _mark_exportable(etable, 'child')

    return Toytree(
        coordinate_axes=['x', 'y'],
        layout=layout,
        tree_height=tree_height,

        ntable=ntable,
        node_colors=node_colors,
        node_sizes=node_sizes,
        node_shapes=node_shapes,
        node_style=node_style, 

        etable=etable,
        edge_widths=edge_widths,
        edge_colors=edge_colors,
        edge_type=edge_type,
        edge_style=edge_style,

        # ttable=ttable,
        tip_labels=tip_labels,
        tip_labels_colors=tip_labels_colors,
        tip_labels_angles=tip_labels_angles,
        tip_labels_style=tip_labels_style,

        node_labels=node_labels,
        node_labels_style=node_labels_style,

        edge_align_style=edge_align_style,
    )



def get_shared_node_styles(mark):
    """
    Reduces node styles to prevent redundancy in HTML.
    """
    # minimum styling of node markers
    unique_styles = {
        'fill': [],
        'fill-opacity': [],
        'stroke': [],
        'stroke-opacity': [],
        'stroke-width': [],
    }

    # iterate through styled node marks to get shared styles and expand axes
    for idx in range(mark.nnodes):

        # all shared keys (shape, size, fill, opacity, stroke-width, etc.)
        nstyle = toyplot.style.combine(unique_styles, mark.node_style)

        # iterate over sorted so fill before fill-opacity.
        for key in sorted(nstyle):

            # special care for colors (override fill if not None)
            if key == "fill":
                if mark.node_colors[idx] is not None:
                    nstyle['fill'] = mark.node_colors[idx]

                if nstyle['fill']:
                    subd = split_rgba_style({'fill': nstyle['fill']})
                    nstyle['fill'] = subd['fill']
                    nstyle['fill-opacity'] = subd['fill-opacity']

            # special care for colors (override fill if not None)
            if key == "stroke":
                if nstyle['stroke']:
                    subd = split_rgba_style({'stroke': nstyle['stroke']})
                    nstyle['stroke'] = subd['stroke']
                    nstyle['stroke-opacity'] = subd['stroke-opacity']

            # if this is a key from nstyle dict
            if key not in unique_styles:
                unique_styles[key] = [nstyle[key]]
            else:
                unique_styles[key].append(nstyle[key])      

    # find shared styles and pop from uniques
    shared_styles = {}
    for key in unique_styles:
        if len(set([str(i) for i in unique_styles[key]])) == 1:
            shared_styles[key] = unique_styles[key][0]
    unique_styles = {
        i: j for (i, j) in unique_styles.items() if i not in shared_styles
    }
    return shared_styles, unique_styles



def get_shared_edge_styles(mark):
    """
    Reduces node styles to prevent redundancy in HTML.
    """
    # minimum styling of node markers
    unique_styles = {
        'stroke': [],
        'stroke-opacity': [],
        'stroke-width': [],
    }

    # iterate through styled node marks to get shared styles and expand axes
    for idx in range(mark.etable.shape[0]):

        # all shared keys (shape, size, fill, opacity, stroke-width, etc.)
        estyle = toyplot.style.combine(unique_styles, mark.edge_style)

        # iterate over sorted so fill before fill-opacity.
        for key in sorted(estyle):

            # special care for colors (override fill if not None)
            if key == "stroke-width":
                if mark.edge_widths[idx] is not None:
                    estyle['stroke-width'] = mark.edge_widths[idx]

            # special care for colors (override fill if not None)
            if key == "stroke":
                if estyle['stroke']:
                    subd = split_rgba_style({'stroke': estyle['stroke']})
                    estyle['stroke'] = subd['stroke']
                    estyle['stroke-opacity'] = subd['stroke-opacity']

            # if this is a key from nstyle dict
            if key not in unique_styles:
                unique_styles[key] = [estyle[key]]
            else:
                unique_styles[key].append(estyle[key])

    # find shared styles and pop from uniques
    shared_styles = {}
    for key in unique_styles:
        if len(set([str(i) for i in unique_styles[key]])) == 1:
            shared_styles[key] = unique_styles[key][0]
    unique_styles = {
        i: j for (i, j) in unique_styles.items() if i not in shared_styles
    }
    return shared_styles, unique_styles



def get_paths(mark, nodes_x, nodes_y):
    """
    # get edge table shape based on edge and layout types
    # 'p': M x y L x y                  # phylogram
    # 'c': M x y L x y L x y            # cladogram
    # 'b': M x y C x y, x y, x y        # bezier phylogram
    # 'f': M x y A r r, x, a, f, x y    # arcs/circle tree
    """
    path_format = PATH_FORMAT[mark.edge_type]
    paths = []
    # countdown from root node idx to tips
    for eidx in range(mark.etable.shape[0] - 1, -1, -1):

        # get parent and child
        pidx = mark.etable['parent', eidx]
        xs, ys = (nodes_x[pidx], nodes_y[pidx])
        cidx = mark.etable['child', eidx]
        xe, ye = (nodes_x[cidx], nodes_y[cidx])

        # build path string
        path = path_format.format(**{
            'xs': xs, 'ys': ys, 'xe': xe, 'ye': ye,
        })
        paths.append(path)
    return paths



class RenderToytree:
    """
    Organized class to call within _render
    """
    def __init__(self, axes, mark, context):

        # inputs
        self.mark = mark
        self.axes = axes
        self.context = context

        # to be constructed
        self.mark_xml = None
        self.edges_xml = None

        # construction funcs
        self.project_coordinates()
        self.build_dom()


    def build_dom(self):
        """
        Creates DOM of xml.SubElements in self.context.
        """
        self.mark_toytree()
        self.mark_edges()
        self.mark_nodes()
        self.mark_node_labels()
        self.mark_tip_labels()



    def project_coordinates(self):
        """
        Stores node coordinates (data units) projecting as pixel units.
        """
        self.nodes_x = self.axes.project('x', self.mark.ntable['x'])
        self.nodes_y = self.axes.project('y', self.mark.ntable['y'])


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
        paths = get_paths(self.mark, self.nodes_x, self.nodes_y)

        # get shared versus unique styles
        shared_styles, unique_styles = get_shared_edge_styles(self.mark)
        shared_styles['fill'] = "none"

        # render the edge group
        self.edges_xml = xml.SubElement(
            self.mark_xml, "g", 
            attrib={"class": "toytree-Edges"}, 
            style=style_to_string(
                {i: shared_styles[i] for i in shared_styles}),
        )

        # render the edge paths
        for idx, path in enumerate(paths):
            xml.SubElement(
                self.edges_xml, "path",
                d=path,
                style=style_to_string(
                    {i: unique_styles[i][idx] for i in unique_styles}
                )
            )


    def mark_nodes(self):
        """
        Creates marker elements for each node under class toytree-Nodes.
        This could store ids to the nodes if we planned some interesting
        downstream JS interactivity...
        """
        if not np.all([self.mark.node_sizes == 0]):
            # get shared versus unique styles
            shared_styles, unique_styles = get_shared_node_styles(self.mark)

            # render the nodes
            self.nodes_xml = xml.SubElement(
                self.mark_xml, "g", 
                attrib={"class": "toytree-Nodes"}, 
                style=style_to_string(
                    {i: shared_styles[i] for i in shared_styles}),
            )

            # add node markers to node xml
            for idx in range(self.mark.nnodes):
                # create marker with shape and size, e.g., <marker='o' size=12>
                marker = toyplot.marker.create(
                    shape=self.mark.node_shapes[idx], 
                    size=self.mark.node_sizes[idx],
                    mstyle={i: unique_styles[i][idx] for i in unique_styles},
                )

                # turn marker into proper svg
                custom_draw_marker(
                    root=self.nodes_xml,
                    marker=marker,
                    cx=self.nodes_x[idx],
                    cy=self.nodes_y[idx],
                    extra_class="toytree-node",
                    title=None,#mark.ntable["idx"][idx], 
                )


    def mark_node_labels(self):
        """
        Creates text elements for node label under class toytree-NodeLabels.
        toytree-NodeLabels stores shared text styling but no positional style,
        and positional styling is interpreted and applied using transform
        methods in 'custom_draw_text' func, with unique text styling applied
        there (only 'fill' currently supported).
        """
        if not np.all([self.mark.node_labels == None]):

            # make xml with non-positioning styles that apply to all text
            style_group = {}
            exc = ["baseline-shift", "-toyplot-anchor-shift", "text-anchor"]
            style_pos = {"text-anchor": "middle", "stroke": "none"}
            style_pos.update(self.mark.node_labels_style)
            style_pos = split_rgba_style(style_pos)
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
            for idx in range(self.mark.nnodes - 1, -1, -1):

                label = self.mark.node_labels[::-1][idx]
                if label not in ("", " ", None):
                    custom_draw_text(
                        root=nlabels_xml,
                        text=str(label),
                        cx=self.nodes_x[idx],
                        cy=self.nodes_y[idx],
                        style_pos=style_pos,
                        style_text={},
                        angle=0,
                        title=self.mark.ntable["idx", idx],
                    )


    def mark_tip_labels(self):
        """
        Creates text elements for tip labels under class toytree-TipLabels.
        Styling here needs to support both linear, circular and unrooted trees,
        which is trick by combining style for -toyplot-anchor-shift and angles
        when setting transform.       
        """
        if self.mark.tip_labels[0] is not None:

            # end anchor style updated for user text style
            top_style = {
                'font-weight': 'normal',
                'stroke': 'none',
                'white-space': 'pre',
                'text-anchor': 'end',
                'font-size': '9px',
            }
            for sty in top_style:
                if sty in self.mark.tip_labels_style:
                    top_style[sty] = self.mark.tip_labels_style[sty]
            top_style['text-anchor'] = 'end'

            # apply font styling but not position stylilng to group.
            tips_left_xml = xml.SubElement(
                self.mark_xml, "g", 
                attrib={"class": "toytree-Tiplabels-L"}, 
                style=style_to_string(top_style),
            )

            # apply font styling but not position stylilng to group.
            top_style = {
                'font-weight': 'normal',
                'stroke': 'none',
                'white-space': 'pre',
                'text-anchor': 'start',
                'font-size': '9px',
            }
            for sty in top_style:
                if sty in self.mark.tip_labels_style:
                    top_style[sty] = self.mark.tip_labels_style[sty]
            top_style['text-anchor'] = 'start'
            tips_right_xml = xml.SubElement(
                self.mark_xml, "g", 
                attrib={"class": "toytree-Tiplabels-R"}, 
                style=style_to_string(top_style)
            )

            # add tip markers
            for tidx, tip in enumerate(self.mark.tip_labels):

                # ONLY if variable tip colors
                tdict = {}
                color = self.mark.tip_labels_colors[tidx]
                if color:
                    tdict = split_rgba_style({"fill": color})

                # assign tip to class depending on coordinates
                if self.mark.layout == "r":
                    parent = tips_right_xml
                    angle = self.mark.tip_labels_angles[tidx]
                elif self.mark.layout == "l":
                    parent = tips_left_xml
                    angle = self.mark.tip_labels_angles[tidx]
                elif self.mark.layout == "d":
                    parent = tips_left_xml
                    angle = self.mark.tip_labels_angles[tidx] + 90
                elif self.mark.layout == "u":
                    parent = tips_right_xml
                    angle = self.mark.tip_labels_angles[tidx] - 90
                elif self.mark.layout == "c":
                    angle = self.mark.tip_labels_angles[tidx]
                    if (angle > 90) and (angle < 270):
                        parent = tips_left_xml
                    else:
                        parent = tips_right_xml

                # short variables
                cx = self.nodes_x[tidx] 
                cy = self.nodes_y[tidx]
                style_pos = self.mark.tip_labels_style
                style_text = tdict
                title = None

                # get baseline given font-size, etc.,
                layout = toyplot.text.layout(
                    tip,
                    style_text,
                    toyplot.font.ReportlabLibrary(),
                )
                baseline = layout.children[0].children[0].baseline

                # adjust projections based on angle and shift args
                ashift = toyplot.units.convert(style_pos["-toyplot-anchor-shift"], "px")

                # if right facing then use anchor-shift to +x, else -x
                if parent.attrib['class'] == "toytree-Tiplabels-R":

                    # anchor shifts left, baseline corrects y
                    if self.mark.layout == "r":
                        cx += ashift
                        cy += baseline

                    # anchor shifts up, baseline shifts right, angle is 90
                    elif self.mark.layout == "u":
                        cx += baseline
                        cy -= ashift
                        angle += 90

                    # 
                    elif self.mark.layout == 'c':
                        # convert ashift to the angle
                        if not angle:
                            cx += ashift
                            cy += baseline
                        else:
                            # get lengths from trig.
                            trans = toyplot.transform.rotation(angle)[0]                
                            ashift_x = ashift * trans[0, 0]
                            ashift_y = ashift * trans[0, 1]
                            bshift_y = baseline * trans[0, 0]
                            bshift_x = baseline * trans[0, 1]
                            cx += ashift_x + bshift_x
                            cy -= ashift_y - bshift_y

                else:

                    # anchor shifts down, baseline shifts left, angle is -90
                    if self.mark.layout == "d":
                        cx += baseline
                        cy += ashift
                        angle += 90

                    elif self.mark.layout == 'l':
                        cx -= ashift
                        cy += baseline
                        angle += 180

                    elif self.mark.layout == 'c':
                        angle += 180

                        # get lengths from trig.
                        trans = toyplot.transform.rotation(angle)[0]                
                        ashift_x = ashift * trans[0, 0]
                        ashift_y = ashift * trans[0, 1]
                        bshift_y = baseline * trans[0, 0]
                        bshift_x = baseline * trans[0, 1]
                        cx = cx - ashift_x + bshift_x
                        cy = cy + ashift_y + bshift_y

                # project points into coordinate space 
                transform = "translate({:.2f},{:.2f})".format(cx, cy)
                if angle:
                    transform += "rotate(%r)" % (-angle)

                # create a group marker for positioning text
                group = xml.SubElement(
                    parent, "g", style=style_to_string(style_text))
                group.set("transform", transform)

                # optionally add a title 
                if title is not None:
                    xml.SubElement(group, "title").text = str(title)

                # style text should only include unique styling which currently for 
                # nodes is nothing, and for tips is only 'fill' and 'fill-opacity'.
                xml.SubElement(group, "text").text = tip






    def mark_tip_labels_align(self):
        """
        ...
        """

        # make the group with text style but not position styles
        align_edges_xml = xml.SubElement(
            self.mark_xml, "g", 
            attrib={"class": "toytree-AlignEdges"}, 
            style=toyplot.style.to_css(style_group),
        )




@dispatch(toyplot.coordinates.Cartesian, Toytree, toyplot.html.RenderContext)
def _render(axes, mark, context):
    RenderToytree(axes, mark, context)





def combine_text_style(root, text, x, y, angle, style):
    """
    Combines default text styling with provided ...
    """
    # update style 
    style = toyplot.style.combine({"font-family": "helvetica"}, style)

    # update coordinates
    if x or y:
        transform = "translate({:.4f},{:.4f})".format(x, y)
    if angle:
        transform += "rotate(%r)" % (-angle)

    group = xml.SubElement(root, "g")
    if transform:
        group.set("transform", transform)



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

        if color is not None:
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

        if color is not None:
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




def custom_draw_text(root, text, cx, cy, style_pos, style_text, angle, title):
    """ 
    This is modified from toyplot.html._draw_text(). It is simplified
    for my simpler purposes and prevents style duplication.
    This could probably be made faster if layout was not called on every
    tip...

    The difficult thing about this func is making it work for both nodes and 
    tips. Split into two funcs (TODO). 

    the Tranform should be easy for tip labels if we enforce that they are 
    always text-anchor start then we don't even need to mess with 



    """
    # get a layout by applying full styling for positioning: this must include
    # font-affecting styles like font-size, font-weight, text-anchor: middle,
    # because these matter based on the size of characters. If these are not
    # specified it inherits the base styles from Canvas (e.g., font-size: 12px)    

    # It is simpler to not include here baseline-shift, -toyplot-anchor-shift
    # since these can be added to cx, cy to move the group.
    # exc = []#"-toyplot-anchor-shift", "baseline-shift"]
    layout = toyplot.text.layout(
        text,
        style_pos,
        toyplot.font.ReportlabLibrary(),
    )

    for child in layout.children:
        for textbox in child.children:

            # project points into coordinate space 
            transform = "translate({:.2f},{:.2f})".format(
                cx + textbox.left,
                cy + textbox.baseline,
            )

            if angle:
                transform += "rotate(%r)" % (-angle)

            # create a group marker for positioning text
            group = xml.SubElement(
                root, "g", style=style_to_string(style_text))
            group.set("transform", transform)

            # optionally add a title 
            if title is not None:
                xml.SubElement(group, "title").text = str(title)

            # style text should only include unique styling which currently for 
            # nodes is nothing, and for tips is only 'fill' and 'fill-opacity'.
            xml.SubElement(group, "text").text = text




# def tip_draw_text(root, text, cx, cy, style_pos, style_text, angle, title):
#     """

#     """ 
#     layout = toyplot.text.layout(
#         text,
#         style_text,
#         toyplot.font.ReportlabLibrary(),
#     )
#     baseline = layout.children[0].children[0].baseline
#     print('baseline', baseline)

#     # adjust projections based on angle and shift args
#     trans = toyplot.transform.rotation(angle)[0]
#     ashift = toyplot.units.convert(style_pos["-toyplot-anchor-shift"], "px")
#     xadjust = ashift * trans[0, 0]
#     yadjust = ashift * trans[0, 1]

#     print('preangle', angle)

#     "toytree-Tiplabels-R"}
#     # if left of origin or below origin then flip text
#     if isinstance(root.attrib['class'] == )
#     # TODO, take care for left-facing linear trees.
#     if (angle > 90) and (angle < 180):
#         xadjust *= -1
#         angle += 180
#     elif (angle > 180) and (angle < 270):
#         yadjust *= -1  

#     print('xadjust', xadjust)
#     print('yadjust', yadjust)
#     print('postangle', angle)
#     # project points into coordinate space 
#     transform = "translate({:.2f},{:.2f})".format(
#         cx + xadjust,
#         cy - yadjust + baseline,
#     )
#     if angle:
#         transform += "rotate(%r)" % (-angle)

#     # create a group marker for positioning text
#     group = xml.SubElement(
#         root, "g", style=style_to_string(style_text))
#     group.set("transform", transform)

#     # optionally add a title 
#     if title is not None:
#         xml.SubElement(group, "title").text = str(title)

#     # style text should only include unique styling which currently for 
#     # nodes is nothing, and for tips is only 'fill' and 'fill-opacity'.
#     xml.SubElement(group, "text").text = text




def custom_draw_marker(root, marker, cx, cy, extra_class, title=None):
    """ 
    This is modified from toyplot.html._draw_marker(). It is simplified
    for my simpler purposes and prevents style duplication.
    """
    # create the marker
    attrib = marker.mstyle
    attrib['class'] = extra_class
    marker_xml = xml.SubElement(root, "g", attrib=attrib)

    # option to add a title to the marker
    if title is not None:
        xml.SubElement(marker_xml, "title").text = str(title)

    # project marker in coordinate space
    transform = "translate({:.3f},{:.3f})".format(cx, cy)
    if marker.angle:
        transform += " rotate(%r)" % (-marker.angle,)
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
            marker_xml, marker.size, width=float(width), height=float(height))
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
    return marker_xml









# TODO
def _render_text_file(owner, key, label, table, filename, context):
    """
    A variant of toyplot.html._render_table that can be used instead
    to download a text file.
    """
    if isinstance(owner, toyplot.mark.Mark) and owner.annotation:
        return
    if isinstance(owner, toyplot.coordinates.Table) and owner.annotation:
        return

    names = []
    columns = []

    if isinstance(table, toyplot.data.Table):
        for name, column in table.items():
            if "toyplot:exportable" in table.metadata(name) and table.metadata(name)["toyplot:exportable"]:
                if column.dtype == toyplot.color.dtype:
                    raise ValueError("Color column table export isn't supported.") # pragma: no cover
                else:
                    names.append(name)
                    columns.append(column.tolist())
    else: # Assume numpy matrix
        for column in table.T:
            names.append(column[0])
            columns.append(column[1:].tolist())

    if not (names and columns):
        return

    owner_id = context.get_id(owner)
    if filename is None:
        filename = "toyplot"

    context.require(
        dependencies=["toyplot/menus/context", "toyplot/io"],
        arguments=[owner_id, key, label, names, columns, filename],
        code="""function(tables, context_menu, io, owner_id, key, label, names, columns, filename)
        {
            tables.set(owner_id, key, names, columns);

            var owner = document.querySelector("#" + owner_id);
            function show_item(e)
            {
                return owner.contains(e.target);
            }

            function choose_item()
            {
                io.save_file("text/csv", "utf-8", tables.get_csv(owner_id, key), filename + ".csv");
            }

            context_menu.add_item("Save " + label + " as CSV", show_item, choose_item);
        }""",
    )



if __name__ == "__main__":
    pass
