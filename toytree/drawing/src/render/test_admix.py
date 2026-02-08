

# from typing import Any
import numpy as np
import xml.etree.ElementTree as xml
from toytree.color.src.concat import concat_style_fix_color
from toytree.network import AdmixtureEdges


def get_admixture_edge_subelements(
    mark_xml: xml.SubElement,
    admixture_edges: list[AdmixtureEdges],
    etable: np.ndarray,
    ntable: np.ndarray,
    layout: str,
    ):
    """Create SVG paths for admixture edges.

    The edge takes the same style as the edge_type of the tree.
    """
    # iterate over colors for subsequent edges unless provided
    default_admix_edge_style = {
        "stroke": 'rgb(90.6%,54.1%,76.5%)',
        "stroke-width": 5,
        "stroke-opacity": 0.6,
        "stroke-linecap": "round",
        "fill": "none",
        "font-size": "14px"
    }

    # create new group in the tree xml element for AdmixEdges
    admix_xml = xml.SubElement(
        mark_xml, 'g',
        attrib={'class': 'toytree-AdmixEdges'},
        style=concat_style_fix_color(default_admix_edge_style)
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
    for aedge in admixture_edges:

        # user arg has been expanded to: int, int, must be an AdmixtureEdge object or Tuple
        src, dst, src_dist, dst_dist, gamma, estyle, label = aedge

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