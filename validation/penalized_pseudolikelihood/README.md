# Penalized-pseudolikelihood validation

This directory contains the pinned simulation and predictive-validation study
for ToyTree's ultrametric branch-length pseudolikelihood models.

## Version 16: correlated final-rate polish

The [V16 design](README-v16.md) adds a conservative, bounded final conditional-
rate polish for the single numerical termination failure exposed by V15. It
first replays all 14 V15 cases above a prespecified near-threshold gradient plus
six controls, then reserves a fresh seed stream for an unchanged-gate,
540-dataset confirmation. The model, fixed lambda values, statistical design,
and release thresholds are unchanged.

The 20-dataset replay and independently seeded 540-dataset confirmation both
passed every frozen gate. Fixed-lambda correlated development is complete
within the tested scope. This result does not validate the separate
terminal-edge cross-validation lambda selector, whose uncertainty limitations
remain documented below.

## Version 15: frozen correlated confirmation

The [V15 design](README-v15.md) freezes the profiled correlated estimator after
the passing V14 replay and evaluates it on 540 datasets from an untouched,
independent seed stream. It is release-gating for fixed-lambda correlated
fitting, not for automatic lambda selection. Increment recovery is retained as
a diagnostic rather than a gate because smoothing intentionally shrinks the
increments being measured.

## Version 14: targeted correlated optimizer replay

The [V14 design](README-v14.md) replays all 14 numerical failures from the V13
pilot plus six matched passing controls. It tests the new conditional
log-rate Newton solve, direct constrained-age optimization, adaptive basin
confirmation, exact-zero handling, and exact calibration-time-unit
normalization. V14 is diagnostic-only; a passing replay leads to a fresh
independently seeded fixed-lambda confirmation.

## Version 13: fixed-lambda correlated validation

The [V13 design](README-v13.md) evaluates correlated-rate dating with lambda
fixed by the generating log-rate increment variance. Independent default,
doubled-start, truth-initialized, and fixed-age fits separate ordinary
optimization, missed basins, and rate identifiability. Calibration-unit
rescaling is tested separately. V13 contains no lambda selection or
cross-validation release gate.

## Version 12: profiled fixed-lambda UCLN validation

The [V12 design](README-v12.md) replaces joint age-rate optimization with
conditional log-rate profiling and direct, linearly constrained age
optimization. It retains observed zero-length branches exactly and reports
their number, location, and fraction rather than silently imposing a positive
floor. V12 first replays all 40 datasets that failed a V11 numerical gate; its
thresholds are unchanged. Only a passing replay and development pilot permit a
new independently seeded confirmation. The replay and 72-dataset pilot passed
every gate. In the independently seeded 540-dataset confirmation, all fits
converged and every positive expected-branch and continuous-Gamma dataset
passed, but three high-variance, zero-rich fractional-Poisson datasets failed at
least one objective/chronogram uniqueness gate. UCLN is therefore validated for
positive continuous additive branch lengths within this design; zero-rich fits
remain conditional on their reported basin-replication and solution-stability
diagnostics.

Fixed-lambda UCLN development is complete within that scope. ToyTree does not
provide a validated per-tree UCLN lambda selector. A compatibility audit pins
the historical confirmation source and verifies that subsequent shared-helper
changes do not alter UCLN fitted values.

## Version 11: frozen failed UCLN confirmation

The [V11 design](README-v11.md) evaluates the hardened
`uncorrelated_lognormal` optimizer at prespecified, simulation-matched fixed
lambda values. It is not a lambda-selection study. Four-start default,
eight-start stress, fixed-age, and calibration-time-rescaled fits are cached as
separate tasks so server runs can use all available cores; scoring never
repeats optimization. The 72-dataset pilot passed, but the frozen 540-dataset
confirmation failed objective, chronogram, and calibration-time-unit numerical
parity gates. Failures were concentrated in zero-rich fractional-Poisson data.
V12 supersedes the optimizer; V11 results and thresholds remain unchanged.

## Version 10: discrete-model finalization

The [V10 design](README-v10.md) finalizes the chronos-compatible `discrete`
implementation and evaluates a multiplicative-Gamma candidate. Smoke and the
nine-case historical failure replay pass after EM initialization, analytic
gradients, bounded fallback optimization, and explicit boundary diagnostics.
The Gamma candidate passes convergence, calibration, recovery, and unit-
invariance gates but fails all doubled-start optimizer-stability gates; better
identified optima continue to appear through 256 starts. Therefore `discrete`
is complete within its compatibility scope, while the Gamma candidate is
retired from the public API and retained privately only for reproducibility.

## Version 9: correlated-lambda uncertainty replay

The [V9 design](README-v9.md) uses a single global worker pool over held-tip
lambda paths, so the targeted replay can use all available server cores while
preserving serial strong-to-weak warm starts within each path. It reruns eight
historical high-uncertainty cases under the current estimator instead of
repeating the obsolete full V6 pilot. Per-path atomic caches make interrupted
fits resumable, and scoring changes do not invalidate fit caches. A cache-only
follow-up compares four prespecified lambda-selection rules after V9 isolated
between-lambda uncertainty as the remaining failure. V9 remains diagnostic-only
because its cases were selected from prior failures.

## Version 8: discrete-mixture validation

The v8 design and run instructions are recorded in
[README-v8.md](README-v8.md). It validates the hardened
chronos-compatible fractional-Poisson mixture and evaluates a scale-equivariant
multiplicative-Gamma candidate. The development pilot passes the Gamma
scale-equivariance and recovery thresholds but not the prespecified optimizer-
stability gates. V10 supersedes this study and retires the Gamma candidate.

## Version 7: strict-clock validation

The v7 design and run instructions are recorded in
[README-v7.md](README-v7.md). The strict clock now profiles its shared rate
analytically and optimizes only free node ages. After a passing development
pilot, an independently seeded 360-dataset confirmation passed every numerical,
recovery, calibration, and time-unit gate. Strict-clock development is complete
within the documented branch-length pseudolikelihood scope. The study uses no
sequence-length input and does not alter the correlated-model v6 study or caches.

## Version 6: correlated-model reliability

The development-only v6 design and run instructions are recorded in
[README-v6.md](README-v6.md). It compares the existing fractional-Poisson
correlated model with a private scale-free multiplicative-Gamma working loss,
while separately testing lambda-path warm starts and iteration-limit retries.
It introduces no sequence-length input and makes no public statistical claim
unless a later independently seeded confirmation passes.

## Version 5: correlated-lambda identifiability

The development-only v5 design and run instructions are recorded in
[README-v5.md](README-v5.md). It does not change the public LOOCV selector.

## Version 4: independent-rate models

Version 4 pins the `ape::chronos` Gamma-CDF `relaxed` objective and evaluates
whether the scale-invariant `uncorrelated_lognormal` model has a distinct,
recoverable use case. It compares the two estimators on paired iid-Gamma and
iid-lognormal rate simulations. The pilot selects one lambda per fitted model
and generating process; confirmation freezes those values before using a new
seed stream. Count observations are release-gating and multiplicative-Gamma
observations are descriptive.

Run the pipeline check and resumable pilot:

    python validation/penalized_pseudolikelihood/run_validation_v4.py \
      --mode smoke --ncores 1 --output-dir /tmp/toytree-pl-v4-smoke

    python validation/penalized_pseudolikelihood/run_validation_v4.py \
      --mode pilot --stage all --ncores 12

After `selected-lambdas-v4-pilot.json` is written, run confirmation:

    python validation/penalized_pseudolikelihood/run_validation_v4.py \
      --mode confirmation --stage all --ncores 12

Then run the separately seeded, identifiable fixed-age rate control:

    python validation/penalized_pseudolikelihood/run_validation_v4_rate_control.py \
      --ncores 12

Every dataset is checkpointed under `v4/cache-v4/`. Score-only reruns reuse
those fits. The lognormal model is retained only if it passes absolute
age-recovery and paired-bootstrap non-inferiority gates in the main study and
the identifiable fixed-age rate-recovery gate in the separate control.

The rate-control stage fixes all internal ages at their simulated values and
uses the lower-noise continuous observation track. It tests whether UCLN
recovers identifiable branch-rate ranks. The count-track control remains in
the main confirmation artifact as a noisy diagnostic; its raw observations do
not meet the prespecified absolute rank-correlation threshold.

The frozen confirmation found 99% UCLN convergence, median normalized age MAE
0.056, absolute age bias 0.009, and an upper 95% paired error ratio of 0.217
relative to `relaxed`. The identifiable control then passed with 100%
convergence and median log-rate Spearman correlation 0.948. These results
support retaining UCLN. The chronos-compatible `relaxed` implementation is
validated by exact objective parity with ape 5.8-1, but it did not pass the
separate absolute-recovery gates under sparse calibration; that limitation is
reported in the user documentation rather than hidden by weakening a gate.

## Version 3: correlated-model lambda selection

Version 2 completed, but its cross-family selector did not meet the predictive
gates. More importantly, that target was not scientifically appropriate:
chronogram software ordinarily asks the user to choose the clock family, then
uses lineage-pruning cross-validation to tune smoothing within a correlated
model. The discrete category count is likewise an explicit modeling choice.
The v1/v2 runners and caches are retained as an immutable diagnostic record,
and their generic selector is private.

Version 3 therefore validates only
`tree.mod.edges_make_ultrametric_correlated_lambda_cv(...)`. It uses
Sanderson-style terminal-edge holdouts, minimum mean Pearson loss, and a
prespecified lambda grid from 1e-4 through 1e4. The release-gating observation
model is continuous multiplicative-Gamma noise on expected branch lengths,
using 24-tip trees with root and internal interval calibrations across log-rate
innovation scales 0.1, 0.2, 0.3, and 0.6. A 24-tip fixed-internal-age control
separates smoothing selection from age-rate confounding. A higher-substitution-
scale continuous control and an integer-count, zero-heavy stress track are
descriptive; the latter is not used to decide whether lambda selection is
validated.

Before the study, run the pinned one-start versus four-start optimizer
diagnostic:

    python validation/penalized_pseudolikelihood/diagnose_correlated_optimizer_v3.py \
      --ncores 12

The 24-case development diagnostic found 95.8% convergence with one start and
100% with four starts. Its one-start 95th-percentile normalized objective gap
was 1.06e-6 (maximum 5.55e-6), narrowly missing the prespecified stability
threshold. Version 3 therefore pins four starts. Correlated fits use analytic
gradients for both log rates and transformed node ages and always finish with a
joint L-BFGS-B polish; convergence is defined by that final joint fit.

Run the inexpensive pipeline check:

    python validation/penalized_pseudolikelihood/run_validation_v3.py \
      --mode smoke --ncores 1 --output-dir /tmp/toytree-pl-v3-smoke

Run a resumable development pilot, then score its cached fits without
recalculation:

    python validation/penalized_pseudolikelihood/run_validation_v3.py \
      --mode pilot --stage all --ncores 12

    python validation/penalized_pseudolikelihood/run_validation_v3.py \
      --mode pilot --stage score --ncores 1

After freezing the implementation, grid, gates, and analysis, use the unused
confirmation seeds on the remote server. Fit and score are separate so a
scoring-only rerun never repeats the expensive likelihood optimization:

    pip install -e ".[test]"

    python validation/penalized_pseudolikelihood/run_validation_v3.py \
      --mode confirmation --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v3.py \
      --mode confirmation --stage score --ncores 1

Only confirmation mode is release-eligible. Candidate fits and held-out
predictions are checkpointed atomically under `v3/cache-v3/`; scoring changes
can reuse them, while estimator, simulation, grid, or calibration changes
invalidate the fingerprints. Dataset completions are emitted as JSON lines for
remote progress monitoring. Return and commit only
`results-v3-confirmation.json`, `environment-v3-confirmation.json`, and
`seeds-v3-confirmation.json`; the large cache directory is intentionally
gitignored.

The frozen confirmation did not pass its lambda-selection gates. Diagnose the
selection framework from the retained caches without refitting:

    python validation/penalized_pseudolikelihood/diagnose_lambda_selection_v3.py \
      --mode confirmation --bootstrap-replicates 2000

This diagnostic reproduces the current minimum-mean-Pearson selector, compares
four prespecified cache-only alternatives, evaluates Gamma and count tracks
with their data-generating variances, and measures paired-fold bootstrap
stability. It writes `v3/diagnostics-v3-confirmation.json`; commit that compact
artifact but not `cache-v3/`. The diagnostic does not change the public
selector or retroactively reinterpret confirmation as passing. Any improved
rule must be validated later with a fresh seed stream.


## Version 1 archived study

For reproduction of the original study from the repository root:

```bash
python validation/penalized_pseudolikelihood/run_validation.py \
  --mode full --ncores 12
```

The full design is defined in `config.json`. It writes `results-full.json`,
`seeds-full.json`, and `environment-full.json`. A nonzero exit status means at
least one prespecified release gate failed. Do not remove or weaken a gate in
response to a failed result; revise the statistical implementation or document
the resulting limitation, then run a new study version.

For a pipeline check that is not release-eligible:

```bash
python validation/penalized_pseudolikelihood/run_validation.py \
  --mode smoke --ncores 1 --output-dir /tmp/toytree-pl-smoke
```


## Version 2 diagnostic and confirmation study

Version 1 completed with primary recovery passing only after results were pooled
across methods, while its predictive model-selection gate failed. Its artifacts
remain the immutable record of that study. Version 2 uses per-method gates,
paired one-standard-error selection, model-matched count and multiplicative
Gamma tracks, and population prediction regret.

Run the development pilot first:

    python validation/penalized_pseudolikelihood/run_validation_v2.py \
      --mode pilot --stage all --ncores 12

Every primary and cross-validation dataset is checkpointed separately under
v2/cache-v2/. Interrupted runs resume by default. The expensive fitting and
cheap scoring phases can also be run separately:

    python validation/penalized_pseudolikelihood/run_validation_v2.py \
      --mode pilot --stage fit --ncores 12

    python validation/penalized_pseudolikelihood/run_validation_v2.py \
      --mode pilot --stage score

Fold observations and predictions and every candidate full-fit prediction are
stored in the cache. Selection rules, prediction scores, population-risk
summaries, and reporting can therefore be changed without refitting. Changes
to estimator source, simulations, calibrations, or candidate configurations
invalidate the relevant caches automatically.

After reviewing the pilot, freeze the implementation and configuration before
using unused confirmation seeds:

    python validation/penalized_pseudolikelihood/run_validation_v2.py \
      --mode confirmation --stage all --ncores 12

Version 2 is archived and is not release-eligible because cross-family
selection was rejected as the target. Its smoke mode exercises all four data-generating families and the CV path but
uses too few replicates and candidate configurations to support inference.

### Targeted version-1 diagnostics

The committed diagnostic runner rechecks all nonconverged discrete replicates at
1, 4, and 8 starts and measures uncorrelated rate recovery with all internal
ages fixed:

    python validation/penalized_pseudolikelihood/diagnose_v1_failures.py \
      --ncores 12

The recorded diagnostics-v1.json artifact found that all 33 failed discrete
seeds converged with four starts. Four- and eight-start objectives had a median
absolute difference of 6.2e-9 and a maximum difference of 0.0192. The 20
fixed-age uncorrelated controls had median log-rate Spearman 0.930, showing
that the weaker free-age result is primarily age-rate nonidentifiability.
This justified the historical four-start default. V10 supersedes that
recommendation after replaying newer zero-rich and Gamma-mixture failures:
public `discrete` now defaults to eight starts and is stress-tested against
sixteen. The retired private Gamma helper used sixteen versus thirty-two starts
in its final evaluation; other public methods retain their model-specific
defaults.


### V10 discrete finalization

V8 established Gamma recovery and exact input/calibration scale behavior but
found fractional-Poisson boundary fits and four-versus-eight-start instability.
V10 adds EM mixture initialization, a bounded fallback optimizer, projected
gradient diagnostics, and explicit category/time-boundary metadata. Its
nine-dataset failure replay passes all targeted gates using each model-specific
default and its doubled-start reference. The development pilot passed convergence, calibration, Gamma-recovery, and
scale-invariance gates, but failed all doubled-start stability gates. Targeted
128- and 256-start fits continued to find better optima. Consequently,
`discrete` is finalized for chronos compatibility, while the Gamma candidate is
removed from the public API. Its private helper and V8/V10 evidence are retained
for reproducibility; no confirmation run is planned. See README-v10.md.

### Deferred correlated lambda-selection work

The correlated V9 result should not be summarized as showing that lambda is
generally unidentifiable. V9 deliberately replayed difficult cases. It showed
that minimum-mean terminal-edge CV can select a useful point estimate while
the supported lambda interval and chronogram sensitivity remain broad for
some individual trees. Future correlated work should retain the current point
selector and expose lambda-support/chronogram-sensitivity diagnostics.

The UCLN V4 result is not an equivalent per-tree CV result. Its lambda was
selected across a simulation pilot using known true ages and then frozen for
confirmation. Before claiming that UCLN lambda is more identifiable than
correlated lambda, run both penalties through the same per-tree held-edge CV
design on paired trees, calibrations, and lambda grids. The expected advantage
of UCLN is its single global centered-log-rate shrinkage direction, whereas
the correlated penalty regularizes many local parent-child contrasts; that
hypothesis remains to be tested directly.
