#!/usr/bin/env python

"""
The ToyTreeSequence class generates ToyTree drawings from tree sequences.

Examples
--------
>>> ts = msprime.sim_ancestry()
>>> mts = msprime.sim_mutations()
>>> tts = ToyTreeSequence(tts)

Draw an individual tree w/ mutations.
>>> tts.draw_tree(idx=0, ...)
>>> tts.draw_tree(site=30, ...)

Draw the TreeSequence w/ mutations.
>>> tts.draw_tree_sequence(max_trees=10, chromosome=...)
"""

from typing import Optional, List, Iterable, Union, Dict
import numpy as np
from toytree.utils.tree_sequence.src.draw_tree_seq import TreeSequenceDrawing
import toytree


class ToyTreeSequence:
    """Wrapper around a tskit.trees.TreeSequence.

    Parameters
    ----------
    tree_sequence: tskit.trees.TreeSequence
        A tree sequence object from msprime, tskit, SLiM, etc.
    sample: int or Iterable [int]
        The max number of samples per population to include in a tree.
    seed: int
        A random seed used to sample the samples to include in tree.
    """
    def __init__(
        self, 
        tree_sequence: 'tskit.trees.TreeSequence',
        sample: Union[int,Iterable[int]]=5,
        seed: Optional[int]=None,
        ):

        # store user args
        self.rng = np.random.default_rng(seed)
        self.npopulations = len(list(tree_sequence.populations()))
        if isinstance(sample, int):
            self.sample = [sample] * self.npopulations
        else:
            self.sample = sample
        self.tree_sequence = self._get_subsampled_ts(tree_sequence)
        self._i = 0

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

    def _get_subsampled_ts(self, tree_sequence):
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
        sampled_ts = tree_sequence.simplify(samps)
        return sampled_ts

    def at_index(self, index: int):
        """Return a ToyTree from the indexed order in the tree_sequence."""
        tree = self.tree_sequence.at_index(index)
        return self._get_toytree(tree)

    def at_site(self, pos: int):
        """Return a ToyTree for a position in the tree_sequence."""
        tree = self.tree_sequence.at(pos)
        return self._get_toytree(tree, site=pos)

    def _get_toytree(self, tree: 'tskit.trees.Tree', site: Optional[int]=None):
        """Return a ToyTreeMut for a tree selected by site or index.
        """
        # create the root node
        pdict = tree.get_parent_dict()        
        root_idx = max(pdict.values())
        idx_dict = {root_idx: toytree.TreeNode(name=root_idx, dist=0)}
        idx_dict[root_idx].add_feature("tsidx", root_idx)

        # add all children nodes
        for cidx in pdict:
            pidx = pdict[cidx]
            if pidx in idx_dict:
                pnode = idx_dict[pidx]
            else:
                pnode = toytree.TreeNode(
                    name=str(pidx),
                    dist=tree.branch_length(pidx)
                )
                pnode.add_feature("tsidx", pidx)
                idx_dict[pidx] = pnode
            if cidx in idx_dict:
                cnode = idx_dict[cidx]
            else:
                pop = self.tree_sequence.tables.nodes.population[cidx]
                cnode = toytree.TreeNode(
                    name=f"p{pop}-{cidx}",
                    dist=tree.branch_length(cidx),
                )
                cnode.add_feature("tsidx", cidx)
                idx_dict[cidx] = cnode
            cnode.up = pnode
            pnode.children.append(cnode)

        # wrap TreeNode as a toytree
        ttree = toytree.ToyTree(idx_dict[root_idx])#.ladderize()

        # add mutations as metadata
        if site is not None:
            ttree.mutations = [i for i in tree.mutations() if i.position == site]
        else:
            ttree.mutations = list(tree.mutations())

        # add dict to translate ts idx to toytree idx
        ttree.tsidx_dict = ttree.get_feature_dict("tsidx", None)
        return ttree

    def draw_tree_sequence(
        self,
        start: int=0,
        max_trees: int=10,
        height: int=None,
        width: int=None,
        # show_mutations: bool=True,
        scrollable: bool=True,
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
        tsd = TreeSequenceDrawing(
            trees, breaks, 
            width=width, height=height,
            scrollable=scrollable,
            **kwargs,
        )
        return tsd.canvas, tsd.axes, tsd.marks

    def draw_tree(
        self,
        site: Optional[int]=None,
        idx: Optional[int]=None,
        mutation_size: Union[int, Iterable[int]]=8,
        mutation_style: Dict[str,str]=None,
        mutation_color_palette: Iterable['color']=None,
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
            else toytree.COLORS1)

        # build mutation marker info
        xpos = []
        ypos = []
        titles = []
        colors = []
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
                ypos.append(node.x)
                xpos.append(time)        
            elif mark.layout == "r":
                ypos.append(node.x)
                xpos.append(-time)
            elif mark.layout == "d":
                xpos.append(node.x)
                ypos.append(time)      
            elif mark.layout == "u":
                xpos.append(node.x)
                ypos.append(-time)

            # store color and title for this point
            mtype = int(mut.metadata['mutation_list'][0]['mutation_type'])
            color = colormap[mtype]
            colors.append(color)
            title = (
                f"id: {mut.id}\n"
                f"pos: {mut.position:.0f}\n"
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
    import toyplot.browser

    TREE = toytree.rtree.unittree(10, treeheight=1e5)
    MOD = ipcoal.Model(tree=TREE, Ne=1e4, nsamples=1)
    MOD.sim_loci(5, 2000)
    
    # optional: access the tree sequences directly
    TS = MOD.ts_dict[0]

    # get a specific ToyTree
    TOYTS = ToyTreeSequence(TS)

    # draw the tree sequence
    TOYTS.draw(width=None, height=300, idxs=None, scrollable=True)

    # draw one tree
    TOY = TOYTS.at_index(0)
    TOY.draw()
