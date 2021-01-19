#!/usr/bin/env python

"""
Modify internal node ages from a dictionary input
"""



def set_node_heights_from_dict(tree, hdict):
    """
    Enter a dictionary mapping node idx to heights. Nodes that 
    are not included as keys will remain at there existing height.
    """
    # set node heights on a new tree copy
    ntre = tree.copy()

    # set node height to current value for those not in hdict
    for nidx in tree.idx_dict:
        if nidx not in hdict:
            hdict[nidx] = tree.idx_dict[nidx].height

    # iterate over nodes from tips to root
    for node in ntre.treenode.traverse("postorder"):
            
        # shorten or elongate child stems to reach node's new height
        for child in node.children:
            child.dist = hdict[node.idx] - hdict[child.idx] 
    return ntre





if __name__ == "__main__":

    import toytree
    tre = toytree.rtree.unittree(ntips=6, treeheight=100, seed=123)

    new_heights = {
        10: 200,
        9: 10,
        8: 150,
        7: 130,
        6: 20,
    }

    new_tre = set_node_heights_from_dict(tre, new_heights)

    print(tre.get_feature_dict("idx", "height"))
    print(new_tre.get_feature_dict("idx", "height"))    

    # import toyplot.browser
    # c1, a, m = tre.draw(ts='p', layout='r', scalebar=True)
    # c2, a, m = new_tre.draw(ts='p', layout='r', scalebar=True)
    # toyplot.browser.show([c1, c2])
