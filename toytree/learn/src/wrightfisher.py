#!/usr/bin/env python

"""Create Wright-Fisher plots.

This is used to demonstrate how genetic drift creates by allele
frequency change over generations, and generates genealogies.
"""

from typing import Optional, Dict
import toyplot
import numpy as np
from toytree import ToyTree, Node
from toytree.color import COLORS1, COLORS2, ToyColor, ColorType


class WrightFisherPlot:
    def __init__(self, time=20, popsize=20, seed: Optional[int] = None, **kwargs):
        self.rng: np.random.Generator = np.random.default_rng(seed)
        """: numpy random number generator."""
        self.grid: np.ndarray = None
        """: numpy int (time, 2N) array of node IDs as a grid."""
        self.edges: np.ndarray = None
        """: numpy int (2N * time, 2) array of edges by node IDs."""
        self.sampled_edges: np.ndarray = None
        """: numpy int (??, 2) array of edges for nsamples."""
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
            width=kwargs.get("width", 500),
            height=kwargs.get("height", 500),
            style={"background-color": "white"},
        )
        self.axes = self.canvas.cartesian(
            ylabel="Time (generations)",
            xlabel="Gene copies",
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

    def draw_diploids(self):
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

    def get_ancestry_edges(self, sort: bool=True) -> None:
        """Sample ancestor-descendant relationships and store to .edges.

        This defines the ancestry connecting all gene copies in each
        generation to an ancestor from the previous generation.
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

    def draw_edges(self, **kwargs):
        """Draw ancestry edges with information in .edges."""
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

    def get_sampled_edges(self, nsamples: int):
        """Add sampled genealogy lines from N random samples, or a list of sampled indices."""
        if not nsamples:
            return
        samples = list(self.rng.choice(self.grid[-1], size=nsamples, replace=False))
        tracked = samples.copy()
        for edg in self.edges:
            if edg[0] in tracked:
                tracked.append(edg[1])

        # get the node pairs that make up each of these edges
        mask = np.isin(self.edges[:, 0], tracked)
        self.sampled_edges = self.edges[mask]

    def draw_sampled_edges(self, **kwargs):
        """Draw genealogy connecting sampled gene copies."""
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
        mark = self.axes.graph(
            self.sampled_edges,
            vcoordinates=self.coords[sorted(np.unique(self.sampled_edges))],
            **style,
        )
        self.marks['genealogy'] = mark

    def get_allele_states(self, allele_frequency=0.5):
        """Fills allele states based on ancestry edges."""
        if allele_frequency in [0, 1]:
            self.alleles[:] = 0
        else:
            self.alleles[:2 * self.popsize] = self.rng.binomial(
                n=1, p=allele_frequency, size=2 * self.popsize)
            for child in range(self.popsize * 2, self.popsize * 2 * self.time):
                parent = self.edges[self.edges[:, 0] == child, 1][0]
                self.alleles[child] = self.alleles[parent]

    def draw_nodes(self, color: Optional[ColorType], **kwargs):
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
            "size": 6,  #self.canvas.width / self.grid.shape[1] / 7.5,
            "mstyle": {
                "stroke": "black",
                "stroke-opacity": 0.75,
                "stroke-width": 1.5,
            },
        }
        style.update(kwargs)

        if color is None:
            color1 = ToyColor(COLORS1[0]).css
            color2 = ToyColor(COLORS1[1]).css
        else:
            color = ToyColor(color)
            rgb = [1 - i for i in color.rgba[:3]]
            color1 = color.css
            color2 = ToyColor(tuple(rgb + [1.0])).css
        style['color'] = [color1 if i == 0 else color2 for i in self.alleles]

        # plot marks
        mark = self.axes.scatterplot(
            self.coords[:, 0], self.coords[:, 1],
            **style,
        )
        self.marks['haploids'] = mark

    def get_genealogy(self, nsamples: int) -> ToyTree:
        """Returns a toytree matching to the evolved genealogy."""

        raise NotImplementedError("Coming soon.")
        # build dict of samples {0: Node(), 1: Node(), 2: Node(), ...}
        nodes = {i: Node(name=i) for i in range(nsamples)}

        # build coal time dict: {time0: (0, 1), time1: (2, 3), ...}
        # ...

        # build tree connecting nodes at coal times.
        tree = toytree.ToyTree()


def wright_fisher_simulation(
    time: int,
    popsize: int,
    seed: Optional[int] = None,
    nsamples: Optional[int] = None,
    sort_edges: bool = True,
    show_diploids: bool = False,
    allele_frequency: float = 1.0,
    node_size: int = 6,
    node_color: Optional[ColorType] = None,
    **kwargs,
) -> toyplot.Canvas:
    """Simulate a population evolving as a Wright-Fisher process.

    A WF process model generates 2N haploid gene copies in discrete
    non-overlapping generations, where each generation gene copies
    are randomly sampled with replacement from the previous generation.
    This process creates a genealogy of edges connecting all gene
    copies. Some gene copies leave no descendants, while others can
    leave multiple. Genetic variation, represented by different
    alleles (e.g., colors) among gene copies will be lost over time
    by this random sampling procedure, representing a manifestation
    of genetic drift.

    Parameters
    ----------
    time: int
        Number of generations to simulate evolution.
    popsize: int
        The number of diploid individuals in the population (N).
    seed: int
        Optional random number seed to make simulation repeatable.
    nsamples: int
        Optional, number of random gene copies to sample at the
        present. A genealogy will be drawn to connect the samples.
    sort_edges: bool
        If True the gene copies will be sorted so that edges are
        easier to interpret.
    show_diploids: bool
        If True a rectangle is drawn around pairs of gene copies to
        show how they can be randomly joined into diploid genomes.
    node_size: int
        The size of node markers for gene copies.
    node_color: Color
        Optional, a color of node markers for gene copies. If None
        then
    allele_frequency: float
        Starting allele frequency for bi-allelic variation.
    """
    model = WrightFisherPlot(seed=seed, time=time, popsize=popsize, **kwargs)
    model.get_ancestry_edges(sort=sort_edges)
    model.get_allele_states(allele_frequency=allele_frequency)
    model.get_sampled_edges(nsamples=nsamples)

    if show_diploids:
        model.draw_diploids()
    model.draw_edges()
    if nsamples is not None:
        model.draw_sampled_edges(vsize=node_size + 2)
    model.draw_nodes(size=node_size, color=node_color)
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
        show_diploids=True,
        node_size=6,
        allele_frequency=0.5,
        # node_color='red'
    )
    toyplot.browser.show(wf.canvas)
