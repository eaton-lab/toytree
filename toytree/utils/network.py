#!/usr/bin/env python

"""
Network parsing utilities
"""

import os
import re
import toytree



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
                small, big = sorted(node.children, key=len)
                root = toytree.TreeNode(name='root')
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
