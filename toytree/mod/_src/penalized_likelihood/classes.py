#!/usr/bin/env python

"""Apply penalized likelihood to get an ultrametric tree.

References
----------
...
"""

from typing import Dict, Optional, TypeVar
import subprocess
from loguru import logger
import toyplot
import numpy as np
from scipy import stats
from scipy.optimize import minimize, Bounds, LinearConstraint
from scipy.special import factorial
import toytree
from toytree.utils import ToytreeError

logger = logger.bind(name="toytree")

ToyTree = TypeVar("ToyTree")
AGES_MIN = 1e-8
AGES_MAX = 1e8
RATES_MIN = 1e-9
RATES_MAX = 1e5


class Chronos:
    """Return an ultrametric tree using penalized likelihood.

    Scales edge lengths of a non-ultrametric tree to make it 
    ultrametric (all tips align at zero) by treating edge lengths
    as rate x time (which is typically true for ML estimated trees),
    and estimating rate variation among all edges so that the age of 
    tip nodes=0. 

    Parameters
    -----------
    tree: ToyTree
        A toytree instance.
    model: str
        A model of rate variation among edges ("relaxed", ...). 
    weight: float
        Weighting of the rate variation (penalty component) to the 
        penalized likelihood score. This is referred to as lambda 
        by Sanderson. Lower values allow less variation.
    epsilon: float
        Convergence diagnostic... Default=1e-8.
    tol: float
        Tolerance for convergence, the minimum on rates. Default=1e-8.
    verbose: bool
        Prints information on model fitting and results. Default=False.

    Returns
    -------
    ToyTree: with transformed dist (edge length) feature values, and
    features for ages and rates.

    References
    ----------
    Sanderson
    https://github.com/cran/ape/blob/master/R/chronos.R
    Paradis article ...
    """
    def __init__(
        self, 
        tree: ToyTree,
        calibrations: Optional[Dict]=None,
        model: str="relaxed",
        weight: float=1, 
        tol: float=1e-8, 
        verbose: bool=False,
        ):

        # store tree data
        self.tree = tree
        self.model = model
        self.weight = weight
        self.tol = tol
        self.epsilon = 1e-8
        self.calibrations = (
            calibrations if calibrations is not None
            else {self.tree.treenode.idx: (1, 1)}
        )

        # simple logger
        self.print = (print if verbose else iter)

        # store tree components
        self.edges = self.tree.get_edges()
        self.dists = self.tree.get_edge_values("dist")
        self.dists_lf = np.log(factorial(self.dists))
        self.edge_paths = [
            (leaf.idx,) + tuple(i.idx for i in leaf.iter_ancestors()) 
            for leaf in self.tree.treenode.get_leaves()
        ]

        # starting ages
        self.ages_est_idxs = np.zeros(self.tree.nnodes)
        self.ages_init = np.zeros(self.tree.nnodes)
        self.ages_lens = np.zeros(self.edges.shape[0])
        self.get_ages_init()

        # starting rates
        self.rates_init = self.dists / self.ages_lens
        
        # get bound conditions on nodes ages and rates
        self.get_bounds()

        # parameters to estimate and results to store 
        self.params = np.concatenate([
            self.rates_init, 
            self.ages_init[self.ages_est_idxs],
        ])
        self.ploglik = None
        self.results = self.params
        self.print('{} parameters to estimate'.format(self.params.size))

        # gradient incidence matrices for relaxed model
        self.mat_a = np.array([self.edges[:, 1] == i for i in self.ages_est_idxs])
        self.mat_d = np.array([self.edges[:, 0] == i for i in self.ages_est_idxs])

        # gradient incidence matrices for correlated model
        self.ni_ = np.bincount(self.edges[:].flatten())[:-1]
        self.mat_n = np.zeros((self.edges.shape[0], self.edges.shape[0]), dtype=bool)
        for nidx in range(self.tree.nnodes):
            node = self.tree[nidx]
            if node.up:
                self.mat_n[nidx, nidx] = True
                ind = [i.idx for i in node.children]
                self.mat_n[nidx][ind] = True

        # fit the model iteratively
        # self.iterative_model_fit()

    def run(self):
        """
        Calls optimization function, calculate PhiiC and applies results
        to nodes of a Toytree.
        """
        # report results
        self.print('init ploglik: {}'.format(-self.objective(self.params)))
        self.optimize()
        self.print('final ploglik: {}'.format(-self.objective(self.results)))

        # get phic
        self.get_phiic()

        # store final converted tree
        self.tree = self.get_transformed_tree()

    def get_ages_init(self):
        """
        Finds starting values for age lens by applying values between 
        contraints. If no calibrations then it sets root to 1, otherwise, 
        it can accommodate node calibrations.
        """
        self.print("setting initial dates")        

        # hard-coded values for finding starting fit
        root_multiplier = 3
        max_attempts = 10
        attempt = 0

        # iterate to get starting values using hard-coded limits
        while 1:
            
            # set ages to 0 (tips) or nan (all others)
            self.ages_init[:] = np.nan
            self.ages_init[:self.tree.ntips] = 0

            # set the ages of calibrations at their midpoint
            for nidx in self.calibrations:
                age = self.calibrations[nidx]
                self.ages_init[nidx] = age[0] + ((age[1] - age[0]) / 2.)

            # set root age, if not already calibrated, using an approximation
            if np.isnan(self.ages_init[self.tree.treenode.idx]):
                self.ages_init[self.tree.treenode.idx] = root_multiplier * max(self.ages_init)

            # indices of the nodes that need age estimates
            self.ages_est_idxs = np.where(np.isnan(self.ages_init))[0]

            # sort edge paths so that younger ages are set before older ones
            sorted_epaths = sorted(self.edge_paths, key=len)
            # sorted_epaths = sorted(self.edge_paths, key=lambda x: (~np.isnan(x[1:])).argmax())
            # for idx in range(len(self.edge_paths)):
                # print([self.ages_init[i] for i in sorted_epaths[idx]], sorted_epaths[idx])
           
            # sort paths by nodes until first non-nan
            # visit edge paths in order, e.g., [(5, 9, 10), (4, 7, 9, 10), ...]
            # for path in self.edge_paths[::-1]:
            for path in sorted_epaths:
                
                # get ages on this path, e.g., [0.0, nan, nan, 1.0]
                path_ages = [self.ages_init[i] for i in path]
                
                # counting down reversed path indices, e.g., [ 3, 2, 1, 0 ]
                for pidx in range(len(path_ages))[::-1]:
                    
                    # if age is nan then split the distance to next non-nan
                    if np.isnan(path_ages[pidx]):

                        # get value spaced between data with nnodes
                        maxage = path_ages[pidx + 1]
                        minidx = (~np.isnan(path_ages[:pidx])).argmax()
                        minage = path_ages[minidx]
                        interval = maxage - minage
                        extent = interval - (interval / (pidx - minidx + 1))

                        # store the new age value
                        self.ages_init[path[pidx]] = extent
            
            # get age edge lengths
            self.ages_lens = (
                self.ages_init[self.edges[:, 0]] - self.ages_init[self.edges[:, 1]]
            )
            
            # check that all edges are positive in length        
            if all(self.ages_lens >= 0):
                break
            attempt += 1
            root_multiplier *= 1.5
            if attempt == max_attempts:
                raise ToytreeError("bad starting values")

        # store initial values for method validation
        self.init_tree = self.get_transformed_tree()

    def get_bounds(self):
        """
        Stores a list of tuples of (min, max) for every parameter made up 
        of the calibration info or default limits.
        """
        # RATES_MIN = max(RATES_MIN, self.tol)
        self.bounds = [(RATES_MIN, RATES_MAX) for i in self.rates_init]
        self.bounds += [(AGES_MIN, AGES_MAX) for i in self.ages_est_idxs]

        # bounds can be further constrained by hard calibrated nodes
        for nidx in self.calibrations:
            cmin, cmax = self.calibrations[nidx]

            # if calibration is a range then add node back to be estimated.
            if cmin != cmax:
                self.bounds += [cmin, cmax]
                self.ages_est_idxs = np.concatenate(
                    [self.ages_est_idxs, [nidx]]
                )

    def optimize(self, rates=True, ages=True):
        """
        Maximum likelihood optimization of the objective function.
        """
        # estimate all rates and all ages except tips and calibrated nodes
        # fit = minimize(
        #     fun=self.objective,
        #     x0=self.params,
        #     args=(rates, ages),
        #     # method="L-BFGS-B",
        #     method="SLSQP",
        #     # method="TNC",
        #     bounds=self.bounds,
        #     jac=self.gradient,
        #     options={
        #         # "maxiter": 100,
        #         # "disp": False,
        #     }
        # )
        fit = minimize(
            fun=self.objective,
            x0=self.params,
            args=(rates, ages),
            method="L-BFGS-B",
            bounds=self.bounds,
            options={
                # "maxiter": 100,
                # "disp": False,
            }
        )        
        self.results = fit.x
        self.ploglik = fit.fun

    def update(self, params, rates, ages):
        """
        Update one or both parameter sets...
        """
        # separate params
        if rates:
            self.rates_hat = params[:self.rates_init.size]
        else:
            self.rates_hat = self.results[:self.rates_init.size]

        if ages:
            self.ages_hat = params[self.rates_init.size:]
        else:
            self.ages_hat = self.results[self.rates_init.size:]

        # impute estimated ages into the full set of ages
        self.ages_init[self.ages_est_idxs] = self.ages_hat

    def objective(self, params, rates=True, ages=True):
        """
        The penalized likelihood function to MINIMIZE
        """
        # update params on self
        self.update(params, rates, ages)

        # component 2
        if self.model == "relaxed":
            penalty = self.lik_penalty_relaxed().sum()
        elif self.model == "correlated":
            penalty = self.lik_penalty_correlated().sum()

        # return the full score
        return -self.lik_poisson() + (self.weight * penalty)

    def lik_poisson(self):
        """
        The poisson function returns higher values for better fit.
        When dealing with count data the Poisson likelihood statistic 
        can be used to measure how well a particular model describes 
        the data, and is especially appropriate when there are just a 
        few counts per bin, because in that case the Least Squares method 
        is inappropriate. 
        """
        # check that edge lengths are still all positive
        age_lens = self.ages_init[self.edges[:, 0]] - self.ages_init[self.edges[:, 1]]
        if any(age_lens < 0):
            return -1e100

        # calculate likelihood
        ratelens = self.rates_hat * age_lens
        loglik = np.sum(
            self.dists * np.log(ratelens) - ratelens - self.dists_lf
        )
        return loglik

    def lik_penalty_relaxed(self):
        """
        Penalty component to likelihood for the relaxed model.
        """
        alpha = self.rates_hat.mean()
        pdens = sorted(stats.gamma.cdf(self.rates_hat, alpha))
        pcdf = ((np.arange(1, self.rates_hat.size + 1) / self.rates_hat.size) - pdens) ** 2
        return pcdf

    def lik_penalty_correlated(self):
        """
        Penalty component to likelihood for the correlated rates model.
        """
        ele2 = np.var([self.rates_hat[i] for i in self.edges[-2:, 1]])
        ele1 = [
            ((self.rates_hat[edge[0]] - self.rates_hat[edge[1]]) ** 2) 
            for edge in self.edges[:-2]
        ]
        return self.weight * (np.sum(ele1) + ele2)

    def gradient(self, params, rates=True, ages=True):
        """
        Combined gradient function for poisson and penalty components
        """
        # 
        self.update(params, rates, ages)

        # get poisson gradient on params
        gradient = self.gradient_poisson()

        # add the effect of rate model on gradients of rate params
        if self.model == "relaxed":
            gradient[:self.rates_hat.size] += self.gradient_penalty_relaxed()

        # return gradient
        return gradient

    def gradient_poisson(self):
        """
        Gradient function for the Poisson component.
        """
        # get edge lengths between node ages
        age_lens = self.ages_init[self.edges[:, 0]] - self.ages_init[self.edges[:, 1]]

        # gradient for the rates
        rates_gr = (self.dists / self.rates_hat) - age_lens

        # gradient for the dates
        inner = (self.dists / age_lens) - self.rates_hat
        dates_gr = np.sum((inner * self.mat_a) - (inner * self.mat_d), axis=1)

        # return as a concatenated list
        return np.concatenate([rates_gr, dates_gr])

    def gradient_penalty_relaxed(self):
        """
        Gradient function for the relaxed model penalty component
        """
        alpha = self.rates_hat.mean()
        a = stats.gamma.pdf(self.rates_hat, alpha)
        b = np.argsort(self.rates_hat) / self.rates_hat.size
        c = stats.gamma.cdf(self.rates_hat, alpha)
        gradient = 2 * a * (b - c)       
        return self.weight * gradient

    def gradient_penalty_correlated(self):
        """
        Gradient function for the correlated rates penalty component
        """
        # gr <- gradient.poisson(rate, node.time)
        #if (all(gr == 0)) return(gr)

        ## contribution of the penalty for the rates:
        # gr[RATE] <- gr[RATE] - lambda * 2 * 

        # (eta_i * rate - sapply(X, function(x) sum(rate[x])))

        # gradient = (
        #     self.ni[i] * self.rates_hat[i]) - 
        #     self.rates_hat[self.matN[i]].sum()
        #  self.weight * 2 * gradient
        
        # the contribution of the root variance term:
        # if (Nbasal == 2) { # the simpler formulae if there's a basal dichotomy
        #     i <- basal[1]
        #     j <- basal[2]
        #     gr[i] <- gr[i] - lambda * (rate[i] - rate[j])
        #     gr[j] <- gr[j] - lambda * (rate[j] - rate[i])
        # } 

        # if not basal dichotomy then support this...
        # else { # the general case
        #     for (i in 1:Nbasal)
        #         j <- basal[i]
        #         gr[j] <- gr[j] -
        #         lambda*2*(rate[j]*(1 - 1/Nbasal) - sum(rate[basal[-i]])/Nbasal)/(Nbasal - 1)
        #    }
        #    gr
        # }

    def get_transformed_tree(self):
        """
        Returns a toytree with new ages (dists) and rates on nodes from the 
        estimated values in self.results.
        """
        # copy and return tree with starting edges
        newtre = self.tree.copy()
        for node in newtre.treenode.traverse("postorder"):
            if node.up:
                node.dist = self.ages_init[node.up.idx] - self.ages_init[node.idx]
                # node.rate = self.params[node.]
        return newtre

    def iterative_model_fit(self):
        """
        Fits the model by ML iteratively, fitting rates then dates, until
        the change in likelihood score is less than epsilon.
        """
        # initial fit: all params
        self.optimize()
        self.print("initial model fit P-loglik: {}".format(self.ploglik))

        # start iterative loop
        tries = 0
        while 1:

            # params and score at start
            curparams = self.results
            curscore = self.ploglik

            # fit rates holding dates constant
            self.optimize(True, False)
            self.print("optimizing rates P-loglik: {}".format(self.ploglik))

            # reject new model fit
            if self.ploglik > curscore:
                self.results = self.params = curparams
                self.ploglik = curscore
                self.print("rejected rates, P-loglik: {}".format(self.ploglik))
            else:
                curscore = self.ploglik
                curparams = self.results

            # fit dates holding rates constant
            self.optimize(False, True)
            self.print("optimizing dates P-loglik: {}".format(self.ploglik))

            # reject new model fit
            if self.ploglik > curscore:
                self.results = self.params = curparams
                self.ploglik = curscore
                self.print("rejected rates, P-loglik: {}".format(self.ploglik))
            else:
                curscore = self.ploglik
                curparams = self.results

            tries += 1
            if tries > 100:
                break
        # 
        self.print()

    def get_phiic(self):

        # get rates
        self._rates = self.params[:self.rates_init.size]

        # 
        if self.model == 'relaxed':
            # alpha = self._rates.mean()
            # pgams = gamma.pdf(self._rates, alpha ** 2, loc=0, scale=1 / alpha)
            alpha = self.rates_hat.mean()
            pdens = sorted(stats.gamma.cdf(self.rates_hat, alpha))
            dx_ = np.linalg.svd([pdens])[1][0]

        # calculate 
        self.phiic = np.sum([
            -2 * self.ploglik,
            2 * len(self.bounds),
            self.weight * dx_,
        ])
        self.print('loglik: {}'.format(self.lik_poisson()))
        self.print('PHIIC: {}'.format(self.phiic))



    # def phi_correlated(edges, r):
    #     ele2 = np.var([r[i] for i in edges[-2:, 1]])
    #     ele1 = [(r[edge[0]] - r[edge[1]]) ** 2 for edge in edges[:-2]]
    #     return np.sum(ele1) + ele2


    # def gradient_ages(self, rate, time):
    #     age[unknown.ages] <- node.time
    #     real.edge.length <- age[e1] - age[e2]

    #     ## gradient for the rates:
    #     gr <- el/rate - real.edge.length

    #     ## gradient for the dates:
    #     tmp <- el/real.edge.length - rate
    #     tmp2 <- tmp[D_ki]
    #     tmp2[is.na(tmp2)] <- 0
    #     gr.dates <- sapply(A_ki, function(x) sum(tmp[x])) - tmp2

    #     c(gr, gr.dates)


    # def gradient_penalty(self, rate, time):
    #     gr <- gradient.poisson(rate, node.time)
    #     #if (all(gr == 0)) return(gr)

    #     ## contribution of the penalty for the rates:
    #     mean.rate <- mean(rate)

    #     ## rank(rate)/Nb.rates is the same than ecdf(rate)(rate) but faster
    #     # gr[RATE] <- gr[RATE] + lambda*2*dgamma(rate, mean.rate)*(rank(rate)/Nb.rates - pgamma(rate, mean.rate))
    #     # gr



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

    TREE = toytree.rtree.unittree(10, treeheight=1e6)
    TSA = TreeSampler(TREE, neff=5e5, gentime=1, gamma=3)
    TRE = TSA.get_tree()
    print(TRE)
