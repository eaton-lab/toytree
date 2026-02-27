#!/usr/bin/env python

"""Thin wrapper for GeneRax reconciliation-aware gene-tree optimization.

This module provides a minimal interface for running an external ``generax``
binary on one gene family and parsing its optimized gene-tree output back into
a ``ToyTree`` object.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Mapping

import pandas as pd

import toytree
from toytree import ToyTree
from toytree.utils import ToytreeError

__all__ = ["generax_optimize"]


def _resolve_binary(binary_path: str | Path | None) -> str:
    """Resolve executable path for GeneRax.

    Args:
        binary_path: Optional explicit path to the GeneRax executable.

    Returns
    -------
        A string path to an executable binary.

    Raises
    ------
        ToytreeError: If the binary cannot be found or is not executable.
    """
    if binary_path is not None:
        path = Path(binary_path).expanduser().resolve()
        if not path.exists():
            raise ToytreeError(f"GeneRax binary not found: {path}")
        if not path.is_file():
            raise ToytreeError(f"GeneRax binary path is not a file: {path}")
        if not path.stat().st_mode & 0o111:
            raise ToytreeError(f"GeneRax binary is not executable: {path}")
        return str(path)

    found = shutil.which("generax")
    if found:
        return found
    raise ToytreeError(
        "Could not find 'generax' in $PATH. Set 'binary_path' to a GeneRax "
        "executable, or install GeneRax and ensure it is on $PATH."
    )


def _coerce_tree_input(
    tree: ToyTree | str | Path,
    *,
    workdir: Path,
    name: str,
) -> tuple[ToyTree, Path]:
    """Normalize tree input to a ToyTree and a Newick file path."""
    outpath = workdir / f"{name}.nwk"
    if isinstance(tree, ToyTree):
        obj = tree
        obj.write(path=str(outpath))
        return obj, outpath

    pth = Path(tree).expanduser()
    if pth.exists():
        obj = toytree.tree(str(pth))
        return obj, pth.resolve()

    obj = toytree.tree(str(tree))
    obj.write(path=str(outpath))
    return obj, outpath


def _load_imap_table(path: Path) -> dict[str, str]:
    """Load a 2-column imap file with gene->species labels."""
    data = pd.read_csv(
        path,
        sep=None,
        engine="python",
        header=None,
        comment="#",
        dtype=str,
    )
    if data.shape[1] < 2:
        raise ToytreeError(
            "imap file must contain at least two columns (gene, species)."
        )
    data = data.iloc[:, :2].dropna(axis=0, how="any")
    if data.empty:
        raise ToytreeError("imap file has no usable rows.")
    imap = dict(zip(data.iloc[:, 0], data.iloc[:, 1], strict=False))
    if not imap:
        raise ToytreeError("imap file could not be parsed into gene->species mappings.")
    return imap


def _coerce_imap(
    imap: Mapping[str, str] | str | Path | None,
    *,
    gene_tree: ToyTree,
    species_tree: ToyTree,
    workdir: Path,
) -> tuple[dict[str, str], Path]:
    """Normalize mapping input and write GeneRax mapping file."""
    gene_labels = gene_tree.get_tip_labels()
    species_labels = set(species_tree.get_tip_labels())

    if imap is None:
        mapping = {i: i for i in gene_labels}
    elif isinstance(imap, Mapping):
        mapping = {str(k): str(v) for k, v in imap.items()}
    else:
        mapping = _load_imap_table(Path(imap).expanduser().resolve())

    missing = [i for i in gene_labels if i not in mapping]
    if missing:
        ex = ", ".join(missing[:5])
        raise ToytreeError(f"imap missing one or more gene tips (e.g., {ex}).")

    bad_species = sorted(
        {mapping[i] for i in gene_labels if mapping[i] not in species_labels}
    )
    if bad_species:
        ex = ", ".join(bad_species[:5])
        raise ToytreeError(f"imap maps to unknown species labels (e.g., {ex}).")

    outpath = workdir / "mapping.txt"
    with outpath.open("w", encoding="utf-8") as out:
        for gname in gene_labels:
            out.write(f"{gname}\t{mapping[gname]}\n")
    return mapping, outpath


def _write_family_file(
    *,
    workdir: Path,
    gene_tree_path: Path,
    alignment_path: Path,
    mapping_path: Path,
    subst_model: str,
) -> Path:
    """Write a one-family GeneRax family file."""
    outpath = workdir / "families.txt"
    lines = [
        "[FAMILIES]",
        "- family_1",
        f"starting_gene_tree = {gene_tree_path}",
        f"alignment = {alignment_path}",
        f"mapping = {mapping_path}",
        f"subst_model = {subst_model}",
    ]
    outpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return outpath


def _parse_optimized_tree(workdir: Path) -> ToyTree:
    """Discover and parse optimized tree from GeneRax outputs."""
    candidates = sorted(workdir.rglob("*.newick"))
    if not candidates:
        candidates = sorted(workdir.rglob("*.nwk"))
    if not candidates:
        candidates = sorted(workdir.rglob("*.tree"))
    if not candidates:
        raise ToytreeError("GeneRax finished but no candidate output tree was found.")

    for cpath in candidates:
        try:
            text = cpath.read_text(encoding="utf-8", errors="ignore").strip()
        except OSError:
            continue
        if "(" not in text or ")" not in text or ";" not in text:
            continue
        try:
            return toytree.tree(text.splitlines()[0])
        except Exception:
            continue
    raise ToytreeError("Failed to parse an optimized gene tree from GeneRax outputs.")


def _parse_reconciliation_summary(workdir: Path) -> dict[str, float | int | str]:
    """Parse reconciliation summary values from text reports when available."""
    summary: dict[str, float | int | str] = {}
    patterns = ("dup", "loss", "trans", "ll", "likelihood", "score")
    for cpath in workdir.rglob("*.txt"):
        try:
            text = cpath.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            if ":" not in line:
                continue
            key, val = [i.strip() for i in line.split(":", 1)]
            if not key:
                continue
            lkey = key.lower()
            if not any(p in lkey for p in patterns):
                continue
            try:
                if "." in val or "e" in val.lower():
                    summary[key] = float(val)
                else:
                    summary[key] = int(val)
            except ValueError:
                summary[key] = val
    return summary


def generax_optimize(
    gene_tree: ToyTree | str | Path,
    species_tree: ToyTree | str | Path,
    alignment: str | Path,
    *,
    imap: Mapping[str, str] | str | Path | None = None,
    subst_model: str = "GTR+G",
    binary_path: str | Path | None = None,
    workdir: str | Path | None = None,
    seed: int | None = None,
    threads: int = 1,
    allow_overwrite: bool = False,
    keep_temp: bool = False,
    log_level: str | None = None,
) -> dict[str, object]:
    """Run one-family GeneRax optimization and return parsed results.

    Args:
        gene_tree: Input gene tree as a ``ToyTree``, path, or Newick string.
        species_tree: Input rooted species tree as ``ToyTree``, path, or Newick.
        alignment: Path to alignment file for this family.
        imap: Optional gene->species mapping as dict or 2-column file path.
            If omitted, exact label matching is attempted.
        subst_model: Substitution model string passed to GeneRax.
        binary_path: Optional explicit path to ``generax`` binary.
            If ``None``, the function searches ``$PATH``.
        workdir: Optional output directory. If ``None``, a temp dir is created.
        seed: Optional RNG seed passed to GeneRax.
        threads: Number of worker threads for GeneRax.
        allow_overwrite: If ``False`` and ``workdir`` exists with files, raise.
        keep_temp: If ``True``, keep auto-created temporary workdir.
        log_level: Optional GeneRax log level string.

    Returns
    -------
        Dict with keys:
        - ``optimized_tree``: ToyTree parsed from GeneRax output.
        - ``reconciliation``: Parsed reconciliation summary values.
        - ``command``: Executed command list.
        - ``stdout``: Captured subprocess stdout.
        - ``stderr``: Captured subprocess stderr.
        - ``workdir``: Path to output working directory.

    Raises
    ------
        ToytreeError: On invalid inputs, binary resolution failures, subprocess
            failures, or output parsing failures.
    """
    binary = _resolve_binary(binary_path)

    # Resolve / create workdir.
    cleanup_dir = False
    if workdir is None:
        wdir = Path(tempfile.mkdtemp(prefix="toytree-generax-"))
        cleanup_dir = not keep_temp
    else:
        wdir = Path(workdir).expanduser().resolve()
        if wdir.exists() and any(wdir.iterdir()) and (not allow_overwrite):
            raise ToytreeError(f"workdir exists and is non-empty: {wdir}")
        wdir.mkdir(parents=True, exist_ok=True)

    try:
        gtree, gpath = _coerce_tree_input(gene_tree, workdir=wdir, name="gene_tree")
        sptree, spath = _coerce_tree_input(
            species_tree,
            workdir=wdir,
            name="species_tree",
        )
        if not sptree.is_rooted():
            raise ToytreeError("species_tree must be rooted for GeneRax optimization.")

        apath = Path(alignment).expanduser().resolve()
        if not apath.exists():
            raise ToytreeError(f"alignment file not found: {apath}")

        _imap, mpath = _coerce_imap(
            imap,
            gene_tree=gtree,
            species_tree=sptree,
            workdir=wdir,
        )
        fam_path = _write_family_file(
            workdir=wdir,
            gene_tree_path=gpath,
            alignment_path=apath,
            mapping_path=mpath,
            subst_model=subst_model,
        )

        # Build GeneRax command for one-family optimization.
        cmd: list[str] = [
            binary,
            "--species-tree",
            str(spath),
            "--families",
            str(fam_path),
            "--prefix",
            str(wdir / "generax_out"),
            "--strategy",
            "SPR",
            "--rec-model",
            "UndatedDTL",
            "--si-quite",
        ]
        if seed is not None:
            cmd.extend(["--seed", str(int(seed))])
        if threads > 0:
            cmd.extend(["--cores", str(int(threads))])
        if log_level is not None:
            cmd.extend(["--log-level", str(log_level)])

        proc = subprocess.run(
            cmd,
            cwd=str(wdir),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise ToytreeError(
                "GeneRax failed with non-zero exit status.\n"
                f"returncode={proc.returncode}\n"
                f"stderr={proc.stderr[-2000:]}"
            )

        opt_tree = _parse_optimized_tree(wdir)
        recon = _parse_reconciliation_summary(wdir)
        return {
            "optimized_tree": opt_tree,
            "reconciliation": recon,
            "command": cmd,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "workdir": str(wdir),
        }
    finally:
        if cleanup_dir:
            shutil.rmtree(wdir, ignore_errors=True)
