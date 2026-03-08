#!/usr/bin/env python

"""Internal family/link helpers for pruning-based phylogenetic GLMs.

This module centralizes family-specific response validation and IRLS math used
by :mod:`toytree.pcm.src.phylolinalg.pglm`. Phase 1 fully implements
binomial-logit, poisson-log, negative-binomial-log, gamma-log, and beta-logit
families, while gamma-inverse is currently validated and routed to explicit
``NotImplemented`` errors to keep the public API stable as support expands.

The pruning solver, lambda optimization, and Firth adjustments remain in
``toytree``. This module uses ``statsmodels`` family/link classes internally as
the mathematical backend for supported combinations so link/variance behavior
stays consistent as more families and links are added.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeAlias

import numpy as np
import pandas as pd
from scipy.special import expit, gammaln
from statsmodels.genmod import families as sm_families
from statsmodels.genmod.families import links as sm_links

from toytree.utils.src.exceptions import ToytreeError

__all__ = ["GLMFamilySpec", "get_family_spec"]

FamilyParams: TypeAlias = dict[str, float]

# Centralized numeric guards used across inverse-link and derivative code paths.
LOGIT_ETA_CLIP = (-30.0, 30.0)
LOG_ETA_CLIP = (-700.0, 700.0)
MU_OPEN_EPS = 1e-12
MU_POS_FLOOR = 1e-12
MU_POS_CEIL = 1e300


def _clip_eta_for_link(eta: np.ndarray, link: str) -> np.ndarray:
    """Return eta clipped for numerically stable inverse-link evaluation."""
    arr = np.asarray(eta, dtype=float)
    if link == "logit":
        return np.clip(arr, *LOGIT_ETA_CLIP)
    if link == "log":
        return np.clip(arr, *LOG_ETA_CLIP)
    return arr


def _clip_mu_for_link_domain(mu: np.ndarray, link: str) -> np.ndarray:
    """Return mu clipped away from numerically induced link boundaries."""
    arr = np.asarray(mu, dtype=float)
    if link == "logit":
        return np.clip(arr, MU_OPEN_EPS, 1.0 - MU_OPEN_EPS)
    if link == "log":
        return np.clip(arr, MU_POS_FLOOR, MU_POS_CEIL)
    return arr


@dataclass(frozen=True)
class GLMFamilySpec:
    """Internal description of a supported (or scaffolded) GLM family/link."""

    family: str
    link: str
    implemented: bool
    supports_firth: bool
    response_kind: str
    family_params: dict[str, float] | None
    sm_family: Any | None = None
    response_levels: tuple[str, str] | None = None

    def inv_link(self, eta: np.ndarray) -> np.ndarray:
        """Return mean-scale values from linear predictors."""
        if self.family == "beta" and self.link == "logit":
            eta_eval = _clip_eta_for_link(np.asarray(eta, dtype=float), self.link)
            return _clip_mu_for_link_domain(expit(eta_eval), self.link)
        if self.sm_family is None:
            raise ToytreeError(
                f"Family/link math is not implemented for {self.family}/{self.link}."
            )
        eta = np.asarray(eta, dtype=float)
        # Clip eta only for bounded/positive links so overflow does not create
        # artificial boundary means (0, 1) that fail strict family domains.
        eta_eval = _clip_eta_for_link(eta, self.link)
        mu = np.asarray(self.sm_family.link.inverse(eta_eval), dtype=float)
        # Statsmodels correctly encodes link math, but bounded/positive links can
        # hit exact domain boundaries from floating-point overflow/underflow
        # (e.g., logit -> 0/1, log -> 0). We clip only these numerically induced
        # boundary hits so strict domain checks can remain active for truly
        # invalid links such as identity on positive-mean families.
        return _clip_mu_for_link_domain(mu, self.link)

    def validate_mu(self, mu: np.ndarray) -> None:
        """Raise if response-scale means violate the family domain."""
        mu = np.asarray(mu, dtype=float)
        if not np.all(np.isfinite(mu)):
            raise ToytreeError(
                f"Invalid mean values for family='{self.family}', link='{self.link}'."
            )
        if self.family in {"poisson", "negative_binomial", "gamma"}:
            if np.any(mu <= 0):
                raise ToytreeError(
                    f"Invalid mean values for family='{self.family}' "
                    f"with link='{self.link}': means must be > 0."
                )
            return
        if self.family in {"binomial", "beta"}:
            if np.any((mu <= 0) | (mu >= 1)):
                raise ToytreeError(
                    f"Invalid mean values for family='{self.family}' "
                    f"with link='{self.link}': means must be in (0, 1)."
                )
            return

    def dmu_deta(self, eta: np.ndarray, mu: np.ndarray) -> np.ndarray:
        """Return derivative of the inverse-link, ``dmu/deta``.

        Statsmodels link classes expose derivative APIs with slightly different
        semantics across versions (often ``deta/dmu`` via ``deriv(mu)``). We
        compute ``dmu/deta`` by preferring an explicit inverse-link derivative
        and otherwise inverting ``deta/dmu``.
        """
        if self.family == "beta" and self.link == "logit":
            mu = np.asarray(mu, dtype=float)
            out = mu * (1.0 - mu)
            if not np.all(np.isfinite(out)):
                raise ToytreeError("Non-finite inverse-link derivative for beta/logit.")
            return out
        if self.sm_family is None:
            raise ToytreeError(
                f"Family/link math is not implemented for {self.family}/{self.link}."
            )
        link = self.sm_family.link
        eta = np.asarray(eta, dtype=float)
        eta_eval = _clip_eta_for_link(eta, self.link)
        mu = np.asarray(mu, dtype=float)
        if hasattr(link, "inverse_deriv"):
            out = np.asarray(link.inverse_deriv(eta_eval), dtype=float)
        else:
            # Statsmodels link APIs differ by version; when only deta/dmu is
            # exposed we invert it to get the IRLS-required dmu/deta.
            deriv = np.asarray(link.deriv(mu), dtype=float)
            out = 1.0 / deriv
        # Non-finite derivatives destabilize IRLS weights and should fail early.
        if not np.all(np.isfinite(out)):
            raise ToytreeError(
                f"Non-finite inverse-link derivative for {self.family}/{self.link}."
            )
        return out

    def variance(self, mu: np.ndarray) -> np.ndarray:
        """Return variance function evaluated at ``mu``."""
        if self.family == "beta" and self.link == "logit":
            if not self.family_params or "phi" not in self.family_params:
                raise ToytreeError("Beta variance requires a concrete 'phi' value.")
            phi = float(self.family_params["phi"])
            mu = np.asarray(mu, dtype=float)
            return (mu * (1.0 - mu)) / (1.0 + phi)
        if self.sm_family is None:
            raise ToytreeError(
                f"Family variance is not implemented for {self.family}/{self.link}."
            )
        out = np.asarray(
            self.sm_family.variance(np.asarray(mu, dtype=float)),
            dtype=float,
        )
        return out

    def loglik(self, y: np.ndarray, mu: np.ndarray) -> float:
        """Return the observation log-likelihood under the current family."""
        if self.family == "beta" and self.link == "logit":
            if not self.family_params or "phi" not in self.family_params:
                raise ToytreeError(
                    "Beta log-likelihood requires a concrete 'phi' value."
                )
            phi = float(self.family_params["phi"])
            y = np.asarray(y, dtype=float)
            mu = np.asarray(mu, dtype=float)
            a = mu * phi
            b = (1.0 - mu) * phi
            obs = (
                gammaln(phi)
                - gammaln(a)
                - gammaln(b)
                + (a - 1.0) * np.log(y)
                + (b - 1.0) * np.log(1.0 - y)
            )
            return float(np.sum(obs))
        if self.sm_family is None:
            raise ToytreeError(
                "Family log-likelihood is not implemented for "
                f"{self.family}/{self.link}."
            )
        scale = 1.0
        if self.family == "gamma":
            if not self.family_params or "dispersion" not in self.family_params:
                raise ToytreeError(
                    "Gamma log-likelihood requires a concrete 'dispersion' value."
                )
            scale = float(self.family_params["dispersion"])
        obs = self.sm_family.loglike_obs(
            np.asarray(y, dtype=float),
            np.asarray(mu, dtype=float),
            var_weights=1.0,
            scale=scale,
        )
        return float(np.sum(np.asarray(obs, dtype=float)))


def _validate_empty_family_params(
    family: str,
    family_params: dict[str, Any] | None,
) -> FamilyParams | None:
    """Validate that no unsupported family parameters were passed."""
    if family_params in (None, {}):
        return None
    if not isinstance(family_params, dict):
        raise ToytreeError("family_params must be a dict or None.")
    if family_params:
        keys = ", ".join(sorted(map(str, family_params)))
        raise ToytreeError(
            f"family='{family}' does not accept family_params; got {keys}."
        )
    return None


def _validate_positive_param(
    family: str,
    family_params: dict[str, Any] | None,
    key: str,
) -> FamilyParams:
    """Validate a single required positive scalar family parameter."""
    if not isinstance(family_params, dict):
        raise ToytreeError(
            f"family='{family}' requires family_params={{'{key}': <positive float>}}."
        )
    if set(family_params) != {key}:
        raise ToytreeError(
            f"family='{family}' requires family_params with only key '{key}'."
        )
    value = family_params[key]
    try:
        fval = float(value)
    except Exception as exc:
        raise ToytreeError(
            f"family_params['{key}'] must be a positive float for family='{family}'."
        ) from exc
    if (not np.isfinite(fval)) or fval <= 0:
        raise ToytreeError(
            f"family_params['{key}'] must be a positive float for family='{family}'."
        )
    return {key: fval}


def _validate_optional_positive_param(
    family: str,
    family_params: dict[str, Any] | None,
    key: str,
) -> FamilyParams | None:
    """Validate an optional positive scalar family parameter."""
    if family_params in (None, {}):
        return None
    return _validate_positive_param(family, family_params, key)


def _coerce_binomial_response(
    series: pd.Series,
    response_name: str,
) -> tuple[pd.Series, tuple[str, str] | None]:
    """Coerce a binary response to 0/1 floats and return optional level labels."""
    s = series.copy()
    non_missing = s.dropna()
    if non_missing.empty:
        raise ToytreeError("Response variable contains only missing values.")

    if pd.api.types.is_bool_dtype(s):
        # Keep bool handling explicit so downstream summaries can preserve a
        # stable, human-readable level ordering.
        return s.astype("float").astype("Int64").astype("float"), ("False", "True")

    if pd.api.types.is_numeric_dtype(s):
        vals = set(pd.Series(non_missing).astype(float).unique().tolist())
        if vals.issubset({0.0, 1.0}):
            return s.astype(float), None
        raise ToytreeError(
            f"family='binomial' requires response '{response_name}' values to be "
            "0/1, bool, or two-level strings."
        )

    # Sort labels so string-coded responses map reproducibly across runs and
    # platforms, regardless of pandas category/order internals.
    labels = sorted({str(i) for i in non_missing.unique().tolist()})
    if len(labels) != 2:
        raise ToytreeError(
            f"family='binomial' requires exactly two response levels; got "
            f"{len(labels)} for '{response_name}'."
        )
    mapping = {labels[0]: 0.0, labels[1]: 1.0}
    mapped = s.map(lambda x: np.nan if pd.isna(x) else mapping[str(x)]).astype(float)
    return mapped, (labels[0], labels[1])


def _coerce_count_response(
    series: pd.Series,
    response_name: str,
    family: str,
) -> pd.Series:
    """Validate and coerce count response values for count families."""
    s = pd.to_numeric(series, errors="coerce").astype(float)
    non_missing = s.dropna()
    if non_missing.empty:
        raise ToytreeError("Response variable contains only missing values.")
    if np.any(non_missing.to_numpy() < 0):
        raise ToytreeError(f"family='{family}' requires non-negative count responses.")
    # Require integer-valued counts, but allow float-typed arrays when values
    # are exactly integral (common in CSV/Parquet round-trips).
    if not np.allclose(non_missing.to_numpy(), np.round(non_missing.to_numpy())):
        raise ToytreeError(
            f"family='{family}' requires integer-valued count responses."
        )
    return s


def _coerce_positive_response(
    series: pd.Series,
    response_name: str,
    family: str,
) -> pd.Series:
    """Validate and coerce strictly positive continuous responses."""
    s = pd.to_numeric(series, errors="coerce").astype(float)
    non_missing = s.dropna()
    if non_missing.empty:
        raise ToytreeError("Response variable contains only missing values.")
    if np.any(non_missing.to_numpy() <= 0):
        raise ToytreeError(
            f"family='{family}' requires response '{response_name}' > 0."
        )
    return s


def _coerce_beta_response(series: pd.Series, response_name: str) -> pd.Series:
    """Validate and coerce beta responses constrained to (0, 1)."""
    s = pd.to_numeric(series, errors="coerce").astype(float)
    non_missing = s.dropna()
    if non_missing.empty:
        raise ToytreeError("Response variable contains only missing values.")
    vals = non_missing.to_numpy()
    if np.any((vals <= 0) | (vals >= 1)):
        raise ToytreeError(
            f"family='beta' requires response '{response_name}' strictly "
            "between 0 and 1."
        )
    return s


def _make_sm_family(
    family: str,
    link: str,
    family_params: dict[str, float] | None,
) -> Any | None:
    """Instantiate a statsmodels family/link object for internal math."""
    if family == "binomial" and link == "logit":
        return sm_families.Binomial(link=sm_links.Logit())
    if family == "poisson":
        if link == "log":
            return sm_families.Poisson(link=sm_links.Log())
        if link == "identity":
            return sm_families.Poisson(link=sm_links.Identity())
    if family == "negative_binomial":
        if link in {"log", "identity"}:
            alpha = 1.0 if family_params is None else float(family_params["alpha"])
            link_obj = sm_links.Log() if link == "log" else sm_links.Identity()
            return sm_families.NegativeBinomial(alpha=alpha, link=link_obj)
    if family == "gamma":
        if link in {"log", "inverse", "identity"}:
            if link == "log":
                link_obj = sm_links.Log()
            elif link == "inverse":
                link_obj = sm_links.InversePower()
            else:
                link_obj = sm_links.Identity()
            return sm_families.Gamma(link=link_obj)
    return None


def _build_binomial_spec(
    link: str,
    family_params: dict[str, Any] | None,
    response: pd.Series | None,
    response_name: str,
) -> tuple[GLMFamilySpec, pd.Series | None]:
    """Return validated binomial/logit family spec and coerced response."""
    if link != "logit":
        raise ToytreeError("family='binomial' currently supports only link='logit'.")
    params = _validate_empty_family_params("binomial", family_params)
    levels = None
    rser = response
    if response is not None:
        rser, levels = _coerce_binomial_response(response, response_name)
    return (
        GLMFamilySpec(
            family="binomial",
            link=link,
            implemented=True,
            supports_firth=True,
            response_kind="binary",
            family_params=params,
            sm_family=_make_sm_family("binomial", link, params),
            response_levels=levels,
        ),
        rser,
    )


def _build_poisson_spec(
    link: str,
    family_params: dict[str, Any] | None,
    response: pd.Series | None,
    response_name: str,
) -> tuple[GLMFamilySpec, pd.Series | None]:
    """Return validated poisson/log family spec and coerced response."""
    if link != "log":
        raise ToytreeError("family='poisson' currently supports only link='log'.")
    params = _validate_empty_family_params("poisson", family_params)
    rser = None
    if response is not None:
        rser = _coerce_count_response(response, response_name, "poisson")
    return (
        GLMFamilySpec(
            family="poisson",
            link=link,
            implemented=True,
            supports_firth=True,
            response_kind="count",
            family_params=params,
            sm_family=_make_sm_family("poisson", link, params),
        ),
        rser,
    )


def _build_negative_binomial_spec(
    link: str,
    family_params: dict[str, Any] | None,
    response: pd.Series | None,
    response_name: str,
) -> tuple[GLMFamilySpec, pd.Series | None]:
    """Return validated negative-binomial spec and coerced response."""
    if link != "log":
        raise ToytreeError(
            "family='negative_binomial' currently supports only link='log'."
        )
    params = _validate_optional_positive_param(
        "negative_binomial",
        family_params,
        "alpha",
    )
    rser = None
    if response is not None:
        rser = _coerce_count_response(response, response_name, "negative_binomial")
    return (
        GLMFamilySpec(
            family="negative_binomial",
            link=link,
            implemented=True,
            supports_firth=False,
            response_kind="count",
            family_params=params,
            sm_family=_make_sm_family("negative_binomial", link, params),
        ),
        rser,
    )


def _build_gamma_spec(
    link: str,
    family_params: dict[str, Any] | None,
    response: pd.Series | None,
    response_name: str,
) -> tuple[GLMFamilySpec, pd.Series | None]:
    """Return validated gamma spec and coerced response."""
    if link not in {"log", "inverse"}:
        raise ToytreeError(
            "family='gamma' currently supports only link='log' or 'inverse'."
        )
    # Gamma-log is implemented; gamma-inverse remains scaffolded so callers can
    # validate inputs with stable error messages before not-implemented paths.
    if link == "log":
        params = _validate_optional_positive_param("gamma", family_params, "dispersion")
        implemented = True
    else:
        params = _validate_positive_param("gamma", family_params, "dispersion")
        implemented = False
    rser = None
    if response is not None:
        rser = _coerce_positive_response(response, response_name, "gamma")
    return (
        GLMFamilySpec(
            family="gamma",
            link=link,
            implemented=implemented,
            supports_firth=False,
            response_kind="positive",
            family_params=params,
            sm_family=_make_sm_family("gamma", link, params),
        ),
        rser,
    )


def _build_beta_spec(
    link: str,
    family_params: dict[str, Any] | None,
    response: pd.Series | None,
    response_name: str,
) -> tuple[GLMFamilySpec, pd.Series | None]:
    """Return validated beta/logit spec and coerced response."""
    if link != "logit":
        raise ToytreeError("family='beta' currently supports only link='logit'.")
    params = _validate_optional_positive_param("beta", family_params, "phi")
    rser = None if response is None else _coerce_beta_response(response, response_name)
    # Beta currently uses custom likelihood/variance math in GLMFamilySpec,
    # so no statsmodels family object is attached here.
    return (
        GLMFamilySpec(
            family="beta",
            link=link,
            implemented=True,
            supports_firth=False,
            response_kind="proportion",
            family_params=params,
            sm_family=None,
        ),
        rser,
    )


def get_family_spec(
    family: str,
    link: str,
    family_params: dict[str, Any] | None,
    response: pd.Series | None = None,
    response_name: str | None = None,
) -> tuple[GLMFamilySpec, pd.Series | None]:
    """Validate family/link and optionally coerce a response series.

    Parameters
    ----------
    family, link : str
        Requested family and link names.
    family_params : dict or None
        Family-specific extra parameters.
    response : pandas.Series or None, default=None
        If provided, response values are validated/coerced for the selected
        family. This allows scaffolded families to validate inputs before
        raising not-implemented errors in the model layer.
    response_name : str or None, default=None
        Name used in validation error messages.

    Returns
    -------
    tuple
        ``(spec, response_series_or_none)``
    """
    fam = str(family).lower()
    lnk = str(link).lower()
    if fam == "bernoulli":
        fam = "binomial"
    if fam in {"negative-binomial", "nb", "negbin"}:
        fam = "negative_binomial"
    rname = response_name or "response"

    builders = {
        "binomial": _build_binomial_spec,
        "poisson": _build_poisson_spec,
        "negative_binomial": _build_negative_binomial_spec,
        "gamma": _build_gamma_spec,
        "beta": _build_beta_spec,
    }
    builder = builders.get(fam)
    if builder is None:
        raise ToytreeError(
            "Unsupported family for pglm. Supported now: binomial/bernoulli "
            "(implemented), poisson (implemented), negative_binomial "
            "(implemented with log link), gamma (implemented with log link), beta "
            "(implemented with logit link), and scaffold validation for "
            "gamma-inverse."
        )
    return builder(lnk, family_params, response, rname)
