# stochastic_mapping.py

"""Stochastic character mapping.

This is a method of simulating a history for a discrete character
data set conditioned on the observed states at the tips ...
(and optionally at internal nodes?).

This method also needs a new plotting framework for displaying 
changes along edges of a tree using rectangles with linear-gradient
maps.

References
-----------
Bollback, J. P. (2006) Stochastic character mapping of discrete traits on phylogenies. BMC Bioinformatics, 7, 88.
Huelsenbeck, J. P., R. Neilsen, and J. P. Bollback (2003) Stochastic mapping of morphological characters. Systematic Biology, 52, 131-138.
"""

class StochasticMap:
    """Maps nodes to ndarrays of states and times?

    """
