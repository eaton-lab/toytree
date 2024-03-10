#!/usr/bin/env python

"""Dispatched renderer for toytree marks following the style of toyplot

TODO
----
  - fixed-order extension to tip positions for missing labels..?
  - container tree to Mark
  - Circle tree does not project y-axis...


<g class='pie-0'b style='stroke: black; stroke-width: 1'>
    <path d="M 1 0 A 1 1 0 0 1 0.8 0.5 L 0 0" style='fill:red'><path>
    <path d="M 1 0 A 0 1 0 0 1 0.8 0.5 L 0 0" style='fill:pink'><path>
                     r r x l s  x   y
</g>           |    |                  |
               move to start position on arc.
                    |                  |
                    arc: rx ry x-axis-rotation large-arc-floag sweep-flag x y
                         radius    always 0        %>50 or no    always 1  end
                                       |
                                       move to center of circle. 
"""

from typing import List, Dict, Tuple
import functools
import xml.etree.ElementTree as xml
from multipledispatch import dispatch
from loguru import logger
import numpy as np
import toyplot
from toytree.drawing import ToyTreeMark
from toytree.drawing.src.render_text import render_text
from toytree.drawing.src.render_marker import render_marker
from toytree.color.src.concat import concat_style_fix_color
from toytree.layout.src.get_edge_midpoints import get_edge_midpoints

# SVG path formats for creating edges in tree drawings
PATH_FORMAT = {
    'c': "M {px:.1f} {py:.1f} L {cx:.1f} {cy:.1f}",  # angular /\ format, good for any layout
    'b1': "M {px:.1f} {py:.1f} C {px:.1f} {cy:.1f}, {px:.1f} {cy:.1f}, {cx:.1f} {cy:.3f}",  # bezier 1 format
    'b2': "M {px:.1f} {py:.1f} C {cx:.1f} {py:.1f}, {cx:.1f} {py:.1f}, {cx:.1f} {cy:.3f}",  # bezier 2 format
    'p1': "M {px:.1f} {py:.1f} L {px:.1f} {cy:.1f} L {cx:.1f} {cy:.1f}",  # |_| phylo/angular format 1
    'p2': "M {px:.1f} {py:.1f} L {cx:.1f} {py:.1f} L {cx:.1f} {cy:.1f}",  # |_| phylo/angular format 2
    'pc': "M {cx:.1f} {cy:.1f} L {dx:.1f} {dy:.1f} A {rr:.1f} {rr:.1f} 0 0 {sweep} {px:.1f} {py:.1f}",  # phylo for circular
}

logger = logger.bind(name="toytree")

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
            context.parent, "g",
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
        self.nodes_x = self.axes.project('x', self.mark.ntable[:, 0])
        self.nodes_y = self.axes.project('y', self.mark.ntable[:, 1])
        self.tips_x = self.axes.project('x', self.mark.ttable[:, 0])
        self.tips_y = self.axes.project('y', self.mark.ttable[:, 1])
        mcoords = get_edge_midpoints(
            self.mark.etable, self.mark.ntable, self.mark.layout, self.mark.edge_type)
        self.mid_x = self.axes.project('x', mcoords[:, 0])
        self.mid_y = self.axes.project('y', mcoords[:, 1])

    def build_dom(self):
        """Creates DOM of xml.SubElements in self.context."""
        self.mark_edges()
        self.mark_align_edges()
        self.mark_admixture_edges()
        self.mark_nodes()
        self.mark_node_labels()

        # for multitrees tips are sometimes not drawn.
        self.mark_tip_labels()

    def get_paths(self) -> Tuple[List[str], List[str]]:
        """Return paths and keys in idx order.

        This will build the d="..." path string for the SVG lines
        for edges of the tree. Depending on the edge_type this can be
        relatively simple or more complex.
        """
        # modify order of x or y shift of edges for p,b types.
        if self.mark.edge_type in ('p', 'b'):

            # phylo |_| edge type for cirular trees:
            if self.mark.layout[0] == 'c':
                path_format = PATH_FORMAT["pc"]

                # get differences of nodes relative to root. Note: this is
                # b/c origin is not at (0, 0) if [x,y]baseline was used.
                xdiffs = self.mark.ntable[:, 0] - self.mark.ntable[-1, 0]
                ydiffs = self.mark.ntable[:, 1] - self.mark.ntable[-1, 1]
                radii = np.sqrt(xdiffs ** 2 + ydiffs ** 2)

                # get angles of nodes relative to root in radians (0, 2pi)
                radians = np.arctan2(ydiffs, xdiffs)
                radians[radians < 0] = (2 * np.pi) + radians[radians < 0]

            # phylo or bezier type for non-circular trees. Select the
            # appropriate type given orientation: p1, p2, or b1, b2
            elif self.mark.layout in ('u', 'd'):
                path_format = PATH_FORMAT[f"{self.mark.edge_type}2"]
            else:
                path_format = PATH_FORMAT[f"{self.mark.edge_type}1"]

        # cladogram (\/) style, simplest for any layout
        else:
            path_format = PATH_FORMAT[self.mark.edge_type]

        # store paths here
        paths = []
        keys = []

        # TODO: change here if you want to show the root edge...
        for idx in range(self.mark.nnodes - 1):
            cidx, pidx = self.mark.etable[idx]
            child_x, child_y = self.nodes_x[cidx], self.nodes_y[cidx]
            parent_x, parent_y = self.nodes_x[pidx], self.nodes_y[pidx]

            # for simple edge format (e.g., 'c', 'b')
            if "A" not in path_format:
                keys.append(f"{pidx},{cidx}")
                paths.append(
                    path_format.format(**{
                        'cx': child_x, 'cy': child_y,
                        'px': parent_x, 'py': parent_y,
                    })
                )

            # for 'p' edge format
            else:
                # get radius at parent's level
                xdiff = parent_x - self.nodes_x[-1]
                ydiff = parent_y - self.nodes_y[-1]
                parent_radius = np.sqrt(xdiff ** 2 + ydiff ** 2)

                mid_x = radii[pidx] * np.cos(radians[cidx])
                mid_y = radii[pidx] * np.sin(radians[cidx])

                # project mid points into coordinate space
                px_mid_x = self.axes.project('x', mid_x)
                px_mid_y = self.axes.project('y', mid_y)

                # logger.warning(f"{cidx} {radians[pidx]:.2f} {radians[cidx]:.2f} sweep={int(radians[pidx] < radians[cidx])}")
                keys.append(f"{pidx},{cidx}")
                paths.append(
                    path_format.format(**{
                        'cx': child_x,
                        'cy': child_y,
                        'px': parent_x,
                        'py': parent_y,
                        'dx': px_mid_x,
                        'dy': px_mid_y,
                        'rr': parent_radius,
                        'sweep': int(radians[pidx] < radians[cidx]),  # 1=counter-clockwise, 0=clockwise
                    })
                )
            # keys.append('root-edge')
            # paths.append(
            #     path_format.format(**{
            #         'cx': self.nodes_x[-1],
            #         'cy': self.nodes_y[-1],
            #         'px': self.nodes_x[-1],
            #         'py': self.nodes_y[-1] + self.mark.root_dist,
            #     })
            # )
        return paths, keys

    def mark_edges(self) -> None:
        """Create SVG paths for each tree edge as class toytree-Edges"""
        # get paths based on edge type and layout
        paths, keys = self.get_paths()

        # !always pop 'fill' to set it to 'fill:none' below (no fill btwn edges).
        _ = self.mark.edge_style.pop('fill', None)

        # render the edge group.
        # TODO: consider adding stroke-linejoin:round
        self.edges_xml = xml.SubElement(
            self.mark_xml, "g",
            attrib={"class": "toytree-Edges"},
            style=concat_style_fix_color(self.mark.edge_style, "fill:none")
        )

        # get shared versus unique styles (EdgeStyles)
        unique_styles = get_unique_edge_styles(self.mark)
        # unique_styles.append({"stroke-width": 1.0})
        # logger.info(unique_styles)

        # render the edge paths
        for idx, path in enumerate(paths):
            xml.SubElement(
                self.edges_xml, "path",
                d=path,
                id=keys[idx],
                style=concat_style_fix_color(unique_styles[idx])
            )

    def mark_nodes(self) -> None:
        """Create marker elements for each node in class toytree-Nodes.

        Stores ids to the nodes which in theory can allow for
        downstream JS interactivity.
        """
        # Group all Nodes with shared style applied
        self.nodes_xml = xml.SubElement(
            self.mark_xml, "g",
            attrib={"class": "toytree-Nodes"},
            style=concat_style_fix_color(self.mark.node_style)
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
                self.nodes_xml, "g",
                attrib={"id": f"Node-{nidx}"},
                style=concat_style_fix_color(unique_styles[nidx]),
            )

            # if style string is empty then remove it.
            if not marker_xml.attrib['style']:
                _ = marker_xml.attrib.pop('style')

            # optionally add a title (hover) here only if there is no
            # node_label, otherwise we put the hover on the label later.
            if self.mark.node_hover is not None:
                if self.mark.node_labels is None:
                    xml.SubElement(marker_xml, "title").text = (
                        self.mark.node_hover[nidx])

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
        """Create Node labels in toytree-NodeLabels using render_text"""
        if self.mark.node_labels is None:
            return

        # shared styles popped from text boxes AFTER positioning
        shared_style = {
            "font-size": self.mark.node_labels_style['font-size'],
            "font-weight": self.mark.node_labels_style['font-weight'],
            "font-family": self.mark.node_labels_style['font-family'],
            "vertical-align": "baseline",
            "white-space": "pre",
        }

        # create NodeLabels group element
        node_labels_xml = xml.SubElement(
            self.mark_xml, "g",
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
                "-toyplot-vertical-align": "middle", # baseline not supported.
                "text-anchor": "middle", # start is another option.
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
            "font-size": self.mark.tip_labels_style['font-size'],
            "font-weight": self.mark.tip_labels_style['font-weight'],
            "font-family": self.mark.tip_labels_style['font-family'],
            "fill": self.mark.tip_labels_style['fill'],
            "vertical-align": "baseline",
            "white-space": "pre",
        }

        # Make the <g> TipLabels group element
        tips_xml = xml.SubElement(
            self.mark_xml, "g",
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
                tstyle["-toyplot-anchor-shift"], "px", "px",
            )

            if self.mark.layout in 'rd':
                angle = self.mark.tip_labels_angles[idx]

            # reverse labels
            elif self.mark.layout in 'lu':
                angle = self.mark.tip_labels_angles[idx]
                tstyle['-toyplot-anchor-shift'] = -offset
                tstyle['text-anchor'] = "end"

            # 'c' or unrooted
            else:
                angle = self.mark.tip_labels_angles[idx]
                if 90 < angle < 270:
                    tstyle['text-anchor'] = "end"
                    tstyle['-toyplot-anchor-shift'] = -offset
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
                style=concat_style_fix_color(self.mark.edge_align_style),
            )

            # render the edge paths
            for _, path in enumerate(apaths):
                xml.SubElement(self.align_xml, "path", d=path)

    def mark_admixture_edges(self):
        """Create SVG paths for admixture edges.

        The edge takes the same style as the edge_type of the tree.

        (SRC, DEST, PROP, {STYLE}, TEXT)
        """
        if self.mark.admixture_edges is None:
            return

        # iterate over colors for subsequent edges unless provided
        default_admix_edge_style = {
            "stroke": 'rgb(90.6%,54.1%,76.5%)',
            "stroke-width": 5,
            "stroke-opacity": 0.6,
            "stroke-linecap": "round",
            "fill": "none",
            "font-size": "14px"
        }

        # create edge group element
        self.admix_xml = xml.SubElement(
            self.mark_xml, 'g',
            attrib={'class': 'toytree-AdmixEdges'},
            style=concat_style_fix_color(default_admix_edge_style)
        )

        # get position of 15% tipward from source point
        path_format = [
            "M {sdx:.2f} {sdy:.2f}",
            "L {sux:.2f} {suy:.2f}",
            "L {ddx:.2f} {ddy:.2f}",
            "L {dux:.2f} {duy:.2f}",
        ]

        # ensure admixture_edges is a list of tuples
        if not isinstance(self.mark.admixture_edges, list):
            self.mark.admixture_edges = [self.mark.admixture_edges]

        # drwa each edge
        for aedge in self.mark.admixture_edges:

            # check if nodes have an overlapping interval
            src, dest, *details = aedge

            # parse optional prop float, edgestyle dict, and label text
            aprop = 0.5
            estyle = {}
            label = ""
            if len(details) == 1:
                aprop = details[0]
            elif len(details) == 2:
                aprop, estyle = details
            elif len(details) == 3:
                aprop, estyle, label = details

            # get their parents coord positions
            try:
                psrc = self.mark.etable[self.mark.etable[:, 0] == src, 1][0]
            except IndexError:
                psrc = self.mark.nnodes - 1
            try:
                pdest = self.mark.etable[self.mark.etable[:, 0] == dest, 1][0]
            except IndexError:
                pdest = self.mark.nnodes - 1

            # if only one midpoint then expand to use same for both edges.
            shared = False
            if isinstance(aprop, (int, float)):
                shared = True
                aprop = (aprop, aprop)

            # separate for each layout b/c its haaaard.
            if self.mark.layout in ("r", "l"):
                src_x, src_y = self.nodes_y[src], self.nodes_x[src]
                dst_x, dst_y = self.nodes_y[dest], self.nodes_x[dest]
                p_src_x, p_src_y = self.nodes_y[psrc], self.nodes_x[psrc]
                p_dst_x, p_dst_y = self.nodes_y[pdest], self.nodes_x[pdest]

                # ...
                if self.mark.layout == 'r':
                    disjoint = (p_src_y >= dst_y) or (src_y <= p_dst_y)
                    sign = 1
                else:
                    disjoint = (p_src_y >= dst_y) or (src_y <= p_dst_y)
                    sign = -1

                # ...
                if disjoint or (not shared):
                    src_mid_y = src_y - sign * (abs(src_y - p_src_y) * aprop[0])
                    dest_mid_y = dst_y - sign * (abs(dst_y - p_dst_y) * aprop[1])
                else:
                    # get height of the admix line at midshared.
                    amin = min([src_y, dst_y])
                    amax = max([p_src_y, p_dst_y])
                    admix_ymid = amin + (amax - amin) * aprop[0]
                    dest_mid_y = src_mid_y = admix_ymid

            elif self.mark.layout in ("u", "d"):
                # get x and y of source and destination nodes
                src_x, src_y = self.nodes_x[src], self.nodes_y[src]
                dst_x, dst_y = self.nodes_x[dest], self.nodes_y[dest]

                # get x and y of PARENTS of source and destination nodes
                p_src_x, p_src_y = self.nodes_x[psrc], self.nodes_y[psrc]
                p_dst_x, p_dst_y = self.nodes_x[pdest], self.nodes_y[pdest]

                # check whether the edges overlap, in which case we will
                # draw a straight line between them, otherwise the line
                # will be angled. Straight it preferred.
                if self.mark.layout == "d":
                    disjoint = (dst_y <= p_src_y) or (src_y <= p_dst_y)
                    sign = 1
                else:
                    disjoint = (dst_y >= p_src_y) or (src_y >= p_dst_y)
                    sign = -1

                if disjoint or (not shared):
                    src_mid_y = src_y - sign * (abs(src_y - p_src_y) * aprop[0])
                    dest_mid_y = dst_y - sign * (abs(dst_y - p_dst_y) * aprop[1])
                else:
                    amin = min([src_y, dst_y])
                    amax = max([p_src_y, p_dst_y])
                    admix_ymid = amin - sign * abs(amax - amin) * aprop[0]
                    dest_mid_y = src_mid_y = admix_ymid

            # project angle of up/down lines towards parent nodes.
            if self.mark.edge_type == "c":

                # angle from src to src parent
                if (p_src_x - src_x) == 0:
                    x_shift_src_mid = 0
                else:
                    theta = np.arctan((p_src_y - src_y) / (p_src_x - src_x))
                    x_shift_src_mid = (src_mid_y - src_y) / np.tan(theta)

                # angle from dest to dest parent
                if (p_dst_x - dst_x) == 0:
                    x_shift_dest_mid = 0
                else:
                    theta = np.arctan((p_dst_y - dst_y) / (p_dst_x - dst_x))
                    x_shift_dest_mid = (dest_mid_y - dst_y) / np.tan(theta)
                xend = p_dst_x

            else:
                x_shift_dest_mid = 0
                x_shift_src_mid = 0
                xend = dst_x

            # build the SVG path
            if self.mark.layout in ("r", "l"):
                edge_dict = {
                    'sdy': src_x,  # + x_shift_src_tip + snudge,
                    'sdx': src_y,  # src_tip_y,
                    'suy': src_x + x_shift_src_mid,
                    'sux': src_mid_y,  # admix_ymid,
                    'ddy': dst_x + x_shift_dest_mid,
                    'ddx': dest_mid_y,  # admix_ymid,
                    'duy': xend,
                    'dux': p_dst_y,  # dest_tip_y,
                }
                # tri_dict = {
                #     'x0': admix_ymid - 6,
                #     'x1': admix_ymid + 6,
                #     'x2': admix_ymid,
                #     'y0': np.mean([edge_dict['suy'], edge_dict['ddy']]) - 6,
                #     'y1': np.mean([edge_dict['suy'], edge_dict['ddy']]) - 6,
                #     'y2': np.mean([edge_dict['suy'], edge_dict['ddy']]) + 8,
                # }

            else:
                edge_dict = {
                    'sdx': src_x,  # + x_shift_src_tip + snudge,
                    'sdy': src_y,  # src_tip_y,

                    'sux': src_x + x_shift_src_mid,
                    'suy': src_mid_y,  # admix_ymid,

                    'ddx': dst_x + x_shift_dest_mid,
                    'ddy': dest_mid_y,  # admix_ymid,

                    'dux': xend,
                    'duy': p_dst_y,  # dest_tip_y,
                }

                # TODO: not finished aligning triangle/arrow
                # tri_dict = {
                #     'y0': admix_ymid - 6,
                #     'y1': admix_ymid + 6,
                #     'y2': admix_ymid,
                #     'x0': np.mean([edge_dict['suy'], edge_dict['ddy']]) - 6,
                #     'x1': np.mean([edge_dict['suy'], edge_dict['ddy']]) - 6,
                #     'x2': np.mean([edge_dict['suy'], edge_dict['ddy']]) + 8,
                # }

            # EDGE path
            path = " ".join(path_format).format(**edge_dict)

            # TODO: split style not needed.
            # estyle['stroke'] = split_rgba_style(estyle['stroke'])
            xml.SubElement(
                self.admix_xml, "path",
                d=path,
                style=concat_style_fix_color(estyle),
            )

            lstyle = estyle.copy()
            # LABEL
            if label is not None:

                # RENDER edge label
                lstyle['fill'] = '#262626'
                lstyle['fill-opacity'] = '1.0'
                lstyle['stroke'] = "none"
                lstyle['text-anchor'] = 'middle'

                # position
                if self.mark.layout in ("r", "l"):
                    xtext = np.mean([src_x + x_shift_src_mid, dst_x + x_shift_dest_mid])
                    ytext = np.mean([src_mid_y, dest_mid_y])
                    xtext += 12
                else:
                    ytext = np.mean([src_x + x_shift_src_mid, dst_x + x_shift_dest_mid])
                    xtext = np.mean([src_mid_y, dest_mid_y])

                xml.SubElement(
                    self.admix_xml,
                    "text",
                    x=f"{ytext:.2f}",
                    y=f"{xtext:.2f}",
                    style=concat_style_fix_color(lstyle),
                ).text = str(label)


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
            unique_styles[idx]['stroke-width'] = mark.edge_widths[idx]

        if mark.edge_colors is not None:
            unique_styles[idx]['stroke'] = mark.edge_colors[idx]

        # concat_style_to_str2() will interpret False to write no opacity style
        if mark.edge_style.get("stroke-opacity") is not None:
            unique_styles[idx]['stroke-opacity'] = False

    return unique_styles


def get_unique_node_styles(mark) -> List[Dict]:
    """Return dicts of unique styles (colors) for each Node."""
    unique_styles = [{} for i in range(mark.nnodes)]

    # only if variable tho
    if mark.node_colors is None:
        return unique_styles

    # get fill which will be split later into rgb, a
    for idx in range(mark.nnodes):
        unique_styles[idx]['fill'] = mark.node_colors[idx]
        if mark.node_style.get("fill-opacity") is not None:
            # special handling for transparency...
            unique_styles[idx]['fill-opacity'] = False
    return unique_styles


def test1():
    tree = toytree.rtree.rtree(8, seed=123)
    kwargs = dict(
        ts='p',
        layout='r', #'c0-95',
        tip_labels_align=True,
        edge_type='p',
        width=400,
        height=400,
        node_sizes=18,
        node_colors=None,
        node_mask=False,
        node_hover=True,
        node_labels=True,
        node_labels_style={"font-size": 15, "fill": "black"},
        edge_style={"stroke-width": 3.5},
        node_style={"stroke-width": 2},
        tip_labels_style={"font-size": 15, "-toyplot-anchor-shift": 15},
        # tip_labels_colors=[toytree.color.COLORS1[i] for i in range(tree.ntips)],
        # edge_colors=['red'] + [toytree.color.COLORS1[0]] + ['black'] * (tree.nnodes - 2),
    )
    tree._draw_browser(**kwargs)


def test2():
    # generate a random species tree with 10 tips and a crown age of 10M generations
    tree = toytree.rtree.unittree(10, treeheight=1e6, seed=123)
    # create a new tree copy with Ne values mapped to nodes
    vtree = tree.set_node_data(
        feature="Ne",
        data={i: 2e5 for i in (6, 7, 8, 9, 12, 15, 17)},
        default=1e4,
    )
    vtree._draw_browser(ts='p', )#admixture_edges=[(0, 12, 0.5, {}, "word")]);


if __name__ == "__main__":

    import toytree
    toytree.set_log_level("DEBUG")
    test2()
