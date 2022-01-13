#!/usr/bin/env python

"""Data transformations for formatting node values nicely.
"""


from copy import deepcopy
import numpy as np
from toytree.utils import ToytreeError


def normalize_values(values, nbins=10, min_value=2, max_value=12):
    """Distribute values into bins spaced at reasonable sizes for plotting.

    This is used in tree_style='p' to automatically scale Ne values
    to plot as edge widths.
    """
    # missing values are not allowed
    if np.isnan(np.array(values)).any():
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
