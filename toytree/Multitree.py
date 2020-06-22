#!/usr/bin/env python

"MultiTree objects"

from __future__ import print_function, absolute_import
from builtins import range, str

from copy import deepcopy
from hashlib import md5
from collections import defaultdict
import numpy as np

# used in Consensus
from .TreeNode import TreeNode
from .Toytree import ToyTree
from .TreeParser import TreeParser
from .TreeStyle import TreeStyle

from .StyleChecker import StyleChecker
from .CanvasSetup import GridSetup, CanvasSetup
from .Render import ToytreeMark
from .utils import ToytreeError, bpp2newick
# from .MultiDrawing import CloudTree

"""
TODO: 
    - re-do support for BPP weird format trees.
    - set-like function that drops tips from each tree not shared by all trees.
    - root function that drops tree that cannot be rooted or not set-like
    - consensus function drop tips that are not in set.
    - treegrid simplify args (3, 3) e.g., will make a 600x600 canvas...
    - Annotate class for surrounding markers...
    - A distinct multitree mark for combining styles on topologies 
    - New mark: leave proper space for tips to mtree fits same as tree.
"""



class MultiTree(object):
    """
    Toytree MultiTree object for representing multiple trees. 

    Parameters:
    -----------
    newick: (str)
        string, filepath, or URL for a newick or nexus formatted list of trees
    tree_format: (int)
        ete format for newick tree structure. Default is 0. 
    fixed_order: (bool, list, None)    
        ...

    Attributes:
    -----------
    treelist: list
        A list of toytree objects from the parsed newick file. 

    Functions():
    ------------
    get_consensus_tree: 
        Returns a ToyTree object with support values on nodes.
    draw_cloud_tree:
        Draws a plot with overlapping fixed_order trees.
    draw
        Draws a plot with n x m trees in a grid.
    """
    def __init__(self, newick, tree_format=0):  # , fixed_order=False):

        # setting attributes
        self.style = TreeStyle('m')
        self._i = 0

        # parse the newick object into a list of Toytrees
        self.treelist = []
        if isinstance(newick, str):
            tns = TreeParser(newick, tree_format, multitree=True).treenodes
            self.treelist = [ToyTree(i) for i in tns]

        # iterables (list, tuple, ndarray, Series)
        else:
            # convert to list
            if newick is not None:
                newick = list(newick)

            # load list whether it is newicks, toytrees or treenodes
            if isinstance(newick[0], str):
                tns = TreeParser(newick, tree_format, multitree=True).treenodes
                self.treelist = [ToyTree(i) for i in tns]
            elif isinstance(newick[0], ToyTree):
                self.treelist = newick
            elif isinstance(newick[0], TreeNode):
                self.treelist = [ToyTree(i) for i in newick]

        # set tip plot order for treelist to the first tree order
        # order trees in treelist to plot in shared order...
        # self._fixed_order = fixed_order   # (<list>, True, False, or None)
        # self._user_order = None
        # self._cons_order = None
        # self._set_tip_order()
        # self._parse_treelist()

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


    @property
    def ntrees(self):
        return len(self.treelist)


    @property
    def all_tips_shared(self):
        """
        Check if names are the same in all the trees in .treelist.
        """
        alltips_shared = all([
            set(self.treelist[0].get_tip_labels()) == set(i.get_tip_labels()) 
            for i in self.treelist
        ])
        if alltips_shared:
            return True
        return False


    # TODO: this could be sped up by using toytree copy command.
    # ALSO check that copy() or deepcopy here preserves fixed_order.
    def copy(self):
        return deepcopy(self)


    def write(self, handle=None, format=0):
        if not handle:
            handle = "out.tre"
        with open(handle, 'w') as outtre:
            for tre in self.treelist:
                outtre.write(tre.newick + "\n")


    def reset_tree_styles(self):
        """
        Sets the .style toytree drawing styles to default for all ToyTrees
        in a MultiTree .treelist. 
        """
        for tre in self.treelist:
            tre.style = TreeStyle('n')


    # -------------------------------------------------------------------
    # Tree List Statistics or Calculations
    # -------------------------------------------------------------------
    # def get_tip_labels(self):
    #     """
    #     Returns the tip names in tree plot order for the *list of tree*, 
    #     starting from the zero axis. If all trees in the treelist do not 
    #     share the same set of tips then this will return an error message. 

    #     If fixed_order is a user entered list then names are returned in that
    #     order. If fixed_order was True then the consensus tree order is 
    #     returned. If fixed_order was None or False then the order of the first
    #     ToyTree in .treelist is returned. 
    #     """
    #     if not self.all_tips_shared:
    #         raise Exception(
    #             "All trees in treelist do not share the same set of tips")
    #     return self.treelist[0].get_tip_labels()


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
        best_tree (Toytree or newick string; optional):
            A tree that support values should be calculated for and added to. 
            For example, you want to calculate how often clades in your best 
            ML tree are supported in 100 bootstrap trees. 
        """
        if best_tree is not None:
            if not isinstance(best_tree, ToyTree):
                best_tree = ToyTree(best_tree)
        cons = ConsensusTree(self.treelist, best_tree=best_tree, cutoff=cutoff)
        cons.update()
        return cons.ttree




    def draw(
        self, 
        nrows=1, 
        ncols=4, 
        shared_axes=False,
        idxs=None, 
        width=None,
        height=None,
        **kwargs):
        """
        Draw a set of trees on a grid with nice spacing and optionally with
        a shared axes. Different styles can be set on each tree individually
        or set here during drawing to be shared across trees.

        Parameters:
        -----------
        nrows (int):
            Number of grid cells in x dimension (default=1)
        ncols (int):
            Number of grid cells in y dimension (default=4)
        shared_axes (bool):
            If True then the 'height' dimension will be shared among 
            all trees so heights are comparable, otherwise each tree is 
            scaled to fill the space in its grid cell.
        idxs (int):
            The indices of trees in treelist that you want to draw. By 
            default the first ncols*nrows trees are drawn, but you can 
            select the 10-14th tree by entering idxs=[10,11,12,13]
        width (int):
            Width of the canvas
        height (int):
            Height of the canvas
        kwargs (dict):
            Any style arguments supported by .draw() in toytrees.
        """
        # get index of trees that will be drawn
        if idxs is None:
            tidx = range(0, min(nrows * ncols, len(self.treelist)))
        else:
            tidx = idxs

        # get the trees
        treelist = [self.treelist[i] for i in tidx]
        if kwargs.get("fixed_order") is True:
            fixed_order = (
                MultiTree(treelist)
                .get_consensus_tree()
                .get_tip_labels()
            )
            kwargs["fixed_order"] = fixed_order

        # if less than 4 trees reshape ncols,rows,
        if len(treelist) < 4:
            if nrows > ncols:
                nrows = len(treelist)
                ncols = 1
            else:
                nrows = 1
                ncols = len(treelist)

        # get the canvas and axes that can fit the requested trees.
        layout = (kwargs.get("layout") if kwargs.get("layout") else "r")
        grid = GridSetup(nrows, ncols, width, height, layout)
        canvas = grid.canvas
        axes = grid.axes

        # max height of trees in treelist for shared axes
        maxh = max([t.treenode.height for t in treelist])

        # default style 
        if "tip_labels_style" in kwargs:
            if "-toyplot-anchor-shift" not in kwargs["tip_labels_style"]:
                kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "10px"
            if "font-size" not in kwargs["tip_labels_style"]:
                kwargs["font-size"] = "9px"
        else:
            kwargs["tip_labels_style"] = {
                "-toyplot-anchor-shift": "10px",
                "font-size": "9px",
            }           

        # add toytree-Grid mark to the axes
        marks = []
        for idx in range(grid.nrows * grid.ncols):

            # get the axis
            ax = grid.axes[idx]

            # add the mark
            _, _, mark = treelist[idx].draw(axes=ax, padding=10, **kwargs.copy())

            # store the mark
            marks.append(mark)

            # make tip labels align on shared axes if tip labels
            shrink = (kwargs.get("shrink") if kwargs.get("shrink") else 0)

            if shared_axes:
                if not all([i is None for i in mark.tip_labels]):
                    if mark.layout == "r":
                        ax.x.domain.max = maxh * 0.5 + shrink
                    elif mark.layout == "l":
                        ax.x.domain.min = -maxh * 0.5 - shrink
                    elif mark.layout == "d":
                        ax.y.domain.min = -maxh * 0.5 - shrink
                    elif mark.layout == "u":
                        ax.y.domain.max = maxh * 0.5 + shrink

            # set shared axes
            if shared_axes:
                if mark.layout == "r":
                    ax.x.domain.min = -maxh
                elif mark.layout == "l":
                    ax.x.domain.max = maxh
                elif mark.layout == "d":
                    ax.y.domain.max = maxh
                elif mark.layout == "u":
                    ax.y.domain.min = -maxh

            # axes off if not scalebar
            if not kwargs.get("scalebar") is True:
                ax.show = False

        # add mark to axes
        return canvas, axes, marks



    # def draw_tree_grid(
    #     self, 
    #     axes=None,
    #     nrows=None, 
    #     ncols=None, 
    #     start=0, 
    #     fixed_order=False, 
    #     shared_axis=False, 
    #     **kwargs):
    #     """        
    #     Deprecated. Tree grid drawing are now produced with .draw().
    #     """
    #     raise DeprecationWarning(
    #         ".draw_tree_grid() has been replaced by the .draw() function."
    #     )


    def draw_cloud_tree(self, axes=None, fixed_order=None, **kwargs):
        """
        Draw a series of trees overlapping each other in coordinate space.
        The order of tip_labels is fixed in cloud trees so that trees with 
        discordant relationships can be seen in conflict. To change the tip
        order enter a list of names to 'fixed_order'.

        Parameters:
        -----------
        axes: (None or toyplot.coordinates.Cartesian)
            If None then a new Canvas and Cartesian axes object is returned,
            otherwise if a Cartesian axes object is provided the cloudtree
            will be drawn on the axes.      

        **kwargs: 
            All drawing style arguments supported in the .draw() function 
            of toytree objects are also supported by .draw_cloudtree().
        """
        # canvas styler
        fstyle = TreeStyle('n')
        fstyle.width = (kwargs.get("width") if kwargs.get("width") else None)
        fstyle.height = (kwargs.get("height") if kwargs.get("height") else None)
        fstyle.tip_labels = self.treelist[0].get_tip_labels()
        fstyle.layout = (kwargs.get("layout") if kwargs.get("layout") else 'r')
        fstyle.padding = (kwargs.get("padding") if kwargs.get("padding") else 20)
        fstyle.scalebar = (kwargs.get("scalebar") if kwargs.get("scalebar") else False)
        fstyle.use_edge_lengths = (kwargs.get("use_edge_lengths") if kwargs.get("use_edge_lengths") else True)
        fstyle.xbaseline = (kwargs.get("xbaseline") if kwargs.get("xbaseline") else 0)
        fstyle.ybaseline = (kwargs.get("ybaseline") if kwargs.get("ybaseline") else 0)

        # get canvas and axes
        cs = CanvasSetup(self, axes, fstyle)
        canvas = cs.canvas
        axes = cs.axes

        # fix order treelist
        if not isinstance(fixed_order, list):
            fixed_order = (
                MultiTree(self.treelist)
                .get_consensus_tree()
                .get_tip_labels()
            )

        # add trees
        for tidx, tree in enumerate(self.treelist):

            # the default MultiTree object style.
            curstyle = self.style.copy()

            # allow THIS tree to override some edge style args
            curstyle.edge_style.update(tree.style.edge_style)
            curstyle.edge_colors = tree.style.edge_colors
            curstyle.edge_widths = tree.style.edge_widths

            # if user did not set opacity (assumed from 1.0) then auto-tune it
            if curstyle.edge_style["stroke-opacity"] == 1:
                curstyle.edge_style["stroke-opacity"] = 1 / len(self.treelist)

            # override some styles with user kwargs
            user = dict([
                ("_" + i, j) if isinstance(j, dict) else (i, j)
                for (i, j) in kwargs.items() 
                if (j is not None)  # and (i != "tip_labels")
            ])
            curstyle.update(user)

            # update coords based on layout
            edges = tree._coords.get_edges()
            if curstyle.layout == 'c':
                verts = tree._coords.get_radial_coords(curstyle.use_edge_lengths)
            else:
                verts = tree._coords.get_linear_coords(
                    curstyle.layout, 
                    curstyle.use_edge_lengths,
                    fixed_order,
                    None,  # TODO: add optional jitter to fixed_pos here.
                    )

            # only draw the tips for the first tree
            if tidx != 0:
                curstyle.tip_labels = False

            # check all styles
            fstyle = StyleChecker(tree, curstyle).style

            # generate toyplot Mark
            mark = ToytreeMark(ntable=verts, etable=edges, **fstyle.to_dict())

            # add mark to axes
            axes.add_mark(mark)

        # get shared tree styles.
        return canvas, axes, None



    # def draw_cloud_tree(
    #     self, 
    #     axes=None, 
    #     html=False,
    #     fixed_order=True,
    #     **kwargs):
    #     """
    #     Deprecated
    #     Draw a series of trees overlapping each other in coordinate space.
    #     The order of tip_labels is fixed in cloud trees so that trees with 
    #     discordant relationships can be seen in conflict. To change the tip
    #     order use the 'fixed_order' argument in toytree.mtree() when creating
    #     the MultiTree object.

    #     Parameters:
    #         axes (toyplot.Cartesian): toyplot Cartesian axes object.
    #         html (bool): whether to return the drawing as html (default=PNG).
    #         **kwargs (dict): styling options should be input as a dictionary.
    #     """
    #     # return nothing if tree is empty
    #     if not self.treelist:
    #         print("Treelist is empty")
    #         return None, None

    #     # return nothing if tree is empty
    #     if not self.all_tips_shared:
    #         print("All trees in treelist do not share the same tips")
    #         return None, None            

    #     # make a copy of the treelist so we don't modify the original
    #     if not fixed_order:
    #         raise Exception(
    #             "fixed_order must be either True or a list with the tip order")

    #     # set fixed order on a copy of the tree list
    #     if isinstance(fixed_order, (list, tuple)):
    #         fixed_order = fixed_order
    #     elif fixed_order is True:
    #         fixed_order = self.treelist[0].get_tip_labels()
    #     else:
    #         raise Exception(
    #             "fixed_order argument must be True or a list with the tip order")
    #     treelist = [
    #         ToyTree(i, fixed_order=fixed_order) for i in self.copy().treelist
    #     ]  

    #     # give advice if user tries to enter tip_labels
    #     if kwargs.get("tip_labels"):
    #         if not isinstance(kwargs.get("tip_labels"), dict):
    #             print(TIP_LABELS_ADVICE)
    #             kwargs.pop("tip_labels")

    #     # set autorender format to png so we don't bog down notebooks
    #     try:
    #         changed_autoformat = False
    #         if not html:
    #             toyplot.config.autoformat = "png"
    #             changed_autoformat = True

    #         # dict of global cloud tree style 
    #         mstyle = deepcopy(STYLES['m'])

    #         # if trees in treelist already have some then we don't quash...
    #         mstyle.update(
    #             {i: j for (i, j) in kwargs.items() if 
    #             (j is not None) & (i != "tip_labels")}
    #         )
    #         for tree in treelist:
    #             tree.style.update(mstyle)

    #         # Send a copy of MultiTree to init Drawing object.
    #         draw = CloudTree(treelist, **kwargs)

    #         # and create drawing
    #         if kwargs.get("debug"):
    #             return draw

    #         # allow user axes, and kwargs for width, height
    #         canvas, axes, mark = draw.update(axes)
    #         return canvas, axes, mark

    #     finally:
    #         if changed_autoformat:
    #             toyplot.config.autoformat = "html"


    # # # allow ts as a shorthand for tree_style
    # # if kwargs.get("ts"):
    # #     tree_style = kwargs.get("ts")

    # # # pass a copy of this tree so that any mods to .style are not saved
    # # nself = deepcopy(self)
    # # if tree_style:
    # #     nself.style.update(TreeStyle(tree_style[0]))



class ConsensusTree:
    """
    An extended majority rule consensus function.
    Modelled on the similar function from scikit-bio tree module. If
    cutoff=0.5 then it is a normal majority rule consensus, while if
    cutoff=0.0 then subsequent non-conflicting clades are added to the tree.
    """
    def __init__(self, treelist, best_tree=None, cutoff=0.0):

        # parse args
        self.treelist = treelist
        self.best_tree = best_tree
        if self.best_tree is not None:
            self.best_tree = best_tree.copy().unroot()
            self.names = self.best_tree.get_tip_labels()
        else:
            self.names = self.treelist[0].get_tip_labels()
        self.cutoff = float(cutoff)

        # attrs to fill
        self.namedict = None
        self.treedict = {}
        self.clade_counts = None
        self.fclade_counts = None

        # results 
        self.ttree = None
        self.nodelist = None

        assert cutoff < 1, "cutoff should be a float proportion (e.g., 0.5)"

    def update(self):

        # hash a dict to remove duplicate trees
        self.hash_trees()

        # map onto best_tree of infer majrule consensus
        if self.best_tree is not None:
            self.map_onto_best_tree()

        else:
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


    def hash_trees(self):
        "hash ladderized tree topologies"       
        observed = {}
        for idx, tree in enumerate(self.treelist):
            nwk = tree.write(tree_format=9)
            hashed = md5(nwk.encode("utf-8")).hexdigest()
            if hashed not in observed:
                observed[hashed] = idx
                self.treedict[idx] = 1
            else:
                idx = observed[hashed]
                self.treedict[idx] += 1


    def map_onto_best_tree(self):
        "map clades from tree onto best_tree"

        # index names from the first tree
        ndict = {j: i for i, j in enumerate(self.names)}

        # dictionary of bits describing all clades in the best tree
        idict = {}
        bitdict = {}
        for node in self.best_tree.treenode.traverse("preorder"):

            # get byte string representing split
            bits = np.zeros(self.best_tree.ntips, dtype=np.bool_)
            for child in node.iter_leaf_names():
                bits[ndict[child]] = True
            bitstring = bits.tobytes()

            # record split (mirror image not relevant)
            bitdict[bitstring] = 0
            idict[bitstring] = node
        # print(bitdict)

        # count occurrence of clades in best_tree among other trees
        for tidx, ncopies in self.treedict.items():
            tre = self.treelist[tidx].unroot()
            # print(tidx)
            for node in tre.treenode.traverse("preorder"):
                bits = np.zeros(tre.ntips, dtype=np.bool_)
                for child in node.iter_leaf_names():
                    bits[ndict[child]] = True
                bitstring = bits.tobytes()
                # print(bits.astype(int))
                if bitstring in bitdict:
                    bitdict[bitstring] += ncopies
                else:
                    revstring = np.invert(bits).tobytes()
                    if revstring in bitdict:
                        bitdict[revstring] += ncopies
            # print("")

        # convert to frequencies
        for key, val in bitdict.items():
            # print(key, val, idict[key].name)
            idict[key].support = int(100 * val / float(len(self.treelist)))
        self.ttree = self.best_tree
        self.ttree._coords.update()


    def find_clades(self):
        "Count clade occurrences."
        # index names from the first tree
        ndict = {j: i for i, j in enumerate(self.names)}
        namedict = {i: j for i, j in enumerate(self.names)}

        # store counts
        clade_counts = {}
        for tidx, ncopies in self.treedict.items():

            # testing on unrooted trees is easiest but for some reason slow
            ttree = self.treelist[tidx].unroot()

            # traverse over tree
            for node in ttree.treenode.traverse('preorder'):
                bits = np.zeros(len(ttree), dtype=np.bool_)
                for child in node.iter_leaf_names():
                    bits[ndict[child]] = True

                # get bit string and its reverse
                bitstring = bits.tobytes()
                revstring = np.invert(bits).tobytes()

                # add to clades first time, then check for inverse next hits
                if bitstring in clade_counts:
                    clade_counts[bitstring] += ncopies
                else:
                    if revstring not in clade_counts:
                        clade_counts[bitstring] = ncopies
                    else:
                        clade_counts[revstring] += ncopies

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
        "Remove conflicting clades and those < cutoff to get majority rule"
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

        # create dict of clade counts and set keys
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

        ## return the tree and other trees if present
        self.ttree = ToyTree(tre.write(format=0))
        self.ttree._coords.update()
        self.nodelist = nodelist



TIP_LABELS_ADVICE = """
Warning: ignoring 'tip_labels' argument. 

The 'tip_labels' arg to draw_cloud_tree() should be a dictionary
mapping tip names from the contained ToyTrees to a new string value.
Example: {"a": "tip-A", "b": "tip-B", "c": tip-C"}

# get a MultiTree containing 10 trees with numbered tip names
trees = toytree.mtree([toytree.rtree.imbtree(5) for i in range(10)])

# draw a cloud tree using a set tip order and styled tip names
trees.draw_cloud_tree(
    fixed_order=['0', '1', '2', '3', '4'],
    tip_labels={i: "tip-{}".format(i) for i in trees.treelist[0].get_tip_labels()},
    )
"""
