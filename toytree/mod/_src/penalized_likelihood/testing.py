#!/usr/bin/env python

"""Scripts to run comparison against chronos in R.
"""

import subprocess
import numpy as np
import toyplot

RSTRING = """
library(ape)

# load the Python variables
btree <- read.tree(text="{tree}")
min_ages <- c{min_ages}
max_ages <- c{max_ages}
tips <- list{tips}
lamb <- {lamb}
model <- '{model}'

# run the R code 
nodes <- c()
for (tipset in tips) {{
    mrca <- getMRCA(btree, tipset)
    nodes <- append(nodes, mrca)
}}

calib <- data.frame(node=nodes, age.min=min_ages, age.max=max_ages)

ctree <- chronos(
    btree, 
    lambda=lamb,
    model=model,
    calibration=calib,
)
write.tree(ctree)
"""


def convert_to_rvec(tup):
    return "c('" + "','".join(tup) + "')"

def _run_chronos_in_r(tree, lamb=1, model="relaxed", calibrations=None):
    """
    For testing and validating pen.lik. methods
    """
    calibrations = calibrations if calibrations is not None else {}
    if not calibrations:
        calibrations = {tree.treenode.idx: (1, 1)}
    cmin_age = [str(calibrations[i][0]) for i in sorted(calibrations)]
    cmax_age = [str(calibrations[i][1]) for i in sorted(calibrations)]

    data = {
        "tree": tree.write(),
        "min_ages": "(" + ",".join(cmin_age) + ")",
        "max_ages": "(" + ",".join(cmax_age) + ")",
        "tips": "(" + ",".join(
            convert_to_rvec(tree.get_tip_labels(x))
            for x in sorted(calibrations)
        ) + ")" if calibrations else "()",
        "lamb": lamb,
        "model": model,
    }
    rst = RSTRING.format(**data)
    with open("/tmp/chronos.R", 'w') as out:
        out.write(rst)
    out = subprocess.run(
        ["Rscript", "/tmp/chronos.R"], 
        check=True,
        stdout=subprocess.PIPE,
    )
    out = out.stdout.decode()
    ctre = out.strip().split("[1] ")[-1].strip('"')
    return ctre, out



class TreeSampler:
    """
    Class for applying uncorrelated gamma rate transformations to edges
    to create Generative data for testing the Chronos functions.
    """
    def __init__(self, tree, neff=5e5, gentime=1, gamma=3):
        self.tree = tree
        self.neff = neff
        self.gentime = gentime
        self.gamma = gamma
        self.nnodes = self.tree.nnodes


    def plot_gamma_distributed_rates(self, nsamples=10000, bins=30):
        """
        Draws the stat distribution for verification.
        """
        a = (1 / self.gamma) ** 2
        b = 1
        gamma_rates = np.random.gamma(shape=1 / (a*b**2), scale=a*b**2, size=nsamples)

        # generate a distribution of G or Ne values
        NEVAR = gamma_rates * self.neff
        canvas = toyplot.Canvas(width=600, height=250)
        ax0 = canvas.cartesian(grid=(1, 2, 0), xlabel="gamma distributed Ne variation")
        m0 = ax0.bars(np.histogram(NEVAR, bins=bins))

        GVAR = gamma_rates * self.gentime
        ax1 = canvas.cartesian(grid=(1, 2, 1), xlabel="gamma distributed gentime variation")
        m1 = ax1.bars(np.histogram(GVAR, bins=bins))
        return canvas, (ax0, ax1), (m0, m1)
    
    
    def get_tree(self, N=False, G=False, transform=False, seed=None):
        """
        N (bool):
            Sample gamma distributed variation in Ne values across nodes.
        G (bool):
            Sample gamma distributed variation in G values across nodes.
        transform (int):
            Return edge lengths in requested units by selecting integer value:
            (0) time, (1) coalunits, (2) generations.    
        """
        # get a copy of the sptree
        tree = self.tree.copy()
        
        # use random seed
        if seed:
            np.random.seed(seed)
        
        # get gamma rate multipliers
        a = (1 / self.gamma) ** 2
        b = 1
        
        # sample N values
        if N:
            gamma_rates = np.random.gamma(
                shape=1 / (a*b**2), 
                scale=a*b**2, 
                size=self.nnodes,
            )

            # sample Ne values from gamma dist
            nevals = gamma_rates * self.neff
        
            # apply randomly to nodes of the tree
            tree = tree.set_node_values(
                feature="Ne",
                mapping={i: nevals[i] for i in range(tree.nnodes)}
            )
        else:
            tree = tree.set_node_values("Ne", default=self.neff)
        
        if G:
            gamma_rates = np.random.gamma(
                shape=1 / (a*b**2), 
                scale=a*b**2, 
                size=self.nnodes,
            )

            # sample Ne values from gamma dist
            gvals = gamma_rates * self.gentime
        
            # apply randomly to nodes of the tree
            tree = tree.set_node_values(
                feature="g",
                mapping={i: gvals[i] for i in range(tree.nnodes)}
            )
        else:
            tree = tree.set_node_values("g", default=self.gentime)      
        
        # optionally convert edges to coal units
        if transform == 1:
            tree = tree.set_node_values(
                feature="dist",
                mapping={i: j.dist / (j.Ne * 2 * j.g) for i,j in enumerate(tree)}
            )
            
        elif transform == 2:
            tree = tree.set_node_values(
                feature="dist",
                mapping={i: j.dist / j.g for i,j in enumerate(tree)}
            )            
        return tree


if __name__ == "__main__":

    import toytree
    TREE = toytree.rtree.unittree(10, treeheight=1e6)
    TSA = TreeSampler(TREE, neff=5e5, gentime=1, gamma=3)
    TRE = TSA.get_tree()
    print(TRE)
