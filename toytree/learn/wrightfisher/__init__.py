#!/usr/bin/env python

"""Create Wright-Fisher plots.

This is used to demonstrate how genetic drift creates by allele
frequency change over generations, and generates genealogies.
"""

from typing import Optional, Dict, List, Union
import toyplot
import numpy as np
from toytree import ToyTree, Node
from toytree.color import COLORS1, COLORS2, Color


class WrightFisherPlot:
    def __init__(self, time=20, popsize=20, seed: Optional[int]=None, **kwargs):
        self.rng: np.random.Generator = np.random.default_rng(seed)
        """: numpy random number generator."""
        self.grid: np.ndarray = None
        """: numpy int (time, 2N) array of node IDs as a grid."""
        self.edges: np.ndarray = None
        """: numpy int (2N * time, 2) array of edges by node IDs."""
        self.coords: np.ndarray = None
        """: numpy int (2N * time, 2) array of coordinates by ID."""
        self.canvas: toyplot.Canvas = None
        """: toyplot Canvas."""
        self.axes: toyplot.coordinates.Cartesian = None
        """: toyplot cartesian axes."""
        self.marks: Dict[str, 'toyplot.Mark'] = {}
        """: toyplot Marks."""
        self.time: int = time
        """: Number of discrete generations to simulate evolution."""
        self.popsize: int = popsize
        """: diploid population size (N)."""
        self.alleles: np.ndarray = np.zeros(popsize * 2 * time, dtype=int)
        """: numpy int array of allele states for gene copies by ID."""
        self._setup_grid_and_canvas(**kwargs)

    def _setup_grid_and_canvas(self, **kwargs) -> None:
        """Init values for grid, coords, canvas, and axes."""
        # get node coordinates
        self.grid = np.arange(self.popsize * 2 * self.time)
        self.grid = self.grid.reshape((self.time, self.popsize * 2))
        _ys, _xs = np.where(self.grid > -1)
        self.coords = np.column_stack([_xs, _ys[::-1]])

        # setup the canvas and axes
        self.canvas = toyplot.Canvas(
            width=kwargs.get("width", 800),
            height=kwargs.get("height", 800),
            style={"background-color": "white"},
        )
        self.axes = self.canvas.cartesian(
            ylabel="Time (generations)",
            xlabel="Gene copies at the present",
            margin=70,
            padding=25,
        )
        self.axes.y.ticks.labels.style["font-size"] = 14
        self.axes.y.label.style["font-size"] = 16
        self.axes.y.label.offset = 30
        self.axes.y.ticks.locator = toyplot.locator.Extended()
        self.axes.y.ticks.show = True

        self.axes.x.ticks.show = False
        self.axes.x.ticks.labels.show = False
        self.axes.x.spine.show = False
        self.axes.x.label.style["font-size"] = 16
        self.axes.x.label.offset = 0

    def add_diploids(self):
        """Adds a rectangle around pairs of gene copies to represent a diploid individual."""
        self.marks['diploids'] = self.axes.rectangle(
            self.coords[:, 0][::2] - 0.25,
            self.coords[:, 0][::2] + 1.25,
            self.coords[:, 1][::2] - 0.25,
            self.coords[:, 1][::2] + 0.25,
            style={
                "fill": "lightgrey", "stroke": "grey",
                "stroke-opacity": 0.75, "stroke-width": 1.5,
            },
        )

    def add_lines(self, sort: bool=True, **kwargs):
        """Adds lines from gene copies to randomly sampled parents each generation.

        This defines the ancestry connecting all gene copies in each
        generation to an ancestor from the previous generation. This
        also applies color (alleles) to gene copies based on their
        genealogy.
        """
        # iterate over each generation adding pairs of node indices
        for gen in range(self.grid.shape[0] - 1, 0, -1):

            # children idxs span from left to right
            lower_idxs = self.grid[gen]

            # randomly sample parent idxs (some have many children, some none)
            upper_idxs = self.rng.choice(
                self.grid[gen - 1], size=self.grid[gen - 1].size, replace=True)

            # get sorting index for the upper idxs
            if sort:
                order = np.argsort(upper_idxs)
            else:
                order = np.arange(upper_idxs.size)

            # update array of edges
            iedges = np.column_stack([lower_idxs, upper_idxs[order]])
            if self.edges is not None:
                self.edges = np.concatenate([self.edges, iedges])
            else:
                self.edges = iedges

        # style the graph
        style = {
            "vlshow": False, "ecolor": "black", "ewidth": 1.25, 
            'vsize': 0, 'estyle': {}, 'eopacity': 0.6}
        style.update(kwargs)

        # add graph lines from lower_idxs to upper_idxs, using coordinates for all
        self.marks['genealogy'] = self.axes.graph(
            self.edges,
            vcoordinates=self.coords[sorted(np.unique(self.edges))],
            **style,
        )

    def add_sampled_lines(self, nsamples: int, **kwargs):
        """Add sampled genealogy lines from N random samples, or a list of sampled indices."""
        samples = list(self.rng.choice(self.grid[-1], size=nsamples, replace=False))

        # base styles for the graph
        style = {
            "vlshow": False,
            "vsize": 8,
            "vmarker": 'o',
            "vcolor": "black",
            "vstyle": {'stroke': 'black', 'stroke-width': 2},            
            "ecolor": 'black',
            "ewidth": 3,
            "estyle": {},
        }
        style.update(kwargs)

        # get selected edges to show
        tracked = samples.copy()
        for edg in self.edges:
            if edg[0] in tracked:
                tracked.append(edg[1])

        # get the node pairs that make up each of these edges
        mask = np.isin(self.edges[:, 0], tracked)
        edges = self.edges[mask]

        # add graph lines from lower_idxs to upper_idxs, using coordinates for all
        mark = self.axes.graph(
            edges,
            vcoordinates=self.coords[sorted(np.unique(edges))],
            **style,
        )
        self.marks['genealogy'] = mark

    def add_haploids(self, p=0.5, **kwargs):
        """Add circle marks for gene copies showing allele frequencies.

        Allele frequencies are mapped on generation 1 randomly and then
        inherited in all following generations based on genealogy edges.

        Parameters
        ----------
        p: float
            Frequency of allele 1 at a mono- or bi-allelic locus.
        """
        style = {
            "marker": "o",
            "size": 6, #self.canvas.width / self.grid.shape[1] / 7.5,
            "mstyle": {
                "stroke": "black",
                "stroke-opacity": 0.75,
                "stroke-width": 1.5,
            },
        }
        color1 = Color(COLORS1[0]).css
        color2 = Color(COLORS1[1]).css
        color0 = Color('white').css
        style.update({i:j for i,j in kwargs.items() if i != "color"})
        colors = [color0] * self.coords.shape[0]

        # fill all allele states given the edges
        self.alleles[:2 * self.popsize] = self.rng.binomial(1, p, size=2 * self.popsize)
        if self.edges is not None:
            for child in range(self.popsize * 2, self.popsize * 2 * self.time):
                parent = self.edges[self.edges[:, 0] == child, 1][0]
                self.alleles[child] = self.alleles[parent]
                #  colors = [color1 if i == 0 else color2 for i in self.alleles]

        colors = [color1 if i == 0 else color2 for i in self.alleles]        

        # plot marks
        mark = self.axes.scatterplot(
            self.coords[:, 0], self.coords[:, 1],
            color=colors,
            **style,
        )
        self.marks['haploids'] = mark

    def get_genealogy(self, nsamples: int) -> ToyTree:
        """Returns a toytree matching to the evolved genealogy."""
        
        # build dict of samples {0: Node(), 1: Node(), 2: Node(), ...}
        nodes = {i: Node(name=i) for i in range(nsamples)}

        # build coal time dict: {time0: (0, 1), time1: (2, 3), ...}
        # ...

        # build tree connecting nodes at coal times.
        tree = toytree.ToyTree()


def wright_fisher_simulation(
    time: int,
    popsize: int,
    seed: Optional[int]=None,
    nsamples: Optional[int]=None,
    sort_edges: bool=True,
    show_diploids: bool=False,
    show_alleles: bool=True,
    node_size: int=6,
    **kwargs,
    ) -> toyplot.Canvas:
    """...
    
    Parameters
    ----------
    """
    model = WrightFisherPlot(seed=seed, time=time, popsize=popsize, **kwargs)
    if show_diploids:
        model.add_diploids()
    model.add_lines(sort=sort_edges)
    model.add_sampled_lines(nsamples, vsize=node_size + 2)
    if show_alleles:
        model.add_haploids(size=node_size)
    return model


if __name__ == "__main__":

    import toyplot.browser

    # wf = WrightFisherPlot(seed=None, time=40, popsize=16, width=500, height=800)
    # # wf.add_diploids()
    # wf.add_lines(sort=True)
    # wf.add_sampled_lines(6)
    # wf.add_haploids()            # this should go last

    wf = wright_fisher_simulation(
        time=30, popsize=16, seed=123, nsamples=5, 
        width=500, height=500,
        # show_alleles=False,
        # show_diploids=True,
        node_size=7
    )
    toyplot.browser.show(wf.canvas)
