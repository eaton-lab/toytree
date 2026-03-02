#!/usr/bin/env python

"""Tests for `toytree.io.src.save`."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import patch

import pytest

import toytree
from toytree.io.src.save import _canvas_has_toytree_linear_gradients, save


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


def test_save_pdf_raises_on_gradient_canvas(
    gradient_canvas_factory: Callable[[], object],
) -> None:
    """PDF export raises on canvases with toytree linear gradients."""
    canvas = gradient_canvas_factory()
    with pytest.raises(ValueError) as exc:
        save(canvas, "tmp-output.pdf")

    msg = str(exc.value)
    assert "linearGradients" in msg
    assert "HTML and SVG" in msg
    assert "Inkscape or Illustrator" in msg


def test_save_png_raises_on_gradient_canvas(
    gradient_canvas_factory: Callable[[], object],
) -> None:
    """PNG export raises on canvases with toytree linear gradients."""
    canvas = gradient_canvas_factory()
    with pytest.raises(ValueError):
        save(canvas, "tmp-output.png")


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


@patch("toyplot.pdf.render")
def test_save_pdf_allows_non_gradient_canvas(
    mock_render,
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """PDF export is allowed when no gradient edge mark is present."""
    tree = make_unittree(6, seed=123)
    canvas, _, _ = tree.draw()
    save(canvas, "tmp-output.pdf")
    mock_render.assert_called_once()


@patch("toyplot.png.render")
def test_save_png_allows_non_gradient_canvas(
    mock_render,
    make_unittree: Callable[..., toytree.ToyTree],
) -> None:
    """PNG export is allowed when no gradient edge mark is present."""
    tree = make_unittree(6, seed=123)
    canvas, _, _ = tree.draw()
    save(canvas, "tmp-output.png")
    mock_render.assert_called_once()
