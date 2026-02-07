Toytree
==========

Tree plotting with **Toytree** in Python
----------------------------------------
Welcome to toytree, a Python library for tree object data parsing, visualization,
manipulation, and numerical and evolutionary analyses. If you are new to toytree, head to 
the [User Guide](https://eaton-lab.org/toytree/quick_guide/) to see examples and learn
about its features.

The goal of toytree is to provide a light-weight Python equivalent to widely used tree analysis
and plotting libraries in R, and in doing so, to promote further development of phylogenetic and
evolutionary methods in Python.

Toytree generates rich interactive figures (SVG+HTML+JS) that render in jupyter-notebooks
or webpages, and can be exported as high quality SVG, PDF, or PNG figures for publications.
It has minimal dependencies, is easy to install, and can be easily incorporated
into other projects.

In addition to visualization, toytree includes several modules supporting a suite
of methods to: generate trees (`rtree`); modify trees (`mod`); enumerate
over trees or treespace (`enum`); perform phylogenetic comparative methods (`pcm`);
infer phylogenetic trees using (`infer`); and more.


Current release info
--------------------
| Name | Downloads | Version | Platforms |
| --- | --- | --- | --- |
| [![Conda Recipe](https://img.shields.io/badge/recipe-toytree-green.svg)](https://anaconda.org/conda-forge/toytree) | [![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/toytree.svg)](https://anaconda.org/conda-forge/toytree) | [![Conda Version](https://img.shields.io/conda/vn/conda-forge/toytree.svg)](https://anaconda.org/conda-forge/toytree) | [![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/toytree.svg)](https://anaconda.org/conda-forge/toytree) |

Installing toytree
-------------------
Toytree can be installed using conda or pip (conda preferred):
```
conda install toytree -c conda-forge
```
It is possible to list all of the versions of `toytree` available on your platform with:
```
conda search toytree --channel conda-forge
```

Documentation
-------------
See the full documentation at [http://eaton-lab.org/toytree](http://eaton-lab.org/toytree).


Example code blocks
-------------------

```python
import toytree

# parse newick data from a string, file, or public URL
tre = toytree.tree("https://eaton-lab.org/data/Cyathophora.tre")

# root a tree by selecting an outgroup by name, or regular expression
rtre = tre.root('~prz')

# generate a simple tree drawing
rtre.draw(width=400, tip_labels_align=True);

# or, chain a few functions together to root, modify, and draw a tree
tre.root('~prz').drop_tips("~tham").ladderize().draw();

# or, apply more styling options to tree drawings
rtre.draw(
    tip_labels_colors='pink',
    node_labels='support',
    node_sizes=15,
    node_colors="cyan",
    edge_style={
        "stroke": "darkgrey", 
        "stroke-width": 3,
    },
)
```

```python

```

Example visualizations
----------------------

![./manuscript/ToyTree-figure.svg](./manuscripts/toytree-1.0/ToyTree-figure.svg)


Reference
----------
 Eaton DAR. Toytree: A minimalist tree visualization and manipulation library for Python. Methods Ecol Evol. 2020; 11: 187–191. https://doi.org/10.1111/2041-210X.13313