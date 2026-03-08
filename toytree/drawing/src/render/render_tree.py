#!/usr/bin/env python

"""Dispatched renderer for toytree marks following the style of toyplot."""

import functools
import xml.etree.ElementTree as xml
from typing import Dict, List, Tuple

import numpy as np
import toyplot
from multipledispatch import dispatch

from toytree.color import COLORS2
from toytree.color.src.concat import concat_style_fix_color
from toytree.drawing import ToyTreeMark
from toytree.drawing.src.path_edges import PATH_FORMAT, get_tree_edge_svg_paths
from toytree.drawing.src.render.render_marker import render_marker
from toytree.drawing.src.render.render_text import render_text
from toytree.layout.src.get_edge_midpoints import get_edge_midpoints

# ---------------------------------------------------------------------
# Register multipledispatch to use the toyplot.html namespace
dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)


# register a _render function for ToyTreeMark objects
@dispatch(toyplot.coordinates.Cartesian, ToyTreeMark, toyplot.html.RenderContext)
def _render(axes, mark, context):
    RenderToytree(axes, mark, context)


# ---------------------------------------------------------------------


class RenderToytree:
    """Class with functions to add ToyTree class to the HTML DOM.

    Organized class to call within _render. The top level canvas
    element is .context. From this parent xml subelements are
    added to build the drawing. The toytree mark is in .mark.
    """

    def __init__(self, axes, mark, context):
        # existing
        self.mark = mark
        self.axes = axes
        self.context = context

        # start rendering of this Mark by connecting to context (Canvas)
        self.mark_xml: xml.SubElement = xml.SubElement(
            context.parent,
            "g",
            id=context.get_id(self.mark),
            attrib={"class": "toytree-mark-Toytree"},
        )

        # to be constructed (are these reused?)
        self.edges_xml: xml.SubElement = None
        self.nodes_xml: xml.SubElement = None
        self.admix_xml: xml.SubElement = None
        self.align_xml: xml.SubElement = None

        # data...
        self.nodes_x: np.ndarray = None
        self.nodes_y: np.ndarray = None
        self.tips_x: np.ndarray = None
        self.tips_y: np.ndarray = None
        self.radii: np.ndarray = None

        # construction funcs
        self.project_coordinates()
        self.build_dom()

    def project_coordinates(self):
        """Store node coordinates (data units) projected to px units."""
        self.nodes_x = self.axes.project("x", self.mark.ntable[:, 0])
        self.nodes_y = self.axes.project("y", self.mark.ntable[:, 1])
        self.tips_x = self.axes.project("x", self.mark.ttable[:, 0])
        self.tips_y = self.axes.project("y", self.mark.ttable[:, 1])
        mcoords = get_edge_midpoints(
            self.mark.etable, self.mark.ntable, self.mark.layout, self.mark.edge_type
        )
        self.mid_x = self.axes.project("x", mcoords[:, 0])
        self.mid_y = self.axes.project("y", mcoords[:, 1])

    def build_dom(self):
        """Create DOM of xml.SubElements in self.context."""
        self.mark_edges()
        self.mark_align_edges()
        self.mark_admixture_edges()
        self.mark_nodes()
        self.mark_node_labels()

        # for multitrees tips are sometimes not drawn.
        self.mark_tip_labels()

    def mark_edges(self) -> None:
        """Create SVG paths for each tree edge as class toytree-Edges."""
        # get paths based on edge type and layout
        paths, keys = get_tree_edge_svg_paths(self.axes, self.mark)

        # !always pop 'fill' to set it to 'fill:none' below (no fill btwn edges).
        _ = self.mark.edge_style.pop("fill", None)

        # render the edge group.
        # TODO: consider adding stroke-linejoin:round
        self.edges_xml = xml.SubElement(
            self.mark_xml,
            "g",
            attrib={"class": "toytree-Edges"},
            style=concat_style_fix_color(self.mark.edge_style, "fill:none"),
        )

        # get shared versus unique styles (EdgeStyles)
        unique_styles = get_unique_edge_styles(self.mark)
        # unique_styles.append({"stroke-width": 1.0})
        # logger.info(unique_styles)

        # render the edge paths
        for idx, path in enumerate(paths):
            xml.SubElement(
                self.edges_xml,
                "path",
                d=path,
                id=keys[idx],
                style=concat_style_fix_color(unique_styles[idx]),
            )

    def mark_nodes(self) -> None:
        """Create marker elements for each node in class toytree-Nodes.

        Stores ids to the nodes which in theory can allow for
        downstream JS interactivity.
        """
        # Group all Nodes with shared style applied
        self.nodes_xml = xml.SubElement(
            self.mark_xml,
            "g",
            attrib={"class": "toytree-Nodes"},
            style=concat_style_fix_color(self.mark.node_style),
        )

        # skip drawing any nodes if node_mask=True or all node_sizes=0
        if (self.mark.node_sizes == 0).all():
            return
        if not self.mark.node_mask.any():
            return

        # get dict with only styles not shared by all Nodes. This sets
        # fill-opacity to False (special) if there is a shared style
        # for node_style.fill-opacity (except for fill=transparent)
        unique_styles = get_unique_node_styles(self.mark)

        # get nnodes to draw (fewer if drawing edges or unrooted)
        if self.mark.node_as_edge_data:
            nedges = self.mark.nnodes - 2
            if np.count_nonzero(self.mark.etable[:, 1] == self.mark.etable[-1, 1]) > 2:
                nedges += 1
            nmarkers = nedges
            xcoords = self.mid_x
            ycoords = self.mid_y
        else:
            nmarkers = self.mark.nnodes
            xcoords = self.nodes_x
            ycoords = self.nodes_y

        # add node markers in reverse idx order (levelorder traversal)
        # for nidx in range(self.mark.nnodes):
        for nidx in range(nmarkers):
            # skip if node is masked
            if not self.mark.node_mask[nidx]:
                continue

            # create marker with shape and size, e.g., <marker='o' size=12>
            marker = toyplot.marker.create(
                shape=self.mark.node_markers[nidx],
                size=self.mark.node_sizes[nidx],
            )

            # create the marker
            marker_xml = xml.SubElement(
                self.nodes_xml,
                "g",
                attrib={"id": f"Node-{nidx}"},
                style=concat_style_fix_color(unique_styles[nidx]),
            )

            # if style string is empty then remove it.
            if not marker_xml.attrib["style"]:
                _ = marker_xml.attrib.pop("style")

            # optionally add a title (hover) here only if there is no
            # node_label, otherwise we put the hover on the label later.
            if self.mark.node_hover is not None:
                if self.mark.node_labels is None:
                    xml.SubElement(marker_xml, "title").text = self.mark.node_hover[
                        nidx
                    ]

            # project marker in coordinate space
            transform = "translate({:.6g},{:.6g})".format(
                xcoords[nidx],
                ycoords[nidx],
            )
            if marker.angle:
                transform += " rotate({:.3f})".format(-marker.angle)
            marker_xml.set("transform", transform)

            # get shape type
            render_marker(marker_xml, marker)

    def mark_node_labels(self) -> None:
        """Create Node labels in toytree-NodeLabels using render_text."""
        if self.mark.node_labels is None:
            return

        # shared styles popped from text boxes AFTER positioning
        shared_style = {
            "font-size": self.mark.node_labels_style["font-size"],
            "font-weight": self.mark.node_labels_style["font-weight"],
            "font-family": self.mark.node_labels_style["font-family"],
            "vertical-align": "baseline",
            "white-space": "pre",
        }

        # create NodeLabels group element
        node_labels_xml = xml.SubElement(
            self.mark_xml,
            "g",
            attrib={"class": "toytree-NodeLabels"},
            style=concat_style_fix_color(shared_style, "stroke:none"),
        )

        # get nnodes to draw (fewer if drawing edges or unrooted)
        if self.mark.node_as_edge_data:
            nedges = self.mark.nnodes - 2
            if np.count_nonzero(self.mark.etable[:, 1] == self.mark.etable[-1, 1]) > 2:
                nedges += 1
            nmarkers = nedges
            xcoords = self.mid_x
            ycoords = self.mid_y
        else:
            nmarkers = self.mark.nnodes
            xcoords = self.nodes_x
            ycoords = self.nodes_y

        # apply unique styles to each node label
        for idx in range(nmarkers):
            # masked label
            if not self.mark.node_mask[idx]:
                continue

            # get the label
            label = self.mark.node_labels[idx]
            title = None if self.mark.node_hover is None else self.mark.node_hover[idx]

            # always align node labels in middle of marker (?)
            default = {
                "-toyplot-vertical-align": "middle",  # baseline not supported.
                "text-anchor": "middle",  # start is another option.
            }
            nlstyle = toyplot.style.combine(self.mark.node_labels_style, default)
            render_text(
                root=node_labels_xml,
                text=label,
                xpos=xcoords[idx],
                ypos=ycoords[idx],
                angle=0,
                attributes={"class": "toytree-NodeLabel"},
                style=nlstyle,
                title=title,
            )

    def mark_tip_labels(self):
        """Create tip labels in toytree-TipLabels using render_text."""
        if self.mark.tip_labels is None:
            return

        # if angles are None then compute them now given the layout.

        # TipLabels style keys are popped from TipLabel styles, but
        # do not include positioning styles, which must be passed on.
        # shared_style = self.mark.tip_labels_style.copy()

        # base styles for the <g>, this includes some shared styles
        # such as: fill, stroke, but cannot do baseline-shift,
        # text-anchor, or anchor-shift (positioning text styles)
        shared_style = {
            "font-size": self.mark.tip_labels_style["font-size"],
            "font-weight": self.mark.tip_labels_style["font-weight"],
            "font-family": self.mark.tip_labels_style["font-family"],
            "fill": self.mark.tip_labels_style["fill"],
            "vertical-align": "baseline",
            "white-space": "pre",
        }

        # Make the <g> TipLabels group element
        tips_xml = xml.SubElement(
            self.mark_xml,
            "g",
            attrib={"class": "toytree-TipLabels"},
            style=concat_style_fix_color(shared_style, "stroke:none"),
        )

        # add <text> tip markers from 0 to ntips
        for idx, tip in enumerate(self.mark.tip_labels):
            # get coordinates of tips
            cxx = self.nodes_x[idx]
            cyy = self.nodes_y[idx]
            if self.mark.tip_labels_align:
                cxx = self.tips_x[idx]
                cyy = self.tips_y[idx]

            # style dict for this specific <text> string. This needs to
            # ALSO include the font-size, font-weight, etc., so that we
            # can calculate ... but then it will be popped from CSS.
            tstyle = self.mark.tip_labels_style.copy()
            if self.mark.tip_labels_colors is not None:
                _ = tstyle.pop("fill", None)
                tstyle["fill"] = self.mark.tip_labels_colors[idx]

            # assign tip layout positioning
            offset = toyplot.units.convert(
                tstyle["-toyplot-anchor-shift"],
                "px",
                "px",
            )

            if self.mark.layout in "rd":
                angle = self.mark.tip_labels_angles[idx]

            # reverse labels
            elif self.mark.layout in "lu":
                angle = self.mark.tip_labels_angles[idx]
                tstyle["-toyplot-anchor-shift"] = -offset
                tstyle["text-anchor"] = "end"

            # 'c' or unrooted
            else:
                angle = self.mark.tip_labels_angles[idx]
                if 90 < angle < 270:
                    tstyle["text-anchor"] = "end"
                    tstyle["-toyplot-anchor-shift"] = -offset
                    angle -= 180

            # add text
            render_text(
                root=tips_xml,
                text=tip,
                xpos=cxx,
                ypos=cyy,
                angle=angle,
                attributes={"class": "toytree-TipLabel"},
                style=tstyle,
            )

    def mark_align_edges(self):
        """Create SVG paths for each tip to 0 or radius.

        Currently only group styles are suppored for aligned edges.
        """
        # get paths based on edge type and layout
        if self.mark.tip_labels_align:
            apaths = []
            for tidx, _ in enumerate(self.mark.tip_labels_angles):
                adict = {
                    "cx": self.nodes_x[tidx],
                    "cy": self.nodes_y[tidx],
                    "px": self.tips_x[tidx],
                    "py": self.tips_y[tidx],
                }
                path = PATH_FORMAT["c"].format(**adict)
                apaths.append(path)

            # render the edge group
            self.align_xml = xml.SubElement(
                self.mark_xml,
                "g",
                attrib={"class": "toytree-AlignEdges"},
                style=concat_style_fix_color(self.mark.edge_align_style),
            )

            # render the edge paths
            for _, path in enumerate(apaths):
                xml.SubElement(self.align_xml, "path", d=path)

    def mark_admixture_edges(self):
        """Create SVG paths for admixture edges."""
        if self.mark.admixture_edges is None:
            return

        # iterate over colors for subsequent edges unless provided
        default_admix_edge_style = {
            "stroke": "rgb(90.6%,54.1%,76.5%)",
            "stroke-width": 5,
            "stroke-opacity": 0.6,
            "stroke-linecap": "round",
            "fill": "none",
            "font-size": "14px",
        }

        # create new group in the tree xml element for AdmixEdges
        self.admix_xml = xml.SubElement(
            self.mark_xml,
            "g",
            attrib={"class": "toytree-AdmixEdges"},
            style=concat_style_fix_color(default_admix_edge_style),
        )

        # path format for admix edge
        # branch1-start -> branch1-admix-event -> branch2-admix-event -> branch2-end
        path_format = [
            "M {sdx:.2f} {sdy:.2f}",
            "L {sux:.2f} {suy:.2f}",
            "L {ddx:.2f} {ddy:.2f}",
            "L {dux:.2f} {duy:.2f}",
        ]

        # create path subelement for each admixture edge
        for idx, aedge in enumerate(self.mark.admixture_edges):
            # int idx labels
            c_src, p_src = self.mark.etable[aedge.src]
            c_dst, p_dst = self.mark.etable[aedge.dst]

            if self.mark.layout not in ("r", "l", "u", "d"):
                raise ValueError(
                    f"admixture_edges drawing not supported for layout={self.mark.layout}"
                )

            if self.mark.layout in ("r", "l"):
                depth_coords = self.nodes_x
                span_coords = self.nodes_y
                depth_mid = self.mid_x
                span_mid = self.mid_y
                depth_axis = "x"
            else:
                depth_coords = self.nodes_y
                span_coords = self.nodes_x
                depth_mid = self.mid_y
                span_mid = self.mid_x
                depth_axis = "y"

            depth_sign = -1 if self.mark.layout in ("r", "d") else 1

            # get px coordinates of the src and dst nodes
            c_src_span, c_src_depth = span_coords[c_src], depth_coords[c_src]
            c_dst_span, c_dst_depth = span_coords[c_dst], depth_coords[c_dst]

            # get px coords of their parents
            p_src_span, p_src_depth = span_coords[p_src], depth_coords[p_src]
            p_dst_span, p_dst_depth = span_coords[p_dst], depth_coords[p_dst]

            # get pos of admix on src edge from src_dist else select midpoint on src edge
            if aedge.src_dist is None:
                a_src_span, a_src_depth = span_mid[c_src], depth_mid[c_src]
            else:
                Δspan = (
                    abs(p_src_span - c_src_span) if self.mark.edge_type == "c" else 0.0
                )
                Δdepth = abs(p_src_depth - c_src_depth)
                nudge = 0.0 if Δdepth == 0 else Δspan * (aedge.src_dist / Δdepth)
                a, b = self.axes.project(depth_axis, [0.0, nudge])
                a_src_span = c_src_span + abs(a - b)
                a, b = self.axes.project(depth_axis, [0.0, aedge.src_dist])
                a_src_depth = c_src_depth + (depth_sign * abs(a - b))

            # get ypos of admix on dst edge from dst_dist else select midpoint on dst edge
            if aedge.dst_dist is None:
                a_dst_span, a_dst_depth = span_mid[c_dst], depth_mid[c_dst]
            else:
                Δspan = (
                    abs(p_dst_span - c_dst_span) if self.mark.edge_type == "c" else 0.0
                )
                Δdepth = abs(p_dst_depth - c_dst_depth)
                nudge = 0.0 if Δdepth == 0 else Δspan * (aedge.dst_dist / Δdepth)
                a, b = self.axes.project(depth_axis, [0.0, nudge])
                a_dst_span = c_dst_span + abs(a - b)
                a, b = self.axes.project(depth_axis, [0.0, aedge.dst_dist])
                a_dst_depth = c_dst_depth + (depth_sign * abs(a - b))

            def to_screen(depth_value, span_value):
                if self.mark.layout in ("r", "l"):
                    return depth_value, span_value
                return span_value, depth_value

            # build the SVG path from top of src node edge to src-admix to dst-admix to dst node.
            sdx, sdy = to_screen(
                p_src_depth,
                c_src_span if self.mark.edge_type == "p" else p_src_span,
            )
            sux, suy = to_screen(a_src_depth, a_src_span)
            ddx, ddy = to_screen(a_dst_depth, a_dst_span)
            dux, duy = to_screen(c_dst_depth, c_dst_span)
            edge_dict = {
                "sdx": sdx,
                "sdy": sdy,
                "sux": sux,
                "suy": suy,
                "ddx": ddx,
                "ddy": ddy,
                "dux": dux,
                "duy": duy,
            }

            # EDGE path
            path = " ".join(path_format).format(**edge_dict)

            aedge_style = aedge.style.copy()
            if aedge_style.get("stroke") is None:
                aedge_style["stroke"] = COLORS2[idx % len(COLORS2)]

            # TODO: split style not needed.
            # estyle['stroke'] = split_rgba_style(estyle['stroke'])
            xml.SubElement(
                self.admix_xml,
                "path",
                d=path,
                style=concat_style_fix_color(aedge_style),
            )


# HELPER FUNCTIONS ----------------------
def get_unique_edge_styles(mark) -> List[Dict]:
    """Return dicts of unique edge stroke or width or each Node

    Reduces node styles to prevent redundancy in HTML.
    """
    # minimum styling of node markers
    unique_styles = [{} for i in range(mark.etable.shape[0])]

    # if edge widths and edge colors are both None then just return
    if (mark.edge_colors is None) & (mark.edge_widths is None):
        return unique_styles

    # iterate through styled node marks to get shared styles and expand axes
    for idx in range(mark.etable.shape[0]):
        if mark.edge_widths is not None:
            unique_styles[idx]["stroke-width"] = mark.edge_widths[idx]

        if mark.edge_colors is not None:
            unique_styles[idx]["stroke"] = mark.edge_colors[idx]

        # concat_style_to_str2() will interpret False to write no opacity style
        if mark.edge_style.get("stroke-opacity") is not None:
            unique_styles[idx]["stroke-opacity"] = False

    return unique_styles


def get_unique_node_styles(mark) -> List[Dict]:
    """Return dicts of unique styles (colors) for each Node."""
    unique_styles = [{} for i in range(mark.nnodes)]

    # only if variable tho
    if mark.node_colors is None:
        return unique_styles

    # get fill which will be split later into rgb, a
    for idx in range(mark.nnodes):
        unique_styles[idx]["fill"] = mark.node_colors[idx]
        if mark.node_style.get("fill-opacity") is not None:
            # special handling for transparency...
            unique_styles[idx]["fill-opacity"] = False
    return unique_styles


