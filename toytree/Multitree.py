#!/usr/bin/env python

"MultiTree objects"

from __future__ import print_function, absolute_import
from builtins import str, range

#from contextlib import contextmanager
import os
from copy import deepcopy
from collections import defaultdict
from .etemini import TreeNode
from .Toytree import ToyTree
from .TreeStyle import TreeStyle
from .MultiDrawing import TreeGrid, CloudTree
from .utils import bpp2newick
import toyplot
import toyplot.config
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
    get_consensus_tree: 
        Returns a ToyTree object with support values on nodes.
    draw_cloud_tree:
        Draws a plot with overlapping fixed_order trees.
    draw_grid_tree:
        Draws a plot with n x m trees in a grid.
    """
    def __init__(self, newick, fixed_order=False):

        # setting attributes
        self.newick = newick
        self.style = TreeStyle('m')
        self._fixed_order = fixed_order   # (<list>, True, False, or None)
        self._user_order = None
        self._cons_order = None
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

    @property
    def ntips(self):
        return self.treelist[0].ntips


    def copy(self):
        return deepcopy(self)


    def write(self, handle=None, format=0):
        if not handle:
            handle = "out.tre"
        with open(handle, 'w') as outtre:
            for tre in self.treelist:
                outtre.write(tre.newick + "\n")

    # private functions --------------------------------------------
    def _parse_treelist(self):
        """
        Parse a multiline newick from str, file, or url, and store
        new attributes to self for .newick, .tree_list, and ._tformat
        """
        # if URL prefix then call requests
        if any(i in self.newick for i in ("http://", "https://")):
            try:
                response = requests.get(self.newick)
                response.raise_for_status()
                treelines = response.text.strip().split("\n")
                self._treelines_to_treelist(treelines)
            except Exception as inst:
                raise inst

        # if a list then each element is either a toytree or a str
        elif isinstance(self.newick, list):
            if isinstance(self.newick[0], ToyTree):
                treelines = [i.newick for i in self.newick]
                self._treelines_to_treelist(treelines)

            elif isinstance(self.newick[0], str):
                treelines = self.newick
                self._treelines_to_treelist(treelines)

        # assume remaining type is a str -------
        # check if newick is a file handle
        elif os.path.isfile(self.newick):
            self.newick = os.path.abspath(os.path.expanduser(self.newick))
            with open(self.newick) as infile:
                treelines = infile.read().strip().split("\n")
                self._treelines_to_treelist(treelines)
        else:
            treelines = self.newick.strip().split("\n")
            self._treelines_to_treelist(treelines)


    def _treelines_to_treelist(self, treelines):
        "Parses treelist and sets tip order with fixed_order."
        # check if a bpp tree and convert to normal newick
        if (" #" in treelines[0]) and (": " in treelines[0]):
            treelines = [bpp2newick(i.strip()) for i in treelines]

        # get majrule consensus tree tip order
        treelist = [ToyTree(i.strip()) for i in treelines]
        cons = ConsensusTree(treelist)
        cons.update()
        self._cons_order = cons.ttree.get_tip_labels()

        # if user-set fixed order for tip plotting
        if isinstance(self._fixed_order, list):
            self._user_order = self._fixed_order

        # order to use for constraining ToyTrees: (user > cons > None)
        order = None
        if self._user_order:
            order = self._user_order
        elif self._fixed_order in (False, None):
            order = None
        else:
            order = self._cons_order

        # build tree list
        self.treelist = [
            ToyTree(i.strip(), fixed_order=order) for i in treelines]

    # -------------------------------------------------------------------
    # Tree List Statistics or Calculations
    # -------------------------------------------------------------------
    def get_tip_labels(self):
        """
        Returns the tip names in tree plot order starting from zero axis.
        If fixed_order is a user entered list then names are returned in that
        order. If fixed_order was True then the consensus tree order is 
        returned. If fixed_order was None or False then the order of the first
        ToyTree in .treelist is returned. 
        """
        if self._user_order:
            return self._user_order
        elif self._cons_order:
            return self._cons_order
        else:
            return self.treelist[0].get_tip_labels()


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
            raise NotImplementedError("best_tree option not yet supported.")
        cons = ConsensusTree(self.treelist, cutoff)
        cons.update()
        return cons.ttree

    # -------------------------------------------------------------------
    # Tree List Plotting
    # -------------------------------------------------------------------
    def draw_tree_grid(self, 
        x=1, 
        y=5, 
        start=0, 
        fixed_order=False, 
        shared_axis=False, 
        **kwargs):
        """
        Draw a slice of trees into a x,y grid non-overlapping. 
        x = number of grid cells in x dimension.
        y = number of grid cells in y dimension.
        start: starting index of tree slice from .trees.
        kwargs: plotting functions applied to Canvas, axes, or all marks.
        """
        # return nothing if tree is empty
        if not self.treelist:
            print("Treelist is empty")
            return None, None

        # Toyplot creates a grid and margins and puts trees in them.
        draw = TreeGrid(self.copy())
        if kwargs.get("debug"):
            return draw
        draw.update(x, y, start, shared_axis, **kwargs)


    def draw_cloud_tree(self, axes=None, html=False, edge_styles=None, **kwargs):
        """
        Draw a series of trees overlapping each other in coordinate space.
        The order of tip_labels is fixed in cloud trees so that trees with 
        discordant relationships can be seen in conflict. To change the tip
        order use the 'fixed_order' argument in toytree.mtree() when creating
        the MultiTree object.

        Parameters:
            axes (toyplot.Cartesian): toyplot Cartesian axes object.
            html (bool): whether to return the drawing as html (default=PNG).
            edge_styles: (list): option to enter a list of edge dictionaries.
            **kwargs (dict): styling options should be input as a dictionary.
        """
        # return nothing if tree is empty
        if not self.treelist:
            print("Treelist is empty")
            return None, None

        # set autorender format to png so we don't bog down notebooks
        try:
            changed_autoformat = False
            if not html:
                toyplot.config.autoformat = "png"
                changed_autoformat = True

            # no other pre-built tree styles allowed in clouds, only kwargs
            self.style = TreeStyle('m')
            censored = {i: j for (i, j) in kwargs.items() if j is not None}
            self.style.update(censored)

            # Send a copy of MultiTree to init Drawing object.
            draw = CloudTree(self.copy(), edge_styles)

            # and create drawing
            if kwargs.get("debug"):
                return draw

            # if user provided explicit axes then include them
            canvas, axes = draw.update(axes)
            return canvas, axes

        finally:
            if changed_autoformat:
                toyplot.config.autoformat = "html"




class ConsensusTree:
    """
    An extended majority rule consensus function.
    Modelled on the similar function from scikit-bio tree module. If
    cutoff=0.5 then it is a normal majority rule consensus, while if
    cutoff=0.0 then subsequent non-conflicting clades are added to the tree.
    """
    def __init__(self, treelist, cutoff=0.0):

        self.treelist = treelist
        self.names = self.treelist[0].get_tip_labels()
        self.cutoff = float(cutoff)
        self.namedict = None
        self.clade_counts = None
        self.fclade_counts = None
        self.ttree = None
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
        for ttree in self.treelist:
            
            # testing on unrooted trees is easiest...
            ttree = ttree.unroot()
            for node in ttree.treenode.traverse('preorder'):
                bits = np.zeros(len(ttree), dtype=np.bool_)
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
        self.ttree = ToyTree(tre.write(format=0))
        self.ttree._coords.update()
        self.nodelist = nodelist
