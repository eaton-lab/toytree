#!/usr/bin/env python

"""Dispatched renderer for toytree marks following the style of toyplot

TODO
----
  - fixed-order extension to tip positions for missing labels..?
  - container tree to Mark
  - Cirlce tree does not project y-axis...
"""

import functools
import xml.etree.ElementTree as xml
from multipledispatch import dispatch
from loguru import logger
import numpy as np
import toyplot
from toyplot.html import (_draw_bar, _draw_triangle, _draw_circle, _draw_rect)
from toytree.core.drawing.toytree_mark import ToytreeMark
from toytree.core.drawing.render_text import render_text
from toytree.utils.src.globals import PATH_FORMAT

logger = logger.bind(name="toytree")

# Register multipledispatch to use the toyplot.html namespace
dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)

# register a _render function for ToyTreeMark objects
@dispatch(toyplot.coordinates.Cartesian, ToytreeMark, toyplot.html.RenderContext)
def _render(axes, mark, context):
    RenderToytree(axes, mark, context)


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

        # construction funcs
        self.project_coordinates()
        self.build_dom()

    def build_dom(self):
        """Creates DOM of xml.SubElements in self.context."""
        self.mark_toytree()
        self.mark_edges()
        self.mark_align_edges()
        self.mark_admixture_edges()
        self.mark_nodes()
        self.mark_node_labels()

        # for multitrees tips are sometimes not drawn.
        self.mark_tip_labels()

    def project_coordinates(self):
        """Store node coordinates (data units) projected to pixel units.

        TODO: this could be mostly replaced by improvements to
        ToyTree.get_node_coordinates()
        """
        # project data coordinates into pixels
        self.nodes_x = self.axes.project('x', self.mark.ntable[:, 0])
        self.nodes_y = self.axes.project('y', self.mark.ntable[:, 1])

        # if circular layout then also get radius
        if self.mark.layout[0] == 'c':
            self.radii = self.axes.project('x', self.mark.radii)
            self.maxr = max(self.radii) # used to tips-labels-align
            logger.debug(
                f"maxr: {self.maxr:.2f}"
                f"\nself.mark.radii: {self.mark.radii}\nmark.radii: {self.radii}")

        # if tip labels align then store tips projected coords
        if self.mark.tip_labels_align:

            # coords of aligned tips across fixed x axis 0
            ntips = self.mark.tip_labels_angles.size
            if self.mark.layout == 'r':
                self.tips_x = np.repeat(self.nodes_x.max(), ntips)
                self.tips_y = self.nodes_y[:ntips]
            elif self.mark.layout == 'l':
                self.tips_x = np.repeat(self.nodes_x.min(), ntips)
                self.tips_y = self.nodes_y[:ntips]
            elif self.mark.layout == 'u':
                self.tips_y = np.repeat(self.nodes_y.min(), ntips)
                self.tips_x = self.nodes_x[:ntips]
            elif self.mark.layout == 'd':
                self.tips_y = np.repeat(self.nodes_y.max(), ntips)
                self.tips_x = self.nodes_x[:ntips]

            # coords of tips around a circumference
            elif self.mark.layout[0] == 'c':
                self.tips_x = np.zeros(ntips)
                self.tips_y = np.zeros(ntips)
                for idx, angle in enumerate(self.mark.tip_labels_angles):
                    radian = np.deg2rad(angle)
                    cordx = 0 + max(self.mark.radii) * np.cos(radian)
                    cordy = 0 + max(self.mark.radii) * np.sin(radian)
                    self.tips_x[idx] = self.axes.project('x', cordx)
                    self.tips_y[idx] = self.axes.project('y', cordy)

    def get_paths(self):
        """Return paths and keys in idx order.

        This will build the d="..." path string for the SVG lines 
        for edges of the tree. Depending on the edge_type this can be
        relatively simple or more complex.
        """
        # modify order of x or y shift of edges for p,b types.
        if self.mark.edge_type in ('p', 'b'):
            # selects pc
            if self.mark.layout[0] == 'c':
                path_format = PATH_FORMAT["pc"]
                # logger.warning(
                #     "edge_type='p' w/ layout='c' not currently supported. "
                #     "Contact developers to make a request. Changing "
                #     "edge_type to 'c' for now."
                # )
                # path_format = PATH_FORMAT['c']

            # selects p1, p2, or b1, b2
            elif self.mark.layout in ('u', 'd'):
                path_format = PATH_FORMAT[f"{self.mark.edge_type}2"]
            else:
                path_format = PATH_FORMAT[f"{self.mark.edge_type}1"]
        else:
            # select c (simplest)
            path_format = PATH_FORMAT[self.mark.edge_type]

        # store paths here
        paths = []
        keys = []
        for idx in range(self.mark.nnodes - 1):
            #pidx, cidx = self.mark.etable[idx]
            cidx, pidx = self.mark.etable[idx]
            child_x, child_y = self.nodes_x[cidx], self.nodes_y[cidx]
            parent_x, parent_y = self.nodes_x[pidx], self.nodes_y[pidx]

            # circle 'p' format each line is towards root, then across arc
            # if self.mark.layout[0] == 'c':

            if "A" in path_format:

                # get angle from node to the root
                dy = (self.nodes_y[-1] - child_y)
                dx = (child_x - self.nodes_x[-1])
                theta = 0 if dx == 0 else np.arctan(dy / dx) 
                logger.info(f"dx={dx:.2f} dy={dy:.2f}")

                # get length of edge
                dist = self.radii[idx] - self.radii[pidx]

                # get length of radius to new fake node.
                rdist = self.radii[idx] - dist

                # get x, y positions of the fake node
                logger.info(f"theta={theta:.2f}, rdist={rdist:.2f} {self.radii[idx]:.2f} {self.radii[pidx]:.2f} {dist:.2f}")

                # get length of adjacent ( change in x relative to O )
                x = (dist * np.cos(theta)) #- self.nodes_x[-1]
                logger.info(f"o={self.nodes_x[-1]:.2f}, x={(rdist * np.cos(theta)):.2f}")

                y = (dist * np.sin(theta)) #+ self.nodes_y[-1] 
                logger.info(f"o={self.nodes_y[-1]:.2f}, y={(rdist * np.sin(theta)):.2f}")
                logger.warning("")
                # logger.info(f"{idx} theta={theta:.2f} r={dist:.1f} "
                    # f"rd={rdist:.2f} "
                    # f"x={ + x:.2f} " 
                    # f"y={self.nodes_y[-1] + y:.2f}")
                # dy = dist * np.sin(theta)

                # get start position
                # "M {cx:.1f} {cy:.1f}
                # move towards center of circle (y)
                # L {dx:.1f} {dy:.1f}
                # arc: rx ry x-axis-rotation large-arc-flag sweeep flag x y
                # A {rr:.1f} {rr:.1f} 0 0 {flag} {px:.1f} {py:.1f}",
                # logger.info(f"idx={idx}, mark={self.mark.ntable[idx]}, x={child_x:.2f}, y={child_y:.2f}, px={parent_x:.2f}, py={parent_y:.2f}, angle: {angle:.2f}")
                keys.append(f"{pidx},{cidx}")
                paths.append(
                    path_format.format(**{
                        'cx': child_x, 'cy': child_y,
                        'px': parent_x, 'py': parent_y,
                        'dx': child_x - x, 'dy': child_y + y,
                        'rr': dist, 'flag': 0,
                    })
                )

            # build path string for simple types
            else:
                keys.append(f"{pidx},{cidx}")
                paths.append(
                    path_format.format(**{
                        'cx': child_x, 'cy': child_y,
                        'px': parent_x, 'py': parent_y,
                    })
                )
        return paths, keys

    def mark_toytree(self):
        """TODO: Creates the top-level Toytree mark. Not required."""

    def mark_edges(self):
        """Create SVG paths for each tree edge as class toytree-Edges"""
        # get paths based on edge type and layout
        paths, keys = self.get_paths()

        # get shared versus unique styles
        unique_styles = get_unique_edge_styles(self.mark)
        self.mark.edge_style['fill'] = "none"

        # render the edge group
        self.edges_xml = xml.SubElement(
            self.mark_xml, "g",
            attrib={"class": "toytree-Edges"},
            style=style_to_string({
                i: j for (i, j) in self.mark.edge_style.items()
                if j is not None
            })
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
        """Create marker elements for each node in class toytree-Nodes.

        Stores ids to the nodes which in theory can allow for
        downstream JS interactivity.
        """
        # skip if all node_mask=True or if all node_sizes=0
        if (self.mark.node_sizes == 0).all():
            return
        if self.mark.node_mask.all():
            return

        # get fill style if differs among nodes
        unique_styles = [{} for i in range(self.mark.nnodes)]

        # only if variable tho
        if not self.mark.node_colors is None:

            # get fill and fill-opacity of each mark (levelorder)
            for idx in range(self.mark.nnodes):

                # get the rgba node color
                fill = self.mark.node_colors[idx]

                # split into rgb and opacity and store result dict
                unique_styles[idx] = split_rgba_style({'fill': fill})

                # default fill-opacity is None, so if it is set use it
                if self.mark.node_style['fill-opacity'] is not None:
                    unique_styles[idx]['fill-opacity'] = (
                        self.mark.node_style['fill-opacity'])

        # Group all Nodes with shared style applied
        self.nodes_xml = xml.SubElement(
            self.mark_xml, "g",
            attrib={"class": "toytree-Nodes"},
            style=style_to_string({
                i: j for (i, j) in self.mark.node_style.items()
                if j is not None
            }),
        )

        # add node markers in reverse idx order (levelorder traversal)
        for nidx in range(self.mark.nnodes):

            # skip if node is masked
            if self.mark.node_mask[nidx]:
                continue

            # create marker with shape and size, e.g., <marker='o' size=12>
            marker = toyplot.marker.create(
                shape=self.mark.node_markers[nidx],
                size=self.mark.node_sizes[nidx],
            )

            # create the marker
            marker_xml = xml.SubElement(
                self.nodes_xml, "g",
                attrib={'id': f'node-{nidx}'},
                style=style_to_string(unique_styles[nidx]),
            )
            if not marker_xml.attrib['style']:
                marker_xml.attrib.pop('style')

            # optionally add a title UNLESS node_label, then put the hover
            # on the node text instead.
            if self.mark.node_hover is not None:
                if self.mark.node_labels is None:
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
        """Create Node labels in toytree-NodeLabels using render_text"""
        if self.mark.node_labels is None:
            return

        # shared styles popped from text boxes AFTER positioning
        shared_style = {
            "stroke": "none",
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
            style=style_to_string(shared_style),
        )

        for idx in range(self.mark.nnodes):

            if self.mark.node_mask[idx]:
                continue

            label = self.mark.node_labels[idx]
            title = None
            if self.mark.node_hover is not None:
                title = self.mark.node_hover[idx]

            # self.mark.node_labels_style["text-anchor"] = "start"
            nlstyle = toyplot.style.combine({
                "-toyplot-vertical-align": "middle",
                "text-anchor": "middle",
                },
                self.mark.node_labels_style,
            )
            render_text(
                root=node_labels_xml,
                text=label,
                x=self.nodes_x[idx],
                y=self.nodes_y[idx],
                angle=0,
                attributes={"class": "toytree-NodeLabel"},
                style=nlstyle,
                title=title,
            )

    def mark_tip_labels(self):
        """Create tip labels in toytree-TipLabels using render_text."""
        if self.mark.tip_labels is None:
            return

        # TipLabels style keys are popped from TipLabel styles, but
        # do not include positioning styles, which must be passed on.
        shared_style = {"stroke": "none"}
        if self.mark.tip_labels_style['fill'] is not None:
            # sets fill and fill-opacity
            shared_style.update(
                split_rgba_style({"fill": self.mark.tip_labels_style['fill']}))
        if self.mark.tip_labels_style['fill-opacity'] is not None:
            # overrides fill-opacity from splitting fill above
            shared_style.update(
                {'fill-opacity': self.mark.tip_labels_style['fill-opacity']})

        # shared styles popped from text boxes AFTER positioning
        shared_style.update({
            "font-size": self.mark.tip_labels_style['font-size'],
            "font-weight": self.mark.tip_labels_style['font-weight'],
            "font-family": self.mark.tip_labels_style['font-family'],
            "vertical-align": "baseline",
            "white-space": "pre",
        })

        # Make the TipLabels group element
        tips_xml = xml.SubElement(
            self.mark_xml, "g",
            attrib={"class": "toytree-TipLabels"},
            style=style_to_string(shared_style),
        )

        # add tip markers from 0 to ntips
        for idx, tip in enumerate(self.mark.tip_labels):

            # align tip at end for tip_labels_align=True
            cxx = self.nodes_x[idx]
            cyy = self.nodes_y[idx]
            if self.mark.tip_labels_align:
                cxx = self.tips_x[idx]
                cyy = self.tips_y[idx]

            # assign tip substyle
            tstyle = self.mark.tip_labels_style.copy()
            if self.mark.tip_labels_colors is not None:
                colstyle = split_rgba_style({
                    "fill": self.mark.tip_labels_colors[idx]
                })
                tstyle['fill'] = colstyle['fill']
                # allow style fill-opacity to override
                if self.mark.tip_labels_style['fill-opacity'] is None:
                    tstyle['fill-opacity'] = colstyle['fill-opacity']
            else:
                tstyle.pop('fill')
                tstyle.pop('fill-opacity')

            # assign tip layout positioning
            offset = toyplot.units.convert(
                tstyle["-toyplot-anchor-shift"], "px", "px",
            )
            angles = self.mark.tip_labels_angles[idx]
            if self.mark.layout in ['l', 'u']:
                angles = self.mark.tip_labels_angles[idx]
                tstyle['-toyplot-anchor-shift'] = -offset
                tstyle['text-anchor'] = "end"
            if self.mark.layout[0] == 'c':
                angles = self.mark.tip_labels_angles[idx]

            # add text
            render_text(
                root=tips_xml,
                text=tip,
                x=cxx,
                y=cyy,
                angle=angles,
                attributes={"class": "toytree-TipLabel"},
                style=tstyle,
            )

    def mark_align_edges(self):
        """Create SVG paths for each tip to 0 or radius. """
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
                style=style_to_string({
                    i: j for (i, j) in self.mark.edge_align_style.items()
                    if j is not None
                })
            )

            # render the edge paths
            for _, path in enumerate(apaths):
                xml.SubElement(self.align_xml, "path",  d=path)

    def mark_admixture_edges(self):
        """Create SVG paths for admixture edges.

        The edge takes the same style as the edge_type of the tree.
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
            style=style_to_string(default_admix_edge_style)
        )

        # get position of 15% tipward from source point
        path_format = [
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
            src, dest, aprop, estyle, label = aedge

            # get their parents coord positions
            try:
                psrc = self.mark.etable[self.mark.etable[:, 0] == src, 1][0]
                pdest = self.mark.etable[self.mark.etable[:, 0] == dest, 1][0]

            # except if root edge
            except IndexError as err:
                raise NotImplementedError(
                    "whoops, admixture edge error (root node?). TODO."
                    ) from err

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

                if self.mark.layout == 'r':
                    disjoint = (p_src_y >= dst_y) or (src_y <= p_dst_y)
                    sign = 1
                else:
                    disjoint = (p_src_y >= dst_y) or (src_y <= p_dst_y)
                    sign = -1

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
            estyle['stroke'] = split_rgba_style(estyle['stroke'])
            xml.SubElement(
                self.admix_xml, "path",
                d=path,
                style=style_to_string(estyle),
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
                    style=style_to_string(lstyle),
                ).text = str(label)


# HELPER FUNCTIONS ----------------------
def get_unique_edge_styles(mark):
    """Reduces node styles to prevent redundancy in HTML."""
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
            subd = split_rgba_style({'stroke': mark.edge_colors[idx]})
            unique_styles[idx]['stroke'] = subd['stroke']
            if mark.edge_style['stroke-opacity'] is None:
                unique_styles[idx]['stroke-opacity'] = subd['stroke-opacity']
    return unique_styles


def split_rgba_style(style):
    """Split rgba to rgb and opacity.

    Because many applications (Inkscape, Adobe Illustrator, Qt) don't handle
    CSS rgba() colors correctly this function does a work-around.
    Takes a CSS color in rgba, e.g., 'rgba(40.0%,76.1%,64.7%,1.000)'
    labeled in a dictionary as {'fill': x, 'fill-opacity': y} and
    returns with fill as rgb and fill-opacity from rgba or clobbered
    by the fill-opacity arg. Similar functionality for stroke, stroke-opacity.

    TODO: move this to the Color module?
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
    """Return a style dict as a style string.

    Example
    -------
    >>> x = {'fill': 'rgb(100%,0%,0%)', 'fill-opacity': 1.0}
    >>> print(style_to_string(x))
    >>> # 'fill:rgb(100%,0%,0%);fill-opacity:1.0'
    """
    strs = [f"{key}:{value}" for key, value in sorted(style.items())]
    return ";".join(strs)


if __name__ == "__main__":

    import ipcoal
    import toytree
    toytree.set_log_level("INFO")

    # generate a random species tree with 10 tips and a crown age of 10M generations
    # tree = toytree.rtree.unittree(10, treeheight=1e6, seed=123)
    # # create a new tree copy with Ne values mapped to nodes
    # vtree = tree.set_node_data(
    #     feature="Ne",
    #     mapping={i: 2e5 for i in (6, 7, 8, 9, 12, 15, 17)},
    #     default=1e4,
    # )
    # vtree._draw_browser(ts='p', admixture_edges=[(0, 12, 0.5, {}, "word")]);

    tree = toytree.rtree.unittree(5, seed=123)
    kwargs = dict(
        ts='p',
        layout='c0-95',
        edge_type='p',
        width=800,
        node_sizes=0,
        node_mask=False,
        tip_labels_style={"font-size": 14, "-toyplot-anchor-shift": 10},
        edge_colors=['red'] + ['blue'] + ['black'] * (tree.nnodes - 2),
    )
    tree._draw_browser(**kwargs)