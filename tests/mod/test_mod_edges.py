"""Tests for random edge scaling."""

import numpy as np
import pytest

import toytree


@pytest.mark.parametrize("alpha", [0.5, 3.0, 10.0])
@pytest.mark.parametrize("inplace", [False, True])
def test_edges_multiplier_is_independent_of_tree_units(alpha, inplace):
    """The same random draw must scale each tree by the same proportion."""
    first = toytree.tree("((a:1,b:1):1,c:2);")
    second = first.mod.edges_scale_to_root_height(20)
    original = first.write()
    first_result = first.mod.edges_multiplier(alpha=alpha, seed=123, inplace=inplace)
    second_result = second.mod.edges_multiplier(alpha=alpha, seed=123, inplace=inplace)
    np.testing.assert_allclose(
        [node.dist for node in second_result],
        10 * np.array([node.dist for node in first_result]),
    )
    if not inplace:
        assert first.write() == original
    else:
        assert first_result is first
        assert second_result is second


def test_edges_multiplier_preserves_mean_root_height():
    """A concentrated gamma draw must remain near the starting tree height."""
    tree = toytree.tree("((a:1,b:1):1,c:2);")
    result = tree.mod.edges_multiplier(alpha=1e6, seed=123)
    assert abs(result.treenode.height - 2) < 0.02
