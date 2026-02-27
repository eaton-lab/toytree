#!/usr/bin/env python

"""Wrapper for simulating genealogies with optional ipcoal dependency."""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Mapping
from typing import Any

import pandas as pd

import toytree
from toytree import MultiTree, ToyTree
from toytree.utils import ToytreeError

__all__ = ["ipcoal_sim_trees"]


def _filter_supported_kwargs(func: Any, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Return kwargs accepted by func, preserving explicit user values.

    This allows compatibility across ipcoal versions where some keyword
    names may differ, while still exposing an explicit user-facing API here.
    """
    sig = inspect.signature(func)
    params = sig.parameters.values()
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params):
        return kwargs
    accepted = {p.name for p in params}
    return {key: val for key, val in kwargs.items() if key in accepted}


def _extract_genealogy_strings(df: pd.DataFrame) -> list[str]:
    """Extract simulated genealogy strings from model.df."""
    for col in ("genealogy", "tree", "newick"):
        if col in df.columns:
            values = df[col].dropna().astype(str).tolist()
            if values:
                return values
    raise ToytreeError(
        "Could not find simulated tree strings in model.df. Expected one of "
        "columns: 'genealogy', 'tree', or 'newick'."
    )


def _import_ipcoal() -> Any:
    """Import optional ipcoal dependency at runtime."""
    try:
        return importlib.import_module("ipcoal")
    except ImportError as exc:
        raise ToytreeError(
            "ipcoal is required for ipcoal_sim_trees(). Install with conda, "
            "e.g., `conda install -c conda-forge ipcoal`."
        ) from exc


def ipcoal_sim_trees(
    species_tree: ToyTree,
    Ne: None | int | Mapping,
    nsamples: int | Mapping | None = None,
    admixture_edges: list | None = None,
    recomb: float | None = None,
    mut: float | None = None,
    ancestry_model: str | None = None,
    sequence_length: int | None = None,
    discrete_genome: bool | None = None,
    ploidy: int | None = None,
    seed_trees: int | None = None,
    seed_mutations: int | None = None,
    store_tree_sequences: bool = False,
    ntrees: int = 1,
    nsites: int | None = None,
    return_df: bool = False,
) -> ToyTree | MultiTree | pd.DataFrame:
    """Simulate genealogies with ``ipcoal.Model(...).sim_trees(...)``.

    Args:
        species_tree: Species tree used as the simulation demography.
        Ne: Effective population size scalar, ``None``, or mapping.
        nsamples: Samples per tip (scalar) or per-tip mapping.
        admixture_edges: Optional list of admixture edges for demographic model.
        recomb: Recombination rate.
        mut: Mutation rate.
        ancestry_model: Optional ancestry model name forwarded to ipcoal.
        sequence_length: Optional genome length / sequence length argument.
        discrete_genome: Optional discrete-genome simulation mode.
        ploidy: Optional ploidy setting.
        seed_trees: Seed for tree simulation.
        seed_mutations: Seed for mutation simulation.
        store_tree_sequences: If True request tree-sequence storage in ipcoal.
        ntrees: Number of gene trees to simulate (must be >=1).
        nsites: Optional number of sites argument for ``sim_trees``.
        return_df: If True return ``model.df`` instead of tree objects.

    Returns
    -------
        One of:
        - ``ToyTree`` when one tree is simulated and ``return_df=False``.
        - ``MultiTree`` when multiple trees are simulated and ``return_df=False``.
        - ``pandas.DataFrame`` (``model.df``) when ``return_df=True``.

    Raises
    ------
        ToytreeError: If ipcoal is unavailable, inputs are invalid, simulation
            output is missing expected tree data, or simulated trees cannot be parsed.
    """
    if not isinstance(species_tree, ToyTree):
        raise ToytreeError("'species_tree' must be a ToyTree.")
    if int(ntrees) < 1:
        raise ToytreeError("'ntrees' must be >= 1.")

    # Runtime-only dependency check for optional package.
    ipcoal = _import_ipcoal()

    model_kwargs = {
        "tree": species_tree,
        "Ne": Ne,
        "nsamples": nsamples,
        "admixture_edges": admixture_edges,
        "recomb": recomb,
        "mut": mut,
        "ancestry_model": ancestry_model,
        "sequence_length": sequence_length,
        "discrete_genome": discrete_genome,
        "ploidy": ploidy,
        "seed_trees": seed_trees,
        "seed_mutations": seed_mutations,
        "store_tree_sequences": store_tree_sequences,
    }
    model_kwargs = {k: v for k, v in model_kwargs.items() if v is not None}
    if "store_tree_sequences" not in model_kwargs:
        model_kwargs["store_tree_sequences"] = store_tree_sequences
    model_kwargs = _filter_supported_kwargs(ipcoal.Model, model_kwargs)

    model = ipcoal.Model(**model_kwargs)

    sim_kwargs = {"ntrees": int(ntrees), "nsites": nsites}
    sim_kwargs = {k: v for k, v in sim_kwargs.items() if v is not None}
    sim_kwargs = _filter_supported_kwargs(model.sim_trees, sim_kwargs)
    model.sim_trees(**sim_kwargs)

    if return_df:
        return model.df

    if not hasattr(model, "df") or not isinstance(model.df, pd.DataFrame):
        raise ToytreeError(
            "ipcoal simulation did not produce a valid model.df DataFrame."
        )

    treestrs = _extract_genealogy_strings(model.df)
    trees: list[ToyTree] = []
    for treestr in treestrs:
        try:
            trees.append(toytree.tree(treestr))
        except Exception as exc:
            raise ToytreeError(
                "Failed to parse one or more simulated genealogy strings."
            ) from exc

    if len(trees) == 1:
        return trees[0]
    return toytree.mtree(trees)
