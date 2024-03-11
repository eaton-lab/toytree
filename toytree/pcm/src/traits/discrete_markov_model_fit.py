#!/usr/bin/env python

"""Fit a discrete Markov model to data using Maximum Likelihood.

Model fit estimates model parameters and ancestral states.

Example
-------
>>> toytree.pcm.fit_discrete_markov_data(
        nstates=3, model="ER", 
        rates=None,               # will be estimated
        state_frequencies=None,   # will be estimated
    )
"""

from typing import Optional, Union, List, TypeVar
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import expm
from toytree.utils import ToytreeError
from toytree.pcm.src.discrete_markov_model_sim import MarkovModel


ToyTree = TypeVar("ToyTree")


@dataclass
class FitMarkovModelResult:
    """Result object of a Markov model fit by Maximum Likelihood."""
    nstates: int
    model: str
    transition_matrix: np.ndarray
    state_frequencies: np.ndarray
    data: pd.DataFrame = None
    log_likelihood: float = None
    fixed_rates: np.ndarray = None
    nparams: int = None


@dataclass
class FitMarkovModelBase:
    """Fit a Markov model to discrete data using Maximum Likelihood.

    This uses Felsenstein's pruning algorith to recursively traverse
    a tree to compute conditional likelihoods of each state at each
    Node, and returns the total likelihood as the sum of 
    log-likelihoods of the states at the root.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree instance (usually ultrametric).
    data: pandas.Series or pandas.DataFrame
        If the index is numeric it is interpreted as node idx labels,
        if not, then as string tip labels. Column names are not used,
        and if multiple columns present they are treated as replicate 
        observations of the same trait. Data is treated as categorical
        (0-nstates). 
    nstates: int
        The number of discrete states in the Markov model.
    model: str
        The Markov model type ("ER", "SYM", "ARD") will determine the
        number of parameters to be inferred. The fixed_rates arg can
        be used to fix parameters, which will then not be inferred.
    fixed_rates: Optional[np.ndarray]
        An array of the dimension (nstates,nstates) with fixed rate
        parameters (not to be estimated) in some or all off-diagonal
        cells, or np.nan for parameters that should be estimated. 
        Fixing parameters decrease the number that needs to be 
        estimated. Fixed rates must match allowed values given the 
        model type (e.g., ER must fix all to a single rate b/c only
        on rate is allowed in this model, and SYM model rates must be
        symmetric). Values on the diagonal are ignored.
    fixed_state_frequencies: Optional[np.ndarray]
        An array of dimension nstates with fixed values for the state
        frequencies... how does this relate to root prior...?

    Examples
    --------
    >>> #Fit a 2-state character observed for all tips in the tree.
    >>> tree = ...
    >>> data = tree.pcm.simulate_discrete_data(3, "ER", tips_only=True)
    >>> fit = tree.pcm.fit_discrete_data(data, 3, "ER")
    >>>
    >>> #Fit a 3-state SYM model with observations for some internal nodes.
    >>> data = tree.pcm.simulate_discrete_data(3, "ER", tips_only=True)
    >>> fit = tree.pcm.fit_discrete_data(data, 3, "ER")
    >>>
    >>> #Fit a 2-state ARD model with some rates fixed:
    >>> data = tree.pcm.simulate_discrete_data(2, "ARD",
    >>>    relative_rates=[[0, 2], [1, 0]])
    >>> fixed = np.array([[0, 2],[np.nan, 0]])
    >>> fit = tree.pcm.fit_discrete_data(data, 2, "ARD", fixed_rates=fixed)
    >>>
    >>> #Fit a GTR model to DNA-like 4-state data
    >>> true_rates = 1e-8 * np.array([
    >>>     [0, 1, 2, 2],
    >>>     [1, 0, 2, 2],
    >>>     [2, 2, 0, 1],
    >>>     [2, 2, 1, 0],
    >>> ])
    >>> true_freqs = [0.2,0.3,0.2,0.3]
    >>> data = tree.pcm.simulate_discrete_data(4, "SYM",
    >>>    relative_rates=true_rates, 
    >>>    state_frequencies=true_freqs,
    >>>    rate=1e-8, 
    >>>    nreplicates=500, 
    >>>    tips_only=True,
    >>> )
    >>> fit = tree.pcm.fit_discrete_data(data, 4, "SYM")

    References
    ----------
    - Yang.
    - Paradis et al. (2004).
    - Harmon book.
    """
    tree: ToyTree
    data: Union[pd.Series, pd.DataFrame]
    nstates: int
    model: str

    root_prior: Optional[np.ndarray]=None   
    fixed_rates: Optional[np.ndarray]=None
    fixed_state_frequencies: Optional[np.ndarray]=None

    nparams_fixed: int=field(init=False)
    nparams_free: int=field(init=False)
    rate_matrix: np.ndarray=field(init=False)
    state_frequencies: np.ndarray=field(init=False)

    def __post_init__(self):
        self.model = self.model.upper()
        assert self.model in ("ER", "SYM", "ARD"), (
            "model must be one of 'ER', 'SYM', 'ARD'")

        # Set parameters to be inferred as np.nan, and fixed params
        # to the fixed value, and fill nparams_ counters.
        self._check_freqs()
        self._check_rates_and_nparams()

        # ...
        # self._check_data_with_tree()

        # self._check_rates()
        # self.qmatrix = self._get_qmatrix()

    def _check_freqs(self):
        """Check stationary frequencies given model and nstates.

        Entered values are checked for correct size and that they 
        sum to one. If no values are entered then a uniform frequency
        of the correct size is sampled to represent the best starting
        guess for root state.

        Sets values for array of shape to nstates - 1, e.g., 
        infer states for k=3: [np.nan, np.nan]
        one fixed state for k=3: [0.5, np.nan]
        """
        freqs = self.state_frequencies
        if freqs is None:
            freqs = np.repeat(1.0 / self.nstates, self.nstates)
        else:
            freqs = np.array(freqs)
            if self.model in ("SYM", "ARD"):
                assert freqs.size == self.nstates, (
                    f"states_frequencies should be len={self.nstates}.")
            else:
                fixed = np.repeat(1.0 / self.nstates, self.nstates)
                assert np.allclose(freqs, fixed), (
                    f"ER model with nstates={self.nstates} has fixed state "
                    f"frequences: {fixed}. See SYM or ARD models.")
                freqs = fixed
        assert np.allclose(sum(freqs), 1.0), (
            f"state_frequencies must sum to 1. You entered: {freqs}")
        self.state_frequencies = freqs

    def _check_rates_and_nparams(self):
        """Get nparams based on model, nstates, and fixed params.

        Checks that fixed params is valid given the other args. For
        example, you can fix all parameters in which case no ML
        optimization occurs and the loglik is simply calculated.

        Number of parameters (k=nstates): The "ER" model always has 1 
        parameter; the "SYM" model has ((k * (k-1)) / 2) + (k - 1) 
        parameters; the "ARD" is (k * (k-1)) + (k - 1). The effect of
        fixing a parameter is -2k for SYM, or -k for others.
        """
        rates = np.ones((self.nstates, self.nstates))
        assert rates.shape == self.fixed_rates, (
            "fixed_rates array must be dimension (nstates, nstates)")
        np.fill_diagonal(rates, 0)
        np.fill_diagonal(self.fixed_rates, 0)

        # fixed rates must by symmetric for ER and SYM
        if self.model in ("ER", "SYM"):
            assert np.allclose(self.fixed_rates, self.fixed_rates.T, rtol=1e-5, atol=1e-8), (
                "rates must be symmetric in ER and SYM models. See ARD model.")

        k = self.nstates
        mask = np.invert(np.eye(self.nstates, dtype=bool))
        fixed = self.fixed_rates[mask]
        if self.model == "ER":
            self.nparams_fixed = fixed[~np.isnan(fixed)].size
            self.nparams_free = 1 - self.nparams_fixed
        elif self.model == "SYM":
            self.nparams_free = (k * (k - 1)) / 2
            self.nparams_fixed = 2 * fixed[~np.isnan(fixed)].size
            self.nparams_free = 1 - self.nparams_fixed
        else:
            self.nparams_fixed = fixed[~np.isnan(fixed)].size
            self.nparams_free = (k * (k - 1)) - self.nparams_fixed

    def _check_data_with_tree(self):
        """TODO... """


class FitMarkovModel(FitMarkovModelBase):
    """...

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10, seed=123)
    >>> data = toytree.pcm.simulate_discrete_data(tree, 3, "ER")
    >>>
    >>> # Fit an ER model to the data
    >>> fit = toytree.pcm.fit_discrete_markov_model(tree, data, "ER")
    >>> print(fit.log_likelihood, fit.data)
    """
    def __init__(
        self,
        log_likelihood: float,
        data: pd.DataFrame,
        ):
        pass

    def _check_data_with_tree(self):
        """Data index must be a set length and type.

        Data will be converted to a DataFrame with index=range(nnodes)
        and discrete data as floats 0-nstates or np.nan for missing.
        """
        assert isinstance(self.data, pd.DataFrame), "data must be a DataFrame"
        # if data index is strings then convert to node idxs

        assert set(self.data.index) == set(self.tree.get_tip_labels()), (
            "the index of data must have the same tip names as the input tree")



class DiscreteMarkovModelFit:
    """Fit parameters of an n-state discrete Markov model using 
    maximum likelihood.

    Uses scipy to estimate transition rate parameters under one of
    several supported models ("ER", "SYM", ARD").

    Parameters
    ----------
    tree: ToyTree
        A toytree object with ultrametric branch lengths.
    data: pd.DataFrame
        A DataFrame with tip names as the index, and categorical data 
        values (e.g., int, str, etc.) assigned to every tip in the tree.
        The column names are not used. All columns in the DataFrame are
        analyzed as replicate observations.
    model: str
        ...

    Examples
    --------
    Simulate discrete data on a tree.
    >>> tree = toytree.rtree.unittree(ntips=10, treeheight=10)
    >>> data = tree.pcm.simulate_discrete_data(tree, 3, "ER", rate=0.5)
    
    Fit Markov model to discrete data.
    >>> fit = tree.pcm.fit_discrete_markov_model(tree, data, 3, "ER")
    >>> print(fit.log_likelihood, fit.data)

    See also
    --------
    :func:`toytree.pcm.simulate_discrete_markov_data`

    References
    ----------
    https://github.com/rcohen/hogtie
    """
    def __init__(
        self, 
        tree: 'toytree.ToyTree',
        data: pd.DataFrame,
        model: str,
        prior: Optional[np.ndarray]=None,
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
        value = np.zeros((self.unique.shape[1], self.qidx.shape[0])),
        self.tree = self.tree.set_node_data("likelihood", default=value)
        for nidx in range(self.tree.ntips):
            node = self.tree[nidx]

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
    """Function to optimize for discrete Markov Model. 

    Takes an iterable as the first argument 
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

    TREE = toytree.rtree.unittree(5, treeheight=1)
    print(toytree.pcm.get_markov_model(3, "ER", rate=1).transition_matrix)
    DATA = toytree.pcm.simulate_discrete_data(TREE, 3, "ER", rate=1)
    print(DATA)

    fit = FitMarkovModelBase(TREE, DATA, 3, "ER")
    print(fit)


    # print(TREE.ntips, len(TREE.get_tip_labels()))
    # DATA = DATA[:TREE.ntips]
    # DATA.index = TREE.get_tip_labels()
    # print(DATA)

    # MOD = DiscreteMarkovModelFit(TREE, data=DATA, model="SYM")
    # print(MOD.qidx)
    # print(MOD.params)
    # print(MOD.unique)
    # print(MOD.tree[0].likelihood)
    # MOD.optimize()
    # # print(MOD.prior)
