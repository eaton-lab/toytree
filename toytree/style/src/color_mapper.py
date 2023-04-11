#!/usr/bin/env python

"""...

"""

from typing import Union
import numpy as np
import toyplot
from toytree.color import ToyColor
from toytree.utils.src.exceptions import StyleColorMappingTupleError

ColorMap = Union[str, toyplot.color.Map]


CMAP_ERROR = """
To find a list of valid colormap names supported by toyplot use:
>>> print(toyplot.color.brewer.names())

You can map feature values to colors by entering (feature, colormap):
>>> tree.draw('c', node_colors=('dist', 'Spectral'))

or, load a colormap as a Map object for finer control:
>>> cmap = toyplot.color.brewer.map('BlueRed', domain_min=0, domain_max=1)
>>> tree.draw('c', node_colors=('dist', cmap))\
"""


def get_color_mapped_feature(values: np.ndarray, cmap: ColorMap) -> np.ndarray:
    """Return feature mapped to a continuous or discrete color map.

    Raises helpful error messages if user entered the special tuple
    argument incorrectly, or by accident.
    """
    # select map from str name and check that Map is valid.
    if isinstance(cmap, str):
        try:
            cmap = toyplot.color.brewer.map(cmap)
        except KeyError as inst:
            raise StyleColorMappingTupleError(
                f"'{cmap}' is an invalid colormap argument for the "
                "special color mapping syntax entered as a tuple, e.g., "
                "(feature, colormap).\n" + CMAP_ERROR
            ) from inst
    if not isinstance(cmap, toyplot.color.Map):
        raise StyleColorMappingTupleError(
            f"'{cmap}' is invalid for the special tuple arg type "
            "(feature, colormap)." + CMAP_ERROR
        )

    # auto-set domains to min and max values if not set on cmap.
    if cmap.domain.min is None:
        cmap.domain.min = np.nanmin(values)
    if cmap.domain.max is None:
        cmap.domain.max = np.nanmax(values)

    # broadcast values to color map
    colors = cmap.colors(values)

    # set colors for nan values to "transparent"
    colors[np.isnan(values)] = ToyColor((0, 0, 0, 0))
    return colors


if __name__ == "__main__":

    DATA = np.linspace(0, 1, 8)
    COLOR_MAPS = [
        (DATA, "BlueRed"),
        (DATA, "Spectral"),
        (DATA, toyplot.color.brewer.map("BlueRed")),
    ]

    for values, cmap in COLOR_MAPS:
        print(get_color_mapped_feature(values, cmap))
