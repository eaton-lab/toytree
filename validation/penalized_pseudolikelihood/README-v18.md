# V18: matched per-tree lambda identifiability

V18 asks whether terminal-edge cross-validation contains enough predictive
information to tune lambda on a single tree under the validated fixed-lambda
`correlated` and `uncorrelated_lognormal` (UCLN) estimators. It is diagnostic
only and does not create a public UCLN selector.

Lambda is a smoothing hyperparameter, not an ordinary likelihood parameter.
The primary target is therefore recovery relative to the best candidate
chronogram, not exact recovery of the simulation-matched value
`1 / (2 * sigma_log ** 2)`.

## Frozen design

The pilot contains 128 model-specific datasets: two matched model families,
24 and 48 tips, log-rate sigma 0.3 and 0.6, root-only or root-plus-three
internal interval calibrations, expected or continuous-Gamma branch
observations, and four replicates. Paired model families share topology,
calibration, and observation-noise streams. The 17-candidate grid spans
`1e-4` through `1e4` in half-log10 steps.

Each terminal branch is omitted from both initialization and the objective.
A complete lambda path is serial from strong to weak smoothing, while held-tip
paths from every dataset are pooled globally over worker processes. Stable
solutions continue the next fit; failed or unstable solutions reset the path.
Every lambda is also fitted on the complete tree for oracle recovery and
chronogram-sensitivity scoring.

Fold columns are resampled as paired units 2,000 times. The 2.5--97.5%
quantiles of selected `log10(lambda)` define the descriptive support interval.
The study reports selection frequencies, grid-boundary selections, and the
maximum internal-age spread over full-tree fits in that interval.

The gates are evaluated separately for correlated and UCLN:

- stable selected fits at least 99%;
- all calibrations valid;
- boundary selections at most 10%;
- selected/oracle age-RMSE ratio median at most 1.25 and p90 at most 2.0;
- supported chronogram spread median at most 0.05 and p90 at most 0.15 root ages.

Zero-rich fractional-Poisson data are excluded because fixed-lambda UCLN is
currently validated only for positive continuous branches. A passing UCLN
pilot permits the independently seeded 96-tip confirmation. Same-data
bootstrap-tree aggregation is deferred until per-tree CV demonstrates useful
predictive signal; it cannot rescue an uninformative per-tree criterion.

## Local smoke test

```bash
python validation/penalized_pseudolikelihood/run_validation_v18_lambda_identifiability.py \
  --mode smoke --stage all --ncores 2
```

## Remote pilot

Commit and push the implementation from the development machine:

```bash
git add \
  toytree/mod/_src/penalized_pseudolikelihood/uncorrelated_lognormal.py \
  tests/mod/test_pl_validation_v18.py \
  validation/penalized_pseudolikelihood/config-v18.json \
  validation/penalized_pseudolikelihood/README-v18.md \
  validation/penalized_pseudolikelihood/README.md \
  validation/penalized_pseudolikelihood/run_validation_v18_lambda_identifiability.py \
  validation/penalized_pseudolikelihood/v12/compatibility-v12-current.json

git diff --cached --check
git commit -m "Add matched per-tree lambda validation"
git push origin main
```

On the remote server:

```bash
git pull --ff-only origin main
python validation/penalized_pseudolikelihood/run_validation_v18_lambda_identifiability.py \
  --mode pilot --stage fit --ncores "$(nproc)"
python validation/penalized_pseudolikelihood/run_validation_v18_lambda_identifiability.py \
  --mode pilot --stage score --ncores 1
```

The fit stage resumes fingerprint-compatible path caches automatically. Scoring
never reruns likelihood optimization. Inspect the result with:

```bash
jq '{
  all_models_passed: .summary.all_models_passed,
  correlated: .summary.models.correlated,
  ucln: .summary.models.uncorrelated_lognormal,
  next_stage
}' validation/penalized_pseudolikelihood/v18/results-v18-pilot.json
```

Only if the UCLN pilot passes, run the fresh 96-tip confirmation by replacing
`--mode pilot` with `--mode confirmation` in both commands.
