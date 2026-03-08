#!/usr/bin/env python

"""Runtime implementation for the `relabel` CLI command."""

from __future__ import annotations

from typing import Callable


def _build_transform_fn(
    strip: str | None,
    stripleft: str | None,
    prepend: str | None,
    append: str | None,
) -> Callable[[str], str] | None:
    """Compose strip/stripleft transforms with optional prepend/append."""
    if strip is None and stripleft is None and prepend is None and append is None:
        return None

    def fn(name: str) -> str:
        out = name
        if strip is not None:
            out = out.strip(strip)
        if stripleft is not None:
            out = out.lstrip(stripleft)
        if prepend:
            out = f"{prepend}{out}"
        if append:
            out = f"{out}{append}"
        return out

    return fn


def run_relabel(args):
    """Run the `relabel` CLI command."""
    from toytree.cli._tree_transport import read_tree_auto, write_tree_output
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)
    fn = _build_transform_fn(args.strip, args.stripleft, args.prepend, args.append)
    tre = tre.relabel(
        queries=args.nodes,
        fn=fn,
        delim=args.delim,
        delim_idxs=args.delim_idxs,
        delim_join=args.delim_join,
        italic=args.italic,
        bold=args.bold,
        tips_only=args.tips_only,
        inplace=False,
    )
    if args.exclude_features:
        features = None
    else:
        features = set(tre.features) - {"name", "height", "dist", "support"}
    write_tree_output(
        tre,
        output=args.output,
        binary_out=args.binary_out,
        features=features,
    )
