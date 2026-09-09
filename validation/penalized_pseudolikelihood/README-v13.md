# Version 13: fixed-lambda correlated validation

V13 asks whether the correlated estimator is reliable when its smoothing
parameter is known. It deliberately does not select lambda and has no
cross-validation folds. This separates two questions that were confounded in
V6 and V9:

1. Can the optimizer recover a stable correlated-rate chronogram at fixed
   lambda?
2. Can one observed tree identify lambda precisely enough for automatic
   selection?

Only the first question is release-gating here. Lambda-selection uncertainty
will be revisited after the fixed-lambda estimator is frozen.

## Matched generating model

Log rates evolve from parent edge to child edge by independent Gaussian
increments with standard deviation `sigma_log`. The two basal log rates share
a profiled root mean. The fitted penalty is

    P = sum_nonbasal(log(r_child) - log(r_parent))^2
        + sum_basal(log(r_basal) - mean(log(r_basal)))^2

and the generating variance fixes

    lambda = 1 / (2 * sigma_log^2).

This is a matched fixed-lambda experiment, not an oracle selection rule offered
to users. The simulated baseline rate controls the numerical scale of branch
observations; it is not sequence length and no sequence-length argument is
added to the API.

## Independent fit roles

Every simulated dataset is expanded into independent process-pool tasks:

- `default`: the public four-start fit;
- `stress`: an eight-start reference;
- `oracle_start`: the same estimator initialized once from the simulated
  ages and rates, alongside its ordinary independent start;
- `fixed_age`: all internal ages fixed to truth, isolating rate recovery;
- `time_scaled`: replicate-zero calibrations multiplied by one million,
  testing calibration-unit invariance.

The default fit is compared with the best converged stress or oracle-start
objective. The oracle start is only a diagnostic lower-bound search; recovery
metrics are always computed from the fit available to ordinary users.

V13 scores normalized internal-age recovery, age bias, rate and parent-child
increment recovery with fixed ages, calibration validity, optimization-basin
agreement, exact-zero incidence, and calibration-unit invariance. It records
results separately by observation model, autocorrelation variance, and
calibration density.

## Local verification

Run the focused tests and smoke pipeline:

    pytest -q \
      tests/mod/test_pl_correlated.py \
      tests/mod/test_pl_validation_v13.py

    python validation/penalized_pseudolikelihood/run_validation_v13_correlated.py \
      --mode smoke \
      --stage all \
      --ncores 6 \
      --output-dir /tmp/toytree-v13-smoke

The smoke run verifies orchestration and cache reuse but is diagnostic-only.

## Remote pilot

After pulling the branch and installing the checkout:

    git switch fix/penalized-likelihood-validation
    git pull --ff-only origin fix/penalized-likelihood-validation
    pip install -e ".[test]"

    python validation/penalized_pseudolikelihood/run_validation_v13_correlated.py \
      --mode pilot \
      --stage fit \
      --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v13_correlated.py \
      --mode pilot \
      --stage score \
      --ncores 1

Fit tasks are cached atomically below `v13/cache-v13/`. Rerunning the fit
command resumes matching tasks. The score stage never calls a fitter. Fit and
scoring fingerprints are separate, so changing summaries or decision gates
does not invalidate expensive compatible fits.

If the pilot supports the frozen design, run the independently seeded
confirmation by replacing `pilot` with `confirmation`. Only compact result,
environment, and seed artifacts belong in Git; task caches are ignored.

## Interpretation

A passing confirmation would validate fixed-lambda correlated fitting within
the simulated scope. It would not establish that terminal-edge CV can identify
a unique lambda. Public guidance must continue to distinguish a stable
chronogram across a broad lambda region from precise smoothing-parameter
identification.
