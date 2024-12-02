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
[name                           scope                   ntips                               nnodes      reference]
[----------------------------------------------------------------------------------------------------------------]
[World Plants (WP)              vascular plants          355,576                            ...          Hassler, Michael (1994 - 2024): World Plants. Synonymic Checklist and Distribution of the World Flora. Version 24.11; last update November 5th, 2024.]
[Leipzig Plant Catalogue (LCVP) vascular plants          351,180 (+6,160 hybrids)           ...          Freiberg M (2020). The Leipzig catalogue of vascular plants. German Centre for Integrative Biodiversity Research (iDiv) Halle-Jena-Leipzig. Checklist dataset https://doi.org/10.15468/9qxmn3 accessed via GBIF.org on 2024-11-25.]
[TreeFam (TF)                   animal gene trees        ...                                ...          Jue Ruan, Heng Li, et al. Nucleic Acids Research (2008) doi: 10.1093/nar/gkm1005]
[BirdTree (BT)                  birds                    9,993                              ...          Jetz, W., G. H. Thomas, J. B. Joy, K. Hartmann, and A. O. Mooers. 2012. The global diversity of birds in space and time. Nature 491:444-448    ]


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
