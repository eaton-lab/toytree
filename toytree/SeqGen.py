#!/usr/bin/env python

from __future__ import print_function, division, absolute_import

import numpy as np
from .utils import ToytreeError
from .Toytree import ToyTree
try:
    import scipy.linalg
except ImportError:
    raise ToytreeError(
        "SeqGen module requires scipy. Please run 'conda install scipy'"
    )


"""
From the seq-gen paper:
Seq-Gen reads in a tree from a file containing one or more
trees in PHYLIP format (Felsenstein, 1993). These trees may
be rooted or unrooted, but they must include branch lengths.
Each branch length is assumed to denote the mean number
of nucleotide substitutions per site that will be simulated
along that branch. If this is not the case, then a scaling factor
must be supplied that will transform the branch lengths into
the mean number of substitutions per site. For example, if the
branch lengths are given in units of millions of years (Myr)
and the rate of molecular evolution was 0.5 substitutions
per site per Myr, then the user should give a scaling factor
of 0.5 to obtain the expected amount of substitution along
each branch.
"""


# GLOBALS, using alphabetical order ACGT througout
FREQS = (0.25, 0.25, 0.25, 0.25)

SEQMODEL = {
    "JC": {},                                                     # JC69
    "K8": {"tstv": 1.0},                                          # K80, K2P
    "F8": {"pi": FREQS},                                          # F81
    "HK": {"tstv": 1.0, "pi": FREQS},                             # HKY85
    # "GTR": {"AC": 0.15, "AG": 0.15, "AT": 0.15, 
    # "CG": 0.15, "CT": 0.15, "GT": 0.15}
}

BASEDICT = {
    0: "A", 1: "C", 2: "G", 3: "T",
}


class SeqGen(object):
    """
    Simulate nucleotide sequences on an input ToyTree topology under a number
    of parameterized nucleotide substitution models. 

    Parameters:
    -----------
    tree (ToyTree, str):
        An input topology with branch lengths is expected number of subst.
    model (str):
        Substitution model: JC69, K80, F81, HKY85
    model_kwargs (dict):
        Parameters of the model. Only parameters that are part of the selected
        model will be used. Parameters include transition
        Default transition/transversion ratio=0.5, and 
        default "pi"
    seed (int):
        Random number generator seed.
    """
    def __init__(self, tree, model="JC", model_kwargs={}, seed=None):

        # store X
        np.random.seed(seed)
        if isinstance(tree, ToyTree):
            self.tree = tree
        else:
            self.tree = ToyTree(tree)
        self.seqdict = {}

        # substitution model params
        self.model = model
        self.model_kwargs = SEQMODEL[model[:2].upper()]
        self.model_kwargs.update(
            {i: j for (i, j) in model_kwargs.items() if i in self.model_kwargs}
        )
        # print ignored user params
        ignored = {i for i in model_kwargs if i not in self.model_kwargs}
        if ignored:
            print("The following params will be ignored in model {}: {}"
                .format(self.model, ignored))

        # equilibrium base frequencies, if not freqs param then set to 0.25
        self.pi = np.array(FREQS)
        if "pi" in self.model_kwargs:
            self.pi = np.array(self.model_kwargs["pi"])
        assert np.isclose(1.0, sum(self.pi)), "freqs must sum to 1."


    def mutate(self, nsites=1, mode=0):
        """
        Simulate sequences.

        Parameters:
        -----------
        mode (int):
            0: return dictionary mapping tip names to string sequences. 
            1. return array with rows ordered by tip idx and bases as ints.
            2. return array with  as 1 but return only SNPs.
        """

        # set alpha=beta if not tstv
        ts = (
            self.model_kwargs["tstv"] if self.model_kwargs.get("tstv") else 1.0
        )
        tv = 1.0

        # get transition matrix
        self.w = np.array([
            [0., tv, ts, tv],
            [tv, 0., tv, ts],
            [ts, tv, 0., tv],
            [tv, ts, tv, 0.],
        ])

        # fill diagonal of transition matrix to sum to 1
        np.fill_diagonal(self.w, -self.w.sum(axis=0))

        # multiply transition matrix by starting frequencies.
        self.qmatrix = self.w * self.pi

        # wrap in while loop to repeat if no SNPs found for mode=2
        while 1:
            seqs = {}
            sarr = np.zeros((len(self.tree), nsites), dtype=np.uint8)
            self.seqdict = {
                self.tree.treenode.idx: 
                np.random.choice((0, 1, 2, 3), size=nsites, p=self.pi)
            }

            # traverse tree starting with allele at the root
            for node in self.tree.treenode.traverse("preorder"):
                if not node.is_root():
                    # get ancestral seq for this edge
                    anc = self.seqdict[node.up.idx]

                    # get transition probs for this edge
                    probs = scipy.linalg.expm(self.qmatrix * node.dist)

                    # could JIT this loop for max speed
                    for idx in range(len(anc)):

                        # current state
                        state = anc[idx]

                        # probability matrix for this site on this edge
                        trans = probs[state]
                        new = np.argmax(np.random.multinomial(1, pvals=trans))
                        anc[idx] = new

                    # store this sequence at this node
                    self.seqdict[node.idx] = anc.copy()

                    # store final result
                    if node.is_leaf():
                        seqs[node.name] = "".join([BASEDICT[i] for i in anc])
                        sarr[node.idx] = anc

            # return results
            if mode == 0:
                return seqs
            elif mode == 1:
                return sarr
            else:
                snps = sarr[:, np.any(sarr != sarr[0], axis=0)]
                if snps.size:
                    return snps[:, 0]
