#!/usr/bin/env python

"""Add additional Marks to annotate toytree drawings.

Add annotations to drawings to show data or highlight sections
of a toytree drawing. This module is available as both a package-level
module as well as from ToyTree instances as an API.

Examples
--------
>>> tree = toytree.rtree.bdtree(10, seed=123)
>>> c, a, m = tree.draw(layout='d')
>>> toytree.annotate.node_pie_charts(axes=a, **kwargs)

>>> tree = toytree.rtree.bdtree(10, seed=123)
>>> c, a, m = tree.draw(layout='d', xbaseline=10)
>>> tree.annotate.node_pie_charts(axes=a, layout='d', xbaseline=10)

>>> # other idea, pass the tree Mark as an arg
>>> c, a, m = tree.draw(layout='d', xbaseline=10)
>>> toytree.annotate.node_pie_charts(mark=m)

"""

from .node_pie_charts import draw_node_pie_charts
# ... edge_labels
# ... node_labels
# from .confidence_intervals import draw_node_confidence_intervals
