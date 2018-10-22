#!/usr/bin/env python

"MultiTree objects"

from __future__ import print_function, absolute_import
from builtins import str, range

#from contextlib import contextmanager
import os
from copy import deepcopy
from collections import defaultdict
from .ete3mini import TreeNode
from .Toytree import Toytree
from .TreeStyle import TreeStyle
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
        self._fixed_order = fixed_order
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
        # sample one line for testing --------------------------------
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
            if isinstance(self.newick[0], Toytree):
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
        # check if a bpp tree and convert to normal newick
        if (" #" in treelines[0]) and (": " in treelines[0]):
            treelines = [bpp2newick(i.strip()) for i in treelines]

        # if user-set fixed order for tip plotting
        if isinstance(self._fixed_order, list):
            self.treelist = [
                Toytree(i.strip(), fixed_order=self._fixed_order)
                for i in treelines]

        # if True then use consensus tree tip order
        elif self._fixed_order is True:
            treelist = [Toytree(i.strip()) for i in treelines]
            constre = MultiTree(treelist).get_consensus_tree()
            self._fixed_order = constre.get_tip_labels()
            self.treelist = [
                Toytree(i.strip(), fixed_order=self._fixed_order)
                for i in treelines]

        # don't order nodes for aligned-tip plotting                
        else:
            self.treelist = [Toytree(i.strip()) for i in treelines]

    # -------------------------------------------------------------------
    # Tree List Statistics or Calculations
    # -------------------------------------------------------------------
    def get_tip_labels(self):
        "returns the tip names in tree plot order starting from zero axis."
        if self._fixed_order in (None, False):
            return self.treelist[0].get_tip_labels()
        else:
            return self._fixed_order


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
        cons = ConsensusTree(self, cutoff)
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
        # Toyplot creates a grid and margins and puts trees in them..
        draw = TreeGrid(self, fixed_order)
        if kwargs.get("debug"):
            return draw
        draw.update(x, y, start, shared_axis, **kwargs)


    def draw_cloud_tree(self, axes=None, html=False, fixed_order=False, **kwargs):
        """
        Draw a series of trees overlapping each other in coordinate space.
        """
        # set autorender format to png so we don't bog down notebooks
        try:
            changed_autoformat = False
            if not html:
                toyplot.config.autoformat = "png"
                changed_autoformat = True
            
            # init Drawing. Fixed order is set here in treelist.
            draw = CloudTree(self, fixed_order=fixed_order)

            # and create drawing
            if kwargs.get("debug"):
                #draw.update(axes=axes, **kwargs)
                return draw

            # if user provided explicit axes then include them
            canvas, axes = draw.update(axes=axes, **kwargs)
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
    def __init__(self, mtree, cutoff=0.0):

        self.treelist = mtree.treelist
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
        self.ttree = Toytree(tre.write(format=0))
        self.ttree._coords.update()
        self.nodelist = nodelist



class TreeGrid:
    def __init__(self, mtree, fixed_order):
        
        # plot objects are init on update()
        self.canvas = None
        self.cartesian = None
        self.mtree = MultiTree(mtree.treelist, fixed_order=fixed_order)
        self.style = TreeStyle('n')

        # to be filled
        self.x = None
        self.y = None
        self.treelist = []

    def update(self, x, y, start, shared_axis, **kwargs):

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
        if not shared_axis:
            # get max treeheight
            for tidx, tree in enumerate(self.treelist):
                # set ymax on cartesian so that trees are on same scale
                axes = self.canvas.cartesian(
                    grid=(self.x, self.y, tidx),
                    margin=(20, 20, 35, 35),
                    padding=10,
                )
                tree.draw(axes=axes, **kwargs)
                axes.show = False

        else:
            axes = self.canvas.cartesian(
                    #bounds=()
                    #margin=35,
                    padding=10,
                    )
            # axes = self.axes.share(...)
            for tidx, tree in enumerate(self.treelist):
                pass
                # add +x to their verts?
                # or use share-axis args for axes <- yes.
        #return self.canvas, axes


class CloudTree:

    def __init__(self, mtree, fixed_order=None):
        
        # base style
        self.style = mtree.style

        # inherit fixed order, take arg, or use True
        self.fixed_order = mtree._fixed_order
        if fixed_order:
            self.fixed_order = fixed_order
        if not self.fixed_order:
            self.fixed_order = True

        # make new mtree using fixed order
        self.mtree = MultiTree(mtree.treelist, fixed_order=self.fixed_order)

        # tip labels get updated
        self.tip_labels = None

    def update(self, **kwargs):

        # return nothing if tree is empty
        if not self.mtree.treelist:
            print("Tree is empty")
            return

        # allow ts as a shorthand for tree_style
        if kwargs.get("ts"):
            kwargs["tree_style"] = kwargs.get("ts")

        # update tree_style base if entered as an argument
        if kwargs.get('tree_style'):
            newstyle = TreeStyle(kwargs.get('tree_style')[0])
            self.style.__dict__.update(newstyle.__dict__)

        # store entered args
        userkeys = [
            "height",
            "width",
            "orient",       
            "tip_labels",
            "tip_labels_color",
            "tip_labels_align",
            "node_labels",
            "node_size",
            "node_color",
            "node_hover",
            "edge_type",
            "use_edge_lengths",
            "scalebar",
            "padding",
        ]       
        userargs = {i: j for (i, j) in kwargs.items() if i in userkeys}
        dictkeys = [
            "edge_style",
            "edge_align_style",
            "tip_labels_style",
            "node_style",
            "node_labels_style",
        ]
        dictargs = {i: j for (i, j) in kwargs.items() if i in dictkeys}

        # update tree_style to custom style with user entered args
        censored = {i: j for (i, j) in userargs.items() if j is not None}
        self.style.__dict__.update(censored)

        # update style dicts
        censored = [i for i in dictargs if i is not None]
        for styledict in censored:
            sdict = dictargs[styledict]
            if sdict:
                self.style.__setattr__(styledict, sdict)

        # set reasonable dims if not user entered
        self.set_dims_from_tree_size()

        # if not canvas then creates one else uses the existing
        # sets self.canvas and self.axes
        self.get_canvas_and_axes(kwargs.get('axes'))

        # grab debug flag and pop it from dict
        debug = False
        if kwargs.get("debug"):
            debug = True

        # Decompoase edge_style list into list of dicts
        # could put something here to apply styles based on some calculation
        # such as different colors for different topologies...
        if isinstance(kwargs.get('edge_style'), list):
            if not len(kwargs['edge_style']) == len(self.mtree):
                raise IndexError('stylelist length must match treelist length')
            for idx, tre in enumerate(self.mtree.treelist):
                tre.style.edge_style = kwargs['edge_style'][idx]

        # pop tip labels and styles since they'll be blocked from subtrees
        tip_labels = deepcopy(self.style.tip_labels)
        tip_labels_style = deepcopy(self.style.tip_labels_style)
        self.style.tip_labels = False

        # unpack lists of style if applied to trees differently. Here we
        # can allow node_colors, node_sizes, edge_styles, 

        # plot trees on the same axes with shared style dict
        for tre in self.mtree.treelist:           
            tre.draw(axes=self.axes, **self.style.__dict__)

        # add a single call to tip labels
        self.style.tip_labels = tip_labels
        self.style.tip_labels_style = tip_labels_style
        self.assign_tip_labels_and_colors()
        self.add_tip_labels_to_axes()
        self.fit_tip_labels()

        # debug returns CloudTree object
        if debug:
            return self
        return self.canvas, self.axes


    def get_canvas_and_axes(self, axes):
        if axes: 
            self.canvas = None
            self.axes = axes
        else:
            self.canvas = toyplot.Canvas(
                height=self.style.height,
                width=self.style.width,
            )
            self.axes = self.canvas.cartesian(
                padding=self.style.padding,
            )


    def set_dims_from_tree_size(self):
        "Calculate reasonable height and width for tree given N tips"
        tlen = len(self.mtree.treelist[0])
        if self.style.orient in ("right", "left"):
            # long tip-wise dimension
            if not self.style.height:
                self.style.height = max(275, min(1000, 18 * (tlen)))
            if not self.style.width:
                self.style.width = max(225, min(500, 18 * (tlen)))
        else:
            # long tip-wise dimension
            if not self.style.width:
                self.style.width = max(275, min(1000, 18 * (tlen)))
            if not self.style.height:
                self.style.height = max(225, min(500, 18 * (tlen)))


    def add_tip_labels_to_axes(self):
        """
        Add text offset from tips of tree with correction for orientation, 
        and fixed_order which is usually used in multitree plotting.
        """
        # get tip-coords and replace if using fixed_order
        if self.style.orient in ("up", "down"):
            ypos = np.zeros(self.mtree.ntips)
            xpos = np.arange(self.mtree.ntips)

        if self.style.orient in ("right", "left"):
            xpos = np.zeros(self.mtree.ntips)
            ypos = np.arange(self.mtree.ntips)

        # pop fill from color dict if using color
        tstyle = deepcopy(self.style.tip_labels_style)
        if self.style.tip_labels_color:
            tstyle.pop("fill")

        # add tip names to coordinates calculated above
        self.axes.text(
            xpos, 
            ypos,
            self.tip_labels,  
            angle=(0 if self.style.orient in ("right", "left") else -90),
            style=tstyle,
            color=self.style.tip_labels_color,
        )
        # get stroke-width for aligned tip-label lines (optional)
        # copy stroke-width from the edge_style unless user set it
        if not self.style.edge_align_style.get("stroke-width"):
            self.style.edge_align_style['stroke-width'] = (
                self.style.edge_style['stroke-width'])


    def fit_tip_labels(self):
        """
        Modifies display range to ensure tip labels fit. This is a bit hackish
        still. The problem is that the 'extents' range of the rendered text
        is totally correct. So we add a little buffer here. Should add for 
        user to be able to modify this if needed. If not using edge lengths
        then need to use unit length for treeheight.
        """
        if self.style.use_edge_lengths:
            addon = (self.mtree.treelist[0].treenode.height + \
                (self.mtree.treelist[0].treenode.height * 0.25))
        else:
            addon = self.mtree.treelist[0].treenode.get_farthest_leaf(True)[1]

        # modify display for orientations
        if self.style.tip_labels:
            if self.style.orient == "right":
                self.axes.x.domain.max = addon
            elif self.style.orient == "down":
                self.axes.y.domain.min = -1 * addon


    def assign_tip_labels_and_colors(self):
        "assign tip labels based on user provided kwargs"
        # COLOR
        # tip color overrides tipstyle.fill
        if self.style.tip_labels_color:
            if self.style.tip_labels_style.fill:
                self.style.tip_labels_style.fill = None

        # LABELS
        # False == hide tip labels
        if self.style.tip_labels is False:
            self.style.tip_labels_style["-toyplot-anchor-shift"] = "0px"
            self.tip_labels = [
                "" for i in self.mtree.treelist[0].get_tip_labels()]

        # LABELS
        # user entered something...
        else:
            # if user did not change label-offset then shift it here
            if not self.style.tip_labels_style["-toyplot-anchor-shift"]:
                self.style.tip_labels_style["-toyplot-anchor-shift"] = "15px"

            # if user entered list in get_tip_labels order reverse it for plot
            if isinstance(self.style.tip_labels, list):
                self.tip_labels = self.style.tip_labels

            # True assigns tip labels from tree
            else:
                self.tip_labels = self.fixed_order
                #mtree.treelist[0].get_tip_labels()
