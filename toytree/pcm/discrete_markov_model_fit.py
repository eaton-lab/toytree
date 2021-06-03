#!/usr/bin/env python

"""
Discrete State Markov Model Simulator. 
Some code from ipcoal (McKenzie and Eaton 2020).
"""

from typing import Optional, Union, Dict, Any
from enum import Enum
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import expm
from toytree import ToyTree
from toytree.utils.exceptions import ToytreeError


class DiscreteModelType(str, Enum):
    ard = "all-rates-different"
    er = "all-rates-equal"
    sym = "symmetric"



class DiscreteMarkovModelFit:
    """
    Fit an n-state discrete Markov model using maximum likelihood 
    (in scipy) to estimate transition rate parameters under one of
    several supported models ("ER", "ARD", ...)

    Parameters:
    -----------
    tree (ToyTree):
        A toytree object with ultrametric branch lengths.
    data (pd.DataFrame):
        A DataFrame with tip names as the index, and categorical data 
        values (e.g., int, str, etc.) assigned to every tip in the tree.
        The column names are not used. All columns in the DataFrame are
        analyzed as replicate observations.
    model (str): 
        ...

    Examples:
    ---------
    import numpy as np
    import toytree

    # simulate discrete data on a tree
    tree = toytree.rtree.unittree(ntips=10, treeheight=10)
    qmatrix = [[-0.5, 0.5], [0.1, -0.1]]
    data = tree.pcm.simulate_discrete_data(qmatrix, nsims=10)
    
    # fit Markov model to discrete data
    tree, model = tree.pcm.discrete_markov_model_fit(data)

    # print model summary, or access rates, states, and other stats
    print(model.summary)
    print(model.qmatrix)

    # draw tree with inferred ancestral states
    tree.draw(node_colors=tree.get_node_values('trait'))

    See also: 
    ---------
    - toytree.pcm.stochastic_character_mapping
    - toytree.pcm.discrete_markov_model_sim

    References:
    -----------
    - ...
    - https://github.com/rcohen/hogtie
    """
    def __init__(
        self, 
        tree: ToyTree,
        data: pd.DataFrame,
        model: Union[str,np.ndarray] = "sym",
        prior: Optional[np.ndarray] = None,
        ):

        self.tree = tree    # get's replaced by a copy 
        self.model = model

        # get unique data and ensure tip names aligned
        if isinstance(data, pd.Series):
            data = pd.DataFrame(data)
        assert isinstance(data, pd.DataFrame), "data must be a DataFrame"
        assert set(data.index) == set(tree.get_tip_labels()), (
            "the index of data must have the same tip names as the input tree")
        self.data = data.copy() # gets converted to ints

        # get empty Q matrix ...
        self.ints_to_states = dict(enumerate(np.unique(data)))
        self.states_to_ints = {j:i for i, j in self.ints_to_states.items()}
        self.nstates = len(self.states_to_ints)
        self.prior = (
            prior if prior is not None 
            else np.repeat(1 / self.nstates, self.nstates)
        )
        assert self.prior.size == self.nstates


        # organize data as ints to w/ only uniques
        self.unique = None
        self.inverse = None
        self.get_unique_data()

        # the params to infer depends on the model type and size
        self.qmatrix = np.zeros((self.nstates, self.nstates))
        self.params = {}
        self.qidx = None
        if isinstance(self.model, str):
            self.model = self.model.upper()
            self.set_qmatrix_auto()
        else:
            self.set_qmatrix_custom()

        # prepare data
        self.set_node_arrays_to_tree()


    def get_unique_data(self):
        """
        Record only unique observed tip patterns and the inverse info
        to expand back to the full later.
        """
        for state in self.states_to_ints:
            self.data[self.data == state] = self.states_to_ints[state]
        self.unique, self.inverse = np.unique(
            self.data,
            return_inverse=True,
            axis=1,
        )
        #print(f'unique array shape: {self.unique.shape}')


    def set_qmatrix_custom(self):
        """
        TODO: Parse the custom qmatrix from user and check:
          - todo: cannot enter mixed type w/ numpy tho...
          - Values on the diagonal cannot be set (are overwritten)
          - Values as floats are fixed at their value (not inferred)
          - Values as ints on any off-diagonal are inferred.
        """
        raise NotImplementedError("TODO")
        # try to coerce into an array if not a string
        starting = 1 / self.tree.treenode.height
        self.qidx = np.array(self.model).astype(int)
        self.params = {i: starting for i in np.unique(self.qidx) if i}


    def set_qmatrix_auto(self):
        """
        Get the number of parameters to estimate, and a matrix (qidx)
        with those parameters. 

               ER          SYM          ARD        CUSTOM
           [0 1 1 1]    [0 1 2 3]    [0 1 2 3]      ...
           [1 0 1 1]    [1 0 1 2]    [7 0 4 5]
           [1 1 0 1]    [2 1 0 1]    [8 9 0 6]
           [1 1 1 0]    [3 2 1 0]    [10 11 12 0]

            [0 1 1]      [0 1 2]      [0 1 2]
            [1 0 1]      [1 0 3]      [4 0 3]
            [1 1 0]      [2 3 0]      [5 6 0]

             [0 1]        [0 1]        [0 1]
             [1 0]        [2 0]        [2 0]
        """
        starting = 1 / self.tree.treenode.height        
        self.qidx = np.zeros(self.qmatrix.shape, dtype=int)

        # assign everything to the same one rate (ER)
        if self.model.upper() == "ER":
            self.params[1] = starting
            self.qidx[:] = 1
            self.qidx[np.diag_indices_from(self.qidx)] = 0
            return

        # ARD & SIM: assign a parameter to every cell in upper triangle
        pidx = 1
        indices = np.triu_indices(self.qidx.shape[0], k=1)
        for cidx, cidy in zip(*indices):
            self.params[pidx] = 1 / self.tree.treenode.height
            self.qidx[cidx, cidy] = pidx
            pidx += 1

        # assign a parameter to every cell in upper triangle            
        indices = np.tril_indices(self.qidx.shape[0], k=-1)
        for cidx, cidy in zip(*indices):
            if self.model == "ARD":
                self.params[pidx] = starting
                self.qidx[cidx, cidy] = pidx
                pidx += 1
            elif self.model == "SYM":
                self.qidx[cidx, cidy] = self.qidx[cidy, cidx]
            else: 
                raise ToytreeError(f"model type {self.model} not recognized")


    def set_node_arrays_to_tree(self):
        """
        Sets a numpy array as a feature to every node that will store
        the likelihood of each state in each replicate (nuniq, nstates)       

        3-state model: 
                 [0.5, 0.5, 0]
                 [0, 0.5, 0.5]
                      ...
                 /           \
            [1, 1, 0]     [1, 1, 0]
            [0, 0, 1]     [0, 1, 0]
               ...           ...
        """
        self.tree = self.tree.set_node_values(
            "likelihood", 
            default=np.zeros((self.unique.shape[1], self.qidx.shape[0])),
        )
        for nidx in range(self.tree.ntips):
            node = self.tree.idx_dict[nidx]

            # get column index of this tip
            sidx = self.data.index.tolist().index(node.name)

            # get column from unique matching this tip index
            udata = self.unique[sidx, :]
            for istate in self.ints_to_states:
                node.likelihood[:, istate] = (udata == istate).astype(float)


    def node_conditional_likelihoods(self, node):
        """
        Returns the conditional likelihood at a single node given the
        likelihood's of data at its child nodes.
        """
        # get transition probabilities over each branch length
        probmats = {
            0: expm(self.qmatrix * node.children[0].dist),
            1: expm(self.qmatrix * node.children[1].dist),
        }

        nstates = node.likelihood.shape[1]
        anclik = []
        for ancstate in range(nstates):
            # likelihood of child0 observation if anc==ancstate
            prob = (probmats[0][ancstate, :] * node.children[0].likelihood).sum(axis=1)

            prob = (probmats[1][:, 0] * node.children[1].likelihood).sum(axis=1)            

            # TODO...
            # anclik[ancstate] = x

            for endstate in range(nstates):
                for child in range(2):
                    prob = probmats[child]
                    prob[endstate, 0] * node.children[0].likelihood[:, ]

        anc_liks = []
        for childidx in range(2):
            prob = probmats[childidx]
            for sidx in range():

                # prob child==sidx if anc==sidx
                prob[sidx, sidx]

                # get into a notebook for this...

        # likelihood that child 0 observation occurs if anc==0
        print(prob_child0, '0000')
        child0_is0 = (
            prob_child0[0, 0] * node.children[0].likelihood[:, 0] + 
            prob_child0[0, 1] * node.children[0].likelihood[:, 1]
        )

        # likelihood that child 1 observation occurs if anc==0
        child1_is0 = (
            prob_child1[0, 0] * node.children[1].likelihood[:, 0] + 
            prob_child1[0, 1] * node.children[1].likelihood[:, 1]
        )
        anc_lik_0 = child0_is0 * child1_is0

        # likelihood that child 0 observation occurs if anc==1
        child0_is1 = (
            prob_child0[1, 0] * node.children[0].likelihood[:, 0] + 
            prob_child0[1, 1] * node.children[0].likelihood[:, 1]
        )
        child1_is1 = (
            prob_child1[1, 0] * node.children[1].likelihood[:, 0] + 
            prob_child1[1, 1] * node.children[1].likelihood[:, 1]
        )
        anc_lik_1 = child0_is1 * child1_is1

        # set estimated conditional likelihood on this node
        node.likelihood = np.column_stack([anc_lik_0, anc_lik_1])        


    def pruning_algorithm(self):
        """
        Traverse tree from tips to root calculating conditional 
        likelihood at each internal node on the way, and compute final
        conditional likelihood at root based on priors for root state.
        """
        # traverse tree in order **from tips to root**
        # to get conditional likelihood estimate at root.
        for node in self.tree.treenode.traverse("postorder"):
            if not node.is_leaf():               
                self.node_conditional_likelihoods(node)

        # multiply root prior times the conditional likelihood at root
        root = self.tree.treenode
        print(self.prior)
        print(root.likelihood)
        lik = self.prior * root.likelihood
        print(lik)
        lik = lik.sum()
        print(lik)
            # (1. - self.prior_root_is_1) * root.likelihood[:, 0] + 
            # self.prior_root_is_1 * root.likelihood[:, 1]
        # )
        return lik[self.inverse]


    def optimize(self):
        """
        Use maximum likelihood optimization to find the optimal 
        parameters (from .params) to fit the data.

        TODO: max bounds could be set based on tree height. For smaller
        tree heights (e.g., 1) the max should likely be higher. If the 
        estimated parameters is at the max bound we should report a 
        logger.warning(message).
        """  
        estimate = minimize(
            fun=optim_func,
            x0=np.array([self.params[i] for i in self.params]),
            args=(self,),
            method='L-BFGS-B',
            bounds=[(1e-12, 500) for i in self.params],
        )
        self.model_fit = {
            "params": estimate.x,
            "negLogLik": estimate.fun,
            "convergence": estimate.success,
        }
        print(self.model_fit)
        print(self.qmatrix)
        print(-np.log(self.pruning_algorithm()))




def optim_func(params, model):
    """
    Function to optimize. Takes an iterable as the first argument 
    containing the parameters to be estimated (alpha, beta), and the
    BinaryStateModel class instance as the second argument.
    """
    # update qmatrix with input params
    for pidx, param in enumerate(params):
        idxs = np.where(model.qidx == pidx + 1)
        model.qmatrix[idxs] = params[param]
    for idx in range(model.qmatrix.shape[0]):
        rowsum = model.qmatrix[idx].sum()
        model.qmatrix[idx, idx] = -(rowsum - model.qmatrix[idx, idx])        

    # get likelihood of the data given the model parameters
    liks = model.pruning_algorithm()
    return -np.log(liks).sum()



if __name__ == "__main__":

    import toytree
    from toytree.pcm.discrete_markov_model_sim import simulate_discrete_markov_states    

    TREE = toytree.rtree.unittree(25, treeheight=100)
    QMATRIX = [
        [-0.06, 0.05, 0.01], 
        [0.01, -0.02, 0.01],
        [0.01, 0.03, -0.04],
    ]
    DATA = simulate_discrete_markov_states(TREE, QMATRIX, nsims=10)
    print(DATA)

    MOD = DiscreteMarkovModelFit(TREE, data=DATA, model="SYM")
    print(MOD.qidx)
    print(MOD.params)
    print(MOD.unique)
    print(MOD.tree.idx_dict[0].likelihood)
    MOD.optimize()
    # print(MOD.prior)