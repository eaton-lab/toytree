#!/usr/bin/env python

"""
toytree drawing annotation module.

Add annotations to drawings to show data or highlight sections
of a toytree drawing. This module is available as both a 

Examples
--------
>>> tree = toytree.rtree.bdtree(10, seed=123)
>>> c, a, m = tree.draw(layout='d')
>>> toytree.annotate.draw_pie_charts(axes=a, **kwargs)

>>> tree = toytree.rtree.bdtree(10, seed=123)
>>> c, a, m = tree.draw(layout='d', xbaseline=10)
>>> tree.annotate.draw_pie_charts(axes=a, layout='d', xbaseline=10)

"""

from .node_pie_charts import draw_node_pie_charts
# from .confidence_intervals import draw_node_confidence_intervals