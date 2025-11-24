#!/usr/bin/env python

from pathlib import Path
import sys
import textwrap
import tempfile
import os
import platform
import subprocess
import shutil
import webbrowser
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from .make_wide import make_wide
from loguru import logger


KWARGS = dict(
    prog="draw",
    usage="draw [options]",
    help="return ...",
    formatter_class=make_wide(RawDescriptionHelpFormatter, 120, 140),
    description=textwrap.dedent("""
        -------------------------------------------------------------------
        | draw: generate tree drawing as ascii or ...
        -------------------------------------------------------------------
        | The draw method generates a tree drawing in a variety of formats
        | and with many styling options.
        -------------------------------------------------------------------
    """),
    epilog=textwrap.dedent("""
        Examples
        --------
        $ draw -i TRE.nwk -a
        $ draw -i TRE.nwk -f png -v
        $ draw -i TRE.nwk -f html -v -k ...
        $ draw -i TRE.nwk -f pdf -o /tmp/DRAWING
        $ draw -i TRE.nwk -v -N fill=red -E stroke=pink -T font-size=10px
        $ root -i TRE.nwk -n R | draw -i - -v
    """)
)


def get_parser_draw(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return a parser tool for this method.
    """
    # create parser or connect as subparser to cli parser
    if parser:
        KWARGS['name'] = KWARGS.pop("prog")
        parser = parser.add_parser(**KWARGS)
    else:
        KWARGS.pop("help")
        parser = ArgumentParser(**KWARGS)

    # path args
    parser.add_argument("-i", "--input", type=Path, metavar="path", required=True, help="input tree file (nwk, nex or nhx)")
    parser.add_argument("-o", "--output", type=Path, metavar="path", help="optional basename of outfile path. If None prints to STDOUT")
    # option
    parser.add_argument("-a", "--ascii", action="store_true", help="print ascii tree (overrides other draw args)")
    parser.add_argument("-f", "--format", choices=["html", "svg", "pdf", "png"], default="png", help="file format of drawing [png]")
    parser.add_argument("-v", "--view", type=str, metavar="app", const="auto", nargs="?", help="open drawing in default viewer, or provide an app name")
    parser.add_argument("-e", "--ladderize", action="store_true", help="ladderize the tree")
    parser.add_argument("-k", "--kwargs", type=str, metavar="str", nargs="*", help="any supported toytree.draw kwargs as 'key=val'")
    parser.add_argument("-I", "--internal-labels", type=str, metavar="str", help="parse internal node feature (e.g., support) [auto]")
    parser.add_argument("-l", "--log-level", type=str, metavar="level", default="INFO", help="stderr logging level (DEBUG, [INFO], WARNING, ERROR)")

    parser.add_argument("-ts", "--tree-style", type=str, metavar="str", help="base tree style [[None], 'r', 'c', 's', 'o', 'b']")
    parser.add_argument("-N", "--node-style", type=str, metavar="str", nargs="+", help="node style args")
    parser.add_argument("-E", "--edge-style", type=str, metavar="str", nargs="+", help="edge style args")
    parser.add_argument("-T", "--tip-labels-style", type=str, metavar="str", nargs="+", help="tip labels style args")
    parser.add_argument("-ns", "--node-sizes", type=int, metavar="int", nargs="+", default=[6], help="node sizes")
    parser.add_argument("-nc", "--node-colors", type=str, metavar="str", nargs="+", default=["#262626"], help="node colors")
    parser.add_argument("-tl", "--tip-labels-align", type=bool, metavar="bool", nargs="+", help="align tip labels")
    # parser.add_argument("-L", "--log-file", type=Path, metavar="path", help="append stderr log to a file")
    return parser



def open_with_default_viewer(path: str) -> bool:
    """Try to open a file with the system's default app.
    Returns True on (likely) success, False if we had no good option.
    """
    path = os.path.abspath(path)
    system = platform.system()

    try:
        if system == "Windows":
            # Uses the file association in the registry
            os.startfile(path)  # type: ignore[attr-defined]
            return True

        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", path])
            return True

        else:
            # Most Linux/Unix desktops support xdg-open
            opener = (
                shutil.which("xdg-open")
                or shutil.which("gio")
                or shutil.which("gnome-open")
                or shutil.which("kde-open")
            )
            if opener:
                subprocess.Popen([opener, path])
                return True

        # Fallback: try the webbrowser module
        file_url = f"file://{path}"
        if webbrowser.open(file_url):
            return True

    except Exception:
        # You might want to log this if you have logging set up
        logger.bind(name="toytree").error("could not find a default viewer to open drawing file")
    return False



def run_draw(args):
    from toytree import save
    from toytree.io.src.treeio import tree
    # from toytree.utils.src.logger_setup import set_log_level
    # set_log_level(args.log_level)

    # parse the tree
    if args.input == Path("-"):
        data = sys.stdin.read()
        tre = tree(data, internal_labels=args.internal_labels)
    else:
        data = args.input.expanduser().absolute()
        tre = tree(data, internal_labels=args.internal_labels)

    # ascii tree drawing
    if args.ascii:
        print(tre.treenode.draw_ascii(), sys.stdout)
        return 0

    # create drawing
    # if args.kwargs:
    #     print(args.kwargs)
    #     kwargs = dict(tuple(i.split("=")) for i in args.kwargs)
    # else:
    #     kwargs = {}
    canvas, axes, mark = tre.draw(
        tree_style=args.tree_style,
        node_style=dict(tuple(i.split("=") for i in args.node_style)) if args.node_style else {},
        edge_style=dict(tuple(i.split("=") for i in args.edge_style)) if args.edge_style else {},
        tip_labels_style=dict(tuple(i.split("=") for i in args.tip_labels_style)) if args.tip_labels_style else {},
        node_sizes=args.node_sizes if len(args.node_sizes) > 1 else args.node_sizes[0],
        # node_colors=args.node_colors if len(args.node_colors) > 1 else args.node_colors[0],
        # tip_labels_align=args.tip_labels_align,
        # **kwargs
    )
    canvas.style["background-color"] = "white"

    # write file to tmp or named file
    suffix = "." + args.format.lower()
    if args.output:
        prefix = Path(args.output)
        if not prefix.name:
            prefix = prefix / "toytree"
        out = Path(f"{prefix}").with_suffix(suffix)
    else:
        out = tempfile.NamedTemporaryFile(prefix="toytree", suffix=suffix, delete=False)
        out = out.name
    save(canvas, out)

    # optionally view the file
    if args.view:
        open_with_default_viewer(out)


def main():
    parser = get_parser_draw()
    args = parser.parse_args()
    run_draw(args)


if __name__ == "__main__":
    try:
        main()
    # except ToytreeError as exc:
    #     logger.bind(name="toytree").error(exc)
    except Exception as exc:
        logger.bind(name="toytree").exception(exc)
