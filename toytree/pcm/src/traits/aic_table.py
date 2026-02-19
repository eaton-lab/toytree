
from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Literal, Optional


@dataclass
class ModelResult:
    """Minimal data required for model comparison."""

    model: str
    log_likelihood: float
    nparams: int


def aic_table(
    models: list[ModelResult],
    nobs: Optional[int] = None,
    rank_by: Literal["AIC", "AICc"] = "AIC",
):
    """Return model-comparison table with AIC and optional AICc.

    Parameters
    ----------
    models: list[ModelResult]
        Fitted model result objects with `model`, `log_likelihood`, and `nparams`.
    nobs: int | None
        Number of observations. If provided, AICc columns are computed.
    rank_by: Literal["AIC", "AICc"]
        Criterion used to sort rows and define generic `weight` and
        `evidence_ratio_vs_best` columns.
    """
    rows = []
    for m in models:
        name = m.model
        ll = float(m.log_likelihood)
        k = int(m.nparams)
        aic = 2 * k - 2 * ll
        rows.append((name, ll, k, aic))

    df = pd.DataFrame(rows, columns=["model", "loglik", "k", "AIC"])
    df["dAIC"] = df["AIC"] - df["AIC"].min()
    df["weight_AIC"] = np.exp(-0.5 * df["dAIC"])
    denom_aic = float(df["weight_AIC"].sum())
    if denom_aic > 0:
        df["weight_AIC"] /= denom_aic
    else:
        df["weight_AIC"] = np.nan
    best_w_aic = df["weight_AIC"].max()
    df["evidence_ratio_vs_best_AIC"] = best_w_aic / df["weight_AIC"]

    if nobs is not None:
        n = int(nobs)
        if n <= 0:
            raise ValueError("nobs must be > 0.")
        df["nobs"] = n
        den = n - df["k"] - 1
        corr = np.where(den > 0, (2.0 * df["k"] * (df["k"] + 1)) / den, np.inf)
        df["AICc"] = df["AIC"] + corr
        df["dAICc"] = df["AICc"] - df["AICc"].min()
        df["weight_AICc"] = np.exp(-0.5 * df["dAICc"])
        denom_aicc = float(df["weight_AICc"].sum())
        if denom_aicc > 0:
            df["weight_AICc"] /= denom_aicc
        else:
            df["weight_AICc"] = np.nan
        best_w_aicc = df["weight_AICc"].max()
        df["evidence_ratio_vs_best_AICc"] = best_w_aicc / df["weight_AICc"]

    if rank_by == "AICc":
        if nobs is None:
            raise ValueError("rank_by='AICc' requires nobs.")
        df = df.sort_values("AICc").reset_index(drop=True)
        df["weight"] = df["weight_AICc"]
        df["evidence_ratio_vs_best"] = df["evidence_ratio_vs_best_AICc"]
    else:
        df = df.sort_values("AIC").reset_index(drop=True)
        df["weight"] = df["weight_AIC"]
        df["evidence_ratio_vs_best"] = df["evidence_ratio_vs_best_AIC"]
    df["rank_by"] = rank_by

    return df
