#!/usr/bin/env python

"""Maximum likelihood tree inference.

A didactic version ...
"""

from typing import Tuple, Iterator, Dict
from numpy.typing import ArrayLike
import numpy as np
import toytree

# not yet part of core toytree install
try:
    import sympy
except ImportError:
    pass

# pylint: disable=invalid-name

# BASE_ORDER = list("AGCT")
BASE_ORDER = list("TCAG")  # ziheng Yang


# TODO: this could be an AbstractBaseClass
class SubstitutionModel:
    """Base class for molecular substitution models.

    SubstitutionModel class objects are used to generate the rate 
    matrix and probability matrix, as well as the (log)likelihood 
    expression and function using sympy.
    """
    def __init__(self):
        self._PI = 0.25, 0.25, 0.25, 0.25
        """: default equilibrium frequencies of nucleotides for simple models"""
        self._q_matrix = sympy.Matrix()
        """: rate matrix assigned to the Model."""
        self._t = sympy.Symbol("t")
        """: the symbolic variable to express time span."""
        self._p_matrices = []
        """: probability matrices in from the intermediate (for class) to the simplified (for calculation) forms."""
        self._pairwise_likelihood_formula = None
        """: the likelihood under multinomial probability."""
        self._pairwise_loglikelihood_formula = None

    def q_matrix(self) -> sympy.Matrix:
        """Return the rate matrix (Q) given the model parameters."""
        return self._q_matrix

    def p_matrix(self, intermediate_id: int = -1) -> sympy.Matrix:
        """Return the transition matrix (P) given the model parameters.
        
        Parameters
        ----------
        intermediate_id: int
            ...
        """
        if not self._p_matrices:
            self._update_p_matrix()
        return self._p_matrices[intermediate_id]

    def _update_p_matrix(self):
        """Child classes have a proper function here."""        
        pass

    def get_pairwise_likelihood_formula(self, logarithm: bool = True) -> sympy.Mul:
        """Return the likelihood formula for the substitution model.

        This function uses sympy ...
        """
        if not self._pairwise_loglikelihood_formula:
            self._update_pairwise_likelihood_formula()
        if logarithm:
            return self._pairwise_loglikelihood_formula
        else:
            return self._pairwise_likelihood_formula

    def _update_pairwise_likelihood_formula(self):
        """Child classes have a proper function here."""
        pass


class JC69(SubstitutionModel):
    """
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
            (p_matrix[0, 1] * self._PI[1]) ** self._x * \
            (p_matrix[0, 0] * self._PI[0]) ** (self._n - self._x)
        self._pairwise_loglikelihood_formula = \
            self._x * sympy.log(p_matrix[0, 1] * self._PI[1]) + \
            (self._n - self._x) * sympy.log(p_matrix[0, 0] * self._PI[0])

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
            e.g. example from Z.H. Yang (2014)
            np.array([[179,  23,   1,   0],
                      [ 30, 219,   2,   0],
                      [  2,   1, 291,  10],
                      [  0,   0,  21, 169]])
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
                                  loglike_formula.evalf(subs={self._n: n_obs, self._x: x_obs}))
        else:
            raise TypeError("Please input change_matrix or x_obs and n_obs!")

    def get_p_matrix_function(self):
        """
        The function used in maximum likelihood tree inference

        Returns
        -------
        sympy.core.function
            a function that takes phylogenetic distance (d: float) and kappa_ls (optional) as its parameter(s),
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


class K80(SubstitutionModel):
    """
    """
    def __init__(self):
        super(K80, self).__init__()
        self._alpha = alpha = sympy.Symbol("alpha")
        """: the symbolic variable to store the rate of transitions, i.e. A <-> G, C <-> T"""
        self._beta = beta = sympy.Symbol("beta")
        """: the symbolic variable to store the rate of transversions, i.e. A, G <-> C, T"""
        self._kappa = sympy.Symbol("kappa_ls")
        """: the symbolic variable to store transition/transversion rate ratio, i.e. alpha/beta"""
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
        self._mu = alpha+2*beta
        """: the average substitution rate"""

    def _update_p_matrix(self):
        # original probability matrix
        self._p_matrices.append((self._q_matrix * self._t).exp())
        ###################################################
        # --- use d and kappa_ls to replace alpha and beta ---
        # 1. get the expression of alpha and beta using phylogenetic distance, timespan, kappa_ls
        solution = sympy.solve(
            [self._d - (self._alpha+2*self._beta) * self._t,
             self._kappa - self._alpha / self._beta],
            [self._alpha,
             self._beta])
        # 2. replace alpha and beta
        self._p_matrices.append(sympy.simplify(self._p_matrices[0].
                                               subs(self._alpha, solution[self._alpha]).
                                               subs(self._beta, solution[self._beta])))

    # def _update_p_matrix0(self):
    #     # original probability matrix
    #     self._p_matrices.append((self._q_matrix * self._t).exp())
    #     # use d and kappa_ls to replace alpha and beta
    #     beta_trans = self._d/(self._kappa+2)/self._t
    #     alpha_trans = beta_trans * self._kappa
    #     self._p_matrices.append(self._p_matrices[0].subs(self._alpha, alpha_trans).subs(self._beta, beta_trans))

    def _update_pairwise_likelihood_formula(self):
        p_matrix = self.p_matrix()
        # considering multinomial distribution for all 16 site patterns, the probabilities are
        # p_0/4 for any constant site pattern
        # p_1/4 for any transitional site pattern
        # p_2/4 for any transversional site pattern, respectively
        self._pairwise_likelihood_formula = \
            (p_matrix[0, 0] * self._PI[0]) ** (self._n - self._s - self._v) * \
            (p_matrix[0, 1] * self._PI[1]) ** self._s * \
            (p_matrix[0, 2] * self._PI[2]) ** self._v
        self._pairwise_loglikelihood_formula = \
            (self._n - self._s - self._v) * sympy.log(p_matrix[0, 0] * self._PI[0]) + \
            self._s * sympy.log(p_matrix[0, 1] * self._PI[0]) + \
            self._v * sympy.log(p_matrix[0, 2] * self._PI[0])

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
            e.g. example from Z.H. Yang (2014)
            np.array([[179,  23,   1,   0],
                      [ 30, 219,   2,   0],
                      [  2,   1, 291,  10],
                      [  0,   0,  21, 169]])

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
            loglike_formula = self.get_pairwise_likelihood_formula()
            return sympy.lambdify([self._d, self._kappa],
                                  loglike_formula.evalf(subs={self._n: n_obs, self._s: s_obs, self._v: v_obs}))
        else:
            raise TypeError("Please input change_matrix, or s_obs, v_obs and n_obs!")

    def get_p_matrix_function(self, kappa: float = None):
        """
        The function used in maximum likelihood tree inference

        Parameters
        ----------
        kappa: float
            transitional sites over transversional sites.
            The resulting function will be ca. 15% faster when kappa_ls is fixed

        Returns
        -------
        sympy.core.function
            a function that takes phylogenetic distance (d: float) and kappa_ls (optional) as its parameter(s),
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


class TN93(SubstitutionModel):
    """
    """
    def __init__(self):
        super(TN93, self).__init__()
        self._PI = pi_1, pi_2, pi_3, pi_4 = sympy.symbols(["pi_" + base_type for base_type in BASE_ORDER])
        """: using symbolic variables to rewrite the equilibrium frequencies of nucleotides"""
        self._alpha_1 = alpha_1 = sympy.Symbol("alpha_1")
        """: the symbolic variable to store the rate of transitions, A<->G"""
        self._alpha_2 = alpha_2 = sympy.Symbol("alpha_2")
        """: the symbolic variable to store the rate of transitions, T<->C"""
        self._beta = beta = sympy.Symbol("beta")
        """: the symbolic variable to store the rate of transversions, i.e. A, G <-> C, T"""
        self._kappa_1 = sympy.Symbol("kappa_1")
        """: the symbolic variable to store alpha1/beta"""
        self._kappa_2 = sympy.Symbol("kappa_2")
        """: the symbolic variable to store alpha2/beta"""
        self._d = sympy.Symbol("d")
        """: the symbolic variable to store phylogenetic distance, with d=(alpha+2*beta)*t"""
        self._change_mtx = sympy.Matrix([["O_" + from_b + to_b for from_b in BASE_ORDER] for to_b in BASE_ORDER])
        """: the symbolic matrix to store observed change of matrix"""
        self._q_matrix = sympy.Matrix([[-(pi_2*alpha_1+pi_3*beta+pi_4*beta), pi_1*alpha_1, pi_1*beta, pi_1*beta],
                                       [pi_2*alpha_1, -(pi_1*alpha_1+pi_3*beta+pi_4*beta), pi_2*beta, pi_2*beta],
                                       [pi_3*beta, pi_3*beta, -(pi_1*beta+pi_2*beta+pi_4*alpha_2), pi_3*alpha_2],
                                       [pi_4*beta, pi_4*beta, pi_4*alpha_2, -(pi_1*beta+pi_2*beta+pi_3*alpha_2)]])
        # not the following form
        # self._q_matrix = sympy.Matrix([[-alpha_1*pi_2 - beta*pi_3 - beta*pi_4, alpha_1*pi_2,  beta*pi_3, beta*pi_4],
        #                                [alpha_1*pi_1, -alpha_1*pi_1 - beta*pi_3 - beta*pi_4,  beta*pi_3, beta*pi_4],
        #                                [beta*pi_1, beta*pi_2, -alpha_2*pi_4 - beta*pi_2 - beta*pi_1, alpha_2*pi_4],
        #                                [beta*pi_1, beta*pi_2, alpha_2*pi_3, -alpha_2*pi_3 - beta*pi_2 - beta*pi_1]])

        """: the rate matrix"""
        self._express = None
        """: alpha/beta -> f(d,t,kappa_ls)"""
        self._p_matrix_w = None
        self._log_p_matrix_w = None
        """: tmp variables"""
        self._mu = -(self._q_matrix.diagonal() * sympy.Matrix(self._PI))[0]
        """: substitution rate"""

    def _update_express(self):
        self._express = sympy.solve(
            [self._d - self._mu * self._t,
             self._kappa_1 - self._alpha_1 / self._beta,
             self._kappa_2 - self._alpha_2 / self._beta],
            [self._alpha_1,
             self._alpha_2,
             self._beta])

    def _update_p_matrix(self):
        # original probability matrix
        self._p_matrices.append((self._q_matrix * self._t).exp())
        ###################################################
        # --- use d and kappa_ls to replace alpha and beta ---
        # 1. get the expression of alpha_1, alpha_2, beta using phylogenetic distance, timespan, kappa_1, kappa_2
        if not self._express:
            self._update_express()

        # 2. replace alpha_1, alpha_2, beta
        self._p_matrices.append(sympy.simplify(self._p_matrices[0].
                                               subs(self._alpha_1, self._express[self._alpha_1]).
                                               subs(self._alpha_2, self._express[self._alpha_2]).
                                               subs(self._beta, self._express[self._beta])))

    def _update_pairwise_likelihood_formula(self):
        """considering multinomial distribution for all 16 site patterns"""
        # np.array and sympy.Matrix has different multiplication scheme
        self._p_matrix_w = np.array(self.p_matrix()) * np.array(self._PI)
        self._log_p_matrix_w = np.array(sympy.simplify(sympy.Matrix(self._p_matrix_w).applyfunc(sympy.log)))
        self._pairwise_likelihood_formula = self._p_matrix_w ** np.array(self._change_mtx)
        self._pairwise_loglikelihood_formula = np.array(self._change_mtx) * self._log_p_matrix_w

    def get_pairwise_loglike_function(self, change_matrix: ArrayLike) -> sympy.core.function:
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
            e.g. example from Z.H. Yang (2014)
            np.array([[179,  23,   1,   0],
                      [ 30, 219,   2,   0],
                      [  2,   1, 291,  10],
                      [  0,   0,  21, 169]])

        Returns
        -------
        sympy.core.function
            a function that takes phylogenetic distance (d) as its parameter and outputs the log-likelihood value
        """
        if self._p_matrix_w is None:
            self._update_pairwise_likelihood_formula()
        # here we did not use the self._pairwise_likelihood_formula (directly like JC69 and K80)
        # because the generated function will be slow if two many separate parameters were used
        # instead, we use the self._log_p_matrix_w and the array of change_matrix to generate the formula
        like_formula = (self._log_p_matrix_w * change_matrix).sum()
        return sympy.lambdify([self._d, self._kappa_1, self._kappa_2] + self._PI, like_formula)

    # TODO use pruning algorithm to speed up (maybe)
    def get_p_matrix_function(self,
                              kappa_ls: tuple[float, float] = None,
                              pi_ls: tuple[float, float, float, float] = None):
        """
        The function used in maximum likelihood tree inference.
        The resulting function will be faster when more parameters are fixed.

        Parameters
        ----------
        kappa_ls: tuple[float, float]
            To which kappa_1 (alpha_1/beta) and kappa_2 (alpha_2/beta) are fixed.
        pi_ls: tuple[float, float, float, float]
            To which equilibrium frequencies of nucleotides are fixed.

        Returns
        -------
        sympy.core.function
            a function that takes phylogenetic distance (d: float) and kappa (optional) as its parameter(s),
            and outputs the probability matrix (ArrayLike)
        """
        # much faster than simply using `return sympy.lambdify([self._d, self._kappa], self.p_matrix())`
        p_matrix = self.p_matrix()
        if kappa_ls is not None and pi_ls is not None:
            # fastest
            p_matrix = p_matrix.evalf(
                subs={self._kappa_1: kappa_ls[0],self._kappa_2: kappa_ls[1]} |
                     {self._PI[go_b]: pi_val for go_b, pi_val in enumerate(pi_ls)})
            return sympy.lambdify([self._d], p_matrix)
        elif kappa_ls:
            p_matrix = p_matrix.evalf(subs={self._kappa_1: kappa_ls[0], self._kappa_2: kappa_ls[1]})
            return sympy.lambdify([self._d] + self._PI, p_matrix)
        elif pi_ls:
            p_matrix = p_matrix.evalf(subs={self._PI[go_b]: pi_val for go_b, pi_val in enumerate(pi_ls)})
            return sympy.lambdify([self._d, self._kappa_1, self._kappa_2], p_matrix)
        else:
            return sympy.lambdify([self._d, self._kappa_1, self._kappa_2] + self._PI, p_matrix)


def combine_descendent_conditional_probability(descendant_conditional_prob: Iterator[ArrayLike],
                                               prob_matrices: Iterator[ArrayLike]):
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
        This can be generated using the function of `get_p_matrix_function` under each substitution model objects.
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
def node_conditional_probability(
    node: toytree.Node,
    p_matrix_func: sympy.core.function = K80().get_p_matrix_function(kappa=2.),
    ) -> Tuple[float, float, float, float]:
    """Return the conditional probability of a Node.

    This is a recursive function that can be called on the root Node
    of a tree to get the conditional likelihood of the whole tree. It
    calls itself on all children of each internal Node until it reaches
    the tips of the tree.
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
def get_tree_likelihood(tree: toytree.ToyTree, data: Dict) -> float:
    """Return the likelihood of observing data given a tree.

    """
    # set observed data as features of tip Nodes
    for nidx in range(tree.ntips):
        node = tree[nidx]
        assert node.name in data, f"data must include all tips in the tree. Missing={node.name}"
        state = data[node.name]
        node.conditional_prob = np.array(BASE_ORDER) == state

    # infer internal node conditional probs from tip states
    root_prob = node_conditional_probability(tree.treenode)
    return root_prob



if __name__ == "__main__":

    TESTING_ARRAY = np.array([[179,  23,   1,   0],
                              [ 30, 219,   2,   0],
                              [  2,   1, 291,  10],
                              [  0,   0,  21, 169]])
    TREE = toytree.tree("(((sp-A:0.2,sp-B:0.2):0.1,sp-C:0.2):0.1,(sp-D:0.2,sp-E:0.2):0.1);")
    DATA = {"sp-A": "T", "sp-B": "C", "sp-C": "A", "sp-D": "C", "sp-E": "C"}

    LIK = get_tree_likelihood(TREE, DATA)
    print(LIK)
    TREE.treenode.draw_ascii()
