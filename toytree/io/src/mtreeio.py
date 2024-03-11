#!/usr/bin/env python

"""Generic multitree parsing function.

"""

from typing import Union, Collection
from pathlib import Path
import pandas as pd
from toytree.core.tree import ToyTree
from toytree.core.multitree import MultiTree
from toytree.io.src.parse import parse_multitree, parse_tree
from toytree.utils import ToytreeError


def mtree(data: Union[str, Path, Collection[ToyTree]], **kwargs) -> MultiTree:
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

    # a single file path containing multline newicks or nexus.
    if isinstance(data, (Path, str)):
        return parse_multitree(data, **kwargs)

    # --- Collections of inputs --- #
    assert len(set(type(i) for i in data)) == 1, "input data cannot be multiple types."

    # handle ipcoal sim series
    if isinstance(data, pd.Series):
        data = data.to_list()

    # collection of ToyTrees
    if isinstance(data[0], ToyTree):
        data = [i.copy() for i in data]
        treelist = data

    elif isinstance(data[0], (str, Path)):
        treelist = [parse_tree(i) for i in data]

    else:
        raise ToytreeError("mtree input format not recognized.")

    mtre = MultiTree(treelist)
    assert len(mtre.treelist), "MultiTree is empty, parsing failed."
    return mtre


if __name__ == "__main__":

    import numpy as np
    import ipcoal

    TEST3 = "https://eaton-lab.org/data/densitree.nex"
    URL3 = "https://eaton-lab.org/data/densitree.nex"
    PATHNWK3 = Path("~/Downloads/densitree.nwk").expanduser()
    PATHNEX3 = Path("~/Downloads/densitree.nex").expanduser()
    STRP3 = "~/Downloads/densitree.nex"

    print(mtree(TEST3))

    # parse a newick file with many trees
    print(mtree(PATHNWK3))

    # parse a nexus file with many trees
    print(mtree(PATHNEX3))

    # parse a URL to a file with many trees
    print(mtree(URL3))

    TEST3 = "https://eaton-lab.org/data/densitree.nex"
    TEST4 = """\
#NEXUS
begin trees;
    translate
           1 apple,
           2 blueberry,
           3 cantaloupe,
           4 durian,
        ;
    tree tree0 = [&U] ((1,2),(3,4));
    tree tree1 = [&U] ((1,2),(3,4));
end;
"""

    TEST5 = """\
(((a:1,b:1):1,(d:1.5,e:1.5):0.5):1,c:3);
(((a:1,d:1):1,(b:1,e:1):1):1,c:3);
(((a:1.5,b:1.5):1,(d:1,e:1):1.5):1,c:3.5);
(((a:1.25,b:1.25):0.75,(d:1,e:1):1):1,c:3);
(((a:1,b:1):1,(d:1.5,e:1.5):0.5):1,c:3);
(((b:1,a:1):1,(d:1.5,e:1.5):0.5):2,c:4);
(((a:1.5,b:1.5):0.5,(d:1,e:1):1):1,c:3);
(((b:1.5,d:1.5):0.5,(a:1,e:1):1):1,c:3);
"""

    print(mtree(TEST3))
    print(mtree(TEST4))
    print(mtree(TEST5))
    print(mtree(mtree(TEST5).treelist))
    print(mtree(mtree(TEST5).write()))

    # # set variables
    # Ne = 10000
    # nsamples = 8
    # mut = 1e-7
    # nloci = 100

    # # simulate sequence data
    # model = ipcoal.Model(tree=None, Ne=Ne, nsamples=nsamples, mut=mut)
    # model.sim_loci(nloci=nloci, nsites=20)
    # model.seqs = np.concatenate(model.seqs, 1)

    # # show some of the genealogies that were produced
    # c, a, m = model.draw_genealogies(height=200, shared_axes=True);

    # import toyplot.browser
    # toyplot.browser.show(c)

