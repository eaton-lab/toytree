# Version 9: correlated-lambda uncertainty replay

V9 is a targeted, diagnostic-only replay of the unresolved correlated-model
uncertainty cases. It replaces a full V6 rerun for this question.

The original V6 pilot caches are valid records of the estimator that produced
them, but they cannot be rescored as current fits: the correlated optimizer
changed after those caches were created. Recomputing all 40 V6 datasets would
repeat many cases that already behaved adequately. V9 instead reruns the eight
old-pilot datasets whose between-lambda normalized age spread exceeded 0.1 and
which were not already rerun by the current-estimator V6 stability stress. The
current V6 replay is included only in a separately labeled descriptive summary;
it is not pooled into V9's decision gates.

## What is parallelized

A terminal-edge CV fit must evaluate lambda values from strong to weak smoothing
in sequence because each stable fit warm-starts the next value. Those values
cannot be split safely across processes. The independent unit is therefore one
complete held-tip lambda path.

V9 creates one global process pool across every dataset, observation loss, and
held tip:

- 8 datasets and 2 observation losses;
- 624 independent held-tip paths in the main replay;
- 25 serial lambda fits within each path;
- 32 independent post-CV tasks (a selected-fit path and a full-grid path for
  each dataset/loss combination).

Thus --ncores 80 can launch 80 worker processes during the held-tip phase. It is
no longer capped at eight datasets (or at the five datasets in the earlier V6
stability run). Numerical libraries are restricted to one thread per worker to
avoid nested oversubscription.

Every held-tip path and post-CV path is written atomically to its own cache file.
An interrupted command resumes only unfinished or stale tasks. Fit fingerprints
cover the estimator, simulator, calibrations, lambda grid, and optimizer
settings. Scoring has a separate fingerprint, so changing bootstrap summaries
or decision gates does not invalidate expensive fit caches.

## Scientific target

The multiplicative-Gamma working loss is the release-gating track. The
fractional-Poisson loss is retained as a descriptive baseline. V9 asks whether,
under the current optimizer:

1. every selected Gamma fit is stable and objective-competitive;
2. every bootstrap-supported Gamma lambda has a valid, stable full-grid fit;
3. every Gamma dataset has at least five valid lambda candidates;
4. maximum total normalized age uncertainty is at most 0.1 in every dataset;
5. selected/oracle normalized age-RMSE ratios have median at most 1.25 and
   90th percentile at most 2.0.

The maximum-uncertainty criterion combines uncertainty across
bootstrap-supported lambdas with within-lambda near-optimal chronogram
instability. It intentionally uses the maximum over datasets, not only a pooled
quantile.

This study remains diagnostic-only because its datasets were selected using
historical failures. Passing V9 would justify freezing the implementation and
running a new, independently seeded confirmation; it would not itself establish
release validity. No sequence-length input, RSRCV, model-family selection, or
public Gamma-loss API is introduced.

## Local smoke test

Run the complete pipeline, then prove that score-only reuse does not refit:

    python validation/penalized_pseudolikelihood/run_validation_v9_uncertainty.py \
      --mode smoke \
      --stage all \
      --ncores 4 \
      --bootstrap-replicates 100 \
      --output-dir /tmp/toytree-v9-smoke

    python validation/penalized_pseudolikelihood/run_validation_v9_uncertainty.py \
      --mode smoke \
      --stage score \
      --ncores 1 \
      --bootstrap-replicates 100 \
      --output-dir /tmp/toytree-v9-smoke

The smoke grid has only three candidates, so it is expected to fail the
five-valid-candidate scientific gate. Its purpose is pipeline verification.

## Remote replay

After pulling the branch on the server, install the checked-out code and run:

    git switch fix/penalized-likelihood-validation
    git pull --ff-only origin fix/penalized-likelihood-validation
    pip install -e ".[test]"

    python validation/penalized_pseudolikelihood/run_validation_v9_uncertainty.py \
      --mode uncertainty-replay \
      --stage fit \
      --ncores "$(nproc)"

    python validation/penalized_pseudolikelihood/run_validation_v9_uncertainty.py \
      --mode uncertainty-replay \
      --stage score \
      --ncores 1

The fit phase prints a phase_start record showing worker_processes; on an
80-core host it should report 80 for the 624-task held-tip phase. Each completion
also reports elapsed time and an evolving ETA. If the process stops, rerun the
same fit command. Do not use --no-resume.

Only compact provenance and result artifacts belong in Git:

    git add \
      validation/penalized_pseudolikelihood/v9/results-v9-uncertainty-replay.json \
      validation/penalized_pseudolikelihood/v9/environment-v9-uncertainty-replay.json \
      validation/penalized_pseudolikelihood/v9/seeds-v9-uncertainty-replay.json

    git commit -m "Record V9 correlated uncertainty replay"
    git pull --rebase origin fix/penalized-likelihood-validation
    git push origin HEAD:fix/penalized-likelihood-validation

Do not add v9/cache-v9/; it is large, machine-local, and ignored by Git.
