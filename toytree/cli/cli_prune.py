#!/usr/bin/env python

"""Command line interface to prune method
"""

# from typing import List
import sys
import textwrap
from pathlib import Path
from argparse import ArgumentParser, RawDescriptionHelpFormatter
# from loguru import logger
from .make_wide import make_wide


KWARGS = dict(
    prog="prune",
    usage="prune [options]",
    help="return tree connecting only the selected tip names",
    formatter_class=make_wide(RawDescriptionHelpFormatter, 120, 140),
    description=textwrap.dedent("""
        -------------------------------------------------------------------
        | prune: return tree with only branches connecting a subset of tips
        -------------------------------------------------------------------
        | The prune method returns a tree with a subset of queried Nodes
        | along with the minimal spanning edges required to connect them.
        | Nodes can be queried as individual arguments or as a set of
        | indices, e.g. prune([0,1,2]). When called on a rooted tree, the
        | user can require the originial root to be retained in the pruned
        | tree using --require-root. By default, this is False and the
        | lowest MRCA connecting the queried Nodes is instead be kept as
        | the new root. When internal Nodes are discarded by prune their
        | distances will be merged into the distance of the queried Node
        | such that the original distance between the root and the queried
        | Node remains the same. If not --preserve-dists, then only the
        | original distances assigned to the queried Nodes are retained.
        -------------------------------------------------------------------
    """),
    epilog=textwrap.dedent("""
        Examples
        --------
        $ prune -i TREE.nwk -n A B C D > PRUNED.nwk
        $ prune -i TREE.nwk -n A B C D --preserve-dists --require-root > PRUNED.nwk
        $ prune -i TREE.nwk -n A B C D -o PRUNED.nwk
        $ prune -i TREE.nwk -n '~prefixA' '~prefixB' > PRUNED.nwk
    """)
)



def string_or_stdin_parse(intree: str) -> str:
    """If TREE is stdin then return the string from stdin."""
    if intree == "-":
        return sys.stdin.read().strip()
    return intree


def get_parser_prune(parser: ArgumentParser | None = None) -> ArgumentParser:
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
    parser.add_argument("-i", "--input", type=string_or_stdin_parse, metavar="path", required=True, help="input CDS sequence (aligned or unaligned)")
    parser.add_argument("-o", "--output", type=Path, metavar="path", help="optional outfile path name. If None prints to STDOUT")
    parser.add_argument("-n", "--nodes", type=str, metavar="str", nargs="*", help="One or more names or regular expressions to select nodes")
    # options
    parser.add_argument("-r", "--require-root", action="store_true", help="keep root node even if unary after pruning children")
    parser.add_argument("-p", "--not-preserve-dists", action="store_true", help="if not preserved then children do not inherit parent dists")
    parser.add_argument("-I", "--internal-labels", type=str, metavar="str", help="parse internal node feature (e.g., support) [auto]")
    parser.add_argument("-x", "--exclude-features", action="store_true", help="do not preserve node feature data")
    # parser.add_argument("-f", "--force", action="store_true", help="overwrite existing result files in outdir")
    # parser.add_argument("-l", "--log-level", type=str, metavar="level", default="INFO", help="stderr logging level (DEBUG, [INFO], WARNING, ERROR)")
    # parser.add_argument("-L", "--log-file", type=Path, metavar="path", help="append stderr log to a file")
    return parser


def run_prune(args):
    from toytree.io.src.treeio import tree
    from toytree.mod._src.mod_topo import prune

    # parse the tree
    if args.input == Path("-"):
        data = sys.stdin.read()
        tre = tree(data, internal_labels=args.internal_labels)
    else:
        tre = tree(args.input, internal_labels=args.internal_labels)

    # operate
    tre = prune(tre, *args.nodes, preserve_dists=(not args.not_preserve_dists), require_root=args.require_root)

    # write tree with or wi/o feature data
    if args.exclude_features:
        features = None
    else:
        features = set(tre.features) - {'name', 'height', 'dist', 'support'}
    if args.output:
        tre.write(args.output, features=features)
    else:
        sys.stdout.write(tre.write(None, features=features) + "\n")


def main():
    parser = get_parser_prune()
    args = parser.parse_args()
    run_prune(args)


if __name__ == "__main__":

    try:
        main()
    except Exception as exc:
        raise exc
