#!/usr/bin/env python

"""Maximum likelihood tree inference.

A didactic version with visualizations for learning ML. Not 
optimized for speed.
"""

from typing import Iterator, Callable, Generator, List

from abc import ABC, abstractmethod

from loguru import logger
from numpy.typing import ArrayLike
import numpy as np
import toyplot
import toytree

logger = logger.bind(name="toytree")

# not yet part of core toytree install
try:
    import sympy
except ImportError:
    # logger.warning("sympy is not installed.")
    pass

# pylint: disable=invalid-name

# BASE_ORDER = list("AGCT")
BASE_ORDER = list("TCAG")  # ziheng Yang
BASE_COLOR_SCHEME = ["blue", "green", "orange", "purple"]
AX0_x_width = 0.056  # 66
AX1_x_width = 3.6
AX1_y_width = 15
AX1_y_width_m = 1.3


class SubstitutionModel(ABC):
    """AbstractBaseClass for molecular substitution models.

    SubstitutionModel class objects are used to generate the rate 
    matrix and transition probability matrix, as well as the 
    (log)likelihood expression and function using sympy.
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

    @property
    def q_matrix(self) -> sympy.Matrix:
        """Return the rate matrix (Q) given the model parameters."""
        return self._q_matrix

    @q_matrix.setter
    def q_matrix(self, value: sympy.Matrix) -> None:
        """Set a value to the q_matrix property attribute."""
        self._q_matrix = value

    def p_matrix(self, intermediate_id: int = -1) -> sympy.Matrix:
        """Return the transition probability matrix (P) given model parameters.
        
        Parameters
        ----------
        intermediate_id: int
            The values at intermediate steps can be returned and viewed
            for didactic purposes, if specified here.
        """
        if not self._p_matrices:
            self._update_p_matrix()
        return self._p_matrices[intermediate_id]

    def get_pairwise_likelihood_formula(self, logarithm: bool = True) -> sympy.Mul:
        """Return the likelihood formula for the substitution model.

        This function uses sympy ...
        """
        if not self._pairwise_loglikelihood_formula:
            self._update_pairwise_likelihood_formula()
        if logarithm:
            return self._pairwise_loglikelihood_formula
        return self._pairwise_likelihood_formula

    @abstractmethod
    def _update_p_matrix(self):
        """Child classes have a proper function here."""        

    @abstractmethod
    def _update_pairwise_likelihood_formula(self):
        """Child classes have a proper function here."""

    @abstractmethod
    def get_p_matrix_function(self):
        """Return a function to get P matrix given Q and d."""

    @abstractmethod
    def get_pairwise_loglike_function(self, *args):
        """Return a function to return likelihood given a distance."""


class JC69(SubstitutionModel):
    """Jukes-Cantor substitution Model."""
    def __init__(self):
        # init parent class
        super().__init__()

        # add new attributes of this SubstitutionModel child class
        self._mu = mu = sympy.Symbol("mu")
        """: symbolic variable for instantaneous rate of change to any base"""
        self._d = sympy.Symbol("d")
        """: symbolic variable for phylogenetic distance, with d=3*mu*t"""
        self._n = sympy.Symbol("n")
        """: symbolic variable for observed total number of sites"""
        self._x = sympy.Symbol("x")
        """: symbolic variable for observed number of differences"""
        self._q_matrix = sympy.Matrix([[-3 * mu, mu, mu, mu],
                                       [mu, -3 * mu, mu, mu],
                                       [mu, mu, -3 * mu, mu],
                                       [mu, mu, mu, -3 * mu]])
        """: the rate matrix (Q)"""

    def _update_p_matrix(self):
        """Append P matrix intermediates for didactic purposes."""
        self._p_matrices.append((self._q_matrix * self._t).exp())
        self._p_matrices.append(self._p_matrices[0].subs(self._mu*self._t, self._d/3))

    def _update_pairwise_likelihood_formula(self):
        """Sets function to attribute `._pairwise_(log)likelihood_formula.

        Considering multinomial distribution for all 16 site patterns,
        the probability is p_0/4 for any constant site pattern
        the probability is p_1/4 for any different site pattern
        given that those site patterns apply to all four bases
        """        
        p_matrix = self.p_matrix()
        self._pairwise_likelihood_formula = \
            (p_matrix[0, 1] * self._PI[1]) ** self._x * \
            (p_matrix[0, 0] * self._PI[0]) ** (self._n - self._x)
        self._pairwise_loglikelihood_formula = \
            self._x * sympy.log(p_matrix[0, 1] * self._PI[1]) + \
            (self._n - self._x) * sympy.log(p_matrix[0, 0] * self._PI[0])

    def get_pairwise_loglike_function(
        self,
        change_matrix: ArrayLike = None,
        x_obs: int = None,
        n_obs: int = None,
        ) -> sympy.core.function:
        """Return a function to return likelihood given a distance.

        Generates a function that takes phylogenetic distance (d) as 
        its parameter and returns the (log?)-likelihood value. If x
        and n are input, the change_matrix will be skipped.

        Parameters
        ----------
        change_matrix: np.array
            observed matrix of changes in the form of:
            >>>                 species 2
            >>>                 --------------
            >>>                 A   G   C   T
            >>> species 1 | A  n1  n2  n3  n4
            >>>           | G  n5  n6  n7  n8
            >>>           | C  n9  n10 n11 n12
            >>>           | T  n13 n14 n15 n16
            >>>
            >>> e.g. example from Z.H. Yang (2014)
            >>> np.array([[179,  23,   1,   0],
            >>>           [ 30, 219,   2,   0],
            >>>           [  2,   1, 291,  10],
            >>>           [  0,   0,  21, 169]])
        x_obs : int
            observed number of differences
        n_obs : int
            observed total number of sites

        Returns
        -------
        sympy.core.function
            a function that takes phylogenetic distance (d) as its 
            parameter and returns a log-likelihood float value.
        """
        if (x_obs and n_obs) or change_matrix is not None:
            if not (x_obs and n_obs):
                n_obs = change_matrix.sum()
                x_obs = n_obs - change_matrix.diagonal()
            loglike_formula = self.get_pairwise_likelihood_formula(logarithm=True)
            return sympy.lambdify(
                [self._d],
                loglike_formula.evalf(subs={self._n: n_obs, self._x: x_obs})
            )
        raise TypeError("Please input change_matrix or x_obs and n_obs!")

    def get_p_matrix_function(self) -> Callable:
        """Return a function to calculate transition probability matrix
        for a given distance (d), used to calculate likelihood.

        Note
        ----
        This is much faster than simply using 
        `return sympy.lambdify([self._d], self.p_matrix())`

        Returns
        -------
        sympy.core.function
            a function that takes phylogenetic distance (d: float) and
            kappa_ls (optional) as its parameter(s), and outputs the 
            probability matrix (ArrayLike)
        """
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
    """Kimura 1980 Substitution Model.

    This model has separate rates for transitions (alpha) and 
    tranversions (beta), specified by the parameters kappa=alpha/beta.
    """
    def __init__(self):
        super().__init__()
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
        """Append P matrix intermediates for didactic purposes."""        
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
        self._p_matrices.append(
            sympy.simplify(
                self._p_matrices[0].
                subs(self._alpha, solution[self._alpha]).
                subs(self._beta, solution[self._beta])
            )
        )


    def _update_pairwise_likelihood_formula(self):
        """...

        # considering multinomial distribution for all 16 site patterns, the probabilities are
        # p_0/4 for any constant site pattern
        # p_1/4 for any transitional site pattern
        # p_2/4 for any transversional site pattern, respectively
        """
        p_matrix = self.p_matrix()
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

    def get_p_matrix_function(self, kappa: float = 2.):
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
    """Tamura and Nei (1993) Substitution Model.

    Combines different equilibrium frequency distributions with unequal
    transition (alpha) and transversion (beta) rates, as well as 
    different rates for transitions between pyrimadines (alpha1) and 
    purines (alpha2).
    """
    def __init__(self):
        super().__init__()
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
        """: the rate matrix"""
        # not the following form
        # self._q_matrix = sympy.Matrix([[-alpha_1*pi_2-beta*pi_3-beta*pi_4, alpha_1*pi_2, beta*pi_3, beta*pi_4],
        #                                [alpha_1*pi_1, -alpha_1*pi_1 - beta*pi_3 - beta*pi_4, beta*pi_3, beta*pi_4],
        #                                [beta*pi_1, beta*pi_2, -alpha_2*pi_4 - beta*pi_2 - beta*pi_1, alpha_2*pi_4],
        #                                [beta*pi_1, beta*pi_2, alpha_2*pi_3, -alpha_2*pi_3 - beta*pi_2 - beta*pi_1]])
        # self._express = None
        # """: alpha/beta -> f(d,t,kappa_ls)"""
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

    # def _update_p_matrix(self):
    #     # original probability matrix
    #     self._p_matrices.append((self._q_matrix * self._t).exp())
    #     self._reparametrize_p_matrix()
    #
    # def _reparametrize_p_matrix(self):
    #     # --- use d and kappa_ls to replace alpha and beta ---
    #     # 1. get the expression of alpha_1, alpha_2, beta using phylogenetic distance, timespan, kappa_1, kappa_2
    #     if not self._express:
    #         self._update_express()
    #     # # 2. replace alpha_1, alpha_2, beta
    #     self._p_matrices.append(sympy.simplify(self._p_matrices[-1].
    #                                            subs(self._alpha_1, self._express[self._alpha_1]).
    #                                            subs(self._alpha_2, self._express[self._alpha_2]).
    #                                            subs(self._beta, self._express[self._beta])))

    def _update_p_matrix(self):
        """
        Instead of using self._p_matrices.append((self._q_matrix * self._t).exp())
        we have the p matrix stored to speed up
        """
        pi1, pi2, pi3, pi4 = self._PI
        d = self._d
        b = self._beta
        a1 = self._alpha_1
        a2 = self._alpha_2
        k1 = self._kappa_1
        k2 = self._kappa_2
        t = self._t
        exp = sympy.exp
        # to shorten the expression, do semi-manual combinations in the formula
        pi12 = pi1+pi2   # pyridines or purines
        pi34 = pi3+pi4   # purines or pyridines
        c1 = 2*(k1*pi2*pi1+k2*pi3*pi4+pi12*pi34)
        self._p_matrices.append(
            sympy.Matrix(
                [[(pi3*pi1+pi4*pi1)*exp(-b*t)/pi12+pi2*exp(-a1*pi12*t-b*pi34*t)/pi12+pi1,
                  (pi3*pi1+pi4*pi1)*exp(-b*t)/pi12-pi1*exp(-a1*pi12*t-b*pi34*t)/pi12+pi1,
                  pi1-pi1*exp(-b*t),
                  pi1-pi1*exp(-b*t)],
                 [pi2-pi2*exp(-a1*pi12*t-b*pi34*t)/pi12+(pi3*pi2+pi2*pi4)*exp(-b*t)/pi12,
                  pi2+(pi3*pi2+pi2*pi4)*exp(-b*t)/pi12+pi1*exp(-a1*pi12*t-b*pi34*t)/pi12,
                  pi2-pi2*exp(-b*t),
                  pi2-pi2*exp(-b*t)],
                 [-pi3*exp(-b*t)+pi3,
                  -pi3*exp(-b*t)+pi3,
                  pi3+pi3*pi12*exp(-b*t)/pi34-exp(-a2*pi34*t-b*pi12*t)/(-pi3/pi4-1),
                  pi3-pi3*exp(-a2*pi34*t-b*pi12*t)/pi34+pi3*pi12*exp(-b*t)/pi34],
                 [-pi4*exp(-b*t)+pi4,
                  -pi4*exp(-b*t)+pi4,
                  pi4+pi4*pi12*exp(-b*t)/pi34+exp(-a2*pi34*t-b*pi12*t)/(-pi3/pi4-1),
                  pi3*exp(-a2*pi34*t-b*pi12*t)/pi34+pi4+pi4*pi12*exp(-b*t)/pi34]]
            )
        )

        self._p_matrices.append(
            sympy.Matrix(
                [[pi1+(pi2*exp(d*(-k1*pi12-pi34+1)/c1)+pi1*pi34)*exp(-d/c1)/pi12,
                  pi1+pi1*(pi34-exp(d*(-k1*pi12-pi34+1)/c1))*exp(-d/c1)/pi12,
                  pi1-pi1*exp(-d/c1),
                  pi1-pi1*exp(-d/c1)],
                 [pi2+pi2*(pi34-exp(d*(-k1*pi12-pi34+1)/c1))*exp(-d/c1)/pi12,
                  pi2+(pi2*pi34+pi1*exp(d*(-k1*pi12-pi34+1)/c1))*exp(-d/c1)/pi12,
                  pi2-pi2*exp(-d/c1),
                  pi2-pi2*exp(-d/c1)],
                 [pi3-pi3*exp(-d/c1),
                  pi3-pi3*exp(-d/c1),
                  pi3+(pi3*pi12+pi4*exp(d*(-k2*pi34-pi12+1)/c1))*exp(-d/c1)/pi34,
                  pi3+pi3*(pi12-exp(d*(-k2*pi34-pi12+1)/c1))*exp(-d/c1)/pi34],
                 [pi4-pi4*exp(-d/c1),
                  pi4-pi4*exp(-d/c1),
                  pi4+pi4*(pi12-exp(d*(-k2*pi34-pi12+1)/c1))*exp(-d/c1)/pi34,
                  pi4+(pi3*exp(d*(-k2*pi34-pi12+1)/c1)+pi4*pi12)*exp(-d/c1)/pi34]]
            )
        )

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
        # here we did not use the self._pairwise_likelihood_formula (directly RES_LIKELIHOOD JC69 and K80)
        # because the generated function will be slow if two many separate parameters were used
        # instead, we use the self._log_p_matrix_w and the array of change_matrix to generate the formula
        like_formula = (self._log_p_matrix_w * change_matrix).sum()
        return sympy.lambdify([self._d, self._kappa_1, self._kappa_2] + self._PI, like_formula)

    # TODO using Horner's rule may help speed up, i.e. combining terms in common
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


def node_conditional_probability(
    node: toytree.Node,
    p_matrix_func: sympy.core.function,
) -> ArrayLike:
    """Return the conditional probability of a Node.

    This is a recursive function that can be called on the root Node
    of a tree to get the conditional likelihood of the whole tree. It
    calls itself on all children of each internal Node until it reaches
    the tips of the tree.
    """
    if node.is_leaf():
        return node.conditional_prob

    # internal Node computes conditional from child values
    child_cd_prob_generator = (
        node_conditional_probability(child_node, p_matrix_func)
        for child_node in node.children)
    prob_matrix_generator = (
        p_matrix_func(child_node.dist)
        for child_node in node.children)
    node.conditional_prob = combine_descendent_conditional_probability(
        child_conditional_prob_gen=child_cd_prob_generator,
        child_prob_matrix_gen=prob_matrix_generator)
    return node.conditional_prob


def combine_descendent_conditional_probability(
    child_conditional_prob_gen: Iterator[ArrayLike],
    child_prob_matrix_gen: Iterator[ArrayLike],
) -> ArrayLike:
    r"""Return conditional likelihood of a Node.

    Calculates the conditional probability of current node given its
    descendant conditional probability list and corresponding 
    transition probability matrix.

    Under non-logarithm mode, for node $i$ with descendent nodes {$j$} 
    and for each base type x, it calculates:

    $L_i(x_i)$ = $\product_j \sum_{x_j} p_{{x_i}{x_j}}(t_j)L_j(x_j)$

    the product of the 'transferred conditional probability' from all 
    descendent nodes. The 'transferred conditional probability' 
    ($\sum_{x_j} p_{{x_i}{x_j}}(t_j)L_j(x_j)$) here describe the sum 
    over conditional probabilities that base type x may accumulate from
    all base types from a descendent node.

    Parameters
    ----------
    child_conditional_prob_gen : Iterator[ArrayLike in the shape of (4,)]
        Input iterator that each time generates the conditional probability of a child.
        Each conditional probability array should be of `shape=(4,)`, e.g. `np.array([0.05, 0.001, 0.04, 0.002])`
    child_prob_matrix_gen: Iterator[ArrayLike in the shape of (4,4)]
        Input iterator that each time generates the transition probability matrix of a child.
        Each transition probability matrix should be of `shape=(4,4)`,
        e.g. `np.array([[0.8644351 , 0.06591888, 0.03482301, 0.03482301],
                        [0.06591888, 0.8644351 , 0.03482301, 0.03482301],
                        [0.03482301, 0.03482301, 0.8644351 , 0.06591888],
                        [0.03482301, 0.03482301, 0.06591888, 0.8644351 ]])` # K80 TEST_MODEL with d=0.15, k=2.
        This can be generated using the function of `get_p_matrix_function` under each substitution TEST_MODEL objects.

    Returns
    -------
    ArrayLike[float]
        Output the conditional probability of the combined use np.array in the shape of (4,).
    """
    accumulated_prob = (next(child_conditional_prob_gen) * next(child_prob_matrix_gen)).sum(axis=1)
    for child_prob in child_conditional_prob_gen:
        this_p_matrix = next(child_prob_matrix_gen)
        accumulated_prob *= (child_prob * this_p_matrix).sum(axis=1)
    return accumulated_prob


def get_tree_likelihood(
    tree: toytree.ToyTree,
    data: dict[str: str],
    p_matrix_func: sympy.core.function,
    pi_list: ArrayLike,
) -> float:
    """Return the log-likelihood of observing data given a tree.

    """
    # set observed data as features of tip Nodes
    for nidx in range(tree.ntips):
        node = tree[nidx]
        assert node.name in data, f"data must include all tips in the tree. Missing={node.name}"
        state = data[node.name]
        node.conditional_prob = np.array(BASE_ORDER) == state

    # infer internal node conditional probs from tip states
    root_prob = node_conditional_probability(tree.treenode, p_matrix_func)
    return (root_prob * pi_list).sum()


######################################################
#
# VISUALIZATION FUNCTIONS
#
######################################################


def combine_descendent_conditional_probability_with_plot(
    child_conditional_prob_list: List[ArrayLike],
    child_prob_matrix_list: List[ArrayLike],
    ax1,
) -> ArrayLike:
    """Return visualization of combine_descendent_conditional_probability.

    Parameters
    ----------
    child_conditional_prob_list : Iterator[ArrayLike in the shape of (4,)]
        Input iterator that each time generates the conditional probability
        of a child. Each conditional probability array should be of 
        `shape=(4,)`, e.g. `np.array([0.05, 0.001, 0.04, 0.002])`
    child_prob_matrix_list: Iterator[ArrayLike in the shape of (4,4)]
        Input iterator that each time generates the transition probability 
        matrix of a child. Each transition probability matrix should be of 
        `shape=(4,4)`, e.g.:
        >>> np.array([[0.8644351 , 0.06591888, 0.03482301, 0.03482301],
        >>>           [0.06591888, 0.8644351 , 0.03482301, 0.03482301],
        >>>           [0.03482301, 0.03482301, 0.8644351 , 0.06591888],
        >>>           [0.03482301, 0.03482301, 0.06591888, 0.8644351 ]])`
        >>>           # K80 TEST_MODEL with d=0.15, k=2.
        This can be generated using the function of `get_p_matrix_function`
        under each substitution TEST_MODEL objects.
    ax1: toyplot.Axis
        ...

    Returns
    -------
    ArrayLike[float]
        Output the conditional probability of the combined use np.array
        in the shape of (4,).
    """
    # plot input values
    for go_base in range(4):
        # conditional probs
        x_coords_c = [40 - (1.5 - go_base) * AX1_x_width for foo in child_conditional_prob_list]
        y_coords_c = [20 - (0.5 - go_c) * AX1_y_width for go_c, foo in enumerate(child_conditional_prob_list)]
        ax1.scatterplot(
            x_coords_c,
            y_coords_c,
            size=15,
            marker=[
                toyplot.marker.create(shape='r3.9x1',
                                      label=f'{child_conditional_prob[go_base]:.7f}',
                                      size=11,
                                      mstyle={"fill": BASE_COLOR_SCHEME[go_base], "stroke": "lightgrey",
                                              "fill-opacity": 0.2})
                for child_conditional_prob in child_conditional_prob_list
            ]
        )
        # p matrix
        x_coords_m = [40 - (1.5 - _to_base) * AX1_x_width
                      for foo in child_conditional_prob_list
                      for _to_base in range(4)]
        y_coords_m = [20 - (0.5 - go_c) * AX1_y_width - (3 + go_base) * AX1_y_width_m
                      for go_c, foo in enumerate(child_conditional_prob_list)
                      for _to_base in range(4)]
        ax1.scatterplot(
            x_coords_m,
            y_coords_m,
            size=15,
            marker=[
                toyplot.marker.create(shape='r3.9x1',
                                      label=f'{p_m[go_base][_to_base]:.7f}',
                                      size=11,
                                      mstyle={"fill": BASE_COLOR_SCHEME[_to_base], "stroke": "lightgrey",
                                              "fill-opacity": 0.2})
                for p_m in child_prob_matrix_list
                for _to_base in range(4)
            ]
        )
        # heads of p matrix
        labels = [[from_to + _base for _base in BASE_ORDER] for from_to in ("to ", "from ")]
        ax1.scatterplot(
            [40 + from_to * AX1_x_width * 2.5 - (1.5 - go_base) * AX1_x_width * (1 - from_to)
             for foo in child_conditional_prob_list
             for from_to in range(2)],
            [20 - (0.5 - go_c) * AX1_y_width - (3 + go_base) * AX1_y_width_m * from_to - 2 * (
                    1 - from_to) * AX1_y_width_m
             for go_c, foo in enumerate(child_conditional_prob_list)
             for from_to in range(2)],
            size=15,
            marker=[
                toyplot.marker.create(shape='r3.9x1',
                                      label=f'{labels[from_to][go_base]}',
                                      size=11,
                                      mstyle={"fill": BASE_COLOR_SCHEME[go_base], "stroke": "white",
                                              "fill-opacity": 0.05})
                for foo in child_conditional_prob_list
                for from_to in range(2)
            ]
        )

    # calculate the intermediate matrices
    intermediate_matrices = []
    for go_child, child_conditional_probability in enumerate(child_conditional_prob_list):
        intermediate_matrices.append(child_conditional_probability * child_prob_matrix_list[go_child])
    # plot the intermediate matrices
    for go_base in range(4):
        x_coords_m = [23.5 - (1.5 - _to_base) * AX1_x_width
                      for foo in child_conditional_prob_list
                      for _to_base in range(4)]
        y_coords_m = [20 - (0.4 - go_c) * AX1_y_width - (3 + go_base) * AX1_y_width_m
                      for go_c, foo in enumerate(child_conditional_prob_list)
                      for _to_base in range(4)]
        ax1.scatterplot(
            x_coords_m,
            y_coords_m,
            size=15,
            marker=[
                toyplot.marker.create(shape='r3.9x1',
                                      label=f'{intermediate_m[go_base][_to_base]:.7f}',
                                      size=11,
                                      mstyle={"fill": BASE_COLOR_SCHEME[_to_base], "stroke": "lightgrey",
                                              "fill-opacity": 0.2})
                for intermediate_m in intermediate_matrices
                for _to_base in range(4)
            ]
        )

    # calculate the sums
    summed_matrices = []
    for intermediate_matrix in intermediate_matrices:
        summed_matrices.append(intermediate_matrix.sum(axis=1))
    # plot the sums
    for go_base in range(4):
        # sum
        ax1.scatterplot(
            [23.5 - 2.7 * AX1_x_width for foo in child_conditional_prob_list],
            [20 - (0.4 - go_c) * AX1_y_width - (3 + go_base) * AX1_y_width_m for go_c, foo in
             enumerate(child_conditional_prob_list)],
            size=15,
            marker=[
                toyplot.marker.create(shape='r3.9x1',
                                      label=f'{sum_matrix[go_base]:.7f}',
                                      size=11,
                                      mstyle={"fill": BASE_COLOR_SCHEME[go_base], "stroke": "lightgrey",
                                              "fill-opacity": 0.2})
                for sum_matrix in summed_matrices
            ]
        )

    # calculate the product of the sums
    accumulated_prob = summed_matrices[0]
    for summing_matrix in summed_matrices[1:]:
        accumulated_prob *= summing_matrix
    # plot the final result
    for go_base in range(4):
        x_coords_m = [4 - (1.5 - go_base) * AX1_x_width]
        y_coords_m = [20 - 3 * AX1_y_width_m]
        ax1.scatterplot(x_coords_m, y_coords_m, size=15, marker=[
            toyplot.marker.create(shape='r3.9x1',
                                  label=f'{accumulated_prob[go_base]:.7f}',
                                  size=11,
                                  mstyle={"fill": BASE_COLOR_SCHEME[go_base], "stroke": "lightgrey",
                                          "fill-opacity": 0.2})
        ]
    )
    return accumulated_prob


def node_conditional_probability_with_plot(
    node, p_matrix_func: sympy.core.function, tree: toytree.ToyTree,
) -> Generator:
    """More description...

    Parameters
    ----------
    node: toytree.Node
        ...
    p_matrix_func: Callable
        ...
    tree: toytree.ToyTree
        ...
    """
    if node.is_leaf():
        yield node.conditional_prob, ""
    else:
        # create the generators, recursively
        child_cd_prob_list = []
        child_prob_matrix_list = []
        for child_node in node.children:
            child_generator = node_conditional_probability_with_plot(child_node, p_matrix_func, tree)
            conditional_prob, prob_canvas = next(child_generator)
            yield conditional_prob, prob_canvas
            prob_matrix = p_matrix_func(child_node.dist)
            for conditional_prob, prob_canvas in child_generator:
                yield conditional_prob, prob_canvas
            child_cd_prob_list.append(conditional_prob)
            child_prob_matrix_list.append(prob_matrix)
        # create the canvas
        node.conditional_prob_canvas = toyplot.Canvas(width=1200, height=400)
        ax0 = node.conditional_prob_ax0 = node.conditional_prob_canvas.cartesian(
            bounds=(50, 450, 50, 350), padding=40)
        ax1 = node.conditional_prob_ax1 = node.conditional_prob_canvas.cartesian(
            bounds=(550, 1150, 50, 350), padding=50, xmin=0, xmax=50, ymin=0, ymax=30)
        ax0.show = False
        ax1.show = False
        # plot tree
        tree.style.edge_colors = ['black'] * tree.nnodes
        for child_node in node.children:
            tree.style.edge_colors[child_node.idx] = "red"
        tree.draw(node_labels=True, node_sizes=12, width=30, height=400, axes=ax0)
        node.conditional_prob = combine_descendent_conditional_probability_with_plot(
            child_conditional_prob_list=child_cd_prob_list,
            child_prob_matrix_list=child_prob_matrix_list,
            ax1=ax1)
        # plot generated prob
        for go_base in range(4):
            # plot probs along the tree
            candidate_probs = tree.get_node_data("conditional_prob")
            accessible_points = [bool(len(j)) for j in candidate_probs]
            accessible_probs = [j for go_p, j in enumerate(candidate_probs) if accessible_points[go_p]]
            coords = tree.get_node_coordinates()[accessible_points]
            ax0.scatterplot(
                coords.x - (1.5 - go_base) * AX0_x_width,
                coords.y - 0.2,
                size=15,
                marker=[
                    toyplot.marker.create(shape='r3.9x1',
                                          label=f"{i[go_base]:.7f}",
                                          size=11,
                                          mstyle={"fill": BASE_COLOR_SCHEME[go_base], "stroke": "lightgrey",
                                                  "fill-opacity": 0.2})
                    for i in accessible_probs
                ]
            )
        yield node.conditional_prob, node.conditional_prob_canvas


def get_tree_likelihood_plot_gen(
    tree: toytree.ToyTree,
    tip_states: dict[str: str],
    p_matrix_func: sympy.core.function,
    pi_list: ArrayLike,
    ):
    """...
    """
    for sp_name, sp_state in tip_states.items():
        sp_node = tree.get_nodes(sp_name)[0]  # do we have better function to do this in toytree?
        sp_node.conditional_prob = (np.array(BASE_ORDER) == sp_state).astype(float)
    node_cp_plot_gen = node_conditional_probability_with_plot(tree.treenode, p_matrix_func=p_matrix_func, tree=tree)
    root_prob, current_canvas = next(node_cp_plot_gen)
    if current_canvas:
        yield "", root_prob, current_canvas
    for root_prob, current_canvas in node_cp_plot_gen:
        if current_canvas:
            yield "", root_prob, current_canvas
    yield (root_prob * pi_list).sum(), root_prob, tree.treenode.conditional_prob_canvas



if __name__ == "__main__":

    TEST_ARRAY = np.array([[179,  23,   1,   0],
                           [ 30, 219,   2,   0],
                           [  2,   1, 291,  10],
                           [  0,   0,  21, 169]])
    OBSERVED_DATA = {"sp-A": "T", "sp-B": "C", "sp-C": "A", "sp-D": "C", "sp-E": "C"}
    TREE = toytree.tree("(((sp-A:0.2,sp-B:0.2):0.1,sp-C:0.2):0.1,(sp-D:0.2,sp-E:0.2):0.1);")
    # TEST_MODEL = K80()
    TEST_MODEL = JC69()
    TEST_MODEL.p_matrix()
    print(TEST_MODEL._p_matrices)
    print(TEST_MODEL.q_matrix)

    # LIK = get_tree_likelihood(tree=TREE,
    #                           data=OBSERVED_DATA,
    #                           p_matrix_func=TEST_MODEL.get_p_matrix_function(kappa=2.),
    #                           pi_list=TEST_MODEL._PI)
    # print(LIK)
    # TREE.treenode.draw_ascii()
