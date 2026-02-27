#!/usr/bin/env python

"""toytree external-tools subpackage.

This subpackage contains user-facing methods that call external tools not
installed as required dependencies of toytree (for example external binaries
or optional Python packages).

Rules
-----
- Methods in this subpackage are lazily imported.
- External dependency checks occur at runtime when a method is called.
- For wrappers with a ``binary_path`` argument, the method should check for
  missing binaries at runtime. If ``binary_path`` is ``None``, it should look
  in ``$PATH`` and raise a clear error if missing.
"""

from __future__ import annotations

import importlib

_LAZY_ATTRS = {
    "generax_optimize": ("toytree.external.src.generax", "generax_optimize"),
    "ipcoal_sim_trees": ("toytree.external.src.ipcoal_sim", "ipcoal_sim_trees"),
}


def __getattr__(name: str):
    """Lazily import external-binary wrappers on first access."""
    if name not in _LAZY_ATTRS:
        raise AttributeError(name)
    module_name, attr_name = _LAZY_ATTRS[name]
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
