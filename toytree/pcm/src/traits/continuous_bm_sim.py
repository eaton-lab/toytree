#!/usr/bin/env python

"""Simulate one or more continuous traits under Brownian motion.

"""

from typing import Union, Sequence, Dict
import pandas as pd
import numpy as np
from toytree import ToyTree
from toytree.utils import ToytreeError
from toytree.core.apis import add_subpackage_method, PhyloCompAPI

__all__ = [
    "simulate_continuous_bm",
]


def simulate_continuous_multivariate_bm(
    tree: ToyTree,
    rates: Union[float, Sequence[float], Dict[str, float]],
    root_states: Union[float, Sequence[float], Dict[str, float], None] = None,
    seed: Union[int, np.random.Generator, None] = None,
    df: bool = False,
) -> Union[ToyTree, pd.DataFrame]:
    """Simulate two or more continuous correlated traits under Brownian motion.
    
    THIS CAN PROB BE ACCOMPLISHED WITHIN THE FUNC BELOW BY ALLOWING
    A VCV AS INPUT FOR RATES.

    References
    ----------
    - https://lukejharmon.github.io/pcm/chapter3_bmintro/
    """
    # TODO


@add_subpackage_method(PhyloCompAPI)
def simulate_continuous_bm(
    tree: ToyTree,
    rates: Union[float, Sequence[float]],
    root_states: Union[float, Sequence[float], None] = None,
    tips_only: bool = False,
    inplace: bool = False,
    seed: Union[int, np.random.Generator, None] = None,
) -> Union[pd.DataFrame, None]:
    """Simulate one or more continuous traits under Brownian motion.

    The amount of change in a continuous trait over a given time
    interval can be modeled under Brownian motion as the result of
    a random walk. At each time step the value changes by an amount
    randomly sampled from a normal distribution with mean=0 and variance
    described by an evolutionary rate parameter, sigma**2. To model the
    change over an interval of time we can simply sample a random value
    from a normal distribution with mean=0 and variance as the product
    of the length of time and the rate parameter sigma**2 * t.

    Simulated traits are labeled t0-tN for N traits, unless the rates
    arg is entered as a mapping (e.g., dict) in which case traits can
    be given custom names. By default, simulated data are returned as
    a pandas DataFrame, but can alternatively be stored to the Nodes
    of the tree by using `inplace=True`. 

    Paramaters
    ----------
    tree: ToyTree
        A ToyTree on which traits will be simulated given the topology
        and branch lengths.
    rates: float, Sequence[float], or Mapping[str, float]
        Evolutionary rate parameter(s) (sigma**2) for one or more traits
        which determine the rate of the random walk.
    root_states: None, float, Sequence[float], or Mapping[str, float]
        The root state for each trait value. This is the expected mean
        state for all values at the tips under Brownian motion. If None
        (default) the root states are set to 0.
    tips_only: bool
        If True values are only returned for the tip Nodes.
    inplace: bool
        If False simulated data are returned as a pandas DataFrame; if
        True simulated data are assigned to Nodes on the input tree,
        and can be fetched using `tree.get_node_data()`.
    seed: int, numpy RNG, or None
        Seed for numpy random number generator.

    References
    ----------
    - https://lukejharmon.github.io/pcm/chapter3_bmintro/

    Example
    -------
    >>> tree = toytree.rtree.unittree(10, treeheight=10)
    >>> data = tree.pcm.simulate_continuous_bm(rate=1.0)
    >>> 
    >>> # simulate multiple traits with different rates
    >>> data = tree.pcm.simulate_continuous_bm(rates=[1, 2, 3])
    >>>
    >>> # simulate 100 replicates w/ same rate and assign to tree Nodes
    >>> tree.pcm.simulate_continuous_bm([1.0] * 100, inplace=True)
    >>> print(tree.get_node_data())
    """
    # seed random number generator
    rng = np.random.default_rng(seed)

    # make ratess into a dict w/ trait names (t0, t1, t2, ...) or custom
    if isinstance(rates, (float, int)):
        rates = np.array([rates])
        names = ["t0"]
    elif isinstance(rates, (list, tuple, np.ndarray)):
        rates = np.array(rates)
        names = [f"t{i}" for i in range(len(rates))]
    elif isinstance(rates, dict):
        names = list(rates.keys())
        rates = np.array(list(rates.values()))
    else:
        raise ToytreeError("rate argument type not supported")

    # check root states arg
    if root_states is None:
        root_states = np.zeros(len(rates))
    elif isinstance(root_states, (float, int)):
        root_states = np.array([root_states])
    elif isinstance(root_states, (list, tuple, np.ndarray)):
        root_states = np.array(root_states)
    else:
        raise ToytreeError("root_states argument type not supported.")
    if len(root_states) != len(rates):
        raise ToytreeError(
            "root_states and rates args must be same length, or root_states=None.")

    # create tree copy
    # tree = tree if inplace else tree.copy()

    # store trait values in array
    arr = np.zeros((tree.nnodes, len(root_states)))
    arr[-1] = root_states
    for node in tree[::-1][1:]:
        arr[node.idx] = rng.normal(arr[node.up.idx], node.dist * rates)

    # return as tree (default), array, or dataframe
    end = tree.ntips if tips_only else tree.nnodes
    if inplace:
        for node in tree[:end]:
            for tidx in range(arr.shape[1]):
                trait = names[tidx]
                setattr(node, trait, arr[node._idx, tidx])
        return None
    return pd.DataFrame(arr[:end], columns=names)


if __name__ == "__main__":

    import toytree
    tree = toytree.rtree.unittree(10, treeheight=1)
    data = simulate_continuous_bm(
        tree,
        rates=[1., 2.],
        root_states=[10, 20],
        seed=123,
        tips_only=True,
    )
    print(data)

    data = simulate_continuous_bm(
        tree,
        rates=1.,
        seed=123,
        tips_only=True,
    )
    print(data)

    # tree._draw_browser(
    #     # edge_widths=4,
    #     # ts='c',
    #     # edge_style={"stroke-width": 4},
    #     node_sizes="t0",
    #     node_colors="t0",
    #     node_mask=False,
    #     node_labels=("t0", "{:.2f}"),
    #     node_labels_style={"anchor_shift": -10, "baseline-shift": 10}
    # )

    # vcv = tree.pcm.get_vcv_matrix_from_tree()
    # rng = np.random.default_rng(123)
    # print(rng.multivariate_normal([0] * tree.nnodes, 1. * vcv))
