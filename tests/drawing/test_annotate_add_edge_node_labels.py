#!/usr/bin/env python

"""Render smoke tests for edge and node label annotations."""

import numpy as np
import toyplot.html

import toytree


def test_add_edge_labels_renders_with_default_style() -> None:
    """Edge labels should render when default text stroke is unset."""
    tree = toytree.rtree.unittree(ntips=8, seed=123)
    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_edge_labels(axes, labels="idx")
    assert mark is not None
    toyplot.html.render(canvas)


def test_add_node_labels_renders_with_default_style() -> None:
    """Node labels should render when default text stroke is unset."""
    tree = toytree.rtree.unittree(ntips=8, seed=123)
    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_node_labels(axes, labels="idx")
    assert mark is not None
    toyplot.html.render(canvas)


def test_add_edge_labels_show_all_includes_all_rooted_edges() -> None:
    """mask=False should show all plotted edges, including both root-adjacent."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_edge_labels(axes, labels="idx", mask=False)
    assert len(mark._table["text"]) == tree.nnodes - 1
    toyplot.html.render(canvas)


def test_add_edge_labels_wrap_root_edge_true_maps_root_value() -> None:
    """Root value should be copied to root-adjacent edges when wrapping."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    values = np.arange(tree.nnodes, dtype=int)
    values[-1] = 999
    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_edge_labels(
        axes,
        labels=values,
        mask=False,
        wrap_root_edge=True,
    )
    labels = np.asarray(mark._table["text"], dtype=object)
    root_child_idxs = [node.idx for node in tree[-1].children]
    for idx in root_child_idxs:
        assert labels[idx] == "999"
    toyplot.html.render(canvas)


def test_add_edge_labels_wrap_root_edge_false_keeps_split_values() -> None:
    """Root-adjacent edges should keep child-edge values when not wrapping."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    values = np.arange(tree.nnodes, dtype=int)
    values[-1] = 999
    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_edge_labels(
        axes,
        labels=values,
        mask=False,
        wrap_root_edge=False,
    )
    labels = np.asarray(mark._table["text"], dtype=object)
    for node in tree[-1].children:
        assert labels[node.idx] == str(node.idx)
    toyplot.html.render(canvas)


def test_add_edge_labels_default_mask_uses_root_override_when_wrapped() -> None:
    """mask=None should include root-adjacent edges when wrap_root_edge=True."""
    tree = toytree.rtree.imbtree(ntips=10, seed=123)
    nedges = tree.nnodes - 1
    root_child_idxs = np.array([i.idx for i in tree[-1].children], dtype=int)
    node_mask = tree.get_node_mask(show_tips=False, show_internal=True, show_root=True)
    expected = node_mask[:nedges].copy()
    expected[root_child_idxs] = bool(node_mask[tree.nnodes - 1])

    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_edge_labels(
        axes,
        labels="idx",
        mask=None,
        wrap_root_edge=True,
    )
    assert len(mark._table["text"]) == int(expected.sum())
    toyplot.html.render(canvas)


def test_add_edge_labels_tuple_mask_root_bit_overrides_root_children() -> None:
    """show_root should control all root-adjacent edges when wrapping is enabled."""
    tree = toytree.rtree.imbtree(ntips=10, seed=123)
    nedges = tree.nnodes - 1
    root_child_idxs = np.array([i.idx for i in tree[-1].children], dtype=int)

    node_mask = tree.get_node_mask(show_tips=False, show_internal=True, show_root=False)
    expected = node_mask[:nedges].copy()
    expected[root_child_idxs] = False

    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_edge_labels(
        axes,
        labels="idx",
        mask=(0, 1, 0),
        wrap_root_edge=True,
    )
    assert len(mark._table["text"]) == int(expected.sum())
    toyplot.html.render(canvas)


def test_add_edge_labels_accepts_explicit_edge_sequence() -> None:
    """Labels of length nnodes-1 should be accepted as edge-ordered values."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    labels = np.arange(tree.nnodes - 1, dtype=int)
    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_edge_labels(axes, labels=labels, mask=False)
    got = np.asarray(mark._table["text"], dtype=object)
    assert len(got) == tree.nnodes - 1
    assert got[0] == "0"
    assert got[-1] == str(tree.nnodes - 2)
    toyplot.html.render(canvas)


def test_add_edge_labels_accepts_explicit_edge_mask() -> None:
    """A boolean edge mask of len(nnodes-1) should be accepted directly."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    mask = np.ones(tree.nnodes - 1, dtype=bool)
    mask[::2] = False
    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_edge_labels(axes, labels="idx", mask=mask)
    assert len(mark._table["text"]) == int(mask.sum())
    toyplot.html.render(canvas)


def test_add_edge_markers_show_all_includes_all_rooted_edges() -> None:
    """Edge markers should include both root-adjacent plotted edges."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_edge_markers(axes, mask=False)
    assert mark.ntable.shape[0] == tree.nnodes - 1
    toyplot.html.render(canvas)


def test_add_edge_markers_accepts_explicit_edge_sequence_size() -> None:
    """Size arrays of len(nnodes-1) should map directly to plotted edges."""
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    sizes = np.arange(tree.nnodes - 1, dtype=float) + 1
    canvas, axes, _ = tree.draw(layout="r")
    mark = tree.annotate.add_edge_markers(
        axes,
        mask=False,
        size=sizes,
    )
    assert np.allclose(mark.sizes, sizes)
    toyplot.html.render(canvas)
