import numpy as np
import pandas as pd
import pytest

import toytree
from toytree.pcm.src.traits.pic import (
    get_ancestral_states_pic,
    get_phylogenetic_independent_contrasts,
)


def test_standardized_contrast_bifurcation():
    """Standardized contrast equals raw contrast scaled by branch variance."""
    tree = toytree.tree("(a:1,b:1);")
    trait = pd.Series([2.0, 0.0], index=["a", "b"], name="x")
    pics = get_phylogenetic_independent_contrasts(tree, trait=trait)
    assert pics.shape[0] == 1
    raw = float(pics.iloc[0]["contrast_raw"])
    var = float(pics.iloc[0]["contrast_var"])
    std = float(pics.iloc[0]["contrast"])
    assert raw == pytest.approx(2.0, abs=1e-8)
    assert var == pytest.approx(2.0, abs=1e-8)
    assert std == pytest.approx(2.0 / np.sqrt(2.0), abs=1e-8)


def test_polytomy_returns_k_minus_1_rows():
    """A node with k children yields k-1 independent contrasts."""
    tree = toytree.tree("(a:1,b:1,c:1,d:1);")
    trait = pd.Series([0.0, 1.0, 2.0, 3.0], index=["a", "b", "c", "d"], name="x")
    pics = get_phylogenetic_independent_contrasts(tree, trait=trait)
    # root has 4 children -> 3 independent contrasts
    assert pics.shape[0] == 3
    assert (pics["node"] == tree.treenode.idx).all()
    assert sorted(pics["contrast_id"].tolist()) == [0, 1, 2]


def test_trait_must_be_str_or_series():
    """Trait input must be a feature name or a pandas Series."""
    tree = toytree.tree("(a:1,b:1);")
    with pytest.raises(TypeError):
        get_phylogenetic_independent_contrasts(tree, trait=[1.0, 2.0])


def test_ancestral_assignment_follows_node_idx():
    """Ancestral estimates returned by both APIs agree by node index."""
    tree = toytree.tree("((a:1,b:1):1,c:1);")
    trait = pd.Series([2.0, 0.0, 4.0], index=["a", "b", "c"], name="x")
    pics = get_phylogenetic_independent_contrasts(tree, trait=trait)
    anc = get_ancestral_states_pic(tree, trait=trait, inplace=False)
    for nidx in pics["node"].unique():
        pic_anc = float(pics.loc[pics["node"] == nidx, "anc"].iloc[0])
        assert float(anc.loc[nidx]) == pytest.approx(pic_anc, abs=1e-8)


def test_zero_length_branches_are_stable():
    """Zero-length branches return finite PIC and ancestral estimates."""
    tree = toytree.tree("(a:0,b:0);")
    trait = pd.Series([1.0, 2.0], index=["a", "b"], name="x")
    pics = get_phylogenetic_independent_contrasts(tree, trait=trait)
    assert np.isfinite(pics["contrast"]).all()
    anc = get_ancestral_states_pic(tree, trait=trait, inplace=False)
    assert np.isfinite(float(anc.loc[tree.treenode.idx]))
