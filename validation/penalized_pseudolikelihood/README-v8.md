# V8 discrete-model validation

V8 validates the hardened branchwise finite-mixture optimizer and the new
multiplicative-Gamma observation model. It is independent of the active V6
correlated-model study: it has its own source fingerprint, seeds, cache, and
outputs.

The study covers K=2 and K=3, 24- and 96-tip trees, root-only and
root-plus-internal calibrations, and fixed-age controls. The
`fractional_poisson` datasets exercise the chronos-compatible `discrete`
model. Gamma datasets use true branch CVs 0.05, 0.1, and 0.2 but are all fit
with the documented default `branch_cv=0.1`. Four-versus-eight-start fits are
run on the first replicate of every cell. Gamma fits additionally repeat both
input-branch and calibration-time scales by 1e6.

Run a local smoke test:

```bash
python validation/penalized_pseudolikelihood/run_validation_v8_discrete.py \
  --mode smoke --ncores 1
```

Run the development pilot:

```bash
python validation/penalized_pseudolikelihood/run_validation_v8_discrete.py \
  --mode pilot --ncores 8
```

After the implementation and configuration are frozen, run confirmation on
the remote machine:

```bash
python validation/penalized_pseudolikelihood/run_validation_v8_discrete.py \
  --mode confirmation --ncores 32
```

Do not run confirmation from the current development state. The latest pilot
passes Gamma scale equivariance and its age-, bias-, and mixture-recovery
thresholds, but it fails the prespecified optimizer-stability gates. Four and
eight starts can select different local optima (maximum normalized age RMSE
about 0.086 and maximum relative objective improvement about 0.10). The
fractional-Poisson model also reports failed convergence on datasets with many
exactly zero branch lengths. These are implementation findings to resolve,
not reasons to relax the confirmation thresholds.

Workers write atomic files below `v8/cache-v8/<mode>/`. Re-running the same
command resumes matching cached records. Results, seed manifests, and
environment metadata are written below `v8/`. Confirmation gates are
prespecified in `config-v8.json`. A failed gate is evidence for further
development, not a reason to revise its threshold after seeing the result.
