#!/usr/bin/env python


from __future__ import print_function, division

import toyplot
import numpy as np
import ete3 as ete
import copy
from decimal import Decimal


## color palette as a list
PALETTE = toyplot.color.Palette()
COLORS = [toyplot.color.to_css(i) for i in PALETTE]

## the main tree class
class Tree(object):
    """
    The toytree Tree Class object, a plotting wrapper around an 
    ete3 Tree Class object which can be accessed from the .tree
    attribute. 

    tree: ete3.Tree
        A tree object from the ete3 library. This holds all of the
        information for the tree. See the ete docs for how to modify
        the tree object.
    """

    def __init__(self, newick=None, admix=None, **kwargs):

        ## let ete check whether tree can parse
        self.tree = ete.Tree(newick)
        self.tree.ladderize()

        ## check features on a node that is not root for NHX, since root
        ## is sometimes not appended with values that other nodes have
        testnode = self.tree.children[0]
        features = {"name", "dist", "support"}
        extrafeat = {i for i in testnode.features if i not in features}
        features.update(extrafeat)
        if any(extrafeat):
            self.newick = self.tree.write(format=9, features=features)
        else:
            self.newick = self.tree.write(format=0)

        ## parse newick, assigns idx to nodes, returns tre, edges, verts, names
        ## assigns node_labels, tip_labels, edge_lengths and support values
        self._decompose_tree(**kwargs)

        ## some plotting defaults
        #self.color_palette = [toyplot.color.to_css(i) for i in PALETTE]
        self._kwargs = {}
        self._default_style = {
            ## edge defaults
            "edge_style": {"stroke": "#292724", 
                           "stroke-width": 2, 
                           "stroke-linecap": "round"},

            ## node label defaults
            "node_labels": False,       
            "node_labels_style": {"font-size": "9px"}, 

            ## node defaults
            "node_size": 0,             
            "node_color": COLORS[0],
            "node_style": {"fill": COLORS[0], 
                           "stroke": COLORS[0]},
            "vmarker": "o",

            ## tip label defaults
            "tip_labels": True,         
            "tip_labels_color": toyplot.color.near_black,    
            "tip_labels_style": {"font-size": "12px",
                                 "text-anchor":"start", 
                                 "-toyplot-anchor-shift":"10px", 
                                 "fill": "#292724"},

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
        return [self.tree.search_nodes(name=str(i))[0].dist \
                for i in self.get_node_values("dist")]


    def get_node_values(self, feature=None):
        """
        Returns support values from tree object in node plot order. To modify
        support values you must modify the .tree object directly. For example, 
        
        for node in tree.tree.traverse():
            node.support = 100

        """
        ## access nodes in the order they will be plotted
        ## this is a customized order best sampled this way
        nodes = [self.tree.search_nodes(name=str(i))[0] \
                 for i in self.get_node_labels().values()]

        if not feature:
            feature = "support"
        vals = [i.__getattribute__(feature) if \
               (hasattr(i, feature) and not i.is_leaf() and not i.is_root()) \
               else "" for i in nodes]

        ## convert float to ints for prettier printing unless all floats
        if all([Decimal(str(i)) % 1 == 0 for i in vals if i]):
            vals = [int(i) if isinstance(i, float) else i for i in vals]

        return vals


    def get_node_labels(self):
        """
        return node labels as a dictionary mapping {index: name}
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
        return self.tree.get_leaf_names()


    ## print ascii tree 
    def __str__(self):
        return self.tree.__str__()


    ## re-rooting the tree
    def root(self, outgroup=None, wildcard=None):
        ## starting nnodes
        nnodes = sum(1 for i in self.tree.traverse())

        ## set names or wildcard as the outgroup
        if outgroup:
            outs = [i for i in self.tree.get_leaf_names() if i in outgroup]
        elif wildcard:
            outs = [i for i in self.tree.get_leaves() if wildcard in i.name]
        else:
            raise IPyradError(\
            "must enter either a list of outgroup names or a wildcard selector")
        if len(outs) > 1:
            out = self.tree.get_common_ancestor(outs)
        else:
            out = outs[0]

        ## set new outgroup
        self.tree.set_outgroup(out)

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
        self.__init__(newick=self.newick, 
                      orient=self._orient,
                      use_edge_lengths=self._use_edge_lengths
                      )

    ## reset verts & edges based on args that might change
    def _decompose_tree(self, orient='right', use_edge_lengths=True):
        _decompose_tree(self, orient, use_edge_lengths)



    def _assign_tip_labels(self):
        """ parse arg or arglist for tip_labels and tip_colors """

        ## True=magic (use tip labels), False=None, list=use list
        if self._kwargs["tip_labels"] == False:
            self._kwargs["tip_labels"] = ["" for i in self.get_tip_labels()]

        else:
            if isinstance(self._kwargs["tip_labels"], list):
                self._kwargs["tip_labels"] = self._kwargs["tip_labels"]

            ## True shows tip labels from .tree
            else: 
                self._kwargs["tip_labels"] = self.get_tip_labels()



    def _assign_node_labels(self):
        """ parse arg or arglist for node_labels and node_colors """

        ## True=magic (hide tip nodes), False=None, list=list all including tips
        if self._kwargs["node_labels"] == False:
            self._kwargs["node_labels"] = self.get_node_labels().keys()
            self._kwargs["node_size"] = 0
            self._kwargs["vlshow"] = False

        else:
            ## ensure a large size for node unless user set it explicitly
            self._kwargs["vlshow"] = True
            if not self._kwargs["node_size"]:
                self._kwargs["node_size"] = 18

            ## True shows node labels (integers) including tips
            if isinstance(self._kwargs["node_labels"], list):
                self._kwargs["node_labels"] = self._kwargs["node_labels"]

            else: ## ttree._kwargs["node_labels"] == True:
                self._kwargs["node_labels"] = self.get_node_labels().keys()
                ## offset tips a little if not explicitly set
                if self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] == "10px":
                    self._kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "15px"

            ## only show nodes where there are labels including "0" but not "".
            self._kwargs["node_size"] = \
                [self._kwargs["node_size"] if i or i==0 else 0 \
                for i in self._kwargs["node_labels"]]



    ## this is the user-interface where all options should be visible 
    def draw(
        self, 
        height=None,
        width=None,
        tip_labels=True,
        tip_labels_color=None,
        tip_labels_style=None,
        node_labels=False,
        node_labels_style=None,
        node_size=None,
        node_color=None,
        node_style=None,
        #edge_width=None,
        edge_style=None,
        use_edge_lengths=False, 
        orient="right",
        tree_style="p",
        print_args=False,
        axes=None,
        *args,
        **kwargs):
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

        """
        ## re-decompose tree for new orient and edges args
        self._decompose_tree(orient=orient, use_edge_lengths=use_edge_lengths)

        ## stick all entered option into kwargs
        self._kwargs = copy.deepcopy(self._default_style)#.copy()
        entered = {
            "height": height,
            "width": width,
            "tip_labels": tip_labels, 
            "tip_labels_color": tip_labels_color,
            "tip_labels_style": tip_labels_style,
            "node_labels": node_labels,
            "node_labels_style": node_labels_style,
            "node_size": node_size,
            "node_color": node_color,
            "node_style": node_style,
            #"edge_width": edge_width
            "edge_style": edge_style,
            "tree_style": tree_style, 
        }
        entered = {i:j for i,j in entered.items() if j}
        for key, val in entered.items():
            if val != None:
                if isinstance(val, dict):
                    self._kwargs[key].update(entered[key])
                else:
                    self._kwargs[key] = val

        ## if dims not set then guess a reasonable height & width
        if not self._kwargs.get("width"):
            self._kwargs["width"] = min(1000, 25*len(self.tree))
        if not self._kwargs.get("height"):
            self._kwargs["height"] = self._kwargs["width"]

        ## if not canvas then create one else use the existing
        if axes:
            canvas = None
        else:
            canvas = toyplot.Canvas(height=self._kwargs['height'], 
                                    width=self._kwargs['width'])
            axes = canvas.cartesian(bounds=("10%", "90%", "10%", "90%"))    
            axes.show = False
        
        self._assign_node_labels()
        self._assign_tip_labels()

        if print_args:
            print(self._kwargs)
        _add_tree_to_axes(self, axes)
        _add_tip_labels_to_axes(self, axes)
        return canvas, axes



################################################################################
## TREE FUNCTIONS ##############################################################
################################################################################


def _decompose_tree(ttree, orient='right', use_edge_lengths=True): 
    """ decomposes tree into component parts for plotting """

    ## set attributes
    ttree._orient = orient
    ttree._use_edge_lengths = use_edge_lengths
    ult = use_edge_lengths == False

    ## map numeric values to internal nodes from root to tips
    names = {}
    idx = 0
    for node in ttree.tree.traverse("preorder"):
        if not node.is_leaf():
            if node.name:
                names[idx] = node.name
            else:
                names[idx] = idx
                node.name = str(idx)
            node.idx = idx
            idx += 1
            
    ## map number to the tips, these will be the highest numbers
    for node in ttree.tree.get_leaves(): 
        names[idx] = node.name
        node.idx = idx
        idx += 1

    ## compile coordinates for vertices and edges for plotting
    ttree.edges = np.zeros((idx - 1, 2), dtype=int)
    ttree.verts = np.zeros((idx, 2), dtype=float)
    ttree._lines = []    
    ttree._coords = []   

    ## postorder: first children and then parents. This moves up the list .
    nidx = 0
    tip_num = len(ttree.tree.get_leaves()) - 1
    
    ## tips to root to fill in the verts and edges
    for node in ttree.tree.traverse("postorder"):
        if node.is_leaf():
            ## set the xy-axis positions of the tips
            node.y = ttree.tree.get_distance(node)
            if ult:
                node.y = 0. 
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
    if ttree._orient in ['right', 3]:
        ttree.verts = ttree.verts[:, [1, 0]]
        ttree._coords = ttree._coords[:, [1, 0]]



## add the tree plot 
def _add_tree_to_axes(ttree, axes):

    ## add the tree/graph ------------------------------------------------
    if ttree._kwargs["tree_style"] in ["c", "cladogram"]:
        _ = axes.graph(ttree.edges, 
                       vcoordinates=ttree.verts, 
                       #ewidth=self.kwargs["edge_width"], 
                       #ecolor=toyplot.color.near_black, 
                       estyle=ttree._kwargs["edge_style"], #... add round edges 
                       vlabel=ttree._kwargs["node_labels"], #.keys(),
                       vlshow=ttree._kwargs["vlshow"],
                       vlstyle=ttree._kwargs["node_labels_style"],
                       vsize=ttree._kwargs["node_size"],            #self.kwargs["vsize"],
                       vstyle=ttree._kwargs["node_style"],
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
        
        ## add vertices for phylogram 
        ## should this just use a scatterplot so we can add title?
        _ = axes.graph(ttree.edges,                          ## fixed
                       vcoordinates=ttree.verts,             ## fixed
                       ewidth=0.,                            ## fixed
                       vmarker=ttree._kwargs["vmarker"],     ## def: 'o'
                       vlabel=ttree._kwargs["node_labels"],  ## def: True
                       vlshow=ttree._kwargs["vlshow"],       ## def: True
                       vlstyle=ttree._kwargs["node_labels_style"],     ##
                       vsize=ttree._kwargs["node_size"],     ## def: 10
                       vstyle=ttree._kwargs["node_style"],   ##
                       )



def _add_tip_labels_to_axes(ttree, axes):

    ## get coordinates of text from top to bottom (right-facing)
    if ttree._orient in ["right"]:
        xpos = [ttree.verts[:, 0].max()] * len(ttree._kwargs["tip_labels"])
        ypos = range(len(ttree.tree))[::-1]
        angle = 0.
    elif ttree._orient in ['down']:
        xpos = range(len(ttree.tree))[::-1]
        ypos = [ttree.verts[:, 1].min()] * len(ttree._kwargs["tip_labels"])
        angle = -90.

    ## tip color overrides tipstyle[fill]
    if ttree._kwargs.get("tip_labels_color"):
        ttree._kwargs["tip_labels_style"].pop("fill")

    ## plot on axes. color is added from top to bottom (right-facing)
    _ = axes.text(xpos, ypos, 
            ttree._kwargs["tip_labels"],
            angle=angle,
            style=ttree._kwargs["tip_labels_style"],
            color=ttree._kwargs["tip_labels_color"],
            ) 
