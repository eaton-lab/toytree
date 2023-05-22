#!/usr/bin/env python

"""Custom toyplot.Mark for displaying pie charts.
"""

import numpy as np
import toyplot
from toyplot.mark import Mark


class PieChartMark(Mark):
    """Return a custom Mark as a scatterplot-like with Pie markers.

    To create PieChart instances a user should use the standard
    :meth:`draw` function of ToyTree instances entering an ndarray
    with (ncategories, nnodes) dimension; or, enter the same data
    as an argument to the :meth:tree.annotate.pie_charts() function.

    Parameters
    ----------
    ntable: numpy.ndarray
        Coordinates of markers
    data: numpy.ndarray
        Percentages.
    annotation: bool
        Mark is an 'annotation' not affecting data domain.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=10, seed=123)
    >>> pie_data = np.repeat([1/3, 1/3, 1/3], tree.nnodes)
    >>> c, a, m = tree.draw(node_colors=pie_data)

    >>> tree = toytree.rtree.unittree(ntips=10, seed=123)
    >>> c, a, m = tree.draw(node_colors=pie_data)
    >>> tree.annotate.pie_charts(axes, mark, ...)
    """
    def __init__(
        self,
        coordinates,
        data,
        sizes,
        colors,
        istroke,
        istroke_width,
        ostroke,
        ostroke_width,
        rotate,
        xshift,
        yshift,
    ):
        Mark.__init__(self, annotation=True)
        self._coordinate_axes = ['x', 'y']
        self.coordinates = np.array(coordinates)
        self.data = data
        self.sizes = toyplot.broadcast.scalar(sizes, self.coordinates.shape[0])
        self.ostroke = ostroke
        self.ostroke_width = ostroke_width
        self.istroke = istroke
        self.istroke_width = istroke_width
        self.rotate = rotate
        self.colors = colors
        self.xshift = xshift
        self.yshift = yshift

        # radius is half the size
        self.sizes /= 2.

    def domain(self, axis):
        """The domain of data to fit on Canvas."""
        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self.coordinates[:, index])
        return domain

    def extents(self, axes):
        """..."""
        node_extents = [self.sizes / 2. for i in range(4)]
        node_extents[0] *= -1
        node_extents[2] *= -1
        node_extents[0] += self.xshift
        node_extents[1] += self.xshift
        node_extents[2] += self.yshift
        node_extents[3] += self.yshift
        coords = (
            self.coordinates[:, 0].copy(),
            self.coordinates[:, 1],
        )
        return coords, node_extents


if __name__ == "__main__":

    pass
    # import toyplot
    # c = toyplot.Canvas()
    # a = c.cartesian()
    # mark = PieChartMark()
