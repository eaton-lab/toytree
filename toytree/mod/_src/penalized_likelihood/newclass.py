#!/usr/bin/env python

"""
Penalized likelihood classes
"""

from typing import Dict, Optional, Tuple, List
import subprocess
from dataclasses import dataclass, field, asdict
from loguru import logger
import numpy as np
import scipy.stats as stats
from scipy.optimize import minimize, Bounds, LinearConstraint
from scipy.special import factorial
import toytree


@dataclass
class PenLikBase:
    tree: toytree.ToyTree
    model: str
    weight: float
    epsilon: float
    tol: float
    verbose: bool
    calibrations: Dict[int,Tuple[int,int]]

@dataclass
class PenLik:
    tree: toytree.ToyTree
    model: str="relaxed"
    weight: float=1
    calibrations: Dict[int,Tuple[int,int]]=None
    epsilon: float=field(default=1e-8, repr=False)
    tol: float=field(default=1e-8, repr=False)
    verbose: bool=field(default=False, repr=False)

    # attrs extracted from tree
    edges: np.ndarray = field(init=False, repr=False)
    dists: np.ndarray = field(init=False, repr=False)
    dists_lf: np.ndarray = field(init=False, repr=False)
    edge_paths: List[Tuple] = field(init=False, repr=False)

    def __post_init__(self):
        # super().__init__(**asdict(self))
        if self.calibrations is None:
            self.calibrations = {self.tree.nnodes: (1, 1)}
        self.edges = self.tree.get_edges()
        self.dists = self.tree.get_node_data("dist").values
        self.dists_lf = np.log(factorial(self.dists))
        self.edge_paths = [
            (leaf.idx,) + tuple(i.idx for i in leaf.iter_ancestors()) 
            for leaf in self.tree.treenode.get_leaves()
        ]


if __name__ == "__main__":
    tree = toytree.rtree.rtree(10)    
    pen = PenLik(tree)
    print(pen)
