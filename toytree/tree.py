#!/usr/bin/env python

from __future__ import print_function, division

import toyplot
import numpy as np
import copy
import re
from . import ete3mini
from decimal import Decimal

# pylint: disable=W0212
# pylint: disable=R0902
# pylint: disable=R0912
# pylint: disable=R0914
# pylint: disable=R0915
# pylint: disable=E1101


## color palette as a list
PALETTE = toyplot.color.Palette()
COLORS = [toyplot.color.to_css(i) for i in PALETTE]
DEFAULTS_ALL = {
    ## add-on defaults
    "admixture": None,
    "orient": "right",
    "tree_style": "p", 
    "use_edge_lengths": False,

    ## edge defaults
    "edge_style": {
        "stroke": "#292724", 
        "stroke-width": 2, 
        "stroke-linecap": "round", 
        },
    "edge_align_style": {
        "stroke": "darkgrey",       
        #"stroke-width": 2,   ## copies edge_style for width by default
        "stroke-linecap": "round", 
        "stroke-dasharray": "2, 4",
        },  

    ## node label defaults
    "node_labels": False,       
    "node_labels_style": {
        "font-size": "9px", 
        "fill": "#262626",
        #"text-anchor":"start",  
        }, 

    ## node defaults
    "node_size": None,             
    "node_color": None, #COLORS[0],
    "node_hover": True,
    "node_style": {
        "fill": COLORS[0], 
        "stroke": 'none', #COLORS[0],
        },
    "vmarker": "o", # "r2x1" for rectangles

    ## tip label defaults
    "tip_labels": True,         
    "tip_labels_color": toyplot.color.black,    
    "tip_labels_align": False,
    "tip_labels_style": {
        "font-size": "12px",
        "text-anchor":"start", 
        "-toyplot-anchor-shift": None, #"0px", #None,
        "fill": "#292724", 
        },
}
DEFAULTS_CTREES = {
    "tree_style": "c",    
    "orient": "down", 
    "use_edge_lengths": True,
    "tip_labels_align": False,
    #"tip_labels_angle": None,    
}
DEFAULTS_PTREES = {
    "tree_style": "p",    
    "orient": "right", 
    "use_edge_lengths": True,
    "tip_labels_align": False,
    #"tip_labels_angle": None,    
}
DEFAULTS_ATREES = {
    "tree_style": "c",
    "orient": "down", 
    "use_edge_lengths": True,
    "node_labels": "idx",
    "tip_labels": False,
    "tip_labels_align": False,    
}


## the main tree class
class Toytree(object):
    """
    The toytree Tree Class object, a plotting wrapper around an 
    ete3 Tree Class object which can be accessed from the .tree
    attribute. 

    Parameters:
    -----------
    newick (str):
        An input tree as a newick string, or filepath, or a functional
        weblink to a newick string.
    ladderize (bool):
        Whether to automatically ladderize the tree. Default=True.
    format (int):
        The tree format used for parsing the tree. See ETE tree formats. 
        The default 0 can handle most tree formats including NHX.
    fixed_order (bool):
        Enforce a fixed order of tip-labels. This can make the topology
        look very strange, but is useful for showing differences between
        topologies. Default=False.

    Attributes:
    -----------
    tree: ete3mini.Tree
        An ete TreeNode object representation of the tree. See the
        ete docs for full documentation. Toytree users will not typically
        need to interact with this object, but advanced users can benefit
        from learning the TreeNode object. 
    edges: ndarray
        An array of edges connecting nodes in the tree. Used internally
        for plotting, not of significant use to users.
    verts: ndarray
        An array of node (vertex) locations used for plotting. Used internally
        for plotting, not of significant use to users.
    newick: str
        A New Hampshire Newick format string representation of the tree.
    features: 
        A set of string names of features that are accessible from the tree 
        object. All trees will have {'dist', 'name', 'support'}, although the
        values 

    Functions:
    ----------
    get_tip_labels(): 
        See func docstring.
    get_edge_lengths():
        See func docstring.
    root(): 
        See func docstring.
    """

    def __init__(self, 
        newick=None, 
        ladderize=True, 
        format=0,
        fixed_order=None,
        **kwargs):

        ## use ETE to parse the tree and ladderize
        if newick:
            self.tree = ete3mini.TreeNode(newick, format=format)
            if ladderize and not fixed_order:
                self.tree.ladderize()
        ## otherwise make an empty TreeNode object        
        else:
            self.tree = ete3mini.TreeNode()

        ## default attributes and plot settings
        self.colors = COLORS         
        self._kwargs = {}
        self._default_style = DEFAULTS_ALL

        ## ensures ladderized top-down order for entered tip order
        self._fixed_order = fixed_order

        ## plotting coords
        self.edges = None
        self.verts = None
        self._lines = []    
        self._coords = []   

        ## plotting node values (features)
        ## checks one of root's children for features and extra feats.
        if self.tree.children:
            features = {"name", "dist", "support", "height", "idx"}
            testnode = self.tree.children[0]
            extrafeat = {i for i in testnode.features if i not in features}
            features.update(extrafeat)
            if any(extrafeat):
                self.newick = self.tree.write(format=9, features=features)
            else:
                self.newick = self.tree.write(format=0)

            ## parse newick, assign idx, returns tre, edges, verts, names
            ## assigns node_labels, tip_labels, edge_lengths and support values
            ## use default orient and edge_lengths right now for init.
            self._decompose_tree(
                orient="right", #self._kwargs["orient"],
                use_edge_lengths=True, #self._kwargs["use_edge_lengths"], 
                fixed_order=self._fixed_order)



    @property
    def features(self):
        """ return features registered on ete3mini tree"""
        return self.tree.features


    ## functions to return values from the ete3 .tree object
    def get_edge_lengths(self):
        """
        Returns edge length values from tree object in node plot order. To 
        modify edge length values you must modify nodes in the .tree object 
        directly. For example:
        
        for node in tree.tree.traverse():
            node.dist = 1.
        """
        ## access nodes in the order they will be plotted
        return self.get_node_values('dist', True, True)


    def get_node_values(self, feature=None, show_root=False, show_tips=False):
        """
        Returns node values from tree object in node plot order. To modify
        values you must modify the .tree object directly by setting new 
        'features'. For example, 
        
        for node in tree.tree.traverse():
            node.add_feature("PP", 100)

        By default node and tip values are hidden (set to "") so that they
        are not shown on the tree plot. To include values for these nodes
        use the 'show_root'=True, or 'show_tips'=True arguments. 

        """

        ## access nodes in the order they will be plotted
        ## this is a customized order best sampled this way
        nodes = [self.tree.search_nodes(name=str(i))[0] \
                 for i in self.get_node_dict().values()]
        #nodes = [i for i in self.tree.traverse("preorder")]


        ## get features
        if feature:
            vals = [i.__getattribute__(feature) \
                    if hasattr(i, feature) else "" for i in nodes]
        else:
            vals = [" " for i in nodes]

        ## apply hiding rules
        if not show_root:
            vals = [i if not j.is_root() else "" for i, j  in zip(vals, nodes)]
        if not show_tips:
            vals = [i if not j.is_leaf() else "" for i, j  in zip(vals, nodes)]

        ## convert float to ints for prettier printing unless all floats
        ## raise exception and skip if there are true strings (names)
        try:
            if all([Decimal(str(i)) % 1 == 0 for i in vals if i]):
                vals = [int(i) if isinstance(i, float) else i for i in vals]
        except Exception:
            pass

        return vals


    def get_node_dict(self):
        """
        Return node labels as a dictionary mapping {idx: name} where
        idx is the order of nodes in 'preorder' traversal. Used internally
        by get_node_values() to return values in proper order. 
        """
        names = {}
        idx = sum(1 for i in self.tree.traverse()) -1
        ## preorder: first parent and then children
        for node in self.tree.traverse("preorder"):
            if not node.is_leaf():
                if node.name:
                    names[idx] = node.name
                idx -= 1

        ## names are in ladderized plotting order
        tiporder = self.tree.get_leaves()
        for node in tiporder:
            names[idx] = node.name
            idx -= 1
        return names


    def get_tip_labels(self):
        """
        returns tip labels in ladderized order from tip to bottom on 
        right-facing tree. Take care because this is the reverse of the 
        y-axis order, i.e., the tree plot bottom is at X=0. 
        """
        if self._fixed_order:
            return self._fixed_order[::-1]
        else:
            return self.tree.get_leaf_names()


    def __str__(self):
        """ return ascii tree ... (not sure whether to keep this) """
        return self.tree.__str__()


    def __len__(self):
        """ return len of Tree (ntips) """
        return len(self.tree)
        

    def copy(self):
        """ returns a deepcopy of the tree object"""
        return copy.deepcopy(self)


    ## unlike ete this returns a copy unrooted, not in-place!
    def unroot(self):
        """
        Returns a copy of the tree unrooted. Does not transform tree in-place.
        """
        newtree = copy.deepcopy(self)
        newtree.tree.unroot()
        newtree.tree.ladderize()
        
        ## get features
        testnode = newtree.tree.get_leaves()[0] 
        features = {"name", "dist", "support", "height"}
        extrafeat = {i for i in testnode.features if i not in features}
        features.update(extrafeat)
        if any(extrafeat):
            newtree.newick = newtree.tree.write(format=9, features=features)
        else:
            newtree.newick = newtree.tree.write(format=0)
        return newtree


    ## unlike ete this returns a copy resolved, not in-place!
    def resolve_polytomy(self, default_dist=0.0, default_support=0.0, recursive=False):
        """
        Returns a copy of the tree with resolved polytomies. 
        Does not transform tree in-place.
        """
        newtree = copy.deepcopy(self)
        newtree.tree.resolve_polytomy(
            default_dist=default_dist,
            default_support=default_support,
            recursive=recursive)

        ## get features
        testnode = newtree.tree.get_leaves()[0] 
        features = {"name", "dist", "support", "height"}
        extrafeat = {i for i in testnode.features if i not in features}
        features.update(extrafeat)        
        if any(extrafeat):
            newtree.newick = newtree.tree.write(format=9, features=features)
        else:
            newtree.newick = newtree.tree.write(format=0)
        return newtree


    def is_rooted(self):
        """
        Returns False if the tree is unrooted.
        """
        if len(self.tree.children) > 2:
            return False
        else:
            return True


    def is_bifurcating(self, include_root=True):
        """
        Returns False if there is a polytomy in the tree, including if the tree
        is unrooted (basal polytomy), unless you use the count_basal_polytomy=False
        argument.
        """

        if self.is_rooted():
            if ((2 * len(self)) - 1) == sum(1 for i in self.tree.traverse()):
                return True
            else:
                return False
        else:
            if include_root:
                if ((2 * len(self)) - 2) == sum(1 for i in self.tree.traverse())-1:
                    return True
                else:
                    return False
            else:
                if ((2 * len(self)) - 2) == sum(1 for i in self.tree.traverse()):
                    return True
                else:
                    return False




    ## re-rooting the tree
    def root(self, outgroup=None, wildcard=None, regex=None):
        """
        Re-root a tree on a selected tip or group of tip names. Rooting is 
        done in-place, meaning the tree object will be modified and there is no
        return object. 

        The new root can be selected by entering either a list of outgroup 
        names, by entering a wildcard selector that matches their names, or 
        using a regex command to match their names. For example, to root a tree
        on a clade that includes the samples "1-A" and "1-B" you can do any of 
        the following:

        rtre = tre.root(outgroup=["1-A", "1-B"])
        rtre = tre.root(wildcard="1-")
        rtre = tre.root(regex="1-[A,B]")

        """

        ## make a deepcopy of the tree
        nself = self.copy()

        ## set names or wildcard as the outgroup
        if outgroup:
            if isinstance(outgroup, str):
                outgroup = [outgroup]
            notfound = [i for i in outgroup if i not in nself.tree.get_leaf_names()]
            if any(notfound):
                raise Exception("Sample {} is not in the tree".format(notfound))
            outs = [i for i in nself.tree.get_leaf_names() if i in outgroup]
        elif regex:
            outs = [i.name for i in nself.tree.get_leaves() if re.match(regex, i.name)]
            if not any(outs):
                raise Exception("No Samples matched the regular expression")
        elif wildcard:
            outs = [i.name for i in nself.tree.get_leaves() if wildcard in i.name]
            if not any(outs):
                raise Exception("No Samples matched the wildcard")
        else:
            raise Exception(\
            "must enter an outgroup, wildcard selector, or regex pattern")

        if len(outs) > 1:
            ## check if they're monophyletic
            mbool, mtype, mnames = nself.tree.check_monophyly(
                                        outs, "name", ignore_missing=True)
            if not mbool:
                if mtype == "paraphyletic":
                    outs = [i.name for i in mnames]
                else:
                    raise Exception("Tips entered to root() cannot be paraphyletic")
            out = nself.tree.get_common_ancestor(outs)
        else:
            out = outs[0]

        ## split root node if more than di- as this is the unrooted state
        if not nself.is_bifurcating():
            nself.tree.resolve_polytomy()

        ## root the object with ete's translate
        nself.tree.set_outgroup(out)

        ## get features
        testnode = nself.tree.get_leaves()[0] 
        features = {"name", "dist", "support", "height"}
        extrafeat = {i for i in testnode.features if i not in features}
        features.update(extrafeat)        

        ## if there is a new node now, clean up its features
        nnode = [i for i in nself.tree.traverse() if not hasattr(i, "idx")]
        if nnode:
            ## nnode is the node that was added
            ## rnode is the location where it *should* have been added
            nnode = nnode[0]
            rnode = [i for i in nself.tree.children if i != out][0]

            ## get idxs of existing nodes
            idxs = [int(i.idx) for i in nself.tree.traverse() if hasattr(i, "idx")]

            ## newnode is a tip
            if len(outs) == 1:
                nnode.name = str("rerooted")
                rnode.name = out
                rnode.add_feature("idx", max(idxs) + 1)
                rnode.dist *= 2
                sister = rnode.get_sisters()[0]
                sister.dist *= 2
                rnode.support = 100                
                for feature in extrafeat:
                    nnode.add_feature(feature, getattr(rnode, feature))
                    rnode.del_feature(feature)

            ## newnode is internal
            else:
                nnode.add_feature("idx", max(idxs) + 1)
                nnode.name = str("rerooted")
                nnode.dist *= 2
                sister = nnode.get_sisters()[0]
                sister.dist *= 2
                nnode.support = 100


        ## store tree back into newick and reinit Toytree with new newick
        ## if NHX format then preserve the NHX features. 
        nself.tree.ladderize()
        if any(extrafeat):
            nself.newick = nself.tree.write(format=9, features=features)
        else:
            nself.newick = nself.tree.write(format=0)
        return nself



    ## reset verts & edges based on args that might change
    def _decompose_tree(self, orient, use_edge_lengths, fixed_order):
        _decompose_tree(self, orient, use_edge_lengths, fixed_order)



    ## this is the user-interface where all options should be visible 
    def draw(
        self, 
        height=None,
        width=None,
        tip_labels=True,
        tip_labels_color=None,
        tip_labels_style=None,
        tip_labels_align=None,
        #tip_labels_angle=None,
        node_labels=False,
        node_labels_style=None,
        node_size=None,
        node_color=None,
        node_style=None,
        node_hover=None,
        #edge_width=None,
        edge_style=None,
        edge_align_style=None,        
        use_edge_lengths=None, 
        orient=None,#"right",
        tree_style=None,
        print_args=False,
        padding=50,
        axes=None, 
        *args,
        **kwargs):
        """
        Plot a Toytree tree, returns a tuple of (Canvas, Axes). 


        Parameters:
        -----------
            use_edge_lengths: bool
                Use edge lengths from .tree (.get_edge_lengths) else
                edges are set to length >=1 to make tree ultrametric.

            tip_labels: [True, False, list]
                If True then the tip labels from .tree are added to the plot.
                If False no tip labels are added. If a list of tip labels
                is provided it must be the same length as .get_tip_labels().

            tip_labels_color: 
                ...

            tip_labels_style:
                ...

            tip_labels_align:
                ...

            node_labels: [True, False, list] 
                If True then nodes are shown, if False then nodes are suppressed.
                If a list of node labels is provided it must be the same length 
                and order as nodes in .get_node_dict(). Node labels can be 
                generated in the proper order using the the .get_node_labels() 
                function from a Toytree tree to draw info from the tree features.
                For example: node_labels=tree.get_node_labels("support").

            node_size: [int, list, None]
                If None then nodes are not shown, otherwise, if node_labels 
                then node_size can be modified. If a list of node sizes is 
                provided it must be the same length and order as nodes in 
                .get_node_dict().

            node_color: [list]
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


        """
        ## return nothing if tree is empty
        if not self.tree.children:
            print("Tree is empty")
            return 

        ## load default styling in 'p'
        if tree_style == "c":
            self._kwargs = copy.deepcopy(self._default_style)
            self._kwargs.update(DEFAULTS_CTREES)
        # elif tree_style == "a":
        #     self._kwargs = copy.deepcopy(self._default_style)
        #     self._kwargs.update(DEFAULTS_ATREES)
        else: #if tree_style == "c":
            self._kwargs = copy.deepcopy(self._default_style)
            self._kwargs.update(DEFAULTS_PTREES)

        #self._kwargs = copy.deepcopy(self._default_style)
        entered = {
            "height": height,
            "width": width,
            "orient": orient,
            "tip_labels": tip_labels, 
            "tip_labels_color": tip_labels_color,
            "tip_labels_style": tip_labels_style,
            "tip_labels_align": tip_labels_align,        
            #"tip_labels_angle": tip_labels_angle,  
            "node_labels": node_labels,
            "node_labels_style": node_labels_style,
            "node_size": node_size,
            "node_color": node_color,
            "node_style": node_style,
            "node_hover": node_hover,
            #"edge_width": edge_width,  ## todo
            #"edge_color": edge_color,  ## todo
            "edge_style": edge_style,
            "edge_align_style": edge_align_style,
            "use_edge_lengths": use_edge_lengths,
            "tree_style": tree_style, 
        }

        ## We don't allow the setting of None to update defaults.
        ## stick all entered option into kwargs
        entered = {i:j for i,j in entered.items() if j is not None}
        for key, val in entered.items():
            if val is not None:
                if isinstance(val, dict):
                    self._kwargs[key].update(entered[key])
                else:
                    self._kwargs[key] = val

        ## re-decompose tree for new orient and edges args
        self._decompose_tree(
            orient=self._kwargs["orient"], 
            use_edge_lengths=self._kwargs["use_edge_lengths"], 
            fixed_order=self._fixed_order)

        ## if dims not entered in kwargs then set a reasonable height & width
        self._set_dims_from_tree_size()

        ## if not canvas then create one else use the existing
        if axes:
            canvas = None
        else:
            canvas = toyplot.Canvas(
                height=self._kwargs['height'], 
                width=self._kwargs['width']
                )
            axes = canvas.cartesian(
                #bounds=("10%", "90%", "10%", "90%"), 
                padding=padding,
                )
            axes.show = False

        self._assign_node_labels()
        self._assign_tip_labels()

        if print_args:
            print(self._kwargs)

        ## order of tree/nodes last (on top) is preferred
        tips = _add_tip_labels_to_axes(self, axes)
        tree = _add_tree_to_axes(self, axes)
        node = _add_nodes_to_axes(self, axes)

        return canvas, axes



    def _assign_tip_labels(self):
        """ parse arg or arglist for tip_labels and tip_colors """
        
        ## tip color overrides tipstyle[fill]
        if self._kwargs.get("tip_labels_color"):
            if 'fill' in self._kwargs["tip_labels_style"]:
                self._kwargs["tip_labels_style"].pop("fill")

        ## False = hide tip labels
        if self._kwargs["tip_labels"] == False: # in [False, None]:
            self._kwargs["tip_labels"] = ["" for i in self.get_tip_labels()]
            self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "0px"

        else:
            ## if user did not change label-offset then shift it here, using 
            ## either anchor-shift or baseline-shift depending on orientation
            if not self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"]:
                self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "15px"
                #if not isinstance(self._kwargs["node_size"], list):
                #    ns = [self._kwargs["node_size"], list]
                #else:
                #    ns = self._kwargs["node_size"]
                #if any(ns):
                #    self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "15px"
                #else:
                #    ## todo
                #    self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "15px"
            #else:
            #    pass#self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "10px"

            ## User-defined tip labels list
            if isinstance(self._kwargs["tip_labels"], list):
                self._kwargs["tip_labels"] = self._kwargs["tip_labels"]

            ## True assigns tip labels from tree
            else: 
                if self._fixed_order:
                    self._kwargs["tip_labels"] = self._fixed_order
                else:
                    self._kwargs["tip_labels"] = self.get_tip_labels()



    def _assign_node_labels(self):
        """ 
        parse arg or arglist for node_labels and node_colors. 
        If node_color is provided then it overrides node fill. 
        """

        ## False = Hide nodes and node labels (default)
        if self._kwargs["node_labels"] == False:
            ## make sure node size is a list in case
            if self._kwargs["node_size"]:
                if isinstance(self._kwargs["node_size"], (int, str)):
                    self._kwargs["node_size"] = [self._kwargs["node_size"]] * len(self.get_node_values())
                    self._kwargs["node_labels"] = ["" for i in self.get_node_values("idx")]

        ## True = Show nodes, no labels b/c we are adding interactives
        elif self._kwargs["node_labels"] == True:

            ## hide labels
            self._kwargs["vlshow"] = False
            self._kwargs["node_labels"] = ["" for i in self.get_node_values("idx")]

            ## ensure nsize is a list
            if not self._kwargs["node_size"]:
                self._kwargs["node_size"] = [15] * len(self.get_node_values())
            if isinstance(self._kwargs["node_size"], (int, str)):
                self._kwargs["node_size"] = [int(self._kwargs["node_size"])] * len(self.get_node_values())

        ## user list
        else: 
            ## show labels
            self._kwargs["vlshow"] = True

            ## user-provided list is shown
            if isinstance(self._kwargs["node_labels"], list):
                self._kwargs["node_labels"] = self._kwargs["node_labels"]

            elif isinstance(self._kwargs["node_labels"], str) and \
                 (self._kwargs["node_labels"] in self.features):
                 label = (self._kwargs["node_labels"], 1, 1)
                 self._kwargs["node_labels"] = self.get_node_values(*label)

            ## anything else defaults to idx
            else: 
                self._kwargs["node_labels"] = self.get_node_values("idx", 1, 0)

            ## set node size to 0 if labels are empty including "0" but not "".
            if not isinstance(self._kwargs["node_size"], list):
                ## set default size if none
                if (self._kwargs["node_size"] in [None, False]) and \
                   (self._kwargs["node_size"] != 0):
                    self._kwargs["node_size"] = 22

                ## fill a list of values
                nsizes = []
                for nidx in self.get_node_values("idx", 1, 1):
                    if self._kwargs["node_labels"][nidx] == "":
                        nsizes.append(0)
                    else:
                        nsizes.append(self._kwargs["node_size"])
                self._kwargs["node_size"] = nsizes



    def _set_dims_from_tree_size(self):
        """
        Calculate reasonable height and width for tree given N tips
        """
        if self._kwargs.get("orient") in ["right", "left"]:
            ## long tip-wise dimension 
            if not self._kwargs.get("height"):
                self._kwargs["height"] = max(275, min(1000, 18*(len(self.tree))))
            if not self._kwargs.get("width"):
                self._kwargs["width"] = max(225, min(500, 18*(len(self.tree))))
        else:
            ## long tip-wise dimension 
            if not self._kwargs.get("width"):
                self._kwargs["width"] = max(275, min(1000, 18*(len(self.tree))))
            if not self._kwargs.get("height"):
                self._kwargs["height"] = max(225, min(500, 18*(len(self.tree))))


################################################################################
## RANDOM TREES
################################################################################


def _node_dates_yule(nnodes, b):
    """
    generate a distribution of node ages under a yule model with birth rate.
    """
    pass


def _node_dates_bd(nnodes, b, d):
    """
    generate a distribution of node ages under a yule model with birth rate.
    """
    pass


def _node_dates_coal(nnodes, b):
    """
    generate a distribution of node ages under a yule model with birth rate.
    """
    pass


def randomtree(ntips, node_values={}):
    """
    Function to return a random tree w/ N tips using the ete function 
    'populate()'. Branch lengths can be added after the tree is 
    generated by modifying its features, or you can use one the preset
    modes for generating divergence times by setting nodes to one of 
    ['coalescent', 'yule', 'bd'], and adding params in paramsdict. 
    Examples below. 

    Parameters
    -----------
    ntips (int):
        The number of tips in the randomly generated tree

    node_values:
    
    """

    ## generate tree with N tips.
    tmptree = ete3mini.TreeNode()
    tmptree.populate(ntips)
    #tmptree.convert_to_ultrametric()
    self = Toytree(newick=tmptree.write())

    ## set values
    for fkey, vals in node_values.items():
        for idx, node in enumerate(self.tree.traverse()):
            node.add_feature(fkey, vals[idx])

    ## set tip names by labeling sequentially from t-0
    self.tree.ladderize()
    ntip=0
    for tip in self.get_tip_labels():
        node = self.tree.search_nodes(name=tip)[0]
        node.name = "t-{}".format(ntip)
        ntip += 1
    return self

## TODO: functions to generate trees under different branch length
## processes (Yule, BD) by adding nodes to a TreeNode object...



################################################################################
## TREE FUNCTIONS ##############################################################
################################################################################


def _decompose_tree(ttree, orient, use_edge_lengths, fixed_order): 
    """ 
    Decomposes tree into component coordinates for plotting. Assigns
    a name and idx to every node. 

    """

    ## set tmp attributes 
    ttree._orient = orient
    ttree._use_edge_lengths = use_edge_lengths
    ult = ttree._use_edge_lengths == False

    ## name indexes, start from zero to match normal idx, unless
    ## tip names are already numeric, in which case we assign names
    ## to internal nodes starting from the highest number
    nnodes = sum(1 for i in ttree.tree.traverse())
    idx = nnodes - 1

    ## store node heights 
    #root_height = ttree.tree.get_leaves()[0].dist

    ## highest numbering is for internals (N-M)    
    for node in ttree.tree.traverse("levelorder"):
        if not node.is_leaf():
            if not node.name:
                node.name = "i"+str(idx)
            node.add_feature("idx", idx)
            idx -= 1
            #height = root_height - ttree.tree.get_distance(node)
            #node.add_feature("height", height)

    ## lowest numbers are for tips (0-N)
    for node in ttree.tree.get_leaves():
        if not node.name:
            node.name = "t"+str(idx)
        node.add_feature("idx", idx)
        idx -= 1
        #height = root_height - ttree.tree.get_distance(node)
        #node.add_feature("height", height)

    ## compile coordinates for vertices and edges for plotting
    ttree.edges = np.zeros((nnodes-1, 2), dtype=int)
    ttree.verts = np.zeros((nnodes, 2), dtype=float)
    ttree._lines = []    
    ttree._coords = []   

    ## postorder: first children and then parents. This moves up the list.
    ## counting down from tip_num ensures ladderized order.
    nidx = 0
    tip_num = len(ttree.tree.get_leaves()) - 1
    #tip_num = 0
    
    ## tips to root to fill in the verts and edges
    ## postorder: starts from children then parents.
    for node in ttree.tree.traverse("postorder"):

        if node.is_leaf() and not node.is_root():
            ## get y-pos of tip
            node.y = ttree.tree.get_distance(node)
            if ult:
                node.y = 0. 
            
            ## get x-pos of tip
            if ttree._fixed_order:
                node.x = tip_num - ttree._fixed_order.index(node.name)
            else:
                node.x = tip_num
                tip_num -= 1

            ## edges connect this vert to
            ttree.verts[node.idx] = [node.x, node.y]
            ttree.edges[nidx] = [node.up.idx, node.idx]

        else:
            ## create new nodes left and right
            node.y = ttree.tree.get_distance(node)
            if ult:
                node.y = -1 * node.get_farthest_leaf(True)[1] - 1
            node.x = sum(i.x for i in node.children) / float(len(node.children))
            ttree.verts[node.idx] = [node.x, node.y]
            if not node.is_root():
	            ttree.edges[nidx, :] = [node.up.idx, node.idx]
        nidx += 1
        
    ## root to tips to fill in the coords and lines
    cidx = 0
    for node in ttree.tree.traverse():
        ## add yourself
        if not node.is_leaf():
            ttree._coords += [[node.x, node.y]]
            pidx = cidx
            cidx += 1
            for child in node.children:
                ## add children
                ttree._coords += [[child.x, node.y], [child.x, child.y]]
                ttree._lines += [[pidx, cidx]]    ## connect yourself to newx
                ttree._lines += [[cidx, cidx+1]]  ## connect newx to child
                cidx += 2

    ## convert to arrays
    ttree._coords = np.array(ttree._coords, dtype=float)
    ttree._lines = np.array(ttree._lines, dtype=int)

    ## invert for sideways trees; TODO
    if ttree._orient in ['up', 0]:
        pass
    if ttree._orient in ['left', 1]:
        ttree.verts[:, 1] = ttree.verts[:, 1] * -1
        ttree.verts = ttree.verts[:, [1, 0]]
        ttree._coords[:, 1] = ttree._coords[:, 1] * -1
        ttree._coords = ttree._coords[:, [1, 0]]

    ## TODO: there's a bug in cloud trees 'down' orientation drawings
    if ttree._orient in ['down', 0]:
        ttree.verts[:, 1] = ttree.verts[:, 1] * -1
        ttree._coords[:, 1] = ttree._coords[:, 1] * -1
        ttree.verts[:, 1] += ttree.verts[:, 0].min()
        ttree._coords[:, 1] += ttree._coords[:, 0].min()

    if ttree._orient in ['right', 3]:
        ttree.verts = ttree.verts[:, [1, 0]]
        ttree._coords = ttree._coords[:, [1, 0]]
        ttree.verts[:, 0] -= ttree.verts[:, 0].max()
        ttree._coords[:, 0] -= ttree._coords[:, 0].max()


## add the tree plot 
def _add_tree_to_axes(ttree, axes):
    """
    TODO: add edge color controls.
    """

    ## add the tree/graph ------------------------------------------------
    if ttree._kwargs["tree_style"] in ["c", "cladogram", "a", "admixture"]:
        mark = axes.graph(ttree.edges, 
                       vcoordinates=ttree.verts, 
                       vlshow=False,
                       vsize=0,
                       estyle=ttree._kwargs["edge_style"],
                       #ecolor=self.kwargs["edge_color"], ## ...
                       #ewidth=self.kwargs["edge_width"], ## def: 2
                       )
    else:
        ## add lines for phylogram
        mark = axes.graph(ttree._lines,                   ## fixed
                       vcoordinates=ttree._coords,        ## fixed
                       vlshow=False,                      ## fixed
                       vsize=0.,                          ## fixed
                       estyle=ttree._kwargs["edge_style"],
                       #ecolor=self.kwargs["edge_color"], ## ...
                       #ewidth=self.kwargs["edge_width"], ## def: 2
                       )
    return mark



def _add_nodes_to_axes(ttree, axes):
    """
    add nodes as text-markers
    """

    ## bail out if not any visible nodes (e.g., none w/ size>0)
    if not ttree._kwargs["node_labels"]:
        return

    ## debugging
    #print(ttree._kwargs["node_labels"])
    #print(ttree._kwargs["node_size"])
    #print(ttree._kwargs["node_labels_style"])    

    ## build markers
    marks = []
    for nidx in ttree.get_node_values('idx', 1, 1):

        ## select node value
        nlabel = ttree._kwargs["node_labels"][nidx]
        nsize = ttree._kwargs["node_size"][nidx]
        nstyle = copy.deepcopy(ttree._kwargs["node_style"])
        nlstyle = copy.deepcopy(ttree._kwargs["node_labels_style"])

        ## parsing color types is bit tricky b/c there are many accepted formats
        if isinstance(ttree._kwargs["node_color"], str):
            nstyle["fill"] = ttree._kwargs["node_color"]
        elif isinstance(ttree._kwargs["node_color"], (np.ndarray, list, tuple)):
            color = ttree._kwargs["node_color"][nidx]
            if isinstance(color, (np.ndarray, np.void, list, tuple)):
                color = toyplot.color.to_css(color)
            nstyle["fill"] = color
        else:
            pass

        ## create mark if text or node
        if (nlabel or nsize):
            mark = toyplot.marker.create(
                shape="o", 
                label=str(nlabel), 
                size=nsize,
                mstyle=nstyle,
                lstyle=nlstyle,
                )
        else:
            mark = ""

        ## store the nodes/marks
        marks.append(mark)


    ## build interactive hovers for specified labels
    def fullhover(ttree, ordered_features=["idx", "name", "dist", "support"]):
        ## build full features titles
        ordered_features += list(set(ttree.tree.features) - set(ordered_features))
        ordered_features
        title = [
            ["{}: {}".format(feature, i) for i in \
             ttree.get_node_values(feature, True, True)]
             for feature in ordered_features]
        title = ["\n".join(z) for z in zip(*title[:])]
        return title

    ## node_hover == True is a magic command to show all features interactive
    if (ttree._kwargs["node_hover"] == True):
        title = fullhover(ttree)

    elif isinstance(ttree._kwargs["node_hover"], list):
        ## return advice if improperly formatted
        title = ttree._kwargs["node_hover"]

    ## if hover is false then no hover
    else:
        title = None

    ## add nodes
    mark = axes.scatterplot(
        ttree.verts[:, 0],
        ttree.verts[:, 1], 
        marker=marks,
        title=title,
        )
    return mark



def _add_tip_labels_to_axes(ttree, axes):
    """
    Positions tip labels on the coordinate axes given some orientation
    """

    ## get coordinates of text from top to bottom (right-facing)
    if ttree._kwargs["orient"] in ["right"]:
        angle = 0.

        ## y-positions of tips are the (first) N rows of .verts
        #ypos = ttree.verts[-1*len(ttree.tree):, 1]
        ypos = ttree.verts[:len(ttree.tree), 1]
        if ttree._kwargs["tip_labels_align"]:

            ## x-position (edge) start is in column 0 of first N rows of .verts
            xpos = [ttree.verts[:, 0].max()] * len(ttree.tree)
            start = xpos

            ## x-position end is in column 0 of first N rows of .verts
            finish = ttree.verts[:len(ttree.tree), 0]

            ## make into arrays
            align_edges = np.array([(i, i+len(xpos)) for i in range(len(xpos))])
            align_verts = np.array(list(zip(start, ypos)) + list(zip(finish, ypos)))
        else:
            #x-position (edge) start is in column 0 of first N rows of .verts
            xpos = ttree.verts[:len(ttree.tree), 0]

        ## overwrite tip order after the above stuff if fixed order
        if ttree._fixed_order:
            ypos = range(len(ttree.tree))


    ## orient text for down-facing tree, angle by -90.             
    elif ttree._kwargs["orient"] in ['down']:
        #if ttree._kwargs["tip_labels_angle"]:
        #    angle = ttree._kwargs["tip_labels_angle"]
        #else:
        angle = -90.
        xpos = ttree.verts[:len(ttree.tree):, 0]
        if ttree._kwargs["tip_labels_align"]:
            ypos = [ttree.verts[:, 1].min()] * len(ttree.tree)
            start = ypos
            finish = ttree.verts[:len(ttree.tree), 1]
            align_edges = np.array([(i, i+len(ypos)) for i in range(len(ypos))])
            align_verts = np.array(list(zip(xpos, start)) + list(zip(xpos, finish)))
        else:
            ypos = ttree.verts[:len(ttree.tree), 1]

        ## overwrite tip order after the above stuff if fixed order
        if ttree._fixed_order:
            xpos = range(len(ttree.tree))

    ## add tip names to coordinates calculated above
    mark = axes.text(
        xpos, 
        ypos, 
        ttree._kwargs["tip_labels"][::-1],
        angle=angle,
        style=ttree._kwargs["tip_labels_style"],
        color=ttree._kwargs["tip_labels_color"],
        )

    ## get stroke-width for aligned tip-label lines (optional)
    ## copy stroke-width from the edge_style unless user set it
    if not ttree._kwargs["edge_align_style"].get("stroke-width"):
        ttree._kwargs["edge_align_style"]["stroke-width"] = \
            ttree._kwargs["edge_style"]["stroke-width"]

    ## add lines to connect tree tips to aligned tips. We don't 
    ## return this mark since it's optional.
    if ttree._kwargs["tip_labels_align"]:
        dash = axes.graph(
            align_edges,
            vcoordinates=align_verts,
            estyle=ttree._kwargs["edge_align_style"], 
            vlshow=False,
            vsize=0,
            )
    return mark
