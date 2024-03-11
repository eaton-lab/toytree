#!/usr/bin/env python

"""The utils submodule contains a collection of utility tools.

The functions and classes in `utils` have not yet been developed into
a full submodule in `toytree`, but may be moved eventually. Current
utilities exist for the following topics:

Methods
-------
toytree_sequence(Union[tree_sequence, str])
    Return a ToyTreeSequence object for extracting and drawing trees
    from a tree sequence object produced by msprime or SliM3.
parse_network(str)
    Return a ToyTree and admixture dictionary representing the major
    topology (highest gamma branches) and admixture edges (src, dest
    tuples representing lower gamma branches) from a network file
    produced by SNaQ.
normalize_values(np.ndarray)
    Return an array of values that have been binned into fewer
    discrete integer values. This is useful for plotting edge widths
    (e.g., values look nice in range 2-10) from data in some other
    range (e.g., Ne values in range 1e5 to 1e7).


Notes
------
Organization of code in the utils submodule.

utils/src/
    A folder with the utils source code organized into subsubmodules. 
    The functions intended for use by users are accessible from the 
    top level `toytree.utils`. 
utils/src/tree_sequences/
    The ToyTreeSequence class for working with and visualizing 
    tree_sequence class objects produced by msprime or SLiM, including
    subsampling, simplifying, and showing mutations on edges.
utils/src/exceptions/
    Raising and catching exceptions. Users can access the main
    exception class from the top level module: `toytree.ToyTreeError`
    and so do not need to access it here.
utils/src/networks/
    Network parsing functions. Currently `parse_network` is the only
    function, and is accessible at `toytree.utils.parse_network`.
utils/src/logging/
    The logger setup. Users can set the log level from the top level
    module with `toytree.set_log_level`, or turn it on/off with 
    `from loguru import logger; logger.disable('toytree')`.
utils/src/constants/
    A file with some constants that users should not need to access.
"""

from toytree.utils.src.exceptions import *
from toytree.utils.src.scrollable_canvas import ScrollableCanvas
from toytree.utils.src.browser import show
from toytree.utils.src.toytree_sequence import ToyTreeSequence as toytree_sequence
from toytree.utils.src.style_axes import (
    set_axes_ticks_external,
    set_axes_box_outline,
)
