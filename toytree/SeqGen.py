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



#######################################################
# Seqgen simple class
#######################################################
FREQS = {
    "C": 0.25, "A": 0.25, "T": 0.25, "G": 0.25,
}

SEQMODEL = {
    "JC": {},                                                     # JC69
    "K8": {"tstv": 0.5},                                          # K80, K2P
    "F8": {"freqs": FREQS},                                       # F81
    "HK": {"tstv": 0.5, "freqs": FREQS},                          # HKY85
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
        self.tree = ToyTree(tree)
        self.matrix = np.zeros((len(tree), 1), dtype=bytes)
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

        # equilibrium base frequencies
        self.freqs = FREQS
        if "freqs" in self.model_kwargs:
            self.freqs.update(self.model_kwargs["freqs"])
        self.pi = np.array([self.freqs[i] for i in "ACGT"], dtype=np.float64)
        assert np.isclose(1.0, sum(self.pi)), "freqs must sum to 1."


    def mutate(self, nsites=1):

        # sequence at the ancestral node drawn from equilibrium freqs
        self.seqdict = {
            self.tree.treenode.idx: 
            np.random.choice((0, 1, 2, 3), size=nsites, p=self.pi)
        }

        # the rate matrix
        alpha = 1.0
        beta = (
            self.model_kwargs["tstv"] if self.model_kwargs.get("tstv") else 1.0
        )
        self.w = np.array([
            [0., beta, alpha, beta],
            [beta, 0., beta, alpha],
            [alpha, beta, 0., beta],
            [beta, alpha, beta, 0.],
        ])            
        np.fill_diagonal(self.w, -self.w.sum(axis=0))

        # instantaneous rate matrix (transition matrix X equil freqs)        
        self.qmatrix = self.w * self.pi

        # traverse tree starting with allele at the root
        seqs = {}        
        nsites = len(self.seqdict[self.tree.treenode.idx])
        for node in self.tree.treenode.traverse("preorder"):
            if not node.is_root():
                # get ancestral seq for this edge
                anc = self.seqdict[node.up.idx]

                # get transition probs for this edge
                probs = scipy.linalg.expm(self.qmatrix * node.dist)

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
        return seqs
