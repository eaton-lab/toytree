#!/usr/bin/env python

"""Function to get data from all Nodes in a tree.

Data is returned as a pandas Dataframe and any value can be imputed
for missing values for Nodes that do not have assigned data for a
feature.
"""

from typing import Union, Sequence, Any, TypeVar, Optional
from loguru import logger
import pandas as pd
import numpy as np
from toytree import ToyTree, Node
from toytree.core.apis import add_toytree_method
# from toytree.utils import ToytreeError

Query = TypeVar("Query", int, str, Node)
logger = logger.bind(name="toytree")


@add_toytree_method(ToyTree)
def get_node_data(
    tree: ToyTree,
    feature: Union[str, Sequence[str], None] = None,
    missing: Union[Any, Sequence[Any], None] = None,
) -> Union[pd.DataFrame, pd.Series]:
    """Return a pandas Series or DataFrame with values for one or
    more selected features in the tree.

    This function is convenient for accessing data in tabular
    format, but is slower than accessing data directly from Nodes,
    for example during a traversal, because it spends time checking
    for Nodes with missing values and type-checking missing values.
    See Documentation for accessing data from Nodes.

    Setting complex objects to Node data, such as lists or sets,
    rather than float, int, or str, should generally work fine,
    but beware that this function will not attempt to automatically
    check or fill missing values for these data.

    See Also: `get_feature_dict`, `set_node_data`, `get_tip_data`.

    Parameters
    ----------
    feature: str, Sequence[str], or None
        One or more features of Nodes to get data for. Features
        include the default Node features (idx, name, height, dist,
        support) as well as any attribute that has been set to
        a Node (except attrs with names that start with an '_'.)
    missing: Any, Sequence[Any], or None
        A value to use for missing data (Nodes that do not have
        the feature). Default arg is None which will automatically
        set missing data to `np.nan`. Example: you can set the
        missing values to a default value like 0 for an int feature
        or by entering 0, or you can enter a list of values to
        set default missing for all features.

    Returns
    -------
    pd.DataFrame or pd.Series
        If a single feature is selected then a pd.Series will be
        returned with tip node 'idx' attributes as the index.
        If multiple features are selected (or None, which selects
        all features) then a pd.DataFrame is returned with tip
        node 'idx' attributes as the index and feature names as
        the column labels.

    Examples
    --------
    Add a new feature to some nodes and fetch data for all nodes.
    >>> tree = toytree.rtree.unittree(10)
    >>> tree = tree.set_node_data("trait1", {0: "A", 1: "B"})
    >>> tree = tree.set_node_data("trait2", {2: 3.5, 3: 5.0})
    >>> data1 = tree.get_tip_data(feature="trait1", missing="C")
    >>> data2 = tree.get_tip_data(feature="trait2")
    """
    # Note: tried storing missing as pd.NA which allows not having to
    # convert the dtype of other values from e.g., int to float. BUT, if
    # <NA> gets converted to a string for plottig it causes total havoc
    # on the HTML. And anyways it looks weird to have a mix of NaN
    # and <NA> in the data table. So I chose np.nan instead of pd.NA.
    # Also pd.NA is very slow compared to np.nan.

    # TODO: AVOID FORMATTING FOR COMPLEX FEATURE TYPES (E.G., DICT, SET, ETC).

    # select one or more features to fetch values for
    if feature is None:
        features = tree.features
    elif isinstance(feature, (list, tuple)):
        features = feature
    else:
        features = [feature]

    # create a list of missing values for subs
    if missing is None:
        missing = [np.nan] * len(features)
    elif isinstance(missing, (list, tuple)):
        assert len(missing) == len(features), (
            "when entering multiple missing values it must be the same "
            "length as the number of features")
    else:
        missing = [missing] * len(features)

    # check for bad user features
    for feat in features:
        if feat not in tree.features:
            raise ValueError(f"feature '{feature}' not in tree.features.")

    # store as ordered lists, and let pd.Series convert to dtype
    data = {}
    for fidx, feat in enumerate(features):

        # fill ordered list with Node value or missing value
        ofeat = []
        miss = missing[fidx]

        # if miss is None then find auto-filling type. This is
        # quite slow (milliseconds) making this not the recommended
        # method for quick data fetching, as explained in docs.
        # if miss is None:
        #     values = [getattr(self[nidx], feat, None) for nidx in range(self.nnodes)]
        #     types = [type(i) for i in values if i is not None]

        # get value or set to missing
        for nidx in range(tree.nnodes):
            value = getattr(tree[nidx], feat, miss)

            # if the actual value is nan then replace with miss
            try:
                if np.isnan(value):
                    value = miss
            except (TypeError, ValueError):
                pass
            ofeat.append(value)

        # allow pandas to infer dtype
        series = pd.Series(ofeat)

        # store Series to a dict
        data[feat] = series

    # if a single feature was selected return as a Series else DataFrame
    if len(features) == 1:
        return series
    return pd.DataFrame(data)


@add_toytree_method(ToyTree)
def get_tip_data(
    tree: ToyTree,
    feature: Union[str, Sequence[str], None] = None,
    missing: Optional[Any] = None,
) -> pd.DataFrame:
    """Return a DataFrame with values for one or more selected
    features from every leaf node in the tree.

    Parameters
    ----------
    feature: str, Iterable[str], or None
        One or more features of Nodes to get data for.
    missing: Any
        A value to use for missing data (nodes that do not have
        the feature). Default arg is None which will automatically
        select a missing value based on the data type. Example:
        "" for str type, np.nan for numeric or complex types.
        Any value can be entered here to replace missing data.

    Returns
    -------
    data: pd.DataFrame or pd.Series
        If a single feature is selected then a pd.Series will be
        returned with tip node 'idx' attributes as the index.
        If multiple features are selected (or None, which selects
        all features) then a pd.DataFrame is returned with tip
        node 'idx' attributes as the index and feature names as
        the column labels.

    Examples
    --------
    Add a new feature to some nodes and fetch data for all nodes.
    >>> tree = toytree.rtree.unittree(10)
    >>> tree = tree.set_node_data("trait1", {0: "A", 1: "B"})
    >>> tree = tree.set_node_data("trait2", {2: 3.5, 3: 5.0})
    >>> data1 = tree.get_tip_data(feature="trait1", missing="C")
    >>> data2 = tree.get_tip_data(feature="trait2")

    See Also
    --------
    get_feature_dict
        Get a dict mapping any node feature to another.
    set_node_data
        Set a feature value to one or more Nodes in a ToyTree.

    Note
    ----
    This function is convenient for accessing data in tabular
    format, but is slightly slower than accessing data directly
    from Nodes because it spends time type-checking missing data.
    """
    return tree.get_node_data(feature, missing).iloc[:tree.ntips]


if __name__ == "__main__":

    import toytree
    toytree.set_log_level("INFO")

    tree = toytree.rtree.unittree(ntips=10)

    # tree = tree.set_node_data("x", {11: "red"}, default="blue", inherit=True)
    # print(get_node_data(tree, 'x'))

    tree = tree.set_node_data("x", {11: "red"}, inherit=True)
    print(get_node_data(tree, 'x', missing='red'))
