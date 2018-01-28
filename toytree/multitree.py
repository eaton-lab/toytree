#!/usr/bin/env python

""" MultiTree objects """

from .tree import Toytree as tree
from .tree import COLORS
from collections import defaultdict
from . import ete3mini as ete
import numpy as np
import toyplot
import copy
import re
import os


DEFAULTS_MULTITREE = {
    ## edge defaults
    "edge_style": {
        "stroke": "#292724",
        "stroke-width": 2,
        #"stroke-linecap": "round",
        "opacity": 0.2,
        },

    "edge_align_style": {
        "stroke": "darkgrey",       ## copies edge_style
        #"stroke-linecap": "round",
        "stroke-dasharray": "2, 4",
        },

    ## node label defaults
    "node_labels": False,
    "node_labels_style": {
        "font-size": "9px",
        "fill": "262626"},

    ## node defaults
    "node_size": None,
    "node_color": COLORS[0],
    "node_style": {
        "fill": COLORS[0],
        "stroke": COLORS[0],
        },
    "vmarker": "o",

    ## tip label defaults
    "tip_labels": True,
    "tip_labels_color": toyplot.color.near_black,
    "tip_labels_align": False,
    "tip_labels_style": {
        "font-size": "12px",
        "text-anchor":"start",
        "-toyplot-anchor-shift": "12px",
        "fill": "#292724",
        },

    ## tree style and axes
    "tree_style": "p",
}


###############################################
## MultiTree Class object
###############################################
class MultiTree(object):
    """
    Toytree MultiTree object for representing multiple trees.

    Attributes:
    -----------
    treelist: list
        A list of toytree objects from the parsed newick file

    Functions():
    ------------
    consenstree: str
        Returns a consenus tree object...

    """
    def __init__(self,
        newick,
        tree_format=None,
        treeslice=(None, None, None),
        skip=None,
        fixed_order=None,
        orient='down',
        use_edge_lengths=True,
        #root=None,
        ):

        ## setting attributes
        self.newick = newick
        self.colors = COLORS
        self._tformat = tree_format
        self._fixed_order = fixed_order
        self._orient = orient
        self._use_edge_lengths = use_edge_lengths
        #self.color_palette = [toyplot.color.to_css(i) for i in PALETTE]
        self._kwargs = {}
        self._default_style = DEFAULTS_MULTITREE

        ## parse and build tree list. There are several types
        ## of tree lists. The first we'll support is BPP.

        ## check format of multitree
        if not tree_format:
            ## get line for testing
            if os.path.isfile(self.newick):
                self.newick = os.path.abspath(os.path.expanduser(newick))
                with open(self.newick) as infile:
                    testdat = infile.readline()
            else:
                if ("http://" in newick) or ("https://" in newick):
                    import urllib2
                    response = urllib2.urlopen(newick)
                    testdat = response.readline()
                else:
                    testdat = self.newick.strip().split("\n")[0]
            ## check if a bpp tree
            if (" #" in testdat) and (": " in testdat):
                tformat = "bpp"
            else:
                tformat = "normal"

            ## parse the treefile
            if os.path.isfile(self.newick):
                self.newick = os.path.abspath(os.path.expanduser(newick))
                with open(self.newick) as infile:
                    intrees = infile.readlines()\
                        [treeslice[0]:treeslice[1]:treeslice[2]]
            else:
                if ("http://" in newick) or ("https://" in newick):
                    #response = urllib2.urlopen(newick)
                    response = urllib2.urlopen(newick)
                    intrees = response.readlines()\
                        [treeslice[0]:treeslice[1]:treeslice[2]]
                    intrees = [i.strip() for i in intrees]
                else:
                    intrees = self.newick.strip().split("\n")\
                        [treeslice[0]:treeslice[1]:treeslice[2]]
            ## badnewick to goodnewick
            if tformat == "bpp":
                intrees = [bpp2newick(i.strip()) for i in intrees]
            ## newick to toytree
            if fixed_order:
                self.treelist = [tree(i.strip(), fixed_order=fixed_order) for i in intrees]
            else:
                ## order nodes for plotting
                self.treelist = [tree(i.strip()) for i in intrees]
                constre = self.get_consensus_tree()
                #if root:
                #    constre.root(root)
                self._fixed_order = constre.get_tip_labels()[::-1]
                kwargs = {"format": 0, "fixed_order": fixed_order}
                self.treelist = [tree(i.tree.write(),
                    fixed_order=self._fixed_order) for i in self.treelist]


    def __len__(self):
        return len(self.treelist)


    def get_consensus_tree(self, cutoff=0.0):
        constre, clade_counts = consensus_tree(self.treelist, cutoff=cutoff)
        return tree(constre.write())


    def _set_dims_from_tree_size(self):
        """
        Calculate reasonable height and width for tree given N tips
        """
        tlen = len(self.treelist[0])
        if self._kwargs.get("orient") in ["right", "left"]:
            ## long tip-wise dimension 
            if not self._kwargs.get("height"):
                self._kwargs["height"] = max(275, min(1000, 18*(tlen)))
            if not self._kwargs.get("width"):
                self._kwargs["width"] = max(225, min(500, 18*(tlen)))
        else:
            ## long tip-wise dimension 
            if not self._kwargs.get("width"):
                self._kwargs["width"] = max(275, min(1000, 18*(tlen)))
            if not self._kwargs.get("height"):
                self._kwargs["height"] = max(225, min(500, 18*(tlen)))



    # def rootlist(self, outgroup=None, wildcard=None):
    #     ## root trees
    #     if not wildcard:
    #         _ = [i.root(outgroup=outgroup) for i in self.treelist]
    #     else:
    #         _ = [i.root(wildcard=wildcard) for i in self.treelist]
    #     _ = [i._decompose_tree(
    #             orient=i._orient,
    #             use_edge_lengths=i._use_edge_lengths,
    #             fixed_order=i._fixed_order)
    #             for i in self.treelist]



    def draw_cloudtree(self,
        axes=None,
        height=None,
        width=None,
        tip_labels=True,
        tip_labels_color=None,
        tip_labels_style=None,
        #tip_labels_align=False,
        node_labels=None, #False,
        node_labels_style=None,
        node_size=None,
        node_color=None,
        node_style=None,
        #edge_width=None,
        edge_style=None,
        edge_align_style=None,
        use_edge_lengths=True, #False,
        orient="down",
        tree_style="c",
        #print_args=False,
        #fixed_order=None,
        ):

        ## return nothing if tree is empty
        if not self.treelist:
            print("Tree is empty")
            return

        ## re-decompose tree for new orient and edges args
        for tidx in xrange(len(self.treelist)):
            #tre = self.treelist[tidx]
            self.treelist[tidx]._decompose_tree(
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
            #"tip_labels_align": tip_labels_align,
            "node_labels": node_labels,
            "node_labels_style": node_labels_style,
            "node_size": node_size,
            "node_color": node_color,
            "node_style": node_style,
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
        self._set_dims_from_tree_size()
        #    self._kwargs["width"] = min(1000, 25*len(self.treelist[0].tree))
        #if not 
        #    self._kwargs["height"] = self._kwargs["width"]

        ## if not canvas then create one else use the existing
        if axes:
            canvas = None
        else:
            canvas = toyplot.Canvas(
                height=self._kwargs['height'],
                width=self._kwargs['width'],
                )
            axes = canvas.cartesian(
                #bounds=("10%", "90%", "10%", "90%"))
                padding=50,
                )
            axes.show = False


        ## plot trees
        for tre in self.treelist:
            _, axes = tre.draw(
                axes=axes,
                use_edge_lengths=use_edge_lengths,
                node_labels=False,
                orient=orient,
                tree_style=self._kwargs["tree_style"],
                edge_style=self._kwargs["edge_style"],
                tip_labels=False,
                )

        ## add tip labels
        angle = 0
        if orient == "down":
            angle = -90
        if tip_labels == True:
            self._kwargs["tip_labels"] = self._fixed_order
        if self._kwargs["tip_labels"]:
            axes.text(
                #tre.verts[-1*len(tre):, 0],
                #tre.verts[-1*len(tre):, 1],
                tre.verts[:len(tre), 0],
                tre.verts[:len(tre), 1],
                self._kwargs["tip_labels"],
                style=self._kwargs["tip_labels_style"],
                angle=angle,
            )

        return canvas, axes




    # def root(self, outgroup=None, wildcard=None):
    #     ## starting nnodes
    #     nnodes = sum(1 for i in self.treelist[0].tree.traverse())

    #     ## set names or wildcard as the outgroup
    #     if outgroup:
    #         outs = [i for i in self.treelist[0].tree.get_leaf_names() if i in outgroup]
    #     elif wildcard:
    #         outs = [i for i in self.treelist[0].tree.get_leaves() if wildcard in i.name]
    #     else:
    #         raise Exception(
    #         "must enter either a list of outgroup names or a wildcard selector")

    #     if len(outs) > 1:
    #         out = self.treelist[0].tree.get_common_ancestor(outs)
    #     else:
    #         out = outs[0]

    #     ## set new outgroup
    #     [i.tree.set_outgroup(out) for i in self.treelist]
    #     [i.tree.resolve_polytomy() for i in self.treelist]

    #     ## IF we split a branch to root then double those edges
    #     for tree in self.treelist:
    #         if sum(1 for i in self.treelist[0].tree.traverse()) != nnodes:
    #             tree.children[0].dist *= 2.
    #             tree.children[1].dist *= 2.

    #     ## store tree back into newick and reinit Toytree with new newick
    #     ## if NHX format then preserve the NHX features.
    #     #testnode = self.treelist.tree.children[0]
    #     #features = {"name", "dist", "support"}
    #     #extrafeat = {i for i in testnode.features if i not in features}
    #     #features.update(extrafeat)
    #     #if any(extrafeat):
    #     #    self.newick = self.tree.write(format=9, features=features)
    #     #else:
    #     #    self.newick = self.tree.write(format=0)
    #     consens = self.get_consensus_tree()
    #     newick = "\n".join([i.tree.write() for i in self.treelist])

    #     ## reinit the multitrees object
    #     self.__init__(newick=self.newick,
    #                   #orient=self._orient,
    #                   #use_edge_lengths=self._use_edge_lengths,
    #                   fixed_order=consens.get_tip_labels(),
    #                   )



def consensus_tree(trees, names=None, cutoff=0.0):
    """
    An extended majority rule consensus function for ete.
    Modelled on the similar function from scikit-bio tree module. If
    cutoff=0.5 then it is a normal majority rule consensus, while if
    cutoff=0.0 then subsequent non-conflicting clades are added to the tree.
    """
    assert cutoff < 1, "cutoff should be a float proportion (e.g., 0.5)"

    ## find which clades occured with freq > cutoff
    namedict, clade_counts = _find_clades(trees, names=names)

    ## filter out the < cutoff clades
    fclade_counts = _filter_clades(clade_counts, cutoff)

    ## build tree
    consens_tree, _ = _build_trees(fclade_counts, namedict)
    ## make sure no singleton nodes were left behind
    return consens_tree, clade_counts



def _find_clades(trees, names):
    """
    A subfunc of consensus_tree(). Traverses trees to count clade
    occurrences. Names are ordered by names, else they are in
    the order of the first tree.
    """
    ## index names from the first tree
    if not names:
        names = trees[0].get_tip_labels() #leaf_names()
    ndict = {j:i for i, j in enumerate(names)}
    namedict = {i:j for i, j in enumerate(names)}

    ## store counts
    clade_counts = defaultdict(int)
    ## count as bitarray clades in each tree
    for tree in trees:
        #tree.tree.unroot()
        for node in tree.tree.traverse('postorder'):
            #bits = bitarray('0'*len(tree))
            bits = np.zeros(len(tree), dtype=np.bool_)
            for child in node.iter_leaf_names():
                bits[ndict[child]] = True
                #bits[ndict[child]] = 1
            bitstring = "".join([np.binary_repr(i) for i in bits])
            clade_counts[bitstring] += 1
            #clade_counts[bits.to01()] += 1

    ## convert to freq
    for key, val in clade_counts.items():
        clade_counts[key] = val / float(len(trees))

    ## return in sorted order
    clade_counts = sorted(clade_counts.items(),
                          key=lambda x: x[1],
                          reverse=True)
    return namedict, clade_counts



def _filter_clades(clade_counts, cutoff):
    """
    A subfunc of consensus_tree(). Removes clades that occur
    with freq < cutoff.
    """

    ## store clades that pass filter
    passed = []
    clades = np.array([list(i[0]) for i in clade_counts], dtype=np.int8)
    counts = np.array([i[1] for i in clade_counts], dtype=np.float64)

    for idx in xrange(clades.shape[0]):
        conflict = False

        if counts[idx] < cutoff:
            continue

        if np.sum(clades[idx]) > 1:
            # check the current clade against all the accepted clades to see if
            # it conflicts. A conflict is defined as:
            # 1. the clades are not disjoint
            # 2. neither clade is a subset of the other
            # OR:
            # 1. it is inverse of clade (affects only <fake> root state)
            # because at root node it mirror images {0011 : 95}, {1100 : 5}.
            for aidx in passed:
                #intersect = clade.intersection(accepted_clade)
                summed = clades[idx] + clades[aidx]
                intersect = np.max(summed) > 1
                subset_test0 = np.all(clades[idx] - clades[aidx] >= 0)
                subset_test1 = np.all(clades[aidx] - clades[idx] >= 0)
                invert_test = np.bool_(clades[aidx]) != np.bool_(clades[idx])

                if np.all(invert_test):
                    counts[aidx] += counts[idx]
                    conflict = True
                if intersect:
                    if (not subset_test0) and (not subset_test1):
                        conflict = True

        if conflict == False:
            passed.append(idx)

    ## rebuild the dict
    rclades = []#j for i, j in enumerate(clade_counts) if i in passed]
    ## set the counts to include mirrors
    for idx in passed:
        rclades.append((clades[idx], counts[idx]))
    return rclades



def _build_trees(fclade_counts, namedict):
    """
    A subfunc of consensus_tree(). Build an unrooted consensus tree
    from filtered clade counts.
    """

    ## storage
    nodes = {}
    idxarr = np.arange(len(fclade_counts[0][0]))
    queue = []

    ## create dict of clade counts and set keys
    countdict = defaultdict(int)
    for clade, count in fclade_counts:
        mask = np.int_(list(clade)).astype(np.bool)
        ccx = idxarr[mask]
        queue.append((len(ccx), frozenset(ccx)))
        countdict[frozenset(ccx)] = count

    while queue:
        queue.sort()
        (clade_size, clade) = queue.pop(0)
        new_queue = []

        # search for ancestors of clade
        for (_, ancestor) in queue:
            if clade.issubset(ancestor):
                # update ancestor such that, in the following example:
                # ancestor == {1, 2, 3, 4}
                # clade == {2, 3}
                # new_ancestor == {1, {2, 3}, 4}
                new_ancestor = (ancestor - clade) | frozenset([clade])
                countdict[new_ancestor] = countdict.pop(ancestor)
                ancestor = new_ancestor

            new_queue.append((len(ancestor), ancestor))

        # if the clade is a tip, then we have a name
        if clade_size == 1:
            name = list(clade)[0]
            name = namedict[name]
        else:
            name = None

        # the clade will not be in nodes if it is a tip
        children = [nodes.pop(c) for c in clade if c in nodes]
        node = ete.Tree(name=name)
        #node = toytree.tree(name=name).tree
        for child in children:
            node.add_child(child)
        if not node.is_leaf():
            node.dist = int(round(100*countdict[clade]))
            node.support = int(round(100*countdict[clade]))
        else:
            node.dist = int(100)
            node.support = int(100)

        nodes[clade] = node
        queue = new_queue
    tre = nodes.values()[0]
    #tre.unroot()
    ## return the tree and other trees if present
    return tre, list(nodes.values())



def bpp2newick(bppnewick):
    regex1 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[:]")
    regex2 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[;]")
    regex3 = re.compile(r": ")
    new = regex1.sub(":", bppnewick)
    new = regex2.sub(";", new)
    new = regex3.sub(":", new)
    return new
