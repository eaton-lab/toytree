


Tree plotting with ``Toytree``
-------------------------------
See the `tutorial notebook <http://nbviewer.jupyter.org/github/eaton-lab/toytree/blob/master/docs/tutorial.ipynb>`_ for more details. 
``Toytree`` is a Python tree plotting library designed for use inside 
`jupyter notebooks <http://jupyter.org>`_. It was motivated out of a 
desire for a simple and minimalist tree plotting library with similar
affinities to the `ape` package for ``R``. On the backend ``toytree`` 
uses the rich tree manipulation package
`ete3 <http://etetoolkit.org and the rich plotting library>`_ 
and the modern and minimalist plotting library 
`toyplot <http://toyplot.readthedocs.io/en/stable/index.html>`_. 


.. code:: python

    import toytree


.. code:: python

    newick = \
    """((33588_przewalskii:100,32082_przewalskii:100)100:100,(33413_thamno:100,
    ((35236_rex:100,30556_thamno:100)82:82,((35855_rex:100,40578_rex:100)100:100,
    (38362_rex:100,39618_rex:100)100:100)73:73)91:91)100:100,
    ((30686_cyathophylla:100,29154_superba:100)100:100,
    (41954_cyathophylloides:100,41478_cyathophylloides:100)100:100)100:100);"""



The ``toytree`` Class object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The help documentation for toytree objects can be accessed with ``?`` or ``<tab>-completion``. Toytree brings together the rich tree manipulation library 

.. code:: python

    tre = toytree.tree(newick)
    tre


.. parsed-literal::

    <toytree.Toytree.Tree at 0x7f8d0c0f1bd0>



Tree plotting basics
~~~~~~~~~~~~~~~~~~~~~
The ``.draw()`` function generates a plot and returns a toyplot Canvas and axes
object. 

.. code:: python

    tre.draw(width=400, node_labels=True)


.. image:: https://cdn.rawgit.com/eaton-lab/toytree/master/docs/readme_fig1.svg
   :align: center


Styling options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
toytree utilizes toyplot to generate tree figures, a modern Python plotting 
library that is designed for the web. The default format used by toyplot
is HTML (though you can save figures in additional formats like SVG), 
and it uses familiar CSS styling options to modify plot components. 
The figure below demonstrates how many styling options can be applied
to a tree plot. 


.. code:: python

    tre.draw(
        width=500, 
        height=500,
        node_labels=True,
        node_labels_style={"font-size": "10px", 
                           "fill": "white"},
        node_size=16,
        node_style={"stroke": "green", 
                    "stroke-width": 2, 
                    "fill": "#333333", 
                    "opacity": 0.5},  
        tip_labels=True,
        tip_labels_style={"font-size": "14px", 
                          "-toyplot-anchor-shift": "18px", 
                          "fill": "darkcyan"},
        edge_style={"stroke": "orange", 
                    "stroke-opacity": 0.8, 
                    "stroke-dasharray": "3,3",
                    "stroke-width": 3},
        use_edge_lengths=False,
        tree_style="c",
        orient="down",
        );


.. image:: https://cdn.rawgit.com/eaton-lab/toytree/master/docs/readme_fig2.svg
   :align: center


Combine with standard ``Toyplot`` figures
--------------------------------------------
The ``toyplot.Canvas`` and ``toyplot.axes.cartesian`` objects are returned
by toytree which enables further modification of the canvas and axes, 
to combine multiple plots onto a single or multiple axes, and to save the
the canvas in a number of formats. 


.. code:: python

    import toyplot
    import numpy as np

    ## create a canvas with three subplots
    canvas = toyplot.Canvas(width=900, height=400)
    axes1 = canvas.cartesian(grid=(1, 3, 0))
    axes2 = canvas.cartesian(grid=(1, 3, 1))
    axes3 = canvas.cartesian(grid=(1, 3, 2))

    ## draw a tree into each space by designating the axes
    _, axes1 = tre.draw(axes=axes1, orient='right')
    _, axes2 = tre.draw(axes=axes2, orient='down', 
                        tip_labels_style={"-toyplot-anchor-shift": "95px"})
    _, axes3 = tre.draw(axes=axes3, 
                        tip_labels_style={"-toyplot-anchor-shift": "25px"})

    ## add more styling to axes
    axes1.show = True
    axes2.show = False
    axes3.show = False

    ## add additional plots to axes (axes.show shows coordinates)
    heights = np.random.randint(-5, 0, 13)
    axes2.bars(heights, 
               baseline=[-0.5]*13,
               style={"stroke": "#262626"},
               );

    heights = np.random.randint(5, 15, 13)
    axes3.scatterplot(a=[1]*heights.shape[0], 
                      b=range(heights.shape[0]),
                      size=heights,
                      mstyle={"stroke": "#262626"}
                      );

    ## save figure as HTML & SVG
    import toyplot.html
    import toyplot.svg
    toyplot.html.render(canvas, "figure.html")
    toyplot.svg.render(canvas, "figure.svg")


.. image:: https://cdn.rawgit.com/eaton-lab/toytree/master/docs/readme_fig3.svg
   :align: center
