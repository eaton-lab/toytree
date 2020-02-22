#!/usr/bin/env python

"""
Rooting class
"""

from .NodeAssist import NodeAssist
from .utils import ToytreeError


class Rooter:
    def __init__(self, tree, nastuple, resolve_root_dist, edge_features):
        """
        See docstring in ToyTree.root()
        """
        # store args
        self.tree = tree
        self.resolve_root_dist = resolve_root_dist
        self.edge_features = edge_features
        self.features = {"name", "dist", "support"}
        self.nas = None

        # dict for relabeling nodes {node: [parent, child, feat]}
        self.tdict = {}

        # the new node that will be inserted
        self.nnode = None

        # make a copy and ensure supports are either all int or float
        self.maxsup = max([int(i.support) for i in self.tree.treenode.traverse()])
        self.maxsup = (1.0 if self.maxsup <= 1.0 else 100)
        self.get_features()

        # parse node selecting arguments (nastuple) with NodeAssist
        self.get_match(*nastuple)

        # get the mrca node (or tip node) of the monopyletic matched query.
        self.node1 = self.nas.get_mrca()

        # the node on the other side of the edge to be split.
        self.node2 = self.node1.up

        # if rooting where root already exists then return current tree
        x0 = (self.node1.is_root())
        x1 = (self.node2.is_root() and self.tree.is_rooted())
        if not (x0 or x1):           

            # create new root node on an existing edge to split it.
            self.insert_new_node()

            # update edge lengths given new node insertion
            self.config_root_dist()

            # redirect support values and possibly others
            self.redirect_edge_features()
            self.restructure_tree()

            # update coodrds on tree
            self.update_tree_from_tdict()
            self.update()



    def update_tree_from_tdict(self):
        # update tree structure and node labels
        for node in self.tdict:
            node.up = self.tdict[node][0]
            node.children = self.tdict[node][1]
            for key, val in self.tdict[node][2].items():
                setattr(node, key, val)


    def update(self):
        # update coordinates which updates idx and adds it to any new nodes.
        self.tree.treenode = self.nnode
        self.tree.treenode.ladderize()
        self.tree._coords.update()



    def redirect_edge_features(self):
        """
        Set support values to maximum for new node since the user forced
        rooting, i.e, it is not uncertain. 
        """
        # mark new split with zero...
        for feature in set(self.edge_features) - set(["support", "dist"]):
            self.tdict[self.node2][2][feature] = 0.0

        # unless support value, then mark with full.
        if "support" in self.edge_features:
            self.tdict[self.node2][2]['support'] = self.maxsup
        else:
            self.tdict[self.node2][2]['support'] = self.node2.support



    def restructure_tree(self):
        """
        At this point tdict 
           (node): (parent) (children), features
        {
            nnode: [None, [node1, node2], {}]
            node1: [nnode, node1.children, {'dist'}]
            node2: [nnode, node2.children, {'dist': 0.0}]
        }
        """
        # start with the node leading from new root child2 to the 
        # rest of the tree structure and move up until old root.
        tnode = self.node2.up

        # label all remaining nodes by moving up from tnode to old root.
        while 1:

            # early break
            if not tnode:
                break

            # get parent node (should be already in tdict)
            # and children to be mod'd (the ones not yet in tdict)
            parent = [i for i in tnode.children if i in self.tdict][0]
            children = [i for i in tnode.children if i not in self.tdict]

            # break occurs after tnode is root
            if tnode.is_root():

                # need a root add feature here if unrooted...
                if len(children) > 1:

                    # update dist from new parent
                    self.tdict[tnode] = [
                        parent, 
                        children, 
                        {"dist": parent.dist},
                    ]

                    # update edge features from new parent
                    for feature in self.edge_features:
                        self.tdict[tnode][2][feature] = getattr(parent, feature)

                    # set tnode as parent's new child
                    self.tdict[parent][1].append(tnode)

                    # set children as descendant from tnode
                    for child in children:
                        self.tdict[child] = [tnode, child.children, {}]

                # get children that are not in tdict yet
                else:
                    for child in children:

                        # record whose children they are now 
                        # (node2 already did this)
                        if parent is self.node2:
                            self.tdict[self.node2][1].append(child)
                        else:
                            self.tdict[parent][1].append(child)

                        # record whose parents they have now and find distance
                        dist = {"dist": sum([i.dist for i in tnode.children])}
                        self.tdict[child] = [parent, child.children, dist]

                # finished
                break

            # normal nodes
            else:
                # update tnode.features [dist will be inherited from child]
                features = {'dist': tnode.dist, 'support': tnode.support}

                # keep connecting swap parent-child up to root
                if not tnode.up.is_root():
                    children += [tnode.up]

                # pass support values down (up in new tree struct)
                child = [i for i in tnode.children if i in self.tdict][0]                
                for feature in {'dist'}.union(self.edge_features):                   
                    features[feature] = getattr(child, feature)

                # store node update vals
                self.tdict[tnode] = [parent, children, features]

            # move towards root
            tnode = tnode.up



    def config_root_dist(self):
        """
        Now that the new root node is inserted .dist features must be 
        set for the two descendant nodes. Midpoint rooting is a common 
        option, but users can toggle 'resolve_root_dist' to change this.
        """
        # if not already at root polytomy, then connect node2 to parent
        if self.node2.up:
            if not self.node2.up.is_root():
                self.tdict[self.node2][1] += [self.node2.up]

        # if False create zero length root node
        if self.resolve_root_dist is False:
            self.resolve_root_dist = 0.0

        # if True then use midpoint rooting
        elif self.resolve_root_dist is True:
            self.tdict[self.node1][2]["dist"] = self.node1.dist / 2.
            self.tdict[self.node2][2]["dist"] = self.node1.dist / 2.

        # split the edge on 0 or a float
        if isinstance(self.resolve_root_dist, float):
            self.tdict[self.node1][2]["dist"] = self.node1.dist - self.resolve_root_dist            
            self.tdict[self.node2][2]["dist"] = self.resolve_root_dist
            if self.resolve_root_dist > self.node1.dist:
                raise ToytreeError("\n"
                "To preserve existing edge lengths the 'resolve_root_dist' arg\n"
                "must be smaller than the edge being split (it is selecting a \n"
                "a point along the edge.) The edge above node idx {} is {}."
                .format(self.node1.idx, self.node1.dist)
                )



    def insert_new_node(self):
        """

        """
        # the new root node to be placed on the split
        self.nnode = self.tree.treenode.__class__()
        self.nnode.name = "root"
        self.nnode.add_feature("idx", self.tree.treenode.idx)
        self.nnode.support = self.maxsup

        # remove node1 lineage leaving just node2 branch to be made into child
        self.node2.children.remove(self.node1)

        # new node has no parent and 1,2 as children and default features
        self.tdict[self.nnode] = [None, [self.node1, self.node2], {}]

        # node1 has new root parent, same children, and dist preserved 
        # (or split?), or should: node1.dist / 2.
        self.tdict[self.node1] = [
            self.nnode, 
            self.node1.children, 
            {"dist": self.node1.dist}
        ]  

        # node2 has new root parent, same children + mods, and dist/supp mods
        self.tdict[self.node2] = [
            self.nnode,
            self.node2.children,
            {"dist": 0.0},
        ]



    def get_features(self):
        # define which features to use/keep on nodes and which are "edge" 
        # features which must be redirected on rooting.
        testnode = self.tree.treenode.get_leaves()[0]
        extrafeat = {i for i in testnode.features if i not in self.features}
        self.features.update(extrafeat)



    def get_match(self, names, wildcard, regex):
        # find the selected node
        self.nas = NodeAssist(self.tree, names, wildcard, regex)
        self.nas.match_query()
        self.tipnames = self.nas.get_tipnames()

        # check for reciprocal match
        x0 = (not self.nas.is_query_monophyletic())
        x1 = (self.nas.get_mrca().is_root())
        if x0 or x1:
            clade1 = self.nas.tipnames
            self.nas.match_reciprocal()
            if not self.nas.is_query_monophyletic():
                clade2 = self.nas.tipnames
                raise ToytreeError(
                    "Matched query is paraphyletic: {}"
                    .format(sorted([clade1, clade2], key=len)[0]))
