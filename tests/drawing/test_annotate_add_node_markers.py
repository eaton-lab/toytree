#!/usr/bin/env python

"""Regression tests for annotate.add_node_markers."""

import numpy as np
import toyplot.html

import toytree


def test_add_node_markers_regression_after_edge_labels() -> None:
    """add_node_markers should not fail after adding edge labels."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    canvas, axes, _ = tree.draw(tip_labels=True)
    tree.annotate.add_edge_labels(
        axes, "idx", style={"fill": "red"}, font_size=14, mask=(1, 1, 1)
    )
    mark = tree.annotate.add_node_markers(axes, "o", style={"fill": "red"})
    expected = tree.get_node_mask(show_tips=False, show_internal=True, show_root=True)
    assert mark.ntable.shape[0] == int(expected.sum())
    toyplot.html.render(canvas)


def test_add_node_markers_accepts_array_inputs() -> None:
    """Per-node arrays should map directly onto marker attributes."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    canvas, axes, _ = tree.draw(layout="r")
    sizes = np.arange(tree.nnodes, dtype=float) + 1.0
    opacities = np.linspace(0.1, 0.9, tree.nnodes)
    colors = np.array(["red"] * tree.nnodes, dtype=object)
    mark = tree.annotate.add_node_markers(
        axes,
        marker="o",
        size=sizes,
        opacity=opacities,
        color=colors,
        mask=False,
    )
    assert mark.ntable.shape[0] == tree.nnodes
    assert np.allclose(mark.sizes, sizes)
    assert np.allclose(mark.opacity, opacities)
    toyplot.html.render(canvas)


def test_add_node_markers_tuple_mask_counts_are_correct() -> None:
    """Tuple masks should select expected node groups."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_node_markers(axes, mask=(1, 0, 0))
    assert mark.ntable.shape[0] == tree.ntips
    toyplot.html.render(canvas)


def test_add_node_markers_renders_on_circular_layout() -> None:
    """Node markers should render cleanly on circular layouts."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    canvas, axes, _ = tree.draw(layout="c0-180")
    mark = tree.annotate.add_node_markers(
        axes,
        marker="o",
        size=8,
        color="blue",
        xshift=2,
        yshift=-2,
        mask=False,
    )
    assert mark.ntable.shape[0] == tree.nnodes
    toyplot.html.render(canvas)
