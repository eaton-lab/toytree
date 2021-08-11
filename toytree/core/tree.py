#!/usr/bin/env python

"""
The core ToyTree class object and class constructor function (.tree)

Nearly all API functions are accessible from a ToyTree, including
tree i/o, modifications, drawing, and analysis.

TODO: Test for speed improvements:
- fixed-order and tip-labels colors together
- node_colors supports colormap (docstring link to plot docs)
- reduce deepcopies (in ToyTree done)
- reduce traversals.
- .write w/ feature support.
- use set_node_heights in set_node_feature('heights')
"""

# pylint: disable=too-many-lines, too-many-public-methods, invalid-name
# pylint: disable=inconsistent-return-statements, too-many-branches

import copy
from typing import (
    Union, Optional, Mapping, Iterable, List, Dict, Tuple, Set, Any
)
from pathlib import Path
from loguru import logger
import numpy as np
import toyplot
import pandas as pd

from toytree.core.treenode import TreeNode
from toytree.core.node_assist import NodeAssist
from toytree.core.drawing.coords import Coords
from toytree.core.style.tree_style import TreeStyle
from toytree.core.drawing.render import ToytreeMark
from toytree.core.drawing.draw_toytree import draw_toytree
from toytree.core.io.TreeParser import TreeParser
from toytree.core.io.TreeWriter import NewickWriter
from toytree.utils.exceptions import ToytreeError
from toytree.mod.rooting import Rooter
import toytree.mod.api
import toytree.pcm.api
import toytree.distance.api

# PEP 484 recommend capitalizing alias names
Url = str

class TreeBase:
    def __init__(self, treenode:Optional[TreeNode]=None):
        self.treenode = treenode
        self.mod = toytree.mod.api.TreeModAPI(self)
        self.pcm = toytree.pcm.api.PhyloCompAPI(self)
        self.distance = toytree.distance.api.DistanceAPI(self)
        self.style = TreeStyle()


class ToyTree(TreeBase):
    """
    ToyTree class object Type.

    To initialize a ToyTree instance it is recommended to use
    the general class constructor function `toytree.tree()`.
    """
    def __init__(self, treenode: TreeNode):
        super().__init__(treenode)

        # filled by Coords
        self.nnodes: int = 0
        self.ntips: int = 0
        self.idx_dict: Mapping[int,TreeNode] = {}

        # compile coords
        self._coords: np.ndarray = Coords(self)
        self._coords.update()

    def __str__(self) -> str:
        """ return ascii tree ... (not sure whether to keep this) """
        return self.treenode.__str__()

    def __repr__(self) -> str:
        """string representation of a ToyTree object"""
        return (
            f"<ToyTree rooted={self.is_rooted()}, "
            f"ntips={self.ntips}, "
            f"features={sorted(self.features)}>"
        )

    def __len__(self) -> int:
        """ return len of treenode (ntips) """
        return self.ntips

    @property
    def features(self) -> set:
        """
        Returns a set of all features assigned as attributes to any
        TreeNodes in the Toytree by using .set_node_values().
        """
        feats = set()
        for node in self.treenode.traverse():
            feats.update(node.features)
        return feats

    @property
    def newick(self) -> str:
        """
        Returns a newick representation of the tree, the same as
        calling .write() with default arguments.
        """
        return self.write()

    def write(
        self,
        path:Optional[Path]=None,
        tree_format:int=0,
        features:Optional[List[str]]=None,
        dist_formatter:str="%0.6g",
        ) -> Optional[str]:
        """
        Write newick string representation of the tree with formatting
        options to include branch or node features according to the
        ete3 tree formats.

        See also: write_nexus(), write_extended()

        Parameters:
        -----------
        path: (str):
            A string file name to write output to. If None then newick is
            returned as a string.
        tree_format (int):
            Format of the newick string. See ete3 tree formats. Default=0.
        features (List):
            Features of treenodes that should be written to the newick string
            in NHX format. Examples include "height", "idx", or other features
            you may have saved to treenodes.
        """
        if not self.ntips:
            raise ToytreeError("tree is empty")
        if features is not None:
            if not isinstance(features, (list, tuple)):
                features = [features]

        # get newick string
        writer = NewickWriter(
            treenode=self.treenode,
            tree_format=tree_format,
            features=features,
            dist_formatter=dist_formatter,
        )
        newick = writer.write_newick()

        # write to file or return as string
        if path is None:
            return newick
        with open(path, 'w') as out:
            out.write(newick)
            return None

    def get_edges(self) -> np.ndarray:
        """
        Returns an array with paired edges (parent, child) as
        node indices. This array is primarily for internal use.
        """
        return self._coords.edges

    def get_mrca_idx_from_tip_labels(
        self,
        names:Iterable[str]=None,
        wildcard:str=None,
        regex:str=None,
        ) -> int:
        """
        Returns the node idx label of the most recent common ancestor
        node for the clade that includes the selected tips. Arguments
        can use fuzzy name matching: a list of tip names, wildcard
        selector, or regex string.
        """
        nas = NodeAssist(self, names, wildcard, regex)
        return nas.get_mrca().idx

    def get_node_descendant_idxs(self, idx:int) -> List[int]:
        """
        Returns a node idx and all of its descendants node idxs.
        """
        descs = [i.idx for i in self.idx_dict[idx].get_descendants()]
        descs.append(idx)
        return descs

    # def set_node_values(
    #     self,
    #     feature:str,
    #     mapping:Dict[Union[int,str],Any]=None,
    #     default:Any=None,
    #     **kwargs,
    #     ) -> 'toytree.ToyTree':
    #     """
    #     DEPRECATED: see set_node_data()

    #     Set values to a TreeNode feature and RETURNS A COPY of the
    #     toytree.

    #     If the feature is set to only some nodes then others are set
    #     to NaN. You cannot set the "idx" feature (this is used
    #     internally by toytree). You can set base features like name,
    #     dist, height, support, or create any new named feature.

    #     Example:
    #     --------
    #     tre.set_node_values(feature="Ne", default=5000)
    #     tre.set_node_values(feature="Ne", mapping={0:1e5, 1:1e6, 2:1e3})
    #     tre.set_node_values(feature="Ne", mapping={0:1e5, 1:1e6}, default=5000)
    #     tre.set_node_values(feature="Ne", mapping={'r0':1e5, 'r1':1e6})
    #     tre.set_node_values(feature="state", mapping={0: "A", 1: "B"})

    #     Parameters:
    #     -----------
    #     feature (str):
    #         The name of the node attribute to modify (cannot be 'idx').
    #     mapping (dict):
    #         A dictionary of {int: value} or {str: value}, where int
    #         keys will be interpreted as node idx labels, and str keys
    #         will be interpreted as node name labels.
    #         Note: use tree.draw(node_labels='idx') to see idx labels.
    #     default (int, str, float):
    #         You can use a default value to be filled for all other
    #         nodes not listed in the 'mapping' dictionary.

    #     Returns:
    #     ----------
    #     A ToyTree object is returned with the node values modified.
    #     """
    #     logger.warning(
    #         "The set_node_values() function is deprecated.\n"
    #         "It is replaced by the function .set_node_data(), which "
    #         "performs the same exact action,\nbut is more appropriately "
    #         "named, and is paired with the get_node_data() function."
    #     )
    #     self.set_node_data(feature, mapping, default, **kwargs)

    # def get_node_labels_formatted(
    #     self,
    #     feature: str,
    #     formatter: Callable = None,
    #     # mask: Optional[Iterable[bool]] = None,
    #     ) -> List[str]:
    #     """
    #     Returns a list of string formatted values from a selected
    #     node feature in node idx order (tips to root) for formatting
    #     floats, ints, etc to prettier values for displaying as node
    #     labels in tree drawings.

    #     See also: get_node_data

    #     Parameters:
    #     -----------
    #     feature: str
    #         The feature of one or more nodes that you wish to extact
    #         node labels data for.
    #     mask: Iterable[bool]
    #         A boolean mask in idx order where True sets a node label
    #         to an empty string ("") so it is hidden.
    #     formatter: Callable
    #         A function (or lambda func) for formatting strings.

    #     Examples:
    #     ----------
    #     # get and show node names as node labels
    #     tre.draw(node_labels="name")

    #     # same: get and show node names as node labels
    #     tre.draw(node_labels=tree.get_node_labels_formatted("name"))

    #     # apply formatting to convert support to percentages
    #     tre.draw(
    #         node_labels=tree.get_node_labels_formatted(
    #             feature="support",
    #             formatter=lambda x: f"{(float(x) / 100):.2f}",
    #         )
    #     )

    #     # show only nodes and node_labels where support <= 90
    #     tre.draw(
    #         node_mask=tre.get_node_data("support") > 90,
    #         node_labels="support",
    #         node_sizes=18,
    #     )
    #     """
    #     # get node data for all features. This is a DataFrame where a
    #     # feature column can be of mixed or single dtypes.
    #     data = self.get_node_data()

    #     # raise exception if feature is missing, or all values are NAN
    #     if feature not in data.columns:
    #         data[feature] = [feature] * self.nnodes
    #         # raise ToytreeError("feature does not exist for any nodes in tree.")
    #     if data[feature].isna().all():
    #         raise ToytreeError("feature does not exist for any nodes in tree.")

    #     # get a list of values as strs: ['A', 'B', '', ' ', ' ', ...]
    #     # 'x' = show marker and label
    #     # ' ' = show marker with empty label
    #     # ''  = hide/mask node marker and label
    #     labels = [""] * self.nnodes
    #     for nidx in range(self.nnodes):
    #         value = data.loc[nidx, feature]

    #         # float NAN -> ""
    #         if isinstance(value, float):
    #             if np.isnan(value):
    #                 value = ""
    #             else:
    #                 # trim trailing zeros from floats
    #                 value = round(value, 8)
    #                 if not Decimal(value) % 1:
    #                     value = str(int(value))

    #         # empty strings show as empty strings
    #         labels[nidx] = str(value)

    #     # mask/hide tips and root
    #     if not show_root:
    #         labels[-1] = ""
    #     if not show_tips:
    #         for i in range(self.ntips):
    #             labels[i] = ""

    #     # also hide any True indices in mask argument
    #     if mask is not None:
    #         if isinstance(mask, (pd.DataFrame, pd.Series)):
    #             mask = mask.values
    #         if isinstance(mask, (tuple, list)):
    #             mask = np.array(mask).astype(bool)
    #         assert mask.size == len(labels), (
    #             f"mask must be nnodes is size ({self.nnodes})")
    #         assert mask.dtype == np.bool_, (
    #             "mask must contain only boolean types")
    #         for idx, val in enumerate(mask):
    #             if not val:
    #                 labels[idx] = ""

    #     # apply formatter lambda func to all non-hidden label strings
    #     if formatter is not None:
    #         labels = [
    #             str(formatter(i)) if i not in ("", " ") else i
    #             for i in labels
    #         ]
    #     return labels

    def get_node_coordinates(
        self,
        layout: str=None,
        use_edge_lengths: bool=True,
        ) -> pd.DataFrame:
        """
        Returns coordinates of nodes in a tree drawing for a given 
        layout as a pandas.DataFrame. See also get_tip_coordinates().

        Parameters
        ----------
        layout: str
            A layout for the tree drawing ('r', 'l', 'u', 'd', 'c')
        use_edge_lengths: bool
            If False then edge lenghts (dists) are all set to 1.
        """
        # if layout argument then set style and update coords.
        if layout is None:
            layout = self.style.layout
        if layout == 'c':
            table = self._coords.get_radial_coords(use_edge_lengths)
        table = self._coords.get_linear_coords(layout, use_edge_lengths)
        return pd.DataFrame(
            data=table, index=range(table.shape[0]), columns=list('xy')
        )

    def get_feature_dict(
        self,
        key_feature: Optional[str]=None,
        values_feature: Optional[str]=None,
        ) -> Dict:
        """
        Returns a dictionary mapping one or more selected node
        features to each other, or to TreeNodes (by entering None).
        For example you can create a dictionary mapping names
        to TreeNodes, or 'idx' to 'dist' features. The feature must
        be present for all nodes. For convenient functions for
        working with missing data on some nodes see .get_node_data().

        Parameters:
        -----------
        key_feature: Union[str, None]
            Select a node feature or None (TreeNode) to serve as
            keys of the returned dictionary.
        values_feature: Union[str, None]
            Select a node feature or None (TreeNode) to serve as
            values of the returned dictionary.

        Examples:
        --------
        tree.get_feature_dict("idx", "name")
        tree.get_feature_dict("name", None)
        tree.get_feature_dict(None, "dist")
        """
        ndict = {}
        try:
            for node in self.idx_dict.values():
                if key_feature is not None:
                    key = getattr(node, key_feature)
                else:
                    key = node
                if values_feature is not None:
                    value = getattr(node, values_feature)
                else:
                    value = node
                ndict[key] = value
        except AttributeError as exc:
            raise ToytreeError(
                f"feature_dict cannot build {key_feature} -> {values_feature} "
                "because one or\nmore of the selected features is not assigned "
                "to every TreeNode.\nSee .get_node_data() for working with "
                "missing values."
            ) from exc

        # check that keys were not duplicated
        if len(ndict) != self.nnodes:
            raise ToytreeError(
                f"feature_dict cannot be built because {key_feature} "
                "does not have unique values which are required to act "
                "as keys of a dictionary.")
        return ndict

    def get_tip_coordinates(
        self,
        layout:str=None,
        use_edge_lengths:bool=True,
        ) -> pd.DataFrame:
        """
        Returns coordinates of the tip positions for a tree. If no argument
        for axis then a 2-d array is returned. The first column is the x
        coordinates the second column is the y-coordinates. If you enter an
        argument for axis then a 1-d array will be returned of just that axis.
        """

        # one could imagine a very simple method like this, but to accomodate
        # circ and unrooted layout we'll want a better option.
        # return np.arange(self.ntips) + self.style.xbaseline + ybase...

        # if no layout provided then use current style
        if layout is None:
            layout = self.style.layout

        # get coordinates array
        coords = self.get_node_coordinates(layout, use_edge_lengths)
        return coords[:self.ntips]

    def get_tip_labels(self, idx:Optional[int]=None) -> List[str]:
        """
        Returns tip labels (node .name features) for all tips in tree,
        or optionally for just those descended from a selected node
        idx. Tip labels are returned in node idx order from lowest to
        highest.

        Parameters:
        -----------
        idx: returns a list of names for all tips descended from
        node with index idx. Draw with node_labels='idx' to find.
        """
        if idx is not None:
            tip_nodes = self.idx_dict[idx].get_leaves()
            tip_nodes = sorted(tip_nodes, key=lambda x: x.idx)
            return [i.name for i in tip_nodes]
        return [self.idx_dict[idx].name for idx in range(self.ntips)]

    def get_tip_data(
        self,
        feature:Union[str, Iterable[str], None]=None,
        missing: Optional[Any]=pd.NA,
        ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame with values for the selected
        feature at every tip node with tip names as the index.
        If a node does not have the feature its value is pd.NA.

        Parameters:
        -----------
        feature: Union[str, Iterable[str], None]
            One or more features of terminal TreeNodes in the tree
            for which to return data from in an idx ordered DataFrame.
        missing: Any
            A value to use for missing data. Default is pd.NA.

        Example:
        --------
        tree.get_tip_data("support")

        See Also:
        ---------
        - get_feature_dict
        - set_node_values
        - get_node_data
        """
        if feature is None:
            data = pd.DataFrame(
                index=range(self.ntips),
                columns=self.features,
                data=[[
                    getattr(self.idx_dict[nidx], feature, pd.NA)
                    for feature in self.features
                ] for nidx in range(self.ntips)],
            )
            if missing is not None:
                data = data.where(data.notnull(), missing)
            else:
                data = data.where(data.notnull(), np.nan)
        elif feature in self.features:
            data = pd.Series(
                index=range(self.ntips),
                data=[
                    getattr(self.idx_dict[nidx], feature, pd.NA)
                    for nidx in range(self.ntips)
                ])
            if missing is not None:
                data = data.where(data.notnull(), missing)
            else:
                if data.dtype == "O":
                    data = data.where(data.notnull(), "")
                else:
                    data = data.where(data.notnull(), np.nan)
        else:
            raise ValueError(f"feature not in tree data: {feature}")
        return data

    def get_node_data(
        self,
        feature: Union[str, Iterable[str], None]=None,
        missing: Optional[Any]=None,
        ) -> Union[pd.DataFrame, pd.Series]:
        """
        Returns a pandas DataFrame with values for the selected
        feature at every node with idx labels as the index.
        If a node does not have the feature its value is filled
        with missing (see details below).

        Parameters:
        -----------
        feature: Union[str, Iterable[str], None]
            One or more features of terminal TreeNodes in the tree
            for which to return data from in an idx ordered DataFrame.
        missing: Any
            A value to use for missing data (nodes that do not have
            the feature). Default arg is None which will automatically
            select a missing value based on the data type. Example:
            "" for str type, np.nan for numeric or complex types.
            Any object can be entered to replace missing data.

        Note:
        -----
        This function is convenient for accessing data in tabular
        form, but for time-sensitive operations it is much slower
        than accessing data from TreeNodes directly by indexing
        .idx_dict or using a dict from .get_feature_dict().

        Example:
        --------
        tree = toytree.rtree.unittree(10)

        # show marker and labels for a subset of nodes
        tree = tree.set_node_data("new_trait", {9: "A", 10: "B"})
        nlabels = tree.get_node_data("new_trait", missing="")
        tree.draw(
            node_mask=nlabels == "",
            node_labels=nlabels,
            node_sizes=20,
        )

        # show string formatted (.2f) support node labels
        formatted_nlabels = tree.get_node_data("support").apply(
            lambda x: f"{(x / 100):.2f}"))
        tree.draw(
            node_labels=formatted_nlabels,
            node_sizes=20,
        )

        See Also:
        ---------
        - get_feature_dict
        - get_tip_data
        """
        # return a DataFrame for all features
        if feature is None:
            data = pd.DataFrame(
                index=range(self.nnodes),
                columns=self.features,
                data=[[
                    getattr(self.idx_dict[nidx], feature, np.nan)
                    for feature in self.features
                ] for nidx in range(self.nnodes)],
            )
            if missing is not None:
                data = data.where(data.notnull(), missing)
            else:
                data = data.where(data.notnull(), np.nan)

        # return a Series for a single feature
        elif feature in self.features:
            data = pd.Series(
                index=range(self.nnodes),
                name=feature,
                data=[
                    getattr(self.idx_dict[nidx], feature, np.nan)
                    for nidx in range(self.nnodes)
                ])
            if missing is not None:
                data = data.where(data.notnull(), missing)
            else:
                if data.dtype == "O":
                    data = data.where(data.notnull(), "")
                else:
                    data = data.where(data.notnull(), np.nan)
        else:
            raise ValueError(f"feature not in tree data: {feature}")
        return data

    def set_node_data(
        self,
        feature: str,
        mapping: Dict[Union[int,str],Any]=None,
        default: Any=None,
        inherit: bool=False,
        ) -> 'toytree.ToyTree':
        """
        Create or modify features of TreeNodes in a ToyTree to store
        data. This returns a modified copy of the ToyTree.

        If the feature is set on only some nodes then the value for
        others will be set to np.nan. Some features used internally
        are protected from modification (e.g., idx, up, children),
        but other base features such as name, dist, height, and
        support can be modified. Changing 'dist' or 'height' features
        will change the edge lengths of the tree.

        Example:
        --------
        tre.set_node_data(feature="Ne", default=5000)
        tre.set_node_data(feature="Ne", mapping={0:1e5, 1:1e6, 2:1e3})
        tre.set_node_data(feature="Ne", mapping={0:1e5, 1:1e6}, default=5000)
        tre.set_node_data(feature="Ne", mapping={'r0':1e5, 'r1':1e6})
        tre.set_node_data(
            feature="state",
            mapping={10: "A", 11: "B"},
            inherit=True,
        )

        Parameters:
        -----------
        feature: str
            The name of the node attribute to modify (cannot be 'idx').
        mapping: Dict
            A dictionary of {int: value} or {str: value}, where int
            keys will be interpreted as node idx labels, and str keys
            will be interpreted as node name labels.
            Note: use tree.draw(node_labels='idx') to see idx labels.
        default: Any
            You can use a default value to be filled for all other
            nodes not listed in the 'mapping' dictionary.
        inherit: bool
            If inherit is True then feature values are mapped to the
            selected nodes as well as to all of their descendant
            nodes. Note that the order of entries in mapping can
            affect the values applied if multiple selected nodes
            overlap in their descendants.

        Returns:
        ----------
        A ToyTree object is returned with node features modified.
        """
        if feature in ["idx", "up", "children"]:
            raise ToytreeError(f"cannot modify {feature} values.")

        # make a copy and shortcut to idx_dict
        nself = self.copy()

        # fill ndict with map {TreeNode: newvalue}
        mapping = mapping if mapping is not None else {}
        ndict = {}
        for key in mapping:

            # map value to node
            value = mapping[key]
            if isinstance(key, int):
                node = nself.idx_dict[key]
            else:
                node = NodeAssist(nself, key, None, None).get_mrca()
            ndict[node] = value

            # map value to node's descendants
            if inherit:
                descendants = nself.get_node_descendant_idxs(node.idx)
                for didx in descendants:
                    node = nself.idx_dict[didx]
                    ndict[node] = value

        # fill ndict with map {node: default} for nodes not in ndict
        if default is not None:
            for idx in range(nself.nnodes):
                node = nself.idx_dict[idx]
                if node not in ndict:
                    ndict[node] = default

        # special mod submodule method for height modifications
        if feature == "height":
            height_map = {i: j for (i, j) in ndict.items() if j is not None}
            return nself.mod.set_node_heights(height_map)

        # add value to TreeNodes as a feature
        for node in ndict:
            value = ndict[node]
            if hasattr(value, 'copy'):
                node.add_feature(feature, value.copy())
            else:
                node.add_feature(feature, value)
        return nself

    def copy(self, deepcopy: bool=True) -> 'ToyTree':
        """
        Returns a copy of a ToyTree instance. You can use the fast
        version (deepcopy=False) unless you wish to copy custom
        node features that are stored as a complex type (e.g., not
        str, int, float).
        """
        if deepcopy:
            return copy.deepcopy(self)

        # Avoids recursion errors in TreeNode
        # copy treenodes w/ topology and basic features only.
        nself = ToyTree(self.treenode._clone())
        nself.style = self.style.copy()
        return nself

    def is_rooted(self) -> bool:
        """
        Returns False if the tree is unrooted.
        """
        if len(self.treenode.children) > 2:
            return False
        return True

    def is_bifurcating(self, include_root:bool=True) -> bool:
        """
        Returns False if there is a polytomy in the tree, including
        if the tree is unrooted (basal polytomy), unless you use the
        include_root=False argument, in which case it checks only
        non-root nodes.
        """
        if include_root:
            return any(len(i) > 2 for i in self.idx_dict.values())
        return any(
            len(self.idx_dict[i]) > 2 for i in self.idx_dict
            if not self.idx_dict[i].is_root()
        )

    def ladderize(self, direction:bool=False) -> 'ToyTree':
        """
        Ladderize tree (order descendants) so that left/right child
        has fewer/more descendants. To reverse this pattern use
        direction=1. To also ladderize cherry tipnames use alphanumeric.
        """
        # TODO: alphanumeric ordering option?
        nself = self.copy()
        nself.treenode.ladderize(direction=direction)
        nself._coords.update()
        return nself

    def collapse_nodes(
        self,
        min_dist: float=1e-6,
        min_support: float=0,
        ) -> 'ToyTree':
        """
        Returns a copy of the ToyTree with internal node dists
        <= min_dist removed, resulting in a collapsed tree.

        Examples:
        ----------
        newtre = tre.collapse_nodes(min_dist=0.001)
        newtre = tre.collapse_nodes(min_support=50)
        """
        nself = self.copy()
        for node in nself.treenode.traverse():
            if not node.is_leaf():
                if (node.dist <= min_dist) | (node.support < min_support):
                    node.delete()
        nself._coords.update()
        return nself

    def prune(
        self,
        names:List[str]=None,
        wildcard:str=None,
        regex:str=None,
        ) -> 'ToyTree':
        """
        Returns a copy of a subtree of the existing tree that includes
        only the selected tips and minimal edges needed to connect
        them, i.e., it does not enforce keeping the root unless the
        relationships among the pruned tips spans the root node.

        Tip names can be selected using either names, wildcard or regex.

        Parameters:
        -----------
        names: list of tip names.
        wildcard: a string to match using wildcard characters like *
        regex: a regular expression to match multiple names.

        Examples:
        ---------
        tre = toytree.rtree.imbtree(ntips=15)
        ptre = tre.prune(names=['r1', 'r2', 'r3', 'r6'])
        ptre = tre.prune(regex='r[0-3]$')

        Returns:
        ----------
        ToyTree
        """
        # make a deepcopy of the tree
        nself = self.copy()

        # return if nothing to drop
        if not any([names, wildcard, regex]):
            raise ToytreeError("must enter a selector argument.")

        # get matching names list with fuzzy match
        nas = NodeAssist(nself, names, wildcard, regex)
        tipnames = nas.get_tipnames()

        if len(tipnames) == len(nself):
            raise ToytreeError("You cannot drop all tips from the tree.")

        if not tipnames:
            raise ToytreeError("No tips selected.")

        nself.treenode.prune(tipnames, preserve_branch_length=True)
        if len(nself.treenode) == 1:
            nself.treenode = nself.treenode.children[0].detach()
        nself._coords.update()
        return nself

    def drop_tips(
        self,
        names:Iterable[str]=None,
        wildcard:str=None,
        regex:str=None,
        ) -> 'ToyTree':
        """
        Returns a copy of the ToyTree with the selected tips (and any
        empty internal nodes) removed while retaining the original
        edge lengths between remaining nodes.

        The tip names to remove can be selected as a list of names,
        by a shared string in their names (wildcard), or using a
        regular expression to match multiple names (regex).

        See also: .prune() to extract subtree from tree.

        Parameters:
        -----------
        names: list of tip names.
        wildcard: a string to match using wildcard characters like *
        regex: a regular expression to match multiple names.

        Examples:
        ----------
        tre = toytree.rtree.imbtree(ntips=15)
        ptre = tre.drop_tips(names=['r1', 'r2', 'r3', 'r6'])
        ptre = tre.drop_tips(wildcard='r1')
        ptre = tre.drop_tips(regex='r[0-9]$')

        Returns:
        ----------
        toytree.Toytree.ToyTree
        """
        # make a deepcopy of the tree
        nself = self.copy()
        if not any([names, wildcard, regex]):
            raise ToytreeError("must enter a selector argument.")

        # get matching names list with fuzzy match
        nas = NodeAssist(nself, names, wildcard, regex)
        tipnames = nas.get_tipnames()

        if len(tipnames) == len(nself):
            raise ToytreeError("You cannot drop all tips from the tree.")

        if not tipnames:
            raise ToytreeError("No tips selected.")

        keeptips = [i for i in nself.get_tip_labels() if i not in tipnames]
        nself.treenode.prune(keeptips, preserve_branch_length=True)
        nself._coords.update()
        return nself

    def rotate_node(
        self,
        names:Optional[List[str]]=None,
        wildcard:Optional[str]=None,
        regex:Optional[str]=None,
        idx:Optional[int]=None,
        ) -> 'ToyTree':
        """
        Returns a ToyTree with the selected node rotated for plotting.
        A node can be selected by one of multiple options.
        """
        nself = self.copy()
        if idx is None:
            nas = NodeAssist(nself, names, wildcard, regex)
            nself.idx_dict[nas.get_mrca().idx].children.reverse()
        else:
            nself.idx_dict[idx].children.reverse()
        nself._coords.update()
        return nself

    def resolve_polytomy(
        self,
        dist:float=1.0,
        support:float=100,
        recursive:bool=True,
        ) -> 'ToyTree':
        """
        Returns a copy of the tree with all polytomies randomly resolved.
        Does not transform tree in-place.
        """
        # TREENODE FUNC
        nself = self.copy()
        nself.treenode.resolve_polytomy(
            default_dist=dist,
            default_support=support,
            recursive=recursive)
        nself._coords.update()
        return nself

    def unroot(self) -> 'ToyTree':
        """
        Returns a copy of the tree unrooted. Does not transform tree in-place.
        """
        # TREENODE FUNC
        nself = self.copy()
        # updated unroot function to preserve support values to root node
        nself.treenode.unroot()
        nself.treenode.ladderize()
        nself._coords.update()
        return nself

    def root(
        self,
        names:Optional[List[str]]=None,
        wildcard:Optional[str]=None,
        regex:Optional[str]=None,
        resolve_root_dist:bool=True,
        edge_features:Optional[List[str]]=None,
        ) -> 'ToyTree':
        """
        (Re-)root a tree by moving the tree anchor (real or phantom
        root node) to a new split in the tree.

        Rooting location can be selected by entering a list of tipnames
        descendant from a node, or using wildcard or regex to select
        a list of tipnames.

        names: (list) (default=None)
            A list of tip names. Root is placed along edge to mrca node.

        wildcard: (str) (default=None)
            A string matching multiple tip names. Root is placed along
            edge to the mrca node of selected taxa.

        regex: (str) (default=None)
            A regex string matching multiple tip names. Root is placed
            along edge to the mrca node of selected taxa.

        resolve_root_dist: (float or bool) (default=True)
            Length along the edge at which to place the new root, or a
            boolean indicating auto methods. Default is True, which
            means to use mid-point rooting along the edge. False will
            root at the ancestral node creating a zero length edge. A
            float value will place the new node at a point along the
            edge starting from the ancestral node. A float value
            greater than the edge length will raise an error.

        edge_features: (list) (default=["support"])
            Node labels in this list are treated as edge labels (e.g.,
            support values represent support for a split/edge in the
            tree). This effects how labels are moved when the tree is
            re-rooted. By default support values are treated as edge
            features and moved to preserve clade supports when the tree
            is re-rooted. Other node labels, such as names do not make
            sense to shift in this way. New splits that are created by
            rooting are set to support=100 by default.

        Example:
        --------
        To root on a clade that includes the samples "1-A" and "1-B"
        you can do any of the following:

        rtre = tre.root(names=["1-A", "1-B"])
        rtre = tre.root(wildcard="1-")
        rtre = tre.root(regex="1-[A,B]")
        """
        # insure edge_features is an iterable
        edge_features = ["support"]
        if isinstance(edge_features, (str, int, float)):
            edge_features.append(edge_features)
        elif isinstance(edge_features, list):
            edge_features.extend(edge_features)

        # make a deepcopy of the tree and pass to Rooter class
        nself = self.copy()
        rooter = Rooter(
            nself,
            (names, wildcard, regex),
            resolve_root_dist,
            edge_features,
        )
        return rooter.tree

    # --------------------------------------------------------------------
    # Draw functions imported, but docstring here...
    # TODO:
    #    - expand node_hover=True to a table of all features
    #    - fix admixture_edges
    # --------------------------------------------------------------------
    def draw(
        self,
        tree_style: Optional[str]=None,
        height: int=None,
        width: int=None,
        axes: toyplot.coordinates.Cartesian=None,
        layout: str=None,
        tip_labels: Union[bool,Iterable]=None,
        tip_labels_colors: Union[str,Iterable]=None,
        tip_labels_style: Dict[str,Any]=None,
        tip_labels_align: bool=None,
        node_mask: Union[bool,Iterable[bool]]=None,
        node_labels: Union[bool,Iterable[str]]=None,
        node_labels_style: Dict[str,Any]=None,
        node_sizes: Union[int,Iterable[int]]=None,
        node_colors: Union[str,Iterable[str]]=None,
        node_style: Dict[str,Any]=None,
        node_hover: bool=None,
        node_markers: Iterable[str]=None,
        edge_colors: Union[str,Iterable[str]]=None,
        edge_widths: float=None,
        edge_type: str=None,
        edge_style: Dict[str,Any]=None,
        edge_align_style: Dict[str,Any]=None,
        use_edge_lengths: bool=None,
        scale_bar: bool=None,
        padding: float=None,
        xbaseline: float=None,
        ybaseline: float=None,
        admixture_edges: List[Tuple[int,int]]=None,
        shrink: float=None,
        fixed_order: Iterable[str]=None,
        fixed_position: Iterable[float]=None,
        **kwargs,
        ) -> Tuple[toyplot.Canvas, toyplot.coordinates.Cartesian, ToytreeMark]:
        """
        Draw a Toytree plot, returns a tuple of Toyplot objects for
        the (Canvas, Cartesian, Mark) which will automatically render
        in a jupyter notebook. The Canvas can be saved to file with
        toyplot, or the Axes can be combined with additional drawings
        into composite drawings.

        Examples:
        ---------
        canvas, axes, mark = tree.draw(tree_style="o")

        Parameters:
        -----------
        tree_style (or ts): str
            One of several builtin styles for tree plotting. The
            default is 'n' (normal), others include "c", "d", "o",
            "m", and you can crate your own TreeStyles (see docs).
            TreeStyle sets a base style on top of which other style
            args override.

        height: int (pixels)
            If None the plot height is autosized. If 'axes' arg is
            used tree is drawn on an existing Axes and this arg is
            ignored.

        width: int (pixels)
            If None the plot height is autosized. If 'axes' arg is
            used tree is drawn on an existing Axes and this arg is
            ignored.

        axes: Toyplot.coordinates.Cartesian (default=None)
            A toyplot cartesian axes object. If provided tree is drawn
            on it. If not provided then a new Canvas and Cartesian
            axes are created and returned with the tree plot added to
            it.

        use_edge_lengths: bool (default=False)
            If True edge lengths ('dist' features of TreeNodes)
            are represented in drawings. If False all terminal
            edges are extended to align tips at 0 (ultrametric).

        tip_labels: [bool, list]
            If True tip labels ('name' features on tip nodes) are
            added to the plot; if False no tip labels are added. If a
            list of tip labels is provided it must be the same len as
            ntips and is applied in node idx order.

        tip_labels_colors: [Color, Iterable[Color]]:
            Any valid toyplot Color or Iterable of Colors to apply to
            tip labels in idx order.

        tip_labels_style: Dict[str,str]
            A dictionary of CSS style arguments to apply to text
            tip labels.

        tip_labels_align: bool
            If True tip names will be aligned and dashed edges will
            drawn to extend from tree edges to the tip names.

        node_mask: Union[bool, Iterable[bool]]
            Masks nodes (size, color, shape, label) if True, shows
            nodes if False. An iterable can be entered to selectively
            hide some nodes. The convenience function .get_node_mask()
            can be used to generate mask arrays. Default options
            vary among tree styles, but usually hide tip nodes.

        node_labels: Union[bool, str, Iterable[str]]
            Labels associated with nodes. True shows node idx labels,
            False hides node labels (sets to ""). A string or
            iterable of strings assigns labels to nodes 0-nnodes.
            An iterable of string values can be generated from node
            features using .get_node_data() or .get_node_labels(),
            the latter includes string formatting options.

        node_sizes: Union[int, Iterable[int]]
            Size of node markers can be set as an integer or Iterable
            of integers in node order 0-nnodes. Node size 0 is hidden.
            The node_mask argument sets nodes to size 0 when masked,
            and overrides this argument.

        node_colors: Union[str, Iterable[str]]
            Color of node markers can be a single color or Iterable
            of colors in node order 0-nnodes. Any valid toyplot color
            (str, rgb array, rgba array, hex, etc) is accepted. See
            the toyplot.color module. The default color palette is
            accessible from toytree.colors. If all nodes will be set
            to the same color it is more efficient to use the
            node_style dictionary (node_style={"fill": 'red'}). If
            used, node_colors overrides 'fill' in node_style.

        node_style: Dict[str,str]
            A dict of valid CSS styles to apply to node markers, such
            as 'fill', 'stroke', 'stroke-width', etc.

        node_hover: [True, False, Iterable[str]]
            Default is True in which case node hover will show the
            node values. If False then no hover is shown. If a list or
            dict is provided (which should be in node order) then the
            values will be shown in order. If a dict then labels can
            be provided as well.

        admixture_edges: [Tuple, List[Tuple]]
            Admixture edges add colored edges to the plot in the
            style of the 'edge_align_style'. These will be drawn
            from (source, dest, height, width, color). Example:
            [(4, 3, 50000, 3, 'red')].

        ...

        fixed_order: Iterable[str]
            An Iterable of tip labels in the order they should be
            plotted. The default is the node names in idx order
            0-ntips. These nodes will be plotted on the coordinates
            0-ntips on either the x or y-axis depending on the
            layout of the tree drawing. This is a convenient argument
            for visualizing discordance of trees.

        fixed_position: List[float]
            The positions on the tip axis where ordered tips should
            be plotted. If None then default positions range(0, ntips)
            are used. By setting explicit positions tips can be
            spaced to better show discordance, or extinct taxa, or
            morphology. The order of positions applies to tips in
            order of the 'fixed_order' arg.
        """
        return draw_toytree(
            toytree=self,
            tree_style=tree_style,
            axes=axes,
            height=height,
            width=width,
            layout=layout,
            tip_labels=tip_labels,
            tip_labels_colors=tip_labels_colors,
            tip_labels_align=tip_labels_align,
            tip_labels_style=tip_labels_style,
            node_mask=node_mask,
            node_labels=node_labels,
            node_labels_style=node_labels_style,
            node_sizes=node_sizes,
            node_hover=node_hover,
            node_style=node_style,
            node_colors=node_colors,
            node_markers=node_markers,
            edge_type=edge_type,
            edge_colors=edge_colors,
            edge_widths=edge_widths,
            edge_style=edge_style,
            edge_align_style=edge_align_style,
            use_edge_lengths=use_edge_lengths,
            scale_bar=scale_bar,
            padding=padding,
            xbaseline=xbaseline,
            ybaseline=ybaseline,
            admixture_edges=admixture_edges,
            shrink=shrink,
            fixed_order=fixed_order,
            fixed_position=fixed_position,
            kwargs=kwargs,
        )



def tree(data:Union[str,Path,Url,ToyTree,TreeNode], tree_format:int=0) -> ToyTree:
    """
    toytree flexible data parser and ToyTree class constructor.

    Parameters:
    -----------
    Returns a ToyTree object from a variety of optional input types,
    including a newick or nexus string; a filepath or Url to a newick
    or nexus string; a TreeNode instance; or a ToyTree instance.
    The tree_format argument is an integer corresponding to an ete3
    tree format (the common format 0 generally works fine).

    For speed-intensive tasks you can achieve faster performance with
    the alternative tree parsing functions listed below.

    See also: read_newick(), read_nexus(), or read_extended()

    Examples:
    ---------
    tree = toyreee.tree("((a,b),c);")
    tree = toytree.tree("/tmp/test.nwk")
    tree = toytree.tree("https://eaton-lab.org/data/Cyathophora.tre")
    tree = toytree.tree(toytree.TreeNode())
    """
    treenode = None

    # load from a TreeNode and detach. Must have .idx attributes on nodes.
    if isinstance(data, TreeNode):
        treenode = data.detach()._clone()
        tree = ToyTree(treenode)

    # load TreeNode from a ToyTree (user should use .copy() to preserve style)
    elif isinstance(data, ToyTree):
        # treenode = data.treenode._clone()
        tree = data.copy()

    # parse a str, URL, or file
    elif isinstance(data, (str, bytes, Path)):
        treenode = TreeParser(data, tree_format).treenodes[0]
        tree = ToyTree(treenode)

    # raise an error (to make an empty tree you must enter empty TreeNode)
    else:
        raise ToytreeError(f"Cannot parse input tree data: {data}")

    # enforce ladderize
    #treenode.ladderize()
    return tree


if __name__ == "__main__":

    import toytree
