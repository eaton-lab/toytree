#!/usr/bin/env python

"""Tests for discrete CTMC stochastic character mapping."""

import numpy as np
import pandas as pd
import pytest

import toytree
from toytree.utils import ToytreeError


@pytest.fixture
def tree_data_fit(
    make_unittree,
    simulate_discrete_tips,
    add_feature_from_tip_series,
):
    """Create a reproducible tree, tip data series, and fitted MK model."""
    tree = make_unittree(ntips=7, treeheight=1.0, seed=123)
    data = simulate_discrete_tips(
        tree=tree,
        nstates=2,
        model="ER",
        seed=123,
        as_int=True,
        set_tip_index=True,
    )
    tree = add_feature_from_tip_series(
        tree=tree,
        feature="X",
        series=data,
        default=np.nan,
    )
    fit = toytree.pcm.fit_discrete_ctmc(
        tree=tree,
        data=data,
        nstates=2,
        model="ER",
    )
    return tree, data, fit


def test_feature_name_input_and_schema(tree_data_fit):
    """Accept feature-name input and return expected segment schema."""
    tree, _, fit = tree_data_fit
    out = tree.pcm.simulate_stochastic_map(
        data="X",
        model_fit=fit,
        nreplicates=2,
        seed=1,
    )
    assert isinstance(out, pd.DataFrame)
    for col in [
        "map_id",
        "edge_id",
        "child",
        "parent",
        "state",
        "state_idx",
        "t_start",
        "t_end",
        "duration",
        "time_abs_start",
        "time_abs_end",
    ]:
        assert col in out.columns
    assert sorted(out["map_id"].unique().tolist()) == [0, 1]


def test_series_input(tree_data_fit):
    """Accept direct Series input for tip-level trait states."""
    tree, data, fit = tree_data_fit
    out = toytree.pcm.simulate_stochastic_map(
        tree=tree,
        data=data,
        model_fit=fit,
        nreplicates=1,
        seed=2,
    )
    assert isinstance(out, pd.DataFrame)
    assert out["map_id"].nunique() == 1


def test_duration_sums_match_edge_lengths(tree_data_fit):
    """Ensure segment durations sum to branch lengths per edge/map."""
    tree, _, fit = tree_data_fit
    out = tree.pcm.simulate_stochastic_map(
        data="X",
        model_fit=fit,
        nreplicates=2,
        seed=3,
    )
    dists = tree.get_node_data("dist").to_numpy(dtype=float)
    sums = out.groupby(["map_id", "edge_id"], as_index=False)["duration"].sum()
    edges = tree.get_edges("idx")
    for _, row in sums.iterrows():
        edge_id = int(row["edge_id"])
        child = int(edges[edge_id, 0])
        assert float(row["duration"]) == pytest.approx(float(dists[child]), abs=1e-6)


def test_seed_reproducibility(tree_data_fit):
    """Return identical maps for repeated calls with the same seed."""
    tree, _, fit = tree_data_fit
    a = tree.pcm.simulate_stochastic_map(
        data="X",
        model_fit=fit,
        nreplicates=2,
        seed=11,
    )
    b = tree.pcm.simulate_stochastic_map(
        data="X",
        model_fit=fit,
        nreplicates=2,
        seed=11,
    )
    pd.testing.assert_frame_equal(a.reset_index(drop=True), b.reset_index(drop=True))


def test_uniformization_and_rejection_engines(tree_data_fit):
    """Support both branch-history samplers and preserve schema."""
    tree, _, fit = tree_data_fit
    uni = tree.pcm.simulate_stochastic_map(
        data="X",
        model_fit=fit,
        nreplicates=1,
        seed=22,
        engine="uniformization",
    )
    rej = tree.pcm.simulate_stochastic_map(
        data="X",
        model_fit=fit,
        nreplicates=1,
        seed=22,
        engine="rejection",
    )
    assert isinstance(uni, pd.DataFrame)
    assert isinstance(rej, pd.DataFrame)
    assert set(uni.columns) == set(rej.columns)


def test_return_summary(tree_data_fit):
    """Return summary tables with consistent dwell and segment totals."""
    tree, _, fit = tree_data_fit
    out = tree.pcm.simulate_stochastic_map(
        data="X",
        model_fit=fit,
        nreplicates=3,
        seed=12,
        return_summary=True,
    )
    assert set(out.keys()) == {"segments", "dwell", "transitions"}
    seg = out["segments"]
    dwell = out["dwell"]
    total_seg = float(seg["duration"].sum())
    total_dwell = float(dwell["total_time"].sum())
    assert total_seg == pytest.approx(total_dwell, abs=1e-6)


def test_reject_non_discrete_state_values():
    """Reject non-discrete floating-point state values."""
    tree = toytree.rtree.unittree(ntips=5, treeheight=1.0, seed=2)
    series = pd.Series(
        np.linspace(0.1, 0.5, tree.ntips),
        index=tree.get_tip_labels(),
        name="X",
    )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_stochastic_map(
            data=series,
            model_fit=toytree.pcm.fit_discrete_ctmc(
                tree=tree,
                data=pd.Series(
                    np.where(np.arange(tree.ntips) % 2 == 0, 0, 1),
                    index=tree.get_tip_labels(),
                ),
                nstates=2,
                model="ER",
            ),
        )


def test_invalid_max_branch_attempts(tree_data_fit):
    """Reject invalid non-positive rejection-attempt limits."""
    tree, _, fit = tree_data_fit
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_stochastic_map(
            data="X",
            model_fit=fit,
            max_branch_attempts=0,
        )


def test_invalid_engine(tree_data_fit):
    """Reject unknown engine names."""
    tree, _, fit = tree_data_fit
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_stochastic_map(
            data="X",
            model_fit=fit,
            engine="bad",
        )


def test_requires_model_fit(tree_data_fit):
    """Require a pre-fitted Markov model result object."""
    tree, _, _ = tree_data_fit
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_stochastic_map(data="X", model_fit=None)


def test_accepts_posterior_vector_input(tree_data_fit):
    """Accept posterior vectors as node constraints for simulation."""
    tree, data, fit = tree_data_fit
    result = tree.pcm.infer_ancestral_states_discrete_ctmc(
        data,
        nstates=2,
        model="ER",
    )
    post = result["data"][f"{data.name}_anc_posterior"]
    out = tree.pcm.simulate_stochastic_map(
        data=post,
        model_fit=fit,
        nreplicates=2,
        seed=31,
    )
    assert isinstance(out, pd.DataFrame)
    assert sorted(out["map_id"].unique().tolist()) == [0, 1]


def test_rejects_mixed_scalar_and_vector_input(tree_data_fit):
    """Reject mixing scalar states and posterior vectors in one call."""
    tree, data, fit = tree_data_fit
    mixed = pd.Series(np.nan, index=range(tree.nnodes), dtype=object, name="X")
    mixed.iloc[0] = 0
    mixed.iloc[1] = (0.1, 0.9)
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_stochastic_map(
            data=mixed,
            model_fit=fit,
        )


def test_rejects_invalid_posterior_vectors(tree_data_fit):
    """Reject invalid posterior rows by length/value/sum constraints."""
    tree, _, fit = tree_data_fit
    bad_len = pd.Series(
        [(1.0, 0.0, 0.0)] + [np.nan] * (tree.nnodes - 1),
        index=range(tree.nnodes),
        dtype=object,
        name="X",
    )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_stochastic_map(data=bad_len, model_fit=fit)

    bad_sum = pd.Series(
        [(0.2, 0.2)] + [np.nan] * (tree.nnodes - 1),
        index=range(tree.nnodes),
        dtype=object,
        name="X",
    )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_stochastic_map(data=bad_sum, model_fit=fit)

    bad_neg = pd.Series(
        [(-0.1, 1.1)] + [np.nan] * (tree.nnodes - 1),
        index=range(tree.nnodes),
        dtype=object,
        name="X",
    )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_stochastic_map(data=bad_neg, model_fit=fit)
