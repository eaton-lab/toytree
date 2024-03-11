#!/usr/bin/env python

"""Data transformations for formatting node values nicely.

# Tuple shortcut arg
style_arg=(feature, 2, 10)
"""

from typing import Sequence, Any, Optional, TypeVar
import numpy as np
from scipy.interpolate import interp1d
from pandas.api.types import is_numeric_dtype
from toytree.utils import ToytreeError

ToyTree = TypeVar("ToyTree")
NAN_NOT_ALLOWED = (
    "NaN values are not allowed in feature range mapping when nan_values=None")
ONLY_NUMERIC_ALLOWED = (
    "Only numeric dtypes can be used w/ tuple format (feature, ...)")


def get_range_mapped_feature(
    tree: ToyTree,
    feature: str,
    min_value: float = 5,
    max_value: float = 15,
    nan_value: Optional[float] = 0.,
    tips_only: bool = False
) -> np.ndarray:
    """Return an array of float values mapped to feature data in a tree.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree to extract feature data from.
    feature: str
        Name of a feature to extract from one or more Nodes in the tree.
    min_value: float
        The minimum value (min of the range).
    max_value: float
        The maximum values (max of the range).
    nan_value: float or None
        A value to return for nan values. If None then nan values will
        raise a ValueError.
    tips_only: bool
        If True then data is only projected and returned for tip Nodes.
    """
    if tips_only:
        values = tree.get_tip_data(feature).values
    else:
        values = tree.get_node_data(feature).values
    if not is_numeric_dtype(values):
        raise ToytreeError(ONLY_NUMERIC_ALLOWED)
    return get_range_mapped_values(values, min_value, max_value, nan_value)


def get_range_mapped_values(
    values: Sequence[Any],
    min_value: float = 5,
    max_value: float = 15,
    nan_value: Optional[float] = 0.
) -> np.ndarray:
    """Return values mapped to a value range better for plotting.

    For example, we want to use some feature data such as 'dist' values
    to map Node sizes during plotting, but the dist values are in at
    values of 1/1000 or 1000, i.e., too small or too large for plotting.
    We can use this function to map them into a range more appropriate
    for plotting, such as 5-15 px, while maintaining their _relative_
    differences.

    Parameters
    ----------
    values: Sequence
        A sequence of numeric values. Non numerics will raise TypeError.
    min_value: float
        The minimum value (min of the range).
    max_value: float
        The maximum values (max of the range).
    nan_value: float or None
        A value to return for nan values. If None then nan values will
        raise a ValueError.

    Note
    ----
    This funtion uses `scipy.interpolate.interp1d` for interpolation.

    See Also
    ---------
    - toytree.color.get_color_mapped_feature

    Examples
    --------
    >>> tree = toytree.rtree.imbtree(8)

    >>> # get values from 'dist' feature in range 1-5
    >>> dists = tree.get_node_data("dist")
    >>> mdists = toytree.style.get_range_mapped_feature(dists, 1, 5)
    >>> tree.draw(edge_width=mdists)

    >>> # or, use shortcut to range map values when plotting
    >>> tree.draw(edge_width=('dist', (1, 5)))
    """
    assert isinstance(min_value, (float, int)), "min_values must be int or float"
    assert isinstance(max_value, (float, int)), "min_values must be int or float"

    # get mask of NaN values
    nan_mask = np.isnan(values)
    if all(nan_mask):
        if nan_value is None:
            raise ToytreeError(NAN_NOT_ALLOWED)
        return np.repeat(nan_value, len(values))

    # build interpolator from x data values to y requested range.
    mapper = interp1d(
        x=(np.nanmin(values), np.nanmax(values)),
        y=(min_value, max_value),
    )
    mvalues = np.array([mapper(i) for i in values])

    # handle nans in the data
    if nan_mask.sum():
        if nan_value is None:
            raise ToytreeError(NAN_NOT_ALLOWED)
        mvalues[nan_mask] = nan_value

    # return the range mapped values
    return mvalues


# def normalize_values(
#     values: Sequence[Any],
#     min_value: int = 2,
#     max_value: int = 12,
#     nbins: int = 10,
# ) -> np.ndarray:
#     """Distribute values into bins spaced at reasonable sizes for plotting.

#     This is used in tree_style='p' to automatically scale Ne values
#     to plot as edge widths. The input 'values' arg will usually be
#     a pandas.Series.

#     TODO: get_node_data dtype setting.., rename as discretize values?
#     """
#     # missing values are not allowed
#     if np.isnan(values).any():
#         raise ToytreeError(
#             f"missing values are not allowed:\n{values}.")

#     # make copy of original
#     ovals = deepcopy(values)

#     # if 6X min value is higher than max then add this
#     # as a fake value to scale more nicely
#     vals = list(values)
#     if min(vals) * 6 > max(vals):
#         vals.append(min(vals) * 6)

#     # sorted vals list
#     svals = sorted(vals)

#     # put vals into bins
#     bins = np.histogram(vals, bins=nbins)[0]

#     # convert binned vals to widths in 2-12
#     newvals = {}
#     sizes = np.linspace(min_value, max_value, nbins)
#     for idx, inbin in enumerate(bins):
#         for _ in range(inbin):
#             newvals[svals.pop(0)] = sizes[idx]
#     return np.array([newvals[i] for i in ovals])


if __name__ == "__main__":

    # import ipcoal
    import toytree

    # generate a random species tree with 10 tips and a crown age of 10M generations
    tree = toytree.rtree.unittree(10, treeheight=1e6, seed=123)
    # create a new tree copy with Ne values mapped to nodes
    vtree = tree.set_node_data(
        feature="Ne",
        data={i: 2e5 for i in (6, 7, 8, 9, 12, 15, 17)},
        default=1e4,
    )

    print(vtree.get_node_data())
    # vtree._draw_browser(ts='p', admixture_edges=[(0, 12, 0.5, {'stroke': 'red'}, "hello")]);
