# Version 14: profiled correlated-optimizer replay

V14 is a targeted numerical regression study, not a new statistical design.
It re-simulates the exact deterministic datasets used by the V13 pilot and
refits only:

- all 14 V13 datasets that failed at least one numerical gate; and
- six matched V13 datasets that passed, used as positive controls.

The failures include convergence, multistart stability, objective-basin,
chronogram-basin, and calibration-time-unit discrepancies. They are dominated
by fractional-Poisson datasets containing exact-zero branches, but also
include positive continuous observations whose earlier time-unit differences
slightly exceeded the prespecified tolerance.

The new optimizer solves rates conditionally for every proposed chronogram.
For fixed ages, the correlated log-rate objective is convex. V14 therefore
tests whether an exact Newton rate profile plus direct, linearly constrained
age optimization eliminates V13's numerical failures without changing zero
observations or degrading historically passing controls.

The parent-child increment correlation remains recorded by the underlying V13
scorer, but is not a V14 numerical gate. Penalized estimates intentionally
shrink increments, so their raw rank correlation is a statistical recovery
diagnostic rather than evidence that the optimizer reached the fitted
objective.

## Local smoke test

```bash
pytest -q \
  tests/mod/test_pl_correlated.py \
  tests/mod/test_pl_validation_v14.py

python validation/penalized_pseudolikelihood/run_validation_v14_correlated.py \
  --mode smoke \
  --stage all \
  --ncores 4 \
  --output-dir /tmp/toytree-v14-smoke
```

## Remote replay

```bash
git switch fix/penalized-likelihood-validation
git pull --ff-only origin fix/penalized-likelihood-validation
pip install -e ".[test]"

python validation/penalized_pseudolikelihood/run_validation_v14_correlated.py \
  --mode replay \
  --stage fit \
  --ncores "$(nproc)"

python validation/penalized_pseudolikelihood/run_validation_v14_correlated.py \
  --mode replay \
  --stage score \
  --ncores 1
```

Each fit role is a separate process-pool task and is cached atomically under
`v14/cache-v14/`. The score stage never refits. Commit only the compact
environment, seeds, and result JSON files, not the task cache.

V14 is diagnostic-only. Its passing replay led to the independently seeded,
release-gating V15 confirmation design in `README-v15.md`.
