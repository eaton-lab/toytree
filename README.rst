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
Welcome to toytree, a minimalist tree manipulation and plotting library for use inside jupyter notebooks. Toytree combines a popular tree data structure based on the `ete3 <http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html>`__) library with modern plotting tools based on the `toyplot <http://toyplot.rtfd.io/>`__) plotting library. The goal of toytree is to provide a light-weight Python equivalent to commonly used tree manipulation and plotting libraries in R, and in doing so, to promote further development of phylogenetic methods in Python. Toytree generates rich interactive figures (SVG+HTML+JS) that can be embedded in jupyter-notebooks or webpages, or rendered in SVG, PDF, or PNG for publications. 


Installation
--------------
You can install ``toytree`` and its dependencies (``toyplot`` and ``numpy``) with a single command using conda (preferred), or from pip. 

.. code:: bash

    conda install toytree -c eaton-lab


Documentation
--------
See the `full documentation <http://toytree.readthedocs.io>`_ to see all of the options that toytree provides. Try it out instantly in the cloud using the `toytree binder <http://mybinder.org/repo/eaton-lab/toytree>`__.


Examples
------- 

.. code:: python
    
    # import toyplot and load a newick file from a public URL
    import toytree
    tre = toytree.tree("https://eaton-lab.org/data/Cyathophora.tre")

    # root the tree using a wildcard string matching and draw a tree figure.
    rtre = tre.root(wildcard='prz')
    rtre.draw(width=400, tip_labels_align=True);

    # or chain a few functions together
    tre.root(wildcard='prz').drop_tips(wildcard="tham").ladderize().draw();

    # extensive styling options are available
    rtre.draw(
        tip_labels_color='pink',
        node_labels='support',
        node_size=15,
        node_color="cyan",
        edge_style={
            "stroke": "darkgrey", 
            "stroke-width": 3,
        },
    )