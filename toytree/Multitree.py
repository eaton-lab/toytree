#!/usr/bin/env python

"MultiTree objects"

from __future__ import print_function, absolute_import
from builtins import range, str

from copy import deepcopy
from hashlib import md5
from collections import defaultdict

import toyplot
import toyplot.config
import numpy as np

# used in Consensus
from .etemini import TreeNode
from .Toytree import ToyTree
from .TreeParser import TreeParser
from .TreeStyle import TreeStyle, STYLES
from .MultiDrawing import TreeGrid, CloudTree
from .utils import bpp2newick




###############################################
# MultiTree Class object
###############################################
class MultiTree(object):
    """
    Toytree MultiTree object for representing multiple trees. 

    Several functions are designed for trees with the same set of tips, and 
    may yield erratic behavior if trees have different sets of tips... TODO.
    
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
    draw_grid_tree:
        Draws a plot with n x m trees in a grid.
    """
    def __init__(self, newick, tree_format=0):  # , fixed_order=False):

        # setting attributes
        self.style = TreeStyle('m')
        self._i = 0

        # parse the newick object into a list of Toytrees
        self.treelist = []
        if isinstance(newick, str):
            self.treelist = [
                ToyTree(i) for i in 
                TreeParser(newick, tree_format, multitree=True).treenodes
            ]
        elif isinstance(newick, (list, tuple)):
            if isinstance(newick[0], str):
                self.treelist = [
                    ToyTree(i) for i in 
                    TreeParser(newick, tree_format, multitree=True).treenodes
                ]
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
        #if names are the same in all the trees...
        alltips_shared = all([
            set(self.treelist[0].get_tip_labels()) == set(i.get_tip_labels()) 
            for i in self.treelist
        ])
        if alltips_shared:
            return True
        return False


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
        nrows=None, 
        ncols=None, 
        start=0, 
        fixed_order=False, 
        shared_axis=False, 
        **kwargs):
        """        
        Draw a slice of x*y trees into a x,y grid non-overlapping. 

        Parameters:
        -----------
        x (int):
            Number of grid cells in x dimension. Default=automatically set.
        y (int):
            Number of grid cells in y dimension. Default=automatically set.
        start (int):
            Starting index of tree slice from .treelist.
        kwargs (dict):
            Toytree .draw() arguments as a dictionary. 
        """
        # return nothing if tree is empty
        if not self.treelist:
            print("Treelist is empty")
            return None, None

        # make a copy of the treelist so we don't modify the original
        if not fixed_order:
            treelist = self.copy().treelist
        else:
            if fixed_order is True:
                fixed_order = self.treelist[0].get_tip_labels()
            treelist = [
                ToyTree(i, fixed_order=fixed_order) 
                for i in self.copy().treelist
            ]

        # apply kwargs styles to the individual tree styles
        for tree in treelist:
            tree.style.update(kwargs)

        # get reasonable values for x,y given treelist length
        if not (ncols or nrows):
            ncols = 5
            nrows = 1
        elif not (ncols and nrows):
            if ncols:
                if ncols == 1:
                    if self.ntrees <= 5:
                        nrows = self.ntrees
                    else:
                        nrows = 2
                else:
                    if self.ntrees <= 10:
                        nrows = 2
                    else:
                        nrows = 3

            if nrows:
                if nrows == 1:
                    if self.ntrees <= 5:
                        ncols = self.ntrees 
                    else:
                        ncols = 5
                else:
                    if self.ntrees <= 10:
                        ncols = 5
                    else:
                        ncols = 3
        else:
            pass

        # Return TereGrid object for debugging
        draw = TreeGrid(treelist)
        if kwargs.get("debug"):
            return draw

        # Call update to draw plot. Kwargs still here for width, height, axes
        canvas, axes = draw.update(nrows, ncols, start, shared_axis, **kwargs)
        return canvas, axes


    def draw_cloud_tree(self, 
        axes=None, 
        html=False,
        fixed_order=True,
        **kwargs):
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

        # return nothing if tree is empty
        if not self.all_tips_shared:
            print("All trees in treelist do not share the same tips")
            return None, None            

        # make a copy of the treelist so we don't modify the original
        if not fixed_order:
            raise Exception(
                "fixed_order must be either True or a list with the tip order")

        # set fixed order on a copy of the tree list
        if isinstance(fixed_order, (list, tuple)):
            pass
        elif fixed_order is True:
            fixed_order = self.treelist[0].get_tip_labels()
        else:
            raise Exception(
                "fixed_order argument must be True or a list with the tip order")
        treelist = [
            ToyTree(i, fixed_order=fixed_order) for i in self.copy().treelist
        ]  

        # give advice if user tries to enter tip_labels
        if kwargs.get("tip_labels"):
            print(TIP_LABELS_ADVICE)

        # set autorender format to png so we don't bog down notebooks
        try:
            changed_autoformat = False
            if not html:
                toyplot.config.autoformat = "png"
                changed_autoformat = True

            # dict of global cloud tree style 
            mstyle = STYLES['m']

            # if trees in treelist already have some then we don't quash...
            mstyle.update(
                {i: j for (i, j) in kwargs.items() if 
                (j is not None) & (i != "tip_labels")}
            )
            for tree in treelist:
                tree.style.update(mstyle)

            # Send a copy of MultiTree to init Drawing object.
            draw = CloudTree(treelist, **kwargs)

            # and create drawing
            if kwargs.get("debug"):
                return draw

            # allow user axes, and kwargs for width, height
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
        self.treedict = {}
        self.clade_counts = None
        self.fclade_counts = None
        self.ttree = None
        self.nodelist = None

        assert cutoff < 1, "cutoff should be a float proportion (e.g., 0.5)"

    def update(self):

        # hash a dict to remove duplicate trees
        self.hash_trees()

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


# GLOBALS
TIP_LABELS_ADVICE = """
Warning: tip_labels arg cannot be used in draw_cloud_tree(). Instead, 
you must set the tip labels style on the first tree in your treelist. 
If you wish to change the order of tips then use the fixed_order arg. 
Example: 

# a set of 10 trees with 5 numbers for tip names
trees = toytree.mtree([toytree.rtree.imbtree(5) for i in range(10)])

# set style of tip labels in the FIRST tree in treelist
trees.treelist[0].style.tip_labels = [
    "tip-number-{}".format(i) for i in trees.treelist[0].get_tip_labels()
]

# draw a cloud tree using a set tip order for all trees
trees.draw_cloud_tree(fixed_order=['0', '1', '2', '3', '4'])

"""