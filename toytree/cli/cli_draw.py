#!/usr/bin/env python


import sys
import tempfile
from pathlib import Path

from ._subparser_helpers import (
    _parse_style_kv,
    _scalar_or_list,
)


def open_with_default_viewer(path: str) -> bool:
    """Try to open a file with the system's default app."""
    import os
    import platform
    import shutil
    import subprocess
    import webbrowser

    path = os.path.abspath(path)
    system = platform.system()

    try:
        if system == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
            return True

        if system == "Darwin":
            subprocess.Popen(["open", path])
            return True

        opener = (
            shutil.which("xdg-open")
            or shutil.which("gio")
            or shutil.which("gnome-open")
            or shutil.which("kde-open")
        )
        if opener:
            subprocess.Popen([opener, path])
            return True

        file_url = f"file://{path}"
        if webbrowser.open(file_url):
            return True

    except Exception as exc:
        raise OSError("could not find a default viewer to open drawing file") from exc
    return False


def run_draw(args):
    """Run draw command."""
    from toytree import save
    from toytree.cli._tree_transport import read_tree_auto, resolve_input_arg
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    # read tree from file or stdin pkl
    tre = read_tree_auto(
        resolve_input_arg(args.input), internal_labels=args.internal_labels
    )
    if args.ladderize:
        tre = tre.mod.ladderize(inplace=False)

    # print warning that style/view/out ignored if ASCII
    render_graphic = bool(args.output or args.view)
    if args.ascii:
        render_graphic = False
    if not render_graphic:
        if args.format is not None:
            print(
                "draw: --format ignored in ASCII mode (no --output/--view).",
                file=sys.stderr,
            )
        tre.treenode.draw_ascii()
        return 0

    # parse dict-style cli inputs
    node_style = _parse_style_kv(args.node_style, "--node-style")
    edge_style = _parse_style_kv(args.edge_style, "--edge-style")
    tip_labels_style = _parse_style_kv(args.tip_labels_style, "--tip-labels-style")

    # create tree drawing
    canvas, axes, mark = tre.draw(
        height=args.height,
        width=args.width,
        padding=args.padding,
        tree_style=args.tree_style,
        layout=args.layout,
        scale_bar=args.scale_bar,
        use_edge_lengths=args.use_edge_lengths,
        node_mask=args.node_mask,
        tip_labels=args.tip_labels,
        tip_labels_align=args.tip_labels_align,
        tip_labels_colors=_scalar_or_list(args.tip_labels_colors),
        node_sizes=_scalar_or_list(args.node_sizes),
        node_colors=_scalar_or_list(args.node_colors),
        node_labels=args.node_labels,
        edge_widths=_scalar_or_list(args.edge_widths),
        edge_colors=_scalar_or_list(args.edge_colors),
        edge_type=args.edge_type,
        node_style=node_style,
        edge_style=edge_style,
        tip_labels_style=tip_labels_style,
    )
    canvas.style["background-color"] = "white"

    # save to file
    fmt = args.format or "pdf"
    suffix = "." + fmt.lower()
    if args.output:
        prefix = Path(args.output)
        if not prefix.name:
            prefix = prefix / "toytree"
        out = Path(f"{prefix}").with_suffix(suffix)
    else:
        out = tempfile.NamedTemporaryFile(prefix="toytree-", suffix=suffix, delete=False)
        out = out.name
    save(canvas, out)

    # open saved tree drawing in default viewer
    if args.view:
        open_with_default_viewer(out)
    return 0
