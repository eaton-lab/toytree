#!/usr/bin/env python

"""toytree I/O data parsing utilities.

The generic functions are easiest to use, but a bit slower than if 
the funtions for parsing directly from a string or file.

tree parsing generics
---------------------
- toytree.io.treeio.tree
	parse a ToyTree in many possible formats from str, file, or URL.
- toytree.io.treeio.mtree
	parse a MultiTree in many possible formats from str, file, or URL.

newick string parsing 
---------------------
- toytree.io.parse_newick
	parse a single ToyTree from a newick or NHX+ string.
- toytree.io.parse_newick_custom
	parse a single ToyTree from a newick or NHX+ string with 
	additional options to parse custom/odd additional data.

file parsing
------------
- toytree.io.read_tree_from_newick_file
- toytree.io.read_tree_from_nexus_file
- toytree.io.read_tree_from_mb_file
x- toytree.io.read_tree_from_beast3_file
x- toytree.io.read_tree_from_bpp_file
x- toytree.io.read_tree_from_superbpp_file

tree writing
------------
- toytree.io.write_newick
- toytree.io.write_nexus

data parsing
------------
- toytree.io.read_data_from_nexus_file
- toytree.io.read_data_from_csv_file
- ...
"""

from .src.newick import parse_newick_string, parse_newick_string_custom
from .src.treeio import tree
from .src.writer import write_newick, write_nexus
from .src.helpers import (
	read_newick, 
	read_nexus, 
	read_mb_file,
)
