#!/usr/bin/env python

"""Tests for `toytree.io.src.save`."""

from __future__ import annotations

import xml.etree.ElementTree as xml
from collections.abc import Callable
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

import toytree
from toytree.io.src.save import _canvas_has_toytree_linear_gradients, save


def _make_svg_root(*, path_fill: bool = False, gradient: bool = False) -> xml.Element:
    """Return a minimal SVG root for renderer-selection tests."""
    root = xml.fromstring(
        "<svg width='10px' height='10px' "
        "style='background-color:transparent;border-style:none;border-width:0'/>"
    )
    if gradient:
        defs = xml.SubElement(root, "defs")
        xml.SubElement(defs, "linearGradient", id="grad")
    if path_fill:
        xml.SubElement(
            root,
            "path",
            d="M 0 0 L 1 0 L 0 1 Z",
            style="fill:rgb(255,0,0);fill-opacity:1",
        )
    return root


def test_detector_false_on_plain_canvas(
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """Detector returns False for canvases without gradient edge marks."""
    tree = make_unittree(6, seed=123)
    canvas, _, _ = tree.draw()
    assert not _canvas_has_toytree_linear_gradients(canvas)


def test_detector_true_on_gradient_edge_canvas(
    gradient_canvas_factory: Callable[[], object],
) -> None:
    """Detector returns True when a gradient edge mark is present."""
    canvas = gradient_canvas_factory()
    assert _canvas_has_toytree_linear_gradients(canvas)


@patch("toyplot.svg.render")
def test_save_svg_allows_gradient_canvas(
    mock_render,
    gradient_canvas_factory: Callable[[], object],
) -> None:
    """SVG export remains allowed for canvases with gradients."""
    canvas = gradient_canvas_factory()
    save(canvas, "tmp-output.svg")
    mock_render.assert_called_once()


@patch("toyplot.html.render")
def test_save_html_allows_gradient_canvas(
    mock_render,
    gradient_canvas_factory: Callable[[], object],
) -> None:
    """HTML export remains allowed for canvases with gradients."""
    canvas = gradient_canvas_factory()
    save(canvas, "tmp-output.html")
    mock_render.assert_called_once()


def test_save_pdf_auto_uses_cairosvg_and_passes_options(
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """Auto backend prefers CairoSVG for PDF export when available."""
    tree = make_unittree(6, seed=123)
    canvas, _, _ = tree.draw()
    mock_cairo = SimpleNamespace(svg2pdf=Mock(), svg2png=Mock())

    with (
        patch("toytree.io.src.save._import_cairosvg", return_value=mock_cairo),
        patch("toytree.io.src.save._render_svg_root", return_value=_make_svg_root()),
    ):
        save(
            canvas,
            "tmp-output.PDF",
            dpi=300,
            scale=2.0,
            background_color="white",
            output_width=1200,
            output_height=800,
        )

    mock_cairo.svg2pdf.assert_called_once()
    kwargs = mock_cairo.svg2pdf.call_args.kwargs
    assert kwargs["write_to"] == "tmp-output.PDF"
    assert kwargs["dpi"] == 300
    assert kwargs["scale"] == 2.0
    assert kwargs["background_color"] == "white"
    assert kwargs["output_width"] == 1200
    assert kwargs["output_height"] == 800
    assert kwargs["bytestring"].startswith(b"<svg")


def test_save_png_explicit_cairosvg_missing_raises(
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """Explicit CairoSVG backend raises clearly if CairoSVG is unavailable."""
    tree = make_unittree(6, seed=123)
    canvas, _, _ = tree.draw()
    with patch("toytree.io.src.save._import_cairosvg", return_value=None):
        with pytest.raises(ImportError, match="backend='cairosvg'"):
            save(canvas, "tmp-output.png", backend="cairosvg")


@patch("toyplot.pdf.render")
def test_save_pdf_auto_falls_back_to_reportlab_and_warns(
    mock_render,
    gradient_canvas_factory: Callable[[], object],
    capsys,
) -> None:
    """Auto PDF export falls back to ReportLab with a clear warning."""
    canvas = gradient_canvas_factory()
    with patch("toytree.io.src.save._import_cairosvg", return_value=None):
        save(canvas, "tmp-output.pdf")

    err = capsys.readouterr().err
    assert "falling back to legacy reportlab PDF export" in err
    assert "linear gradients" in err
    mock_render.assert_called_once_with(canvas, "tmp-output.pdf")


@patch("toyplot.pdf.render")
def test_save_pdf_reportlab_warns_on_filled_paths(
    mock_render,
    capsys,
) -> None:
    """Explicit ReportLab export warns when SVG contains filled paths."""
    tree = toytree.rtree.coaltree(20, seed=123)
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

    save(canvas, "tmp-output.pdf", backend="reportlab")

    err = capsys.readouterr().err
    assert "filled paths" in err
    assert "backend='cairosvg'" in err
    mock_render.assert_called_once_with(canvas, "tmp-output.pdf")


@patch("toyplot.svg.render")
def test_save_svg_temporary_background_override(
    mock_render,
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """SVG export can temporarily override canvas background color."""
    tree = make_unittree(6, seed=123)
    canvas, _, _ = tree.draw()
    canvas.style["background-color"] = "white"

    def _assert_black(arg_canvas, _path) -> None:
        assert arg_canvas.style["background-color"] == "black"

    mock_render.side_effect = _assert_black
    save(canvas, "tmp-output.svg", background_color="black")
    assert canvas.style["background-color"] == "white"
    mock_render.assert_called_once()


@patch("toyplot.pdf.render")
def test_save_pdf_reportlab_background_override_is_temporary(
    mock_render,
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """Legacy ReportLab export restores background after render."""
    tree = make_unittree(6, seed=123)
    canvas, _, _ = tree.draw()
    canvas.style["background-color"] = "white"

    def _assert_blue(arg_canvas, _path) -> None:
        assert arg_canvas.style["background-color"] == "blue"

    mock_render.side_effect = _assert_blue
    save(canvas, "tmp-output.pdf", backend="reportlab", background_color="blue")
    assert canvas.style["background-color"] == "white"
    mock_render.assert_called_once()


def test_save_svg_rejects_non_auto_backend(
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """Backend overrides are rejected for HTML and SVG outputs."""
    tree = make_unittree(6, seed=123)
    canvas, _, _ = tree.draw()
    with pytest.raises(ValueError, match="only applies to PDF and PNG"):
        save(canvas, "tmp-output.svg", backend="cairosvg")


def test_save_rejects_unknown_backend(
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """Unknown export backend names raise a clear error."""
    tree = make_unittree(6, seed=123)
    canvas, _, _ = tree.draw()
    with pytest.raises(ValueError, match="Unknown backend"):
        save(canvas, "tmp-output.pdf", backend="bogus")


@patch("toyplot.html.render")
def test_save_without_suffix_defaults_to_html(
    mock_render,
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """Missing filename suffix defaults to .html output."""
    tree = make_unittree(6, seed=123)
    canvas, _, _ = tree.draw()
    save(canvas, "tmp-output")
    mock_render.assert_called_once_with(canvas, "tmp-output.html")


def test_save_raises_type_error_on_non_canvas_input() -> None:
    """Invalid canvas-like inputs raise a clear TypeError."""
    with pytest.raises(TypeError, match="Canvas-like object"):
        save(canvas={}, path="tmp-output.svg")
