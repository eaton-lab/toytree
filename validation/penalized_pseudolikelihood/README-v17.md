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
```

Every engine fit is an atomic file below `v17/cache-v17/`. Repeating the fit
command resumes from valid task fingerprints. Changing bootstrap summaries
does not invalidate fit caches.

The elapsed times from this highly parallel stage measure throughput under
contention and are not used as publication-quality speed estimates. Run the
separate paired timing subset on an otherwise idle server. It is serial,
alternates engine order, and has its own resumable caches:

```bash
python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode pilot --stage timing --ncores 1
```

After reviewing the pilot, freeze any justified design changes before using
the untouched confirmation seed stream:

```bash
python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode confirmation --stage generate --ncores 1

python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode confirmation --stage fit --ncores "$(nproc)"

python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode confirmation --stage score --ncores 1

python validation/penalized_pseudolikelihood/run_validation_v17_benchmark.py \
  --mode confirmation --stage timing --ncores 1
```

Commit only the JSON/CSV result, controlled-timing result, environment, and
seed ledgers. Do not commit the task cache directory.
