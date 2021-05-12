#!/usr/bin/env python

"""
A didactic class for moves in tree space (SPR, TBR, etc.)
"""


#class TreeMoves:
#     def move_spr(self):
#         """
#         Sub-tree pruning and Regrafting. 
#         Select one edge randomly from the tree and split on that edge to create
#         two subtrees. Attach one of the subtrees (e.g., the smaller one) 
#         randomly to the larger tree to create a new node.
#         ... does SPR break edges connected to root when tree is real rooted?
#         """
#         pass
#         # On rooted trees we can work with nodes easier than edges. Start by
#         # selected a node at random that is not root.
#         # nodes = [i for i in self.ttree.tree.traverse() if not i.is_root()]
#         # rnode = nodes[random.randint(0, len(nodes) - 1)]
#         # # get all edges on the tree, skip last one which is non-real root edge
#         # edges = self.ttree.tree.get_edges()[:-1]
#         # # select a random edge
#         # redge = edges[random.randint(0, len(edges))]
#         # # break into subtrees
#         # tre1 = self.tree.prune(self.tree.get_common_ancestor(redge[0]).idx)
#         # tre2 = self.tree.prune(self.tree.get_common_ancestor(redge[1]).idx)



#     def move_tbr(self):
#         pass


#     def move_nni(self):
#         pass


#     def non_parametric_rate_smoothing(self):
#         """
#         Non-parametric rate smooting.
#         A method for estimating divergence times when evolutionary rates are 
#         variable across lineages by minimizing ancestor-descendant local rate
#         changes. According to Sanderson this method is motivated by the 
#         likelihood that evolutionary rates are autocorrelated in time.

#         returns Toytree
#         """
#         # p is a fixed exponent
#         p = 2
#         W = []
#         for node in self.ttree.traverse():
#             if not node.is_leaf():
#                 children = node.children
#                 ks = []
#                 for child in children:
#                     dist = abs(node.dist - child.dist)
#                     ks.append(dist ** p)
#                 W.append(sum(ks))

#         # root rate is mean of all descendant rates -- 
#         # n is the number of edges (rates) (nnodes - 1 for root)
#         r_root = np.mean(W)
#         rootw = []
#         for child in self.ttree.tree.children:
#             rootw.append((r_rroot - child.dist) ** p)
#         w_root = sum(rootw)
#         W.append(w_root)
#         k = []
#         for 
#         k = sum(  np.exp(abs(ri - rj), p)  )
#         W = sum(k)


#     def penalized_likelihood(...):
#         pass
#

# def wfunc(ttree, p):
#     ws = []
#     for node in ttree.tree.traverse():
#         if not node.is_leaf():          
#             w = sum([(node.dist - child.dist) ** p for child in node.children])
#             ws.append(w)
#     return sum(ws)


