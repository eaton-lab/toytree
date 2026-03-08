#!/usr/bin/env python

"""Infer quartet supertree by "Split constrained quartet optimization"

References
----------
- Constructing Optimal Trees from Quartets. (2001) David Bryant
and Mike Steel. Journal of Algorithms 38, 237-259. doi:10.1006/jagm.2000.1133

- H.-J. Bandelt and A. Dress, A canonical decomposition theory for
metrics on a finite set, Adv. Math. 92 (1992), 47-105.
[This paper defines the 'weakly compatible set' and 'maximum set'.]

- D. Bryant, Hunting for trees in binary character sets: efficient
algorithms for extraction, enumeration, and optimization, J. Comput.
Biol. 3 1995 , 275-288.
[Describes a compatibility algorithm that is extended here.]

Notes
-----
Three definitions in Steel:
1. A set of splits L is compatible if it is a subset of splits in T.
2. A set if weakly compatible if for every three splits (A1|B1, A2|B2, A3|B3)
   at least one of the following intersections is empty:
   B1 n B2 n B3
   B1 n A2 n A3
   A1 n B2 n A3
   A1 n A2 n B3
3. A set of weakly compatible splits L on X is maximum if |L| = n(n-1)/2.

The weight of a tree, w(T), is the sum of all its compatible quartet weights.
"""






if __name__ == "__main__":

    # generate a test data set of trees
    # import ipcoal
