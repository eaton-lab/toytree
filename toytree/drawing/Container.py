#!/usr/bin/env python

"""
Container trees for plotting coalescent histories with demographic params
"""

import numpy as np
import toytree
import toyplot

from .utils import ToytreeError


class Container(object):
    def __init__(self, model=None, idx=0, width=400, height=400, spacer=0.25, axes=None):
        """
        Returns a Canvas and Axes with a fill container drawn representing
        widths of lineages (Ne) and divergence times. 
        """
        # setup 
        if not axes:
            self.canvas = toyplot.Canvas(width=width, height=height)
            self.axes = self.canvas.cartesian()
        else:
            self.axes = axes

        # spacer to prevent block overlaps
        self.spacer = spacer

        # draw only the container tree.
        if isinstance(model, toytree.Toytree.ToyTree):
            self.tree = model.copy()

        # draw the genealogies within the container tree.
        else:
            self.model = model
            self.tree = self.model.tree.copy()
            self.gtree = toytree.tree(self.model.df.genealogy[idx])
            self.gtree = self.gtree.mod.make_ultrametric()

        # get idx to Ne map from tree, or from model if not on tree.
        try:
            self.nes = self.tree.get_feature_dict("idx", "Ne")
        except AttributeError:
            self.tree.set_node_values("Ne", None, self.model.Ne)
            self.nes = self.tree.get_feature_dict("idx", "Ne")

        # normalize Ne values for plotting widths
        self.nes = {
            i: j for (i, j) in zip(
                self.nes.keys(), 
                toytree.utils.normalize_values(
                    np.sqrt(list(self.nes.values())),
                    10, 2, 8,
                ),
            )
        }
        self.tree = self.tree.set_node_values("nNe", self.nes)
        self.tree = self.tree.set_node_values("xrange", default=(0, 0))
        self.ndict = self.tree.get_feature_dict("idx")
        self._set_tip_xranges()

        # get colors for each spp
        self.colors = [next(toytree.icolors2) for i in range(len(self.tree))]

        # store blocks coordinates
        self.blocks = {}
        self.children = {}

        # draw container tree
        self._draw_tree()

        # draw genealogies
        if hasattr(self, "model"):
            self._draw_gene_blocks()

        # style the axes
        self._style_axes()


    def _set_tip_xranges(self):
        """
        Sets xrange for each node of the species tree representing the
        log-Ne scaled widths of branches.
        """
        # set tip nodes baselines spaced for Ne
        lidx = 0
        for idx in range(self.tree.ntips):
            node = self.ndict[idx]
            node.xrange = (lidx, lidx + self.nes[node.idx])
            lidx = node.xrange[1] + self.spacer


    def _draw_tree(self):
        """
        Draw the container by calling draw_block() from tip xrange positions.
        """
        # draw angle edges
        for node in self.tree.treenode.traverse("postorder"):
            if not node.is_leaf():
                self._draw_container_block(node.idx)

        # add root
        node = self.tree.treenode
        height = node.height + node.dist
        try:
            gheight = self.gtree.treenode.height
            self.maxheight = max(height, gheight) + 5
        except AttributeError:
            self.maxheight = height
        # self.maxheight = height            

        mp = self.blocks[self.children[node.idx][0]].xt1
        self.axes.fill(
            (node.height, self.maxheight),
            (mp - node.nNe / 2., mp - node.nNe / 2.), 
            (mp + node.nNe / 2., mp + node.nNe / 2.),             
            color='grey',
            opacity=0.25,
            along='y',
            title=(
                "idx={}\nname={}\nNe={}\nt_g={}\nt_c={}"
                .format(
                    node.idx,
                    '{} (root)'.format(node.name),
                    self.ndict[node.idx].Ne,
                    int(node.dist),
                    "{:.3f}".format(
                        (node.dist) / (2 * node.Ne)
                    ),
                ),
            )
        )
        rblock = Block()
        rblock.y0 = node.height
        rblock.y1 = self.maxheight
        rblock.xb0 = mp - node.nNe / 2.
        rblock.xb1 = mp + node.nNe / 2.
        rblock.xt0 = mp - node.nNe / 2.
        rblock.xt1 = mp + node.nNe / 2.
        self.blocks[node.idx] = rblock

        # TODO: check for overlaps and rerun with larger spacer if found
        # ...

        # draw species tree labels 
        xtext = {i: np.mean([j.xb0, j.xb1]) for (i, j) in self.blocks.items()}
        self.axes.text(
            [xtext[i] for i in range(self.tree.ntips)],
            np.repeat(0, len(self.tree)),
            self.tree.get_tip_labels(),  # range(len(self.tree)),
            color="#262626", 
            style={"baseline-shift": "-18px"}
        )


    def _draw_gene_blocks(self):

        # get gene tree
        self.gtree = self.gtree.set_node_values("ystart", None, 0)

        # use idx not names of species tree 
        idx2name = self.tree.get_feature_dict("idx", "name")
        tip2idx = {j: i for (i, j) in idx2name.items() if j.startswith("r")}
        gidx2spidx = {
            i.idx: tip2idx[i.name.split("-")[0]] for i in 
            self.gtree.get_feature_dict() if i.is_leaf()
        }
        self.gtree = self.gtree.set_node_values("inside", gidx2spidx)

        # store coalescences coordinates
        self.node_xs = []
        self.node_ys = []
        self.node_labels = []

        # iterate over the species tree blocks
        self.icount = 999
        for nb in self.tree.treenode.traverse("postorder"):
            self._draw_gene_block(nb.idx)


    def _style_axes(self):
        # styling
        self.axes.x.show = False
        self.axes.y.ticks.show = True

        # scale ticks
        tee = len(str(int(self.maxheight)))
        tze = (1 * 10 ** (tee - 2))
        tma = self.maxheight
        trd = round(tma / tze) * tze
        # print(tee, tze, tma, trd)
        self.axes.y.ticks.locator = toyplot.locator.Explicit(
            np.linspace(0, trd, 6).astype(int)[:-1],
            ["{:.0f}".format(i) for i in np.linspace(0, trd, 6).astype(int)][:-1],
        )
        self.axes.y.domain.max = self.maxheight + (self.maxheight * 0.01)
        self.axes.y.domain.min = -self.maxheight * 0.05


    def _draw_gene_block(self, idx):

        # species tree node index
        self.sidx = idx
        self.snode = self.ndict[self.sidx]
        self.pnode = self.snode.up
        self.block = self.blocks[self.snode.idx]
        if self.pnode:
            self.pblock = self.blocks[self.pnode.idx]

        # iterate until all genealogy nodes in this block are drawn
        while 1:

            # refresh to get nodes that are in this block
            idict = self.gtree.get_feature_dict(None, "inside")
            self.gnodes = [i for i, j in idict.items() if j == self.sidx]
            self.gnodes = [i for i in self.gnodes if not i.is_root()]

            # exit if all nodes completed
            if not self.gnodes:
                break

            # only select nodes with the same min height
            minheight = min([i.height for i in self.gnodes])
            self.gnodes = [i for i in self.gnodes if i.height == minheight]
            # print(
                # 'spnode: {}, gnodes: {} -- {}'.format(
                    # self.sidx, [(i.name) for i in self.gnodes], minheight))


            # if tips then sort by tipnames
            if all([i.ystart == 0 for i in self.gnodes]):
                # set xloc for any gnode that doesn't have one
                xlocs = np.linspace(
                    self.block.xb0, 
                    self.block.xb1, 
                    len(self.gnodes) + 2)[1:-1]

                # tiporder = [
                #     i for i in self.gtree.get_tip_labels() if 
                #     i.split("-")[0] == "r{}".format(self.sidx)
                # ]
                # if len(tiporder):
                #     curorder = [i.name for i in self.gnodes]
                #     tipdict = {j: i for (i, j) in enumerate(tiporder)}
                #     neworder = [tipdict[i] for i in curorder]
                #     xlocs = xlocs[neworder]


            # iterate over these nodes
            for idx, gnode in enumerate(self.gnodes):

                # will it coalesce in this block?
                coal = gnode.height + gnode.dist < self.block.y1

                # tips: set xstart position; non-tips: already have xloc
                if not hasattr(gnode, "xloc"):
                    gnode.xloc = xlocs[idx]
                    self.node_xs.append(xlocs[idx])
                    self.node_ys.append(0)
                    self.node_labels.append(gnode.name)

                # get yend location at coal event or block edge
                if coal:
                    gnode.yend = gnode.height + gnode.dist
                else:
                    gnode.yend = self.block.y1

                # get xend position or let it wiggle
                if coal & hasattr(gnode.up, "xloc"):
                    gnode.xend = gnode.up.xloc 
                else:
                    gnode.xend = None

                # nstops adaptively tuned
                nstops = min(10, max(3, int((gnode.yend - gnode.ystart) / 50000)))

                # get wiggle line
                wiggle = Wiggle(
                    block=self.block, 
                    pblock=self.pblock, 
                    xstart=gnode.xloc,
                    xend=gnode.xend,
                    ystart=gnode.ystart,
                    yend=gnode.yend,
                    nstops=nstops,
                )

                # print(gnode.name, gnode.xloc, gnode.xend, gnode.yend)

                try:
                    wiggle.get_line()
                except ToytreeError:
                    return wiggle

                # set color by species shared ancestry
                spp = [i.split("-")[0] for i in gnode.get_leaf_names()]
                if len(set(spp)) == 1:
                    cidx = int(spp[0][1:])
                    color = self.colors[cidx]
                else:
                    color = "#262626"

                # connect this node to the block edge
                self.axes.plot(
                    wiggle.xs, 
                    wiggle.ys, 
                    color=color,
                    opacity=0.5,
                )          

                # COAL EVENT
                if gnode.up.height < self.block.y1:

                    # mark as finished
                    gnode.inside = -1

                    # this can get revisited within a block...
                    if not hasattr(gnode.up, "xloc"):

                        gnode.up.inside = self.snode.idx

                        # record coal coord
                        self.node_xs.append(wiggle.xs[-1])
                        self.node_ys.append(wiggle.ys[-1])

                        # set parent to start from this end point
                        gnode.up.ystart = wiggle.ys[-1]  # gnode.height + gnode.dist
                        gnode.up.xloc = wiggle.xs[-1]

                # CONTINUE TO NEXT BLOCK
                else:
                    gnode.ystart = self.block.y1
                    gnode.xloc = wiggle.xs[-1]
                    gnode.inside = self.pnode.idx


        # add lines connecting points

        # add points at all nodes
        self.axes.scatterplot(
            np.array(self.node_xs),
            np.array(self.node_ys),
            # title=self.node_labels,
            color="#262626",  # toytree.colors[0],
            mstyle={"stroke": "none"},  # "stroke-opacity": 0.5},
            size=6,
            opacity=0.7,
        )
        self.node_xs = []
        self.node_ys = []


    def _draw_container_block(self, idx):
        """
        Draws paired descendants from each node.
        """
        # get children or skip
        if not self.ndict[idx].children:
            return

        # get paired lineages
        pair = Pair(self, idx)

        # add to plot
        self.axes.fill(
            (pair.block0.y0, pair.block0.y1),  
            (pair.block0.xb0, pair.block0.xt0),
            (pair.block0.xb1, pair.block0.xt1),
            color='grey',
            opacity=0.25,
            along='y',
            title=(
                "idx={}\nname={}\nNe={}\nt_g={}\nt_c={}"
                .format(
                    pair.node0.idx,
                    pair.node0.name,
                    self.ndict[pair.node0.idx].Ne,
                    int(pair.block0.y1 - pair.block0.y0),
                    "{:.3f}".format(
                        (pair.block0.y1 - pair.block0.y0) / \
                        (2 * self.ndict[pair.node0.idx].Ne)
                    ),
                ),
            )
        )
        self.axes.fill(
            (pair.block1.y0, pair.block1.y1),  
            (pair.block1.xb0, pair.block1.xt0),
            (pair.block1.xb1, pair.block1.xt1),
            color='grey',
            opacity=0.25,            
            along='y',
            title=(
                "idx={}\nname={}\nNe={}\nt_g={}\nt_c={}"
                .format(
                    pair.node1.idx,
                    pair.node1.name,
                    self.ndict[pair.node1.idx].Ne,
                    int(pair.block1.y1 - pair.block1.y0),
                    "{:.3f}".format(
                        (pair.block1.y1 - pair.block1.y0) / \
                        (2 * self.ndict[pair.node1.idx].Ne)
                    ),
                ),
            )
        )



class Block(object):
    def __init__(self):
        # coordinates for .fill w/ along='y',
        self.xt0 = 0
        self.xt1 = 0
        self.xb0 = 0
        self.xb1 = 0
        self.y0 = 0
        self.y1 = 0        

    def __repr__(self):
        return str(self.__dict__)

    @property
    def delta_x(self):
        return self.xt0 - self.xb0

    @property
    def delta_y(self):
        return self.y1 - self.y0

    @property
    def slope(self):
        return self.delta_x / self.delta_y


    def inside(self, x, y):
        if y >= self.y0:
            if y <= self.y1:
                if x >= self.xb0 + (y - self.y0) * self.slope:
                    if x <= self.xb1 + (y - self.y0) * self.slope:
                        return True
        return False


    def xrange_at_y(self, y):
        return (
            self.xb0 + (y - self.y0) * self.slope, 
            self.xb1 + (y - self.y0) * self.slope,
        )



class Pair:
    def __init__(self, con, idx):

        # get node dictionary
        self.nes = con.nes
        self.tree = con.tree
        self.ndict = self.tree.get_feature_dict("idx")

        # get children idxs sorted by xrange
        nodes = sorted(
            [i for i in self.ndict[idx].children], 
            key=lambda x: x.xrange[1]
        )
        idx0, idx1 = [i.idx for i in nodes]
        self.node = self.ndict[idx]
        self.node0 = self.ndict[idx0]
        self.node1 = self.ndict[idx1]

        # blocks for each lineage
        self.block0 = Block()
        self.block1 = Block()

        # get vertex where these sisters meet (+x from child 0's right)
        desc = self.tree.get_node_descendant_idxs(self.node0.idx)
        vert = max([self.ndict[i].xrange[1] for i in desc]) + con.spacer / 2

        # set block0 vertices
        self.block0.xt1 = vert
        self.block0.xt0 = vert - (self.node0.xrange[1] - self.node0.xrange[0])
        self.block0.xb0 = self.node0.xrange[0]
        self.block0.xb1 = self.node0.xrange[1]
        self.block0.y0 = self.node0.height
        self.block0.y1 = self.node0.height + self.node0.dist

        # set block1 vertices       
        self.block1.xt0 = vert
        self.block1.xt1 = vert + (self.node1.xrange[1] - self.node1.xrange[0])
        self.block1.xb0 = self.node1.xrange[0]
        self.block1.xb1 = self.node1.xrange[1]
        self.block1.y0 = self.node1.height
        self.block1.y1 = self.node1.height + self.node1.dist    

        # store parent node xrange
        ne = self.nes[idx]
        childnes = [self.nes[i] for i in (idx0, idx1)]
        childnesum = sum(childnes)

        # the range of parent block if centered at midpoint
        midanchor = (self.block0.xt1 - ne / 2, self.block0.xt1 + ne / 2)
        ranchor = (self.block1.xt1 - ne, self.block1.xt1)
        lanchor = (self.block0.xt0, self.block0.xt0 + ne)

        # if parent is wider than both children combined?
        if ne < childnesum:
            # if child0 starts left of parent when mid
            if self.block0.xt0 < midanchor[0]:
                # if child1 ends right of parent when mid
                if self.block1.xt1 > midanchor[1]:
                    # midpoint anchor
                    self.node.xrange = midanchor
                # if child1 is small and parent extends past
                else:
                    # right anchor
                    self.node.xrange = ranchor
            else:
                self.node.xrange = lanchor
        else:
            self.node.xrange = midanchor

        con.blocks[idx0] = self.block0
        con.blocks[idx1] = self.block1
        con.children[idx] = [idx0, idx1]



class Wiggle:
    def __init__(self, block, pblock, xstart, xend, ystart, yend, nstops):
        r"""
        Calculate slope to sample points.

           __/  /\ \
          /     \ \ \
         /____/\_\ \_\
        """
        self.b = block
        self.p = pblock
        self.nstops = nstops

        # intersection of pblock bottom and block top
        if not xend:

            # if hitting the root roof
            if self.p == self.b:
                # bxmin, bxmax = self.b.xrange_at_y(yend)
                xend = np.random.uniform(self.p.xb0, self.p.xb1)

            else:
                # the shared line between block and parent
                bxmin, bxmax = self.b.xrange_at_y(self.p.y0)  # yend)
                pxmin, pxmax = self.p.xrange_at_y(self.p.y0)

                # the trimmed overlap extent
                xmin = max(pxmin, bxmin)
                xmax = min(pxmax, bxmax)

                # a point uniformly sampled in this region
                xend = np.random.uniform(xmin, xmax)

                # if coal before ending then sample on slope towards this point
                if yend < self.b.y1:
                    delta_x = xend - xstart
                    delta_y = self.p.y0 - ystart
                    slope = delta_x / delta_y
                    xend = xstart + (yend - ystart) * slope

        self.xs = np.linspace(xstart, xend, nstops)
        self.ys = np.linspace(ystart, yend, nstops)        


    def get_line(self):
        r"""
        Samples points within bounds to connect lower to upper edge.

                    \   \
           __________\   \
          /        *       \
         /     *       /\   \
        /__*__________/  \___\

        """
        # shift with slope at each sample point
        for i in range(1, self.nstops - 1):     

            # jitter until point falls inside limits
            ntries = 0
            while 1:
                jitter = np.random.normal(self.xs[i], 0.05)
                # print(
                #     i, 
                #     self.xs[i], 
                #     jitter, 
                #     self.ys[i], 
                #     self.b.xrange_at_y(self.ys[i]),
                #     self.b.inside(jitter, self.ys[i])
                # )
                if self.b.inside(jitter, self.ys[i]):
                    break
                else:
                    ntries += 1

                # raise error on too many tries
                if ntries > 100:
                    print("maxtries")
                    raise ToytreeError("cannot connect wiggle")
            self.xs[i] = jitter
