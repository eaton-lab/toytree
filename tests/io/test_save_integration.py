#!/usr/bin/env python

"""Integration tests for CairoSVG-backed save() export."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

import toytree

pytest.importorskip("cairosvg")
Image = pytest.importorskip("PIL.Image")

pytestmark = pytest.mark.integration


def _png_stats(path: Path) -> dict[str, object]:
    """Return simple image stats for an exported PNG."""
    with Image.open(path) as image:
        rgba = np.asarray(image.convert("RGBA"))
    opaque = rgba[rgba[..., 3] > 0]
    unique_colors = 0
    if opaque.size:
        unique_colors = np.unique(opaque.reshape(-1, 4), axis=0).shape[0]
    return {
        "shape": rgba.shape,
        "alpha_max": int(rgba[..., 3].max()),
        "alpha_min": int(rgba[..., 3].min()),
        "unique_colors": int(unique_colors),
        "corner": tuple(int(i) for i in rgba[0, 0]),
    }


def _assert_pdf_written(path: Path) -> None:
    """Assert that a non-empty PDF file was written."""
    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 1500


def test_save_png_respects_output_width_and_background_override(
    tmp_path: Path,
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """PNG export respects explicit output width and background override."""
    tree = make_unittree(8, seed=123)
    canvas, _, _ = tree.draw(width=300, height=300)

    transparent_path = tmp_path / "transparent.png"
    white_path = tmp_path / "white.png"

    toytree.save(
        canvas,
        transparent_path,
        backend="cairosvg",
        output_width=900,
        background_color="transparent",
    )
    toytree.save(
        canvas,
        white_path,
        backend="cairosvg",
        output_width=900,
        background_color="white",
    )

    transparent = _png_stats(transparent_path)
    white = _png_stats(white_path)
    assert transparent["shape"][1] == 900
    assert white["shape"][1] == 900
    assert transparent["corner"][3] == 0
    assert white["corner"][:3] == (255, 255, 255)
    assert white["corner"][3] == 255


def test_save_pdf_png_pie_markers_render_filled_exports(tmp_path: Path) -> None:
    """Pie-marker exports render nonblank PDF and PNG outputs."""
    tree = toytree.rtree.coaltree(50, seed=123)
    trait = tree.pcm.simulate_discrete_trait(
        nstates=3,
        model="ER",
        seed=1234,
        tips_only=True,
        relative_rates=3 / tree.treenode.height,
    )
    fit = tree.pcm.infer_ancestral_states_discrete_ctmc(trait, nstates=3, model="ER")
    canvas, axes, _ = tree.draw(layout="d", scale_bar=True, width=700)
    tree.annotate.add_node_pie_markers(
        axes,
        fit["data"]["X_anc_posterior"],
        colors="Set2",
        istroke_width=1,
    )

    pdf_path = tmp_path / "pies.pdf"
    png_path = tmp_path / "pies.png"
    toytree.save(canvas, pdf_path, backend="cairosvg")
    toytree.save(canvas, png_path, backend="cairosvg")

    _assert_pdf_written(pdf_path)
    stats = _png_stats(png_path)
    assert stats["alpha_max"] == 255
    assert stats["unique_colors"] >= 4


def test_save_pdf_png_gradient_edges_render_nonblank(
    tmp_path: Path,
    gradient_canvas_factory: Callable[[], object],
) -> None:
    """Gradient edge annotations export cleanly through CairoSVG."""
    canvas = gradient_canvas_factory()
    pdf_path = tmp_path / "gradient.pdf"
    png_path = tmp_path / "gradient.png"

    toytree.save(canvas, pdf_path, backend="cairosvg")
    toytree.save(canvas, png_path, backend="cairosvg")

    _assert_pdf_written(pdf_path)
    stats = _png_stats(png_path)
    assert stats["alpha_max"] == 255
    assert stats["unique_colors"] >= 10


def test_save_pdf_png_tip_paths_and_labels_render_nonblank(
    tmp_path: Path,
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """Path-heavy annotations and dense labels render to CairoSVG outputs."""
    tree = make_unittree(16, seed=321)
    canvas, axes, _ = tree.draw(
        layout="r",
        width=700,
        tip_labels_align=True,
        tip_labels_style={"font-size": 11},
    )
    ends = np.linspace(5.0, 55.0, tree.ntips)
    spans = np.arange(tree.ntips, dtype=float)
    tree.annotate.add_tip_paths(
        axes,
        spans=spans,
        ends=ends,
        color="royalblue",
        opacity=0.6,
        depth=40,
    )

    pdf_path = tmp_path / "tip-paths.pdf"
    png_path = tmp_path / "tip-paths.png"
    toytree.save(canvas, pdf_path, backend="cairosvg")
    toytree.save(canvas, png_path, backend="cairosvg")

    _assert_pdf_written(pdf_path)
    stats = _png_stats(png_path)
    assert stats["alpha_max"] == 255
    assert stats["unique_colors"] >= 10
