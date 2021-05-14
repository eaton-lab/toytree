#!/usr/bin/env python

"""
The core toytree class object. 
Nearly all API functions are accessible from a toytree, including
tree i/o, modifications, drawing, and analysis.

TODO: Test for speed improvements: 
- down-facing drawing is broken...
- fixed-order and tip-labels colors together
- show bede how to flip scalebar.
- node_colors supports colormap (docstring link to plot docs)
- reduce deepcopies (in ToyTree done)
- reduce traversals.
- .write w/ feature support.
- use set_node_heights in set_node_feature('heights')
"""

# inconsistent-return-statements

from typing import Union, Optional, Mapping, Iterable, List, Dict, Tuple, Set, Any
from pathlib import Path
import numpy as np
import toyplot
from loguru import logger

from toytree.src.treenode import TreeNode
from toytree.src.node_assist import NodeAssist
from toytree.src.drawing.coords import Coords
from toytree.src.drawing.tree_style import TreeStyle, COLORS2
from toytree.src.drawing.draw_toytree import draw_toytree
from toytree.src.io.TreeParser import TreeParser
from toytree.src.io.TreeWriter import NewickWriter
from toytree.utils.exceptions import ToytreeError
from toytree.utils.transform import normalize_values
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
        self.style = TreeStyle(tree_style='n')


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
    def newick(self):
        return self._newick
    

    def write(
        self, 
        path:Optional[Path]=None, 
        tree_format:int=0, 
        features:Optional[Iterable[str]]=None, 
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
        features (Iterable):
            Features of treenodes that should be written to the newick string
            in NHX format. Examples include "height", "idx", or other features
            you may have saved to treenodes. 
        """
        if not self.ntips:
            raise ToytreeError("tree is empty")

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
            logger.info(f"wrote newick to {path}")
            return None

    def get_edges(self) -> np.ndarray:
        """
        Returns an array with paired edges (parent, child) as  
        node indices. This array is primarily for internal use.
        """
        return self._coords.edges

    def get_edge_values(
        self, 
        feature:str='idx', 
        normalize:bool=False,
        ) -> List:
        """
        Returns edge values in post-order traversal order (tree draw
        order). This function is typically used to pass colors or widths
        to drawing functions for 'edge_colors' or 'edge_widths' options.

        Parameters:
        -----------
        feature (str):
            The node feature to return for each edge, e.g., idx, dist.
        normalize (bool):
            Normalize values to be binned in discrete categories given
            their range of values to make it easier to assign discrete
            categories to edge widths or colors.

        Examples:
        ---------
        colors = tree.get_edge_values("dist", normalize=True)
        tre.draw(edge_colors=colors)
        """
        elist = []
        for eidx in self._coords.edges[:, 1]:
            node = self.idx_dict[eidx]
            elist.append(
                (getattr(node, feature) if hasattr(node, feature) else "")
            )
        elist = np.array(elist)
        if normalize:
            elist = normalize_values(elist)
        return elist

    def get_edge_values_mapped(
        self, 
        clades:Union[Set[int],Dict[int,str],Tuple], 
        include_stem:bool=True,
        ) -> List:
        """
        Enter a dictionary mapping node 'idx' or tuples of tipnames 
        to values that you want mapped to descendant edges of that node. 
        Edge values are returned in post-order traversal order (drawing
        order) to be entered to the 'edge_colors' or 'edge_widths'
        arguments to draw(). To see node idx values use node_labels=True
        in .draw(). If node_mapping keys are integers it is assumed they 
        are node idxs. 

        Note: it is safer to use tip labels to select clades than 
        node idxs since tree tranformations (e.g., rooting) can change
        the mapping of idx values to nodes on the tree.

        This function is most convenient for applying values to clades. 
        To instead map values to specific edges (e.g., a single internal
        edge) it will be easier to use tre.get_edge_values() and then 
        to set the values of the internal edges manually.

        Parameters:
        -----------
        clades:
            A set of int idxs, tuple of tip names, or dict of {ints:str}
            designating clades that should be colored. The first two 
            options automatically apply colors from a colormap, whereas
            the third option (dict) allow the user to enter the color
            for each 

        Examples:
        --------- 
          tre = toytree.tree("((a,b),(c,d));")
          tre.get_edge_values_mapped({5: 'green', 6: 'red'})
          # ['green', 'green', 'green', 'red', 'red', 'red']

          tre = toytree.tree("((a,b),(c,d));")
          tre.get_edge_values_mapped({(a, b): 'green', (c, d): 'red'})          
          # ['green', 'green', 'green', 'red', 'red', 'red']

          tre = toytree.tree("((a,b),(c,d));")
          tre.get_edge_values_mapped({10, 13})
          # ['green', 'green', 'green', 'red', 'red', 'red']

        """
        # get an empty list for length of all edges
        values = [None] * self._coords.edges.shape[0]

        # if tuple: convert to set of int idxs
        if isinstance(clades, tuple):
            clades = set(
                NodeAssist(self, tup, None, None).get_mrca().idx
                for tup in clades
            )

        # if set: convert to dict using COLORS2 set.
        if isinstance(clades, set):
            cols = iter(COLORS2)
            clades = {i: next(cols) for i in clades}

        # build an array of colors given the dict[int:color]
        # iterative from the highest idx to the smallest for nestedness.
        rmap = {}
        for nidx in self.idx_dict:
            node = self.idx_dict[nidx]
            if nidx in rmap:

                # add value to stem edge
                if include_stem:
                    if not node.is_root():
                        values[nidx] = rmap[nidx]

                # add value to descendants edges
                for desc in node.get_descendants():
                    values[desc.idx] = rmap[nidx]
        return values

    def get_mrca_idx_from_tip_labels(
        self, 
        names:Iterable[str]=None, 
        wildcard:str=None, 
        regex:str=None,
        ):
        """
        Returns the node idx label of the most recent common ancestor node 
        for the clade that includes the selected tips. Arguments can use fuzzy
        name matching: a list of tip names, wildcard selector, or regex string.
        """
        nas = NodeAssist(self, names, wildcard, regex)
        return nas.get_mrca().idx

    def get_node_descendant_idxs(self, idx:int) -> List[int]:
        """
        Returns a node idx and all of its descendants node idxs.
        """
        descs = [i.idx for i in self.idx_dict[idx].get_descendants()]
        return [idx] + [descs]

    def get_node_labels(
        self, 
        feature:str, 
        show_root:bool=False, 
        show_tips:bool=False,
        mask:Optional[Iterable[bool]]=None,
        # float_formatter:Optional[str]=".2f",
        # str_formatter:Optional[str]=None,
        ) -> List[str]:
        """
        Returns values for a selected node feature in a post-order 
        traversal (tree plotting order) as a list of formatted
        strings for adding as node labels to a tree drawing.

        The root and tip values can be toggled to be shown or not. 
        The mask argument overrides these two arguments.
        This is a boolean array of length nnodes in post-order traversal
        where False indicates that a node should be hidden (i.e., 
        size, color, shape, label are all hidden). The node labels
        are returned as a list where hidden nodes are shown as "", and
        node with hidden labels (but all else shwown) are " ". A mask
        can be created easily from operations on the array from 
        get_node_values().

        See also: get_node_values

        Usage:
        ----------
        # show node names as node labels
        tree.draw(node_labels=tree.get_node_labels("name"))

        # to show node support values as node labels
        tree.draw(node_labels=tree.get_node_labels("support"))

        # show only node labels where support < 90
        mask = tree.get_node_values("support") < 90
        nlabels = tree.get_node_labels("support", mask=mask)
        tree.draw(node_labels=nlabels)
        """
        # get array of values as (str,int,float,object) dtype
        values = self.get_node_values(feature)

        # if float type then apply float formatter
        # if issubclass(values.type, np.floating):
        # values = np.array()
        # if 
        # try:
        #     if np.can_cast(values.dtype, np.float):
        #         values = []
        # except TypeError as err:
        #     raise 

        labels = values.astype(str)
        labels[labels == "nan"] = " "
        if not show_root:
            labels[0] = ""
        if not show_tips:
            labels[-self.ntips:] = ""
        if mask is not None:
            if isinstance(mask, (tuple, list)):
                mask = np.array(mask).astype(bool)
            assert mask.size == values.size, (
                f"mask must be nnodes is size ({self.nnodes})")
            assert mask.dtype == np.bool_, (
                "mask must be a boolean numpy array")
            labels[np.invert(mask)] = ""

        # TODO: apply string formatter
        labels = labels.tolist()
        return labels

    def get_node_values(
        self, 
        feature:str=None, 
        **kwargs,
        ) -> np.ndarray:
        """
        Returns values for a selected node features in post-order 
        traversal (tree plotting order) as a numpy ndarray. This is
        intended for performing math or set operations on the data 
        values. To get string representations of node values for 
        plotting see instead get_node_labels.

        See also: get_node_labels

        Usage:
        ---------------------
        # get support values as integers and hide nodes w/ values > 95
        mask = tree.get_node_values("support") < 95
        labels = tree.get_node_labels("support", mask=mask, show_tips=False)
        tree.draw(node_sizes=16, node_labels=labels)
        """
        if kwargs:
            logger.warning(
                "The get_node_values() function has changed in toytree > 2.1. "
                "It now returns an array of values in their original type "
                "(e.g., int, float) with missing values as NaN. "
                "To get string representations of node values, including "
                "options to hide root, tips, or other nodes, see the new "
                "get_node_labels() function."
            )
        return np.array([
            getattr(self.idx_dict[i], feature, np.nan) for i in self.idx_dict
        ])

    def get_node_coordinates(self, layout:str=None, use_edge_lengths:bool=True):
        """
        Returns coordinate locations of nodes in the tree as an array. Each
        row is an (x, y) coordinate, ordered by the 'idx' feature of nodes.
        The first ntips rows are the tip coordinates, which can also be 
        returned using .get_tip_coordinates().
        """
        # if layout argument then set style and update coords.
        if layout is None:
            layout = self.style.layout
        if layout == 'c':
            return self._coords.get_radial_coords(use_edge_lengths)
        return self._coords.get_linear_coords(layout, use_edge_lengths)

    def get_feature_dict(
        self, 
        key_attr:Optional[str]=None, 
        values_attr:Optional[str]=None,
        ) -> Dict:
        """
        Returns a dictionary mapping one or more selected node features
        to each other, or to node objects (by entering None). 

        Examples:
        --------
        tree.get_feature_dict("idx", "name")
        tree.get_feature_dict("name", None)
        """
        ndict = {}
        for node in self.idx_dict.values():
            if key_attr is not None:
                key = getattr(node, key_attr)
            else:
                key = node
            if values_attr is not None:
                value = getattr(node, values_attr)
            else:
                value = node
            ndict[key] = value
        return ndict

    def get_tip_coordinates(
        self, 
        layout:str=None, 
        use_edge_lengths:bool=True,
        ) -> np.ndarray:
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

    def get_tip_labels(self, idx:Optional[int]=None):
        """
        Returns tip labels in the order they will be plotted on the 
        tree, i.e., "preorder traversal", which will appear from the
        zero axis and counting up by units of 1 on right-facing 
        ladderized tree.

        Parameters:
        -----------
            idx: returns a list of names for all tips descended from 
            node with index idx. Draw with node_labels='idx' to find.
        """
        if idx is not None:
            return [i.name for i in self.idx_dict[idx].get_leaves()]
        return [self.idx_dict[idx].name for idx in range(self.ntips)]

    def set_node_values(
        self, 
        feature:str, 
        mapping:Dict[Union[int,str],Any]=None, 
        default:Any=None,
        ):
        """
        Set values to a node feature and RETURNS A COPY of the toytree.

        If the feature is set to only some nodes then others are set to
        NaN. You cannot set "idx" (this is used internally by toytree)
        You can set base features like name, dist, height, support, or
        create any new feature.

        Example:
        -------- 
        tre.set_node_values(feature="Ne", default=5000)
        tre.set_node_values(feature="Ne", mapping={0:1e5, 1:1e6, 2:1e3})
        tre.set_node_values(feature="Ne", mapping={0:1e5, 1:1e6}, default=5000)
        tre.set_node_values(feature="Ne", mapping={'r0':1e5, 'r1':1e6})

        Parameters:
        -----------
        feature (str):
            The name of the node attribute to modify (cannot be 'idx').
        mapping (dict):
            A dictionary of {node: value}. To select nodes you can use either
            integer values corresponding to the node 'idx' labels, or strings
            corresponding to the node 'name' labels. 
            Note: use tree.draw(node_labels='idx') to see idx labels on tree.
        default (int, str, float):
            You can use a default value to be filled for all other nodes not 
            listed in the values dictionary.

        Returns:
        ----------
        A ToyTree object is returned with the node values modified.
        """
        # make a copy
        nself = self.copy()

        # make default ndict using idxs, regardless of values
        ndict = nself.idx_dict

        # if first value is a string then use name_dict instead of idx_dict
        if mapping:
            val0 = list(mapping)[0]
            if isinstance(val0, (str, bytes)):
                ndict = {ndict[i].name: ndict[i] for i in ndict}
            elif isinstance(val0, int):
                pass
            else:
                raise ToytreeError(
                    "mapping dict keys should be int or str type")

        # find special cases
        if feature == "idx":
            raise ToytreeError("cannot modify idx values.")
        if feature == "height":
            raise ToytreeError(
                "modifying heights not supported, use .mod.set_node_heights")

        # set everyone to a default value for this attribute
        if default is None:
            if any(isinstance(i, str) for i in mapping.values()):
                default = ""
            else:
                default = np.nan
        for key in ndict:
            node = ndict[key]
            node.add_feature(feature, default)

        # set specific values
        if mapping:
            if not isinstance(mapping, dict):
                msg = ("Values should be a dictionary. "
                    "Use default to set a single value.")
                logger.warning(msg)
                raise ToytreeError(msg)

            # check that all keys are valid
            for nidx in mapping:
                if nidx not in ndict:
                    raise ToytreeError(
                        f"node idx or name {nidx} not in tree")

            # then set selected nodes to new values
            for key, val in mapping.items():
                node = ndict[key]
                node.add_feature(feature, val)
        return nself

    def copy(self):
        """ 
        Returns a copy of a ToyTree instance (but faster than deepcopy)
        """
        # copy treenodes w/ topology, node attrs, nnodes, ntips, 
        # and idx_dict... copy=True is important, or atlest kwargs is...
        nself = ToyTree(self.treenode._clone())           
        # copy=True,
        # fixed_order=self._fixed_order,)

        # update style dicts
        nself.style = self.style.copy()

        # update coords by copying instead of coords.update
        # nself._coords.edges = nself._coords.get_edges()
        # nself._coords.verts = self._coords.verts.copy()
        return nself

    def is_rooted(self):
        """
        Returns False if the tree is unrooted.
        """
        if len(self.treenode.children) > 2:
            return False
        return True

    # TODO: replace with .nnodes and idx_dict usage.
    def is_bifurcating(self, include_root:bool=True):
        """
        Returns False if there is a polytomy in the tree, including if the tree
        is unrooted (basal polytomy), unless you use the include_root=False
        argument.
        """
        ctn1 = -1 + (2 * len(self))
        ctn2 = -2 + (2 * len(self))
        if self.is_rooted():
            return bool(ctn1 == sum(1 for i in self.treenode.traverse()))
        if include_root:
            return bool(ctn2 == -1 + sum(1 for i in self.treenode.traverse()))
        return bool(ctn2 == sum(1 for i in self.treenode.traverse()))

    # TODO: support alpha
    def ladderize(self, direction:int=0):#, alphanumeric:bool=False):
        """
        Ladderize tree (order descendants) so that left/right child
        has fewer/more descendants. To reverse this pattern use 
        direction=1. To also ladderize cherry tipnames use alphanumeric.
        """
        # nself._fixed_order = None        
        nself = self.copy()
        nself.treenode.ladderize(direction=direction)
        nself._coords.update()
        return nself

    def collapse_nodes(self, min_dist:float=1e-6, min_support:float=0):
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

    def prune(self, names:Iterable[str]=None, wildcard:str=None, regex:str=None):
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
        tre = toytree.rtree.imbtree(ntips=10)
        ptre = tre.prune(names=['r1', 'r2', 'r3', 'r6'])
        ptre = tre.prune(regex='r[0-3]')

        Returns:
        ----------
        ToyTree
        """
        # make a deepcopy of the tree
        nself = self.copy()

        # return if nothing to drop
        if not any([names, wildcard, regex]):
            return nself

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

    def drop_tips(self, names:Iterable[str]=None, wildcard:str=None, regex:str=None):
        """
        Returns a copy of the tree with the selected tips removed. The 
        entered value can be a name or list of names. To prune on an 
        internal node to create a subtree see the .prune() function
        instead.

        Parameters:
        -----------
        names: list of tip names.
        wildcard: a string to match using wildcard characters like *
        regex: a regular expression to match multiple names.

        Examples:
        ----------
        tre = toytree.rtree.imbtree(ntips=10)
        ptre = tre.prune(names=['r1', 'r2', 'r3', 'r6'])
        ptre = tre.prune(regex='r[0-3]')

        Returns:
        ----------
        toytree.Toytree.ToyTree
        """
        # make a deepcopy of the tree
        nself = self.copy()

        # return if nothing to drop
        if not any([names, wildcard, regex]):
            return nself

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
        names=None, 
        wildcard=None, 
        regex=None, 
        idx=None,
        ):
        """
        Returns a ToyTree with the selected node rotated for plotting.
        tip colors do not align correct currently if nodes are rotated...
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
        ):
        """
        Returns a copy of the tree with all polytomies randomly resolved.
        Does not transform tree in-place.
        """
        nself = self.copy()
        nself.treenode.resolve_polytomy(
            default_dist=dist,
            default_support=support,
            recursive=recursive)
        nself._coords.update()
        return nself

    def unroot(self):
        """
        Returns a copy of the tree unrooted. Does not transform tree in-place.
        """
        nself = self.copy()
        # updated unroot function to preserve support values to root node
        nself.treenode.unroot()       
        nself.treenode.ladderize()
        nself._coords.update()
        return nself        

    def root(
        self, 
        names:Iterable[str]=None, 
        wildcard:str=None, 
        regex:str=None, 
        resolve_root_dist:bool=True,
        edge_features:List[str]=["support"],
        ):
        """
        (Re-)root a tree by moving the tree anchor (real or phantom 
        root node) to a new split in the tree. 

        Rooting location can be selected by entering a list of tipnames
        descendant from a node, or using wildcard or regex to select 
        a list of tipnames. 

        names: (list) (default=None)
            A list of tip names. Root is placed along edge to mrca node. 

        wildcard: (str) (default=None)
            A string matching multiple tip names. Root is placed along edge to
            the mrca node of selected taxa.

        regex: (str) (default=None)
            A regex string matching multiple tip names. Root is placed along 
            edge to the mrca node of selected taxa.

        resolve_root_dist: (float or bool) (default=True)
            Length along the edge at which to place the new root, or a boolean
            indicating auto methods. Default is True, which means to use mid-
            point rooting along the edge. False will root at the ancestral node
            creating a zero length edge. A float value will place the new node
            at a point along the edge starting from the ancestral node. A float
            value greater than the edge length will raise an error.

        edge_features: (list) (default=["support"])
            Node labels in this list are treated as edge labels (e.g., support
            values represent support for a split/edge in the tree). This effects
            how labels are moved when the tree is re-rooted. By default support
            values are treated as edge features and moved to preserve clade
            supports when the tree is re-rooted. Other node labels, such as 
            names do not make sense to shift in this way. New splits that are
            created by rooting are set to 100 by default.

        Example:
        --------
        To root on a clade that includes the samples "1-A" and "1-B" 
        you can do any of the following:

        rtre = tre.root(names=["1-A", "1-B"])
        rtre = tre.root(wildcard="1-")
        rtre = tre.root(regex="1-[A,B]")
        """       
        # insure edge_features is an iterable
        if not edge_features:
            edge_features = []
        if isinstance(edge_features, (str, int, float)):
            edge_features = [edge_features]

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
    # Draw functions imported, but docstring here
    # --------------------------------------------------------------------
    def draw(
        self,
        tree_style:Optional[str]=None,
        height:Optional[int]=None,
        width:Optional[int]=None,
        axes:Optional[toyplot.coordinates.Cartesian]=None,    
        layout:Optional[str]=None,
        tip_labels:Union[bool,Iterable]=None,
        tip_labels_colors=None,
        tip_labels_style=None,
        tip_labels_align=None,
        node_labels=None,
        node_labels_style=None,
        node_sizes=None,
        node_colors=None,
        node_style=None,
        node_hover=None,
        node_markers=None,
        edge_colors=None,
        edge_widths=None,
        edge_type=None,
        edge_style=None,
        edge_align_style=None,
        use_edge_lengths=None,
        scalebar=None,
        padding=None,
        xbaseline=None,
        ybaseline=None,
        admixture_edges=None,
        shrink=None,
        fixed_order=None,
        fixed_position=None,
        **kwargs):
        """
        Draw a Toytree plot, returns a tuple of Toyplot objects for the
        (Canvas, Axes, Mark).

        Examples:
        ---------
        canvas, axes, mark = tree.draw(tree_style="o")

        Parameters:
        -----------
        tree_style (or ts): str
            One of several builtin styles for tree plotting. The default
            is 'n' (normal), others include "c", "d", "o", "m", and you
            can crate your own TreeStyles (see docs). TreeStyle sets 
            a base style on top of which other style args override.

        height: int (pixels)
            If None the plot height is autosized. If 'axes' arg is used
            tree is drawn on an existing Axes and this arg is ignored.

        width: int (pixels)
            If None the plot height is autosized. If 'axes' arg is used
            tree is drawn on an existing Axes and this arg is ignored.

        axes: Toyplot.Cartesian (default=None)
            A toyplot cartesian axes object. If provided tree is drawn 
            on it. If not provided then a new Canvas and Cartesian axes 
            are created and returned with the tree plot added to it.

        use_edge_lengths: bool (default=False)
            Use edge lengths from .treenode (.get_edge_lengths) else
            edges are set to length >=1 to make tree ultrametric.

        tip_labels: [bool, list]
            If True tip labels ('name' features on tip nodes) are added 
            to the plot; if False no tip labels are added. If a list of 
            tip labels is provided it must be same len as ntips.

        tip_labels_colors:
            ...

        tip_labels_style:
            ...

        tip_labels_align:
            ...

        node_labels: [True, False, list]
            If True then nodes are shown, if False then nodes are suppressed
            If a list of node labels is provided it must be the same length
            and order as nodes in .get_node_values(). Node labels can be 
            generated in the proper order using the the .get_node_labels() 
            function from a Toytree tree to draw info from the tree features.
            For example: node_labels=tree.get_node_labels("support").

        node_sizes: [int, list, None]
            If None then nodes are not shown, otherwise, if node_labels
            then node_size can be modified. If a list of node sizes is
            provided it must be the same length and order as nodes in
            .get_node_dict().

        node_colors: [list]
            Use this argument only if you wish to set different colors for
            different nodes, in which case you must enter a list of colors
            as string names or HEX values the length and order of nodes in
            .get_node_dict(). If all nodes will be the same color then use
            instead the node_style dictionary:
            e.g., node_style={"fill": 'red'}

        node_style: [dict]

        ...

        node_hover: [True, False, list, dict]
            Default is True in which case node hover will show the node
            values. If False then no hover is shown. If a list or dict
            is provided (which should be in node order) then the values
            will be shown in order. If a dict then labels can be provided
            as well.

        admixture_edges: [tuple, list]
            Admixture edges will add colored edges to the plot in the style 
            of the 'edge_align_style'. These will be drawn from (source, dest, 
            height, width, color). Example: [(4, 3, 50000, 3, 'red')]

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
            scalebar=scalebar,
            padding=padding,
            xbaseline=xbaseline, 
            ybaseline=ybaseline,
            admixture_edges=admixture_edges,
            shrink=shrink,
            fixed_order=fixed_order,
            fixed_position=fixed_position,
            kwargs=kwargs,
        )



def tree(data=Union[str,Path,Url,ToyTree,TreeNode], tree_format:int=0) -> ToyTree:
    """
    toytree flexible data parser and ToyTree class constructor.

    Parameters:
    -----------
    Returns a ToyTree object from a variety of optional input types,
    including a newick or nexus string; a filepath or Url to a newick
    or nexus string; a TreeNode class object; or a ToyTree class object.
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
    tree = toytree.tree(TreeNode())
    """
    treenode = None

    # load from a TreeNode and detach. Must have .idx attributes on nodes.
    if isinstance(data, TreeNode):
        treenode = data.detach()

    # load TreeNode from a ToyTree (user should use .copy() to preserve style)
    elif isinstance(data, ToyTree):
        treenode = data.treenode

    # parse a str, URL, or file
    elif isinstance(data, (str, bytes, Path)):
        treenode = TreeParser(data, tree_format).treenodes[0]

    # raise an error (to make an empty tree you must enter empty TreeNode)
    else:
        raise ToytreeError(f"cannot parse input tree data: {data}")

    # enforce ladderize
    treenode.ladderize()
    return ToyTree(treenode)


if __name__ == "__main__":

    import toytree
    tree = toytree.rtree.unittree(10)

    tre = toytree.tree(tree.write())
    tre = toytree.tree(tre.treenode)
    tre = toytree.tree(tre)    
    print(tre)
