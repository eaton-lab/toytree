# Version 6: correlated-model reliability

Version 6 is a development-only paired study. It tests whether correlated-model
failures come from numerical optimization, the fractional-Poisson working
observation model, or irreducible age-rate confounding. It does not change the
public API or make the experimental warning eligible for removal.

The study never accepts alignment length, sequence length, or an inferred
effective site count. Both estimators consume only phylogram branches in
substitutions per site. The multiplicative-Gamma candidate uses a scale-free
working loss and has no precision parameter.

## Changes under test

The existing fractional-Poisson model remains the public default. Internally,
correlated fits now retry an iteration-limited final polish once, and
cross-validation fits each held edge from strong to weak smoothing so adjacent
lambda values can share a converged warm start.

A private validation switch adds a multiplicative-Gamma unit-deviance loss,

    y / mu - log(y / mu) - 1,

where y is an observed branch estimate and mu is its fitted expectation. Its
held-branch score is the matching Gamma deviance. It requires positive observed
branches; zero-length trees remain supported only by the existing
fractional-Poisson path during this study.

## Run order

Run focused unit tests and the local pipeline smoke study:

    pytest -q tests/mod/test_pl_correlated.py tests/mod/test_pl_lambda_cv.py

    python validation/penalized_pseudolikelihood/run_validation_v6_reliability.py \
      --mode smoke --stage all --ncores 1 \
      --output-dir /tmp/toytree-pl-v6-smoke

The 40-dataset pilot is intended for the remote server:

    python validation/penalized_pseudolikelihood/run_validation_v6_reliability.py \
      --mode pilot --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v6_reliability.py \
      --mode pilot --stage score --ncores 1

Run the targeted 96-tip optimizer replay separately. Its four seeds are the
recorded v5 replicates that produced iteration-limit failures:

    python validation/penalized_pseudolikelihood/run_validation_v6_reliability.py \
      --mode optimizer-stress --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v6_reliability.py \
      --mode optimizer-stress --stage score --ncores 1

Every paired dataset is written atomically beneath `v6/cache-v6/`. The score
stage reads only fingerprint-matched caches and never calls a fitting function.
Commit the compact result, environment, and seed artifacts, but not the caches.

## Prespecified interpretation

The primary endpoint is root-normalized internal-node age recovery. Exact
recovery or narrow bootstrap concentration of lambda is not required when the
chronograms across bootstrap-supported lambda values are stable.

Optimizer changes are retained only when fold/full-fit convergence passes the
configured gates and warm-started objectives are no worse than the independent
selected fit. The Gamma loss is a candidate for a later public design only if
it is noninferior under both Gamma and lognormal branch noise, improves paired
chronogram recovery, and preserves normalized ages when every phylogram branch
is multiplied by `1e-3` or `1e3`.

If optimization becomes reliable but neither observation loss yields stable
chronograms under sparse calibration, the result is evidence of structural
age-rate non-identifiability. In that case automatic lambda selection remains
experimental; the study must not be rescued by weakening its gates or by
adding a sequence-length proxy.
