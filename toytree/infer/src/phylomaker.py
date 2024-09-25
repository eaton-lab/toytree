#!/usr/bin/env python

"""A phylomaker-type tool that returns a pruned tree from a list of names.

As an example, the R tool "V.PhyloMaker2" takes ~42 hours to load an
existing large tree and prune it down to a list of >350K supplied taxa.

References
----------
Yi, J & Hong Q (2023) V.PhyloMaker2: An updated and enlarged R package
that can generate very large phylogenies for vascular plants.
Plant Diversity. https://doi.org/10.1016/j.pld.2022.05.005

Data Sources
------------
[name     scope       ntips        nnodes      reference]
[-------------------------------------------------------]
[...      birds      10,000        20,000      author...]
[...      plants    300,000       400,000      author...]
[...       ...        ...           ...          ...    ]

Development Plan
-----------------
return dataframe w/ [tree-name, taxon-scope, ntips, nnodes, reference]
>>> toytree.infer.phylomaker.show_sources()
fetch newick of a big tree (from web) and write to disk.
>>> toytree.infer.phylomaker.fetch_newick(name)
fetch newick of a big tree (from web) and parse to toytree.
>>> toytree.infer.phylomaker.fetch_tree(name)
get a subtree as a ToyTree from a tree source and list of taxa.
this fetches and parses the full tree and caches a pickled copy
of the Toytree so it does not need to be re-parsed if re-run. It
logs warnings about bad taxon names, etc. and prunes the tree to
allow internal node name sampling such as genus, family.
>>> toytree.infer.phylomaker.get_subtree(name, list, cache=False)
"""


if __name__ == "__main__":
    pass
