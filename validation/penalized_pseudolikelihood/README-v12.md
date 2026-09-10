# Version 12: profiled fixed-lambda UCLN validation

Version 12 addresses the numerical failures in the frozen V11 fixed-lambda
`uncorrelated_lognormal` confirmation. It does not change the statistical
model, likelihood, smoothing values, simulation design, or release thresholds.
Instead, it profiles branch log rates conditionally for every candidate
chronogram and optimizes node ages directly under linear ancestry and
calibration constraints. A final joint polish is accepted only when it improves
the objective, after which rates are re-profiled at the returned ages. The
requested multistarts combine a bounded strict-clock candidate, a guaranteed
interior candidate, and feasible perturbed candidates. If only one requested
start reaches the winning basin, one additional independently perturbed,
feasible local start tests whether that basin can be replicated. The result
reports both `nstarts` and `evaluated_starts`, plus
`basin_confirmation_run`.

The joint polish is optional because it uses the older unconstrained age
transform. If a line-search trial saturates that transform at a boundary, the
fit retains the already-converged direct-age/profiled-rate solution. General
joint-optimizer failures are not treated this way and still fail convergence.

## Zero-length branch policy

Observed zero-length branches remain valid fractional-Poisson observations and
are passed to the objective unchanged. They are not rejected and are not
replaced by an arbitrary positive floor. A floor can hide optimizer instability:
in a V11 failure, `1e-6` made four and eight starts agree, but a 32-start search
found a better basin and a substantially different chronogram.

Every fit reports counts of zero terminal and internal branches, their overall
fraction, the smallest positive branch length, and its ratio to the positive
median. A warning explains that many zeros can weaken age-rate identifiability.
An internal zero edge may be collapsed before fitting when it represents an
unresolved relationship, but that is a modeling decision and is never performed
silently. A zero terminal edge may be biologically meaningful and is retained.

## Prespecified sequence

The first stage reconstructs all 40 V11 confirmation datasets that exceeded at
least one objective, chronogram, or calibration-time-unit numerical threshold.
They expand into 125 independent cached tasks: four-start defaults, eight-start
stress fits, fixed-age controls, and the applicable calibration-rescaled fits.
The V11 results are read only to select cases; V12 uses a new cache fingerprint
and does not alter any V11 artifact.

The replay uses the same release gates as V11. If it passes, run the development
pilot with the new optimizer. Only if both replay and pilot pass without changing
code or thresholds should the independently seeded confirmation be run. The
confirmation retains the V11 simulation matrix and a new seed stream.

## Frozen results and decision

The 40-dataset replay (125 fit tasks) and 72-dataset development pilot (252 fit
tasks) passed all nine prespecified gates. The independently seeded confirmation
completed 540 datasets and 1,674 fit tasks. All fits converged, every calibration
was valid, median root-normalized internal-age MAE was `0.03291`, maximum
absolute age bias was `0.004680`, and median fixed-age rate Spearman correlation
was `0.8334` overall and `0.9128` among identifiable controls. Maximum
calibration-time rescaling errors were `1.52e-6` for ages, `1.47e-6` for rates,
and `1.46e-7` for the penalty.

The confirmation did not pass every gate. Three of 540 datasets failed at least
one numerical uniqueness criterion. All three used fractional-Poisson
observations, `sigma_log=0.6`, and contained many exact zeros. One 96-tip fit
found a better eight-start basin than its four-start fit (maximum relative
objective gap `2.68e-4`; maximum normalized age difference `0.153`). One 24-tip
fit had nearly equivalent objectives but a normalized age difference of
`0.0355`, demonstrating a flat, weakly identified chronogram. One 96-tip fit
returned the same default and stress solution but did not independently
replicate its best basin. All positive expected-branch and continuous-Gamma
datasets passed the numerical gates.

The release decision is therefore scoped rather than post hoc: UCLN is
validated for positive continuous additive branch lengths within this design.
Exact-zero observations remain supported and are never floored, but a zero-rich
fit should be used for inference only when `converged`,
`best_basin_replicated`, and `solution_stable` are all true. Failure of those
diagnostics indicates data-specific weak identifiability, not a reason to
replace zeros by arbitrary pseudo-lengths.

This completes fixed-lambda UCLN development within that scope. V12 supplied
the generating, prespecified lambda; it did not validate a per-tree lambda
selector, and ToyTree does not expose one. The earlier V4 pilot chose lambda
using known simulated ages before freezing it for confirmation, which is not a
procedure available for empirical trees.

The committed confirmation records source hash
`370a04071ea1c6b430c6edbfdd904064300d93581d718685f8a67d09a86f396d`.
Later correlated-model work changed the broad V12 hash because it added unused
functions to `optimization.py` and enriched only exception records in
`_run_multistart`. Subsequent work changed the legacy `relaxed` path stored in
the same source file as UCLN. The public UCLN function dispatches to its
separate profiled implementation, whose fitted-value path is unchanged; the
clock initializer and V12 runner also remain unchanged. The machine-readable
compatibility audit in
`v12/compatibility-v12-current.json` pins both source hashes and the reviewed
differences; no equivalent 1,674-fit rerun is required.

## Run order

Run focused tests and an inexpensive smoke study locally:

    pytest -q tests/mod/test_pl_uncorrelated_lognormal.py \
      tests/mod/test_pl_validation_v12.py \
      tests/mod/test_pl_ape_parity.py

    python validation/penalized_pseudolikelihood/run_validation_v12_ucln.py \
      --mode smoke --stage all --ncores 4 \
      --output-dir /tmp/toytree-pl-v12-smoke

Replay the frozen V11 numerical failures:

    python validation/penalized_pseudolikelihood/run_validation_v12_ucln.py \
      --mode replay --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v12_ucln.py \
      --mode replay --stage score --ncores 1

If every replay gate passes, run and score the development pilot:

    python validation/penalized_pseudolikelihood/run_validation_v12_ucln.py \
      --mode pilot --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v12_ucln.py \
      --mode pilot --stage score --ncores 1

Only after both stages pass, freeze the branch and run the new confirmation:

    python validation/penalized_pseudolikelihood/run_validation_v12_ucln.py \
      --mode confirmation --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v12_ucln.py \
      --mode confirmation --stage score --ncores 1

Commit only the compact result, environment, and seed JSON files. Task caches
under `v12/cache-v12/` are resumable and remain untracked.
