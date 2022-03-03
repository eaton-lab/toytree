#!/usr/bin/env python

"""Data transformations for formatting node values nicely.
"""

from copy import deepcopy
import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from toytree.utils import ToytreeError


def normalize_values(
    values: pd.Series,
    nbins: int=10,
    min_value: int=2,
    max_value: int=12,
    ) -> ArrayLike:
    """Distribute values into bins spaced at reasonable sizes for plotting.

    This is used in tree_style='p' to automatically scale Ne values
    to plot as edge widths. The input 'values' arg will usually be
    a pandas.Series.

    TODO: get_node_data dtype setting..
    """
    # missing values are not allowed
    if values.isna().any():
        raise ToytreeError(
            f"missing values are not allowed:\n{values}.")

    # make copy of original
    ovals = deepcopy(values)

    # if 6X min value is higher than max then add this
    # as a fake value to scale more nicely
    vals = list(values)
    if min(vals) * 6 > max(vals):
        vals.append(min(vals) * 6)

    # sorted vals list
    svals = sorted(vals)

    # put vals into bins
    bins = np.histogram(vals, bins=nbins)[0]

    # convert binned vals to widths in 2-12
    newvals = {}
    sizes = np.linspace(min_value, max_value, nbins)
    for idx, inbin in enumerate(bins):
        for _ in range(inbin):
            newvals[svals.pop(0)] = sizes[idx]
    return np.array([newvals[i] for i in ovals])


if __name__ == "__main__":

    import ipcoal
    import toytree

    # generate a random species tree with 10 tips and a crown age of 10M generations
    tree = toytree.rtree.unittree(10, treeheight=1e6, seed=123)
    # create a new tree copy with Ne values mapped to nodes
    vtree = tree.set_node_data(
        feature="Ne",
        mapping={i: 2e5 for i in (6, 7, 8, 9, 12, 15, 17)},
        default=1e4,
    )

    vtree._draw_browser(ts='p', admixture_edges=[(0, 12, 0.5, {'stroke': 'red'}, "hello")]);
