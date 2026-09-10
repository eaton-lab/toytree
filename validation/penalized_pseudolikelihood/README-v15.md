# Version 15: fixed-lambda correlated confirmation

V15 is the independently seeded, release-gating confirmation of ToyTree's
correlated penalized-pseudolikelihood estimator. The implementation and design
were frozen after V14 resolved all 14 numerical failures from the V13 pilot
while preserving six passing controls.

The study evaluates the estimator at the smoothing value implied by the
generating log-rate increment variance:

    lambda = 1 / (2 * sigma_log^2)

This validates fixed-lambda estimation. It does not validate precise automatic
selection of lambda from a single tree.

## Frozen design

The confirmation contains 540 independently seeded datasets: three tree sizes
(24, 48, and 96 tips), two calibration regimes, three observation models,
three correlated log-rate variances, and ten replicates per cell.

Each dataset has independent default, doubled-start stress, truth-initialized,
and fixed-age fit tasks. Replicate zero in every cell also has a matched
calibration-time-rescaled task. This gives 2,214 globally parallel, atomically
cached fit tasks.

Release gates cover convergence, calibration validity, multistart stability,
profiled-rate first-order conditions, basin replication, objective and
chronogram agreement, age recovery and bias, fixed-age rate recovery, and
calibration-time-unit invariance. Parent-child rate-increment recovery remains
reported but is not a gate: the penalty intentionally shrinks increments, so
their raw rank correlation does not diagnose whether the optimizer solved its
stated objective.

The confirmation seed is distinct from the development seed used by V13 and
V14. Do not inspect confirmation results to tune code or thresholds.

## Local preflight

Smoke mode verifies orchestration, caching, and numerical diagnostics. Its six
datasets are not large enough to interpret the confirmation's aggregate
statistical gates, so a false smoke `gates_passed` value is not a failure.

    pytest -q \
      tests/mod/test_pl_correlated.py \
      tests/mod/test_pl_validation_v15.py

    python validation/penalized_pseudolikelihood/run_validation_v15_correlated.py \
      --mode smoke \
      --stage all \
      --ncores 6 \
      --output-dir /tmp/toytree-v15-smoke

## Remote confirmation

Use a clean checkout of the pushed commit:

    git switch fix/penalized-likelihood-validation
    git pull --ff-only origin fix/penalized-likelihood-validation
    pip install -e ".[test]"

    python validation/penalized_pseudolikelihood/run_validation_v15_correlated.py \
      --mode confirmation \
      --stage fit \
      --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v15_correlated.py \
      --mode confirmation \
      --stage score \
      --ncores 1

Rerunning the fit command resumes matching tasks. Scoring never fits and its
fingerprint is separate from the expensive fit fingerprint.

The completed confirmation passed every statistical-performance gate but
failed two linked numerical gates because one truth-initialized diagnostic fit
ended at a projected conditional-rate gradient of `1.963e-6`, just above the
frozen `1e-6` threshold. The independent default and stress fits agreed in
objective to approximately `1e-11`. The gate was not weakened; V16 treats the
V15 result as development evidence, repairs the final-solve retry gap, and
uses a fresh confirmation stream.

After scoring, commit only the compact artifacts:

    git add \
      validation/penalized_pseudolikelihood/v15/results-v15-confirmation.json \
      validation/penalized_pseudolikelihood/v15/environment-v15-confirmation.json \
      validation/penalized_pseudolikelihood/v15/seeds-v15-confirmation.json

    git commit -m "Record V15 correlated confirmation results"
    git pull --rebase origin fix/penalized-likelihood-validation
    git push origin HEAD:fix/penalized-likelihood-validation

Task caches below `v15/cache-v15/` are ignored and must not be committed.
