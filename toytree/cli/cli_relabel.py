#!/usr/bin/env python

import textwrap
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from typing import Any, Callable


KWARGS = dict(
    prog="relabel",
    usage="relabel [options]",
    help="relabel node name features for all nodes or selected subsets",
    formatter_class=lambda prog: RawDescriptionHelpFormatter(
        prog, width=120, max_help_position=120
    ),
    description=textwrap.dedent(
        """
        -------------------------------------------------------------------
        | relabel: transform node name features using query and text rules
        -------------------------------------------------------------------
        | Apply delimiter parsing, built-in transforms, prepend/append, and
        | optional italic/bold wrappers to tip names or selected nodes.
        -------------------------------------------------------------------
        """
    ),
    epilog=textwrap.dedent(
        """
        Examples
        --------
        $ relabel -i TRE.nwk --strip '_-'
        $ relabel -i TRE.nwk --delim '|' --delim-idxs 0 2 --delim-join '_'
        $ relabel -i TRE.nwk -n '~^DE' --append '_X'
        $ relabel -i TRE.nwk --prepend 'sp_' --stripleft '._'
        $ relabel -i TRE.nwk --italic --bold
        $ relabel -i TRE.nwk --strip '_-' -b | draw -i - -a
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


def get_parser_relabel(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for relabel command."""
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
        help="input tree file/path/url/newick string, or '-' for stdin",
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="path",
        help="optional output file path; default writes to stdout",
    )
    io_group.add_argument(
        "-b",
        "--binary-out",
        action="store_true",
        help="write output as binary pickled ToyTree for fast piping between commands",
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="Parse internal labels as this feature (overrides auto-detect)",
    )
    io_group.add_argument(
        "-x",
        "--exclude-features",
        action="store_true",
        help="omit non-default node features from output Newick",
    )

    relabel_group = p.add_argument_group(title="Relabeling")
    relabel_group.add_argument(
        "-n",
        "--nodes",
        type=str,
        nargs="*",
        metavar="query",
        help="optional node queries (idx/name/regex) to relabel",
    )
    relabel_group.add_argument(
        "--tips-only",
        type=parse_bool,
        nargs="?",
        const=True,
        default=True,
        metavar="bool",
        help="relabel only tips (true/false) [default: true]",
    )
    relabel_group.add_argument("--delim", type=str, metavar="str", help="delimiter for splitting names")
    relabel_group.add_argument(
        "--delim-idxs",
        type=int,
        nargs="+",
        metavar="int",
        help="split part indices to keep",
    )
    relabel_group.add_argument(
        "--delim-join",
        type=str,
        default="_",
        metavar="str",
        help="join string for selected split parts [_]",
    )
    relabel_group.add_argument("--strip", type=str, metavar="str", help="strip chars from both ends")
    relabel_group.add_argument("--stripleft", type=str, metavar="str", help="strip chars from left side only")
    relabel_group.add_argument("--prepend", type=str, metavar="str", help="prepend constant string")
    relabel_group.add_argument("--append", type=str, metavar="str", help="append constant string")
    relabel_group.add_argument(
        "--italic",
        action="store_true",
        help="wrap names in <i>...</i>",
    )
    relabel_group.add_argument(
        "--bold",
        action="store_true",
        help="wrap names in <b>...</b>",
    )

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


def run_relabel(args):
    """Run relabel command."""
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


def main():
    parser = get_parser_relabel()
    args = parser.parse_args()
    run_relabel(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise exc
