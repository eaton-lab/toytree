# Version 17: paired ToyTree–ape benchmark

V17 is a publication-oriented, paired simulation benchmark of ToyTree's
branch-length pseudolikelihood chronogram implementations and
`ape::chronos`. Each simulated dataset is written once to a fingerprinted
manifest. ToyTree and ape then fit the identical Newick tree and calibration
constraints as independently cached tasks.

The study compares strict clock, two- and three-category discrete, correlated,
and chronos-compatible relaxed fits. ToyTree's UCLN model is included as a
ToyTree-only accuracy and timing control because `chronos` has no matching
centered-log-rate model. Clock, discrete, and relaxed have compatible
objectives, so V17 reports fitted-objective and chronogram parity for them.
ToyTree's correlated model instead uses a scale-invariant log-rate penalty and
an explicit basal-edge term; its numerical objective is therefore not compared
directly with the raw-rate chronos penalty.

The benchmark estimates performance, not automatic model selection. Category
counts and lambda values are fixed by the scenario. It records convergence,
normalized internal-age error, paired chronogram differences, runtime, and
bootstrap confidence intervals for paired accuracy and speed contrasts. Raw
per-dataset results are retained so publication figures and alternative
summaries can be reproduced without refitting.

Primary recovery summaries include only successful, converged,
calibration-valid fits. Primary parity summaries additionally require both
engines to meet those conditions on the same dataset. All returned values are
retained under explicitly named diagnostic fields. This distinction matters
for fractional-Poisson simulations: exact zero branch lengths are valid
ToyTree inputs, but `chronos` frequently returns a nonconverged tree for them.
Those cells measure input robustness and are not allowed to contaminate
objective-parity or accuracy summaries.

## Dependencies

The Python environment must contain ToyTree's development dependencies. R must
provide `Rscript` and the exact ape version declared in `config-v17.json`
(currently 5.8.1). The R adapter deliberately does not require `jsonlite`.

Check the remote environment:

```bash
Rscript --version
Rscript -e 'cat(as.character(packageVersion("ape")), "\n")'
```

## Local smoke test

```bash
python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode smoke --stage all --ncores 2 \
  --output-dir /tmp/toytree-pl-v17-smoke
```

## Remote pilot

Run generation once, all independent fits with the full worker pool, and then
cache-only scoring:

```bash
python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode pilot --stage generate --ncores 1

python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode pilot --stage fit --ncores "$(nproc)"

python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode pilot --stage score --ncores 1

python validation/penalized_pseudolikelihood/diagnose_validation_v17.py \
  --mode pilot
```

Every engine fit is an atomic file below `v17/cache-v17/`. Repeating the fit
command resumes from valid task fingerprints. Changing bootstrap summaries
does not invalidate fit caches.

The elapsed times from this highly parallel stage measure throughput under
contention and are not used as publication-quality speed estimates. Run the
separate paired timing subset on an otherwise idle server. It is serial,
alternates engine order, and has its own resumable caches. The pilot uses
three paired replicates per tree-size/model cell; confirmation uses ten:

```bash
python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode pilot --stage timing --ncores 1
```

### Targeted relaxed-basin diagnostic

The pilot's relaxed-model result must be diagnosed before confirmation. The
targeted runner selects the four largest cases where ape has the better
penalized objective and two opposite-direction controls. It independently
re-evaluates both cached fits under ToyTree's ape-compatible objective, then
runs three trials of eight randomized starts for each selected dataset. The 18
fit tasks are globally parallel and independently resumable:

~~~bash
python validation/penalized_pseudolikelihood/diagnose_relaxed_v17.py \
  --mode pilot --stage fit --ncores "$(nproc)"

python validation/penalized_pseudolikelihood/diagnose_relaxed_v17.py \
  --mode pilot --stage score --ncores 1
~~~

If objective re-evaluation matches the cached values and random multistarts
reach ape's objective, the compatibility problem is initialization or default
start coverage. If re-evaluation matches but random multistarts do not reach
ape, the next diagnostic is an ape-solution warm start and gradient check.
Neither outcome justifies running confirmation yet.

The pilot random-multistart diagnostic reproduced the cached objectives to
floating-point precision (maximum error below `3e-14`), but it still failed to
reach the ape solution in the four strongest `n=48` failures. The next focused
test maps each cached ape solution into ToyTree's parameterization, evaluates
the gradient there, and starts the existing ToyTree optimizer from that exact
point:

```bash
python validation/penalized_pseudolikelihood/diagnose_relaxed_warmstart_v17.py \
  --mode pilot --stage fit --ncores "$(nproc)"

python validation/penalized_pseudolikelihood/diagnose_relaxed_warmstart_v17.py \
  --mode pilot --stage score --ncores 1
```

This diagnostic runs only four independent tasks, uses the cached ape fits,
and does not invoke R or refit ape. Its per-dataset results are resumable.

That test reproduced all four ape objectives exactly, but the projected
gradient at ape's reported solutions ranged from `0.021` to `0.245`. Starting
ToyTree at those points improved the objective by `0.078` to `0.763`. The
Gamma-CDF objective is therefore shared, while the optimizers stop in
different basins and ape's supplied relaxed-penalty gradient is not the full
derivative of that objective.

A regenerated failure showed that a strict-clock chronogram provides a much
better deterministic start without using ape: normalized age MAE fell from
`0.535` to `0.060`, versus `0.100` for ape, while the penalized objective
improved by `12.19`. The production relaxed fitter now uses this start when
the nested clock fit converges. Replay all 36 relaxed pilot datasets in a new
cache namespace, leaving the frozen original fits intact:

```bash
python validation/penalized_pseudolikelihood/run_validation_v17_relaxed_initialization.py \
  --mode pilot --stage fit --ncores "$(nproc)"

python validation/penalized_pseudolikelihood/run_validation_v17_relaxed_initialization.py \
  --mode pilot --stage score --ncores 1
```

This replay invokes neither R nor ape. All 36 fits converged with valid
calibrations. Median normalized age MAE fell from `0.396` under the former
topology-only start to `0.052`, compared with `0.109` for ape among its 31
eligible fits. The paired mean improvement over ape was `0.0666` with a 95%
bootstrap interval of `0.0542` to `0.0795`, and every ToyTree fit reached an
objective at least as high as ape. The clock start improved the former
ToyTree objective in 35 of 36 datasets. In the exception, the objective was
only `0.0324` lower while age MAE improved from `0.124` to `0.087`; ape did
not converge. Running both deterministic starts would therefore double work
to select a less accurate chronogram in this case, illustrating the weak
alignment between this compatibility objective and age recovery.

The pilot supports retaining the strict-clock start and unblocks the frozen
confirmation benchmark. It does not change `relaxed` from compatibility-only
status or make it preferable to UCLN for new analyses.

### Confirmation

The relaxed issue is resolved for the benchmark and the design is frozen. Use
the untouched confirmation seed stream:

```bash
python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode confirmation --stage generate --ncores 1

python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode confirmation --stage fit --ncores "$(nproc)"

python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode confirmation --stage score --ncores 1

python validation/penalized_pseudolikelihood/diagnose_validation_v17.py \
  --mode confirmation

python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode confirmation --stage timing --ncores 1
```

Commit only the JSON/CSV result, controlled-timing result, environment, and
seed ledgers. Do not commit the task cache directory.
