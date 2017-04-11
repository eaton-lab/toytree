
Installation
--------------

You can install ``toytree`` and its dependencies (``toyplot`` and ``numpy``) with a single command using conda. 


.. code:: bash

    conda install toytree -c eaton-lab


Tutorial
--------

See the `tutorial notebook <http://nbviewer.jupyter.org/github/eaton-lab/toytree/blob/master/docs/tutorial.ipynb>`_ for a detailed walk-through of available plotting options in ``Toytree``. Lauch a jupyter-notebook on your machine to try it out for yourself, or, *click on the "binder" badge below* to launch a jupyter notebook in the cloud where you can try it without having to install anything (the web notebook might take a minute or two to spin up).

.. image:: http://mybinder.org/badge.svg 
    :target: http://mybinder.org:/repo/eaton-lab/toytree


Tree plotting with ``Toytree``
------------------------------

``Toytree`` is a Python tree plotting library designed for use inside 
`jupyter notebooks <http://jupyter.org>`_. It was motivated from of a 
desire for a simple tree plotting library with a design similar to the ``'ape'`` package for ``R``. To parse, represent, and manipulate tree objects ``toytree`` uses a stripped-down version of the 
`ete3 <http://etetoolkit.org>`_ library (which we call `ete3mini`), and to generate plots ``toytree`` uses the 'graph' functionality from the minimalist plotting library `toyplot <http://toyplot.readthedocs.io/en/stable/index.html>`_. Some example usage is demonstrated below.

.. code:: python

    import toytree

    ## store a newick string representation of a tree
    newick = \
    """(41954_cyathophylloides:0.00008888031167776559,(((32082_przewalskii:
    0.00259326350604092027,33588_przewalskii:0.00247133969857381459)100:
    0.03587422609749137820,(33413_thamno:0.00565358258838428562,(30556_thamno:
    0.00653218253974622003,((40578_rex:0.00335406134690998791,35855_rex:
    0.00339963302433546593)100:0.00222999650239191338,(35236_rex:0.00580524693403740473,
    (39618_rex:0.00096208118162745867,38362_rex:0.00109218434613194098)100:
    0.00617527349892385037)96:0.00073890038051916795)99:0.00078336549990502716)100:
    0.00103379657491441167)100:0.00538723112354794632)100:0.00297626149201316807,
    (29154_superba:0.00634236826447889986,30686_cyathophylla:0.00669944988923529706)
    100:0.00237994755604001816)100:0.00941020878048287081,41478_cyathophylloides:
    0.00005282184335845886);"""

    ## load newick string to create a Toytree class object
    tre = toytree.tree(newick)


Tree plotting basics
~~~~~~~~~~~~~~~~~~~~~
The ``.draw()`` function generates a plot which is returned as two objects, 
a ``toyplot.Canvas`` object and a ``toyplot.Canvas.cartesian`` object. 
In a jupyter-notebook the ``canvas`` will automatically render as a figure
in a cell of the notebook. Toytree applies a default styling to the tree
which can be modified.  

.. code:: python

    canvas, axes = tre.draw(width=400, node_labels=True)
    canvas


.. image:: https://cdn.rawgit.com/eaton-lab/toytree/master/docs/readme_fig1.svg
   :align: center


Styling options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
By default toytree generates figures in HTML following the design 
ethos of toyplot, which is designed to create figures for the web
(though figures can also be saved in common formats like SVG). 
It uses CSS styling options to modify plot components that will be 
familiar to users with web-design experience. For advanced usage
I recommend becoming more familiar with the Toyplot documentation. 
The figure below demonstrates several styling options that can 
be applied to a tree plot. 


.. code:: python

    tre.draw(
        width=500, 
        height=500,
        node_labels=True,
        node_labels_style={
            "font-size": "10px", 
            "fill": "white"
            },
        node_size=16,
        node_style={
            "stroke": "green", 
            "stroke-width": 2, 
            "fill": "#333333", 
            "opacity": 0.5,
            },  
        tip_labels=True,
        tip_labels_style={
            "font-size": "14px", 
            "-toyplot-anchor-shift": "18px", 
            "fill": "darkcyan",
            },
        edge_style={
            "stroke": "orange", 
            "stroke-opacity": 0.8, 
            "stroke-dasharray": "3,3",
            "stroke-width": 3,
            },
        use_edge_lengths=False,
        tree_style="c",
        orient="down",
        );


.. image:: https://cdn.rawgit.com/eaton-lab/toytree/master/docs/readme_fig2.svg
   :align: center


Combine with standard ``Toyplot`` figures
--------------------------------------------
The ``toyplot.Canvas`` and ``toyplot.axes.cartesian`` objects that 
are returned by toytree can be further modified to combine multiple 
plots onto a single or multiple axes, or to save the the canvas in 
a number of formats. Trees can be easily combined with other types
of data to add barplots or scatterplots to the axes. Here we 
generate three plots, apply different styling to each, and save 
the final canvas as HTML and SVG. The first axes object is set to 
display its axis coordinates to show how data points are aligned.


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

