# Version 5: correlated-lambda identifiability

Version 5 is a development-only study of when terminal-edge LOOCV contains
enough information to tune the correlated model's smoothing parameter. It
does not change the public selector, does not use random-subsample CV, and is
not eligible to overturn the failed version-3 confirmation.

The pilot separates three possible limitations: the number of terminal
observations, multiplicative-Gamma precision, and age-rate confounding. Its
fixed-age control crosses 24, 48, and 96 tips with Gamma shapes 100 and 400.
Its chronogram control compares the existing sparse calibration regime with
three distributed internal intervals on 48- and 96-tip trees. Baseline rate
remains fixed because scaling the mean does not change relative precision
under multiplicative-Gamma noise. The lambda grid extends from `1e-8` to
`1e4`, and agreement between CV and the population oracle at the lower grid
boundary is recorded as a legitimate near-unsmoothed result.

Run the pipeline smoke test and resumable development pilot:

    python validation/penalized_pseudolikelihood/run_validation_v5_identifiability.py \
      --mode smoke --ncores 1 --output-dir /tmp/toytree-pl-v5-smoke

    python validation/penalized_pseudolikelihood/run_validation_v5_identifiability.py \
      --mode pilot --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v5_identifiability.py \
      --mode pilot --stage score --ncores 1

The pilot contains 40 datasets. Every dataset caches the simulation truth,
all terminal-edge folds, and all full-grid fits under `v5/cache-v5/`, so score
and bootstrap diagnostics can be repeated without likelihood optimization.
Only a condition meeting the pinned predictive, recovery, and convergence
gates becomes a candidate for a separately seeded confirmation study. Until
such a confirmation is designed and passes, correlated-lambda selection
remains unvalidated.

After scoring, compare the current Pearson selector with relative-squared and
Gamma-deviance scores using only the retained caches:

    python validation/penalized_pseudolikelihood/diagnose_lambda_selection_v5.py \
      --mode pilot --bootstrap-replicates 2000

This writes `v5/diagnostics-v5-pilot.json`. It also reports lambda ranges that
remain within 15% and 50% of the population-oracle risk and summarizes failed
folds and full fits by condition, lambda, and optimizer message. It never calls
a fitting function and does not change the public selector.
