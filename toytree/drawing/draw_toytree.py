#!/usr/bin/env python

"""
Function to parse user args to toytree.draw() and return drawing.
See full args/docstring at toytree.core.Toytree.ToyTree.draw()
"""

from loguru import logger

from toytree.drawing.TreeStyle import TreeStyle
from toytree.drawing.StyleChecker import StyleChecker
from toytree.drawing.Render import ToytreeMark
from toytree.drawing.CanvasSetup import CanvasSetup


def draw_toytree(**kwargs):
    """
    Draw toytree with user entered kwargs.
    """
    # get the parent toytree object
    self = kwargs.pop('toytree')

    # get curstyle: use base style (ts or tree_style), or use default ts
    if kwargs['kwargs'].get("ts"):
        kwargs['tree_style'] = kwargs['kwargs'].pop("ts")
    if kwargs['tree_style']:
        base_style = TreeStyle(kwargs['tree_style'][0])
    else:
        base_style = self.style.copy()

    # warn user if they entered kwargs that arent't supported.
    if kwargs.get("kwargs"):
        logger.warning(
            f"Unrecognized arguments skipped: {list(kwargs['kwargs'])}."
            "\nCheck the docs, argument names may have changed.")
        kwargs.pop('kwargs')

    # drop None value'd args from user kwargs and update base_style
    user = dict(
        ("_" + i, j) if isinstance(j, dict) else (i, j)
        for (i, j) in kwargs.items() if j is not None
    )
    base_style.update(user)

    # update coords based on layout
    edges = self._coords.get_edges()
    if kwargs['layout'] == 'c':
        verts = self._coords.get_radial_coords(base_style.use_edge_lengths)
    else:
        verts = self._coords.get_linear_coords(
            base_style.layout, 
            base_style.use_edge_lengths,
            kwargs['fixed_order'],
            kwargs['fixed_position'],
        )

    # check all styles
    fstyle = StyleChecker(self, base_style).style

    # debugging returns the mark and prints the modified kwargs
    if kwargs.get('debug'):
        logger.debug(user)
        return fstyle

    # get canvas and axes
    csetup = CanvasSetup(self, kwargs['axes'], fstyle)
    canvas = csetup.canvas
    axes = csetup.axes

    # generate toyplot Mark
    mark = ToytreeMark(ntable=verts, etable=edges, **fstyle.to_dict())

    # add mark to axes
    axes.add_mark(mark)
    return canvas, axes, mark


# DEPREXATED OLD FUNC
# def draw_toytree2(
#     self,
#     tree_style:Optional[str]=None,
#     height:Optional[int]=None,
#     width:Optional[int]=None,
#     axes:Optional[toyplot.coordinates.Cartesian]=None,    
#     layout:Optional[str]=None,
#     tip_labels:Union[bool,Iterable]=None,
#     tip_labels_colors=None,
#     tip_labels_style=None,
#     tip_labels_align=None,
#     node_labels=None,
#     node_labels_style=None,
#     node_sizes=None,
#     node_colors=None,
#     node_style=None,
#     node_hover=None,
#     node_markers=None,
#     edge_colors=None,
#     edge_widths=None,
#     edge_type=None,
#     edge_style=None,
#     edge_align_style=None,
#     use_edge_lengths=None,
#     scalebar=None,
#     padding=None,
#     xbaseline=None,
#     ybaseline=None,
#     admixture_edges=None,
#     shrink=None,
#     fixed_order=None,
#     fixed_position=None,
#     **kwargs,
#     ) -> Tuple:
#     """
#     Draw toytree (see toytree.core.Toytree.draw) for full docstring.
#     """
#     # update kwargs to merge it with user-entered arguments:
#     userargs = {
#         "height": height,
#         "width": width,
#         "layout": layout,
#         "tip_labels": tip_labels,
#         "tip_labels_colors": tip_labels_colors,
#         "tip_labels_align": tip_labels_align,
#         "tip_labels_style": tip_labels_style,
#         "node_labels": node_labels,
#         "node_labels_style": node_labels_style,
#         "node_sizes": node_sizes,
#         "node_colors": node_colors,
#         "node_hover": node_hover,
#         "node_style": node_style,
#         "node_markers": node_markers,
#         "edge_type": edge_type,
#         "edge_colors": edge_colors,
#         "edge_widths": edge_widths,
#         "edge_style": edge_style,
#         "edge_align_style": edge_align_style,
#         "use_edge_lengths": use_edge_lengths,
#         "scalebar": scalebar,
#         "padding": padding,
#         "xbaseline": xbaseline, 
#         "ybaseline": ybaseline,
#         "admixture_edges": admixture_edges,
#         "shrink": shrink,
#         "fixed_order": fixed_order,
#         "fixed_position": fixed_position
#     }

#     # shortcut name for tree style
#     if kwargs.get("ts"):
#         tree_style = kwargs.get("ts")

#     # use a base style preset over which other options override
#     if tree_style:
#         curstyle = TreeStyle(tree_style[0])

#     # or use current tree settings (DEFAULT unless changed by user)
#     else:           
#         curstyle = self.style.copy()

#     # optionally override current style with style args entered to draw()
#     kwargs.update(userargs)
#     user = dict(
#         ("_" + i, j) if isinstance(j, dict) else (i, j)
#         for (i, j) in kwargs.items() if j is not None
#     )
#     curstyle.update(user)

#     # warn user if they entered kwargs that arent't supported.
#     allkeys = list(userargs.keys()) + ["debug", "ts"]
#     unrecognized = [i for i in kwargs if i not in allkeys]
#     if unrecognized:
#         logger.warning("Unrecognized arguments skipped: {}"
#             "\ncheck the docs, argument names may have changed."
#             .format(unrecognized))

#     # update coords based on layout
#     edges = self._coords.get_edges()
#     if layout == 'c':
#         verts = self._coords.get_radial_coords(curstyle.use_edge_lengths)
#     else:
#         verts = self._coords.get_linear_coords(
#             curstyle.layout, 
#             curstyle.use_edge_lengths,
#             fixed_order,
#             fixed_position,
#         )
#     logger.debug('verts\n{}'.format(verts))

#     # check all styles
#     fstyle = StyleChecker(self, curstyle).style

#     # debugging returns the mark and prints the modified kwargs
#     if kwargs.get('debug'):
#         logger.debug(user)
#         return fstyle

#     # get canvas and axes
#     csetup = CanvasSetup(self, axes, fstyle)
#     canvas = csetup.canvas
#     axes = csetup.axes

#     # generate toyplot Mark
#     mark = ToytreeMark(ntable=verts, etable=edges, **fstyle.to_dict())

#     # add mark to axes
#     axes.add_mark(mark)
#     return canvas, axes, mark
