#!/usr/env/bin python

"""
A collection of tree distance metrics.


Authors: Deren Eaton, Patrick McKenzie, Scarlet Ming-sha Au
"""

from toytree.distance.robinson_foulds import RobinsonFoulds

def robinson_foulds(tree1, tree2, *args):
    """
    Faster cleaner version of RF
    """
    tool = RobinsonFoulds(tree1, tree2, *args)
    tool.run()
    return tool.data

def quartet_distance(tree1, tree2, *args):
    """
    ...
    """
    pass
