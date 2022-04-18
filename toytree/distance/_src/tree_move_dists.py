#!/usr/bin/env python

"""Tree distance measures based on tree moves (SPR and NNI).

TODO.

References
----------
- 
"""


def tree_dist_nni():
    """

    Use the approach of Li et al. (1996) to approximate the Nearest 
    Neighbour Interchange distance (Robinson, 1971) between 
    phylogenetic trees.

    FROM TREEDIST:
    https://cran.r-project.org/web/packages/TreeDist/TreeDist.pdf

    In brief, this approximation algorithm works by identifying edges in one tree that do not match
    edges in the second. Each of these edges must undergo at least one NNI operation in order to
    reconcile the trees. Edges that match in both trees need never undergo an NNI operation, and divide
    each tree into smaller regions. By ’cutting’ matched edges into two, a tree can be divided into a
    number of regions that solely comprise unmatched edges.
    These regions can be viewed as separate trees that need to be reconciled. One way to reconcile
    these trees is to conduct a series of NNI operations that reduce a tree to a pectinate (caterpillar) tree,
    then to conduct an analogue of the mergesort algorithm. This takes at most n log n + O(n) NNI
    operations, and provides a loose upper bound on the NNI score. The maximum number of moves
    for an n-leaf tree (OEIS A182136) can be calculated exactly for small trees (Fack et al. 2002); this
    provides a tighter upper bound, but is unavailable for n > 12. NNIDiameter() reports the limits on
    this bound.    

    References
    ----------
    - Li et al. (1996)
    - Fack V, Lievens S, Van der Jeugt J (2002). “On the diameter of 
    the rotation graph of binary coupling trees.” Discrete Mathematics,
    245(1-3), 1–18.
    - Robinson DF (1971). “Comparison of labeled trees with valency 
    three.” Journal of Combinatorial Theory, Series B, 11(2), 105–119.
    """


def tree_dist_spr(tree1, tree2, max_dist: int=10) -> float:
    """Heuristic search algorithm to count N SPR moves separating two trees.
    
    Starting from tree1 all SPR moves that decrease the distance 
    ... continue until dist=0 or max_dist is exceeded.
    """


if __name__ == "__main__":
    pass
