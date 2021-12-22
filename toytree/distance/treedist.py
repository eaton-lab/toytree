#!/usr/env/bin python

"""
A collection of tree distance metrics.

Authors: Deren Eaton, Patrick McKenzie, Scarlet Ming-sha Au
"""

# from toytree.distance.robinson_foulds import RobinsonFoulds


def robinson_foulds(tree1, tree2, *args):
    """Returns the Robinson-Foulds distance between two trees.

    Faster cleaner version of RF...

    Parameters
    ----------
    tree1: toytree.ToyTree
        A first toytree instance to compare to another tree.
    tree2: toytree.ToyTree
        A second toytree instance to compare to tree1.
    *args: 
        Additional args TBD.

    Examples
    ---------
    >>> tree1 = toytree.rtree.unittree(10, seed=123)
    >>> tree2 = toytree.rtree.unittree(10, seed=321)
    >>> toytree.distance.treedist.robinson_foulds(tree1, tree2)
    """
    tool = RobinsonFoulds(tree1, tree2, *args)
    tool.run()
    return tool.data

def quartet_distance(tree1, tree2, *args):
    """Returns the quartet tree distance between two trees.

    Parameters
    ----------
    tree1: toytree.ToyTree
        A first toytree instance to compare to another tree.
    tree2: toytree.ToyTree
        A second toytree instance to compare to tree1.
    *args: 
        Additional args TBD.

    Examples
    --------
    >>> tree1 = toytree.rtree.unittree(10, seed=123)
    >>> tree2 = toytree.rtree.unittree(10, seed=321)
    >>> toytree.distance.treedist.quartets(tree1, tree2)
    """
    pass
