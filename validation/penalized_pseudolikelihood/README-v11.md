# Version 11: fixed-lambda UCLN validation

Version 11 evaluates the hardened `uncorrelated_lognormal` estimator at a
prespecified smoothing value. It is deliberately not a lambda-selection
study. For simulated log-rate standard deviation `sigma_log`, the matching
penalty is fixed as `lam = 1 / (2 * sigma_log**2)`. The returned
`implied_sigma_log` reports this deterministic interpretation; it is not an
estimate from the fitted tree.

The study uses no sequence-length or effective-site-count input. Input branch
lengths are simulated in one arbitrary additive unit and calibrations define
the returned time unit. The expected-branch track tests model-matched means,
the fractional-Poisson track tests the working observation model, and the
continuous-Gamma track tests robustness to low continuous branch noise.

## Prespecified design

The pilot crosses 24- and 48-tip birth-death chronograms, root-only and
root-plus-internal-interval calibration regimes, three observation tracks,
and iid log-rate standard deviations 0.1, 0.3, and 0.6. The independent
confirmation adds 96-tip trees and uses ten new replicates per cell.

Each dataset expands into independent cached tasks:

- the supported four-start free-age fit and an eight-start stress fit;
- a four-start fit with every internal age fixed to truth; expected-branch
  controls with `sigma_log >= 0.3` test identifiable rate-rank recovery; and
- for the first replicate in every cell, a four-start fit after multiplying
  all calibration ages by one million.

This task granularity allows a remote run to use substantially more cores than
a dataset-level worker. Every numerical library is restricted to one thread
inside each worker. Fit caches are written atomically and fingerprint the
UCLN, clock initializer, shared optimizer utilities, runner, and configuration.
The score stage reads matching caches and cannot invoke a fitter.

The prespecified gates cover convergence, calibration validity, four-start
default versus eight-start stress objective and chronogram agreement,
cross-start chronogram stability, root-normalized age recovery and bias,
fixed-age rate-rank recovery, and calibration-time-unit invariance of ages,
rates, and the centered log-rate penalty. A confirmation is run only after the pilot design,
implementation, and thresholds are frozen.

## Development pilot outcome

The 72-dataset pilot expanded to 252 independent fit tasks and passed all nine
prespecified gates. All 216 primary, stress, and fixed-age fits converged, and
all eight-start stress fits had stable near-optimal chronograms. The maximum
four-start versus eight-start root-normalized age difference was `7.53e-4`,
and the maximum relative objective gap was `5.95e-6`. Median root-normalized
internal-age MAE was `0.0309`, maximum absolute observation-track age bias was
`0.00258`, and median fixed-age rate Spearman correlation in the identifiable
expected-branch controls was `0.920`. After internal time normalization, the
largest calibration-unit discrepancies were `5.77e-9` for ages, `2.79e-8` for
rates, and `1.48e-8` for the penalty. These are development results.

## Frozen confirmation outcome

The independently seeded confirmation evaluated 540 datasets as 1,674 cached
fit tasks. Convergence, calibration validity, age recovery, rate-rank recovery,
and cross-start solution-stability gates passed. Three numerical gates failed:
the largest four-start versus eight-start relative objective gap was
`0.00290868`, the largest corresponding root-normalized age difference was
`0.137204`, and calibration-time rescaling produced maximum discrepancies of
`0.001748` for normalized ages, `0.0037289` for rates, and `0.000436` for the
penalty.

The failures were concentrated in fractional-Poisson datasets containing many
observed zero-length branches, especially 96-tip trees. Zero branches are valid
observations under that working likelihood; replacing them by a small positive
floor did not solve the optimization problem. A `1e-12` floor retained a
four-versus-eight-start age gap of `0.0431`, while a `1e-6` floor made those two
runs agree but a 32-start search found a better basin with an age difference of
`0.1472`. V11 is therefore frozen as a failed numerical confirmation. Its
thresholds and cached results are not revised or rerun. V12 replaces the joint
optimizer with conditional rate profiling and replays every V11 numerical
failure before using a new confirmation seed stream.

## Run order

Run focused tests and the inexpensive smoke study locally:

    pytest -q tests/mod/test_pl_uncorrelated_lognormal.py \
      tests/mod/test_pl_ape_parity.py \
      tests/mod/test_pl_validation_v11.py

    python validation/penalized_pseudolikelihood/run_validation_v11_ucln.py \
      --mode smoke --stage all --ncores 2 \
      --output-dir /tmp/toytree-pl-v11-smoke

Run or resume the pilot remotely with all available cores:

    python validation/penalized_pseudolikelihood/run_validation_v11_ucln.py \
      --mode pilot --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v11_ucln.py \
      --mode pilot --stage score --ncores 1

Only if every pilot gate passes, freeze the branch and run the independent
confirmation:

    python validation/penalized_pseudolikelihood/run_validation_v11_ucln.py \
      --mode confirmation --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v11_ucln.py \
      --mode confirmation --stage score --ncores 1

Commit the compact result, environment, and seed JSON files. The task cache
under `v11/cache-v11/` is resumable but should remain untracked.
