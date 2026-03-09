#!/usr/bin/env python

"""Regression tests for user-facing CLI runtime error handling."""

from __future__ import annotations

from pathlib import Path

from toytree.cli import main


def test_set_missing_table_reports_clean_error_no_traceback(tmp_path, capsys):
    """Missing table files should print a concise error without traceback."""
    tree_path = Path(tmp_path) / "tree.nwk"
    tree_path.write_text("((a:1,b:1):1,c:1);\n", encoding="utf-8")

    status = main.main(f"set -i {tree_path} --table A.tsv")
    assert status == 1

    captured = capsys.readouterr()
    assert "Traceback" not in captured.err
    assert "Error:" in captured.err
    assert "A.tsv" in captured.err
