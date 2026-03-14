#!/usr/bin/env python

"""Render hook for TreeDomainMark (intentionally emits no SVG)."""

from __future__ import annotations

import functools

import toyplot
from multipledispatch import dispatch

from toytree.drawing.src.mark_tree_domain import (
    HostDomainMark,
    HostVisibleDomainMark,
    TreeDomainMark,
)

dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)


@dispatch(toyplot.coordinates.Cartesian, TreeDomainMark, toyplot.html.RenderContext)
def _render(axes, mark, context):
    """No-op renderer: mark exists only to contribute domain/extents."""
    _ = (axes, mark, context)
    return


@dispatch(toyplot.coordinates.Cartesian, HostDomainMark, toyplot.html.RenderContext)
def _render(axes, mark, context):
    """No-op renderer: mark exists only to contribute domain/extents."""
    _ = (axes, mark, context)
    return


@dispatch(
    toyplot.coordinates.Cartesian,
    HostVisibleDomainMark,
    toyplot.html.RenderContext,
)
def _render(axes, mark, context):
    """No-op renderer: mark exists only to contribute domain/extents."""
    _ = (axes, mark, context)
    return
