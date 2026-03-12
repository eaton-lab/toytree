#!/usr/bin/env python

"""Runtime implementation for the ``anc-state-discrete`` CLI command."""

from __future__ import annotations

import json
import math
import sys


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

    # parse data input from binary or newick
    tre = read_tree_auto(
        resolve_input_arg(args.input), internal_labels=args.internal_labels
    )

    # select and extract the feature data from the tree
    try:
        observed = tre.get_node_data(args.feature, missing=math.nan)
    except Exception as exc:
        raise ToytreeError(
            f"feature {args.feature!r} is not present on this tree. "
            "Use set-node-data first to assign discrete observations."
        ) from exc

    # fit the CTMC
    result = tre.pcm.infer_ancestral_states_discrete_ctmc(
        data=args.feature,
        nstates=args.nstates,
        model=args.model,
        inplace=True,
    )
    fit = result["model_fit"]
    nobs = int(observed.notna().sum())

    # optionally report model fit as JSON
    if args.json:
        payload = _fit_summary_payload(feature=args.feature, fit=fit, nobs=nobs)
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)

    # optionally do not write features
    if args.exclude_features:
        features = None
    else:
        features = set(tre.features) - {"name", "height", "dist", "support"}

    # write tree+features to binary or newick
    write_tree_output(
        tre,
        output=args.output,
        binary_out=args.binary_out,
        features=features,
    )
