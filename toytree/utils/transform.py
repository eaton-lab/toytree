#!/usr/bin/env python

"""
Data transformations for formatting node values nicely.
"""


from copy import deepcopy
import numpy as np


def normalize_values(vals, nbins=10, minsize=2, maxsize=12):
    """
    Distributes values into bins spaced at reasonable sizes for
    plotting. Example, this can be used automatically scale Ne values
    to plot as edge widths.
    """
    # make copy of original
    ovals = deepcopy(vals)

    # if 6X min value is higher than max then add this 
    # as a fake value to scale more nicely
    vals = list(vals)
    if min(vals) * 6 > max(vals):
        vals.append(min(vals) * 6)

    # sorted vals list
    svals = sorted(vals)

    # put vals into bins
    bins = np.histogram(vals, bins=nbins)[0]

    # convert binned vals to widths in 2-12
    newvals = {}
    sizes = np.linspace(minsize, maxsize, nbins)
    for idx, inbin in enumerate(bins):
        for _ in range(inbin):
            newvals[svals.pop(0)] = sizes[idx]
    return np.array([newvals[i] for i in ovals])
