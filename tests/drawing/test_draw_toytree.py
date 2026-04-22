#!/usr/bin/env python

"""Tests for draw_toytree argument handling and layout dispatch."""

from __future__ import annotations

import toytree


def test_draw_unknown_extra_kwargs_warn_and_ignore(capsys) -> None:
    """Unknown draw kwargs should be warned and ignored."""
    tree = toytree.rtree.unittree(8, seed=1)
    _, _, mark = tree.draw(not_a_draw_kwarg=True)
    captured = capsys.readouterr()

    assert mark is not None
    assert (
        "Unrecognized keyword arguments passed to draw() were ignored:" in captured.err
    )
    assert "not_a_draw_kwarg" in captured.err


def test_draw_removed_shrink_kwarg_warns_and_ignores(capsys) -> None:
    """Removed draw kwargs should follow the generic unsupported-arg warning path."""
    tree = toytree.rtree.unittree(8, seed=11)
    _, _, mark = tree.draw(shrink=10)
    captured = capsys.readouterr()

    assert mark is not None
    assert (
        "Unrecognized keyword arguments passed to draw() were ignored:" in captured.err
    )
    assert "shrink" in captured.err


def test_draw_prefers_tree_style_over_ts_alias() -> None:
    """Explicit tree_style should win over ts shorthand."""
    tree = toytree.rtree.unittree(8, seed=2)
    _, _, mark = tree.draw(tree_style="s", ts="u")
    assert mark.layout == "r"


def test_tree_has_no_stored_style_attribute() -> None:
    """ToyTree should no longer store persistent draw style state."""
    tree = toytree.rtree.unittree(8, seed=20)

    try:
        _ = tree.style
    except AttributeError:
        pass
    else:
        raise AssertionError("ToyTree.style should not exist.")


def test_draw_layout_none_keeps_base_style_layout() -> None:
    """layout=None should keep the base style layout."""
    tree = toytree.rtree.unittree(8, seed=3)
    _, _, mark = tree.draw(layout=None)
    assert mark.layout == "r"


def test_draw_layout_u_is_up_not_unrooted() -> None:
    """layout='u' should select the up-facing linear layout."""
    tree = toytree.rtree.unittree(8, seed=4)
    _, _, mark = tree.draw(layout="u")
    assert mark.layout == "u"


def test_draw_unrooted_layout_from_un_prefix_and_unmatched() -> None:
    """un-prefixed and unmatched layouts should map to unrooted."""
    tree = toytree.rtree.unittree(8, seed=5)
    _, _, mark_un = tree.draw(layout="un")
    _, _, mark_other = tree.draw(layout="layout-not-recognized")
    assert mark_un.layout == "unrooted"
    assert mark_other.layout == "unrooted"
