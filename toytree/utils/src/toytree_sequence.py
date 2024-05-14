#!/usr/bin/env python

"""Utilities for visualizing TreeSequences from tskit or SLiM.

The :class:`ToyTreeSequence` class holds the tskit.trees.TreeSequence 
object in its `.tree_sequence` attribute. It is primarily used to 
generate drawings of one or more trees with the option to display 
mutations, MutationTypes, and a chromosome structure. These latter 
options are mostly for SLiM simulated TreeSequences.

Examples
--------
>>> ts = msprime.sim_ancestry()
>>> mts = msprime.sim_mutations()
>>> tts = ToyTreeSequence(tts)

>>> # Draw an individual tree w/ mutations.
>>> tts.draw_tree(idx=0, ...)
>>> tts.draw_tree(site=30, ...)

# Draw the TreeSequence w/ mutations.
>>> tts.draw_tree_sequence(max_trees=10, chromosome=...)
"""

from typing import Optional, Iterable, Union, Dict, TypeVar, Collection, Mapping
from loguru import logger
import numpy as np
from toytree.utils.src.toytree_sequence_drawing import ToyTreeSequenceDrawing
import toytree


logger = logger.bind(name="toytree")

ToyTree = TypeVar("toytree.ToyTree")
TskitTree = TypeVar("tskit.trees")
TreeSequence = TypeVar("tskit.trees.TreeSequence")


class ToyTreeSequence:
    """Return an instance of a ToyTreeSequence.

    ToyTreeSequence objects wrap around tskit.trees.TreeSequence 
    objects to make it easier to extract subsamples from trees, and 
    visualize one or multiple trees as a sequence.

    Parameters
    ----------
    tree_sequence: tskit.trees.TreeSequence
        A tree sequence object from msprime, tskit, SLiM, etc.
    sample: int or Iterable [int]
        The max number of samples per population to include in a tree.
    seed: int
        A random seed used to sample the samples to include in tree.
    name_dict: Mapping[int,str]
        Optionally include a dictionary mapping tree sequence int node 
        IDs to st names. If not provided then tip Nodes will be auto
        renamed from treesequence data as {pop-id}-{node-id}.
    """
    def __init__(
        self,
        tree_sequence: TreeSequence,
        sample: Union[int, Iterable[int], None] = None,
        seed: Optional[int] = None,
        name_dict: Optional[Mapping[int, str]] = None,
    ):
        # TODO: perhaps combine name_dict and 'sample' request method?

        # store user args
        self.rng = np.random.default_rng(seed)
        """: numpy random number generator seeeded."""
        self.npopulations = len(list(tree_sequence.populations()))
        """: number of populations in the TreeSequence."""
        self.sample: Collection = None
        """: the number of haplotypes to sample from the TreeSequence."""
        self.tree_sequence: TreeSequence = None
        """: the TreeSequence object."""
        self.name_dict: Mapping[int, str] = {} if name_dict is None else name_dict
        self._i = 0
        """: iterable counter."""

        # subsample/simplify treesequence to same or smaller nsamples
        if sample is None:
            self.sample = [tree_sequence.sample_size]
            self.tree_sequence = tree_sequence
        elif isinstance(sample, int):
            self.sample = [sample] * self.npopulations
            self.tree_sequence = self._get_subsampled_ts(tree_sequence)
        else:
            self.sample = sample
            self.tree_sequence = self._get_subsampled_ts(tree_sequence)

    def __len__(self):
        return self.tree_sequence.num_trees

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.at_index(self._i)
        except IndexError as err:
            self._i = 0
            raise StopIteration from err
        self._i += 1
        return result

    def __repr__(self):
        return f"<ToyTreeSequence ntrees={len(self)}>"

    def _get_subsampled_ts(self, tree_sequence: TreeSequence) -> TreeSequence:
        """Return a subsampled (simplify'd) tree sequence.

        Samples a maximum of `self.sample` nodes at time=0 from each
        population. This is useful for working with simulations from
        SLiM where nodes of the entire population are often present.
        """
        samps = []
        for pidx, pop in enumerate(tree_sequence.populations()):
            ndt = tree_sequence.tables.nodes
            mask = (ndt.population == pop.id) & (ndt.time == 0) & (ndt.flags == 1)
            if mask.sum():
                arr = np.arange(mask.shape[0])[mask]
                size = min(arr.size, self.sample[pidx])
                samp = self.rng.choice(arr, size=size, replace=False)
                samps += samp.tolist()
        logger.debug(samps)
        sampled_ts = tree_sequence.simplify(samps, keep_input_roots=True)
        return sampled_ts

    def at_index(self, index: int):
        """Return a ToyTree from the indexed order in the tree_sequence."""
        tree = self.tree_sequence.at_index(index)
        return self._get_toytree(tree)

    def at_site(self, pos: int):
        """Return a ToyTree for a position in the tree_sequence."""
        tree = self.tree_sequence.at(pos)
        return self._get_toytree(tree, site=pos)

    def _get_toytree(self, tree: TskitTree, site: Optional[int] = None) -> ToyTree:
        """Return a ToyTree with mutations for a tree selected by site or index.

        It is assumed here that the tree is fully coalesced, returning
        a multitree for multiple trees present is not yet supported...
        """
        # create a psuedo-root that will either be replaced by the root
        # of the tree, if it has a single one, or will be the root to
        # multipe subtrees if they do not coalesce. This root will have
        # the root nodes as children, but they will only have None as up

        # create the root node
        tsidx_dict = {}

        # warn use if multiple roots are present
        if tree.has_multiple_roots:
            logger.warning(f"tree has multiple ({len(tree.roots)}) roots.")
            # a special name to indicate the root is masked ancestors
            pseudo_root = toytree.Node(name="MASKED-ANCESTORS")
            pseudo_root.tsidx = -1
            for tsidx in tree.roots:
                node = toytree.Node(name=tsidx, dist=tree.branch_length(tsidx))
                node.tsidx = tsidx
                # setting disconnected root children causes more problems
                # than its worth. It was easier to just hide the root node
                # during visualizations if desired.
                # node._up = None
                # pseudo_root._children += (node, )
                pseudo_root._add_child(node)
                tsidx_dict[tsidx] = node
                logger.debug(f"adding root: {tsidx}")

                # if root has no children then
        else:
            tsidx = tree.roots[0]
            pseudo_root = toytree.Node(name=tsidx, dist=0)
            pseudo_root.tsidx = tsidx
            tsidx_dict[tsidx] = pseudo_root

        # root_idx = max(pdict.values())
        # idx_dict = {root_idx: toytree.TreeNode(name=root_idx, dist=0)}
        # idx_dict[root_idx].add_feature("tsidx", root_idx)

        # dict of {child: parent, ...} e.g., {0: 5, 1: 8, 2: 7, ...}
        pdict = tree.get_parent_dict()
        logger.debug(pdict)

        # iterate over child, parent items
        for cidx, pidx in pdict.items():
            # if parent already in tsdict get existing Node
            if pidx in tsidx_dict:
                pnode = tsidx_dict[pidx]

            # else create a new Node for it.
            else:
                pnode = toytree.Node(name=str(pidx), dist=tree.branch_length(pidx))
                pnode.tsidx = pidx
                tsidx_dict[pidx] = pnode
                logger.debug(f"adding child: {cidx} to parent: {pidx}")

            # if child node already exists use Node.
            if cidx in tsidx_dict:
                cnode = tsidx_dict[cidx]

            # create a new Node
            else:
                if cidx in self.name_dict:
                    name = self.name_dict[cidx]
                else:
                    pop = self.tree_sequence.tables.nodes.population[cidx]
                    name = f"p{pop}-{cidx}"
                cnode = toytree.Node(
                    name=name,
                    dist=tree.branch_length(cidx),
                )
                cnode.tsidx = cidx
                tsidx_dict[cidx] = cnode
            pnode._add_child(cnode)

        # wrap TreeNode as a toytree
        # return pseudo_root
        ttree = toytree.ToyTree(pseudo_root)  # root_idx])#.ladderize()

        # add mutations as metadata
        if site is not None:
            ttree.mutations = [i for i in tree.mutations() if i.site == site]
        else:
            ttree.mutations = list(tree.mutations())

        # add dict to translate ts idx to toytree idx
        ttree.tsidx_dict = ttree.get_feature_dict("tsidx", None)
        return ttree

    def draw_tree_sequence(
        self,
        start: int = 0,
        max_trees: int = 10,
        height: int = None,
        width: int = None,
        # show_mutations: bool=True,
        scrollable: bool = True,
        **kwargs,
    ):
        # -> Tuple[toyplot.Canvas, toyplot.coordinates.cartesian, :
        """
        Returns a toyplot Canvas, Axes, and list of marks composing 
        a TreeSequenceDrawing with genealogies corresponding to 
        positions along a chromosome.

        Parameters:
        -----------
        """
        # get list of trees.
        ntrees = len(self)
        tmax = start + min(ntrees, max_trees)
        tree_range = range(start, tmax)
        trees = [self.at_index(i) for i in tree_range]
        breaks = self.tree_sequence.breakpoints(True)[start: tmax + 1]
        tsd = ToyTreeSequenceDrawing(
            trees, breaks,
            width=width, height=height,
            scrollable=scrollable,
            **kwargs,
        )
        return tsd.canvas, tsd.axes, tsd.marks

    def draw_tree(
        self,
        site: Optional[int] = None,
        idx: Optional[int] = None,
        mutation_size: Union[int, Iterable[int]] = 8,
        mutation_style: Dict[str, str] = None,
        mutation_color_palette: Iterable['color'] = None,
        show_label=True,
        **kwargs,
    ):
        """Return a toytree drawing of a selected tree site or index.

        You can select a tree by index or site, but not both. The
        selected tree is extracted from the tree_sequence as a
        ToyTree object with relabeled tips showing the population id.
        Mutations are drawn on edges and colored by MutationType, if
        info is present.
        """
        if (site is None) and (idx is None):
            idx = 0
        if (site is not None) and (idx is not None):
            raise ValueError("must enter a 'site' or 'idx' argument, but not both.")
        if site is not None:
            label = f"tree at site {site}"
            tree = self.at_site(site)
        else:
            ivals = list(self.tree_sequence.breakpoints())
            label = f"tree in interval {idx} (sites {ivals[idx]:.0f}-{ivals[idx+1]:.0f})"
            tree = self.at_index(idx)

        # draw the tree with kwargs
        canvas, axes, mark = tree.draw(**kwargs)

        # standard color palette for mtypes, or user-specified one.
        colormap = (
            mutation_color_palette if mutation_color_palette is not None
            else toytree.color.COLORS1)

        # build mutation marker info
        xpos = []
        ypos = []
        titles = []
        colors = []

        # TODO: iterate over .sites() to show positions and describe
        # whether multiple mutations occurred at a position. This
        # needs to be tested for both msprime and slim data types...
        for mut in tree.mutations:

            # get node id and time using the 'tsidx' (tskit node id)
            node = tree.tsidx_dict[mut.node]
            time = mut.time

            # TODO: make optional.
            # do now show mutations on root node.
            if node.is_root():
                continue

            # project mutation points to proper layout type
            if mark.layout == "l":
                ypos.append(node._x)
                xpos.append(time)
            elif mark.layout == "r":
                ypos.append(node._x)
                xpos.append(-time)
            elif mark.layout == "d":
                xpos.append(node._x)
                ypos.append(time)
            elif mark.layout == "u":
                xpos.append(node._x)
                ypos.append(-time)

            # try to extract mtype from metadata if present.
            try:
                mtype = int(mut.metadata['mutation_list'][0]['mutation_type'])
            except Exception:
                mtype = 0

            # store color and title for this point
            color = colormap[mtype]
            colors.append(color)
            title = (
                f"id: {mut.id}\n"
                f"site: {mut.site:.0f}\n"
                f"time: {mut.time:.0f}\n"
                f"mtype: {mtype}")
            titles.append(title)

        # update mutation style dict
        mstyle = {"stroke": "black"}
        if mutation_style is not None:
            mstyle.update(mutation_style)

        # draw the mutations
        mark2 = axes.scatterplot(
            xpos, ypos,
            marker='o',
            size=mutation_size,
            color=colors if colors else None,
            mstyle=mstyle,
            title=titles if titles else None,
        )

        # add axes labels
        if show_label:
            axes.label.text = label
        return canvas, axes, (mark, mark2)


if __name__ == "__main__":

    # EXAMPLE
    import ipcoal
    # import toyplot.browser
    # import pyslim
    toytree.set_log_level("DEBUG")

    # SLIM/shadie example
    import tskit
    TSFILE = "/tmp/test.trees"
    # full ts
    ts = tskit.load(TSFILE)
    # subsampled ts
    tts = ToyTreeSequence(ts, sample=10)
    # get a toytree
    node = tts.at_index(0)
    print(node)
    for child in node.children:
        print(child, child.up)
    # print(node.draw_ascii())
    toytree.ToyTree(node)  # ._draw_browser()
    # tts._get_toytree(tts.at_index(0))

    # ...
    # TRE = toytree.rtree.unittree(ntips=6, treeheight=1e6, seed=123)
    # MOD = ipcoal.Model(tree=TRE, Ne=1e5, recomb=2e-9, store_tree_sequences=True)
    # MOD.sim_loci(1, 10000)

    # # slim_ts = pyslim.load("/tmp/test2.trees")
    # ts = MOD.ts_dict[0]
    # tts = ToyTreeSequence(ts, sample=5, seed=123)  #.at_index(0)
    # tts.draw_tree(width=None, height=300)  #, idxs=None)# scrollable=True)
    # tts = ToyTreeSequence(slim_ts, sample=5, seed=123).at_index(0)

    # TREE = toytree.rtree.unittree(10, treeheight=1e5)
    # MOD = ipcoal.Model(tree=TREE, Ne=1e4, nsamples=1)
    # MOD.sim_loci(5, 2000)

    # # optional: access the tree sequences directly
    # TS = MOD.ts_dict[0]

    # # get a specific ToyTree
    # TOYTS = ToyTreeSequence(TS)

    # # draw the tree sequence
    # # TOYTS.draw_tree(width=None, height=300, idxs=None, scrollable=True)

    # # draw one tree
    # TOY = TOYTS.at_index(0)
    # print(TOY)
