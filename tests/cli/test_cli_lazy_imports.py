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

MULTITREE_HEAVY_PREFIXES = (
    "numpy",
    "pandas",
    "toyplot",
    "loguru",
    "toytree.drawing",
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
""" % (repr(HEAVY_PREFIXES),)
    heavy = _parse_heavy_list(_run_python(code))
    assert heavy == []


def test_import_toytree_does_not_eager_import_heavy_modules():
    """Importing top-level toytree should not import heavy subpackages."""
    code = r"""
import json
import sys
import toytree  # noqa: F401
heavy = [i for i in sys.modules if i.startswith(tuple(%s))]
print("JSON:" + json.dumps(sorted(heavy)))
""" % (repr(HEAVY_PREFIXES),)
    heavy = _parse_heavy_list(_run_python(code))
    assert heavy == []


def test_import_core_multitree_stays_lightweight():
    """Importing `toytree.core.multitree` should avoid heavy draw deps."""
    code = r"""
import json
import sys
import toytree.core.multitree  # noqa: F401
heavy = [i for i in sys.modules if i.startswith(tuple(%s))]
print("JSON:" + json.dumps(sorted(heavy)))
""" % (repr(MULTITREE_HEAVY_PREFIXES),)
    heavy = _parse_heavy_list(_run_python(code))
    assert heavy == []


def test_import_toytree_multitree_attr_stays_lightweight():
    """Touching `toytree.MultiTree` should not import draw-time modules."""
    code = r"""
import json
import sys
import toytree
_ = toytree.MultiTree
heavy = [i for i in sys.modules if i.startswith(tuple(%s))]
print("JSON:" + json.dumps(sorted(heavy)))
""" % (repr(MULTITREE_HEAVY_PREFIXES),)
    heavy = _parse_heavy_list(_run_python(code))
    assert heavy == []


def test_help_screens_do_not_import_heavy_modules():
    """Help parsing should keep heavy modules unloaded."""
    code = r"""
import json
import sys
import toytree.cli.main as main
for cmd in ("-h", "view -h", "draw -h", "rtree -h", "anc-state-discrete -h"):
    try:
        main.main(cmd)
    except SystemExit:
        pass
heavy = [i for i in sys.modules if i.startswith(tuple(%s))]
print("JSON:" + json.dumps(sorted(heavy)))
""" % (repr(HEAVY_PREFIXES),)
    heavy = _parse_heavy_list(_run_python(code))
    assert heavy == []


def test_rtree_runtime_does_not_import_io_stack():
    """Executing rtree generation should only import lightweight IO writer."""
    code = r"""
import contextlib
import io
import json
import sys
import toytree.cli.main as main
with contextlib.redirect_stdout(io.StringIO()):
    main.main("rtree -n 6 -m r --seed 1")
mods = [i for i in sys.modules if i.startswith("toytree.io")]
print("JSON:" + json.dumps(sorted(mods)))
"""
    heavy = _parse_heavy_list(_run_python(code))
    assert heavy == [
        "toytree.io",
        "toytree.io.src",
        "toytree.io.src.writer",
    ]


def test_import_toytree_io_does_not_import_parse_stack():
    """Importing toytree.io should not eagerly import parse modules."""
    code = r"""
import json
import sys
import toytree.io  # noqa: F401
mods = [i for i in sys.modules if i.startswith("toytree.io")]
print("JSON:" + json.dumps(sorted(mods)))
"""
    mods = _parse_heavy_list(_run_python(code))
    assert mods == ["toytree.io"]


def test_import_io_writer_does_not_import_parse_stack():
    """Importing io writer should avoid parse/treeio/mtreeio modules."""
    code = r"""
import json
import sys
import toytree.io.src.writer  # noqa: F401
mods = [i for i in sys.modules if i.startswith("toytree.io")]
print("JSON:" + json.dumps(sorted(mods)))
"""
    mods = _parse_heavy_list(_run_python(code))
    assert mods == [
        "toytree.io",
        "toytree.io.src",
        "toytree.io.src.writer",
    ]


def test_import_toytree_utils_stays_lazy():
    """Importing toytree.utils should not pull in optional helper modules."""
    code = r"""
import json
import sys
import toytree.utils  # noqa: F401
mods = [
    i for i in sys.modules
    if (
        i.startswith("toyplot")
        or i == "toytree.utils.src.browser"
        or i == "toytree.utils.src.exceptions"
        or i == "toytree.utils.src.scrollable_canvas"
        or i == "toytree.utils.src.style_axes"
    )
]
print("JSON:" + json.dumps(sorted(mods)))
"""
    mods = _parse_heavy_list(_run_python(code))
    assert mods == []


def test_plain_newick_parse_avoids_optional_heavy_modules():
    """Plain Newick parsing should avoid optional heavy imports."""
    code = r"""
import json
import sys
import toytree

toytree.tree("((a,b),c);")
mods = [
    i for i in sys.modules
    if (
        i.startswith("numpy")
        or i.startswith("pandas")
        or i.startswith("toyplot")
        or i == "toytree.io.src.nexus"
        or i == "toytree.utils.src.browser"
        or i == "toytree.utils.src.logger_setup"
        or i == "toytree.utils.src.scrollable_canvas"
        or i == "toytree.utils.src.style_axes"
    )
]
print("JSON:" + json.dumps(sorted(mods)))
"""
    mods = _parse_heavy_list(_run_python(code))
    assert mods == []


def test_unittree_runtime_does_not_import_penalized_likelihood_stack():
    """Executing unittree generation should not import PL optimization modules."""
    code = r"""
import contextlib
import io
import json
import sys
import toytree.cli.main as main
with contextlib.redirect_stdout(io.StringIO()):
    main.main("rtree -n 6 -m u --seed 1")
mods = [
    i for i in sys.modules
    if i.startswith("toytree.mod._src.penalized_likelihood")
]
print("JSON:" + json.dumps(sorted(mods)))
"""
    heavy = _parse_heavy_list(_run_python(code))
    assert heavy == []


def test_rtree_runtime_does_not_import_logger_stack_by_default():
    """Default rtree runtime should not import logger setup or loguru."""
    code = r"""
import contextlib
import io
import json
import sys
import toytree.cli.main as main
with contextlib.redirect_stdout(io.StringIO()):
    main.main("rtree -n 6 -m u --seed 1")
mods = [
    i for i in sys.modules
    if (i == "toytree.utils.src.logger_setup") or i.startswith("loguru")
]
print("JSON:" + json.dumps(sorted(mods)))
"""
    mods = _parse_heavy_list(_run_python(code))
    assert mods == []


def test_anc_runtime_does_not_import_logger_stack_by_default():
    """Default anc runtime should not import logger setup or loguru."""
    code = r"""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import toytree.cli.main as main

path = pathlib.Path(tempfile.mkdtemp()) / "tree.nwk"
path.write_text("((a[&X=A]:1,b[&X=B]:1):1,c[&X=A]:1);\n", encoding="utf-8")
with contextlib.redirect_stdout(io.StringIO()):
    main.main(f"anc-state-discrete -i {path} -f X -n 2 -m ER")
mods = [
    i for i in sys.modules
    if (i == "toytree.utils.src.logger_setup") or i.startswith("loguru")
]
print("JSON:" + json.dumps(sorted(mods)))
"""
    mods = _parse_heavy_list(_run_python(code))
    assert mods == []


def test_view_runtime_does_not_import_graphics_or_logger_stack_by_default():
    """View runtime should avoid graphics and logger modules by default."""
    code = r"""
import contextlib
import io
import json
import sys
import toytree.cli.main as main
with contextlib.redirect_stdout(io.StringIO()):
    main.main("view -i ((a,b),c);")
mods = [
    i for i in sys.modules
    if (
        i.startswith("toyplot")
        or i.startswith("toytree.drawing")
        or i == "toytree.utils.src.logger_setup"
        or i.startswith("loguru")
    )
]
print("JSON:" + json.dumps(sorted(mods)))
"""
    mods = _parse_heavy_list(_run_python(code))
    assert mods == []


def test_view_ladderize_and_heavy_runtime_avoids_mod_graphics_and_logger_stack():
    """View ladderize and heavy selectors should stay on the light path."""
    code = r"""
import contextlib
import io
import json
import sys
import toytree.cli.main as main
with contextlib.redirect_stdout(io.StringIO()):
    main.main("view -i ((a,b)95,c); --ladderize --heavy support>50")
mods = [
    i for i in sys.modules
    if (
        i.startswith("toytree.mod")
        or i.startswith("toyplot")
        or i.startswith("toytree.drawing")
        or i == "toytree.utils.src.logger_setup"
        or i.startswith("loguru")
    )
]
print("JSON:" + json.dumps(sorted(mods)))
"""
    mods = _parse_heavy_list(_run_python(code))
    assert mods == []


def test_touching_discrete_pcm_attr_does_not_import_phylolinalg_stack():
    """Accessing discrete CTMC API should not import PGLS/PGLM dependencies."""
    code = r"""
import json
import sys
import toytree

tree = toytree.tree("((a,b),c);")
_ = tree.pcm.infer_ancestral_states_discrete_ctmc
mods = [
    i for i in sys.modules
    if i.startswith("statsmodels") or i.startswith("toytree.pcm.src.phylolinalg")
]
print("JSON:" + json.dumps(sorted(mods)))
"""
    mods = _parse_heavy_list(_run_python(code))
    assert mods == []
