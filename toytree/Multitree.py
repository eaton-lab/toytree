#!/usr/bin/env python

"MultiTree objects"

from __future__ import print_function, absolute_import
from builtins import str, range

#from contextlib import contextmanager
import os
from collections import defaultdict
from .ete3mini import TreeNode
from .Toytree import Toytree
from .TreeStyle import TreeStyle
from .utils import bpp2newick
import toyplot
import requests
import numpy as np


###############################################
# MultiTree Class object
###############################################
class MultiTree:
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
    def __init__(self, newick):

        # setting attributes
        self.newick = newick
        self._ts = tree_slice
        self._fixed_order = None      # <- do we need this before plotting?
        self._style = TreeStyle("m")
        self._i = 0

        # parse the newick object into a list of Toytrees
        self.treelist = []
        self._parse_treelist()

    # attributes of multitrees
    def __len__(self):  
        return len(self.treelist)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.treelist[self._i]
        except IndexError:
            self._i = 0
            raise StopIteration
        self._i += 1
        return result

    # private functions --------------------------------------------
    def _parse_treelist(self):
        """
        Parse a multiline newick from str, file, or url, and store
        new attributes to self for .newick, .tree_list, and ._tformat
        """
        # sample one line for testing --------------------------------
        if any(i in self.newick for i in ("http://", "https://")):
            try:
                response = requests.get(self.newick)
                response.raise_for_status()
                treelines = response.text.strip().split("\n")
                #treelines = treelines[self._ts[0]:self._ts[1]:self._ts[2]]
                self._treelines_to_treelist(treelines)
            except Exception as inst:
                raise inst

        # if a list then each element is either a toytree or a str
        elif isinstance(self.newick, list):
            if isinstance(self.newick[0], Toytree):
                treelines = [i.newick for i in self.newick]
                self._treelines_to_treelist(treelines)

            elif isinstance(self.newick[0], str):
                treelines = self.newick#[self._ts[0]:self._ts[1]:self._ts[2]]
                self._treelines_to_treelist(treelines)

        # assume remaining type is a str -------
        # check if newick is a file handle
        elif os.path.isfile(self.newick):
            self.newick = os.path.abspath(os.path.expanduser(self.newick))
            with open(self.newick) as infile:
                treelines = infile.read().split("\n")
                treelines = treelines#[self._ts[0]:self._ts[1]:self._ts[2]]
                self._treelines_to_treelist(treelines)
        else:
            treelines = self.newick.strip().split("\n")
            treelines = treelines#[self._ts[0]:self._ts[1]:self._ts[2]]
            self._treelines_to_treelist(treelines)


    def _treelines_to_treelist(self, treelines):

        #### TODO: get rid of treeformat and allow automatic detection...
        # check if a bpp tree
        tformat = "normal"
        if (" #" in treelines[0]) and (": " in treelines[0]):
            tformat = "bpp"

        # badnewick to goodnewick
        if tformat == "bpp":
            treelines = [bpp2newick(i.strip()) for i in treelines]

        # use user-set fixed order for tip plotting
        if self._fixed_order:
            self.treelist = [
                Toytree(i.strip(), fixed_order=self._fixed_order)
                for i in treelines]

        # get fixed order for tip plotting from consensus tree
        else:
            # order nodes for plotting
            self.treelist = [Toytree(i.strip()) for i in treelines]
            #self._fixed_order = self.treelist[0].get_tip_labels()
            # = self.get_consensus_tree().get_tip_labels()[::-1]
            # redefine treelist with trees plotted in consensus tip order
            #self.treelist = [
            #    Toytree(i.tree.write(), fixed_order=self._fixed_order)
            #    for i in self.treelist]

    # -------------------------------------------------------------------
    # Tree List Statistics or Calculations
    # -------------------------------------------------------------------
    def get_consensus_tree(self, cutoff=0.0, best_tree=None):
        """
        Returns an extended majority rule consensus tree as a Toytree object.
        Node labels include 'support' values showing the occurrence of clades 
        in the consensus tree across trees in the input treelist. 
        Clades with support below 'cutoff' are collapsed into polytomies.
        If you enter an optional 'best_tree' then support values from
        the treelist calculated for clades in this tree, and the best_tree is
        returned with support values added to nodes. 

        Params
        ------
        cutoff (float; default=0.0): 
            Cutoff below which clades are collapsed in the majority rule 
            consensus tree. This is a proportion (e.g., 0.5 means 50%). 
        best_tree (Toytree; optional):
            A tree that support values should be calculated for and added to. 
            For example, you want to calculate how often clades in your best 
            ML tree are supported in 100 bootstrap trees. 
        """
        if best_tree:
            raise NotImplemented("best_tree option not yet supported.")
        cons = ConsensusTree(self, cutoff)
        cons.update()
        return cons.tree
        #constre, clade_counts = consensus_tree(self.treelist, cutoff=cutoff)
        #return Toytree(constre.write())

    # -------------------------------------------------------------------
    # Tree List Plotting
    # -------------------------------------------------------------------
    def draw_tree_grid(self, x=1, y=5, start=0, **kwargs):
        """
        Draw a slice of trees into a x,y grid non-overlapping. 
        x = number of grid cells in x dimension.
        y = number of grid cells in y dimension.
        start: starting index of tree slice from .trees.
        kwargs: plotting functions applied to Canvas, axes, or all marks.
        """
        # Toyplot creates a grid and margins and puts trees in them..
        if kwargs.get("debug"):
            return TreeGrid(self)
        TreeGrid(self).update(x, y, start, **kwargs)


    def draw_cloud_tree(self):
        """
        Docstring...
        """
        CloudTree().update()




class ConsensusTree:
    """
    An extended majority rule consensus function.
    Modelled on the similar function from scikit-bio tree module. If
    cutoff=0.5 then it is a normal majority rule consensus, while if
    cutoff=0.0 then subsequent non-conflicting clades are added to the tree.
    """
    def __init__(self, mtree, cutoff=0.0):

        self.treelist = mtree.treelist
        self.names = self.treelist[0].get_tip_labels()
        self.cutoff = float(cutoff)
        self.tree = None
        self.namedict = None
        self.clade_counts = None
        self.fclade_counts = None
        self.tree = None
        self.nodelist = None

        assert cutoff < 1, "cutoff should be a float proportion (e.g., 0.5)"

    def update(self):
        # Find which clades occured with freq > cutoff. 
        # Fills namedict, clade_counts
        self.find_clades()

        # Filter out the < cutoff clades
        # Fills fclade_counts
        self.filter_clades()

        # Build consensus tree.
        # Fills .tree
        self.build_trees()  # fclade_counts, namedict)
        ## todo. make sure no singleton nodes were left behind ...


    def find_clades(self):
        "Count clade occurrences."
        # index names from the first tree
        ndict = {j: i for i, j in enumerate(self.names)}
        namedict = {i: j for i, j in enumerate(self.names)}

        # store counts
        clade_counts = {}
        for tree in self.treelist:
            
            # testing on unrooted trees is easiest...
            tree = tree.unroot()
            for node in tree.tree.traverse('preorder'):
                bits = np.zeros(len(tree), dtype=np.bool_)
                for child in node.iter_leaf_names():
                    bits[ndict[child]] = True

                # get bit string and its reverse
                bitstring = "".join((str(i) for i in bits.astype(int)))
                revstring = "".join((str(i) for i in np.invert(bits).astype(int)))

                # add to clades first time, then check for inverse next hits
                if bitstring in clade_counts:
                    clade_counts[bitstring] += 1
                else:
                    if revstring not in clade_counts:
                        clade_counts[bitstring] = 1
                    else:
                        clade_counts[revstring] += 1

        # convert to freq
        for key, val in clade_counts.items():
            clade_counts[key] = val / float(len(self.treelist))

        ## return in sorted order
        self.namedict = namedict
        self.clade_counts = sorted(
            clade_counts.items(),
            key=lambda x: x[1],
            reverse=True)


    def filter_clades(self):
        passed = []
        carrs = np.array([list(i[0]) for i in self.clade_counts], dtype=int)
        freqs = np.array([i[1] for i in self.clade_counts])

        for idx in range(carrs.shape[0]):
            conflict = False
            if freqs[idx] < self.cutoff:
                continue
            
            for pidx in passed:
                intersect = np.max(carrs[idx] + carrs[pidx]) > 1
                
                # is either one a subset of the other?
                subset_test0 = np.all(carrs[idx] - carrs[pidx] >= 0)
                subset_test1 = np.all(carrs[pidx] - carrs[idx] >= 0)
                if intersect:
                    if (not subset_test0) and (not subset_test1):
                        conflict = True

            if not conflict:
                passed.append(idx)

        rclades = []
        for idx in passed:
            rclades.append((carrs[idx], freqs[idx]))
        self.fclade_counts = rclades


    def build_trees(self):
        "Build an unrooted consensus tree from filtered clade counts."

        # storage
        nodes = {}
        idxarr = np.arange(len(self.fclade_counts[0][0]))
        queue = []

        ## create dict of clade counts and set keys
        countdict = defaultdict(int)
        for clade, count in self.fclade_counts:
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
                name = self.namedict[name]
            else:
                name = None

            # the clade will not be in nodes if it is a tip
            children = [nodes.pop(c) for c in clade if c in nodes]
            node = TreeNode(name=name)
            for child in children:
                node.add_child(child)
            if not node.is_leaf():
                node.dist = int(round(100 * countdict[clade]))
                node.support = int(round(100 * countdict[clade]))
            else:
                node.dist = int(100)
                node.support = int(100)

            nodes[clade] = node
            queue = new_queue
        nodelist = list(nodes.values())
        tre = nodelist[0]
        #tre.unroot()
        ## return the tree and other trees if present
        self.tree = Toytree(tre.write(format=0))
        self.tree._coords.update()
        self.nodelist = nodelist




class TreeGrid:
    def __init__(self, mtree):
        
        # plot objects are init on update()
        self.canvas = None
        self.cartesian = None
        self.trees = None
        self.mtree = mtree

        # to be filled
        self.x = None
        self.y = None
        self.treelist = []

    def update(self, x, y, start, **kwargs):

        # store plot dims and assert that they fit well enough
        self.x = x
        self.y = y
        self.treelist = self.mtree.treelist[start:start + self.x * self.y]

        # todo: mess with padding and margins...
        wdef = min(1000, self.y * 300)
        hdef = min(1000, self.x * 300)
        self.canvas = toyplot.Canvas(
            width=(kwargs.get('width') if kwargs.get('width') else wdef), 
            height=(kwargs.get('height') if kwargs.get('height') else hdef),
        ) 
        # todo: test with kwargs

        # get max treeheight
        ymax = max([i.tree.height for i in self.mtree])
        for tidx, tree in enumerate(self.treelist):
            # set ymax on cartesian so that trees are on same scale
            axes = self.canvas.cartesian(
                grid=(self.x, self.y, tidx),
                ymax=ymax,
                margin=35,
                padding=10,
            )
            tree.draw(axes=axes, **kwargs)
            axes.x.show = False


# TODO:
# This is going to require working with .fixed_order. This should be an 
# attribute of mtree objects, not Toytrees... right?. It needs to be used 
# by Toytrees during .update() tho..., or atleast by Coords for node positions.
class CloudTree:

    def __init__(self):
        pass

    def update(self):
        pass

    def set_dims_from_tree_size(self):
        "Calculate reasonable height and width for tree given N tips"
        tlen = len(self.treelist[0])
        if self._style.get("orient") in ["right", "left"]:
            # long tip-wise dimension
            if not self._style.get("height"):
                self._style["height"] = max(275, min(1000, 18 * (tlen)))
            if not self._style.get("width"):
                self._style["width"] = max(225, min(500, 18 * (tlen)))
        else:
            # long tip-wise dimension
            if not self._style.get("width"):
                self._style["width"] = max(275, min(1000, 18 * (tlen)))
            if not self._style.get("height"):
                self._style["height"] = max(225, min(500, 18 * (tlen)))
