#!/usr/bin/env python


from __future__ import print_function, division

import toyplot
import numpy as np
import copy
import re
import ete3mini
from decimal import Decimal

## color palette as a list
PALETTE = toyplot.color.Palette()
COLORS = [toyplot.color.to_css(i) for i in PALETTE]


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
        look very strange. Default=False.

    Attributes:
    -----------
    tree: ete3mini.Tree
        An ete TreeNode object representation of the tree. See the
        ete docs for full documentation. 
    edges: ndarray
        An array of edges connecting nodes in the tree. Used internally
        for plotting, not of significant use to users.
    verts: ndarray
        An array of node (vertex) locations used for plotting. These
        locations are useful for adding additional node information
        using Toyplot.scatterplot or related functions.
    newick: str
        A New Hampshire Newick format string representation of the tree.

    Functions:
    ----------
    get_edge_lengths():
        returns 

    """

    def __init__(self, 
        newick=None, 
        ladderize=True, 
        format=0, 
        fixed_order=None,
        **kwargs):

        ## let ete check whether tree can parse
        self.colors = COLORS         
        if newick:
            self.tree = ete3mini.TreeNode(newick, format=format)
            if ladderize and not fixed_order:
                self.tree.ladderize()
        else:
            self.tree = ete3mini.TreeNode()

        ## check features on a node that is not root for NHX, since root
        ## is sometimes not appended with values that other nodes have
        self._orient = "right"
        self._use_edge_lengths = False
        self._fixed_order = fixed_order

        ## plotting coords
        self.edges = None
        self.verts = None
        self._lines = []    
        self._coords = []   

        ## plotting node values (features)
        if self.tree.children:
            features = {"name", "dist", "support"}
            testnode = self.tree.children[0]
            extrafeat = {i for i in testnode.features if i not in features}
            features.update(extrafeat)
            if any(extrafeat):
                self.newick = self.tree.write(format=9, features=features)
            else:
                self.newick = self.tree.write(format=0)

            ## parse newick, assigns idx to nodes, returns tre, edges, verts, names
            ## assigns node_labels, tip_labels, edge_lengths and support values
            self._decompose_tree(
                orient=self._orient,
                use_edge_lengths=self._use_edge_lengths, 
                fixed_order=self._fixed_order)

        ## some plotting defaults
        #_palette = [toyplot.color.to_css(i) for i in PALETTE]
        self._kwargs = {}
        self._default_style = {
            ## add-on defaults
            "admixture": None,

            ## edge defaults
            "edge_style": {
                "stroke": "#292724", 
                "stroke-width": 2, 
                "stroke-linecap": "round", 
                },

            "edge_align_style": {
                "stroke": "darkgrey",       ## copies edge_style
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
            "vmarker": "o",

            ## tip label defaults
            "tip_labels": True,         
            "tip_labels_color": toyplot.color.near_black,    
            "tip_labels_align": False,
            "tip_labels_style": {
                "font-size": "12px",
                "text-anchor":"start", 
                "-toyplot-anchor-shift": None, #"0px", #None,
                "fill": "#292724", 
                },

            ## tree style and axes
            "tree_style": "p",
            }


    ## functions to return values from the ete3 .tree object
    def get_edge_lengths(self):
        """
        Returns edge length values from tree object in node plot order. To modify
        edge length values you must modify the .tree object directly. For example, 
        
        for node in tree.tree.traverse():
            node.dist = 1.
        """
        ## access nodes in the order they will be plotted
        return self.get_node_values('dist', True, True)
        #return [self.tree.search_nodes(name=str(i))[0].dist \
        #        for i in self.get_node_values("dist")]


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
                 for i in self.get_node_labels().values()]

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


    def get_node_labels(self):
        """
        return node labels as a dictionary mapping {idx: name}
        """
        names = {}
        idx = 0
        for node in self.tree.traverse("preorder"):
            if not node.is_leaf():
                if node.name:
                    names[idx] = node.name
                else:
                    names[idx] = idx
                idx += 1
        for node in self.tree.get_leaves(): 
            names[idx] = node.name
            idx += 1
        return names


    def get_tip_labels(self):
        """
        returns tip labels in ladderized order from tip to bottom on 
        right-facing tree. Take care because this is the reverse of the 
        y-axis order, i.e., the tree plot bottom is at X=0. 
        """
        if self._fixed_order:
            return self._fixed_order
        else:
            return self.tree.get_leaf_names()


    def __str__(self):
        """ return ascii tree ... (not sure whether to keep this) """
        return self.tree.__str__()


    def __len__(self):
        """ return len of Tree (ntips) """
        return len(self.tree)
        

    ## re-rooting the tree
    def root(self, outgroup=None, wildcard=None, regex=None):
        ## starting nnodes
        nnodes = sum(1 for i in self.tree.traverse())

        ## split root node if more than di-
        self.tree.resolve_polytomy()

        ## set names or wildcard as the outgroup
        if outgroup:
            if isinstance(outgroup, str):
                outgroup = [outgroup]
            notfound = [i for i in outgroup if i not in self.tree.get_leaf_names()]
            if any(notfound):
                raise Exception("Sample {} is not in the tree".format(notfound))
            outs = [i for i in self.tree.get_leaf_names() if i in outgroup]
        elif regex:
            if not any([i for i in self.tree.get_leaves() if re.match(regex, i.name)]):
                raise Exception("No Samples matched the regular expression")
            outs = [i for i in self.tree.get_leaves() if re.match(regex, i.name)]
        elif wildcard:
            if not any([i for i in self.tree.get_leaves() if wildcard in i.name]):
                raise Exception("No Samples matched the wildcard")
            outs = [i for i in self.tree.get_leaves() if wildcard in i.name]
        else:
            raise Exception(\
            "must enter an outgroup, wildcard selector, or regex pattern")
        if len(outs) > 1:
            out = self.tree.get_common_ancestor(outs)
        else:
            out = outs[0]

        ## set new outgroup
        self.tree.set_outgroup(out)
        self.tree.resolve_polytomy()

        ## IF we split a branch to root then double those edges
        if sum(1 for i in self.tree.traverse()) != nnodes:
            self.tree.children[0].dist = 2.*float(self.tree.children[0].dist)
            self.tree.children[1].dist = 2.*float(self.tree.children[1].dist)

        ## store tree back into newick and reinit Toytree with new newick
        ## if NHX format then preserve the NHX features. 
        testnode = self.tree.children[0]
        features = {"name", "dist", "support"}
        extrafeat = {i for i in testnode.features if i not in features}
        features.update(extrafeat)
        if any(extrafeat):
            self.newick = self.tree.write(format=9, features=features)
        else:
            self.newick = self.tree.write(format=0)

        ## reinit
        if isinstance(self, Toytree):
            self.__init__(newick=self.newick, 
                          orient=self._orient,
                          use_edge_lengths=self._use_edge_lengths
                          )
        else:
            self._decompose_tree(
                orient=self._orient, 
                use_edge_lengths=self._use_edge_lengths, 
                fixed_order=self._fixed_order
                )


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
        tip_labels_align=False,
        node_labels=False,
        node_labels_style=None,
        node_size=None,
        node_color=None,
        node_style=None,
        node_hover=None,
        #edge_width=None,
        edge_style=None,
        edge_align_style=None,        
        use_edge_lengths=False, 
        orient="right",
        tree_style="p",
        print_args=False,
        padding=50,
        axes=None):
        """
        plot the tree using toyplot.graph. 

        Parameters:
        -----------
            use_edge_lengths: bool
                Use edge lengths from .tree (.get_edge_lengths) else
                edges are set to length >=1 to make tree ultrametric.

            tip_labels: [True, False, list]
                If True then the tip labels from .tree are added to the plot.
                If False no tip labels are added. If a list of tip labels
                is provided it must be the same length as .get_tip_labels().

            node_labels: [True, False, list] 
                If True then then the `support` attribute from the .tree 
                are added to the plot with default styling.
                If False no node labels are added. If a list of node labels
                is provided it must be the same length as .get_node_labels().
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

        ## re-decompose tree for new orient and edges args
        self._decompose_tree(
            orient=orient, 
            use_edge_lengths=use_edge_lengths, 
            fixed_order=self._fixed_order)

        ## stick all entered option into kwargs
        ## start from default styles copied
        self._kwargs = copy.deepcopy(self._default_style)
        entered = {
            "height": height,
            "width": width,
            "tip_labels": tip_labels, 
            "tip_labels_color": tip_labels_color,
            "tip_labels_style": tip_labels_style,
            "tip_labels_align": tip_labels_align,        
            "node_labels": node_labels,
            "node_labels_style": node_labels_style,
            "node_size": node_size,
            "node_color": node_color,
            "node_style": node_style,
            "node_hover": node_hover,
            #"edge_width": edge_width
            "edge_style": edge_style,
            "edge_align_style": edge_align_style,
            "tree_style": tree_style, 
        }
        ## We don't allow the setting of None to update defaults.
        entered = {i:j for i,j in entered.items() if j != None}
        for key, val in entered.items():
            if val != None:
                if isinstance(val, dict):
                    self._kwargs[key].update(entered[key])
                else:
                    self._kwargs[key] = val
        ## if dims not set then guess a reasonable height & width
        if not self._kwargs.get("width"):
            self._kwargs["width"] = min(1000, 40*len(self.tree))
        if not self._kwargs.get("height"):
            self._kwargs["height"] = self._kwargs["width"]

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
        _add_tip_labels_to_axes(self, axes)
        _add_tree_to_axes(self, axes)
        _add_nodes_to_axes(self, axes)

        return canvas, axes



    def _assign_tip_labels(self):
        """ parse arg or arglist for tip_labels and tip_colors """
        
        ## tip color overrides tipstyle[fill]
        if self._kwargs.get("tip_labels_color"):
            self._kwargs["tip_labels_style"].pop("fill")

        ## False = hide tip labels
        if self._kwargs["tip_labels"] in [False, None]:
            self._kwargs["tip_labels"] = ["" for i in self.get_tip_labels()]
            self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "0px"

        else:
            ## if user did not change label-offset then shift it here, using 
            ## either anchor-shift or baseline-shift depending on orientation
            if not self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"]:
                if not isinstance(self._kwargs["node_size"], list):
                    ns = [self._kwargs["node_size"], list]
                else:
                    ns = self._kwargs["node_size"]
                if any(ns):
                    self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "15px"
                else:
                    ## todo
                    self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "15px"
            else:
                pass#self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "10px"


            ## User-defined tip labels list
            if isinstance(self._kwargs["tip_labels"], list):
                self._kwargs["tip_labels"] = self._kwargs["tip_labels"]

            ## True assigns tip labels from tree
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
                self._kwargs["node_size"] = [ns] * len(self.get_node_values())                

        ## user list
        else: 
            ## show labels
            self._kwargs["vlshow"] = True

            ## user-provided list is shown
            if isinstance(self._kwargs["node_labels"], list):
                self._kwargs["node_labels"] = self._kwargs["node_labels"]

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



################################################################################
## RANDOM TREE
################################################################################

def randomtree(ntips, node_values={}):

    ## generate tree
    tmptree = ete3mini.TreeNode()
    tmptree.populate(ntips)
    self = Toytree(newick=tmptree.write())

    ## set values
    for fkey, vals in node_values.iteritems():
        for idx, node in enumerate(self.tree.traverse()):
            node.add_feature(fkey, vals[idx])

    ## set tip names
    self.tree.ladderize()
    ntip=0
    for tip in self.get_tip_labels():
        node = self.tree.search_nodes(name=tip)[0]
        node.name = "t-{}".format(ntip)
        ntip += 1
    return self



class RandomTree(Toytree):
    def __init__(self, ntips, node_values={}):
        Toytree.__init__(self)

        ## generate tree
        self.tree = ete3mini.TreeNode()
        self.tree.populate(ntips)
        self.newick = self.tree.write()

        ## set values
        for fkey, vals in node_values.iteritems():
            for idx, node in enumerate(self.tree.traverse()):
                node.add_feature(fkey, vals[idx])

        ## set tip names
        self.tree.ladderize()
        ntip=0
        for tip in self.get_tip_labels():
            node = self.tree.search_nodes(name=tip)[0]
            node.name = "t-{}".format(ntip)
            ntip += 1
        self._decompose_tree(
            orient=self._orient, 
            use_edge_lengths=self._use_edge_lengths, 
            fixed_order=self._fixed_order
            )

        self.__init__(newick=self.newick, 
                      orient=self._orient,
                      use_edge_lengths=self._use_edge_lengths
                          )


################################################################################
## TREE FUNCTIONS ##############################################################
################################################################################


def _decompose_tree(ttree, orient, use_edge_lengths, fixed_order): 
    """ decomposes tree into component parts for plotting """

    ## set attributes
    ttree._orient = orient
    ttree._use_edge_lengths = use_edge_lengths
    ult = ttree._use_edge_lengths == False

    ## map numeric values to internal nodes from root to tips
    idx = 0
    for node in ttree.tree.traverse("preorder"):
        if not node.is_leaf():
            if not node.name:
                node.name = str(idx)
            node.add_feature("idx", idx)
            idx += 1
            
    ## map number to the tips, these will be the highest numbers
    for node in ttree.tree.get_leaves(): 
        if not ttree._fixed_order:
            node.add_feature("idx", idx)
            idx += 1
        else:
            node.add_feature("idx", idx + ttree._fixed_order.index(node.name))
    if ttree._fixed_order:
        idx += len(ttree.tree)

    ## compile coordinates for vertices and edges for plotting
    ttree.edges = np.zeros((idx - 1, 2), dtype=int)
    ttree.verts = np.zeros((idx, 2), dtype=float)
    ttree._lines = []    
    ttree._coords = []   

    ## postorder: first children and then parents. This moves up the list.
    nidx = 0
    tip_num = len(ttree.tree.get_leaves()) - 1
    
    ## tips to root to fill in the verts and edges
    for node in ttree.tree.traverse("postorder"):
        if node.is_leaf() and not node.is_root():
            ## set the xy-axis positions of the tips
            node.y = ttree.tree.get_distance(node)
            if ult:
                node.y = 0. 
            if not ttree._fixed_order:
                node.x = tip_num
            else:
                node.x = ttree._fixed_order.index(node.name)
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

    ## add the tree/graph ------------------------------------------------
    if ttree._kwargs["tree_style"] in ["c", "cladogram"]:
        _ = axes.graph(ttree.edges, 
                       vcoordinates=ttree.verts, 
                       estyle=ttree._kwargs["edge_style"], #... add round edges 
                       vsize=0,
                       vlshow=False,
                       #ecolor=self.kwargs["edge_color"], ## ...
                       #ewidth=self.kwargs["edge_width"], ## def: 2
                       )
    else:
        ## add lines for phylogram
        _ = axes.graph(ttree._lines,                      ## fixed
                       vcoordinates=ttree._coords,        ## fixed
                       vlshow=False,                      ## fixed
                       vsize=0.,                          ## fixed
                       estyle=ttree._kwargs["edge_style"],
                       #ecolor=self.kwargs["edge_color"], ## ...
                       #ewidth=self.kwargs["edge_width"], ## def: 2
                       )


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

        ## if no user specified shift, then shift based on values
        ## to fit better within nodes
        #hshift = "-{}px".format(len(str(nlabel)))
        #vshift = "-1.5px"
        #if not nlstyle.get("-toyplot-anchor-shift"):
        #    nlstyle["-toyplot-anchor-shift"] = hshift
        #if not nlstyle.get("baseline-shift"):
        #    nlstyle["baseline-shift"] = vshift

        ## color nodes
        if isinstance(ttree._kwargs["node_color"], list):
            nstyle["fill"] = ttree._kwargs["node_color"][nidx]

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
    axes.scatterplot(
        ttree.verts[:, 0],
        ttree.verts[:, 1], 
        marker=marks,
        title=title,
        )

    # ## plot feature nodes with interactive hover titles
    # axes.scatterplot(
    #     ttree.verts[:, 0],
    #     ttree.verts[:, 1], 
    #     mstyle=ttree._kwargs["node_style"],
    #     size=ttree._kwargs["node_size"],
    #     color=ttree._kwargs["node_color"],
    #     title=title,
    #     ##vmarker=ttree._kwargs["vmarker"],     ## def: 'o'            
    #     )

    # ## add node text ...
    # if ttree._kwargs["vlshow"]:
    #     axes.text(
    #         ttree.verts[:, 0], 
    #         ttree.verts[:, 1], 
    #         ttree._kwargs["node_labels"],
    #         style=ttree._kwargs["node_labels_style"],
    #         )



def _add_tip_labels_to_axes(ttree, axes):

    ## get coordinates of text from top to bottom (right-facing)
    if ttree._orient in ["right"]:
        angle = 0.
        ypos = ttree.verts[-1*len(ttree.tree):, 1]
        if ttree._kwargs["tip_labels_align"]:
            xpos = [ttree.verts[:, 0].max()] * len(ttree.tree)
            start = xpos
            finish = ttree.verts[-1*len(ttree.tree):, 0]
            align_edges = np.array([(i, i+len(xpos)) for i in range(len(xpos))])
            align_verts = np.array(zip(start, ypos) + zip(finish, ypos))
        else:
            xpos = ttree.verts[-1*len(ttree.tree):, 0]
            
    elif ttree._orient in ['down']:
        angle = -90.
        xpos = ttree.verts[-1*len(ttree.tree):, 0]
        if ttree._kwargs["tip_labels_align"]:
            ypos = [ttree.verts[:, 1].min()] * len(ttree.tree)
            start = ypos
            finish = ttree.verts[-1*len(ttree.tree):, 1]
            align_edges = np.array([(i, i+len(ypos)) for i in range(len(ypos))])
            align_verts = np.array(zip(xpos, start) + zip(xpos, finish))
        else:
            ypos = ttree.verts[-1*len(ttree.tree):, 1]

    ## add tip names 
    _ = axes.text(
        xpos, 
        ypos, 
        ttree._kwargs["tip_labels"],
        angle=angle,
        style=ttree._kwargs["tip_labels_style"],
        color=ttree._kwargs["tip_labels_color"],
        )

    ## copy stroke-width from the edge_style unless user set it
    if not ttree._kwargs["edge_align_style"].get("stroke-width"):
        ttree._kwargs["edge_align_style"]["stroke-width"] = \
            ttree._kwargs["edge_style"]["stroke-width"]

    ## add lines to connect tree tips to aligned tips
    if ttree._kwargs["tip_labels_align"]:
        axes.graph(
            align_edges,
            vcoordinates=align_verts,
            estyle=ttree._kwargs["edge_align_style"], 
            vlshow=False,
            vsize=0,
            )

