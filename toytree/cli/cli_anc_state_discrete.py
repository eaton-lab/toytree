#!/usr/bin/env python

"""Runtime implementation for the ``anc-state-discrete`` CLI command."""

from __future__ import annotations

import math
import sys


def _pack_posteriors(
    rows,
    *,
    sep: str,
    float_format: str,
):
    """Return packed posterior strings from iterable probability rows."""
    from toytree.utils import ToytreeError

    packed: list[str] = []
    for row in rows:
        values = []
        for value in row:
            try:
                values.append(float_format % float(value))
            except Exception as exc:  # pragma: no cover - invalid format string
                raise ToytreeError(
                    "invalid posterior float format "
                    f"{float_format!r} for value {value!r}"
                ) from exc
        packed.append(sep.join(values))
    return packed


def _print_fit_summary(
    *,
    feature: str,
    fit,
    nobs: int,
    posterior_mode: str,
    meta_base: str,
) -> None:
    """Print model-fit and reconstruction summary statistics to stderr."""
    log_likelihood = float(fit.log_likelihood)
    nparams = int(fit.nparams)
    aic = (2.0 * nparams) - (2.0 * log_likelihood)
    if (nobs - nparams - 1) > 0:
        aicc = aic + (2.0 * nparams * (nparams + 1.0)) / (nobs - nparams - 1.0)
    else:
        aicc = float("inf")
    bic = (
        (math.log(nobs) * nparams) - (2.0 * log_likelihood)
        if nobs > 0
        else float("nan")
    )

    print(f"feature={feature}", file=sys.stderr)
    print(f"meta_base={meta_base}", file=sys.stderr)
    print(f"posterior_mode={posterior_mode}", file=sys.stderr)
    print(f"model={fit.model}", file=sys.stderr)
    print(f"nstates={fit.nstates}", file=sys.stderr)
    print(f"nobs={nobs}", file=sys.stderr)
    print(f"nparams={nparams}", file=sys.stderr)
    print(f"log_likelihood={log_likelihood:.12g}", file=sys.stderr)
    print(f"AIC={aic:.12g}", file=sys.stderr)
    print(f"AICc={aicc:.12g}", file=sys.stderr)
    print(f"BIC={bic:.12g}", file=sys.stderr)
    print(f"state_frequencies={fit.state_frequencies}", file=sys.stderr)
    print(f"relative_rates={fit.relative_rates}", file=sys.stderr)
    print(f"qmatrix={fit.qmatrix}", file=sys.stderr)


def run_anc_state_discrete(args):
    """Run the ``anc-state-discrete`` CLI command."""
    import numpy as np

    from toytree.cli._tree_transport import read_tree_auto, write_tree_output
    from toytree.utils import ToytreeError
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    if args.posterior_mode == "packed":
        # Packed posterior strings must avoid writer delimiters or key/value
        # parsing in extended Newick metadata becomes ambiguous.
        if args.posterior_sep in {args.features_delim, args.features_assignment}:
            raise ToytreeError(
                "--posterior-sep cannot match --features-delim or --features-assignment"
            )

    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)

    try:
        observed = tre.get_node_data(args.feature, missing=np.nan)
    except Exception as exc:
        raise ToytreeError(
            f"feature {args.feature!r} is not present on this tree. "
            "Use set-node-data first to assign discrete observations."
        ) from exc

    result = tre.pcm.infer_ancestral_states_discrete_ctmc(
        data=args.feature,
        nstates=args.nstates,
        model=args.model,
        inplace=False,
    )
    fit = result["model_fit"]
    data = result["data"]
    nobs = int(observed.notna().sum())
    base = args.meta_base or args.feature

    anc_col = f"{args.feature}_anc"
    anc_out_col = f"{base}_anc"
    tre.set_node_data(
        feature=anc_out_col,
        data=dict(enumerate(data[anc_col].tolist())),
        inplace=True,
    )

    posterior_col = f"{args.feature}_anc_posterior"
    rows = data[posterior_col].tolist()
    if args.posterior_mode == "packed":
        packed = _pack_posteriors(
            rows, sep=args.posterior_sep, float_format=args.features_formatter
        )
        tre.set_node_data(
            feature=f"{base}_anc_posterior",
            data=dict(enumerate(packed)),
            inplace=True,
        )
    elif args.posterior_mode == "split":
        post_array = np.vstack([np.asarray(row, dtype=float) for row in rows])
        for state_idx in range(post_array.shape[1]):
            tre.set_node_data(
                feature=f"{base}_anc_p{state_idx}",
                data=dict(enumerate(post_array[:, state_idx].tolist())),
                inplace=True,
            )

    if args.full:
        _print_fit_summary(
            feature=args.feature,
            fit=fit,
            nobs=nobs,
            posterior_mode=args.posterior_mode,
            meta_base=base,
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
        newick_write_kwargs={
            "features_prefix": args.features_prefix,
            "features_delim": args.features_delim,
            "features_assignment": args.features_assignment,
            "features_formatter": args.features_formatter,
        },
    )
