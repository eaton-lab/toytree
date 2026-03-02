#!/usr/bin/env python

"""Tests for GeneRax wrapper utility."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

import toytree
from toytree import tree
from toytree.external.src.generax import generax_optimize
from toytree.utils import ToytreeError


@pytest.fixture
def generax_case(tmp_path: Path) -> dict[str, object]:
    """Build rooted tree and alignment fixtures for GeneRax tests."""
    gtree = tree("((a:1,b:1):1,c:1);")
    sptree = tree("((a:1,b:1):1,c:1);")
    aln = tmp_path / "aln.phy"
    aln.write_text("3 4\na AAAA\nb AAAA\nc AAAA\n", encoding="utf-8")
    return {"gtree": gtree, "sptree": sptree, "aln": aln, "tmpdir": tmp_path}


def _mock_run_success(cmd, cwd, capture_output, text, check):
    """Mock subprocess.run that creates output files expected by parser."""
    assert capture_output
    assert text
    assert not check
    wdir = Path(cwd)
    (wdir / "best.newick").write_text("((a:1,b:1):1,c:1);\n", encoding="utf-8")
    (wdir / "recon.txt").write_text(
        "duplications: 1\nlosses: 2\ntransfers: 0\n",
        encoding="utf-8",
    )

    class Proc:
        returncode = 0
        stdout = "ok"
        stderr = ""

    return Proc()


def test_api_location() -> None:
    """Ensure generax wrapper is exposed from external, not infer."""
    assert hasattr(toytree.external, "generax_optimize")
    assert not hasattr(toytree.infer, "generax_optimize")


@patch("toytree.external.src.generax.shutil.which", return_value=None)
def test_binary_resolution_failure_raises(_mock_which, generax_case: dict[str, object]):
    """Raise informative error when no binary path and not found in PATH."""
    with pytest.raises(ToytreeError):
        generax_optimize(
            generax_case["gtree"], generax_case["sptree"], generax_case["aln"]
        )


@patch("toytree.external.src.generax.subprocess.run")
@patch("toytree.external.src.generax.shutil.which", return_value="generax")
def test_run_success_parses_tree_and_summary(
    _mock_which,
    mock_run,
    generax_case: dict[str, object],
):
    """Run mocked subprocess and parse returned optimized tree."""
    mock_run.side_effect = _mock_run_success
    out = generax_optimize(
        generax_case["gtree"],
        generax_case["sptree"],
        generax_case["aln"],
        workdir=generax_case["tmpdir"],
        allow_overwrite=True,
        seed=12,
        threads=4,
    )
    assert "optimized_tree" in out
    assert out["optimized_tree"].ntips == generax_case["gtree"].ntips
    assert "duplications" in out["reconciliation"]
    cmd = out["command"]
    assert "--seed" in cmd
    assert "12" in cmd
    assert "--cores" in cmd
    assert "4" in cmd


@patch("toytree.external.src.generax.subprocess.run")
@patch("toytree.external.src.generax.shutil.which", return_value="generax")
def test_accepts_dict_imap(_mock_which, mock_run, generax_case: dict[str, object]):
    """Allow imap as an in-memory dict[str, str] mapping."""
    mock_run.side_effect = _mock_run_success
    out = generax_optimize(
        generax_case["gtree"],
        generax_case["sptree"],
        generax_case["aln"],
        imap={"a": "a", "b": "b", "c": "c"},
        workdir=generax_case["tmpdir"],
        allow_overwrite=True,
    )
    assert "optimized_tree" in out


@patch("toytree.external.src.generax.shutil.which", return_value="generax")
def test_requires_rooted_species_tree(_mock_which, generax_case: dict[str, object]):
    """Reject unrooted species tree before subprocess execution."""
    with pytest.raises(ToytreeError):
        generax_optimize(
            generax_case["gtree"],
            generax_case["sptree"].unroot(),
            generax_case["aln"],
        )


@patch("toytree.external.src.generax.shutil.which", return_value="generax")
def test_missing_imap_match_raises(_mock_which, generax_case: dict[str, object]):
    """Reject exact-match fallback when gene labels are absent in species tree."""
    bad_gtree = tree("((x:1,y:1):1,z:1);")
    with pytest.raises(ToytreeError):
        generax_optimize(bad_gtree, generax_case["sptree"], generax_case["aln"])
