#!/usr/bin/env python

"""...

"""

from typing import Union
from loguru import logger
import numpy as np
import toyplot
from toytree.color import ToyColor
from toytree.utils.src.exceptions import ToytreeError

ColorMap = Union[str, toyplot.color.Map]
logger = logger.bind(name="toytree")


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


def get_color_mapped_feature(values: np.ndarray, cmap: ColorMap) -> np.ndarray:
    """Return feature mapped to a continuous or discrete color map.

    Raises helpful error messages if user entered the special tuple
    argument incorrectly, or by accident.
    """
    # if colormap is str then expand to a color.Map
    if isinstance(cmap, str):
        try:
            cmap = toyplot.color.brewer.map(cmap)
        except KeyError as exc:
            msg = "Invalid colormap arg for (feature, colormap) input.\n" + CMAP_ERROR
            raise ToytreeError(msg) from exc

    # if colormap is not Map or Palette (good) then check for messier formats
    if not isinstance(cmap, (toyplot.color.Map, toyplot.color.Palette)):

        # try converting colormap to a Palette for ndarray or Sequence[Color]
        # and add a transparent color at end to use for np.nan.
        try:
            cmap = toyplot.color.Palette(cmap)
            cmap += toyplot.color.Palette(["transparent"])
        except Exception:
            msg = "Invalid colormap arg for (feature, colormap) input.\n" + CMAP_ERROR
            raise ToytreeError(msg)

    # --- colormap is now CategoricalMap, LinearMap or Palette ---

    # if map is Categorical
    if isinstance(cmap, toyplot.color.CategoricalMap):

        # convert data to str, with nan as highest sort str character
        cvalues = [str(i) for i in values]
        cvalues = ["~~" + i if i == "nan" else i for i in cvalues]

        # convert str data to int categories
        categories, cvalues = np.unique(cvalues, return_inverse=True)

        # raise warning if not enough categories for data
        if cmap.domain.max < len(categories):
            logger.warning(CATEGORICAL_TOO_FEW_CATEGORIES)

        # broadcast data to color map
        colors = cmap.colors(cvalues)

    # if is a Palette
    elif isinstance(cmap, toyplot.color.Palette):

        # convert data to int categories
        cvalues = [str(i) for i in values]

        categories, cvalues = np.unique(cvalues, return_inverse=True)

        # raise warning if not enough categories for data
        if len(cmap) < len(categories):
            raise ToytreeError(PALETTE_TOO_FEW_CATEGORIES)

        # broadcast data to color map
        colors = np.array([cmap.color(i) for i in cvalues])

    # if map is Linear
    else:

        # convert values to floats and fit colormap to data domain
        try:
            cvalues = np.array(values, dtype=float)

        # but if data is categorical then convert data to ints
        except (TypeError, ValueError):
            cvalues = [str(i) for i in values]
            categories, cvalues = np.unique(cvalues, return_inverse=True)

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
                colors[idx] = ToyColor((0, 0, 0, 0))
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
    ]

    for idx, values in enumerate(DATA):
        for cmap in COLOR_MAPS:
            print(f"dataset={idx}, colormap={cmap}")
            print(get_color_mapped_feature(values, cmap))