#!/usr/bin/env python

from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
import sys
import tempfile
import textwrap
import re
from typing import Any


KWARGS = dict(
    prog="draw",
    usage="draw [options]",
    help="draw tree as ascii or graphic",
    formatter_class=lambda prog: RawDescriptionHelpFormatter(
        prog, width=120, max_help_position=120
    ),
    description=textwrap.dedent(
        """
        -------------------------------------------------------------------
        | draw: generate tree drawing as ascii or graphics
        -------------------------------------------------------------------
        | Default mode prints an ASCII tree to stdout.
        | Use --output and/or --view to render graphic output to html,
        | svg, pdf, or png and optionally open for viewing. Apply tree
        | drawing styles or use built-in styles with --treestyle.
        -------------------------------------------------------------------
        """
    ),
    epilog=textwrap.dedent(
        """
        Examples
        --------
        $ draw -i TRE.nwk
        $ draw -i TRE.nwk --output tree.svg
        $ draw -i TRE.nwk -f png --view
        $ draw -i TRE.nwk -f html -v -ts c
        $ draw -i TRE.nwk -f pdf -o /tmp/DRAWING -ns 8 -nc teal -ta true
        $ draw -i TRE.nwk -v -ta
        $ draw -i TRE.nwk -v -ta false
        $ draw -i TRE.nwk -v -N fill=red -E stroke=pink -T font-size=10px fill=blue
        $ root -i TRE.nwk -n R | draw -i - -v
        """
    ),
)


def parse_bool(value: Any) -> bool:
    """Parse bool-like CLI values."""
    if isinstance(value, bool):
        return value
    sval = str(value).strip().lower()
    if sval in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if sval in {"0", "false", "f", "no", "n", "off"}:
        return False
    raise ValueError(f"invalid boolean value: {value}")


def parse_node_mask(value: Any) -> bool | tuple[bool, bool, bool]:
    """Parse node-mask CLI values.

    Accepts:
    - bool-like strings: true/false, 1/0, yes/no
    - 3-value binary tuple/list text: (1,0,1), [1, 0, 1], 1,0,1
    """
    if isinstance(value, bool):
        return value
    sval = str(value).strip()

    # bool mode
    try:
        return parse_bool(sval)
    except ValueError:
        pass

    # tuple/list mode
    if (sval.startswith("(") and sval.endswith(")")) or (sval.startswith("[") and sval.endswith("]")):
        sval = sval[1:-1].strip()
    parts = [i for i in re.split(r"[\s,]+", sval) if i]
    if len(parts) != 3:
        raise ValueError(
            "invalid node mask. Use true/false or a 3-value binary tuple/list like '(1,0,1)'."
        )
    if any(i not in {"0", "1"} for i in parts):
        raise ValueError("node-mask tuple/list values must be binary 0/1.")
    return tuple(bool(int(i)) for i in parts)


def _scalar_or_list(values):
    """Return scalar for single-value lists, otherwise list, or None."""
    if values is None:
        return None
    return values if len(values) > 1 else values[0]


def _parse_style_kv(values, argname: str) -> dict[str, str]:
    """Parse repeated key=value style args into a dict."""
    if not values:
        return {}
    style = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"{argname} expects key=value entries, got: '{item}'")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"{argname} has empty key in '{item}'")
        style[key] = value
    return style


def get_parser_draw(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for draw command."""
    if parser:
        kwargs = dict(KWARGS)
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs = dict(KWARGS)
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        required=True,
        help="input tree file (nwk, nex, nhx), Newick string, or stdin (-)",
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="path",
        help="output path. If omitted, ASCII is printed to stdout",
    )
    io_group.add_argument(
        "-f",
        "--format",
        choices=["html", "svg", "pdf", "png"],
        default=None,
        help="graphic output format [pdf]",
    )
    io_group.add_argument(
        "-v",
        "--view",
        type=str,
        metavar="app",
        const="auto",
        nargs="?",
        help="open rendered graphic in default viewer, or provided app name",
    )
    io_group.add_argument("-I", "--internal-labels", type=str, metavar="str", help="Parse internal labels as this feature (overrides auto-detect)")

    render_group = p.add_argument_group(title="Render Mode")
    render_group.add_argument(
        "-a",
        "--ascii",
        action="store_true",
        help="force ASCII output (overrides graphic rendering)",
    )
    render_group.add_argument(
        "-e", "--ladderize", action="store_true", help="ladderize tree before drawing"
    )

    layout_group = p.add_argument_group(title="Layout")
    layout_group.add_argument("-wi", "--width", type=int, metavar="int", help="width in pixels")
    layout_group.add_argument("-he", "--height", type=int, metavar="int", help="height in pixels")
    layout_group.add_argument("-la", "--layout", type=str, metavar="str", help="layout ['r', 'l', 'u', 'd', 'c', 'c0-180', 'un']")
    layout_group.add_argument("-ts", "--tree-style", type=str, metavar="str", help="base tree style ['n', 'r', 'c', 's', 'o', 'b']")
    layout_group.add_argument("-pa", "--padding", type=float, metavar="float", help="canvas padding in pixels")
    layout_group.add_argument(
        "-sb",
        "--scale-bar",
        type=parse_bool,
        metavar="bool",
        nargs="?",
        const=True,
        help="draw scale bar (true/false) [default: auto]",
    )
    layout_group.add_argument(
        "-ue",
        "--use-edge-lengths",
        type=parse_bool,
        metavar="bool",
        nargs="?",
        const=True,
        help="use edge lengths (true/false) [default: auto]",
    )

    node_group = p.add_argument_group(title="Node Style")
    node_group.add_argument("-nm", "--node-mask", type=parse_node_mask, metavar="bool|a,b,c", help="node mask: true/false or 3-value binary tuple for (tips,internal,root)")
    node_group.add_argument("-ns", "--node-sizes", type=float, metavar="float", nargs="+", help="node sizes (scalar or list)")
    node_group.add_argument("-nc", "--node-colors", type=str, metavar="str", nargs="+", help="node colors (scalar or list)")
    node_group.add_argument("-nl", "--node-labels", type=str, metavar="str", help="node labels feature or literal")
    node_group.add_argument("-N", "--node-style", type=str, metavar="str", nargs="+", help="node style key=value args")

    edge_group = p.add_argument_group(title="Edge Style")
    edge_group.add_argument("-et", "--edge-type", type=str, metavar="str", choices=["p", "c", "b"], help="edge type ([p]hylogram, [c]ladogram, [b]ezier)")
    edge_group.add_argument("-ew", "--edge-widths", type=float, metavar="float", nargs="+", help="edge widths (scalar or list)")
    edge_group.add_argument("-ec", "--edge-colors", type=str, metavar="str", nargs="+", help="edge colors (scalar or list)")
    edge_group.add_argument("-E", "--edge-style", type=str, metavar="str", nargs="+", help="edge style key=value args")

    label_group = p.add_argument_group(title="Label Style")
    label_group.add_argument(
        "-tl",
        "--tip-labels",
        type=parse_bool,
        metavar="bool",
        nargs="?",
        const=True,
        help="draw tip labels (true/false) [default: auto]",
    )
    label_group.add_argument(
        "-ta",
        "--tip-labels-align",
        type=parse_bool,
        metavar="bool",
        nargs="?",
        const=True,
        help="align tip labels (true/false) [default: auto]",
    )
    label_group.add_argument("-tc", "--tip-labels-colors", type=str, metavar="str", nargs="+", help="tip-label colors (scalar or list)")
    label_group.add_argument("-T", "--tip-labels-style", type=str, metavar="str", nargs="+", help="tip-label style key=value args")

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-l",
        "--log-level",
        type=str,
        metavar="level",
        default=None,
        help="set toytree logger level (DEBUG, INFO, WARNING, ERROR)",
    )
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    return p


def open_with_default_viewer(path: str) -> bool:
    """Try to open a file with the system's default app."""
    import os
    import platform
    import subprocess
    import shutil
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
    from toytree.cli._tree_transport import read_tree_auto
    from toytree import save
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)
    if args.ladderize:
        tre = tre.mod.ladderize(inplace=False)

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

    node_style = _parse_style_kv(args.node_style, "--node-style")
    edge_style = _parse_style_kv(args.edge_style, "--edge-style")
    tip_labels_style = _parse_style_kv(args.tip_labels_style, "--tip-labels-style")

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

    if args.view:
        open_with_default_viewer(out)
    return 0


def main():
    parser = get_parser_draw()
    args = parser.parse_args()
    run_draw(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise exc
