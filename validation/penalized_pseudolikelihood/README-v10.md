# V10 discrete finalization and Gamma-candidate evaluation

V10 preserves the failed V8 pilot as a diagnostic, validates the hardened
chronos-compatible finite-mixture optimizer, and evaluates a separate
multiplicative-Gamma candidate. It separates two conclusions:

- `discrete` is validated for `ape::chronos` objective/full-fit parity,
  numerical robustness, calibration validity, and honest boundary reporting.
  Its fractional-Poisson recovery measurements are diagnostic rather than
  release gates.
- The private multiplicative-Gamma candidate is scale invariant and passed
  its age, bias, mixture-recovery, scale, and convergence gates, but it failed
  optimizer-stability gates and was retired from the public API.

The implementation uses EM to initialize rates and weights at fixed clock
ages, followed by the unchanged joint likelihood optimization. Failed
L-BFGS-B fits receive an extended retry and then a bounded SLSQP fallback.
`discrete` defaults to eight starts and is stress-tested against sixteen.
For historical evaluation, the sharper low-noise Gamma surface used sixteen
starts and was stress-tested against thirty-two. Category collapse is returned
as a valid boundary fit with explicit
metadata; it is not silently interpreted as evidence for the requested K.

The V10 runner schedules main, fixed-age, model-specific doubled-start
stress, scale, and branch-CV sensitivity fits as independent tasks. Therefore
`--ncores 80` can use up to 80 workers even when a replay contains only a few datasets.
Each fit is atomically cached below `v10/cache-v10/<mode>/`.

## Development runs

Run the fast smoke study:

```bash
python validation/penalized_pseudolikelihood/run_validation_v10_discrete.py \
  --mode smoke --ncores 8
```

Replay every convergence or multistart failure identified by V8:

```bash
python validation/penalized_pseudolikelihood/run_validation_v10_discrete.py \
  --mode failure-replay --ncores 16
```

The final smoke and nine-dataset historical failure replay pass. The replay
contains thirty independent fit tasks.

Run the representative development pilot:

```bash
python validation/penalized_pseudolikelihood/run_validation_v10_discrete.py \
  --mode pilot --ncores 32
```

Primary Gamma fits use the same `branch_cv` used to simulate each dataset
(0.05, 0.1, or 0.2). Separate default-`0.1` fits at true CV 0.05 and 0.2
measure misspecification sensitivity but do not replace the matched primary
fit and are not release gates.

The development pilot passed every convergence, calibration, Gamma-recovery,
and scale-invariance gate. It failed all multistart-stability gates. Moving
`discrete_gamma` from 8/16 to 16/32 starts still produced a maximum normalized
age RMSE of 0.0612, p90 of 0.0324, and maximum relative objective improvement
of 1.046 among identified mixtures. Targeted 128- and 256-start replays found
further improvements, so a larger fixed start count is not a validated remedy.
Only 7 of 54 identified primary fits independently replicated their selected
optimum within the tight objective tolerance. This result supports retiring
rather than escalating the start budget of the free-age Gamma candidate. Its
private replay fit reports `optimum_replicated` for diagnostic use.

## Final disposition

No confirmation run will be performed for the Gamma candidate. The public
`discrete_gamma` method and dispatcher option were removed. The implementation
is retained as a private helper solely to reproduce V8/V10 and to preserve
useful likelihood code for future research.

For general uncorrelated-rate dating, use `uncorrelated_lognormal`. If a future
model needs a small number of biologically persistent rate regimes, implement
an explicit local-clock model rather than reviving this independently mixed
free-age formulation.
