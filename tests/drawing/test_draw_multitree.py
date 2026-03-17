#!/usr/bin/env python

"""Tests for multitree drawing style selection behavior."""

from __future__ import annotations

import xml.etree.ElementTree as xml

import pytest
import toyplot.html

import toytree
from toytree.annotate import get_toytree_scale_cartesian


def _make_mtree(ntrees: int) -> toytree.MultiTree:
    """Return a deterministic multitree for drawing tests."""
    trees = [toytree.rtree.unittree(6, seed=idx) for idx in range(ntrees)]
    return toytree.mtree(trees)


def _make_long_label_mtree(ntrees: int) -> toytree.MultiTree:
    """Return a multitree whose tip labels force wide rendered extents."""
    trees = [toytree.rtree.unittree(6, seed=idx) for idx in range(ntrees)]
    for tidx, tree in enumerate(trees):
        for nidx in range(tree.ntips):
            tree[nidx].name = f"tree{tidx}_tip{nidx}_" + ("longlabel" * 12)
    return toytree.mtree(trees)


def _canvas_size(canvas) -> tuple[float, float]:
    """Return canvas width and height as plain floats."""
    return float(canvas.width), float(canvas.height)


def _projection_span(axis, which: str) -> float:
    """Return finalized host-axis domain span on one axis."""
    axis._finalize()
    proj = axis._x_projection if which == "x" else axis._y_projection
    return float(proj._segments[-1].domain.max - proj._segments[0].domain.min)


def test_mtree_draw_accepts_tree_style_u() -> None:
    """Passing ``tree_style='u'`` should resolve layout without error."""
    mtree = _make_mtree(2)
    _, _, marks = mtree.draw(
        shape=(1, 2),
        tree_style="u",
        tip_labels=False,
    )
    assert len(marks) == 2
    assert all(mark.layout == "unrooted" for mark in marks)


def test_mtree_draw_preserves_requested_shape_for_partial_grid() -> None:
    """Requested grid shape should not collapse when fewer trees are drawn."""
    mtree = _make_mtree(2)
    _, axes, marks = mtree.draw(shape=(2, 2), tip_labels=False)

    assert len(axes) == 4
    assert len(marks) == 2
    assert axes[2].x.show is False
    assert axes[2].y.show is False
    assert axes[3].x.show is False
    assert axes[3].y.show is False


def test_mtree_draw_shared_axes_handles_partial_grid() -> None:
    """Shared-axis post-processing should skip unused cells without crashing."""
    mtree = _make_mtree(5)
    _, axes, marks = mtree.draw(shape=(2, 3), shared_axes=True, tip_labels=False)

    assert len(axes) == 6
    assert len(marks) == 5
    assert axes[5].x.show is False
    assert axes[5].y.show is False


def test_mtree_draw_accepts_empty_idxs_selection() -> None:
    """An explicit empty selection should return a blank grid and no marks."""
    mtree = _make_mtree(3)
    _, axes, marks = mtree.draw(shape=(1, 4), idxs=[])

    assert len(axes) == 4
    assert marks == []
    assert all(axis.x.show is False and axis.y.show is False for axis in axes)


@pytest.mark.parametrize(
    "shape",
    [
        (0, 2),
        (2, 0),
        (1,),
        (1, 2, 3),
    ],
)
def test_mtree_draw_rejects_invalid_shape(shape) -> None:
    """Shape must be exactly two positive integers."""
    mtree = _make_mtree(2)
    with pytest.raises(toytree.ToytreeError, match="shape"):
        mtree.draw(shape=shape)


def test_mtree_draw_rejects_out_of_range_idxs() -> None:
    """Invalid tree indices should raise ToytreeError with a clear message."""
    mtree = _make_mtree(2)
    with pytest.raises(toytree.ToytreeError, match="out-of-range"):
        mtree.draw(shape=(1, 2), idxs=[10])


def test_mtree_draw_tip_labels_style_defaults_do_not_mutate_input(capsys) -> None:
    """Caller tip-label style dict should not be modified in place."""
    mtree = _make_mtree(2)
    style = {"fill": "red"}

    _, _, marks = mtree.draw(shape=(1, 2), tip_labels_style=style)
    captured = capsys.readouterr()

    assert len(marks) == 2
    assert style == {"fill": "red"}
    assert "Unrecognized keyword arguments" not in captured.err
    assert "font-size" not in captured.err


def test_mtree_draw_removed_shrink_kwarg_warns_and_ignores(capsys) -> None:
    """Removed draw kwargs should be warned and ignored once per multitree draw."""
    mtree = _make_mtree(2)

    _, _, marks = mtree.draw(shape=(1, 2), tip_labels=False, shrink=10)
    captured = capsys.readouterr()

    assert len(marks) == 2
    assert (
        captured.err.count(
            "Unrecognized keyword arguments passed to draw() were ignored:"
        )
        == 1
    )
    assert "shrink" in captured.err


def test_mtree_draw_broadcasts_scalar_label_to_rendered_trees() -> None:
    """A scalar label should apply to rendered trees only, not blank cells."""
    mtree = _make_mtree(5)
    _, axes, marks = mtree.draw(shape=(2, 3), label="tree", tip_labels=False)

    assert len(marks) == 5
    assert [axes[idx].label.text for idx in range(5)] == ["tree"] * 5
    assert axes[5].label.text is None


def test_mtree_draw_applies_label_sequence_in_render_order() -> None:
    """Sequence labels should map by rendered-tree order, not grid-cell count."""
    mtree = _make_mtree(5)
    labels = ["a", "b", "c", "d", "e"]
    _, axes, _ = mtree.draw(shape=(2, 3), label=labels, tip_labels=False)

    assert [axes[idx].label.text for idx in range(5)] == labels
    assert axes[5].label.text is None


def test_mtree_draw_rejects_label_sequence_for_blank_cells() -> None:
    """Label sequences must match rendered trees rather than total grid cells."""
    mtree = _make_mtree(5)
    with pytest.raises(toytree.ToytreeError, match="label sequence length"):
        mtree.draw(
            shape=(2, 3),
            label=["a", "b", "c", "d", "e", "f"],
            tip_labels=False,
        )


def test_mtree_draw_shared_axes_scale_bar_false_keeps_scale_axes_hidden() -> None:
    """Shared axes should equalize depth without creating a tree scale bar."""
    tree1 = toytree.tree("((a:10,b:1):2,(c:3,d:4):5);")
    tree2 = toytree.tree("((a:2,b:2):2,(c:2,d:2):2);")
    mtree = toytree.mtree([tree1, tree2])

    _, axes, _ = mtree.draw(
        shape=(1, 2),
        layout="r",
        shared_axes=True,
        scale_bar=False,
        tip_labels=False,
    )

    scale_axes = get_toytree_scale_cartesian(axes[0], create=False)
    assert scale_axes is None

    spans = [_projection_span(axis, "x") for axis in axes]
    assert spans[0] == pytest.approx(spans[1], rel=1e-6)


def test_mtree_draw_shared_axes_uses_rendered_depth_when_edge_lengths_disabled() -> (
    None
):
    """Shared depth should follow rendered unit depths, not raw tree heights."""
    tree1 = toytree.tree("((a:10,b:1):2,(c:3,d:4):5);")
    tree2 = toytree.tree("((a:2,b:2):2,(c:2,d:2):2);")
    mtree = toytree.mtree([tree1, tree2])

    _, axes, _ = mtree.draw(
        shape=(1, 2),
        layout="r",
        shared_axes=True,
        scale_bar=False,
        use_edge_lengths=False,
        tip_labels=False,
    )

    spans = [_projection_span(axis, "x") for axis in axes]
    assert spans[0] == pytest.approx(spans[1], rel=1e-6)
    assert 1.5 < spans[0] < 3.0


@pytest.mark.parametrize("layout", ["c", "unrooted"])
def test_mtree_draw_shared_axes_rejects_non_linear_layouts(layout: str) -> None:
    """Shared axes should only be available on linear layouts."""
    mtree = _make_mtree(2)
    with pytest.raises(toytree.ToytreeError, match="linear layouts"):
        mtree.draw(shape=(1, 2), layout=layout, shared_axes=True, tip_labels=False)


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"width": 0}, "width"),
        ({"height": -1}, "height"),
        ({"padding": -1}, "padding"),
        ({"padding": True}, "padding"),
        ({"margin": True}, "margin"),
        ({"margin": (1, 2, 3)}, "margin"),
        ({"margin": (1, 2, True, 4)}, "margin"),
        ({"margin": "bad"}, "margin"),
    ],
)
def test_mtree_draw_rejects_invalid_canvas_or_margin_inputs(kwargs, match) -> None:
    """Width, height, and margin should fail with ToytreeError."""
    mtree = _make_mtree(2)
    with pytest.raises(toytree.ToytreeError, match=match):
        mtree.draw(shape=(1, 2), tip_labels=False, **kwargs)


def test_mtree_draw_shared_axes_does_not_render_transparent_point_spacers() -> None:
    """Shared-axis depth padding should not introduce toyplot Point marks."""
    mtree = _make_mtree(2)
    canvas, _, _ = mtree.draw(
        shape=(1, 2),
        layout="r",
        shared_axes=True,
        scale_bar=False,
        tip_labels=False,
    )

    text = xml.tostring(toyplot.html.render(canvas), encoding="unicode")
    assert "toyplot-mark-Point" not in text


def test_mtree_draw_fixed_order_true_single_tree_skips_consensus(
    monkeypatch,
) -> None:
    """A single rendered tree should not infer consensus just to fix tip order."""
    mtree = _make_mtree(3)

    def fail(*args, **kwargs):
        raise AssertionError("consensus tree should not be called")

    monkeypatch.setattr(toytree.MultiTree, "get_consensus_tree", fail)

    _, _, marks = mtree.draw(
        shape=(1, 2),
        idxs=[0],
        fixed_order=True,
        tip_labels=False,
    )
    assert len(marks) == 1


def test_mtree_draw_explicit_fixed_order_sequence_skips_consensus(
    monkeypatch,
) -> None:
    """Explicit fixed-order sequences should bypass consensus inference."""
    mtree = _make_mtree(3)

    def fail(*args, **kwargs):
        raise AssertionError("consensus tree should not be called")

    monkeypatch.setattr(toytree.MultiTree, "get_consensus_tree", fail)

    _, _, marks = mtree.draw(
        shape=(1, 2),
        fixed_order=mtree[0].get_tip_labels(),
        tip_labels=False,
    )
    assert len(marks) == 2


def test_mtree_draw_fixed_order_true_reuses_cached_consensus_order(
    monkeypatch,
) -> None:
    """Repeated fixed-order draws should reuse cached inferred tip order."""
    mtree = _make_mtree(3)
    count = {"calls": 0}

    def fake(self, *args, **kwargs):
        count["calls"] += 1
        return self.treelist[0]

    monkeypatch.setattr(toytree.MultiTree, "get_consensus_tree", fake)

    mtree.draw(shape=(1, 2), fixed_order=True, tip_labels=False)
    mtree.draw(shape=(1, 2), fixed_order=True, tip_labels=False)

    assert count["calls"] == 1


def test_mtree_draw_auto_size_keeps_compact_rooted_default() -> None:
    """Short rooted trees should keep the compact baseline grid size."""
    mtree = _make_mtree(4)

    canvas, _, _ = mtree.draw(shape=(2, 2))

    assert _canvas_size(canvas) == pytest.approx((450.0, 500.0))


def test_mtree_draw_auto_size_expands_for_long_tip_labels() -> None:
    """Long tip labels should widen rooted grids beyond the compact baseline."""
    mtree = _make_long_label_mtree(4)

    canvas, _, _ = mtree.draw(shape=(2, 2))

    assert _canvas_size(canvas) == pytest.approx((800.0, 500.0))


def test_mtree_draw_auto_size_expands_circular_grids() -> None:
    """Circular layouts should default to larger square-ish grid cells."""
    mtree = _make_mtree(4)

    canvas, _, _ = mtree.draw(shape=(2, 2), layout="c", tip_labels=False)

    assert _canvas_size(canvas) == pytest.approx((700.0, 700.0))


def test_mtree_draw_auto_size_respects_explicit_width() -> None:
    """A user width override should preserve width and auto-size height only."""
    mtree = _make_long_label_mtree(4)

    canvas, _, _ = mtree.draw(shape=(2, 2), width=900)

    assert _canvas_size(canvas) == pytest.approx((900.0, 500.0))


def test_mtree_draw_auto_size_respects_explicit_height() -> None:
    """A user height override should preserve height and auto-size width only."""
    mtree = _make_long_label_mtree(4)

    canvas, _, _ = mtree.draw(shape=(2, 2), height=600)

    assert _canvas_size(canvas) == pytest.approx((800.0, 600.0))


def test_mtree_draw_auto_size_applies_width_soft_cap() -> None:
    """Long wide grids should soft-cap auto width without shrinking below base."""
    mtree = _make_long_label_mtree(6)

    canvas, _, _ = mtree.draw(shape=(1, 6))

    assert _canvas_size(canvas) == pytest.approx((1600.0, 250.0))


def test_mtree_draw_auto_size_applies_height_soft_cap() -> None:
    """Tall circular grids should soft-cap auto height for rendered trees."""
    mtree = _make_mtree(4)

    canvas, _, _ = mtree.draw(shape=(4, 1), layout="c", tip_labels=False)

    assert _canvas_size(canvas) == pytest.approx((350.0, 1200.0))


def test_mtree_draw_auto_size_ignores_blank_cells_when_sizing_marks() -> None:
    """Per-cell sizing should be based on rendered trees rather than blank cells."""
    mtree = _make_long_label_mtree(2)

    canvas1, _, _ = mtree.draw(shape=(1, 2))
    canvas2, _, _ = mtree.draw(shape=(1, 4), idxs=[0, 1])

    width1, _ = _canvas_size(canvas1)
    width2, _ = _canvas_size(canvas2)
    assert width1 / 2.0 == pytest.approx(width2 / 4.0)
