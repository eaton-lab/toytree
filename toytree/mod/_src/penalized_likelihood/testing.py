#!/usr/bin/env python

"""Scripts to run comparison against chronos in R.
"""

from typing import List, Tuple
import subprocess

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

ctrl <- chronos.control(nb.rate.cat = 2)
ctree <- chronos(
    btree, 
    lambda=lamb,
    model=model,
    calibration=calib,
    control=ctrl,
)

write.tree(ctree)
"""


def _run_chronos_in_r(tree, lamb=1, model="relaxed", calibrations:List[Tuple[int,int]]=None):
    """For testing and validating pen.lik. methods
    """
    calibrations = calibrations if calibrations is not None else {}
    if not calibrations:
        calibrations = {tree.treenode.idx: (1, 1)}
    cmin_age = [str(calibrations[i][0]) for i in sorted(calibrations)]
    cmax_age = [str(calibrations[i][1]) for i in sorted(calibrations)]

    # make
    tips = []
    for x in sorted(calibrations):
        names = tree.get_nodes(x)[0].get_leaf_names()
        rvec = "c('" + "','".join(names) + "')"
        tips.append(rvec)
    tips = ",".join(tips)
    print(tips)

    data = {
        "tree": tree.write(),
        "min_ages": "(" + ",".join(cmin_age) + ")",
        "max_ages": "(" + ",".join(cmax_age) + ")",
        "tips": f"({tips})" if calibrations else "()",
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



if __name__ == "__main__":

    import toytree
    from toytree.mod._src.penalized_likelihood.pl_utils import get_tree_with_categorical_rates
    toytree.set_log_level("DEBUG")

    # tree = toytree.rtree.rtree(ntips=20, seed=123)
    tree = get_tree_with_categorical_rates(ntips=50, nrates=2, seed=123)

    # clock, discrete, relaxed, correlated
    tre, out = _run_chronos_in_r(tree, lamb=1, model="discrete", calibrations={})
    print(out)
    toytree.tree(tre)._draw_browser(ts='s', use_edge_lengths=True, tmpdir="~")


    # {'loglik': -185.90250920810345, 'PHIIC': 473.8050184162069, 'rates': [4.697960544460034, 53.74799195502471], 'freqs': [0.4725447347829576, 0.5274552652170423], 'tree': <toytree.ToyTree at 0x7edd326f32f0>, 'converged': True}
