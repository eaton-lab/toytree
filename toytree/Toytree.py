#!/usr/bin/env python

from __future__ import print_function, absolute_import

import itertools
from decimal import Decimal
from copy import deepcopy
import numpy as np

from .TreeNode import TreeNode
from .TreeStyle import TreeStyle
from .Coords import Coords
from .Drawing import Drawing
from .utils import ToytreeError, TreeMod, fuzzy_match_tipnames, NodeAssist
from .TreeParser import TreeParser
from .TreeWriter import NewickWriter


class ToyTree(object):
    """
    Toytree class object. 

    Parameters:
    -----------
    newick: (str, file, URL, or ToyTree)
        A newick or nexus formatted string, or file handle or URL of file 
        containing correctly formatted string. A toytree can also be reloaded
        from another toytree object.

    tree_format: int
        Format of the newick tree structure to be parsed. 

    Attributes:
    -----------


    Functions:
    ----------
    """
    def __init__(self, newick=None, tree_format=0, fixed_order=None):

        # if loadeing from a Toytree then inherit that trees draw style
        inherit_style = False

        # load from a TreeNode
        if isinstance(newick, TreeNode):
            self.treenode = newick

        # load TreeNode from a ToyTree
        elif isinstance(newick, ToyTree):
            self.treenode = newick.treenode
            inherit_style = True

        # prase a str, URL, or file
        elif isinstance(newick, (str, bytes)):
            self.treenode = TreeParser(newick, tree_format).treenodes[0]

        # make an empty tree
        else:
            self.treenode = TreeNode()

        # set tips order if fixing for multi-tree plotting (default None)
        self._fixed_order = None
        self._fixed_idx = list(range(self.ntips))
        if fixed_order:
            if not isinstance(fixed_order, (list, tuple)):
                raise ToytreeError("fixed_order arg should be a list")
            self._set_fixed_order(fixed_order)

        # ladderize the tree unless user fixed order and wants it not.
        if not self._fixed_order:
            self.treenode.ladderize()

        # Object for storing default plot settings or saved styles.
        # Calls several update functions when self.draw() to fit canvas.
        if inherit_style:
            self.style = newick.style
        else:
            self.style = TreeStyle(tree_style='n')

        # Object for plot coordinates. Calls .update() whenever tree modified.
        self._coords = Coords(self)
        self._coords.update()

        # Object for modifying trees beyond root, prune, drop
        self.mod = TreeMod(self)

    # --------------------------------------------------------------------
    # Class definitions 
    # --------------------------------------------------------------------    
    # ... could add __repr__, __iter__, __next__, but .tree has most already
    def __str__(self):
        """ return ascii tree ... (not sure whether to keep this) """
        return self.treenode.__str__()

    def __len__(self):
        """ return len of Tree (ntips) """
        return len(self.treenode)


    def _set_fixed_order(self, fixed_order):
        """
        Setting fixed_idx is important for when nodes are rotated, and edges
        are different lengths, b/c it allows updating coords to match up.
        """
        if fixed_order:
            if set(fixed_order) != set(self.treenode.get_leaf_names()):
                raise ToytreeError(
                    "fixed_order must include same tipnames as tree")
            self._fixed_order = fixed_order
            names = self.treenode.get_leaf_names()[::-1]
            self._fixed_idx = [names.index(i) for i in self._fixed_order]

    # --------------------------------------------------------------------
    # properties are not changeable by the user
    # --------------------------------------------------------------------    
    @property
    def features(self):
        feats = set()
        for node in self.treenode.traverse():
            feats.update(node.features)    
        return feats

    @property
    def nnodes(self):
        "The total number of nodes in the tree including tips and root."        
        return sum(1 for i in self.treenode.traverse())

    @property
    def ntips(self):
        "The number of tip nodes in the tree."
        return sum(1 for i in self.treenode.get_leaves())

    @property
    def newick(self, tree_format=0):
        "Returns newick represenation of the tree in its current state."
        # checks one of root's children for features and extra feats.
        if self.treenode.children:
            features = {"name", "dist", "support", "height", "idx"}
            testnode = self.treenode.children[0]
            extrafeat = {i for i in testnode.features if i not in features}
            features.update(extrafeat)
            return self.treenode.write(format=tree_format)

    # --------------------------------------------------------------------
    # functions to return values from the ete3 .treenode object ----------
    # --------------------------------------------------------------------
    def write(self, handle=None, tree_format=0, features=None):
        """
        Write newick string representation of the tree. 

        Parameters:
        -----------
        handle (str):
            A string file name to write output to. If None then newick is 
            returned as a string. 
        tree_format (int):
            Format of the newick string. See ete3 tree formats. Default=0.
        features (list, set, or tuple):
            Features of treenodes that should be written to the newick string
            in NHX format. Examples include "height", "idx", or other features
            you may have saved to treenodes. 

        """
        if self.treenode.children:
            # features = {"name", "dist", "support", "height", "idx"}
            # testnode = self.treenode.children[0]
            # extrafeat = {i for i in testnode.features if i not in features}
            # features.update(extrafeat)

            # get newick string
            writer = NewickWriter(
                treenode=self.treenode,
                tree_format=tree_format,
                features=features,
            )
            newick = writer.write_newick()

            # write to file or return as string
            if handle:
                with open(handle, 'w') as out:
                    out.write(newick)
            else:
                return newick


    def get_edges(self):
        """
        Returns an array with paired edges (parent, child).
        """
        return self._coords.edges


    # def get_edge_lengths(self):
    #     """
    #     Returns edge length values from tree object in node plot order. To
    #     modify edge length values you must modify nodes in the .treenode object
    #     directly. 
    #     """
    #     return self.get_node_values('dist', True, True)


    def get_edge_values(self, feature='idx'):
        """
        Returns edge values in the order they are plotted (see .get_edges())
        """
        elist = []
        for cidx in self._coords.edges[:, 1]:
            node = self.treenode.search_nodes(idx=cidx)[0]
            elist.append(
                # (node.__getattribute__(feature) if hasattr(node, feature) else "")
                (getattr(node, feature) if hasattr(node, feature) else "")
                )
        return np.array(elist)


    def get_edge_values_from_dict(self, node_value_dict=None, include_stem=True):
        """
        Enter a dictionary mapping node 'idx' or tuple of tipnames to values 
        that you want mapped to the stem and descendant edges that node. 
        Edge values are returned in proper plot order to be entered to the 
        edge_colors or edge_widths arguments to draw(). To see node idx values 
        use node_labels=True in draw(). If dictionary keys are integers it is
        assumed they are node idxs. 

        Note: it is safer to use tip labels to identify clades than node idxs 
        since tree tranformations (e.g., rooting) can change the mapping of 
        idx values to nodes on the tree.

        This function is most convenient for applying values to clades. To
        instead map values to specific edges (e.g., a single internal edge) 
        it will be easier to use tre.get_edge_values() and then to set the 
        values of the internal edges manually.

        Example 1: 
          tre = toytree.tree("((a,b),(c,d));")
          tre.get_edge_values_from_dict({5: 'green', 6: 'red'})
          # ['green', 'green', 'green', 'red', 'red', 'red']

        Example 2: 
          tre = toytree.tree("((a,b),(c,d));")
          tre.get_edge_values_from_dict({(a, b): 'green', (c, d): 'red'})          
          # ['green', 'green', 'green', 'red', 'red', 'red']
        """
        # map node idxs to the order in which edges are plotted
        idxs = {j: i for (i, j) in enumerate(self.get_edge_values())}
        values = [None] * self._coords.edges.shape[0]
        if node_value_dict is None:
            return values

        # convert tipname lists to node idxs
        rmap = {}
        for (key, val) in node_value_dict.items():
            if isinstance(key, (str, tuple)):
                node = fuzzy_match_tipnames(self, key, None, None, True, False)
                rmap[node.idx] = val
            else:
                rmap[key] = val
        node_value_dict = rmap

        # map over tree
        for node in self.treenode.traverse("levelorder"):
            if node.idx in node_value_dict:

                # add value to stem edge
                if include_stem:
                    if not node.is_root():
                        values[idxs[node.idx]] = node_value_dict[node.idx]

                # add value to descendants edges
                for desc in node.get_descendants():
                    values[idxs[desc.idx]] = node_value_dict[node.idx]
        return values


    def get_mrca_idx_from_tip_labels(self, names=None, wildcard=None, regex=None):
        """
        Returns the node idx label of the most recent common ancestor node 
        for the clade that includes the selected tips. Arguments can use fuzzy
        name matching: a list of tip names, wildcard selector, or regex string.
        """
        if not any([names, wildcard, regex]):
            raise ToytreeError("at least one argument required")
        node = fuzzy_match_tipnames(
            self, names, wildcard, regex, True, False)
        return node.idx


    def get_node_coordinates(self):
        """
        Returns coordinate locations of nodes in the tree as an array. Each
        row is an (x, y) coordinate, ordered by the 'idx' feature of nodes.
        The first ntips rows are the tip coordinates, which can also be 
        returned using .get_tip_coordinates()
        """
        return self._coords.verts


    def get_node_values(
        self, 
        feature=None, 
        show_root=False, 
        show_tips=False, 
        ):
        """
        Returns node values from tree object in node plot order. To modify
        values you must modify the .treenode object directly by setting new
        'features'. For example

        for node in ttree.treenode.traverse():
            node.add_feature("PP", 100)

        By default node and tip values are hidden (set to "") so that they
        are not shown on the tree plot. To include values for these nodes
        use the 'show_root'=True, or 'show_tips'=True arguments.

        tree.get_node_values("support", True, True)
        """
        # return input if feature does not exist
        # if feature is None:
        #     feature = ""
        # else:
        #     feature = str(feature)

        # access nodes in the order they will be plotted
        ndict = self.get_node_dict(return_internal=True, return_nodes=True)
        nodes = [ndict[i] for i in range(self.nnodes)[::-1]]

        # get features
        if feature:
            vals = [getattr(i, feature) if hasattr(i, feature)
                    else "" for i in nodes]
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
        return np.array(vals)


    def get_node_dict(self, return_internal=False, return_nodes=False):
        """
        Return node labels as a dictionary mapping {idx: name} where idx is 
        the order of nodes in 'preorder' traversal. Used internally by the
        func .get_node_values() to return values in proper order. 

        return_internal: if True all nodes are returned, if False only tips.
        return_nodes: if True returns TreeNodes, if False return node names.
        """
        if return_internal:
            if return_nodes:
                return {
                    i.idx: i for i in self.treenode.traverse("preorder")
                }
            else:
                return {
                    i.idx: i.name for i in self.treenode.traverse("preorder")
                }
        else:
            if return_nodes:
                return {
                    i.idx: i for i in self.treenode.traverse("preorder")
                    if i.is_leaf()
                }
            else:
                return {
                    i.idx: i.name for i in self.treenode.traverse("preorder")
                    if i.is_leaf()
                }


    def get_tip_coordinates(self, axis=None):
        """
        Returns coordinates of the tip positions for a tree. If no argument
        for axis then a 2-d array is returned. The first column is the x 
        coordinates the second column is the y-coordinates. If you enter an 
        argument for axis then a 1-d array will be returned of just that axis.
        """
        # get coordinates array
        coords = self.get_node_coordinates()
        if axis == 'x':
            return coords[:self.ntips, 0]
        elif axis == 'y':
            return coords[:self.ntips, 1]
        return coords[:self.ntips]


    def get_tip_labels(self, idx=None):
        """
        Returns tip labels in the order they will be plotted on the tree, i.e.,
        starting from zero axis and counting up by units of 1 (bottom to top 
        in right-facing trees; left to right in down-facing). If 'idx' is 
        indicated then a list of tip labels descended from that node will be 
        returned, instead of all tip labels. This is useful in combination 
        with other functions that select nodes/clades of the tree based on a 
        list of tip labels. You can use the toytree draw() command with 
        tip_labels='idx' or tip_labels=True to see idx labels plotted on nodes. 

        Parameters:
            idx (int): index label of a node.
        """
        if idx:
            treenode = self.treenode.search_nodes(idx=idx)[0]
            if self._fixed_order:
                return [i for i in self._fixed_order if i in 
                    treenode.get_leaf_names()]
            else:
                return treenode.get_leaf_names()[::-1]                
        else:
            if self._fixed_order:
                return self._fixed_order
            else:
                return self.treenode.get_leaf_names()[::-1]


    def set_node_values(self, attr, values=None, default=None):
        """
        Set values for a node attribute and RETURNS A COPY of the tree with 
        node values modified. If the attribute does not yet exist
        and you set vaues for only some nodes then a null values ("") will 
        be set to all other nodes. You cannot set "idx" (this is used 
        internally by toytree to draw trees). You can use this to set names, 
        change node distances ("dist") or heights ("height"; which will modify
        dist values to do so). If values is a single value it will be set for 
        all nodes, otherwise it should be a dictionary of idx numbers as keys
        and values as values. 

        Example:
        -------- 
        tre.set_node_values(attr="Ne", default=5000)
        tre.set_node_values(attr="Ne", values={0:1e5, 1:1e6, 2:1e3})
        tre.set_node_values(attr="Ne", values={0:1e5, 1:1e6}, default=5000)

        Parameters:
        -----------
        attr (str):
            The name of the node attribute to modify (cannot be 'idx').
        values (dict):
            A dictionary of {idx: value}. Values are set to their keys by 
            idx. Use .draw(node_labels='idx') to see idx labels on tree.
        default (int, str, float):
            You can use a default value to be filled for all other nodes not 
            listed in the values dictionary.

        Returns:
        ----------
        A ToyTree object is returned with the node values modified.
        """
        # make a copy
        nself = deepcopy(self)
        ndict = nself.get_node_dict(True, True)

        # find special cases
        if attr == "idx":
            raise ToytreeError("cannot modify idx values.")
        if attr == "height":
            raise ToytreeError("modifying heights not yet supported, coming..")

        # set everyone to a default value
        if default is not None:
            for key in ndict:
                setattr(ndict[key], attr, default)

        # set specific values
        if values:

            if not isinstance(values, dict):
                print(
                    "Values should be a dictionary. Use default to set"
                    " a single value.")
            else:
                # check that all keys are valid
                for nidx in values:
                    if nidx not in nself.get_node_values("idx", 1, 1):
                        raise ToytreeError(
                            "node idx {} not in tree".format(nidx))

                # or, set everyone to a null value
                else:           
                    for key in ndict:
                        if not hasattr(ndict[key], attr):
                            setattr(ndict[key], attr, "")

                # then set selected nodes to new values
                for key, val in values.items():
                    setattr(ndict[key], attr, val)
        return nself



    def copy(self):
        """ returns a deepcopy of the tree object"""
        return deepcopy(self)


    def is_rooted(self):
        """
        Returns False if the tree is unrooted.
        """
        if len(self.treenode.children) > 2:
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
            return bool(ctn1 == sum(1 for i in self.treenode.traverse()))
        if include_root:
            return bool(ctn2 == -1 + sum(1 for i in self.treenode.traverse()))
        return bool(ctn2 == sum(1 for i in self.treenode.traverse()))

    # --------------------------------------------------------------------
    # functions to modify the ete3 tree - MUST CALL ._coords.update()
    # --------------------------------------------------------------------
    def ladderize(self, direction=0):
        """
        Ladderize tree (order descendants) so that top child has fewer 
        descendants than the bottom child in a left to right tree plot. 
        To reverse this pattern use direction=1.
        """
        nself = deepcopy(self)
        nself.treenode.ladderize(direction=direction)
        nself._fixed_order = None
        nself._coords.update()
        return nself


    def collapse_nodes(self, min_dist=1e-6, min_support=0):
        """
        Returns a copy of the tree where internal nodes with dist <= min_dist
        are deleted, resulting in a collapsed tree. e.g.:

        newtre = tre.collapse_nodes(min_dist=0.001)
        newtre = tre.collapse_nodes(min_support=50)
        """
        nself = self.copy()
        for node in nself.treenode.traverse():
            if not node.is_leaf():
                if (node.dist <= min_dist) | (node.support < min_support):
                    node.delete()
        nself._coords.update()
        return nself



    def drop_tips(self, names=None, wildcard=None, regex=None):
        """
        Returns a copy of the tree with the selected tips removed. The entered
        value can be a name or list of names. To prune on an internal node to
        create a subtree see the .prune() function instead.

        Parameters:
        tips: list of tip names.

        # example:
        ptre = tre.drop_tips(['a', 'b'])
        """
        # make a deepcopy of the tree
        nself = self.copy()

        # return if nothing to drop
        if not any([names, wildcard, regex]):
            return nself

        # get matching names list with fuzzy match
        nas = NodeAssist(nself, names, wildcard, regex)
        tipnames = nas.get_tipnames()
        # tipnames = fuzzy_match_tipnames(
        #     ttree=nself,
        #     names=names,
        #     wildcard=wildcard,
        #     regex=regex,
        #     mrca=False,
        #     mono=False,
        # )

        if len(tipnames) == len(nself):
            raise ToytreeError("You cannot drop all tips from the tree.")

        if not tipnames:
            raise ToytreeError("No tips selected.")

        keeptips = [i for i in nself.get_tip_labels() if i not in tipnames]
        nself.treenode.prune(keeptips, preserve_branch_length=True)
        nself._coords.update()
        return nself


    # TODO: could swap or reverse .children node attr to swap_children & update
    def rotate_node(
        self, 
        names=None, 
        wildcard=None, 
        regex=None, 
        idx=None):
        # modify_tree=False,
        """
        Returns a ToyTree with the selected node rotated for plotting.
        tip colors do not align correct currently if nodes are rotated...
        """
        # make a copy
        revd = {j: i for (i, j) in enumerate(self.get_tip_labels())}
        neworder = {}

        # get node to rotate
        treenode = fuzzy_match_tipnames(
            self, names, wildcard, regex, True, True)
        children = treenode.up.children
        names = [[j.name for j in i.get_leaves()] for i in children]
        nidxs = [[revd[i] for i in j] for j in names]

        # get size of the big clade
        move = max((len(i) for i in nidxs))
        if len(nidxs[0]) > len(nidxs[1]):
            move = min((len(i) for i in nidxs))

        # newdict
        cnames = list(itertools.chain(*names))
        tdict = {i: None for i in cnames}
        cycle = itertools.cycle(itertools.chain(*nidxs))
        for m in range(move):
            next(cycle)
        for t in cnames:
            tdict[t] = next(cycle)

        for key in revd:
            if key in tdict:
                neworder[key] = tdict[key]
            else:
                neworder[key] = revd[key]

        revd = {j: i for (i, j) in neworder.items()}
        neworder = [revd[i] for i in range(self.ntips)]

        # returns a new tree (i.e., copy) modified w/ a fixed order
        nself = ToyTree(self.newick, fixed_order=neworder)
        nself._coords.update()
        return nself


    def resolve_polytomy(
        self,
        dist=1.0,
        support=100,
        recursive=True):
        """
        Returns a copy of the tree with all polytomies randomly resolved.
        Does not transform tree in-place.
        """
        nself = self.copy()
        nself.treenode.resolve_polytomy(
            default_dist=dist,
            default_support=support,
            recursive=recursive)
        nself._coords.update()
        return nself


    def unroot(self):
        """
        Returns a copy of the tree unrooted. Does not transform tree in-place.
        """
        nself = self.copy()
        # updated unroot function to preserve support values to root node
        nself.treenode.unroot()       
        nself.treenode.ladderize()
        nself._coords.update()
        return nself



    def root(
        self, 
        names=None, 
        wildcard=None, 
        regex=None, 
        resolve_root_dist=True,
        edge_features=["support"],
        ):
        """
        (Re-)root a tree by moving the tree anchor (real or phantom root node)
        to a new split in the tree. 

        Rooting location can be selected by entering 
        a list of tipnames descendant from a node, or using wildcard or regex 
        to get a list of tipnames. 

        names: (list) (default=None)
            A list of tip names. Root is placed along edge to mrca node. 

        wildcard: (str) (default=None)
            A string matching multiple tip names. Root is placed along edge to
            the mrca node of selected taxa.

        regex: (str) (default=None)
            A regex string matching multiple tip names. Root is placed along 
            edge to the mrca node of selected taxa.

        resolve_root_dist: (float or bool) (default=True)
            Length along the edge at which to place the new root, or a boolean
            indicating auto methods. Default is True, which means to use mid-
            point rooting along the edge. False will root at the ancestral node
            creating a zero length edge. A float value will place the new node
            at a point along the edge starting from the ancestral node. A float
            value greater than the edge length will raise an error.

        edge_features: (list) (default=["support"])
            Node labels in this list are treated as edge labels (e.g., support
            values represent support for a split/edge in the tree). This effects
            how labels are moved when the tree is re-rooted. By default support
            values are treated as edge features and moved to preserve clade
            supports when the tree is re-rooted. Other node labels, such as 
            names do not make sense to shift in this way. New splits that are
            created by rooting are set to 100 by default.

        Example:
        To root on a clade that includes the samples "1-A" and "1-B" you can
        do any of the following:

        rtre = tre.root(outgroup=["1-A", "1-B"])
        rtre = tre.root(wildcard="1-")
        rtre = tre.root(regex="1-[A,B]")
        """
        # insure edge_features is an iterable
        if not edge_features:
            edge_features = []
        if isinstance(edge_features, (str, int, float)):
            edge_features = [edge_features]

        # make a deepcopy of the tree
        nself = self.copy()
        maxsup = max([int(i.support) for i in nself.treenode.traverse()])
        maxsup = (1.0 if maxsup <= 1.0 else 100)

        # define which features to use/keep and which are "edge" features
        testnode = nself.treenode.get_leaves()[0]
        features = {"name", "dist", "support"}
        extrafeat = {i for i in testnode.features if i not in features}
        features.update(extrafeat)        

        # find the node whose parent edge will be pinched to root
        nas = NodeAssist(nself, names, wildcard, regex)
        nas.match_query()
        if (not nas.is_query_monophyletic()) or (nas.get_mrca().is_root()):
            clade1 = nas.tipnames
            nas.match_reciprocal()
            if not nas.is_query_monophyletic():
                clade2 = nas.tipnames
                raise ToytreeError(
                    "Matched query is paraphyletic: {}"
                    .format(sorted([clade1, clade2], key=len)[0]))

        # get the mrca node (or tip node) of the monopyletic matched query.
        node1 = nas.get_mrca()

        # the node on the other side of the edge to be split.
        node2 = node1.up

        # if rooting where root already exists then bail out.
        if (node1.is_root() or (node2.is_root() and nself.is_rooted())):
            print("No effect, tree is already rooted by {}.".format(nas.tipnames))            
            return self

        # the new root node to be placed on the split
        nnode = nself.treenode.__class__()
        nnode.name = "root"
        nnode.add_feature("idx", nself.treenode.idx)
        nnode.support = maxsup

        # remove node1 lineage leaving just node2 branch to be made into child
        node2.children.remove(node1)

        # create dictionary for relabeling nodes {node: [parent, child, feat]}
        tdict = {}

        # new node has no parent and 1/2 as children and default features
        tdict[nnode] = [None, [node1, node2], {}]

        # node1 has new root parent, same children, and dist preserved (or split?)
        tdict[node1] = [nnode, node1.children, {"dist": node1.dist}]  # node1.dist / 2.

        # node2 has new root parent, same children + mods, and dist/supp mods
        tdict[node2] = [nnode, node2.children, {"dist": 0.0}]

        # if not already at root polytomy, then connect node2 to parent
        if node2.up:
            if not node2.up.is_root():
                tdict[node2][1] += [node2.up]

        # if False create zero length root node
        if resolve_root_dist is False:
            resolve_root_dist = 0.0
        
        # if True then use midpoint rooting
        if resolve_root_dist is True:
            tdict[node1][2]["dist"] = node1.dist / 2.
            tdict[node2][2]["dist"] = node1.dist / 2.
        
        # split the edge on 0 or a float
        if isinstance(resolve_root_dist, float):
            tdict[node1][2]["dist"] = node1.dist - resolve_root_dist            
            tdict[node2][2]["dist"] = resolve_root_dist
            if resolve_root_dist > node1.dist:
                raise ToytreeError("\n"
                "To preserve existing edge lengths the 'resolve_root_dist' arg\n"
                "must be smaller than the edge being split (it is selecting a \n"
                "a point along the edge.) The edge above node idx {} is {}."
                .format(node1.idx, node1.dist)
                )

        # mark new split with zero...
        for feature in set(edge_features) - set(["support"]):
            tdict[node2][2][feature] = 0.0

        # unless support value, then mark with full.
        if "support" in edge_features:
            tdict[node2][2]['support'] = maxsup
        else:
            tdict[node2][2]['support'] = node2.support

        # label all remaining nodes
        tnode = node2.up
        while 1:

            # early break
            if not tnode:
                break

            # get parent node and children to be mod'd
            parent = [i for i in tnode.children if i in tdict][0]
            children = [i for i in tnode.children if i not in tdict]

            # break after the root
            if tnode.is_root():

                # need a root add feature here if unrooted...
                if len(children) > 1:

                    # update dist from new parent
                    tdict[tnode] = [parent, children, {"dist": parent.dist}]
                    
                    # update edge features from new parent
                    for feature in edge_features:
                        tdict[tnode][2][feature] = getattr(parent, feature)

                    # set tnode as parent's new child
                    tdict[parent][1].append(tnode)

                    # set children as descendant from tnode
                    for child in children:
                        tdict[child] = [tnode, child.children, {}]

                # get children that are not in tdict yet
                else:
                    for child in children:

                        # record whose children they are now (node2 already did this)
                        if parent is node2:
                            tdict[node2][1].append(child)
                        else:
                            tdict[parent][1].append(child)

                        # record whose parents they have now and find distance
                        dist = {"dist": sum([i.dist for i in tnode.children])}
                        tdict[child] = [parent, child.children, dist]

                # finished
                break

            # normal nodes
            else:
                # update tnode.features
                features = {i: getattr(tnode, i) for i in ('dist', 'support')}
                
                # keep connecting swap parent-child up to root
                if not tnode.up.is_root():
                    children += [tnode.up]

                # pass support values down (up in new tree struct)
                for feature in edge_features:
                    child = [i for i in tnode.children if i in tdict][0]
                    features[feature] = getattr(child, feature)

                # store node update vals
                tdict[tnode] = [parent, children, features]

            # move towards root
            tnode = tnode.up

        # update tree structure and node labels
        for node in tdict:
            node.up = tdict[node][0]
            node.children = tdict[node][1]
            for key, val in tdict[node][2].items():
                setattr(node, key, val)

        # update coordinates which updates idx and adds it to any new nodes.
        nself.treenode = nnode
        nself.treenode.ladderize()
        nself._coords.update()
        return nself              


    # old root function that used 'set_outgroup', now deprecated.
    # def root(self, names=None, wildcard=None, regex=None):
    #     """
    #     (Re-)root a tree by creating selecting a existing split in the tree,
    #     or creating a new node to split an edge in the tree. Rooting location
    #     is selected by entering the tips descendant from one child of the root
    #     split (e.g., names='a' or names=['a', 'b']). You can alternatively
    #     select a list of tip names using a fuzzy selector based on a unique
    #     shared string (wildcard="prz") or a regex matching pattern.

    #     Example:
    #     To root on a clade that includes the samples "1-A" and "1-B" you can
    #     do any of the following:

    #     rtre = tre.root(outgroup=["1-A", "1-B"])
    #     rtre = tre.root(wildcard="1-")
    #     rtre = tre.root(regex="1-[A,B]")
    #     """
    #     # make a deepcopy of the tree
    #     nself = self.copy()

    #     # get treenode of the common ancestor of selected tips
    #     try:
    #         node = fuzzy_match_tipnames(
    #             nself, names, wildcard, regex, True, True)       

    #     except ToytreeError:           
    #         # try reciprocal taxon list
    #         tipnames = fuzzy_match_tipnames(
    #             nself, names, wildcard, regex, False, False)
    #         tipnames = list(set(self.get_tip_labels()) - set(tipnames))
    #         node = fuzzy_match_tipnames(
    #             nself, tipnames, None, None, True, True)

    #     # split root node if more than di- as this is the unrooted state
    #     if not nself.is_bifurcating():
    #         nself.treenode.resolve_polytomy()

    #     # root the object with ete's translate
    #     nself.treenode.set_outgroup(node)
    #     nself._coords.update()

    #     # get features
    #     testnode = nself.treenode.get_leaves()[0]
    #     features = {"name", "dist", "support", "height"}
    #     extrafeat = {i for i in testnode.features if i not in features}
    #     features.update(extrafeat)

    #     # if there is a new node now, clean up its features
    #     nnode = [i for i in nself.treenode.traverse() if not hasattr(i, "idx")]
    #     if nnode:
    #         # nnode is the node that was added
    #         # rnode is the location where it *should* have been added
    #         nnode = nnode[0]
    #         rnode = [i for i in nself.treenode.children if i != node][0]

    #         # get idxs of existing nodes
    #         maxidx = max(
    #             [int(i.idx) for i in nself.treenode.traverse()
    #             if hasattr(i, "idx")])                   

    #         # newnode is a tip
    #         if node.is_leaf():
    #             nnode.name = str("rerooted")
    #             rnode.name = node
    #             rnode.add_feature("idx", maxidx + 1)
    #             rnode.dist *= 2
    #             sister = rnode.get_sisters()[0]
    #             sister.dist *= 2
    #             rnode.support = 100
    #             for feature in extrafeat:
    #                 nnode.add_feature(feature, getattr(rnode, feature))
    #                 rnode.del_feature(feature)

    #         # newnode is internal
    #         else:
    #             nnode.add_feature("idx", maxidxs + 1)
    #             nnode.name = str("rerooted")
    #             nnode.dist *= 2
    #             sister = nnode.get_sisters()[0]
    #             sister.dist *= 2
    #             nnode.support = 100

    #     # store tree back into newick and reinit Toytree with new newick
    #     # if NHX format then preserve the NHX features.
    #     nself.treenode.ladderize()
    #     nself._coords.update()
    #     return nself        

    # --------------------------------------------------------------------
    # Draw functions imported, but docstring here
    # --------------------------------------------------------------------
    def draw(
        self,
        tree_style=None,
        height=None,
        width=None,
        axes=None,        
        layout=None,
        tip_labels=None,
        tip_labels_colors=None,
        tip_labels_style=None,
        tip_labels_align=None,
        node_labels=None,
        node_labels_style=None,
        node_sizes=None,
        node_colors=None,
        node_style=None,
        node_hover=None,
        node_markers=None,
        edge_colors=None,
        edge_widths=None,
        edge_type=None,
        edge_style=None,
        edge_align_style=None,
        use_edge_lengths=None,
        scalebar=None,
        padding=None,
        xbaseline=None,
        ybaseline=None,
        admixture_edges=None,
        **kwargs):
        """
        Plot a Toytree tree, returns a tuple of Toyplot (Canvas, Axes) objects.

        Parameters:
        -----------
        tree_style: str
            One of several preset styles for tree plotting. The default is 'n'
            (normal). Other options inlude 'c' (coalescent), 'd' (dark), and
            'm' (multitree). You also create your own TreeStyle objects.
            The tree_style sets a default set of styling on top of which other
            arguments passed to draw() will override when plotting.

        height: int (optional; default=None)
            If None the plot height is autosized. If 'axes' arg is used then 
            tree is drawn on an existing Canvas, Axes and this arg is ignored.

        width: int (optional; default=None)
            Similar to height (above). 

        axes: Toyplot.Cartesian (default=None)
            A toyplot cartesian axes object. If provided tree is drawn on it.
            If not provided then a new Canvas and Cartesian axes are created
            and returned with the tree plot added to it.

        use_edge_lengths: bool (default=False)
            Use edge lengths from .treenode (.get_edge_lengths) else
            edges are set to length >=1 to make tree ultrametric.

        tip_labels: [True, False, list]
            If True then the tip labels from .treenode are added to the plot.
            If False no tip labels are added. If a list of tip labels
            is provided it must be the same length as .get_tip_labels().

        tip_labels_colors:
            ...

        tip_labels_style:
            ...

        tip_labels_align:
            ...

        node_labels: [True, False, list]
            If True then nodes are shown, if False then nodes are suppressed
            If a list of node labels is provided it must be the same length
            and order as nodes in .get_node_values(). Node labels can be 
            generated in the proper order using the the .get_node_labels() 
            function from a Toytree tree to draw info from the tree features.
            For example: node_labels=tree.get_node_labels("support").

        node_sizes: [int, list, None]
            If None then nodes are not shown, otherwise, if node_labels
            then node_size can be modified. If a list of node sizes is
            provided it must be the same length and order as nodes in
            .get_node_dict().

        node_colors: [list]
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

        admixture_edges: [tuple, list]
            Admixture edges will add colored edges to the plot in the style 
            of the 'edge_align_style'. These will be drawn from (source, dest, 
            heightsource, heightdest). 

        """
        # allow ts as a shorthand for tree_style
        if kwargs.get("ts"):
            tree_style = kwargs.get("ts")

        # pass a copy of this tree so that any mods to .style are not saved
        nself = deepcopy(self)
        if tree_style:
            nself.style.update(TreeStyle(tree_style[0]))

        # update kwargs to merge it with user-entered arguments:
        userargs = {
            "height": height,
            "width": width,
            "layout": layout,
            "tip_labels": tip_labels,
            "tip_labels_colors": tip_labels_colors,
            "tip_labels_align": tip_labels_align,
            "tip_labels_style": tip_labels_style,
            "node_labels": node_labels,
            "node_labels_style": node_labels_style,
            "node_sizes": node_sizes,
            "node_colors": node_colors,
            "node_hover": node_hover,
            "node_style": node_style,
            "node_markers": node_markers,
            "edge_type": edge_type,
            "edge_colors": edge_colors,
            "edge_widths": edge_widths,
            "edge_style": edge_style,
            "edge_align_style": edge_align_style,
            "use_edge_lengths": use_edge_lengths,
            "scalebar": scalebar,
            "padding": padding,
            "xbaseline": xbaseline, 
            "ybaseline": ybaseline,
            "admixture_edges": admixture_edges,
            # "orient": orient,
        }

        # update kwargs with userargs, update style w/ kwargs except empty ones
        kwargs.update(userargs)
        censored = {i: j for (i, j) in kwargs.items() if j is not None}
        nself.style.update(censored)

        # warn user if they entered kwargs that weren't recognized:
        allkeys = list(userargs.keys()) + ["debug", "ts"]
        unrecognized = [i for i in kwargs if i not in allkeys]
        if unrecognized:
            print("unrecognized arguments skipped: {}".format(unrecognized))
            print("check the docs, argument names may have changed.")

        # Init Drawing class object.
        draw = Drawing(nself)

        # Debug returns the object to test with.
        if kwargs.get("debug"):
            return draw

        # Make plot. If user provided explicit axes then include them.
        canvas, axes = draw.update(axes=axes)
        return canvas, axes




class RawTree():
    """
    Barebones tree object that only parses newick and assigns idx
    """
    def __init__(self, newick):
        self.treenode = TreeParser(newick, 0).treenodes[0]
        self.ntips = len(self.treenode)
        self.nnodes = (len(self.treenode) * 2) + 1
        self.update_idxs()


    def update_idxs(self):
        "set root idx highest, tip idxs lowest ordered as ladderized"

        # n internal nodes - 1 
        idx = self.nnodes - 1

        # from root to tips label idx
        for node in self.treenode.traverse("levelorder"):
            if not node.is_leaf():
                node.add_feature("idx", idx)
                idx -= 1

        # external nodes: lowest numbers are for tips (0-N)
        for node in self.treenode.iter_leaves():
            node.add_feature("idx", idx)
            idx -= 1
