#!/usr/bin/env python

from __future__ import print_function, division, absolute_import

import numpy as np
from .utils import ToytreeError
from .Toytree import ToyTree

# requirements for submodule not included in conda recipe
try:    
    import scipy.linalg
except ImportError:
    raise ToytreeError(
        "SeqGen module requires scipy. Please run 'conda install scipy'"
    )

try:    
    from numba import njit
except ImportError:
    raise ToytreeError(
        "SeqGen module requires numba. Please run 'conda install numba'"
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


A nice description of models here:
https://en.wikipedia.org/wiki/Models_of_DNA_evolution
"""


# GLOBALS, using alphabetical order ACGT througout
FREQS = (0.25, 0.25, 0.25, 0.25)

BASEDICT = {
    0: "A", 1: "C", 2: "G", 3: "T",
}

GENERAL = np.array([
    [0, 1, 1, 1],
    [1, 0, 1, 1],
    [1, 1, 0, 1],
    [1, 1, 1, 0],
], dtype=np.float64)


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
        Parameters of GTR subfamily subsitution models. 
        pi: (tuple)
            Equilibrium frequencies of A,C,G,T. Default (0.25,0.25,0.25,0.25)
        tstv: (float)
            transition to transversion ratio (kappa). Default=1.0
        rates: (tuple)
            C<->T, A<->T, G<->T, A<->C, C<->G. Default (1,1,1,1,1,1).
    seed (int):
        Random number generator seed.
    """
    def __init__(self, tree, model_kwargs={}, seed=None, quiet=False):

        # store X
        np.random.seed(seed)
        if isinstance(tree, ToyTree):
            self.tree = tree
        else:
            self.tree = ToyTree(tree)
        self.seqdict = {}

        # substitution model params
        self.model_kwargs = {
            "pi": (0.25, 0.25, 0.25, 0.25),
            "tstv": 1.0, 
            "rates": (1.0, 1.0, 1.0, 1.0, 1.0, 1.0),
        }
        self.model_kwargs.update(model_kwargs)

        # print summary of the model
        if not quiet:
            mr = model_kwargs.get("rates")
            tr = model_kwargs.get("tstv")
            pr = model_kwargs.get("pi")
            if mr:
                print("[GTR] ...")
                raise NotImplementedError("Sorry, not model yet supported.")
            elif tr:
                if pr:
                    print("[HKY85] tstv={}; pi={}".format(tr, pr))
                else:
                    print("[K80] ts/tv={} (kappa={});".format(tr))
            elif pr:
                print("[F81] pi={}".format(pr))
            else:
                print("[JC69]")

        # equilibrium base frequencies, if not freqs param then set to 0.25
        self.pi = np.array(FREQS)
        if "pi" in self.model_kwargs:
            self.pi = np.array(self.model_kwargs["pi"])
        assert np.isclose(1.0, sum(self.pi)), "freqs must sum to 1."

        # get transition matrix, e.g., [0., 1., 1., 1.,]
        self.t = GENERAL.copy()
        
        # incorporate transition/transversion ratio
        ka = self.model_kwargs["tstv"]
        self.t *= np.array([
            [0., 1., ka, 1.],
            [1., 0., 1., ka],
            [ka, 1., 0., 1.],
            [1., ka, 1., 0.],
        ])

        # incorporate equilibrium frequencies
        self.w = self.t * self.pi
        self.qmatrix = self.w / self.w.sum(axis=1)

        # fill diagonal, e.g., [-3., 1., 1., 1.]
        np.fill_diagonal(self.qmatrix, -self.qmatrix.sum(axis=1))
        # self.qmatrix = self.qmatrix / self.qmatrix.min() * -1

        # store probability matrix
        self.qdict = {}
        for node in self.tree.treenode.traverse("preorder"):
            self.qdict[node.idx] = scipy.linalg.expm(self.qmatrix * node.dist)
        # self.qdict = check_k80(self.tree.treenode, self.pi)


    def mutate(self, nsites=1, mode=0):
        """
        Simulate sequences.

        Parameters:
        -----------
        mode (int):
            0: return dictionary mapping tip names to string sequences. 
            1. return array with rows ordered by tip idx and bases as ints.
            2. return array with 1 randomly sampled SNP.
        """
        # wrap in while loop to repeat if no SNPs found for mode=2
        while 1:

            # store results for tips of tree in both dict and array
            seqs = {}
            sarr = np.zeros((len(self.tree), nsites), dtype=np.uint8)

            # store all internals seqs in a dict, starting with root seq.
            self.seqdict = {
                self.tree.treenode.idx: 
                np.random.choice((0, 1, 2, 3), size=nsites)
            }

            # traverse tree starting parents to children and simulate seqs
            for node in self.tree.treenode.traverse("preorder"):
                if not node.is_root():
                    # get ancestral seq for this edge
                    anc = self.seqdict[node.up.idx].copy()

                    # get transition probs for this edge
                    probs = self.qdict[node.idx]
                    
                    # jitted function 
                    anc = mutate_sites(nsites, anc, probs)

                    # store this sequence at this node
                    self.seqdict[node.idx] = anc

                    # store final result
                    if node.is_leaf():
                        seqs[node.name] = "".join([BASEDICT[i] for i in anc])
                        sarr[node.idx] = anc

            # return results, ends simulation unless mode=2 and no SNPs
            if mode == 0:
                return seqs
            elif mode == 1:
                return sarr
            else:
                snps = sarr[:, np.any(sarr != sarr[0], axis=0)]
                if snps.size:
                    return snps[:, 0]




def check_jc69(treenode, pi):
    qdict = {}
    for node in treenode.traverse("preorder"):
        dist = node.dist
        beta = 1 / (1 - (pi[0]**2) - (pi[1]**2) - (pi[2]**2) - (pi[3]**2))
        exbd = np.exp(-1 * beta * dist)
        pii = [(exbd + i * (1 - exbd)) for i in pi]
        pij = [i * (1 - exbd) for i in pi]

        # build the prob matrix
        matr = np.array([
            [pii[0], pij[1], pij[2], pij[3]],
            [pij[0], pii[1], pij[2], pij[3]],
            [pij[0], pij[1], pii[2], pij[3]],
            [pij[0], pij[1], pij[2], pii[3]],
        ])
        qdict[node.idx] = matr
    return qdict


def check_k80(treenode, pi):
    return check_jc69(treenode, pi)


def check_f81():
    pass

def check_hky85():
    pass


# b = 1 / (1 - pi[0]**2 - pi[1]**2 - pi[2]** - pi[3]**2)
# ebv = np.exp(-b * dist)
# ii = [ebv + pi[j] * (1 - ebv) for j in pi]
# ij = [pi[j] * (1 - ebv) for j in pi]

# P = [
#     [ii, ij, ij, ij],
#     [ij, ii, ij, ij],
#     [ij, ij, ii, ij],
#     [ij, ij, ij, ii],
# ]



class Distance(object):
    def __init__(self, arr):
        self.arr = arr
        self.ntaxa = self.arr.shape[0]
        self.matr = np.zeros((self.ntaxa, self.ntaxa))


    def hamming_distance(self):
        pass


    def jc_distance(self):    
        for i in range(self.ntaxa):
            for j in range(self.ntaxa):
                if i != j:
                    # get proportion differences
                    ps = np.sum(self.arr[i] != self.arr[j]) / self.arr.shape[1]
                    dist = (-3.0 / 4.0) * np.log(1. - (4.0 / 3.0 * ps))
                    self.matr[i, j] = round(dist, 4)
        return self.matr


    def k80_distance(self):    
        for i in range(self.ntaxa):
            for j in range(self.ntaxa):
                if i != j:
                    # get proportion transitions and transversion
                    ps = np.sum(self.arr[i] != self.arr[j]) / self.arr.shape[1]
                    dist = (-3.0 / 4.0) * np.log(1. - (4.0 / 3.0 * ps))
                    self.matr[i, j] = round(dist, 4)
        return self.matr

    # def get_HKY85(self):    
    #     for i in range(self.ntaxa):
    #         for j in range(self.ntaxa):
    #             if i != j:
    #                 # get proportion transitions and transversion
    #                 ps = np.sum(self.arr[i] != self.arr[j]) / self.arr.shape[1]
    #                 dist = (-3.0 / 4.0) * np.log(1. - (4.0 / 3.0 * ps))
    #                 self.matr[i, j] = round(dist, 4)
    #     return self.matr        



@njit
def mutate_sites(nsites, ancestral_seq, prob_matrix):
    for site in range(nsites):
        state = ancestral_seq[site]
        trans = prob_matrix[state]
        newsite = np.argmax(np.random.multinomial(1, pvals=trans))
        ancestral_seq[site] = newsite
    return ancestral_seq