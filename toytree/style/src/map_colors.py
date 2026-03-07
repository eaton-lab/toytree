#!/usr/bin/env python

"""Map feature values to colors for plotting."""

from collections.abc import Mapping
from typing import Any, Optional, Sequence, TypeVar, Union

import numpy as np
import pandas as pd
import toyplot

from toytree.color import ToyColor
from toytree.utils.src.exceptions import ToytreeError

ToyTree = TypeVar("ToyTree")


CMAP_ERROR = """
To find a list of valid colormap names supported by toyplot use:
>>> print(toyplot.color.brewer.names())

You can map feature values to colors by entering (feature, colormap):
>>> tree.draw('c', node_colors=('dist', 'Spectral'))

or, load a colormap as a Map object for finer control:
>>> cmap = toyplot.color.brewer.map('BlueRed', domain_min=0, domain_max=1)
>>> tree.draw('c', node_colors=('dist', cmap))

(See https://toyplot.readthedocs.io/en/stable/colors.html#Color-Maps)\
"""

CATEGORICAL_TOO_FEW_CATEGORIES = """Error in (feature, colormap)
Data contains more unique values than contained in the selected CategoricalMap
colormap. Consider selecting a LinearMap instead, such as 'Spectral'.

(See https://toyplot.readthedocs.io/en/stable/colors.html#Color-Maps)\
"""

PALETTE_TOO_FEW_CATEGORIES = """Error in (feature, colormap)
Data contains more unique values than contained in the selected Palette.
Consider selecting a LinearMap instead, such as 'Spectral'.

(See https://toyplot.readthedocs.io/en/stable/colors.html#Color-Maps)\
"""


def get_color_mapped_feature(
    tree: ToyTree,
    feature: str,
    cmap: Union[str, toyplot.color.Map] = None,
    domain_min: Optional[float] = None,
    domain_max: Optional[float] = None,
    nan_value: Optional[float] = None,
    tips_only: bool = False,
    reverse: bool = False,
) -> np.ndarray:
    """Return colors mapped from a named tree feature.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree used to extract values when `data` is a feature name.
    feature: str
        Name of a feature to extract from tree nodes.
    cmap: str or toyplot.color.Map
        A toyplot colormap object or a str name of a colormap.
    domain_min: float or None
        If None the domain will be automatically fit to the data min.
    domain_max: float or None
        If None the domain will be automatically fit to the data max.
    nan_value: float or None
        A value to substitute for any missing (NaN) values. If None
        then NaN values will be mapped to 'transparent'.
    tips_only: bool
        If True then data is only projected and returned for tip Nodes.
    reverse: bool
        Reverse the order of the colormap.

    Returns
    -------
    np.ndarray
        Colors mapped to the entered values.

    Raises
    ------
    ToytreeError
        If `feature` is not a str name or does not exist on the tree.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(4).set_node_data("x", [2, 2, 2, 0, 0, 0, 0])
    >>> colors = toytree.style.get_color_mapped_feature(tree, "x", "Set2")
    >>> len(colors) == tree.nnodes
    True
    >>> tip_colors = toytree.style.get_color_mapped_feature(
    ...     tree, "x", "Set2", tips_only=True
    ... )
    >>> len(tip_colors) == tree.ntips
    True
    """
    if not isinstance(feature, str):
        raise ToytreeError(
            "get_color_mapped_feature() requires feature as a str name. "
            "Use get_color_mapped_values(data=...) for direct value mapping."
        )
    try:
        if tips_only:
            values = tree.get_tip_data(feature).values
        else:
            values = tree.get_node_data(feature).values
    except Exception as exc:
        raise ToytreeError(f"feature '{feature}' not in tree.features.") from exc
    return get_color_mapped_values(
        values, cmap, domain_min, domain_max, nan_value, reverse
    )


def get_color_mapped_values(
    data: pd.Series | Sequence[Any],
    cmap: Union[str, toyplot.color.Map] = None,
    domain_min: Optional[float] = None,
    domain_max: Optional[float] = None,
    nan_value: Optional[float] = None,
    reverse: bool = False,
) -> np.ndarray:
    """Return values mapped to a continuous or discrete color map.

    Parameters
    ----------
    data: pd.Series | Sequence[Any]
        Values to map. If a Series, its index is interpreted as node idx
        labels and values are placed into an array of size max(idx)+1.
        If a Sequence, values are interpreted in positional order.
    cmap: str or toyplot.color.Map
        A toyplot colormap object or a str name of a colormap.
    domain_min: float or None
        If None the domain will be automatically fit to the data min.
    domain_max: float or None
        If None the domain will be automatically fit to the data max.
    nan_value: float or None
        A value to substitute for any missing (NaN) values. If None
        then NaN values will be mapped to 'transparent'.
    reverse: bool
        Reverse the order of the colormap.

    Returns
    -------
    np.ndarray
        Colors mapped to the entered values. Empty input returns an empty array.

    Raises
    ------
    ToytreeError
        If `data` is a plain str or Mapping, if Series index labels are not
        integer-valued, or if colormap input is invalid.

    Examples
    --------
    >>> colors = toytree.style.get_color_mapped_values([2, 2, 2, 0, 0, 0, 0], "Set2")
    >>> len(colors)
    7

    >>> series = pd.Series(["A", "B"], index=[0, 3])
    >>> colors = toytree.style.get_color_mapped_values(series, "Set2")
    >>> len(colors)
    4
    >>> toytree.color.ToyColor(colors[1]) == toytree.color.ToyColor("transparent")
    True

    >>> data = np.array([1.0, np.nan, 2.0])
    >>> colors = toytree.style.get_color_mapped_values(data, "BlueRed")
    >>> toytree.color.ToyColor(colors[1]) == toytree.color.ToyColor("transparent")
    True

    >>> empty = toytree.style.get_color_mapped_values([], "BlueRed")
    >>> len(empty)
    0
    """
    if isinstance(data, str):
        raise ToytreeError(
            "get_color_mapped_values() does not accept plain str data. "
            "Use get_color_mapped_feature(tree, data='feature_name', ...)."
        )
    if isinstance(data, Mapping):
        raise ToytreeError(
            "get_color_mapped_values() does not accept Mapping data. "
            "Enter a Series or Sequence."
        )

    values = _coerce_values_data(data)
    values = np.asarray(values, dtype=object)

    # Empty input always returns empty output, independent of colormap type.
    if values.size == 0:
        return np.array([], dtype=object)

    # Missing-value handling is centralized so all branches treat np.nan, pd.NA,
    # and None consistently, and missing values do not count as categories.
    missing_mask = pd.isna(values)
    valid_mask = ~missing_mask

    # Use Spectral as default map if None provided.
    if cmap is None:
        cmap = "Spectral"

    # store original cmap var before conversion to ColorMap
    cmap_orig = cmap

    # If colormap is a string name, resolve it into a toyplot Map.
    if isinstance(cmap, str):
        # Try categorical brewer maps first.
        try:
            cmap = toyplot.color.brewer.map(
                cmap, domain_min=domain_min, domain_max=domain_max, reverse=reverse
            )
        except KeyError:
            # Then try continuous linear maps.
            try:
                cmap = toyplot.color.linear.map(
                    cmap, domain_min=domain_min, domain_max=domain_max
                )
            except KeyError:
                # Finally try diverging maps.
                try:
                    cmap = toyplot.color.diverging.map(
                        cmap,
                        domain_min=domain_min,
                        domain_max=domain_max,
                        reverse=reverse,
                    )
                except KeyError:
                    msg = (
                        "Invalid colormap arg for (feature, colormap) input.\n"
                        + CMAP_ERROR
                    )
                    raise ToytreeError(msg)

    # If cmap is not already Map/Palette, attempt palette coercion.
    if not isinstance(cmap, (toyplot.color.Map, toyplot.color.Palette)):
        # try converting colormap to a Palette for ndarray or Sequence[Color]
        # and add a transparent color at end to use for np.nan.
        try:
            cmap = toyplot.color.Palette(cmap, reverse=reverse)
            cmap += toyplot.color.Palette(["transparent"])
        except Exception:
            msg = "Invalid colormap arg for (feature, colormap) input.\n" + CMAP_ERROR
            raise ToytreeError(msg)

    # --- colormap is now CategoricalMap, LinearMap or Palette ---

    # If map is Categorical, treat incoming values as categories.
    if isinstance(cmap, toyplot.color.CategoricalMap):
        valid_values = np.asarray(values[valid_mask], dtype=object)
        if valid_values.size:
            categories, valid_codes = np.unique(
                np.array([str(i) for i in valid_values], dtype=object),
                return_inverse=True,
            )
        else:
            categories = np.array([], dtype=object)
            valid_codes = np.array([], dtype=int)

        # Missing values do not consume categorical slots.
        if (cmap.domain.max is not None) and (cmap.domain.max < len(categories)):
            raise ToytreeError(CATEGORICAL_TOO_FEW_CATEGORIES)

        # Recreate brewer maps by observed category count when possible.
        if isinstance(cmap_orig, str) and len(categories):
            try:
                cmap = toyplot.color.brewer.map(
                    cmap_orig,
                    count=len(categories),
                    domain_min=domain_min,
                    domain_max=domain_max,
                    reverse=reverse,
                )
            except KeyError:
                cmap = toyplot.color.brewer.map(
                    cmap_orig,
                    count=max(3, len(categories)),
                    domain_min=domain_min,
                    domain_max=domain_max,
                    reverse=reverse,
                )

        cvalues = np.zeros(values.size, dtype=int)
        cvalues[valid_mask] = valid_codes
        colors = cmap.colors(cvalues)

    # If cmap is an explicit palette, categories index directly into it.
    elif isinstance(cmap, toyplot.color.Palette):
        valid_values = np.asarray(values[valid_mask], dtype=object)
        if valid_values.size:
            categories, valid_codes = np.unique(
                np.array([str(i) for i in valid_values], dtype=object),
                return_inverse=True,
            )
        else:
            categories = np.array([], dtype=object)
            valid_codes = np.array([], dtype=int)

        if len(cmap) < len(categories):
            raise ToytreeError(PALETTE_TOO_FEW_CATEGORIES)

        cvalues = np.zeros(values.size, dtype=int)
        cvalues[valid_mask] = valid_codes
        colors = np.array([cmap.color(int(i)) for i in cvalues])

    # For linear maps, prefer numeric values but fall back to categorical ints.
    else:
        # convert values to floats and fit colormap to data domain
        try:
            cvalues = np.asarray(values, dtype=float)

        # but if data is categorical then convert data to ints
        except (TypeError, ValueError):
            valid_values = np.asarray(values[valid_mask], dtype=object)
            if valid_values.size:
                categories, valid_codes = np.unique(
                    np.array([str(i) for i in valid_values], dtype=object),
                    return_inverse=True,
                )
            else:
                categories = np.array([], dtype=object)
                valid_codes = np.array([], dtype=int)
            cvalues = np.zeros(values.size, dtype=int)
            cvalues[valid_mask] = valid_codes

            # Recreate map using category count when data are non-numeric labels.
            try:
                if isinstance(cmap_orig, str) and len(categories):
                    cmap = toyplot.color.brewer.map(
                        cmap_orig,
                        count=len(categories),
                        domain_min=domain_min,
                        domain_max=domain_max,
                        reverse=reverse,
                    )
            # try to convert linearmap to categorical
            except KeyError:
                cmap = toyplot.color.brewer.map(
                    cmap_orig,
                    count=max(3, len(categories)),
                    domain_min=domain_min,
                    domain_max=domain_max,
                    reverse=reverse,
                )

        # Fit colormap domain to non-missing values only.
        valid_cvalues = np.asarray(cvalues[valid_mask])
        if valid_cvalues.size:
            if cmap.domain.min is None:
                cmap.domain.min = np.nanmin(valid_cvalues)
            if cmap.domain.max is None:
                cmap.domain.max = np.nanmax(valid_cvalues)

        # broadcast values to color map
        colors = cmap.colors(cvalues)

    # Assign missing-value colors in one step using the shared missing mask.
    if missing_mask.any():
        if nan_value is None:
            colors[missing_mask] = ToyColor((0, 0, 0, 0))
        else:
            colors[missing_mask] = cmap.color(nan_value)
    return colors


def _coerce_values_data(data: pd.Series | Sequence[Any]) -> np.ndarray:
    """Return a 1D values array from Series or Sequence input.

    Parameters
    ----------
    data : pandas.Series or Sequence[Any]
        Input values to map into colors.

    Returns
    -------
    numpy.ndarray
        One-dimensional object array. For Series input, values are projected
        into dense idx space from 0 to max(idx), with missing idx positions
        filled by NaN.

    Raises
    ------
    ToytreeError
        If Series index labels are invalid or if input is not one-dimensional.
    """
    # Branch 1: Series input is treated as sparse node-idx keyed values.
    if isinstance(data, pd.Series):
        if data.empty:
            return np.array([], dtype=float)

        # Validate index labels as integer-valued node idx values.
        idx = np.asarray(data.index)
        if np.issubdtype(idx.dtype, np.integer):
            idx = idx.astype(int, copy=False)
        else:
            try:
                idxf = pd.to_numeric(data.index, errors="raise").to_numpy(dtype=float)
            except Exception as exc:
                raise ToytreeError(
                    "Series index must contain integer node idx labels."
                ) from exc
            if np.any(~np.isfinite(idxf)) or np.any(idxf != np.floor(idxf)):
                raise ToytreeError("Series index must contain integer node idx labels.")
            idx = idxf.astype(int)
        if np.any(idx < 0):
            raise ToytreeError("Series index cannot contain negative idx labels.")
        if np.unique(idx).size != idx.size:
            raise ToytreeError("Series index contains duplicate idx labels.")

        # Project sparse values to dense idx space, filling absent idx with NaN.
        values = np.full(int(idx.max()) + 1, np.nan, dtype=object)
        values[idx] = data.to_numpy(dtype=object)
        return values

    # Branch 2: Sequence input is interpreted in positional order.
    values = np.asarray(data, dtype=object)
    if values.ndim != 1:
        raise ToytreeError("data must be one-dimensional.")
    return values


if __name__ == "__main__":
    DATA = [
        np.linspace(0, 1, 7),
        [1, 1, 1, 0, 0, 0, 0],
        [1] * 3 + [np.nan] * 4,
        list("aaabbbb"),
        ["a"] * 3 + [0] + [np.nan] * 3,
    ]

    COLOR_MAPS = [
        "BlueRed",
        "Spectral",
        toyplot.color.brewer.map("BlueRed"),
        "Set2",
    ]

    for idx, values in enumerate(DATA):
        for cmap in COLOR_MAPS:
            print(f"dataset={idx}, colormap={cmap}")
            print(get_color_mapped_values(values, cmap))
