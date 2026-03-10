#!/usr/bin/env python

"""Runtime implementation for the ``anc-state-discrete`` CLI command."""

from __future__ import annotations

import json
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


def _fit_summary_payload(
    *,
    feature: str,
    fit,
    nobs: int,
) -> dict:
    """Return model-fit summary values as a JSON-serializable payload."""

    def _jsonify(value):
        if value is None:
            return None
        if hasattr(value, "item"):
            try:
                value = value.item()
            except Exception:
                pass
        if isinstance(value, float) and not math.isfinite(value):
            return None
        if isinstance(value, (list, tuple)):
            return [_jsonify(i) for i in value]
        if hasattr(value, "tolist"):
            return _jsonify(value.tolist())
        return value

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
    return {
        "feature": feature,
        "model": str(fit.model),
        "nstates": int(fit.nstates),
        "nobs": int(nobs),
        "nparams": nparams,
        "log_likelihood": log_likelihood,
        "AIC": float(aic),
        "AICc": float(aicc),
        "BIC": float(bic),
        "state_frequencies": _jsonify(fit.state_frequencies),
        "relative_rates": _jsonify(fit.relative_rates),
        "qmatrix": _jsonify(fit.qmatrix),
    }


def run_anc_state_discrete(args):
    """Run the ``anc-state-discrete`` CLI command."""
    from toytree.cli._tree_transport import (
        read_tree_auto,
        resolve_input_arg,
        write_tree_output,
    )
    from toytree.utils import ToytreeError

    if args.log_level is not None:
        from toytree.utils.src.logger_setup import set_log_level

        set_log_level(args.log_level)

    tre = read_tree_auto(
        resolve_input_arg(args.input), internal_labels=args.internal_labels
    )

    try:
        observed = tre.get_node_data(args.feature, missing=math.nan)
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

    anc_col = f"{args.feature}_anc"
    anc_out_col = f"{args.feature}_anc"
    tre.set_node_data(
        feature=anc_out_col,
        data=dict(enumerate(data[anc_col].tolist())),
        inplace=True,
    )

    posterior_col = f"{args.feature}_anc_posterior"
    rows = data[posterior_col].tolist()
    if args.binary_out:
        tre.set_node_data(
            feature=f"{args.feature}_anc_posterior",
            data=dict(enumerate(rows)),
            inplace=True,
        )
    else:
        packed = _pack_posteriors(rows, sep="|", float_format="%.12g")
        tre.set_node_data(
            feature=f"{args.feature}_anc_posterior",
            data=dict(enumerate(packed)),
            inplace=True,
        )

    if args.json:
        payload = _fit_summary_payload(feature=args.feature, fit=fit, nobs=nobs)
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    elif args.full:
        _print_fit_summary(
            feature=args.feature,
            fit=fit,
            nobs=nobs,
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
