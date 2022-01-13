#!/usr/bin/env python

"""Annotation functions for adding to toytree drawings.
"""


class Annotator(object):
    """
    Add annotations as a new mark on top of an existing toytree mark.
    """
    def __init__(self, tree, axes, mark):
        self.tree = tree
        self.axes = axes
        self.mark = mark

    def draw_clade_box(
        self, 
        names=None, 
        regex=None, 
        wildcard=None, 
        yspace=None, 
        xspace=None, 
        **kwargs):
        """
        Draw a rectangle around a clade on a toytree.

        Parameters:
        -----------
        names, regex, wildcard:
            Choose one of these three methods to select one or more tipnames. 
            The clade composing all descendants of their common ancestor will 
            be highlighted.

        yspace (float or None):
            The extent to which boxes extend above and below the root and tip
            nodes. If None then this is automatically generated.

        xspace (float or None):
            The extent to which the clade box extends to the sides 
            (out of the clade towards other tips.) If None default uses 0.5.

        kwargs:
            Additional styling options are supported: color, opacity, etc.

        Returns:
        ------------
        Toyplot.mark.Range
        """

        # get the common ancestor
        nidx = self.tree.get_mrca_idx_from_tip_labels(
            names=names, regex=regex, wildcard=wildcard)

        # get tips descended from mrca
        tips = self.tree[nidx].get_leaves()
        tidxs = [i.idx for i in tips]

        # extent to which box bounds extend outside of the exact clade size.
        if not yspace:
            yspace = self.tree.treenode.height / 15.
        if not xspace:
            xspace = 0.45

        # left and right positions
        if self.mark.layout == 'r':
            xmin = self.mark.ntable[nidx, 0] - yspace
            xmax = max(self.mark.ntable[tidxs, 0]) + yspace
            ymin = min(self.mark.ntable[tidxs, 1]) - xspace
            ymax = max(self.mark.ntable[tidxs, 1]) + xspace   

        if self.mark.layout == 'l':
            xmin = self.mark.ntable[nidx, 0] + yspace
            xmax = max(self.mark.ntable[tidxs, 0]) - yspace
            ymin = max(self.mark.ntable[tidxs, 1]) + xspace
            ymax = min(self.mark.ntable[tidxs, 1]) - xspace   

        elif self.mark.layout == 'd':
            ymax = self.mark.ntable[nidx, 1] + yspace
            ymin = min(self.mark.ntable[tidxs, 1]) - yspace
            xmin = min(self.mark.ntable[tidxs, 0]) - xspace
            xmax = max(self.mark.ntable[tidxs, 0]) + xspace               

        elif self.mark.layout == 'u':
            ymin = self.mark.ntable[nidx, 1] - yspace
            ymax = min(self.mark.ntable[tidxs, 1]) + yspace
            xmin = min(self.mark.ntable[tidxs, 0]) - xspace
            xmax = max(self.mark.ntable[tidxs, 0]) + xspace               

        # draw the rectangle
        newmark = self.axes.rectangle(xmin, xmax, ymin, ymax, **kwargs)

        # put tree at the top of the scenegraph
        self.axes._scenegraph.remove_edge(self.axes, 'render', self.mark)
        self.axes._scenegraph.add_edge(self.axes, 'render', self.mark)

        return newmark



    # def draw_tip_box(
    #     self, 
    #     names=None, 
    #     regex=None, 
    #     wildcard=None, 
    #     yspace=None, 
    #     xspace=None, 
    #     **kwargs):
    #     """
    #     Draw a rectangle around the tips of a clade on a toytree.

    #     Parameters:
    #     -----------
    #     names, regex, wildcard:
    #         Choose one of these three methods to select one or more tipnames. 
    #         The clade composing all descendants of their common ancestor will 
    #         be highlighted.

    #     yspace (float or None):
    #         The extent to which boxes extend above and below the root and tip
    #         nodes. If None then this is automatically generated.

    #     xspace (float or None):
    #         The extent to which the clade box extends to the sides 
    #         (out of the clade towards other tips.) If None default uses 0.5.

    #     kwargs:
    #         Additional styling options are supported: color, opacity, etc.

    #     Returns:
    #     ------------
    #     Toyplot.mark.Range
    #     """

    #     # get the common ancestor
    #     nidx = self.tree.get_mrca_idx_from_tip_labels(
    #         names=names, regex=regex, wildcard=wildcard)

    #     # get tips descended from mrca
    #     tips = self.tree[nidx].get_leaves()
    #     tidxs = [i.idx for i in tips]

    #     # get nudge size from dists in the tree or user supplied
    #     if not yspace:
    #         yspace = self.tree.get_node_values("dist", 1, 1).mean() / 4.
    #     if not xspace:
    #         xspace = 0.5

    #     # distance in PIXELS to the tip labels
    #     tipx = toyplot.units.convert(
    #         mark.tip_labels_style["-toyplot-anchor-shift"], 'px')

    #     # left and right positions
    #     if self.mark.layout == 'r':           

    #         # get unit conversion
    #         tipstart = tipx / (axes.project('x', 1) - axes.project('x', 0))
    #         xmin = self.mark.ntable[nidx, 0] - yspace
    #         xmax = max(self.mark.ntable[tidxs, 0]) + yspace
    #         ymin = min(self.mark.ntable[tidxs, 1]) - xspace
    #         ymax = max(self.mark.ntable[tidxs, 1]) + xspace   

    #     if self.mark.layout == 'l':
    #         xmin = self.mark.ntable[nidx, 0] + yspace
    #         xmax = max(self.mark.ntable[tidxs, 0]) - yspace
    #         ymin = max(self.mark.ntable[tidxs, 1]) + xspace
    #         ymax = min(self.mark.ntable[tidxs, 1]) - xspace   

    #     elif self.mark.layout == 'd':
    #         ymax = self.mark.ntable[nidx, 1] + yspace
    #         ymin = min(self.mark.ntable[tidxs, 1]) - yspace
    #         xmin = min(self.mark.ntable[tidxs, 0]) - xspace
    #         xmax = max(self.mark.ntable[tidxs, 0]) + xspace               

    #     elif self.mark.layout == 'u':
    #         ymin = self.mark.ntable[nidx, 1] - yspace
    #         ymax = min(self.mark.ntable[tidxs, 1]) + yspace
    #         xmin = min(self.mark.ntable[tidxs, 0]) - xspace
    #         xmax = max(self.mark.ntable[tidxs, 0]) + xspace               

    #     # draw the rectangle
    #     mark = self.axes.rectangle(xmin, xmax, ymin, ymax, **kwargs)
    #     return mark



    # def generate_rectangle(self, firstname=None, lastname=None, axes=None, color="green", opacity=.25):
    #     """
    #     Returns an updated axes with a generated rectangle based on input labels provided
    #     """
    #     index_of_first = self.get_mrca_idx_from_tip_labels(names=firstname)
    #     index_of_last =  self.get_mrca_idx_from_tip_labels(names=lastname)
    #     x_vals = (x[0] for x in self.get_node_coordinates())

    #     axes.rectangle(
    #         min(self.get_tip_coordinates()[index_of_first][0],  self.get_tip_coordinates()[index_of_last][0]),
    #         max(x_vals),
    #         self.get_tip_coordinates()[index_of_first][1],
    #         self.get_tip_coordinates()[index_of_last][1],
    #         opacity=opacity,
    #         color=color,
    #     )
    #     return axes

