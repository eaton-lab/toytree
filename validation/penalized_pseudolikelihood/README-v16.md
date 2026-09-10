# Version 16: correlated final-rate-polish confirmation

V16 addresses the sole numerical failure in the completed V15 confirmation.
V15 passed every statistical recovery, bias, calibration, stability, parity,
and time-unit gate. One of 2,160 primary fits—a truth-initialized diagnostic
fit—ended with a projected conditional-rate gradient of `1.963e-6`, above the
frozen `1e-6` limit, despite agreeing with the independent optimum to about
`1e-11` objective units.

The corrected estimator retains the Newton conditional-rate solver and adds a
bounded L-BFGS-B polish only when the *final* fixed-chronogram rate solve misses
the existing gradient tolerance. It accepts the polish only when its objective
is non-worsening to floating-point precision and its projected gradient does
not increase. If objective-relative L-BFGS-B termination still leaves the
gradient above tolerance, bound-aware Newton steps directly refine stationarity
under the same acceptance rule. This does not change the model, lambda,
objective, or convergence threshold.

## Frozen development replay

The replay contains the 14 V15 datasets whose maximum role-level projected
gradient exceeded `5e-7`, including the failed case, plus six stratified
low-gradient controls. All four primary fit roles are independent tasks, for
80 globally parallel fits. V15 confirmation data are development data from
this point onward; the replay is diagnostic-only.

Run locally or remotely:

    pytest -q \
      tests/mod/test_pl_correlated.py \
      tests/mod/test_pl_validation_v14.py \
      tests/mod/test_pl_validation_v16.py

    python validation/penalized_pseudolikelihood/run_validation_v16_correlated.py \
      --mode replay --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v16_correlated.py \
      --mode replay --stage score --ncores 1

The replay must pass without changing its gates before confirmation begins.

## Fresh confirmation

V16 freezes the same 540-dataset factorial design, 2,214 independent fit tasks,
and release gates as V15, but uses a new confirmation seed. Do not inspect or
tune against these data before running the confirmation.

    python validation/penalized_pseudolikelihood/run_validation_v16_correlated.py \
      --mode confirmation --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v16_correlated.py \
      --mode confirmation --stage score --ncores 1

Rerunning a fit command resumes matching atomic caches. Commit only the
`results`, `environment`, and `seeds` JSON files for the completed mode; never
commit `v16/cache-v16/`.
