Toytree
==========

.. image:: https://badges.gitter.im/toytree-help/Lobby.svg
   :alt: Join the chat at https://gitter.im/toytree-help/Lobby
   :target: https://gitter.im/toytree-help/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge  

.. image:: https://anaconda.org/eaton-lab/toytree/badges/installer/conda.svg
   :alt: Install with conda
   :target: https://conda.anaconda.org/eaton-lab  

.. image:: https://travis-ci.org/eaton-lab/toytree.svg?branch=master
    :target: https://travis-ci.org/eaton-lab/toytree
       

Tree plotting with **Toytree**
------------------------------

**Toytree** is a Python tree plotting library designed for use inside 
`jupyter notebooks <http://jupyter.org>`_. It was motivated from a 
desire for a simple tree plotting library with a similar aesthetic to 
the *ape* package for *R*. To parse, represent, and manipulate 
tree objects **Toytree** uses a modified (minimal) version of the 
`ete3 <http://etetoolkit.org>`_ library (which we call `ete3mini`). 
**Toytree** is written within the framework of the minimalist plotting 
library `toyplot <http://toyplot.readthedocs.io/en/stable/index.html>`_, 
which generates rich interactive figures (SVG+HTML+JS) that can be embedded in 
Jupyter-notebooks or webpages, or rendered in SVG or PDF format for publications. 


Installation
--------------
You can install ``toytree`` and its dependencies (``toyplot`` and ``numpy``) with a single command using conda. 

.. code:: bash

    conda install toytree -c eaton-lab


Documentation
--------
See the `full documentation <http://toytree.readthedocs.io>`_. Launch a jupyter-notebook on your machine to try it out for yourself. 


Examples
------- 

.. , or, *click on the "binder" badge below* to launch a jupyter notebook in the cloud where you can try it without having to install anything (the web notebook might take a minute or two to spin up -- it's a bit buggy and may not work at the moment).

.. image: http://mybinder.org/badge.svg 
..     :target: http://mybinder.org:/repo/eaton-lab/toytree


.. code:: python
    
    ## import the toyplot and toytree modules
    import toytree
    import toyplot


.. code:: python

    ## load trees from newick str, filepath, or URL
    url = "http://eaton-lab.org/data/Vib-Oreino.tre"
    path = "./tree.newick"
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
    tre1 = toytree.tree(url)
    tre2 = toytree.tree(path)
    tre3 = toytree.tree(newick)
    


Tree plotting basics
~~~~~~~~~~~~~~~~~~~~~
The ``.draw()`` function generates a plot that is returned as a tuple 
containing a ``toyplot.Canvas`` object and a ``toyplot.Canvas.cartesian``
object. In a jupyter-notebook the ``canvas`` will automatically render 
as HTML in an output cell. Toytree applies a default styling to the tree
which can be modified extensively.  

.. code:: python

    canvas, axes = tre3.draw(width=400, node_labels=True)
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

    tre3.draw(
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
