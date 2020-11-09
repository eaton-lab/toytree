#!/usr/bin/env python

from __future__ import print_function, division, absolute_import


import re
import os
from copy import deepcopy
import numpy as np
import toytree
import toyplot


#######################################################
# Exception Classes
#######################################################
class ToytreeError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TreeError(Exception):
    "A problem occurred during a TreeNode operation"
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return repr(self.value)


# TREE FORMATS
NW_FORMAT = {
    # flexible with support
    # Format 0 = (A:0.35,(B:0.72,(D:0.60,G:0.12)1.00:0.64)1.00:0.56);
    0: [
        ('name', str, True),
        ('dist', float, True),
        ('support', float, True),
        ('dist', float, True),
    ],

    # flexible with internal node names
    # Format 1 = (A:0.35,(B:0.72,(D:0.60,G:0.12)E:0.64)C:0.56);
    1: [
        ('name', str, True),
        ('dist', float, True),
        ('name', str, True),
        ('dist', float, True),      
    ],

    # strict with support values
    # Format 2 = (A:0.35,(B:0.72,(D:0.60,G:0.12)1.00:0.64)1.00:0.56);
    2: [
        ('name', str, False),
        ('dist', float, False),
        ('support', str, False),
        ('dist', float, False),      
    ],

    # strict with internal node names
    # Format 3 = (A:0.35,(B:0.72,(D:0.60,G:0.12)E:0.64)C:0.56);
    3: [
        ('name', str, False),
        ('dist', float, False),
        ('name', str, False),
        ('dist', float, False),      
    ],

    # strict with internal node names
    # Format 4 = (A:0.35,(B:0.72,(D:0.60,G:0.12)));
    4: [
        ('name', str, False),
        ('dist', float, False),
        (None, None, False),
        (None, None, False),      
    ],

    # Format 5 = (A:0.35,(B:0.72,(D:0.60,G:0.12):0.64):0.56);
    5: [
        ('name', str, False),
        ('dist', float, False),
        (None, None, False),
        ('dist', float, False),      
    ],

    # Format 6 = (A:0.35,(B:0.72,(D:0.60,G:0.12)E)C);
    6: [
        ('name', str, False),
        (None, None, False),
        (None, None, False),        
        ('dist', float, False),      
    ],

    # Format 7 = (A,(B,(D,G)E)C);
    7: [
        ('name', str, False),
        ('dist', float, False),
        ('name', str, False),        
        (None, None, False),        
    ],    


    # Format 8 = (A,(B,(D,G)));
    8: [
        ('name', str, False),
        (None, None, False),
        ('name', str, False),        
        (None, None, False),
    ],

    # Format 9 = (,(,(,)));
    9: [
        ('name', str, False),
        (None, None, False),
        (None, None, False),
        (None, None, False),
    ],    

    # Format 10 = ((a[&Z=1,Y=2]:1.0[&X=3], b[&Z=1,Y=2]:3.0[&X=2]):1.0[&L=1,W=0], ...
    # NHX Like mrbayes NEXUS common
    10: [
        ('name', str, True),
        ('dist', str, True),
        ('name', str, True),
        ('dist', str, True),
    ]
}



def parse_network(net, disconnect=True):
    """
    Parse network to extract the major topology. 
    This leaves the hybrid nodes in the tree and labels each with 
    .name="H{int}" and .gamma={float}.
    """
    # if net is a file then read the first line
    if os.path.exists(net):
        with open(net, 'r') as infile:
            net = infile.readline()

    # trim off loglik and anything after it (TODO: keep loglik)
    if ";" in net:
        net = net.split(";")[0] + ';'

    # sub :xxx:: to be ::: b/c I don't care about admix edge bls
    net = re.sub(r":\d.\w*::", ":::", net)

    # change H nodes to proper format
    while ",#" in net:
        pre, post = net.split(",#", 1)
        npre, npost = post.split(")", 1)
        newpre = npre.split(":")[0] + "-" + npre.split(":")[-1]
        net = pre + ")#" + newpre + npost
    net = net.replace(":::", "-")

    # parse cleaned newick and set empty gamma on all nodes
    net = toytree.tree(net, tree_format=1)

    # store admix data
    admix = {}

    # if not rooted choose any non-H root
    if not net.is_rooted():
        net = net.root(
            [i for i in net.get_tip_labels() if not i.startswith("#H")][0]
        )

    # Traverse tree to find hybrid nodes. If a hybrid node is labeled as a 
    # distinct branch in the tree then it is dropped from the tree and 
    for node in net.treenode.traverse("postorder"):

        # find hybrid nodes as internal nchild=1, or external with H in name
        if (len(node.children) == 1) or node.name.startswith("#H"):

            # assign name and gamma to hybrid nodes
            aname, aprop = node.name.split("-")
            aname = aname.lstrip("#")
            node.name = aname

            # assign hybrid to closest nodes up and down from edge
            # node.children[0].hybrid = int(aname[1:])
            # node.gamma = round(float(aprop), 3)
            # node.up.hybrid = int(aname[1:])

            # if root is a hybrid edge (ugh)
            if node.up is None:
                small, big = sorted(node.children, key=lambda x: len(x))
                root = toytree.TreeNode.TreeNode(name='root')
                node.children = [small]
                small.up = node
                node.up = root
                big.up = root
                root.children = [node, big]
                net.treenode = root

            # disconnect node by connecting children to parent
            if disconnect:

                # if tip is a hybrid
                if not node.children:
                    # get sister node
                    sister = [i for i in node.up.children if i != node][0]

                    # connect sister to gparent
                    sister.up = node.up.up
                    node.up.up.children.remove(node.up)
                    node.up.up.children.append(sister)

                # if hybrid is internal
                else:
                    node.up.children.remove(node)
                    for child in node.children:
                        child.up = node.up
                        node.up.children.append(child)

            # store admix data by descendants but remove hybrid tips
            desc = node.get_leaf_names()
            if aname in desc:
                desc = [i for i in node.up.get_leaf_names() if i != aname]
            desc = [i for i in desc if not i.startswith("#H")]

            # put this node into admix
            if aname not in admix:
                admix[aname] = (desc, aprop)

            # matching edge in admix, no arrange into correct order by minor
            else:
                # this is the minor edge
                if aprop < admix[aname][1]:
                    admix[aname] = (
                        admix[aname][0], 
                        desc, 
                        0.5, 
                        {}, 
                        str(round(float(aprop), 3)),
                    )

                # this is the major edge
                else:
                    admix[aname] = (
                        desc, 
                        admix[aname][0], 
                        0.5, 
                        {}, 
                        str(round(float(admix[aname][1]), 3)),
                    )

    # update coords needed if node disconnection is turned back on.
    net._coords.update()
    net = net.ladderize()
    return net, admix




class Annotator(object):
    """
    Add annotations as a new mark on top of an existing toytree mark.
    """
    def __init__(self, tree, axes, mark):
        self.tree = tree
        self.axes = axes
        self.mark = mark


    def draw_clade_box(
        self, 
        names=None, 
        regex=None, 
        wildcard=None, 
        yspace=None, 
        xspace=None, 
        **kwargs):
        """
        Draw a rectangle around a clade on a toytree.

        Parameters:
        -----------
        names, regex, wildcard:
            Choose one of these three methods to select one or more tipnames. 
            The clade composing all descendants of their common ancestor will 
            be highlighted.

        yspace (float or None):
            The extent to which boxes extend above and below the root and tip
            nodes. If None then this is automatically generated.

        xspace (float or None):
            The extent to which the clade box extends to the sides 
            (out of the clade towards other tips.) If None default uses 0.5.

        kwargs:
            Additional styling options are supported: color, opacity, etc.

        Returns:
        ------------
        Toyplot.mark.Range
        """

        # get the common ancestor
        nidx = self.tree.get_mrca_idx_from_tip_labels(
            names=names, regex=regex, wildcard=wildcard)

        # get tips descended from mrca
        tips = self.tree.idx_dict[nidx].get_leaves()
        tidxs = [i.idx for i in tips]

        # extent to which box bounds extend outside of the exact clade size.
        if not yspace:
            yspace = self.tree.treenode.height / 15.
        if not xspace:
            xspace = 0.45

        # left and right positions
        if self.mark.layout == 'r':
            xmin = self.mark.ntable[nidx, 0] - yspace
            xmax = max(self.mark.ntable[tidxs, 0]) + yspace
            ymin = min(self.mark.ntable[tidxs, 1]) - xspace
            ymax = max(self.mark.ntable[tidxs, 1]) + xspace   

        if self.mark.layout == 'l':
            xmin = self.mark.ntable[nidx, 0] + yspace
            xmax = max(self.mark.ntable[tidxs, 0]) - yspace
            ymin = max(self.mark.ntable[tidxs, 1]) + xspace
            ymax = min(self.mark.ntable[tidxs, 1]) - xspace   

        elif self.mark.layout == 'd':
            ymax = self.mark.ntable[nidx, 1] + yspace
            ymin = min(self.mark.ntable[tidxs, 1]) - yspace
            xmin = min(self.mark.ntable[tidxs, 0]) - xspace
            xmax = max(self.mark.ntable[tidxs, 0]) + xspace               

        elif self.mark.layout == 'u':
            ymin = self.mark.ntable[nidx, 1] - yspace
            ymax = min(self.mark.ntable[tidxs, 1]) + yspace
            xmin = min(self.mark.ntable[tidxs, 0]) - xspace
            xmax = max(self.mark.ntable[tidxs, 0]) + xspace               

        # draw the rectangle
        newmark = self.axes.rectangle(xmin, xmax, ymin, ymax, **kwargs)

        # put tree at the top of the scenegraph
        self.axes._scenegraph.remove_edge(self.axes, 'render', self.mark)
        self.axes._scenegraph.add_edge(self.axes, 'render', self.mark)

        return newmark



    # def draw_tip_box(
    #     self, 
    #     names=None, 
    #     regex=None, 
    #     wildcard=None, 
    #     yspace=None, 
    #     xspace=None, 
    #     **kwargs):
    #     """
    #     Draw a rectangle around the tips of a clade on a toytree.

    #     Parameters:
    #     -----------
    #     names, regex, wildcard:
    #         Choose one of these three methods to select one or more tipnames. 
    #         The clade composing all descendants of their common ancestor will 
    #         be highlighted.

    #     yspace (float or None):
    #         The extent to which boxes extend above and below the root and tip
    #         nodes. If None then this is automatically generated.

    #     xspace (float or None):
    #         The extent to which the clade box extends to the sides 
    #         (out of the clade towards other tips.) If None default uses 0.5.

    #     kwargs:
    #         Additional styling options are supported: color, opacity, etc.

    #     Returns:
    #     ------------
    #     Toyplot.mark.Range
    #     """

    #     # get the common ancestor
    #     nidx = self.tree.get_mrca_idx_from_tip_labels(
    #         names=names, regex=regex, wildcard=wildcard)

    #     # get tips descended from mrca
    #     tips = self.tree.idx_dict[nidx].get_leaves()
    #     tidxs = [i.idx for i in tips]

    #     # get nudge size from dists in the tree or user supplied
    #     if not yspace:
    #         yspace = self.tree.get_node_values("dist", 1, 1).mean() / 4.
    #     if not xspace:
    #         xspace = 0.5

    #     # distance in PIXELS to the tip labels
    #     tipx = toyplot.units.convert(
    #         mark.tip_labels_style["-toyplot-anchor-shift"], 'px')

    #     # left and right positions
    #     if self.mark.layout == 'r':           

    #         # get unit conversion
    #         tipstart = tipx / (axes.project('x', 1) - axes.project('x', 0))
    #         xmin = self.mark.ntable[nidx, 0] - yspace
    #         xmax = max(self.mark.ntable[tidxs, 0]) + yspace
    #         ymin = min(self.mark.ntable[tidxs, 1]) - xspace
    #         ymax = max(self.mark.ntable[tidxs, 1]) + xspace   

    #     if self.mark.layout == 'l':
    #         xmin = self.mark.ntable[nidx, 0] + yspace
    #         xmax = max(self.mark.ntable[tidxs, 0]) - yspace
    #         ymin = max(self.mark.ntable[tidxs, 1]) + xspace
    #         ymax = min(self.mark.ntable[tidxs, 1]) - xspace   

    #     elif self.mark.layout == 'd':
    #         ymax = self.mark.ntable[nidx, 1] + yspace
    #         ymin = min(self.mark.ntable[tidxs, 1]) - yspace
    #         xmin = min(self.mark.ntable[tidxs, 0]) - xspace
    #         xmax = max(self.mark.ntable[tidxs, 0]) + xspace               

    #     elif self.mark.layout == 'u':
    #         ymin = self.mark.ntable[nidx, 1] - yspace
    #         ymax = min(self.mark.ntable[tidxs, 1]) + yspace
    #         xmin = min(self.mark.ntable[tidxs, 0]) - xspace
    #         xmax = max(self.mark.ntable[tidxs, 0]) + xspace               

    #     # draw the rectangle
    #     mark = self.axes.rectangle(xmin, xmax, ymin, ymax, **kwargs)
    #     return mark



    # def generate_rectangle(self, firstname=None, lastname=None, axes=None, color="green", opacity=.25):
    #     """
    #     Returns an updated axes with a generated rectangle based on input labels provided
    #     """
    #     index_of_first = self.get_mrca_idx_from_tip_labels(names=firstname)
    #     index_of_last =  self.get_mrca_idx_from_tip_labels(names=lastname)
    #     x_vals = (x[0] for x in self.get_node_coordinates())

    #     axes.rectangle(
    #         min(self.get_tip_coordinates()[index_of_first][0],  self.get_tip_coordinates()[index_of_last][0]),
    #         max(x_vals),
    #         self.get_tip_coordinates()[index_of_first][1],
    #         self.get_tip_coordinates()[index_of_last][1],
    #         opacity=opacity,
    #         color=color,
    #     )
    #     return axes





# class TreeInference:
# - get distance matrix (from an input data set... phy, nex)
# - ----- create a class to store DNA matrix (pandas colored)
# - NJ tree infer
#   ------ uses distance matrix
# - UPGMA tree infer
#   ------ uses distance matrix


#class TreeMoves:
#     def move_spr(self):
#         """
#         Sub-tree pruning and Regrafting. 
#         Select one edge randomly from the tree and split on that edge to create
#         two subtrees. Attach one of the subtrees (e.g., the smaller one) 
#         randomly to the larger tree to create a new node.
#         ... does SPR break edges connected to root when tree is real rooted?
#         """
#         pass
#         # On rooted trees we can work with nodes easier than edges. Start by
#         # selected a node at random that is not root.
#         # nodes = [i for i in self.ttree.tree.traverse() if not i.is_root()]
#         # rnode = nodes[random.randint(0, len(nodes) - 1)]
#         # # get all edges on the tree, skip last one which is non-real root edge
#         # edges = self.ttree.tree.get_edges()[:-1]
#         # # select a random edge
#         # redge = edges[random.randint(0, len(edges))]
#         # # break into subtrees
#         # tre1 = self.tree.prune(self.tree.get_common_ancestor(redge[0]).idx)
#         # tre2 = self.tree.prune(self.tree.get_common_ancestor(redge[1]).idx)



#     def move_tbr(self):
#         pass


#     def move_nni(self):
#         pass


#     def non_parametric_rate_smoothing(self):
#         """
#         Non-parametric rate smooting.
#         A method for estimating divergence times when evolutionary rates are 
#         variable across lineages by minimizing ancestor-descendant local rate
#         changes. According to Sanderson this method is motivated by the 
#         likelihood that evolutionary rates are autocorrelated in time.

#         returns Toytree
#         """
#         # p is a fixed exponent
#         p = 2
#         W = []
#         for node in self.ttree.traverse():
#             if not node.is_leaf():
#                 children = node.children
#                 ks = []
#                 for child in children:
#                     dist = abs(node.dist - child.dist)
#                     ks.append(dist ** p)
#                 W.append(sum(ks))

#         # root rate is mean of all descendant rates -- 
#         # n is the number of edges (rates) (nnodes - 1 for root)
#         r_root = np.mean(W)
#         rootw = []
#         for child in self.ttree.tree.children:
#             rootw.append((r_rroot - child.dist) ** p)
#         w_root = sum(rootw)
#         W.append(w_root)
#         k = []
#         for 
#         k = sum(  np.exp(abs(ri - rj), p)  )
#         W = sum(k)


#     def penalized_likelihood(...):
#         pass
#

# def wfunc(ttree, p):
#     ws = []
#     for node in ttree.tree.traverse():
#         if not node.is_leaf():          
#             w = sum([(node.dist - child.dist) ** p for child in node.children])
#             ws.append(w)
#     return sum(ws)






#######################################################
# Other
#######################################################
def bpp2newick(bppnewick):
    "converts bpp newick format to normal newick. ugh."
    regex1 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[:]")
    regex2 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[;]")
    regex3 = re.compile(r": ")
    new = regex1.sub(":", bppnewick)
    new = regex2.sub(";", new)
    new = regex3.sub(":", new)
    return new.strip()



# TODO: would be useful for (eg., root) to have option to return not mrca, 
# and fuzzy match just tips, or nodes, etc...




def normalize_values(vals, nbins=10, minsize=2, maxsize=12):
    """
    Distributes values into bins spaced at reasonable sizes for plotting.
    Example, this can be used automatically scale Ne values to plot as 
    edge widths.
    """

    # make copy of original
    ovals = deepcopy(vals)

    # if 6X min value is higher than max then add this 
    # as a fake value to scale more nicely
    vals = list(vals)
    if min(vals) * 6 > max(vals):
        vals.append(min(vals) * 6)

    # sorted vals list
    svals = sorted(vals)

    # put vals into bins
    bins = np.histogram(vals, bins=nbins)[0]

    # convert binned vals to widths in 2-12
    newvals = {}
    sizes = np.linspace(minsize, maxsize, nbins)
    for idx, inbin in enumerate(bins):
        for num in range(inbin):
            newvals[svals.pop(0)] = sizes[idx]
    return np.array([newvals[i] for i in ovals])



# def fuzzy_match_tipnames(ttree, names, wildcard, regex, mono=True, retnode=True):
def fuzzy_match_tipnames(ttree, names, wildcard, regex, mrca=True, mono=True):
    """
    Used in multiple internal functions (e.g., .root()) and .drop_tips())
    to select an internal mrca node, or multiple tipnames, using fuzzy matching
    so that every name does not need to be written out by hand.

    name: verbose list
    wildcard: matching unique string
    regex: regex expression
    mrca: return mrca node of selected tipnames. 
    mono: raise error if selected tipnames are not monophyletic    
    """
    # require arguments
    if not any([names, wildcard, regex]):
        raise ToytreeError(
            "must enter an outgroup, wildcard selector, or regex pattern")

    # get list of **nodes** from {list, wildcard, or regex}
    tips = []
    if names:
        if isinstance(names, (str, int)):
            names = [names]
        notfound = [i for i in names if i not in ttree.get_tip_labels()]
        if any(notfound):
            raise ToytreeError(
                "Sample {} is not in the tree".format(notfound))
        tips = [i for i in ttree.treenode.get_leaves() if i.name in names]

    # use regex to match tipnames
    elif regex:
        tips = [
            i for i in ttree.treenode.get_leaves() if re.match(regex, i.name)
        ]               
        if not any(tips):
            raise ToytreeError("No Samples matched the regular expression")

    # use wildcard substring matching
    elif wildcard:
        tips = [i for i in ttree.treenode.get_leaves() if wildcard in i.name]
        if not any(tips):
            raise ToytreeError("No Samples matched the wildcard")

    # build list of **tipnames** from matched nodes
    if not tips:
        raise ToytreeError("no matching tipnames")       
    tipnames = [i.name for i in tips]

    # if a single tipname matched no need to check for monophyly
    if len(tips) == 1:
        if mrca:
            return tips[0]
        else:
            return tipnames

    # if multiple nodes matched, check if they're monophyletic
    mbool, mtype, mnames = (
        ttree.treenode.check_monophyly(
            tipnames, "name", ignore_missing=True)
    )

    # get mrca node
    node = ttree.treenode.get_common_ancestor(tips)

    # raise an error if required to be monophyletic but not
    if mono:
        if not mbool:
            raise ToytreeError(
                "Taxon list cannot be paraphyletic")

    # return tips or nodes
    if not mrca:
        return tipnames
    else:
        return node
