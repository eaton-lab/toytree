#!/usr/bin/env python

"""Map numeric values into plotting ranges."""

from collections.abc import Mapping
from typing import Any, Optional, Sequence, TypeVar

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from scipy.interpolate import interp1d

from toytree.utils import ToytreeError

ToyTree = TypeVar("ToyTree")
NAN_NOT_ALLOWED = (
    "NaN values are not allowed in feature range mapping when nan_values=None"
)
ONLY_NUMERIC_ALLOWED = "Only numeric dtypes can be used w/ tuple format (feature, ...)"


def get_range_mapped_feature(
    tree: ToyTree,
    feature: str,
    min_value: float = 5,
    max_value: float = 15,
    nan_value: Optional[float] = 0.0,
    tips_only: bool = False,
) -> np.ndarray:
    """Return numeric values mapped from a named tree feature.

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

    Raises
    ------
    ToytreeError
        If `feature` is not a str name, does not exist on the tree, or
        contains non-numeric values.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(4).set_node_data("x", [0, 1, 2, 3, 4, 5, 6])
    >>> vals = toytree.style.get_range_mapped_feature(
    ...     tree, "x", min_value=1, max_value=5
    ... )
    >>> float(np.nanmin(vals)), float(np.nanmax(vals))
    (1.0, 5.0)
    >>> tip_vals = toytree.style.get_range_mapped_feature(tree, "x", tips_only=True)
    >>> len(tip_vals) == tree.ntips
    True
    """
    if not isinstance(feature, str):
        raise ToytreeError(
            "get_range_mapped_feature() requires feature as a str name. "
            "Use get_range_mapped_values(data=...) for direct value mapping."
        )
    try:
        if tips_only:
            values = tree.get_tip_data(feature).values
        else:
            values = tree.get_node_data(feature).values
    except Exception as exc:
        raise ToytreeError(f"feature '{feature}' not in tree.features.") from exc
    if not is_numeric_dtype(values):
        raise ToytreeError(ONLY_NUMERIC_ALLOWED)
    return get_range_mapped_values(values, min_value, max_value, nan_value)


def get_range_mapped_values(
    data: pd.Series | Sequence[Any],
    min_value: float = 5,
    max_value: float = 15,
    nan_value: Optional[float] = 0.0,
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
    data: pd.Series | Sequence[Any]
        Numeric values to map. If a Series, its index is interpreted as node
        idx labels and values are placed into an array of size max(idx)+1.
        If a Sequence, values are interpreted in positional order.
    min_value: float
        The minimum value (min of the range).
    max_value: float
        The maximum values (max of the range).
    nan_value: float or None
        A value to return for nan values. If None then nan values will
        raise a ValueError.

    Raises
    ------
    ToytreeError
        If data is plain str or Mapping, if Series index is invalid,
        if values are non-numeric, or when NaN exists and nan_value is None.

    Examples
    --------
    >>> toytree.style.get_range_mapped_values([0, 10, 20], min_value=2, max_value=4)
    array([2., 3., 4.])

    >>> series = pd.Series([0.0, 10.0], index=[0, 3])
    >>> toytree.style.get_range_mapped_values(
    ...     series, min_value=1, max_value=3, nan_value=0
    ... )
    array([1., 0., 0., 3.])

    >>> toytree.style.get_range_mapped_values([1.0, np.nan, 2.0], 1, 2, nan_value=None)
    Traceback (most recent call last):
    ...
    toytree.utils.src.exceptions.ToytreeError: NaN values are not allowed...
    """
    if isinstance(data, str):
        raise ToytreeError(
            "get_range_mapped_values() does not accept plain str data. "
            "Use get_range_mapped_feature(tree, data='feature_name', ...)."
        )
    if isinstance(data, Mapping):
        raise ToytreeError(
            "get_range_mapped_values() does not accept Mapping data. "
            "Enter a Series or Sequence."
        )

    values = _coerce_numeric_values_data(data)
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


def _coerce_numeric_values_data(data: pd.Series | Sequence[Any]) -> np.ndarray:
    """Return a 1D float array from Series or Sequence numeric input.

    Parameters
    ----------
    data : pandas.Series or Sequence[Any]
        Input values to coerce.

    Returns
    -------
    numpy.ndarray
        One-dimensional float array. For Series input, values are projected
        into dense idx space from 0 to max(idx), with missing idx positions
        filled by NaN.

    Raises
    ------
    ToytreeError
        If Series index labels are invalid, if values are non-numeric, or if
        input is not one-dimensional after coercion.
    """
    # Branch 1: Series input is treated as sparse node-idx keyed values.
    if isinstance(data, pd.Series):
        if data.empty:
            return np.array([], dtype=float)

        # Validate index labels as integer node idx values.
        idx = np.asarray(data.index)
        if not np.issubdtype(idx.dtype, np.integer):
            try:
                idx = idx.astype(int)
            except Exception as exc:
                raise ToytreeError(
                    "Series index must contain integer node idx labels."
                ) from exc
        if np.any(idx < 0):
            raise ToytreeError("Series index cannot contain negative idx labels.")
        if np.unique(idx).size != idx.size:
            raise ToytreeError("Series index contains duplicate idx labels.")

        # Project sparse values to dense idx space, filling absent idx with NaN.
        values = np.full(int(idx.max()) + 1, np.nan, dtype=float)
        try:
            series_values = pd.to_numeric(data, errors="raise").to_numpy(dtype=float)
        except Exception as exc:
            raise ToytreeError(ONLY_NUMERIC_ALLOWED) from exc
        values[idx] = series_values

    # Branch 2: Sequence input is interpreted as positional values directly.
    else:
        try:
            values = np.asarray(data, dtype=float)
        except (TypeError, ValueError) as exc:
            raise ToytreeError(ONLY_NUMERIC_ALLOWED) from exc
        if values.ndim != 1:
            raise ToytreeError("data must be one-dimensional.")

    # Final guard to keep downstream mapping logic numeric-only.
    if not is_numeric_dtype(values):
        raise ToytreeError(ONLY_NUMERIC_ALLOWED)
    return values


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
    # vtree._draw_browser(...);
