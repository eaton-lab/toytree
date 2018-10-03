#!/usr/bin/env python

"""Functions to render HTML markup."""

# pylint: disable=function-redefined

from __future__ import division, absolute_import

import base64
import collections
import copy
import functools
import io
import itertools
import json
import string
import uuid
import xml.etree.ElementTree as xml

from multipledispatch import dispatch
import numpy

import toyplot.coordinates
import toyplot.canvas
import toyplot.color
import toyplot.compatibility
import toyplot.mark
import toyplot.marker

from toyplot.html import RenderContext, _color_fixup


_namespace = dict()

#: Decorator for registering custom rendering code.
#:
#: This is only of use when creating your own custom Toyplot marks.  It is
#: not intended for end-users.
#:
#: Example
#: -------
#: To register your own rendering function::
#:
#:     @toyplot.html.dispatch(toyplot.coordinates.Cartesian, MyCustomMark, toyplot.html.RenderContext)
#:     def _render(axes, mark, context):
#:         # Rendering implementation here
dispatch = functools.partial(dispatch, namespace=_namespace)


# ## get canvas instance
# canvas = toyplot.require.instance(c, toyplot.canvas.Canvas)
# canvas.autorender(False)
# # make top-level HTML element
# root_xml = xml.Element(
#     'div',
#     attrib={"class": "toyplot"},
#     id="t" + uuid.uuid4().hex,
#     )
# # Register a Javascript module to keep track of the root id
# context = RenderContext(root=root_xml)
# context.define("toyplot/root/id", value=root_xml.get("id"))
# context.define(
#     "toyplot/root",
#     ["toyplot/root/id"],
#     factory="""function(root_id){return document.querySelector("#" + root_id)};""")
# mark = M
# axes = a


# toytree Marker object which has a custom render function below.
# The init function for creating a Toytree Mark is similar to what
# used to be in the draw() function.
class Toytree(toyplot.mark.Mark):
    def __init__(self, newick):
        super(Toytree, self).__init__()

        self.toytree = toytree.tree(newick)
        self.markers = []
        edge_marker = get_edge_mark(self.toytree)
        text_marker = get_text_mark(self.toytree)
        node_marker = get_node_mark(self.toytree)
        etip_marker = get_etip_mark(self.toytree)
        for marker in [edge_marker, text_marker, node_marker, etip_marker]:
            if marker:
                self.markers.append(marker)

    # domain is the tree/edge domain
    def domain(self, axis):
        return self.markers[0].domain(axis)
        # if axis == "x":
        #   ## max should fit tip names
        #       return toyplot.data.minimax(self._toytree.verts[:, 0])
        # else:
        #   return toyplot.data.minimax(self._toytree.verts[:, 1])

    # Entents depends on tree orientation, since we extend for text direction
    def extents(self, axes):
        extents = toyplot.text.extents(
            self._table[self._text[0]],
            self._table[self._angle[0]],
            self._style)
        return coordinates, extents



# this is a hybrid of Toyplot's Graph, Text, and Scatterplot _render
# functions with just the elements I want selected out. It also
# makes minifying calls to simplify style dictionaries for shared styles
@dispatch(toyplot.coordinates.Cartesian, Toytree, RenderContext)
def _render(axes, mark, context):

    dimension1 = numpy.ma.column_stack(
        [mark._table[key] for key in mark._coordinates[0::2]])
    dimension2 = numpy.ma.column_stack(
        [mark._table[key] for key in mark._coordinates[1::2]])
    if mark._coordinate_axes[0] == "x":
        X = axes.project("x", dimension1)
        Y = axes.project("y", dimension2)
    elif mark._coordinate_axes[0] == "y":
        X = axes.project("x", dimension2)
        Y = axes.project("y", dimension1)

    # group styles with common values
    shared_styles, unique_styles = split_styles(mark)

    # create root Scatterplot element
    mark_xml = xml.SubElement(
        root_xml,
        "g",
        id=context.get_id(mark),
        attrib={"class": "toyplot-mark-Scatterplot"},
    )
    print xml.tostring(mark_xml)

    ##
    mvectors = [
        X.T,
        Y.T,
        [mark._table[key] for key in mark._marker],
        [mark._table[key] for key in mark._mtitle],
    ]

    for x, y, marker, mtitle in zip(*mvectors):
        not_null = numpy.invert(numpy.logical_or(
            numpy.ma.getmaskarray(x), numpy.ma.getmaskarray(y)))

        # create a Series element to hold all data points
        series_xml = xml.SubElement(
            mark_xml,
            "g",
            attrib={
                "class": "toyplot-Series",
                "style": shared_styles,
            },
        )
        print xml.tostring(series_xml)
        print ""

        # subselect markers for missing data
        vals = [
            itertools.count(step=1),
            x[not_null],
            y[not_null],
            marker[not_null],
            mtitle[not_null],
        ]
        for idx, dx, dy, dmarker, dtitle in zip(*vals):
            marker = toyplot.marker.create(
                size=dmarker.size,
                shape=dmarker.shape,
                mstyle=unique_styles["node"][idx],
                lstyle={},
                label=dmarker.label)
            marker_xml = _draw_marker(
                root=series_xml,
                marker=marker,
                cx=dx,
                cy=dy,
                extra_class="toyplot-Datum",
                title=dtitle,
            )
            # print xml.tostring(marker_xml)
            # print ""
            if marker.label:
                _draw_text(
                    root=marker_xml,
                    text=marker.label,
                    style=unique_styles['text'][idx],
                )
            print xml.tostring(marker_xml)
            print ""
            # create new simplified marker... working off Line 3177 in html.py


## tip names text
def get_text_mark(ttree):
    """ makes a simple Text Mark object"""
    
    if ttree._orient in ["right"]:
        angle = 0.
        ypos = ttree.verts[-1*len(ttree.tree):, 1]
        if ttree._kwargs["tip_labels_align"]:
            xpos = [ttree.verts[:, 0].max()] * len(ttree.tree)
            start = xpos
            finish = ttree.verts[-1*len(ttree.tree):, 0]
            align_edges = np.array([(i, i+len(xpos)) for i in range(len(xpos))])
            align_verts = np.array(zip(start, ypos) + zip(finish, ypos))
        else:
            xpos = ttree.verts[-1*len(ttree.tree):, 0]
            
    elif ttree._orient in ['down']:
        angle = -90.
        xpos = ttree.verts[-1*len(ttree.tree):, 0]
        if ttree._kwargs["tip_labels_align"]:
            ypos = [ttree.verts[:, 1].min()] * len(ttree.tree)
            start = ypos
            finish = ttree.verts[-1*len(ttree.tree):, 1]
            align_edges = np.array([(i, i+len(ypos)) for i in range(len(ypos))])
            align_verts = np.array(zip(xpos, start) + zip(xpos, finish))
        else:
            ypos = ttree.verts[-1*len(ttree.tree):, 1]
    
    table = toyplot.data.Table()
    table['x'] = toyplot.require.scalar_vector(xpos)
    table['y'] = toyplot.require.scalar_vector(ypos, table.shape[0])
    table['text'] = toyplot.broadcast.pyobject(ttree.get_tip_labels(), table.shape[0])
    table["angle"] = toyplot.broadcast.scalar(angle, table.shape[0])
    table["opacity"] = toyplot.broadcast.scalar(1.0, table.shape[0])
    table["title"] = toyplot.broadcast.pyobject(None, table.shape[0])
    style = toyplot.style.require(ttree._kwargs["tip_labels_style"],
                                  allowed=toyplot.style.allowed.text)
    default_color = [toyplot.color.black]
    color = toyplot.color.broadcast(
        colors=ttree._kwargs["tip_labels_color"],
        shape=(table.shape[0], 1),
        default=default_color,
        )
    table["fill"] = color[:, 0]
    
    text_mark = toyplot.mark.Text(
        coordinate_axes=['x', 'y'],
        table=table,
        coordinates=['x', 'y'],
        text=["text"],
        angle=["angle"],
        fill=["fill"],
        opacity=["opacity"],
        title=["title"],
        style=style,
        annotation=True,
        filename=None
        )
    return text_mark


## toytree uses edges, no need for vertices
def get_edge_mark(ttree):
    """ makes a simple Graph Mark object"""
    
    ## tree style
    if ttree._kwargs["tree_style"] in ["c", "cladogram"]:
        a=ttree.edges
        vcoordinates=ttree.verts
    else:
        a=ttree._lines               
        vcoordinates=ttree._coords    
   
    ## fixed args
    along='x'
    vmarker='o'
    vcolor=None
    vlshow=False            
    vsize=0.         
    estyle=ttree._kwargs["edge_style"]

    ## get axes
    layout = toyplot.layout.graph(a, vcoordinates=vcoordinates)
    along = toyplot.require.value_in(along, ["x", "y"])
    if along == "x":
        coordinate_axes = ["x", "y"]
    elif along == "y":
        coordinate_axes = ["y", "x"]
        
    ## broadcast args along axes
    vlabel = layout.vids
    vmarker = toyplot.broadcast.pyobject(vmarker, layout.vcount)
    vsize = toyplot.broadcast.scalar(vsize, layout.vcount)
    estyle = toyplot.style.require(estyle, allowed=toyplot.style.allowed.line)

    ## fixed args
    vcolor = toyplot.color.broadcast(colors=None, shape=layout.vcount, default=toyplot.color.black)
    vopacity = toyplot.broadcast.scalar(1.0, layout.vcount)
    vtitle = toyplot.broadcast.pyobject(None, layout.vcount)
    vstyle = None
    vlstyle = None
    
    ## this could be modified in the future to allow diff color edges
    ecolor = toyplot.color.broadcast(colors=None, shape=layout.ecount, default=toyplot.color.black)
    ewidth = toyplot.broadcast.scalar(1.0, layout.ecount)
    eopacity = toyplot.broadcast.scalar(1.0, layout.ecount)
    hmarker = toyplot.broadcast.pyobject(None, layout.ecount)
    mmarker = toyplot.broadcast.pyobject(None, layout.ecount)
    mposition = toyplot.broadcast.scalar(0.5, layout.ecount)
    tmarker = toyplot.broadcast.pyobject(None, layout.ecount)
    
    ## tables are required if I don't want to edit the class
    vtable = toyplot.data.Table()
    vtable["id"] = layout.vids
    for axis, coordinates in zip(coordinate_axes, layout.vcoordinates.T):
        vtable[axis] = coordinates
        #_mark_exportable(vtable, axis)
    vtable["label"] = vlabel
    vtable["marker"] = vmarker
    vtable["size"] = vsize
    vtable["color"] = vcolor
    vtable["opacity"] = vopacity
    vtable["title"] = vtitle

    etable = toyplot.data.Table()
    etable["source"] = layout.edges.T[0]
    #_mark_exportable(etable, "source")
    etable["target"] = layout.edges.T[1]
    #_mark_exportable(etable, "target")
    etable["shape"] = layout.eshapes
    etable["color"] = ecolor
    etable["width"] = ewidth
    etable["opacity"] = eopacity
    etable["hmarker"] = hmarker
    etable["mmarker"] = mmarker
    etable["mposition"] = mposition
    etable["tmarker"] = tmarker
    
    edge_mark = toyplot.mark.Graph(
        coordinate_axes=['x', 'y'],
        ecolor=["color"],
        ecoordinates=layout.ecoordinates,
        efilename=None,
        eopacity=["opacity"],
        eshape=["shape"],
        esource=["source"],
        estyle=estyle,
        etable=etable,
        etarget=["target"],
        ewidth=["width"],
        hmarker=["hmarker"],
        mmarker=["mmarker"],
        mposition=["mposition"],
        tmarker=["tmarker"],
        vcolor=["color"],
        vcoordinates=['x', 'y'],
        vfilename=None,
        vid=["id"],
        vlabel=["label"],
        vlshow=False,
        vlstyle=None,
        vmarker=["marker"],
        vopacity=["opacity"],
        vsize=["size"],
        vstyle=None,
        vtable=vtable,
        vtitle=["title"],
        )
    return edge_mark


## nodes on tree
def get_node_mark(ttree):
    return


## Currently this clobbers some text styling (e.g., alignment-baseline)
## during the 'toyplot.text.layout' restyling. Not sure why.
def split_styles(mark):
    """ get shared styles """
    
    markers = [mark._table[key] for key in mark._marker][0]
    nstyles = []
    for m in markers:
        ## fill and stroke are already rgb() since already in markers
        msty = toyplot.style.combine({
            "fill": m.mstyle['fill'],
            "stroke": m.mstyle['stroke'],
            "opacity": m.mstyle["fill-opacity"],
        }, m.mstyle)
        msty = _color_fixup(msty)
        nstyles.append(msty)
    
    ## uses 'marker.size' so we need to loop over it
    lstyles = []
    for m in markers:
        lsty = toyplot.style.combine({
        "font-family": "Helvetica",
        "-toyplot-vertical-align": "middle",
        "fill": toyplot.color.black,
        "font-size": "%rpx" % (m.size * 0.75),
        "stroke": "none",
        "text-anchor": "middle",
        }, m.lstyle)
        ## update fonts
        fonts = toyplot.font.ReportlabLibrary()
        layout = toyplot.text.layout(m.label, lsty, fonts)
        lsty = _color_fixup(layout.style)
        lstyles.append(lsty)
    
    nallkeys = set(itertools.chain(*[i.keys() for i in nstyles]))
    lallkeys = set(itertools.chain(*[i.keys() for i in lstyles]))
    nuniquekeys = []
    nsharedkeys = []
    for key in nallkeys:
        vals = [nstyles[i].get(key) for i in range(len(nstyles))]
        if len(set(vals)) > 1:
            nuniquekeys.append(key)
        else:
            nsharedkeys.append(key)
    luniquekeys = []
    lsharedkeys = []
    for key in lallkeys:
        vals = [lstyles[i].get(key) for i in range(len(lstyles))]
        if len(set(vals)) > 1:
            luniquekeys.append(key)
        else:
            lsharedkeys.append(key)

    ## keys shared between mark and text markers
    repeated = set(lsharedkeys).intersection(set(nsharedkeys))
    for repeat in repeated:
        ## if same then keep only one copy of it
        lidx = lsharedkeys.index(repeat)
        nidx = nsharedkeys.index(repeat)
        if lsharedkeys[lidx] == nsharedkeys[nidx]:
            lsharedkeys.remove(repeat)
        else:
            lsharedkeys.remove(repeat)
            luniquekeys.append(repeat)
            nsharedkeys.remove(repeat)
            nuniquekeys.append(repeat)
            
    ## check node values
    natt = ["%s:%s" % (key, nstyles[0][key]) for key in sorted(nsharedkeys)]
    latt = ["%s:%s" % (key, lstyles[0][key]) for key in sorted(lsharedkeys)]
    shared_styles = ";".join(natt+latt)
    unique_styles = {
        "node": [{k:v for k,v in nstyles[idx].items() if k in nuniquekeys} for idx in range(len(markers))],
        "text": [{k:v for k,v in lstyles[idx].items() if k in luniquekeys} for idx in range(len(markers))]
    }
    
    return shared_styles, unique_styles



## Unlike toyplot, I do not want to add text styling at draw time, 
## but rather before hand so that we can simplify the HTML. 
## MAYBE, better way to do this by editing HTML after its written
## inside my own render function, so that less breaking with 
## toyplot is needed. This is here for now...
def _draw_text(
    root,
    text,
    x=0,
    y=0,
    style=None,
    angle=None,
    title=None,
    attributes=None,
    layout=None,
    ):

    if not text:
        return

    if attributes is None:
        attributes = {}

    transform = ""
    if x or y:
        transform += "translate(%r,%r)" % (x, y)
    if angle:
        transform += "rotate(%r)" % (-angle)

    group = xml.SubElement(
        root,
        "g",
        attrib=attributes,
        )
    if transform:
        group.set("transform", transform)

    if title is not None:
        xml.SubElement(group, "title").text = str(title)

    fonts = toyplot.font.ReportlabLibrary()
    layout = text if isinstance(text, toyplot.text.Layout) else toyplot.text.layout(text, style, fonts)
    if layout.style.get("-toyplot-text-layout-visibility", None) == "visible":
        xml.SubElement(
            group,
            "rect",
            x=str(layout.left),
            y=str(layout.top),
            width=str(layout.width),
            height=str(layout.height),
            stroke="red",
            fill="none",
            opacity="0.5",
            )
        xml.SubElement(
            group,
            "circle",
            x="0",
            y="0",
            r="3",
            stroke="none",
            fill="red",
            opacity="0.5",
            )

    hyperlink = []
    for line in layout.children:
        if line.style.get("-toyplot-text-layout-line-visibility", None) == "visible":
            xml.SubElement(
                group,
                "rect",
                x=str(line.left),
                y=str(line.top),
                width=str(line.width),
                height=str(line.height),
                stroke="green",
                fill="none",
                opacity="0.5",
                )
            xml.SubElement(
                group,
                "line",
                x1=str(line.left),
                y1=str(line.baseline),
                x2=str(line.right),
                y2=str(line.baseline),
                stroke="green",
                fill="none",
                opacity="0.5",
                )
        for box in line.children:
            if isinstance(box, toyplot.text.TextBox):
                xml.SubElement(
                    group,
                    "text",
                    x=str(box.left),
                    y=str(box.baseline),
                    style=toyplot.style.to_css(style), #toyplot.style.to_css(box.style),
                    ).text = box.text

                if box.style.get("-toyplot-text-layout-box-visibility", None) == "visible":
                    xml.SubElement(
                        group,
                        "rect",
                        x=str(box.left),
                        y=str(box.top),
                        width=str(box.width),
                        height=str(box.height),
                        stroke="blue",
                        fill="none",
                        opacity="0.5",
                        )
                    xml.SubElement(
                        group,
                        "line",
                        x1=str(box.left),
                        y1=str(box.baseline),
                        x2=str(box.right),
                        y2=str(box.baseline),
                        stroke="blue",
                        fill="none",
                        opacity="0.5",
                        )

            elif isinstance(box, toyplot.text.MarkerBox):
                if box.marker:
                    _draw_marker(
                        group,
                        cx=(box.left + box.right) * 0.5,
                        cy=(box.top + box.bottom) * 0.5,
                        marker=toyplot.marker.create(size=box.height) + box.marker,
                        )
                if box.style.get("-toyplot-text-layout-box-visibility", None) == "visible":
                    xml.SubElement(
                        group,
                        "rect",
                        x=str(box.left),
                        y=str(box.top),
                        width=str(box.width),
                        height=str(box.height),
                        stroke="blue",
                        fill="none",
                        opacity="0.5",
                        )
                    xml.SubElement(
                        group,
                        "line",
                        x1=str(box.left),
                        y1=str(box.baseline),
                        x2=str(box.right),
                        y2=str(box.baseline),
                        stroke="blue",
                        fill="none",
                        opacity="0.5",
                        )

            elif isinstance(box, toyplot.text.PushHyperlink):
                hyperlink.append(group)
                group = xml.SubElement(group, "a")
                group.set("xlink:href", box.href)
            elif isinstance(box, toyplot.text.PopHyperlink):
                group = hyperlink.pop()



## copy from this to draw my own graph renderer
#@dispatch(toyplot.coordinates.Cartesian, toyplot.mark.Graph, RenderContext)
def _render_graph(axes, mark, context): 
    # Project edge coordinates.
    for i in range(2):
        if mark._coordinate_axes[i] == "x":
            edge_x = axes.project("x", mark._ecoordinates.T[i])
        elif mark._coordinate_axes[i] == "y":
            edge_y = axes.project("y", mark._ecoordinates.T[i])
    edge_coordinates = numpy.column_stack((edge_x, edge_y))

    # Project vertex coordinates.
    for i in range(2):
        if mark._coordinate_axes[i] == "x":
            vertex_x = axes.project("x", mark._vtable[mark._vcoordinates[i]])
        elif mark._coordinate_axes[i] == "y":
            vertex_y = axes.project("y", mark._vtable[mark._vcoordinates[i]])

    # NO VERTEX LABELS
    #vertex_markers = []
    #for vmarker, vsize, vcolor, vopacity in zip(
    #        mark._vtable[mark._vmarker[0]],
    #        mark._vtable[mark._vsize[0]],
    #        mark._vtable[mark._vcolor[0]],
    #        mark._vtable[mark._vopacity[0]],
    #    ):
    #    if vmarker:
    #        vstyle = toyplot.style.combine(
    #            {
    #            "fill": toyplot.color.to_css(vcolor),
    #            "stroke": toyplot.color.to_css(vcolor),
    #            "opacity": vopacity,
    #            },
    #            mark._vstyle)
    #        vertex_marker = toyplot.marker.create(size=vsize, mstyle=vstyle, lstyle=mark._vlstyle) + toyplot.marker.convert(vmarker)
    #        vertex_markers.append(vertex_marker)
    #    else:
    #        vertex_markers.append(None)

    # EDGE STYLES
    edge_styles = []
    for ecolor, ewidth, eopacity in zip(
            mark._etable[mark._ecolor[0]],
            mark._etable[mark._ewidth[0]],
            mark._etable[mark._eopacity[0]],
        ):
        edge_styles.append(
            toyplot.style.combine(
                {
                "fill": "none",
                "stroke": toyplot.color.to_css(ecolor),
                "stroke-width": ewidth,
                "stroke-opacity": eopacity,
                },
                mark._estyle,
            )
        )

    edge_marker_styles = []
    for ecolor, estyle in zip(
            mark._etable[mark._ecolor[0]],
            edge_styles,
            ):
        edge_marker_styles.append(toyplot.style.combine(estyle, {"fill": toyplot.color.to_css(ecolor)}))

    # Identify ranges of edge coordinates for each edge.
    index = 0
    edge_start = []
    edge_end = []
    for eshape in mark._etable[mark._eshape[0]]:
        edge_start.append(index)
        for segment in eshape:
            if segment == "M":
                count = 1
            elif segment == "L":
                count = 1
            elif segment == "Q":
                count = 2
            elif segment == "C":
                count = 3
            index += count
        edge_end.append(index)

    # Adjust edge coordinates so edges don't overlap vertex markers.
    for esource, etarget, start, end in zip(
            mark._etable[mark._esource[0]],
            mark._etable[mark._etarget[0]],
            edge_start,
            edge_end,
        ):

        # Skip loop edges.
        if esource == etarget:
            continue

        source_vertex_marker = vertex_markers[esource]
        target_vertex_marker = vertex_markers[etarget]

        if source_vertex_marker:
            dp = source_vertex_marker.intersect(edge_coordinates[start + 1] - edge_coordinates[start])
            edge_coordinates[start] += dp

        if target_vertex_marker:
            dp = target_vertex_marker.intersect(edge_coordinates[end - 2] - edge_coordinates[end - 1])
            edge_coordinates[end - 1] += dp

    # Render the graph.
    mark_xml = xml.SubElement(
        context.parent, "g", 
        id=context.get_id(mark), 
        attrib={"class": "toyplot-mark-Graph"}
        )
    #_render_table(
    #    owner=mark, 
    #    key="vertex_data", 
    #    label="graph vertex data", 
    #    table=mark._vtable, 
    #    filename=mark._vfilename, 
    #    context=context)

    ## THIS ADDS THE DOWNLOAD INFO (NEWICK STRING FILE) TO THE GRAPH
    _render_table(
        owner=mark, 
        key="edge_data", 
        label="graph edge data", 
        table=mark._etable, 
        filename=mark._efilename, 
        context=context
        )

    # Render edges.
    ## THIS IS WHERE WE STICK IN THE COMMON STYLE ELEMENTS
    edge_xml = xml.SubElement(
        mark_xml, 
        "g", 
        attrib={"class": "toyplot-Edges"}
        )
    ## THEN PUT IN THE UNIQUE STYLE ELEMENTS
    for esource, etarget, eshape, estyle, hmarker, mmarker, mposition, tmarker, start, end in zip(
            mark._etable[mark._esource[0]],
            mark._etable[mark._etarget[0]],
            mark._etable[mark._eshape[0]],
            edge_styles,
            mark._etable[mark._hmarker[0]],
            mark._etable[mark._mmarker[0]],
            mark._etable[mark._mposition[0]],
            mark._etable[mark._tmarker[0]],
            edge_start,
            edge_end,
        ):

        path = []
        index = 0
        for segment in eshape:
            if segment == "M":
                count = 1
            elif segment == "L":
                count = 1
            elif segment == "Q":
                count = 2
            elif segment == "C":
                count = 3
            path.append(segment)
            for _ in range(count):
                path.append(str(edge_coordinates[start + index][0]))
                path.append(str(edge_coordinates[start + index][1]))
                index += 1

        xml.SubElement(
            edge_xml,
            "path",
            d=" ".join(path),
            style=_css_style(estyle),
            )

    # Render edge head markers.
    # marker_xml = xml.SubElement(edge_xml, "g", attrib={"class": "toyplot-HeadMarkers"})
    # for marker, mstyle, estart, eend in zip(
    #         mark._etable[mark._hmarker[0]],
    #         edge_marker_styles,
    #         edge_start,
    #         edge_end,
    #     ):
    #     if marker:
    #         # Create the marker with defaults.
    #         marker = toyplot.marker.create(size=10, mstyle=mstyle) + toyplot.marker.convert(marker)

    #         # Compute the marker angle using the first edge segment.
    #         edge_angle = -numpy.rad2deg(numpy.arctan2(
    #             edge_coordinates[estart+1][1] - edge_coordinates[estart][1],
    #             edge_coordinates[estart+1][0] - edge_coordinates[estart][0],
    #             ))

    #         transform = "translate(%r, %r)" % (edge_coordinates[estart][0], edge_coordinates[estart][1])
    #         if edge_angle:
    #             transform += " rotate(%r)" % (-edge_angle,)
    #         transform += " translate(%r, 0)" % (marker.size / 2,)
    #         if marker.angle is not None:
    #             if isinstance(marker.angle, toyplot.compatibility.string_type) and marker.angle[0:1] == "r":
    #                 angle = float(marker.angle[1:])
    #             else:
    #                 angle = -edge_angle + float(marker.angle)
    #             transform += " rotate(%r)" % (-angle,)

    #         _draw_marker(
    #             marker_xml,
    #             marker=marker,
    #             transform=transform,
    #             )

    # # Render edge middle markers.
    # marker_xml = xml.SubElement(edge_xml, "g", attrib={"class": "toyplot-MiddleMarkers"})
    # for mstyle, marker, mposition, start, end in zip(
    #         edge_marker_styles,
    #         mark._etable[mark._mmarker[0]],
    #         mark._etable[mark._mposition[0]],
    #         edge_start,
    #         edge_end,
    #     ):
    #     if marker:
    #         # Create the marker with defaults.
    #         marker = toyplot.marker.create(size=10, mstyle=mstyle) + toyplot.marker.convert(marker)

    #         # Place the marker within the first edge segment.
    #         x, y = edge_coordinates[start] * (1 - mposition) + edge_coordinates[start+1] * mposition

    #         # Compute the marker angle using the first edge segment.
    #         angle = -numpy.rad2deg(numpy.arctan2(
    #             edge_coordinates[start+1][1] - edge_coordinates[start][1],
    #             edge_coordinates[start+1][0] - edge_coordinates[start][0],
    #             ))
    #         if marker.angle is not None:
    #             if isinstance(marker.angle, toyplot.compatibility.string_type) and marker.angle[0:1] == "r":
    #                 angle += float(marker.angle[1:])
    #             else:
    #                 angle = float(marker.angle)

    #         marker = marker + toyplot.marker.create(angle=angle)

    #         _draw_marker(
    #             marker_xml,
    #             cx=x,
    #             cy=y,
    #             marker=marker,
    #             )

    # # Render edge tail markers.
    # marker_xml = xml.SubElement(edge_xml, "g", attrib={"class": "toyplot-TailMarkers"})
    # for mstyle, marker, start, end in zip(
    #         edge_marker_styles,
    #         mark._etable[mark._tmarker[0]],
    #         edge_start,
    #         edge_end,
    #     ):
    #     if marker:
    #         # Create the marker with defaults.
    #         marker = toyplot.marker.create(size=10, mstyle=mstyle, lstyle={}) + toyplot.marker.convert(marker)

    #         # Compute the marker angle using the last edge segment.
    #         edge_angle = -numpy.rad2deg(numpy.arctan2(
    #             edge_coordinates[end-1][1] - edge_coordinates[end-2][1],
    #             edge_coordinates[end-1][0] - edge_coordinates[end-2][0],
    #             ))

    #         transform = "translate(%r, %r)" % (edge_coordinates[end-1][0], edge_coordinates[end-1][1])
    #         if edge_angle:
    #             transform += " rotate(%r)" % (-edge_angle,)
    #         transform += " translate(%r, 0)" % (-marker.size / 2,)
    #         if marker.angle is not None:
    #             if isinstance(marker.angle, toyplot.compatibility.string_type) and marker.angle[0:1] == "r":
    #                 angle = float(marker.angle[1:])
    #             else:
    #                 angle = -edge_angle + float(marker.angle)
    #             transform += " rotate(%r)" % (-angle,)


    #         _draw_marker(
    #             marker_xml,
    #             marker=marker,
    #             transform=transform,
    #             )

    # Render vertex markers
    #vertex_xml = xml.SubElement(mark_xml, "g", attrib={"class": "toyplot-Vertices"})
    #for vx, vy, vmarker, vtitle in zip(
    #        vertex_x,
    #        vertex_y,
    #        vertex_markers,
    #        mark._vtable[mark._vtitle[0]],
    #    ):
    #    if vmarker:
    #        _draw_marker(
    #            vertex_xml,
    #            cx=vx,
    #            cy=vy,
    #            marker=vmarker,
    #            extra_class="toyplot-Datum",
    #            title=vtitle,
    #            )

    # Render vertex labels
    #if mark._vlshow:
    #    vlabel_xml = xml.SubElement(mark_xml, "g", attrib={"class": "toyplot-Labels"})
    #    for dx, dy, dtext in zip(vertex_x, vertex_y, mark._vtable[mark._vlabel[0]]):
    #        _draw_text(
    #            root=vlabel_xml,
    #            text=toyplot.compatibility.unicode_type(dtext),
    #            x=dx,
    #            y=dy,
    #            style=mark._vlstyle,
    #            attributes={"class": "toyplot-Datum"},
    #            )

