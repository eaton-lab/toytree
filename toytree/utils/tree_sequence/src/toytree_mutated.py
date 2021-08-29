#!/usr/bin/env python

"""

"""

import toytree


class ToyTreeMutated(toytree.ToyTree):
    """Superclass of ToyTree for auto-adding mutations to drawings.

    Parameters
    ----------
    treenode: toytree.TreeNode
        A treenode to wrap as a ToyTree object.
    mutations: List[Dict]
        A list of dicts of mutations, where mutation dict must include
        {node: int, time: float, 'metadata': {'mutation_list': [{'mutation_type': 1}]}}
    """
    def __init__(self, treenode, mutations):
        super().__init__(treenode)

    def draw(self, **kwargs):
        """Draw mutated ToyTree.
        """
        # warn user about disallowed styles in this class.
        # ...

        # draw the tree
        tree = self
        canvas, axes, mark = toytree.ToyTree.draw(tree, **kwargs)

        # add mutations to the tree
        xpos = []
        ypos = []
        for mut in tree.mutations:
            node = tree.tsidx_dict[mut.node]
            time = mut.time
            if m.layout == "l":
                ypos.append(node.x)
                xpos.append(time)
                marker='r0.4x1.5'
                
            elif m.layout == "r":
                ypos.append(node.x)
                xpos.append(-time)
                marker='o'#'r0.4x1.5'

            #
            elif m.layout == "d":
                opp = ydiff = node.dist
                adj = xdiff = node.x - node.up.x
                angle = np.arctan(opp / adj)
                new = time / np.tan(angle)
                print(node.y, node.x, opp, adj, angle, new)
                xpos.append(node.x )
                ypos.append(time)
                marker = 'o'
                
                
            elif m.layout == "u":
                xpos.append(node.x)
                ypos.append(-time)
                marker = 'r1.5x0.3'

        axes.scatterplot(
            xpos,
            ypos,
            marker='o',
            size=6,
            mstyle={"fill": toytree.COLORS2[3], "stroke": "black"},
            title=[
                f"mutation: {i.id}\npos: {i.position:.0f}\n"
                f"derived_state: {i.derived_state}\ntime: {time:.2f}"
                for i in tree.mutations
            ]
        );        