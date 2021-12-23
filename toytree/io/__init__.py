#!/usr/bin/env python

"""toytree I/O data parsing utilities.

tree parsing generics
---------------------
- toytree.io.treeio.tree
	Tree FILE parsing function for newick, nexus, NHX.
- toytree.io.parse_newick
	Tree STRING parsing function for newick strings, including NHX+.
- toytree.io.parse_newick_custom
	Tree STRING parsing function with customizable parsing functions.

tree parsing specifics
----------------------
- toytree.io.parse_tree_from_newick_file
- toytree.io.parse_tree_from_nexus_file
x- toytree.io.parse_tree_from_mb_file
x- toytree.io.parse_tree_from_beast3_file
x- toytree.io.parse_tree_from_bpp_file
x- toytree.io.parse_tree_from_superbpp_file

tree writing
------------
- ...

data parsing
------------
- toytree.io.parse_data_from_nexus_file
- toytree.io.parse_data_from_csv_file
- ...
"""

from .src.newick import parse_newick_string, parse_newick_string_custom
from .src.treeio import tree
from .src.writer import write_newick, write_nexus
