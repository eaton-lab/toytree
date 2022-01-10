#!/usr/bin/env python

"""Distance-based tree inference functions.

"""

from typing import Union
import numpy as np
import pandas as pd
from scipy import spatial
import toytree


def get_distance_matrix(
    data: Union[np.ndarray, pd.DataFrame]) -> pd.DataFrame:
    """Return pairwise distances between samples from a data matrix.

    D measured between samples represents the Euclidean distance, 
    also termed the Minkowski distance with p=2, and is calculated
    under the hood using `scipy.distance`.

    Note
    ----
    This method does not currently support missing data. Any missing
    values should be imputed before using.

    Data should be quantitative (e.g., trait measurements) or binary,
    however, multi-state characters (e.g., DNA sequences) should use
    the option ...

    Examples
    --------
    >>> 
    >>> 
    """
    return pd.DataFrame(spatial.distance_matrix(data, data))


def infer_upgma_tree_from_distance_matrix(
    data: Union[np.ndarray, pd.DataFrame]) -> toytree.ToyTree:
    """Return a ToyTree inferred by UPGMA on a distance matrix.

    Unweighted pairwise grouping by mm average....
    """
    return DistanceTree(data, method="upgma")


if __name__ == "__main__":
    pass
