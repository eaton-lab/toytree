#!/usr/bin/env python

"""Calculate distance matrices from aligned discrete character data.

TODO: use substitution model functions derived from ML code.

Examples
--------
>>> # get DNA alignment matrix
>>> seqs = toytree...
>>>
>>> # get distance matrices
>>> distJC69 = toytree.infer.get_distance_matrix(data, model="JC69")
>>> distF84 = toytree.infer.get_distance_matrix(data, model="F84")
>>> distK2P = toytree.infer.get_distance_matrix(data, model="K2P")

"""

from typing import Union, Optional
import numpy as np
from numpy.typing import ArrayLike
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


def get_expected_distance(
    time: float,
    length: int,
    model: 'MutationModel',
    ) -> pd.DataFrame:
    """Return expected distance between two samples given a subst model.

    """
    raise NotImplementedError("TODO")



####################################################################
##
##
## should these take seqs as input, or diffs???

def get_distance_JC69(seq1: ArrayLike, seq2: ArrayLike) -> float:
    """Return the JC69 distance between two sequences.

    Parameters
    ----------
    seq1: ArrayLike
        A 1-dimensional array of int or str dtype.
    seq2: ArrayLike
        A 1-dimensional array of same size and dtype as seq1.
    """
    return np.sum(seq1 != seq2) / seq1.size


def get_distance_K2P(ntransitions: int, ntransversions: int, length: int) -> float:
    """Return the K2P distance between two sequences...
    """


if __name__ == "__main__":
    pass
