#!/usr/bin/env python

"""Command line interface to prune method
"""

# from typing import List
import textwrap
from pathlib import Path
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter


KWARGS = dict(
    prog="prune",
    usage="prune [options]",
    help="return tree connecting only the selected tip names",
    formatter_class=lambda prog: RawDescriptionHelpFormatter(prog, width=120, max_help_position=120),
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
        $ prune -i TREE.nwk -n A B -b | set-node-data -i - -f score -s a=1 b=2 > OUT.nwk
    """)
)



def get_parser_prune(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return a parser tool for this method.
    """
    # create parser or connect as subparser to cli parser
    if parser:
        kwargs = dict(KWARGS)
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        parser = parser.add_parser(**kwargs)
    else:
        kwargs = dict(KWARGS)
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        parser = ArgumentParser(**kwargs)

    io_group = parser.add_argument_group(title="Input / Output")
    io_group.add_argument("-i", "--input", type=str, metavar="path", required=True, help="input tree path/url/newick string, or '-' for stdin")
    io_group.add_argument("-o", "--output", type=Path, metavar="path", help="optional outfile path name. If None prints to STDOUT")
    io_group.add_argument("-b", "--binary-out", action="store_true", help="write output as binary pickled ToyTree for fast piping between commands")
    io_group.add_argument("-I", "--internal-labels", type=str, metavar="str", help="Parse internal labels as this feature (overrides auto-detect)")
    io_group.add_argument("-x", "--exclude-features", action="store_true", help="do not preserve node feature data")

    edit_group = parser.add_argument_group(title="Prune")
    edit_group.add_argument("-n", "--nodes", type=str, metavar="str", nargs="*", help="One or more names or regular expressions to select nodes")
    edit_group.add_argument("-r", "--require-root", action="store_true", help="keep root node even if unary after pruning children")
    edit_group.add_argument("-p", "--not-preserve-dists", action="store_true", help="if not preserved then children do not inherit parent dists")
    options_group = parser.add_argument_group(title="Options")
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
    return parser


def run_prune(args):
    from toytree.cli._tree_transport import read_tree_auto, write_tree_output
    from toytree.mod._src.mod_topo import prune
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    # parse the tree
    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)

    # operate
    tre = prune(tre, *args.nodes, preserve_dists=(not args.not_preserve_dists), require_root=args.require_root)

    # write tree with or wi/o feature data
    if args.exclude_features:
        features = None
    else:
        features = set(tre.features) - {'name', 'height', 'dist', 'support'}
    write_tree_output(
        tre,
        output=args.output,
        binary_out=args.binary_out,
        features=features,
    )


def main():
    parser = get_parser_prune()
    args = parser.parse_args()
    run_prune(args)


if __name__ == "__main__":

    try:
        main()
    except Exception as exc:
        raise exc
