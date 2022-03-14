#!/usr/bin/env python

"""Generic multitree parsing function.

"""

from typing import Union, Collection
from pathlib import Path
from toytree.core.tree import ToyTree
from toytree.core.multitree import MultiTree
from toytree.io.src.parser import TreeIOParser
from toytree.utils import ToytreeError


def mtree(
    data:Union[str, Path, Collection[Union[ToyTree, str, Path]]],
    **kwargs) -> MultiTree:
    """General class constructor to parse and return a MultiTree.

    Input arguments as a multi-newick string, filepath, Url, or 
    Collection of Toytree objects.
    
    Parameters
    ----------
    data: str, Path, or Collection
        string, filepath, or URL for a newick or nexus formatted list
        of trees, or a collection of ToyTree objects.

    Examples
    --------
    >>> mtre = toytree.mtree("many_trees.nwk")
    >>> mtre = toytree.mtree("((a,b),c);\n((c,a),b);")
    >>> mtre = toytree.mtree([toytree.rtree.rtree(10) for i in range(5)])
    """
    # parse the newick object into a list of Toytrees
    treelist = []
    # e.g., path to a newick file with multi-line str of trees.
    if isinstance(data, Path):
        data = str(Path)
    # e.g., a multi-line str of trees.
    if isinstance(data, str):
        treelist = TreeIOParser(data, multitree=True, **kwargs).trees
    # e.g., a list of ToyTree objects
    elif isinstance(data[0], ToyTree):
        treelist = [i.copy() for i in data]
    # e.g., a list of newick strings or file paths
    elif isinstance(data[0], (str, Path)):
        treelist = TreeIOParser(data, multitree=True).trees
    else:
        raise ToytreeError("mtree input format unrecognized.")
    return MultiTree(treelist)


if __name__ == "__main__":

    import numpy as np
    import ipcoal

    # set variables
    Ne = 10000
    nsamples = 8
    mut = 1e-7
    nloci = 100

    # simulate sequence data
    model = ipcoal.Model(tree="", Ne=Ne, nsamples=nsamples, mut=mut)
    model.sim_loci(nloci=nloci, nsites=20)
    model.seqs = np.concatenate(model.seqs, 1)    

    # show some of the genealogies that were produced
    c, a, m = model.draw_genealogies(height=200, shared_axes=True);

    import toyplot.browser
    toyplot.browser.show(c)

