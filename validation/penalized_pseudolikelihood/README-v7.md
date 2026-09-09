# Version 7: strict-clock validation

Version 7 completed numerical and simulation validation of the strict-clock
estimator. The single shared rate is profiled analytically at every candidate
age vector, so the numerical optimizer searches only over free internal-node
ages. The public default remains one start. Four starts are used as an
independent stability comparator, not as a different statistical model.

The study uses no sequence-length or effective-site-count input. Simulated
phylogram branches use expected substitutions per site, but this is the chosen
simulation unit rather than a requirement of the estimator. Calibrations are
expressed in relative time, then selected cases are repeated after multiplying
every calibration age by one million. A calibration-time-unit-invariant fit should
all inferred ages by one million, divide the rate by one million, and preserve
the normalized chronogram.

## Prespecified pilot

The 48-dataset pilot crosses 12- and 48-tip birth-death chronograms, root-only
and root-plus-internal-interval calibrations, and three observation regimes:
exact strict-clock branch expectations, multiplicative Gamma noise with shape
100, and mean-one lognormal noise with coefficient of variation 0.1. There are
four replicates in each cell.

The pilot checks:

- convergence and calibration validity for both one and four starts;
- agreement of their optimized objectives and normalized node ages;
- agreement among near-optimal four-start chronograms;
- exact/noisy age recovery and signed age bias; and
- calibration-time-unit invariance under the one-million-fold rescaling.

These development seeds were not release-confirmatory. The implementation,
design, and thresholds were frozen before using the separate confirmation seed
stream. A failed gate would have been recorded rather than repaired by weakening
the threshold after seeing results.

## Development pilot outcome

The 48-dataset pilot passed all prespecified gates. All 96 primary fits
converged, every four-start fit was stable, and every calibration remained
valid. The maximum one-start versus four-start relative objective gap was
`4.24e-11`, and their maximum root-normalized age difference was `2.78e-6`.
Median normalized internal-age MAE was `1.22e-7` for noiseless observations and
`0.00750` across the two noisy regimes. The largest age discrepancy after the
one-million-fold calibration-time-unit change was `1.81e-6`; the corresponding maximum rate
rescaling error was `1.33e-6`. These are development results, not an
independently seeded confirmation.

## Independent confirmation outcome

The confirmation used 360 new datasets: 12-, 48-, and 96-tip trees; root-only
and root-plus-internal-interval calibrations; noiseless, Gamma-noise, and
lognormal-noise observations; and 20 replicates per cell. All nine release gates
passed. All 720 primary fits converged, all four-start fits were stable, and all
calibrations were valid. The maximum relative objective gap between one and four
starts was `1.16e-9`, and the maximum root-normalized age difference was
`5.45e-6`. Median internal-age MAE was `1.84e-7` without noise and `0.00727`
across noisy observations. The largest calibration-time-unit rescaling discrepancies were
`2.78e-6` for ages and `2.26e-6` for rates. Mean normalized age bias was
`0.000350` or less in absolute value across observation regimes.

Together with analytic-gradient checks, exact conditional-rate tests, edge-case
and calibration tests, and the pinned `ape::chronos` 5.8-1 parity fixture, this
completes development validation of the strict-clock estimator within its
documented branch-length pseudolikelihood scope. It does not claim to model
topology error or uncertainty in branch lengths estimated from sequence data.

## Run order

Run the focused tests and inexpensive smoke study locally:

    pytest -q tests/mod/test_pl_clock.py \
      tests/mod/test_make_ultrametric_api.py \
      tests/mod/test_pl_multistart.py \
      tests/mod/test_pl_ape_parity.py

    python validation/penalized_pseudolikelihood/run_validation_v7_clock.py \
      --mode smoke --stage all --ncores 1 \
      --output-dir /tmp/toytree-pl-v7-smoke

Run or resume the development pilot:

    python validation/penalized_pseudolikelihood/run_validation_v7_clock.py \
      --mode pilot --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v7_clock.py \
      --mode pilot --stage score --ncores 1

Reproduce the independently seeded confirmation:

    python validation/penalized_pseudolikelihood/run_validation_v7_clock.py \
      --mode confirmation --stage fit --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v7_clock.py \
      --mode confirmation --stage score --ncores 1

Each dataset is checkpointed atomically beneath `v7/cache-v7/`. The score stage
only reads fingerprint-matched caches and never calls a fitting function. Commit
compact result, environment, and seed artifacts when a remote run is requested;
the cache directory is intentionally ignored.
