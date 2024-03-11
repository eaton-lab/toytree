#!/usr/bin/env python

"""Convert data to an array of colors.

The function `get_color_mapped_values` can translate a series of numeric
values to a Linear or Categorical color map, and can translate an array
including non-numeric data types to a Categorical color map. In all
cases NaN values are mapped to 'transparent'.
"""

from typing import Union, Optional, Sequence, Any, TypeVar
from loguru import logger
import numpy as np
import toyplot
from toytree.color import ToyColor
from toytree.utils.src.exceptions import ToytreeError

logger = logger.bind(name="toytree")
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
    """Return an array of colors mapped to feature data in a tree.

    Parameters
    ----------
    tree: ToyTree
        A ToyTree to extract feature data from.
    feature: str
        Name of a feature to extract from one or more Nodes in the tree.
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
    """
    assert hasattr(tree, "nnodes"), "first argument must be a ToyTree."
    if tips_only:
        values = tree.get_tip_data(feature).values
    else:
        values = tree.get_node_data(feature).values
    return get_color_mapped_values(values, cmap, domain_min, domain_max, nan_value, reverse)


def get_color_mapped_values(
    values: Sequence[Any],
    cmap: Union[str, toyplot.color.Map] = None,
    domain_min: Optional[float] = None,
    domain_max: Optional[float] = None,
    nan_value: Optional[float] = None,
    reverse: bool = False,
) -> np.ndarray:
    """Return feature mapped to a continuous or discrete color map.

    Raises helpful error messages if user entered the special tuple
    argument incorrectly, or by accident.

    Parameters
    ----------
    values: Series[float]
        A Series of numeric values.
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

    Examples
    --------
    >>> ...
    """
    # Use Spectral as default map if None provided.
    if cmap is None:
        cmap = "Spectral"

    # store original cmap var before conversion to ColorMap
    cmap_orig = cmap

    # if colormap is str then expand to a color.Map
    if isinstance(cmap, str):
        # return as Categorial or LinearMap or...
        try:
            cmap = toyplot.color.brewer.map(cmap, domain_min=domain_min, domain_max=domain_max, reverse=reverse)
        except KeyError:
            # return as LinearMap
            try:
                cmap = toyplot.color.linear.map(cmap, domain_min=domain_min, domain_max=domain_max)
            except KeyError:
                # return as DivergingMap
                try:
                    cmap = toyplot.color.diverging.map(cmap, domain_min=domain_min, domain_max=domain_max, reverse=reverse)
                except KeyError:
                    msg = "Invalid colormap arg for (feature, colormap) input.\n" + CMAP_ERROR
                    raise ToytreeError(msg)

    # if colormap is not Map or Palette (good) then check for messier formats
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

    # if map is Categorical then try to treat data as categorical, or raise error
    if isinstance(cmap, toyplot.color.CategoricalMap):
        # convert data to str, with nan as highest sort str character
        cvalues = [str(i) for i in values]
        cvalues = ["~~" + i if i == "nan" else i for i in cvalues]

        # convert str data to int categories
        categories, cvalues = np.unique(cvalues, return_inverse=True)

        # raise warning if not enough categories for data
        if cmap.domain.max < len(categories):
            # logger.warning(CATEGORICAL_TOO_FEW_CATEGORIES)
            raise ToytreeError(CATEGORICAL_TOO_FEW_CATEGORIES)

        # recreate the map using count of current data
        if isinstance(cmap_orig, str):
            # handle toyplot error that does not allow ncategories=2
            try:
                cmap = toyplot.color.brewer.map(cmap_orig, count=len(categories), domain_min=domain_min, domain_max=domain_max, reverse=reverse)
            # ...HERE...
            except KeyError:
                cmap = toyplot.color.brewer.map(cmap_orig, count=max(3, len(categories)), domain_min=domain_min, domain_max=domain_max, reverse=reverse)                

        # broadcast data to color map
        colors = cmap.colors(cvalues)

    # if cmap is a Palette
    elif isinstance(cmap, toyplot.color.Palette):

        # convert data to int categories
        cvalues = [str(i) for i in values]
        categories, cvalues = np.unique(cvalues, return_inverse=True)

        # raise warning if not enough categories for data
        if len(cmap) < len(categories):
            raise ToytreeError(PALETTE_TOO_FEW_CATEGORIES)

        # broadcast data to color map
        colors = np.array([cmap.color(i) for i in cvalues])

    # if map is Linear (data can be linear or categorial)
    else:

        # convert values to floats and fit colormap to data domain
        try:
            cvalues = np.array(values, dtype=float)

        # but if data is categorical then convert data to ints
        except (TypeError, ValueError):
            cvalues = [str(i) for i in values]
            categories, cvalues = np.unique(cvalues, return_inverse=True)

            # recreate the map using count of current data
            try:
                if isinstance(cmap_orig, str):
                    cmap = toyplot.color.brewer.map(cmap_orig, count=len(categories), domain_min=domain_min, domain_max=domain_max, reverse=reverse)
            # try to convert linearmap to categorical
            except KeyError:
                cmap = toyplot.color.brewer.map(cmap_orig, count=max(3, len(categories) + 1), domain_min=domain_min, domain_max=domain_max, reverse=reverse)                
                # raise ToytreeError(
                #     "Data cannot be colormapped. You selected discrete data but a linear colormap.\n"
                #     f"  data={cvalues[:5]}...\n"
                #     f"  cmap={cmap}.\n"
                #     "Try an alternative cmap such as 'Set2'.\n\n"
                #     "(See https://toyplot.readthedocs.io/en/stable/colors.html#Color-Maps)"
                # ) from exc

        # fit colormap domain to float values or int categories
        if not all(np.isnan(cvalues)):
            if cmap.domain.min is None:
                cmap.domain.min = np.nanmin(cvalues)
            if cmap.domain.max is None:
                cmap.domain.max = np.nanmax(cvalues)

        # broadcast values to color map
        colors = cmap.colors(cvalues)

    # replace color w/ "transparent" for any nan data points. BTW, Broadcasting
    # can't be used here b/c we converted values to a list earlier.
    for idx, value in enumerate(values):
        try:
            if np.isnan(value):
                if nan_value is None:
                    colors[idx] = ToyColor((0, 0, 0, 0))
                else:
                    colors[idx] = cmap.color(nan_value)
                # logger.warning(f"NAN color: {colors[idx]}")
        # skip if type=str or other that cannot be checked for nan.
        except TypeError:
            pass
    return colors


if __name__ == "__main__":

    DATA = [
        np.linspace(0, 1, 7),
        [1, 1, 1, 0, 0, 0, 0],
        [1] * 3 + [np.nan] * 4,
        list("aaabbbb"),
        ['a'] * 3 + [0] + [np.nan] * 3,
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
