#!/usr/bin/env python

"""Example data strings."""

import numpy as np
import pandas as pd


newick_str = "((a,b),c);"
newick_url = "https://eaton-lab.org/Cyathophora.nwk"
newick_file = "..."

newick_multitree_str = """\

"""

nexus_str = """\
"""

nexus_multitree_str = """\
"""


distance_matrix = pd.DataFrame(
    index=["dog", "bear", "raccoon", "weasel", "seal", "sea lion", "cat", "monkey"],
    columns=["dog", "bear", "raccoon", "weasel", "seal", "sea lion", "cat", "monkey"],
    data=np.array([
        [0, 32, 48, 51, 50, 48, 98, 148],
        [32, 0, 26, 34, 29, 33, 84, 136],
        [48, 26, 0, 42, 44, 44, 92, 152],
        [51, 34, 42, 0, 44, 38, 86, 142],
        [50, 29, 44, 44, 0, 24, 89, 142],
        [48, 33, 44, 38, 24, 0, 90, 142],
        [98, 84, 92, 86, 89, 90, 0, 148],
        [148, 136, 152, 142, 142, 142, 148, 0],
    ])
)


if __name__ == "__main__":

    import toytree
    toytree.tree(newick_str)
