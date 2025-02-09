#!/usr/bin/env python

"""
TODO
----
- make this into a unittest to ensure that tests several scenarios to
ensure that our results are similar within a tolerance value to the 
results of the same stat calculation in R.

"""

import toytree
from toytree.utils.src.run_r_script import run_r_script


def write_test_data(ntips: int = 24, seed: int = 123) -> None:
    """
    """
    # path to write data to
    nwk_path = "/tmp/tree.nwk"
    csv_path = "/tmp/traits.csv"    

    # generate tree
    tree = toytree.rtree.unittree(ntips=ntips, seed=seed, treeheight=10.)

    # generate data
    tree.pcm.simulate_continuous_brownian(
        rates=[5.0, 0.5], tips_only=True, seed=seed, inplace=True)

    # write data to csv
    feature = tree.get_node_data(["t0", "t1"])[:tree.ntips]
    feature.index = tree.get_tip_labels()
    feature.to_csv(csv_path)

    # write tree to newick
    tree.write(nwk_path)
    return nwk_path, csv_path


def run_phytools(nwk_path, csv_path) -> str:
    """Run the full R script."""
    rscript = rf"""
    library(phytools)

    tree <- read.tree("{nwk_path}")
    traits <- read.csv("{csv_path}", row.names=1)

    k1 <- phylosig(tree, traits$t0, test=TRUE)
    print(k1)

    k2 <- phylosig(tree, traits$t0, test=TRUE, se=traits$t1)
    print(k2)
    """
    print(run_r_script(rscript))



if __name__ == "__main__":
    
    toytree.set_log_level("DEBUG")

    # nwk_path, csv_path = write_test_data()
    # print(run_phytools(nwk_path, csv_path))

    nwk_path, csv_path = write_test_data(50, 123)
    print(run_phytools(nwk_path, csv_path))
