#!/usr/bin/env python

"""Tests for SVG tree-edge path construction."""

from __future__ import annotations

import re

import numpy as np
import toyplot.html

import toytree
from toytree.drawing.src.path_edges import _get_edge_data, get_tree_edge_svg_paths


def test_circular_phylogram_svg_sweep_matches_shortest_delta_on_wrapped_fan() -> None:
    """Wrapped fan seams should not flip SVG arc direction."""
    tree = toytree.rtree.unittree(12, seed=123).ladderize()
    canvas, axes, mark = tree.draw(layout="c270-90", tip_labels=False)
    toyplot.html.render(canvas)

    _, _, _, radians, _, _ = _get_edge_data(axes, mark, space="pixel")
    paths, keys = get_tree_edge_svg_paths(axes, mark)

    for idx, key in enumerate(keys):
        cidx, pidx = mark.etable[idx]
        dtheta = (radians[pidx] - radians[cidx] + np.pi) % (2 * np.pi) - np.pi
        expected_sweep = int(dtheta < 0)
        match = re.search(r"A [^ ]+ [^ ]+ 0 0 ([01]) ", paths[idx])
        assert match is not None
        observed_sweep = int(match.group(1))
        assert observed_sweep == expected_sweep, key
