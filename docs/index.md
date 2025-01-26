---
section: Getting Started
icon: material/table-edit
---

# Welcome to toytree

Welcome to **toytree**, a Python library for tree visualization, manipulation,
and numerical and evolutionary analyses. If you are new to toytree, head to 
the [User Guide](/toytree/quick_guide/) to see examples and learn about its 
features.

## History
`toytree` is an object-oriented library built to meet the desire for a framework
that combines a Python-based tree object (similar to [ete3](http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html))
with a more modern and minimalist graphical design framework (e.g., like [toyplot](https://toyplot.rtfd.io)).
`toytree` has since expanded far beyond this simple goal, and now also provides
a suite of subpackages for additional features such as tree manipulation,
enumeration, comparison, and evolutionary analyses. In this respect, `toytree`
aims to fill a similar role for Python as the packages 'ape' and 'phytools'
do in the R language. 

## Usage
`toytree` is purposefully designed to promote interactive use within jupyter
notebooks where users can make use of modern Python and web development
features such as tab-completion and interactive plotting that make it easy
to learn and use. `toytree` can also serve as a powerful but
lightweight addition to other Python projects to provide efficient tree-based
and phylogenetic algorithms.


## Features
+ **style**: beautiful "out-of-the-box” tree drawings that require minimal styling.
- **customization**: drawings are highly customizable and export to PDF, SVG, or HTML.
- **extendable**: tree drawings are easily combined with scatterplots, barplots, etc.
- **io**: easily and flexibly parse tree data from newick, nexus, or extended NHX formats.
- **mod**: manipulate tree topology, rooting, and data using efficient algorithms.
- **distance**: calculate distances between trees (e.g., RF) or nodes on trees (e.g., paths).
- **enum**: enumerate tree partitions (e.g., quartets, bipartitions) or tree space.
- **multitree**: visualize or analyze sets of trees (e.g., cloud_trees, consensus).
- **rtree**: efficiently generate random trees for testing, demonstration, or research.
- **network**: parse and plot phylogenetic networks.
- **reproducibility**: simple and readable code.
- **minimalism**: few dependencies, easy installation, organized modular code base.
- **and more**: Have a feature request? Raise a ticket on [GitHub](http://github.com/eaton-lab/toytree).
