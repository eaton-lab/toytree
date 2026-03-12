#!/usr/bin/env python

"""Runtime implementation for the `io` CLI command."""

from __future__ import annotations

import sys
from pathlib import Path


def _is_nexus_output(args) -> bool:
    """Return True when output should be serialized as Nexus text."""
    if args.nexus:
        return True
    out = args.output
    if isinstance(out, Path):
        return out.suffix.lower() in {".nex", ".nexus"}
    return False


def run_io(args) -> None:
    """Run the `io` CLI command."""
    from toytree.cli._tree_transport import (
        is_binary_tree_payload,
        read_tree_auto,
        resolve_input_arg,
        write_tree_output,
    )
    from toytree.utils import ToytreeError

    nexus_out = _is_nexus_output(args)
    if args.write_single_feature is not None:
        if args.binary_out:
            raise ToytreeError(
                "--write-single-feature is only valid for text output "
                "(not --binary-out)."
            )
        if nexus_out:
            raise ToytreeError(
                "--write-single-feature is not supported for Nexus output."
            )
    if args.features_pack in {args.features_delim, args.features_assignment}:
        raise ToytreeError(
            "--features-pack cannot match --features-delim or "
            f"--features-assignment: {args.features_pack!r}"
        )

    input_arg = resolve_input_arg(args.input)

    # Fast path: io binary->binary mode can pass through transport bytes
    # without parsing/re-serializing the tree object.
    if args.binary_out:
        input_bytes: bytes | None = None
        if input_arg == "-":
            input_bytes = sys.stdin.buffer.read()
            if not input_bytes:
                raise ToytreeError("no data received on stdin.")
        else:
            path = Path(input_arg)
            if path.exists():
                input_bytes = path.read_bytes()
        if input_bytes is not None and is_binary_tree_payload(input_bytes):
            if args.output:
                args.output.write_bytes(input_bytes)
            else:
                sys.stdout.buffer.write(input_bytes)
                sys.stdout.buffer.flush()
            return

    tree = read_tree_auto(
        input_arg,
        internal_labels=args.internal_labels,
        feature_prefix=args.in_feature_prefix,
        feature_delim=args.in_feature_delim,
        feature_assignment=args.in_feature_assignment,
        feature_unpack=args.in_feature_unpack,
    )

    # Binary mode is a direct transport of the in-memory tree object.
    if args.binary_out:
        write_tree_output(tree, output=args.output, binary_out=True)
        return

    features = set(tree.features) - {"name", "dist", "height", "support"}
    write_kwargs = {
        "features_prefix": args.features_prefix,
        "features_delim": args.features_delim,
        "features_assignment": args.features_assignment,
        "features_pack": args.features_pack,
        "features_formatter": args.features_formatter,
        "nexus": nexus_out,
    }
    if args.write_single_feature is not None:
        write_kwargs["write_single_feature"] = args.write_single_feature

    # `-x` suppresses both support internal labels and extra metadata comments.
    if args.exclude_features:
        features = None
        write_kwargs["internal_labels"] = None

    write_tree_output(
        tree,
        output=args.output,
        binary_out=False,
        features=features,
        newick_write_kwargs=write_kwargs,
    )
