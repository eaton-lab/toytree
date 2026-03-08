#!/usr/bin/env python

"""Regression tests for CLI lazy-loading behavior."""

from __future__ import annotations

import json
import subprocess
import sys

HEAVY_PREFIXES = (
    "toytree.core",
    "toytree.mod",
    "toytree.io",
    "toytree.distance",
    "toytree.infer",
    "toytree.pcm",
    "numpy",
    "pandas",
    "toyplot",
)


def _run_python(code: str) -> str:
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def _parse_heavy_list(stdout: str) -> list[str]:
    lines = [i.strip() for i in stdout.splitlines() if i.strip()]
    marker = [i for i in lines if i.startswith("JSON:")]
    assert marker, stdout
    return json.loads(marker[-1].split("JSON:", 1)[1])


def test_import_main_does_not_eager_import_heavy_modules():
    """Importing CLI main should not import heavy runtime modules."""
    code = r"""
import json
import sys
import toytree.cli.main  # noqa: F401
heavy = [i for i in sys.modules if i.startswith(tuple(%s))]
print("JSON:" + json.dumps(sorted(heavy)))
""" % (
        repr(HEAVY_PREFIXES),
    )
    heavy = _parse_heavy_list(_run_python(code))
    assert heavy == []


def test_help_screens_do_not_import_heavy_modules():
    """Help parsing should keep heavy modules unloaded."""
    code = r"""
import json
import sys
import toytree.cli.main as main
for cmd in ("-h", "draw -h", "rtree -h"):
    try:
        main.main(cmd)
    except SystemExit:
        pass
heavy = [i for i in sys.modules if i.startswith(tuple(%s))]
print("JSON:" + json.dumps(sorted(heavy)))
""" % (
        repr(HEAVY_PREFIXES),
    )
    heavy = _parse_heavy_list(_run_python(code))
    assert heavy == []
