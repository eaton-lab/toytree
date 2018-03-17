#!/usr/bin/env python

from __future__ import print_function, division, absolute_import

from decimal import Decimal
from .ete3mini import TreeNode
from .style import TreeStyle
import numpy as np
import requests
import toyplot
import random  # b/c ete uses random seed.
import copy
import re

# from builtins import object


# the main tree class
class Toytree(object):
    """
    The toytree Tree Class object, a plotting wrapper around an
    ete3 Tree Class object which can be accessed from the .tree
    attribute.

    Parameters:
    -----------
    newick (str):
        The input tree as a newick string, or filepath, or a functional
        weblink to a newick string. This is stored and updated if the tree
        structure is modified. 
    ladderize (bool):
        Whether to automatically ladderize the tree. Default=True.
    tree_format (int):
        The tree format used for parsing the tree. See ETE tree formats.
        The default 0 can handle most tree formats including NHX.
    fixed_order (bool):
        Enforce a fixed order of tip-labels. This can make the topology
        look very strange, but is useful for showing differences between
        topologies. Default=False.

    Attributes:
    -----------
    tree: ete3mini.TreeNode
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

    Functions: (see function docstrings)
    ----------
    get_tip_labels  
    get_edge_lengths  
    get_node_values  
    get_node_dict  
    is_rooted  
    is_bifurcating 
    copy
    prune 
    drop_tips
    resolve_polytomy 
    root 
    unroot 
    draw 
    """

    def __init__(
        self,
        newick=None,
        ladderize=True,
        tree_format=0,
        fixed_order=None,
        **style):

        # ensures ladderized top-down order for entered tip order
        self.jitter = Jitter(self)
        self._fixed_order = fixed_order
        self._parse_newick(newick, tree_format, ladderize)

        # default attributes and plot settings
        self._style = TreeStyle(tree_style='p')

        # plotting coordinates
        self.edges = np.zeros((self.nnodes - 1, 2), dtype=int)
        self.verts = np.zeros((self.nnodes, 2), dtype=float)
        self._lines = []
        self._coords = []

        # assign idx, orient, verts, and update newick with features
        self._decompose_tree()


    # should this be a .get named func instead?
    @property
    def features(self):
        """ return features saved on nodes of the tree"""
        return self.tree.features

    @property
    def nnodes(self):
        return sum(1 for i in self.tree.traverse())


    @property
    def newick(self, fmt=0):
        """
        Returns newick represenation of the tree in its current state.
        """
        # checks one of root's children for features and extra feats.
        if self.tree.children:
            features = {"name", "dist", "support", "height", "idx"}
            testnode = self.tree.children[0]
            extrafeat = {i for i in testnode.features if i not in features}
            features.update(extrafeat)
            return self.tree.write(format=0)


    # functions to return values from the ete3 .tree object
    def get_edge_lengths(self):
        """
        Returns edge length values from tree object in node plot order. To
        modify edge length values you must modify nodes in the .tree object
        directly. For example:

        for node in tree.tree.traverse():
            node.dist = 1.
        """
        # access nodes in the order they will be plotted
        return self.get_node_values('dist', True, True)


    def get_node_values(self, feature=None, show_root=False, show_tips=False):
        """
        Returns node values from tree object in node plot order. To modify
        values you must modify the .tree object directly by setting new
        'features'. For example

        for node in tree.tree.traverse():
            node.add_feature("PP", 100)

        By default node and tip values are hidden (set to "") so that they
        are not shown on the tree plot. To include values for these nodes
        use the 'show_root'=True, or 'show_tips'=True arguments.
        """
        # access nodes in the order they will be plotted
        # this is a customized order best sampled this way
        nodes = [self.tree.search_nodes(name=str(i))[0]
                 for i in self.get_node_dict().values()]

        # get features
        if feature:
            vals = [i.__getattribute__(feature)
                    if hasattr(i, feature) else "" for i in nodes]
        else:
            vals = [" " for i in nodes]

        # apply hiding rules
        if not show_root:
            vals = [i if not j.is_root() else "" for i, j in zip(vals, nodes)]
        if not show_tips:
            vals = [i if not j.is_leaf() else "" for i, j in zip(vals, nodes)]

        # convert float to ints for prettier printing unless all floats
        # raise exception and skip if there are true strings (names)
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
        idx = -1 + sum(1 for i in self.tree.traverse())

        # preorder: first parent and then children
        for node in self.tree.traverse("preorder"):
            if not node.is_leaf():
                if node.name:
                    names[idx] = node.name
                idx -= 1

        # names are in ladderized plotting order
        tiporder = self.tree.get_leaves()
        for node in tiporder:
            names[idx] = node.name
            idx -= 1
        return names


    def get_tip_labels(self):
        """
        returns tip labels in ladderized order from top to bottom on
        right-facing tree. Take care because this is the reverse of the
        y-axis order, i.e., the tree plot bottom is at X=0.
        """
        if self._fixed_order:
            return self._fixed_order[::-1]
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


    def is_rooted(self):
        """
        Returns False if the tree is unrooted.
        """
        if len(self.tree.children) > 2:
            return False
        return True


    def is_bifurcating(self, include_root=True):
        """
        Returns False if there is a polytomy in the tree, including if the tree
        is unrooted (basal polytomy), unless you use the include_root=False
        argument.
        """
        ctn1 = -1 + (2 * len(self))
        ctn2 = -2 + (2 * len(self))
        if self.is_rooted():
            return bool(ctn1 == sum(1 for i in self.tree.traverse()))
        if include_root:
            return bool(ctn2 == -1 + sum(1 for i in self.tree.traverse()))
        return bool(ctn2 == sum(1 for i in self.tree.traverse()))


    # unlike ete this returns a copy with dropped tips, not in-place!
    def prune(self, node_idx):
        """
        Returns a subtree pruned from the full tree at the selected
        node index. To find the appropriate index try using
        tre.draw(node_labels=True) and use the interactive hover
        feature, or tre.draw(node_labels='idx') to find the 'idx'
        value of the node on which you wish to prune the tree. If you
        simply want to drop tips from the tree rather than prune on an
        internal node, see the .drop_tip() function instead.

        ptre = tre.prune(15)
        """
        # make a deepcopy of the tree
        nself = self.copy()

        # ensure node_idx is int
        node = nself.tree.search_nodes(idx=int(node_idx))[0]
        nself.tree.prune(node)
        return nself


    # unlike ete this returns a copy with dropped tips, not in-place!
    def drop_tips(self, tips):
        """
        Returns a copy of the tree with the selected tips pruned from
        the tree. The entered value can be a name or list of names. To
        prune on an internal node to create a subtree of the existing
        tree see the .prune() function instead.

        ptre = tre.drop_tips(['a', 'b'])
        """
        # make a deepcopy of the tree
        nself = self.copy()

        # if tips is a string or Treenode
        if isinstance(tips, str):
            tips = [tips]
        elif isinstance(tips, TreeNode):
            tips = [tips.name]

        keeptips = [i for i in nself.get_tip_labels() if i not in tips]
        nself.tree.prune(keeptips)
        return nself


    # unlike ete this returns a copy resolved, not in-place!
    def resolve_polytomy(
        self,
        default_dist=0.0,
        default_support=0.0,
        recursive=False):
        """
        Returns a copy of the tree with resolved polytomies.
        Does not transform tree in-place.
        """
        newtree = self.copy()
        newtree.tree.resolve_polytomy(
            default_dist=default_dist,
            default_support=default_support,
            recursive=recursive)
        return newtree


    # returns a copy unrooted, not in place
    def unroot(self):
        """
        Returns a copy of the tree unrooted. Does not transform tree in-place.
        """
        newtree = self.copy()
        newtree.tree.unroot()
        newtree.tree.ladderize()
        return newtree


    # returns a copy rooted, not in place
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

        # make a deepcopy of the tree
        nself = self.copy()

        # set names or wildcard as the outgroup
        og = outgroup
        if og:
            if isinstance(og, str):
                outgroup = [og]
            notfound = [i for i in og if i not in nself.tree.get_leaf_names()]
            if any(notfound):
                raise Exception(
                    "Sample {} is not in the tree".format(notfound))
            outs = [i for i in nself.tree.get_leaf_names() if i in outgroup]

        elif regex:
            outs = [i.name for i in nself.tree.get_leaves()
                    if re.match(regex, i.name)]
            if not any(outs):
                raise Exception("No Samples matched the regular expression")

        elif wildcard:
            outs = [i.name for i in nself.tree.get_leaves()
                    if wildcard in i.name]
            if not any(outs):
                raise Exception("No Samples matched the wildcard")

        else:
            raise Exception(
                "must enter an outgroup, wildcard selector, or regex pattern")

        if len(outs) > 1:
            # check if they're monophyletic
            mbool, mtype, mnames = nself.tree.check_monophyly(
                outs, "name", ignore_missing=True)
            if not mbool:
                if mtype == "paraphyletic":
                    outs = [i.name for i in mnames]
                else:
                    raise Exception(
                        "Tips entered to root() cannot be paraphyletic")
            out = nself.tree.get_common_ancestor(outs)
        else:
            out = outs[0]

        # split root node if more than di- as this is the unrooted state
        if not nself.is_bifurcating():
            nself.tree.resolve_polytomy()

        # root the object with ete's translate
        nself.tree.set_outgroup(out)

        # get features
        testnode = nself.tree.get_leaves()[0]
        features = {"name", "dist", "support", "height"}
        extrafeat = {i for i in testnode.features if i not in features}
        features.update(extrafeat)

        # if there is a new node now, clean up its features
        nnode = [i for i in nself.tree.traverse() if not hasattr(i, "idx")]
        if nnode:
            # nnode is the node that was added
            # rnode is the location where it *should* have been added
            nnode = nnode[0]
            rnode = [i for i in nself.tree.children if i != out][0]

            # get idxs of existing nodes
            idxs = [int(i.idx) for i in nself.tree.traverse()
                    if hasattr(i, "idx")]

            # newnode is a tip
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

            # newnode is internal
            else:
                nnode.add_feature("idx", max(idxs) + 1)
                nnode.name = str("rerooted")
                nnode.dist *= 2
                sister = nnode.get_sisters()[0]
                sister.dist *= 2
                nnode.support = 100

        # store tree back into newick and reinit Toytree with new newick
        # if NHX format then preserve the NHX features.
        nself.tree.ladderize()
        return nself


    # returns a (canvas, axes) tuple
    def draw(
        self,
        height=None,
        width=None,
        axes=None,        
        tip_labels=None,
        tip_labels_color=None,
        tip_labels_style=None,
        tip_labels_align=None,
        node_labels=None,
        node_labels_style=None,
        node_size=None,
        node_color=None,
        node_style=None,
        node_hover=None,
        edge_type=None,
        edge_style=None,
        edge_align_style=None,
        use_edge_lengths=None,
        orient=None,  
        tree_style=None,
        scalebar=None,
        padding=None,
        # edge_width=None,
        # tip_labels_angle=None,        
        ):
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
            If True then nodes are shown, if False then nodes are
            suppressed. If a list of node labels is provided it must be the
            same length and order as nodes in .get_node_dict(). Node labels
            can be generated in the proper order using the the
            .get_node_labels() function from a Toytree tree to draw info
            from the tree features.
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
        # store entered args
        canvas_args = {
            "height": height,
            "width": width,
        }
        axes_args = {
            "padding": padding,
            "scalebar": scalebar,
        }
        mark_args = {
            "orient": orient,
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
            "edge_type": edge_type,  
            "edge_style": edge_style,
            "edge_align_style": edge_align_style,
            "use_edge_lengths": use_edge_lengths,
            "tree_style": tree_style,
            # "edge_width": edge_width,  ## todo
            # "edge_color": edge_color,  ## todo
            # "tip_labels_angle": tip_labels_angle,
        }

        # update mark option in TreeStyle
        ts = (tree_style if tree_style else 'normal')
        self._style = TreeStyle(tree_style=ts)
        self._style.update_mark(mark_args)
        self._style.update_axes(axes_args)
        self._style.update_canvas(canvas_args)

        # reset plotting coordinates for new orient and edges args
        self._decompose_tree()

        # if dims not entered in style then set a reasonable height & width
        self._set_dims_from_tree_size()

        # if axes arg then assume existing canvas, else create one
        if axes:
            canvas = None
        else:
            canvas = toyplot.Canvas(
                height=self._style['height'],
                width=self._style['width'],
            )
            axes = canvas.cartesian(padding=self._style["axes"]["padding"])
            axes.show = False

        # return nothing if tree is empty
        if not self.tree.children:
            print("Tree is empty")
            canvas, axes

        # build tree style 
        self._assign_node_labels()
        self._assign_tip_labels()

        # order of tree/nodes last (on top) is preferred
        self._add_tip_labels_to_axes(axes)
        self._add_tree_to_axes(axes)
        self._add_nodes_to_axes(axes)

        # update axes for scalebar, etc.
        axes = self._add_axes_style(axes)
        return canvas, axes


    # private functions -------------------------------------------------
    def _parse_newick(self, newick, tree_format, ladderize):
        """
        Parse the newick string as either text, filepath or URL,
        and create an ete.TreeNode object as .tree. If no newick
        then init an empty TreeNode object.
        """
        if newick:
            # is newick a URL or string, path?
            if any(i in newick for i in ("http://", "https://")):
                try:
                    response = requests.get(newick)
                    response.raise_for_status()
                    self.tree = TreeNode(response.text.strip())
                except Exception as inst:
                    raise inst

            # create .tree attribute as TreeNode
            self.tree = TreeNode(newick, format=tree_format)
            if ladderize and not self._fixed_order:
                self.tree.ladderize()

        # otherwise make an empty TreeNode object
        else:
            self.tree = TreeNode()


    def _set_dims_from_tree_size(self):
        """
        Calculate reasonable height and width for tree given N tips
        """
        ntips = len(self.tree)
        if self._style.get("orient") in ["right", "left"]:
            # long tip-wise dimension
            if not self._style.get("height"):
                self._style["height"] = max(275, min(1000, 18 * ntips))
            if not self._style.get("width"):
                self._style["width"] = max(225, min(500, 18 * ntips))
        else:
            # long tip-wise dimension
            if not self._style.get("width"):
                self._style["width"] = max(275, min(1000, 18 * ntips))
            if not self._style.get("height"):
                self._style["height"] = max(225, min(500, 18 * ntips))


    def _decompose_tree(self): 
        """
        Update cartesian coordinates for plotting tree graph.

        Assigns updated name and idx features to every node. Coordinates are 
        stored to .edges and .verts.
        """
        # internal nodes: root is highest idx
        idx = self.nnodes - 1
        for node in self.tree.traverse("levelorder"):
            if not node.is_leaf():
                node.add_feature("idx", idx)
                if not node.name:
                    node.name = "i" + str(idx)
                idx -= 1

        # external nodes: lowest numbers are for tips (0-N)
        for node in self.tree.get_leaves()[::-1]:
            node.add_feature("idx", idx)
            if not node.name:
                node.name = "t" + str(idx)
            idx -= 1

        # get coordinates and then reorient 
        self._assign_coordinates()
        self._reorient_coordinates()
        #self._update_newick()


    def _assign_coordinates(self):
        """
        Update _coords and _verts
        """
        # postorder: first children and then parents. This moves up the list.
        # counting down from tip_num to ensure ladderized order.
        nidx = 0
        tidx = len(self) - 1

        # tips to root to fill in the verts and edges
        for node in self.tree.traverse("postorder"):
            if node.is_leaf() and not node.is_root():

                # get y-pos of tip
                node.y = self.tree.get_distance(node)
                if self._style["use_edge_lengths"] is False:
                    node.y = 0.

                # get x-pos of tip
                if self._fixed_order:
                    node.x = tidx - self._fixed_order.index(node.name)
                else:
                    node.x = tidx
                    tidx -= 1

                # verts are coordinates, edges connect parent-child
                self.verts[node.idx] = [node.x, node.y]
                self.edges[nidx] = [node.up.idx, node.idx]

            else:
                # create new nodes left and right
                node.y = self.tree.get_distance(node)
                if self._style["use_edge_lengths"] is False:
                    node.y = -1 * node.get_farthest_leaf(True)[1] - 1
                if node.children:
                    nch = node.children
                    node.x = sum(i.x for i in nch) / float(len(nch))
                else:
                    node.x = tidx

                self.verts[node.idx] = [node.x, node.y]
                if not node.is_root():
                    self.edges[nidx, :] = [node.up.idx, node.idx]
            nidx += 1

        # root to tips to fill in the coords and lines
        self._lines = []
        self._coords = []
        cidx = 0
        for node in self.tree.traverse():
            # add yourself
            if not node.is_leaf():
                self._coords += [[node.x, node.y]]
                pidx = cidx
                cidx += 1
                for child in node.children:
                    # add children
                    self._coords += [[child.x, node.y], [child.x, child.y]]
                    self._lines += [[pidx, cidx]]      # connect to newx
                    self._lines += [[cidx, cidx + 1]]  # connect newx to child
                    cidx += 2

        # convert to arrays
        self._coords = np.array(self._coords, dtype=float)
        self._lines = np.array(self._lines, dtype=int)


    def _reorient_coordinates(self):
        # invert for sideways trees; TODO
        if self.nnodes > 1:

            if self._style["orient"] in ['up', 0]:
                raise NotImplementedError()

            if self._style["orient"] in ['left', 1]:
                raise NotImplementedError()
                #self.verts[:, 1] = self.verts[:, 1] * -1
                #self.verts = self.verts[:, [1, 0]]
                #self._coords[:, 1] = self._coords[:, 1] * -1
                #self._coords = self._coords[:, [1, 0]]

            # TODO: there's a bug in cloud trees 'down' orientation drawings
            if self._style["orient"] in ['down', 0]:
                self.verts[:, 1] -= self.verts[:, 1].max()
                self.verts[:, 1] *= -1
                self._coords[:, 1] -= self._coords[:, 1].max()  # * -1
                self._coords[:, 1] *= -1
                #self.verts[:, 1] = self.verts[:, 1]  # * -1
                #self.verts = self.verts[:, [1, 0]]
                #self.verts[:, 1] += self.verts[:, 0].min()
                #self._coords[:, 1] += self._coords[:, 0].min()

            if self._style["orient"] in ['right', 3]:
                self.verts = self.verts[:, [1, 0]]
                self.verts[:, 0] -= self.verts[:, 0].max()
                self._coords = self._coords[:, [1, 0]]
                self._coords[:, 0] -= self._coords[:, 0].max()


    def _fullhover(self, ordered_features=["idx", "name", "dist", "support"]):
        # build full features titles
        lfeatures = list(set(self.tree.features) - set(ordered_features))
        ordered_features += lfeatures
        title = [
            ["{}: {}".format(feature, i) for i in
             self.get_node_values(feature, True, True)]
            for feature in ordered_features]
        title = ["\n".join(z) for z in zip(*title[:])]
        return title


    def _assign_tip_labels(self):
        """ parse arg or arglist for tip_labels and tip_colors """

        # shorthand label
        anchorshift = "-toyplot-anchor-shift"

        # tip color overrides tipstyle[fill]
        if self._style.get("tip_labels_color"):
            if 'fill' in self._style["tip_labels_style"]:
                self._style["tip_labels_style"].pop("fill")

        # tip_labels is False then hide tip labels
        if self._style["tip_labels"] is False:
            self._style["tip_labels"] = ["" for i in self.get_tip_labels()]
            self._style["tip_labels_style"][anchorshift] = "0px"

        # tip labels is not false, figure out tiplabels
        else:
            # if user did not change label-offset then shift it here
            if not self._style["tip_labels_style"][anchorshift]:
                self._style["tip_labels_style"][anchorshift] = "15px"

            # if user-defined tip labels as list [reversed]
            if isinstance(self._style["tip_labels"], list):
                self._style["tip_labels"] = self._style["tip_labels"]

            # True assigns tip labels from tree
            else:
                if self._fixed_order:
                    self._style["tip_labels"] = self._fixed_order
                else:
                    self._style["tip_labels"] = self.get_tip_labels()


    def _assign_node_labels(self):
        """
        parse arg or arglist for node_labels and node_colors.
        If node_color is provided then it overrides node fill.
        """

        # shorthand
        nvals = self.get_node_values()
        nidxs = self.get_node_values("idx")

        # False = Hide nodes and node labels (default)
        if self._style["node_labels"] is False:
            # make sure node size is a list in case
            if self._style["node_size"]:
                if isinstance(self._style["node_size"], (int, str)):
                    self._style["node_size"] = [
                        self._style["node_size"]] * len(nvals)
                    self._style["node_labels"] = ["" for i in nvals]

        # True = Show nodes, no labels b/c we are adding interactives
        elif self._style["node_labels"] is True:

            # hide labels
            self._style["vlshow"] = False
            self._style["node_labels"] = ["" for i in nidxs]

            # use default node size as a list if not provided
            if not self._style["node_size"]:
                self._style["node_size"] = [15] * len(nvals)

            # ensure entered node size arg is a list
            if isinstance(self._style["node_size"], (int, str)):
                self._style["node_size"] = [
                    int(self._style["node_size"])] * len(nvals)

        # user list
        else:
            # show labels
            self._style["vlshow"] = True

            # user-provided list is shown
            if isinstance(self._style["node_labels"], list):
                self._style["node_labels"] = self._style["node_labels"]

            elif isinstance(self._style["node_labels"], str) and \
                (self._style["node_labels"] in self.features):
                label = (self._style["node_labels"], 1, 1)
                self._style["node_labels"] = self.get_node_values(*label)

            # anything else defaults to idx
            else:
                self._style["node_labels"] = self.get_node_values("idx", 1, 0)

            # set node size to 0 if labels are empty including "0" but not "".
            if not isinstance(self._style["node_size"], list):
                # set default size if none
                if (self._style["node_size"] in [None, False]) and \
                   (self._style["node_size"] != 0):
                    self._style["node_size"] = 22

                # fill a list of values
                nsizes = []
                for nidx in self.get_node_values("idx", 1, 1):
                    if self._style["node_labels"][nidx] == "":
                        nsizes.append(0)
                    else:
                        nsizes.append(self._style["node_size"])
                self._style["node_size"] = nsizes


    def _get_tip_label_coords(self):
        # get coordinates of text from top to bottom (right-facing)
        xpos = ypos = align_edges = align_verts = angle = None

        if self._style["orient"] in ["right"]:
            angle = 0.
            # y-positions of tips are the (first) N rows of .verts
            # ypos = ttree.verts[-1*len(self.tree):, 1]
            ypos = self.verts[:len(self.tree), 1]
            if self._style["tip_labels_align"]:

                # x-position (edge) start is in column 0 of first N rows of .verts
                xpos = [self.verts[:, 0].max()] * len(self.tree)
                start = xpos

                # x-position end is in column 0 of first N rows of .verts
                finish = self.verts[:len(self.tree), 0]

                # make into arrays
                align_edges = np.array([
                    (i, i + len(xpos)) for i in range(len(xpos))])
                align_verts = np.array(
                    list(zip(start, ypos)) + list(zip(finish, ypos)))
            else:
                # x-position (edge) start is in column 0 of first N rows of .verts
                xpos = self.verts[:len(self.tree), 0]

            # overwrite tip order after the above stuff if fixed order
            if self._fixed_order:
                ypos = range(len(self.tree))

        # orient text for down-facing tree, angle by -90.
        elif self._style["orient"] in ['down']:
            angle = -90.
            xpos = self.verts[:len(self.tree):, 0]
            if self._style["tip_labels_align"]:
                ypos = [self.verts[:, 1].min()] * len(self.tree)
                start = ypos
                finish = self.verts[:len(self.tree), 1]
                align_edges = np.array(
                    [(i, i + len(ypos)) for i in range(len(ypos))])
                align_verts = np.array(
                    list(zip(xpos, start)) + list(zip(xpos, finish)))
            else:
                ypos = self.verts[:len(self.tree), 1]

            # overwrite tip order after the above stuff if fixed order
            if self._fixed_order:
                xpos = range(len(self.tree))

        return xpos, ypos, align_edges, align_verts, angle


    def _add_tree_to_axes(self, axes):
        """
        Add tree as a toyplot graph
        """
        if self._style["edge_type"] == 'c':
            mark = axes.graph(
                self.edges,
                vcoordinates=self.verts,
                vlshow=False,
                vsize=0,
                estyle=self._style["edge_style"],
                # ecolor=self._style["edge_color"], ## ...
            )
        else:
            mark = axes.graph(
                self._lines,
                vcoordinates=self._coords,
                vlshow=False,
                vsize=0.,
                estyle=self._style["edge_style"],
                # ecolor=self._style["edge_color"], ## ...
            )
        return mark


    def _add_tip_labels_to_axes(self, axes):
        """
        Positions tip labels on the coordinate axes given some orientation
        """
        xpos, ypos, aedges, averts, angle = self._get_tip_label_coords()

        # add tip names to coordinates calculated above
        mark = axes.text(
            xpos,
            ypos,
            self._style["tip_labels"],
            angle=angle,
            style=self._style["tip_labels_style"],
            color=self._style["tip_labels_color"],
        )

        # get stroke-width for aligned tip-label lines (optional)
        # copy stroke-width from the edge_style unless user set it
        if not self._style["edge_align_style"].get("stroke-width"):
            self._style["edge_align_style"]["stroke-width"] = \
                self._style["edge_style"]["stroke-width"]

        # add lines to connect tree tips to aligned tips. We don't
        # return this mark since it's optional.
        if self._style["tip_labels_align"]:
            axes.graph(
                aedges,
                vcoordinates=averts,
                estyle=self._style["edge_align_style"],
                vlshow=False,
                vsize=0,
            )
        return mark


    def _add_nodes_to_axes(self, axes):
        """
        add nodes as text-markers
        """
        # bail out if not any visible nodes (e.g., none w/ size>0)
        if not self._style["node_labels"]:
            return

        # shorthand names
        ncs = self._style["node_color"]

        # build markers
        marks = []
        for nidx in self.get_node_values('idx', 1, 1):
            # select node value
            nlabel = self._style["node_labels"][nidx]
            nsize = self._style["node_size"][nidx]
            nstyle = copy.deepcopy(self._style["node_style"])
            nlstyle = copy.deepcopy(self._style["node_labels_style"])

            # parsing color is tricky b/c there are many accepted formats
            if isinstance(ncs, str):
                nstyle["fill"] = self._style["node_color"]

            elif isinstance(ncs, (np.ndarray, list, tuple)):
                color = self._style["node_color"][nidx]
                if isinstance(color, (np.ndarray, np.void, list, tuple)):
                    color = toyplot.color.to_css(color)
                nstyle["fill"] = color
            else:
                pass

            # create mark if text or node
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

            # store the nodes/marks
            marks.append(mark)

        # node_hover == True to show all features interactive
        if (self._style["node_hover"] is True):
            title = self._fullhover()

        elif isinstance(self._style["node_hover"], list):
            # return advice if improperly formatted
            title = self._style["node_hover"]

        # if hover is false then no hover
        else:
            title = None

        # add nodes
        mark = axes.scatterplot(
            self.verts[:, 0],
            self.verts[:, 1],
            marker=marks,
            title=title,
        )
        return mark


    # returns modified axes
    def _add_axes_style(self, axes):
        
        axes.padding = self._style["axes"]["padding"]
        axes.show = self._style["axes"]["show"]
        
        # scalebar        
        axes.x.show = self._style["axes"]["x.show"]
        axes.x.ticks.show = self._style["axes"]["x.ticks.show"]
        axes.x.ticks.labels.angle = self._style["axes"]["x.ticks.labels.angle"]
        axes.x.domain.min = self._style["axes"]["x.domain.min"]
        axes.x.domain.max = self._style["axes"]["x.domain.max"]        

        # scalebar
        axes.y.show = self._style["axes"]["y.show"]
        axes.y.ticks.show = self._style["axes"]["y.ticks.show"]
        axes.y.ticks.labels.angle = self._style["axes"]["y.ticks.labels.angle"]
        axes.y.domain.min = self._style["axes"]["y.domain.min"]
        axes.y.domain.max = self._style["axes"]["y.domain.max"]        

        # allow coloring axes
        if (self._style["axes"]["x_label_color"] or 
            self._style["axes"]["y_label_color"]):
            axes.x.spine.style.update(
                {"stroke": self._style["axes"]["x_label_color"]})
            axes.x.ticks.style.update(
                {"stroke": self._style["axes"]["x_label_color"]})            
            axes.x.ticks.labels.style.update(
                {"stroke": self._style["axes"]["x_label_color"]})                        
            axes.y.spine.style.update(
                {"stroke": self._style["axes"]["y_label_color"]})                                    
            axes.y.ticks.style.update(
                {"stroke": self._style["axes"]["y_label_color"]})                                                
            axes.y.ticks.labels.style.update(
                {"stroke": self._style["axes"]["y_label_color"]})                                                            

        return axes



class Jitter:
    """
    Return a tree with edge lengths modified according to one of 
    the jitter functions. 

    node_slider: 

    node_multiplier:

    """
    def __init__(self, ttree):
        self.ttree = ttree

    def node_slider(self, prop=0.99):
        """
        Returns a toytree copy with node heights modified while retaining the 
        same topology but not necessarily node branching order. Node heights are
        moved up or down uniformly between their parent and highest child node 
        heights in 'levelorder' from root to tips. The total tree height is 
        retained at 1.0, only relative edge lengths change.

        ## for example run:
        c, a = node_slide(ctree).draw(
            width=400,
            orient='down', 
            node_labels='idx',
            node_size=15,
            tip_labels=False
            );
        a.show = True
        a.x.show = False
        a.y.ticks.show = True
        """
        assert isinstance(prop, float), "prop must be a float"
        assert prop < 1, "prop must be a proportion >0 and < 1."

        ctree = self.ttree.copy()
        for node in ctree.tree.traverse():

            ## slide internal nodes 
            if node.up and node.children:

                ## get min and max slides
                minjit = max([i.dist for i in node.children]) * prop
                maxjit = (node.up.height * prop) - node.height
                newheight = random.uniform(-minjit, maxjit)

                ## slide children
                for child in node.children:
                    child.dist += newheight

                ## slide self to match
                node.dist -= newheight
        return ctree


    def node_multiplier(self, multiplier=0.5):
        # make tree height = 1 * rheight
        ctree = self.ttree.copy()
        low, high = sorted([multiplier, 1. / multiplier])
        mult = random.uniform(low, high)
        for node in ctree.tree.traverse():
            node.dist = node.dist * mult
        return ctree



#############################################################################
# RANDOM TREES
#############################################################################

class RandomTree(object):

    @staticmethod
    def coaltree(ntips, ne=None, seed=None):
        """
        Returns a coalescent tree with ntips samples and waiting times 
        between coalescent events drawn from the kingman coalescent:
        (4N)/(k*(k-1)), where N is population size and k is sample size.
        Edge lengths on the tree are in generations.

        If no Ne argument is entered then edge lengths are returned in units
        of 2*Ne, i.e., coalescent time units. 
        """

        # seed generator
        random.seed(seed)

        # convert units
        coalunits = False
        if not ne:
            coalunits = True
            ne = 10000

        # build tree
        tips = [
            Toytree().tree.add_child(name=str(i)) for i in range(ntips)]
        while len(tips) > 1:
            rtree = Toytree()
            tip1 = tips.pop(random.choice(range(len(tips))))
            tip2 = tips.pop(random.choice(range(len(tips))))
            kingman = (4. * ne) / float(ntips * (ntips - 1))
            dist = random.expovariate(1. / kingman)
            rtree.tree.add_child(tip1, dist=tip2.height + dist)
            rtree.tree.add_child(tip2, dist=tip1.height + dist)
            tips.append(rtree.tree)

        # build tree
        self = Toytree(tips[0].write())    
        self.tree.ladderize()

        # make tree edges in units of 2N (then N doesn't matter!)
        if coalunits:
            for node in self.tree.traverse():
                node.dist /= (2. * ne)

        ## ensure tips are at zero
        for node in self.tree.traverse():
            if node.is_leaf():
                node.dist += node.height

        # set tipnames, decompose will fill internals
        ntip = 0
        for tip in self.get_tip_labels():
            node = self.tree.search_nodes(name=tip)[0]
            node.name = "r{}".format(ntip)
            ntip += 1

        # decompose fills in internal node names and idx
        self._decompose_tree()
        return self


    @staticmethod
    def unittree(ntips, treeheight=1.0, seed=None):
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

        treeheight(float):
            Scale tree height (all edges) so that root is at this height.
        """

        # seed generator
        random.seed(seed)

        # generate tree with N tips.
        tmptree = TreeNode()
        tmptree.populate(ntips)
        self = Toytree(newick=tmptree.write())

        # set tip names by labeling sequentially from 0
        self.tree.ladderize()
        self.tree.convert_to_ultrametric()

        # make tree height = 1 * treeheight
        _height = self.tree.height
        for node in self.tree.traverse():
            node.dist = (node.dist / _height) * treeheight

        # set tipnames, decompose will fill internals
        nidx = 0 
        for tip in self.get_tip_labels():
            node = self.tree.search_nodes(name=tip)[0]
            node.name = "r{}".format(nidx)
            nidx += 1

        # fill internal node names and idx
        self._decompose_tree()
        return self
