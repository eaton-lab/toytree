#!/usr/bin/env python

"""CLI for making trees ultrametric."""

import sys
import textwrap
from pathlib import Path
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter
import re


KWARGS = dict(
    prog="make-ultrametric",
    usage="make-ultrametric [options]",
    help="make a tree ultrametric using fast or penalized-likelihood methods",
    formatter_class=lambda prog: RawDescriptionHelpFormatter(
        prog, width=130, max_help_position=36
    ),
    description=textwrap.dedent(
        """
        -------------------------------------------------------------------------
        | make-ultrametric: transform a tree to ultrametric branch lengths
        -------------------------------------------------------------------------
        | method=extend      : fast tip-extension alignment.
        | method=clock       : strict-clock penalized-likelihood fit.
        | method=discrete    : ncat rate classes penalized-likelihood fit.
        | method=relaxed     : uncorrelated relaxed-clock penalized-likelihood fit.
        | method=correlated  : correlated relaxed-clock penalized-likelihood fit.
        -------------------------------------------------------------------------
        """
    ),
    epilog=textwrap.dedent(
        """
        Examples
        --------
        $ make-ultrametric -i TREE.nwk -m extend > UTREE.nwk
        $ make-ultrametric -i TREE.nwk -m clock -c -1=1.0 > UTREE.nwk
        $ make-ultrametric -i TREE.nwk -m discrete --ncat 3 -c -1=1.0 > UTREE.nwk
        $ make-ultrametric -i TREE.nwk -m relaxed --lam 0.5 -c -1=1.0 > UTREE.nwk
        $ make-ultrametric -i TREE.nwk -m correlated --lam 0.5 -c -1=1.0 > UTREE.nwk
        $ make-ultrametric -i TREE.nwk -m correlated --lam 0.5 --nstarts 8 --ncores 4 --seed 123 > UTREE.nwk
        $ make-ultrametric -i TREE.nwk -m discrete --estimate 5 -c -1=1.0 > UTREE.nwk
        $ make-ultrametric -i TREE.nwk -m clock -c AB=0.8-1.2 CD=0.4
        $ cat TREE.nwk | make-ultrametric -i - --method extend
        $ make-ultrametric -i TREE.nwk -m relaxed -b | root -i - --mad > UTREE.nwk
        """
    ),
)

NEGATIVE_CAL_QUERY_PREFIX = "__toytree_negidx__"


def normalize_calibration_argv(argv: list[str]) -> list[str]:
    """Protect calibration tokens like '-1=10' from argparse option parsing."""
    out: list[str] = []
    in_cal_block = False
    for tok in argv:
        if tok in {"-c", "--calibrations"}:
            in_cal_block = True
            out.append(tok)
            continue

        if tok.startswith("--calibrations="):
            value = tok.split("=", 1)[1]
            if re.match(r"^-\d+=", value):
                value = NEGATIVE_CAL_QUERY_PREFIX + value[1:]
                out.append(f"--calibrations={value}")
            else:
                out.append(tok)
            in_cal_block = False
            continue

        if in_cal_block:
            if tok.startswith("-") and (not re.match(r"^-\d+=", tok)):
                in_cal_block = False
                out.append(tok)
                continue
            if re.match(r"^-\d+=", tok):
                out.append(NEGATIVE_CAL_QUERY_PREFIX + tok[1:])
            else:
                out.append(tok)
            continue

        out.append(tok)
    return out


def _parse_calibration_value(text: str):
    """Parse calibration value as float or (float, float) range."""
    text = text.strip()
    rng = re.match(
        r"^([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*-\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)$",
        text,
    )
    if rng:
        low = float(rng.group(1))
        high = float(rng.group(2))
        if low > high:
            raise ValueError(f"invalid calibration range '{text}' (min > max)")
        return (low, high)
    return float(text)


def _parse_calibrations(tree, items: list[str] | None) -> dict[int, float | tuple[float, float]]:
    """Parse calibration args as query=value or query=min-max."""
    if not items:
        return {}
    calibrations = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"calibration must be query=value or query=min-max, got: '{item}'")
        query, value = item.split("=", 1)
        query = query.strip()
        value = value.strip()
        if query.startswith(NEGATIVE_CAL_QUERY_PREFIX):
            query = "-" + query.removeprefix(NEGATIVE_CAL_QUERY_PREFIX)
        if not query or not value:
            raise ValueError(f"invalid calibration entry: '{item}'")

        try:
            selector = int(query)
        except ValueError:
            selector = query
        nodes = tree.get_nodes(selector)
        if len(nodes) != 1:
            raise ValueError(
                f"calibration query '{query}' matched {len(nodes)} nodes; must match exactly one node."
            )
        calibrations[nodes[0].idx] = _parse_calibration_value(value)
    return calibrations


def get_parser_make_ultrametric(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for make-ultrametric command."""
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
        help="input tree (path/URL/Newick), or '-' for stdin",
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="path",
        help="output path; default writes to stdout",
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

    method_group = p.add_argument_group(title="Method")
    method_group.add_argument(
        "-m",
        "--method",
        type=str,
        default="extend",
        choices=("extend", "clock", "discrete", "relaxed", "correlated"),
        metavar="method",
        help="method: extend|clock|discrete|relaxed|correlated [extend]",
    )
    method_group.add_argument(
        "-c",
        "--calibrations",
        type=str,
        nargs="*",
        metavar="query=value",
        help="clock/discrete/relaxed/correlated: one or more query=value or query=min-max entries",
    )
    method_group.add_argument(
        "--ncat",
        type=int,
        default=None,
        metavar="int",
        help="discrete only: number of rate categories (required unless --estimate is set)",
    )
    method_group.add_argument(
        "--lam",
        type=float,
        default=None,
        metavar="float",
        help="relaxed/correlated only: penalty lambda; lower=weaker regularization [1.0]",
    )
    method_group.add_argument(
        "--estimate",
        type=int,
        default=None,
        metavar="int",
        help="estimate ncat/lam by PHIIC using this many candidate values",
    )

    opt_group = p.add_argument_group(title="Optimization")
    opt_group.add_argument(
        "--max-iter",
        type=int,
        default=100_000,
        metavar="int",
        help="PL only: max optimizer iterations [100000]",
    )
    opt_group.add_argument(
        "--max-fun",
        type=int,
        default=100_000,
        metavar="int",
        help="PL only: max optimizer function evaluations [100000]",
    )
    opt_group.add_argument(
        "--max-refine",
        type=int,
        default=20,
        metavar="int",
        help="PL only: max alternating refinement rounds [20]",
    )
    opt_group.add_argument(
        "--nstarts",
        type=int,
        default=1,
        metavar="int",
        help="PL only: number of starts; best fit retained [1]",
    )
    opt_group.add_argument(
        "--ncores",
        type=int,
        default=1,
        metavar="int",
        help="PL only: worker processes for multistart [1]",
    )
    opt_group.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="int",
        help="PL only: random seed for reproducible multistart",
    )
    opt_group.add_argument(
        "--full",
        action="store_true",
        help="PL only: print model-fit summary fields to stderr",
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


def run_make_ultrametric(args):
    """Run make-ultrametric command."""
    from toytree.cli._tree_transport import read_tree_auto, write_tree_output
    from toytree.utils import ToytreeError
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)
    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)
    calibrations = _parse_calibrations(tre, args.calibrations)
    if args.lam is not None and args.lam < 0:
        raise ToytreeError("--lam must be >= 0.")
    force_full = bool(args.full or (args.estimate is not None))
    if args.method == "discrete" and args.estimate is None and args.ncat is None:
        raise ToytreeError("--ncat is required when --method discrete is used without --estimate.")

    result = tre.mod.edges_make_ultrametric(
        method=args.method,
        calibrations=calibrations,
        ncategories=None if args.ncat is None else int(args.ncat),
        lam=args.lam,
        full=force_full,
        inplace=False,
        max_iter=args.max_iter,
        max_fun=args.max_fun,
        max_refine=args.max_refine,
        nstarts=args.nstarts,
        ncores=args.ncores,
        seed=args.seed,
        estimate=args.estimate,
    )
    if force_full:
        if args.estimate is not None:
            for rec in result.get("search", []):
                cand = rec.get("candidate")
                phiic = rec.get("PHIIC")
                conv = rec.get("converged")
                print(f"estimate candidate={cand} PHIIC={phiic} converged={conv}", file=sys.stderr)
            print(
                f"estimated_parameter={result.get('estimated_parameter')} estimated_value={result.get('estimated_value')}",
                file=sys.stderr,
            )
        if args.full:
            for key, val in result.items():
                if key != "tree":
                    print(f"{key}={val}", file=sys.stderr)
        tre = result["tree"]
    else:
        tre = result

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
    parser = get_parser_make_ultrametric()
    args = parser.parse_args(normalize_calibration_argv(sys.argv[1:]))
    run_make_ultrametric(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise exc
