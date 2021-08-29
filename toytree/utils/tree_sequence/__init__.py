#!/usr/bin/env python

"""
Utilities for visualizing TreeSequences from tskit or SLiM.

The :class:`ToyTreeSequence` class holds the tskit.trees.TreeSequence 
object in its `.tree_sequence` attribute. It is primarily used to 
generate drawings of one or more trees with the option to display 
mutations, MutationTypes, and a chromosome structure. These latter 
options are mostly for SLiM simulated TreeSequences.

Examples
--------
>>> tts = toytree.utils.tree_sequence.ToyTreeSequence(tree_sequence)
>>> tts.draw_tree(idx=0)
>>> tts.draw()
"""

from .src.toytree_sequence import ToyTreeSequence
