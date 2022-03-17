#!/usr/bin/env python
"""Maximum likelihood tree inference.

"""
from typing import Tuple, Iterator
from numpy.typing import ArrayLike
import numpy as np
import sympy
import toytree


# BASE_ORDER = list("AGCT")
BASE_ORDER = list("TCAG")  # ziheng Yang

testing_array = np.array([[179,  23,   1,   0],
                          [ 30, 219,   2,   0],
                          [  2,   1, 291,  10],
                          [  0,   0,  21, 169]])


class SubstitutionModel:
    """
    Base class for other substitution model class objects used to
    generate the rate matrix, probability matrix, (log)likelihood expression and function, etc.
    """
    def __init__(self):
        self._q_matrix = sympy.Matrix()
        """: rate matrix assigned to the Model."""
        self._t = sympy.Symbol("t")
        """: the symbolic variable to store time span"""
        self._p_matrices = []
        """: probability matrices in from the intermediate (for class) to the simplified (for calculation) forms."""
        self._pairwise_likelihood_formula = None
        """: the likelihood under multinomial probability"""
        self._pairwise_loglikelihood_formula = None

    def q_matrix(self) -> sympy.Matrix:
        return self._q_matrix

    def p_matrix(self, intermediate_id: int = -1) -> sympy.Matrix:
        if not self._p_matrices:
            self._update_p_matrix()
        return self._p_matrices[intermediate_id]

    def _update_p_matrix(self):
        pass

    def get_pairwise_likelihood_formula(self, logarithm: bool = True) -> sympy.Mul:
        if not self._pairwise_loglikelihood_formula:
            self._update_pairwise_likelihood_formula()
        if logarithm:
            return self._pairwise_loglikelihood_formula
        else:
            return self._pairwise_likelihood_formula

    def _update_pairwise_likelihood_formula(self):
        pass


# TODO use static formula to speed up
class JC69(SubstitutionModel):
    """
    for illustration
    """
    def __init__(self):
        super(JC69, self).__init__()
        self._mu = mu = sympy.Symbol("mu")
        """: the symbolic variable to store instantaneous rate of changing into every other nucleotide"""
        self._d = sympy.Symbol("d")
        """: the symbolic variable to store phylogenetic distance, with d=3*mu*t"""
        self._n = sympy.Symbol("n")
        """: the symbolic variable to store observed total number of sites"""
        self._x = sympy.Symbol("x")
        """: the symbolic variable to store observed number of differences"""
        self._q_matrix = sympy.Matrix([[-3 * mu, mu, mu, mu],
                                       [mu, -3 * mu, mu, mu],
                                       [mu, mu, -3 * mu, mu],
                                       [mu, mu, mu, -3 * mu]])
        """: the rate matrix"""

    def _update_p_matrix(self):
        self._p_matrices.append((self._q_matrix * self._t).exp())
        self._p_matrices.append(self._p_matrices[0].subs(self._mu*self._t, self._d/3))

    def _update_pairwise_likelihood_formula(self):
        p_matrix = self.p_matrix()
        # considering multinomial distribution for all 16 site patterns,
        # the probability is p_0/4 for any constant site pattern
        # the probability is p_1/4 for any different site pattern
        # given that those site patterns apply to all four bases
        self._pairwise_likelihood_formula = \
            (p_matrix[0, 1] / 4) ** self._x * (p_matrix[0, 0] / 4) ** (self._n - self._x)
        self._pairwise_loglikelihood_formula = \
            self._x * sympy.log(p_matrix[0, 1] / 4) + (self._n - self._x) * sympy.log(p_matrix[0, 0] / 4)

    def get_pairwise_loglike_function(self,
                                      change_matrix: ArrayLike = None,
                                      x_obs: int = None,
                                      n_obs: int = None) -> sympy.core.function:
        """
        This function generates a function that takes phylogenetic distance (d) as its parameter
        and output the log-likelihood value.
        If x and n are input, change_matrix will be skipped.

        Parameters
        ----------
        change_matrix: np.array
            observed matrix of changes in the form of
                            species 2
                            --------------
                            A   G   C   T
            species 1 | A  n1  n2  n3  n4
                      | G  n5  n6  n7  n8
                      | C  n9  n10 n11 n12
                      | T  n13 n14 n15 n16
        x_obs : int
            observed number of differences
        n_obs : int
            observed total number of sites
        Returns
        -------
        sympy.core.function
            a function that takes phylogenetic distance (d) as its parameter and output the log-likelihood value
        """
        if (x_obs and n_obs) or change_matrix is not None:
            if not (x_obs and n_obs):
                n_obs = change_matrix.sum()
                x_obs = n_obs - change_matrix.diagonal()
            loglike_formula = self.get_pairwise_likelihood_formula()
            return sympy.lambdify([self._d],
                                  loglike_formula.subs(self._n, n_obs).subs(self._x, x_obs))
        else:
            raise TypeError("Please input change_matrix or x_obs and n_obs!")

    def get_p_matrix_function(self):
        """
        The function used in maximum likelihood tree inference

        Returns
        -------
        sympy.core.function
            a function that takes phylogenetic distance (d: float) and kappa (optional) as its parameter(s),
            and outputs the probability matrix (ArrayLike)
        """
        # much faster than simply using `return sympy.lambdify([self._d], self.p_matrix())`
        p_matrix = self.p_matrix()
        p0_f = sympy.lambdify([self._d], p_matrix[0, 0], modules="numpy")
        p1_f = sympy.lambdify([self._d], p_matrix[0, 1], modules="numpy")

        def _p_matrix_quick_func(_d, _kappa):
            p0, p1, = p0_f(_d, _kappa), p1_f(_d, _kappa)
            return np.array([[p0, p1, p1, p1],
                             [p1, p0, p1, p1],
                             [p1, p1, p0, p1],
                             [p1, p1, p1, p0]])
        return _p_matrix_quick_func


# TODO use static formula to speed up
class K80(SubstitutionModel):
    """
    for illustration
    """
    def __init__(self):
        super(K80, self).__init__()
        self._alpha = alpha = sympy.Symbol("alpha")
        """: the symbolic variable to store the rate of transitions, i.e. A<->G"""
        self._beta = beta = sympy.Symbol("beta")
        """: the symbolic variable to store the rate of transversions, i.e. A, G <-> C, T"""
        self._kappa = sympy.Symbol("kappa")
        """: the symbolic variable to store transition/transversion rate ratio"""
        self._d = sympy.Symbol("d")
        """: the symbolic variable to store phylogenetic distance, with d=(alpha+2*beta)*t"""
        self._n = sympy.Symbol("n")
        """: the symbolic variable to store observed total number of sites"""
        self._s = sympy.Symbol("S")
        """: the symbolic variable to store observed transitions"""
        self._v = sympy.Symbol("V")
        """: the symbolic variable to store observed transversions"""
        self._q_matrix = sympy.Matrix([[-(alpha+2*beta), alpha, beta, beta],
                                       [alpha, -(alpha+2*beta), beta, beta],
                                       [beta, beta, -(alpha+2*beta), alpha],
                                       [beta, beta, alpha, -(alpha+2*beta)]])
        """: the rate matrix"""

    def _update_p_matrix(self):
        # original probability matrix
        self._p_matrices.append((self._q_matrix * self._t).exp())
        # use d and kappa to replace alpha and beta
        beta_trans = self._d/(self._kappa+2)/self._t
        alpha_trans = beta_trans * self._kappa
        self._p_matrices.append(self._p_matrices[0].subs(self._alpha, alpha_trans).subs(self._beta, beta_trans))

    def _update_pairwise_likelihood_formula(self):
        p_matrix = self.p_matrix()
        # considering multinomial distribution for all 16 site patterns, the probabilities are
        # p_0/4 for any constant site pattern
        # p_1/4 for any transitional site pattern
        # p_2/4 for any transversional site pattern, respectively
        self._pairwise_likelihood_formula = (p_matrix[0, 0] / 4) ** (self._n - self._s - self._v) * \
                                            (p_matrix[0, 1]/4) ** self._s * \
                                            (p_matrix[0, 2]/4) ** self._v
        self._pairwise_loglikelihood_formula = (self._n - self._s - self._v) * sympy.log(p_matrix[0, 0] / 4) + \
                                               self._s * sympy.log(p_matrix[0, 1]/4) + \
                                               self._v * sympy.log(p_matrix[0, 2]/4)

    def get_pairwise_loglike_function(self,
                                      change_matrix: ArrayLike = None,
                                      s_obs: int = None,
                                      v_obs: int = None,
                                      n_obs: int = None) -> sympy.core.function:
        """
        This function generates a function that takes phylogenetic distance (d) as its parameter,
        and outputs the log-likelihood value.
        If x and n are input, change_matrix will be skipped.

        Parameters
        ----------
        change_matrix: np.array
            observed matrix of changes in the form of
                            species 2
                            --------------
                            A   G   C   T
            species 1 | A  n1  n2  n3  n4
                      | G  n5  n6  n7  n8
                      | C  n9  n10 n11 n12
                      | T  n13 n14 n15 n16
        s_obs : int
            observed transitional sites
        v_obs : int
            observed transversional sites
        n_obs : int
            observed total number of sites
        Returns
        -------
        sympy.core.function
            a function that takes phylogenetic distance (d) as its parameter and outputs the log-likelihood value
        """
        if (s_obs and v_obs and n_obs) or change_matrix is not None:
            if not (s_obs and v_obs and n_obs):
                n_obs = change_matrix.sum()
                s_obs = change_matrix[0, 1] + change_matrix[1, 0] + change_matrix[2, 3] + change_matrix[3, 2]
                v_obs = n_obs - change_matrix.diagonal().sum() - s_obs
                print(n_obs, s_obs, v_obs)
            loglike_formula = self.get_pairwise_likelihood_formula()
            return sympy.lambdify([self._d, self._kappa],
                                  loglike_formula.subs(self._n, n_obs).subs(self._s, s_obs).subs(self._v, v_obs))
        else:
            raise TypeError("Please input change_matrix, or s_obs, v_obs and n_obs!")

    def get_p_matrix_function(self, kappa: float = None):
        """
        The function used in maximum likelihood tree inference

        Parameters
        ----------
        kappa: float
            transitional sites over transversional sites.
            The resulting function will be ca. 15% faster when kappa is fixed

        Returns
        -------
        sympy.core.function
            a function that takes phylogenetic distance (d: float) and kappa (optional) as its parameter(s),
            and outputs the probability matrix (ArrayLike)
        """
        # three times faster than simply using `return sympy.lambdify([self._d, self._kappa], self.p_matrix())`
        # even slightly faster (ca. 15%) than a straightforward function based on the formula
        p_matrix = self.p_matrix()
        p0_f = sympy.lambdify([self._d], p_matrix[0, 0].subs(self._kappa, kappa), modules="numpy")
        p1_f = sympy.lambdify([self._d], p_matrix[0, 1].subs(self._kappa, kappa), modules="numpy")
        p2_f = sympy.lambdify([self._d], p_matrix[0, 2].subs(self._kappa, kappa), modules="numpy")
        if kappa is not None:
            def _p_matrix_quick_func(_d):
                p0, p1, p2 = p0_f(_d), p1_f(_d), p2_f(_d)
                return np.array([[p0, p1, p2, p2],
                                 [p1, p0, p2, p2],
                                 [p2, p2, p0, p1],
                                 [p2, p2, p1, p0]])
        else:
            def _p_matrix_quick_func(_d, _kappa):
                p0, p1, p2 = p0_f(_d, _kappa), p1_f(_d, _kappa), p2_f(_d, _kappa)
                return np.array([[p0, p1, p2, p2],
                                 [p1, p0, p2, p2],
                                 [p2, p2, p0, p1],
                                 [p2, p2, p1, p0]])
        return _p_matrix_quick_func


def combine_descendent_conditional_probability(descendant_conditional_prob: Iterator[ArrayLike],
                                               prob_matrices: Iterator[ArrayLike],
                                               logarithm: bool=True):
    """Used to calculate the conditional probability of current node
    given its descendant conditional probability list and corresponding transition probability matrix.

    Under non-logarithm mode, for node $i$ with descendent nodes {$j$} and for each base type x, it calculate
    $L_i(x_i)$ = $\product_j \sum_{x_j} p_{{x_i}{x_j}}(t_j)L_j(x_j)$
    the product of the 'transferred conditional probability' from all descendent nodes.
    The 'transferred conditional probability' ($\sum_{x_j} p_{{x_i}{x_j}}(t_j)L_j(x_j)$) here describe
    the sum over conditional probabilities that base type x may accumulate from all base types from a descendent node.

    Parameters
    ----------
    descendant_conditional_prob : Iterator[ArrayLike in the shape of (4,)]
        Input iterator that each time generates the conditional probability of a child.
        Each conditional probability array should be of `shape=(4,)`, e.g. `np.array([0.05, 0.001, 0.04, 0.002])`
    prob_matrices: Iterator[ArrayLike in the shape of (4,4)]
        Input iterator that each time generates the transition probability matrix of a child.
        Each transition probability matrix should be of `shape=(4,4)`,
        e.g. `np.array([[0.8644351 , 0.06591888, 0.03482301, 0.03482301],
                        [0.06591888, 0.8644351 , 0.03482301, 0.03482301],
                        [0.03482301, 0.03482301, 0.8644351 , 0.06591888],
                        [0.03482301, 0.03482301, 0.06591888, 0.8644351 ]])` # K80 model with d=0.15, k=2.
    Returns
    -------
    ArrayLike
        Output the conditional probability of the combined use np.array in the shape of (4,).
    """
    accumulated_prob = (next(descendant_conditional_prob) * next(prob_matrices)).sum(axis=1)
    for child_prob in descendant_conditional_prob:
        this_p_matrix = next(prob_matrices)
        accumulated_prob *= (child_prob * this_p_matrix).sum(axis=1)
    return accumulated_prob


# TODO plot each step
def node_conditional_probability(node: toytree.Node,
                                 p_matrix_func: sympy.core.function = K80().get_p_matrix_function(kappa=2.),
                                 ) -> Tuple[float, float, float, float]:
    """
    more description
    """
    if node.is_leaf():
        return node.conditional_prob
    else:
        child_cd_prob_generator = (node_conditional_probability(child_node) for child_node in node.children)
        prob_matrix_generator = (p_matrix_func(child_node.dist) for child_node in node.children)
        node.conditional_prob = combine_descendent_conditional_probability(
            descendant_conditional_prob=child_cd_prob_generator,
            prob_matrices=prob_matrix_generator)
        return node.conditional_prob


# works! to be continued
def get_tree_likelihood():
    tree = toytree.tree("(((sp-A:0.2,sp-B:0.2):0.1,sp-C:0.2):0.1,(sp-D:0.2,sp-E:0.2):0.1);")
    observed_data = {"sp-A": "T", "sp-B": "C", "sp-C": "A", "sp-D": "C", "sp-E": "C"}
    for sp_name, sp_state in observed_data.items():
        sp_node = tree.get_nodes(sp_name)[0]  # do we have better function to do this in toytree?
        sp_node.conditional_prob = np.array(list(BASE_ORDER)) == sp_state
    root_prob = node_conditional_probability(tree.treenode)


