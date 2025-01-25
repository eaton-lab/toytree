#!/usr/bin/env python

"""Simple command line tool for viewing trees in browser.

Commands
>>> toytree draw [options] STDIN              # return as HTML
>>> toytree root [options] STDIN              # root and return to nwk
>>> toytree distance [options] STDIN1 STDIN2  # compare trees
>>> toytree io [options] STDIN                # read/write to nwk

Chain commands
>>> toytree root -o A B C $file | toytree draw - -o /tmp/tree.html
>>> toytree draw -o /tmp/test.html -ts p '((a,b),c)'
>>> toytree root \
>>>   https://eaton-lab.org/data/Cyathophora.tre -o "prz*" -r | \
>>>   toytree draw -v -ts o -
"""

from typing import Optional
import argparse
import sys
import tempfile
import subprocess
from pathlib import Path
import toytree

TMPFILE = Path(tempfile.gettempdir()) / "test"
DESCRIPTION = "toytree command line tool. Select a subcommand."
EPILOG = "EXAMPLE:\n$ toytree draw TREE -ts o -d 400 400 -v"


def string_or_stdin_parse(intree) -> str:
    """If TREE is stdin then return the string from stdin."""
    if intree == "-":
        return sys.stdin.read().strip()
    return intree


def setup_parsers() -> argparse.ArgumentParser:
    """Setup and return an ArgumentParser w/ subcommands."""
    parser = argparse.ArgumentParser(
        prog="toytree",
        description=DESCRIPTION,
        epilog=EPILOG,
    )
    parser.add_argument("-v", "--version", action='version', version=f"toytree {toytree.__version__}")
    subparsers = parser.add_subparsers(help="sub-commands", dest="subcommand")

    # toytree draw [options] TREE --------------------------------------------
    parser_draw = subparsers.add_parser(
        "draw", 
        help="create tree drawing",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_draw.add_argument(
        "-ts", type=str, default="n", metavar="treestyle", help="tree style",
    )
    parser_draw.add_argument(
        "-d", type=int, metavar="dim", nargs=2, default=(None, None),
        help="width height (px)",
    )
    parser_draw.add_argument(
        "-o", type=Path, metavar="basename", default=TMPFILE,
        help="output basename[.format suffix]",
    )
    parser_draw.add_argument(
        "-v", type=str, metavar="app", nargs="?", const="auto",
        help="open file with default browser or app.",
    )
    parser_draw.add_argument(
        "-f", type=str, help="output file format", default="html",
        choices=["html", "svg", "pdf"]
    )
    parser_draw.add_argument(
        "TREE", type=string_or_stdin_parse, help="tree newick file or string",
    )

    # toytree root [options] TREE --------------------------------------------
    parser_root = subparsers.add_parser("root", help="(re)root tree and return to STDOUT")
    parser_root.add_argument("-o", type=str, nargs="+", default=(), help="outgroup")
    # parser_root.add_argument("-r", action="store_true", help="use regex matching on outgroup string.")
    parser_root.add_argument("TREE", type=str, help="tree newick file or string")

    # toytree distance [options] TREE TREE ----------------------------------
    parser_distance = subparsers.add_parser("distance", help="compute distance between trees")
    parser_distance.add_argument("TREE1", type=str, help="tree1 newick file or string")
    parser_distance.add_argument("TREE2", type=str, help="tree2 newick file or string")
    parser_distance.add_argument(
        "-m", type=str,
        choices=['rf', 'rfi', 'rfj', 'qrt'],
        default='rf',
        help="distance metric method",
    )
    parser_distance.add_argument(
        "-n", "--normalize", action="store_true",
        help="normalize value between [0-1]")
    return parser


def main(cmd: Optional[str] = None) -> int:
    """Command line tool."""
    parser = setup_parsers()
    args = parser.parse_args(cmd.split() if cmd else None)

    # root
    if args.subcommand == "root":
        tree = toytree.tree(args.TREE)
        tree = tree.root(*args.o)
        sys.stdout.write(tree.write(None))
        return 0

    # draw
    if args.subcommand == "draw":
        # print(args)
        tree = toytree.tree(args.TREE)
        width, height = args.d
        canvas, _, _ = tree.draw(tree_style=args.ts, width=width, height=height)
        canvas.style['background-color'] = "white"

        path = Path(args.o).with_suffix(f".{args.f}")
        if args.f == "html":
            import toyplot.html
            toyplot.html.render(canvas, str(path))
        if args.f == "svg":
            import toyplot.svg
            toyplot.svg.render(canvas, str(path))
        if args.f == "pdf":
            import toyplot.pdf
            toyplot.pdf.render(canvas, str(path))
        if args.v:
            if args.v == "auto":
                import webbrowser
                webbrowser.open(str(path))
            else:
                subprocess.run([str(args.v), str(path)], check=True)
        return 0

    # distance
    if args.subcommand == "distance":
        tree1 = toytree.tree(args.TREE1)
        tree2 = toytree.tree(args.TREE2)
        norm = {"normalize": args.normalize}
        if args.m == "rf":
            val = toytree.distance.get_treedist_rf(tree1, tree2, **norm)
        elif args.m == "rfg_mci":
            val = toytree.distance.get_treedist_rfg_mci(tree1, tree2, **norm)
        elif args.m == "rfg_spi":
            val = toytree.distance.get_treedist_rfg_spi(tree1, tree2, **norm)
        elif args.m == "rfi":
            val = toytree.distance.get_treedist_rfi(tree1, tree2, **norm)
        elif args.m == "qrt":
            val = toytree.distance.get_treedist_qrt(tree1, tree2)
        sys.stdout.write(val)
        return 0

    # unreachable
    parser.print_help()
    return 1


def test():
    parser = setup_parsers()
    # print(parser.parse_args(["--version"]))
    # print(parser.parse_args(["--help"]))
    # print(parser.parse_args("root ((a,b),c); -o a".split()))
    # print(parser.parse_args("root ((a,b),c);".split()))
    print(parser.parse_args("root -o a b ((a,b),c);".split()))
    # parser.parse_args(["root", "--help"])


if __name__ == "__main__":

    main()
