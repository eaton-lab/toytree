#!/usr/bin/env python

"""Add additional Marks to annotate toytree drawings.

Add annotations to drawings to show data or highlight sections
of a toytree drawing. This module is available as both a package-level
module as well as from ToyTree instances as an API.

Examples
--------
>>> tree = toytree.rtree.bdtree(10, seed=123)
>>> c, a, m = tree.draw(layout='d')
>>> toytree.annotate.add_node_pie_charts(axes=a, **kwargs)

>>> tree = toytree.rtree.bdtree(10, seed=123)
>>> c, a, m = tree.draw(layout='d', xbaseline=10)
>>> tree.annotate.node_pie_charts(axes=a, layout='d', xbaseline=10)

>>> # other idea, pass the tree Mark as an arg
>>> c, a, m = tree.draw(layout='d', xbaseline=10)
>>> toytree.annotate.node_pie_charts(mark=m)

Functions
---------
- add_node_markers()
- add_node_labels()
- add_node_pie_charts()

- add_edge_markers()
- add_edge_labels()
- add_edge_pie_charts()
- add_edge_root()

- add_scale_bar()
- add_confidence_intervals()

- add_tip_markers()
- add_tip_labels()
- add_tip_heatmap()

- add_image_markers(xpos, ypos, image[s], size, **style)

- radial_...
"""

# from toytree.annotate.src.node_pie_charts import draw_node_pie_charts
from toytree.annotate.src.add_edge_markers import *
from toytree.annotate.src.add_node_markers import *
from toytree.annotate.src.add_tip_markers import *
from toytree.annotate.src.add_axes_box_outline import *
from toytree.annotate.src.add_scale_bar import *
from toytree.annotate.src.add_pie_markers import *
from toytree.annotate.src.add_tip_labels import *

# ... edge_labels
# ... node_labels
# from .confidence_intervals import draw_node_confidence_intervals
