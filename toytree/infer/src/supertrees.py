#!/usr/bin/env python

"""Implementatin of supertree inference methods.


References
----------
https://pubmed.ncbi.nlm.nih.gov/39119174/
"""

import numpy as np
from toytree.core import ToyTree
from toytree.core.multitree import MultiTree


def get_matrix_representation(trees: ToyTree, tiplabels: list[str]) -> np.ndarray:
    """Return a matrix representation of a set of rooted trees.

    This matrix can be analyzed using a phylogenetic inference tool
    to infer a tree. A common approach is to infer a parsimony tree in
    which case the supertree is termed a matrix representation with
    parsimony (MRP) tree.
    """
    # get array filled w/ 1 for tips in each clade
    data = []
    for bipart in tree.enum.iter_bipartitions():
        dat = np.zeros(len(tiplabels), dtype=int)
        for i in bipart[0]:
            dat[tiplabels.index(i)] = 1
        data.append(dat)

    # get mask of missing taxa in this tree
    mask = np.zeros(len(tiplabels), dtype=np.bool_)
    for i in set(tiplabels) - set(tree.get_tip_labels()):
        mask[tiplabels.index(i)] = True

    # create a masked array to
    marr = np.ma.array(
        data=data,
        mask=[mask for i in data],
        dtype=int,
    )
    print(marr.T)


if __name__ == "__main__":

    import toytree
    t0 = "((a,b),((c,d),f));"
    t1 = "((a,b),((c,d),e));"
    t2 = "((a,c),((b,d),(e,f)));"
    t3 = "((a,c),(b,e));"

    names = list("abcdef")
    trees = toytree.mtree([t0, t1, t2, t3])
    for tree in trees:
        marr = get_matrix_representation(tree, names)
        print(marr)