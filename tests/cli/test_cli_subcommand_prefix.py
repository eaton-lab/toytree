#!/usr/bin/env python

"""Tests for top-level CLI subcommand prefix expansion."""

from __future__ import annotations

import pytest

from toytree.cli import main, subparsers


def test_unique_prefix_set_expands_to_set_node_data_help(capsys):
    """`set -h` should expand to the `set-node-data` help screen."""
    with pytest.raises(SystemExit) as exc:
        main.main("set -h")
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "set-node-data" in out
    assert "assign feature values to nodes and return tree" in out


def test_unique_prefix_get_expands_to_get_node_data_help(capsys):
    """`get -h` should expand to the `get-node-data` help screen."""
    with pytest.raises(SystemExit) as exc:
        main.main("get -h")
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "get-node-data" in out
    assert "return tabular feature data from tree nodes" in out


def test_ambiguous_prefix_raises_error(capsys):
    """Ambiguous prefixes should raise with matching command names."""
    with pytest.raises(SystemExit) as exc:
        main.main("d -h")
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "ambiguous subcommand prefix" in err
    assert "draw" in err
    assert "distance" in err


def test_unknown_subcommand_keeps_argparse_invalid_choice_behavior(capsys):
    """Unknown command names should still report argparse invalid-choice."""
    with pytest.raises(SystemExit) as exc:
        main.main("zzz")
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "invalid choice" in err


def test_exact_command_name_still_works(capsys):
    """Exact command names should continue to work unchanged."""
    with pytest.raises(SystemExit) as exc:
        main.main("set-node-data -h")
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "set-node-data" in out


def test_make_prefix_applies_calibration_token_normalization(monkeypatch):
    """`make` prefix should still trigger calibration token normalization."""
    observed = {}

    def fake_load_handler(spec):
        observed["spec"] = spec

        def _run(args):
            observed["args"] = args

        return _run

    monkeypatch.setattr(main, "_load_handler", fake_load_handler)
    status = main.main("make -i ((a,b),c); -m extend -c -1=1.0")
    assert status == 0
    assert observed["spec"] == "toytree.cli.cli_make_ultrametric:run_make_ultrametric"
    calibrations = observed["args"].calibrations
    assert calibrations
    assert calibrations[0].startswith(subparsers.NEGATIVE_CAL_QUERY_PREFIX)
